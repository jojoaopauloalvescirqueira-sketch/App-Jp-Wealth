# Revisão independente Task 2

## Escolha visual registrada antes da leitura das fontes

Escolho **B** pela clareza dos próximos passos para iniciante e pela identificação de componentes: sequência numerada, destino a conferir, locais do Navegador, gráfico de apoio separado, comandos exatos e resultado esperado. A apresenta uma lista de arquivos e compilação, mas deixa menos explícito o próximo passo operacional no terminal.

Maior lacuna de B: o passo de retirar produtores legados exige reconhecer e localizar esses programas; nesta captura, não há nomes ou critério observável para concluir essa retirada com segurança.

Limite: os escopos diferem (programa único versus suíte em dois gráficos), e nomes e identidades são reconhecíveis. A comparação avalia apenas clareza do recorte exibido; não houve cegamento completo nem demonstração de vitória funcional, instalação real ou execução MT5.

Registro feito após abrir ambas as imagens reais com view_image e antes de consultar os arquivos de briefing, relatório, contrato ou diff. O arquivo mapping-private não foi consultado.

## Veredictos separados

- **Compliance: PRODUCT_FAIL**, por prévia que pode pertencer a outro alvo (F1) e fechamento automático mesmo quando há recuperação manual pendente (F2). A confirmação e o ciclo de cancelamento não satisfazem integralmente o contrato no candidate revisado.
- **Qualidade: PRODUCT_FAIL**, pelos mesmos defeitos em fluxos críticos. A escolha visual B não é aprovação do assistente nativo ou da instalação.
- Build cruzado: **PASS declarado no relatório Task 2**, não reexecutado nesta revisão. WinForms, teclado/Narrador/DPI, Windows/Parallels e MT5: **NOT_RUN**. A falta de execução nativa permanece limite, sem ser transformada em defeito observado.

## Findings

### F1 — [P1] Prenda a prévia ao alvo que foi inspecionado

**Arquivo:** `tools/stoikus-installer/src/Stoikus.Installer.App/WizardForm.cs:244-264`, com `:128-135`, `:203-221` e `:279-293`.

`SetBusy(true)` desabilita navegação e execução, mas a lista `_targets`, os rádios e o botão manual da página 0 continuam habilitados. Durante o `await Task.Run(() => _service.Inspect(_target, _action))`, o usuário pode mudar de A para B depois de o worker já receber A. `TargetChanged` atualiza `_target` e o texto dos caminhos para B e zera `_inspection`; porém a continuação do worker recoloca em `_inspection` a prévia de A, sem verificar identidade ou versão da seleção. A página seguinte exibe caminhos B com arquivos/impedimentos/candidatos de A. `ExecuteAsync` usa B. Em remoção, os recibos e listas de arquivos podem diferir; em instalação, os arquivos existentes e candidatos também. A reinspeção interna do Core protege integridade/identidade de arquivo, mas não fornece ao usuário a prévia de B que ele precisa aprovar.

**Correção delimitada:** desabilitar controles que mudam alvo/ação durante conferência; capturar alvo e ação em variáveis locais e descartar resposta se a seleção mudar. Impedir reparos/conferências concorrentes pelo mesmo mecanismo. A verificação somente leitura também deve mostrar resultado associado ao alvo capturado.

**Evidência:** encadeamento estático das chamadas acima e Core `InstallerService.cs:123-181,202-224`; não se alega reprodução WinForms. Contraprova útil após correção: atrasar uma inspeção de fixture A, tentar escolher B e demonstrar que não existe continuação com prévia A/destino B. Não exige repetir a suíte inteira.

### F2 — [P2] Não feche automaticamente quando a recuperação falhou

**Arquivo:** `tools/stoikus-installer/src/Stoikus.Installer.App/WizardForm.cs:300-308`.

Após Cancelar/fechar, `_closeRequested` é true. A condição de fechamento aceita qualquer `_result is not null`, inclusive `Success=false`. O Core retorna um `OperationResult` normal com `Success=false` e mensagem `Recuperação manual necessária` quando `Rollback` falha (`InstallerService.cs:380-403`); pode também acrescentar falha ao persistir relatório. Logo o assistente fecha e oculta o único resumo/atalho de relatório exatamente no caso em que ainda existe recuperação pendente. A proteção atual só preserva a janela em exceção sem resultado; resultado negativo não prova recuperação segura.

**Correção delimitada:** manter a janela e os detalhes quando o resultado for negativo, especialmente quando o contrato não expõe um estado estruturado de recuperação segura; liberar fechamento explícito posterior após a pessoa ler o resultado. Fechar automaticamente somente sob uma confirmação segura que o contrato realmente possa provar.

**Evidência:** caminho estático concreto do catch Core até o finally UI. Não há alegação de abandono de thread ainda ativa: a UI aguarda o retorno, mas confunde retorno com recuperação concluída. Contraprova útil: resultado sintético negativo com recuperação pendente após pedido de cancelamento deve manter o resumo/relatório acessível.

### O1 — [P3] Complete o procedimento de retirada dos legados para um iniciante

**Arquivo:** `tools/stoikus-installer/docs/guia-primeiro-uso.html:26,53`.

O guia completo resolve parcialmente a lacuna da captura B ao nomear Observer e Accountant; ainda manda retirá-los de todos os gráficos sem indicar como reconhecer a instância anexada, distinguir EA de indicador e confirmar a retirada. Como Ctrl+I é apresentado depois especificamente para indicadores, um iniciante pode procurá-los apenas nessa lista e iniciar o Monitor com outro produtor ainda ativo. Acrescentar um procedimento curto, conferível e validado para retirar cada tipo, antes do passo do Monitor. Esta observação editorial é separada dos dois defeitos de código bloqueantes.

## Cobertura e evidência desta revisão

Li briefing, contrato, relatório e diff Task 2 integral, fontes App/guia e documentos auxiliares; Core foi consultado somente para conferir consequências das chamadas públicas, sem revisão geral nem edição. Não consultei mapping-private. Nenhum código foi alterado, nenhum comando Git executado e nenhum MT5 iniciado.

Conferi por SHA-256 todos os oito arquivos listados no fingerprint do relatório: todos coincidem, incluindo WizardForm `c368ff69…`, ManualTargetForm `ddd8d06b…` e guia HTML `c41eac45…`. Validação somente leitura do payload gerado: archive hash e tamanho coincidem, conjunto ZIP/manifesto coincide e hashes/tamanhos das **82 entradas** coincidem. Isso comprova consistência desses arquivos, não identidade dos recursos de um EXE publicado nem execução nativa.

Implementação examinada sem novos achados específicos: descoberta não seleciona alvo; portátil é escolha explícita e exige pasta coincidente, com associação restante delegada ao Core; organização começa desmarcada com itens individuais CanOrganize; Verify é separado de Repair; Remove tem prévia e confirmação; relatório é texto interno limitado ao stateRoot com recusa de reparse point; nenhum conteúdo de relatório vira URL/comando; guia abre apenas por ação manual; recursos ZIP/manifesto são passados em bytes ao Core que valida hashes; beta não assinada é visível; guia distingue anexação/amostra/histórico e orienta negociação desmarcada/false-false-vazio; esquema está rotulado e tem title/desc, tabelas possuem captions/headers. Estes são resultados de inspeção de fonte, não PASS de comportamento nativo.

Nenhuma repetição dos testes já registrados é solicitada. A revisão não cobre autenticação da distribuição, assinatura, publicação, aceite humano ou rotina financeira do produto.

---

## Re-revisão delimitada — fix round 1, 14/10/2026

A revisão original e seu **PRODUCT_FAIL** acima permanecem como evidência da fotografia anterior. Esta seção julga somente F1, F2, O1 e regressões introduzidas nas correções, sem homologar Windows/WinForms/MT5 nem autorizar Git ou distribuição.

### Veredictos da rodada

| Item | Veredicto | Evidência no candidate atual |
| --- | --- | --- |
| F1 — prévia de A aplicada a B | **ADDRESSED** | `WizardForm.cs:233-261,284-313,326-345` e `WizardOperationState.cs:18-52` |
| F2 — fechamento com recuperação pendente | **ADDRESSED** | `WizardOperationState.cs:54-55` e `WizardForm.cs:352-360` |
| O1 — procedimento para retirar legados | **ADDRESSED** | `guia-primeiro-uso.html:27-35` |

**Compliance desta rodada: PASS no escopo revisado. Qualidade desta rodada: PASS no escopo revisado.** Nenhum novo finding concreto foi identificado nas alterações delimitadas. Isso encerra os dois bloqueios da revisão original e a observação editorial para este candidate; não é aprovação funcional nativa ou aceite operacional.

### Fundamentação

**F1:** a lista, rádios, botão manual e reparo agora são desabilitados durante a conferência e os handlers recusam início concorrente. `BeginInspection` captura alvo, ação, modo, revisão e número de pedido; Verify/Inspect recebem exclusivamente o snapshot. A continuação só publica a resposta se o snapshot ainda corresponder à seleção corrente; mudanças programáticas invalidam a revisão, incluindo A → B → A. A execução exige a prévia atual antes e depois da confirmação modal e passa ao Core o alvo/ação capturados nessa prévia. Conferi a integração concreta no Form; a classe não é apenas um auxiliar usado por testes.

**F2:** `CanAutoClose` permite fechamento automático exclusivamente para pedido explícito com `Success=true`; resultado false ou nulo mantém a janela. O Form usa essa regra, restaura Fechar e mostra a orientação de ler falha/relatório e eventual recuperação pendente. O fechamento explícito posterior permanece permitido. Não há classificação de recuperação por busca de texto na mensagem.

**O1:** o guia distingue EAs de indicadores, nomeia os três legados do catálogo, orienta usar a lista de Experts dos gráficos abertos, preservar Entradas, retirar somente a instância identificada e reabrir a lista para confirmar ausência. Identidade duvidosa bloqueia o próximo passo do Monitor por orientação expressa. Conferi nesta rodada a [ajuda oficial do MT5](https://www.metatrader5.com/en/terminal/help/charts_advanced/charts_objects_list): ela documenta a lista abrangendo todos os gráficos abertos, identificação de gráfico, Properties e Delete, separadamente de Ctrl+I. Esta conferência documental não comprova que o roteiro foi executado nativamente.

### Fingerprint e evidências examinadas

Li `task-2-fixround1-report.md`, o JSON de fingerprint, o pacote `task-2-fix1-current.diff` e os fontes/testes/documentos alterados. Comparei por parsing local o pacote atual contra o pacote original da primeira revisão, sem Git: diferenças pertinentes restritas a WizardForm, nova WizardOperationState, procedimento HTML, duas notas documentais e ui-tests. **Os 11 hashes SHA-256 do fingerprint coincidem com os arquivos atuais**, inclusive WizardForm `8761418c…`, WizardOperationState `9ec5ea48…` e guia `6680d377…`.

Examinei os registros já existentes, sem repetir os comandos:

- `task-2-fixround1-red.txt`: **3/12 PASS, 9 FAIL**, usando extração das regras anteriores; não é reprodução da janela Windows.
- `task-2-fixround1-green.txt`: **12/12 PASS**, lógica real compartilhada por link com o App; testes de estado, sem controles WinForms.
- `task-2-fixround1-build.txt`: **PASS, 0 warnings / 0 errors**, build cruzado App + Core, 21.40 s.
- `task-2-fixround1-browser.json`: recorte HTML em 1280×900 e 390×844, sem overflow horizontal, sem requisições externas e sem pageerrors; quatro passos principais e quatro passos de retirada.

O csproj dos ui-tests compila diretamente `WizardOperationState.cs` do App. Os cenários cobrem bloqueio enquanto aguarda, descarte de resposta A/B e revisão A/B/A, ação/modo, concorrência, invalidade de Verify para autorizar Repair e fechamento negativo/nulo/positivo. A revisão dos handlers complementa esses testes, mas não transforma o seu escopo em automação nativa.

Windows/WinForms, teclado/Narrador/DPI, Parallels, retirada de EAs e MT5: **NOT_RUN**. Build confirma apenas build. O EXE de distribuição precisa refletir os bytes corrigidos por novo publish do responsável; esta re-revisão não verificou esse artefato. A/B não foi repetido; a escolha e os limites originais permanecem. Somente este relatório foi escrito; nenhum código, teste, Git ou payload foi alterado pelo revisor.
