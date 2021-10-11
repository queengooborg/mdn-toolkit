const bcd = require('../browser-compat-data');
const { walk } = require('../browser-compat-data/utils');

const browsers = Object.keys(bcd.browsers);

const entryPoints = [
  'api',
  //'browsers',
  'css',
  'html',
  'http',
  'javascript',
  'mathml',
  'svg',
  // Not web exposed in the typical way:
  // 'webdriver', 'webextensions',
];

function main() {
  console.log(`path,deprecated,experimental,${browsers.join(',')},comments`);
  for (const { path, compat } of walk(entryPoints, bcd)) {
    const url = compat.mdn_url;
    const linkedPath = url
      ? `=HYPERLINK(${JSON.stringify(url)};${JSON.stringify(path)})`
      : `=${JSON.stringify(path)}`;
    const statuses = [compat.status.deprecated, compat.status.experimental].map(
      s => `=${String(s).toUpperCase()}`,
    );
    const links = [];
    const flatSupport = browsers
      .map(b => {
        // Determine whether or not a feature has all real values
        let ranges = compat.support[b];
        if (!ranges) {
          // If browser support isn't defined, consider non-real
          return null;
        }
        for (const range of Array.isArray(ranges) ? ranges : [ranges]) {
          if (
            [true, null, undefined].includes(range.version_added) ||
            range.version_removed === true
          ) {
            return false;
          }
        }

        return true;
      })
      .map(version => {
        return version ? '=TRUE' : '=FALSE';
      });
    let crbug = links.find(href => href.startsWith('https://crbug.com/'));
    if (crbug) {
      crbug = `=HYPERLINK(${JSON.stringify(crbug)};${JSON.stringify(
        crbug.substr(8),
      )})`;
    } else {
      crbug = '';
    }
    console.log([linkedPath, ...statuses, ...flatSupport, crbug].join(','));
  }
}

if (require.main === module) {
  main();
}
