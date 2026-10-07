# CHG-JPW-FOREX-PROFESSIONAL-TEST-20261005

```yaml
{
  "schema": "jp-harness/chg/v1",
  "change_id": "CHG-JPW-FOREX-PROFESSIONAL-TEST-20261005",
  "status": "approved",
  "objective": "Focal do painel profissional e expectativas visuais deliberadas, sem alterar oráculos financeiros ou gates",
  "risk_level": "N3",
  "authority_required": "A4",
  "approved_by": "Proprietário: PLEASE IMPLEMENT THIS PLAN — JP Wealth painel profissional de desempenho e risco (2026-10-05); implementação local, projeção e contrato separado de testes explicitamente aprovados",
  "target": {
    "root": "/Users/joaopauloalves/.codex/.chatgpt-projects/g-p-6a4fc0aa51dc8191af013579f37179a3/outputs/jpw-forex-professional-panel-20261005/candidate",
    "branch": "codex/forex-professional-panel-20261005",
    "baseline_sha": "ac3a2faffeb398357ff105adbf1d47f70ca309bd"
  },
  "scope": {
    "allowed_files": [
      "tools/forex_professional_panel_test.py",
      "tools/forex_visual_risk_test.py",
      "tools/fx_consolidated_ui_test.py"
    ],
    "forbidden_files": [
      "AGENTS.md",
      "skills/**",
      "src/js/00-core/**",
      "mt5/**",
      "tools/quality_gate.py",
      ".github/**",
      "src/js/10-domain/17-fx-consolidated-model.js",
      "src/js/10-domain/00-forex-engine.js",
      "src/js/10-domain/00-forex-state.js"
    ],
    "allowed_actions": [
      "bounded_edit",
      "synthetic_tests",
      "independent_audit",
      "official_generation"
    ],
    "forbidden_actions": [
      "commit",
      "push",
      "merge",
      "publish",
      "real_data_reads",
      "real_data_mutation"
    ],
    "regressions_forbidden": [
      "financial formulas",
      "persistence and schemas",
      "twenty columns",
      "drafts and financial guards"
    ]
  },
  "derived_artifacts": {
    "allowed": [
      "src/js/manifest.json",
      "build-id.js",
      "dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html",
      "src/vendor/pdfjs/runtime-assets.js",
      "src/vendor/normative/statute-payload.js"
    ],
    "generation_commands": [
      "python3 tools/rebuild_monolith.py"
    ],
    "manual_edit": "forbidden"
  },
  "data": {
    "test_policy": "synthetic_only",
    "schema_change": "forbidden",
    "approved_real_data": []
  },
  "acceptance_criteria": [
    "Valores idênticos aos produtores canônicos; ausência diferente de zero; cobertura e origem explícitas",
    "Gráficos compartilhando consulta e base temporal, filtros sem rebase silencioso; resumo PDF permanece no período",
    "Movimentos, distribuições e registro local acessíveis sem writes ou perda de rascunho",
    "Grid 20 colunas e proporções preservadas; quatro layouts e 320-1440px; teclado/toque e zoom200",
    "DD14 histórico continua PRODUCT_FAIL; raw gates e revisão independente sem reclassificação"
  ],
  "approved_tests": [
    "focal baseline and candidate",
    "browser dimensions and tasks",
    "financial regressions",
    "standard",
    "raw full",
    "independent audit"
  ],
  "rollback": {
    "source": [
      "/Users/joaopauloalves/.codex/.chatgpt-projects/g-p-6a4fc0aa51dc8191af013579f37179a3/outputs/jpw-forex-professional-panel-20261005/baseline.tar.gz"
    ],
    "application_state": [
      "unchanged; synthetic disposable browser only"
    ],
    "data": [
      "no real-data access or financial schema change"
    ],
    "environment": [
      "close only disposable test processes"
    ],
    "verification": [
      "compare baseline hashes and rerun affected tests"
    ]
  },
  "approved_at": "2026-10-05T19:13:12.308973+00:00",
  "expires_on": [
    "target root/branch/base changes",
    "scope or authority changes"
  ],
  "external_side_effects": {
    "network": "allowed",
    "allowed_targets": [
      "isolated localhost synthetic fixtures"
    ],
    "temporary_artifacts": "allowed",
    "cleanup_required": true
  },
  "toolchain": {
    "dependency_changes": [],
    "allowed_processes": [
      "Python test runners",
      "existing Playwright Chromium",
      "official generator",
      "local fixture servers"
    ]
  }
}
```

Baseline: candidate 0b165ab8911f1f3b, fingerprint 5db9ab6ea38c9f8994a522aa5da6c5dd1cea7083ee2f44dd1e5a648e44f0b494; 15 alterações anteriores preservadas.

Expectativa visual adicional: a data da importação passa de `#fxcCoverage` para a faixa única `#fxcIdentity .fxc-selection-meta`. O teste confere o horário exato do recibo salvo nesse local e mantém a metodologia no bloco de cobertura. A tentativa anterior 31/32 e seu juiz foram preservados; nenhum valor, oráculo financeiro ou classificação de gate foi relaxado.
