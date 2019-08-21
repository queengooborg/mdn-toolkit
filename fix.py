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


samsunginternet = {
	True: True, False: False, None: None,
	"1": "1.0", "2": "1.0", "3": "1.0", "4": "1.0", "5": "1.0", "6": "1.0", "7": "1.0", "8": "1.0", "9": "1.0", "10": "1.0", "11": "1.0", "12": "1.0", "13": "1.0", "14": "1.0", "15": "1.0", "16": "1.0", "17": "1.0", "18": "1.0",
	"19": "1.5", "20": "1.5", "21": "1.5", "22": "1.5", "23": "1.5", "24": "1.5", "25": "1.5", "26": "1.5", "27": "1.5", "28": "1.5",
	"29": "2.0", "30": "2.0", "31": "2.0", "32": "2.0", "33": "2.0", "34": "2.0",
	"35": "3.0", "36": "3.0", "37": "3.0", "38": "3.0",
	"39": "4.0", "40": "4.0", "41": "4.0", "42": "4.0", "43": "4.0", "44": "4.0",
	"45": "5.0", "46": "5.0", "47": "5.0", "48": "5.0", "49": "5.0", "50": "5.0", "51": "5.0",
	"52": "6.0", "53": "6.0", "54": "6.0", "55": "6.0", "56": "6.0",
	"57": "7.0", "58": "7.0", "59": "7.0", "59": "7.0",
	"60": "8.0", "61": "8.0", "62": "8.0", "63": "8.0",
	"64": "9.0", "65": "9.0", "66": "9.0", "67": "9.0",
	"68": False, "69": False, "70": False, "71": False, "72": False, "73": False, "74": False, "75": False, "76": False
}

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
				new_value['version_added'] = samsunginternet.get(new_value['version_added'], new_value['version_added'])
			
			if 'version_removed' in value and new_value['version_removed'] != None:
				new_value['version_removed'] = samsunginternet.get(new_value['version_removed'], new_value['version_removed'])
			
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
			if js[root]['version_added'] in [True, None]:
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
