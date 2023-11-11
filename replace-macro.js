#!/bin/node

/*
 * replace-macro.js - © 2023 @queengooborg
 * Written by Queen Vinyl Da.i'gyu-Kazotetsu <https://www.queengoob.org>
 * Script to replace macros within MDN content with other text, useful for mass removal of macros
 *
 * Requirements:
 * - NodeJS
 * - mdn/content or mdn/translated-content as CWD
 */

import fs from "node:fs/promises";
import path from "node:path";

const re = /{{\s?(?<macro>\w+)\s?(?:\((?<args>(?:(?:"([^"](\\")?)*"|'([^'](\\')?)*'|[\w\d]*)(?:,\s*)?)*?)\))?\s?}}/g;

// https://gist.github.com/lovasoa/8691344
async function* walk(dir) {
	for await (const d of await fs.opendir(dir)) {
		const entry = path.join(dir, d.name);
		if (d.isDirectory()) yield* walk(entry);
		else if (d.isFile() && d.name != ".DS_Store") yield entry;
	}
}
// END SNIPPET

const parseArgs = (args) => {
	if (!args) {
		return args;
	}

	const result = [];
	for (const arg of args) {
		// Some arguments use single quotes
		if (arg.search(/'([^']*)'/g) > -1) {
			result.push(arg.substr(1, arg.length - 2));
			continue;
		}

		try {
			result.push(JSON.parse(arg));
		} catch(e) {
			result.push(arg);
		}
	}

	return result;
}

const processMacro = (macro, args) => {
	switch (macro) {
		case 'compat':
			if (args) {
				return '{{Compat}}';
			}
			break;
		case 'bug':
			return `[Firefox bug ${args[0]}](https://bugzil.la/${args[0]})`;
		case 'htmlattrdef':
			return `\`${args[0]}\``;
		case 'xref_cssvisual':
			return `{{cssxref("Media/Visual", "visual")}}`
	}
}

const main = async (macroFilter = null) => {
	for await (const p of walk((`./files`))) {
		// Skip non-Markdown files
		if (!(p.endsWith('.md'))) continue;

		const originalContents = await fs.readFile(p, 'utf-8');
		let contents = originalContents;
		let changed = false;

		for (const match of originalContents.matchAll(re)) {
			const macro = match.groups.macro.toLowerCase();
			const args = parseArgs(match.groups.args?.split(/,\s?/g));

			if (macroFilter && macro != macroFilter) {
				continue;
			}

			const result = processMacro(macro, args);

			if (result !== undefined) {
				changed = true;
				contents = contents.replace(match[0], result);
			}
		}

		if (changed) {
			await fs.writeFile(p, contents);
		}
	}
}

await main(process.argv[2]);
