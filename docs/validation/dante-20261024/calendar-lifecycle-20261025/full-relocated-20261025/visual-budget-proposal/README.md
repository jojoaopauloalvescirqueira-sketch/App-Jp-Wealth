# Proposta A1 — reduzir leituras repetidas no verificador visual

25/10/2026. Somente investigação e candidato em scratch. **Não aplicado ao projeto, não executado, não aprovado.** Nenhum navegador, teste de runtime, sinal de processo, mudança nos 679 inputs, gate ou limite foi iniciado por este agente. O FULL em curso pertence ao principal.

## Evidência e limites

A leitura do focal `visual-isolated/ui-visual-quality-results.json` confirma 413 casos PASS, de 05:05:13.888735 a 05:19:26.718523 UTC: 852,829788s internos; o recibo do comando informa 853,471s de processo. Não são a mesma medição. A rodada FULL atual excedeu 900s mesmo com diretório fisicamente scratch; isso não demonstra causalidade de CloudDocs. Não foi comprovado browser antigo acumulado, interferência humana, travamento, falta de CPU ou falha de produto.

A distribuição do focal encontra trabalho real concentrado em:

| Parte | Casos | Tempo das ações |
|---|---:|---:|
| Matriz original dos controles | 80 | 251,142s |
| Conjunto compact sem native | 100 | 240,096s |
| `compact-month-details-complete` incluído acima | 1 | 66,854s |
| Calendar sem native | 40 | 62,408s |
| Matriz original native200 | 8 | 32,076s |

Os intervalos entre fim e início de casos somam setup, controle, bootstrap, fechamento e limpeza. O maior é 22,558s antes de `closure-native200-sidebar-light`; outro é 14,021s antes de `compact-native200-sidebar-light`. Não há instrumentação suficiente para atribuí-los a `context.close`, `rmtree`, launch ou seed. O relatório não os chama de latência de filesystem.

As 88 jornadas original+native registram **2.000 inspeções de botões e 880 de campos**. Hoje, cada botão realiza oito chamadas remotas no caminho válido: scroll, duplo RAF, contagem SVG, identificação de Fechar, contagem do locator, geometria de texto/desenho, bounding box e corte pelos ancestrais. `CONTENT_GEOMETRY` já devolve a contagem de SVG e o retângulo externo, repetidos por outras chamadas. Essa redundância é demonstrável por código e pelas 2.000 evidências, independentemente do motivo da variância temporal entre FULL e focal.

`compact-month-details-complete` percorre 120 meses nos dois modos, abrindo cada um pelo controle real. Muitas formatações e consultas de campos atravessam o protocolo individualmente. Isso é oportunidade posterior, mas a primeira proposta não toca esse módulo nem reduz o percurso, as identidades, os valores ou os controles.

## Candidato mínimo, revisável

`batch-control-read.patch` altera somente `tools/ui_visual_quality_test.py`, funções `centered` e `controls_geometry`:

1. Preserva scroll de cada controle, sua ordem, **duplo RAF** e contagem exata do locator.
2. A mesma `CONTENT_GEOMETRY` é chamada no navegador; no mesmo snapshot lê `isClose` e os mesmos cortes pelos ancestrais.
3. Reutiliza `geometry.svg` e `geometry.outer` que já foram medidos, em lugar de duas consultas redundantes.
4. Todas as assertivas Python permanecem AST-idênticas. `centered` conserva seu caminho padrão para consumidores atuais; somente o chamador local envia a medição que acabou de obter do DOM real.

O caminho válido passa de oito para quatro chamadas por botão: **8.000 roundtrips a menos** nas 2.000 inspeções registradas. Isso é contagem estática, **não ganho temporal medido**. Não há promessa de que sozinho faça a suíte caber em 900s; medir é condição de aceite. Os valores são lidos no mesmo instante após a sincronização, em vez de em várias operações separadas.

A troca de `bounding_box()` por `geometry.outer` é restrita a dimensões width/height que ambas obtêm de `getBoundingClientRect` nos botões do documento principal. O patch não usa x/y de frames. Caso o helper passe a abranger iframe no futuro, essa equivalência precisa de contrato próprio; o escopo atual é Planejamento no documento principal.

O código mantém 413 IDs, 4 layouts, 2 temas, todas as larguras, zoom nativo200, toques, as ações, ausência de gravações e contraprovas. `required_ids`, `validate_coverage`, `matrix`, `native_zoom`, `main`, `counterproofs` e `gate_counterproof` são AST-idênticos. A entrada e o teto900s de `quality_gate.py` não mudam. Isso é conferência estática, não execução de tais casos.

## Autoridade e contrato antes de qualquer aplicação

Este é **N3/control plane** e está em A1. Não é sincronização corretiva já autorizada: modifica a forma como o próprio juiz obtém medições. O AGENTS exige CHG separado, autorização humana específica A4, comparação, contraprovas, revisão independente e aceite humano. A proposta não é concessão de autoridade e não deve ser aplicada antes desse gate. Produto, oráculos financeiros, 679 inputs anteriores e seus recibos ficam intactos enquanto aguarda.

O contrato deve delimitar a redução de RPC e suas equivalências: nenhum critério, limiar, universo de casos, timeout ou expectativa é enfraquecido; nenhum dado sintético substitui a leitura real. Não usar a otimização para anunciar a causa do timeout identificada.

## Contraprovas e aceitação planejadas (NOT_RUN)

Antes de FULL, em perfis sintéticos isolados:

- Executar o caminho original e o batched sobre o mesmo controle estável após o mesmo scroll/duploRAF. Comparar medidas text/ink/outer/labels/svg/isClose/cuts e a decisão de aceitação. Isolar a comparação de qualquer gravação financeira.
- Passar cada violação pelo **caminho `controls_geometry` batched**, não só pelo `centered` direto: texto +5px, SVG +5px, Fechar com20px, botão cortado pelo ancestral. O mesmo oráculo precisa recusar as quatro. Validar ainda controle íntegro e ausência de conteúdo. As contraprovas atuais diretas permanecem.
- Confirmar zero e múltiplos locators recusados no predicado `centered` e que alteração do conteúdo real antes da inspeção muda a medida; nenhuma medição anterior poderá ser reutilizada como cache entre controles/casos.
- Conferir ações e ordem, foco, rolagem, retorno de diálogo e zero writers. Verificar igualdade dos 413 IDs/critério/matriz/limites e ausência de skips/xfails, mantendo os testes negativos de cobertura.
- Instrumentar contagens e tempos em scratch sem mudar o runner: prova de redução de RPC (método atribuído a cada caso) e execução completa all sob900s, com resultado próprio e fontes congeladas. Não interpretar redução de chamadas como ganho percentual de tempo.
- Só após o focal completo e revisão independente, executar FULL com102 checks e900s por check. Não juntar recibos de rodadas diferentes para obter um FULL verde. Se continuar no teto, preservar a falha e voltar à investigação de fases; não ampliar limite nem reduzir casos.

O arquivo `static-receipt.json` comprova parse e as equivalências de AST descritas. `timing-and-counts.json` conserva os números retirados do recibo real. **Runtime e desempenho do patch: NOT_RUN.**
