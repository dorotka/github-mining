#!/usr/bin/env python3
"""
Extract commits that are fixes. It performs syntactic and semantic analysis according to the SZZ algorithm.
It creates a tuple (commit, message, number(possible bug), syntactic score, author email, semantic score)
Saves fixes in ./data/<project>/fixes.json
If test is True, then it will save ./data/<project>/test/test_fixes.json with positive and negative results for verification.

Args:
      project: project to get commits from

  Usage:
      python3 extract_fixes.py <project>

"""
from argparse import ArgumentParser
from sys import stderr

from helper import load_data, save_in_file, list_to_dict, get_test_dir
from githubapi import giturlopen
from os import path
from logger import log_debug

import json
import re


argparser = ArgumentParser()
argparser.add_argument('project',
    help='project to get fixes from')

user_email = {}
test = False


def is_bug_number(mssg, number, number_pattern):
    """
        Find the bug numbers in the message and verify it against the number in the link
    """
    bug_pattern = re.compile('(bug[# \t]*[0-9]+|pr[# \t]*[0-9]+|show\_bug\.cgi\?id=[0-9]+|\[[0-9]+\]|issue[# \t]*[0-9]+|gh-*[0-9]+|issue-*[0-9]+|fix-*[0-9]+|gh/*[0-9]+|ice_*[0-9]+)', re.IGNORECASE)
    bugs = bug_pattern.findall(mssg)
    for bug in bugs:
        if number in bug:
            return True
    return False


def is_merge(mssg):
    merge = 'merge' in mssg.lower()
    squash = mssg.strip().startswith('Squashed')
    return merge or squash


def is_hash_number(mssg, number, number_pattern):
    # Note: Any hash number since some repos use that convention.
    bug_pattern = re.compile('(# *[0-9]+)', re.IGNORECASE)
    bugs = bug_pattern.findall(mssg)
    for bug in bugs:
        if number in bug:
            return True
    return False


def is_number(mssg):
    plain_number_pattern = re.compile('^[0-9]+$')
    num = plain_number_pattern.match(mssg)
    return num is not None


def is_test(mssg):
    """
        Detects test added for a fix
        :param mssg:
        :return:
    """
    test = re.compile('test(s?) for[# \t]*[0-9]+|test case for[# \t]*[0-9]+|integration test|regression test|add test|added test', re.IGNORECASE)
    t = test.findall(mssg)
    return len(t) > 0


def is_revert(mssg):
    return mssg.strip().lower().startswith('revert')


def is_keyword(mssg):
    # Note: Does not contain issue since it caused too many false positives because of included urls.
    keyword_pattern = re.compile('(fix(ing|e[ds])?|bug(s)?|defect(s)?|patch|resolve)', re.IGNORECASE)
    keywords = keyword_pattern.findall(mssg)
    return len(keywords) > 0


def select_number(item):
    if item.strip().startswith('#'):
        return item[1:]
    if item.strip().startswith('/'):
        return item[1:]
    if item.strip().startswith('-'):
        return item[1:]
    else:
        return item.strip()


def is_fixed(labels):
    for label in labels:
        if 'fixed' in label['name']:  # regex?
            return True
    return False


def get_email(user_url, user_id):
    if user_id in user_email.keys():
        return user_email.get(user_id)
    page = giturlopen(user_url)
    try:
        user = json.loads(page.read().decode())
        user_email[user_id] = user['email']
        return user['email']
    except Exception as e:
        log_debug(None, e, None)


def same_emails(email1, email2):
    if email1 is None:
        return False
    if email1 == email2:
        return True
    # more flexible comparison: cgdecker@gmail.com vs cgdecker@google.com
    user1 = email1.split('@')[0]
    user2 = email2.split('@')[0]
    if user1 == user2:
        return True


def is_closed(bug, time, number):
    """Check if the bug was closed on the same date or later than the commit was commited"""
    return bug['state'] == 'closed'


def analyze_syntax_commits(directory, project):
    """
    Creates links from the commit to the possible bug number from the commit message together with the syntactic score.
    It checked syntax only -- there is no verification whether the numbers considered to be possible bugs are indeed bug numbers.
    :param directory:
    :return: a list of tuples - links between commits and the possible bug numbers with the syntactic scores
    """
    commits_dir = path.join(directory, 'commits.json')
    number_pattern = re.compile('[# \t][0-9]+|[/ \t][0-9]+|[- \t][0-9]+')
    commits = load_data(commits_dir)
    links = list()
    for commit in commits:
        # Note: omit merge commits
        if is_merge(commit['message']) or is_revert(commit['message']):
            continue
        for n in number_pattern.findall(commit['message']):
            num = select_number(n)
            if int(num) < 1:
                continue
            syntactic = 0
            if is_bug_number(commit['message'], num, number_pattern) or is_hash_number(commit['message'], num, number_pattern):
                syntactic += 1
            if is_number(commit['message']) or is_keyword(commit['message']):
                syntactic += 1
            if is_test(commit['message']):
                syntactic = 0
            link = (commit['commit'], commit['message'], num, syntactic, commit['author_email'], commit['time'])
            links.append(link)
    if test:
        test_dir = get_test_dir(directory)
        save_in_file(links, 'test_fix_partial_links.json', test_dir)
    return links


def analyze_semantics_commits(links, directory, project):
    """
    Performs semantic analysis: bug number verification, closed issue verification, email addresses of assignee and similar messages between the bug and the commit.
    :param links: results from the syntactic analysis
    :param directory: of the data
    :return: list of fixes
    """
    bugs_dir = path.join(directory, 'bugs.json')
    bugs = load_data(bugs_dir)
    ranked = set()
    bugs_dict = list_to_dict(bugs, 'number')
    for link in links:
        semantic = 0
        key = int(link[2])
        if key in bugs_dict.keys():
            bug = bugs_dict.get(key)
            if is_fixed(bug['labels']) or is_closed(bug, link[5], link[2]):
                semantic += 1
            if bug['title'] in link[1]:
                semantic += 1
            if bug['assignee'] is not None:
                assignee_email = get_email(bug['assignee']['url'], bug['assignee']['id'])
                if same_emails(assignee_email,link[4]):
                    semantic += 1
            score = (semantic,)
            new_link = link + score
            if new_link[3] > 0 or new_link[6] > 0:
                ranked.add(new_link)
    fixes = choose_fixes(ranked, directory, project)
    return fixes


def choose_fixes(links, directory, project):
    fixes = set()
    if test:
        test_fixes_positive = list()
        test_fixes_negative = list()
        test_fixes = {"positives": test_fixes_positive, "negatives": test_fixes_negative, "notes": ""}
    for link in links:
        # sytax > 0 and semantics = 1  or  semantics > 1
        if (int(link[3]) > 0 and int(link[6]) == 1) or int(link[6]) > 1:
            fixes.add(link[0])
            if test:
                pos = (link[0], link[1], link[2], link[3], link[6])
                test_fixes_positive.append(pos)
        elif test:
            neg = (link[0], link[1], link[2], link[3], link[6])
            test_fixes_negative.append(neg)
    log_debug(project, 'Number of fixes: {0[0]}', (len(fixes),))
    if test:
        # Note: There may be more positives than fixes since full data is saved there. It does not mean duplicate fixes.
        log_debug(project, 'Number of positives: {0[0]}', (len(test_fixes_positive),))
        log_debug(project, 'Number of negatives: {0[0]}', (len(test_fixes_negative),))
        test_fixes.update({"fixes": len(fixes)})
        test_dir = get_test_dir(directory)
        save_in_file(test_fixes, 'test_fixes.json', test_dir)
    return fixes


def extract_fixes(directory, project):
    links = analyze_syntax_commits(directory, project)
    fixes = analyze_semantics_commits(links, directory, project)
    save_in_file(list(fixes), 'fixes.json', directory)


def main():
    args = argparser.parse_args()
    if args.project is None:
        stderr.write('Project name is required!')
    out_dir = path.join('data', args.project)
    extract_fixes(out_dir, args.project)


if __name__ == '__main__':
    main()
