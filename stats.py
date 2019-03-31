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
			'true': float(r[2][0:-1]),
			'null': float(r[3][0:-1])
		}

	return data

master = """| browser | real values | `true` values | `null` values |
| --- | --- | --- | --- |
| total | 55.87% | 22.49% | 21.64% |
| chrome | 66.15% | 24.43% | 9.42% |
| chrome android | 51.11% | 32.40% | 16.49% |
| edge | 55.70% | 20.01% | 24.30% |
| firefox | 73.89% | 13.52% | 12.59% |
| ie | 60.66% | 14.81% | 24.53% |
| safari | 49.77% | 19.16% | 31.07% |
| safari ios | 41.59% | 20.64% | 37.79% |
| webview android | 48.09% | 34.95% | 16.96% |"""

os.chdir("/Users/vinyldarkscratch/Developer/git/browser-compat-data")
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

