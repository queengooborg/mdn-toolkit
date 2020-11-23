# Vinyl's BCD Toolkit

This is a collection of scripts that I use to aid in the workflow of my [BCD](https://github.com/mdn/browser-compat-data) contributions.  While they are not particularly written for public use, the scripts should work just fine with a few folder path tweaks.

## Requirements
- Python 3.x
- NodeJS v10+
- [MDN web docs' Browser Compat Data](https://github.com/mdn/browser-compat-data) locally cloned (for modifications)

## Setup
```
npm i
pip install -r requirements.txt
```

## Scripts

### check_webidl.py
This script is a part of an attempt to set true/false values based upon implementation in a browser's WebIDL.  This was discontinued as there is far too much ambiguity in the WebIDL, though the script was retained for archival purposes

#### Requirements
- Cloned sources of Chrome, Firefox, and Safari.

#### Usage
```
python check_webidl.py <browser>
```

### get_nonreal.py
This script iterates through the values of BCD to find any non-real values (`true` or `null` values), and calculates an HTML-formatted, categorized list of entries.

#### Usage
```
python get_nonreal.py <folder> [browser]
```

### open_docs.py
This script takes a feature identifier and opens its MDN web docs page in the specified browser (defaults to Chrome).  If the feature identifier doesn't have an `mdn_url` specified, it will get the parent's instead.

#### Usage
```
python open_docs.py <feature> [browser]
```

### set.py
This script is a command-line to quickly set a feature to a specific value.

#### Usage
```
python set.py <feature> [browser1,browser2...] [value]
```

### stats.py
This script calculates the statistics difference between the latest BCD release and the current `HEAD` of the local clone.

#### Usage
```
python stats.py [browser]
```

#### Caveats
Currently, the latest BCD release stats must be manually calculated.
