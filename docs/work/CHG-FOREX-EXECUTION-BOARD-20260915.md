# FOREX-EXECUTION-BOARD-01 — CHG/CTX

```yaml
{
  "schema": "jp-harness/chg/v1",
  "change_id": "CHG-FOREX-EXECUTION-BOARD-20260915",
  "status": "approved",
  "objective": "Execution Board compacto, contexto de conta, projeções factuais separadas do V11, observações por instrumento e edição atômica por linha.",
  "risk_level": "N3",
  "authority_required": "A4",
  "target": {
    "root": "/Users/joaopauloalves/.codex/forex-execution-board/20260915/product",
    "branch": "codex/forex-execution-board-20260915",
    "baseline_sha": "594c86ebf13661d0e5846a3b64a0288631fd938d"
  },
  "scope": {
    "allowed_files": [
      "/Users/joaopauloalves/.codex/forex-execution-board/20260915/product/tools/operation_finalize_test.py",
      "/Users/joaopauloalves/.codex/forex-execution-board/20260915/product/tools/async_generation_test.py",
      "/Users/joaopauloalves/.codex/forex-execution-board/20260915/product/tools/storage_governance_test.py",
      "/Users/joaopauloalves/.codex/forex-execution-board/20260915/product/tools/phases_visibility_test.py",
      "/Users/joaopauloalves/.codex/forex-execution-board/20260915/product/tools/order_guards_test.py",
      "/Users/joaopauloalves/.codex/forex-execution-board/20260915/product/index.html",
      "/Users/joaopauloalves/.codex/forex-execution-board/20260915/product/src/styles/app.css",
      "/Users/joaopauloalves/.codex/forex-execution-board/20260915/product/src/js/10-domain/00-forex-state.js",
      "/Users/joaopauloalves/.codex/forex-execution-board/20260915/product/src/js/10-domain/01-risk-instruments.js",
      "/Users/joaopauloalves/.codex/forex-execution-board/20260915/product/src/js/10-domain/02-risk-calculations.js",
      "/Users/joaopauloalves/.codex/forex-execution-board/20260915/product/src/js/10-domain/03-phase-transitions.js",
      "/Users/joaopauloalves/.codex/forex-execution-board/20260915/product/src/js/10-domain/04-stop-statistics.js",
      "/Users/joaopauloalves/.codex/forex-execution-board/20260915/product/src/js/10-domain/11-operation-lifecycle.js",
      "/Users/joaopauloalves/.codex/forex-execution-board/20260915/product/src/js/10-domain/18-execution-board-model.js",
      "/Users/joaopauloalves/.codex/forex-execution-board/20260915/product/src/js/10-domain/19-execution-market.js",
      "/Users/joaopauloalves/.codex/forex-execution-board/20260915/product/src/js/20-ui/03-main-render.js",
      "/Users/joaopauloalves/.codex/forex-execution-board/20260915/product/src/js/20-ui/13-exec-views.js",
      "/Users/joaopauloalves/.codex/forex-execution-board/20260915/product/src/js/20-ui/26-forex-engine-views.js",
      "/Users/joaopauloalves/.codex/forex-execution-board/20260915/product/src/js/20-ui/30-execution-board.js",
      "/Users/joaopauloalves/.codex/forex-execution-board/20260915/product/src/js/30-accounting/01-daily-ledger.js",
      "/Users/joaopauloalves/.codex/forex-execution-board/20260915/product/src/js/40-app/01-navigation.js",
      "/Users/joaopauloalves/.codex/forex-execution-board/20260915/product/src/js/40-app/06-boot.js",
      "/Users/joaopauloalves/.codex/forex-execution-board/20260915/product/src/js/40-app/07-finalize-session.js",
      "/Users/joaopauloalves/.codex/forex-execution-board/20260915/product/src/js/40-app/13-dashboard-layout.js",
      "/Users/joaopauloalves/.codex/forex-execution-board/20260915/product/src/js/manifest.json",
      "/Users/joaopauloalves/.codex/forex-execution-board/20260915/product/sw.js",
      "/Users/joaopauloalves/.codex/forex-execution-board/20260915/product/build-id.js",
      "/Users/joaopauloalves/.codex/forex-execution-board/20260915/product/dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html",
      "/Users/joaopauloalves/.codex/forex-execution-board/20260915/product/tools/forex_execution_board_test.py",
      "/Users/joaopauloalves/.codex/forex-execution-board/20260915/product/tools/forex_execution_market_test.py",
      "/Users/joaopauloalves/.codex/forex-execution-board/20260915/product/tools/forex_execution_projection_test.py",
      "/Users/joaopauloalves/.codex/forex-execution-board/20260915/product/tools/operation_wiring_test.py",
      "/Users/joaopauloalves/.codex/forex-execution-board/20260915/product/tools/exec_three_column_test.py",
      "/Users/joaopauloalves/.codex/forex-execution-board/20260915/product/tools/forex_v11_state_test.py",
      "/Users/joaopauloalves/.codex/forex-execution-board/20260915/product/tools/forex_v11_read_model_test.py",
      "/Users/joaopauloalves/.codex/forex-execution-board/20260915/product/tools/forex_v11_journey_test.py",
      "/Users/joaopauloalves/.codex/forex-execution-board/20260915/product/tools/forex_recording_test.py",
      "/Users/joaopauloalves/.codex/forex-execution-board/20260915/product/docs/work/CHG-FOREX-EXECUTION-BOARD-20260915.md",
      "/Users/joaopauloalves/.codex/forex-execution-board/20260915/product/docs/work/ACTIVE-TASK.md",
      "/Users/joaopauloalves/.codex/forex-execution-board/20260915/product/docs/architecture/FOREX-EXECUTION-BOARD.md",
      "/Users/joaopauloalves/.codex/forex-execution-board/20260915/product/docs/architecture/FOREX-V11-ENGINE.md",
      "/Users/joaopauloalves/.codex/forex-execution-board/20260915/product/docs/architecture/STATE-SCHEMA.md",
      "/Users/joaopauloalves/.codex/forex-execution-board/20260915/product/docs/architecture/CODE-MAP.md",
      "/Users/joaopauloalves/.codex/forex-execution-board/20260915/product/docs/architecture/DB-STORAGE-GOVERNANCE.md",
      "/Users/joaopauloalves/.codex/forex-execution-board/20260915/product/docs/recovery/DATA-RECOVERY.md"
    ],
    "forbidden_files": [
      "AGENTS.md",
      "CLAUDE.md",
      "skills/",
      "docs/normative/",
      "src/js/00-core/00-forex-policy.js",
      "src/js/10-domain/00-forex-engine.js",
      "tools/quality_gate.py",
      ".github/"
    ],
    "allowed_actions": [
      "implementação delimitada N2/N3",
      "fixtures sintéticas",
      "testes focais/FULL",
      "geração oficial",
      "auditoria independente",
      "recovery/comparador"
    ],
    "forbidden_actions": [
      "staging",
      "commit",
      "push",
      "pull",
      "PR",
      "merge",
      "deploy",
      "reset",
      "stash",
      "nova dependência",
      "reescrita financeira normativa"
    ],
    "regressions_forbidden": [
      "perda de dados/rascunhos",
      "lucro positivo como crédito normativo",
      "mistura conta/período/moeda/operação",
      "LEGACY convertido implicitamente"
    ]
  },
  "derived_artifacts": {
    "allowed": [
      "build-id.js",
      "dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html"
    ],
    "generation_commands": [
      "python3 tools/rebuild_monolith.py"
    ],
    "manual_edit": "forbidden"
  },
  "external_side_effects": {
    "network": "allowed",
    "allowed_targets": [
      "Git ls-remote read-only",
      "localhost synthetic browser",
      "existing Frankfurter daily reference endpoint; tests intercepted"
    ],
    "temporary_artifacts": "allowed",
    "cleanup_required": false
  },
  "data": {
    "test_policy": "synthetic_only",
    "approved_real_data": [],
    "schema_change": "approved: optional versioned per-instrument observations/daily references and order snapshots; no new store"
  },
  "toolchain": {
    "dependency_changes": [],
    "allowed_processes": [
      "Python",
      "Node",
      "Chromium existing runtime",
      "official generator"
    ]
  },
  "acceptance_criteria": [
    "Compact readable Board 100%/200%, mobile/light/dark",
    "Save/Cancel by row, one reason/correction, draft/navigation guards",
    "Mestre proposed for new operation only, independent Consolidado selection",
    "Open stops and compensated economic readings separate from committed V11 risk",
    "Per-instrument observations with provenance and daily source date",
    "Quota/refusal/UNKNOWN/conflict/epoch/backup/finalization preserve existing protocols",
    "FULL/focals/audit/reproducibility and identifiable candidate; human acceptance pending"
  ],
  "approved_tests": [
    "forex_execution_board_test.py",
    "forex_execution_market_test.py",
    "forex_execution_projection_test.py",
    "V11/recording/history/navigation/Settings/registration/import/storage relevant regressions",
    "quality_gate.py --tier full",
    "PWA/portable/reproducibility existing mechanisms"
  ],
  "rollback": {
    "source": [
      "/Users/joaopauloalves/.codex/forex-execution-board/20260915/evidence/baseline-recovery.tar.gz",
      "/Users/joaopauloalves/.codex/forex-execution-board/20260915/evidence/baseline.json"
    ],
    "application_state": [
      "synthetic browser profiles only"
    ],
    "data": [
      "existing full backup/restore; no real data access"
    ],
    "environment": [
      "one isolated worktree; preserve other roots/stash"
    ],
    "verification": [
      "restore only owned delta by explicit file copy from recovery; no reset/clean",
      "353 baseline hashes/modes; archive checksum"
    ]
  },
  "approved_by": "proprietário: PLEASE IMPLEMENT THIS PLAN, seguido de Autorizo para opção A específica",
  "approved_at": "2026-09-15",
  "expires_on": [
    "material baseline divergence",
    "new normative rule or scope",
    "different root or branch"
  ]
}
```

```yaml
{
  "schema": "jp-harness/ctx/v1",
  "context_change_id": "CTX-FOREX-EXECUTION-BOARD-20260915",
  "status": "approved",
  "root": "/Users/joaopauloalves/.codex/forex-execution-board/20260915/product",
  "mode": "CONCORRENTE",
  "approved_branch": "codex/forex-execution-board-20260915",
  "create": [
    "docs/work/CHG-FOREX-EXECUTION-BOARD-20260915.md",
    "docs/architecture/FOREX-EXECUTION-BOARD.md"
  ],
  "modify": [
    "docs/work/ACTIVE-TASK.md",
    "docs/architecture/FOREX-V11-ENGINE.md",
    "docs/architecture/STATE-SCHEMA.md",
    "docs/architecture/CODE-MAP.md",
    "docs/architecture/DB-STORAGE-GOVERNANCE.md",
    "docs/recovery/DATA-RECOVERY.md"
  ],
  "preserve": [
    "all historical entries",
    "main/other worktrees/stash/evidence/recovery"
  ],
  "do_not_touch": [
    "CURRENT-STATE",
    "SESSION_HANDOFF",
    "AGENTS/Harness/skills/CI/gates/normative sources"
  ],
  "approved_by": "proprietário: PLEASE IMPLEMENT THIS PLAN, seguido de Autorizo para opção A específica",
  "approved_at": "2026-09-15"
}
```

## Compreensão e decisão normativa
JP Wealth organiza registro, análise e governança financeira local. Operação registra fatos operacionais independentemente da elegibilidade. Hoje três cartões equalizados desperdiçam altura, valores truncam e 19 colunas misturam cadastro, controles e auditoria; o plano aprovado substitui isso por faixas compactas e rascunho RAM com salvamento por linha. Escritores, epoch, revisão e UNKNOWN existentes permanecem autoridades de persistência. Projeção pura não seleciona conta nem grava estado; UI não calcula finanças. Uma única operação conserva sua conta. Mestre só é proposta na criação, e ausência/ambiguidade exige seleção.

Harness c1b5ca9da4dfa2c9a9d1fa3d87a9f7ef9c4cb741fffeedee33d37978f5b800c8 §§12–14/24/31; AGENTS/SKILL-ROUTING e skills preflight/change-control/data-safety/design IMPLEMENTAR/normative-audit lidos. Fontes: docs/normative/Estatuto_JP_WEALTH_UNIFICADO.pdf pp39–43/51–54/66/69–72/81–83 e ANEXO_PARAMETRICO_CANONICO.md P03/P11/P12/P14/P17/P18/P20/P21; contratos FOREX-V11-ENGINE, STATE-SCHEMA, DB-STORAGE-GOVERNANCE, DATA-RECOVERY e navegação. Hashes exatos das fontes pertencem ao baseline.json. README/CURRENT-STATE são fotografias históricas; aviso material de preflight não autoriza curadoria geral.

| Referência da planilha | Norma/decisão | Motor/projeção | UI/prova |
|---|---|---|---|
| Exposição/defesas | Plano: risco aberto − líquido assinado | openRisk/closedNet, custos uma vez | 500−200=300 econômico; RC não diminui |
| Fases/termômetros | P03 seis faixas DD,22% encerra | engine existente, sem budgets inventados | Genesis/Ataque/Intermédio/Defesa/Cuidado/Preparação |
| PS normal/alta | P12b 0.50/0.25 referência nominal | min(SI,equity)×fator/nocional de lote | base10000/EURUSD1.25→0.04/0.02 lotes teóricos |
| ATR/VRM | P11 ATR55/660 H4;1.20/1.50 | vínculo explícito instrumento/conta/período | global legado nunca distribuído |
| Lucro Técnico/MOR/RaizN | P08/P14/P17/P18/P21 e requisitos pendentes | sem cálculo inventado | indisponibilidade específica |

Controles N2 (dados/backup/cotações/rascunhos) e N3 (projeções factuais) explicitamente aprovados; nenhuma edição da política/engine normativa ou mudança de fonte de autoridade. Base de risco positiva e resultado assinado: custos incluídos não repetem; custos separados somam com sinal; falta não vira0. Lucros normativamente não expandem risco comprometido. Fases LEGACY seguem intactas.

## Casos fixados antes da implementação
SI10000/equity9700/fluxo0→DD3%; equity7800→DD22% e encerramento. BUY1.10/SL1.00/0.01lot/100000/conv1→100. Abertos100+pendentes100+perdas20+custos5→RC225; ganho30 não abate. Resultado100/custo−10 separado→90; resultado90 incluído→90. Risco100−resultado−20→120; risco100−resultado150→−50 somente econômico. Quaisquer conta/período/moeda/id incompatíveis impedem total completo. VRM1.20/1.50 pertence TRANSITION. Ausência de sizing/TRA não vira permissão.

## Limites e evidência
Baseline e autorização em ../evidence. Nenhuma fixture financeira real. A12 parcial, OPEN05/V11/FCR/FEO e AUD05/P2 preservados. A implementação não concede aceite, homologação ou integração. Testes antigos de autosave/geometria só mudam para a experiência expressamente aprovada, preservando contraprovas; gates/juízes não mudam. Relatório final registra execução real, fingerprint, recovery e auditoria; ganho de UX depende do proprietário.

## Complemento de regressões diretamente afetadas

FULL exploratório identificou expectativas antigas em `order_guards_test.py` (autosave em select) e `phases_visibility_test.py` (crachá antigo .badge). Incluídos no delta de testes autorizado: gesto de Salvar linha/motivo com contraprova de zero escrita ao digitar; identificação LEGACY no cabeçalho atual. Oráculos financeiros, elegibilidade e preservação permanecem. Não muda gate nem protocolo.

A prova de governança de armazenamento isola agora o provedor diário com resposta sintética indisponível: seu oráculo de documento virgem não deve incluir atos do novo escritor de referências. Igualdade, exportação, sequência, checkpoint e falhas permanecem integrais; o escritor diário tem focais próprios. Settings/finalização ficam sem mudança de teste; a atualização repetida de mesmas taxas foi corrigida no produto como no-op sem novo audit.

O focal async_generation mantém a contraprova wipe/epoch/recovery em modular e portátil, mas sua fixture passa a fornecer identificação/data válidas ao novo parser diário e a observar dailyReferences, preservando o preço legado/manual. A prova aguarda/cancela o bootstrap antes de abrir nova rodada coordenada; recuperação exige ausência de nova requisição em vez de esperar fetch bloqueado. Controle e julgamentos de integridade não foram removidos.

## Complemento focal de validação — revisão final-r2

O FULL da revisão final concluiu 54 PASS e uma falha bruta PRODUCT_FAIL em operation-finalize. A contraprova `../evidence/closure-drafts-final/fixture-diagnosis.json` identificou contaminação da fixture: o caso de digitação deixa rascunho RAM; o próximo caso resemeia S, mas não resolve esse rascunho. O caso isolado passa, e passa após Cancelar explicitamente a linha. Incluído `tools/operation_finalize_test.py` para teardown explícito do caso de digitação, com contraprova de ausência de gravação. Mantidos todos os oráculos de persistência e a guarda do produto. Nenhuma edição de runtime, política, gate ou CI. Manifesto, diff, archive e FULL anteriores são preservados; revisão nova recebe fingerprint próprio.
