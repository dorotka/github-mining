#!/usr/bin/env python3
"""
    Download labels for the repo. Labels will be saves in ./data/<project>/labels.json

    Args:
        u : Repo owner
        project : Project name

    Usage:
        python3 labels.py -u <repo_user> <project>

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
    help='saves data in data/<project>/labels.json')
argparser.add_argument('-u',
    help='github user that owns the project')


def download_labels(user, project):
  assert user != None
  assert project != None
  labels = []
  url = 'https://api.github.com/repos/{}/{}/labels'.format(user, project)
  try:
    while url:
      page = giturlopen(url)
      labels += json.loads(page.read().decode())
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
  return labels


def rate_labels(labels, project):
  rated = {}
  for label in labels:
    new_label = {label["name"]: {"score" : 0} }
    bug_confident_regex = re.compile(r'(.*?)(bug|defect)(.*?)')
    bug_regex = re.compile(r'(.*?)(critical|needsfix|release-blocker|issues|good-first-patch|errors|with[- \t]reproduction[- \t]steps)(.*?)')
    not_bug_regex = re.compile(r'(.*?)(enhancement|feature|question|proposal|documentation|docs)(.*?)')
    # exceptions
    if project == 'selenium':
      bug_regex = re.compile(
        r'(.*?)(critical|needsfix|release-blocker|issues|good-first-patch|errors|with[- \t]reproduction[- \t]steps|d-)(.*?)')
    if project == 'servo':
      bug_regex = re.compile(
        r'(.*?)(critical|needsfix|release-blocker|issues|good-first-patch|errors|with[- \t]reproduction[- \t]steps|wrong|crash|perf-slow)(.*?)')
      not_bug_regex = re.compile(r'(.*?)(enhancement|feature|question|proposal|documentation|docs|not-a-bug)(.*?)')

    if bug_regex.match(label["name"].lower()):
      new_label[label["name"]]["score"] += 2
    if not_bug_regex.match(label["name"].lower()):
      new_label[label["name"]]["score"] -= 4
    if bug_confident_regex.match(label["name"].lower()):
      new_label[label["name"]]["score"] += 4
    rated.update(new_label)
  return rated


def get_labels(owner, project, directory):
  labels = download_labels(owner, project)
  rated = rate_labels(labels, project)
  save_in_file(rated, 'labels.json', directory)


def main():
  args = argparser.parse_args()
  if args.u is None:
    stderr.write('E: Tell me the owner with with -u.\n')
    return
  out_dir = os.path.join('data', args.project)
  makedirs(out_dir, exist_ok=True)
  get_labels(args.u, args.project, out_dir)


if __name__ == '__main__':
  main()
