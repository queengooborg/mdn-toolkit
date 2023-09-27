#!/bin/python3
# -*- encoding: utf-8 -*-
#
# get_nonreal.py - © 2023 @queengooborg
# Written by Queen Vinyl Da.i'gyu-Kazotetsu <https://www.queengoob.org>
# This script iterates through the values of BCD to find any non-real values (`true` or `null` values), and calculates an HTML-formatted, categorized list of entries.
#
# Requirements:
# - Python 3.10
# - CWD must be a local checkout of mdn/browser-compat-data@github
#

from pathlib import Path
import re
import os
import sys
import subprocess

if len(sys.argv) < 2:
	print("Usage: python get_nonreal.py <folder> [browser]")
	sys.exit(0)

bcd_path = Path.cwd()
browsers = [sys.argv[2]] if len(sys.argv) > 2 else ['Chrome', 'Edge', 'Firefox', 'IE', 'Safari']
folder = sys.argv[1]

# The script will pick the first matching category in the following order
categories = {
	'api': {
		'RTC': r'RTC.*',
		'Authentication': r'.*Credential.*',
		'Canvas/WebGL': r'(Canvas|Paint|WebGL|(ANGLE|OES|WEBGL)_).*',
		'Console': r'Console',
		'CSS': r'(CSS|Media(List|Query)|StyleSheet).*',
		'Document/Shadow Root': r'(Document|ShadowRoot).*',
		'DOM': r'DOM(Error|Exception|Implementation|String|Token).*',
		'Element': r'Element',
		'Fetch': r'(Fetch.*|Request|Response)',
		'File': r'File.*',
		'Font': r'Font.*',
		'Gamepad': r'Gamepad.*',
		'Geolocation': r'Geolocation.*',
		'Geometry': r'(DOM(Point|Rect).*|Geometry.*|WebKitCSSMatrix)',
		'History': r'History',
		'HTML Element': r'HTML.*',
		'IDB': r'IDB.*',
		'Location': r'Location',
		'Multimedia': r'((Local)?Media|.*Track|VTTCue).*',
		'Navigator': r'Navigator.*',
		'Notification': r'Notification.*',
		'Node': r'(Child|Named|Parent)?Node.*',
		'Payment': r'(BasicCard|Payer|Payment).*',
		'Performance': r'Performance.*',
		'Permissions': r'Permissions.*',
		'Range/Selection': r'(Range|Selection).*',
		'SVG': r'SVG.*',
		'Touch': r'Touch.*',
		'Web Audio': r'((Audio|BaseAudio|OfflineAudio|MIDI).*|.*Node(List)?)',
		'URL': r'URL.*',
		'Window/Screen': r'(Window|Screen).*',
		'Worker': r'.*Worker.*',
		'XR': r'.*VR.*',
		'XML/XSLT': r'(XML|XPath|XSLT).*',
		'Event': r'.*Event.*'
	}
}

features = {}
for browser in browsers:
	result = subprocess.run(['node', 'scripts/traverse.js', browser.replace(' ', '').lower(), folder], cwd=bcd_path, stdout=subprocess.PIPE).stdout.decode('utf-8').split('\n')[0:-1]

	count = int(result[-1])

	if count < 1:
		continue

	for f in result[0:-1]:
		feature = f.split(" (")[0]
		feature_parts = feature.split('.')
		category = "zzzzz Misc."

		if feature_parts[0] in categories:
			for cat, regex in categories[feature_parts[0]].items():
				if re.match(regex, feature_parts[1]):
					category = cat
					break

		if category not in features:
			features[category] = {}

		if feature in features[category]:
			if browser not in features[category][feature]:
				features[category][feature].append(browser)
		else:
			features[category][feature] = [browser]

for category in sorted(features.keys()):
	print("<details>\n<summary>{0}</summary>".format(
		category.replace("zzzzz ", "")
	))

	for feature in sorted(features[category].keys()):
		print("{0} - {1}<br />".format(
			feature, ", ".join(features[category][feature])
		))

	print("</details>\n")
