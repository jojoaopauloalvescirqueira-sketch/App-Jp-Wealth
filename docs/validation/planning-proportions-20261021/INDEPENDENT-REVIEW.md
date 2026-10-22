# Crítica independente — Task1 Planejamento

Data: 2026-10-21. Classificação: **PASS da revisão focal, sem defeitos concretos bloqueadores encontrados no delta examinado**. Não equivale ao FULL, à distribuição, ao aceite humano ou à homologação financeira. Não executei FULL, build, helper de alteração, Git nem alteração de fontes.

## Separação e avaliação A/B

Não participei da construção. Antes de ler o plano, o diff e os recibos, abri somente `gauntlet/sample-a.png` e `sample-b.png` e registrei a preferência **B** em `task1-independent-ab.md`. B oferece campos proporcionais e mantém os dois marcos agrupados ao lado das perguntas. A tem distinção por cor e duração em anos/meses mais imediata. Essas observações são julgamento de agente, sem teste humano.

As pistas de página inteira versus modal, contexto do aplicativo, azul versus vermelho/verde, foco ativo e um cartão adicional já permitiam inferir origem na etapa A/B; não houve cegamento completo. Depois do registro inicial, o acesso a UI/CSS e templates tornou inferível que B corresponde ao candidato. Não abri `mapping-root-only.json`.

## Evidências e conclusão técnica

- Li o plano aprovado, CHG, `task1-review.diff`, relatório, inventário, GREEN r4 e recibo de identidade dos oráculos. Comparei novamente os templates e o CSS com a cópia `candidate-09d53-before.tar.gz`: no formulário, o delta estrutural reúne o rótulo/opcional; na Parada, acrescenta o texto da data. O restante do delta JS muda somente apresentação dos marcos e visibilidade da saída pendente. Os dois trechos alterados do CSS ficam no bloco Planning. Motor `01-engine.js` e estado `02-state.js` são idênticos em bytes à cópia anterior.
- Recalculei a igualdade AST das seis funções dos cinco oráculos entre o teste RED pré-produto e o teste atual: todas iguais. O RED pré-produto e a contraprova final têm os cinco defeitos esperados; a contraprova final e o GREEN r4 usam o mesmo SHA do teste (`270e6aea…`). O recibo GREEN contém 94 casos PASS e fonte estável. Isso é auditoria dos recibos existentes, não uma segunda execução independente dos 94 casos.
- A centralização usa o viewport nos dois eixos; os oráculos medem erro máximo de 2 CSS px, larguras aprovadas e gutters. Revisei as fronteiras 1100×720 e os estilos de fechamento 44×44, corpo rolável, alinhamento moeda/valor, orientação pendente, legenda e rodapé da Parada.
- Executei interação própria em cinco contextos Chromium novos, com bootstrap e dados sintéticos: 320×700, 390×568, 1440×480, 1100×720 e 1440×900. Foram 300 passos Tab nos formulários e subdialogs; não encontrei controles focados cortados nem foco em controles de fundo. Escape devolveu o foco aos respectivos abridores de Perfis e Parada. Os cinco cancelamentos preservaram o snapshot financeiro. O rodapé acompanhou a seleção `jan. de 2028`, incluindo mês e ano.
- Executei um focal adicional com digitação por teclado em 390×568, sem `locator.fill` ou `select_option`: ano, mês por typeahead, capital 1000, aporte 100, Perfil Base por Enter, moedas USD por typeahead, objetivos 50/100. O resultado continuou mar/2027 e jan/2028. `Ver sua previsão` recebeu Enter, focou a previsão e, após a animação, deixou o título inteiro dentro do corpo rolável (título 126,44–154,33; corpo 104,08–458,06 CSS px). Escape fechou o modal e devolveu o foco ao botão `Preencher o formulário`; nenhuma escrita financeira. Os hashes UI/CSS/engine/state permaneceram iguais antes/depois.

As imagens móveis de Perfis, Parada e previsão foram inspecionadas. O conteúdo que não cabe na altura continua no corpo rolável; cabeçalho, fechar e ações permanecem visíveis. As frases longas dos marcos exigem leitura para distingui-los, mas isso não constitui falha no contrato aprovado.

## Lacunas e limites de prova

1. O oráculo permanente do rodapé da Parada verifica apenas uma parte do nome do mês, sem afirmar o ano exato. A implementação usa mês/ano e minha sondagem própria confirmou `jan. de 2028`; a fragilidade é de cobertura futura, sem defeito atual reproduzido.
2. A matriz permanente de proporções cobre geometria e retorno por Escape, mas não realiza esse percurso de digitação real completo. O focal independente complementa essa lacuna para um viewport; não certifica todos os teclados, tamanhos, navegadores ou tecnologias assistivas.
3. As medidas iniciais da previsão em `interaction.json` e nas capturas correspondentes foram tomadas no começo da rolagem suave; não provam o destino final. O recibo `keyboard-entry-r3.json` e sua imagem aguardam a animação e são a evidência conclusiva desse comportamento.
4. `keyboard-entry.json` falhou ao conduzir o select nativo com Home/ArrowDown no Chromium/mac; a sondagem por typeahead resolveu. `keyboard-entry-r2.json` falhou apenas na expectativa textual do abridor (`Preencher formulário` versus `Preencher o formulário`) depois de atingir valores/marcos corretos. São erros da sondagem, preservados; não são defeitos do produto. R3 terminou PASS com identidade do elemento e sem relaxar finanças ou visibilidade do título.
5. A/B não é comparação de conteúdo estritamente equivalente: A é página e B é modal, com patrimônio adicional e duração em meses. Preferência de agente não substitui aceite humano. Safari, leitor de tela, toque físico e Google autenticado não foram executados por mim. Build/distribuições/FULL pertencem à validação do root.

## Arquivos desta revisão

- `task1-independent-ab.md`: decisão visual anterior ao acesso às fontes.
- `independent-ui/interaction.json`: cinco contextos, 300 passos Tab, geometria, rodapé e cancelamento.
- `independent-ui/oracle-audit.json`: identidade dos oráculos, contagens RED/GREEN, inventário e engine/state.
- `independent-ui/delta-and-keyboard-audit.json`: delta decodificado dos templates/CSS e resumo das sondagens.
- `independent-ui/keyboard-entry-r3.json` e `keyboard-forecast-r3-390x568.png`: percurso conclusivo de digitação/foco/rolagem/Escape.

Nenhuma correção adicional é exigida por esta revisão focal. O root pode prosseguir com freeze e FULL do candidato final; os limites acima devem acompanhar o resultado.
