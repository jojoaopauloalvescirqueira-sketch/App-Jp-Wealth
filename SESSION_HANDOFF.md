# Session Handoff - Galton Board, candidato validado localmente

- Data: 2026-08-11
- Branch: `codex/galton-board`
- `BASE_SHA` e HEAD: `d9510dbb55f0`
- Arvore: candidato material nao commitado
- Manifest: 53 scripts, hashes reconciliados
- Build ID: `dbca7e887edd287b`
- Publicacao: nenhuma; commit, push, merge e deploy nao autorizados

O estado Git e o runtime devem ser confirmados por `git status` e preflight. Esta
nota representa o candidato local gerado e testado; expira se fonte, manifest,
fixture, testes ou gerados mudarem.

## Implementado no candidato

- Caminho `Configuracoes > Laboratorio de Probabilidade > Galton Board`.
- Planck.js `1.5.0` vendorizado sob MIT, SHA-256
  `69c6675a04121ec4042921b7d3d298058617d3211c243d8ea4d940a58af99974`,
  sem CDN ou download em runtime.
- Seis scripts classicos em `src/js/40-app/18-galton-board/`, namespace
  `window.JPWGalton`: config/geometry, PRNG, estatistica, fisica, renderer e
  controller.
- Passo fisico fixo de `1/120 s`, acumulador separado do render, limite de substeps,
  fila, teto de corpos ativos e remocao idempotente apos assentamento.
- Defaults finais: 10 linhas; espacamentos horizontal `1` e vertical `0.82`; raio de
  pino `0.09`; raio de bola `0.14`; densidade `1`; restituicao `0.28`; atrito `0.22`;
  gravidade `9.81`; jitter `0.07`; tolerancia `0`; bola-bola desligada.
- Geometria com chute superior, guias simetricas no envelope triangular, soltura
  normalizada limitada a abertura segura e `N + 1` bins para `N` linhas.
- Histograma empirico, N/media/desvio/moda/assimetria/curtose, detalhes acessiveis por
  bin e binomial `p=0.5` apenas em configuracao simetrica/centralizada, sem fitting.
- Controles +1/+10/+100/+500, executar, pausar/continuar/reset, velocidades
  0.5x/1x/2x/4x, release, inclinacao -3 a +3, presets e parametros avancados.
- Lifecycle pausa ao sair/fechar/ocultar; descarte remove RAF, listeners, observers e
  mundo. Canvas HiDPI tem equivalente DOM e reduced motion.
- Preferencia isolada `jpwealth_galton_preferences_v1`; nenhum corpo/resultado e
  persistido. `Finalizar sessao` remove a chave por allowlist e preserva chaves de
  outras aplicacoes.
- `sw.js` inclui todo o manifest, inclusive as duas omissoes do baseline
  (`12-nav-style.js`, `17-economic-calendar.js`); o validador passa a impor o
  invariante manifest-precache.
- Correcao visual do recorte do modal em `390 x 844` e regressao geometrica no teste
  de Configuracoes.
- Teste focal integrado ao tier `standard`; benchmark longo de 10.000 bolas separado.

## Evidencia disponivel

| Comando/fluxo | Resultado | Observacao |
|---|---|---|
| `python3 tools/agent_preflight.py --mode edit --allow-dirty` | PASS | Branch, HEAD, manifest/hashes e dirty conhecido; aviso de impacto agentico esperado. |
| `python3 -u tools/galton_board_test.py` | PASS | Fisica/matematica, storage inacessivel ou incompatível, wipe, UI, teclado, responsividade e lifecycle em Chromium. |
| `python3 -u tools/galton_board_benchmark.py` | PASS | 10.000/10.000 assentadas, 0 expiradas/rejeitadas, `bodyCount=1`, pico de 240 corpos ativos; 602,84 bolas/s apenas informativos. |
| `python3 tools/settings_modal_test.py` | PASS | Navegacao, busca, foco, subdialogos e geometria movel. |
| `python3 tools/finalize_session_test.py` | PASS | Wipe seletivo local/remoto e nenhuma ressurreicao da preferencia por controlador ja montado. |
| `python3 tools/service_worker_upgrade_test.py` | PASS | Descoberta real do update, worker novo em `waiting`, duas abas antigas preservadas e build novo online/offline depois do fechamento. |
| `python3 tools/build_reproducibility_test.py` | PASS | Build ID canonico `dbca7e887edd287b`. |
| In-app Browser + Chromium da suite focal | PASS | Rota, Canvas, execucao e disclaimer; instalacao cacheada atualizou para `dbca7e887edd287b` e abriu Galton online/offline; `390 x 844`, temas e reduced motion automatizados. |
| `python3 tools/quality_gate.py --tier full` | PASS 17/17 | Zero falhas/erros/omissoes; artefato `tools/.artifacts/quality-20260811T165927-full.json`. |

O benchmark informou distancia de variacao total `0.3581`; isso e diagnostico
qualitativo, nao gate, calibracao ou fitting da curva teorica.

## Gerados oficiais

`build-id.js` e `dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html` foram reconstruidos
pelo gerador oficial. O Build ID e `dbca7e887edd287b`; o SHA-256 do portatil e
`038f9bf948aca9cec41bed34af4f130865f57c327b5f975216ea411f929bb416`.
Nao editar esses derivados manualmente.

## Reconciliacao agentica

- Veredito: `AGENTIC IMPACT DETECTED`.
- Motivo: nova arquitetura/feature, dependencia, script manifest, contrato de
  preferencia auxiliar, rota de Configuracoes, PWA e composicao de testes atingem
  representacoes consumidas por agentes.
- Acao local executada: `CODE-MAP`, `ARCHITECTURE`, `CURRENT-STATE`, modelo de
  seguranca, gates, README, changelog, inventario, testes e este handoff.
- `AGENTS.md`, autoridade, skills e routing: afetados semanticamente, mas continuam
  atuais por referencia; nenhuma alteracao local necessaria.
- Norma/ADRs N3: nao afetados.
- Indice/vetor: mecanismo oficial inexistente; `INDEX NOT REQUIRED`.
- Estado: runtime, manifest, build, contratos, contexto e evidencias reconciliados;
  `SYSTEM RECONCILED`.

## Proximas acoes

1. Fazer o sweep final de seguranca/supply chain, `git diff --check`,
   `git diff --stat` e revisao integral do diff.
2. Apresentar a evidencia ao gestor. Aguardar autorizacoes separadas para commit,
   push, merge ou publicacao.

## Limites e rollback

- Nenhuma regra N3 foi alterada; as dez pendencias normativas de
  `CURRENT-STATE.md` permanecem bloqueadas.
- Hipoteses guiadas de experimento e audio ficam para Fase 2.
- Uma configuracao avancada extrema pode manter corpos em equilibrio sobre pinos ate
  o limite de idade. Esses vencimentos sao comunicados e excluidos da amostra; os
  defaults, presets e o benchmark de 10.000 terminaram com zero vencimentos.
- Rollback de runtime: reverter apenas os arquivos autorizados ao `BASE_SHA`, gerar
  novamente os derivados e repetir gates. A exclusao da chave local no navegador
  exige autorizacao humana; nao usar reset destrutivo nem reescrever historico.
