# GENETRIX 1.18.2 — candidato de fontes

Data: 05/10/2026. Classificação: `CANDIDATE`. Produto `1.18.2`, metadado MQL compartilhado `1.182`, cálculo financeiro `1.9.0`. Base: pacote 1.18.1 congelado R2; esta revisão não transfere o aceite nem os resultados de testes da anterior.

## Correção e alcance

Em `JPWRenderRaizDetails()`, os dois cabeçalhos agora usam `background`, já capturado no próprio escopo. Não foi acrescentada variável global nem alterada a geometria. Os leitores Raiz N, Profile, MDD e Genesis recebem `FileSize()` como `ulong`, rejeitam zero ou tamanho superior a 8192, 65536, 2048 e 2048 bytes, respectivamente, antes das conversões `int`/`uint`.

O catálogo conserva a correção da 1.18.1: redimensionamento com recusa em falha de alocação e atribuição de cada estrutura do mesmo tipo. Fórmulas, limites de arquivos, schemas, parâmetros financeiros e estados `PENDING`, `NOT_HOMOLOGATED` e `BLOCKED` permanecem preservados. Os outros reparos da 1.18.1 continuam documentados em `GENETRIX_REPAIR_1_18_1.md`.

A captura do usuário mostra três erros e quatro avisos compatíveis com os fontes anteriores. Ela não demonstra a identidade de todo o conjunto instalado. O recibo externo desta entrega distingue contraprovas, testes host, compilação nativa e execução operacional.

## Um conjunto coerente de arquivos

O ZIP completo é `JPW_Genetrix_Fontes_v1.18.2.zip`. Use o manifesto externo e seus hashes para conferir cada arquivo. Não sobreponha somente o indicador a includes de outra revisão: os cinco programas compartilham dependências. A versão exibida não comprova a identidade de um `.ex5` antigo.

Esta entrega não instala nem substitui arquivos do terminal. Para uma futura conferência nativa, prepare uma instalação MT5 separada, copie o conjunto completo de `MQL5/Include/JPWealth`, `MQL5/Images/JPWealth`, os dois indicadores e os três EAs para os destinos equivalentes dessa instalação. Preserve os demais arquivos do MT5 e suas bibliotecas oficiais. Registre a pasta usada, a versão/build do MetaEditor, as bibliotecas oficiais efetivamente consultadas e os hashes dos inputs. Evite compilar contra includes JPWealth de outra pasta.

## Compilação isolada

No MetaEditor da instalação separada, abra e compile individualmente:

1. `MQL5/Indicators/JPWealth/JPW_Alavancagem_Atual.mq5`.
2. `MQL5/Indicators/JPWealth/JPW_NoCuda_Channels.mq5`.
3. `MQL5/Experts/JPWealth/JPW_Alavancagem_Observer.mq5`.
4. `MQL5/Experts/JPWealth/JPW_Genetrix_Accountant.mq5`.
5. `MQL5/Experts/JPWealth/JPW_Genetrix_Supervisor.mq5`.

Conserve o log completo de cada tentativa e compare os hashes dos fontes antes/depois. Critério: ausência dos três erros e quatro avisos relatados; novos erros ou avisos exigem registro e triagem. Vincule cada `.ex5` ao log, build, dependências e fontes correspondentes. Compilar não anexa nem executa o programa. Não arme o supervisor, não habilite negociação e não anexe os EAs à conta operacional para provar compilação.

Sem evidência nativa dessa revisão, compilação e execução são `NOT_RUN`; nenhum `.ex5` é distribuível. Um teste C++ host verifica somente os contratos adaptados explicitamente no seu recibo, sem substituir o compilador MQL5 ou a inspeção visual do MT5.

## Gauntlet e limitações

Os critérios foram congelados antes das correções. O teste de escopo compila o corpo inteiro da função legada, sem uma global substituta: a base deve falhar pelo identificador fora de escopo e o candidato deve passar. Os demais casos verificam tema/geometria dos cabeçalhos, limites e leituras incompletas, conteúdo inválido e catálogo. Cada caso novo exige três processos novos e guarda todas as tentativas. Os testes comportamentais anteriores são reexecutados contra esta revisão. Juízes antigos e suas falhas ficam preservados, com triagem separada.

Resultados, contagens, hashes e parecer independente ficam no relatório externo da entrega. Nenhuma média compensa falha obrigatória. Um bloqueio de compilador não se transforma em aprovação operacional. Esta correção não homologa eficácia financeira, correspondência nativa do Fibonacci, clipboard, desempenho nem proteção em qualquer corretora.

## Rollback

Os pacotes 1.18.0 e 1.18.1, os fontes originais, a instalação operacional e os registros locais foram preservados. Abandonar este candidato exige somente deixar de utilizá-lo. Se uma instalação de teste vier a ser preparada, guarde cópia do conjunto anterior e de suas bases antes de substituições; retorne ao conjunto coerente anterior sem misturar includes ou reaproveitar `.ex5` de origem desconhecida. Não apague, recrie ou altere bancos para simular recuperação. Publicação e instalação operacional exigem decisão posterior sobre o candidato concreto.

## Referências técnicas

- [MetaQuotes — ArrayCopy](https://www.mql5.com/en/docs/array/arraycopy): restrição para estruturas com membros que exigem inicialização.
- [MetaQuotes — FileSize](https://www.mql5.com/en/docs/files/filesize): assinatura de retorno `ulong`.
- [MetaQuotes — compilação no MetaEditor](https://www.metatrader5.com/en/metaeditor/help/development/compile).
- [MetaQuotes — integração com outros IDEs](https://www.metatrader5.com/en/metaeditor/help/beginning/integration_ide).

Fontes técnicas consultadas em 05/10/2026. As instruções acima orientam uma futura compilação; não afirmam que ela ocorreu nesta entrega.
