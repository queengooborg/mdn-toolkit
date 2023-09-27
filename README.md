# Vinyl's MDN Toolkit

This is a collection of scripts that I use as a part of my workflow while contributing to MDN Web Docs projects, such as [browser-compat-data](https://github.com/mdn/browser-compat-data) and [MDN content](https://github.com/mdn/content).  While they are not particularly written for public use, the scripts should work just fine with a few folder path tweaks.

## Requirements
- Python 3.x
- NodeJS v10+

## Setup
```
npm i
pip install -r requirements.txt
```

## Scripts for BCD

Requirements:
- [MDN Web Docs' Browser Compat Data](https://github.com/mdn/browser-compat-data) locally cloned (for modifications)

### check_webidl.py
This script is a part of an attempt to set true/false values based upon implementation in a browser's WebIDL.  This was discontinued as there is far too much ambiguity in the WebIDL, though the script was retained for archival purposes.

#### Requirements
- Cloned sources of Chrome, Firefox, and Safari.

#### Usage
```sh
python check_webidl.py <browser>
```

### compare_stats.py
This script calculates the statistics difference between the latest BCD release and the current `HEAD` of the local clone.

#### Usage
```sh
python compare_stats.py [browser]
```

#### Caveats
Currently, the latest BCD release stats must be manually calculated.

### get_nonreal.py
This script iterates through the values of BCD to find any non-real values (`true` or `null` values), and calculates an HTML-formatted, categorized list of entries.

#### Usage
```sh
python get_nonreal.py <folder> [browser]
```

#### Usage
```sh
python set.py <feature> [browser1,browser2...] [value]
```

### open_docs.py
This script takes a feature identifier and opens its MDN web docs page in the specified browser (defaults to Chrome).  If the feature identifier doesn't have an `mdn_url` specified, it will get the parent's instead.

#### Usage
```sh
python open_docs.py <feature> [browser]
```

### set.py
This script is a command-line to quickly set a feature to a specific value.

#### Usage
```sh
python set.py <feature> [browser1,browser2...] [value]
```

### walk-csv.js
[Description pending...]

#### Usage
```sh
node walk-csv.js
```

## Scripts for MDN Content

Requirements:
- [MDN Web Docs' Content](https://github.com/mdn/content) and/or [Translated Content](https://github.com/mdn/translated-content) locally cloned (for modifications)

### mdn-content-check_file_age.py
This script checks to see how long ago a file has been modified for content and assigns a corresponding color to its age.  This is designed to check the age of files in the https://github.com/mdn/content or https://github.com/mdn/translated-content repositories.

#### Usage
```sh
cd path/to/mdn/[translated-]content/repo
python mdn-content-check_file_age.py
```
