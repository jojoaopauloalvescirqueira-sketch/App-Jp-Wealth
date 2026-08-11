# Estado atual do projeto

- Data da fotografia: 2026-08-11
Source revision representada: `d9510dbb55f0`
- Nota da revisao: este e o candidato material validado; o diff Galton ainda nao
  possui revisao commitada.
- Branch do candidato: `codex/galton-board`
- HEAD atual: `d9510dbb55f0` com diff material nao commitado
- Estado de integracao: candidato local; nao commitado, nao enviado, nao integrado e
  nao publicado
- Validade: esta fotografia descreve o disco no build local
  `dbca7e887edd287b`. Qualquer mudanca posterior em fonte, manifest, fixture, gerados
  ou testes invalida as evidencias afetadas.

## Estado confirmado no disco

- A aplicacao permanece estatica, local-first, sem framework e sem backend
  obrigatorio. Os scripts continuam classicos e globais.
- `src/js/manifest.json` registra 53 scripts: os 46 do baseline, Planck.js vendorizado
  e seis modulos do Galton Board anexados ao fim, sem reordenar o legado.
- A chave financeira principal continua `jpwealth_v9_state` e seu schema nao mudou.
- O candidato adiciona somente a chave auxiliar
  `jpwealth_galton_preferences_v1`, autorizada como N2 delimitada para preferencias do
  laboratorio. Ela nunca armazena bolas, fila, histograma, estatisticas ou resultado.
- O caminho da feature e
  `Configuracoes > Laboratorio de Probabilidade > Galton Board`.
- Planck.js `1.5.0` esta local em `src/vendor/planck/`, sob licenca MIT, sem CDN e
  com SHA-256 fixo
  `69c6675a04121ec4042921b7d3d298058617d3211c243d8ea4d940a58af99974`.
- O mundo fisico usa passo fixo de `1/120 s`. O default tem 10 linhas, espacamento
  horizontal `1`, vertical `0.82`, raio de pino `0.09`, raio de bola `0.14`, densidade
  `1`, restituicao `0.28`, atrito `0.22`, gravidade `9.81`, jitter `0.07`, tolerancia
  `0` e colisao bola-bola desligada.
- A geometria possui chute superior e guias simetricas que acompanham o envelope
  triangular; a soltura normalizada fica limitada a abertura segura e `N` linhas
  produzem `N + 1` compartimentos.
- `sw.js` inclui os 53 scripts, inclusive as duas omissoes do baseline
  (`12-nav-style.js` e `17-economic-calendar.js`). `validate_project.py` agora exige
  equivalencia entre manifest e precache.
- O tier `standard` passa a ter 7 verificacoes e o `full`, 17. O benchmark de 10.000
  bolas e separado e nao integra um tier cumulativo.
- `build-id.js` e `dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html` foram gerados
  exclusivamente por `tools/rebuild_monolith.py`. O Build ID e
  `dbca7e887edd287b`; o portatil tem SHA-256
  `038f9bf948aca9cec41bed34af4f130865f57c327b5f975216ea411f929bb416`.

## Escopo e autoridade

- N1/A2: simulador, navegacao, acessibilidade, responsividade, PWA, testes e docs.
- N2/A3 delimitado: somente preferencias na chave
  `jpwealth_galton_preferences_v1` e sua remocao por `Finalizar sessao`.
- N3/A4: fora do escopo. Nenhuma formula financeira, perfil, fase, limite, MDD, DD,
  LIFO, stop, quarentena, contabilidade, MEI ou artigo do Estatuto foi alterado.
- Criacao da branch local foi autorizada. Commit, push, merge e deploy continuam
  sem autorizacao.

## Evidencia deste candidato

| Verificacao | Resultado | Escopo/observacao |
|---|---|---|
| `python3 tools/agent_preflight.py --mode edit --allow-dirty` | PASS | Branch `codex/galton-board`, HEAD `d9510dbb55f0`, 53 scripts; dirty conhecido e autorizado. |
| `python3 -u tools/galton_board_test.py` | PASS | Matematica, fisica deterministica, persistencia protegida, UI, teclado, responsividade e lifecycle em Chromium real. |
| `python3 -u tools/galton_board_benchmark.py` | PASS | 10.000/10.000 assentadas, 0 expiradas/rejeitadas, `bodyCount=1`, pico de 240 corpos e 602,84 bolas/s informativos. |
| `python3 tools/settings_modal_test.py` | PASS | Rota, foco, busca, subdialogos e geometria movel sem alterar estado financeiro. |
| `python3 tools/finalize_session_test.py` | PASS | Wipe seletivo local/remoto, controlador montado em duas abas e nenhuma ressurreicao da preferencia Galton. |
| `python3 tools/service_worker_upgrade_test.py` | PASS | Descoberta pelo runtime sem `update()` externo, `waiting` conservador, duas abas, ativacao apos fechamento, build novo online/offline e cache externo preservado. |
| `python3 tools/build_reproducibility_test.py` | PASS | Build ID canonico `dbca7e887edd287b`; inputs oficiais ausentes bloqueiam o build e arquivos locais ignorados nao o alteram. |
| Navegador real | PASS | In-app Browser confirmou rota, painel, Canvas, execucao e disclaimer; uma instalacao ja cacheada ativou `dbca7e887edd287b` depois de fechar todos os clientes e abriu Galton online e com o servidor desligado. A suite focal cobriu `390 x 844`, temas e reduced motion em Chromium. |
| `python3 tools/quality_gate.py --tier full` | PASS 17/17 | Zero `PRODUCT_FAIL`, `TEST_HARNESS_FAIL`, `ENVIRONMENT_ERROR`, `BASELINE_FAIL` ou `NOT_RUN`; artefato `tools/.artifacts/quality-20260811T165927-full.json`. |

Relatorios locais de qualidade ficam em `tools/.artifacts/` e sao ignorados pelo Git.
Usar apenas o artefato cuja arvore/candidato corresponda ao estado examinado.

## Impacto agentico e reconciliacao

`AGENTIC IMPACT CHECK: AGENTIC IMPACT DETECTED`

`BASIS:` a feature material altera arquitetura, manifest, PWA, contrato de
persistencia auxiliar, navegacao de Configuracoes, composicao dos gates e inventario
de arquivos — representacoes consumidas pelo preflight, pelas skills e por agentes.
Foram examinadas as categorias existentes de agentes, skills, routing/registry,
bootstrap/preflight, contexto operacional, contratos, arquitetura, fontes canonicas
e indice/memoria.

Blast radius do changeset `d9510dbb55f0 + diff Galton`:

| Categoria | Impacto | Acao local | Estado no checkpoint |
|---|---|---|---|
| `AGENTS.md` e autoridade | AFFECTED | NOT_REQUIRED | CURRENT: a classificacao N1/N2/N3 existente cobre a mudanca. |
| Skills e routing | AFFECTED | NOT_REQUIRED | CURRENT: preflight, change-control, data-safety, security, browser, test-triage, arquitetura e post-audit ja roteiam o trabalho. |
| Bootstrap/preflight e manifest | AFFECTED | REQUIRED | Manifest com 53 entradas; preflight passou apos hashes finais. |
| Contexto operacional | AFFECTED | REQUIRED | `ACTIVE-TASK`, este `CURRENT-STATE` e `SESSION_HANDOFF` representam o candidato. |
| Arquitetura/contratos | AFFECTED | REQUIRED | `ARCHITECTURE.md`, `CODE-MAP.md`, `GALTON-BOARD.md`, seguranca e gates reconciliados. |
| Changelog/inventario | AFFECTED | REQUIRED | `CHANGELOG.md`, `README.md`, `tests/README.md` e `PROJECT-FILES.txt` reconciliados. |
| Norma e ADRs N3 | NOT_AFFECTED | NOT_REQUIRED | O laboratorio nao altera o dominio normativo. |
| Indice/vetor/memoria de projeto | NOT_AFFECTED | NOT_REQUIRED | Nao existe mecanismo oficial de indexacao ou vetorizacao no repositorio. `INDEX NOT REQUIRED`. |

Natureza: a feature e `MATERIAL`; a atualizacao destes documentos e
`RECONCILIACAO`. Nao ha nova source revision commitada. Runtime, contratos,
manifest, build, contexto e evidencias estao reconciliados: `SYSTEM RECONCILED`.

## Contratos N2 vigentes

- `reserveMasterCapital` deriva de `params.saldoIni` tambem no boot fresco, conforme
  a formula ja usada por `migrate()` (`7d18bca`).
- Recuperacao so substitui estado depois de leitura, validacao, normalizacao e
  confirmacao atomica (`8296f1a`).
- `investorPassword` permanece apenas em memoria da sessao e nunca entra em storage,
  checkpoint ou backup (`e0b59d3`).
- A preferencia Galton e isolada, preserva extensoes desconhecidas, bloqueia escrita
  para JSON/envelope/schema incompatível e tambem quando o getter de `localStorage`
  lança `SecurityError`. A fixture e sintetica. `Finalizar sessao` remove a chave
  pela allowlist local/remota e invalida controladores montados; nenhuma limpeza usa
  `localStorage.clear()`.

## Pendencias normativas bloqueantes

Nao corrigir silenciosamente. Cada item exige decisao/confirmacao N3 e branch propria:

1. Perfis conservadores no codigo usam fatores revogados (66/50/33) em conflito com a tabela V10 (53/40/27).
2. `compute()` deriva drawdown do risco programado e perdas realizadas, nao da equity oficial ao vivo.
3. Ordem Genese nao aplica de forma combinada o teto de risco e o de alavancagem.
4. Stop abaixo de 2 ATR e classificado, mas nao bloqueado.
5. Downgrade nao aplica integralmente histerese de 0,50 ponto percentual e confirmacao H4.
6. Gatilho compulsorio de poda LIFO em +1,00 ponto percentual nao esta implementado.
7. Fase 4 permite inclusao operacional sem todo o rito de salvaguarda previsto.
8. Quarentena/guilhotina depende de formalizacao manual e nao de uma fonte autoritativa de equity.
9. Fator padrao do Stop Raiz-N aparece como 1,8, enquanto a norma atual indica 1,25.
10. Projecoes MEI por perfil precisam de decisao sobre memoria de calculo e aderencia normativa.

## Divida e riscos residuais

- `openOnboardingModal()` concentra aproximadamente duas mil linhas e muitos
  contratos globais.
- Estado, dominio e interface ainda compartilham escopo global legado.
- Cabecalhos de seguranca sao minimos e nao ha CSP documentada.
- Planck.js e terceiro minificado; a mitigacao e pin, proveniencia, licenca, hash,
  operacao offline e regressao fisica. Atualizacao exige nova auditoria.
- Uma combinacao avancada extrema, fisicamente valida, ainda pode aprisionar corpos
  sobre pinos ate `maxBallAge`; esses vencimentos sao exibidos, classificados e
  excluidos do histograma. Defaults, presets e benchmark de 10.000 encerraram sem
  vencimentos.
- A cobertura automatizada e mais forte em fluxos recentes do que no nucleo
  financeiro.

## Regra de atualizacao

Quem alterar fonte, teste, manifest, fixture ou gerado depois deste checkpoint deve
repetir as verificacoes afetadas. Nao remover falha porque deixou de aparecer em um
teste; registrar causa, comando, candidato e evidencia.
