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
- `settings_modal_test.py`: oito categorias, subpaginas, busca, foco, modal e geometria mobile.
- `galton_board_test.py`: PRNG, geometria, estatistica, binomial, colisao Planck,
  passo fixo, reproducibilidade, persistencia isolada, UI, `Enter`/`Space` em
  controles nativos, consolidacao por `Tab`, tabela de bins focalizavel e lifecycle;
  nao representa uma navegacao integral do modal somente por teclado.
- `storage_governance_test.py`: pasta, sequencia, backup e estado de governanca.
- `persistence_failure_test.py`: falhas de leitura/escrita e aviso persistente.
- `persistence_recovery_test.py`: modo de recuperacao e importacao valida/invalida.
- `service_worker_upgrade_test.py`: precache, descoberta real do worker novo pelo
  bootstrap do produto (sem `registration.update()` disparado pelo harness), cliente
  transitório com HTML novo/controller antigo, `waiting` conservador, troca após o
  fechamento de todos os clientes, abertura online/offline e preservação de cache
  externo.
- `mvp_notes_test.py`: CRUD, pastas, filtros, inspector, exportacao e layout.
- `investor_password_test.py`: ausencia da senha em storage, checkpoint, backup e migracao.
- `import_xss_security_test.py`: importacao hostil nao executa nem persiste markup.
- `async_generation_test.py`: callbacks antigos nao recriam estado apos wipe.
- `build_reproducibility_test.py`: build ID e portatil derivam das fontes oficiais.
- `preflight_context_test.py`: frescor material TRUE/FALSE/UNKNOWN.

Composicao vigente: `fast` 4 verificacoes, `standard` 7 e `full` 17. O teste do
Galton Board integra `standard`; portanto tambem integra `full`.

## Benchmark longo do Galton Board

```bash
python3 tools/galton_board_benchmark.py
```

Executa 10.000 bolas em lotes deterministas de 500. O gate funcional exige todas as
bolas assentadas, zero expiracao/rejeicao, fila e corpos dinamicos zerados, teto de
240 corpos ativos e histograma de 11 bins. Tempo e bolas/segundo sao apenas
diagnosticos e o benchmark nao substitui os tiers.

## Regra

Atualizar uma expectativa exige prova de que o contrato do produto mudou deliberadamente. Nao reduzir assertions para esconder `PRODUCT_FAIL`. Falta de Node, Playwright ou Chromium e `ENVIRONMENT_ERROR`, nunca PASS.
