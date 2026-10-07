// 用 MathJax 把复杂公式渲染成 SVG，再用 Chromium 截图成 PNG。
// 用法: node render.mjs <formulas.json> <输出目录>
import fs from 'fs';
import path from 'path';
import { createRequire } from 'module';
const require = createRequire(path.resolve(process.env.MJ_DIR || 'node_modules/..', 'package.json'));
const { mathjax } = require('mathjax-full/js/mathjax.js');
const { TeX } = require('mathjax-full/js/input/tex.js');
const { SVG } = require('mathjax-full/js/output/svg.js');
const { liteAdaptor } = require('mathjax-full/js/adaptors/liteAdaptor.js');
const { RegisterHTMLHandler } = require('mathjax-full/js/handlers/html.js');
const { AllPackages } = require('mathjax-full/js/input/tex/AllPackages.js');
const { chromium } = require('/opt/node22/lib/node_modules/playwright');

const [, , inFile, outDir] = process.argv;
const items = JSON.parse(fs.readFileSync(inFile, 'utf8'));
const adaptor = liteAdaptor();
RegisterHTMLHandler(adaptor);
const doc = mathjax.document('', {
  InputJax: new TeX({ packages: AllPackages.filter(p => p !== 'bussproofs') }),
  OutputJax: new SVG({ fontCache: 'local', mtextInheritFont: true }),
});
let body = '';
const meta = {};
for (const it of items) {
  const node = doc.convert(it.tex, { display: it.display, em: 16, ex: 8, containerWidth: 1000 });
  const svg = adaptor.firstChild(node);
  const style = adaptor.getAttribute(svg, 'style') || '';
  meta[it.id] = { width: adaptor.getAttribute(svg, 'width'), height: adaptor.getAttribute(svg, 'height'), style };
  body += `<div class="f"><span id="${it.id}" style="display:inline-block;padding:2px 3px;background:#fff">${adaptor.outerHTML(svg)}</span></div>\n`;
}
const page = `<html><head><meta charset="utf-8"><style>body{margin:0;font-size:16px;font-family:"WenQuanYi Zen Hei",serif;background:#fff} .f{margin:6px}</style></head><body>${body}</body></html>`;
fs.mkdirSync(outDir, { recursive: true });
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
const pg = await browser.newPage({ deviceScaleFactor: 3, viewport: { width: 1400, height: 900 } });
await pg.setContent(page);
for (const it of items) {
  await pg.locator('#' + it.id).screenshot({ path: path.join(outDir, it.id + '.png'), omitBackground: false });
}
await browser.close();
fs.writeFileSync(path.join(outDir, 'meta.json'), JSON.stringify(meta));
console.log('rendered', items.length);
