//
// Script to replace macros within MDN content with other text
// Useful for mass removal of macros
// Written by @queengooborg
//

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

const processMacro = (macro, args) => {
    switch (macro) {
        case 'compat':
            if (args) {
                return '{{Compat}}'
            }
            break;
    }
}

const main = async () => {
    for await (const p of walk((`${process.env.HOME}/Developer/Gooborg/MDN/translated-content/files`))) {
        // Skip non-Markdown files
        if (!(p.endsWith('.md'))) continue;

        const originalContents = await fs.readFile(p, 'utf-8');
        let contents = originalContents;
        let changed = false;

        for (const match of originalContents.matchAll(re)) {
            const macro = match.groups.macro.toLowerCase();
            const args = match.groups.args?.split(',');

            const result = processMacro(macro, args);

            if (result) {
                changed = true;
                contents = contents.replace(match[0], result);
            }
        }

        if (changed) {
            await fs.writeFile(p, contents);
        }
    }
}

await main();
