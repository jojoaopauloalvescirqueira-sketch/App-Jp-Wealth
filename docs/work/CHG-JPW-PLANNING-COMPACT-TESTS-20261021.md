# CHG-JPW-PLANNING-COMPACT-TESTS-20261021

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
    "quality_gate.py --tier full",
    "planning_ui_test.py"
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
  "change_id": "CHG-JPW-PLANNING-COMPACT-TESTS-20261021",
  "risk_level": "N3",
  "authority_required": "A4",
  "objective": "Ampliar oráculos/cobertura aprovados e substituir somente a expectativa18colunas pelo contrato7/3+dados completos emdetalhes, sem enfraquecer96checks/98casos.",
  "scope": {
    "allowed_files": [
      "tools/planning_compact_table_test.py",
      "tools/ui_visual_quality_test.py",
      "tools/planning_parity_test.py",
      "tools/planning_parity_layout_test.py",
      "tools/regression-memory.json",
      "docs/superpowers/plans/2026-10-21-planning-consolidated-monthly-compact.md",
      "docs/validation/planning-consolidated-monthly-compact-20261021/",
      "tools/planning_ui_test.py"
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


## Reconciliação delimitada após a primeira rodada

A mesma autorização humana exige: “Adaptar a expectativa antiga de 18 colunas, substituindo-a por provas de sete/três colunas e acesso a todos os dados. Preservar os demais critérios e checks.” A concretização inicial omitiu duas localizações de `current_month_journey` em `tools/planning_ui_test.py`. Acrescenta-se exclusivamente esse arquivo para um leitor de apresentação e as duas chamadas correspondentes, preservando valores100/20, qualificadores, resultados1050/1030, mensagens, confirmações e snapshots. Não é ampliação do objetivo ou da autoridade.

`planning_parity_layout_test.py`, já permitido condicionalmente, troca somente o seletor de grupo único pelo grupo semântico de projeção; todos os limiares de texto e geometria permanecem. As propostas foram testadas fora dos arquivos versionados, com contraprovas pelo mesmo leitor/oráculo e revisão independente antes da aplicação. [Diagnósticos F1](../validation/planning-consolidated-monthly-compact-20261021/PLANNING-UI-FINDING.md) e [F2](../validation/planning-consolidated-monthly-compact-20261021/PLANNING-LAYOUT-FINDING.md). A primeira rodada94/96, suas classificações brutas e seu freeze permanecem preservados em `attempt-1`; é obrigatório novo freeze e novo FULL integral. Runner,96checks, financeiro, fórmulas, normativos, instruções, publicação e Git continuam inalterados.
