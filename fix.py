import json
import sys
import os

if len(sys.argv) < 2:
	print("Not enough arguments!  Usage: python set.py <feature> [browser(s)] [value]")
	sys.exit(1)

feature = sys.argv[1].split(".")
bcd_path = "/Users/vinyldarkscratch/Developer/git/browser-compat-data"
browser = ['edge', 'edge_mobile']

if len(sys.argv) >= 3:
	browser = sys.argv[2].split(",")

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

def int_or_float(string):
	try:
		return int(string)
	except:
		return float(string)

def create_webview_range(value):
	if value < 37: return "≤37"
	return str(value)

def bump_version(value, browser):
	if isinstance(value, list):
		new_value = []
		for v in value:
			new_value.append(bump_version(v, browser))
	else:
		new_value = dict(value)

		if browser == 'chrome_android':
			if isinstance(new_value['version_added'], str):
				new_value['version_added'] = str(max(15, int_or_float(new_value['version_added'])))

			if 'version_removed' in value:
				if isinstance(new_value['version_removed'], str):
					new_value['version_removed'] = str(max(15, int_or_float(new_value['version_removed'])))

		elif browser == 'edge':
			if 'version_removed' in value and new_value['version_removed'] != None:
				new_value['version_removed'] = False
			elif new_value['version_added'] != None:
				new_value['version_added'] = '12' if bool(new_value['version_added']) else None
			
			if 'notes' in value:
				if not isinstance(new_value['notes'], list):
					new_value['notes'] = new_value['notes'].replace("Internet Explorer", "Edge")

		elif browser == 'firefox_android':
			if isinstance(new_value['version_added'], str):
				new_value['version_added'] = str(max(4, int_or_float(new_value['version_added'])))
			
			if 'version_removed' in value:
				if isinstance(new_value['version_removed'], str):
					new_value['version_removed'] = str(max(4, int_or_float(new_value['version_removed'])))

		elif browser == 'opera':
			if isinstance(value['version_added'], str):
				new_value['version_added'] = str(max(15, int(value['version_added']) - 13))
			
			if 'version_removed' in value:
				if isinstance(value['version_removed'], str):
					new_value['version_removed'] = str(max(15, int(value['version_removed']) - 13))
			
			if 'notes' in value:
				new_value['notes'] = new_value['notes'].replace("Chrome", "Opera")
		
		elif browser == 'opera_android':
			if isinstance(value['version_added'], str):
				new_value['version_added'] = str(max(15, int(value['version_added']) - 13))
			
			if 'version_removed' in value:
				if isinstance(value['version_removed'], str):
					new_value['version_removed'] = str(max(15, int(value['version_removed']) - 13))
			
			if 'notes' in value:
				new_value['notes'] = new_value['notes'].replace("Chrome", "Opera")
		
		elif browser == 'samsunginternet_android':
			if new_value['version_added'] != None:
				new_value['version_added'] = bool(new_value['version_added'])
			
			if 'version_removed' in value and new_value['version_removed'] != None:
				new_value['version_removed'] = bool(new_value['version_removed'])
			
			if 'notes' in value:
				if not isinstance(new_value['notes'], list):
					new_value['notes'] = new_value['notes'].replace("Chrome", "Samsung Internet")
		
		elif browser == 'webview_android':
			if isinstance(new_value['version_added'], str):
				new_value['version_added'] = create_webview_range(int_or_float(new_value['version_added']))
			
			if 'version_removed' in value:
				if isinstance(new_value['version_removed'], str):
					new_value['version_removed'] = create_webview_range(int_or_float(new_value['version_removed']))
			
			if 'notes' in value:
				new_value['notes'] = new_value['notes'].replace("Chrome", "WebView")

	return new_value

def set_feature(feature_path, value, js, browser):
	root = feature_path.pop(0)
	if len(feature_path) and isinstance(js[root], dict):
		js[root] = set_feature(feature_path, value, js[root], browser)
	else:
		if isinstance(js[root], dict):
			if js[root]['version_added'] == None:
				if browser in ['chrome_android', 'opera', 'opera_android', 'samsunginternet_android', 'webview_android']:
					source_browser = 'chrome'
				elif browser == 'firefox_android':
					source_browser = 'firefox'
				elif browser == 'edge':
					source_browser = 'ie'
				elif browser == 'safari_ios':
					source_browser = 'safari'
				js[root] = bump_version(js[source_browser], browser)
		else:
			if value != None:
				js[root] = value
	return js

for b in browser:
	try:
		fp = feature + ['__compat', 'support', b]
		j = set_feature(fp, None, j, b)
	except KeyError:
		pass

with open(p, 'w') as f:
	json.dump(j, f, indent=2)
	f.write("\n")
