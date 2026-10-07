# CHG-JPW-INTERFACE-BUGFIX-20261006

```yaml
{
  "schema": "jp-harness/chg/v1",
  "change_id": "CHG-JPW-INTERFACE-BUGFIX-20261006",
  "status": "approved",
  "objective": "Rastrear, reproduzir e corrigir defeitos concretos da interface, preservando dados e cálculos",
  "risk_level": "N1",
  "authority_required": "A2",
  "approved_by": "Proprietário: rastreie e corrija bugs da interface",
  "target": {
    "root": "/Users/joaopauloalves/Library/Mobile Documents/com~apple~CloudDocs/99X - Codex/Migracao-2026-10-05/Projetos Work/g-p-6a4fc0aa51dc8191af013579f37179a3/outputs/jpw-interface-bugfix-20261006/candidate",
    "branch": "codex/forex-professional-panel-20261005",
    "baseline_sha": "ac3a2faffeb398357ff105adbf1d47f70ca309bd",
    "baseline_build": "3ea4d24e6b8c3bf7"
  },
  "scope": {
    "allowed_files": [
      "index.html",
      "src/styles/app.css",
      "src/js/20-ui/*.js",
      "src/js/30-accounting/02-accounting-engine.js",
      "src/js/30-accounting/05-fx-planning/05-fx-ui.js",
      "src/js/40-app/01-navigation.js",
      "src/js/40-app/06-boot.js",
      "src/js/40-app/09-settings-modal.js",
      "src/js/40-app/11-operational-shell.js",
      "src/js/40-app/13-dashboard-layout.js",
      "README.md",
      "docs/work/ACTIVE-TASK.md",
      "docs/work/*JPW-INTERFACE-BUGFIX-20261006*"
    ],
    "forbidden_files": [
      "AGENTS.md",
      "skills/**",
      "src/js/00-core/**",
      "src/js/10-domain/**",
      "mt5/**",
      "docs/normative/**",
      "tools/**",
      ".github/**",
      "sw.js"
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
      "financial formulas and schemas",
      "save/rollback and data guards",
      "drafts and context",
      "existing routes, aliases and preferences"
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
    "Defeitos possuem reprodução antes e contraprova depois",
    "Sem perda de rascunho/foco nem gravação por desenho/navegação",
    "Cálculos, domínios, normas, MT5 e juízes do repositório intocados",
    "Revisão independente, focais externos e gates sem mascarar resultados",
    "Base3ea preservada com hashes e rollback"
  ],
  "approved_tests": [
    "isolated synthetic reproduction",
    "external regression probes",
    "applicable existing focal suites",
    "standard",
    "full",
    "independent review"
  ],
  "rollback": {
    "source": [
      "/Users/joaopauloalves/Library/Mobile Documents/com~apple~CloudDocs/99X - Codex/Migracao-2026-10-05/Projetos Work/g-p-6a4fc0aa51dc8191af013579f37179a3/outputs/jpw-interface-bugfix-20261006/baseline.tar.gz"
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
  "approved_at": "2026-10-06T00:05:00-03:00",
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
      "existing Python and Chromium",
      "local synthetic servers",
      "official generators"
    ]
  }
}
```

Escopo refinado após reprodução: Escape em Novo Ticket/Notas reativa Configurações ao fundo; handlers de apresentação 06-boot/09-settings incluídos no mesmo N1/A2 autorizado, sem mudar domínio ou autoridade.
