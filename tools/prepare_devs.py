#!/usr/bin/env python3
"""
    Prepares data. It groups the commits per author, per date. It removes the non-prolific developers according to the cutoff value.

    Args:
        project : Repo name

    Usage:
        python3 prepare_devs.py <project>

"""

from argparse import ArgumentParser
from os import path
from helper import save_in_file, load_commits, includes_author
from datetime import datetime
from logger import log_debug
import math

argparser = ArgumentParser()
argparser.add_argument('project',
    help='project to get commits from')

test = False
cutoff_perc = 0.35

def by_author(commits, project):
    """
    Groups data per author, per day.
    :param commits: commits annotated with good and buggy lines
    :return: data grouped by author
    """
    per_author = {}
    for commit in commits:
        # can't divide by 0
        if commit['inserted'] is 0:
            ratio = 0
        else:
            ratio = commit['buggy'] /commit['inserted']
        changes = [ commit['buggy'], commit['good'], commit['inserted'], ratio]
        assert commit['buggy'] + commit['good'] == commit['inserted']
        assert ratio >= 0
        d = datetime.utcfromtimestamp(int(commit['time'])).strftime('%Y/%m/%d')
        if datetime.utcfromtimestamp(int(commit['time'])).year < 2014 or datetime.utcfromtimestamp(int(commit['time'])).year > 2017:
            continue
        c = {d: {'commits': [{commit['commit']: commit['files']}], 'changes': changes}}
        auth = includes_author(per_author.keys(), commit['author_email'])
        if auth:
            if d in per_author.get(auth).keys():
                per_author.get(auth).get(d).get('changes')[0] += commit['buggy']
                per_author.get(auth).get(d).get('changes')[1] += commit['good']
                per_author.get(auth).get(d).get('changes')[2] += commit['inserted']
                if per_author.get(auth).get(d).get('changes')[2] is 0:
                    per_author.get(auth).get(d).get('changes')[3] = 0
                else:
                    per_author.get(auth).get(d).get('changes')[3] = per_author.get(auth).get(d).get('changes')[0]/per_author.get(auth).get(d).get('changes')[2]
                try:
                    assert per_author.get(auth).get(d).get('changes')[1] + per_author.get(auth).get(d).get('changes')[0] == per_author.get(auth).get(d).get('changes')[2]
                    assert per_author.get(auth).get(d).get('changes')[3] >= 0
                except AssertionError:
                    log_debug(project, 'AssertionError for {0[0]} in the commit {0[1]}', (auth, commit['commit']))
                per_author.get(auth).get(d).get('commits').append({commit['commit']: commit['files']})
            else:
                per_author.get(auth).update(c)
        else:
            per_author.update({commit['author_email'] : c})
    remove_outliers(per_author, project)
    log_debug(project, 'Returned {0[0]} authors.', (len(per_author),))
    return per_author


def remove_outliers(authors, project):
    """
    Removes the authors with the bottom <cutoff_perc>% of the lines.
    :param authors: dictionary of authors with day commit data
    :return: prolific authors
    """
    sums = dict()
    sum_list = list()
    for a in authors.keys():
        sum = 0
        for date, changes in authors[a].items():
            sum += changes['changes'][2]
        if sum in sums.keys():
            sums[sum].append(a)
        else:
            sums.update({sum: [a]})
    for key, value in sums.items():
        temp = [key, value]
        sum_list.append(temp)
    # bottom %
    sorted_sums = sorted(sum_list, key=lambda x: int(x[0]))
    if test == True:
        dir = path.join('data/test', project)
        save_in_file(sorted_sums, 'test_sums.json', dir)
    start = math.ceil(cutoff_perc * len(sorted_sums))
    remove = sorted_sums[0:start]
    for s in remove:
        for auth in s[1]:
            del authors[auth]
    assert sorted_sums[start + 1][0] > sorted_sums[start][0]
    info = 'Removed (line nums) {0[0]} - {0[1]}% from {0[2]} with the lowest lines: {0[3]} and cutoff: {0[4]}'
    log_debug(project, info, (len(remove), cutoff_perc, len(sorted_sums), sorted_sums[start+1][0], sorted_sums[start][0]) )


def prep_data(project):
    directory = path.join('data', project)
    commits = load_commits(directory)
    author_data = by_author(commits, project);
    save_in_file(author_data, 'authors.json', directory)


def main():
    args = argparser.parse_args()
    prep_data(args.project)


if __name__ == '__main__':
    main()
