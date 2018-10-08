#!/usr/bin/env python3
"""
    The script combines authors from different repositories and gets the ratios.
    Some authors appear across the repositories, they are combined based on the email.

    Usage:
        python3 combine.py
"""
import os
from helper import save_in_file, load_data, get_repos
from logger import log_debug, log_error
from functools import reduce
from time import time


def combine():
    T = time()
    combines = dict()
    for repo in get_repos():
        dir = os.path.join('data', repo, 'authors.json')
        authors = load_data(dir)
        for author in authors.keys():
            if combines.get(author) is None:
                combines.update({author: authors.get(author)})
            else:
                for date in authors.get(author).keys():
                    if combines.get(author).get(date) is None:
                        combines.get(author).update({date: authors.get(author).get(date)})
                    else:
                        combines.get(author).get(date)['commits'].extend(authors.get(author).get(date)['commits'])
                        combines.get(author).get(date)['changes'][0] += authors.get(author).get(date)['changes'][0] # buggy
                        combines.get(author).get(date)['changes'][1] += authors.get(author).get(date)['changes'][1] # good
                        combines.get(author).get(date)['changes'][2] += authors.get(author).get(date)['changes'][2] # inserted
                        # ratio
                        if combines.get(author).get(date)['changes'][2] == 0:
                            combines.get(author).get(date)['changes'][3] = 0
                        else:
                            combines.get(author).get(date)['changes'][3] = combines.get(author).get(date)['changes'][0] / combines.get(author).get(date)['changes'][1]
    log_debug(None, 'Combined authors in {0[0]}s. There are {0[1]} authors.', (time()-T, len(combines)))
    return combines


def obj_to_sorted_list(obj, key_name, value_name, sort_attr):
    l = list()
    for key in obj.keys():
        l.append({key_name : key, value_name : obj[key]})
    sorted_list = sorted(l, key=lambda x: x[value_name][sort_attr])
    return sorted_list


def get_ratios(per_author):
    """
    Computes ratios for developers
    :param per_author:
    :return: authors sorted by line_ratio asc
    """
    authors = {}
    for author in per_author.keys():
        dates = per_author[author]
        daily_ratio_counter = 1
        daily_ratios = list()
        for date, commit in dates.items():
            auth = author in authors.keys()
            if auth:
                authors[author]['buggy'] += commit['changes'][0]
                authors[author]['good'] += commit['changes'][1]
                authors[author]['sum'] += commit['changes'][2]
                daily_ratio_counter += 1
                daily_ratios.append(commit['changes'][3])
                if authors[author]['sum'] is 0:
                    ratio = 0
                else:
                    ratio = authors[author]['buggy'] / authors[author]['sum']
                authors[author]['ratio'] = ratio
            else:
                if commit['changes'][2] is 0:
                    ratio = 0
                else:
                    ratio = commit['changes'][0] / commit['changes'][2]
                daily_ratios.append(commit['changes'][3])
                c = {'buggy': commit['changes'][0], 'good': commit['changes'][1], 'sum': commit['changes'][2], 'daily_ratio': commit['changes'][3], 'ratio' : ratio}
                authors.update({author: c})
        daily_ratio_product = reduce(lambda x, y: x*y, daily_ratios)
        daily_ratio = daily_ratio_product**(1/daily_ratio_counter) # geometric mean
        authors[author]['daily_ratio'] = daily_ratio
        try:
            assert authors[author]['buggy'] + authors[author]['good'] == authors[author]['sum']
            assert authors[author]['ratio'] >= 0
        except AssertionError:
            log_error(None, 'E: get_ratios - AssertionError for {0[0]}', (author,))
    authors_sorted = obj_to_sorted_list(authors, 'dev', 'commits', 'ratio')
    return authors_sorted


def combine_authors():
    combined = combine()
    save_in_file(combined, 'authors_combined.json', 'data')
    authors = get_ratios(combined)
    save_in_file(authors, 'authors_ratio.json', 'data')


def main():
    combine_authors()


if __name__ == '__main__':
    main()