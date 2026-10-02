# CHG-JPW-MT5-DESIGN-20260930

```yaml
{
  "schema": "jp-harness/chg/v1",
  "change_id": "CHG-JPW-MT5-DESIGN-20260930",
  "status": "approved",
  "objective": "JPW MT5 1.13.0: clareza e acabamento visual de NoCuda e Cockpit, preservando matemática e registros",
  "risk_level": "N1",
  "authority_required": "A2",
  "target": {
    "root": "/private/tmp/jpw-cockpit-ui-20260930",
    "branch": "codex/jpw-cockpit-ui-20260930",
    "baseline_sha": "deffc5061fe2eff3d83b6f6e742fa105ac9c5b06"
  },
  "scope": {
    "allowed_files": [
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_NoCuda_UI.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Indicators/JPWealth/JPW_NoCuda_Channels.mq5",
      "mt5/jpw-alavancagem-atual/MQL5/Indicators/JPWealth/JPW_Alavancagem_Atual.mq5",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_Panel.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_Presentation.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_Version.mqh",
      "mt5/jpw-alavancagem-atual/README.md",
      "docs/architecture/JPW-NOCUDA-CHANNELS.md",
      "index.html",
      "downloads/jpw-alavancagem-atual/manifest.json",
      "tools/jpw_nocuda_integration_test.py",
      "tools/jpw_mt5_design_test.py",
      "tools/leverage_package_test.py",
      "tools/leverage_page_test.py",
      "tools/leverage_geometry_test.py",
      "tools/leverage_details_event_test.py",
      "docs/work/CHG-JPW-MT5-DESIGN-20260930.md",
      "docs/work/BRIEF-JPW-MT5-DESIGN-20260930.md",
      "docs/work/ACTIVE-TASK.md"
    ],
    "forbidden_files": [
      "AGENTS.md",
      "mt5/jpw-alavancagem-atual/AGENTS.md",
      "skills/**",
      "docs/normative/**",
      "tools/quality_gate.py",
      "tools/agent_instruction_structure_test.py",
      ".github/**",
      "downloads/nocuda/**",
      "src/js/**",
      "src/styles/app.css",
      "mt5/**/JPW_*Core*.mqh",
      "mt5/**/JPW_*Store*.mqh",
      "mt5/**/JPW_NoCuda_Projection*.mqh",
      "mt5/**/JPW_*Terminal*.mqh",
      "mt5/**/JPW_Alavancagem_Actions.mqh",
      "mt5/**/JPW_Alavancagem_Cockpit.mqh",
      "mt5/**/JPW_Alavancagem_Coordinator.mqh",
      "mt5/**/JPW_Alavancagem_Observer.mq5"
    ],
    "allowed_actions": [
      "edit_scoped",
      "official_artifact_generation",
      "synthetic_tests",
      "independent_audit"
    ],
    "forbidden_actions": [
      "commit",
      "push",
      "merge",
      "deploy",
      "operational_MT5_install",
      "trade",
      "read_real_account"
    ],
    "regressions_forbidden": [
      "formulas, unidades, estados Current/Estimated/N/A ou calendarios alterados",
      "schema financeiro ou preferencias migrados",
      "redesenho grava revisoes ou inicia coleta",
      "rascunho/campo em edicao perdido em update",
      "valor numerico cortado",
      "HUD dimensionado pelo valor vivo",
      "gate, timeout, classificacao ou autoridade alterados"
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
      "loopback tests",
      "official public documentation"
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
      "C++ host shim",
      "existing Chromium/Playwright",
      "isolated MetaEditor only if available"
    ]
  },
  "acceptance_criteria": [
    "NoCuda e Cockpit compartilham hierarquia neutra e contraste verificado nos temas",
    "NoCuda mostra etapas e rascunho/confirmado/historico sem parsear frases",
    "Medidas apresenta rotulos persistentes, numeros completos e paginacao",
    "Atualizacoes preservam rascunho e campos em edicao",
    "Preferencias antigas e seis metricas continuam funcionando",
    "Somente a acao explicita Confirmar cria revisao; nenhum redraw escreve",
    "Teclas nao atravessam uma janela NoCuda em edicao para aplicar acao no Cockpit",
    "Focais e gate obrigatorio classificados no candidate congelado",
    "Sem ambiente isolado: native NOT_RUN, sem EX5 ou prontidao operacional"
  ],
  "approved_tests": [
    "NoCuda integration/core/projection/store",
    "new visual/interaction focal",
    "Cockpit host suite",
    "package/page focal",
    "unchanged full gate",
    "independent audit"
  ],
  "rollback": {
    "source": "Restaurar somente delta listado contra baseline.tar.gz e hashes1.12.0",
    "data": "Nenhum registro local real aberto ou alterado",
    "verification": "Hashes protegidos, formulas e schemas iguais; nao resetar worktree dirty"
  },
  "approved_by": "proprietário — pedido vigente: Agora trabalhe em um aprimoramento de design, visual e interface do usuário para melhorar toda a utilização do programa",
  "approved_at": "2026-09-30T22:41:22.367207+00:00",
  "expires_on": [
    "root/branch changes",
    "scope expands into financial rules or persistence schema",
    "material source conflict"
  ],
  "baseline_candidate": "1.12.0 / 521a18656e89a962c4ce3cd5704fe56cf777871d1057457da913efbb2769e9da"
}
```

Este contrato delimita a autorização humana de melhoria visual e UX; não cria autoridade. A2/N1. Git, publicação, dados reais e instruções ficam fora.


Ajuste de escopo por achado UX em2026-09-30: a rotina atual do Cockpit aceita teclas enquanto sua janela está aberta, inclusive após clique num controle estrangeiro. O novo suporte de teclado NoCuda poderia entregar Enter às duas janelas. A melhoria autorizada inclui um filtro de propriedade do foco no encaminhamento de OnChartEvent do indicadorCockpit, com helper de apresentação e teste de coexistência. Actions, fórmulas, dados, coleta, gravação e contratos de persistência permanecem protegidos; não acrescenta ações financeiras. O ajuste torna concreto o pedido humano de aprimorar toda a utilização do programa.
