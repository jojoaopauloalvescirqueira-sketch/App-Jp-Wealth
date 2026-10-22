# CHG-JPW-PLANNING-CONTROLS-20261021

Autorização conversacional: plano corrente, sem ampliar permissões.

```yaml
{
  "schema": "jp-harness/chg/v1",
  "status": "approved",
  "target": {
    "root": "/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS",
    "branch": "codex/planejamento-patrimonial-20261020",
    "baseline_sha": "ea15afc9c6a9c30cc69c5b98a8b85c85211ffb34"
  },
  "derived_artifacts": {
    "allowed": [
      "index.html",
      "build-id.js",
      "sw.js",
      "dist/",
      "src/js/manifest.json",
      "src/vendor/"
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
    "invariantes financeiros",
    "revisão independente",
    "FULL final e aceite humano separado"
  ],
  "approved_tests": [
    "ui_visual_quality_test.py",
    "regressões existentes",
    "quality_gate.py --tier full"
  ],
  "rollback": {
    "source": [
      "/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/.superpowers/sdd/planning-controls-visual-quality-20261021/candidate-0dc016-before.tar.gz",
      "/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/.superpowers/sdd/planning-controls-visual-quality-20261021/baseline.json"
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
  "approved_by": "proprietário no pedido PLEASE IMPLEMENT THIS PLAN desta conversa",
  "approved_at": "2026-10-21T16:25:00.599851-03:00",
  "expires_on": [
    "raiz/branch/HEAD/escopo material mudar"
  ],
  "change_id": "CHG-JPW-PLANNING-CONTROLS-20261021",
  "risk_level": "N1",
  "authority_required": "A2",
  "objective": "Organizar13 ações e alinhar conteúdo dos controles, preservando contratos financeiros.",
  "scope": {
    "allowed_files": [
      "src/js/30-accounting/06-planning/03-ui.js",
      "src/styles/app.css",
      "src/js/manifest.json",
      "index.html",
      "README.md",
      "CHANGELOG.md",
      "SESSION_HANDOFF.md",
      "docs/architecture/PLANNING.md",
      "docs/governance/CURRENT-STATE.md",
      "docs/work/ACTIVE-TASK.md",
      "docs/validation/planning-controls-visual-quality-20261021/"
    ],
    "forbidden_files": [
      "skills/",
      "docs/normative/",
      "src/js/30-accounting/06-planning/01-engine.js",
      "src/js/30-accounting/06-planning/02-state.js"
    ],
    "allowed_actions": [
      "implementar plano delimitado",
      "testar/reconstruir/revisar"
    ],
    "forbidden_actions": [
      "commit",
      "push",
      "merge",
      "deploy",
      "configurar AI Memory",
      "alterar dados financeiros"
    ],
    "regressions_forbidden": [
      "preservar95 checks",
      "preservar candidato preexistente"
    ]
  }
}
```

Regra/gate estão em CHG separado. Provas existentes: menu flex wrapping e jump -5px. Fechar: caixa centrada não demonstra desenho tipográfico; substituir por SVG conforme plano.
Registros factuais explicitamente delimitados neste CHG pelo plano humano: README/CHANGELOG/PLANNING/estado/tarefa/handoff e relatório desta entrega; sem editar normas, claims históricos ou ampliar gates. A regra N3 permanece em contrato separado.
