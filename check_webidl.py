#!/bin/python3
# -*- encoding: utf-8 -*-
#
# check_webidl.py - © 2023 @queengooborg
# Written by Queen Vinyl Da.i'gyu-Kazotetsu <https://www.queengoob.org>
# This script scans the WebIDL within web browsers' source code to determine if a feature is supported or not.
#
# Requirements:
# - Python 3.10
# - Cloned sources of Chrome, Firefox, and Safari.
#

import os
import sys
import widlparser
from pathlib import Path

prefix_list = ["", "webkit", "Webkit", "WebKit", "Moz", "moz"]

if len(sys.argv) == 1:
	print("Usage: python check_webidl.py <browser>")
	sys.exit(1)

browser = sys.argv[1]
if browser == 'firefox':
	webidl_path = "/Users/queengooborg/Developer/browsers/gecko-dev/dom/webidl"
elif browser == 'chrome':
	webidl_path = "/Users/queengooborg/Developer/browsers/chromium/src/third_party/blink"
elif browser == 'safari':
	webidl_path = "/Users/queengooborg/Developer/browsers/WebKit/Source"
else:
	print("Browser {0} unknown!".format(browser))
	sys.exit(1)

Path("generated").mkdir(exist_ok=True)

data = ""
with open("generated/{0}_null.txt".format(browser), 'r') as f:
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

with open("generated/{0}.idl".format(browser), 'w') as f:
	f.write(data)

widl = widlparser.parser.Parser(data)

with open("generated/{0}.data.txt".format(browser), 'w') as f:
	for entry in entries_to_check:
		c = check_entry(entry)
		f.write("%s - %s\n" %(entry, c))
