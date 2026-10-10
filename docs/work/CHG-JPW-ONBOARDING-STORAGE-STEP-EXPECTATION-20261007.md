# CHG-JPW-ONBOARDING-STORAGE-STEP-EXPECTATION-20261007

```json
{
  "schema": "jp-harness/chg/v1",
  "change_id": "CHG-JPW-ONBOARDING-STORAGE-STEP-EXPECTATION-20261007",
  "status": "approved",
  "objective": "Adequar somente duas ações UI do teste de governança à validação por etapa aprovada; preservar todas as 43 asserções, fixtures, oráculos, gates e resultados brutos",
  "risk_level": "N3",
  "authority_required": "A4",
  "approved_by": "Proprietário: Aprovo a sugestão completa",
  "target": {
    "root": "/private/tmp/jpw-onboarding-20261007",
    "branch": "codex/onboarding-first-access-20261007",
    "baseline_sha": "7f0828488b2fc0ea62dc7c421174799cda47a34a",
    "baseline_build": "ba167320c0817398"
  },
  "scope": {
    "allowed_files": [
      "tools/storage_governance_test.py",
      "docs/work/CHG-JPW-ONBOARDING-STORAGE-STEP-EXPECTATION-20261007.md",
      "docs/work/BRIEF-JPW-ONBOARDING-20261007.md"
    ],
    "forbidden_files": [
      "AGENTS.md",
      "skills/**",
      "mt5/**",
      "docs/normative/**",
      ".github/**",
      "tools/quality_gate.py",
      "src/js/00-core/**"
    ],
    "allowed_actions": [
      "bounded_edit",
      "synthetic_tests",
      "official_generation",
      "independent_review"
    ],
    "forbidden_actions": [
      "commit",
      "push",
      "merge",
      "publish",
      "real_data_access",
      "financial_rule_change",
      "gate_weakening",
      "remove_legacy_assertions",
      "change_financial_oracles",
      "change_fixtures",
      "suppress_errors",
      "reclassify_raw_failure"
    ]
  },
  "data": {
    "test_policy": "synthetic_only",
    "schema_change": "forbidden"
  },
  "derived_artifacts": {
    "generation_commands": [
      "python3 tools/rebuild_monolith.py"
    ],
    "manual_edit": "forbidden"
  },
  "acceptance_criteria": [
    "Abrir explicitamente a etapa Database e acionar Continuar valida a responsabilidade vazia nessa etapa",
    "Todas as 43 asserções originais permanecem AST idênticas",
    "O teste inteiro mantém cobertura de sequência, backup, colisão, migração, wipe e IndexedDB",
    "Revogar responsabilidade antes do commit conserva S, LSKEY, financeiro e armazenamento exatos, sem escrita",
    "Produto, fixtures, oráculos financeiros, gates e classificação intactos; RAW full R4 e contraprovas separados"
  ],
  "approved_tests": [
    "Full R4 original (56 PASS / 1 PRODUCT_FAIL retained)",
    "Independent full storage-governance in-memory counterproof (43 asserts retained, PASS)",
    "Independent final responsibility guard R11 (PASS)",
    "Written storage-governance replay",
    "full"
  ],
  "rollback": {
    "source": "/Users/joaopauloalves/Library/Mobile Documents/com~apple~CloudDocs/99X - Codex/Migracao-2026-10-05/Projetos Work/g-p-6a4fc0aa51dc8191af013579f37179a3/outputs/jpw-onboarding-implementation-20261007/baseline.tar",
    "application_state": "unchanged; disposable synthetic browser only"
  },
  "approved_at": "2026-10-07",
  "expires_on": [
    "scope, target or authority change"
  ],
  "external_side_effects": {
    "network": "isolated synthetic fixtures and existing public bootstrap fixtures",
    "temporary_artifacts": "outside product"
  }
}
```

A aprovação integral escolheu validação por etapa, com revisão global somente após preenchimento. O teste antigo acionava Revisar configuração numa Identificação vazia e esperava prioritariamente o erro da sétima etapa. Este contrato registra a adaptação deliberada de apenas duas ações UI: abrir new/database e acionar obStepNext. Não altera a obrigatoriedade da responsabilidade nem qualquer assert.

Reprodução original: gauntlet-final-r4/full.json, 56 PASS / 1 PRODUCT_FAIL. Contraprova e revisão independente: audit-independent/STORAGE-STEP-EXPECTATION-REVIEW.md, storage-governance-step-ui-counterproof.json e POST-GATE-R4-COUNTERPROOFS.md. O arquivo inteiro passou com as 43 asserções originais AST idênticas. A guarda final R11 retirou o aceite sem evento, após conferência integral, e comprovou zero escrita, erro específico e resumo invalidado. Produto e fonte normativa não mudam. A reprodução original permanece PRODUCT_FAIL; não é reclassificada, apagada ou substituída pelo replay novo.
