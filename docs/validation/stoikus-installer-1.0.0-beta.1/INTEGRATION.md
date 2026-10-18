# Instalador Stoikus 1.0.0-beta.1 — evidências do candidato

Estado: **candidato local R2 gerado**, com correção integrada e **re-revisão independente R2 aprovada no escopo de código**. Provas nativas e distribuição pública pendentes. Base `0037bd3c8a7ab2b4e21f7fdcb60f66ed93230874`, branch `codex/stoikus-installer-20261014`, worktree `/private/tmp/jpw-stoikus-installer-20261014`. A fotografia é um delta não commitado sobre essa base; não representa um novo commit.

## Candidato exato

Arquivo: `Stoikus_Setup_1.0.0-beta.1_win-x64.exe`. Tamanho: **116779573 bytes**. SHA-256: **`e326a7e9e5fb2bf2dd36e6406468a10d82af8ba1696c6affa672ca056bbcb1eb`**. **Beta sem assinatura digital**: PE32+ AMD64, tabela Authenticode vazia. Runtime .NET 10.0.13 incorporado; SDK oficial 10.0.402. Esse EXE inclui as correções de recuperação R2; o R1 tem outro hash e não foi aprovado.

A compilação cruzada do instalador terminou com sucesso. Estrutura PE e publicação local não comprovam execução Windows, compatibilidade ARM por emulação ou compilação MQL. O site mantém o botão indisponível e o manifesto não declara URL, caminho público, hash ou tamanho de um instalador disponível. Nenhum EX5 é distribuído: o instalador deve compilar os quatro programas localmente. Recibo de quatro programas não aprova o SDK nem preenche `nativeArtifact`.

## Provas independentes

| Prova | Estado e limite |
| --- | --- |
| Motor | **56/56 PASS**, arquivos sintéticos reais; processo de compilador substituído nos testes |
| Lógica da UI integrada ao Core | **18/18 PASS**, classe de estado usada pelo Form; sem executar controles WinForms |
| Payload/distribuição | **9/9 PASS**; download/uso/pacote existentes também aprovados |
| Host/distribuição, scope all | **44/44 PASS**, novos recibos sobre inputs web/MQL congelados |
| Site, tier full | **57/57 PASS**, novos recibos sobre os mesmos 280 inputs |
| Builds Core/App e EXE cruzado | **PASS**, zero erros/avisos nos builds registrados |
| Revisões por entregável | **PASS após correções**, falhas originais preservadas |
| Revisão final R1 | **CHANGES_REQUESTED**, F1/P1 e F2/P2 reproduzidos; tentativa preservada |
| Revisão final R2 | **PASS no escopo revisado**, F1/F2 ADDRESSED; aprovação operacional não estabelecida |
| Compilação MQL dos quatro programas | **NOT_RUN** |
| Instalação/abertura/saúde MT5 | **NOT_RUN** |
| Windows x64 e Windows ARM/Parallels reais | **NOT_RUN** |
| Download real do EXE pelo navegador | **NOT_RUN** |
| WinForms nativo, teclado/Narrador/DPI | **NOT_RUN** |
| Aceite com usuário iniciante | **NOT_RUN** |
| Commit/push/merge/release/site | **NOT_RUN** nesta tarefa |

O guia HTML passou nos recortes Chromium 1280×900 e 390×844 sem overflow da página, pageerrors ou requisições externas; as duas capturas foram inspecionadas. A ilustração é esquemática, não captura de MT5. Isso não substitui aceitação nativa.

## Recuperação: tentativas preservadas

O EXE **R1**, 116760629 bytes, SHA-256 `6b46da92d652f31bb1842e071a7065094622221192d5906c56813b0bd4172af7`, recebeu **CHANGES_REQUESTED**. A prévia normal bloqueava o acesso à recuperação depois de interrupção sem recibo; token já cancelado ainda permitia rollback. EXE, metadados, freeze, contraprova e parecer R1 permanecem guardados.

A correção **R2** acrescenta **Recuperar** com detecção somente leitura, prévia própria, confirmação, exclusão mútua e processos fechados. Ações normais recusam diário pendente. Recuperação não compila nem instala; sucesso invalida a prévia e exige nova conferência da ação original. Token previamente cancelado preserva alvo e diário. Testes atravessam a classe real da interface e o Core com primeira instalação sem recibo, reparo parcial com recibo, conflito, processo aberto, cancelamento e reinspeção obrigatória.

Os RED e PRODUCT_FAIL das rodadas anteriores não foram substituídos por PASS. Core final56/56 e UI final18/18 têm logs próprios; o RED integrado12/18 teve guarda antiga extraída e scaffold inicial explicitamente descritos no relatório. A contraprova R1 contra assembly Release permanece separada.

## Referência de clareza

O crítico escolheu B antes de conhecer a identificação explícita das capturas: A era a instalação oficial do Position Sizer; B, o roteiro dos dois gráficos Stoikus. Identidades reconhecíveis e escopos distintos limitam o cegamento. Não há conclusão de superioridade funcional nem aceite de iniciante. O guia orienta Monitor em gráfico de apoio, retirada prévia de Observer/Accountant, Conta+NoCuda no gráfico de trabalho e término normal do abridor. Não ativa Supervisor ou negociação e não transforma cobertura insuficiente em aprovação.

## Ambiente e preservação

SDK .NET10.0.402 osx-arm64 obtido de builds.dotnet.microsoft.com e SHA-512 verificado contra metadados oficiais antes de extrair em `/private/tmp/jpw-dotnet10`. Runtime10.0.13. Sem instalação de .NET no sistema ou alteração de dependências MQL.

Windows11 no Parallels está em execução. `prlctl exec 'Windows 11' cmd.exe /c ver` retornou “The command is available only in Parallels Desktop for Mac Pro or Business Edition.” Isso limita o canal de automação do host disponível. O teste de abrir o EXE dentro do Windows continua possível, sem depender desse comando.

**141/141** fontes/documentos MQL e ZIPs de baseline permanecem byte-idênticos; somente o manifesto de downloads recebeu a entrada opcional do instalador. Os **280 inputs web/MQL** dos gates permaneceram inalterados após a correção C#. Os testes C#/build/revisão e a nova identidade R2 cobrem esse delta separadamente. Fotografias anteriores de estado/tarefa/handoff foram copiadas byte a byte para os arquivos `HISTORY-BEFORE-STOIKUS-INSTALLER`.

## Próxima validação

Em Windows x64 e Windows ARM/Parallels, usar os **mesmos bytes R2** numa instalação MT5 demo com pasta de dados separada. Registrar versões de Windows, MT5 e MetaEditor, hash do EXE, logs e quatro EX5 novos. Ensaiar os cenários do plano, transporte real pelo navegador, acessibilidade e roteiro com iniciante. Distinguir **instalado**, **compilado** e **abertura ainda não verificada**; compilação não aprova regras financeiras ou operação.

Qualquer rebuild que mude o hash precisa de provas ligadas à nova identidade. Publicação GitHub/site permanece posterior aos testes e à autorização correspondente. Não houve instalação em terminal, ativação de negociação ou modificação de bancos, preferências, estudos e gráficos nesta execução.

[Parecer independente integral, incluindo R1 e R2](evidence/final-review.md). Os registros locais e as tentativas anteriores acompanham a entrega em `Stoikus_Evidencias_1.0.0-beta.1_R2.zip`.
