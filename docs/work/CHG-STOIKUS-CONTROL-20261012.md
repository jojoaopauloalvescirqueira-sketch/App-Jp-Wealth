# CHG dedicado — gerador e verificadores Stoikus

A aprovacao do proprietario abrange o plano 1.22.0 incluindo esta trilha N3/A4. Nenhuma formula, fixture ou criterio financeiro e modificado. Referencia: CHG-STOIKUS-RENAMING-20261012.md; antes/depois auditaveis pelo BASELINE.json e diff.

```yaml
{
  "schema": "jp-harness/chg/v1",
  "change_id": "CHG-STOIKUS-CONTROL-20261012",
  "status": "approved",
  "objective": "Adaptar gerador e verificadores exclusivamente para nomes/paths/versao aprovados, preservando criterios e oraculos",
  "risk_level": "N3",
  "authority_required": "A4",
  "target": {
    "root": "/private/tmp/jpw-stoikus-renaming-20261012",
    "branch": "codex/stoikus-renaming-20261012",
    "baseline_sha": "0f247215cc20829fdba40c3b33458ee976c17ea1"
  },
  "scope": {
    "allowed_files": [
      ".gitignore",
      "mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth/JPW_Genetrix_Ledger_Tests.mq5",
      "mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth/JPW_Genetrix_Risk_Tests.mq5",
      "mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth/JPW_Stoikus_Ledger_Tests.mq5",
      "mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth/JPW_Stoikus_Risk_Tests.mq5",
      "tools/build_leverage_package.py",
      "tools/core_monitor_judge.py",
      "tools/core_preparation_judge.py",
      "tools/core_replay_judge.py",
      "tools/jpw_genetrix_brand_test.py",
      "tools/jpw_genetrix_ledger_test.py",
      "tools/jpw_genetrix_oracle_test.py",
      "tools/jpw_genetrix_risk_test.py",
      "tools/jpw_genetrix_ui_test.py",
      "tools/jpw_mt5_design_test.py",
      "tools/jpw_nocuda_fibo_ui_test.py",
      "tools/jpw_nocuda_integration_test.py",
      "tools/jpw_personal_history_gauntlet.py",
      "tools/jpw_personal_history_oracle.py",
      "tools/jpw_positions_core_test.py",
      "tools/jpw_positions_ui_test.py",
      "tools/jpw_stoikus_brand_test.py",
      "tools/jpw_stoikus_ledger_test.py",
      "tools/jpw_stoikus_oracle_test.py",
      "tools/jpw_stoikus_risk_test.py",
      "tools/jpw_stoikus_ui_test.py",
      "tools/leverage_details_event_test.py",
      "tools/leverage_geometry_test.py",
      "tools/leverage_host_layout.py",
      "tools/leverage_package_test.py",
      "tools/leverage_page_test.py",
      "tools/leverage_panel_test.py",
      "tools/leverage_reliability_test.py",
      "tools/leverage_scheduler_test.py",
      "tools/leverage_stop_risk_test.py",
      "tools/leverage_suite.py"
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
      "Atualizar expectativas de nome/version/paths deliberadamente aprovados",
      "Manter casos negativos e checks historicos separados do candidate atual",
      "Preservar fontes, fixtures, oraculos e recibos financeiros antigos"
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
  "approved_at": "2026-10-12T23:03:30.659912+00:00",
  "authorization_evidence": "PLEASE IMPLEMENT THIS PLAN: Renomeacao deGENETRIXpara Stoikus, incluindo gerador/verificadoresemtrilhapropria; resposta Autorizarbranch eworktree isolada",
  "expires_on": [
    "root/branch/HEAD ouescopodivergir",
    "Novaalteracaomaterialnaoautorizada"
  ]
}
```
