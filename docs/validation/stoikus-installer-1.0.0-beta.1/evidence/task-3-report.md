# Task 3 — distribuição e payload — 2026-10-14

Raiz explícita `/private/tmp/jpw-stoikus-installer-20261014`, branch `codex/stoikus-installer-20261014`, base `0037bd3c8a7a`. Autoridade: task-3-brief + contratos congelados + plano aprovado fornecidos pelo root. Propriedade respeitada: nenhum arquivo `src/` ou `docs/` dentro do instalador, MQL ou docs de projeto foi editado por esta autoria. `tools/rebuild_monolith.py` teve delta estreito explicitamente autorizado depois pelo root.

## Entregue

- `tools/stoikus-installer/prepare_payload.py`: valida manifesto corrente, SHA/tamanhos de ZIPs, identidade fontes/SDK/diário, fechamento de dependências, paths/case/duplicação, catálogo de quatro ZIPs históricos congelados. Copia bytes do ZIP diário; não reempacota.
- Payload gerado: ZIP 441515 bytes, SHA-256 `2dd00aa8a4b4cb90f6b4eca36af4ef8d3e475ad5c856e163d9dc5c19fe6a99cf`; JSON schema congelado com 82 arquivos, 4 programas, 215 knownFiles e 70 legacyFiles. Legacy contém só MQ5/EX5 não diários; exclui saídas diárias, includes/imagens, Files/locks/dados.
- `build.py` e `global.json`: SDK oficial fixado 10.0.402, restore/publish autocontido single-file win-x64, sem trimming/AOT, staging limpo, EXE candidato e metadados locais ignorados. Assembly real esperado: `JPWealth.Stoikus.Installer.exe`; saída pública futura: `Stoikus_Setup_1.0.0-beta.1_win-x64.exe`. Build helper CLI/sintaxe verificados; restore/publish ficam para root após Core/App prontos.
- Gerador oficial `build_leverage_package.py` preserva e valida registro opcional `downloads.installer`; registrado `available:false`, três estados `NOT_RUN`, sem path/hash/tamanho/URL públicos. Registro disponível futuro exige EXE local com bytes/hash exatos + Windowsx64/ParallelsARM/browser PASS + recibos hash-bound com candidateSha256 e etapa + allowlist de release HTTPS do repositório GitHub.
- Card visível beta não assinado no `index.html`, requisitos Windows11/MT5/MetaEditor, botão desabilitado e limites. JS preserva fluxos daily/SDK/compiled e adiciona verificação de EXE futuro com SHA/tamanho/caminho/MIME/allowlist/metadados nativos. Não inventou release live. EXE file:// desabilitado.
- Gerador oficial monolith exclui sempre installer da incorporação de bytes, inclusive futuro available:true, preservando ZIPs. `.gitignore` inclui .superpowers e derivados próprios.

## TDD e verificações

- RED inicial: `python3 tools/stoikus_installer_test.py`: 4 falhas esperadas (gerador ausente). GREEN: 4/4 após implementação.
- RED downloader: `python3 tools/stoikus_download_test.py`: falha esperada com botão installer novo não desabilitado em manifesto inválido. GREEN após inclusão do kind/validações.
- RED incorporação: teste executa a expressão AST real de `rebuild_monolith.py` com ZIP/EXE sintéticos em diretório temporário; falhou porque incorporava installer. GREEN após filtro estreito. Nenhum rebuild pesado foi usado para esse caso.
- PASS final `python3 tools/stoikus_installer_test.py`: **6/6**. Fixture temporária valida identidade/determinismo, mutação de ZIP/fonte/histórico, traversal, case collision, membros extras/ausentes, registros indisponíveis e disponíveis com recibos sintéticos (inclui recusa de receipt de outro candidato), não incorporação do EXE.
- PASS `python3 tools/stoikus_download_test.py`: SHA real em Node; 3 downloads ZIP online; daily file://; installer fixture online; EXE file:// recusado; corruption hash/tamanho, MIME HTML recusado, release host/query/path inválidos e provas nativas/recibos ausentes recusados. São seams DOM/network, não prova de navegador real/release.
- PASS `python3 tools/stoikus_daily_package_test.py`: inventários independentes, idempotência, ausências, traversal, symlink e EX5 não comprovado recusado, arquivos correntes/históricos corretos.
- PASS `python3 tools/leverage_package_test.py`: determinismo, extração, controles negativos e hashes históricos. Slice nativo retornou NOT_RUN corretamente.
- PASS comparação baseline: **141/141 fontes MQL e ZIPs byte-idênticos**, nenhuma alteração. Manifesto é o único arquivo dessa área alterado por intenção (novo registro).
- PASS `python3 tools/stoikus-installer/prepare_payload.py --record-unavailable`: payload/hash acima, geração oficial do registro; não mudou ZIPs nem fontes.
- PASS `python3 tools/stoikus-installer/build.py --help`; PASS compilação sintática Python com `PYTHONPYCACHEPREFIX=/private/tmp/jpw-pythoncache python3 -m py_compile ...`.
- ENVIRONMENT_ERROR histórico: tentativa inicial de py_compile usou cache padrão fora da sandbox (`/Users/.../Library/Caches/com.apple.python/private`) e foi recusada; mesma verificação passou usando cache permitido em /private/tmp. Não é falha do produto.
- PASS `git diff --check`; diff próprio integral revisado.

## Pendências e integração do root

- Rebuild monolith/PWA final e sincronização do hash do script 31 no manifesto JS: NOT_RUN por esta autoria, root assume após freeze. O gerador é compatível com registro installer indisponível e nunca incorpora EXE, conforme teste de fixture.
- Dotnet restore/publish do candidato real: NOT_RUN por esta autoria, aguardou Core/App. O SDK10.0.402 está provisionado pelo root. Executar `python3 tools/stoikus-installer/build.py` quando fontes de App/Core estiverem estáveis.
- Testes de navegador real, Windows x64, Parallels ARM, compilação/instalação MT5, uso, aceite, publicação: NOT_RUN. O estado público continua indisponível independentemente do build local. `nativeArtifact` do SDK foi preservado.
- Não executei commit/push/publicação/instalação MT5 nem alterei código financeiro. Reversão possível removendo o delta da tarefa e regenerando derivados com ferramentas oficiais; não foi executada.

## Fix round 1 — revisão independente F1/F2 + portabilidade do helper

Fonte recebida: `task-3-review.md` (CHANGES_REQUESTED). Os casos apontados foram confirmados executando fixtures reais temporárias antes da correção. Esta seção acrescenta evidência nova; não substitui os resultados anteriores.

- **F1/P2 corrigido:** `validate_installer_record` exige bytes inteiro positivo dentro do intervalo seguro do JS; recibos exigem caminho ASCII restrito `docs/validation/... .json`, compatível com o consumidor, além das verificações existentes de path/hash/candidate/etapa. Não mudou o significado de PASS, os estágios nativos nem `nativeArtifact`.
- **F2/P3 corrigido:** botão de instalador recebe `Baixar instalador .exe` somente quando o registro e o protocolo permitem o download; permanece `Instalador .exe · indisponível` quando desabilitado. Cobertos estado futuro válido, metadados rejeitados e `file:`.
- **Portabilidade solicitada pelo root:** `build.py` deixou de assumir `/private/tmp` como default do executável/cache. `--dotnet` explícito é preservado; na sua ausência usa `JPW_DOTNET` e depois PATH. Respeita `DOTNET_CLI_HOME`/`NUGET_PACKAGES` já definidos; defaults são subpastas no `tempfile.gettempdir()` da plataforma. SDK continua fixado 10.0.402. README ajustado para documentar overrides e reproduzir caches do Mac. Nenhum publish novo foi executado.

### RED→GREEN observado

- RED `python3 tools/stoikus_installer_test.py`: **9 casos, 4 falhas** (EXE vazio aceito; recibo `.txt` aceito; recibo com nome não ASCII aceito; helper de ambiente portátil ausente). Demais verificações preservadas.
- RED `python3 tools/stoikus_download_test.py`: rótulo esperado `Baixar instalador .exe`, observado `Instalador .exe · indisponível` após habilitar fixture válida.
- GREEN final `python3 tools/stoikus_installer_test.py`: **9/9 PASS**, incluindo EXE vazio e recibos incompatíveis recusados, ambiente padrão/overrides preservados.
- GREEN `python3 tools/stoikus_download_test.py`: PASS inclusive rótulos nos estados habilitado/desabilitado, integridade e barreiras existentes.
- PASS regressões `python3 tools/stoikus_daily_package_test.py` e `python3 tools/leverage_package_test.py`.
- PASS `python3 tools/stoikus-installer/build.py --help`; compilação sintática com cache em `/private/tmp/jpw-pythoncache`; `git diff --check`.
- PASS comparação baseline **141/141** fontes MQL/ZIP byte-idênticos. Manifesto público: `available:false`, três estados `NOT_RUN` confirmados.

### Arquivos para re-review

`tools/build_leverage_package.py`, `src/js/20-ui/31-tools-services.js`, `tools/stoikus_download_test.js`, `tools/stoikus_installer_test.py`, `tools/stoikus-installer/build.py`, `tools/stoikus-installer/README.md` e esta seção do relatório. Nenhum novo binário/arquivo gerado foi produzido nesta rodada. Hashes JS/monolith/PWA final continuam sob integração do root e devem refletir o JS alterado antes de gates de navegador finais.
