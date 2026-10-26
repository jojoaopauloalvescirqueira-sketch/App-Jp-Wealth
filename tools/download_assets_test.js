'use strict';
// Behavioral contract for lazy, integrity-checked public download assets.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const { webcrypto, createHash } = require('node:crypto');
const loaderPath = path.join(__dirname, '../src/js/00-core/10-download-assets.js');
const bytes = Buffer.from('synthetic shared archive bytes\n');
const hash = value => createHash('sha256').update(value).digest('hex');
const resourceId = 'leverage/source', payloadId = 'leverage-fixture';
const buildId = 'fixture-build-001';
const envelope = delta => ({ schemaVersion: 1, buildId, id: payloadId,
  files: { [resourceId]: bytes.toString('base64') }, ...delta });
function harness({ protocol = 'https:', inline, fetchBytes = bytes, rejectFetch = false, cryptoOverride } = {}) {
  const calls = { fetch: 0, decode: 0, scripts: [], timers: [] };
  const descriptor = { path: 'downloads/leverage/fixture.zip', filename: 'fixture.zip',
    mime: 'application/zip', bytes: bytes.length, sha256: hash(bytes), payload: payloadId };
  const manifest = { schemaVersion: 1, buildId, resources: { [resourceId]: descriptor },
    payloads: { [payloadId]: { path: 'src/vendor/downloads/leverage-fixture-payload.js', elementId: 'jpw-download-payload-leverage-fixture' } } };
  const document = { currentScript: null,
    getElementById(id) { return inline && id === manifest.payloads[payloadId].elementId ?
      { type: 'application/json', textContent: JSON.stringify(inline) } : null; },
    createElement() { return { dataset: {}, remove() {} }; },
    head: { appendChild(script) { calls.scripts.push(script); }, append(script) { calls.scripts.push(script); } } };
  const window = { JPW_BUILD_ID: buildId, JPW_DOWNLOAD_MANIFEST: manifest };
  // The official bootstrap exposes a classic lexical constant, not a window property.

  const context = vm.createContext({ window, document, location: { protocol }, crypto: cryptoOverride||webcrypto,
    Uint8Array, ArrayBuffer, TextDecoder, AbortController, DOMException, URL,
    atob(value) { calls.decode++; return Buffer.from(value, 'base64').toString('binary'); },
    fetch: async () => { calls.fetch++; if(rejectFetch)throw new Error('offline');
      return { ok: true, arrayBuffer: async () => Uint8Array.from(fetchBytes).buffer }; },
    setTimeout(fn, delay) { const timer = { fn, delay }; calls.timers.push(timer); return timer; },
    clearTimeout() {}, console });
  vm.runInContext(`const JP_WEALTH_BUILD_ID = ${JSON.stringify(buildId)};`, context);
  if(fs.existsSync(loaderPath))vm.runInContext(fs.readFileSync(loaderPath, 'utf8'), context);
  const api = window.JPWDownloadAssets;
  return { api, calls, manifest, document,
    register(value, script = calls.scripts.at(-1)) { document.currentScript = script; try { return api.register(payloadId, value); } finally { document.currentScript = null; } } };
}
const cases = [];
function test(name, run) { cases.push({name, run}); }
function apiOf(h) {
  assert(h.api && typeof h.api.getBytes === 'function' && typeof h.api.getText === 'function' && typeof h.api.register === 'function',
    'JPWDownloadAssets must expose getBytes/getText/register before tools-services');
  return h.api;
}
test('initialization performs no fetch or decode', () => {
  const h = harness(); apiOf(h); assert.equal(h.calls.fetch, 0); assert.equal(h.calls.decode, 0); assert.equal(h.calls.scripts.length, 0);
});
test('HTTP loads original bytes and checks integrity', async () => {
  const h = harness(); const result = await apiOf(h).getBytes(resourceId);
  assert.deepEqual(Buffer.from(result), bytes); assert.equal(h.calls.fetch, 1); assert.equal(h.calls.decode, 0);
});
test('getText decodes the verified bytes', async () => {
  const h = harness(); assert.equal(await apiOf(h).getText(resourceId), bytes.toString('utf8'));
});
for(const [name, fetchBytes] of [['size', Buffer.concat([bytes, Buffer.from('x')])], ['hash', Buffer.alloc(bytes.length, 120)]]) {
  test(`reject corrupt HTTP ${name}`, async () => { const h = harness({fetchBytes}); await assert.rejects(apiOf(h).getBytes(resourceId)); });
}
test('unknown resource never requests a network asset', async () => {
  const h = harness(); await assert.rejects(apiOf(h).getBytes('leverage/missing.zip')); assert.equal(h.calls.fetch, 0);
});
test('portable HTTP uses inert envelope only after action', async () => {
  const h = harness({inline: envelope()}); const api = apiOf(h); assert.equal(h.calls.decode, 0);
  assert.deepEqual(Buffer.from(await api.getBytes(resourceId)), bytes); assert.equal(h.calls.fetch, 0); assert.equal(h.calls.decode, 1);
});
for(const delta of [{buildId: 'stale'}, {id: 'other'}, {schemaVersion: 2}, {files: {[resourceId]: Buffer.alloc(bytes.length, 120).toString('base64')}}]) {
  test(`reject invalid portable envelope ${JSON.stringify(delta)}`, async () => {
    const h = harness({inline: envelope(delta)}); await assert.rejects(apiOf(h).getBytes(resourceId)); assert.equal(h.calls.fetch, 0);
  });
}
test('file protocol shares one sidecar and one decode between consumers', async () => {
  const h = harness({protocol:'file:'}); const api = apiOf(h);
  const first = api.getBytes(resourceId), second = api.getText(resourceId);
  assert.equal(h.calls.scripts.length, 1); assert.equal(h.calls.decode, 0);
  h.register(envelope());
  assert.deepEqual(Buffer.from(await first), bytes); assert.equal(await second, bytes.toString());
  assert.equal(h.calls.fetch, 0); assert.equal(h.calls.decode, 1);
});
test('abort rejects only that consumer', async () => {
  const h = harness({protocol:'file:'}); const api = apiOf(h), controller = new AbortController();
  const first = api.getBytes(resourceId, {signal:controller.signal}); const rejection = assert.rejects(first, error => error.name === 'AbortError');
  const second = api.getBytes(resourceId); controller.abort(); await rejection; h.register(envelope());
  assert.deepEqual(Buffer.from(await second), bytes); assert.equal(h.calls.scripts.length, 1);
});
test('sidecar failure is retryable and late registration cannot settle the retry', async () => {
  const h = harness({protocol:'file:'}); const api = apiOf(h);
  const first = api.getBytes(resourceId); const rejection = assert.rejects(first);
  const old = h.calls.scripts[0]; assert.equal(typeof old.onerror, 'function'); old.onerror(new Error('fixture load failed')); await rejection;
  const retry = api.getBytes(resourceId); assert.equal(h.calls.scripts.length, 2);
  try { h.register(envelope(), old); } catch (_) {}
  assert.equal(h.calls.decode, 0, 'late prior script must not decode or register');
  h.register(envelope()); assert.deepEqual(Buffer.from(await retry), bytes);
});
test('sidecar times out at 15 seconds and permits next click', async () => {
  const h = harness({protocol:'file:'}); const api = apiOf(h);
  const first = api.getBytes(resourceId); const rejection = assert.rejects(first);
  const timeout = h.calls.timers.find(timer => timer.delay === 15000); assert(timeout, 'sidecar requires a bounded 15 second timeout');
  timeout.fn(); await rejection;
  const retry = api.getBytes(resourceId); h.register(envelope()); assert.deepEqual(Buffer.from(await retry), bytes);
});
for(const [field, value] of [['path','../fixture.zip'], ['bytes',0], ['bytes',Number.MAX_SAFE_INTEGER+1], ['sha256','bad'], ['payload','missing']]) {
  test(`reject invalid descriptor ${field} before loading`, async () => {
    const h = harness(); h.manifest.resources[resourceId][field] = value;
    await assert.rejects(apiOf(h).getBytes(resourceId)); assert.equal(h.calls.fetch,0); assert.equal(h.calls.scripts.length,0);
  });
}
test('pre-aborted consumer cannot start file sidecar', async () => {
  const h = harness({protocol:'file:'}), controller = new AbortController(); controller.abort();
  await assert.rejects(apiOf(h).getBytes(resourceId,{signal:controller.signal}),error=>error.name==='AbortError');
  assert.equal(h.calls.scripts.length,0); assert.equal(h.calls.decode,0);
});
test('HTTP cache/PWA response follows original-byte path without sidecar', async () => {
  const h = harness(); const api = apiOf(h);
  assert.equal(await api.getText(resourceId),bytes.toString()); assert.equal(h.calls.scripts.length,0);
  assert.equal(h.calls.decode,0); assert.equal(h.calls.fetch,1);
});
test('network failure never falls through to a file-only sidecar', async () => {
  const h = harness({rejectFetch:true}); await assert.rejects(apiOf(h).getBytes(resourceId));
  assert.equal(h.calls.scripts.length,0); assert.equal(h.calls.decode,0);
});
test('envelope missing requested resource fails closed', async () => {
  const h = harness({inline:envelope({files:{}})});
  await assert.rejects(apiOf(h).getBytes(resourceId)); assert.equal(h.calls.fetch,0);
});
test('returned byte arrays cannot corrupt another consumer or validated cache', async () => {
  const h=harness(),api=apiOf(h);const [a,b]=await Promise.all([api.getBytes(resourceId),api.getBytes(resourceId)]);
  a[0]^=255;assert.deepEqual(Buffer.from(b),bytes);assert.deepEqual(Buffer.from(await api.getBytes(resourceId)),bytes);
  assert.equal(h.calls.fetch,1);
});
test('old resource hash failure cannot erase another resource retry in the same group', async () => {
  let release,started;const gate=new Promise(resolve=>release=resolve),digestStarted=new Promise(resolve=>started=resolve);let count=0;
  const cryptoOverride={subtle:{async digest(...args){if(++count===1){started();await gate;}return webcrypto.subtle.digest(...args);}}};
  const h=harness({protocol:'file:',cryptoOverride}),api=apiOf(h),other='leverage/dailySource';
  h.manifest.resources[other]={...h.manifest.resources[resourceId],path:'downloads/leverage/second.zip',filename:'second.zip'};
  const a=api.getBytes(resourceId),aFails=assert.rejects(a),b=api.getBytes(other),bFails=assert.rejects(b);
  h.register(envelope({files:{[resourceId]:Buffer.alloc(bytes.length,120).toString('base64')}}));
  await digestStarted;await bFails;
  const retry=api.getBytes(other);assert.equal(h.calls.scripts.length,2);
  release();await aFails;
  assert.equal(h.register(envelope({files:{[other]:bytes.toString('base64')}})),true,'old failure erased new group attempt');
  assert.deepEqual(Buffer.from(await retry),bytes);
});
(async () => {
  let failures = 0;
  for(const {name, run} of cases)try { await run(); console.log('PASS',name); } catch(error) { failures++; console.error('FAIL',name,'—',error.message); }
  console.log(`${cases.length-failures}/${cases.length} download asset contracts passed`); if(failures)process.exitCode = 1;
})();
