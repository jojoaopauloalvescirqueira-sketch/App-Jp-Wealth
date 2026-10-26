# Revisão independente — Calendário e Mercados

Escopo A0 somente leitura do delta de produto e verificadores contra a4bf278, branch codex/calendario-mercados-20261024. Nenhuma fonte, teste ou documento do projeto foi editado por este revisor; sem mutação Git, instalação ou dados reais. Artefatos sintéticos isolados neste diretório.

## Veredito focal

Nenhum achado material permanece aberto nos focos revisados após as correções. Este veredito não substitui FULL, distribuições, matriz visual integral, teste humano nem aceite do proprietário.

## Achados reproduzidos e corrigidos

1. P2: retry de catálogo pendente roubava foco de controle externo no sucesso (04-controller restoreFocus incondicional). Reprodução inicial: additional-review.json. Recheck CM-P2-01 PASS com guarda do iniciador/contexto.
2. P2: falha de snapshot na exploração mobile com mapa recolhido deixava tabela antiga sem status/retry visível (status dentro do resumo oculto; alternativa no mapa oculto). Reprodução inicial: additional-review.json. Recheck CM-P2-02 PASS; status/retry agora fora do resumo oculto.
3. P2: entrada fria por tools-market-hours ancorava antes do crescimento lazy do DOM, título permanecia a ~445px em desktop. Reprodução inicial: alias-scroll-review.json; 1RAF isolado foi rejeitado por raf-delayed-catalog-review.json. Recheck CM-P2-03 PASS; prova adicional final-anchor-recheck.json cobre catálogo atrasado, abandono do foco e substituição por tools-calendar.
4. P2: botão B3 do resumo tinha22.58×44px em320px, abaixo de44×44. RED: ui-current/report.json. GREEN: ui-fixed/report.json, CM-UI-01 PASS.
5. P2: mudança de outra linha do resumo reanexava nó sobrevivente focado e perdia foco para BODY. RED: summary-tick-focus-review.json. GREEN: p2-fixed/report.json, CM-P2-04 PASS, incluindo fallback quando a linha focada sai do resumo.

## Preservação dos verificadores e da navegação

Revisão do diff de navigation_ia_test.py e market_hours_integration_test.py: troca delimitada das expectativas superadas de item/child independente tools-market-hours pelo child canônico tools-calendar. Verificação adicional conserva requested/localView legados. Permanecem as guardas de recusa, cobertura por diálogo, lazy mobile, seleção, descarte, escrita financeira e distribuições; nenhum runner/gate foi alterado nesses diffs.

Prova real de navegação: navigateLocal(tools, market-hours) aceita e abre/ancora a exploração; guarda de execução recusando retornafalse e não cria full DOM. JPWTools.ui.selectView é adapter físico, normaliza para calendar e não publica navegação/expansão; não foi convertido em caminho que burle guardas. navigation-review.json conserva o observado antes da correção da âncora.

## Evidência e limites

PASS focal executado por este revisor: tools/calendar_markets_test.py --only CM-P2 (4casos), --only CM-UI-01 (1caso), ambos Chromium1223/Playwright e runtime existente, stableInputs true, zero failures/errors. Relatórios em p2-fixed/report.json e ui-fixed/report.json registram os hashes completos.

Inspeção: composição HTML/CSS, API/controller/view, compatibilidade de rota/local, ownership calendário/mercados, scheduler compartilhado e fronteiras de carga/visibilidade. Exploração adicional de atraso, foco, erro e transição em fixture produção sintética e host modular HTTP.

FULL e distribuições: não executados por este revisor. Teste manual/visual humano, Safari, leitor de tela e toque físico: NOT_RUN. Preflight observado durante edição retornou BLOCKED por hashes de manifest ainda divergentes; o responsável precisa verificar o candidate final após geração. O resultado não foi ocultado nem tratado como aprovação.

AGENTIC IMPACT CHECK: AGENTIC IMPACT DETECTED. BASIS: o delta altera os contratos de arquitetura CALENDAR-AGENDA/MARKET-HOURS e ACTIVE-TASK consumidos pelos agentes. A reconciliação desses documentos é responsabilidade do executor; este revisor não os alterou.
