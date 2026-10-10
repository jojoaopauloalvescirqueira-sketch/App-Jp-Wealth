# CHG JPW-BEHAVIOR-DRAFTS-20261008

Risco/autoridade: N2/A3.
Autorizacao: Pedido humano nesta conversa: corrige todas as falhas, implemente todas as melhorias, e refaca os testes e auditoria. Registro do reconhecimento desta autorizacao, nao aceite do candidate final.

Raiz: /private/tmp/jpw-behavior-fixes-20261008/candidate
Branch herdada: codex/onboarding-first-access-20261007; HEAD/base 7f0828488b2fc0ea62dc7c421174799cda47a34a; sem criacao/troca de branch.
Baseline de produto f70839305b2d7fb8, 874 hashes e20 alteracoes preexistentes preservadas fora deste candidate.

## Contrato delimitado

DATA-PF-001: preservar texto e recuperacao sob REFUSED/UNKNOWN; confirmar apenas pelo writer atual. UI-01: orientar cobertura Backup Completo/Markdown e Finalizar corretamente.

Arquivos permitidos: ["src/js/20-ui/18-finpes-budget.js", "index.html", "README.md", "CHANGELOG.md", "tools/behavior_draft_recovery_regression_test.py"]. TESTS e produto tem autores separados; a notacao de familias de teste nao concede alteracao de gates/instrucoes. Cada arquivo realmente alterado sera listado no diff e no recibo.

## Invariantes e efeitos

Somente dados sinteticos. Sem novas formulas, schema financeiro, DEFAULTS, migracao, dados reais, credenciais, programacao/instalacao MT5, Git ou publicacao. Preservar vazio/zero/ausencia, fontes, contexto, contratos CONFIRMED/REFUSED/UNKNOWN, recuperacao, historico e guardas. Geradores oficiais somente apos coordenacao; sem edicao manual de derivados.

## Aceite e teste

Reproduzir baseline vermelho; provar fluxo real no candidate, recusas/recarga, contexto concorrente e zero escrita por consulta. Comparar mesmas entradas com produtores atuais. Testes focais, full bruto/standard e auditoria independente nos bytes finais. Criterios que exigem MT5/Safari/AT fisicos ficam NOT_RUN sem prova propria, nunca PASS inferido.

## Rollback

Restaurar apenas o delta desta tarefa a partir de baseline-snapshot.tar.gz, preservando as20 alteracoes anteriores e o candidate original intacto. Sem restauracao de dados reais, limpeza de localStorage ou rollback automatico. Historico de tentativas brutas preservado. Aceite humano e Git/publicacao permanecem etapas separadas.

Documentacao informativa das mesmas correcoes em README/CHANGELOG: texto nao altera autoridade, regra, source of truth ou criterios de aceite. A reconciliacao agêntica de arquivos canonicos docs tem CHG N3 separado.
