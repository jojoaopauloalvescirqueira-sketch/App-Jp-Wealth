# Roteiro manual da interface — beta 1.0.0-beta.1

Estado atual dos itens abaixo: **NOT_RUN no Windows**. Crossbuild não valida desenho, automação WinForms, teclado, leitor de tela ou interação MT5. Use uma instalação MT5 isolada e dados sintéticos para os ensaios que gravam arquivos. O guia HTML pode ser inspecionado separadamente em navegador local.

| Cenário | Resultado exigido |
| --- | --- |
| Abrir com um único MT5 descoberto | Nenhum alvo selecionado; Continuar desabilitado até seleção explícita |
| Abrir sem MT5 | Instrução para seleção manual; ausência não vira sucesso |
| Recurso ausente ou hash inválido | Erro legível, ação indisponível e orientação de obter cópia íntegra |
| Selecionar manualmente pasta normal | Dados, terminal64.exe e metaeditor64.exe visíveis; associação origin validada pelo motor |
| Marcar portátil | Marcação começa desativada; dados devem coincidir com a pasta dos executáveis |
| Verificar | Somente Verify executado; nenhuma chamada ExecuteAsync; retorno legível e reparo separado |
| Trocar alvo/ação durante inspeção atrasada | Controles de seleção desabilitados; captura imutável de alvo/ação/modo; qualquer mudança programática invalida e descarta a resposta antiga |
| Preparar reparo | Nova prévia Repair; nenhum reparo até conferência e confirmação final |
| Prévia com impedimentos | Motivos legíveis; próximo passo bloqueado |
| Diário pendente após primeira instalação interrompida, sem recibo | Prévia normal permanece bloqueada; Ver recuperação continua disponível e produz prévia própria somente leitura |
| Recuperar operação interrompida | Snapshot do mesmo alvo, prévia e confirmação explícita; nenhum legado selecionado, compilação ou instalação nova |
| Recuperação concluída | Resultado e relatório visíveis; Reinspecionar destino refaz a ação original; nenhuma prévia anterior autoriza instalar/reparar/remover |
| Recuperação com conflito, processo aberto ou token já cancelado | Arquivos protegidos, motivo legível e relatório quando produzido; nenhum fechamento automático de falha |
| Organização opcional | Checkbox e itens inicialmente desmarcados; só candidatos CanOrganize disponíveis |
| Desmarcar organização | Seleções individuais removidas e nenhum caminho de organização enviado |
| Remover | Prévia específica e confirmação final com destino; conclusão não instrui abrir programas como instalados |
| Aplicar | Interface responsiva; Voltar e Continuar indisponíveis durante mutação |
| Cancelar/fechar na compilação e na cópia | Solicitação ao CancellationToken; janela aguarda retorno; falha sem resultado mantém detalhes visíveis |
| Cancelar e receber Success=false | Janela continua aberta, com falha e relatório acessíveis; nenhuma inferência por texto; Fechar explícito permitido após retorno |
| Erro ou resultado Success=false | Nenhuma mensagem de sucesso; detalhes preservados; progresso não forçado a 100 |
| Ler relatório | Texto interno; arquivo deve estar sob stateRoot, sem reparse point, até 10 MB; não executa caminhos do relatório |
| Abrir guia | Somente HTML incorporado extraído para pasta própria no estado; abertura manual no navegador |
| Guia detalhado | LEIA_PRIMEIRO.md original do payload validado lido como texto, sem execução de links ou scripts |
| Tab, Shift+Tab, Espaço, Enter e Alt | Ordem coerente; seleção de legado por Espaço; confirmação final padrão em Não |
| 100%, 150%, 200% e alto contraste | Textos e controles legíveis, painel rolável e ações alcançáveis |
| Narrador/leitor de tela | Nomes acessíveis de alvos, caminhos, prévia, progresso e lista; verificar anúncio efetivo de mudanças |

O aplicativo usa fontes do sistema, cores do sistema nos controles nativos, escala por DPI, campos de texto somente leitura selecionáveis e botões com mnemônicos. Isso descreve implementação, não certificação de acessibilidade. Escala e anúncios precisam de ensaio nativo.

## Regressões portáteis de estado

`dotnet run --project tools/stoikus-installer/ui-tests/Stoikus.Installer.UiTests.csproj` compila no net10 a mesma classe pura `WizardOperationState.cs` usada pelo aplicativo. As regras cobrem captura e revisão do alvo/ação/modo, bloqueio de conferências concorrentes, descarte de A após troca para B (inclusive A → B → A), verificação incapaz de aprovar reparo e fechamento automático condicionado a pedido explícito e `OperationResult.Success=true`. Resultados negativos ou ausentes mantêm a janela aberta. Esses testes executam lógica real C#; não substituem ensaio dos controles WinForms.

Os testes de integração em `RecoveryIntegrationTests.cs` usam o Core real e arquivos sintéticos temporários junto com as decisões de disponibilidade, snapshot e confirmação efetivamente usadas pelo Form. Cobrem EX5 parcial sem recibo, reparo parcial com recibo anterior, conflito preservado, processo aberto, cancelamento anterior à chamada e confirmação explícita. A substituição de processo/compilador só prepara a instalação sintética necessária ao cenário de reparo; não é prova MetaEditor ou MT5.

## Evidência HTML no host

Em 14/10/2026, Chromium headless via Playwright 1.60 abriu o HTML local em 1280×900 e 390×844. Nas duas larguras: sem overflow horizontal da página, sem requisições externas e sem pageerrors; quatro passos presentes. As capturas completas foram visualizadas. A tentativa inicial em sandbox recebeu `MachPortRendezvousServer ... Permission denied`; a repetição autorizada fora do sandbox renderizou normalmente. Esse resultado não é ensaio WinForms nem MT5.
