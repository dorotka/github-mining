#!/usr/bin/env python3
"""
    This file contains methods that verify the results from prepare_devs.py and combine.py.
    The author data for all the repos must be ready together with the combined data.

    Usage:
        Run the script from tools directory.
        python3 test/test_authors.py
"""
from datetime import datetime
from os import path
from helper import load_data, get_repos, load_commits
from time import time
from logger import log_info
from prepare_devs import remove_outliers
from combine import get_ratios


all = list()
all_authors = list()


def load_authors(repo):
    dir = path.join('data', repo, 'authors.json')
    return load_data(dir)


def report_results(errors, project, name):
    good = name + ' -- OK'
    bad = name + ' -- Errors: {0[0]}'
    if len(errors) == 0:
        log_info(project, good, None)
    else:
        log_info(project, bad, errors)


def test_dates():
    for project in get_repos():
        directory = path.join('data', project)
        commits = load_commits(directory)
        authors = load_authors(project)
        errors = list()
        for commit in commits:
            author = authors.get(commit['author_email'])
            if author is None:
                continue
            d = datetime.utcfromtimestamp(int(commit['time']))
            date = author.get(d.strftime('%Y/%m/%d'))
            if date is None:
                if 2018 > d.year >= 2014:
                    log_info(project, 'No such date: {0[0]} for {0[1]}. The commit timestamp: {0[2]}', (d, commit['author_email'], commit['time']))
                    errors.append(commit['commit'])
                continue
            if commit['commit'] not in [ list(x.keys())[0] for x in date.get('commits')]:
                errors.append(commit['commit'])
                log_info(project, 'No commit{0[0]} for {0[1]}', (commit['commit'], commit['time']))
        if len(errors) == 0:
            log_info(project, 'OK -- All dates correct', None)
    #todo: test that the commits grouped under specific date are indeed for that date


def test_changes_sum():
    for project in get_repos():
        authors = load_authors(project)
        errors = list()
        for author, dates in authors.items():
            for date, d in dates.items():
                if d.get('changes')[0] + d.get('changes')[1] != d.get('changes')[2]:
                    errors.append((author, date))
        report_results(errors, project, 'test_changes_sum')


def test_changes_inserted():
    for project in get_repos():
        authors = load_authors(project)
        errors = list()
        for author, dates in authors.items():
            for date, d in dates.items():
                inserted = 0
                for c in d.get('commits'):
                    for sha, files in c.items():
                        for file in files:
                            inserted += len(file.get('inserted'))
                if inserted != d.get('changes')[2]:
                    errors.append((author, list(c.keys())[0]))
        report_results(errors, project, 'test_changes_inserted')


def test_outliers_sums():
    pass
    #todo: load sums for each repo and authors, and verify that the authors were put in the right sum category -- will be only for those who were not eleminated


def test_outliers_full():
    authors = setup_data()
    project = 'test'
    remove_outliers(authors, project)
    if len(authors) != 5:
        log_info(None, 'Error: test_outliers_full. There should be 5 authors left, and there were {0[0]} instead.', (len(authors),))
    else:
        log_info(None, 'OK -- test_outliers_full', None)


def setup_data():
    authors = {
        'author1' : {
            '01/01/2014' : {
                "changes": [
                    0,
                    1,
                    1,
                    0.0
                ]
            }
        },
        'author2': {
            '02/02/2014': {
                "changes": [
                    0,
                    1,
                    1,
                    0.0
                ]
            }
        },
        'author3': {
            '03/03/2014': {
                "changes": [
                    0,
                    1,
                    1,
                    0.0
                ]
            },
            '03/04/2014': {
                "changes": [
                    0,
                    1,
                    1,
                    0.0
                ]
            }
        },
        'author4': {
            '04/04/2014': {
                "changes": [
                    0,
                    1,
                    1,
                    0.0
                ]
            },
            '04/05/2014': {
                "changes": [
                    0,
                    1,
                    1,
                    0.0
                ]
            }
        },
        'author5': {
            '05/05/2014': {
                "changes": [
                    0,
                    1,
                    1,
                    0.0
                ]
            },
            '05/06/2014': {
                "changes": [
                    0,
                    2,
                    2,
                    0.0
                ]
            }
        },
        'author6': {
            '06/06/2014': {
                "changes": [
                    0,
                    2,
                    2,
                    0.0
                ]
            },
            '06/07/2014': {
                "changes": [
                    0,
                    2,
                    2,
                    0.0
                ]
            }
        },
        'author7': {
            '07/07/2014': {
                "changes": [
                    0,
                    5,
                    5,
                    0.0
                ]
            }
        },
        'author8': {
            '08/08/2014': {
                "changes": [
                    0,
                    6,
                    6,
                    0.0
                ]
            }
        },
        'author9': {
            '09/09/2014': {
                "changes": [
                    0,
                    7,
                    7,
                    0.0
                ]
            }
        },
        'author10': {
            '10/10/2014': {
                "changes": [
                    0,
                    6,
                    6,
                    0.0
                ]
            },
            '10/11/2014': {
                "changes": [
                    0,
                    2,
                    2,
                    0.0
                ]
            },
            '10/12/2014': {
                "changes": [
                    0,
                    2,
                    2,
                    0.0
                ]
            }
        }
    }
    return authors


def setup_buggy_data():
    authors = {
        'author1' : { # ratio 4/11
            '01/01/2014' : {
                "changes": [
                    0,
                    1,
                    1,
                    0.0
                ]
            },
            '10/10/2014': {
                "changes": [
                    2,
                    4,
                    6,
                    0.0
                ]
            },
            '10/11/2014': {
                "changes": [
                    0,
                    2,
                    2,
                    0.0
                ]
            },
            '10/12/2014': {
                "changes": [
                    2,
                    0,
                    2,
                    0.0
                ]
            }
        },
        'author2': { # ratio 0
            '02/02/2014': {
                "changes": [
                    0,
                    1,
                    1,
                    0.0
                ]
            },
            '09/09/2014': {
                "changes": [
                    0,
                    7,
                    7,
                    0.0
                ]
            }
        },
        'author3': { # ratio 4/6
            '03/03/2014': {
                "changes": [
                    1,
                    0,
                    1,
                    0.0
                ]
            },
            '03/04/2014': {
                "changes": [
                    1,
                    0,
                    1,
                    0.0
                ]
            },
            '06/06/2014': {
                "changes": [
                    1,
                    1,
                    2,
                    0.0
                ]
            },
            '06/07/2014': {
                "changes": [
                    1,
                    1,
                    2,
                    0.0
                ]
            }
        },
        'author4': { # ratio 0
            '04/04/2014': {
                "changes": [
                    0,
                    0,
                    0,
                    0.0
                ]
            }
        }
    }
    return authors


def load_all():
    for project in get_repos():
        authors = load_authors(project)
        for author, data in authors.items():
            all_authors.append(author)
            all.append({author: data})



def test_combine_unique(combined):
    seen_comb = dict()
    errors = list()
    for auth in combined.keys():
        if seen_comb.get(auth) is None:
            seen_comb.update({auth : 1})
        else:
            seen_comb[auth] += 1
            errors.append(auth)
    report_results(errors, None, 'test_combine_unique')


def test_combine_count(combined):
    count = 0
    seen = list()
    errors = list()
    for author in all_authors:
        if author not in seen:
            count += 1
            seen.append(author)
    if count != len(combined):
        errors.append((count, len(combined)))
    report_results(errors, None, 'test_combine_count')


def test_combine_repeating(combined):
    """ Test the number of commits and inserted lines for the authors who repeat across repositories.
    Those authors were combined using combine.py script."""
    seen = dict()
    repeating = list()
    errors = list()
    for author_data in all:
        author = list(author_data.keys())[0]
        data = author_data.get(author)
        if author not in seen.keys():
            seen.update({author : [{author: data}]})
        else:
            repeating.append(author)
            seen.get(author).append({author: data})
    for auth in repeating:
        authors = seen.get(auth)
        dates = dict()
        dups = list()
        for a in authors:
            for date, d in a.get(auth).items():
                if dates.get(date) is None:
                    dates.update({date: [d]})
                else:
                    dups.append(date)
                    dates.get(date).append(d)
        for dup in dups:
            cc = 0 # commits count
            ic = 0 # inserted count
            combined_data = combined.get(auth).get(dup)
            if combined_data is None:
                errors.append((auth, dup, 'combined for this date is None'))
                continue
            same_dates = dates.get(dup)
            for check in same_dates:
                cc += len(check['commits'])
                ic += check['changes'][2]
            if cc != len(combined_data['commits']):
                errors.append((auth, dup, 'commits', cc, len(combined_data['commits'])))
            if ic != combined_data['changes'][2]:
                errors.append((auth, dup, 'inserted', ic, combined_data['changes'][2]))
    report_results(errors, None, 'test_combine_repeating')


def test_ratios():
    authors = setup_buggy_data()
    sorted = get_ratios(authors)
    errors = list()
    for author in sorted:
        if author['dev'] == 'author1' and author['commits']['ratio'] != (4/11):
            errors.append((author['dev'], author['commits']['ratio'], (4/11)))
        if author['dev'] == 'author2' and author['commits']['ratio'] != 0:
            errors.append((author['dev'], author['commits']['ratio'], 0))
        if author['dev'] == 'author3' and author['commits']['ratio'] != (4/6):
            errors.append((author['dev'], author['commits']['ratio'], (4/6)))
        if author['dev'] == 'author4' and author['commits']['ratio'] != 0:
            errors.append((author['dev'], author['commits']['ratio'], 0))
    report_results(errors, None, 'test_ratios')


def main():
    T1 = time()
    test_dates()
    test_changes_sum()
    test_changes_inserted()
    test_outliers_full()
    load_all()
    dir = path.join('data', 'authors_combined.json')
    combined = load_data(dir)
    test_combine_unique(combined)
    test_combine_count(combined)
    test_combine_repeating(combined)
    test_ratios()
    log_info(None, 'Tests run in {0[0]}', (time()-T1,))


if __name__ == '__main__':
    main()
