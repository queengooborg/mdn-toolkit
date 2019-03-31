import json
import sys
import os
import webbrowser

if len(sys.argv) < 2:
	print("Not enough arguments!  Usage: python open_docs.py <feature> [browser]")
	sys.exit(1)

feature = sys.argv[1].split(".")
bcd_path = "/Users/vinyldarkscratch/Developer/git/browser-compat-data"

p = bcd_path
i = 0
while True:
	if i == len(feature):
		print("Could not find feature!")
		sys.exit(1)
	p = os.path.join(p, feature[i])
	if os.path.isfile(p+".json"):
		p += ".json"
		break
	i += 1

j = json.load(open(p, 'r'))

js = j
mdn_url = ""
for f in feature:
	js = js.get(f)
	if not js:
		print("Could not find feature!")
		sys.exit(1)
	mdn_url = js.get('__compat', {}).get("mdn_url", mdn_url)

webbrowser.get(sys.argv[2] if len(sys.argv) >= 3 else 'chrome').open(mdn_url)
