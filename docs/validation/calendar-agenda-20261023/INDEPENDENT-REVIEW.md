# Revisão independente — Calendário e Agenda

Revisor distinto do construtor, acesso somente leitura; baseline recomposta a partir do manifesto e tar iniciais. Revisão de produto, fronteiras de dados e do próprio verificador separadas do aceite humano.

## Resultados observados antes do gate final

- Agenda22/22 e feed17/17 passaram na revisão inicial. Depois, correção de escape acrescentou dois testes:19/19 no foco da correção.
- Duas páginas reais: token antigo recusado por CONFLICT após gravação na outra página; disco preservado.
- Títulos/notas contendo tags e handlers renderizados literalmente, sem elementos executáveis; famílias financeiras preservadas.
- Gate96→102, seis entradas novas e nenhuma removida; visual322→369,47 novos e nenhuma remoção/duplicação.
- Planejamento, Notificações, escritor central e AGENTS mantiveram hashes da baseline. SW recebeu somente três URLs.
- Baseline do Dashboard recomposta em servidor em memória: cinco capítulos e cinco atalhos; expectativa Apple antiga de quatro já falhava. Sem alterar produto ou promover o focal a PASS.

## Achados tratados

1. **P2, pacote externo inline:** builder não escapava terminadorHTML. Demonstração independente de execução em Chromium apenas com dados sintéticos. Builder agora escapa `<` na representaçãoJS, preservando JSON e strings originais. Dois testes RED/GREEN permanentes.
2. **P2, classificação/atribuição:** impacto editorial não explicado na UI, apesar de existir nos metadados. Filtros agora identificam impacto editorial, [i] explica a classificação JP Wealth e fontes/licenças podem ser consultadas. RED/GREEN focal.
3. **Harness, ordem de ciclo:** chamada à matriz visual estava depois de browser.close. Corrigida antes de executar a matriz; prova estrutural e execução oficial.
4. **Oracle, formulário:** a contraprova de Salvar avaliava a grade intencionalmente oculta. Usa agora o oráculo do formulário, tanto na aceitação válida como na rejeição. Três violações de contraste/destaque continuam rejeitadas.
5. **Oracle visual inicial:** aparência dos marcadores, distinção hoje/seleção e cortes verticais não tinham asserção direta. Criticou-se o próprio teste, acrescentando medições e contraprovas sem reduzir o critério.

A re-revisão dos últimos deltas e o FULL final têm registros próprios. Esta revisão não substitui teste humano, Safari, leitor de tela, toque físico, publicação ou aceite financeiro.

## Re-revisão dos deltas finais

Revisor executou19/19 do feed e edgesUI320, confirmando o fechamento dos doisP2. Validou em ambos os temas a contraprova de Hoje/seleção/Salvar pelo estado correto. Para a nova apresentação de licenças, o teste de distribuição agora confere11fontes porIDs/nomes/hrefs e quatro atribuições/licenças separadas. Contraprovas independentes deIDincorreto, licençaerrada e atribuição ausente rejeitadas; quatro distribuições passaram no foco, com fontes estáveis.

A prova extraApple320 registrou254asserções:252PASS e duas falhas da expectativa histórica de quatro capítulos. Contraste do calendário PASS em claro5,315 e escuro6,161. Cabeçalho:34casosPASS, incluindoHTTP/portátil e320–1440px. Essas são provas focais, não o FULL.

## Seleção adjacente, recuperação e contagens

Três critérios adicionais tiveram RED no produto e GREEN13/13 do runner padrão. Revisor distinto executou3/3: diaadjacente preserva mês/foco; consultas incluem toda grade; cobertura corresponde à data selecionada; cache mantém somente contexto de intervalo/fuso/moedas/impactos compatível, com aviso de desatualização e recuperação posterior.

Última revisão de apresentação: edges320PASS e seis combinações de filtros independentes com2eventos+2tarefas+1lembrete. Totais5→3→1→0→2→0, grupos, bolinhas e nomes acessíveis coerentes; documento principal preservado byte a byte. UI96abcfb9494912a3592dff787ae07730fa44ac2f8f47320e66f5522d61a6a200; testeae0fcc5656cf4b1d87255b06d94ae1fe5b21b9d2fc94816a55b626d2cc91c59d; CSSa928c5590254978eed2cef71e7b347e912d26852addc1697253554ac7f3b87b9. Nenhum achado material restante nesse escopo; FULL permanece prova separada.

## Ocorrências do primeiro FULL completo

A matriz visual executou369casos:368PASS e uma falha bruta no autocheck que ainda exigia96checks. Ajuste do catálogo agora exige96IDs/comandosAST históricos preservados, seis novos exatos, ordem eCLIcompleta;17 contraprovas rejeitadas e revisão independente do próprio juiz. Nenhum critério visual foi removido.

Smoke tinha a contagem antiga de quatro ações no cabeçalho: alterada somente para cinco; GREEN focal. ScannerUSD/BRL apontou a palavra authorization na nova expressão que rejeita chaves de credencial. Exceção limitada à linha exata, única e apenas no portátil; as seis exceções antigas permaneceram. Revisor independente executou32inserções (oitomarcadores×quatroposições), guarda alterada, duplicata e outroarquivo: detectadas. Motor de cotação preservado e focoGREEN. As falhas brutas continuam nos logs; classificação conciliada desses três casos é TEST_HARNESS_FAIL de expectativas antigas, sem promover o FULL aPASS.

Dashboard identificou um defeito real novo: header com seis controles mínimos44px e gaps4 excedeu390px emCSSzoom125%, provocando3px de overflow. Correção proposta por contraprova: auto-fit de colunas mínimas44px, gap2 e padding-inline0. Matriz original30/30 passou com estilo injetado somente na fixture; não é aprovação de fonte integrada. A correção será aplicada após o FULL corrente preservar seu recibo e validada no candidato reconstruído.

## Cabeçalho integrado e compatibilidade dos consumidores

Após preservar o FULL3 bruto, o cabeçalho móvel recebeu reflow local: colunas auto-fit com mínimo44px, gap2px e sem padding lateral adicional. As30apresentações doDashboard e32doMiniGames passaram no candidato reconstruído5c6a4e7af7a747a3. Revisão distinta confirmou escopo local e preservação de alvos e ordemDOM.

NoCuda129/129 passou nas distribuições do seu runner. O único trecho substituído é o workspace agora mensal; o teste continua abrindo o overlay semanal e verificandoEUR, sem mutar preferências mensais. Downloads, payloads, XSS, transferências e provas de escrita permanecem.

O Guia mantém52casos e hash dos106caminhos históricos. A extensão de três scripts exige identidades únicas, dependências e cache/API após reload offline real. O crítico encontrou uma lacuna do juiz: omitir os três ao mesmo tempo ainda passava. Após RED, a intenção da feature é detectada independentemente no candidato e a13ªcontraprova rejeita a omissão coletiva. Compatibilidade comroot antigo sem fontes/launcher testada separadamente. SHA final do juiz4a94b16dba95538f67ab575557228a7fb97f60c939c4fae111e4b37d7fa70517. Revisor independente executou o positivo atual e as13contraprovas, confirmou a exigência por launcher mesmo sem módulos no filesystem e a aceitação da cadeia antiga somente emroot sem feature. Recibos startup/offline-13 comPASS e fontes inalteradas. Nenhum bloqueador material restante nesse recorte; FULL4 e aceite humano permanecem separados.

## Limite da alimentação econômica e errata descritiva

A conferência independente do plano confirmou que o pacote local parcial é compatível com a entrega em etapas e com a cobertura das séries declaradas. BLS, Fed, RBNZ, CHF e o calendário completo deStatsNZ permanecem pendências do roteiro. O gate técnico não demonstra conclusão integral de toda a alimentação econômica prevista. O relatório final deve manter essa distinção explícita.

Foi identificada uma frase descritiva divergente no contrato: “Cancelados não produzem bolinha”. O modelo e a interface preservam os eventos cancelados, identificados comoCancelado, sob os mesmos filtros de lista e marcadores; o plano humano exige preservá-los e não determina sua exclusão. A errata deve alinhar a descrição ao comportamento comprovado, sem modificar o runtime, calendário ou verificador. A fonte executável permanece congelada até o fim do FULL4.

## Deltas finais antes do FULL5

Revisor distinto confirmou o conflito de especificidade doGlass, o recolhimento limitado e o toggle fora do grupo ocultado. Depois confirmou o helper de foco, preservação de restore=false e guarda contra novo diálogo/foco escolhido pelo usuário. O novo oráculo deriva o alvo doDOM, sem chamar o helper do produto; doisrAFsincronizam o retorno assíncrono, sem relaxar timeout ou clique. Conferência de catálogo:47casos antigos mais1novo,48noCalendar e370totais, sem duplicação ou remoção. A execução oficial48/48PASS comfontes inalteradas ficou registrada emcalendar-focus-48-GREEN.json. FULL5 permanece prova independente da execução focal.

## Revisão do diagnóstico de Notas antes do FULL6

Revisor distinto conferiu a SHA `603586aa2cecc4f8596e1eb628c2ecfad8ba8effb3f3f0f8d8b582f7c061c911`. Remover apenas o helper e os três campos diagnósticos recupera a AST anterior: critérios, eventos, timeouts e caminhos positivos são idênticos. As chamadas ocorrem somente em `except`. Exercício em página sintética aberta capturou DOM, viewport, navegação, ancestrais, overlays, trace, erros, PNG e HTML válidos sem mutar a página. Página fechada preservou os quatro erros de captura e a causa original. [Recibo independente](notes-diagnostics-independent-open.json).

A revisão aprova somente a capacidade diagnóstica e a preservação do juiz. A causa do timeout no FULL5 permanece indeterminada; o resultado bruto continua sendo uma falha de harness e não é reclassificado pelo PASS focal. Nenhuma alteração preventiva de produto foi feita.

## Conferência independente dos recibos finais

O revisor recalculou os 102 checks: **101 PASS e 1 ENVIRONMENT_ERROR**, com o hash bruto igual ao RESULT e prontidão NOT_APPROVED. Freeze antes/depois idêntico em 2.358 caminhos; oito arquivos protegidos iguais à baseline. Três prefixos exatamente iguais aos diffs autorizados, com os históricos completos preservados por hash. Recuperou e conferiu o gzip visual: **370/370 PASS**; distribuição **4/4**, calendário **13/13** e recuperação **8/8** coerentes. A prévia 58998 e os cinco hashes HTTP correspondem ao build `85ae832b1f542745`. O diagnóstico posterior mantém causa indeterminada e não substitui o gate. Cobertura econômica parcial e aceite humano NOT_RUN explícitos.

**PASS limitado do relato documental**, sem aprovação técnica integral, sem reclassificação da falha de entrada e sem novo browser/teste ou alteração de fonte pelo revisor. Não foi encontrado bloqueador documental. [Estado final](delivery-state.json) · [Resultado e limites](RESULT.json).
