import sys
import subprocess

if len(sys.argv) < 2:
	print("Usage: python get_nonreal.py <folder>")
	sys.exit(0)

bcd_path = "/Users/vinyldarkscratch/Developer/Gooborg/browser-compat-data"
browsers = ['Chrome', 'Edge', 'Firefox', 'IE', 'Opera', 'Safari']
folder = sys.argv[1]
print_browsers = False

features = {}

for browser in browsers:
	result = subprocess.run(['node', 'scripts/traverse.js', browser.lower(), folder], cwd=bcd_path, stdout=subprocess.PIPE).stdout.decode('utf-8').split('\n')[0:-2]

	for f in result:
		feature = f.split(" (")[0]
		if feature in features:
			if browser not in features[feature]:
				features[feature].append(browser)
		else:
			features[feature] = [browser]

for feature in sorted(features.keys()):
	print(feature)

	if print_browsers:
		for b in features[feature]:
			print("\t- {0}".format(b))
