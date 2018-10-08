#!/usr/bin/env python3
"""
  Extract commits from the repository using 'git log' command.
  It requires local repository under ./repos/<project>/. The commits will be saves under ./data/<project>/commits.json

  Args:
      project: project to get commits from

  Usage:
      python3 extract_commits.py <project>
"""

from sys import stderr, stdout
from os import path, makedirs
from argparse import ArgumentParser
from helper import save_in_file
from logger import log_debug

import subprocess
import logging

logging.basicConfig(filename='github-error.log',level=logging.ERROR)

argparser = ArgumentParser()
argparser.add_argument('project',
    help='project to get commits from')

cmd = ['git', 'log', '--since=2014-01-01', '--until=2018-01-01', '--pretty=format:commit %H%nauthor %aE%ntime %at%nlogin %aN%n message %s%n _body %b%n end_commit']


def save_commit(cs, last_commit, last_author, last_time, message, login):
  if last_commit != None:
    if last_author == None or last_time == None or message == None or login == None:
      stderr.write('W: Data missing for {}\n'.format(last_commit))
      logging.error('W: Data missing for {}\n'.format(last_commit))
    cs.append(
          { 'commit' : last_commit
          , 'author_email' : last_author
          , 'author_login': login
          , 'time' : last_time
          , 'message' : message } )


def extract_commits_basic(project, repo):
  cs = []
  completed = subprocess.run(cmd, stdout=subprocess.PIPE, universal_newlines=True, cwd=repo)
  lines_str = str(completed.stdout)
  commits = lines_str.split('end_commit')
  for commit in commits:
      if len(commit) < 1:
        continue
      body = commit.split('_body')[1]
      lines_rest = commit.split('_body')[0]
      lines = lines_rest.split('\n\n')
      for line in lines:
        ws = line.split()
        if len(ws) < 1:
            continue
        if ws[0] == 'commit':
          message = line.split('message')[1]
          login = line.split('login')[1].split('\n')[0]
          time = line.split('time ')[1].split('\n')[0]
          save_commit(cs, ws[1], ws[3], time, message + ". " + body, login)
        else:
          log_debug(project, 'Unexpected commit line format for line {0[0]} in ws: {0[1]}', (line, ws))
         # logging.error("Unexpected commit line format for {}".format(project))
  return cs


def save_commits(project, repo, directory):
    commits = extract_commits_basic(project, repo)
    save_in_file(commits, 'commits.json', directory)


def main():
  args = argparser.parse_args()
  out_dir = path.join('data', args.project)
  makedirs(out_dir, exist_ok=True)
  repo_dir = path.join('repos', args.project)
  save_commits(args.project, repo_dir, out_dir)


if __name__ == '__main__':
  main()
