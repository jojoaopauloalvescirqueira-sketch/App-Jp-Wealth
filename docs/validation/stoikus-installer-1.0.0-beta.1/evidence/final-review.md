# Revisão final independente — instalador Stoikus 1.0.0-beta.1

Data: 2026-10-14. Raiz: `/private/tmp/jpw-stoikus-installer-20261014`. Base: `0037bd3c8a7ab2b4e21f7fdcb60f66ed93230874`. Branch observada pelo preflight: `codex/stoikus-installer-20261014`.

## Veredictos

- **Compliance: CHANGES_REQUESTED / PRODUCT_FAIL** no requisito de recuperação acessível pelo assistente após interrupção. O mecanismo existe no Core, mas sua integração com a prévia impede acioná-lo em um estado parcial válido.
- **Qualidade: CHANGES_REQUESTED / PRODUCT_FAIL** por F1 e F2 abaixo, reproduzidos na mesma contraprova estreita contra o assembly Release do candidate. Nenhum outro finding bloqueante concreto identificado nesta revisão.
- **Windows x64, Windows ARM/Parallels, MetaEditor/MT5, transporte real de download, acessibilidade nativa e aceite iniciante: NOT_RUN.** Esses limites não são tratados como defeitos demonstrados nem como PASS.

Não basta o PASS por peça para aprovar o fluxo integrado. O candidate atual deve permanecer local e indisponível publicamente. Corrigir F1 exige novo build/hash e atualização das evidências afetadas; as fotografias anteriores devem ser preservadas.

## F1 — [P1] Tornar a recuperação do diário acessível antes do bloqueio por instalação parcial

**Local principal:** `tools/stoikus-installer/src/Stoikus.Installer.App/WizardForm.cs:261`.

**Linhas relacionadas:** `WizardForm.cs:245-254,284-313,326-345`; `tools/stoikus-installer/src/Stoikus.Installer.Core/InstallerService.cs:137-139,165-168,224`; `tools/stoikus-installer/src/Stoikus.Installer.Core/Transactions.cs:214-224`.

Após interrupção durante a primeira instalação, pode existir um EX5 recém-gravado, um diário `mutating` com hash e estado `written`, e ainda nenhum `receipt.json` (o recibo só é publicado após todas as gravações). Esse EX5 não pertence ao catálogo de fontes nem tem recibo de propriedade. `Inspect(Install)` o classifica corretamente como desconhecido protegido; `Inspect(Repair)` e `Inspect(Remove)` recusam a ausência de recibo. A interface exige `Inspect.CanProceed` em `HasCurrentPreview`, tanto para avançar como para executar. Entretanto, `Recover` só é chamado dentro de `ExecuteAsync`, antes do preflight interno. O usuário fica sem caminho pelo assistente para alcançar a recuperação que o motor já sabe fazer. Na interrupção de reparo/atualização, a divergência entre recibo antigo e arquivos parcialmente atualizados pode produzir o mesmo bloqueio.

Isso não é uma dúvida sobre Windows ou power-loss: é a composição determinística das guardas de UI com a API real. As verificações de identidade devem continuar protegendo arquivos desconhecidos; não devem ser desativadas para permitir a instalação direta.

**Contraprova nova:** projeto isolado `/private/tmp/stoikus-final-review-recovery-probe`, referenciando o assembly já publicado `src/Stoikus.Installer.Core/bin/Release/net10.0/Stoikus.Installer.Core.dll`. A fixture criou somente arquivos sintéticos temporários, um EX5 parcial e diário correspondente, sem recibo. Chamou as três prévias públicas. Depois chamou diretamente `ExecuteAsync` com token já cancelado, de modo que somente a recuperação anterior à checagem do token fosse executada, sem compilação ou instalação nova.

Comando:

```sh
DOTNET_CLI_HOME=/private/tmp/jpw-dotnet-home NUGET_PACKAGES=/private/tmp/jpw-nuget /private/tmp/jpw-dotnet10/dotnet run --project /private/tmp/stoikus-final-review-recovery-probe/probe.csproj -v quiet
```

Saída relevante (exit 0 da contraprova, resultado do produto **PRODUCT_FAIL**):

```text
UI_PREVIEW Install: CanProceed=False; Arquivo desconhecido protegido: MQL5/Experts/JPWealth/JPW_Stoikus_Monitor.ex5
UI_PREVIEW Repair: CanProceed=False; Não há recibo de propriedade para esta instalação.
UI_PREVIEW Remove: CanProceed=False; Não há recibo de propriedade para esta instalação.
BEFORE_DIRECT_CORE journal=mutating
AFTER_DIRECT_CORE result=False; partialEX5Exists=False; journal=rolled-back
```

O `result=False` final é o cancelamento intencional após a recuperação, não falha da recuperação. O EX5 parcial foi removido e o diário finalizado, comprovando que o problema é o acesso pelo assistente. O build da contraprova emitiu warnings CS0649 sobre campos não usados da fixture copiada; isso não altera a observação e não é atribuído ao build do produto. Não foi iniciado MetaEditor ou terminal.

**Correção requerida:** oferecer fluxo explícito e seguro para detectar/revisar/confirmar recuperação pendente no alvo escolhido, antes de exigir uma prévia de instalação íntegra. Usar o mesmo lock, exigir processos fechados, validar associação de alvo/diário/backups, preservar conflitos e mostrar resultado/relatório. Após recuperação, invalidar a prévia antiga e exigir nova conferência para instalar/reparar/remover. A operação somente leitura de Verify não deve recuperar silenciosamente. O desenho exato da API fica com a implementação.

**Regressão necessária:** o teste deve atravessar a lógica real de seleção/prévia/recuperação/nova prévia do assistente com Core real e arquivos sintéticos. Cobrir pelo menos primeira instalação interrompida com EX5 sem recibo, reparo parcial com recibo antigo, conflito preservado, processo aberto e recuperação bem-sucedida que não autoriza automaticamente a próxima instalação. Os testes existentes que chamam `ExecuteAsync` diretamente não detectam esta falha de integração.

## F2 — [P2] Respeitar cancelamento já solicitado antes de recuperar arquivos

**Local:** `tools/stoikus-installer/src/Stoikus.Installer.Core/InstallerService.cs:224-225`.

A contraprova F1 também demonstra que um token já cancelado não impede gravações de recuperação: `Recover` é executado antes de `ThrowIfCancellationRequested`. Na fixture, a chamada cancelada removeu o EX5 parcial e finalizou o diário. Não existe uma operação em andamento a desfazer nessa nova chamada; trata-se de recuperação de execução anterior, iniciada mesmo após cancelamento. Conferir o token antes de iniciar a recuperação. Uma vez iniciada uma etapa de restauração, definir o cancelamento para preservar a consistência do diário e os arquivos, sem abandonar gravação intermediária. A nova ação explícita de recuperação também deve cobrir token cancelado antes da chamada, mantendo target e diário inalterados. Essa constatação é de arquivos sintéticos reais e não depende de comportamento nativo do MetaEditor.

## Identidade e escopo conferidos

- Leitura do plano aprovado, contrato congelado, relatórios/revisões Task 1/2/3 e correções, pacote `final-review.diff`, fontes pertinentes atuais, INTEGRATION e recibos do candidate.
- `python3 tools/agent_preflight.py --mode audit`: **PASS**, HEAD/branch acima e 22 alterações existentes declaradas. Nenhuma dessas alterações foi limpa ou incorporada por este revisor.
- Comparação SHA-256 local dos **47 arquivos** de `source-candidate-freeze.json`: **47/47 correspondem**, inclusive derivados e snapshots históricos listados. Isso confirma identidade da fotografia examinada, não a correção funcional de seus conteúdos.
- Bytes do EXE conferidos diretamente: **116760629 bytes**, SHA-256 **`6b46da92d652f31bb1842e071a7065094622221192d5906c56813b0bd4172af7`**; coincidem com `installer-candidate.json` e `exe-structural.json`.
- Recibo estrutural indica PE32+ AMD64 e tabela Authenticode vazia, explicitamente limitado a estrutura. Não reexecutei inspeção PE ou executei esse EXE.
- Projeto App incorpora ZIP, manifesto e guia com os nomes lógicos do contrato. Build helper fixa SDK, win-x64/autocontido/single-file, estágio de publicação limpo e status local. Não extraí os recursos do bundle para uma segunda comparação binária independente; a proveniência de build é o log registrado, o projeto e os metadados.

## Integração positiva examinada e limites

A interface captura alvo/ação/revisão da prévia, recusa resultados obsoletos, verifica o snapshot novamente após a confirmação modal e mantém falha/cancelamento visíveis. A execução corre fora do thread de UI. Os testes portáteis da lógica real ajudam nessas guardas, mas não cobrem o fluxo F1 acima nem substituem WinForms nativo.

O Core verifica payload, caminhos, catálogo, arquivos desconhecidos e alterações em arquivos de sua propriedade. A execução adquire exclusão mútua, revalida processos/identidades após compile e antes de cada gravação, persiste backup e diário, verifica hashes após escrita e preserva conflito em rollback. Organizados previamente permanecem no recibo para remoção/restauração. Os cenários de interrupção presentes exercitam janelas distintas; sua recuperação é chamada diretamente, ponto que ocultou F1.

A separação de fonte diária, recibo local dos quatro programas e `nativeArtifact` SDK permanece explícita. O manifesto público corrente não publica caminho/hash/URL do EXE; download permanece desabilitado. O gerador exige recibos de cada estágio vinculados ao mesmo hash para um registro futuro disponível, e o consumidor valida versão, URL, tamanho, estados, MIME e hash. As correções anteriores de tamanho zero, caminho do recibo e rótulo do botão estão presentes. Fixtures de transporte não comprovam CORS/redirect/MIME em release GitHub real.

O guia offline e as notas distinguem os gráficos de apoio/trabalho, retirada de legados, carregamento/remoção normal do script e estados de cobertura. A comparação A/B registrada limita corretamente seu cegamento e não declara aceite de iniciante. Inspeção de fonte e resultados HTML registrados não comprovam clareza em uso real ou acessibilidade Windows.

## Evidências já executadas pelo builder, revistas sem repetição

- Core: registro **48/48 PASS**, com REDs preservados; processos de compilação substituídos nos testes.
- Lógica UI: registro **12/12 PASS**; classe real compartilhada, sem controles WinForms executados.
- Payload/integração: registro **9/9 PASS** e revisão independente por peça; não é compilação MQL.
- Host/distribuição: `leverage-all-R1.log` encerra **44 PASS**, demais estados zero; declara compilação/execução nativas NOT_RUN.
- Web full: leitura final de `quality-full-R1.log` e existência do recibo `quality-full-R1.json` confirmam encerramento **57/57 PASS** do builder. Não reexecutei o gate. Esse resultado cobre o host/web congelado; não corrige F1 nem constitui prova Windows/MT5.

O único ensaio novo desta revisão foi a contraprova F1. Nenhuma suíte já registrada foi repetida. Não alterei fontes/testes, MQL, dados, payload, histórico, Git ou publicação. Escritas restritas a este relatório e ao projeto temporário isolado da contraprova.


---

## Re-revisão focal R2 — recuperação explícita, 2026-10-14

O parecer R1 acima e sua contraprova **PRODUCT_FAIL / CHANGES_REQUESTED** permanecem preservados integralmente. Esta seção avalia a correção de F1/F2 e possíveis regressões no delta da rodada. Não reabre nem substitui as provas operacionais ainda pendentes.

### Veredictos R2

- **F1: ADDRESSED.** A recuperação pendente agora tem caminho próprio acessível na interface, independentemente da aprovação da prévia normal.
- **F2: ADDRESSED.** Token previamente cancelado é conferido antes de criar estado, lock ou relatório e antes de qualquer recuperação.
- **Compliance R2: PASS no escopo implementado/revisado. Qualidade R2: PASS no mesmo escopo.** Nenhum novo finding concreto identificado no delta focal. Isso fecha os findings do parecer final R1 para este candidate R2.
- **Prontidão pública e operacional: não estabelecida.** Windows x64, Parallels ARM/Windows, MetaEditor/MT5, download real, WinForms/acessibilidade nativa e aceite de iniciante continuam **NOT_RUN**. A aprovação de código não autoriza disponibilizar o EXE.

### Fundamentos e linhas conferidas

**F1:** `WizardForm.cs:92-99,214-220,269,325-336` usa `HasPendingRecovery` somente leitura no snapshot selecionado e oferece o botão de recuperação sem depender de `Inspect.CanProceed` da ação normal. A nova prévia chama `Inspect(target,Recover)`; checkbox, confirmação modal e `ConfirmedSelection` garantem ação/alvo/revisão conferidos (`WizardForm.cs:228-236,360-380`; `WizardOperationState.cs:18-28`). Recover sempre recebe lista de organização vazia.

No Core, `InstallerService.cs:126-157,245-264` separa descoberta, prévia e execução: as ações normais recusam diário pendente e não efetuam recuperação implícita. A nova ação revalida sob o lock existente, exige terminal/editor fechados, rejeita organização e chama somente rollback, sem alcançar o ramo de compilação/instalação. `Transactions.cs:214-322` valida alvo, paths/identidades do diário, fases/transições, recibo anterior e arquivos/backups pertinentes. A prévia preserva bytes e identifica conflitos. A recuperação conserva o protocolo de rollback e seu diário durável; uma falha mantém evidência e não se torna sucesso.

O retorno positivo chama a implementação real `CompleteRecovery`, invalida a prévia e limpa a confirmação. `WizardForm.cs:275-281,311,382-385,415-421` oferece **Reinspecionar destino**, refazendo a ação original, em vez de avançar ao guia de abrir programas. Não há aprovação implícita da próxima instalação. Falha/cancelamento continua visível, com relatório quando produzido; uma nova tentativa passa por reinspeção.

**F2:** `InstallerService.cs:232` testa cancelamento antes de criar estado ou caminhos de relatório; `:244` repete após lock/processos e `:254` imediatamente antes do rollback explícito. Após esse limite, a restauração termina com consistência; não abandona arquivos no meio de uma transição. O tratamento de falha mantém a distinção entre rollback da transação corrente e recuperação explícita do diário anterior. As regressões verificam bytes do alvo e diário antes/depois, além de ausência de chamadas de compilador.

### Testes e evidências examinados, sem repetição de suítes

Li o delta `final-fix.diff`, os fontes correntes envolvidos, o append finalfix de `task-1-report.md`, `task-2-finalfixwave-report.md`, os testes integrados e os registros de build/execução/publicação. Os testes não se limitam a verificar strings ou reproduzir predicados: o novo `RecoveryIntegrationTests.cs` combina a classe de decisão real usada pelo Form com o Core real e arquivos sintéticos temporários. Examina EX5 sem recibo, reparo parcial com recibo anterior, preservação de conflito, processo aberto, cancelamento prévio, consentimento e descarte de prévia. O Form foi lido para conferir que utiliza esses métodos e seus resultados.

- `task-1-finalfix-green.log`: **56/56 PASS** registrados pelo builder; `task-1-finalfix-build.log`: **zero erros / zero warnings**.
- `task-2-finalfixwave-green.txt`: **18/18 PASS, zero FAIL** registrados pelo builder; `task-2-finalfixwave-build.txt`: **zero erros / zero warnings**.
- A migração dos testes históricos de recuperação implícita para `InstallAction.Recover` corresponde à emenda explícita do contrato desta rodada; as asserções de restauração, retry e byte-identidade foram mantidas. Os RED e a tentativa intermediária continuam registrados.
- `publish-R2.log` registra geração do novo candidate local com App/Core Release e o hash abaixo. O recibo estrutural R2 indica AMD64/PE32+ e tabela de certificados vazia, com `nativeExecution: NOT_RUN`.
- Web full **57/57 PASS** e host/distribuição **44/44 PASS** permanecem as execuções previamente examinadas para suas entradas inalteradas. Não repeti gates web/MQL, testes Core/UI ou publicação nesta re-revisão.

Não executei nova contraprova R2: a revisão de código e os testes integrados registrados resolvem os dois cenários concretos levantados, sem novo defeito específico que justificasse execução adicional. Isso descreve revisão independente de evidências, não execução independente das suítes.

### Identidade exata examinada

Conferência SHA-256 direta dos arquivos atuais:

- `source-finalfix-freeze.json`: **23/23 correspondem**.
- `task-1-finalfix-sha256.json`: **7/7 correspondem**.
- `task-2-finalfixwave-fingerprint.json`: **12/12 correspondem**.

EXE R2 lido e calculado diretamente: **116779573 bytes**, SHA-256 **`e326a7e9e5fb2bf2dd36e6406468a10d82af8ba1696c6affa672ca056bbcb1eb`**. Coincide com `installer-candidate.json`, `publish-R2.log` e `exe-structural-R2.json`. `scope: LOCAL_CANDIDATE_ONLY`, `publicDownloadAvailable: false`, três estágios nativos `NOT_RUN`. Payload e manifesto incorporável conservam os hashes `2dd00aa8a4b4cb90f6b4eca36af4ef8d3e475ad5c856e163d9dc5c19fe6a99cf` e `c92cc8223df899af7a90b3b7106a9d69c4326ec0b7d371dd24c6fc8586a12515` nos metadados. Não extraí o bundle para uma prova adicional de recursos nem executei o EXE.

Conferida a presença de `candidate-R1/` contendo o EXE e recibos anteriores. O hash R1 não foi tratado como identidade R2. Esta aprovação fica vinculada ao código congelado e ao novo artefato acima; mudança material posterior exige revisão/evidência correspondente. Nesta rodada escrevi somente este append do relatório; nenhum código, teste, MQL, payload, Git ou publicação foi alterado pelo revisor.
