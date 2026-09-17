#!/usr/bin/env node
'use strict';

// Synthetic drawing transport and geometry oracles. No market/account data.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.resolve(__dirname, '..');
const sandbox = {};
['document', 'localStorage', 'sessionStorage', 'fetch', 'S'].forEach(function (key) {
  Object.defineProperty(sandbox, key, { get: function () { throw new Error('Forbidden side effect: ' + key); } });
});
vm.createContext(sandbox);
vm.runInContext(fs.readFileSync(path.join(root, 'src/js/10-domain/16-nocuda-transfer.js'), 'utf8'), sandbox);
const api = sandbox.JPWNocudaTransfer;
// The fixture file may have the repository text-file terminator; wire does not.
const fixture = fs.readFileSync(path.join(root, 'tools/fixtures/nocuda/synthetic-v1.txt'), 'utf8').replace(/\n$/, '');
let passed = 0;
function test(name, fn) {
  try { fn(); passed += 1; process.stdout.write('PASS ' + name + '\n'); }
  catch (error) { process.stderr.write('PRODUCT_FAIL ' + name + '\n'); throw error; }
}
function value() { const result = api.parse(fixture); assert.equal(result.ok, true); return result.value; }
function replace(field, replacement, text) {
  return (text || fixture).split('|').map(function (part) { return part.startsWith(field + '=') ? field + '=' + replacement : part; }).join('|');
}
function reject(text, code, field) {
  const result = api.parse(text);
  assert.equal(result.ok, false, 'Input must fail closed');
  assert.equal(result.error.code, code);
  if (field !== undefined) assert.equal(result.error.field, field);
  assert.equal(Object.hasOwn(result, 'value'), false, 'Failure must not return a partial drawing');
  assert.equal(Object.hasOwn(result, 'canonical'), false);
}
function close(actual, expected, message) { assert.ok(Math.abs(actual - expected) < 1e-8, message || actual + ' versus ' + expected); }

test('fixture / example / serializer round trip and immutable API', function () {
  assert.equal(api.example(), fixture);
  const result = api.parse(fixture);
  assert.equal(result.ok, true);
  assert.equal(result.canonical, fixture);
  assert.equal(api.serialize(result.value), fixture);
  assert.equal(Object.isFrozen(api), true);
});
test('price lexical precision and offset metadata survive three origins', function () {
  const v = value();
  v.a.price = '100.0000000000000000000000000000';
  v.d = '10.0000000000000000000000000000';
  v.a.offset = 120; v.b.offset = 180; v.c.offset = -180;
  ['MT5', 'TV', 'JPW'].forEach(function (source) {
    v.src = source;
    const out = api.parse(api.serialize(v));
    assert.equal(out.ok, true);
    assert.equal(out.value.a.price, v.a.price);
    assert.equal(out.value.d, v.d);
    assert.equal(out.value.a.time, 1767600000000, 'UTC not shifted by source offset');
    assert.equal(out.value.a.offset, 120);
    assert.equal(out.value.b.offset, 180);
    assert.equal(out.value.c.offset, -180);
  });
});
test('arbitrary key order normalizes without losing values', function () {
  const parts = fixture.split('|');
  const reversed = [parts[0]].concat(parts.slice(1).reverse()).join('|');
  assert.equal(api.parse(reversed).canonical, fixture);
});
test('independent anchor and milestone geometry', function () {
  const g = api.geometry(value());
  assert.equal(g.slope, 1); assert.equal(g.width, 10);
  assert.equal(g.lines.length, 49);
  assert.equal(g.minOrdinal, -7); assert.equal(g.maxOrdinal, 41);
  const expected = { 1: 82, 3: 84.5, 5: 87, 9: 92, 17: 102, 41: 132 };
  Object.entries(expected).forEach(function (pair) {
    const line = g.lines.find(function (l) { return l.ordinal === Number(pair[0]); });
    close(line.atC, pair[1]);
    close(line.toPrice - line.fromPrice, 4, 'all lines parallel');
  });
  g.lines.slice(1).forEach(function (line, index) { close(line.atC - g.lines[index].atC, 1.25, 'fixed width/8'); });
  close(g.lines.find(function (l) { return l.ordinal === 17; }).fromPrice, 100);
  close(g.lines.find(function (l) { return l.ordinal === 17; }).toPrice, 104);
});
test('negative width and falling slope retain signed geometry', function () {
  const v = value(); v.b.price = '96'; v.c.price = '108'; v.d = '-10';
  const g = api.geometry(v);
  assert.equal(g.slope, -1); assert.equal(g.width, -10);
  close(g.lines.find(function (l) { return l.ordinal === 9; }).atC, 108);
  close(g.lines.find(function (l) { return l.ordinal === 1; }).atC, 118);
  close(g.lines.find(function (l) { return l.ordinal === 17; }).atC, 98);
});
test('reversed A/B anchors and C outside segment', function () {
  const v = value(); const priorA = v.a; v.a = v.b; v.b = priorA; v.ab = -4; v.ac = -2;
  assert.equal(api.parse(api.serialize(v)).ok, true);
  close(api.geometry(v).lines.find(function (l) { return l.ordinal === 9; }).atC, 92);
  v.c.time = v.a.time + 7200000; v.ac = 2; v.c.price = '96';
  assert.equal(api.parse(api.serialize(v)).ok, true);
  close(api.geometry(v).lines.find(function (l) { return l.ordinal === 9; }).atC, 96);
});
test('same-time A/C valid on same candle; wrong relative order rejected', function () {
  const v = value(); v.c.time = v.a.time; v.c.price = '90'; v.ac = 0;
  assert.equal(api.parse(api.serialize(v)).ok, true);
  reject(replace('c', '1767600000000,92,0'), 'BAR_ORDER', 'ac');
  reject(replace('b', '1767590000000,104,0'), 'BAR_ORDER', 'ab');
  reject(replace('c', '1767614400000,92,0'), 'BAR_ORDER', 'ac');
});
test('weekend/session gap does not become elapsed-time bars', function () {
  const v = value(); v.b.time += 172800000; v.c.time += 172800000;
  const round = api.parse(api.serialize(v));
  assert.equal(round.ok, true); assert.equal(round.value.ab, 4); assert.equal(round.value.ac, 2);
  close(api.geometry(round.value).lines.find(function (l) { return l.ordinal === 9; }).atC, 92);
});
test('appearance keeps groups, visibility, max and fixed count', function () {
  const v = value(); const g = api.geometry(v);
  assert.equal(g.lines[0].group, 'sx');
  assert.equal(g.lines.find(function (l) { return l.ordinal === 2; }).group, 'si');
  assert.equal(g.lines.find(function (l) { return l.ordinal === 3; }).group, 's3');
  assert.equal(g.lines.find(function (l) { return l.ordinal === 41; }).label, 'MAX');
  v.styles.s3.on = 0;
  assert.equal(api.geometry(v).lines.find(function (l) { return l.ordinal === 3; }).label, '');
  v.labels.mode = 'N';
  assert.ok(api.geometry(v).lines.every(function (l) { return l.label === ''; }));
  v.labels.mode = 'A'; v.labels.showMax = 0;
  assert.equal(api.geometry(v).lines.find(function (l) { return l.ordinal === 41; }).label, '41');
  v.before = 0; v.after = 0; assert.equal(api.geometry(v).lines.length, 17);
  v.before = 160; v.after = 160; assert.equal(api.geometry(v).lines.length, 337);
});
test('zero and negative prices preserved; flat line has valid width', function () {
  const v = value(); v.a.price = '0'; v.b.price = '0'; v.c.price = '-10';
  assert.equal(api.parse(api.serialize(v)).ok, true);
  assert.equal(api.geometry(v).slope, 0);
});
test('label decimal canonicalization never introduces exponent notation', function () {
  const text = replace('labels', 'M,12,239,83,80,0,R,O,0.0000001,2,0,0,1,1');
  const result = api.parse(text);
  assert.equal(result.ok, true); assert.equal(result.canonical, text);
  assert.equal(api.parse(api.serialize(result.value)).ok, true);
});
test('caller input is not mutated by serialization or geometry', function () {
  const v = value(); const before = JSON.stringify(v);
  api.serialize(v); const g = api.geometry(v);
  g.lines[0].style.r = 0;
  assert.equal(JSON.stringify(v), before);
});

const invalid = [
  ['empty', '', 'EMPTY'], ['null', null, 'TYPE'], ['object', {}, 'TYPE'],
  ['oversized', 'A'.repeat(16385), 'SIZE'], ['magic', fixture.replace('NOCUDA', 'OTHER'), 'MAGIC'],
  ['newline', fixture + '\n', 'CHARACTER'], ['space', fixture + ' ', 'CHARACTER'],
  ['BOM', '\ufeff' + fixture, 'CHARACTER'], ['Unicode', replace('id', 'ação'), 'CHARACTER'],
  ['null byte', fixture + '\0', 'CHARACTER'], ['zero width', replace('id', 'foo\u200bbar'), 'CHARACTER'],
  ['duplicate', fixture + '|d=10', 'DUPLICATE_FIELD'],
  ['unknown', fixture + '|other=1', 'UNKNOWN_FIELD'],
  ['prototype', fixture + '|__proto__=1', 'UNKNOWN_FIELD'],
  ['missing', fixture.replace('|ab=4', ''), 'MISSING_FIELD'],
  ['empty pair', fixture + '|', 'FIELD'], ['double equals', replace('d', '10=10'), 'FIELD'],
  ['missing value', replace('id', ''), 'FIELD'],
  ['unknown version', replace('v', '2'), 'ENUM'], ['unknown geometry', replace('geom', 'time'), 'ENUM'],
  ['wrong step', replace('step', '0.25'), 'ENUM'], ['log scale', replace('scale', 'G'), 'ENUM'],
  ['unknown source', replace('src', 'WEB'), 'ENUM'], ['wrong ext', replace('ext', 'X'), 'ENUM'],
  ['HTML', replace('id', '<script>'), 'IDENTIFIER'], ['huge id', replace('id', 'A'.repeat(65)), 'IDENTIFIER'],
  ['zero tf', replace('tf', '0'), 'RANGE'], ['large tf', replace('tf', '2592001'), 'RANGE'],
  ['exponent tf', replace('tf', '3.6e3'), 'INTEGER'], ['float tf', replace('tf', '3600.0'), 'INTEGER'],
  ['positive sign', replace('tf', '+3600'), 'INTEGER'], ['leading zeros', replace('tf', '03600'), 'INTEGER'],
  ['negative time', replace('a', '-1,100,0'), 'RANGE'],
  ['late time', replace('a', '4102444800001,100,0'), 'RANGE'],
  ['float time', replace('a', '1767600000000.1,100,0'), 'INTEGER'],
  ['invalid offset', replace('a', '1767600000000,100,841'), 'RANGE'],
  ['short anchor', replace('a', '1767600000000,100'), 'ARITY'],
  ['locale decimal', replace('a', '1767600000000,100,01,0'), 'ARITY'],
  ['NaN price', replace('a', '1767600000000,NaN,0'), 'DECIMAL'],
  ['infinite price', replace('a', '1767600000000,Infinity,0'), 'DECIMAL'],
  ['exponent price', replace('a', '1767600000000,1e2,0'), 'DECIMAL'],
  ['oversized price', replace('a', '1767600000000,1000000000001,0'), 'RANGE'],
  ['zero ab', replace('ab', '0'), 'DEGENERATE'], ['large ab', replace('ab', '5000'), 'RANGE'],
  ['large ac', replace('ac', '-5000'), 'RANGE'], ['width mismatch', replace('d', '9'), 'WIDTH_MISMATCH'],
  ['zero width', replace('d', '0'), 'DEGENERATE'], ['tiny width', replace('d', '0.000000000001'), 'DEGENERATE'],
  ['projection range', replace('before', '161'), 'RANGE'], ['negative projection', replace('after', '-1'), 'RANGE'],
  ['style unknown', replace('si', '1,1,2,3,0,1,X'), 'ENUM'],
  ['style flag', replace('si', '2,1,2,3,0,1,S'), 'RANGE'],
  ['style RGB', replace('si', '1,256,2,3,0,1,S'), 'RANGE'],
  ['style alpha', replace('si', '1,1,2,3,101,1,S'), 'RANGE'],
  ['style width', replace('si', '1,1,2,3,0,6,S'), 'RANGE'],
  ['style float RGB', replace('si', '1,1.1,2,3,0,1,S'), 'INTEGER'],
  ['style arity', replace('si', '1,1,2,3,0,1'), 'ARITY'],
  ['label mode', replace('labels', 'X,12,239,83,80,0,R,O,1,2,0,0,1,1'), 'ENUM'],
  ['label size', replace('labels', 'M,25,239,83,80,0,R,O,1,2,0,0,1,1'), 'RANGE'],
  ['label gap', replace('labels', 'M,12,239,83,80,0,R,O,51,2,0,0,1,1'), 'RANGE'],
  ['label bars', replace('labels', 'M,12,239,83,80,0,R,O,1,101,0,0,1,1'), 'RANGE'],
  ['label missing', replace('labels', 'M,12,239,83,80,0,R,O,1,2,0,0,1'), 'ARITY']
];
invalid.forEach(function (entry) { test('reject ' + entry[0], function () { reject(entry[1], entry[2]); }); });
test('every required field missing and duplicated fails closed', function () {
  fixture.split('|').slice(1).forEach(function (token) {
    const key = token.split('=')[0];
    reject(fixture.split('|').filter(function (part) { return part !== token; }).join('|'), 'MISSING_FIELD', key);
    reject(fixture + '|' + token, 'DUPLICATE_FIELD', key);
  });
});
test('serializer refuses partial values, unknown fields and lossy price coercion', function () {
  const partial = value(); delete partial.d; assert.throws(function () { api.serialize(partial); }, /Campos incompletos/);
  const extra = value(); extra.other = 1; assert.throws(function () { api.serialize(extra); }, /Campos incompletos/);
  const price = value(); price.a.price = 100; assert.throws(function () { api.serialize(price); }, /texto decimal/);
  const bad = value(); bad.d = '9'; assert.throws(function () { api.serialize(bad); }, /largura não corresponde/);
});
test('range edges and identifiers are preserved', function () {
  const v = value(); v.id = 'A'.repeat(64); v.feed = 'UNKNOWN'; v.symbol = 'BROKER:ABC-1.0/+_';
  v.a.offset = -840; v.b.offset = 840; v.tf = 2592000;
  assert.equal(api.parse(api.serialize(v)).value.symbol, v.symbol);
});
process.stdout.write('PASS: ' + passed + ' Nocuda transfer checks; no financial state or external runtime used.\n');
