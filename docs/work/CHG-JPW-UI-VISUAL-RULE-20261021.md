# CHG-JPW-UI-VISUAL-RULE-20261021

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
  "change_id": "CHG-JPW-UI-VISUAL-RULE-20261021",
  "risk_level": "N3",
  "authority_required": "A4",
  "objective": "Registrar regra visual permanente do projeto; cobertura executável inicial Planejamento, demais superfícies pendentes.",
  "scope": {
    "allowed_files": [
      "AGENTS.md",
      "docs/governance/UI-VISUAL-QUALITY.md",
      "docs/governance/CURRENT-STATE.md",
      "docs/work/ACTIVE-TASK.md",
      "SESSION_HANDOFF.md",
      "docs/architecture/PLANNING.md",
      "docs/work/CHG-JPW-UI-VISUAL-RULE-20261021.md",
      "docs/superpowers/plans/2026-10-21-planning-controls-visual-quality.md"
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

A implantação local da regra não concede aceite humano nem autorização Git. Registros factuais README/CHANGELOG estão na allowlist específica do CHG-JPW-PLANNING-CONTROLS-20261021, conforme plano; PLANNING/estado/handoff nesta CTX e no CHG produto; histórico permanece. Este contrato de instruções é um subconjunto deliberado e não autoriza o juiz/gate, cujo CHG é separado. Contrato de gate separado. Auditoria de estrutura pode manter limitação histórica CURRENT-STATE; não enfraquecer o teste.
```yaml
{
  "schema": "jp-harness/ctx/v1",
  "context_change_id": "CTX-JPW-UI-VISUAL-RULE-20261021",
  "status": "approved",
  "root": "/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS",
  "mode": "SEQUENCIAL",
  "approved_branch": "codex/planejamento-patrimonial-20261020",
  "create": [
    "docs/governance/UI-VISUAL-QUALITY.md"
  ],
  "modify": [
    "AGENTS.md",
    "docs/governance/CURRENT-STATE.md",
    "docs/work/ACTIVE-TASK.md",
    "SESSION_HANDOFF.md",
    "docs/architecture/PLANNING.md"
  ],
  "merge": [],
  "preserve": [
    "histórico",
    "95 checks",
    "candidato0dc016"
  ],
  "do_not_touch": [
    "skills/",
    "docs/normative/"
  ],
  "archive_requires_confirmation": [],
  "source_of_truth": {
    "plano": "docs/superpowers/plans/2026-10-21-planning-controls-visual-quality.md",
    "autoridade": "pedido humano corrente"
  },
  "information_promotion": [
    {
      "from": "docs/superpowers/plans/2026-10-21-planning-controls-visual-quality.md",
      "to": "docs/governance/UI-VISUAL-QUALITY.md",
      "reason": "regra explicitamente aprovada"
    }
  ],
  "expiration_rules": [
    {
      "artifact": "regra",
      "event": "nova decisão humana"
    }
  ],
  "privacy_actions": [
    "somente dados sintéticos"
  ],
  "acceptance_criteria": [
    "registros factuais e cobertura honesta"
  ],
  "approved_by": "proprietário no pedido PLEASE IMPLEMENT THIS PLAN desta conversa",
  "approved_at": "2026-10-21T16:25:00.599851-03:00",
  "expires_on": [
    "raiz/branch/HEAD/escopo material mudar"
  ]
}
```
