import os
import sys
import widlparser

prefix_list = ["", "webkit", "Webkit", "WebKit", "Moz", "moz"]

browser = 'firefox'
if len(sys.argv) > 1:
	browser = sys.argv[1]

if browser == 'firefox':
	webidl_path = "/Users/vinyldarkscratch/Developer/browsers/gecko-dev/dom/webidl"
elif browser == 'chrome':
	webidl_path = "/Users/vinyldarkscratch/Developer/browsers/chromium/src/third_party/blink"
elif browser == 'safari':
	webidl_path = "/Users/vinyldarkscratch/Developer/browsers/WebKit/Source"

data = ""
with open("%s_null.txt" %browser) as f:
	entries_to_check = [l.replace("\n", "") for l in f.readlines() if l.startswith("api.")]

def dir_walk(path):
	response = []
	for root, subdirs, files in os.walk(path):
		response += [os.path.join(root, f) for f in files if (f.endswith('.idl') or f.endswith('.webidl'))]
		for s in subdirs:
			response += dir_walk(s)
	return response

def prefixes(name):
	return [p + name for p in prefix_list]

def get_interface(name, widl):
	definitions = []
	implements = []

	for w in widl:
		if w.name in prefixes(name):
			if w.idlType == 'interface':
				definitions.append(w)
			elif w.idlType == 'implements':
				implements.append(w.implements)

	for i in implements:
		definitions += get_interface(i, widl)

	return definitions


def which_prefix(entry):
	for i in range(1, len(prefix_list)):
		if entry.name.startswith(prefix_list[i]):
			return " - Prefix: {0}".format(prefix_list[i])
	return ""

def get_runtime_flags(entry):
	for flag in entry.extendedAttributes:
		if flag.name in ['RuntimeEnabled', 'Pref']:
			return " - Flag: {0}".format(flag.attribute.value or flag.attribute.string)
	return ""

def check_entry(entry):
	e = entry.split(".")
	for w in widl:
		if w.name in prefixes(e[1]):
			if len(e) == 2:
				return "found{0}{1}".format(get_runtime_flags(w), which_prefix(w))
			elif len(e) >= 4:
				return "feature_requires_manual_review"
			elif len(e) == 3:
				if hasattr(w, 'members'):
					for d in get_interface(w.name, widl):
						for m in d.members:
							if m.name in prefixes(e[2]):
								return "found{0}{1}".format(get_runtime_flags(m), which_prefix(m))
					return "not_defined"
	return "no_idl"

files = sorted(dir_walk(webidl_path))
for fn in files:
	with open(os.path.join(webidl_path, fn), 'r') as f:
		new_data = f.read()
		data += new_data

with open("{0}.idl".format(browser), 'w') as f:
	f.write(data)

widl = widlparser.parser.Parser(data)

with open("{0}.data.txt".format(browser), 'w') as f:
	for entry in entries_to_check:
		c = check_entry(entry)
		f.write("%s - %s\n" %(entry, c))
