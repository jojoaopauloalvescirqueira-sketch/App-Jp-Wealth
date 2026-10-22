# Revisão independente de UX — Planejamento — 20/10/2026

## Candidate e fronteira

Revisão A0 do produto, com escrita somente neste recibo ignorado e em evidências sintéticas do mesmo diretório. Raiz CloudDocs/SOFTWARES & EAS/JP Wealth OS; branch `codex/planejamento-patrimonial-20261020`; HEAD `ea15afc9c6a9c30cc69c5b98a8b85c85211ffb34` mais delta autorizado. Preflight audit executado: PASS, com aviso de 85 alterações preexistentes, preservadas. Fontes/testes não foram editados pelo revisor, não houve Gitops, instalação de dependências nem abertura do perfil do proprietário.

O packet inicial indicava build `01c95fcc16b97c9b`. Antes de abrir o browser, foi observado build `b53198001ffdb7ef`; o autor confirmou que removeu somente comentário obsoleto de index.html e reconstruiu oficialmente. Esta revisão examina `b53198001ffdb7ef`: ID capturado no arquivo antes do percurso desktop e também no runtime do celular. UI/CSS e build-id têm hashes em `ux-independent/observations.json`; HEAD isoladamente não identifica a árvore examinada. Alteração posterior exige recheck proporcional. A leitura do DOM e as capturas abaixo são anteriores às correções textuais propostas pelo autor.

Contexto lido: AGENTS, README, CONTEXT-MAP, PROJECT-CONTEXT, trechos focais de CURRENT-STATE/ACTIVE-TASK, CHG-JPW-PLANNING-20261020 e PLANNING.md. Procedimentos locais usados: JP Engenharia, preflight, change-control em A0, browser-verification, critical-review e test-triage. Cálculos financeiros não foram reinterpretados. A referência externa foi tratada como evidência, sem copiar contas/balancetes reais.

## Percurso observado — PASS funcional focal

Ambiente: Python `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3`, Chromium Testing 1223 no caminho do packet; um browser, contextos descartáveis separados, service workers bloqueados e bootstrap econômico sintético `USDBRL=5`. Aplicação original servida em localhost; nenhuma substituição de UI/estado/writer. Tráfego externo do produto foi interceptado pela fixture existente; rede inesperada registrada: nenhuma. Todos os fatos financeiros usados são fictícios. Validade do câmbio e funcionamento da rede real não são conclusões desta revisão.

Executado em 1440×1000 e 390×844:

1. Entrada pelo botão real da navegação. No celular, abrir `Menu` → `Planejamento`. Em prova adicional, o atalho real `Abrir Planejamento` do Dashboard também abriu a área.
2. Estado vazio → `Criar primeira conta`. Nome fictício, início out/2026, capital USD 1.000, aporte previsto USD 100, perfil Base, meta 300 USD. `Revisar prévia` exibiu projeção final USD 147.080,94 em set/2036; havia zero contas antes de `Confirmar criação`.
3. Mensal abriu out/2026 como `Mês atual`; capital 1.000, resultado previsto 30, aporte previsto 100, saldo em projeção 1.130. Os rótulos distinguem previsto de registrado e indicam que falta fechar o mês.
4. `Registrar resultado` → 30 USD → `Salvar resultado`; `Registrar aporte` → 20 USD e 100 BRL → `Salvar aporte`. Aportes registrados substituíram o previsto, sem somar 100+20.
5. `Finalizar mês` mostrou resultado 30, aporte 20, saque zero e fechamento efetivo 1.050, com conferência explícita desmarcada. Confirmar conferência e fechamento gravou 1.050 USD. Recarregar manteve uma conta e saldo confirmado 1.050 nos dois tamanhos.
6. Consolidado mostrou saldo/aportes/resultado confirmados separados do saldo projetado. `Encontrar primeiro mês` com limite 5% encontrou jul/2033, projetando USD 137.469,00, redução 4,79%; `Aplicar parada` abriu confirmação com esses valores. Esta prova cancelou o diálogo, sem aplicar a parada.
7. Referência e Contas foram abertas. Escape devolveu o foco ao botão de criação; reabrir recuperou nome digitado no rascunho da prova móvel.

Nas duas jornadas: zero `pageerror`, zero mensagens de console de nível erro e larguras document/body iguais ao viewport em todos os checkpoints. Isso não certifica ausência de sobreposição local ou de todos os defeitos. No celular, tabela mensal teve rolagem interna horizontal, mantendo o documento dentro de 390px. O gráfico apresentou linhas/legenda visíveis nas capturas; não foi avaliado com leitor de tela.

Os botões de ação medidos têm altura 44px. Desktop mostrou Registrar resultado em y≈864; celular em y≈1183 e a busca de parada em y≈1838 antes da rolagem. São medidas de geometria deste conteúdo, não tempo de tarefa nem prova de compreensão de iniciantes.

## Três maiores lacunas de explicação no candidate examinado

### UX-01 — P2 — Resultado não explicita que é o total do mês e substitui o anterior

**CONFIRMADO, interação real:** nos dois tamanhos, o diálogo contém conta/mês e um campo `Resultado · USD`, com `Salvar resultado`. Não explica lucro/prejuízo/zero, exclusão dos aportes/saques, total mensal ou substituição em uma correção. Capturas `desktop-result-form.png` e `mobile-result-form.png`; DOM em observations.json. **Observação estática:** `flowForm()` em `src/js/30-accounting/06-planning/03-ui.js` linha145 confirma a ausência; o original `Formulario.verified.gs` linha1549 explica o resultado TOTAL, sinais, exclusão de fluxos e substituição. Sua linha1551 ainda explicita a base do percentual na conferência.

**INFERÊNCIA, confiança moderada:** um iniciante pode informar saldo da conta, incluir depósito ou registrar apenas uma operação pensando que soma. Não foi observado um humano cometer esse erro. A falta do texto é certa; a taxa de erro não foi medida. **Menor ajuste recomendado:** rótulo `Resultado total do mês · USD` e explicação curta de sinais, zero, sem fluxos e substituição. Preservar o registro factual em USD e a validação existente.

### UX-02 — P2 — As metas não dizem que representam renda mensal

**CONFIRMADO, interação real:** criação/prévia e Consolidado usam `Meta adequada` e `Meta ideal`; não identificam renda mensal nem explicam o critério que produz a data. Meta 300 USD gerou jan/2030. Capturas `desktop-create-preview.png`, `mobile-create-preview.png` e Consolidado; DOM em observations.json. **Observação estática:** `currencyField`/`goalHTML` do 03-ui.js; `goalReadModel` em 01-engine.js linhas290–292 encontra o primeiro `resultUsd >= goal.usd`. O contrato PLANNING.md explica que é o primeiro resultado mensal que alcança a renda, e não retirada sustentável. O original verificado, linha519, rotula `Renda mensal desejada` e apresenta `Renda mensal ideal em reais`.

**INFERÊNCIA, confiança moderada:** o usuário pode preencher patrimônio final desejado ou interpretar a data como independência financeira garantida. Não houve estudo humano nem teste de sustentabilidade. **Menor ajuste recomendado:** nomear renda mensal adequada/ideal no formulário, resumo e referência e explicar em uma frase o marco calculado e sua natureza de estimativa. Preservar o motor.

### UX-03 — P2 — Aplicar parada omite a consequência de adiá-la depois

**CONFIRMADO, interação real:** a confirmação informa remover aportes previstos após jul/2033, preservar lançamentos confirmados, saldo projetado, redução e limite. Não informa que mover a parada para depois não restaura as previsões zeradas. Capturas `desktop-stop-confirmation.png` e `mobile-stop-confirmation.png`, e texto do diálogo no JSON móvel. **Observação estática:** `actionDialog('apply-stop')` do 03-ui.js linha156; PLANNING.md fluxo7 documenta expressamente que adiar não restaura valores anteriores e que as projeções continuam editáveis. Este efeito posterior não foi executado nesta revisão; sua fonte é o contrato, não uma alegação de interação observada.

**INFERÊNCIA, confiança moderada:** um usuário pode tratar a parada como controle reversível de cenário e esperar restauração automática. **Menor ajuste recomendado:** declarar essa consequência na confirmação, indicando a edição em Mensal. Preservar a simulação temporária e a confirmação própria antes da aplicação.

## Lacuna móvel adicional — UX-04 — P2 — Prévia calculada fica quase toda abaixo da área visível

**CONFIRMADO por interação e geometria de viewport**, sem depender da posição de diálogo em captura full-page: em 390×844, depois de clicar `Revisar prévia`, o bloco de prévia ficou em y694,25..1065,20. O rodapé fixo começa em y726,06; somente cerca de32px do início da prévia fica visível e `Confirmar criação` já está habilitado em y765. Valores finais/metas exigem nova rolagem interna. O foco permanece em `Revisar prévia`. A prova separada rolou a prévia e confirmou que o conteúdo era alcançável; não há bloqueio de acesso.

Evidências: `ux-independent/probe.json`, `mobile-preview-viewport.png` e `mobile-preview-scrolled-viewport.png`. **INFERÊNCIA:** uma pessoa pode confirmar sem perceber que a prévia está abaixo. Não houve confirmação inadvertida por humano. Menor ajuste recomendado: após o cálculo, trazer título/conteúdo da prévia à área visível e manter a navegação por teclado coerente. Esse achado foi enviado ao autor antes de encerrar o recibo.

## Comparação com a planilha de referência

**Benchmark interativo completo nativo: NOT_RUN.** O contexto anônimo abriu a URL original, título e canvas de Google Planilhas; os menus padrão estavam presentes, `Fazer login` também, e o menu `Stoikus` estava ausente. A mera presença de Fazer login não demonstra acesso negado. Não havia sessão autenticada nem cópia nativa sintética gravável; criação/registro/fechamento/parada nativos não foram executados. Nenhuma conta/perfil real foi aberto pelo revisor. Uma captura nativa produzida pelo script exploratório foi descartada preventivamente; não se conserva captura nem valores financeiros da planilha neste pacote.

A comparação acima é **heurística documental** contra os scripts originais locais verificados, especialmente Formulario.verified.gs e ApresentacaoConsolidado.gs. Ela demonstra diferenças de instruções e apresentação, não superioridade medida de experiência. Não houve comparação cega, medida de tempo, taxa de erro, entrevista ou teste com iniciantes. O aplicativo teve percurso sintético funcional observado; não se declara vitória sobre Sheets.

## Comandos, classificação e limites

- `python3 tools/agent_preflight.py --mode audit`: PASS com aviso preservado de85 alterações.
- `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 /private/tmp/jpw-planning-ux-independent.py`: primeira chamada TEST_HARNESS_FAIL antes do browser (regex de ID inadequada); corrigido somente o script temporário. Chamada seguinte executou desktop e terminou TEST_HARNESS_FAIL ao tentar clicar navegação móvel ainda recolhida. Nenhuma dessas falhas foi atribuída ao produto. A continuação abriu Menu pela UI real e concluiu mobile e consulta anônima de referência; PASS no recorte descrito. Desktop finalizado foi preservado, sem repetir seus testes por formalidade.
- `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 /private/tmp/jpw-planning-ux-probe.py`: PASS de coleta complementar (entrada pelo Dashboard, preview móvel, Escape/rascunho, menus nativos anônimos).
- FULL, paridade numérica extensa, distribuição, Safari, leitor de tela, tema escuro e toque em aparelho físico: NOT_RUN por este revisor. Os recebidos pelo autor são provas separadas e não são substituídos por este recibo.

**Veredito desta fotografia:** percurso funcional focal PASS; clareza de ação/consequência com quatro lacunas P2 registradas. A revisão não homologa compreensão humana nem superioridade sobre Sheets. Autor informou intenção de corrigir as três lacunas textuais; qualquer recheck será adendo com novo build/hashes, preservando estes achados. Aceite manual do proprietário é externo.


## Adendo — recheck delimitado — build5e8a1978a7ef3cb2

O autor informou correções de texto e rolagem/foco; o revisor não editou produto ou testes. O novo ID foi conferido no runtime de ambos os tamanhos. Hashes de index.html, build-id.js, UI, CSS, engine e state foram capturados antes e depois do recheck, com igualdade integral do recorte. Chromium148.0.7778.96. Fonte: `ux-independent/recheck.json`.

Comando `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 /private/tmp/jpw-planning-ux-recheck.py`: PASS, em1440×1000 e390×844, para os quatro pontos abaixo. A primeira tentativa preservada em recheck-first.json foi TEST_HARNESS_FAIL: a asserção temporária exigia a palavra literal `mensal` e `zero`; a redação real usa `do mês`, semanticamente correta. A coleta foi adaptada para aceitar `do mês` e relatar separadamente a ausência de exemplo de zero, sem atribuir essa restrição artificial ao produto. Produto não mudou entre essas duas chamadas.

- **UX-01: núcleo da lacuna mitigado.** O diálogo agora diz `Resultado total do mês · USD`, orienta positivo/lucro e negativo/prejuízo, exclui aportes/saques e explica que a correção substitui o anterior, sem somar diferença. Texto visível nos dois tamanhos; capturas recheck-desktop-result-viewport.png e recheck-mobile-result-viewport.png. Resta sugestão P3: dar exemplo de zero para mês sem resultado, já que o texto ainda não o explica. Isso não demonstra falha no tratamento numérico de zero.
- **UX-02: ambiguidade principal mitigada.** Formulário e prévia passam a `Renda mensal adequada` e `Renda mensal ideal`. O alvo deixa de parecer patrimônio final. Resta sugestão P3: explicar junto ao marco que é o primeiro resultado mensal projetado a alcançar a renda, sem implicar retirada sustentável. A semântica está no contrato; compreensão humana não foi medida.
- **UX-03: lacuna textual resolvida no recorte.** A confirmação diz que adiar não restaura aportes já zerados e informa que permanecem editáveis em Mensal. Capturas recheck-desktop-stop-viewport.png e recheck-mobile-stop-viewport.png. Recheck abriu/cancelou a confirmação; não executou uma alteração de parada.
- **UX-04: resolvida no cenário móvel examinado.** Após Revisar prévia, o foco foi para a região `Prévia antes de gravar`. Em390×844, o bloco passou a y321,25..692,20, integralmente acima do rodapé que começa em726,06. Antes era y694,25..1065,20. Em1440×1000, o bloco ficou y611,05..846,42, acima do rodapé y884. Capturas de viewport mostram valores e metas antes de confirmar; largura documental permaneceu390/1440. Essa é prova de visibilidade e foco neste cenário, não de leitura/compreensão humana.

O recheck criou contas fictícias e abriu os diálogos pertinentes pela interface real; não repetiu a jornada financeira extensa porque seu objetivo era somente essas correções. Zero erros de página/console e zero rede inesperada. O recorte de hashes ficou estável. O gate completo e qualquer novo teste permanente são executados pelo autor/outros agentes, fora deste recibo.

**Veredito atualizado:** recheck focal PASS; as quatro lacunas P2 desta revisão receberam mitigação observável nos textos/visibilidade examinados. Permanecem as duas sugestões P3 explicitadas e as provas externas: benchmark interativo completo em Sheets NOT_RUN, uso de iniciante real NOT_RUN e aceite do proprietário externo. Não se declara superioridade medida sobre Sheets, compreensão garantida ou aprovação global do produto.
