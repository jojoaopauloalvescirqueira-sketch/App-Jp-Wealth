# Auditoria de qualidade do codigo - 2026-08-09

- Baseline: `f722eb3`
- Escopo: aplicacao estruturada, persistencia, regras de risco, MEI-JP, PWA, testes e governanca de agentes
- Metodo: leitura integral orientada por manifest, buscas de dependencias, casos em Chromium e suite Python
- Estado: **bloqueado para classificacao institucional/release; Onda A/B implementada e verificada**

## Nota

**4,2/10 para o runtime atual como software financeiro institucional.** A nota e orientada pelo risco e nao e uma media aritmetica: divergencia financeira N3 bloqueante limita a prontidao mesmo quando a engenharia de suporte melhora.

Essa nota permanece porque esta branch nao altera as regras financeiras que concentram os achados criticos. A capacidade de engenharia/governanca passou a **7,5/10** apos a implementacao de contexto canonico, skills, preflight, gate reproduzivel, CI preparada e reconciliacao do harness. Essa segunda nota mede capacidade de entrega controlada, nao prontidao financeira para release.

| Dimensao | Nota | Motivo principal |
|---|---:|---|
| Correcao financeira/normativa | 3,0 | Divergencias N3 em perfis, DD, Genese, fases, LIFO e Stop Raiz-N. |
| Confiabilidade e dados | 5,0 | Boas protecoes recentes, mas recuperacao e canonicalizacao do estado ainda possuem defeitos. |
| Testes e evidencia | 7,5 | Gate unificado, Chromium real e evidencia classificada; cobertura do nucleo financeiro ainda e insuficiente. |
| Seguranca e privacidade | 4,5 | Export remove segredo e ha preflight, mas senha de investidor permanece em texto claro no estado local. |
| Manutenibilidade | 5,5 | Contexto e skills reduzem desalinhamento; globais e funcoes muito extensas ainda elevam acoplamento. |
| Arquitetura | 5,0 | Manifest e gerador sao bons contratos, mas o monolito global limita isolamento. |
| UX e acessibilidade | 6,5 | Fluxos recentes e alvos corrigidos; landmarks e semantica estrutural permanecem inconsistentes. |

Evidencia pos-implementacao: tier `standard` PASS 5/5; tier `full` PASS em 9 verificacoes e `PRODUCT_FAIL` em 2 defeitos N2 conhecidos. Nenhuma falha N3 foi silenciada ou corrigida sem decisao.

## Pontos fortes confirmados

- Ordem de carga e hashes formalizados em `src/js/manifest.json`.
- Original e artefato portatil preservados, com gerador deterministico.
- Migração defensiva cobre muitas chaves antigas e o fluxo recente de Finalizar Sessao evita `localStorage.clear()`.
- Testes Playwright exercitam navegador real, persistencia, modal, responsividade e multiplas abas.
- MEI-JP separa retorno simples e logaritmico, usa desvio amostral (`n-1`), `Math.max(...simple)`/`Math.min(...simple)`, Box-Muller e correcao de Ito em `src/js/30-accounting/03-mei-jp.js:40-202`.
- Exportacao remove senha de investidor em `src/js/30-accounting/01-daily-ledger.js:78-115`.

## Achados criticos N3

### C-01 - Perfis conservadores revogados permanecem ativos

- Local: `src/js/00-core/01-risk-profiles.js:4-8`.
- Evidencia: Longevity/High/Plus usam fatores 0,66/0,50/0,33, MDD 9,90/7,50/4,95 e alavancagem 0,26/0,20/0,13.
- Norma corrente incorporada ao projeto aponta 0,53/0,40/0,27, MDD 7,95/6,00/4,05 e 0,21/0,16/0,11.
- Impacto: todos os limites derivados por perfil podem ficar mais permissivos.
- Correcao: ADR N3 com tabela unica aprovada, teste de todas as derivacoes e migracao sem reescrever a escolha nominal salva.

### C-02 - Drawdown operacional nao usa equity oficial ao vivo

- Local: `src/js/10-domain/02-risk-calculations.js:2-35`.
- Evidencia: `ddDollar` e a soma de risco aberto e perdas realizadas; uma queda de equity sem ordens nao altera o DD.
- Impacto: fase, alarme e guilhotina podem divergir da perda patrimonial real.
- Correcao: definir fonte autoritativa de equity, cadencia e contingencia; criar exemplos estatutarios antes do codigo.

### C-03 - Ordem Genese nao combina teto de risco e teto de alavancagem

- Local: `src/js/10-domain/03-phase-transitions.js:289-316`.
- Evidencia: `checkPhaseCap()` bloqueia risco da Genese, mas nao o nocional/alavancagem por ordem.
- Impacto: ordem pode respeitar risco financeiro e violar exposicao maxima.
- Correcao: decisao N3 e gate atomico que avalie ambos os tetos sobre saldo inicial.

### C-04 - Stop abaixo de 2 ATR e apenas classificado

- Local: `src/js/10-domain/04-stop-statistics.js:15-23` e fluxo de gravacao da ordem.
- Evidencia: `atrStrat()` retorna rotulo; nao existe veto operacional correspondente.
- Impacto: operacao estatisticamente fragil pode ser registrada sem rito de excecao.
- Correcao: decidir se a norma exige bloqueio ou ciencia formal e testar fronteiras 1x, 2x, 3,5x, 5x e 7x.

### C-05 - Downgrade ignora histerese e confirmacao H4

- Local: `src/js/10-domain/03-phase-transitions.js:162-177`.
- Evidencia: basta a matematica indicar fase inferior e as superiores estarem vazias.
- Impacto: oscilacao de fronteira pode causar downgrade prematuro.
- Correcao: aplicar decisao formal de histerese/confirmacao a uma fonte de DD validada.

### C-06 - Gatilho compulsorio de poda LIFO nao esta implementado

- Local: `src/js/10-domain/02-risk-calculations.js:58-67` e transicoes.
- Evidencia: ha sugestao textual de poda quando ja existe excesso, nao o gatilho processual de +1,00 pp com auditoria.
- Impacto: reducao obrigatoria pode depender de acao discricionaria tardia.
- Correcao: ADR N3 com evento, ordem de poda, idempotencia e registro de auditoria.

### C-07 - Fase 4 aceita inclusao sem todo o rito de salvaguarda

- Local: `src/js/10-domain/03-phase-transitions.js:289-316` e renderizacao da grade ativa.
- Evidencia: o gate verifica teto por ordem/consolidado, mas nao pedido formal, veto, executor e unicidade da defesa.
- Impacto: exposicao nova pode entrar na fase mais critica sem governanca completa.
- Correcao: modelar o rito como estado auditavel antes de liberar escrita.

### C-08 - Quarentena nao deriva automaticamente da condicao autoritativa

- Local: `src/js/10-domain/01-risk-instruments.js:176-178`.
- Evidencia: `quarantineActive()` verifica apenas datas ja formalizadas em `S.quarantine`.
- Impacto: guilhotina e quarentena podem ficar desacopladas do evento real.
- Correcao: definir equity oficial, evento de disparo e persistencia idempotente; manter correcao de entrada sem mensagem fantasma.

### C-09 - Fator padrao do Stop Raiz-N diverge da norma atual

- Local: `src/js/00-core/03-default-state.js:67`, `src/js/00-core/04-persistence.js:608`, `src/js/10-domain/04-stop-statistics.js:28-56`.
- Evidencia: padrao 1,8 em tres caminhos; a versao normativa atual aponta 1,25.
- Impacto: stop estatistico recomendado muda materialmente.
- Correcao: decisao N3, consolidacao em fonte unica e migracao que preserve valores escolhidos manualmente.

### C-10 - Projecao MEI herda retorno por perfil sob conflito normativo

- Local: `src/js/30-accounting/03-mei-jp.js:121-202`.
- Evidencia: `runMEIMonteCarlo()` usa `riskProfileMonthlyTarget(cal.pr)` como drift.
- Impacto: cenarios podem apresentar meta como parametro estatistico mesmo quando a memoria de calculo nao esta aprovada.
- Correcao: manter o motor matematico, mas decidir separadamente a origem do drift e os rotulos de projecao.

## Achados altos e medios

### H-01 - Importacao invalida libera persistencia antes da validacao (N2)

- Local: `src/js/30-accounting/01-daily-ledger.js:274-303`.
- Evidencia: `resumeJPWealthPersistence()` roda antes de `FileReader`, parse, normalizacao e confirmacao.
- Impacto: modo de recuperacao pode perder protecao mesmo quando o arquivo e invalido.
- Teste: `tools/persistence_recovery_test.py` encontra a regressao.
- Correcao: manter gate bloqueado ate backup validado e confirmado; liberar somente na resolucao atomica.

### H-02 - Estado vazio nao e canonico apos reload (N2)

- Local: `src/js/00-core/04-persistence.js`, representacao inicial e checkpoint de Finalizar Sessao.
- Evidencia: `reserveMasterCapital` nasce como `''`, mas a migracao o converte para `'0'`; apos reload, `sessionHasChanges()` acusa alteracao inexistente.
- Impacto: falso positivo de dados pendentes e experiencia incoerente no encerramento.
- Teste: `tools/finalize_session_test.py` falha com diff estrutural restrito a essa chave.
- Correcao: definir uma representacao canonica, migrar de forma idempotente e cobrir vazio, reload, backup antigo e valor real.

### H-03 - Falha de exportacao nao orientava contingencia manual (N1/N2) - RESOLVIDO

- Local: `src/js/30-accounting/01-daily-ledger.js:249-251`.
- Correcao aplicada: alerta orienta registro manual das ordens, fechamentos e notas recentes antes de fechar a pagina.
- Teste: `tools/persistence_failure_test.py` PASS nas superficies modular e portatil.

### H-04 - Service worker nao precacheava todos os recursos carregados (N1) - RESOLVIDO

- Local: `sw.js:5-28` versus `index.html:1194-1199` e logo do cabecalho.
- Correcao aplicada: logo e scripts `10` a `15` adicionados ao precache; fonte externa de calendario isolada no teste de lifecycle.
- Teste: `tools/service_worker_upgrade_test.py` PASS.

### H-05 - Notas possuia sobreposicao e visibilidade quebrada (N0-V/N1) - RESOLVIDO

- Local: `src/styles/app.css:1709` e `1804-1814`; regra geral do shell para `.header-action`.
- Correcao aplicada: regras explicitas de `hidden`, offset dinamico do inspetor, alvos de toque e menu contextual lateral.
- Teste: `tools/mvp_notes_test.py` PASS em desktop, mobile, CRUD, filtros, menus, backup e portatil.

### H-06 - Credencial de leitura persiste em texto claro (N2/seguranca)

- Local: `src/js/00-core/04-persistence.js:615-617` e onboarding.
- Impacto: script na mesma origem ou acesso ao perfil pode ler a senha de investidor.
- Correcao: decisao de produto sobre nao persistir, cofre do navegador ou criptografia com chave fora do mesmo armazenamento; nao prometer seguranca por ofuscacao.

### M-01 - `openOnboardingModal()` possui cerca de 1.983 linhas

- Local: `src/js/40-app/04-onboarding.js:187-2169`.
- Impacto: alto acoplamento entre estado temporario, render, validacao e listeners; regressao visual frequente.
- Correcao: somente apos gates verdes, extrair componentes puros por etapa mantendo IDs e contrato global.

### M-02 - Semantica HTML inconsistente

- Local: `index.html` possui tres elementos `main` e nenhum `h1` estatico.
- Impacto: landmarks ambiguos para tecnologia assistiva.
- Correcao: tarefa N1 dedicada com teste de acessibilidade e sem alterar layout.

### M-03 - Calibracao MEI e heuristica e outliers sao apenas diagnosticos

- Local: `src/js/30-accounting/03-mei-jp.js:79-143`.
- Evidencia: interpolacao linear de sigmas e declarada escolha de engenharia; IQR nao estabiliza os parametros.
- Impacto: amostras pequenas/extremas podem alterar a dispersao de modo instavel.
- Correcao: manter transparência; avaliar winsorization robusta, shrinkage por variancia e backtest fora do runtime antes de qualquer troca.

## Plano de melhoria

1. **Onda A - Governanca executavel (implementada, aguardando revisao):** contexto em camadas, skills locais, preflight, gates, templates, auditoria e handoff.
2. **Onda B - Baseline N0/N1 verde (implementada nesta branch):** alvos de toque/Notas, precache, portatil e avisos corrigidos; tier standard verde.
3. **Onda C - Integridade N2:** recuperacao atomica, persistencia sob falha e estrategia de credenciais, com fixtures antigas e round-trip.
4. **Onda D - Decisoes N3:** aprovar uma ADR por conflito, adicionar testes de caracterizacao e somente entao alterar codigo financeiro.
5. **Onda E - Arquitetura:** decompor onboarding e globais depois que os contratos estiverem cobertos.

## Conclusao

O projeto agora possui evidencia reproduzivel e um baseline nao normativo verde, mas ainda nao atende o nivel institucional pretendido: dois defeitos N2 permanecem confirmados e os maiores riscos continuam na aderencia normativa. A proxima ordem segura e resolver cada N2 em branch propria e, depois, aprovar ADRs N3 antes de qualquer mudanca financeira.
