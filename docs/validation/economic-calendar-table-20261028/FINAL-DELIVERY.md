# Calendário econômico — entrega técnica local

Build **aabc8d09faff4aee**, branch `codex/calendario-tabela-ff-20261028`, HEAD `3e24f60f8cfe87f79335f40e95a0927379a9f834`. Candidato anterior e suas 133 alterações pendentes preservados. Sem commit, merge, push, publicação, ativação externa ou dependências novas. Aceite visual humano separado.

[Prévia versionada](http://127.0.0.1:57622/index.html?v=aabc8d09faff4aee) · [Bytes HTTP conferidos](PREVIEW-DELIVERY.json) · [Identidade final](DELIVERY-IDENTITY.json)

## Resultado

Os cartões econômicos foram substituídos pela mesma tabela adaptável na página Calendário e Mercados e no painel do ícone: **Horário, Moeda, Impacto, Evento, Atual, Projeção e Anterior**. Impacto tem símbolo e identificação acessível; valores permanecem como texto recebido, com sinais, unidades e zero explícito. Atual é sempre `—`, explicado como **Não fornecido nesta alimentação**; não é inferido de Projeção, Anterior, horário ou estado Publicado.

A grade mensal ocupa 308 px. Abaixo de 700 px úteis, calendário e agenda ficam empilhados; com pelo menos 720 px úteis na área econômica aparecem sete colunas. Abaixo desse segundo limite, cada evento tem identificação e uma faixa de valores rotulados, sem rolagem horizontal. É um único DOM, com controles de 44 px, altura automática e números alinhados à direita.

O botão i expande fonte, horário original e referências na própria linha; avisos relevantes continuam visíveis. Estado de detalhe em memória, independente por superfície e por observação exata. Atualização, desaparecimento e ambiguidade não transferem detalhes para outro evento. Foco, rolagem, seleção e rascunhos foram exercitados. Filtros e marcadores compartilham a seleção existente. Agenda pessoal, Bolsas Globais, consumidores semanais, APIs, coletor, cache, preferências e backup mantêm seus contratos.

Produto concentrado em `src/js/40-app/19-calendar-agenda.js` e `src/styles/app.css`, com documentação e derivados oficiais. Os cinco controles e o delta FF V3 têm [contrato separado e autorizações](../../work/CHG-JPW-ECONOMIC-CALENDAR-TABLE-CONTROLS-20261028.md). Não houve mudança de fórmulas ou escritores financeiros.

## Provas atuais

| Prova | Resultado | Evidência |
| --- | --- | --- |
| FULL original | **116/116 PASS**, zero outras classificações; saída 0 | [Recibo integral](full-final/full.json), [saída e estabilidade](full-final/full-exit.json) |
| Matriz visual | **413/413 PASS**, sem casos ausentes/duplicados | [Revisão dos IDs e medições](review/inventory-visual-actual.md) |
| Calendário | **22/22 PASS** no FULL | [Recibo bruto compactado](full-final/calendar-raw.json.gz) |
| Feed/cache e integração | **186 checks PASS**, em 18 cenários no FULL | [Recibo bruto compactado](full-final/ff-raw.json.gz) |
| Distribuições | **4/4 PASS**: HTTP, PWA offline, arquivo local, portátil | [Recibo bruto compactado](full-final/distribution-raw.json.gz) |
| Contraprovas específicas da tabela | **12 violações rejeitadas** pelo oráculo correspondente | [Inventário com limites de CP11/CP12](FINAL-TEST-INVENTORY.md), [revisão](review/cp-applied37-review.md) |

Os números não são somados como se representassem a mesma população. Os 413 casos incluem os 48 de Calendário: 32 combinações regulares, oito de zoom nativo de 200% e oito contraprovas visuais. Quatro layouts, dois temas, movimento reduzido e tolerância de 2 px mantidos; limite de 900 segundos por comando preservado. A matriz visual terminou em 894,997 segundos, sem ampliar o limite.

FULL executado em **29/10/2026, 11h23m25–12h12m59, America/Sao_Paulo**, duração do supervisor 49m34s. **1.648 inputs materiais** congelados: nenhum modificado, adicionado ou removido durante a execução nem na conferência posterior. Evidências em `docs/validation/` são saídas e ficaram fora do freeze; ambiente e dependências ignoradas não foram integralmente congelados. [Freeze](full-final/INPUT-FREEZE.json), [conferência posterior](DELIVERY-IDENTITY.json).

O teste de motor Hedge reemitiu um recibo histórico. A nova emissão foi preservada; como a única diferença era timestampUTC, os bytes históricos originais foram restaurados exatamente. [Preservação](full-final/historical-preservation.json). Caffeinate e processos próprios encerrados; nenhum processo de outra sessão foi interrompido.

[Inventário completo](FINAL-TEST-INVENTORY.md) · [Recibos brutos, hashes e cópias gzip com ida e volta exata](full-final/RAW-RECEIPTS.json) · [Parecer final do FULL](review/FINAL-FULL-AUDIT.md)

## Capturas e observação de uso

[Capturas atuais com o pacote econômico público local](captures-current/inventory.json), em contexto descartável sem dados pessoais: [desktop 1440 claro](captures-current/execEcal-1440-light.png), [painel 390 escuro](captures-current/calendarDialog-390-dark.png), [celular 320 claro](captures-current/execEcal-320-light.png).

Comparação controlada: **três pares, seis capturas**, com os mesmos seis eventos sintéticos, domínio idêntico, mesmo relógio e shell. O antes usa apenas renderizador/CSS da baseline sobre o shell atual; não é uma release histórica completa. Os exemplos não foram gravados na base do aplicativo.

| Cenário | Antes | Depois |
| --- | --- | --- |
| 1440 claro, página | [Antes](comparison-final/1440-light-execEcal-before.png) | [Depois](comparison-final/1440-light-execEcal-after.png) |
| 390 escuro, painel | [Antes](comparison-final/390-dark-calendarDialog-before.png) | [Depois](comparison-final/390-dark-calendarDialog-after.png) |
| 320 claro, página | [Antes](comparison-final/320-light-execEcal-before.png) | [Depois](comparison-final/320-light-execEcal-after.png) |

[Inventário bruto da comparação](comparison-final/inventory.json). No celular, Notas pode encobrir conteúdo próximo ao rodapé em certas posições iniciais. Após rolagem, os seis avisos amostrados e os seis centros dos botões i ficaram acessíveis, sem interseção com Notas. O agregado bruto de cinco pontos dos botões permanece **false**: os 24 cantos atingiram o elemento pai, compatível com o formato arredondado. Não se declara toda a caixa de 44×44 clicável nem ausência absoluta de sobreposição. [Revisão independente da observação](review/FINAL-EXPLORATORY-REVIEW.md).

Toque **emulado** observado em quatro contextos: 390/320 × página/painel. Foram registrados touchstart, touchend e click confiáveis: abrir, recolher e reabrir detalhes, fonte visível e comportamento de Escape preservado em cada superfície. Bytes financeiros sintéticos antes/depois iguais, sem erros de página. É coleta exploratória bruta, `NOT_JUDGED`, avaliada independentemente; não é um novo teste do Harness nem aumenta os 116/413. [Registros](touch-observation/raw-observations.json), [delimitação](review/touch-observation-authority-review.md).

## Preservação, histórico e limites

[Revisão de preservação](review/preservation-final-review.md): nenhum arquivo regular anterior removido; 1.625 materiais idênticos, 18 diferenças explicadas e cinco novos arquivos esperados. Sete payloads auxiliares diferem apenas no buildId; o portátil contém somente fontes autorizadas e metadados regenerados. Original preservado no tar verificado, SHA256 `5c50501d04c0207027e1f9a9d43bc6980b25dad88fd827433d9058af7c3d9d3d`.

As tentativas vermelhas, o erro inicial do launcher de contraprovas e o desvio de sequência do preflight permanecem nos recibos e fotografias anteriores do README. Não contam como aprovação; a correção de compatibilidade foi no produto, sem enfraquecer o teste. [Delta](COMPATIBILITY-DELTA.json), [manifesto e recuperação](MANIFEST-REFRESH-RECOVERY.json), [aplicação V3](APPLIED-V3.json), [revisão da aplicação](review/applied-v3-final-review.md).

O aceite humano deve verificar localizar uma notícia, comparar Projeção/Anterior e compreender por que Atual não é fornecido. Safari, leitor de tela, toque físico e aceite visual humano continuam não comprovados por esta entrega. Dados econômicos presentes no pacote não demonstram cobertura integral, publicação/ativação externa, atualização imediata ou resultado econômico divulgado. Nenhum dado pessoal foi enviado ao alimentador.
