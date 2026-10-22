# FULL — candidato corrigido de Planejamento

Build `d93561c064cf5f40`; **91/91 PASS**. Inputs de runtime397, testes257 e runner preservados. Recibo integral local: `.superpowers/sdd/planning-parity-20261020/full-final.json`; o hash e os resultados compactos estão em [FULL-RESULT](FULL-RESULT.json).

Início: 2026-10-20T16:35:06-03:00. Fim: 2026-10-20T16:56:39-03:00.

Cada linha é um check do runner, que pode conter muitos casos. Este resultado não inclui aceite humano ou execução autenticada Google.

| Check | Resultado | Duração (s) | Comando |
|---|---|---:|---|
| preflight | PASS | 0.234 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/agent_preflight.py --mode audit --allow-dirty` |
| structure | PASS | 5.385 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/validate_project.py` |
| diff-check | PASS | 0.334 | `git diff --check` |
| preflight-context | PASS | 1.472 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/preflight_context_test.py` |
| navigation-ia | PASS | 4.484 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/navigation_ia_test.py` |
| dashboard-macro | PASS | 34.042 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/dashboard_macro_test.py` |
| research-navigation | PASS | 8.619 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/research_navigation_test.py` |
| smoke | PASS | 9.146 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/smoke_test.py` |
| settings | PASS | 18.938 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/settings_modal_test.py` |
| brand-identity-contract | PASS | 2.947 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/brand_identity_contract_test.py` |
| brand-identity-browser | PASS | 1.398 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/brand_identity_browser_test.py` |
| statute-documentary | PASS | 9.123 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/statute_documentary_test.py` |
| galton-board | PASS | 7.271 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/galton_board_test.py` |
| planning-engine | PASS | 0.831 | `/Users/joaoalvescirqueira/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node tools/planning_engine_test.js` |
| planning-parity-engine | PASS | 0.485 | `/Users/joaoalvescirqueira/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node tools/planning_parity_engine_test.js` |
| planning-state | PASS | 1.613 | `/Users/joaoalvescirqueira/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node tools/planning_state_test.js` |
| planning-navigation | PASS | 0.032 | `/Users/joaoalvescirqueira/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node tools/planning_navigation_test.js` |
| planning-quote | PASS | 0.032 | `/Users/joaoalvescirqueira/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node tools/planning_quote_test.js` |
| planning-boundaries | PASS | 0.03 | `/Users/joaoalvescirqueira/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node tools/planning_boundaries_test.js` |
| planning-ui | PASS | 16.621 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/planning_ui_test.py` |
| planning-parity-ui | PASS | 8.665 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/planning_parity_test.py` |
| planning-reserve-compat | PASS | 2.175 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/fx_planning_test.py` |
| exec-submenu | PASS | 10.665 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/exec_submenu_test.py` |
| nocoda | PASS | 6.021 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/nocoda_test.py` |
| pivot-studies | PASS | 6.034 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/pivot_studies_test.py` |
| order-guards | PASS | 6.06 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/order_guards_test.py` |
| operation-identity | PASS | 2.451 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/operation_identity_test.py` |
| operation-finalize | PASS | 2.539 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/operation_finalize_test.py` |
| operation-history | PASS | 1.516 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/operation_history_test.py` |
| operation-wiring | PASS | 3.015 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/operation_wiring_test.py` |
| phases-visibility | PASS | 1.54 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/phases_visibility_test.py` |
| exec-three-column | PASS | 3.542 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/exec_three_column_test.py` |
| finpes-foundation | PASS | 5.978 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/finpes_foundation_test.py` |
| finpes-finalize-preservation | PASS | 2.926 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/finpes_finalize_preservation_test.py` |
| finpes-backup-roundtrip | PASS | 3.307 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/finpes_backup_roundtrip_test.py` |
| finpes-navigation | PASS | 2.977 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/finpes_navigation_test.py` |
| finpes-budget | PASS | 17.2 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/finpes_budget_test.py` |
| finpes-debt-credit | PASS | 13.553 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/finpes_debt_credit_test.py` |
| finpes-comparison | PASS | 8.632 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/finpes_comparison_test.py` |
| finpes-scenarios | PASS | 32.233 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/finpes_scenarios_test.py` |
| finpes-overview | PASS | 7.275 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/finpes_overview_test.py` |
| usd-brl-quote | PASS | 11.103 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/usd_brl_quote_test.py` |
| alladin-unit | PASS | 0.65 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/alladin_unit_test.py` |
| alladin-ledger | PASS | 0.502 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/alladin_ledger_test.py` |
| alladin-position | PASS | 0.414 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/alladin_position_test.py` |
| alladin-foundation | PASS | 23.703 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/alladin_foundation_test.py` |
| alladin-finalize-preservation | PASS | 33.927 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/alladin_finalize_preservation_test.py` |
| session-epoch-protocol | PASS | 17.237 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/session_epoch_protocol_test.py` |
| session-write-serialization | PASS | 19.522 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/session_write_serialization_test.py` |
| alladin-ui-readonly | PASS | 6.915 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/alladin_ui_readonly_test.py` |
| alladin-ui-crud | PASS | 43.532 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/alladin_ui_crud_test.py` |
| alladin-ui-ledger | PASS | 26.501 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/alladin_ui_ledger_test.py` |
| alladin-ui-tx-write | PASS | 14.153 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/alladin_ui_tx_write_test.py` |
| alladin-ui-tx-reverse | PASS | 9.883 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/alladin_ui_tx_reverse_test.py` |
| planning-distribution | PASS | 5.393 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/planning_distribution_test.py` |
| planning-parity-layout | PASS | 16.804 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/planning_parity_layout_test.py --out '/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/tools/.artifacts/app-efficiency-full-20261020T163506396932/planning-layout'` |
| session-finalization | PASS | 50.761 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/finalize_session_test.py` |
| storage-governance | PASS | 7.857 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/storage_governance_test.py` |
| persistence-failure | PASS | 30.679 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/persistence_failure_test.py` |
| persistence-recovery | PASS | 42.678 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/persistence_recovery_test.py` |
| investor-password | PASS | 6.863 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/investor_password_test.py` |
| import-xss | PASS | 70.931 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/import_xss_security_test.py` |
| state-integrity | PASS | 6.879 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/state_integrity_test.py` |
| async-generation | PASS | 4.96 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/async_generation_test.py` |
| build-reproducibility | PASS | 32.767 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/build_reproducibility_test.py` |
| service-worker-upgrade | PASS | 20.496 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/service_worker_upgrade_test.py` |
| mvp-notes | PASS | 50.245 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/mvp_notes_test.py` |
| notification-center | PASS | 13.325 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/notification_center_test.py` |
| notification-efficiency | PASS | 14.628 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/notification_efficiency_test.py` |
| consolidated-efficiency | PASS | 6.364 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/consolidated_efficiency_test.py --out '/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/tools/.artifacts/app-efficiency-full-20261020T163506396932/consolidated.json'` |
| consolidated-model | PASS | 0.953 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/fx_consolidated_model_test.py` |
| consolidated-storage | PASS | 16.125 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/fx_consolidated_storage_test.py --out '/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/tools/.artifacts/app-efficiency-full-20261020T163506396932/consolidated-storage.json'` |
| consolidated-ui | PASS | 4.025 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/fx_consolidated_ui_test.py --output '/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/tools/.artifacts/app-efficiency-full-20261020T163506396932/consolidated-ui.json'` |
| forex-professional-panel | PASS | 35.167 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/forex_professional_panel_test.py --out '/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/tools/.artifacts/app-efficiency-full-20261020T163506396932/professional-panel' --native-zoom` |
| execution-efficiency | PASS | 12.367 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/forex_execution_efficiency_test.py --artifacts '/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/tools/.artifacts/app-efficiency-full-20261020T163506396932/rows'` |
| execution-table | PASS | 18.546 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/forex_execution_table_test.py --artifacts '/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/tools/.artifacts/app-efficiency-full-20261020T163506396932/table' --native-zoom` |
| execution-workbook | PASS | 34.664 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/forex_execution_workbook_test.py --out '/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/tools/.artifacts/app-efficiency-full-20261020T163506396932/workbook'` |
| execution-proportions | PASS | 25.667 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/forex_execution_proportions_test.py --out '/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/tools/.artifacts/app-efficiency-full-20261020T163506396932/proportions'` |
| forex-context | PASS | 5.078 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/forex_context_bar_test.py --output '/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/tools/.artifacts/app-efficiency-full-20261020T163506396932/context.json'` |
| forex-navigation-journey | PASS | 12.557 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/forex_navigation_journey_test.py --output '/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/tools/.artifacts/app-efficiency-full-20261020T163506396932/journey.json'` |
| learning-guide | PASS | 101.544 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/learning_guide_test.py --out '/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/tools/.artifacts/app-efficiency-full-20261020T163506396932/guide.json' --baseline-root '/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS'` |
| nocuda-tools | PASS | 9.78 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/nocuda_tools_test.py` |
| stoikus-downloads | PASS | 0.682 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/stoikus_download_test.py` |
| download-assets-unit | PASS | 0.044 | `/Users/joaoalvescirqueira/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node tools/download_assets_test.js` |
| download-assets-browser | PASS | 13.032 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/download_assets_browser_test.py --out-dir '/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/tools/.artifacts/app-efficiency-full-20261020T163506396932/downloads'` |
| capital-currents-unit | PASS | 0.129 | `/Users/joaoalvescirqueira/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node tools/capital_currents_unit_test.js` |
| capital-currents-progress | PASS | 0.036 | `/Users/joaoalvescirqueira/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node tools/capital_currents_progress_test.js` |
| capital-currents-browser | PASS | 54.653 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/capital_currents_browser_test.py --mode all --out-dir '/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/tools/.artifacts/app-efficiency-full-20261020T163506396932/capital-currents'` |
| time-twins-unit | PASS | 0.169 | `/Users/joaoalvescirqueira/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node tools/time_twins_unit_test.js` |
| time-twins-browser | PASS | 78.581 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/time_twins_browser_test.py --mode all --out-dir '/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/tools/.artifacts/app-efficiency-full-20261020T163506396932/time-twins'` |
| minigames | PASS | 8.009 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/minigames_test.py` |
