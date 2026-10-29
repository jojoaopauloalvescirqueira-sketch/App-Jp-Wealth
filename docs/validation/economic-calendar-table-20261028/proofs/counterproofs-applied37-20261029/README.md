# Contraprovas do produto corrigido — aplicado37 — 29/10/2026

**Executado uma única vez após GO:12/12 PASS, todas as violações REJECTED pela propriedade esperada. Browser, contexts e servidor fechados e execução headless liberada.** Nenhuma escrita no repositório, mudança de juiz, aplicação FFV3 ou execução concorrente.

## Bytes vinculados

Cópias feitas diretamente da raiz real para este diretório, com hashes conferidos:

- `product-inputs/19-calendar-agenda.js`: `8cfaec067a59ba393ff2aa53ad097196460e64e6de111945d92d3da21c47a518`.
- `product-inputs/app.css`: `31e7659038d380c2348919a7ffa4229be125c5893d03540a89f728e3ad3aed5e`.
- `product-inputs/build-id.js`: build `aabc8d09faff4aee`, SHA256 `e09a14541af933658c25e929e5ff712ebcc79c8f55ea5605c4ac573894f36247`.
- `candidates/tools/`: os cinco arquivos atualmente aplicados da autorização37, copiados da raiz real; todos iguais aos candidatos originais do37. Helper `35ea10d57ed2c8c4e6042ce14a88033cc232214f28790de9eacb9e9baf85c80a`; FF permanece `f66f357830f04a2c9f6eeb92ac469d8e04c190b6aa1a42aad161f65ebde859a7`, sem aplicar V3.

O launcher usa apenas as novas cópias locais de JS/CSS; não lê a antiga proposta de produto1e2e. Os módulos de suporte/servidor existentes continuam sendo os da raiz real, com contextos sintéticos e roteamento que bloqueia rede externa.

## Mesmo juiz, mesmos12 estímulos

O launcher deriva do v2 corrigido que exige mensagem da exceção e frame final exato do helper, vinculados ao SHA35ea. CP08 continua exigindo seu statement exato porque sua mensagem é vazia. CP05 conserva o deslocamento−5px que chega à asserção real th/td sem provocar overflow antes.

`launcher-binding.diff` demonstra somente três mudanças: caminho de entrada PRODUCT, hashes EXPECTED de JS/CSS e caminho da saída. Reverter textualmente essas três mudanças produz os bytes do launcher anterior. Os12 calls record e o catálogo ORACLE_FRAMES são idênticos por AST. Nenhuma tolerância, fixture, mutação, expectativa ou helper foi editado.

Launcher novo: `2d445a571a1c07f5d00c98e71832115aa8d540a66d1318b82994c61fdbb53516`.
Launcher anterior corrigido: `9e1b4cff1b6c4c6e4eed37f6569165dba9066a555cbfc8331a29fb97faf55260`.
Diff de binding: `c687137a58031200df99a76ec3a5d844f19a253d2d0168c70946fcc8f85f087c`.

`input-binding.json` contém proveniência dos arquivos copiados e identidades do index/manifest da raiz real. Os resultados/triagens anteriores permanecem nos diretórios próprios, incluindo o v1 inválido classificado TEST_HARNESS_FAIL.

## Comando executado uma única vez

```sh
PYTHONDONTWRITEBYTECODE=1 JP_WEALTH_CHROMIUM='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' '/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/.superpowers/sdd/2026-10-21-planning-monthly-inline/runtime/bin/python3' /private/tmp/jpw-economic-calendar-table-20261028/tests-proposal/counterproofs-applied37-20261029/run_counterproofs.py
```

O diretório `results/` foi criado sem sobrescrita. Antes da execução, foi verificada igualdade dos fontes vivos da raiz e de todas as cópias novas com input-binding. O launcher comprovou hashes de produto/helper antes de abrir o navegador e igualdade dos cinco candidatos antes/depois. FULL, nativo, distribuição, geradores e testes além das12 contraprovas não foram executados. A execução foi serial após liberação explícita do responsável. Não repetir o comando sobre o mesmo diretório de resultados.

## Resultados vinculados ao produto atual

`results/receipt.json` é o recibo bruto, com12 casos PASS e identidade do launcher/produto/candidatos. `results/oracle-identities.json` fornece o resumo compacto de cada rejeição, mensagem e função/linha final do helper; todas coincidem com o esperado. `validation-summary.json` registra limites e liberação do navegador. Os12 hashes de mutação, marcadores esperados e larguras foram comparados e são iguais aos do recibo anterior corrigido; nenhum estímulo foi alterado. CP05 continua em assert_layout:101 pela borda real th/td, CP08 em table_case:171 pelo statement exato de última coleta.

`input-binding-pre-GO.json` preserva a fotografia de preparação e seu NOT_RUN era histórico; `input-binding.json` descreve agora a execução concluída. Os recibos antigos continuam intactos. PASS destas contraprovas demonstra sensibilidade do juiz às violações propostas, não aceite humano ou aprovação do FULL.
