# Tarefa ativa - Laboratorio de Probabilidade: Galton Board

- Data: 2026-08-11
- `BASE_SHA`: `d9510dbb55f0`
- Branch: `codex/galton-board`
- Nivel: N1 (simulador, navegacao, acessibilidade e PWA) + N2 delimitado (preferencias locais isoladas)
- Autoridade: A2 para a implementacao N1 e A3 apenas para a chave de preferencias explicitamente solicitada no brief; commit, push, merge e deploy nao autorizados
- Estado: tecnicamente pronta e validada no candidato local; sem autorizacao para
  commit ou publicacao

O estado Git corrente (branch, HEAD e arvore) deve ser confirmado pelo preflight. Este contrato nao substitui fatos mutaveis do disco.

## Objetivo

Implementar, dentro de Configuracoes, um Galton Board educacional com fisica rigida 2D real, simulacao deterministica por seed, histograma empirico, comparacao teorica honesta, estatisticas, controles acessiveis e lifecycle seguro. O laboratorio deve permanecer isolado do motor financeiro, de credenciais e do estado operacional `S`.

## Classificacao e limites de autoridade

- N1/A2: UI, Canvas, motor fisico, estatistica descritiva, navegacao, acessibilidade, responsividade, lifecycle, testes e documentacao.
- N2/A3 delimitado: somente `localStorage['jpwealth_galton_preferences_v1']`, com preferencias uteis; nunca bolas, fila, histograma, resultados ou estado intermediario.
- N3/A4: nao autorizado e fora do escopo. Nenhuma formula, limite, perfil, fase, risco, LIFO, DD, contabilidade ou norma financeira pode mudar.
- Git/publicacao: branch local autorizada; commit, push, merge e deploy continuam pendentes de autorizacao separada.

## Arquivos permitidos

- `src/vendor/planck/**`;
- `src/js/40-app/18-galton-board/**`;
- `src/js/40-app/09-settings-modal.js`;
- `src/js/40-app/07-finalize-session.js`;
- `src/js/40-app/06-app-icons.js`, apenas para descoberta real de atualizacao do service worker;
- `src/styles/app.css`;
- `src/js/manifest.json`, `index.html`, `sw.js`, `build-id.js` e `dist/**` somente pela integracao/rebuild oficial;
- `data/samples/galton-preferences-v1.json`;
- testes e validadores diretamente relacionados em `tools/**` e `tests/README.md`;
- documentacao diretamente afetada em `docs/architecture/**`, `docs/governance/**`, `docs/testing/**`, `docs/security/**`, `docs/recovery/**`, `CHANGELOG.md`, `PROJECT-FILES.txt`, `README.md` e `SESSION_HANDOFF.md`.

Qualquer outro caminho exige nova avaliacao antes de editar.

## Invariantes

- O Galton Board nao le nem escreve `S`, `DEFAULTS`, contas, ordens, ledger, perfis, credenciais ou APIs financeiras.
- A trajetoria resulta apenas da integracao fisica; aleatoriedade deterministica pode atuar no ponto de soltura e na tolerancia fixa dos pinos, nunca como decisao esquerda/direita durante o percurso.
- O passo fisico e fixo em `1/120 s`, independente do `requestAnimationFrame`, com acumulador e limite de substeps.
- Mesma seed, configuracao e sequencia de liberacao devem reproduzir o experimento no mesmo motor/runtime; nenhuma promessa de identidade bit a bit entre plataformas.
- A curva binomial teorica aparece apenas quando o arranjo e simetrico e o ponto de soltura esta centralizado; nunca e ajustada aos dados observados.
- Corpos assentados sao contados uma vez, removidos do mundo e preservados apenas como agregados.
- Ao sair do painel, fechar Configuracoes, ocultar a pagina ou desmontar, loops e observadores devem pausar ou ser limpos sem vazamentos.
- `prefers-reduced-motion` e alternativas acessiveis ao hover/Canvas devem ser respeitados.
- O simulador e educativo e nao e um modelo de retorno de Forex nem promessa de desempenho.
- Nenhum recurso de runtime depende de CDN, telemetria ou rede externa.

## Criterios de aceite

1. Configuracoes oferece `Laboratorio de Probabilidade > Galton Board` e o modal continua navegavel por teclado.
2. A placa triangular tem `linhas + 1` compartimentos, colisao real via Planck.js vendorizado e gravidade inclinavel de -3 a +3 graus.
3. Controles cobrem fila +1/+10/+100/+500, executar, pausar/continuar, reset, velocidade 0.5x/1x/2x/4x, ponto de soltura, presets e parametros avancados seguros.
4. O painel exibe histograma empirico, estatisticas, detalhes por compartimento, mensagem de convergencia e curva teorica apenas quando elegivel.
5. Preferencias validas sobrevivem ao reload, estado transitorio nao; JSON corrompido ou falha de escrita nao pode sobrescrever estado financeiro.
6. PWA inclui todos os scripts do manifest no precache e abre o laboratorio offline apos o cache ser atualizado.
7. Testes cobrem PRNG, geometria, estatisticas, elegibilidade teorica, persistencia, lifecycle, manifest/precache, responsividade e smoke fisico.
8. Benchmark registra cenario de 10.000 bolas em lotes sem crescimento ilimitado de corpos.
9. Verificacao real no navegador cobre desktop, viewport movel, temas claro/escuro e reduced motion.

## Baseline e riscos conhecidos

- `python3 tools/quality_gate.py --tier standard`: PASS 6/6 no `BASE_SHA`.
- `python3 tools/service_worker_upgrade_test.py`: BASELINE_FAIL no `BASE_SHA`; `sw.js` nao precacheia `src/js/20-ui/12-nav-style.js` nem `src/js/40-app/17-economic-calendar.js`, quebrando o offline. A correcao e diretamente necessaria para o requisito PWA desta tarefa.
- Viewport 390 x 844: defeito visual de baseline; regra tardia de `#settingsOverlay` sobrepoe o padding movel e recorta o modal. A correcao N0-V e teste de geometria pertencem a integracao do novo painel.
- O preflight detecta 19 caminhos materiais posteriores a `83f688f`; `CURRENT-STATE`, `CODE-MAP`, tarefa ativa e handoff devem ser reconciliados com o runtime atual antes da conclusao.

## Dependencia vendorizada

- Planck.js `1.5.0`, licenca MIT, sem dependencias transitivas de runtime.
- O arquivo vendorizado deve preservar os bytes oficiais e registrar versao, origem, integridade publicada e SHA-256 local.
- A dependencia deve constar no manifest, build portatil, precache e verificacoes de seguranca; nenhuma URL remota pode ser carregada em runtime.

## Plano de rollback

Reverter apenas os arquivos listados neste contrato para `BASE_SHA`, remover a chave isolada `jpwealth_galton_preferences_v1` se o gestor autorizar a exclusao de dados locais e executar novamente os gates. Nao usar reset destrutivo nem reescrever historico.

## Fase posterior deliberadamente adiada

- Hipoteses/experimentos guiados e audio ficam para uma Fase 2.
- A Fase 1 nao interpreta o resultado como mercado financeiro e nao integra o laboratorio ao dominio normativo.

## Resultado atual

- Implementacao concluida no build local `dbca7e887edd287b`, sem alteracao N3.
- Suite focal Galton, Settings, Finalizar sessao, reproducibilidade de build e upgrade
  PWA: `PASS` no candidato consolidado.
- Benchmark: `PASS`, 10.000/10.000 assentadas, zero expiracoes/rejeicoes,
  `bodyCount=1` e pico de 240 corpos; tempo e comparacao binomial sao diagnosticos,
  nunca criterio de fitting.
- Browser: `PASS` para rota/Canvas/execucao no desktop e, pela suite Chromium,
  viewport `390 x 844`, temas e reduced motion.
- Gate `full`: `PASS 17/17`, zero falhas, erros ou omissoes; artefato
  `tools/.artifacts/quality-20260811T165927-full.json`.
- Commit, push, merge e deploy permanecem pendentes de autorizacao humana separada.
