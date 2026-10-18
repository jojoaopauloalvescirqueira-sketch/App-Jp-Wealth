# Task 2 — recuperação explícita integrada, finalfixwave

Correção implementada e congelada para nova revisão, em resposta a `final-review.md`. O PRODUCT_FAIL anterior permanece registrado. Esta rodada não declara PASS da revisão independente, do formulário nativo ou do MT5.

## Fluxo efetivo do Form

Depois de escolher um alvo e pedir conferência, `InspectAsync` consulta `HasPendingRecovery` em somente leitura usando o mesmo snapshot imutável de alvo/ação/modo. A página da prévia oferece **Ver recuperação da operação interrompida** se houver pendência válida, mesmo quando a prévia normal de instalar/reparar/remover está bloqueada. A decisão `WizardOperationState.CanOfferRecovery` não exige `CanProceed` da ação normal. Alterar a seleção invalida também a indicação de pendência.

O botão inicia outra prévia, agora `Inspect(target,Recover)`, conservando revisão e identidade. A recuperação exige seu checkbox de conferência e confirmação modal; `ConfirmedSelection`, compartilhado com os testes portáteis, exige prévia atual, confirmada e permitida. `ExecuteAsync` recebe exclusivamente Recover e lista de organização vazia. Não há compilação nem instalação nova nesse caminho.

Quando a recuperação retorna sucesso, `CompleteRecovery` — método real compartilhado entre o Form e os testes — invalida a prévia anterior. A mensagem informa **recuperação concluída** e o próximo passo é **Reinspecionar destino**, refazendo a ação original e exigindo outra confirmação. O fluxo Recover não conduz à página de abrir painéis nem rotula uma instalação nova como concluída. Resultado negativo ou ausente permanece visível; fechamento automático conserva a regra pedido explícito + Success=true. Falha retornada permite ler o relatório e pedir reinspeção manualmente.

## Regressão integrada com Core real

Novo `ui-tests/RecoveryIntegrationTests.cs`, no projeto net10 existente, atravessa as decisões e o estado de produção usados pelo Form e a API real do Core. Os arquivos de terminal, dados, diário, recibos e backups são fixtures sintéticas reais temporárias; o processo/compilador é substituído somente porque os ensaios rodam no macOS. A fixture de primeira instalação começa diretamente no ponto de interrupção após gravar o EX5 e antes do recibo. A fixture de reparo instala via Core real com compilador sintético, preserva o recibo e planta o diário parcial. Nenhum resultado é prova de MetaEditor ou MT5.

Casos novos:

1. Primeira instalação interrompida: EX5 parcial e nenhum recibo; três prévias normais bloqueadas atravessam snapshots reais e não podem ser confirmadas; recuperação continua acessível, prévia readonly preserva bytes e diário, confirmação chama Recover, EX5 parcial sai, compilador não é chamado e a nova prévia Install fica possível.
2. Reparo parcial com recibo anterior: prévia Repair bloqueada não executa, Recover restaura EX5 e recibo anteriores byte a byte, não recompila e exige nova prévia Repair.
3. Conflito: bytes modificados são preservados, a prévia de recuperação bloqueia confirmação, eventual chamada direta também falha com relatório/pêndencia mantidos e não fecha automaticamente a janela.
4. Processo aberto: descoberta da recuperação continua visível; prévia bloqueia confirmação com motivo.
5. Token já cancelado: após prévia e confirmação válidas, a chamada retorna falha sem mudar alvo nem diário; pendência e detalhes continuam disponíveis, sem compilação.
6. Confirmação: sem consentimento, com ação diferente ou snapshot invalidado não há seleção executável; busy bloqueia o botão de recuperação.

Os 12 testes de estado anteriores permanecem no mesmo projeto.

## Evidências preservadas

| Escopo | Resultado e arquivo |
| --- | --- |
| RED integrado inicial | **12/18 PASS, 6 FAIL**, `task-2-finalfixwave-red.txt` |
| GREEN integrado final | **18/18 PASS, zero FAIL**, `task-2-finalfixwave-green.txt` |
| Crossbuild App + Core real | **PASS, zero warnings / zero errors, 21.57 s**, `task-2-finalfixwave-build.txt` |
| Guia HTML após atualização | **PASS no recorte observado**, desktop 1280×900 e tela estreita 390×844; sem overflow da página, requisições externas ou pageerrors; `task-2-finalfixwave-browser.json` |
| Inspeção das duas capturas completas | Capturas abertas com view_image; sem corte/sobreposição percebidos. `task-2-finalfixwave-guide-1280.png` e `task-2-finalfixwave-guide-390.png` |
| WinForms, teclado/Narrador/DPI, Windows/Parallels, MT5 e ensaio iniciante | **NOT_RUN** |

Precisão do RED: os testes foram escritos antes da correção; rodaram contra a guarda de acesso anterior extraída e contra a introdução inicial da nova API Core, cujo probe ainda era scaffold false fornecido pelo proprietário do Core para o RED. A saída mostra falhas comportamentais esperadas de rota/prévia inexistentes, sem erro de compilação. Não é repetição nativa do formulário original; a contraprova contra o assembly anterior permanece em `final-review.md`. O GREEN usa o Core implementado e a classe real do aplicativo, sem scaffold.

Comandos principais, SDK oficial 10.0.402:

```text
DOTNET_CLI_HOME=/private/tmp/jpw-dotnet-home NUGET_PACKAGES=/private/tmp/jpw-nuget /private/tmp/jpw-dotnet10/dotnet run --project tools/stoikus-installer/ui-tests/Stoikus.Installer.UiTests.csproj --no-restore --verbosity minimal
DOTNET_CLI_HOME=/private/tmp/jpw-dotnet-home NUGET_PACKAGES=/private/tmp/jpw-nuget /private/tmp/jpw-dotnet10/dotnet build tools/stoikus-installer/src/Stoikus.Installer.App/Stoikus.Installer.App.csproj --no-restore --verbosity minimal
```

## Escopo e identidade

Alterados somente App/WizardForm.cs, App/WizardOperationState.cs, docs/guia-primeiro-uso.html, docs/VALIDACAO-INTERFACE.md, ui-tests/Program.cs e novo ui-tests/RecoveryIntegrationTests.cs, mais os relatórios e evidências autorizados. Core/API e testes próprios pertencem ao outro agente e não foram editados por este agente. Nenhum Git, publish de EXE, payload, MQL, metadado público ou gate foi alterado aqui.

`task-2-finalfixwave-fingerprint.json` contém hashes de todos os 12 arquivos de fonte/docs/testes do escopo App/UI. Fontes congeladas após o build; apenas relatórios foram escritos depois. O EXE anterior não representa estas correções; recompilação/publicação de arquivo candidato e nova identidade pertencem ao responsável pela integração. Distribuição pública e aceite permanecem separados.
