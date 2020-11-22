import sys
import os
import subprocess

bcd_path = os.path.abspath("../browser-compat-data")

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

# Last run on 2.0.5
last_release = """| browser | real values | ranged values | `true` values | `null` values |
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
