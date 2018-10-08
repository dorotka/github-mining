#!/usr/bin/env python3
"""
    Download issues for the repo.

    Args:
        u : Repo owner
        project : Repo name
        d: local directory for issues data

    Usage:
        python3 download_issues.py -u <repo_owner> <project> -d <local_directory>

"""

from argparse import ArgumentParser
from githubapi import giturlopen
from os import makedirs
from random import gauss
from sys import stderr
from time import sleep
from helper import save_in_file

import json
import link_header
import os.path
import re
import logging

logging.basicConfig(filename='github-error.log',level=logging.ERROR)

argparser = ArgumentParser()
argparser.add_argument('project',
    help='saves data in data/<project>/issues.json')
argparser.add_argument('-u',
    help='github user that owns the project')
argparser.add_argument('-d',
    help='local directory for data folder')


def download_issues(user, project):
  assert user != None
  assert project != None
  issues = []
  url = 'https://api.github.com/repos/{}/{}/issues?state=all&since=2013-01-01T00:01:00Z'.format(user, project)
  try:
    while url:
      print("Url : ", url)
      # logging.info(url)
      page = giturlopen(url)
      issues += json.loads(page.read().decode())
      headers = dict(page.getheaders())
      url = None
      if 'Link' in headers:
        for link in link_header.parse(headers['Link']).links:
          if 'rel' in link and link.rel == 'next':
            url = link.href
            sleep(max(0, gauss(1, 1/3)))
            break
  except Exception as e:
    stderr.write('E: cannot load {} because of\n  {}\n'.format(url, e))
    logging.error(e)
  return issues

def guess_project_user(project):
  pat = re.compile('git@github.com:([^/]+)/{}.git'.format(project))
  try:
    with open(os.path.join('repos', project, '.git', 'config'), 'r') as f:
      for line in f:
        m = pat.search(line)
        if m:
          return m.group(1)
  except Exception as e:
    stderr.write('E: error while trying to guess github user:\n{}\n'.format(e))
    logging.error(e)
  return None


def save_issues(owner, project, directory):
  bs = download_issues(owner, project)
  save_in_file(bs, 'issues.json', directory)


def main():
  args = argparser.parse_args()
  if args.u is None:
    args.u = guess_project_user(args.project)
  if args.u is None:
    stderr.write('E: Could not guess username. Try telling me with -u.\n')
    logging.error('E: Could not guess username.\n')
    return
  out_dir = os.path.join('data', args.project)
  if args.d is not None:
    out_dir = os.path.join(args.d, args.project)
  makedirs(out_dir, exist_ok=True)
  save_issues(args.u, args.project, out_dir)

if __name__ == '__main__':
  main()
