#!/usr/bin/env python3
"""
    Get good and bad developers

    Usage:
        python3 get_devs.py

"""

from prepare_devs import prep_data
from combine import combine_authors
from select_devs import select_devs
from helper import get_repos


def get_authors():
    for repo in get_repos():
        prep_data(repo)


def main():
   get_authors()
   combine_authors()
   select_devs()


if __name__ == '__main__':
    main()
