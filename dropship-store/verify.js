/**
 * Storefront verification. Serves dist/ and drives it in a real browser.
 *
 *   NODE_PATH=/opt/node22/lib/node_modules node verify.js
 *
 * Checks the things that actually break a store: dead links, horizontal scroll
 * on a phone, tap targets too small to hit, a cart that miscounts, and a
 * checkout that pretends to work when no payment provider is connected.
 *
 * Exits non-zero if any check fails. Prints a pass/fail line for every check so
 * the report is the tool's output, not a claim about it.
 */

'use strict';

const { chromium } = require('playwright');
const http = require('http');
const fs = require('fs');
const path = require('path');

const DIST = path.join(__dirname, 'dist');
const PORT = 8347;
const MIME = { '.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript' };

const results = [];
function check(name, ok, detail) {
  results.push({ name, ok, detail: detail || '' });
  console.log(`${ok ? 'PASS' : 'FAIL'}  ${name}${detail ? '  — ' + detail : ''}`);
}

function serve() {
  return new Promise((resolve) => {
    const server = http.createServer((req, res) => {
      const clean = decodeURIComponent(req.url.split('?')[0]);
      let file = path.join(DIST, clean === '/' ? 'index.html' : clean);
      if (!file.startsWith(DIST)) { res.writeHead(403).end(); return; }
      fs.readFile(file, (err, data) => {
        if (err) { res.writeHead(404).end('not found'); return; }
        res.writeHead(200, { 'Content-Type': MIME[path.extname(file)] || 'application/octet-stream' });
        res.end(data);
      });
    });
    server.listen(PORT, () => resolve(server));
  });
}

(async () => {
  if (!fs.existsSync(DIST)) {
    console.error('dist/ not found — run: python3 build.py');
    process.exit(2);
  }

  const server = await serve();
  const base = `http://127.0.0.1:${PORT}`;
  const browser = await chromium.launch();

  try {
    // ---------------------------------------------------------- desktop pass
    const desktop = await browser.newContext({ viewport: { width: 1280, height: 900 } });
    const page = await desktop.newPage();

    const consoleErrors = [];
    page.on('pageerror', (e) => consoleErrors.push(String(e)));

    const pages = fs.readdirSync(DIST).filter((f) => f.endsWith('.html'));
    check('all expected pages built', pages.length >= 8, `${pages.length} pages: ${pages.join(', ')}`);

    // Every internal link on every page resolves.
    const broken = [];
    for (const file of pages) {
      const resp = await page.goto(`${base}/${file}`, { waitUntil: 'domcontentloaded' });
      if (!resp || resp.status() !== 200) { broken.push(`${file} -> ${resp && resp.status()}`); continue; }
      const hrefs = await page.$$eval('a[href]', (as) => as.map((a) => a.getAttribute('href')));
      for (const href of hrefs) {
        if (!href || href.startsWith('http') || href.startsWith('#') || href.startsWith('mailto:')) continue;
        const r = await page.request.get(`${base}/${href}`);
        if (r.status() !== 200) broken.push(`${file} -> ${href} (${r.status()})`);
      }
    }
    check('no broken internal links', broken.length === 0, broken.join('; ') || 'all resolve');

    // Every page has exactly one h1 and a non-empty title.
    const headingProblems = [];
    for (const file of pages) {
      await page.goto(`${base}/${file}`, { waitUntil: 'domcontentloaded' });
      const h1s = await page.$$eval('h1', (n) => n.length);
      const title = await page.title();
      if (h1s !== 1) headingProblems.push(`${file}: ${h1s} h1`);
      if (!title.trim()) headingProblems.push(`${file}: empty title`);
    }
    check('one h1 and a title on every page', headingProblems.length === 0,
      headingProblems.join('; ') || 'ok');

    // ------------------------------------------------------------ cart logic
    await page.goto(`${base}/product.html`, { waitUntil: 'domcontentloaded' });
    const shownPrice = (await page.textContent('[data-price-display]')).trim();
    await page.selectOption('[data-variant-select]', { index: 1 });
    const switchedPrice = (await page.textContent('[data-price-display]')).trim();
    check('price updates when the variant changes', shownPrice !== switchedPrice,
      `${shownPrice} -> ${switchedPrice}`);

    await page.fill('[data-qty]', '3');
    await page.click('[data-add-to-cart]');
    await page.waitForTimeout(200);
    const badgeAfterAdd = (await page.textContent('[data-cart-count]')).trim();
    check('cart badge counts quantity, not clicks', badgeAfterAdd === '3', `badge=${badgeAfterAdd}`);

    await page.goto(`${base}/cart.html`, { waitUntil: 'domcontentloaded' });
    const total = (await page.textContent('[data-cart-total]')).trim();
    const expected = '$' + (parseFloat(switchedPrice.replace(/[$,]/g, '')) * 3).toFixed(2);
    check('cart subtotal is price x quantity', total === expected, `${total} vs expected ${expected}`);

    // The single most important check: no fake checkout.
    const disabled = await page.$('[data-checkout-disabled]');
    const live = await page.$('[data-checkout]');
    check('checkout is disabled while no payment provider is configured',
      Boolean(disabled) && !live,
      disabled ? 'button disabled with an explanation' : 'a live checkout button is present');

    // Removing the last item empties the cart.
    await page.click('.link-btn');
    await page.waitForTimeout(150);
    const emptyShown = await page.isVisible('[data-cart-empty]');
    check('removing the last item empties the cart', emptyShown);

    // Missing business details are visibly marked, not silently blank.
    await page.goto(`${base}/returns.html`, { waitUntil: 'domcontentloaded' });
    const markers = await page.$$eval('mark.missing', (m) => m.length);
    check('unsupplied business details render as visible markers', markers > 0,
      `${markers} marker(s) on the returns page`);

    check('no uncaught JavaScript errors', consoleErrors.length === 0,
      consoleErrors.join('; ') || 'none');
    await desktop.close();

    // ----------------------------------------------------------- mobile pass
    const mobile = await browser.newContext({
      viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true,
      deviceScaleFactor: 3,
    });
    const mp = await mobile.newPage();

    const overflow = [];
    for (const file of pages) {
      await mp.goto(`${base}/${file}`, { waitUntil: 'domcontentloaded' });
      const over = await mp.evaluate(() =>
        document.documentElement.scrollWidth > document.documentElement.clientWidth + 1);
      if (over) overflow.push(file);
    }
    check('no horizontal scroll at 390px', overflow.length === 0,
      overflow.join(', ') || 'all pages fit');

    await mp.goto(`${base}/index.html`, { waitUntil: 'domcontentloaded' });
    const navHiddenFirst = !(await mp.isVisible('#nav a'));
    await mp.click('.nav-toggle');
    await mp.waitForTimeout(150);
    const navOpens = await mp.isVisible('#nav a');
    check('mobile menu is collapsed then opens on tap', navHiddenFirst && navOpens,
      `collapsed=${navHiddenFirst} opens=${navOpens}`);

    await mp.goto(`${base}/product.html`, { waitUntil: 'domcontentloaded' });
    const smallTargets = await mp.$$eval(
      'button, a.btn, select, input[type=number]',
      (els) => els.filter((el) => {
        const r = el.getBoundingClientRect();
        return r.height > 0 && r.height < 44;
      }).map((el) => `${el.tagName.toLowerCase()}:${Math.round(el.getBoundingClientRect().height)}px`));
    check('primary controls are at least 44px tall', smallTargets.length === 0,
      smallTargets.join(', ') || 'all meet the 44px target');

    fs.mkdirSync(path.join(__dirname, 'screenshots'), { recursive: true });
    for (const file of ['index.html', 'product.html', 'cart.html']) {
      await mp.goto(`${base}/${file}`, { waitUntil: 'domcontentloaded' });
      await mp.screenshot({
        path: path.join(__dirname, 'screenshots', `mobile-${file.replace('.html', '')}.png`),
        fullPage: true,
      });
    }
    check('mobile screenshots captured', true, 'screenshots/');
    await mobile.close();

  } finally {
    await browser.close();
    server.close();
  }

  const failed = results.filter((r) => !r.ok);
  console.log(`\n${results.length - failed.length}/${results.length} checks passed`);
  if (failed.length) {
    console.log('\nFAILED:');
    failed.forEach((f) => console.log(`  - ${f.name}: ${f.detail}`));
  }
  process.exit(failed.length ? 1 : 0);
})();
