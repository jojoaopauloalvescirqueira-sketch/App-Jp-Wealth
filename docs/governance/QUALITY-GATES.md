# Gates de qualidade e evidencia

## Taxonomia obrigatoria

- `PASS`: comando executado e criterio atendido.
- `PRODUCT_FAIL`: produto violou contrato valido.
- `TEST_HARNESS_FAIL`: teste, fixture ou expectativa esta incorreta.
- `ENVIRONMENT_ERROR`: ambiente impediu conclusao.
- `BASELINE_FAIL`: falha anterior ao diff, comprovada no baseline.
- `NOT_RUN`: verificacao omitida com justificativa.

## Tiers locais

### Fast

Para documentacao, governanca e iteracao curta:

- preflight auditavel;
- `validate_project.py`;
- `git diff --check`;
- `preflight_context_test.py` (frescor material do contexto: TRUE/FALSE/UNKNOWN, com UNKNOWN != FALSE).

### Standard

Para N0-V e N1:

- tudo do fast;
- `navigation_ia_test.py`: cinco rotas canônicas exatas, compatibilidade física,
  falha fechada atômica, zero escrita e isolamento do placeholder Alladin;
- smoke test;
- Central de Configuracoes;
- `galton_board_test.py`, incluindo matematica, fisica, persistencia, UI e lifecycle;
- `fx_planning_test.py`: motor do Planejamento FX (casos 1-20), reservas FCR/FEO,
  baseline x forecast x realizado, persistencia do agregado e fluxo real de UI;
- `usd_brl_quote_test.py`: cotacao USD/BRL, cache e integracao com o Planejamento FX;
- `exec_submenu_test.py`: faixa contextual do Execution Board, destinos, teclado e foco;
- `nocoda_test.py`: geometria do canal NoCoda, identidade de instrumento e persistencia;
- `pivot_studies_test.py`: derivacao e estatistica dos Estudos dos Pivots, criterio de
  correcao, ordenacao numerica, CRUD real e compatibilidade de estado;
- `order_guards_test.py`: nenhuma edicao de ordem ultrapassa o teto de risco da fase,
  com caso de controle para a guarda nao recusar tudo;
- `operation_identity_test.py`: identidade da Operacao Unica, proveniencia da
  abertura e normalizacao de estado legado;
- `operation_finalize_test.py`: finalizacao transacional (candidato, validacao,
  troca, rollback em falha e em excecao), trilha de auditoria na mesma gravacao,
  revisao igual ao snapshot persistido, integridade ternaria da Fase da Conta e
  invariante cronologica `openedAt <= closedAt`;
- `operation_history_test.py`: Historico somente leitura, denominadores
  explicitos, repintura parcial preservando foco e cursor da busca;
- `operation_wiring_test.py`: evento REAL de DOM atravessando dominio, estado e
  disco — categoria criada depois de um defeito de fiacao passar por testes
  unitarios verdes;
- browser real nos fluxos e viewports afetados.

`state_integrity_test.py` pertence ao tier `full`, e nao ao `standard` — a
listagem anterior o colocava aqui por engano.

### Full

Para N2, N3, integracao ou candidato de release:

- tudo do standard;
- todos os testes `*_test.py` listados pelo gate;
- rebuild portatil e verificacao de drift;
- auditoria de seguranca e persistencia;
- revisao integral do diff final.

Execute com:

```bash
python3 tools/quality_gate.py --tier fast
python3 tools/quality_gate.py --tier standard
python3 tools/quality_gate.py --tier full
```

O gate grava relatorio local em `tools/.artifacts/`, que e ignorado pelo Git. O relatorio deve conter SHA, dirty state, comando, duracao, retorno e cauda da saida.

## Composicao atual

| Tier | Quantidade | Verificacoes adicionais |
|---|---:|---|
| `fast` | 4 | preflight, estrutura, diff-check e frescor material |
| `standard` | 31 | fundacao semantica NAV-01, smoke, Configuracoes, Galton Board, Planejamento FX, submenu do Execution Board, NoCoda, Pivots, guardas de ordem, Operacao Unica (identidade, finalizacao, historico e fiacao) cotacao USD/BRL, fases visiveis, tres colunas do Exec, Financas Pessoais (fundacao, preservacao na finalizacao, round-trip de backup e navegacao; Orcamento Mensal, Dividas & Credito, Comparativo Mensal e Visao Geral) e Alladin (unidade em Chromium isolado — moeda, ids, write gate transacional, owners/isSelf, regimes de classificacao, cripto com network, symbolHistory, falha parcial, integridade referencial; integracao de persistencia — migracao v1->v2, round-trip com as quatro colecoes povoadas, fail-closed, rollback no build pre-Alladin e no build C1, reload real, XSS/privacidade e round-trip de backup) |
| `full` | 42 | finalizacao, storage, falhas/recuperacao de persistencia, senha, XSS, integridade de estado, corrida assincrona, build, service worker e Notas |

O baseline `d9510dbb55f0` tinha 46 scripts e `standard` 6/6. O candidato
`codex/galton-board` tem 53 scripts e acrescenta a suite focal ao tier standard. Essa
composicao nao e, por si so, evidencia de PASS do candidato.

## Evidencia especifica do Galton Board

Suite focal obrigatoria:

```bash
python3 tools/galton_board_test.py
```

Ela cobre PRNG e seed, limites/configuracao, geometria `rows + 1`, estatisticas,
binomial/elegibilidade, colisao Planck, acumulador de `1/120 s`, assentamento unico,
descarte de corpos, isolamento de persistencia, reload vazio, comandos, ativacao real
por `Enter`/`Space` em controles nativos, consolidacao de campo avancado por `Tab`,
tabela de bins focalizavel, alternativa ao Canvas e lifecycle. Essa cobertura nao
equivale a uma varredura completa de navegacao do modal somente por teclado.

Benchmark longo, deliberadamente fora dos tiers cumulativos para nao transformar
tempo de maquina em gate implicito:

```bash
python3 tools/galton_board_benchmark.py
```

O criterio e funcional: 10.000 bolas aceitas e contabilizadas, fila drenada, nenhum
corpo dinamico remanescente, nenhum vencimento/rejeicao, teto de 240 corpos ativos e
11 compartimentos no default. Tempo e taxa sao diagnosticos informativos.

Verificacao manual/real obrigatoria para o candidato final:

- `Configurações > Laboratório de Probabilidade > Galton Board` em desktop;
- viewport `390 x 844`, incluindo contenção completa do modal;
- temas claro e escuro;
- `prefers-reduced-motion: reduce`;
- pausa ao navegar/fechar/ocultar e instancia unica ao reabrir;
- fluxo PWA online, upgrade e abertura offline com todos os scripts do manifest.

`tools/validate_project.py` verifica ainda o hash fixo de Planck.js, a presença de
licença/proveniência, proíbe `Math.random` nos módulos do laboratório e exige todo
script do manifest no precache.

`tools/service_worker_upgrade_test.py` exercita a descoberta do worker pelo runtime:
o harness publica uma raiz nova e abre uma navegação ainda controlada pelo worker
anterior, mas não chama `registration.update()` por fora do produto. Polling em
Python confirma o worker novo em `waiting/installed`; as duas abas já abertas e o
cliente de descoberta permanecem integralmente no build/controller antigo, sem
`pageerror`, erro de console ou requisição falha. Depois do fechamento de todos os
clientes, a próxima abertura recebe o build novo coerente online e offline. O teste
também confirma que caches externos não são removidos.

## Validade da evidencia

- Mudanca em runtime, teste, manifest, fixture ou configuracao invalida os gates afetados.
- Teste focado nao substitui o tier exigido.
- Resultado antigo pode ser citado como baseline, nunca como PASS atual.
- Teste que deixa de falhar apos afrouxar uma expectativa precisa de justificativa independente.
- CI verde nao substitui fluxo manual quando o criterio exige percepcao visual ou dados do navegador.
- Benchmark verde nao substitui suite focal, tier `full` nem verificacao visual.
