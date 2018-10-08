#!/usr/bin/env python3
"""
    Classify the issues in ./data/<project>/issues.json and extract bugs to ./data/<project>/bugs.json.
    Issues and labeles must be extracted before this script runs.
    If test is True, then it will save ./data/<project>/test/test_bugs.json with positive and negative results for verification.

    Args:
        project : the project name

    Usage:
        python3 extract_bugs.py <project>
"""

from argparse import ArgumentParser
from helper import load_data, save_in_file, get_test_dir
from os import makedirs, path

import logging

logging.basicConfig(filename='github-error.log',level=logging.ERROR)

argparser = ArgumentParser()
argparser.add_argument('project',
                       help='classify the issues in data/<project>/issues.json')

test = False

def load_labels(d):
  file = path.join(d, 'labels.json')
  labels = load_data(file)
  return labels


def load_issues(d):
  file = path.join(d, 'issues.json')
  issues = load_data(file)
  return issues


def determine_bugs(d):
  if test:
    counter = 0
    test_bugs_positive = list()
    test_bugs_negative = list()
    test_bugs = {'positives' : test_bugs_positive, 'negatives' : test_bugs_negative }
    test_dir = get_test_dir(d)
  issues = load_issues(d)
  label_score = load_labels(d)
  bugs = list()
  for x in issues:
    score = 0
    for label in x['labels']:
      if label['name'] in label_score:
        score += label_score[label['name']]['score']
      else:
        logging.error('E: extract_bugs: unknown label {}'.format(label['name']))
    if score > 0:
      bug = {'number': x['number'],'labels' : x['labels'], 'title': x['title'], 'assignee': x['assignee'], 'state': x['state'], 'body': x['body'], 'created_at': x['created_at'], 'closed_at' : x['closed_at']}
      bugs.append(bug)
      if test:
        counter += 1
        if counter % 3 == 0 and len(test_bugs_positive) < 25:
          test_bugs_positive.append(bug)
    elif test:
        counter += 1
        if counter % 7 == 0 and len(test_bugs_negative) < 25:
          test_bugs_negative.append(x)
  if test:
    print('size of negatives:', len(test_bugs_negative))
    print('size of positives:', len(test_bugs_positive), '\n size of bugs: ', len(bugs))
    save_in_file(test_bugs, 'test_bugs.json', test_dir)
  return bugs


def save_bugs(project):
  directory = path.join('data', project)
  makedirs(directory, exist_ok=True)
  if test:
    get_test_dir(directory)
  bugs = determine_bugs(directory)
  save_in_file(bugs, 'bugs.json', directory)


def main():
  args = argparser.parse_args()
  save_bugs(args.project)


if __name__ == '__main__':
  main()
