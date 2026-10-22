# Planejamento — Consolidado e tabela mensal compacta

Implementação local do plano aprovado, sobre o candidato a9713063cd241820 e as alterações pendentes preservadas. Build oficial atual: **2ddbac03d67141d0**. Sem commit, merge, push ou publicação.

## Alterações

- Consolidado dividido em posição confirmada, projeção e objetivos, e referências de câmbio.
- Ano calendário vigente em verde discreto, com “Em andamento”, independentemente do ano da projeção.
- Preenchimento mensal com sete colunas a partir de 900 px úteis; três colunas e detalhes expansíveis abaixo dessa largura. Valores em US$/R$ agrupados, 120 meses e dez subtotais preservados.
- Estados de calendário separados da confirmação financeira. Os controles existentes mudam de lugar sem duplicação; os dados complementares ficam nos detalhes.

## Evidências e estado da validação

A execução final concluiu **96/96 PASS**, com saída real zero, fontes congeladas e identidades conferidas. O verificador visual concluiu **206/206 PASS**. [Resultado completo](FULL-RESULT.json), [processo e horários](FULL-COMMAND.json) e [resumo da entrega](DELIVERY.json). Revisão independente e aceite visual humano têm registros separados.

- [Build oficial](OFFICIAL-BUILD.json) e [oito focais aprovados](FOCAL-GREEN.json), com [saída real e horários](FOCAL-GREEN-COMMAND.json).
- [RED nos bytes atuais dos testes](RED-REVIEWED-FINAL.json): oito casos com falha de produto ao servir a apresentação anterior preservada; [proveniência do override](RED-REVIEWED-FINAL-PROVENANCE.json) e [processo observado](RED-REVIEWED-FINAL-PROCESS.json). O relatório bruto identifica as fontes atuais em disco; a proveniência separa explicitamente os dois arquivos antigos efetivamente servidos. As tentativas RED originais também foram preservadas.
- [Verificador visual no FULL](FULL-VISUAL-QUALITY.json): **206 de 206 PASS**, conservando os **98 casos anteriores** e acrescentando **108 casos**. Inclui oito contraprovas por oráculos positivos: overflow, controles duplicados, ano errado, fechamento falso, valor futuro errado, custo/cobertura errado, subtotal errado e ano atual omitido.
- [Distribuições](DISTRIBUTION-COMPACT.json): web, PWA offline, arquivo modular e portátil com os dados mensais e subtotais; [contraprovas executadas](COUNTERPROOFS.json): oito de oito PASS.
- [Impacto e reconciliação agêntica delimitados](AGENTIC-IMPACT.md). Produto e alteração dos testes têm CHGs separados.

As 96 aprovações anteriores e seu incidente histórico Alladin não são resultado deste pacote. Incidentes anteriores não são encerrados automaticamente por repetição bem-sucedida.

## Limites

Engine, estado, fórmulas, dados reais, confirmações, três abas, formulário, Stoikus, minigames e Bolsas Globais preservados. Não houve instalação de dependências, persistência nova, migração, configuração do AI Memory ou escrita de memória global. Backup recuperável dos 1.787 arquivos e oito links está na área ignorada desta tarefa.

Testes automatizados e revisão de agentes não equivalem a compreensão ou aceite visual humano. Safari, leitor de tela real e toque físico permanecem sem prova específica nesta entrega. A cobertura visual do restante do legado não é declarada integral.

## Capturas comparáveis com dados sintéticos

| Superfície | Antes | Depois |
|---|---|---|
| Consolidado | [Antes](captures/before-consolidated-desktop.png) | [Depois](captures/after-consolidated-desktop.png) |
| Mensal no computador | [Antes](captures/before-monthly-desktop.png) | [Depois](captures/after-monthly-desktop.png) |
| Mensal no celular | [Antes](captures/before-monthly-mobile.png) | [Depois](captures/after-monthly-mobile.png) |

[Ano corrente destacado](captures/after-current-year.png). As capturas anteriores servem a apresentação preservada; as finais correspondem ao build oficial atual, sem alteração do navegador do proprietário.

## Comparação medida

[Medidas com as mesmas fixtures e oráculos](BEFORE-AFTER.json):

| Tela | Largura útil | Antes | Depois |
|---|---:|---|---|
| Computador de 1.440 px | 978 px | 18 colunas, tabela de 2.218 px | 7 colunas, tabela de 978 px |
| Celular de 390 px | 298 px | 18 colunas, tabela de 2.218 px | 3 colunas, tabela de 298 px |

Dados adicionais continuam acessíveis nos detalhes, sem duplicar os campos. Essas medidas demonstram adaptação geométrica; não são pesquisa de compreensão com usuários.

## Impressão

[PDF sintético do teste corrente](PDF-SYNTHETIC.pdf), [inspeção](PDF-INSPECTION.json), [página 1](captures/pdf-page-1.png) e [página 2](captures/pdf-page-2.png). Conteúdo legível, sem cortes ou sobreposições observados. Há uma **limitação de paginação**: a segunda página contém somente a continuação de duas linhas do rodapé. A composição e os estilos de impressão foram preservados na fonte; não se declara PDF perfeito nem se atribui causa experimental sem reprodução anterior. O refinamento dessa paginação permanece fora da substituição da tabela mensal.

## Reexecução integral após adaptação dos consumidores

A [primeira execução](attempt-1/FULL-RESULT.json) terminou com 94 PASS e duas falhas brutas preservadas. A revisão localizou dois consumidores antigos: uma leitura da nona coluna, agora nos detalhes, e um seletor singular que passou a encontrar os três grupos. Os adaptadores mantêm valores, limiares e demais jornadas. Os testes reais de interface e layouts passaram após a correção, assim como os oito focais compactos. O novo FULL96 foi executado integralmente e passou; os 94 resultados anteriores não foram combinados com os focais para anunciar aprovação.

## Entrega técnica

[Auditoria final independente](FINAL-INDEPENDENT-AUDIT.md): PASS no escopo implementado, sem achado bloqueante remanescente. [Inventário](INVENTORY.md), [revisões](REVIEWS.md), [identidade final](FULL-RESULT.json) e [prévia conferida](PREVIEW-HTTP.json) documentam preservação e limites. Prévia local: http://127.0.0.1:8000/index.html?v=2ddbac03d67141d0. Aceite visual humano/N3 pendente; nenhum commit, merge, push ou publicação.
