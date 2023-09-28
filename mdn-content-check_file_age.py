#!/bin/python3
# -*- encoding: utf-8 -*-
#
# mdn-content-check_file_age.py - © 2023 @queengooborg
# Written by Queen Vinyl Da.i'gyu-Kazotetsu <https://www.queengoob.org>
# This script checks to see how long ago a file has been modified for content and assigns a corresponding color to its age.  This is designed to check the age of files in the https://github.com/mdn/content or https://github.com/mdn/translated-content repositories.
#
# Requirements:
# - Python 3.10
# - pip install tqdm
# - CWD must be a local checkout of mdn/content@github or mdn/translated-content@github
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

NOW = datetime.now()

def safe_int(string, default=0):
	try:
		return int(string)
	except ValueError:
		return default

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
		['git', 'show', commit_hash, '--format=%at', '--numstat'],
		cwd=MDN_CONTENT_ROOT,
		capture_output=True
	).stdout.decode('utf-8').split('\n')

	# Get commit date
	details['date'] = datetime.fromtimestamp(int(raw_details[0]))

	files_changed = raw_details[2:-1]

	for f in files_changed:
		insertions, deletions, filename = f.split('\t')

		details['files_changed'] += 1

		details['global_changes']['insertions'] += safe_int(insertions)
		details['global_changes']['deletions'] += safe_int(deletions)

		if filename == filepath:
			# Set file-specific change counts
			details['file_changes']['insertions'] = safe_int(insertions)
			details['file_changes']['deletions'] = safe_int(deletions)
			details['file_changes']['total'] = details['file_changes']['insertions'] + details['file_changes']['deletions']

			# Check if the target file was renamed to Markdown
			if filename == os.path.dirname(filepath) + "/{index.html => index.md}":
				details['converted_to_markdown'] = True

	details['global_changes']['total'] = details['global_changes']['insertions'] + details['global_changes']['deletions']

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

def check_file_age(commit):
	# Return a hue between Green-Red or Black, following the age:
		# Green - modified within the last three months
		# Lime - modified within the last six months
		# Yellow - modified within the last nine months
		# Orange - modified within the last year
		# Red - modified over a year ago
		# Black - not modified since Markdown conversion

	if not commit:
		return "Black"

	if commit['date'] >= NOW - timedelta(days=30*3):
		return "Green"
	if commit['date'] >= NOW - timedelta(days=30*6):
		return "Lime"
	if commit['date'] >= NOW - timedelta(days=30*9):
		return "Yellow"
	if commit['date'] >= NOW - timedelta(days=30*12):
		return "Orange"
	return "Red"

def get_file_details(file):
	filepath = os.path.relpath(file, start=MDN_CONTENT_ROOT)
	commit = get_significant_commit(filepath)
	age = check_file_age(commit)
	return [filepath, age, commit]

def main():
	files = sorted(MDN_CONTENT_PATH.rglob('*.md'))
	result = []

	with multiprocessing.Pool(multiprocessing.cpu_count()) as pool:
		for details in tqdm.tqdm(pool.imap_unordered(get_file_details, files), total=len(files), leave=False):
			result.append(details)

	print('File,Age,Commit')
	for r in sorted(result, key=lambda x: x[0]):
		print(','.join(r))

if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		print('Keyboard interrupt detected! Closing.')
