#!/usr/bin/env python3
"""
    Requirements: data/<project>/issues.json, data/<project>/labels.json. Script must be run once.
    It runs each of the below scripts on every repository:
    extract_bugs.py
    extract_commits.py
    extract_fixes.py

    Usage:
        python3 setup_fixes.py
"""

from extract_commits import save_commits
from extract_bugs import save_bugs
from extract_fixes import extract_fixes
from helper import get_repos
from logger import log_info
import os.path


def get_data():
    for repo in get_repos():
        repo_dir = os.path.join('repos', repo)
        directory = os.path.join('data', repo)
        save_commits(repo, repo_dir, directory)
        save_bugs(repo)


def run_fixes():
    for repo in get_repos():
        directory = os.path.join('data', repo)
        extract_fixes(directory, repo)


def main():
    get_data()
    log_info(None, 'Extracting fixes...', None)
    run_fixes()


if __name__ == '__main__':
    main()
