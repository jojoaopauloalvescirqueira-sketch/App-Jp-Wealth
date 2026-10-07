# CHG-JPW-FOREX-TASK-DESIGN-20261005-TEST

```yaml
{
  "schema": "jp-harness/chg/v1",
  "change_id": "CHG-JPW-FOREX-TASK-DESIGN-20261005-TEST",
  "status": "approved",
  "objective": "Focais de comportamento da apresentação aprovada e expectativas visuais específicas; não alterar oráculos financeiros ou gates",
  "risk_level": "N3",
  "authority_required": "A4",
  "approved_by": "Proprietário: PLEASE IMPLEMENT THIS PLAN — JP Wealth Forex com design sóbrio e navegação por tarefa",
  "target": {
    "root": "/Users/joaopauloalves/Library/Mobile Documents/com~apple~CloudDocs/99X - Codex/Migracao-2026-10-05/Projetos Work/g-p-6a4fc0aa51dc8191af013579f37179a3/outputs/jpw-forex-task-design-20261005/candidate",
    "branch": "codex/forex-professional-panel-20261005",
    "baseline_sha": "ac3a2faffeb398357ff105adbf1d47f70ca309bd",
    "baseline_build": "df2caa32013cb2cc"
  },
  "scope": {
    "allowed_files": [
      "tools/forex_task_design_test.py",
      "tools/forex_professional_panel_test.py",
      "tools/forex_visual_risk_test.py",
      "tools/forex_execution_table_test.py",
      "tools/forex_execution_proportions_test.py",
      "tools/forex_clarity_test.py",
      "tools/navigation_ia_test.py",
      "tools/exec_submenu_test.py",
      "tools/fx_consolidated_ui_test.py",
      "docs/work/CHG-JPW-FOREX-TASK-DESIGN-20261005-TEST.md"
    ],
    "forbidden_files": [
      "tools/quality_gate.py",
      ".github/**",
      "tools/*engine*test.py",
      "tools/*workbook*test.py",
      "tools/forex_market_test.py"
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
    "Mesmas fórmulas, dados e registros; 20 colunas14/36desktop16/48touch",
    "Ferramentas inicialmente recolhidas preservam identidade de campos, rascunhos, cursor e seleção",
    "Histórico consulta contas ativas/arquivadas em RAM, sem trocar operacional",
    "Sete destinos e aliases com agrupamento não interativo; quatro layouts e mobile",
    "Cabeçalhos compactos, tabs visíveis e ausência de sobreposição das ações flutuantes no Forex",
    "Medições comparáveis mostram aproximação dos gráficos/grade",
    "DD14 continua falha financeira separada; raw gates preservados"
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
      "/Users/joaopauloalves/Library/Mobile Documents/com~apple~CloudDocs/99X - Codex/Migracao-2026-10-05/Projetos Work/g-p-6a4fc0aa51dc8191af013579f37179a3/outputs/jpw-forex-task-design-20261005/baseline.tar.gz"
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
  "approved_at": "2026-10-06T02:01:32.512979+00:00",
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

A expectativa antiga de tools sempre visíveis é ajustada somente pelo clique no novo acionador; a asserção de “Não salvo” segue o texto da grade já aprovada. Nenhum oráculo financeiro foi alterado.

O focal exec_submenu_test mantém sete destinos e todos os IDs. Somente ordem e rótulos passam a seguir os três grupos aprovados; ArrowDown continua exigindo foco no segundo filho, agora Histórico. Uma reprodução externa confirmou o teste completo com essas três mudanças antes de aplicá-las. A falha bruta anterior permanece no relatório.
