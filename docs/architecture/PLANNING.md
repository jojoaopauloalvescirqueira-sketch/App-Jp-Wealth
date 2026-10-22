# Planejamento — fechamento guiado e recuperação de revisão

Fonte: plano aprovado22/10/2026, `2026-10-22-planning-monthly-close.md`. A falta de resultado realizado oferece entrada explícita em percentual/US$ na própria janela. Prévia não grava; Salvar resultado e revisar fechamento confirma somente `recordResult` e então prepara revisão nova, com conferência desmarcada. Confirmar fechamento usa `finalizeMonth` existente. Cancelar após salvar informa resultado registrado e mês aberto. Não presume zero, aporte previsto ou fechamento em lote.

`previewFinalizeMonth` conserva ok/status/errors/row e acrescenta blockers[{code,month}]: MISSING_RESULT, PREVIOUS_UNCONFIRMED (primeiro anterior pendente), ALREADY_FINALIZED, FUTURE_MONTH, INVALID_CONTEXT ou NOT_COMPUTABLE. Consulta apenas; validação financeira original permanece fonte do aceite.

Rascunhos preservam campos, mas revisão e consentimentos anteriores não autorizam dados novos. Atualizar revisão é explícito, com mesma conta/plano/sessão válida e nova conferência. Conflito/recusa preservam entrada; resultado indeterminado bloqueia repetição. Mudança de plano/invalidação de sessão exige novo fluxo. Escopo produto e verificadores têm CHGs próprios; nenhuma fórmula, escritor, schema ou preferência nova.

[Resultados e limites](../validation/planning-monthly-close-20261022/README.md). Aceite humano separado.

## Contratos históricos preservados

# Planejamento — contrato mensal compacto e editável

Fonte: [plano humano aprovado](../superpowers/plans/2026-10-21-planning-monthly-inline.md),21/10/2026. [Produto](../work/CHG-JPW-PLANNING-INLINE-PRODUCT-20261021.md) e [verificadores](../work/CHG-JPW-PLANNING-INLINE-TESTS-20261021.md) têm escopos separados. Este contrato substitui somente os controles mensais e as preferências visuais anteriores; Consolidado, formulário, Stoikus, fórmulas, fatos e histórico permanecem.

- Leitura mensal: sete colunas a partir de900px úteis, três abaixo, resultadoUSD/percentual juntos eBRLsecundário onde disponível. Linhas comuns em desktop até64pxCSS, com altura automática para valores maiores e alvos44px. Um detalhe expandido; dados completos, sem rolagem horizontal.
- Célula acionável por clique/toque/Enter abre edição com Salvar/Cancelar; Escape cancela. Clicar fora e perder foco não grava nem descarta. Resultado factual aceita percentual ouUSD, exige revisão e confirmação contextual e usa somente recordResult existente. Aportes e saques conservam lançamentos individuais/IDs; custoBRLdo aporte obrigatório, BRLrecebido no saque opcional, sem preenchimento automático pela cotação. Correções informam fechamentos dependentes a reconferir.
- Consulta aditiva somente leitura `JPWPlanning.queries.previewResultInput({accountId,month,unit,value})`: unit PERCENT ouUSD, value numérico finito; PERCENT são pontos percentuais. Lê abertura atual, converte para centavos e delega a previewFlow existente. Retorna validade/erros, abertura, resultadoUSD e taxa derivada do valor arredondado. Sem abertura positiva, percentual indisponível; USD conserva validações anteriores. Nenhum campo financeiro, escritor ou fórmula muda.
- Futuro conserva setProjection, com Salvar explícito. Digitação, prévia, expansão, filtros e redimensionamento não gravam fatos. Dados calculados permanecem calculados. Rascunho, foco e cursor sobrevivem à mudança de modo; mudança de contexto exige resolver edição pendente, sem renovar silenciosamente o token.
- Verde passado é temporal, inclusive pendente; não significa Finalizado. Mês atual conserva seu destaque. Preferências Destacar meses passados e Todos os meses/Atual em diante são independentes do filtro de ano, cujo padrão é Todos. Grupos vazios ocultos; subtotais identificam o ciclo completo, mesmo quando filtrado.
- Chave isolada `jpwealth_planning_monthly_view_v1`: somente versão e duas preferências booleanas. Fora deS e Backup Completo, integra limpeza explícita de preferências. Falha permite uso temporário com aviso; conteúdo incompatível é preservado. Finalização invalida controladores e confirmações pendentes pelo ciclo existente.

[Execução e limites](../validation/planning-monthly-inline-20261021/README.md): somente os recibos deste candidato determinam a validação atual. Resultados anteriores são históricos; aceite humano separado.

## Contratos históricos preservados — controles substituídos conforme contrato acima

# Planejamento — contrato de apresentação atual

Fonte: [plano humano aprovado](../superpowers/plans/2026-10-21-planning-consolidated-monthly-compact.md),21/10/2026. Substitui exclusivamente a distribuição visual anterior de18colunas por grade essencial e detalhes; fórmulas, calendário financeiro, estado e comandos abaixo permanecem. [Produto](../work/CHG-JPW-PLANNING-COMPACT-20261021.md) e [testesN3](../work/CHG-JPW-PLANNING-COMPACT-TESTS-20261021.md) têm contratos separados.

- Consolidado agrupa Posição confirmada, Projeção e objetivos e Referências de câmbio. Conserva indicadores, fechamento de referência, gráficos, comparativos e estados pendentes. Ano calendário local vigente aparece em verde suave/Em andamento, distinto de confirmação financeira/ano de projeção.
- Mensal: largura útil>=900px apresenta Mês, Saldo inicial, Resultado(percentual+USD/BRL), Saque, Aporte, Patrimônio(USD/BRL), Finalizado. Abaixo900px mantém Mês, Resultado e Patrimônio, com detalhe inline por mês. Um detalhe aberto; US$principal/R$secundário somente onde o read-model fornece ambos. Sem overflowhorizontal/cortes/abreviações; rolagementevertical permitida.
- Detalhes conservam saldo/controles no modo compacto e os dados complementares em ambos: pagoBRL, câmbio do mês, preço médio, última cotação, variação e cobertura/situação do custo. Fase integra agrupamentos dos12meses; estado acompanha mês.120meses/subtotais de ciclos preservados, diferentes de anoscivis.
- Controles únicos são reposicionados, nunca clonados, durante mudança de modo. Conservar valorparcial/foco/seleção/scroll; expandir detalhe antes de deslocar campo focado. Trocar conta/estado e desativar limpa observadores locais, sem persistência nova. Navegar/expandir/redimensionar não grava.
- Calendário e confirmação independentes: mês atualverde/texto mesmo quando finalizado; passado finalizado tem símbolo/texto; passado pendente é identificado; futuro é projetado e mantém avisos de premissas pendentes. Nenhum fechamento automático por data. Reabrir/finalizar/corrigir usam os protocolos anteriores.
- Comece aqui/formulário/Stoikus, três abas públicas, engine/state/backup e PDF próprio completo não são substituídos. APIs públicas financeiras inalteradas. Demais normas de [qualidade visual](../governance/UI-VISUAL-QUALITY.md) permanecem.

## Contratos anteriores preservados — a distribuição visual de18colunas é histórica

## Controles e verificação visual

Stoikus é um menu vertical de13ações em5grupos: Contas; Registros mensais; Correções; Consulta e relatórios; Reinício. Usa limite320px/gutter12px/rolagem disponível, posição abaixo ou acima sem encobrir o acionador, setas/Home/End/Enter/Escape e Tab. Fecha por ação, interação externa, troca de área ou diálogo, sem alterar seleção implícita de contas ou contratos dos comandos.

Fechar mantém nome acessível e alvo44×44 com SVG simétrico. Ver sua previsão conserva ordem e destino, centralizando conteúdo nos dois eixos. [Contrato visual](../governance/UI-VISUAL-QUALITY.md) exige medir conteúdo interno, além da caixa. Teste inicial `tools/ui_visual_quality_test.py` compõe standard/full e declara cobertura/limites. Fórmulas, dados, rascunhos e confirmações existentes permanecem sob contratos abaixo. [Execução e provas](../validation/planning-controls-visual-quality-20261021/README.md).

### Contrato anterior preservado

# Planejamento patrimonial — candidato de 20/10/2026

Menu principal independente, após Research e antes de Forex na ordem padrão editável. **Comece aqui, Consolidado e Preenchimento mensal** são as únicas três abas públicas. Referência é um dado interno dos comparativos, sem quarta aba. As visões anteriores ficam preservadas em fotografias históricas, não na navegação atual. Os aliases `forex-planning` e `fxplan` resolvem para `planning`; não dependem de Forex ativo. O congelamento remove menu, Dashboard e acesso, preservando os dados e o preenchimento.

## Referência e limites

Modelo: planilha original [Planejamento](https://docs.google.com/spreadsheets/d/1Wo1Qwvfd7okSClnCwKateirerP77Z0fWGHmg51wG2EA/edit), dez arquivos de scripts originais verificados em 19/10, incluindo o apêndice Horizonte. A correção solicitada em20/10 substitui a apresentação adaptada do build ff0f078f por reprodução do fluxo e dos textos originais. O projeto Apps Script vivo, manifesto e acionadores instalados não foram acessados; não há alegação de execução Google autenticada. Identidades e hashes estão na [decisão](../decisions/2026-10-20-planning-reference.md). O aplicativo funciona independentemente do Google Sheets. Não importa contas nem registros da planilha.

Perfis hipotéticos mensais: High Risk 6%, Base 3%, Conservador 2%, Segurança 1,5%; MDD informativo 40%,20%,13%,10%. Não são perfis operacionais Forex, promessas, autorização ou política de risco. Cada plano tem 120 meses, com calendário próprio e início entre janeiro de1900 e dezembro de2199, como na referência. O Consolidado usa a união completa dos calendários, sem cortar o maior a 120 meses.

O câmbio corrente reutiliza a referência diária do site. Fonte, data econômica e consulta são distintos. Novas metas em BRL exigem consulta realizada nas últimas24horas, mantendo a data econômica distinta. Metas em BRL capturam uma conversão ao criar/alterar a meta; não mudam com novas consultas. Meses passados usam referência histórica do próprio mês ou o snapshot do fechamento. Falta de câmbio mantém USD disponível e BRL indisponível. A consulta histórica é técnica, sob demanda, com data, cache e cancelamento; não grava movimentos. O endpoint histórico documentado pelo [Frankfurter](https://frankfurter.dev/) recebe o último dia do mês, limitado ao provedor BCE. Diferenças de cotação do Google Finance são uma exceção expressamente aprovada.

## Fluxo de uso

1. **Comece aqui** contém as instruções originais e **Preencher o formulário**. O formulário pergunta, nessa ordem: ano e mês iniciais; capital; aporte opcional; parada opcional; perfil escolhido em comparação gráfica; padrão de vida atual opcional e renda ideal em BRL/USD; identificação opcional; opções do plano. Nova conta não recebe um perfil escolhido automaticamente. O botão abre a janela em todos os estados: criar no primeiro uso, editar conta explicitamente selecionada ou única ativa, e escolha explícita criar/editar quando há várias contas sem seleção. Essa escolha local não altera o filtro do Consolidado nem escolhe a primeira conta automaticamente. A prévia mantém visíveis os estados de custo atual e renda dos sonhos, com prazo desde início e mês/ano ou explicação do dado pendente. No desktop acompanha os campos; em espaço estreito Ver sua previsão leva ao bloco. Revisão, voltar e cancelar não gravam contas. Confirmar libera o plano; a mensagem de sucesso leva ao Consolidado.
2. **Consolidado** usa Conta/Todas as contas, quatro indicadores no mesmo fechamento, preço médio dos aportes, dólar de referência e prazos individuais. Uma única conta ativa fornece os prazos mesmo em Todas; várias não somam objetivos pessoais. O ano da projeção é independente do período do gráfico. Há visão anual completa ou matriz de meses nas linhas/anos nas colunas, com os quatro indicadores nativos. O gráfico realizado oferece quatro modos e somente meses confirmados. Planejado × realizado usa o mesmo fechamento e informa desvio USD e percentual, sem percentual fabricado sobre base zero.
3. **Preenchimento mensal** conserva as dezoito colunas financeiras significativas D:U e os subtotais a cada doze meses do plano. São diferentes dos resumos por ano civil no Consolidado. Registrar rentabilidade pergunta mês e resultado total USD; aporte pergunta USD e BRL pago; saque pergunta USD e BRL recebido opcional. Todos exibem revisão antes da confirmação; alterações não confirmadas não se tornam fatos. A taxa do resultado é derivada do saldo de abertura, antes dos fluxos no fim do mês.
4. Campos azuis de meses futuros são editáveis diretamente. Vazio em taxa calcula0% provisório; aporte vazio calcula zero e permanece visualmente vazio, distinto de zero explícito. Premissas admitem precisão livre como o formulário; fatos realizados mantêm centavos. Ao editar o formulário sem **Reaplicar**, cada projeção existente permanece. Reaplicar substitui taxa e aporte somente nos meses futuros não finalizados, inclusive zeros de uma parada anterior. Aporte previsto expira ao fim do mês; registro efetivo o substitui, não soma os dois.
5. Finalizar exige resultado registrado e conferência dos fluxos, em sequência. Correção substitui o total e preserva a versão anterior; invalida fechamentos dependentes. Os fatos e rascunhos permanecem. Ausência de cotação mantém USD disponível e BRL indisponível, conforme o contrato independente/offline.
6. **Referência interna** conserva metadados, trajetória e aporte acumulado para os comparativos, sem página pública. Chamadas legadas reference/accounts abrem Consolidado; não reintroduzem uma quarta tela. Referência financeira é preservada nas edições e no reinício de uma conta. **Iniciar outro plano** cria nova referência, mas havendo fatos exige antes o reinício dedicado. Início/capital só podem mudar sem fatos ativos.
7. **Reiniciar** distingue uma conta e todas: prévia, alcance, identificação, contagens e confirmação literal. Uma conta arquiva o plano completo e reaplica as premissas atuais; todas arquivam cada plano e voltam ao formulário inicial. A identidade da primeira fica reservada para a confirmação, sem inventar perfil/capital/objetivos ativos. Nenhum arquivo histórico é apagado. A referência de renda após reinício individual usa as metas atuais, mantendo separada a referência financeira.
8. **Planejar quando parar de aportar** pertence ao formulário. O comparativo usa trajetórias, limite, primeira data viável e peso dos primeiros/últimos aportes; escolher data não grava. Alterar premissas invalida a escolha inclusive no rascunho serializado. Somente confirmar o formulário aplica a parada atomicamente com a configuração. Plano novo admite a data desde o mês anterior ao início; conta existente respeita calendário/histórico atual. Paradas não restauram automaticamente aportes já zerados.
9. O menu Stoikus operacional separado conserva cadastro, edição, reinício, histórico, explicação dos prazos, meses, lançamentos, correções, custos pendentes e relatório. Acompanhar registro e Atualizar visão eram infraestrutura ou redesenho redundante e deixam a UI; os protocolos de confirmação/idempotência permanecem. Os blocos retirados pelo autor da apresentação nativa (objetivos projetados, esforço de aumentar aportes e câmbio detalhado) não são expostos; preço médio, dólar e prazos atuais no topo são mantidos. O PDF usa composição própria baseada em RelatórioA1:K36, com escopo do Consolidado e impressão local A4paisagem, em vez de imprimir a tela atual. O mecanismo local de impressão difere do download autenticado do Google.

O preço médio de aquisição inclui somente aportes com custo BRL conhecido; capital inicial, rendimentos e saques não são novas compras de USD. A cobertura é explícita. Metas identificam o primeiro resultado mensal que alcança a renda informada, não uma promessa de retirada sustentável. Meses restantes usam o mês corrente; uma alteração da própria meta suspende atribuir diferenças à execução.

## Dados e gravação

Agregado opcional `S.patrimonialPlanning`, schema1, revisão, contas, arquivo, auditoria e recibos de operações. Campos opcionais `pendingConfiguration` reservam a identidade após reinício total e `plan.incomeBaselineGoals` preserva a base de renda após reinício individual; envelopes antigos continuam válidos sem eles. Ausência é leitura vazia. Versão futura ou forma inválida bloqueia comandos; o conteúdo original permanece. Campos desconhecidos são preservados. Não há migração automática de `S.fxPlanning`.

`JPWPlanning.engine` é puro; `queries` retorna cópias e modelos de leitura; `commands.execute(type,payload,token)` usa o escritor existente de documento completo com comparação e read-back. A memória adota o candidato somente após CONFIRMED. REFUSED preserva o rascunho; CONFLICT exige revisão; UNKNOWN bloqueia repetição até recuperação. Token vincula revisão, plano e sessão; confirmações não usam valores antigos silenciosamente. Repetição exata de uma operação confirmada não duplica lançamento. Isso conserva o protocolo existente de concorrência, sem alegar transação multiaba além dele.

UI, gráficos, tabelas e PDF consomem o mesmo modelo. A UI não implementa fórmulas financeiras. Filtrar, navegar e simular não chamam writers. Rascunhos permanecem em memória e no mecanismo existente de Backup Completo; importados são disponibilizados para leitura/cópia e conferência manual, sem reabertura automática de comandos; a gravação financeira exige ação explícita. Adoção de outra base ou finalização invalida callbacks/rascunhos. Configurações de uso não escrevem no agregado.

## Implementação e compatibilidade

- `30-accounting/06-planning/01-engine.js`: calendário, cálculo, metas, consolidação e simulação.
- `02-state.js`: validação, queries, comandos confirmados, versões e histórico.
- `03-ui.js`: montagem sob demanda, visões, formulários, ajuda, impressão e rascunhos.
- CSS escopado a `#planning` em `app.css`; scripts clássicos no manifesto; artefatos gerados oficialmente.
- Contabilidade continua exibindo fatos da conta/período operacional, sem atribuir um plano global a ela. O adaptador canônico de Reservas foi preservado em `02-accounting-engine.js`, separado do motor novo.
- Legado `fxPlanning` permanece no documento e no Backup Completo. O legado permanece recuperável pelos mecanismos existentes de backup/exportação, sem avisos ou botões nas três páginas do novo planejamento; não é convertido para a nova estrutura. A implementação antiga deixa a distribuição ativa.

## Verificação

Proteções permanentes: `planning_engine_test.js`, `planning_state_test.js`, `planning_navigation_test.js`, `planning_quote_test.js`, `planning_boundaries_test.js`, `planning_ui_test.py`, `planning_distribution_test.py`, `planning_parity_engine_test.js` e `planning_parity_test.py`, mais regressões do shell, Dashboard, disponibilidade, backup, finalização e distribuição. O gate troca a entrada do produto aposentado pelas suítes novas correspondentes; os demais checks permanecem. Mapeamento dos testes aposentados e execução por revisão ficam no relatório da tarefa. Testes de referência externa são adicionais e exigem os originais locais; o gate permanente usa oráculos sintéticos autocontidos.

Matemática, persistência, browser automatizado, comparação independente e aceitação humana são critérios distintos. Consulte a entrega atual e seus recibos; fotografias históricas não comprovam aprovação deste candidato.

## Limites da comparação

A independência aprovada usa armazenamento e escritor local, não as permissões owner/editor, fila, triggers e locks do Google. A comparação executável do formulário original usa o HTML/JavaScript extraído, com respostas de leitura e confirmação sintéticas; é prova do fluxo daquele fonte, não de execução nativa autenticada. As cotações seguem a exceção aprovada para a fonte diária do site. Resultados automatizados, fonte-harness, Google vivo e aceite humano são estados distintos. Os recibos do build anterior permanecem históricos; a correção tem evidência própria.

## Correção da experiência atual

Fonte pública atual: [três abas, formulário, menu e Notas](../superpowers/plans/2026-10-20-planning-three-tabs.md). O metadata vivo confirma Referência oculta; o snapshot anterior com quatro abas continua histórico. Os cálculos em01-engine e o escritor em02-state permanecem intactos. A interface usa estados explicativos de previsão em vez de esconder a região em entradas incompletas. [Resultados desta correção](../validation/planning-three-tabs-20261020/README.md) têm atribuição própria;91/91 do pacote anterior não os substituem.


## Proporções e diálogos — contrato aprovado de21/10/2026

A apresentação usa somente estilos locais: todas as janelas centralizadas (tolerância2CSSpx), gutter24px ou12px em largura<=700px/altura<=600px. Formulário até1120px com previsão lateral apenas se viewport>=1100×720CSSpx; caso contrário até720px com sequência e Ver sua previsão. Perfis/Parada até800px; escolha/revisão/sucesso/confirmações até720px, sempre limitados à viewport.

Moeda/valor têm controles alinhados mesmo com rótulo quebrado; opcional permanece no rótulo sem linha artificial. Fechar44px com título completo, cabeçalho/ações acessíveis durante rolagem. Estados incompletos explicam a falta uma vez; resultado numérico recebe o destaque. A legenda da Parada representa as linhas reais, e o rodapé identifica a data calculada/selecionada. Nenhuma dessas atualizações altera perguntas, cálculos, dados, seleção, rascunhos ou confirmação.

Provas: regressões permanentes de proporções, matriz de temas/layouts/resize/zoom, crítica independente e FULL do pacote final, com limites e estado em ../validation/planning-proportions-20261021/README.md.
