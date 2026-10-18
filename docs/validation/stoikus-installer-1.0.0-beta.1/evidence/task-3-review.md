# Task 3 — revisão independente

Candidate inspecionado: `/private/tmp/jpw-stoikus-installer-20261014`, base indicada `0037bd3c8a7a`. Fontes: `task-3-brief.md`, `contracts.md`, plano aprovado, `task-3-report.md`, `task-3-review.diff` e arquivos correntes pertinentes. Revisão somente leitura, exceto este relatório. Não rodei suítes registradas, build, gates, Git mutante ou publicação. Não avaliei comportamento do motor/App fora da integração de recursos do projeto.

## Veredictos separados

- **Compliance: CHANGES_REQUESTED**, restrito ao contrato futuro `available:true`: o gerador oficial aceita registros que o consumidor oficial necessariamente recusa (F1). Estado público atual, separação de provas e escopo de arquivos: sem violação identificada.
- **Qualidade: CHANGES_REQUESTED** por F1; F2 é melhoria pequena de comportamento futuro. Nenhum P0/P1 identificado nesta superfície.
- **Prova nativa/publicação: NOT_RUN**, conforme o contrato e o estado público. Estes limites conhecidos não são, por si, defeitos desta implementação.

## Findings

### F1 — [P2] Tornar o registro disponível aceito pelo gerador compatível com o consumidor

`tools/build_leverage_package.py:204-205` aceita arquivo de tamanho zero quando `bytes=0` e SHA do vazio coincidem. `tools/build_leverage_package.py:216` também aceita recibos JSON em qualquer extensão/nome aceito por `checked_file`. Em contraste, `src/js/20-ui/31-tools-services.js:120` exige tamanho positivo e `:124` exige caminho restrito terminado em `.json`. Portanto, o build oficial pode validar e preservar `available:true` e produzir um site cujo botão fica desabilitado. O primeiro caso também deixa o validador aprovar como artefato público um arquivo completamente vazio.

Contraprova nova, isolada em `TemporaryDirectory`, importou apenas `validate_installer_record`, criou arquivos/recibos sintéticos vinculados ao hash e chamou o validador real. Resultado observado:

```
ACCEPTED_SYNTHETIC {'bytes': 0, 'receiptSuffix': '.json', 'startsMZ': False}
ACCEPTED_SYNTHETIC {'bytes': 10, 'receiptSuffix': '.txt', 'startsMZ': False}
```

Isso não é evidência nativa: as provas eram fixtures deliberadas. Demonstra a lacuna de validação. Unificar os limites de tamanho/caminho/tipos entre produtor e consumidor; ao menos recusar arquivo vazio e recibos que o site não aceita. Acrescentar contraprovas focadas para ambos. Não ampliar o significado de PASS nem alterar o contrato `nativeArtifact`.

### F2 — [P3] Atualizar o rótulo quando o instalador futuro se tornar disponível

`index.html:1369` fixa o texto do botão como `Instalador .exe · indisponível`. `src/js/20-ui/31-tools-services.js:165-170` atualiza disponibilidade, hash e status, mas não o rótulo do botão. Quando um registro disponível válido for usado, o botão será habilitado e continuará dizendo “indisponível”, contradizendo o status “Disponível”. Atualizar o texto de acordo com o estado e cobrir ambos os estados no teste de DOM. O rótulo atual é correto para o candidate indisponível.

## Evidência positiva e limites

- Contraprova somente leitura do payload corrente: hash global confere; 441515 bytes; 82 registros com tamanho/hash correspondentes a todos os membros; quatro fontes MQ5 exatas; knownFiles sem duplicatas caminho/hash; legacyFiles exclui paths atuais e as quatro saídas EX5. Payload ZIP é byte-idêntico ao ZIP diário corrente. Resultado: **PASS**, escopo somente identidade/estrutura, sem compilação/execução.
- `git diff --name-only 0037bd3c8a7a -- mt5 downloads/jpw-alavancagem-atual` retornou somente `downloads/jpw-alavancagem-atual/manifest.json`. Nesta comparação, MQL e ZIPs não apresentam delta. Não equivale a aceite da revisão anterior.
- Manifesto público corrente observado: `installer.available:false`, sem URL/hash/tamanho público, todos os três estágios `NOT_RUN`. Site tem botão inicialmente desabilitado e mantém o estado indisponível. Não identifiquei download indevido atual nem alegação de prova nativa atual.
- Leitura confirma hashes históricos congelados, catálogo apenas de MQL5 oficial, schema de payload congelado e LEIA_PRIMEIRO separado de MQL5. Gerador usa bytes do daily, sem reempacotar o payload. Catálogo não interpreta esses hashes como aprovação nativa.
- Delta do gerador oficial preserva a validação anterior dos pacotes e separa `downloads.installer` de `nativeArtifact`; registro opcional é validado antes de regenerar arquivos. Não identifiquei enfraquecimento da validação SDK anterior no diff.
- Expressão oficial de incorporação exclui `installer`; o manifesto ainda transporta metadados. JS recusa EXE em `file:`, verifica SHA/tamanho/MIME após fetch e restringe a URL inicial à release HTTPS do repositório indicado.
- Build helper fixa SDK 10.0.402 e flags self-contained/single-file/win-x64, usa ambiente indicado e staging temporário. Recursos do csproj referenciam os nomes lógicos congelados. **Não executei restore/publish** nem verifiquei PE real/recursos incorporados do candidato final.
- **Não verificável por esta revisão:** execução Windows x64/Parallels ARM, MetaEditor/MT5, qualidade visual/acessibilidade em navegador real, conteúdo probatório humano dos futuros recibos e publicação. A fixture de download usa seams e não demonstra CORS/redirect/MIME reais de releases GitHub. Esse transporte precisa do gate browser real antes de habilitar disponibilidade; não o classifiquei como falha observada sem uma release real testada.
- Monolith/PWA final e atualização de fingerprints eram integração explicitamente delegada ao root; não foram executados nem declarados PASS por esta revisão.

## Re-review — fix round 1

Escopo desta rodada: apêndice `Fix round 1` do `task-3-report.md`, comparação por arquivo entre `task-3-review.diff` e `task-3-fix1-current.diff`, e leitura das linhas correntes alteradas. Os dois pacotes são contra a mesma BASE; comparei os deltas entre seus conteúdos para não tratar alterações originais como novas. A tentativa original acima permanece preservada. Não repeti as suítes nem executei publish/Git mutante.

### Resolução dos findings

- **F1: ADDRESSED.** `tools/build_leverage_package.py:205-206` agora exige inteiro positivo até `9007199254740991`, alinhado ao tamanho seguro do JS, além de preservar tamanho/hash dos bytes reais. `:215-218` exige caminho string ASCII restrito terminado em `.json`, com `checked_file` mantendo rejeição de componentes `.`/`..`, normalização e symlinks. Assim, as duas contraprovas originais deixam de satisfazer os guardas. Os testes adicionados usam arquivos/recibos reais temporários para vazio, `.txt` e nome não ASCII; o teste anterior que detecta recibo de outro candidato foi preservado. Avaliação por leitura do fix; os resultados 9/9 Python e regressões são evidência registrada pelo builder, não execuções minhas nesta rodada.
- **F2: ADDRESSED.** `src/js/20-ui/31-tools-services.js:166` escolhe o texto `Baixar instalador .exe` apenas quando `ready` é verdadeiro e conserva `indisponível` nos demais casos. O estado `file:` também depende de `ready`, portanto não anuncia download disponível. O teste JS agora confere rótulos habilitado, metadados rejeitados e portátil, sem relaxar as verificações anteriores de hash/tamanho/URL/MIME.

### Portabilidade do helper

Leitura do delta em `tools/stoikus-installer/build.py:17-34` e CLI `:70`: seleção segue `--dotnet` explícito → `JPW_DOTNET` → `shutil.which('dotnet')`, verifica arquivo e resolve caminho antes de executá-lo. O ambiente copia o chamador, preserva overrides `DOTNET_CLI_HOME`/`NUGET_PACKAGES` e usa diretório temporário da plataforma somente na ausência deles. README corresponde a esse comportamento. Permanecem SDK exato 10.0.402, staging limpo, flags win-x64/autocontido/single-file, metadados `LOCAL_CANDIDATE_ONLY`, `NOT_RUN` e download público falso. Nenhuma quebra nova identificada nesse delta. Testes novos verificam ambiente/defaults; seleção real de SDK em Windows continua não executada por esta revisão.

### Veredictos atuais desta superfície

- **Compliance: APPROVED**, para o delta Task 3 revisado, com F1/F2 resolvidos e sem quebra nova identificada nas alterações da rodada.
- **Qualidade: APPROVED**, para o mesmo escopo de revisão de código/contratos. Isso não declara testes próprios da rodada nem funcionamento nativo.
- **Windows x64, Parallels ARM, MetaEditor/MT5, transporte real GitHub no navegador, monolith/PWA final e publicação: NOT_RUN por esta revisão.** Os limites anteriores permanecem. A aprovação desta revisão não habilita download nem substitui os gates/aceite do candidate final.
