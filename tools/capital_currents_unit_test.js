#!/usr/bin/env node
'use strict';
// Preserve the quality-gate CLI while running the actual approved q/p field oracles.
const path = require('node:path');
const {spawnSync} = require('node:child_process');
for (const file of ['capital_field_unit_test.js', 'capital_field_catalog_test.js']) {
  const result = spawnSync(process.execPath, [path.join(__dirname, file)], {stdio: 'inherit'});
  if (result.error || result.signal || result.status !== 0) {
    console.error(`FAIL semantic field suite ${file}: ${result.error || result.signal || result.status}`);
    process.exit(1);
  }
}
console.log('PASS semantic pressure/price field and discovery catalog suites');
