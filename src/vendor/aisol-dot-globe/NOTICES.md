# Incorporated Aisol Dot Globe adaptation — JP Wealth

This directory is the local source/build record for the globe incorporated into the JP Wealth application. It is not a standalone component offering or a claim that Aisol is open source.

## Original and attribution

Author: **Aisol Studio**, handle **@ulz-song**. Marketplace listing published/updated September 28, 2026; checked October 15, 2026. Free ($0) Content, **Limited Commercial License**, not MIT.

- Listing: <https://www.framer.com/marketplace/components/aisol-dot-globe/>
- Exact wrapper: <https://framer.com/m/AisolDotGlobe-H7p0ip.js@wBW3SS2w70bMrirlfjgb>
- Exact module: <https://framerusercontent.com/modules/jc1u9OiVnVkL0QlNh7Kh/wBW3SS2w70bMrirlfjgb/AisolDotGlobe.js>
- Frozen `component.original.js`: 48,275 bytes; SHA256 `11208679f0598d6813913d079140f29f620b0a82cc2d27a1ced651b0d67ea7b5`.
- Terms: <https://www.framer.com/legal/community-terms/>, section 7.3.1, checked October 15, 2026.

The checked terms permit modification and use in the user's own projects, including commercial projects, and incorporation into a broader client end product. The terms restrict standalone asset redistribution/publication/sharing/sublicensing, reposting on competing marketplaces/repositories/platforms, competing templates/components/design assets, and claiming original authorship. Ownership remains with Aisol Studio. The local adaptation is incorporated product work authorized by the project owner. No standalone asset publication or public repository release was performed. Any future distribution must be checked against its concrete packaging; this directory does not grant standalone redistribution rights.

`engine.js` extracts the original mask, sampling, coordinate helpers, shaders, camera and base engine; `entry.js` removes React/Framer integration and adds product lifecycle, safe DOM fallback, per-city colors, stable city identifiers and selection. The received bare Three import does not identify the original Framer-resolved version. **Three 0.186.1 is the tested compatible local version**, not a claim about the original deployment.

## Three.js

Three.js **0.186.1**, copyright Three.js Authors, MIT; full permission notice in `THREE-LICENSE.txt`, also retained in the executable bundle's legal comment. Official package <https://registry.npmjs.org/three/0.186.1>. The actual package, build/source input hashes and npm integrity are pinned in `build-lock.json`. Only the browser bundle runs in the application; no Three global is exported.

## Natural Earth

The original module embeds a 720×360 mask identified by its author as Natural Earth 1:50m. Natural Earth's underlying raster/vector map data are public domain. Attribution: **Made with Natural Earth**; contributors include Tom Patterson and Nathaniel Vaughn Kelso. Terms checked October 15, 2026: <https://www.naturalearthdata.com/about/terms-of-use/>. This data status does not extend to Aisol's code/encoded component as a whole.

## Build tool

esbuild **0.25.12**, MIT, build only. Full notice in `ESBUILD-LICENSE.txt`. Official metadata <https://registry.npmjs.org/esbuild/0.25.12>. Platform binary `@esbuild/darwin-arm64` 0.25.12 checked against official npm integrity. Package and binary SHA256 are in the lock. No global installation or package lifecycle scripts were executed.

Build: `python3 tools/build_market_globe.py --three-root /private/tmp/jpw-globe-build/node_modules/three --esbuild-bin /private/tmp/jpw-globe-build/node_modules/.bin/esbuild`. Build checks frozen Aisol source, all pinned Three source/build inputs, package/tool versions and the esbuild binary hash. Output: classical IIFE `aisol-globe.iife.js`, platform browser, ES2020, legal comments inline, no external imports. `build-meta.json` uses normalized dependency paths; `build-receipt.json` records executable/input hashes and size.
