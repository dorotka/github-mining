#!/usr/bin/env python3
"""
    Script annotates each commit from commits.json with number of good and buggy lines, list of files modified and the changes.
    Results in commits_changes.json file that contains each commit with number of good and buggy lines.
    Requires: commits.json, buggy_changes.json.

    Args:
        project: project to analyze

    Usage: python3 annotate_commits.py <project>
"""


import subprocess
from argparse import ArgumentParser
from os import path
from helper import save_in_file, load_data, get_short, get_short_man, get_commit_differences
from time import time
from logger import log_debug


argparser = ArgumentParser()
argparser.add_argument('project',
    help='project to get commits from')


def load_commits(directory):
    com_dir = path.join(directory, 'commits.json')
    return load_data(com_dir)


def load_buggy(directory):
    buggy_dir = path.join(directory, 'buggy_changes.json')
    return load_data(buggy_dir)


def get_inserted_lines(commit, project):
    """
    The method returns number of inserted lines in a commit. It uses 'git show --stat' command.
    :param commit:
    :param project:
    :return: number of inserted lines
    """
    repo_dir = path.join('repos', project)
    completed = subprocess.run(['git', 'show', '--stat', commit], stdout=subprocess.PIPE, universal_newlines=True, cwd=repo_dir)
    lines = str(completed.stdout)
    lines = lines.split('\n')
    for line in lines:
        # todo: needs to deal with merges
        if 'insertions(+)' in line or 'insertion(+)' in line:
            num = 1
            if 'insertions(+)' in line:
                l = line.split('insertions(+)')[0]
                num = l.split(', ')[1]
                try:
                    num = int(num)
                except ValueError as e:
                    print('Inserted lines - not a number', commit, num, e)
                    continue
            return num
    return 0


def annotate_commits(project, commits, buggy):
    """
    The method annotates each commit with number of buggy and good inserted lines.
    :param project:
    :param commits: commits for selected time period
    :param buggy: the buggy commits with buggy lines
    :return: annotated commits
    """
    annotated = list()
    for commit in commits:
        modified = get_commit_differences(commit['commit'], project, True)
        if modified is None:
            continue
        new_commit = commit
        new_commit.update({'files': list(modified.values())[0]})
        inserted_sum = 0
        for f in new_commit.get('files'):
            inserted_sum += len(f.get('inserted'))
        new_commit.update({'inserted': inserted_sum})
        short = get_short_man(new_commit['commit'], project)
        bs = 0
        if buggy.get(new_commit['commit']) is not None:
            bs += len(buggy.get(new_commit['commit']))
        elif buggy.get(short) is not None:
            bs += len(buggy.get(short))
        new_commit.update({'buggy': bs, 'good': inserted_sum-bs})
        try:
            assert new_commit['good'] >= 0
        except AssertionError:
            log_debug(project, 'Negative line number for the {0[0]} commit - inserted: {0[1]}', (new_commit['commit'], new_commit['inserted']))
        annotated.append(new_commit)
    return annotated


def rate_developers(project):
    T = time()
    directory = path.join('data', project)
    commits = load_commits(directory)
    buggy = load_buggy(directory)
    annotated = annotate_commits(project, commits, buggy)
    log_debug(project, 'Commits annotated in {0[0]} seconds\n', (time() - T,))
    save_in_file(annotated, 'commits_changes.json', directory)


def main():
    args = argparser.parse_args()
    rate_developers(args.project)


if __name__ == '__main__':
    main()