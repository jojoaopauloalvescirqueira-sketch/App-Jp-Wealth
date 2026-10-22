# CHG-JPW-UI-VISUAL-GATE-20261021

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
    "FULL final e aceite humano separado",
    "Adaptação de seletor aos cinco SVGs de gráfico reais, sem mudar quantidade5, limitesw>80/h>40, layouts, estados ou commands dos95checks"
  ],
  "approved_tests": [
    "ui_visual_quality_test.py",
    "regressões existentes",
    "quality_gate.py --tier full",
    "planning_parity_layout_test.py e contraprovas de gráfico removido/colapsado"
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
  "change_id": "CHG-JPW-UI-VISUAL-GATE-20261021",
  "risk_level": "N3",
  "authority_required": "A4",
  "objective": "Acrescentar juiz visual identificável, oráculos independentes e contraprovas, sem remover95 checks.",
  "scope": {
    "allowed_files": [
      "tools/ui_visual_quality_test.py",
      "tools/quality_gate.py",
      "tools/regression-memory.json",
      "docs/superpowers/plans/2026-10-21-planning-controls-visual-quality.md",
      "docs/work/CHG-JPW-UI-VISUAL-GATE-20261021.md",
      "docs/validation/planning-controls-visual-quality-20261021/",
      "tools/planning_parity_layout_test.py"
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

Antes:95 checks, sem medição do conteúdo interno. Depois:96 checks, adição standard/full. Teste novo mede geometria real em Chromium, prova rejeição de violações. Revisão independente necessária; não implica aceite humano. Não enfraquecer testes para obter verde; a adaptação de compatibilidade delimitada abaixo preserva o oráculo dos cinco gráficos.
## Compatibilidade delimitada do teste antigo — execução observada

O plano humano aprovou fecharSVG e preservação dos95checks. A execução completa real95PASS/1TEST_HARNESS_FAIL demonstrou que o seletor geral de SVG confundia o novo ícone decorativo com os cinco gráficos existentes. Este é reparo necessário para preservar o contrato de gráficos da mesma mudança aprovada, não nova regra ou autorização adjacente. A allowlist inclui somente tools/planning_parity_layout_test.py para trocar uma ocorrência de profile.locator('svg') por profile.locator('svg.pl-native-chart'). Quantidade5 e limitesw>80/h>40, casos, fluxo e todos os comandos/IDs permanecem. Proposta8ab2189… e original9fac456… foram comparados; quatro contraprovas reais passaram; auditor independente confirmou preservação do oráculo. Nenhum outro teste antigo será editado, e nenhum resultado anterior será apagado. Sem mudança de produto, financeira, plugin ou Git. Nova freeze e execução FULL são obrigatórias.
