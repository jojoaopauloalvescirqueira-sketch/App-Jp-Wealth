# Task 1 — motor Stoikus

Implementado em `tools/stoikus-installer/src/Stoikus.Installer.Core/` e `tools/stoikus-installer/tests/`. API congelada preservada. Overload adicional `InstallerService(byte[], byte[], string, IInstallerPlatform)` mantém a substituição de compilador/processos restrita às dependências de plataforma; o construtor público original usa WindowsInstallerPlatform real. Nenhuma instalação em terminal MT5 real, alteração de fontes MQL/produto, commit, push ou publicação foi feita nesta tarefa.

## Evidência executada

SDK temporário .NET 10.0.402 em `/private/tmp/jpw-dotnet10/dotnet`; build net10.0 de Core e harness: **0 erros, 0 warnings**. Harness final: **34/34 PASS** em filesystem temporário real no macOS, usando FakePlatform para processos/compilação. Isso NÃO constitui compilação MQL5 nativa nem prova operacional do MetaEditor/Windows.

Comandos reproduzíveis, executados da raiz `/private/tmp/jpw-stoikus-installer-20261014`:

```sh
DOTNET_CLI_HOME=/private/tmp/jpw-dotnet-home NUGET_PACKAGES=/private/tmp/jpw-nuget /private/tmp/jpw-dotnet10/dotnet restore tools/stoikus-installer/tests/Stoikus.Installer.Tests --configfile tools/stoikus-installer/tests/NuGet.Config -p:NuGetAudit=false --ignore-failed-sources
DOTNET_CLI_HOME=/private/tmp/jpw-dotnet-home NUGET_PACKAGES=/private/tmp/jpw-nuget /private/tmp/jpw-dotnet10/dotnet build --no-restore --disable-build-servers tools/stoikus-installer/tests/Stoikus.Installer.Tests -t:Rebuild -p:UseSharedCompilation=false
DOTNET_CLI_HOME=/private/tmp/jpw-dotnet-home /private/tmp/jpw-dotnet10/dotnet tools/stoikus-installer/tests/Stoikus.Installer.Tests/bin/Debug/net10.0/Stoikus.Installer.Tests.dll
```

Logs preservados nesta pasta:

- `task-1-red.log`: contrato inicial sem comportamento, 6/15 PASS e 9 falhas reais. Os seis negativos que passaram contra o stub não foram tratados como demonstração de TDD isolado; a implementação completa foi submetida às rodadas seguintes e aos testes positivos correspondentes.
- `task-1-round2-red.log`: 27/28, falha real ao aceitar log terminal válido sem prefixo Result.
- `task-1-round3-red.log`: 30/32, falhas reais em recuperação antes de exigir terminal fechado e sufixo de log truncado.
- `task-1-round4-red.log`: 33/34, falha real na identidade exata dos quatro programas daily.
- `task-1-build.log` e `task-1-green.log`: rebuild final e 34/34 PASS.

Rodada intermediária também revelou erro de reinstalação: o recibo convertia “original ausente” em hash do arquivo já instalado; corrigido preservando explicitamente OriginalHash nulo. Não sobrescrevi os históricos RED com o resultado final.

## Comportamento e cobertura

Pacote: hash/tamanho integral e por entrada, duplicação case-insensitive, traversal/raiz/fora namespace, symlink em ZIP e filesystem, quatro fontes daily exatas, saída EX5 não pré-incorporada. O payload real gerado de 82 arquivos/4 programas também foi validado pelo Core.

Alvo: associação portable explícita ou origin.txt, terminal64/metaeditor64 junto à instalação e MQL5 existente, processos fechados antes da recuperação e novamente antes de mutar, verificação somente leitura. Estado fica fora do terminal e rejeita UNC em Windows; stage/relatórios/backups permanecem fora de MQL5.

Compilação: stage novo sem EX5 antigo; closure literal transitivo da biblioteca selecionada, sementes Canvas/Canvas.mqh e Math/Stat/Normal.mqh, includes JPWealth provenientes do payload, nenhuma cópia ampla de arquivos privados; include não literal/ausente/fora da raiz bloqueia. `/compile`, `/include` e `/log` são explícitos. WindowsInstallerPlatform usa `/log` e move o log criado ao lado do fonte para o diretório de evidências. Timeout e cancelamento matam o processo iniciado e aguardam sua saída. Logs UTF16 com BOM e UTF8 aceitam resumo terminal com Result opcional, zero erros/avisos, tempo/CPU quando presentes. EX5 deve ser novo, não vazio e recente. Nenhuma gravação no alvo até os quatro resultados válidos.

Transação: lock de arquivo por identidade do alvo, journal com flush antes de backup e gravações, backup externo validado, conferência de hash antes/depois da gravação, publicação atômica do recibo, recuperação de operação interrompida, rollback repetível e preservação de edição concorrente com indicação de recuperação manual. Remoção restaura originais e remove criados inalterados; reparo ausente usa recibo e proteção contra alterações. Reinstalação mantém identidade dos originais e legado organizado. Guia LEIA_PRIMEIRO não vai ao terminal.

Os 34 testes cobrem adulteração, traversal/namespace, caixa, desconhecidos fonte/binário, terceiro compile falhando sem mutação, EX5 antigo real no alvo não atendendo build, logs erro/aviso/truncamento, dependência ausente/escapada, closure sem arquivo privado, processos abertos, cancelamento antes e depois de gravar, instalar/reinstalar/reparar/remover, alteração pelo usuário, original conhecido, legado oficial/desconhecido, mutex, backup adulterado, falha real de criação de backup, falha real de cópia por colisão com diretório, recovery de journal e conflito manual.

## Limites explícitos

Windows/MetaEditor nativo, edição exata de log emitido pela instalação do usuário, ACL/antivírus e power-loss real: **NOT_RUN**. Fixtures de log desta suíte são sintéticas e não são apresentadas como captura nativa. A invocação real está implementada, mas compatibilidade final exige prova Windows isolada. `prlctl exec` segue bloqueado pela edição instalada; CPURegular, nativeArtifact SDK e aceitação manual não são presumidos. Relatórios registram scope local-four, CPU NOT_PROVEN e nativeSdk/validação nativa NOT_RUN. Revisão independente pertence à etapa seguinte do parent.

O comando `dotnet format` encontrou bloqueio de named-pipe do sandbox; a formatação foi feita com Roslyn NormalizeWhitespace em utilitário temporário fora do produto. Build usa `--disable-build-servers -p:UseSharedCompilation=false` para evitar o mesmo limite. Isso não impediu a compilação/testes executados.

## Fixround1 — resposta à revisão PRODUCT_FAIL

A revisão original `task-1-review.md` permanece preservada como **PRODUCT_FAIL** do candidate anterior. Corrigidos R1 e R2; a aprovação desta correção depende da nova revisão independente.

**R1:** `CaptureApprovedIdentities` captura e valida path/hash/tamanho antes da compilação contra recibo ou catálogo oficial. Isso inclui os arquivos desejados e o legado selecionado. Depois da compilação, a seleção deve continuar entre os candidatos oficiais e todas as identidades devem permanecer iguais. Cada row do journal recebe `BeforeHash` e `BeforeBytes` da identidade aprovada, não adota os bytes atuais; a identidade é exigida novamente ao construir a row, antes do backup e antes de cada escrita. A regressão real de filesystem substitui o legado no progresso do quarto compile e exige falha sem retirar a edição nem escrever outro arquivo no alvo. Outra regressão troca um arquivo desejado por uma segunda versão oficial durante compile; mesmo sendo outro hash do catálogo, a operação rejeita a identidade alterada.

**R2:** cada tentativa tem `CompileEvidence` com execução/stage, source e output absolutos/relativos, hash do fonte, caminho/hash/versão do editor, argumentos, dependências e hashes, início, timeout configurado e status. O relatório é gravado com flush/rename **antes** da invocação. `finally` captura término e hashes disponíveis do log/EX5; falha, cancelamento ativo e timeout ficam registrados com status/diagnóstico e exit quando disponível. O relatório de erro inclui run/stage e toda a lista acumulada, inclusive a tentativa falha. O teste do terceiro compile verifica semanticamente três tentativas, associação aos arquivos reais, hashes, comandos/dependências, metadados de processo, dois status succeeded e um failed; outro teste lê o relatório dentro do fake de processo e comprova que a tentativa já estava persistida antes da chamada.

Também cobertas as lacunas concretas da revisão: cancelamento enquanto CompileAsync está aguardando; timeout do seam; recuperação depois de publicar recibo antes de committed (tanto recibo anterior ausente quanto bytes exatos de recibo anterior existente); retomada de status restoring antes/depois da restauração; recuperação repetida; backup temporariamente ausente seguido de retry; origin.txt UTF8 e UTF16, associação divergente e editor de outra instalação; reparse de dependência transitiva, estado, backup e stage. O teste do stage detectou uma imprecisão adicional: a operação recusava o stage redirecionado, mas a primeira tentativa ainda aparecia como succeeded. A validação de reparse dos outputs/log foi movida para antes de atribuir succeeded; agora a própria tentativa fica failed.

Evidências novas, sem substituir históricos anteriores:

- `task-1-fixround1-red.log`: **40/45**, cinco falhas reproduzidas (R1 legado, R1 arquivo desejado, R2 terceiro compile, R2 cancelamento ativo e R2 timeout).
- `task-1-fixround1-stage-red.log`: **47/48**, status incorreto da tentativa com stage redirecionado.
- `task-1-fixround1-build.log`: rebuild final **0 erros / 0 warnings**.
- `task-1-fixround1-green.log`: **48/48 PASS**.

Mesmos comandos restore/build/harness anteriores, com `-t:Rebuild --disable-build-servers -p:UseSharedCompilation=false`. Alterações restritas a InstallerService.cs, Transactions.cs, Compilation.cs, StateModels.cs, testes Program.cs e este append de relatório. Contrato público e arquivos MQL/dados do produto permanecem inalterados nesta rodada.

As janelas de recovery foram representadas por estados persistidos reais de filesystem, não por power-loss ou crash nativo. Cancelamento/timeout são do seam fake; kill/timeout reais do adapter Windows, junction/ACL NTFS, compilação MetaEditor, CPU/SDK e aceite operacional continuam **NOT_RUN/NOT_PROVEN**. Nenhuma publicação, commit ou instalação MT5 real.

Código congelado após o build/testes finais desta rodada, disponível para re-review.

## Finalfixwave — recuperação explícita F1/F2

A revisão integrada `final-review.md` e seus veredictos PRODUCT_FAIL anteriores permanecem preservados. Implementada a emenda de contrato acordada: `InstallAction.Recover`, `HasPendingRecovery(TerminalTarget)` somente leitura, `Inspect(target, Recover)` somente leitura e execução isolada de recuperação. O probe valida associação de alvo/diário e caminhos de estado; diário de outro alvo ou estrutura inválida não é autorizado. Conflitos de conteúdo/backup num diário com identidade válida continuam detectáveis para mostrar a prévia bloqueada e informar recuperação manual.

A prévia de Recover descreve os arquivos a preservar, restaurar do backup ou remover como criação da operação; confere hashes, backups e reparse sem gravar. A execução usa o mesmo lock e exige terminal/editor fechados, revalida o diário e a prévia, efetua somente o rollback desse diário e gera relatório com `action: Recover`, `compiled: false`. O sucesso exige nova conferência da ação desejada; não compila nem instala silenciosamente.

Por orientação explícita do coordenador nesta rodada, a proteção ficou mais forte que a recuperação automática anterior: **Inspect e Execute das ações Install/Repair/Remove recusam um diário pendente e exigem a ação Recover separada**, inclusive quando ele surge depois da prévia normal. A própria recuperação usa um único objeto de diário validado por execução, evitando reler duas fotografias diferentes entre validação e rollback.

F2: o cancelamento é conferido antes de criar o estado da nova execução, novamente depois do lock/processos e imediatamente antes de iniciar o rollback explícito. Um token já cancelado não grava no alvo nem no diário pendente. Depois do último limite de cancelamento, a recuperação termina o rollback consistente com suas transições duráveis; não abandona uma restauração entre backup e finalização. O rollback de uma transação iniciada pela própria chamada continua sendo a proteção de erro/cancelamento dessa chamada.

Novas regressões de filesystem real: primeira instalação interrompida com EX5 sem recibo → descoberta/prévia readonly → recuperação sem compilador → nova prévia Install; reparo parcial e recibo anterior restaurado; cancelamento prévio para Install e Recover preservando bytes de alvo e diário; diário aparecendo entre prévia normal/Execute não provoca recuperação silenciosa; ausência de diário não autoriza instalação; edição do usuário e backup adulterado preservados com relatório manual; associação de diário a outro alvo bloqueada; processos abertos e lock concorrente também bloqueiam Recover. A regressão atravessando a lógica real do assistente pertence ao owner da UI e não é substituída por estes testes Core.

Evidências desta rodada:

- `task-1-finalfix-red.log`: **50/56**, seis falhas antes da implementação (com API stub para viabilizar os testes).
- `task-1-finalfix-firstgreen.log`: tentativa intermediária **51/56**, em que as oito regressões novas já passavam e cinco testes históricos ainda exigiam recuperação implícita. Esses cinco testes foram migrados à ação Recover do novo contrato, mantendo as verificações de restauração, byte-identidade, retry e recibo.
- `task-1-finalfix-build.log`: rebuild final **0 erros / 0 warnings**.
- `task-1-finalfix-green.log`: **56/56 PASS**.
- `task-1-finalfix-sha256.json`: hashes do Core e harness congelados para integração/re-review.

Alterações desta rodada limitadas a Contracts.cs, InstallerService.cs, Transactions.cs, Program.cs dos testes e este append. Sem publicação de EXE, Git ou arquivos MQL/dados. Compilação MetaEditor/execução Windows/WinForms e power-loss real continuam **NOT_RUN**; recuperação testada por estados persistidos sintéticos reais e compilador fake.
