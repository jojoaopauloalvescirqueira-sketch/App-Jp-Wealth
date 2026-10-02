# JPW GENETRIX — provenance of embedded brand resources

Source: `assets/jp-wealth-brand-red.png`, the existing red JP Wealth website wordmark.
Source SHA-256: `a77960904ec84b92ad2b1701b5beec6979613b8192dc449e9be8ecbdde10cd85`.
Source dimensions: 1179 × 128. No logo redesign or lettering was performed.

Deterministic derivation: Pillow RGBA conversion; Lanczos resize to heights 16, 20, 24 and 32, preserving aspect ratio with rounded width; alpha composite onto header chrome; save RGB 24-bit BMP. Light chrome is `#e9eef4`; dark chrome is `#272d36`. The renderer chooses a 100/125/150/200% resource from screen DPI and available header height; narrow or refused bitmap assignment uses the textual identity. Resources and their hashes are part of the source build.

| Resource | Dimensions | SHA-256 |
|---|---|---|
| `JPW_Genetrix_Logo_Light_100.bmp` | 147 × 16 | `998b31b190b7bf9dc7de9352318da44dc1bc0ef299ef2e2d97231251b061511d` |
| `JPW_Genetrix_Logo_Light_125.bmp` | 184 × 20 | `942dc58a343a042f3e8ff1782cfbfc52bbce3daf75aa0aa818319947774d4458` |
| `JPW_Genetrix_Logo_Light_150.bmp` | 221 × 24 | `b8f0cea6d304cec380c965301f210969490e91e2978a2fb77d62a937edf5e269` |
| `JPW_Genetrix_Logo_Light_200.bmp` | 295 × 32 | `5ca59f6dd99b56d3cd9611641f4e17d85f63b28dfc565e099a8d22c49ee59f0c` |
| `JPW_Genetrix_Logo_Dark_100.bmp` | 147 × 16 | `15c78989ae13ccf8a3c846b15494a029fae31b8203c2c04e08022fac93ed1c4c` |
| `JPW_Genetrix_Logo_Dark_125.bmp` | 184 × 20 | `208fe345ca9f33491f06fca5b3a8178dd546f814642b81e3ce493582b43ed6a3` |
| `JPW_Genetrix_Logo_Dark_150.bmp` | 221 × 24 | `06b891b0c94f68c863d7dc4bc1a3ca96ea5c69e7aace890222c70c202c136614` |
| `JPW_Genetrix_Logo_Dark_200.bmp` | 295 × 32 | `172b83dfd4fb4b8586e6289384f3b13611c389bd7727b9c5c10c5c7e7c2ba5c9` |

Native resource loading, visual scale, contrast and interactions in MT5 remain `NOT_RUN` until isolated receipts identify the exact compiled bytes. Host object-renderer checks do not prove native loading. The old NoCuda resource remains preserved for rollback.
