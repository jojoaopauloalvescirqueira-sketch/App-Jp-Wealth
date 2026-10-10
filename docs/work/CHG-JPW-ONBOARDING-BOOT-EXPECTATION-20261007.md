# CHG-JPW-ONBOARDING-BOOT-EXPECTATION-20261007

```json
{
  "schema": "jp-harness/chg/v1",
  "change_id": "CHG-JPW-ONBOARDING-BOOT-EXPECTATION-20261007",
  "status": "approved",
  "objective": "Adequar somente a expectativa de abertura automática à acolhida aprovada, acrescentando provas de ausência de gravação; preservar todas as asserções anteriores do smoke",
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
      "tools/smoke_test.py",
      "docs/work/CHG-JPW-ONBOARDING-BOOT-EXPECTATION-20261007.md",
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
    "Acolhida abre automaticamente com as três opções aprovadas",
    "Fechar conserva S, LSKEY e geração exatos, sem aceite implícito",
    "Legado abre explicitamente antes das verificações originais",
    "Todas as linhas originais do smoke permanecem, inclusive finanças, validação, navegação e Notas",
    "Classificação/gates/fixtures intactos; RAW anterior preservado e auditoria independente confirma adaptação"
  ],
  "approved_tests": [
    "Original smoke reproduction (PRODUCT_FAIL retained)",
    "Independent in-memory counterproof (PASS)",
    "Written smoke replay",
    "standard",
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

A aprovação integral da proposta escolheu acolhida em vez da abertura automática do cadastro Forex. Este contrato registra essa mudança deliberada de expectativa; não concede nova autoridade, não corrige resultados financeiros nem autoriza enfraquecer o juiz.

Reprodução original: `smoke-original-reproduction.log`, falha porque Operador/Supervisor não existem na acolhida. Revisão independente: `audit-independent/BOOT-EXPECTATION-REVIEW.md` e `smoke-boot-expectation-counterproof.json`; inserção provisória executou o smoke inteiro e passou, mantendo todos os bytes originais. A alteração escrita reproduz essa inserção. O RAW continua PRODUCT_FAIL; não é reclassificado nem apagado. Gate e seu classificador não mudam.
