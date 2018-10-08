#!/usr/bin/env python3
"""
    Select good and bad developers.

    Args:
        -l : Ratio limit for good devs

    Usage:
        python3 select_devs.py -l <limit>

"""
import os
import csv
from helper import save_in_file, load_data, get_repos
from logger import log_debug
from argparse import ArgumentParser

argparser = ArgumentParser()
argparser.add_argument('-l',
    help='ratio limit for good devs')

test = False


def overview():
    """
    Creates overview of all repos with data: repo, min line num, max line ratio, max daily line ratio,
    commit min, commit ratio max, devs num, devs with ratio of exactly 0.
    """
    repos = get_repos()
    overview = dict()
    for repo in repos:
        ratios_dir = os.path.join('data', repo, 'authors_line_ratio.json')
        commit_dir = os.path.join('data', repo, 'authors_commits_ratio.json')
        authors = load_data(ratios_dir)
        commits = load_data(commit_dir)
        data = [1000, 0, 0, 10, 0, 0, 0]
        for author in authors:
            if data[0] > author['commits']['sum']:
                data[0] = author['commits']['sum']
            if data[1] < author['commits']['ratio']:
                data[1] = author['commits']['ratio']
            if data[2] < author['commits']['daily_ratio']:
                data[2] = author['commits']['daily_ratio']
            c = [(x['commits']['buggy'], x['commits']['good']) for x in commits if x['dev'] == author['dev']]
            if (c[0][0] + c[0][1]) < data[3]:
                data[3] = (c[0][0] + c[0][1])
            if c[0][1] == 0:
                cr = 1
            else:
                cr = c[0][0] / c[0][1]
            if cr > data[4]:
                data[4] = cr
            data[5] += 1
            if author['commits']['ratio'] == 0:
                data[6] += 1
        log_debug(repo, data, None)
        overview.update({repo: data})


def devs_table():
    """
    Create a csv file summing up the data of each dev for each repo separately - dev email, total commits, total lines, ratio, daily ratio, commit ratio
    :return: None
    """
    repos = get_repos()
    # todo: should we do it one for all repos?
    for repo in repos:
        data = list()
        data.append(['Author', 'Line Ratio', 'Daily Line Ratio', 'Lines', 'Commit Ratio', 'Commits'])
        ratios_dir = os.path.join('data', repo, 'authors_line_ratio.json')
        commit_dir = os.path.join('data', repo, 'authors_commits_ratio.json')
        authors = load_data(ratios_dir)
        commits = load_data(commit_dir)
        for author in authors:
            d = [author['dev'], author['commits']['ratio'], author['commits']['daily_ratio'], author['commits']['sum']]
            c = [ (x['commits']['buggy'], x['commits']['good']) for x in commits if x['dev'] == author['dev'] ]
            if c[0][1] == 0:
                d.append(1)
            else:
                d.append(c[0][0]/c[0][1])
            d.append(c[0][0]+c[0][1])
            data.append(d)
        save_in_file([], 'authors.csv', os.path.join('data', repo))
        myFile = open(os.path.join('data', repo, 'authors.csv'), 'w')
        with myFile:
            writer = csv.writer(myFile)
            writer.writerows(data)
        log_debug(repo, 'done', None)


def ranges(authors):
    """
    Collect number of developers falling into each range. Upper list contains the upper limit of the range.
    :return: Ranges with number of develoeprs
    """
    upper = [[0, 0], [0.0001, 0], [0.001, 0], [0.01, 0], [0.1, 0], [0.2, 0], [0.3, 0], [0.4, 0], [1, 0]]
    sum = 0
    for author in authors:
        sum += 1
        for n in upper:
            if author['commits']['ratio'] <= n[0]:
                n[1] += 1
                break
    test_sum = 0
    for n in upper:
        test_sum += n[1]
    assert sum == test_sum
    return upper


def select(ratio_limit, authors):
    """
    Select good developers based on the supplied ratio.
    :param ratio_limit:
    :return: Developers divided into good and bad.
    """
    good = list()
    bad = list()
    sum = 0
    sum += len(authors)
    for author in authors:
        if author['commits']['ratio'] <= ratio_limit:
            good.append(author)
        else:
            bad.append(author)
    assert len(good) + len(bad) == sum
    log_debug(None, 'Good: {0[0]}, Bad: {0[1]}, Limit: {0[2]}', (len(good), len(bad), ratio_limit))
    return good, bad


def get_authors():
    ratios_dir = os.path.join('data', 'authors_ratio.json')
    return load_data(ratios_dir)


def select_devs():
    authors = get_authors()
    r = ranges(authors)
    log_debug(None, r, None)
    ratio_limit = 0
    args = argparser.parse_args()
    if args.l is not None:
        ratio_limit = float(args.l)
    good, bad = select(ratio_limit, authors)
    if test:
        save_in_file({'good': good, 'bad': bad}, 'selected_test.json', 'data/test')
    save_in_file({'good': [x['dev'] for x in good], 'bad': [x['dev'] for x in bad]}, 'selected.json', 'data')


def main():
    select_devs()


if __name__ == '__main__':
    main()