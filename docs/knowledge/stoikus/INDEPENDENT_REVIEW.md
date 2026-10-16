# Revisão independente — mapas Stoikus para IAs

**SOURCE_APPROVED**, sem achados pendentes no escopo de fontes, proveniência, navegação e entrega local dos mapas. Esta aprovação não é compilação ou execução MT5, aceite financeiro/operacional, medição de qualidade de respostas ou autorização de publicação.

Revisor `/root/stoikus_independent_review`, sem autoria do produto, fragmentos, geradores ou mapas. Contraprova de fluxos e receitas por `/root/stoikus_independent_review/graph_flow_reference_check`, também sem autoria. O browser teve crítico independente separado. A revisão só leu dados/fontes e gravou os próprios pareceres; não editou produto, recibos, geradores, grafos, instruções ou Git, nem executou suítes do produto.

## Candidato conferido

Freeze final `REVIEW-FREEZE-R2.json`, **51 artefatos**, SHA-256 `aeb487a3e29f25621873e9d85fe8d23fd7fe802df8ce26bfa18e2929940ce667`. Todos os hashes foram confrontados com o disco sem divergência.

| Mapa | Nós | Pares direcionados | Registros de proveniência |
| --- | ---: | ---: | ---: |
| Arquitetura | 125 | 228 | 242 |
| Fluxos | 104 | 172 | 185 |
| Testes/evidências | 225 | 983 | 1.055 |
| Master | 301 | 1.144 | 1.230 |

O inventário inicial contém 191 arquivos: 104 MQL, 47 runners, 31 documentos/apoios e nove BMP. A detecção textual tem 182 arquivos; os BMP são somente inventário, sem interpretação visual. O manifesto final tem **246 registros**, adicionando oito recibos e 47 logs congelados. Todos os hashes de fontes originais e cópias foram conferidos. Os oito recibos são byte-idênticos aos originais; o conteúdo não foi reescrito para substituir paths históricos.

A biblioteca instalada Graphify 0.9.41 foi comparada diretamente ao wheel empacotado: **215 arquivos de pacote iguais**, zero modificações. Wheel SHA `5f5bfa1de21e9b76ade0168d3c1f9213115c30a985e44ed5b1f3000176f98777`. O builder próprio faz extração literal, consolidação e pós-processamento CSS; não altera o runtime do plugin.

## Proveniência e limites semânticos

- Conferi endpoints, unicidade de pares, existência das fontes, intervalos de linhas e literais em nós/registros dos quatro mapas: zero erro. Não há relação `calls`, `covers`, `coverage` ou `native_pass` fabricada.
- Os **1.230 registros originais** são exatamente o mesmo multiconjunto dos registros preservados dentro dos 1.144 pares do master. A consolidação de 86 registros adicionais não os apaga nem promove sua confiança. EXTRACTED: 1.222; INFERRED: oito. As quatro vistas declaram seus totais antes/depois, com `relation_records` e `RELATION_RECORDS.json` disponíveis.
- Includes têm direção consumidor → dependência; referência lexical ou hash não vira cobertura. Os dois Includes padrão MT5 são referências externas com arquivo/linha do consumidor, sem inventar versão ou bytes do header instalado.
- Os quatro programas diários são exatamente Monitor, Alavancagem Atual, NoCuda Channels e Abrir Painéis. Dependências/SDK e Supervisor opcional não são apresentados como um quinto programa obrigatório.
- O revisor de fluxos confrontou Begin/Step/EOF, reserva/owner/data_version, snapshot/tupla UI, cancelamento, conta capturada de exportação e separação heartbeat/captura com os contratos e fontes reais. O mapa é de arquivos e contratos; não oferece rastreio completo de chamadas ou telemetria de uma conta instalada.
- O relatório complementar `FILE_CONTEXT_REPORT.md` foi conferido contra o JSON: consumidores diretos e referências de teste dos quatro exemplos coincidem. O grau de um nó, frequentemente ampliado por hashes de recibos, não é anunciado como relevância funcional ou cobertura.

O grafo anterior de símbolos MQL permanece separado, parcial e preservado. Seus 17/104 arquivos com erros do adaptador C++ não recebem nova aprovação nativa por serem referenciados. Os relatórios nativos Graphify filtram inventário/stubs na apresentação; o relatório complementar esclarece as duas comunidades conceituais exibidas e as 28 comunidades totais do master em JSON/HTML.

## Receitas e navegação

As **oito receitas Q01–Q08** chegam às fontes esperadas na contraprova somente leitura, respeitando direção e profundidade. Isto verifica roteamento a fontes conhecidas, não qualidade de uma resposta de IA. Foram conferidos os papéis dos dois gráficos, impacto no Store, limpeza NoCuda, versões/cálculo, auditoria/snapshot, provas nativas pendentes, Monitor e runner/recibos.

O guia orienta conferir hashes antes de usar o mapa e ler a fonte na linha citada. Distingue os paths relativos no topo de graph.json dos paths absolutos de proveniência original em relation_records/EXTRACTION e no manifesto. Explica a resolução em outro checkout pelo path relativo do manifesto ou pela remoção do prefixo root exato. Nenhum intérprete ou comando armazenado deve ser executado por existir no grafo. Não foram instalados hooks, watchers, MCP nem instruções de agente.

## Achados encerrados e revisão visual

**FLOW-01 — referências por prefixo:** nomes Monitor_Core/Status/UI haviam recebido associações EXTRACTED com o programa Monitor.mq5. O helper passou a exigir filename/token adequado. A revalidação removeu as falsas associações mantendo as referências legítimas e os pares coalescidos. A montagem anterior está preservada em attempts/pre-review-FLOW-01.

**FLOW-02 — portabilidade:** o guia dizia que todos os paths eram relativos, embora os registros internos preservassem raízes absolutas da fotografia. O texto foi esclarecido sem normalizar ou perder a proveniência congelada. Contraprova final de fluxos: SOURCE_APPROVED, 185 registros e 8/8 receitas; `FLOW_REVIEW.md/json`.

**B1 — caminho de fonte cortado:** o browser encontrou recorte do texto longo. R2 acrescenta apenas CSS de quebra de texto aos quatro HTMLs e o helper correspondente no builder. Removendo exatamente esse CSS/comentário, os quatro HTMLs reproduzem os hashes R1; JavaScript, dados e JSONs não mudaram. O único arquivo novo R2 é FILE_CONTEXT_REPORT.md. Não há outro delta em receitas, fontes, confiança ou relações.

O recibo independente `BROWSER-SMOKE-R2.json`, SHA `90a138d4c4fe57fa5d099e67269f937b6ecedb607bc74ad7609cfdc2fad5feed`, registra **24/24 verificações focais** em quatro contextos novos: seleção, fonte completa/tail visível, comunidade, ausência de overflow e erros. Os 64 checks funcionais R1 são preservados e estão explicitamente **NOT_RERUN em R2**; não os conto como 64 execuções novas. O revisor deste parecer leu e vinculou o recibo, sem repetir o browser.

## Preservação e integração local

Conferi os **136 arquivos do produto**, os **1.023 inputs anteriores do candidato** e os **18 artefatos do grafo anterior** contra o baseline: nenhum mudou. O fingerprint MQL permanece `a27bb5ccfe778cc83fc0cb37309d7bf9a1bcbfc3c50f69142c2788934b067d4e`; build `5a207fbd41e59c2d2544f94264105d45c69911518433d0d66176eb9c0c427a1b`; cálculo 1.9.0.

As **102 cópias declaradas** em LOCAL-INTEGRATION.json foram conferidas no destino `/private/tmp/jpw-stoikus-continuity-20261014/docs/knowledge/stoikus`, sem diferença. Foram acrescentados artefatos de conhecimento; não foram alterados dados, código, schemas, stores, locks, preferências, estudos, pacotes históricos ou instruções existentes.

Os erros de geração anteriores, a navegação inicial 6/8 e o recorte B1 não foram apagados. A errata identifica expectativas de anchors que pertenciam ao design e à integração atuais, sem mudar traversal ou código para produzir PASS. Os fragmentos finais estão congelados por hash, distintos das tentativas anteriores.

## Estados de evidência

Os **47 PASS host/distribuição** e **57 PASS web** são snapshots R2 históricos, preservados por bytes. A construção dos mapas não voltou a executar essas suítes. Hash de fonte e referência ao runner não equivalem a resultado observado ou cobertura; o recibo HIS conserva facetas e full_acceptance NOT_RUN, e CONT-14 continua vínculo à regressão original, não uma execução adicional.

Compilação/execução MT5, instalação, aceite humano e negociação real continuam **NOT_RUN**. O contador numérico data_version de uma conexão instalada não está registrado; fingerprint não o substitui. Consumo de tokens do host está **UNAVAILABLE**. CONTEXT_SIZE_ESTIMATE estima tamanho de contexto, sem medir economia real, tempo, qualidade, superioridade ou eficiência de uma IA. Os HTMLs dependem da CDN/internet; os JSONs e relatórios podem ser lidos localmente.

**Parecer final: SOURCE_APPROVED.** Nenhum achado pendente para os novos mapas e sua integração local. Commit, push, merge, publicação e liberação operacional não fazem parte desta aprovação.
