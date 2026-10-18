# Task 1 — revisão independente do motor

Resultado de conformidade: **PRODUCT_FAIL**. Resultado de qualidade: **PRODUCT_FAIL**. O candidate precisa corrigir R1 e R2 antes da aprovação desta revisão. Nenhum código, contrato, teste do produto ou estado Git foi alterado pelo reviewer.

## Candidate e evidência

Revisados contracts.md, task-1-brief.md, task-1-report.md, plano aprovado, diff inicial e o candidate final `task-1-review-frozen.diff`. Todos os sete arquivos Core e os quatro arquivos de testes/configuração do diff congelado foram comparados com disco e deram MATCH. Fingerprints principais:

- InstallerService.cs: `fa752e897bca31d03f9d175b4d975ce5421a2718d6e073a098d3e3bea095b08e`.
- Transactions.cs: `39509b6e2d61f39033ae41b5649cff84b27800edb9f246e5fd6f112e433bec3e`.
- Compilation.cs: `0e5bbfec57a521cd5bc5f189a35a4f69c9fbf0878c5b9de1b189af9cacebd1e5`.
- Tests/Program.cs: `db8e9a60f0010f48fb9edf7dce1666b7dcab36b2531f2fd7d50b8eab88eeedc4`.

O log do builder termina em 34/34 passed e o relatório registra build 0 erros/0 warnings. Não repeti essa suíte. Executei somente duas contraprovas novas, em projeto temporário `/private/tmp/stoikus-core-review-probe/Probe.csproj`, referenciando a DLL já construída do Core e reutilizando fixtures de filesystem e o fake de compilador do harness. Os warnings CS0649 da contraprova são campos não utilizados da fixture copiada; não são warnings do produto. Não executado MetaEditor/Windows/MT5 nativo.

`python3 tools/agent_preflight.py --mode audit` encontrou a branch `codex/stoikus-installer-20261014`, HEAD `0037bd3c8a7a`, 19 alterações e BLOCKED por hash divergente de `src/js/20-ui/31-tools-services.js`. Registrado ao coordenador; não corrigido nesta revisão do Core e não usado como defeito deste motor.

## Conformidade

A leitura confirma API congelada preservada; verificação integral de ZIP/entradas; identidade dos quatro programas daily; proteção de arquivos desconhecidos no primeiro install; isolamento de stage; closure literal de includes; invocação real com `/compile`, `/include` e `/log`; guarda Windows; parser de resumo terminal; EX5 não vazio e novo; backups/journal anteriores às mutações; comparação de hashes; recibo e recuperação; preservação de modificação concorrente durante rollback. Esses itens foram inspecionados, sem converter leitura em execução nativa.

A conformidade falha em dois requisitos explícitos: organização somente por identidade oficial vigente (R1) e evidências de compilação/erro rastreáveis (R2).

## Achados de qualidade

### R1 — P1 — Revalidar a identidade do legado após compilar e vinculá-la ao journal

Arquivo: `tools/stoikus-installer/src/Stoikus.Installer.Core/InstallerService.cs`, linhas **274–276**, com consumo nas linhas **284–311** e remoção **354–357**.

`selected` é validado contra `preflight.LegacyCandidates` antes dos quatro compiles (228–230). A inspeção fresca recalcula candidatos, mas o executor consulta somente `fresh.CanProceed`: um legado que deixou de ser oficial não é problema global porque sua organização é opcional. A transação depois aceita o hash atual como `BeforeHash`, faz backup e remove esse arquivo. Isso transforma alteração de usuário durante a compilação em autorização de organização que ele não deu para esses bytes.

Contraprova executada: registrar `Legacy.mq5` como arquivo oficial e selecioná-lo; no progresso `compile` com Completed=4, substituir o conteúdo por `USER MODIFIED WHILE COMPILING`. A inspeção passa de 1 para 0 candidatos. Mesmo assim o resultado foi:

```text
Initial candidate count=1
Changed legacy: candidates now=0
Operation success=True
Modified legacy still exists=False
```

O backup conserva os bytes, portanto não afirmo perda irrecuperável. O defeito é retirar do terminal um arquivo alterado sem identidade autorizada e anunciar sucesso. Congelar path/hash/tamanho da identidade selecionada, revalidá-la depois da compilação e impedir que a construção das rows adote bytes diferentes resolve a causa; não basta testar que existe backup. Regressão exigida: alteração concorrente do legado selecionado implica falha antes de qualquer mutação e mantém o arquivo alterado no lugar.

### R2 — P2 — Persistir a evidência também quando a compilação falha

Arquivo: `tools/stoikus-installer/src/Stoikus.Installer.Core/InstallerService.cs`, linhas **398–401**, relacionado a **234**, **260–266**.

`buildEvidence` é local ao bloco try e só entra no relatório de sucesso. O registro do programa atual também só é acrescentado depois da validação de log/EX5. Se o terceiro compile falha, os dois resultados anteriores e o comando/editor/dependências do terceiro desaparecem do relatório. A falha ocorre antes do journal existir: o relatório tem `journal: null` e nem identifica o diretório da execução. Os logs/fontes ficam no disco, mas não preservam o hash/versão do editor executado nem associam a execução ao relatório; isso não é uma trilha reproduzível de erro.

Contraprova executada com FailAt=3 e leitura do relatório real:

```text
Compile-failure operation success=False
Failure report keys=success,message,error,journal
Failure report journal=null
Retained logs=3
```

Persistir identificação da execução e metadados do compile antes da invocação; registrar exit/timeout/cancel/erro e os hashes disponíveis após ela, inclusive em falha; incluir a evidência acumulada no relatório de erro. A regressão deve verificar conteúdo e associação dos metadados, não apenas a existência dos três logs.

## Cobertura ainda insuficiente nos testes atuais

Além das regressões R1/R2, o brief pede comportamentos para os quais os 34 casos não trazem demonstração completa:

1. Cancelamento durante um compile ativo: existe token já cancelado e cancelamento depois de gravação, mas não um fake de processo em espera cancelado durante CompileAsync. Timeout/kill do adapter real continuam dependentes do ensaio Windows, explicitamente NOT_RUN.
2. Interrupções nos limites de persistência: o teste de recovery semeia um único journal `writing`; não há contraprova para crash após publicar recibo/antes de `committed`, interrupção durante restauração e retry da restauração. São janelas do protocolo diferentes do caso atual e podem ser simuladas estreitamente sem declarar power-loss nativo.
3. Associação de alvo não portátil: as fixtures usam somente Portable=true; não demonstram origem UTF16/UTF8, origin.txt divergente e tentativa de misturar editor de outra instalação. O código de validação foi lido, mas esses caminhos não estão cobertos pelo harness.
4. Reparse de stage/include/estado: há symlink do alvo e symlink ZIP; faltam casos para dependência transitiva e backup/estado com reparse. Não alego bypass comprovado nesses caminhos; classifico como cobertura ausente pertinente ao contrato.

Essas lacunas não devem ser preenchidas com expectativas mais permissivas nem com rótulo de prova nativa. Foram listadas separadamente dos dois defeitos reproduzidos. Compatibilidade MetaEditor, ACL/antivírus, power-loss real e aceite manual continuam **NOT_RUN**, conforme o limite já aprovado.

## Comando das contraprovas

```sh
DOTNET_CLI_HOME=/private/tmp/jpw-dotnet-home NUGET_PACKAGES=/private/tmp/jpw-nuget /private/tmp/jpw-dotnet10/dotnet run --project /private/tmp/stoikus-core-review-probe/Probe.csproj --disable-build-servers -p:UseSharedCompilation=false -p:NuGetAudit=false
```

O processo saiu 0 porque é um programa observacional; os resultados acima evidenciam PRODUCT_FAIL do comportamento, não um harness de testes aprovado. O projeto temporário permanece disponível ao coordenador. A suíte original e os históricos RED/verde foram preservados.


## Re-review fixround1 — R1/R2 e regressões do delta

**Veredito do delta: PASS em conformidade e qualidade. R1: ADDRESSED. R2: ADDRESSED. Nenhum novo defeito acionável encontrado no delta revisado.** O PRODUCT_FAIL acima permanece como resultado histórico do candidate anterior; esta conclusão é delimitada às correções e respectivas regressões, não representa execução nativa ou aprovação de publicação.

### Identidade e método

Lidos o apêndice fixround1 de task-1-report.md, task-1-fixround1-sha256.json e task-1-fix1-current.diff. Comparei o pacote atual com task-1-review-frozen.diff para reconstruir o delta, pois não houve commits. Os sete fingerprints do JSON conferem com os arquivos atuais; todos os arquivos Core e de testes/configuração reconstruídos do pacote atual conferem byte a byte com disco. Core/Contracts.cs e WindowsInstallerPlatform.cs permanecem idênticos ao candidate anterior. Fingerprints principais atuais:

- InstallerService.cs: `96b37cf51edc4514693a743b8ce9341837a61a95f294aac909ddc15d7df92ea6`.
- Transactions.cs: `5829ca27e7ba7195058f1bf12784921946ef3c5507e7342620135d3c51c3340d`.
- Compilation.cs: `49445ef6465c6b3c2e16caf4eb83e87d416510fdd546c957c3deb023be221853`.
- Tests/Program.cs: `b82628b7fd72986b8fcbeb94eb0d411014989bb84457b34c4cf10081291c248b`.

A re-review foi por leitura do delta, dos novos oráculos dos testes e dos logs preservados. Não repeti a suíte nem as contraprovas já incorporadas como regressões, não editei código/testes e não executei operações Git.

### R1 — ADDRESSED

`Transactions.cs:11–41` captura caminho/hash/tamanho antes da compilação e verifica a identidade contra catálogo/recibo. `InstallerService.cs:233` congela essa captura; `315–318` exige seleção ainda oficial e identidades inalteradas depois da compilação; `331–353` usa os bytes/hash aprovados para o journal; `377` e `393` revalidam antes de backup e gravação. A operação não adota mais o hash modificado como baseline da própria autorização. A proteção também cobre troca de um arquivo desejado por outra versão oficial durante a preparação.

Os testes novos em `Tests/Program.cs:404` e `422` reproduzem as alterações durante o quarto compile e exigem falha com snapshot igual ao estado editado, preservando tanto a edição quanto os demais arquivos. O RED contém os dois contraexemplos; o log final registra PASS de ambos. Não houve relaxamento do critério: a existência de backup não é aceita como substituta da preservação do arquivo alterado.

### R2 — ADDRESSED

`InstallerService.cs:207–208` mantém run/stage/lista fora do try. As tentativas são acrescentadas antes de invocar o compilador, com identidade do fonte/editor, argumentos, dependências e timeout; `283` persiste esses dados antes da chamada. `293–302` distingue failed/cancelled/timeout e registra término; `Compilation.cs:11–29` coleta hashes disponíveis sem ocultar o diagnóstico original. `InstallerService.cs:443` inclui run/stage/todas as tentativas no relatório de erro. Assim, o terceiro compile falho conserva a associação e os dois resultados anteriores.

Os testes em `Tests/Program.cs:440`, `468`, `482` e `607` verificam o relatório real, a correspondência de hashes/caminhos, os resultados de falha/cancelamento/timeout e a persistência anterior à invocação. A inspeção do stage/output antes de marcar succeeded (`InstallerService.cs:286–290`) também corrige o erro intermediário de status documentado no RED 47/48. Não identifiquei quebra nova de rollback, recibo, API ou dos critérios de compilação decorrente deste delta.

### Cobertura adicional e evidência observada

Os 14 novos casos exercitam as regressões acima e fecham as lacunas listadas nesta revisão no âmbito do filesystem/seam: cancelamento ativo; timeout simulado; recibo publicado antes de committed com/sem recibo anterior; restoring antes/depois da cópia e retry; backup ausente recuperável; origin.txt UTF8/UTF16 e editor incompatível; reparse transitivo/estado/backup/stage. Os estados de crash são fixtures persistidas, não interrupções reais do sistema.

Conferidos diretamente os logs preservados: `task-1-fixround1-red.log` registra 40/45 com cinco falhas específicas; `task-1-fixround1-stage-red.log`, 47/48 com status incorreto de stage; `task-1-fixround1-build.log`, build 0 warnings/0 errors; `task-1-fixround1-green.log`, 48/48 passed. São execuções do builder cujos registros foram revisados, não uma segunda execução independente do reviewer.

MetaEditor/Windows/MT5 nativo, kill/timeout real do adapter, junction/ACL NTFS, antivírus, power-loss, CPU/SDK e aceite manual continuam **NOT_RUN/NOT_PROVEN**. O fechamento de R1/R2 não amplia esse estado nem autoriza commit, publicação ou instalação em terminal real.
