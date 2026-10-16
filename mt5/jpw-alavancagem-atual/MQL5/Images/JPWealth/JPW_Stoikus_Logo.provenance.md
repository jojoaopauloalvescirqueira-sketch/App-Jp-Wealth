# Stoikus by JP Wealth — provenance of embedded brand resources

Approved horizontal signature: 240 × 28 logical pixels; Stoikus in Arial regular 24px; “by” in Arial regular 12px; the original red JP Wealth PNG at12px high, preserving its1179:128 ratio. The approved SVG composition is used directly; the institutional lettering is not redrawn.

Institutional source: `assets/jp-wealth-brand-red.png`,1179 ×128, SHA-256 `a77960904ec84b92ad2b1701b5beec6979613b8192dc449e9be8ecbdde10cd85`.

Editable signature sources:

- `assets/stoikus/stoikus-assinatura-clara.svg`, SHA-256 `646f1383149e184760630d6373e19b21e61e90bf741ae78a212eb72c0ef99b67`.
- `assets/stoikus/stoikus-assinatura-escura.svg`, SHA-256 `2a3cd0ed124a2b217197144b3ba86bb394d6db3a261077693412c58fe1457181`.

Derivation: `tools/render_stoikus_brand.py` rasterizes the approved SVG locally using Chromium canvas at100/125/150/200%, saves transparent PNG counterparts in `assets/stoikus`, composites the same pixels onto header chrome and writes RGB24-bit BMPs. Light chrome is `#e9eef4`; dark chrome is `#272d36`. Exact machine-readable output hashes: `assets/stoikus/raster-provenance.json`.

The MQL renderer chooses the matching DPI resource without shrinking the approved lettering to fit a short header. Optional branding is omitted when the complete functional section and signature cannot coexist, and the measured textual function remains. A rejected bitmap or geometry setter removes the partial bitmap before textual fallback. No account collection, financial persistence, execution or preference mutation belongs to this header.

| Resource | Dimensions | SHA-256 |
|---|---|---|
| `JPW_Stoikus_Logo_Light_100.bmp` | 240 × 28 | `dd815b191fa8e6e25669cad12134a0fba4f1e1bfd78a71f24953e551d4c3744a` |
| `JPW_Stoikus_Logo_Light_125.bmp` | 300 × 35 | `6208c8b01ebc0d5b6448324dea8d473cf7d800b4b8546705b8c885ce63b2ba65` |
| `JPW_Stoikus_Logo_Light_150.bmp` | 360 × 42 | `c943a80f6e77c7518051df9412bbf47fc6d0006ff266f2c9074213fe289b4d88` |
| `JPW_Stoikus_Logo_Light_200.bmp` | 480 × 56 | `ff4f6667c2f05ed4ccda8de73920ce87460b770bfd85666f8dee76215bb43727` |
| `JPW_Stoikus_Logo_Dark_100.bmp` | 240 × 28 | `749c2b28ff55b09434995a2be028f5bf86f2274c2be0ed860e1dca6f08b4d82d` |
| `JPW_Stoikus_Logo_Dark_125.bmp` | 300 × 35 | `7d3679be4a8123e262d18a88424610f6f089528f5f897c7c5118adea5345d3e3` |
| `JPW_Stoikus_Logo_Dark_150.bmp` | 360 × 42 | `ee123cab4b2b7df358f8759a50254fb768d18368e261868d8bdfbf93217844a7` |
| `JPW_Stoikus_Logo_Dark_200.bmp` | 480 × 56 | `b756abb78bc3be7bb9abee6337338ccce1e5570847fa78016c1b664a3af483b1` |

These are new presentation bytes; previous package and native receipts cannot approve them. Native bitmap loading, lettering, contrast, templates and DPI interactions remain `NOT_RUN` until an isolated MT5/MetaEditor receipt identifies these exact sources and EX5. Host object-renderer checks do not prove native loading. The separate NoCuda wordmark resource and identity remain preserved.
