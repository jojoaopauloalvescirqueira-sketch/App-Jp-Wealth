# FULL — proporções de Planejamento e regressões preservadas

Build `0dc016f9c7618385`;95/95 checks PASS nesta execução.

Início: 2026-10-21T13:54:44-03:00. Fim: 2026-10-21T14:22:03-03:00.

327 inputs oficiais ordenados; inventário separado397 runtime/recursos;260 testes;1 runner.
O exit0 e a sessão são observações fornecidas pelo root. As provas anteriores, inclusive90 logs do FULL interrompido, permanecem históricas; não aprovam este candidato.

| Check | Resultado | Duração(s) | Comando |
|---|---|---:|---|
| preflight | PASS | 0.254 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/agent_preflight.py --mode audit --allow-dirty` |
| structure | PASS | 6.824 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/validate_project.py` |
| diff-check | PASS | 0.388 | `git diff --check` |
| preflight-context | PASS | 2.221 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/preflight_context_test.py` |
| navigation-ia | PASS | 6.82 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/navigation_ia_test.py` |
| dashboard-macro | PASS | 49.457 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/dashboard_macro_test.py` |
| research-navigation | PASS | 10.975 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/research_navigation_test.py` |
| smoke | PASS | 12.251 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/smoke_test.py` |
| settings | PASS | 23.764 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/settings_modal_test.py` |
| brand-identity-contract | PASS | 3.013 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/brand_identity_contract_test.py` |
| brand-identity-browser | PASS | 1.296 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/brand_identity_browser_test.py` |
| statute-documentary | PASS | 13.424 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/statute_documentary_test.py` |
| galton-board | PASS | 7.869 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/galton_board_test.py` |
| planning-engine | PASS | 0.948 | `/Users/joaoalvescirqueira/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node tools/planning_engine_test.js` |
| planning-parity-engine | PASS | 0.653 | `/Users/joaoalvescirqueira/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node tools/planning_parity_engine_test.js` |
| planning-state | PASS | 1.847 | `/Users/joaoalvescirqueira/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node tools/planning_state_test.js` |
| planning-navigation | PASS | 0.035 | `/Users/joaoalvescirqueira/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node tools/planning_navigation_test.js` |
| planning-quote | PASS | 0.034 | `/Users/joaoalvescirqueira/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node tools/planning_quote_test.js` |
| planning-boundaries | PASS | 0.036 | `/Users/joaoalvescirqueira/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node tools/planning_boundaries_test.js` |
| planning-ui | PASS | 18.849 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/planning_ui_test.py` |
| planning-parity-ui | PASS | 10.074 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/planning_parity_test.py` |
| planning-reserve-compat | PASS | 4.532 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/fx_planning_test.py` |
| exec-submenu | PASS | 12.66 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/exec_submenu_test.py` |
| nocoda | PASS | 6.74 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/nocoda_test.py` |
| pivot-studies | PASS | 7.509 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/pivot_studies_test.py` |
| order-guards | PASS | 8.328 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/order_guards_test.py` |
| operation-identity | PASS | 2.95 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/operation_identity_test.py` |
| operation-finalize | PASS | 3.339 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/operation_finalize_test.py` |
| operation-history | PASS | 1.867 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/operation_history_test.py` |
| operation-wiring | PASS | 3.277 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/operation_wiring_test.py` |
| phases-visibility | PASS | 1.791 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/phases_visibility_test.py` |
| exec-three-column | PASS | 3.949 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/exec_three_column_test.py` |
| finpes-foundation | PASS | 6.745 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/finpes_foundation_test.py` |
| finpes-finalize-preservation | PASS | 2.482 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/finpes_finalize_preservation_test.py` |
| finpes-backup-roundtrip | PASS | 4.292 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/finpes_backup_roundtrip_test.py` |
| finpes-navigation | PASS | 3.546 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/finpes_navigation_test.py` |
| finpes-budget | PASS | 18.97 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/finpes_budget_test.py` |
| finpes-debt-credit | PASS | 19.49 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/finpes_debt_credit_test.py` |
| finpes-comparison | PASS | 11.513 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/finpes_comparison_test.py` |
| finpes-scenarios | PASS | 43.061 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/finpes_scenarios_test.py` |
| finpes-overview | PASS | 9.126 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/finpes_overview_test.py` |
| usd-brl-quote | PASS | 13.412 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/usd_brl_quote_test.py` |
| alladin-unit | PASS | 0.961 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/alladin_unit_test.py` |
| alladin-ledger | PASS | 0.56 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/alladin_ledger_test.py` |
| alladin-position | PASS | 0.457 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/alladin_position_test.py` |
| alladin-foundation | PASS | 28.028 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/alladin_foundation_test.py` |
| alladin-finalize-preservation | PASS | 36.816 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/alladin_finalize_preservation_test.py` |
| session-epoch-protocol | PASS | 24.805 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/session_epoch_protocol_test.py` |
| session-write-serialization | PASS | 21.105 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/session_write_serialization_test.py` |
| alladin-ui-readonly | PASS | 7.398 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/alladin_ui_readonly_test.py` |
| alladin-ui-crud | PASS | 52.852 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/alladin_ui_crud_test.py` |
| alladin-ui-ledger | PASS | 31.489 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/alladin_ui_ledger_test.py` |
| alladin-ui-tx-write | PASS | 15.81 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/alladin_ui_tx_write_test.py` |
| alladin-ui-tx-reverse | PASS | 10.432 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/alladin_ui_tx_reverse_test.py` |
| planning-distribution | PASS | 7.134 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/planning_distribution_test.py` |
| planning-three-tabs | PASS | 11.311 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/planning_three_tabs_test.py --receipt '/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/tools/.artifacts/app-efficiency-full-20261021T135444884378/planning-three-tabs.json'` |
| planning-proportions | PASS | 36.786 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/planning_proportions_test.py --out '/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/tools/.artifacts/app-efficiency-full-20261021T135444884378/planning-proportions'` |
| planning-parity-layout | PASS | 20.517 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/planning_parity_layout_test.py --out '/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/tools/.artifacts/app-efficiency-full-20261021T135444884378/planning-layout'` |
| session-finalization | PASS | 58.812 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/finalize_session_test.py` |
| storage-governance | PASS | 8.737 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/storage_governance_test.py` |
| persistence-failure | PASS | 32.467 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/persistence_failure_test.py` |
| persistence-recovery | PASS | 43.993 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/persistence_recovery_test.py` |
| investor-password | PASS | 7.592 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/investor_password_test.py` |
| import-xss | PASS | 77.992 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/import_xss_security_test.py` |
| state-integrity | PASS | 7.521 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/state_integrity_test.py` |
| async-generation | PASS | 5.593 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/async_generation_test.py` |
| build-reproducibility | PASS | 40.431 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/build_reproducibility_test.py` |
| service-worker-upgrade | PASS | 36.702 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/service_worker_upgrade_test.py` |
| mvp-notes | PASS | 64.924 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/mvp_notes_test.py` |
| notes-launcher | PASS | 35.707 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/notes_launcher_test.py --out '/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/tools/.artifacts/app-efficiency-full-20261021T135444884378/notes-launcher.json' --native-zoom` |
| notes-global-launcher | PASS | 23.684 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/notes_global_launcher_test.py --out '/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/tools/.artifacts/app-efficiency-full-20261021T135444884378/notes-global-launcher.json'` |
| notification-center | PASS | 16.043 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/notification_center_test.py` |
| notification-efficiency | PASS | 15.767 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/notification_efficiency_test.py` |
| consolidated-efficiency | PASS | 6.816 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/consolidated_efficiency_test.py --out '/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/tools/.artifacts/app-efficiency-full-20261021T135444884378/consolidated.json'` |
| consolidated-model | PASS | 1.017 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/fx_consolidated_model_test.py` |
| consolidated-storage | PASS | 21.209 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/fx_consolidated_storage_test.py --out '/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/tools/.artifacts/app-efficiency-full-20261021T135444884378/consolidated-storage.json'` |
| consolidated-ui | PASS | 5.693 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/fx_consolidated_ui_test.py --output '/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/tools/.artifacts/app-efficiency-full-20261021T135444884378/consolidated-ui.json'` |
| forex-professional-panel | PASS | 46.775 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/forex_professional_panel_test.py --out '/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/tools/.artifacts/app-efficiency-full-20261021T135444884378/professional-panel' --native-zoom` |
| execution-efficiency | PASS | 15.868 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/forex_execution_efficiency_test.py --artifacts '/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/tools/.artifacts/app-efficiency-full-20261021T135444884378/rows'` |
| execution-table | PASS | 23.529 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/forex_execution_table_test.py --artifacts '/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/tools/.artifacts/app-efficiency-full-20261021T135444884378/table' --native-zoom` |
| execution-workbook | PASS | 38.492 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/forex_execution_workbook_test.py --out '/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/tools/.artifacts/app-efficiency-full-20261021T135444884378/workbook'` |
| execution-proportions | PASS | 27.329 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/forex_execution_proportions_test.py --out '/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/tools/.artifacts/app-efficiency-full-20261021T135444884378/proportions'` |
| forex-context | PASS | 5.748 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/forex_context_bar_test.py --output '/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/tools/.artifacts/app-efficiency-full-20261021T135444884378/context.json'` |
| forex-navigation-journey | PASS | 12.655 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/forex_navigation_journey_test.py --output '/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/tools/.artifacts/app-efficiency-full-20261021T135444884378/journey.json'` |
| learning-guide | PASS | 104.741 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/learning_guide_test.py --out '/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/tools/.artifacts/app-efficiency-full-20261021T135444884378/guide.json' --baseline-root '/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS'` |
| nocuda-tools | PASS | 10.052 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/nocuda_tools_test.py` |
| stoikus-downloads | PASS | 0.702 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/stoikus_download_test.py` |
| download-assets-unit | PASS | 0.048 | `/Users/joaoalvescirqueira/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node tools/download_assets_test.js` |
| download-assets-browser | PASS | 13.955 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/download_assets_browser_test.py --out-dir '/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/tools/.artifacts/app-efficiency-full-20261021T135444884378/downloads'` |
| capital-currents-unit | PASS | 0.238 | `/Users/joaoalvescirqueira/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node tools/capital_currents_unit_test.js` |
| capital-currents-progress | PASS | 0.037 | `/Users/joaoalvescirqueira/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node tools/capital_currents_progress_test.js` |
| capital-currents-browser | PASS | 55.647 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/capital_currents_browser_test.py --mode all --out-dir '/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/tools/.artifacts/app-efficiency-full-20261021T135444884378/capital-currents'` |
| time-twins-unit | PASS | 0.158 | `/Users/joaoalvescirqueira/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node tools/time_twins_unit_test.js` |
| time-twins-browser | PASS | 92.79 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/time_twins_browser_test.py --mode all --out-dir '/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/tools/.artifacts/app-efficiency-full-20261021T135444884378/time-twins'` |
| minigames | PASS | 11.581 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/minigames_test.py` |
