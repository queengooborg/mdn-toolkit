#!/bin/python3
# -*- encoding: utf-8 -*-
#
# compare_stats.py - © 2023 @queengooborg
# Written by Queen Vinyl Da.i'gyu-Kazotetsu <https://www.queengoob.org>
# This script calculates the statistics difference between the latest BCD release and the current `HEAD` of the local clone.
#
# Requirements:
# - Python 3.10
# - CWD must be a local checkout of mdn/browser-compat-data@github
#

from pathlib import Path
import sys
import os
import subprocess

bcd_path = Path.cwd()

browsers = ['chrome', 'chrome android', 'edge', 'firefox', 'ie', 'safari', 'safari ios', 'webview android']
if len(sys.argv) >= 2:
	if sys.argv[1] == 'chrome':
		browsers = ['chrome', 'chrome android', 'webview android']
	elif sys.argv[1] == 'firefox':
		browsers = ['firefox']
	elif sys.argv[1] == 'safari':
		browsers = ['safari', 'safari ios']

def parse(string):
	rows = [r[2:-2].split(" | ") for r in string.split("\n") if r.startswith("| ") and not (r.startswith("| browser") or r.startswith("| ---"))]

	data = {}
	for r in rows:
		data[r[0]] = {
			'real': float(r[1][0:-1]),
			'ranged': float(r[2][0:-1]),
			'true': float(r[3][0:-1]),
			'null': float(r[4][0:-1])
		}

	return data

def compare(browser, before, after):
	diff = {
		'real': after['real']-before['real'],
		'ranged': after['ranged']-before['ranged'],
		'true': after['true']-before['true'],
		'null': after['null']-before['null']
	}
	print("| {0} (before) | {1[real]:.2f}% | {1[ranged]:.2f}% | {1[true]:.2f}% | {1[null]:.2f}% |".format(browser, before))
	print("| {0} (after) | {1[real]:.2f}% **({2[real]:+.2f}%)** | {1[ranged]:.2f}% **({2[ranged]:+.2f}%)** | {1[true]:.2f}% **({2[true]:+.2f}%)** | {1[null]:.2f}% **({2[null]:+.2f}%)** |".format(browser, after, diff))

# Last run on 2.0.7
last_release = """| browser | real values | ranged values | `true` values | `null` values |
| --- | --- | --- | --- | --- |
| total | 77.05% | 2.97% | 11.72% | 8.25% |
| chrome | 81.68% | 0.00% | 13.01% | 5.31% |
| chrome android | 76.44% | 0.00% | 18.05% | 5.50% |
| edge | 80.96% | 14.22% | 0.03% | 4.79% |
| firefox | 82.50% | 0.00% | 10.60% | 6.89% |
| ie | 81.97% | 0.00% | 7.51% | 10.51% |
| safari | 74.58% | 1.84% | 10.58% | 13.01% |
| safari ios | 71.53% | 1.75% | 12.16% | 14.57% |
| webview android | 66.76% | 5.99% | 21.83% | 5.43% |"""

os.chdir(bcd_path)
branch = str(subprocess.check_output(['npm', 'run', 'stats'])).replace("\\n", "\n")

data = {
	'before': parse(last_release),
	'after': parse(branch)
}

print("| browser | real values | ranged values | `true` values | `null` values |")
print("| --- | --- | --- | --- | --- |")
compare('total', data['before']['total'], data['after']['total'])
for browser in browsers:
	compare(browser, data['before'][browser], data['after'][browser])
