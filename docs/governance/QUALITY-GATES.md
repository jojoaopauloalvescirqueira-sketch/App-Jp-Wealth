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
- `navigation_ia_test.py`: cinco primários, seis filhos Forex em ordem exata,
  cinco filhos Research, defaults/aliases, compatibilidade sem falso owner, falha fechada atômica,
  zero escrita e isolamento do Alladin (a navegacao nao le nem altera o dominio patrimonial);
- `research_navigation_test.py`: cinco filhos Research na ordem exata,
  Research/Forex com três destinos, ownership único de Calendário/NoCoda/Pivots,
  Exec reduzido a quatro views, empty states neutros, Galton intacto, storage
  isolado e browser desktop/mobile claro/escuro;
- smoke test;
- Central de Configuracoes;
- `galton_board_test.py`, incluindo matematica, fisica, persistencia, UI e lifecycle;
- `fx_planning_test.py`: motor do Planejamento FX (casos 1-20), reservas FCR/FEO,
  baseline x forecast x realizado, persistencia do agregado e fluxo real de UI;
- `alladin_ledger_test.py`: Cash Ledger (ALD-03 S1) em Chromium isolado — deposito,
  saque e saldo DERIVADO; transferencia interna como UM registro que nao altera o
  patrimonio global; flowScope como perimetro; reversal preservando o original e
  somando zero; dedupe fail-closed; qualidade bloqueante em vez de saldo parcial;
  ordem economica; write gate e schema futuro fechados;
- `usd_brl_quote_test.py`: cotacao USD/BRL, cache e integracao com o Planejamento FX;
- `exec_submenu_test.py`: faixa Forex N2/N3, defaults, estado ativo, teclado,
  foco, desktop/mobile, temas, overflow e targets de toque;
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
| `standard` | 39 | navegacao NAV-01..NAV-03 (cinco primarios, seis filhos Forex, cinco filhos Research e N2/N3), smoke, Configuracoes, Galton Board, Planejamento FX, NoCoda, Pivots, guardas de ordem, Operacao Unica (identidade, finalizacao, historico e fiacao) cotacao USD/BRL, fases visiveis, tres colunas do Exec, Financas Pessoais (fundacao, preservacao na finalizacao, round-trip de backup e navegacao; Orcamento Mensal, Dividas & Credito, Comparativo Mensal e Visao Geral) e Alladin (unidade em Chromium isolado — moeda, ids, write gate transacional, owners/isSelf, regimes de classificacao, cripto com network, symbolHistory, falha parcial, integridade referencial; integracao de persistencia — migracao v1->v2, round-trip com as quatro colecoes povoadas, fail-closed, rollback no build pre-Alladin e no build C1, reload real, XSS/privacidade e round-trip de backup; preservacao no Finalizar Sessao — agregado sobrevive ao encerramento operacional inclusive em schema futuro, Zona de Perigo continua apagando, e falha de copia aborta o ato inteiro) e causalidade entre geracoes da base (replay pos-wipe rejeitado, mixed-build nos dois sentidos contra o build baseline servido por `git archive`, seqlock epoch-documento-epoch, bootstrap deterministico e deduplicacao por `tipo:token`) e serializacao cross-tab dos escritores do documento (Web Locks no critical section com transacao write-before-clear e revalidacao de revisao; modo degraded explicito sem Web Locks; guarda sincrona de concorrencia no save(); epoch com confirmacao estrita releitura===valor) e a superficie cadastral read-only do Alladin (C3-S1 — quatro destinos locais, cadastro C2 real, zero conteudo economico, zero escrita, snapshots desacoplados do read-model, READ_ONLY em schema futuro sem normalizar; ledger economico (ALD-03 S1/S2 — deposito, saque, transferencia interna que nao vira aporte; BUY/SELL como fato unico de duas pernas com fees/taxes embutidos e flowScope ausente em trades; reversal com o original preservado e consistente com ele tambem na leitura; saldo derivado fail-closed com guardas de inteiro seguro; schema futuro e mixed-build contra build v3 real; posicao por quantidade derivada — ALD-04 S1, alladin-position: identidade instrumentId+accountId, aritmetica decimal exata, zero fora da colecao, negativa fiel, adulteracao/orfandade/moeda/schema futuro BLOCKING, saida deterministica) e manutencao cadastral C3-S2 — as quatro entidades pelo modal real: Account e CashAccount (S2-A) e Instrument e Asset (S2-B), DC-4 pos-criacao com decisao explicita e copia distinta para criacao e edicao, taxonomia de avisos com informativos preservados fora da decisao, moeda imutavel e symbolHistory mantidos so pelo dominio, cripto com rede de fonte unica, identificadores externos, owners em basis points por aritmetica inteira, tags e data, patch-diff enviando so o campo alterado, status x4 via setRecordStatus com confirmacao, write gate na abertura e no submit, double submit e cancelamentos zero-write) |
| `full` | 50 | finalizacao, storage, falhas/recuperacao de persistencia, senha, XSS, integridade de estado, corrida assincrona, build, service worker e Notas |

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

## Caso que depende de historico nao pode terminar em PASS

Algumas suites servem builds antigos por `git archive` de um SHA pinado, para
provar que uma versao anterior do aplicativo nao corrompe dados gravados pela
atual: `alladin_foundation_test` (casos F e F2) e `session_epoch_protocol_test`
(casos E6 e E15). Esses casos so existem se o objeto pinado estiver no clone.

O CI clonava raso. `actions/checkout` traz por padrao apenas o commit do evento
(`fetch-depth: 1`), e nenhum dos SHAs pinados sobrevive a isso. As duas suites
reagiram de maneiras opostas a exatamente a mesma condicao:

- `session_epoch_protocol` reprovava o gate inteiro com `ENVIRONMENT_ERROR`;
- `alladin_foundation` imprimia uma linha e retornava zero — **contada como
  `PASS` com dois casos que nunca rodaram**.

O segundo comportamento e o perigoso. Um vermelho recorrente ao menos se faz
notar; um verde que omite os casos de rollback afirma uma prova que ninguem fez.
Por quatro execucoes seguidas o resumo disse `PASS` para uma verificacao
parcialmente cega, e nenhum numero do relatorio revelava a diferenca.

**Regra.** Caso que nao rodou nunca soma como aprovado. Quando a condicao de
execucao falta, a suite registra o caso, termina em `NOT_RUN` e sai diferente de
zero. `NOT_RUN` ja existe na taxonomia justamente para isso: e a diferenca entre
*"verifiquei e esta certo"* e *"nao verifiquei"*.

**Consequencia pratica.** O ambiente e que deve ser corrigido, nao a expectativa:
o workflow agora clona com `fetch-depth: 0`, e as quatro provas historicas passam
a ser efetivamente executadas no Linux do CI. O caminho de `NOT_RUN` continua
existindo para clones rasos legitimos — nunca como forma de silenciar ausencia.

**Cuidado na emissao.** O classificador casa o primeiro marcador que encontra na
saida, e `NOT_RUN` precede `PRODUCT_FAIL` na ordem dele. Uma suite que tenha
falhas reais **nao** deve imprimir o marcador literal, ou uma falha de produto
seria reclassificada como caso nao executado. Havendo falha real, ela manda; os
casos nao executados sao relatados em prosa, sem marcador.

## Prove que esta testando os bytes do candidato

Durante QA local foi observado que uma origem em `127.0.0.1` servia bytes
antigos associados ao cache/service worker, enquanto `localhost:8000` servia o
candidato atual. As duas origens sao distintas para o navegador, e cada uma tem
o seu proprio registro de service worker e o seu proprio armazenamento.

A licao nao e "use sempre localhost" — e que **a origem pode mentir sobre qual
build esta em teste**. Antes de classificar divergencia visual ou funcional como
regressao:

- confirmar que a origem esta servindo o build esperado;
- conferir `build-id`/artefato esperado quando aplicavel;
- suspeitar de cache/service worker quando uma origem local divergir de outra;
- repetir a verificacao em origem local limpa antes de atribuir o problema ao
  produto.

Um candidato julgado sobre bytes que nao sao os dele produz as duas falhas
possiveis: aprova o que deveria reprovar e reprova o que deveria aprovar.

## Validade da evidencia

- Mudanca em runtime, teste, manifest, fixture ou configuracao invalida os gates afetados.
- Teste focado nao substitui o tier exigido.
- Resultado antigo pode ser citado como baseline, nunca como PASS atual.
- Teste que deixa de falhar apos afrouxar uma expectativa precisa de justificativa independente.
- CI verde nao substitui fluxo manual quando o criterio exige percepcao visual ou dados do navegador.
- Benchmark verde nao substitui suite focal, tier `full` nem verificacao visual.
