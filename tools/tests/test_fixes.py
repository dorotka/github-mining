#!/usr/bin/env python3
"""
    This file contains methods that verify the results from extract_fixes.py

    Usage:
        Run the script from tools directory.
        python3 tests/test_fixes.py <project>
"""
import re
from os import path
from helper import save_in_file, load_data, get_repos
from logger import log_info


def report_results(errors, project, name):
    good = name + ' -- OK\n'
    bad = name + ' -- The following fixes need extra verification: {0[0]}. There are {0[1]} items to verify.\n'
    if len(errors) == 0:
        log_info(project, good, None)
    else:
        if len(errors) > 10:
            t = path.join('data', project, 'test')
            f = name + '_fixes.json'
            save_in_file(list(errors), f, t)
            show = list(errors)[:3]
            mssg = str(show) + '...... See the file for more'
            log_info(project, bad, (mssg, len(errors)))
        else:
            log_info(project, bad, (errors, len(errors)))


def test_small_bugs(project, fixes):
    verify = set()
    for fix in fixes.get('positives'):
        if int(fix[2]) < 100:
            verify.add(fix[0])
    report_results(verify, project, 'test_small_bugs')


def test_antikeywords(project, fixes):
    antikeywords = re.compile('test|merge|revert', re.IGNORECASE)
    verify = set()
    for fix in fixes.get('positives'):
        if len(antikeywords.findall(fix[1])) > 0:
            verify.add(fix[0])
    report_results(verify, project, 'test_antikeywords')


def test_fixes():
    repos = get_repos()
    for project in repos:
        dir = path.join('data', project, 'test', 'test_fixes.json')
        fixes = load_data(dir)
        test_antikeywords(project, fixes)
        test_small_bugs(project, fixes)


def main():
    test_fixes()


if __name__ == '__main__':
    main()