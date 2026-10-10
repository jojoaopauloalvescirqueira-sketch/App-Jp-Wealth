# R8 — Manutenção de linkage do juiz host de risco

**Estado: rascunho documental externo, preparado para adoção delimitada pelo coordenador.** A correção pertence à infraestrutura de testes, classificada como **N3 de control plane**. Este documento não é nova autorização, assinatura, aceite humano, norma financeira ou retirada de bloqueio. Nenhum repositório, candidato original ou checkpoint já arquivado no vault foi editado por este autor.

## Pedido e autoridade existente

As instruções humanas já registradas incluem:

> “integre esse a última versão do site”

> “Agora quero que você consertes os bugs do genetrix, utilize tecnicas de gauntlet loop específicas para desenvolver EAS de nível HARVARD, faça o mesmo para aprimoramento de design.”

> “Execute commit, push e merge”

O primeiro pedido foi transmitido no packet atual de integração e também está citado no CHG correspondente; os demais constam da conversa. A correção delimitada do teste necessária à integração utiliza esse escopo de integração e reparos. A autorização Git é própria e será executada pelo coordenador após os gates aplicáveis. Esses pedidos não autorizam negociação, instalação operacional, mudança de regra financeira, alteração do resultado esperado para obter aprovação ou hospedagem externa.

## Problema observado e delta

A primeira execução Linux da CI falhou ao construir o executável host do ensaio de risco: a chamada ao primitivo `SHA256` não tinha a biblioteca de linkage requerida naquele caminho. A falha ocorreu antes de executar as assertions do risco. O log bruto da tentativa 1 registra **39 `PASS` e 1 `TEST_HARNESS_FAIL`**, com zero `PRODUCT_FAIL`; esse resultado permanece histórico e não será sobrescrito ou promovido.

O delta em `tools/jpw_genetrix_risk_test.py` é importar `sys`, montar o comando original de compilação e acrescentar **`-lcrypto` somente quando `sys.platform != 'darwin'`**, após o arquivo de entrada. O caminho Darwin mantém os flags originais. O shim já distingue CommonCrypto no macOS do primitivo SHA256 no outro caminho; os julgadores existentes de configuração e ledger usam a mesma forma de ligação condicional. Não se altera fixture C++, assertion, valor esperado, classificação ou fonte MQL.

| Identidade | SHA-256 |
|---|---|
| Juiz antes, registrado no contrato | `e9a445c66df1ceb0323cf7707d66119cb76179bc7e6ffa61d1698927883886dd` |
| Juiz depois, conferido no arquivo e freeze | `bd4e00a853f72dca015b6d8978287b9132fa842cc675bcb93f72e46625e3f5a7` |
| LINKAGE-CRITERIA-R8.json | `196ab62845d4f8b52e5833f233709c166674ef1550f36a1c98cddd761e62ed39` |
| freeze-R8.json | `4bf95596069abb4c0bb1f57d8987778f4475850aabef45bf64c905e66ac2041d` |
| Log CI tentativa 1 | `155b9a9ec36181c8cf668237b5ef11067bbdc4e5b75d8c3c5fcd6feb7bedb689` |

A base local do contrato é `90b39df7a9d6097970a82013cd4e0c9b6e5fee02`. Hash confirma identidade; não comprova competência normativa ou aprovação por si só.

## Critérios congelados antes das novas execuções

O [contrato R8](LINKAGE-CRITERIA-R8.json) exige preservação de `-std=c++17 -Wall -Wextra -Werror`, flags originais Darwin e `-lcrypto` no caminho não Darwin. Permanecem intactos as fixtures, assertions, resultados esperados, classificação e fontes MQL. A referência de comportamento financeiro não é reescrita.

O [congelamento R8](freeze-R8.json) registra os bytes usados ao iniciar os testes. Os deltas dos dois helpers de layout/runtime por fim de arquivo são anteriores, têm revisão e recibos próprios e não são confundidos com esta alteração de linkage. O pacote source-only, manifesto, página e fontes MQL ficam fora desta correção.

## Evidência e pendências no checkpoint

| Camada | Estado observado |
|---|---|
| Risco host local, três processos novos | **3/3 `PASS`**, **51 assertions aprovadas por processo**, compile exit 0 e execute exit 0; [recibos e logs](R8-risk-processes/) |
| Suíte host local R8 | **40/40 `PASS`**, zero falhas nas outras classes; [recibo](mt5-host-R8.json) |
| Suíte web completa R8 | **Pendente neste checkpoint**; não havia recibo `full-R8.json` ao escrever o rascunho |
| Revisão independente do delta de linkage | **Em preparação pelo revisor separado**; acrescentar o parecer e os controles após recebê-los |
| Nova execução Linux/CI | **Pendente**; o resultado Darwin não demonstra que o caminho Linux passou |
| Compilação nativa e execução MT5 da 1.21.2 | Compilação **`NOT_RUN`**; execução **`NOT_RUN/BLOCKED`**; prontidão **`BLOCKED_NATIVE_VALIDATION`** |
| Git/PR/merge desta correção | Coordenados separadamente; conferir recibos posteriores antes de declarar conclusão |

Os testes host executam corpos selecionados por adaptação local e APIs sintéticas. Não comprovam orquestração real do EA, transações de corretora, durabilidade diante de crash ou interface/alertas no MT5. `OrderSend`, arranjo dos EAs, fórmulas, cálculo 1.9.0 e schemas financeiros não foram alterados por este delta.

## Impacto, revisão e rollback

**Alcance agêntico:** comando de construção do juiz host e seus consumidores, incluindo suíte host e CI. **Fronteira:** infraestrutura do julgador; não modelo JP Wealth/Nocuda nem produto financeiro. O juiz não pode ampliar suas permissões ou escolher expectativas mais fracas para tornar o resultado verde. A revisão independente compara before/after e distingue o defeito de linkage de um defeito do produto.

A adoção exige conservar a primeira CI vermelha, as três tentativas locais, o freeze, o parecer independente, as suítes aplicáveis e a nova evidência Linux. Se o novo julgamento revelar outra falha, registrá-la e diagnosticar em nova rodada; não absorvê-la como aprovação herdada. O rollback proposto reverte somente o delta de import/comando de compilação, com operação Git especificamente autorizada, preservando os registros e reconhecendo que o caminho Linux anterior continua falhando.

O harness interno continua `CANDIDATE`; piloto histórico `FAIL`, `PRODUCT_FAIL`, `PENDING`, `NOT_HOMOLOGATED` e outros bloqueios não são alterados por manutenção do linkage. A correção não usa exceção de auditoria para dispensar gate bruto. Este rascunho e o posterior recibo não certificam homologação financeira ou eficácia.
