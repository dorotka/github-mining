#!/usr/bin/env python3
"""
    Clones repos to the repos directory.

    Usage:
        python3 load_repos.py
"""
import subprocess
from os import path, makedirs


def load_repos():
    subprocess.run(['git', 'clone', 'https://github.com/elastic/elasticsearch.git'], stdout=subprocess.PIPE,
                   universal_newlines=True, cwd='repos')
    subprocess.run(['git', 'clone', 'https://github.com/ansible/ansible.git'], stdout=subprocess.PIPE,
                   universal_newlines=True, cwd='repos')
    subprocess.run(['git', 'clone', 'https://github.com/servo/servo.git'], stdout=subprocess.PIPE,
                   universal_newlines=True, cwd='repos')
    subprocess.run(['git', 'clone', 'https://github.com/bitcoin/bitcoin.git'], stdout=subprocess.PIPE,
                   universal_newlines=True, cwd='repos')
    subprocess.run(['git', 'clone', 'https://github.com/SeleniumHQ/selenium.git'], stdout=subprocess.PIPE,
                   universal_newlines=True, cwd='repos')
    subprocess.run(['git', 'clone', 'https://github.com/spring-projects/spring-boot.git'], stdout=subprocess.PIPE,
                   universal_newlines=True, cwd='repos')
    subprocess.run(['git', 'clone', 'https://github.com/rust-lang/rust.git'], stdout=subprocess.PIPE,
                   universal_newlines=True, cwd='repos')
    subprocess.run(['git', 'clone', 'https://github.com/Microsoft/TypeScript.git'], stdout=subprocess.PIPE,
                   universal_newlines=True, cwd='repos')
    subprocess.run(['git', 'clone', 'https://github.com/symfony/symfony.git'], stdout=subprocess.PIPE,
                   universal_newlines=True, cwd='repos')
    subprocess.run(['git', 'clone', 'https://github.com/rails/rails.git'], stdout=subprocess.PIPE,
                   universal_newlines=True, cwd='repos')

def main():
    makedirs('repos', exist_ok=True)
    load_repos()


if __name__ == '__main__':
    main()