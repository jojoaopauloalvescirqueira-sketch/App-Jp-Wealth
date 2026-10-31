# CHG — consumidores do pacote único e progresso — 31/10/2026

Control plane N3/A4 delimitado: autorização recebida nesta conversa, pelo coordenador após interromper o FULL da worktree, para adaptar todos os consumidores de teste afetados pelo ZIP e pela cobertura workspace3 já aprovados. Este registro não cria autoridade. Branch `codex/backup-unificado-20261031`, base `69b6cb677de2486be5c30681e4b2e02d4180d704`. Sem produto, cálculo, schema produtor, personalidade de Dante, fontes de outras frentes, runner/gates ou Git/publicação. Preservar trabalho anterior e resultados brutos.

## Problema e responsabilidade

O aplicativo mantém fatos financeiros confirmados; o backup transporta esses fatos, preferências/progresso separados e originais. `dgBuildBackupBlob` continua JSON para leitores legados/diretos. A entrega padrão por `exportFullBackup` é ZIP. Testes que liam o download como UTF-8/JSON ou procuravam marcadores na representação numérica do último Blob não inspecionavam mais o artefato correto. Guide/Capital ainda proibiam a cobertura agora aprovada. Tempo adicional de validação pertence a esta adaptação de formato, sem mudança financeira.

Fontes: `COMPLETE-BACKUP.md` atual (workspace3, quatro famílias e legado opaco), `LEARNING-GUIDE.md`, `TIME-TWINS.md`, `CAPITAL-CURRENTS.md`, `PLANNING.md` com notas atuais e históricos preservados; código do workspace/ledger apenas como evidência; consumidores e hooks reais de entrega. As notas datadas esclarecem que os raws confirmados de Dante, Time Twins e Capital novo pertencem a `workspace.preferences`; Capital legado é somente consulta opaca, sem aplicação/ativação. Importar restaura snapshot confirmado e não concede novos marcos. Validações financeiras/engines e evidências históricas permanecem.

## Escopo e invariantes

Consumidores: `learning_guide_test.py`, `capital_currents_browser_test.py`, `planning_distribution_test.py`, `finpes_backup_roundtrip_test.py`, `management_distribution_test.py`, `mvp_notes_test.py`, `onboarding_first_access_test.py`, `backup_import_audit_test.py`, `session_epoch_protocol_test.py` (E14) e `session_write_serialization_test.py` (SA2). Helper novo somente de testes: `backup_package_fixture.py`, usando zipfile/hashlib da biblioteca padrão, leitura independente do container efetivamente entregue e seus hashes/CRC. Acrescentar helper aos fingerprints existentes pertinentes; os consumidores sem recibo próprio são vinculados pelo recibo externo de execução.

Preservar assertions de domínio, dinheiro/null/extensões, rascunhos, reload, importação real, isolamento, epoch, origem DISCO versus RAM, segredos e não-zero. Roundtrips passam a importar os bytes ZIP reais; casos que fabricam JSON legado continuam JSON. E14/SA2 capturam no hook `dgDownloadViaAnchor(filename,blob)`, não no construtor de Blob. Contraprovas de conteúdo atuam depois da decodificação válida para falharem pelo oráculo correspondente, sem usar checksum inválido como substituto.

Guia exporta raw exato, separado de estado financeiro, sem alterar seu progresso; importação restaura o snapshot confirmado de guia, distinto do progresso posterior do destino, mantendo pausa/invalidação de prática pendente. Capital compara raw novo exato e legado opaco recuperável, estado financeiro inalterado; restauração real em contexto novo mantém bytes legados distintos no destino e não monta/inicia campanha. Contraprovas rejeitam ausência, valor/cópia financeira, promoção do legado a preferência e corrupção do texto opaco.

Sentinelas Capital/Time Twins antes eram strings não JSON. Agora são objetos JSON sintéticos explícitos com os mesmos marcadores, sem alegação de schema histórico canônico. Permanecem incompatíveis/opacos e têm igualdade de bytes antes/depois; não se tornam progresso ativo nem são normalizados. A recusa de exportação opaca ilegível e os testes adversariais dos produtores ficam intactos.

Aceite adicional do coordenador: estender os mesmos18casos de `unified_backup_test.py` para exigir raw exato das quatro famílias no primeiro destino novo e após reload. Esperados vêm diretamente das quatro chaves semeadas antes de construir o backup, nunca do próprio produtor de backup. Os três modos modular/portátil/file devem ser reexecutados. Não criar prática nem gravar defaults para mascarar omissão.

Varredura: todos os usos de exportFullBackup/botão, expect_download, Blob.text/read_text/json.loads, construtor de Blob, chaves/allowlist e captura workspace foram classificados. Time Twins não tinha exclusão de backup a corrigir: seus oráculos de storage/lifecycle ficam intactos e o roundtrip de quatro famílias o cobre explicitamente. Downloads de estatuto/Markdown/artefatos e chamadas diretas ao builder JSON não são alterados. Inventário rastreável e linhas estão nos artefatos da rodada5.

## Evidências, revisão e rollback

REDs preservados: Guia falha ao ler ZIP como texto e na exclusão do progresso; Capital falha com sentinela opaca ilegível; predicados antigos de exclusão rejeitam snapshots aprovados. Focais atualizados precisam executar integralmente cada consumidor afetado, os34casos inline e18casos de pacote nas três distribuições. Preservar IDs/quantidades das suítes,413casos UI,2px,44px, zoom nativo200%,116entradas/timeout do gate. Novo helper não instala dependências nem lê dados reais.

Congelar fontes, diffs, hashes, exit codes e limitações; revisão independente somente leitura antes de UI/FULL novos pelo coordenador. Falha histórica ou ambiental não vira PASS por anotação. Nenhum FULL é executado por esta frente. Rollback restaura somente testes/documentação desta rodada e mantém explícita sua incompatibilidade com o contrato atual; não toca stores ou dados.
