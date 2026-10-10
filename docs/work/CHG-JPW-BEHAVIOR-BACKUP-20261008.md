# CHG JPW-BEHAVIOR-BACKUP-20261008

Risco/autoridade: N2/A3. Autorizacao humana: corrigir todas as falhas e refazer testes/auditoria nesta conversa.
Base preservada: f70839305b2d7fb8, HEAD 7f0828488b2fc0ea62dc7c421174799cda47a34a. Candidate isolado /private/tmp/jpw-behavior-fixes-20261008/candidate.

## DATA-PF-003 — identidade na restauracao

O Backup Completo v2 exportava exatamente os dados, mas preservar extensoes por id vazio/repetido duplicava orderId e revisoes entre ordens. Identidade so sera usada se escalar nao vazia e unica nas duas listas. Itens anonimos ou ambiguos usam posicao somente com as guardas existentes de comprimento, campos compartilhados e fronteira de schema. Nao inferir identidade por label nem fabricar fatos.

Arquivos: src/js/30-accounting/01-daily-ledger.js (helper dgBackupPreserveCompatibleFields) e tools/behavior_backup_field_preservation_regression_test.py. Sem formulas, schema, MT5, dados reais, Git ou publicacao.

Aceite: 12 casos novos, contraprovas de id vazio/repetido/unico/reordenado e schema, roundtrip v2 exato pelo exportador/restaurador reais e recarga; revisao independente. Antes: 7 PRODUCT_FAIL preservados. Candidate: 12 PASS a repetir nos bytes finais.

Rollback: restaurar delta pelo snapshot baseline-snapshot.tar.gz externo, preservando as 20 alteracoes anteriores. Nenhuma restauracao automatica de dados do usuario.
