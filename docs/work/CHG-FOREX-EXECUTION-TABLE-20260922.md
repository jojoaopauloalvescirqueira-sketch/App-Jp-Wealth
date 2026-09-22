# Execution Board — contrato de implementação

```yaml
schema: jp-harness/chg/v1
change_id: CHG-FOREX-EXECUTION-TABLE-20260922
status: approved
objective: Reorganizar Forex e entregar Execution Board tabular conforme plano confirmado.
risk_level: N3
authority_required: A4
target:
  root: /Users/joaopauloalves/.codex/forex-execution-board-table/20260922/product
  branch: codex/forex-execution-board-table-20260922
  baseline_sha: a62258f1a1ca5b0e32ea9f36bb4106fba37e4414
scope:
  allowed_files:
    - index.html
    - src/styles/app.css
    - src/js/10-domain/00-forex-engine.js
    - src/js/10-domain/00-forex-state.js
    - src/js/10-domain/11-operation-lifecycle.js
    - src/js/10-domain/18-execution-board-model.js
    - src/js/40-app/11-operational-shell.js
    - src/js/20-ui/13-exec-views.js
    - src/js/20-ui/30-execution-board.js
    - src/js/40-app/01-navigation.js
    - src/js/manifest.json
    - Validadores de estado e apresentação de histórico estritamente relacionados ao contrato aditivo
    - Suites focais e fixtures sintéticas afetadas em tools
    - docs/architecture/FOREX-EXECUTION-BOARD.md
    - docs/architecture/NAVIGATION-HIERARCHY.md
    - docs/architecture/STATE-SCHEMA.md
    - docs/governance/CURRENT-STATE.md
    - docs/work/ACTIVE-TASK.md
    - docs/work/CHG-FOREX-EXECUTION-TABLE-20260922.md
  forbidden_files: [AGENTS.md, CLAUDE.md, docs/normative, skills, tools/quality_gate.py, CI]
  allowed_actions: [edit, test, review, generate_official_artifacts]
  forbidden_actions: [commit, push, merge, deploy, reset, stash]
derived_artifacts:
  allowed: [build-id.js, dist, manifest]
  generation_commands: [python3 tools/rebuild_monolith.py]
  manual_edit: forbidden
data:
  test_policy: synthetic_only
  schema_change: approved
approved_by: Proprietário, aprovação conversacional explícita do plano integral
approved_at: mensagem PLEASE IMPLEMENT THIS PLAN desta tarefa
```

## Compreensão e fontes

JP Wealth é aplicação local de gestão operacional e risco. Forex distingue registro factual e elegibilidade; a mudança melhora o preenchimento sem ativar normas. Navegação compartilha nós/controladores em quatro layouts; projeção lê domínio; writers transacionais protegem estado/backup/histórico.

Fontes lidas na base: AGENTS, README, CONTEXT-MAP, FOREX-V11-ENGINE, FOREX-EXECUTION-BOARD, Anexo P03/P11/P21/P22. Harness localizado na pasta `B - Suma & Estudo/99 Prompts & Skills/99B - SOFTWARE DEV`, arquivo `A0 - HARNESS - JP Wealth MASTER SPECIFICATION.md`, §§12–14,24,28–30,36–49; SHA256 `c1b5ca9da4dfa2c9a9d1fa3d87a9f7ef9c4cb741fffeedee33d37978f5b800c8`.

Antes: quatro destinos Forex; histórico em Contabilidade; ID sem HASH; percentuais SI; alavancagem min(SI,equity); ATR atual/stop; Raiz-N indisponível. Depois: Dashboard, Execution Board, History, Contabilidade, Management Accounts (Contas/Fator de Correção), Planejamento, Reservas. Blocos por fases atuais; histórico só operações finalizadas.

Decisão financeira citável: plano integral aprovado, após respostas específicas. Hard Stop SI×0,78+fluxo conciliado; exposição só abertas/saldo atual; compensada só resultado líquido DEFENSE; nocional/saldo separado da leitura normativa; ATR entrada/stop; VRM55/660; Raiz-N ATR55×sqrt(N)×F com N/F declarados, sem defaults. Política, tetos, RC, reservas e admissão preservados.

HASH textual por linha; ID/HASH exigidos em novas ordens abertas/fechadas; HASH pode aguardar em pendentes; legado preservado. Diagnósticos opcionais separados de observações, por conta/período/instrumento, revisionados. Schemas existentes preservados; extensão diagnóstica v1, backup antigo válido, inválidos recusados antes da escrita, snapshots sem reconstruir passado.

## Validação e rollback

Oráculos: SI10.000→7.800; saldo12.000/nocional24.000→2x; risco600→5%; defesa200→400/3,333%; OTHER500 não compensa; entrada1,10/SL1,08/ATR0,005→4x; ATR0,002/N25/F1,5→0,015 e 1,25% com entrada1,20. Testar sinais/câmbio/custos/ausências, IDs, legado, reload, backup, recusa/conflito/UNKNOWN, rascunhos e quatro layouts. Focais, full, PWA/portátil e auditoria independente; capturas sintéticas desktop/mobile.

Rollback apenas delta desta branch/base; sem dados reais, outras worktrees ou fontes normativas. Candidate técnico não é aceite visual, integração ou publicação. Atualizar apenas contratos e contexto afetados, sem control plane ou reindexação. Preflight material-freshness anterior é evidência histórica, não falha nova do recurso.


## Avaliação de impacto do contexto agentivo

Impacto material e limitado: navegação Forex, identidade por linha, projeções econômicas, diagnóstico e backup. Reconciliar somente `FOREX-EXECUTION-BOARD`, `STATE-SCHEMA`, `NAVIGATION-HIERARCHY` e `CURRENT-STATE`, mantendo as fotografias históricas identificadas. Gate, instruções, CI, fontes normativas e parâmetros permanecem sem alteração. O aviso histórico de freshness do preflight existe no baseline; a avaliação desta entrega não declara reconciliação geral dos 242 caminhos nem homologação financeira.

O manifesto mantém ordem e arquivos; hashes são atualizados a partir dos fontes. `rebuild_monolith.py` regenera build e portátil. Nenhuma dependência/ativo remoto novo.


### Correção de retorno de gravação durante validação

A suite de persistência encontrou no baseline a62258f seis casos em que o writer contextual Forex marcava UNKNOWN, mas deixava visível a confirmação anterior de gravação. O writer compartilhado pelas linhas e diagnósticos agora chama `hideStaleSavedTag` ao recusar/indeterminar a gravação, sem alterar rollback, journal, epoch ou estado financeiro. Recibos baseline em `evidence/persistence-triage/`; as 42 contraprovas passaram sem enfraquecer asserções. A correção integra o contrato aprovado de feedback fiel de salvamento.


## Evidências do candidate local

Build congelado `247bf13458098290`, base `a62258f1a1ca5b0e32ea9f36bb4106fba37e4414`. Fontes/artefatos e recibos em `~/.codex/forex-execution-board-table/20260922/evidence/`. Nenhum commit, push, merge ou publicação nesta etapa; esta tarefa não alterou a main.

- Motor:65/65; projeção:116/116; histórico Node:17/17. Recibos finais em `final-identity-finalization/` com hashes antes/depois.
- Identidade/diagnóstico:14 contratos VM e browser ponta a ponta: writers reais, finalização com FECHADO, HASH textual longo, snapshot N/F, History sem escritas, recarga e backup/importação em sessão limpa.
- Persistência:42/42 após correção da indicação de salvo. `persistence-triage/candidate-confirmed-feedback.json`; teste idêntico ao recibo36/42 anterior. Baselines e tentativas anteriores preservados.
- Navegação: sete destinos nos quatro layouts; jornada54/54, guardas reais de rascunho; Settings/checklist restauram foco após evento assíncrono. Novos focais não tornam a aprovação do layout anterior aprovação deste recurso.
- UI: matriz7larguras×2temas com tabela real, overflow interno e cabeçalhos/ID fixos; teclas Tab/Shift+Tab, recusa/conflito, zoom nativo200%. `table-release/` e `table-final-check/`; capturas finais de revisão em `review/`, dados sintéticos.
- Backup Completo modular/portátil e tabela `file://` offline:PASS. Reprodutibilidade e ciclo PWA online/offline incluídos no gate. Fonte e ordem do manifesto preservadas; artefatos gerados oficialmente.
- Revisões independentes cruzadas: `independent-engine-ui-review.md`, `independent-state-navigation-review.md` e revisão da correção de confirmação. Nenhum finding material pendente do delta; revisão técnica não substitui aceite visual humano.

A primeira full (46/57) encontrou hashes de manifesto ainda não regenerados, quatro fixtures sem o novo HASH e boots HTTP parciais. Manifesto e fixtures foram corrigidos sem enfraquecer asserções. Segunda rodada (51/57) e rodada congelada (54/57) tiveram falhas variáveis de bootstrap. As falhas congeladas de Alladin foram confrontadas com main/reexecução intacta; módulos inalterados também apresentaram scripts ausentes. Relatórios brutos mantêm PRODUCT_FAIL; a triagem externa distingue falha de carregamento do oráculo funcional, sem declarar esses relatórios verdes.

A última execução usa os mesmos testes/gate com ambiente de servidor HTTP sintético ajustado de backlog5 para128 via `sitecustomize.py` externo. Não modifica testes, produto ou gates, não ignora erros nem desativa asserções. Motivo e hash em `controlled-server/environment.json`. Resultado bruto: 54 PASS, 2 NOT_RUN e 1 PRODUCT_FAIL. Durante a execução, a pasta principal mudou de `6J - SOFTWAREs, EAS` para `6 - SOFTWAREs, EAS`, deixando inválido o ponteiro Git da worktree. O histórico continuava presente: o erro dos testes que dizia clone raso era consequência do acesso Git quebrado. Após conferir branch, HEAD e o registro recíproco, foi reparado somente o ponteiro `.git` desta worktree. Os três checks afetados (alladin-foundation, session-epoch-protocol e build-reproducibility) passaram em reexecução intacta, no mesmo build. Recibos em `worktree-location-repair.json` e `worktree-location-recheck/`. Há evidência de aprovação para os 57 checks, mas nenhuma rodada única full 57/57 é declarada. O relatório bruto permanece preservado.

Limitações herdadas fora do delta: a suite antiga `forex_execution_board_test` semeia `S.phases` global sem contexto; `forex_execution_market_test` tem uma expectativa de seleção incompatível já no baseline (30/31 nos dois); `forex_v11_history_test --browser` semeia contas/períodos diferentes da seleção. Esses casos não são contados como PASS. O novo focal tabular e a finalização real cobrem os fluxos atuais; não houve alteração desses oráculos antigos para ocultar falhas.


## Fechamento técnico e entrega

Candidate local concluído para revisão visual, build `247bf13458098290`. A revisão documental final corrigiu a descrição do snapshot: N/F é capturado ao registrar/corrigir a ordem e a finalização conserva a última versão confirmada. Testes numéricos, identidade, persistência, navegação, tabela, Backup Completo e PWA possuem recibos; os três oráculos legados mencionados acima permanecem classificados, sem alegação de aprovação. Fingerprint final externo em `evidence/candidate-inputs.json`; consolidação em `evidence/final-validation.json`. Aprovação visual, integração Git e publicação continuam separadas. A main manteve HEAD `a62258f`; alterações documentais e mudança de pasta observadas nela durante o trabalho são externas a esta implementação e foram preservadas.

## Integração Git autorizada posteriormente

Em solicitação posterior, o proprietário autorizou expressamente commit, merge e push desta entrega. O candidate foi registrado em `346e701` e publicado na branch `codex/forex-execution-board-table-20260922`. Essa autorização posterior substitui apenas a proibição de ações Git da fase inicial; publicação do aplicativo e homologação financeira permanecem fora do escopo. O estado final da integração é verificado pelas referências Git, sem incorporar as alterações documentais preexistentes da pasta principal.
