# CHG-JPW-ONBOARDING-TEST-20261007

```json
{
  "schema": "jp-harness/chg/v1",
  "change_id": "CHG-JPW-ONBOARDING-TEST-20261007",
  "status": "approved",
  "objective": "Adicionar jornadas reais do primeiro acesso e registrar mudanças deliberadas de expectativas visuais",
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
      "tools/onboarding_first_access_test.py",
      "docs/work/*ONBOARDING*"
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
      "gate_weakening"
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
    "Primeiro acesso distingue acolhida, cadastro e preparação explícita",
    "Legado conclui com objetivo anual ausente, sem fabricar zero",
    "Rascunhos e foco preservados; segredo não persistido",
    "Leitura e consentimento continuam distintos e versionados",
    "Sem cortes e controles inacessíveis nos ambientes testados",
    "Mesmos comandos, normas, dados, gates e MT5"
  ],
  "approved_tests": [
    "baseline reproductions",
    "onboarding_first_access_test",
    "account registration/setup regressions",
    "backup/governance/regression focals",
    "standard",
    "full",
    "MT5 host regression",
    "independent audit"
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

Contrato delimitado pelo brief da mesma tarefa. Novos testes não mudam a classificação dos resultados nem a composição dos gates; expectativas antigas divergentes serão diagnosticadas separadamente.

