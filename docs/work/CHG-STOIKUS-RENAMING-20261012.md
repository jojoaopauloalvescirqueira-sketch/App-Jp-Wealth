# CHG — Stoikus 1.22.0 — renomeacao delimitada

Este registro documenta a aprovacao conversacional do plano; nao cria autoridade. Gitlocal autorizado apenas para criarbranch/worktree e renomear arquivos do mapa; commit/push/merge/deploy separados. Base0f24721, checkoutprincipal daauditoria preservado.

```yaml
{
  "schema": "jp-harness/chg/v1",
  "change_id": "CHG-STOIKUS-PRODUCT-20261012",
  "status": "approved",
  "objective": "Renomear a marca e os 34 arquivos correntes para Stoikus 1.22.0 preservando comportamento e dados",
  "risk_level": "N1",
  "authority_required": "A2",
  "target": {
    "root": "/private/tmp/jpw-stoikus-renaming-20261012",
    "branch": "codex/stoikus-renaming-20261012",
    "baseline_sha": "0f247215cc20829fdba40c3b33458ee976c17ea1"
  },
  "scope": {
    "allowed_files": [
      "CHANGELOG.md",
      "README.md",
      "build-id.js",
      "dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html",
      "downloads/jpw-alavancagem-atual/JPW_Stoikus_Fontes_v1.22.0.zip",
      "downloads/jpw-alavancagem-atual/manifest.json",
      "index.html",
      "mt5/jpw-alavancagem-atual/MQL5/Experts/JPWealth/JPW_Alavancagem_Observer.mq5",
      "mt5/jpw-alavancagem-atual/MQL5/Experts/JPWealth/JPW_Genetrix_Accountant.mq5",
      "mt5/jpw-alavancagem-atual/MQL5/Experts/JPWealth/JPW_Genetrix_Monitor.mq5",
      "mt5/jpw-alavancagem-atual/MQL5/Experts/JPWealth/JPW_Genetrix_Supervisor.mq5",
      "mt5/jpw-alavancagem-atual/MQL5/Experts/JPWealth/JPW_Stoikus_Accountant.mq5",
      "mt5/jpw-alavancagem-atual/MQL5/Experts/JPWealth/JPW_Stoikus_Monitor.mq5",
      "mt5/jpw-alavancagem-atual/MQL5/Experts/JPWealth/JPW_Stoikus_Supervisor.mq5",
      "mt5/jpw-alavancagem-atual/MQL5/Images/JPWealth/JPW_Genetrix_Logo.provenance.md",
      "mt5/jpw-alavancagem-atual/MQL5/Images/JPWealth/JPW_Genetrix_Logo_Dark_100.bmp",
      "mt5/jpw-alavancagem-atual/MQL5/Images/JPWealth/JPW_Genetrix_Logo_Dark_125.bmp",
      "mt5/jpw-alavancagem-atual/MQL5/Images/JPWealth/JPW_Genetrix_Logo_Dark_150.bmp",
      "mt5/jpw-alavancagem-atual/MQL5/Images/JPWealth/JPW_Genetrix_Logo_Dark_200.bmp",
      "mt5/jpw-alavancagem-atual/MQL5/Images/JPWealth/JPW_Genetrix_Logo_Light_100.bmp",
      "mt5/jpw-alavancagem-atual/MQL5/Images/JPWealth/JPW_Genetrix_Logo_Light_125.bmp",
      "mt5/jpw-alavancagem-atual/MQL5/Images/JPWealth/JPW_Genetrix_Logo_Light_150.bmp",
      "mt5/jpw-alavancagem-atual/MQL5/Images/JPWealth/JPW_Genetrix_Logo_Light_200.bmp",
      "mt5/jpw-alavancagem-atual/MQL5/Images/JPWealth/JPW_Stoikus_Logo.provenance.md",
      "mt5/jpw-alavancagem-atual/MQL5/Images/JPWealth/JPW_Stoikus_Logo_Dark_100.bmp",
      "mt5/jpw-alavancagem-atual/MQL5/Images/JPWealth/JPW_Stoikus_Logo_Dark_125.bmp",
      "mt5/jpw-alavancagem-atual/MQL5/Images/JPWealth/JPW_Stoikus_Logo_Dark_150.bmp",
      "mt5/jpw-alavancagem-atual/MQL5/Images/JPWealth/JPW_Stoikus_Logo_Dark_200.bmp",
      "mt5/jpw-alavancagem-atual/MQL5/Images/JPWealth/JPW_Stoikus_Logo_Light_100.bmp",
      "mt5/jpw-alavancagem-atual/MQL5/Images/JPWealth/JPW_Stoikus_Logo_Light_125.bmp",
      "mt5/jpw-alavancagem-atual/MQL5/Images/JPWealth/JPW_Stoikus_Logo_Light_150.bmp",
      "mt5/jpw-alavancagem-atual/MQL5/Images/JPWealth/JPW_Stoikus_Logo_Light_200.bmp",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_Actions.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_Cockpit.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_Coordinator.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_Core.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_Diagnostics.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_Diagnostics_Core.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_Genesis_Core.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_Genesis_Store.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_MDD.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_Observer_Presence.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_Panel.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_Positions.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_Presentation.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_Profile.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_RaizN_Config.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_RaizN_Core.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_RaizN_Factor.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_RaizN_Horizon.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_RaizN_Live.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_RaizN_Observer.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_RaizN_Store.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_Samples.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_StopRisk_Core.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_StopRisk_Store.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_StopRisk_Terminal.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_Store_Result.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_Terminal.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_Version.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Genetrix_Accountant_Runtime.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Genetrix_Brand.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Genetrix_Ledger_Bridge.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Genetrix_Ledger_Core.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Genetrix_Ledger_Preparation.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Genetrix_Ledger_Store.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Genetrix_Ledger_Terminal.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Genetrix_Monitor_Core.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Genetrix_Monitor_Status.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Genetrix_Monitor_UI.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Genetrix_Observer_Runtime.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Genetrix_Risk_Core.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Genetrix_Risk_Store.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Genetrix_Risk_Terminal.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Genetrix_UI.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_NoCuda_Core.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_NoCuda_Fibo_Controller.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_NoCuda_Fibo_Core.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_NoCuda_Fibo_Store.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_NoCuda_Fibo_Sync.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_NoCuda_Fibo_Terminal.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_NoCuda_Fibo_UI.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_NoCuda_Projection.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_NoCuda_Projection_Core.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_NoCuda_Render.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_NoCuda_Store.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_NoCuda_Terminal.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_NoCuda_UI.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_PersonalHistory_Controller.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_PersonalHistory_Core.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_PersonalHistory_Export.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_PersonalHistory_Store.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_PersonalHistory_Terminal.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_PersonalHistory_UI.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_SignalCopy_Controller.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_SignalCopy_Core.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_SignalCopy_Terminal.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_SignalCopy_Types.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_SignalCopy_UI.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Stoikus_Accountant_Runtime.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Stoikus_Brand.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Stoikus_Ledger_Bridge.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Stoikus_Ledger_Core.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Stoikus_Ledger_Preparation.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Stoikus_Ledger_Store.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Stoikus_Ledger_Terminal.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Stoikus_Monitor_Core.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Stoikus_Monitor_Status.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Stoikus_Monitor_UI.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Stoikus_Observer_Runtime.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Stoikus_Risk_Core.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Stoikus_Risk_Store.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Stoikus_Risk_Terminal.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Stoikus_UI.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_UI_Design.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_UI_Focus.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Indicators/JPWealth/JPW_Alavancagem_Atual.mq5",
      "mt5/jpw-alavancagem-atual/MQL5/Indicators/JPWealth/JPW_NoCuda_Channels.mq5",
      "mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth/JPW_Alavancagem_Consultar_MDD.mq5",
      "mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth/JPW_Alavancagem_Diagnostics_Tests.mq5",
      "mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth/JPW_Alavancagem_Genesis_Store_Tests.mq5",
      "mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth/JPW_Alavancagem_Genesis_Tests.mq5",
      "mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth/JPW_Alavancagem_Metrics_Tests.mq5",
      "mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth/JPW_Alavancagem_Observer_Tests.mq5",
      "mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth/JPW_Alavancagem_Panel_Tests.mq5",
      "mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth/JPW_Alavancagem_Positions_Tests.mq5",
      "mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth/JPW_Alavancagem_Profile_Tests.mq5",
      "mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth/JPW_Alavancagem_RaizN_Config_Tests.mq5",
      "mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth/JPW_Alavancagem_RaizN_Factor_Tests.mq5",
      "mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth/JPW_Alavancagem_RaizN_Horizon_Tests.mq5",
      "mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth/JPW_Alavancagem_RaizN_Live_Tests.mq5",
      "mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth/JPW_Alavancagem_RaizN_Store_Tests.mq5",
      "mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth/JPW_Alavancagem_RaizN_Tests.mq5",
      "mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth/JPW_Alavancagem_StopRisk_Tests.mq5",
      "mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth/JPW_Alavancagem_Tests.mq5",
      "mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth/JPW_Alavancagem_Verificar_USC.mq5",
      "mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth/JPW_Genetrix_Ledger_Tests.mq5",
      "mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth/JPW_Genetrix_Risk_Tests.mq5",
      "mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth/JPW_NoCuda_Core_Tests.mq5",
      "mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth/JPW_NoCuda_Fibo_Lab.mq5",
      "mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth/JPW_NoCuda_Fibo_Tests.mq5",
      "mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth/JPW_NoCuda_Projection_Tests.mq5",
      "mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth/JPW_NoCuda_Store_Tests.mq5",
      "mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth/JPW_PersonalHistory_Tests.mq5",
      "mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth/JPW_SignalCopy_Tests.mq5",
      "mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth/JPW_Stoikus_Ledger_Tests.mq5",
      "mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth/JPW_Stoikus_Risk_Tests.mq5",
      "mt5/jpw-alavancagem-atual/README.md",
      "mt5/jpw-alavancagem-atual/STOIKUS_RENAME_1_22_0.md",
      "src/js/40-app/01-navigation.js",
      "src/js/manifest.json"
    ],
    "forbidden_files": [
      "docs/normative/**",
      "docs/decisions/**",
      "docs/validation/genetrix-*/**",
      "mt5/jpw-alavancagem-atual/harness/**",
      "mt5/jpw-alavancagem-atual/GENETRIX_*.md",
      ".github/**",
      "tools/quality_gate.py",
      "AGENTS.md",
      "CLAUDE.md"
    ],
    "allowed_actions": [
      "Implementar somente a renomeacao delimitada aprovada",
      "Testar dados sinteticos e manter evidencias externas",
      "Gerar derivados pelos geradores oficiais"
    ],
    "forbidden_actions": [
      "commit",
      "push",
      "merge",
      "deploy",
      "instalar noMT5",
      "armarSupervisor",
      "migrar/apagar dados",
      "alterar formulas/unidades/limites"
    ],
    "regressions_forbidden": [
      "Perder historico/persistencia/locks/preferencias",
      "Tratar fonte como compilado/aceite",
      "Afrouxar criterios ou reinterpretar comprovacao antiga"
    ]
  },
  "derived_artifacts": {
    "allowed": [
      "downloads/jpw-alavancagem-atual/manifest.json",
      "downloads/jpw-alavancagem-atual/JPW_Stoikus_Fontes_v1.22.0.zip",
      "build-id.js",
      "dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html"
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
      "localhost sintetico"
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
      "python3",
      "C++host",
      "Chromiumdescartavel",
      "Gitlocal somenteacoesautorizadas"
    ]
  },
  "acceptance_criteria": [
    "Marca publicaStoikus;NoCuda conserva nome",
    "Mapaexato34arquivos atualizado sem colisao",
    "Namespaces, schemas, guardsfinanceiros, formulas e locks preservados",
    "Antigosaliasesreconhecidosna admissao dosindicadores",
    "ZIPshistoricosbyte-identicos",
    "Pacotenovo/version/build/hashes coesos semEX5",
    "Hostall/full e revisaoindependente dofreeze final"
  ],
  "approved_tests": [
    "python3 tools/leverage_suite.py --scope all",
    "python3 tools/quality_gate.py --tier full",
    "python3 tools/jpw_stoikus_oracle_test.py",
    "Focais marca/guards/package/page;controlesnegativosisolados",
    "Conferencia hashes/links/diff/recursos/renames/reprodutibilidade"
  ],
  "rollback": {
    "source": [
      "Repor apenas delta autorizado a partir deBASE0f24721 ou dosZIPspreservados aposautorizacaodaoperacaoGitpertinente"
    ],
    "application_state": [
      "Nenhum dado real ouMT5 foi alterado"
    ],
    "environment": [
      "Encerrar processosdescartaveis proprios"
    ],
    "verification": [
      "Comparar fontes eZIPshistoricos comBASELINE.json"
    ],
    "data": []
  },
  "approved_by": "Proprietario nesta conversa",
  "approved_at": "2026-10-12T23:03:30.659505+00:00",
  "authorization_evidence": "PLEASE IMPLEMENT THIS PLAN: Renomeacao deGENETRIXpara Stoikus, incluindo gerador/verificadoresemtrilhapropria; resposta Autorizarbranch eworktree isolada",
  "expires_on": [
    "root/branch/HEAD ouescopodivergir",
    "Novaalteracaomaterialnaoautorizada"
  ]
}
```



## Mapa exato autorizado

| Antes | Depois |
|---|---|
| `mt5/jpw-alavancagem-atual/MQL5/Experts/JPWealth/JPW_Genetrix_Accountant.mq5` | `mt5/jpw-alavancagem-atual/MQL5/Experts/JPWealth/JPW_Stoikus_Accountant.mq5` |
| `mt5/jpw-alavancagem-atual/MQL5/Experts/JPWealth/JPW_Genetrix_Monitor.mq5` | `mt5/jpw-alavancagem-atual/MQL5/Experts/JPWealth/JPW_Stoikus_Monitor.mq5` |
| `mt5/jpw-alavancagem-atual/MQL5/Experts/JPWealth/JPW_Genetrix_Supervisor.mq5` | `mt5/jpw-alavancagem-atual/MQL5/Experts/JPWealth/JPW_Stoikus_Supervisor.mq5` |
| `mt5/jpw-alavancagem-atual/MQL5/Images/JPWealth/JPW_Genetrix_Logo.provenance.md` | `mt5/jpw-alavancagem-atual/MQL5/Images/JPWealth/JPW_Stoikus_Logo.provenance.md` |
| `mt5/jpw-alavancagem-atual/MQL5/Images/JPWealth/JPW_Genetrix_Logo_Dark_100.bmp` | `mt5/jpw-alavancagem-atual/MQL5/Images/JPWealth/JPW_Stoikus_Logo_Dark_100.bmp` |
| `mt5/jpw-alavancagem-atual/MQL5/Images/JPWealth/JPW_Genetrix_Logo_Dark_125.bmp` | `mt5/jpw-alavancagem-atual/MQL5/Images/JPWealth/JPW_Stoikus_Logo_Dark_125.bmp` |
| `mt5/jpw-alavancagem-atual/MQL5/Images/JPWealth/JPW_Genetrix_Logo_Dark_150.bmp` | `mt5/jpw-alavancagem-atual/MQL5/Images/JPWealth/JPW_Stoikus_Logo_Dark_150.bmp` |
| `mt5/jpw-alavancagem-atual/MQL5/Images/JPWealth/JPW_Genetrix_Logo_Dark_200.bmp` | `mt5/jpw-alavancagem-atual/MQL5/Images/JPWealth/JPW_Stoikus_Logo_Dark_200.bmp` |
| `mt5/jpw-alavancagem-atual/MQL5/Images/JPWealth/JPW_Genetrix_Logo_Light_100.bmp` | `mt5/jpw-alavancagem-atual/MQL5/Images/JPWealth/JPW_Stoikus_Logo_Light_100.bmp` |
| `mt5/jpw-alavancagem-atual/MQL5/Images/JPWealth/JPW_Genetrix_Logo_Light_125.bmp` | `mt5/jpw-alavancagem-atual/MQL5/Images/JPWealth/JPW_Stoikus_Logo_Light_125.bmp` |
| `mt5/jpw-alavancagem-atual/MQL5/Images/JPWealth/JPW_Genetrix_Logo_Light_150.bmp` | `mt5/jpw-alavancagem-atual/MQL5/Images/JPWealth/JPW_Stoikus_Logo_Light_150.bmp` |
| `mt5/jpw-alavancagem-atual/MQL5/Images/JPWealth/JPW_Genetrix_Logo_Light_200.bmp` | `mt5/jpw-alavancagem-atual/MQL5/Images/JPWealth/JPW_Stoikus_Logo_Light_200.bmp` |
| `mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Genetrix_Accountant_Runtime.mqh` | `mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Stoikus_Accountant_Runtime.mqh` |
| `mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Genetrix_Brand.mqh` | `mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Stoikus_Brand.mqh` |
| `mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Genetrix_Ledger_Bridge.mqh` | `mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Stoikus_Ledger_Bridge.mqh` |
| `mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Genetrix_Ledger_Core.mqh` | `mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Stoikus_Ledger_Core.mqh` |
| `mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Genetrix_Ledger_Preparation.mqh` | `mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Stoikus_Ledger_Preparation.mqh` |
| `mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Genetrix_Ledger_Store.mqh` | `mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Stoikus_Ledger_Store.mqh` |
| `mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Genetrix_Ledger_Terminal.mqh` | `mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Stoikus_Ledger_Terminal.mqh` |
| `mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Genetrix_Monitor_Core.mqh` | `mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Stoikus_Monitor_Core.mqh` |
| `mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Genetrix_Monitor_Status.mqh` | `mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Stoikus_Monitor_Status.mqh` |
| `mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Genetrix_Monitor_UI.mqh` | `mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Stoikus_Monitor_UI.mqh` |
| `mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Genetrix_Observer_Runtime.mqh` | `mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Stoikus_Observer_Runtime.mqh` |
| `mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Genetrix_Risk_Core.mqh` | `mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Stoikus_Risk_Core.mqh` |
| `mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Genetrix_Risk_Store.mqh` | `mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Stoikus_Risk_Store.mqh` |
| `mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Genetrix_Risk_Terminal.mqh` | `mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Stoikus_Risk_Terminal.mqh` |
| `mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Genetrix_UI.mqh` | `mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Stoikus_UI.mqh` |
| `mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth/JPW_Genetrix_Ledger_Tests.mq5` | `mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth/JPW_Stoikus_Ledger_Tests.mq5` |
| `mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth/JPW_Genetrix_Risk_Tests.mq5` | `mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth/JPW_Stoikus_Risk_Tests.mq5` |
| `tools/jpw_genetrix_brand_test.py` | `tools/jpw_stoikus_brand_test.py` |
| `tools/jpw_genetrix_ledger_test.py` | `tools/jpw_stoikus_ledger_test.py` |
| `tools/jpw_genetrix_oracle_test.py` | `tools/jpw_stoikus_oracle_test.py` |
| `tools/jpw_genetrix_risk_test.py` | `tools/jpw_stoikus_risk_test.py` |
| `tools/jpw_genetrix_ui_test.py` | `tools/jpw_stoikus_ui_test.py` |
