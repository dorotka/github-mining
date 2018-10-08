#!/usr/bin/env python3
"""
    Extract commits that introduced the bugs.
    buggy_changes.json file will contain the commit and the number of buggy lines across the files of the commit.
    Requires fixes.json.
    If test flag is True, then it will save test_buggy_changes.json with positive and negative results for verification.

    Usage: python3 extract_buggy_commits.py <project>
"""

import re
from logger import log_debug
import subprocess
from argparse import ArgumentParser
from os import path
from helper import save_in_file, load_data, get_test_dir, get_commit_differences
from time import time
from sys import stderr

test = False
argparser = ArgumentParser()
argparser.add_argument('project', help='project to get commits from')

hunk_header = re.compile(r'@@ -([0-9]+)(?:,([0-9]+))? \+([0-9]+)(?:,([0-9]+))? @@')
diff_line = re.compile(r'diff --git (?:a/(.+)|"a/([^"]+)") (?:b/(.+)|"b/([^"]+)")')


def load_fixes(directory):
  file = path.join(directory, 'fixes.json')
  fixes = load_data(file)
  return fixes


def get_short(commit, project):
    repo_dir = path.join('repos', project)
    num = 11
    short_num = '--short=' + str(num)
    cmd = ['git',  'rev-parse', short_num, commit]
    completed = subprocess.run(cmd, stdout=subprocess.PIPE,
                               universal_newlines=True,
                               cwd=repo_dir)
    short = str(completed.stdout).split('\n')[0]
    return short


def get_fix_changes(project):
    """
        Get deleted and inserted lines for each fix
    """
    T = time()
    directory = path.join('data', project)
    differences = dict()
    for fix in load_fixes(directory):
        diffs = get_commit_differences(fix, project, False)
        if diffs is None:
            continue
        commit = get_short(list(diffs.keys())[0], project)
        if differences.get(commit) is not None:
            continue
        differences.update({commit: diffs})
    log_debug(project, 'Fix changes done in {0[0]} seconds', (format(time() - T)))
    if test:
        save_in_file(differences, 'test_buggy_fix_diffs.json', get_test_dir(directory))
    return list(differences.values())


def get_lines(lines):
    """
    Divide group of lines with a large range into multiple groups with smaller range.
    :param lines: Deleted lines
    :return: list of line ranges
    """
    lines_partitions = list()
    if len(lines) == 1:
        lines_str = str(lines[0]) + ',' + str(lines[0])
        lines_partitions.append(lines_str)
    else:
        if lines[len(lines) - 1] - lines[0] > 200:
            count = 0
            start = lines[0]
            for l in lines:
                if l - start > 200:
                    lines_str = str(start) + ',' + str(lines[count - 1])
                    lines_partitions.append(lines_str)
                    start = l
                count += 1
            lines_str = str(start) + ',' + str(lines[len(lines) - 1])
            lines_partitions.append(lines_str)
        else:
            lines_str = str(lines[0]) + ',' + str(lines[len(lines) - 1])
            lines_partitions.append(lines_str)
    return lines_partitions


def get_fix_inducing(fixes, project):
    """
        Get commits and line numbers of the fix-inducing changes.
        fic is a collection of { buggy commit : lines considered buggy }
        while blame_coll contains full buggy lines for troubleshooting and verification.
        ./data/<project>/buggy_changes.json file contain the commit (and the line numbers) that introduced a bug.
        For each fix, 'git blame' is run on parents for the files modified and lines deleted.
        Output of blame is parsed to indicate lines inserted in each fix-inducing commit corresponding to a fix.
    """
    if test:
        blame_coll = list()
        test_lines = list()
    fic = {} # fix inducing commits
    T = time()
    repo_dir = path.join('repos', project)
    directory = path.join('data', project)
    for fix in fixes:
        if fix is None:
            continue
        commit = list(fix.keys())[0]
        for fo in fix.get(commit):
            # Note: We may get two parents in case of a merge.
            parents = get_commit_parents(commit, '1', repo_dir)
            lines = fo['deleted'] # lines deleted in a fix
            if len(lines) == 0 or lines is None:
                continue
            line_groups = get_lines(lines)
            for lines_str in line_groups:
                line_start = int(lines_str.split(',')[0])
                for parent in parents[0].split(" "):
                    if fo['old'] is None:
                        continue
                    cmd = ['git', 'blame', '-f', '-L', lines_str, parent, '--', fo['old']]
                    completed = subprocess.run(cmd, stdout=subprocess.PIPE, universal_newlines=True, cwd=repo_dir)
                    blames = str(completed.stdout).split('\n')
                    if test:
                        new_blames = list()
                        test_l = list()
                    # save only the lines we are interested in
                    line = line_start
                    for blame in blames:
                        if line in list(lines):
                            buggy_commit = blame.strip().split(' ')[0]
                            if len(buggy_commit) < 2:
                                continue
                            if fic.get(buggy_commit) is not None:
                                if (line, fo['old']) not in fic.get(buggy_commit):
                                    fic.get(buggy_commit).append((line, fo['old']))
                            else:
                                # Note: we may have dup line numbers from different files.
                                ls = list()
                                fix_inducing = {buggy_commit: ls}
                                ls.append((line, fo['old']))
                                fic.update(fix_inducing)
                            if test:
                                new_blames.append(blame)
                                test_l.append((buggy_commit, line, fo['old']))
                        line += 1
                    if test:
                        blame_coll.append({commit : new_blames, 'lines': lines, 'file': fo['old'], "parent" : parent})
                        test_lines.append({commit : test_l})
    log_debug(project, 'Blames done in {0[0]} seconds\n', (time() - T, ))
    save_in_file(fic, 'buggy_changes.json', directory)
    if test:
        test_dir = get_test_dir(directory)
        save_in_file(blame_coll, 'test_buggy_lines.json', test_dir)
        save_in_file(test_lines, 'test_buggy_lines_dups.json', test_dir)
        log_debug(project, 'Number of buggy commits: {0[0]}.\n', (len(fic),))
    return fic


def get_commit_parents(commit, num, repo_dir):
    """
    Get parents of the specified commit.
    :param commit:
    :param num:
    :param repo_dir:
    :return: parent revisions
    """
    log_lines = subprocess.run(['git', 'log', '--pretty=format:%P', '-n', num,  commit],
                               stdout=subprocess.PIPE, universal_newlines=True,
                               cwd=repo_dir)
    parents = str(log_lines.stdout)
    parents = parents.split('\n')
    return parents


def fix_inducing_changes(project):
    if project is None:
        stderr.write('Error: Provide project name!')
    fix_differences = get_fix_changes(project)
    get_fix_inducing(fix_differences, project)


def main():
    args = argparser.parse_args()
    fix_inducing_changes(args.project)


if __name__ == '__main__':
    main()