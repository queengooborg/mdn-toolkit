import sys
import os
import subprocess

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

# Last run on 2.0.5
master = """| browser | real values | ranged values | `true` values | `null` values |
| --- | --- | --- | --- | --- |
| total | 76.14% | 2.54% | 12.56% | 8.76% |
| chrome | 81.66% | 0.00% | 13.03% | 5.31% |
| chrome android | 76.41% | 0.00% | 18.07% | 5.52% |
| edge | 80.84% | 14.34% | 0.02% | 4.81% |
| firefox | 81.09% | 0.00% | 11.85% | 7.05% |
| ie | 81.94% | 0.00% | 7.55% | 10.51% |
| safari | 72.36% | 0.00% | 12.78% | 14.86% |
| safari ios | 68.09% | 0.00% | 15.35% | 16.56% |
| webview android | 66.76% | 5.98% | 21.84% | 5.43% |"""

os.chdir(os.path.abspath("../browser-compat-data"))
branch = str(subprocess.check_output(['npm', 'run', 'stats'])).replace("\\n", "\n")

data = {
	'before': parse(master),
	'after': parse(branch)
}

print("| browser | real values | `true` values | `null` values |")
print("| --- | --- | --- | --- |")
print("| {0} (before) | {1:.2f}% | {2:.2f}% | {3:.2f}% |".format('total', data['before']['total']['real'], data['before']['total']['true'], data['before']['total']['null']))
print("| {0} (after) | {1:.2f}% ({4:+.2f}%) | {2:.2f}% ({5:+.2f}%) | {3:.2f}% ({6:+.2f}%) |".format('total', data['after']['total']['real'], data['after']['total']['true'], data['after']['total']['null'], data['after']['total']['real']-data['before']['total']['real'], data['after']['total']['true']-data['before']['total']['true'], data['after']['total']['null']-data['before']['total']['null']))
for browser in browsers:
	print("| {0} (before) | {1:.2f}% | {2:.2f}% | {3:.2f}% |".format(browser, data['before'][browser]['real'], data['before'][browser]['true'], data['before'][browser]['null']))
	print("| {0} (after) | {1:.2f}% ({4:+.2f}%) | {2:.2f}% ({5:+.2f}%) | {3:.2f}% ({6:+.2f}%) |".format(browser, data['after'][browser]['real'], data['after'][browser]['true'], data['after'][browser]['null'], data['after'][browser]['real']-data['before'][browser]['real'], data['after'][browser]['true']-data['before'][browser]['true'], data['after'][browser]['null']-data['before'][browser]['null']))

