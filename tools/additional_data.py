#!/usr/bin/env python3
"""
    Get additional data on the resutls .

    Usage:
        python3 additional_data.py
"""

from helper import get_repos, load_data
from os import path
from logger import log_info
import math


def get_fixes_stats():
    no_deletes = 0
    total = 0
    total_commits = 0
    no_deletes_commits = 0
    for repo in get_repos():
        file = path.join('data', repo, 'test', 'test_buggy_fix_diffs.json')
        differences = load_data(file)
        for commit in differences.values():
            total_commits += 1
            nd = True # no delete
            for files in commit.values():
                for file in files:
                    if len(file['deleted']) == 0:
                        no_deletes += 1
                    total += 1
                    if len(file['deleted']) > 0:
                        nd = False
                        continue
            if nd:
                no_deletes_commits += 1
        log_info(repo, 'Number of fixed files with no deleted lines is {0[0]} out of {0[1]}', (no_deletes, total))
        log_info(repo, 'Number of fixes with no deleted lines is {0[0]} out of {0[1]}', (no_deletes_commits, total_commits))


def calculate(ps):
    result = 0
    for p in ps:
        result += -(p * math.log(p, 2))
    print("ps:", ps, " resutls:", result )


def main():
    # get_fixes_stats()
    ps = [1/3]
    calculate(ps)


if __name__ == '__main__':
    main()