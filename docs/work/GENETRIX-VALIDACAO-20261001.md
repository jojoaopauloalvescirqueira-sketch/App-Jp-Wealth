# GENETRIX 1.17.0 — validação, revisões e limites

O candidato implementa a proteção adicional em 7x, contabilidade de ciclos e consulta do flutuante compensado em cópia isolada. **CANDIDATE; prontidão operacional indisponível.** Compilação nativa, EX5, inspeção visual MT5 e sessões demo permanecem `NOT_RUN`. Esta classificação técnica não modifica os estados normativos do modelo.

## O que foi implementado

- Supervisor separado, com observação inicial, armamento explícito exclusivamente demo hedging, teto bruto/equity estrito e LIFO integral. A prevenção examina as pendentes conjuntamente. Uma intenção impede segunda solicitação enquanto o desfecho for incerto.
- Accountant e ledger próprio por conta/servidor/moeda/símbolo/direção, sem filtro por Magic. Deals, correções e exclusões testemunhadas permitem reconstrução e revisões; replay não duplica resultados.
- Sétima métrica no indicador, seleção explícita de ciclo, componentes e lista paginada de identificadores observados, incluindo membros fechados. Floating P/L e controles antigos preservam seu escopo. Preferência V3 conserva visibilidade anterior, inclusive todas as métricas ocultas.
- Memória de cálculo, fixtures anteriores à execução, manuais de observação/demo/rollback e pareceres cruzados. O ciclo inferido não certifica a Operação formal V11.

## Evidência local e denominadores

A revisão final RC2 obteve, em três processos novos para cada suíte, **12 de 12 tentativas locais PASS**, sem drift durante cada tentativa. Recibos: rc2-risk/ledger/oracle/ui-session-01…03. A revisão RC1 também obteve 12 de 12 e foi preservada; não substitui os recibos RC2. Processos locais não são sessões MT5, nem uma medição de confiabilidade futura.

| Verificação RC2 | Evidência por processo | Limite |
|---|---:|---|
| Risco | 51 de 51 asserts | 26 do Core/script, 12 de codec/store/lock sintético, 13 do ramo de cancelamento real extraído com histórico sintético |
| Ledger | 19 de 19 variantes financeiras; 135 asserts; seis de recuperação | Core/Store/ReadLive/Bridge reais traduzidos, SQLite e APIs de terminal sintéticas |
| Oráculos independentes | 7 de 7 cenários do planejador | Entradas do JSON congelado contra código MQL efetivo; 19 referências Decimal do ledger conferidas separadamente |
| Interface | 10.396 de 10.396 checks | Helpers, preferências, amostras, eventos e renderer com adaptadores; não renderização MT5 |
| Regressão e distribuição | 17 de 17 verificações PASS | Suíte do observador, pacote e página ilustrativa; sem execução nativa |

O pacote contém **100 de 100 membros declarados**, ligados por SHA-256 no manifesto. Fonte ZIP final: `4a58c496ac76a7fbf5637fe64f4ebcc21bb53f71c432ccc635b98c169a7edaf1`.

Os fixtures mantêm literalmente seus estados `DESIGNED/NOT_RUN`. Os recibos registram quais parcelas foram executadas no host; não reclassificam o caso integral da corretora. Não há média que compense falha crítica. A compilação C++ dos corpos extraídos não é compilação MQL e não produz EX5.

## Revisão por autores diferentes

| Autor do módulo | Revisor | Achados e alcance |
|---|---|---|
| Risco/execução | Autor da interface; autor do ledger | Estado visível antigo corrigido; corrida FILLED sem vínculo corrigida e ramo focal reexecutado. Orquestração completa e persistência nativa do testemunho continuam NOT_RUN |
| Ledger/persistência | Autor da interface | Tick fracionário e mudança de conta/inventário corrigidos; leitura real com APIs sintéticas. Lista vazia indevidamente aceita no codec foi corrigida e o contraexemplo reconferido. Cobertura continua DECLARADA pelo operador |
| Interface | Autor do risco | Revisão de leitura, tooltip 1–7 e preservação de preferências; não aprovação nativa da tela |
| Dossiê/manual/CHG | Revisor documental | Saldo da geração, detalhes parciais e natureza derivada corrigidos. Não homologa normas ou aprova módulos de sua autoria |

Os pareceres preservam achados iniciais, hashes antes/depois, correções, uma inferência retirada e limites. Agentes distintos aumentam a cobertura, mas não constituem certificação profissional independente externa.

## Falhas e tentativas preservadas

- Primeira suíte ampla: 54 PASS, duas PRODUCT_FAIL e um NOT_RUN, em 57 verificações. Estrutura foi corrigida pela inclusão explícita das dependências; timeout documental teve tentativa posterior PASS. A tentativa original permanece no recibo.
- Segunda suíte ampla: 56 PASS e uma PRODUCT_FAIL, em 57 verificações. O ramo de documento normativo ausente falhou no teste de reprodutibilidade. `rebuild_monolith.py` conserva exatamente o hash capturado na base: lê o PDF antes da guarda que deveria emitir a mensagem esperada. O resultado bruto PRODUCT_FAIL foi preservado; a origem herdada foi documentada em `BUILD-BASELINE-FAILURE.json`. Isso não é prova de não determinismo do ZIP quando todos os inputs estão presentes.
- Primeira suíte MT5 local: 16 PASS, uma PRODUCT_FAIL e uma TEST_HARNESS_FAIL. A contagem antiga de 87 arquivos foi atualizada para os 100 membros aprovados. A reconstrução concorrente alterou derivados durante a suíte; ela não certificou um único candidato. Nova tentativa estável: 17 PASS.
- Leitura do kit salvo: primeira execução de UI impedida pela ausência do helper Python `leverage_source`; a dependência foi incluída e a tentativa permaneceu registrada. A conferência final usa os arquivos efetivamente salvos.

A terceira suíte ampla registrou 55 PASS e duas PRODUCT_FAIL em 57 verificações: repetiu a falha herdada de reprodutibilidade e teve timeout de navegação no laboratório. A repetição isolada de research_navigation_test passou, sem alterar código ou critérios; não converte a execução ampla original em PASS. Essa suíte examina o site herdado e foi executada antes do freeze final RC2; não certifica os novos membros no MT5.

O relatório amplo final e as tentativas subsequentes constam nos recibos. Gates não foram afrouxados nem falhas apagadas para obter PASS. Os ajustes de adaptadores da sétima métrica estão documentados em `GENETRIX-TESTE-ADAPTADORES-20261001.md`.

## O que ainda não foi demonstrado

1. MetaEditor/build exato e vínculo fontes → dependências → EX5. O executável foi localizado; Wine utilizável não foi localizado, comando no Windows via Parallels exigiu edição Pro/Business e a tela do convidado não foi legível para automação segura. Evidência: `NATIVE-ENVIRONMENT.json`.
2. Callbacks, eventos perdidos, fechamento parcial e cancelamento/execução concorrentes na corretora. Os guards do código não demonstram o comportamento efetivo do servidor.
3. Durabilidade dos stores, locks, lease e intenção sob falha real de terminal/energia/rede. SQLite entre processos no host cobre cenários específicos, não todas essas condições.
4. Painel MT5, DPI/temas, template, datas, atualização e seleção observadas nativamente.
5. Três sessões novas por cenário crítico em demo hedging dedicada. Nenhuma sessão foi executada; nenhum pedido foi enviado à conta operacional.
6. Integração ao checkout paralelo, publicação, revisão final por responsável único e perfil da corretora. Nenhum merge, push ou publicação foi realizado por esta frente.

O supervisor não oferece veto prévio universal a celular/outros terminais. Pode retirar hedge e aumentar exposição direcional; o protocolo demo exige inventário antes/depois. Locks locais não coordenam VPS/terminais diferentes. A cobertura contábil não é verificada automaticamente pelo input de confirmação; dados insuficientes permanecem parciais ou indisponíveis. Histórico acima dos limites de processamento exige revisão posterior.

## Como conferir e avançar

Conferir `CANDIDATE-FROZEN.json`, o ZIP e seus 100 membros, os fixtures congelados e os recibos. O kit `Reproducao` permite repetir os quatro testes locais sem MT5. Para o ambiente nativo, seguir o roteiro de demo e rollback, compilar os bytes exatos e preservar todas as tentativas. O armamento demo só pode ocorrer após revisão do candidato concreto e do ambiente dedicado. Conta real e publicação continuam fora desta entrega.

Resultados favoráveis não demonstram lucro, vantagem estatística, conformidade integral V11 ou comportamento futuro em qualquer corretora.
