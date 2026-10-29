# Inventário final dos testes — tabela econômica — V3 aplicada

Leitura/scratch em 2026-10-29T11:31:12-03:00. Nenhum teste, importação de módulo do produto, navegador, gerador ou escrita material no repositório foi executado para este inventário. O FULL foi iniciado pelo responsável às11:23:25 BRT de29/10; **nenhum resultado final do FULL foi avaliado ou declarado aqui**. Os números413/116 abaixo são população/estrutura preservadas, não PASS atual.

## Identidade e autoridade

Produto atual: JS19 `8cfaec067a59ba393ff2aa53ad097196460e64e6de111945d92d3da21c47a518`; CSS `31e7659038d380c2348919a7ffa4229be125c5893d03540a89f728e3ad3aed5e`; build `aabc8d09faff4aee`. Todos os cinco hashes lidos agora coincidem com [INPUT-FREEZE](/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/docs/validation/economic-calendar-table-20261028/full-final/INPUT-FREEZE.json).

O pacote37 foi autorizado para cinco arquivos; o delta posterior de **um** arquivo FFV3 foi expressamente autorizado na resposta `call_9750abf485524af2b6709be09677412e`, conforme [APPLIED-V3](/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/docs/validation/economic-calendar-table-20261028/APPLIED-V3.json) e [CHG N3](/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/docs/work/CHG-JPW-ECONOMIC-CALENDAR-TABLE-CONTROLS-20261028.md). Delta aplicado37→V3 `60a06bce255bd10370c43e9f6fa31855fa703f60da6d69050d66da45ff5004de`; pacote consolidadoV3 `7c9ca1442b18cbd5081ee2a56179a3697062637da3be119825a983d53cec9159`. Autorizar controles não autoriza Git/publicação nem equivale a aceite humano.

| Arquivo atual | SHA256 atual, coincidente com freeze |
| --- | --- |
| [calendar_agenda_test.py](/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/tools/calendar_agenda_test.py) | `655556061f9fbbecd28f73de0861ac2e05741a658d7da0777b2591da28ab7ddd` |
| [calendar_distribution_test.py](/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/tools/calendar_distribution_test.py) | `cbaf54be1a5dd0ebecf80773158a86453f849fbf0ab8734a1ad32376065003a9` |
| [calendar_economic_table_contract.py](/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/tools/calendar_economic_table_contract.py) | `35ea10d57ed2c8c4e6042ce14a88033cc232214f28790de9eacb9e9baf85c80a` |
| [calendar_visual_quality_test.py](/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/tools/calendar_visual_quality_test.py) | `b883b966e1be638707da5c53999392cfc6ae02da36440500ddd18fc12970b95f` |
| [ff_news_cache_test.py](/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/tools/ff_news_cache_test.py) | `a3f3a00c5a1ff8e1059bc7eb1fd8c69870a5ecf48d1ea2020b8033503194862a` |

## Propriedade → caso/ID → oráculo → evidência

| Superfície/propriedade | Casos/IDs | Oráculo observado | Evidência e limite |
| --- | --- | --- | --- |
| Calendário acumulado | **22 casos:17 anteriores+5 novos** | Navegação/teclado, marcadores/grupos, tipos de conteúdo, data civil, preferências opacas/extensões/duplicatas, recortes adjacentes, falha/recuperação, foco/info, lifecycle e inclusão explícita de moedas. | [calendar-after-compat:22/22PASS](/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/docs/validation/economic-calendar-table-20261028/calendar-after-compat.json). O primeiro21/22 vermelho permanece em [applied-calendar-agenda-37](/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/docs/validation/economic-calendar-table-20261028/applied-calendar-agenda-37.json); caption/grupo e horário civil foram corrigidos no produtoN1, sem mudar o teste. |
| Área natural, compacto e ampla | `calendar-table-natural-1440-light`, `calendar-table-compact-390-dark`, `calendar-table-wide-2400-light` | Quatro layouts naturais; sete campos; strings0/0.0%/−0.5%/1.2M/ausência, Atual—explicado; sem overflow; th/td reais≤2px; Range dos valores à direita; i44px na célula Evento. | Mesmo recibo22. Widehost1800 em viewport2400 é estímulo controlado; a superfície natural1440 também é exercitada, não substituída por ele. Não equivale a todos os tamanhos/idiomas/fontes. |
| Dois limites independentes | `calendar-table-boundaries-1440-light` | Viewport fixa; área útil do painel699/700 controla empilhamento/grade308px; depois área econômica719/720 controla duas faixas/sete colunas. Todos os valores rotulados visíveis no compacto. | [assert_layout/table_case](/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/tools/calendar_economic_table_contract.py:71). Não confundir largura da viewport com área disponível do componente. |
| Estado/disclosure exatos | `calendar-table-state-1440-light` + anterior `calendar-economic-focus-320-light` | Um detalhe por host, IDs únicos entre hosts, Enter/Espaço/click; fontes/horário original/referência oficial e avisos críticos; recaptura exata preserva expansão/foco; instante diferente e duplicata ambígua não herdam; rolagem nãozero é comparada exatamente; draft, cursor, mês/dia e bytes de estado/cache preservados; Escape mantém contrato legado. | [table_case](/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/tools/calendar_economic_table_contract.py:167) e [economic_focus](/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/tools/calendar_agenda_test.py:314); positivos no recibo22. São contextos sintéticos, não dados do operador nem prova de concorrência universal. |
| Sensibilidade do juiz | `CP01`…`CP12`, standalone scratch | Violações deliberadas submetidas aos mesmos helpers; exigidos mensagem e último frame do helper exatos, vinculados ao SHA35ea. | [12/12 corrigidos no produto atual](/private/tmp/jpw-economic-calendar-table-20261028/tests-proposal/counterproofs-applied37-20261029/results/receipt.json); [identidades](/private/tmp/jpw-economic-calendar-table-20261028/tests-proposal/counterproofs-applied37-20261029/results/oracle-identities.json). Não entram como nova entrada do FULL, não substituem o gate nem provam todas as propriedades isoladamente. |
| Quatro distribuições | `http`, `pwa-offline`, `modular-file`, `portable-file` | API/runtime e bytes; datas/filtros/marcadores frente ao pacote embarcado; campos/valores/disclosures; escritor canônico com criação/edição/conclusão/exclusão e reload; finanças adjacentes preservadas; PWA com cache/moduleSHA e respostaSW real offline; portátil isolado de umHTML sem dependência local extra. | [distribution-after-compat:4/4PASS](/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/docs/validation/economic-calendar-table-20261028/distribution-after-compat.json), fonte19/CSS atuais, sourceUnchanged=true;3/4/3/3 reloads. Feed remoto deliberadamente503: prova fallback/distribuição; transporte FF vivo sintético é prova separada. |
| Produtor/cache→domínio→tabela V3 | `ff-news-cache`:**186 checks em18 cenários**, não186cenários |16 cenários=8 falhas/cache em1440/light e390/dark: quota-old/quota-empty/read-denied/invalid-json/invalid-envelope/http-invalid/http-error/fresh-and-inflight. Mais2shared-v2-pipeline:payloadv2 nove moedas, corte semanal legado, CAD/USD alto, Médio excluído, fonte por ID/href após abrir i, warning explicitamente visível, concorrência coalescida, draft/foco/cursor e último cache válido preservados. | [applied-ff-v3-final:186PASS/0FAIL](/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/docs/validation/economic-calendar-table-20261028/applied-ff-v3-final.json), testSHAa3f3 e produto8cfa/31e. IDsshared-**v2** referem ao schema do payload; o arquivo de teste é a revisão**V3**. Não é chamada à rede externa real. |
| Juiz visual e gate acumulados | `ui-visual-quality` default:**413 IDs**; submatriz Calendário48IDs; FULL:**116 entradas** | Calendário conserva32 combinações(4layouts×2temas×4tamanhos),8native200 e8contraprovas. Novas asserções dentro de geometry medem layout da tabela e mesmo centered/ink2px do i; required_ids permaneceu idêntico. Main visual exige população exata/sem IDs faltantes e rejeita zero casos executados; o verificador do gate valida identidade, ordem e comandos. | [required_ids visual](/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/tools/ui_visual_quality_test.py:617), [calendar required_ids](/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/tools/calendar_visual_quality_test.py:33), [gate preservado](/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/tools/quality_gate.py). **413/413 e116/116 atuais ainda não afirmados**; dependem do FULL em curso e recibo final do responsável. |

Os cinco IDs novos, exatamente como aparecem no recibo22:

- `calendar-table-natural-1440-light`
- `calendar-table-compact-390-dark`
- `calendar-table-wide-2400-light`
- `calendar-table-state-1440-light`
- `calendar-table-boundaries-1440-light`

Os17 anteriores são6casosui(1440/390/320×light/dark) e11casos: edges, lifecycle, pref-read, pref-extension, pref-duplicates, adjacent-selection, adjacent-range, feed-recovery, info-focus, economic-focus einclude-new. Nenhum desses IDs foi removido ou substituído por um focal estreito no gate.

## Doze contraprovas: o que cada rejeição demonstra

A rodada atual12 ocorreu sobre o aplicado37, cujo arquivo FF era f66f. A posterior V3 alterou somente esse teste FF, que não é executado/importado pelo launcher das CP; helper35ea e produto8cfa/31e continuam exatamente iguais. Os186checks V3 são a prova separada do arquivo FF atual.

Todas abaixo: PASS no sentido de **violação REJECTED**; precondição válida passou antes da mutação. Mensagens/frames/mutações constam no recibo e no resumo de identidades, sobre produto8cfa/31e e helper35ea. O launcher só recebeu novos caminhos/hashes de input/output;12estímulos, larguras, marcadores e oráculos permaneceram iguais por AST e SHA.

| ID | Violação | Primeira asserção que a rejeitou | Limite específico |
| --- | --- | --- | --- |
| `CP01` | Projeção0 não vira ausência | `assert_values:58` | Só o valor da fixture alterado; não prova semântica de resultado realizado. |
| `CP02` | Atual não inventado como0 | `assert_values:58` | Ausência visual nesta alimentação; não é coleta de Actual. |
| `CP03` | Anterior removido por display:none | `assert_layout:93` | Rejeita campo oculto nesse compacto; não valida leitor de tela. |
| `CP04` | Atual sem explicação acessível | `assert_values:66` | Rejeita retirada de rótulo/nota testada; não comprova compreensão humana. |
| `CP05` | Último th deslocado−5px | `assert_layout:101` | Bordas reais th/td≤2px; não rejeição antecipada por overflow. |
| `CP06` | Valor numérico alinhado à esquerda | `assert_layout:97` | Range.right versus borda interna da célula≤2px. |
| `CP07` | Sete cabeçalhos em719px econômicos | `assert_layout:91` | Não é contraprova independente do limite700 do painel. |
| `CP08` | Aviso última coleta escondido | `table_case:171` | Statement exato, mensagem vazia; não muta isoladamente Cancelado/divergência. |
| `CP09` | Detalhe anterior continua visível | `table_case:179` | Rejeita antes do count==1 da linha180; não prova toda máquina de estados. |
| `CP10` | aria-controls aponta outro host | `details:33` | Não muta isoladamente toda forma de ID duplicado. |
| `CP11` | Forçar expansão/foco após mudar instante | `table_case:193` | Primeira rejeição é expansão; foco isolado não é demonstrado por esta CP. |
| `CP12` | Corromper valor e cursor do draft | `table_case:215` | Rejeição por valor do draft; cursor/foco isolados não são demonstrados por esta CP. |

**CP11 não demonstra isoladamente a restauração/fallback de foco**: a mutação força expansão e foco juntos, e a execução interrompe na expansão falsa esperada, antes da asserção de foco. **CP12 não demonstra isoladamente cursor ou foco**: a mutação altera valor e seleção, e a rejeição é pelo valor do draft, antes da seleção. Os positivos de table-state/economic_focus verificam os resultados corretos de foco/cursor, mas não há aqui contraprovas independentes para cada falha de foco/cursor. Não transformar12rejeições em cobertura universal de12famílias de comportamento.

Histórico preservado: o primeiro launcher declarou12PASS, mas CP05 foi rejeitada por overflow antes do alinhamento e seu matcher achou o marcador no próprio callsite. Essa rodada é **TEST_HARNESS_FAIL**, conforme [triagemv1](/private/tmp/jpw-economic-calendar-table-20261028/tests-proposal/counterproofs-v1-triage.json); não aprova12propriedades. O v2 corrigido passa a comparar str(error)+frame final exato, eCP05 usa−5px. CP08 vazia exige source statement exato. A rodada atual12/12 não apaga a falha anterior.

## Escopo N3 antes/depois e preservação

| Arquivo/controle | Antes → depois autorizado | Preservação/alcance |
| --- | --- | --- |
| `calendar_economic_table_contract.py` | Ausente → helper novo compartilhado, com valores/layout/disclosures/state. | Nenhum runner ou gate concorrente; importa Playwright existente, não instala dependência. Oráculo deriva do desenho humano, não de snapshotCSS. |
| `calendar_agenda_test.py` |17→22 por5casos aditivos; economic_focus ganha abertura do detalhe e coleta DOM após mudar instante. | Mesma expectativa de observação exata/financeiro; a nova coleta rejeita qualquer foco dentro de linha/detalhe alterado, sem aguardar link visível que deixa de existir. Nenhuma função/caso antigo retirado. |
| `calendar_distribution_test.py` | read_pack_and_filters ganha campos/valores/layout/collapsed no dia já selecionado. | Mesmos4ambientes, CRUD/recuperação/reload/IDs e fronteiras financeiras. Sem alterar fixture financeira ou gerador. |
| `calendar_visual_quality_test.py` | geometry ganha assert_layout e centered/ink do novo i. | Mesma required_ids/matriz, nenhuma remoção/renomeação; main413 e calendar48 permanecem. O juiz continua2px; a superfície wide de workspace é foco dos5casos novos, não se deve alegar que os48modais cobrem todo workspace. |
| `ff_news_cache_test.py` | Fixture pública sintética ganha strings0/0.0%/−0.5%/1.2M; pipeline ganha helpers. DeltaFFV3 de f66f→a3f3 adapta somente duas expectativas deliberadamente superadas. | Contagem global de links sempre abertos → proveniência por CAD/USD com i e href do payload; literal antigo → mesmo estado pendente nas duas linhas, **to_be_visible antes do texto**. Mantém todos os passos de cache/falha/retry/concorrência/draft/financeiro e186checks. V2texto semvisibilidade é histórico parcial, não conclusão final. |
| `quality_gate.py`, `ui_visual_quality_test.py` | Sem delta nesta tarefa. | FULL116, visual413,900s por comando e2px preservados; nenhum skip/xfail/filtro novo, expectativa financeira ou schema alterado. Os focais não substituem os comandos completos padrão do gate. |

Fontes de preservação: [preservation.json da proposta37](/private/tmp/jpw-economic-calendar-table-20261028/tests-proposal/preservation.json), [aplicação37](/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/docs/validation/economic-calendar-table-20261028/APPLIED-CONTROLS-37.json), [aplicaçãoFFV3](/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/docs/validation/economic-calendar-table-20261028/APPLIED-V3.json), [CHG de controles](/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/docs/work/CHG-JPW-ECONOMIC-CALENDAR-TABLE-CONTROLS-20261028.md). O reparo posterior do caption/grupo/horário foi **produtoN1**, não alteração de testes para fazê-los passar: [compatibilidade](/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/docs/validation/economic-calendar-table-20261028/COMPATIBILITY-DELTA.json).

Hashes atuais dos controles amplos, iguais aos registrados antes do delta desta tarefa:

- `tools/quality_gate.py`: `51fae2e0a9b25972d68c9d8e70023d28536fb4f590e386e8a518eecc568ab84d`.
- `tools/ui_visual_quality_test.py`: `2dacc347c77eade52358e1342d223e619f3e40250a03e47f1e556cae67a7370a`.

## Limites de conclusão para o relatório final

1. 22/22,12/12,4/4 e186/186 são provas focais delimitadas; não homologam finanças, conferem aceite visual humano ou aprovam FULL. Compatibilidade com Safari, leitor de tela, toque físico e dados reais do operador não é demonstrada por essas fixtures.
2. PacoteFF não fornece Atual: os testes exigem ausência explicada; não comprovam valor realizado, publicação, cancelamento ou cobertura integral de toda fonte/mês. Nenhum cálculo/sinal operacional é inferido.
3. Fontes externas foram substituídas por fixtures sintéticas e o fallback público embarcado nas distribuições; não se demonstrou endpoint remoto publicado/ativado, licença, cron externo ou condições reais de rede.
4. Para declarar FULL/visual atuais, o responsável ainda deve avaliar o recibo final, cobertura413/116, resultados reais de filhos, estados de ambiente e igualdade do freeze(incluindo arquivos adicionados/removidos). A execução começou conforme [full-process](/private/tmp/jpw-economic-calendar-table-20261028/full-process.json); **este inventário não consultou nem afirmou PASS final**.
