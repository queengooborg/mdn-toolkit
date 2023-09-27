#!/bin/python3
# -*- encoding: utf-8 -*-
#
# mdn-content-check_file_age.py - © 2023 @queengooborg
# Written by Queen Vinyl Da.i'gyu-Kazotetsu <https://www.queengoob.org>
# This script checks to see how long ago a file has been modified for content and assigns a corresponding color to its age.  This is designed to check the age of files in the https://github.com/mdn/content repository.
#
# Requirements:
# - Python 3.10
# - pip install tqdm
# - CWD must be a local checkout of mdn/content@github
#

from datetime import datetime, timedelta, timezone
from pathlib import Path
import os.path
import multiprocessing
import re
import subprocess

import tqdm

MDN_CONTENT_ROOT = Path.cwd()
MDN_CONTENT_PATH = MDN_CONTENT_ROOT / 'files'

NOW = datetime.now(timezone.utc)

def re_search(regex, string, group=0, default_value=None, cast=str):
	search = re.search(regex, string)
	if not search:
		return default_value
	try:
		return cast(search.group(group))
	except IndexError:
		# The group doesn't exist; return the default value
		return default_value

def get_commit_details(commit_hash, filepath):
	details = {
		'hash': commit_hash,
		'date': None,
		'converted_to_markdown': False,
		'files_changed': 0,
		'global_changes': {
			'insertions': 0,
			'deletions': 0,
			'total': 0
		},
		'file_changes': {
			'insertions': 0,
			'deletions': 0,
			'total': 0
		},
	}

	raw_details = subprocess.run(
		['git', 'show', commit_hash, '--stat'],
		cwd=MDN_CONTENT_ROOT,
		capture_output=True
	).stdout.decode('utf-8')

	# Get commit date
	date = re_search(r"Date:\s+([\w\d \-\+:]+)\n", raw_details, 1)
	details['date'] = datetime.strptime(date, '%c %z')
	details['files_changed'] = re_search(r"(\d+) files? changed", raw_details, 1, 0, int)

	details['global_changes']['insertions'] = re_search(r"(\d+) insertions?\(\+\)", raw_details, 1, 0, int)
	details['global_changes']['deletions'] = re_search(r"(\d+) deletions?\(-\)", raw_details, 1, 0, int)
	details['global_changes']['total'] = details['global_changes']['insertions'] + details['global_changes']['deletions']

	if re.search(os.path.dirname(filepath) + r"/{index\.html => index\.md}", raw_details):
		details['converted_to_markdown'] = True

	raw_file_details = subprocess.run(
		['git', 'show', commit_hash, '--stat', filepath],
		cwd=MDN_CONTENT_ROOT,
		capture_output=True
	).stdout.decode('utf-8')

	# Get change counts
	details['file_changes']['insertions'] = re_search(r"(\d+) insertions?\(\+\)", raw_file_details, 1, 0, int)
	details['file_changes']['deletions'] = re_search(r"(\d+) deletions?\(-\)", raw_file_details, 1, 0, int)
	details['file_changes']['total'] = details['file_changes']['insertions'] + details['file_changes']['deletions']

	return details

def get_significant_commit(filepath):
	# Get the file's Git history
	commit_list = subprocess.run(
		['git', 'rev-list', 'HEAD', '--', filepath],
		cwd=MDN_CONTENT_ROOT,
		capture_output=True
	).stdout.decode('utf-8').rstrip().split('\n')

	for commit_hash in commit_list:
		commit = get_commit_details(commit_hash, filepath)

		if commit['converted_to_markdown']:
			# There have been no changes since Markdown conversion
			return None
		if commit['files_changed'] > 25:
			# XXX Bump to 50 if "_redirects.txt" modified
			# It's probably a mass formatting change, ignore commit
			continue
		if commit['file_changes']['total'] < 1:
			# It's a typo fix or other small change, ignore commit
			continue
		# If only codeblocks are modified:
			# It's probably a mass formatting change
			# Ignore this commit

		# The commit is probably a significant, non-formatting change at this point
		return commit

	# There probably have been no content updates since Markdown conversion
	return None

def check_file_age(filepath):
	commit = get_significant_commit(filepath)

	# Return a hue between Green and Red, following the age:
		# Green - modified within the last three months
		# Lime - modified within the last six months
		# Yellow - modified within the last nine months
		# Orange - modified within the last year
		# Red - modified over a year ago
		# Black - not modified since Markdown conversion

	if not commit:
		return ["Black", "undefined"]

	if commit['date'] >= NOW - timedelta(days=30*3):
		return ["Green", commit['hash']]
	if commit['date'] >= NOW - timedelta(days=30*6):
		return ["Lime", commit['hash']]
	if commit['date'] >= NOW - timedelta(days=30*9):
		return ["Yellow", commit['hash']]
	if commit['date'] >= NOW - timedelta(days=30*12):
		return ["Orange", commit['hash']]
	return ["Red", commit['hash']]

def get_file_details(file):
	filepath = os.path.relpath(file, start=MDN_CONTENT_ROOT)
	age, commit = check_file_age(filepath)
	return filepath + ',' + age + ',' + commit

def main():
	files = sorted(MDN_CONTENT_PATH.rglob('*.md'))
	result = []

	with multiprocessing.Pool(multiprocessing.cpu_count()) as pool:
		for details in tqdm.tqdm(pool.imap_unordered(get_file_details, files), total=len(files), leave=False):
			result.append(details)

	print('File,Age,Commit')
	print('\n'.join(result))

if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		print('Keyboard interrupt detected! Closing.')
