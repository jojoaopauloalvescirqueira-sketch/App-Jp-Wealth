'use strict';
// Exercise the public downloader with real SHA-256 and DOM/network seams.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const { webcrypto, createHash } = require('node:crypto');
const path = require('node:path');
const text = fs.readFileSync(path.join(__dirname, '../src/js/20-ui/31-tools-services.js'), 'utf8');
const start = text.indexOf('  function initLeverageDownloads(){');
const end = text.indexOf('  function initGenetrixUI(){', start);
assert(start >= 0 && end > start);
const payload = Buffer.from('independent daily archive fixture bytes');
const sha = bytes => createHash('sha256').update(bytes).digest('hex');
const entry = kind => ({ available: true, path: `downloads/jpw-alavancagem-atual/fixture-${kind}.zip`,
  filename: `fixture-${kind}.zip`, bytes: payload.length, sha256: sha(payload) });
const manifest = () => ({ schemaVersion: 1, version: '1.22.1', validation: {
  compilation: { status: 'pending', detail: 'NOT_RUN' }, terminal: { status: 'pending', detail: 'NOT_RUN' } },
  downloads: { dailySource: entry('dailySource'), source: entry('source'), compiled: entry('compiled') } });
function harness({ metadata = manifest(), bytes = payload, protocol = 'https:', embedded = {}, missingButton, duplicateKind, onFetch } = {}) {
  const downloads = [], notices = { textContent: '', dataset: {} }, metas = new Map(), buttons = {}, extraButtons = {};
  const makeButton = () => ({ disabled: false, handlers: {}, addEventListener(event, fn) { this.handlers[event] = fn; } });
  for (const kind of ['dailySource', 'source', 'compiled']) {
    if (kind === missingButton) continue;
    buttons[kind] = makeButton();
    if(kind === duplicateKind)extraButtons[kind] = makeButton();
  }
  const document = {
    querySelector(selector) { return buttons[selector.match(/download="([^"]+)"/)?.[1]] || null; },
    querySelectorAll(selector) { const kind = selector.match(/download="([^"]+)"/)?.[1];
      if(kind)return [buttons[kind],extraButtons[kind]].filter(Boolean);
      const name = selector.match(/meta="([^"]+)"/)?.[1];
      if (!metas.has(name)) metas.set(name, { textContent: '' }); return [metas.get(name)]; },
    createElement() { return { href: '', download: '', click() { downloads.push(this.download); }, remove() {} }; },
    body: { append() {} }
  };
  const context = vm.createContext({ window: { JPW_LEVERAGE_MANIFEST: metadata, JPW_LEVERAGE_FILES: embedded },
    document, el: () => notices, location: { protocol }, Uint8Array, Blob, crypto: webcrypto,
    fetch: async () => { if(onFetch)onFetch({buttons,extraButtons});
      return { ok: true, arrayBuffer: async () => Uint8Array.from(bytes).buffer }; },
    URL: { createObjectURL: () => 'blob:fixture', revokeObjectURL() {} }, setTimeout() {},
    atob: value => Buffer.from(value, 'base64').toString('binary') });
  vm.runInContext(text.slice(start, end) + '\ninitLeverageDownloads();', context);
  return { buttons, extraButtons, metas, notices, downloads,
    async click(kind, second = false) { const button = (second ? extraButtons : buttons)[kind];
      if (button?.handlers.click) await button.handlers.click(); } };
}
(async () => {
  for (const kind of ['dailySource', 'source', 'compiled']) {
    const h = harness();
    assert.equal(h.buttons[kind].disabled, false);
    await h.click(kind);
    assert.deepEqual(h.downloads, [`fixture-${kind}.zip`], `${kind} did not pass integrity verification`);
    assert.match(h.notices.textContent, /verificado/);
  }
  const repeated = harness({ duplicateKind: 'dailySource', onFetch({buttons,extraButtons}) {
    assert(buttons.dailySource.disabled && extraButtons.dailySource.disabled, 'all entries of a kind must lock during verification');
  } });
  await repeated.click('dailySource', true);
  assert.deepEqual(repeated.downloads, ['fixture-dailySource.zip'], 'second daily entry lacks a listener');
  assert(!repeated.buttons.dailySource.disabled && !repeated.extraButtons.dailySource.disabled);
  for (const [bytes, expected] of [[Buffer.concat([payload, Buffer.from('x')]), /Tamanho/],
      [Buffer.alloc(payload.length, 120), /Hash/]]) {
    const h = harness({ bytes }); await h.click('dailySource');
    assert.deepEqual(h.downloads, []); assert.match(h.notices.textContent, expected);
    assert.equal(h.notices.dataset.state, 'error');
  }
  const old = manifest(); delete old.downloads.dailySource;
  const legacy = harness({ metadata: old });
  assert.equal(legacy.buttons.dailySource.disabled, true);
  await legacy.click('dailySource'); assert.deepEqual(legacy.downloads, []);
  await legacy.click('source'); assert.deepEqual(legacy.downloads, ['fixture-source.zip']);
  for (const metadata of [null, { schemaVersion: 99 }, { ...manifest(), version: 'untrusted' }]) {
    const h = harness({ metadata });
    assert(Object.values(h.buttons).every(button => button.disabled));
    await h.click('dailySource'); assert.deepEqual(h.downloads, []);
  }
  for (const delta of [{ path: 'downloads/jpw-alavancagem-atual/../bad.zip' },
      { filename: 'wrong.zip' }, { bytes: 0 }, { bytes: Number.MAX_SAFE_INTEGER + 1 },
      { sha256: '0'.repeat(63) }, { available: false }]) {
    const metadata = manifest(); Object.assign(metadata.downloads.dailySource, delta);
    const h = harness({ metadata }); assert.equal(h.buttons.dailySource.disabled, true);
    await h.click('dailySource'); assert.deepEqual(h.downloads, []);
  }
  const embedded = { dailySource: { mime: 'application/zip', base64: payload.toString('base64') } };
  const offline = harness({ protocol: 'file:', embedded }); await offline.click('dailySource');
  assert.deepEqual(offline.downloads, ['fixture-dailySource.zip']);
  const corrupt = harness({ protocol: 'file:', embedded: { dailySource: {
    mime: 'application/zip', base64: Buffer.alloc(payload.length, 120).toString('base64') } } });
  await corrupt.click('dailySource'); assert.deepEqual(corrupt.downloads, []); assert.match(corrupt.notices.textContent, /Hash/);
  for (const embedded of [{}, { dailySource: { mime: 'text/html', base64: payload.toString('base64') } }]) {
    const h = harness({ protocol: 'file:', embedded }); assert.equal(h.buttons.dailySource.disabled, true);
  }
  harness({ missingButton: 'dailySource' });
  console.log('PASS daily/source/compiled online; daily offline; corrupt size/hash; legacy and invalid manifests; unsafe records; absent button');
})().catch(error => { console.error(error); process.exitCode = 1; });
