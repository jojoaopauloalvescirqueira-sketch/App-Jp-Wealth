# CHG JPW-BEHAVIOR-FINANCE-20261008

Risco/autoridade: N2/A3.
Autorizacao: Pedido humano nesta conversa: corrige todas as falhas, implemente todas as melhorias, e refaca os testes e auditoria. Registro do reconhecimento desta autorizacao, nao aceite do candidate final.

Raiz: /private/tmp/jpw-behavior-fixes-20261008/candidate
Branch herdada: codex/onboarding-first-access-20261007; HEAD/base 7f0828488b2fc0ea62dc7c421174799cda47a34a; sem criacao/troca de branch.
Baseline de produto f70839305b2d7fb8, 874 hashes e20 alteracoes preexistentes preservadas fora deste candidate.

## Contrato delimitado

FIN-01/02/03: consulta explicita de conta e periodo; confirmacao de depositos ACTUAL; reservas canonicas. FIN-04, descoberto na contraprova independente: preservar o pico da fase observado na mesma conta/periodo ao confirmar equity, inclusive antes de recuperacao; rollback e ausencia sem inventar observacoes. FIN-05, contraprova da anulação: preservar o motivo humano sem sobrescrevê-lo pela razão transitória da seleção. FIN-06: conciliar o comprovante histórico integral com as linhas confirmadas anuladas ou Migrada; manter intactos os filtros financeiros, net, cronologia, scope, hash e igualdade exata de fatos. Sem formula, schema, norma, ativacao operacional ou guarda enfraquecida.

Arquivos permitidos: ["src/js/30-accounting/01-daily-ledger.js", "src/js/30-accounting/05-fx-planning/03-fx-state.js", "src/js/30-accounting/05-fx-planning/05-fx-ui.js", "tools/behavior_finance_regression_test.py", "src/js/00-core/04-persistence.js", "src/js/10-domain/00-forex-state.js", "tools/behavior_account_phase_capture_regression_test.py", "src/js/10-domain/11-operation-lifecycle.js", "tools/behavior_void_reason_regression_test.py", "tools/behavior_finalization_trace_regression_test.py"]. TESTS e produto tem autores separados; a notacao de familias de teste nao concede alteracao de gates/instrucoes. Cada arquivo realmente alterado sera listado no diff e no recibo.

## Invariantes e efeitos

Somente dados sinteticos. Sem novas formulas, schema financeiro, DEFAULTS, migracao, dados reais, credenciais, programacao/instalacao MT5, Git ou publicacao. Preservar vazio/zero/ausencia, fontes, contexto, contratos CONFIRMED/REFUSED/UNKNOWN, recuperacao, historico e guardas. Geradores oficiais somente apos coordenacao; sem edicao manual de derivados.

## Aceite e teste

Reproduzir baseline vermelho; provar fluxo real no candidate, recusas/recarga, contexto concorrente e zero escrita por consulta. Comparar mesmas entradas com produtores atuais. Testes focais, full bruto/standard e auditoria independente nos bytes finais. Criterios que exigem MT5/Safari/AT fisicos ficam NOT_RUN sem prova propria, nunca PASS inferido.

## Rollback

Restaurar apenas o delta desta tarefa a partir de baseline-snapshot.tar.gz, preservando as20 alteracoes anteriores e o candidate original intacto. Sem restauracao de dados reais, limpeza de localStorage ou rollback automatico. Historico de tentativas brutas preservado. Aceite humano e Git/publicacao permanecem etapas separadas.
