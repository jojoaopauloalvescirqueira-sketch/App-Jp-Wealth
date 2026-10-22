# Engenharia reversa da dinâmica — 20/10/2026

Pedido humano: substituir a adaptação do build ff0f078f pela dinâmica da planilha original. O livro original é somente referência: nenhuma conta, valor pessoal, registro ou credencial foi importado e nenhuma escrita foi enviada ao Google.

## Fontes identificadas

Planilha original: `1Wo1Qwvfd7okSClnCwKateirerP77Z0fWGHmg51wG2EA`, título conferido por metadata; última modificação informada pelo Drive:19/10/2026 às20:57:32.066Z. Leitura atual de20/10 confirmou Comece aqui, Consolidado, Preenchimento mensal e Referência, textos, perguntas, cabeçalhos, validações e fórmulas pertinentes. Os dez arquivos finais Apps Script e seus hashes estão no inventário adjacente. As266funções declaradas incluem infraestrutura Google e ferramentas de instalação, não266ações de usuário a portar individualmente. O apêndice Horizonte já integra o Formulario.verified; não foi contado duas vezes.

O HTML original utilizado no comparativo em navegador é idêntico ao literal JSON do fonte Formulario.verified.gs519, sem reescrita de seu JavaScript. A adaptação de callbacks fornece somente dados sintéticos e confirmações isoladas; essa prova não equivale ao runtime autenticado do Google.

| Fonte original | Contrato reproduzido / fronteira da comparação |
|---|---|
| Comece aqui, leitura atual | Texto original, três passos, conceitos, avisos e Preencher o formulário; primeiro acesso libera as demais abas somente depois de confirmar. |
| Formulario | Ano/mês separados; capital/aporte; perfil sem seleção prévia; comparação dos quatro perfis; custo atual opcional; pergunta de renda desejada; moedas e snapshots separados; identificação/opções; previsão; revisão, voltar, confirmar e sucesso. |
| Formulario, configuração e múltiplas contas | Seleções independentes de Consolidado/Mensal/Referência; ações globais referem-se ao Consolidado. Nome opcional, precisão livre nas premissas, cálculo de renda, revisão sem escrita. |
| Projecoes | Células azuis de meses futuros; vazio/zero distintos; preservação ao editar sem Reaplicar; referência inicial preservada; aporte previsto não vira fato. |
| Prazos | Objetivos individuais, primeira renda mensal suficiente, prazo desde início e restante desde hoje, comparação com referência. Todas com uma conta usa seus objetivos; várias contas não somam rendas pessoais. |
| ParadaAportes | Comparação de trajetórias, limite, busca da primeira data, pesos dos aportes; escolha invalidada quando mudam premissas; nenhuma escrita antes da confirmação final do formulário. |
| Saques | Múltiplos registros por mês, USD e BRL opcional, retirada no fim, revisão, correção e anulação com histórico. |
| Reinicio | Alcance CONTA/TODAS, conta, efeito, contagens, ciência, frase literal, prévia fresca, arquivamento integral, identidade e pedidos antigos inválidos. Configuração pendente total não cria premissas financeiras artificiais. |
| RegistrosProtegidos | Equivalência dos resultados confirmados/recusados/indeterminados e da idempotência pelo escritor local. Não há emulação artificial da fila, permissões owner/editor ou triggers Google. |
| ApresentacaoConsolidado | Indicadores no mesmo fechamento, ano projetado independente, preço médio/câmbio, prazos, tabela anual ou meses×anos, comparação planejado×realizado e detalhes progressivos. |
| GraficoReal | Quatro modos e somente histórico confirmado. O período do gráfico projetado não corta o histórico realizado. |
| Horizonte, apêndice de Formulario | União completa dos calendários, posições mantidas após120meses de cada conta, janela de11anos civis na tabela, sem gerar novos fatos. |
| Mensal, leitura atual D:U e subtotais | Dezoito colunas financeiras, cores/estados, edição futura, três questionários com revisão, finalização e totais a cada doze meses do plano. Esses totais não são confundidos com ano civil. |
| Referência, leitura atual B13:I13 | Metadados e oito cabeçalhos originais,120meses, taxa, aporte, acumulado, resultado, patrimônio, situação e perfil de origem. |
| Code / RelatórioA1:K36 | Composição dedicada, escopo do Consolidado, indicadores, projeção, gráfico e método; PDF pela impressão localA4paisagem. O download autenticado do Google é uma diferença de plataforma. |

## Limites e aceite

- O câmbio usa a fonte do site aprovada pelo proprietário, com origem/data; não há igualdade prometida entre cotações BCE e GoogleFinance.
- O aplicativo independente conserva seu protocolo local de persistência, conflitos e uso offline. Ausência de referência cambial não apaga valores USD nem inventa BRL.
- Conteúdo vivo do projeto Apps Script em20/10, `appsscript.json`, acionadores instalados, execução autenticada e permissões Google: **NOT_RUN**. A data de modificação é compatível com os fontes de19/10, mas não autentica equivalência integral do projeto vivo.
- A comparação do HTML/JavaScript original, cálculos puros, jornadas reais do site, distribuição e teste humano são provas distintas. Recibos do candidato anterior permanecem históricos; resultados novos são registrados separadamente.

Não declarar identidade universal de comportamento ou aceite humano a partir de uma suíte finita. Os resultados finais deste candidato ficam no relatório de paridade.
