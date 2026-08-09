# Testes

## Gate recomendado

```bash
python3 tools/quality_gate.py --tier fast
python3 tools/quality_gate.py --tier standard
python3 tools/quality_gate.py --tier full
```

O relatorio JSON fica em `tools/.artifacts/` e nao e versionado. Consulte `docs/governance/QUALITY-GATES.md` para a taxonomia de resultados.

## Suites

- `validate_project.py`: arquivos obrigatorios, manifest/hashes/ordem, sintaxe JS, PWA, IDs e rebuild portatil.
- `smoke_test.py`: boot real, quatro telas operacionais, onboarding, reset, dashboard, configuracoes e Notas.
- `finalize_session_test.py`: checkpoint, backup, exclusao seletiva, corrida assincrona, multiplas abas e responsividade.
- `settings_modal_test.py`: sete categorias, subpaginas, busca, foco, modal e mobile.
- `storage_governance_test.py`: pasta, sequencia, backup e estado de governanca.
- `persistence_failure_test.py`: falhas de leitura/escrita e aviso persistente.
- `persistence_recovery_test.py`: modo de recuperacao e importacao valida/invalida.
- `service_worker_upgrade_test.py`: precache, troca de build e cache antigo.
- `mvp_notes_test.py`: CRUD, pastas, filtros, inspector, exportacao e layout.

## Regra

Atualizar uma expectativa exige prova de que o contrato do produto mudou deliberadamente. Nao reduzir assertions para esconder `PRODUCT_FAIL`. Falta de Node, Playwright ou Chromium e `ENVIRONMENT_ERROR`, nunca PASS.
