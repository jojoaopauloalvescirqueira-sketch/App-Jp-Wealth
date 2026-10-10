# CHG JPW-BEHAVIOR-LAYOUT-20261008

Risco/autoridade: N1/A2.
Autorizacao: pedido humano corrente de corrigir falhas e implementar melhorias com testes e auditoria.
Raiz: /private/tmp/jpw-behavior-fixes-20261008/candidate. Baseline f70839305b2d7fb8, HEAD7f0828488b2fc0ea62dc7c421174799cda47a34a;20alteracoes/874hashes preservados na origem.

## Contrato delimitado

UI-02/03, descobertos em contraprovas isoladas: conter o texto sr-only da tabela Contabilidade no contêiner local; permitir que a grade de Aparencia encolha à largura útil sem cortes. Somente seletores locais. Sem reorganizacao ampla, formulas, schema, autosave, preferencia nova, autoridade normativa, MT5 ou dados reais.

Arquivos permitidos: ["src/styles/app.css", "tools/behavior_layout_regression_test.py"]. Derivados somente pelos geradores oficiais (validate_project.py/build.py), sem edicao manual. Testes antigos só podem ser reconciliados pelo CHG TESTS separado; nenhum gate/classificador editado.

## Aceite

Baseline vermelho, contraprova descartavel e candidate verde. Desktop/mobile,320/390/768/1440CSSpx, quatro layouts, claro/escuro, teclado/foco, controles/valores completos e zero escrita provocada por layout. Zoom nativo, toque fisico e tecnologias assistivas NOT_RUN sem prova propria. Auditoria independente dos deltas e focais/full bruto nos bytes finais.

## Rollback

Restaurar somente o delta especifico do snapshot baseline, preservando os20deltas herdados. Sem rollback de dados pessoais, Git, instalacao ou publicacao. Evidencias anteriores e resultados intermediarios ficam preservados.
