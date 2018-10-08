#!/usr/bin/env python3
"""
    This file contains methods that verify the results from extract_buggy_lines.py and annotate_commits.py

    Usage:
        Run the script from tools directory.
        python3 test/test_buggy_lines.py
"""
from os import path
from helper import save_in_file, load_data, get_short_man, get_repos
from time import time
from logger import log_info
from extract_buggy_commits import get_lines
from annotate_commits import get_inserted_lines
import subprocess


def load_annotated(project):
    dir = path.join('data', project, 'commits_changes.json')
    return load_data(dir)


def load_buggy(project):
    dir = path.join('data', project, 'buggy_changes.json')
    return load_data(dir)


def report_results(errors, project, name):
    good = name + ' -- OK'
    bad = name + ' -- Errors: {0[0]}'
    if len(errors) == 0:
        log_info(project, good, None)
    else:
        if len(errors) > 3 and name == 'test_buggy_duplicates':
            t = path.join('data', project, 'test')
            f = name + '_buggy.json'
            save_in_file(list(errors), f, t)
            mssg = '...... See the file for the list to examine'
            log_info(project, bad, (mssg,))
        else:
            log_info(project, bad, (errors,))


def test_buggy_annotated(project):
    """
        Test whether the buggy lines were correctly accounted for in the annotated changes.
    """
    errors = list()
    buggy = load_buggy(project)
    for commit in load_annotated(project):
        short = get_short_man(commit['commit'], project)
        if buggy.get(short) is not None:
            if commit['buggy'] != len(buggy.get(short)):
                errors.append(commit['commit'])
    report_results(errors, project, 'test_buggy_annotated')


def test_annotated_sums(project):
    """Test annotated lines sums = good + buggy"""
    errors = list()
    for commit in load_annotated(project):
        if commit['buggy'] + commit['good'] != commit['inserted']:
            log_info(project, 'Incorrect sum of good + buggy in annotated: {0[0]}', (commit['commit'],))
            errors.append(commit['commit'])
    report_results(errors, project, 'test_annotated_sums')


def test_annotated_negatives(project):
    """test annotated lines for negative lines"""
    errors = list()
    for commit in load_annotated(project):
        if commit['buggy'] < 0 or commit['good'] < 0 or commit['inserted'] < 0:
            log_info(project, 'Negative line number in annotated: {0[0]}', (commit['commit'],))
            errors.append(commit['commit'])
    report_results(errors, project, 'test_annotated_negatives')


def test_buggy_duplicates(project):
    """Out of all the buggy commits, if there is a duplicate line, test what are the file names and if the same, note as error.
    Those are not really errors, just the duplicates that need to be investigated so that all the commits don't have to
    be investigated for duplicates, just the suspects."""
    errors = list()
    for commit, lines in load_buggy(project).items():
        names = dict()
        dups = set()
        for l in lines:
            file = l[1].split('/')
            name = file[len(file) - 1]
            if names.get(name) is not None:
                if l[0] in list(names.get(name).keys()):
                    # print('increasing occurance for ', commit, name)
                    names.get(name).get(l[0])['occurance'] += 1
                    dups.add((name, l[0]))
                else:
                    names.get(name)[l[0]] = {'occurance': 1}
            else:
                names.update({name: {l[0] :{'occurance': 1}}})
        if len(dups) > 0:
            errors.append({commit: list(dups)})
    if len(errors) > 0:
        log_info(project, 'Number of duplicates to investigate: {0[0]}', (len(errors),))
    report_results(errors, project, 'test_buggy_duplicates')


def get_files(c, repo):
    """Returns the list of files modified in the commit."""
    repo_dir = path.join('repos', repo)
    try:
        completed = subprocess.run(['git', 'diff-tree', '--no-commit-id', '--name-only', '-r', c], stdout=subprocess.PIPE, universal_newlines=True, cwd=repo_dir)
    except Exception as e:
        log_info.error(e)
        return None
    lines = str(completed.stdout)
    return lines.split('\n')


def test_files():
    pass
    #todo: git diff-tree --no-commit-id --name-only -r 5e4b70461dfd869c7d96b2528e666a9dd8e29183 gives you files divided by \n


def test_buggy_lines(project):
    """Test that all the buggy lines were the deleted lines in a fix."""
    errors = list()
    bd = path.join('data', project, 'test', 'test_buggy_lines.json')
    fd = path.join('data', project, 'test', 'test_buggy_fix_diffs.json')
    buggy_lines = load_data(bd)
    fix_diffs = load_data(fd)
    for commit in buggy_lines:
        sha = list(commit.keys())[0]
        buggy = commit['lines']
        file = commit['file']
        sha_short = sha[0:11]
        fix = fix_diffs.get(sha_short)
        if fix is None:
            print(project, sha, sha_short)
            continue
        for f in fix.get(sha):
            if f['old'] == file:
                deleted = f.get('deleted')
                if deleted != buggy:
                    errors.append((sha, file))
    report_results(errors, project, 'test_buggy_lines')


def test_buggy_lines_single(project, commit):
    """Test a specific commit's buggy lines with pre-verified data."""
    errors = list()
    buggy = load_buggy(project)
    fd = path.join('data', project, 'test', 'test_buggy_fix_diffs.json')
    fix_diffs = load_data(fd) # fix differences
    bc = 'dd1c14a0c70' # buggy commit
    rf = ['e64989beb455b144dcf576b1ec36c039258d5127', '479cbfc63c8261577b359b7703d7e6168c1a74f5',
          '42cfacf83bc6186fb72d1d724fd97b9aa5a84171', '88e1aa94fa0a0494b9808aaf9adec850444e3dbe'] # related fixes
    for b in buggy.get(bc):
        line = b[0]
        file = b[1]
        found = 0
        for sha in rf:
            sha_short = sha[0:11]
            fix = fix_diffs.get(sha_short)
            for f in fix.get(sha):
                if f['old'] == file:
                    deleted = f.get('deleted')
                    if line in deleted:
                        found = 1
                        break
        if found == 0:
            errors.append((bc, file, line, sha))
    report_results(errors, project, 'test_buggy_lines_single')
    # could authomate it. For each bc, go over buggy_lines blame lines, and if the sha is the same, add the fix to the list to examine. The rest would be the same.


def test_annotated_inserted(project):
    """Verify that number of inserted lines is correct."""
    errors = list()
    annotated = load_annotated(project)
    for commit in annotated:
        sha = commit['commit']
        inserted_num = get_inserted_lines(sha, project)
        if commit['inserted'] != inserted_num:
            errors.append(sha)
    report_results(errors, project, 'test_annotated_inserted')


def test_ranges():
    """test ranges in the buggy lines"""
    lines = [1, 2, 20, 199, 200, 215, 300, 350, 689, 1020, 1238, 1239, 1240, 1300]
    ranges = get_lines(lines)
    errors = list()
    for range in ranges:
        nums = range.split(',')
        if int(nums[1]) - int(nums[0]) > 200 or int(nums[1]) - int(nums[0]) < 0:
            errors.append(range)
    report_results(errors, None, 'test_ranges')


def test_buggy():
    repos = get_repos()
    for project in repos:
        test_buggy_annotated(project)
        test_annotated_sums(project)
        test_annotated_negatives(project)
        test_buggy_duplicates(project)
        test_buggy_lines(project)
        # test_annotated_inserted(project)


def main():
    T = time()
    test_buggy()
    test_ranges()
    test_buggy_lines_single('ansible', None)
    log_info(None, 'Tests run in {0[0]}', (time()-T,))


if __name__ == '__main__':
    main()