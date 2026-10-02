# CHG-JPW-POSITIONS-TABLE-20261001

```yaml
{
  "schema": "jp-harness/chg/v1",
  "change_id": "CHG-JPW-POSITIONS-TABLE-20261001",
  "status": "approved",
  "objective": "JPW Cockpit 1.15.0: tabela unificada de posicoes com ticket, volume, contribuicao individual de leverage e fechamento acessivel",
  "risk_level": "N3",
  "authority_required": "A4",
  "target": {
    "root": "/private/tmp/jpw-cockpit-ui-20260930",
    "branch": "codex/jpw-cockpit-ui-20260930",
    "baseline_sha": "deffc5061fe2eff3d83b6f6e742fa105ac9c5b06",
    "baseline_fingerprint": "069e2644776da90cdb2c0900544e0b8de0278dc4d1de696daba8f62447780e14"
  },
  "scope": {
    "allowed_files": [
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_Positions*.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_Coordinator.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_Presentation.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_Actions.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_Panel.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_Cockpit.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_Version.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Indicators/JPWealth/JPW_Alavancagem_Atual.mq5",
      "mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth/JPW_Alavancagem_Positions_Tests.mq5",
      "mt5/jpw-alavancagem-atual/README.md",
      "downloads/jpw-alavancagem-atual/manifest.json",
      "index.html",
      "tools/jpw_positions_*test.py",
      "tools/leverage_details_event_test.py",
      "tools/leverage_geometry_test.py",
      "tools/leverage_stop_ui_test.py",
      "tools/leverage_panel_test.py",
      "tools/leverage_page_test.py",
      "tools/leverage_package_test.py",
      "docs/work/CHG-JPW-POSITIONS-TABLE-20261001.md",
      "docs/work/BRIEF-JPW-POSITIONS-TABLE-20261001.md",
      "docs/work/ACTIVE-TASK.md",
      "docs/governance/CURRENT-STATE.md",
      "tools/leverage_scheduler_test.py"
    ],
    "forbidden_files": [
      "AGENTS.md",
      "mt5/jpw-alavancagem-atual/AGENTS.md",
      "skills/**",
      "docs/normative/**",
      "tools/quality_gate.py",
      "tools/leverage_suite.py",
      ".github/**",
      "mt5/**/JPW_Alavancagem_Core.mqh",
      "mt5/**/JPW_Alavancagem_*Store*.mqh",
      "mt5/**/JPW_Alavancagem_Observer.mq5",
      "mt5/**/JPW_NoCuda_*.mqh",
      "mt5/**/JPW_SignalCopy_*.mqh"
    ],
    "allowed_actions": [
      "edit_scoped",
      "official_artifact_generation",
      "synthetic_tests",
      "independent_audit"
    ],
    "forbidden_actions": [
      "commit",
      "merge",
      "push",
      "deploy",
      "read_real_account",
      "operational_MT5_install",
      "trade",
      "send_group_message"
    ],
    "regressions_forbidden": [
      "financial formulas or schemas changed",
      "draw initiates collection or persistence",
      "partial sum presented as account total",
      "SL/EA absence hides current catalog",
      "stale position reused as active",
      "ticket truncated",
      "pending labeled as current deployed leverage"
    ]
  },
  "derived_artifacts": {
    "allowed": [
      "source_zip",
      "portable_html",
      "build_id",
      "offline_cache",
      "external_evidence"
    ],
    "generation_commands": [
      "python3 tools/build_leverage_package.py",
      "python3 tools/rebuild_monolith.py"
    ],
    "manual_edit": "forbidden"
  },
  "external_side_effects": {
    "network": "allowed",
    "allowed_targets": [
      "loopback synthetic tests",
      "official public docs"
    ],
    "temporary_artifacts": "allowed",
    "cleanup_required": true
  },
  "data": {
    "test_policy": "synthetic_only",
    "approved_real_data": [],
    "schema_change": "forbidden"
  },
  "toolchain": {
    "dependency_changes": [],
    "allowed_processes": [
      "Python",
      "host C++ shim",
      "existing Chromium/Playwright",
      "isolated MetaEditor only if usable"
    ]
  },
  "acceptance_criteria": [
    "all current positions available in same tab with within-tab scrolling for long catalogs",
    "MT5 ticket full digits and remaining volume displayed",
    "per-position leverage reuses accepted account notional quotes/scales/routes/equity and reconciles before rounding",
    "account and operation scopes distinct; stops keep exact-symbol/direction scope",
    "historical stops explicitly LAST NOT ACTIVE and separate evidence",
    "unique header Close plus footer close/Esc; no writes on draw",
    "no native readiness claim without exact-byte MT5 receipts"
  ],
  "approved_tests": [
    "same-production-core synthetic math",
    "accepted readmodel replay with identity expiry and shrinking arrays",
    "actual table render/action replay with keyed chart objects",
    "existing MT5 host suite and Signal Copy/NoCuda regressions",
    "package/page focals",
    "unchanged raw full",
    "independent frozen candidate audit"
  ],
  "rollback": {
    "source": [
      "restore only this delta from external baseline-v1140.tar.gz"
    ],
    "application_state": [
      "no preference or financial schema migration"
    ],
    "data": [
      "no real financial or account data read or changed"
    ],
    "environment": [
      "terminate owned synthetic processes"
    ],
    "verification": [
      "compare protected baseline hashes and preserve 98 inherited dirty entries"
    ]
  },
  "approved_by": "proprietario: pedido explicito de tabela unica, ticket, volume, leverage individual e botao Fechar nesta conversa",
  "approved_at": "2026-10-01",
  "expires_on": [
    "root/branch drift",
    "new financial formula or financial schema change",
    "material scope expansion"
  ]
}
```

A instalação preserva A4 para N3 (AGENTS.md §§Classificação e autoridade, linhas 81, 87 e 93). A autorização específica é o pedido humano vigente para ticket, volume e alavancagem de cada posição; a execução reutiliza o cálculo existente, sem mudar norma, parâmetro ou schema. O rótulo não concede Git, negociação, instalação nem outra operação crítica. As 98 alterações herdadas e os 593 hashes da base 1.14.0 foram preservados antes da escrita. A correção deste campo registra a autoridade já recebida, não cria aprovação pelo executor.

Fonte de engenharia confirmada: `/Users/joaopauloalves/Library/Mobile Documents/iCloud~md~obsidian/Documents/2 - TRABALHO/5C - SOFTWARE/A0 - HARNESS - JP Wealth MASTER SPECIFICATION.md`, SHA-256 `b5680c22e44cf3f4a5cd3aa5deeb96f8b65c7908f14543e8c5d7f0c2f4e17b95`, §§12–14, 19, 31.4; exceção §19.1 continua inativa.

Adaptação necessária do aparelho de replay: scheduler-test extrai funções isoladas do Coordinator; os novos hooks de inventário não existiam no seu shim. Ajustar somente dependências sintéticas mantendo as assertivas, orçamento, timeouts e classificação. O recibo compilado anterior será preservado; a integração real do read model é testada separadamente no replay novo.
