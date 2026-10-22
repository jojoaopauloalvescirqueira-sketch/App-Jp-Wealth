# FULL2 failure and minimal comment correction

Read actual full2.json:95 PASS/1 PRODUCT_FAIL, only usd-brl-quote exits1 at static credential keyword scan for authorization in portable HTML. Raw result remains PRODUCT_FAIL, never relabeled PASS. The quoted source occurrence was a new backup explanatory comment, not a demonstrated secret.

Independently checked corrected UI: replacing the one revised comment with its original wording reconstructs exactly FULL2 frozen UI SHA256. Thus the patch changes only that comment; no executable behavior differs. Security test SHA25622007c083dde7933ac97be5abd05d635b5e3b39f9858d975e80f6739a863a3df matches FULL2 freeze unchanged. The existing scanner run against newly rebuilt portable text has zero remaining authorization hits after its unchanged existing masking. This static check is not the complete USD-BRL suite or final FULL.

Minimal comment correction is appropriate: it preserves the scanner and all executable behavior. Retain FULL2 raw failure and freeze separately; new generated artifacts/candidate require new freeze and full validation. No secret disclosure established by this diagnostic. Final FULL3 receipt review pending.
