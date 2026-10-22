# FULL — pacote final de Planejamento

Build `443c1a59f2c1f46d`; **91/91 PASS** em execução própria, sem herdar o FULL de `d93561c064cf5f40`.

Congelados: 327 inputs oficiais ordenados do fingerprint, inventário separado de 397 caminhos de runtime/recursos, 257 testes e runner. O inventário de 397 caminhos não é a lista completa dos inputs do fingerprint.

Início: 2026-10-20T17:04:44-03:00. Fim: 2026-10-20T17:27:03-03:00.

Exit0 do processo informado pelo root após observá-lo; este script não executa o runner. Todos os 91 checks têm PASS e returncode0. Recibo e hashes em [FULL-RESULT](FULL-RESULT.json).

Não inclui Google autenticado, equivalência de permissões/triggers ou aceite humano.

| Check | Resultado | Duração (s) | Comando |
|---|---|---:|---|
| preflight | PASS | 0.339 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/agent_preflight.py --mode audit --allow-dirty` |
| structure | PASS | 5.045 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/validate_project.py` |
| diff-check | PASS | 0.335 | `git diff --check` |
| preflight-context | PASS | 1.49 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/preflight_context_test.py` |
| navigation-ia | PASS | 5.054 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/navigation_ia_test.py` |
| dashboard-macro | PASS | 32.525 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/dashboard_macro_test.py` |
| research-navigation | PASS | 9.275 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/research_navigation_test.py` |
| smoke | PASS | 9.653 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/smoke_test.py` |
| settings | PASS | 19.254 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/settings_modal_test.py` |
| brand-identity-contract | PASS | 2.755 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/brand_identity_contract_test.py` |
| brand-identity-browser | PASS | 1.416 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/brand_identity_browser_test.py` |
| statute-documentary | PASS | 9.115 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/statute_documentary_test.py` |
| galton-board | PASS | 7.422 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/galton_board_test.py` |
| planning-engine | PASS | 0.829 | `/Users/joaoalvescirqueira/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node tools/planning_engine_test.js` |
| planning-parity-engine | PASS | 0.495 | `/Users/joaoalvescirqueira/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node tools/planning_parity_engine_test.js` |
| planning-state | PASS | 1.572 | `/Users/joaoalvescirqueira/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node tools/planning_state_test.js` |
| planning-navigation | PASS | 0.04 | `/Users/joaoalvescirqueira/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node tools/planning_navigation_test.js` |
| planning-quote | PASS | 0.035 | `/Users/joaoalvescirqueira/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node tools/planning_quote_test.js` |
| planning-boundaries | PASS | 0.032 | `/Users/joaoalvescirqueira/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node tools/planning_boundaries_test.js` |
| planning-ui | PASS | 17.132 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/planning_ui_test.py` |
| planning-parity-ui | PASS | 9.064 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/planning_parity_test.py` |
| planning-reserve-compat | PASS | 2.246 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/fx_planning_test.py` |
| exec-submenu | PASS | 10.822 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/exec_submenu_test.py` |
| nocoda | PASS | 6.293 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/nocoda_test.py` |
| pivot-studies | PASS | 6.396 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/pivot_studies_test.py` |
| order-guards | PASS | 7.394 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/order_guards_test.py` |
| operation-identity | PASS | 2.646 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/operation_identity_test.py` |
| operation-finalize | PASS | 2.693 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/operation_finalize_test.py` |
| operation-history | PASS | 1.636 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/operation_history_test.py` |
| operation-wiring | PASS | 3.955 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/operation_wiring_test.py` |
| phases-visibility | PASS | 1.734 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/phases_visibility_test.py` |
| exec-three-column | PASS | 4.257 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/exec_three_column_test.py` |
| finpes-foundation | PASS | 6.292 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/finpes_foundation_test.py` |
| finpes-finalize-preservation | PASS | 2.978 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/finpes_finalize_preservation_test.py` |
| finpes-backup-roundtrip | PASS | 3.394 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/finpes_backup_roundtrip_test.py` |
| finpes-navigation | PASS | 3.041 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/finpes_navigation_test.py` |
| finpes-budget | PASS | 17.372 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/finpes_budget_test.py` |
| finpes-debt-credit | PASS | 13.995 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/finpes_debt_credit_test.py` |
| finpes-comparison | PASS | 8.837 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/finpes_comparison_test.py` |
| finpes-scenarios | PASS | 32.948 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/finpes_scenarios_test.py` |
| finpes-overview | PASS | 7.391 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/finpes_overview_test.py` |
| usd-brl-quote | PASS | 11.387 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/usd_brl_quote_test.py` |
| alladin-unit | PASS | 0.663 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/alladin_unit_test.py` |
| alladin-ledger | PASS | 0.533 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/alladin_ledger_test.py` |
| alladin-position | PASS | 0.424 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/alladin_position_test.py` |
| alladin-foundation | PASS | 24.492 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/alladin_foundation_test.py` |
| alladin-finalize-preservation | PASS | 34.339 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/alladin_finalize_preservation_test.py` |
| session-epoch-protocol | PASS | 17.327 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/session_epoch_protocol_test.py` |
| session-write-serialization | PASS | 20.205 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/session_write_serialization_test.py` |
| alladin-ui-readonly | PASS | 6.96 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/alladin_ui_readonly_test.py` |
| alladin-ui-crud | PASS | 44.748 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/alladin_ui_crud_test.py` |
| alladin-ui-ledger | PASS | 26.628 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/alladin_ui_ledger_test.py` |
| alladin-ui-tx-write | PASS | 14.169 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/alladin_ui_tx_write_test.py` |
| alladin-ui-tx-reverse | PASS | 9.946 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/alladin_ui_tx_reverse_test.py` |
| planning-distribution | PASS | 5.525 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/planning_distribution_test.py` |
| planning-parity-layout | PASS | 17.471 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/planning_parity_layout_test.py --out '/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/tools/.artifacts/app-efficiency-full-20261020T170444035334/planning-layout'` |
| session-finalization | PASS | 52.321 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/finalize_session_test.py` |
| storage-governance | PASS | 8.32 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/storage_governance_test.py` |
| persistence-failure | PASS | 30.875 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/persistence_failure_test.py` |
| persistence-recovery | PASS | 43.268 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/persistence_recovery_test.py` |
| investor-password | PASS | 6.905 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/investor_password_test.py` |
| import-xss | PASS | 72.512 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/import_xss_security_test.py` |
| state-integrity | PASS | 7.882 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/state_integrity_test.py` |
| async-generation | PASS | 5.772 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/async_generation_test.py` |
| build-reproducibility | PASS | 35.138 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/build_reproducibility_test.py` |
| service-worker-upgrade | PASS | 23.607 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/service_worker_upgrade_test.py` |
| mvp-notes | PASS | 51.19 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/mvp_notes_test.py` |
| notification-center | PASS | 15.455 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/notification_center_test.py` |
| notification-efficiency | PASS | 15.554 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/notification_efficiency_test.py` |
| consolidated-efficiency | PASS | 7.22 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/consolidated_efficiency_test.py --out '/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/tools/.artifacts/app-efficiency-full-20261020T170444035334/consolidated.json'` |
| consolidated-model | PASS | 1.04 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/fx_consolidated_model_test.py` |
| consolidated-storage | PASS | 17.246 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/fx_consolidated_storage_test.py --out '/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/tools/.artifacts/app-efficiency-full-20261020T170444035334/consolidated-storage.json'` |
| consolidated-ui | PASS | 4.162 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/fx_consolidated_ui_test.py --output '/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/tools/.artifacts/app-efficiency-full-20261020T170444035334/consolidated-ui.json'` |
| forex-professional-panel | PASS | 36.957 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/forex_professional_panel_test.py --out '/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/tools/.artifacts/app-efficiency-full-20261020T170444035334/professional-panel' --native-zoom` |
| execution-efficiency | PASS | 13.055 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/forex_execution_efficiency_test.py --artifacts '/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/tools/.artifacts/app-efficiency-full-20261020T170444035334/rows'` |
| execution-table | PASS | 19.383 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/forex_execution_table_test.py --artifacts '/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/tools/.artifacts/app-efficiency-full-20261020T170444035334/table' --native-zoom` |
| execution-workbook | PASS | 38.067 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/forex_execution_workbook_test.py --out '/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/tools/.artifacts/app-efficiency-full-20261020T170444035334/workbook'` |
| execution-proportions | PASS | 26.509 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/forex_execution_proportions_test.py --out '/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/tools/.artifacts/app-efficiency-full-20261020T170444035334/proportions'` |
| forex-context | PASS | 5.179 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/forex_context_bar_test.py --output '/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/tools/.artifacts/app-efficiency-full-20261020T170444035334/context.json'` |
| forex-navigation-journey | PASS | 12.587 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/forex_navigation_journey_test.py --output '/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/tools/.artifacts/app-efficiency-full-20261020T170444035334/journey.json'` |
| learning-guide | PASS | 103.158 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/learning_guide_test.py --out '/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/tools/.artifacts/app-efficiency-full-20261020T170444035334/guide.json' --baseline-root '/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS'` |
| nocuda-tools | PASS | 9.811 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/nocuda_tools_test.py` |
| stoikus-downloads | PASS | 0.705 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/stoikus_download_test.py` |
| download-assets-unit | PASS | 0.051 | `/Users/joaoalvescirqueira/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node tools/download_assets_test.js` |
| download-assets-browser | PASS | 13.956 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/download_assets_browser_test.py --out-dir '/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/tools/.artifacts/app-efficiency-full-20261020T170444035334/downloads'` |
| capital-currents-unit | PASS | 0.228 | `/Users/joaoalvescirqueira/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node tools/capital_currents_unit_test.js` |
| capital-currents-progress | PASS | 0.037 | `/Users/joaoalvescirqueira/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node tools/capital_currents_progress_test.js` |
| capital-currents-browser | PASS | 56.445 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/capital_currents_browser_test.py --mode all --out-dir '/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/tools/.artifacts/app-efficiency-full-20261020T170444035334/capital-currents'` |
| time-twins-unit | PASS | 0.172 | `/Users/joaoalvescirqueira/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node tools/time_twins_unit_test.js` |
| time-twins-browser | PASS | 81.998 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/time_twins_browser_test.py --mode all --out-dir '/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/tools/.artifacts/app-efficiency-full-20261020T170444035334/time-twins'` |
| minigames | PASS | 8.464 | `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 tools/minigames_test.py` |
