# Validação scratch final — correção do launcher de contraprovas

Estado atual: cinco casos finais PASS5/5 e contraprovas corrigidas v2 PASS12/12. Browser, contexts e servidor foram fechados; execução headless está liberada.

A conclusão original12/12 foi **TEST_HARNESS_FAIL**, não aprovação de12 propriedades. O launcher v1 buscava o marcador em mensagem+traceback, podendo encontrá-lo no seu próprio callsite. CP05 falhou por overflow antes de atingir a asserção de alinhamento th/td. Recibo bruto preservado em `counterproofs-final/receipt.json`, launcher em `run_counterproofs-v1.py`, triagem em `counterproofs-v1-triage.json`, texto e resumo originais nos arquivos -v1. A reexecução posterior não apaga essa falha.

A correção modifica somente o launcher scratch. O v2 exige o marcador na mensagem da exceção e o último frame pertencente ao helper, com função/linha exatas vinculadas ao SHA congelado. CP08 tem mensagem vazia e exige exatamente table_case:171 e a linha `assert 'última coleta' in rows.nth(3).inner_text()`. CP05 passa a deslocar o último th−5px, sem causar overflow. Não houve mudança nos cinco candidatos, produto ou repositório por este agente.

## Evidências atuais

- `final-scratch-five.json`: nova execução PASS5/5 para natural1440(4layouts),compact390,wide2400/host1800,state e limites700/720.
- `counterproofs-final-v2/receipt.json`: PASS12/12, todas as violações REJECTED pela propriedade correta após precondição válida passar; zero TEST_HARNESS_FAIL nesta execução. Mensagem e identidade de frame registradas por caso.
- `counterproofs-final-v2/oracle-identities.json`: resumo verificável das12 identidades de oráculo. CP05: assert_layout:101, mensagem Real header and cell column bounds align…; CP08: table_case:171 e statement exato.
- `final-scratch-summary.json`: o v1 inválido e o v2 atual estão separados; os cinco candidatos mantêm os hashes congelados antes/depois.

Produto no overlay e fontes agora lidas na raiz real: JS `1e2e518bef9dccca48790f9752c48ba62619cd64c128ec87c55c6c58c779c831`, CSS `f1007dfe4122ac80aa2e8260b4db91079ad5291cec5f1b2dd6ab0aa3910beb38`. Helper `35ea10d57ed2c8c4e6042ce14a88033cc232214f28790de9eacb9e9baf85c80a`. Launcher v2 `9e1b4cff1b6c4c6e4eed37f6569165dba9066a555cbfc8331a29fb97faf55260`.

As12 contraprovas cobrem zero≠ausência; Atual não inventado; três valores compactos visíveis; ausência explicada; alinhamento real th/td; tinta numérica à direita; limite719px; aviso crítico visível; detalhe único; aria-controls no mesmo host; identidade não herdada após mudar horário; draft/cursor preservados. As mutações sequenciais usam uma fixture que chama setup original e injeta somente DOM/MutationObserver; table_case e expectativas permanecem congeladas. PASS das contraprovas significa sensibilidade do juiz, não presença dessas falhas no produto.

## Economic_focus anterior

`calendar-economic-focus-320-light` permanece PASS em `overlay-state-5.json`, com produto e todos os cinco candidatos exatamente iguais aos da nova execução final, comparação demonstrada no resumo. Conserva foco no mesmo link após recaptura com observação exata; após mudar horário, rejeita qualquer foco na linha econômica ou detalhe associado; financeiro permanece idêntico. A coleta abre o i antes de focar o link e, após a mudança fechar o detalhe, coleta foco via DOM em vez de esperar um link visível inexistente. O oráculo anterior foi preservado e fortalecido.

## Comandos usados

```sh
JPW_TEST_PY='/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/.superpowers/sdd/2026-10-21-planning-monthly-inline/runtime/bin/python3'
JPW_TABLE_SCRATCH='/private/tmp/jpw-economic-calendar-table-20261028/tests-proposal'
PYTHONDONTWRITEBYTECODE=1 JP_WEALTH_CHROMIUM='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' JPW_TABLE_PRODUCT_OVERLAY='/private/tmp/jpw-economic-calendar-table-20261028/product-proposal' "$JPW_TEST_PY" "$JPW_TABLE_SCRATCH/run_candidate.py" --case table-natural --case table-compact --case table-wide --case table-state --case table-boundaries --artifact "$JPW_TABLE_SCRATCH/final-scratch-five.json"
PYTHONDONTWRITEBYTECODE=1 JP_WEALTH_CHROMIUM='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' "$JPW_TEST_PY" "$JPW_TABLE_SCRATCH/run_counterproofs.py"
```

Não reexecutar os comandos acima sobre os recibos existentes. Para repetir preservando evidências, usar outro nome de `--artifact` nos cinco casos; para as contraprovas, copiar o launcher e `candidates/tools/` para uma nova subpasta scratch vazia (o driver calcula HERE a partir de sua localização):

```sh
mkdir -p "$JPW_TABLE_SCRATCH/replay-001/candidates"
cp "$JPW_TABLE_SCRATCH/run_counterproofs.py" "$JPW_TABLE_SCRATCH/replay-001/"
cp -R "$JPW_TABLE_SCRATCH/candidates/tools" "$JPW_TABLE_SCRATCH/replay-001/candidates/"
PYTHONDONTWRITEBYTECODE=1 JP_WEALTH_CHROMIUM='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' "$JPW_TEST_PY" "$JPW_TABLE_SCRATCH/replay-001/run_counterproofs.py"
```

A subpasta replay deve ser nova. O driver recusa produto/helper com hashes diferentes e recusa sobrescrever diretório de recibos. Este replay é instrução reproduzível, não uma execução adicional já feita.

A autorização de aplicar os cinco arquivos de testes no repositório continua separada. FULL, distribuição final,413 visuais, aceite humano, Safari, toque físico e leitor de tela permanecem NOT_RUN por este agente.
