# Preservação final do delta — revisão independente em leitura

**AUDIT_PASS delimitado.** Não identifiquei reversão de trabalho anterior fora do delta autorizado. FULL permanece em execução e não é julgado aqui. Nenhum teste, browser, gerador, Git mutante ou edição do repositório foi executado.

## Base e método

Comparados baseline-hashes.json e arquivos regulares atuais, excluindo docs/validation, que recebe evidências durante o FULL. Originais lidos diretamente do tar em memória, sem extração. Arquivo baseline-pending.tar.gz SHA256 `5c50501d04c0207027e1f9a9d43bc6980b25dad88fd827433d9058af7c3d9d3d`, igual ao recibo original. Dezessete originais modificados vêm desse arquivo; calendar_visual_quality_test.py não estava pendente, portanto foi recuperado em leitura do HEAD original 3e24f60. Todos os 18 originais correspondem individualmente ao hash registrado no baseline.

População fora de validação: **1.643 arquivos preexistentes; 1.625 inalterados, 18 modificados, zero removidos; cinco arquivos regulares novos**. Listas e hashes completos: preservation-final-data.json.

## Payloads e geração oficial

Nos seis arquivos de downloads (daily-source, native-kit, native-pin, preview JS/JSON e source) e no runtime-payload de market-hours, a única diferença é **uma ocorrência literal** de `5b4ef1141c9583bf` substituída por `aabc8d09faff4aee`. Após essa única substituição, cada arquivo antigo é exatamente igual ao atual. Bases64, ZIPs incorporados, fontes MT5, HTML de prévia, pin, catálogo e renderer permanecem com conteúdo idêntico.

build-id.js difere exclusivamente pelo identificador do build e pelo envelopeSha256 da prévia JSON, consequência dessa substituição. Envelope antigo SHA `8bb5eb81d7f7d38f05cbfc5720c3c982c8e4c9c3eea958a275bf5ff63ce51289`; atual `9e8b274a7d2ba89f0cc171c5c953c7dabdd704d29e384bd4028e3c14685d6418`. Feitas essas duas substituições, o arquivo é idêntico. Metadados de versão/classificação/pendências nativas dos outros produtos estão preservados.

O portátil atual é exatamente o portátil arquivado após substituir uma ocorrência integral de cada fonte 19-calendar-agenda.js, app.css e build-id.js por sua versão atual e atualizar o buildId nos envelopes restantes. **Nenhuma diferença residual.** O manifesto JS altera somente o SHA da entrada 19; ordem, quantidade e demais metadados permanecem. Esse padrão corresponde à lógica lida no gerador oficial rebuild_monolith.py, cujos bytes também permanecem inalterados. Não reexecutei o gerador.

## Demais caminhos e escopo

Além dos sete payloads e do portátil, os dez caminhos modificados são: dois fontes de apresentação, manifesto JS, quatro verificadores autorizados, contrato CALENDAR-AGENDA, ACTIVE-TASK e build-id.js. Identidades de fontes/verificadores já confrontadas no applied-v3-final-review.md. CALENDAR-AGENDA apenas adiciona o contrato de tabela; o conteúdo inteiro do ACTIVE-TASK arquivado permanece como trecho contíguo do atual.

Os cinco arquivos regulares novos são o plano econômico de28/10, BRIEF, CHGs N1/N3 e helper calendar_economic_table_contract.py, todos ligados à mudança autorizada. Dezoito links de diretórios de skills aparentavam ser novos por não constarem no inventário de arquivos regulares: são symlinks já presentes no HEAD original, com destinos idênticos. Não são adições deste delta; isso verifica os destinos, não o conteúdo externo das skills.

## Limites

A prova é de preservação de bytes e compatibilidade das diferenças geradas com o gerador oficial, não de autoria histórica de cada operação. Não audita arquivos ignorados, conteúdo externo dos symlinks, estado de navegador, dados financeiros em armazenamento, sincronização iCloud ou execução MT5. Evidências em docs/validation foram excluídas enquanto o FULL escreve recibos. Resultado FULL, população do freeze após execução, testes nativos e aceite humano dependem de seus próprios recibos.
