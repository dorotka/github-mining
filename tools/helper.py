#!/usr/bin/env python3
"""
    Helper methods for the project
"""

from sys import stderr
from os import makedirs, path, listdir
from logger import log_error, log_debug
import json
import subprocess
import re
import math

test = False


def save_in_file(data, name, directory):
    """
    :param data: data to be saved
    :param name: file name with extension
    :param directory: directory to save file in
    """
    out_dir = directory
    makedirs(out_dir, exist_ok=True)
    try:
        with open(path.join(out_dir, name), 'w') as f:
            json.dump(data, f, sort_keys=True, indent=2)
    except Exception as e:
        stderr.write('E: error while trying to write the file: {}/{}\n'.format(directory, name))
        print(e)
    # logging.info('Saved file {}/{}\n'.format(directory, name))



def get_short_man(commit, project):
    limit = {
        'bitcoin': 10,
        'elasticsearch': 12
    }
    num = 11
    if limit.get(project) is not None:
        num = limit.get(project)
    short = commit[0:num]
    return short


def get_short(commit, project):
    """
    The method returns the short SHA for the commit. Number of characters vary for different repos.
    :param commit:
    :param project:
    :return: SHA
    """
    limit = {
        'bitcoin' : 10,
        'elasticsearch' : 12
    }
    repo_dir = path.join('repos', project)
    num = 11
    if limit.get(project.lower()) is not None:
        num = limit.get(project.lower())
    short_num = '--short=' + str(num)
    cmd = ['git',  'rev-parse', short_num, commit]
    completed = subprocess.run(cmd, stdout=subprocess.PIPE,
                               universal_newlines=True, cwd=repo_dir)
    short = str(completed.stdout).split('\n')[0]
    return short


def load_data(filename):
    """
    Load data from json file
    :param filename:
    :return: json data
    """
    try:
        with open(filename, mode='r') as f:
            # logging.info('Loading data from {}\n'.format(filename))
            return json.load(f)
    except Exception as e:
        stderr.write('E: cannot load {} because of\n  {}\n'.format(filename, e))
        log_error(None, '{0[0]}', e)


def get_test_dir(directory):
    test_dir = path.join(directory, 'test')
    makedirs(test_dir, exist_ok=True)
    return test_dir


def list_to_dict(list, key):
    """

    :param list:
    :param key:
    :return:
    """
    dict = {}
    for item in list:
        dict[item[key]] = item
    return dict


def load_commits(directory):
    com_dir = path.join(directory, 'commits_changes.json')
    return load_data(com_dir)


def get_repos():
    directory = 'data'
    repos = [x for x in listdir(directory) if 'text' not in x and 'test' not in x and '.' not in x and '_' not in x]
    return repos


def get_commit_differences(commit, project, ignore_merge):
    hunk_header = re.compile(r'@@ -([0-9]+)(?:,([0-9]+))? \+([0-9]+)(?:,([0-9]+))? @@')
    diff_line = re.compile(r'diff --git (?:a/(.+)|"a/([^"]+)") (?:b/(.+)|"b/([^"]+)")')

    """
    Get lines modified for the commit specified. It uses 'git show' command and parses the output to save file names and lines modified.
    :param commit:
    :param project:
    :return: the commit with the files altered and lines modified in each
    """
    repo_dir = path.join('repos', project)
    try:
        completed = subprocess.run(['git', 'show', commit], stdout=subprocess.PIPE, universal_newlines=True, encoding='utf-8', cwd=repo_dir)
    except Exception as e:
        log_error(project, 'E: get_commit_differences for {0[1]} -- {0[0]}', (e, commit))
        return None
    ls = str(completed.stdout)
    cleaned_lines = ls.replace('^M', 'hatM')
    lines = cleaned_lines.split('\n')
    state = 0
    current_diff = list()
    modified = dict()
    modified.update({commit: current_diff})
    current_old_line = None
    current_new_line = None
    old_line_todo = None
    new_line_todo = None
    errors = list()
    errs = list()
    for line in lines:
        # Note: Ignore merges not to account for the merged commit twice
        if line.startswith('Merge'):
            if ignore_merge:
                return None
            else:
                merge_commit = line.split(" ")[2]
                return get_commit_differences(merge_commit, project, False)
        if line.startswith('diff --git '):  # beginning of differences
            current_file_diff = {'inserted': [], 'deleted': []}
            current_diff.append(current_file_diff)
            # NOTE: Can't rely on '---' and '+++' because they aren't always there
            m = diff_line.match(line)  # get the file(s) modified
            if m is None:
                print('sad9f8a', line)
            current_file_diff['old'] = m.group(1) if m.group(1) else m.group(2)  # old and new file
            current_file_diff['new'] = m.group(3) if m.group(3) else m.group(4)
        elif line.startswith('rename from '):
            name = line[12:]  # if just renaming, save old file name
            if name.startswith('"') and name.endswith('"'):
                name = name[1:-1]
            current_file_diff['old'] = name
        elif line.startswith('rename to '):
            name = line[10:]
            if name.startswith('"') and name.endswith('"'):
                name = name[1:-1]
            current_file_diff['new'] = name  # new file name
        elif line.startswith('new file'):
            # NOTE: for new/deleted files, 'diff --git' repeats the name twice!
            current_file_diff['old'] = None
        elif line.startswith('deleted file'):
            current_file_diff['new'] = None
        elif line.startswith('@@ '):  # we have files - we are going to the line level
            assert 'old' in current_file_diff
            assert 'new' in current_file_diff  # we need file names
            m = hunk_header.match(line)  # get lines changed
            assert m
            current_old_line = int(m.group(1)) - 1  # subtract 1 since we add 1 before saving
            if m.group(2) is None:
                old_line_todo = 1
            else:
                old_line_todo = int(m.group(2))  # how many lines were modified in a
            current_new_line = int(m.group(3)) - 1  # b line change start
            if m.group(4) is None:
                # new file has no newline char.
                new_line_todo = 1
            else:
                new_line_todo = int(m.group(4))  # how many lines in b
            state = 1
        elif state == 1:
            if line.startswith('+'):
                current_new_line += 1
                new_line_todo -= 1
                current_file_diff['inserted'].append(current_new_line)  # each line number of inserted line
            elif line.startswith('-'):
                current_old_line += 1
                old_line_todo -= 1
                current_file_diff['deleted'].append(current_old_line)  # each line number of deleted line
            elif line.startswith(' '):  # otherwise we just go on
                current_new_line += 1
                new_line_todo -= 1
                current_old_line += 1
                old_line_todo -= 1
            else:
                if not line.startswith(r'\ No newline'):
                    #Note: Line iaccurately broken caused by different encoding that PIPE can't handle. Continue without incrementing the lines.
                    if commit not in errors and test:
                        log_debug(project, 'Newline inaccurately broken for {0[0]}. ({0[1]})', (commit, line))
                        errors.append(commit)
            try:
                assert new_line_todo >= 0
                assert old_line_todo >= 0
            except AssertionError as a:
                # revert erroneous action:
                current_new_line -= 1
                new_line_todo += 1
                current_old_line -= 1
                old_line_todo += 1
                if commit not in errs:
                    log_error(project, 'Todo lines assertion error for {0[0]}. ({0[1]}) --- {0[2]} -- {0[3]}\n', (commit, line, (new_line_todo, old_line_todo), m))
                    errs.append(commit)
            if new_line_todo == 0 and old_line_todo == 0:
                state = 0
    return modified


def includes_author(authors, auth):
    """Simple merge for emails."""
    if auth in authors:
        return auth
    e = auth.split('@')[0]
    for email in authors:
        if e == email.split('@')[0] and (email.split('@')[1] == 'gmail.com' or email.split('@')[1] == 'google.com'):
            return email
    return False


def get_log(num):
    return math.log(num, 2)