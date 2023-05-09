#!/bin/python3

#
# bcd-auto-pr.py - © 2023 @queengooborg
# This script is deigned to make creating PRs for BCD changes much, much easier. Originally
# written in bash, this has been ported to Python for easier maintenance over time.
#
# Requirements:
# - Python 3.10
#   - inquirer package
# - CWD must be a local checkout of mdn/browser-compat-data@github
#   - Assumes that the 'origin' remote is the remote to push branches to
# - Assumes a local checkout of GooborgStudios/mdn-bcd-collector@github is present at
#   ../mdn-bcd-collector
#

import os.path
import json
from pathlib import Path
import subprocess
from itertools import chain

import inquirer

# --- Config ---

with open(Path(__file__).parent / '../mdn-bcd-collector/package.json', 'r') as package_file:
	collector_version = json.load(package_file).get('version', '')

mdn_bcd_collector = "[mdn-bcd-collector](https://mdn-bcd-collector.gooborg.com) project (v{0})".format(collector_version)
collector_guide_link = "_Check out the [collector's guide on how to review this PR](https://github.com/GooborgStudios/mdn-bcd-collector/blob/main/docs/reviewing-bcd-changes.md)._"

# Titles and descriptions for each type of PR and their specific parameters
pr_types = {
	"Corrections": {
		"title": "Update {browser} data for {title}",
		"description": "This PR updates and corrects version values for {browser_full} for the {feature_description}.",
		"branch_suffix": "corrections"
	},
	"New Entry": {
		"title": "Add missing features for {title}",
		"description": {
			"parts_of_feature": "This PR is a part of a project to add missing interfaces and interface features to BCD that are from an active spec (including WICG specs) and is supported in at least one browser. This particular PR adds the missing features of the {feature_description}.",
			"entire_feature": "This PR is a part of a project to add missing interfaces and interface features to BCD that are from an active spec (including WICG specs) and is supported in at least one browser. This particular PR adds the missing {feature_description}."
		},
		"branch_suffix": "additions"
	},
	"Real Values Additions": {
		"title": "Add {browser} versions for {title}",
		"description": "This PR replaces `true`/`null` values with exact version numbers (or `false`) for {browser_full} for the {feature_description}.",
		"branch_suffix": "real-values"
	},
	"Feature Removal": {
		"title": "Remove {title} from BCD",
		"description": "This PR removes the {feature_description} from BCD.",
		"reasons": {
			"Irrelevant": f"Per the [data guidelines](https://github.com/mdn/browser-compat-data/blob/main/docs/data-guidelines/index.md#removal-of-irrelevant-features), this feature can be considered irrelevant and may be removed from BCD accordingly. Even if the current data suggests that the feature is supported, lack of support has been confirmed by the {mdn_bcd_collector}.",
			"Non-Interface": "This feature is a type (ex. a dictionary, enum, mixin, constant or WebIDL typedef) that we have explicitly stated not to document separately from the feature(s) that depend on it, as they are virtually invisible to the end developer."
		},
		"branch_suffix": "removal"
	},
	"Flag Removal": {
		"by_flag": {
			"title": "Remove irrelevant `{flag}` flag in {browser}",
			"description": "This PR removes irrelevant flag data for the `{flag}` flag of {browser_full} as per the corresponding [data guidelines](https://github.com/mdn/browser-compat-data/blob/main/docs/data-guidelines/index.md#removal-of-irrelevant-flag-data). This PR was created from results of the `remove-redundant-flags` script."
		},
		"by_feature": {
			"title": "Remove irrelevant {browser} flag data for {title}",
			"description": "This PR removes irrelevant flag data for {browser_full} for the {feature_description} as per the corresponding [data guidelines](https://github.com/mdn/browser-compat-data/blob/main/docs/data-guidelines/index.md#removal-of-irrelevant-flag-data). This PR was created from results of the `remove-redundant-flags` script."
		},
		"branch_suffix": "flag-removal"
	},
}

# Details on where the data comes from
data_sources = {
	"mdn-bcd-collector": {
		"description": f"The data comes from the {mdn_bcd_collector}.\n\n_Check out the [collector's guide on how to review this PR](https://github.com/GooborgStudios/mdn-bcd-collector#reviewing-bcd-changes)._",
		"source": "Tests Used: {source}"
	},
	"Manual": {
		"description": "The data comes from manual testing, running test code through BrowserStack, SauceLabs and custom VMs.",
		"source": "Test Code: \n```\n{source}\n```"
	},
	"Commit": {
		"description": "The data comes from a commit in the browser's source code, mapped to a version number using available tooling or via the commit timestamp.",
		"source": "Commit: {source}"
	},
	"Bug": {
		"description": "The data comes from a bug in the web browser's bug tracker.",
		"source": "Bug: {source}"
	}
}

# More specific categories should always come after less specific ones
categories = {
	"api": { "title": "API", "label": "data:api :rabbit2:" },
	"css.at-rules": { "title": "CSS at-rule", "label": "data:css :art:" },
	"css.selectors": { "title": "CSS selector", "label": "data:css :art:" },
	"css.types": { "title": "CSS value type", "label": "data:css :art:" },
	"css.properties": { "title": "CSS property", "label": "data:css :art:" },
	"html": { "title": "HTML feature", "label": "data:html :page_facing_up:" },
	"html.elements": { "title": "HTML element", "label": "data:html :page_facing_up:" },
	"html.manifest": { "title": "HTML manifest property", "label": "data:html :page_facing_up:" },
	"http": { "title": "HTTP feature", "label": "data:http :mountain_cableway:" },
	"http.headers": { "title": "HTTP header", "label": "data:http :mountain_cableway:" },
	"javascript": { "title": "JavaScript feature", "label": "data:js :pager:" },
	"javascript.builtins": { "title": "JavaScript builtin", "label": "data:js :pager:" },
	"javascript.operators": { "title": "JavaScript operator", "label": "data:js :pager:" },
	"mathml": { "title": "MathML feature", "label": "data:mathml :heavy_division_sign:" },
	"mathml.elements": { "title": "MathML element", "label": "data:mathml :heavy_division_sign:" },
	"svg.attributes": { "title": "SVG attribute", "label": "data:svg :paintbrush:" },
	"svg.elements": { "title": "SVG element", "label": "data:svg :paintbrush:" },
	"webdriver.commands": { "title": "Web Driver command", "label": "data:webdriver :racing_car:" },
	"webextensions": { "title": "Web Extensions feature", "label": "data:webext :game_die:" },
	"webextensions.api": { "title": "Web Extensions interface", "label": "data:webext :game_die:" },
	"webextensions.manifest": { "title": "Web Extensions manifest property", "label": "data:webext :game_die:" },
}

# All applicable web browsers
browsers = {
	"chrome": {
		"name": "Chromium",
		"long_name": "Chromium (Chrome, Opera, Samsung Internet, WebView Android)",
	},
	"edge": {
		"name": "Edge",
		"long_name": "Microsoft Edge",
	},
	"firefox": {
		"name": "Firefox",
		"long_name": "Firefox and Firefox Android",
	},
	"opera": {
		"name": "Opera",
		"long_name": "Opera and Opera Android",
	},
	"safari": {
		"name": "Safari",
		"long_name": "Safari (Desktop and iOS/iPadOS)",
	},
	"safariios": {
		"name": "Safari iOS",
		"long_name": "Safari iOS/iPadOS",
	},
	"webkit": {
		"name": "Chrome/Safari",
		"long_name": "Chrome and Safari",
	},
	"webview": {
		"name": "WebView",
		"long_name": "WebView Android",
	},
	"nodejs": {
		"name": "NodeJS",
		"long_name": "NodeJS",
	},
	"fenix": {
		"name": "Firefox Android",
		"long_name": "Firefox Android"
	},
	"samsung": {
		"name": "Samsung Internet",
		"long_name": "Samsung Internet"
	},
	"all": {
		"name": "all browsers",
		"long_name": "all browsers"
	},
}

# --- Helper Functions ---

def get_category(feature):
	cat = None
	for key, value in categories.items():
		if feature.startswith(key):
			# We don't return yet as there may be a more specific match
			cat = {"key": key, **value}
	return cat

def _get_subfeature(feature, category):
	subfeature = feature.replace(category['key'] + '.', '')
	subfeature_parts = subfeature.split('.')
	if len(subfeature_parts) == 1:
		return [subfeature_parts[0], ""]
	return [subfeature_parts[0], ".".join(subfeature_parts[1:])]

def get_feature_description(feature, category):
	subfeature = _get_subfeature(feature, category)
	if subfeature[1]:
		return f"`{subfeature[1]}` member of the `{subfeature[0]}` {category['title']}".format(subfeature=subfeature, category=category)
	return f"`{subfeature[0]}` {category['title']}".format(subfeature=subfeature, category=category)

def get_feature_title(feature, category):
	subfeature = _get_subfeature(feature, category)
	if subfeature[1]:
		return feature
	return f"{subfeature[0]} {category['title']}".format(subfeature=subfeature, category=category)

def get_branch_name(config):
	if config['flag_removal_type'] == 'By Flag':
		return f"flagremoval/{config['flag']}/{config['browser']['id']}"

	branch_name = f"{config['feature'].replace('.', '/').replace('*', '')}"
	branch_suffix = pr_types[config['pr_type']].get('branch_suffix')
	browser_id = config['browser']['id']

	if browser_id:
		if branch_suffix:
			return f"{branch_name}/{browser_id}-{branch_suffix}"
		return f"{branch_name}/{browser_id}"
	if branch_suffix:
		return f"{branch_name}/{branch_suffix}"
	return branch_name

def get_collector_test_url(feature):
	base_url = "https://mdn-bcd-collector.gooborg.com/tests/"
	slug = feature.replace('.', '/')
	return base_url + slug.replace('/worker_support', '?exposure=Worker')

def _find_feature_in_file(feature, file_path):
	parts = feature.split('.')
	with open(file_path, 'r') as file:
		obj = json.load(file)

	for part in parts:
		obj = obj.get(part)
		if not obj:
			return False

	return True

def find_file_by_feature(feature, skip_file_search = False):
	parts = feature.split('.')
	cwd = Path('.')

	for part in parts:
		dir_path = cwd / part
		json_path = cwd / (part+".json")

		if os.path.exists(json_path):
			# In some cases, we should just return the first possible match
			if skip_file_search:
				return json_path

			# If the .json exists, check if the feature is present
			found = _find_feature_in_file(feature, json_path)
			if found:
				return json_path
			# If it isn't, we'll check for a matching directory
		
		if os.path.exists(dir_path):
			# A matching directory exists, continue search in that directory
			cwd = dir_path
			continue
		else:
			# Neither a .json nor folder was found, assume feature not present
			# XXX Handle special cases, such as _globals folder
			return False

	# We have gone through all parts of the feature and did not find a matching file or folder
	return False

def non_empty(_, current):
	if len(current) < 1:
		raise inquirer.errors.ValidationError('', reason="Field cannot be blank.")
	return True

def run_command(description, command, silent=True):
	print(description)
	output = subprocess.run(command, capture_output=silent)
	if output.returncode != 0:
		raise Exception(output.stderr)

def flatten(l):
	return [item for sublist in l for item in sublist]

# --- Main Script ---

def get_description(config):
	title = pr_types[config['pr_type']].get('title', '')
	description = pr_types[config['pr_type']].get('description', '')

	if config['pr_type'] == 'New Entry':
		untracked_files = subprocess.run(
			['git', 'ls-files', '--other', '--exclude-standard'],
			capture_output=True
		).stdout.decode('utf-8')
		file_untracked = str(config['file']) in untracked_files
		description = pr_types['New Entry']['description']['entire_feature' if file_untracked else 'parts_of_feature']
	elif config['pr_type'] == 'Feature Removal':
		description += " " + pr_types['Feature Removal']['reasons'].get(
			config['feature_removal_reason'], config['feature_removal_reason']
		)
	elif config['pr_type'] == 'Flag Removal':
		title = pr_types['Flag Removal'][config['flag_removal_type']]['title']
		description = pr_types['Flag Removal'][config['flag_removal_type']]['description']

	if config['source']['type']:
		source_data = data_sources.get(config['source']['type'], None)
		if source_data:
			if config['pr_type'] != 'Feature Removal':
				description += " " + source_data['description']
			description += "\n\n" + source_data['source'].format(source=config['source']['data'])
		else:
			description += " " + config['source']['type']

	fmt = dict(config)
	del fmt['browser']

	title = title.format(**fmt, browser=config['browser']['name'], browser_full=config['browser']['long_name'])
	description = description.format(**fmt, browser=config['browser']['name'], browser_full=config['browser']['long_name'])

	if config['additional_notes']:
		description += "\n\nAdditional Notes: " + config['additional_notes']

	return title + '\n\n' + description

def get_config():
	config = {
		"pr_type": "",
		"feature": "",
		"category": "",
		"file": "",
		"branch": "",
		"labels": [],
		"description": "",

		"browser": {
			"id": "",
			"name": "",
			"long_name": ""
		},
		"source": {
			"type": "",
			"data": ""
		},
		"content_update": False,
		"additional_notes": "",
		"auto_stage": False,

		"flag_removal_type": "",
		"flag": "",

		"feature_removal_reason": ""
	}

	# Get PR type
	config['pr_type'] = inquirer.list_input(
		"What type of pull request should this be?",
		choices=pr_types.keys()
	)

	# Get details for flag removal type
	if config['pr_type'] == 'Flag Removal':
		config['flag_removal_type'] = inquirer.list_input(
			"Is removal by the flag, or by the feature?",
			choices=["By Flag", "By Feature"]    
		)

	# Get flag or feature name
	if config['pr_type'] == 'Flag Removal' and config['flag_removal_type'] == 'By Flag':
		config['flag'] = inquirer.text("Flag Name")
		config['file'] = None
	else:
		config['feature'] = inquirer.text("Feature Identifier", validate=non_empty)
		config['category'] = get_category(config['feature'])
		config['file'] = find_file_by_feature(config['feature'], config['pr_type'] == 'Feature Removal')
		config['feature_description'] = get_feature_description(config['feature'], config['category'])
		config['title'] = get_feature_title(config['feature'], config['category'])

	# Get supporting information
	if config['pr_type'] == 'Feature Removal':
		config['feature_removal_reason'] = inquirer.list_input(
			"Why is this feature being removed?",
			choices=list(pr_types['Feature Removal']['reasons'].keys()),
			other=True
		)

		# The source for confirming feature removal is always the collector
		# Non-interface removal doesn't have a source; it is its own source
		if config['feature_removal_reason'] != 'Non-Interface':
			config['source']['type'] = 'mdn-bcd-collector'
			config['source']['data'] = get_collector_test_url(config['feature'])

		config['content_update'] = inquirer.confirm("Is an mdn/content update required?", default=True)
		if config['content_update']:
			config['labels'].append('needs content update 📝')
	elif config['pr_type'] != 'Flag Removal':
		if config['pr_type'] != 'New Entry':
			config['browser'] = inquirer.list_input(
				'What browser is updated in this PR?',
				choices=[(v['name'], {"id": k, **v}) for k, v in browsers.items()]
			)

		source = inquirer.list_input(
			"Where does this data come from?",
			choices=list(data_sources.keys()),
			other=True
		)

		if source not in data_sources.keys():
			config['source']['type'] = "Other"
			config['source']['data'] = source
		else:
			config['source']['type'] = source

			if source == "mdn-bcd-collector":
				config['source']['data'] = get_collector_test_url(config['feature'])
			elif source == "Manual":
				config['source']['data'] = inquirer.text('Test Code')
			elif source == "Commit":
				config['source']['data'] = inquirer.text('Link to Commit(s)')
			elif source == "Bug":
				config['source']['data'] = inquirer.text('Bug Link(s)')

	if config['category']:
		config['labels'].append(config['category']['label'])

	# Get additional notes
	config['additional_notes'] = inquirer.text('Is there anything else you want to add?')

	# Ask if file should be automatically staged
	if config['file']:
		config['auto_stage'] = inquirer.confirm(f"Should {config['file']} be staged?", default=True)

	config['description'] = get_description(config)
	config['branch'] = get_branch_name(config)

	return config

def do_lint(config):
	if not config['file']:
		return

	# Run the fix command first
	fix_run = subprocess.run(["npm", "run", "fix", config["file"]])

	# Recursively run linting
	do_lint = True
	while do_lint:
		lint_run = subprocess.run(["npm", "run", "lint", config["file"]])
		if lint_run.returncode == 0:
			# If no errors were detected, proceed
			do_lint = False
		else:
			print("")
			print("Linting errors detected! Please fix them.")
			# If errors were detected, allow for user skipping
			do_lint = inquirer.confirm('Do you want to try linting again?', default=True)

def do_pr(config):
	action = "normal"
	branch_exists = {
		"local": subprocess.run(['git', 'rev-parse', '--verify', config['branch']], capture_output=True).returncode == 0,
		"remote": subprocess.run(['git', 'ls-remote', '--exit-code', '--heads', 'origin', config['branch']], capture_output=True).returncode == 0
	}

	# XXX Remove me once force pushing and branch deletion is supported
	if branch_exists['local'] or branch_exists['remote']:
		print(f"This branch exists either locally or upstream!  You will need to delete the branch first before proceeding.")
		return

	if branch_exists['remote']:
		pr_exists = False # XXX Not working
		# pr_exists = subprocess.run(['gh', 'pr', 'view', config['branch']], capture_output=True)
		if pr_exists:
			action = inquirer.list_input(
				'A PR exists for this branch!',
				choices=[
					('Cancel', "cancel"),
					('Force push to existing PR', 'force-pr'),
					('Delete upstream branch and continue', 'delete')
				]
			)
		else:
			action = inquirer.list_input(
				'This branch exists upstream!',
				choices=[
					('Cancel', "cancel"),
					('Force push and continue', 'force-continue'),
					('Delete upstream branch and continue', 'delete')
				]
			)
	elif branch_exists['local']:
		action = inquirer.list_input(
			'This branch exists locally!',
			choices=[
				('Cancel', "cancel"),
				('Force push and continue', 'force-continue'),
				('Delete branch and continue', 'delete')
			]
		)

	if action == "cancel":
		print("PR creation cancelled.")
		return
	if action == 'delete':
		# XXX Delete upstream branch and continue
		pass
	if action.startswith('force-'):
		# XXX Force push branch
		if action == 'force-pr':
			print("Force pushed!")
			return

	current_branch = subprocess.run(['git', 'branch', '--show-current'], capture_output=True).stdout.decode("utf-8").replace('\n', '')

	run_command("Creating branch...", ['git', 'branch', config['branch']])
	run_command("Checking out branch...", ['git', 'checkout', config['branch']])
	
	# Stage files if needed
	if config['auto_stage']:
		run_command(f"Staging {config['file']}...", ['git', 'add', config['file']])

	# Create commit and pull request
	run_command("Creating commit...", ['git', 'commit'] + flatten([
		['-m', line] for line in config['description'].split('\n')
	]))
	run_command("Pushing branch...", ['git', 'push', '--set-upstream', 'origin', config['branch']])
	run_command("Creating PR...", ['gh', 'pr', 'create', '--fill'] + flatten([['-l', label] for label in config['labels']]))

	# Reset
	if not config['auto_stage']:
		run_command("Stashing other changes...", ['git', 'stash'])
	
	run_command("Switching back to original branch...", ['git', 'checkout', current_branch])
	run_command("Deleting new branch...", ['git', 'branch', '-d', config['branch']])

	if not config['auto_stage']:
		stashes = subprocess.run(['git', 'stash', 'list'], capture_output=True).stdout.decode('utf-8').rstrip().split('\n')
		if stashes[0]: # If there's a stash, pop it
			run_command("Popping stash...", ['git', 'stash', 'pop'])
			run_command("Resetting state...", ['git', 'reset'])

	print("Complete!")

def main():
	config = get_config()

	do_lint(config)
	print("")
	do_pr(config)

if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		print("Keyboard interrupt!  Exiting.")
