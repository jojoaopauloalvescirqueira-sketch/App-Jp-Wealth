# CHG-JPW-COCKPIT-UI-20260929 — JPW Cockpit 1.8.0, produto

```yaml
schema: jp-harness/chg/v1
change_id: CHG-JPW-COCKPIT-UI-20260929
status: implemented_local_pending_native_and_audit
objective: cockpit legivel e preferencias visuais por grafico para o indicador MT5
risk_level: N2
authority_required: A3
target:
  root: /private/tmp/jpw-alavancagem-atual-20260926
  branch: codex/jpw-alavancagem-atual-20260926
  baseline_sha: f5145b25e86af6b4ccbfef847cba0d84d74e7c8a
derived_from: jpw-alavancagem-atual-20260929-r11
baseline_version: 1.7.0
baseline_build: a5c2908d9fbb832a
baseline_fingerprint: 2395a737dc1b441b8b03594d4b71fddc0cadb539c93748688bcfdae2375b9934
approved_by: Proprietario, pedido PLEASE IMPLEMENT THIS PLAN para JPW Cockpit 1.8.0
```

## Contrato e fronteira

O r11 congelado foi confrontado com a worktree antes da escrita: 77/77 hashes coincidentes. O parecer r11 permanece BLOCKED, com full bruto 50 PASS / 7 PRODUCT_FAIL, focal da pagina falho e compilacao/execucao nativas NOT_RUN. A autorizacao atual e para a interface, nao para alterar formulas, conversoes, estados financeiros, P-21 ou formatos dos registros de MDD, Genese, USC e Raiz N.

Cinco metricas em ingles ficam visiveis por padrao, reunidas num bloco cinza com contraste e espacamento medido, abaixo do cabecalho do instrumento. Cada linha abre seu detalhe; um botao abre o cockpit central temporario. O cockpit tem cartoes de valor/qualidade/motivo, detalhes de formula, insumos, origem, horarios e limites, e uma area de estado dos dados. O EA observador mostra somente a ultima captura conhecida, nunca presenca atual presumida. A interface usa apresentacao tipada e amostra identificada; troca de conta ou simbolo invalida a amostra. A ocultacao visual nao interrompe coleta, qualidade nem gravacao do MDD.

Personalizar permite alternar as cinco linhas, escolher canto e densidade, previsualizar, Aplicar/Cancelar/restaurar padrao. Sem linhas, o botao permanece. A configuracao versionada pertence ao grafico, separada dos registros financeiros; ausencia resulta em cinco linhas e configuracao invalida produz aviso sem apagar bytes anteriores. O usuario pode salvar manualmente um template do MT5; restauracao funcional exige ciclo nativo comprovado e nao sera presumida. Cor e fonte continuam nas Entradas do indicador.

## Preflight, escopo e rollback

`tools/agent_preflight.py --mode audit` passou com aviso de frescor historico; `--mode edit` bloqueou genericamente por 39 alteracoes preexistentes. Isso foi reconciliado pelo snapshot r11 (77/77) e pela autorizacao para derivar nesta mesma branch; nenhuma limpeza, reset ou modificacao da branch foi feita. O aviso nao aprova codigo nem substitui os gates.

Permitidos: indicador, include de apresentacao, testes focais pertinentes, pagina, README, manifesto e derivados oficiais, CHG/ACTIVE-TASK e evidencias externas. O guia `mt5/jpw-alavancagem-atual/AGENTS.md` e tratado em CHG separado. Proibidos: dados de conta real, terminal operacional, ordens, Estatuto/Anexo/Harness, alteracao de quality gate/classificacao, commit, push, merge, deploy, publicacao ou instalacao operacional.

Validar estado visual, eventos, Apply/Cancel, configuracao ausente/corrompida, dois graficos, troca de identidade, independencia financeira, temas/cantos/DPI e grafico estreito. Compilacao e ciclo template so em MT5 isolado. Congelar primeiro o delta de produto, com hashes e diff desde r11, antes de acrescentar o guia. Reversao restaura os bytes r11 do produto; nao toca registros de usuario. Focais e full bruto serao classificados conforme resultado, sem herdar PASS anterior.

## Resultado

Interface e pagina 1.8.0 implementadas localmente. Focais no host: preferencias/limpeza de objetos 1820 PASS / 0 FAIL, eventos 46 PASS / 0 FAIL, geometria 5956 PASS / 0 FAIL e painel sintético 624 asserts / 0 falhas; o focal da pagina passou em HTTP, arquivo local, portatil e PWA offline nos quatro layouts. Esses testes nao substituem compilacao ou interacao no MT5. MetaEditor X64, grafico/DPI/temas/cliques e ciclo de template estao NOT_RUN por falta de ambiente isolado. Snapshot de produto e auditoria independente seguem como recibos externos separados. Human Acceptance e operacoes Git permanecem posteriores.
