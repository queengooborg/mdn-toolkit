import re
import os
import sys
import subprocess

if len(sys.argv) < 2:
	print("Usage: python get_nonreal.py <folder> [browser]")
	sys.exit(0)

bcd_path = os.path.abspath("../browser-compat-data")
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
		'File': r'File.*',
		'Font': r'Font.*',
		'Gamepad': r'Gamepad.*',
		'Geometry': r'(DOM(Point|Rect).*|Geometry.*|WebKitCSSMatrix)',
		'History': r'History',
		'HTML Element': r'HTML.*',
		'IDB': r'IDB.*',
		'Location': r'Location',
		'Multimedia': r'((Local)?Media|.*Track|VTTCue).*',
		'Navigator': r'Navigator.*',
		'Node': r'(Child|Named|Parent)?Node.*',
		'Payment': r'(BasicCard|Payer|Payment).*',
		'Performance': r'Performance.*',
		'Range/Selection': r'(Range|Selection).*',
		'SVG': r'SVG.*',
		'Web Audio': r'((Audio|BaseAudio).*|.*Node(List)?)',
		'URL': r'URL.*',
		'Window': r'Window.*',
		'Worker': r'.*Worker.*',
		'XR': r'.*VR.*',
		'XML/XSLT': r'(XML|XPath|XSLT).*',
		'Event': r'.*Event.*'
	}
}

features = {}
for browser in browsers:
	result = subprocess.run(['node', 'scripts/traverse.js', browser.lower(), folder], cwd=bcd_path, stdout=subprocess.PIPE).stdout.decode('utf-8').split('\n')[0:-2]

	for f in result:
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
