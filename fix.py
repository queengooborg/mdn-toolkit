import json
import sys
import os

if len(sys.argv) < 2:
	print("Not enough arguments!  Usage: python set.py <feature> [browser(s)] [value]")
	sys.exit(1)

feature = sys.argv[1].split(".")
bcd_path = "/Users/vinyldarkscratch/Developer/git/browser-compat-data"
browser = ['firefox', 'firefox_android']

if len(sys.argv) >= 3:
	browser = sys.argv[2].split(",")
if len(sys.argv) >= 4:
	state = True if sys.argv[3].lower() == "true" else False if sys.argv[3].lower() == "false" else None if sys.argv[3].lower() == "null" else sys.argv[3]

p = bcd_path
i = 0
while True:
	if i == len(feature):
		print("Could not find feature %s!" %".".join(feature))
		sys.exit(1)
	p = os.path.join(p, feature[i])
	if os.path.isfile(p+".json"):
		p += ".json"
		break
	i += 1

with open(p, 'r') as f:
	j = json.load(f)

## Opera / Opera Android
# def bump_version(value):
# 	if isinstance(value, list):
# 		new_value = []
# 		for v in value:
# 			new_value.append(bump_version(v))
# 	else:
# 		new_value = dict(value)
# 		if isinstance(value['version_added'], str):
# 			new_value['version_added'] = str(max(15, int(value['version_added']) - 13))

# 		if 'version_removed' in value:
# 			if isinstance(value['version_removed'], str):
# 				new_value['version_removed'] = str(max(15, int(value['version_removed']) - 13))

# 		if 'notes' in value:
# 			new_value['notes'] = new_value['notes'].replace("Chrome", "Opera")

# 	return new_value

## Samsung Internet
# def bump_version(value):
# 	if isinstance(value, list):
# 		new_value = []
# 		for v in value:
# 			new_value.append(bump_version(v))
# 	else:
# 		new_value = dict(value)
# 		if new_value['version_added'] != None:
# 			new_value['version_added'] = bool(new_value['version_added'])
# 		if 'version_removed' in value and new_value['version_removed'] != None:
# 			new_value['version_removed'] = bool(new_value['version_removed'])
# 		if 'notes' in value:
# 			if not isinstance(new_value['notes'], list):
# 				new_value['notes'] = new_value['notes'].replace("Chrome", "Samsung Internet")

# 	return new_value

def int_or_float(string):
	try:
		return int(string)
	except:
		return float(string)

## Chrome Android / Webview
def bump_version(value):
	if isinstance(value, list):
		new_value = []
		for v in value:
			new_value.append(bump_version(v))
	if isinstance(value, dict):
		new_value = dict(value)
		if isinstance(new_value['version_added'], str):
			new_value['version_added'] = str(max(4, int_or_float(new_value['version_added'])))
		if 'version_removed' in value:
			if isinstance(new_value['version_removed'], str):
				new_value['version_removed'] = str(max(4, int_or_float(new_value['version_removed'])))
	return new_value

def set_feature(feature_path, value, js):
	root = feature_path.pop(0)
	if len(feature_path) and isinstance(js[root], dict):
		js[root] = set_feature(feature_path, value, js[root])
	else:
		if isinstance(js[root], dict):
			if js[root]['version_added'] == None:
				js[root] = bump_version(js['firefox'])
		else:
			if value != None:
				js[root] = value
	return js

for b in browser:
	try:
		fp = feature + ['__compat', 'support', b]
		j = set_feature(fp, None, j)
	except KeyError:
		pass

with open(p, 'w') as f:
	json.dump(j, f, indent=2)
	f.write("\n")
