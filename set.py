#!/bin/python3
# -*- encoding: utf-8 -*-
#
# set.py - © 2023 @queengooborg
# Written by Queen Vinyl Da.i'gyu-Kazotetsu <https://www.queengoob.org>
# This script sets a value for a specified BCD feature and browser.
#
# Requirements:
# - Python 3.10
# - CWD must be a local checkout of mdn/browser-compat-data@github
#

from pathlib import Path
import json
import sys
import os

if len(sys.argv) < 2:
    print("Usage: python set.py <feature> [browser1,browser2...] [value]")
    sys.exit(1)

feature = sys.argv[1].split(".")
bcd_path = Path.cwd()
state = True
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

def set_feature(feature_path, value, js):
    root = feature_path.pop(0)
    if len(feature_path) and isinstance(js[root], dict):
        js[root] = set_feature(feature_path, value, js[root])
    else:
        if (value is True and js[root] == None) or value is False or isinstance(value, str):
            js[root] = value
    return js

for b in browser:
    try:
        fp = feature + ['__compat', 'support', b, 'version_added']
        j = set_feature(fp, state, j)
    except KeyError:
        pass

with open(p, 'w') as f:
    json.dump(j, f, indent=2, ensure_ascii=False)
    f.write("\n")
