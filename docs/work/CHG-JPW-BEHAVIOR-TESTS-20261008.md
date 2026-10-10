# CHG JPW-BEHAVIOR-TESTS-20261008

Risco/autoridade: N3/A4.
Autorizacao: Pedido humano nesta conversa: corrige todas as falhas, implemente todas as melhorias, e refaca os testes e auditoria. Registro do reconhecimento desta autorizacao, nao aceite do candidate final.

Raiz: /private/tmp/jpw-behavior-fixes-20261008/candidate
Branch herdada: codex/onboarding-first-access-20261007; HEAD/base 7f0828488b2fc0ea62dc7c421174799cda47a34a; sem criacao/troca de branch.
Baseline de produto f70839305b2d7fb8, 874 hashes e20 alteracoes preexistentes preservadas fora deste candidate.

## Contrato delimitado

Reparar apenas fixtures, dependencias, sincronizacao e expectativas comprovadamente superadas por contratos ja aprovados. Manter cenarios, oraculos validos e classificadores; registrar antes/depois e revisao independente. Sem quality_gate.py, CI ou validadores alterados.

Arquivos permitidos: ["tools/*_test.py", "tools/*_test.js", "tools/browser_fixture_server.py", "tools/personal_history_host/ui_cases.cpp", "tools/fixtures/saving_persistence_integrity_probe.js"]. TESTS e produto tem autores separados; a notacao de familias de teste nao concede alteracao de gates/instrucoes. Cada arquivo realmente alterado sera listado no diff e no recibo.

## Invariantes e efeitos

Somente dados sinteticos. Sem novas formulas, schema financeiro, DEFAULTS, migracao, dados reais, credenciais, programacao/instalacao MT5, Git ou publicacao. Preservar vazio/zero/ausencia, fontes, contexto, contratos CONFIRMED/REFUSED/UNKNOWN, recuperacao, historico e guardas. Geradores oficiais somente apos coordenacao; sem edicao manual de derivados.

## Aceite e teste

Reproduzir baseline vermelho; provar fluxo real no candidate, recusas/recarga, contexto concorrente e zero escrita por consulta. Comparar mesmas entradas com produtores atuais. Testes focais, full bruto/standard e auditoria independente nos bytes finais. Criterios que exigem MT5/Safari/AT fisicos ficam NOT_RUN sem prova propria, nunca PASS inferido.

## Rollback

Restaurar apenas o delta desta tarefa a partir de baseline-snapshot.tar.gz, preservando as20 alteracoes anteriores e o candidate original intacto. Sem restauracao de dados reais, limpeza de localStorage ou rollback automatico. Historico de tentativas brutas preservado. Aceite humano e Git/publicacao permanecem etapas separadas.
