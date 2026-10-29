# Adendo — matriz visual atual concluída

**PASS visual413/413 confirmado por leitura independente do recibo bruto. Isto não declara FULL116/116:** os demais checks continuam sob responsabilidade do executor; nenhum resultado final do FULL foi avaliado neste adendo. Nenhum teste, navegador, importação do produto, gerador ou escrita material no repositório foi executado para esta conferência.

## Recibo e identidade

- Fonte: [ui-visual-quality-results.json](/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/tools/.artifacts/app-efficiency-full-20261029T112325182239/ui-visual-quality/ui-visual-quality-results.json).
- SHA256 do recibo de20.916.323bytes: `218942eec221236b38efdb335c91d2a5c45c5b199cea908614782b6c952e8b60`.
- `classification=PASS`, `selection=all`, `source_unchanged=true`, Chromium `156.0.8078.48`.
- Intervalo interno registrado: `2026-10-29T14:25:15.979105+00:00` → `2026-10-29T14:40:10.294293+00:00`, 894.315188s. Duração do subprocess informada pelo responsável:894.997s; são medidas de fronteiras diferentes. Timeout original900s preservado; não houve mudança por este adendo.
- Identidade comparada com [INPUT-FREEZE.json](/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/docs/validation/economic-calendar-table-20261028/full-final/INPUT-FREEZE.json) e fontes atuais. Produto19 `8cfaec067a59ba393ff2aa53ad097196460e64e6de111945d92d3da21c47a518`, CSS `31e7659038d380c2348919a7ffa4229be125c5893d03540a89f728e3ad3aed5e`, build congelado `aabc8d09faff4aee`.

## Contagem sem deduplicação

| Conferência sobre listas brutas | Resultado |
| --- | --- |
| Registros realmente presentes em cases |413|
| Entradas realmente presentes em required_case_ids |413|
| Classificações nos413 registros |413PASS;0outros|
| IDs duplicados em cases |Nenhum|
| IDs duplicados em required_case_ids |Nenhum|
| Multiconjuntos executado/requerido |Iguais, inclusive multiplicidades|
| coverage registrado |executed413, required413, unique=true|

As contagens usam len das listas brutas e Counter para multiplicidades. Não foi feita deduplicação antes de contar, nem aproveitado só o primeiro registro de cada ID. Nenhum ID ausente ou inesperado foi encontrado.

## Calendário48/48 e tolerância2px

| Grupo atual | População executada e PASS |
| --- | --- |
| Matriz regular |32=4layouts(sidebar/topbar/glass/submenu)×2temas(light/dark)×4tamanhos(320×700,390×844,1440×900,1440×480)|
| Zoom nativo200% |8=4layouts×2temas|
| Contraprovas visuais próprias |8 IDs calendar-counterproof-*|
| Total Calendário |48 registros únicos, iguais aos48 IDs requeridos;48PASS|

Os oito IDs de contraprova são: inner-svg, economic-dot, overflow, personal-only-economic-dot, marker-appearance, today-selection, vertical-clipping e focus-return. São distintos das12CP scratch de valores/estado do inventário principal.

`tolerance_css_px=2` no recibo. Nos40 casos positivos de Calendário(32regulares+8zoom), foram lidos **1360 registros de centragem** salvos: máximo|Δx|=0.0078125pxCSS e máximo|Δy|=0.65625pxCSS. Os **240 registros do i econômico**(rótulo Detalhes de...) têm máximo|Δx|=0 e máximo|Δy|=0. Esses números são medições salvas, não novos IDs/casos. Foram excluídas dessa agregação as oito contraprovas deliberadamente incorretas.

Os oito casos `calendar-native200-*` registram, cada um, `native_zoom=200` e medição `outer1440/inner720/css1`. Isso preserva a distinção entre zoom do navegador e zoomCSS artificial. Todos os quatro layouts e ambos os temas aparecem uma vez, sem deduplicação. A matriz principal também declara native_zoom200 e reduced_motion=true.

## Hashes de fontes e testes

Os153 hashes presentes em source_sha256 coincidem com os arquivos atuais **e** com as153 entradas correspondentes do freeze;0arquivos ausentes,0divergências,0entradas fora do freeze. O hash do próprio runner, tanto test_sha256 quanto mapa de fontes, é `2dacc347c77eade52358e1342d223e619f3e40250a03e47f1e556cae67a7370a`, também igual ao atual/freeze. Quality_gate permanece `51fae2e0a9b25972d68c9d8e70023d28536fb4f590e386e8a518eecc568ab84d`.

| Cinco controlesV3 atuais | SHA256 atual=freeze | Presente no mapa específico deste recibo visual? |
| --- | --- | --- |
| `calendar_agenda_test.py` | `655556061f9fbbecd28f73de0861ac2e05741a658d7da0777b2591da28ab7ddd` | Sim |
| `calendar_distribution_test.py` | `cbaf54be1a5dd0ebecf80773158a86453f849fbf0ab8734a1ad32376065003a9` | Não; conferido atual↔freeze à parte |
| `calendar_economic_table_contract.py` | `35ea10d57ed2c8c4e6042ce14a88033cc232214f28790de9eacb9e9baf85c80a` | Não; conferido atual↔freeze à parte |
| `calendar_visual_quality_test.py` | `b883b966e1be638707da5c53999392cfc6ae02da36440500ddd18fc12970b95f` | Sim |
| `ff_news_cache_test.py` | `a3f3a00c5a1ff8e1059bc7eb1fd8c69870a5ecf48d1ea2020b8033503194862a` | Não; conferido atual↔freeze à parte |

O mapa visual específico não enumera o helper35ea, o teste de distribuição ou o testeFF; sua identidade atual foi conferida separadamente contra o freeze. Não afirmar que esses três foram guardados pelo campo source_unchanged deste check visual. O freeze e a comparação global final do FULL continuam a fronteira para a preservação de todos os inputs; seu resultado final ainda não é afirmado aqui.

O caso `coverage-missing-and-zero-rejected` está PASS e registra rejeição de seleção vazia/incompleta/NOT_RUN, além da validação da estrutura do gate: STANDARD71 e FULL116, com o comando visual completo exatamente uma vez. Isso comprova a **estrutura**, não a execução aprovada dos116checks. O gate continua nos checks seguintes ao visual.

## Limites da conclusão

1. Este adendo atualiza somente a linha visual do [inventário principal](/private/tmp/jpw-economic-calendar-table-20261028/tests-proposal/FINAL-TEST-INVENTORY.md):413/413 já é prova atual do check visual, não só população contratada. As afirmações anteriores de FULL ainda não concluído continuam.
2. O Calendário48 cobre as superfícies/estados declarados pelo módulo visual; não equivale a todos os módulos, toda combinação de conteúdo ou toda largura de workspace. Os cinco focais da tabela continuam sendo evidência complementar de workspace natural/amplo e limites700/720.
3. O próprio recibo mantém human_acceptance, Safari, screen_reader e physical_touch como NOT_RUN. A tinta do popup nativo de select não foi medida; foram medidos controles fechados/opções/alcance conforme o limite registrado. Não promover esse resultado a aceite humano ou homologação financeira.
4. Nada foi reexecutado para esta análise. O digest, os registros de tempo e os hashes referem-se ao recibo concluído específico; uma alteração material posterior exige nova avaliação da prova afetada.
