# CHG-JPW-DD-BOUNDARY-FIX-20261006

```yaml
{
  "schema": "jp-harness/chg/v1",
  "change_id": "CHG-JPW-DD-BOUNDARY-FIX-20261006",
  "status": "approved",
  "objective": "Corrigir precisão de DD operacional e preservar limites estritos de fase, fechamento e histerese",
  "risk_level": "N3",
  "authority_required": "A4",
  "approved_by": "Proprietário: Corrija a falha financeira conhecida",
  "target": {
    "root": "/Users/joaopauloalves/Library/Mobile Documents/com~apple~CloudDocs/99X - Codex/Migracao-2026-10-05/Projetos Work/g-p-6a4fc0aa51dc8191af013579f37179a3/outputs/jpw-dd-boundary-fix-20261006/candidate",
    "branch": "codex/forex-professional-panel-20261005",
    "baseline_sha": "ac3a2faffeb398357ff105adbf1d47f70ca309bd",
    "baseline_build": "571d8c2c99b56fbd"
  },
  "scope": {
    "allowed_files": [
      "src/js/10-domain/00-forex-engine.js",
      "README.md",
      "CHANGELOG.md",
      "docs/architecture/FOREX-V11-ENGINE.md",
      "docs/work/ACTIVE-TASK.md",
      "docs/work/*JPW-DD-BOUNDARY-FIX-20261006*"
    ],
    "forbidden_files": [
      "src/js/00-core/00-forex-policy.js",
      "src/js/10-domain/00-forex-state.js",
      "src/js/00-core/04-persistence.js",
      "AGENTS.md",
      "skills/**",
      "tools/**",
      ".github/**",
      "mt5/**",
      "docs/normative/**",
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
      "Norma/parâmetros e comparadores estritos; sem epsilon ou arredondamento de 2casas",
      "Schemas, fatos, histórico, histerese e snapshots de pico preservados",
      "Dados reais e credenciais não acessados",
      "Interface corrigida da base preservada"
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
    "DD14 exato permanece fase4; todos limites exatos respeitados",
    "DD22 exato fecha também para si0.50/equity0.39",
    "DD verdadeiro imediatamente acima não é recolocado no limite; histerese não ganha retorno indevido",
    "Invariância USD/USC sobre decimais canônicos, cashflow documentado e estados inválidos preservados",
    "Oráculo racional independente, foco real state→UI, full bruto e auditoria independente",
    "Nenhuma reescrita silenciosa de phaseState/maxAccountPhaseReached antigos"
  ],
  "approved_tests": [
    "Caracterização da base com núcleo real",
    "Probes externos com oráculo Fraction decimal independente",
    "Focais financeiros originais, workbook e jornadas",
    "Full original sem alteração de juiz",
    "Auditoria matemática e de consumidores independente"
  ],
  "rollback": {
    "source": [
      "/Users/joaopauloalves/Library/Mobile Documents/com~apple~CloudDocs/99X - Codex/Migracao-2026-10-05/Projetos Work/g-p-6a4fc0aa51dc8191af013579f37179a3/outputs/jpw-dd-boundary-fix-20261006/baseline.tar.gz",
      "/Users/joaopauloalves/Library/Mobile Documents/com~apple~CloudDocs/99X - Codex/Migracao-2026-10-05/Projetos Work/g-p-6a4fc0aa51dc8191af013579f37179a3/outputs/jpw-dd-boundary-fix-20261006/baseline.json"
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
  "approved_at": "2026-10-06",
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
