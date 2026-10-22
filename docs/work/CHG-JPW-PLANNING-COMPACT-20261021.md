# CHG-JPW-PLANNING-COMPACT-20261021

Autorização: plano humano desta conversa; não concede ações adjacentes.

```yaml
{
  "schema": "jp-harness/chg/v1",
  "status": "approved",
  "target": {
    "root": "/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS",
    "branch": "codex/planejamento-patrimonial-20261020",
    "baseline_sha": "ea15afc9c6a9c30cc69c5b98a8b85c85211ffb34",
    "candidate_build": "a9713063cd241820"
  },
  "derived_artifacts": {
    "allowed": [
      "index.html",
      "build-id.js",
      "sw.js",
      "dist/",
      "src/js/manifest.json",
      "src/vendor/downloads/",
      "src/vendor/market-hours/runtime-payload.js"
    ],
    "generation_commands": [
      "python3 tools/rebuild_monolith.py --refresh-manifest"
    ],
    "manual_edit": "forbidden"
  },
  "external_side_effects": {
    "network": "allowed",
    "allowed_targets": [
      "localhost"
    ],
    "temporary_artifacts": "allowed",
    "cleanup_required": false
  },
  "data": {
    "test_policy": "synthetic_only",
    "approved_real_data": [],
    "schema_change": "forbidden"
  },
  "toolchain": {
    "dependency_changes": [],
    "allowed_processes": [
      "Python existente",
      "Chromium existente",
      "Node existente",
      "builder oficial"
    ]
  },
  "acceptance_criteria": [
    "plano humano satisfeito",
    "RED/GREEN e contraprovas",
    "invariantes financeiros preservados",
    "revisão independente",
    "FULL final e aceite humano separado"
  ],
  "approved_tests": [
    "ui_visual_quality_test.py",
    "planning_compact_table_test.py",
    "regressões existentes",
    "quality_gate.py --tier full"
  ],
  "rollback": {
    "source": [
      "/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/.superpowers/sdd/2026-10-21-planning-consolidated-monthly-compact/candidate-a971-before.tar.gz",
      "/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/.superpowers/sdd/2026-10-21-planning-consolidated-monthly-compact/baseline.json"
    ],
    "application_state": [
      "nenhuma migração"
    ],
    "data": [
      "dados reais intocados"
    ],
    "environment": [
      "sem instalação"
    ],
    "verification": [
      "comparar hashes com baseline"
    ]
  },
  "approved_by": "proprietário no PLEASE IMPLEMENT THIS PLAN: Consolidado organizado e tabela mensal compacta desta conversa",
  "approved_at": "2026-10-21T22:34:12.942959+00:00",
  "expires_on": [
    "raiz/branch/HEAD/escopo material mudar"
  ],
  "change_id": "CHG-JPW-PLANNING-COMPACT-20261021",
  "risk_level": "N1",
  "authority_required": "A2",
  "objective": "Agrupar Consolidado e apresentar grade7/3com detalhes semoverflow, preservando dados/cálculos/fluxos.",
  "scope": {
    "allowed_files": [
      "src/js/30-accounting/06-planning/03-ui.js",
      "src/styles/app.css",
      "README.md",
      "CHANGELOG.md",
      "SESSION_HANDOFF.md",
      "docs/architecture/PLANNING.md",
      "docs/governance/CURRENT-STATE.md",
      "docs/work/ACTIVE-TASK.md",
      "docs/validation/planning-consolidated-monthly-compact-20261021/"
    ],
    "forbidden_files": [
      "skills/",
      "AGENTS.md",
      "docs/normative/",
      "src/js/30-accounting/06-planning/01-engine.js",
      "src/js/30-accounting/06-planning/02-state.js",
      "tools/quality_gate.py"
    ],
    "allowed_actions": [
      "implementar plano delimitado",
      "testar/reconstruir/revisar",
      "registrar evidência factual delimitada"
    ],
    "forbidden_actions": [
      "commit",
      "push",
      "merge",
      "deploy",
      "configurar AI Memory",
      "alterar dados financeiros",
      "enfraquecer critérios não alterados pelo plano"
    ],
    "regressions_forbidden": [
      "preservar96checks/98casosanteriores",
      "preservar candidato anterior e histórico"
    ]
  }
}
```

Produto e juiz em trilhas separadas. UI pode mudar quantidade/distribuição visível conforme plano; nenhum cálculo, writer ou formato muda. A adaptação de testes preserva os mesmos dados financeiros disponíveis e todos os demais cenários/critérios. Casos novos têm contraprovas; aceite humano e Git permanecem posteriores. Registros factuais do produto estão delimitados na allowlist acima, sem alterar normas/instruções.
