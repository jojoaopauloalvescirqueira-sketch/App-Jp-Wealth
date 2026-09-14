# DASHBOARD-SURFACES-01 — separação da estrutura e painéis

## Brief e autoridade
O Dashboard sintetiza Forex, Finanças Pessoais, Research e Alladin pelas fontes canônicas existentes; oferece atalhos sem assumir suas mutações. Header/sidebar orientam o usuário e a marca retorna ao Dashboard. A tarefa modifica somente a apresentação: divisórias coerentes, maior presença óptica do logo e quatro painéis largos empilhados, claros sobre o canvas neutro, com equivalente escuro.

O proprietário respondeu “autorizo” à proposta de três mudanças, branch `codex/dashboard-surfaces-20260914` e worktree isolada a partir de `5f0c968`. Não autoriza integração. Base Git real: `5f0c9680bdd9a93e9d184ca751999c70193a72aa`, Settings publicado mas PR19 ainda bloqueado pelo FULL remoto (session-finalization). Isso permanece dívida externa ao delta, não é PASS nem defeito causalmente atribuído. Base reproduzida:306 inputs, build `3d363e1cf0d07f06`, fingerprint `b9394484f9fb5764398cb6d17eed269eb30f2625273d68f4eb5d4036ea0a7340`.

Raiz: `/Users/joaopauloalves/.codex/dashboard-surfaces/20260914/product`. Risco N0-V / autoridade A2 para apresentação; autorização específica de criar branch/worktree recebida, sem demais ações Git. CHG e CTX limitados a este documento e cabeçalho de ACTIVE-TASK. Contexto histórico preservado, não declarar main atualizada. Evidência: `../evidence/`; controles de demonstração: `../control/`; recuperação externa. Snapshot anterior, main, stash e outras worktrees intocados.

## Caminhos permitidos (relativos à raiz acima)
- `src/styles/app.css`: somente divisórias da shell, tamanho proporcional da marca e composição dos quatro painéis de #dashMacro.
- `tools/dashboard_macro_test.py`: trocar contrato 2x2 pelo empilhamento aprovado; manter as demais asserções e acrescentar prova visual focal.
- `tools/visual_proportion_test.py`, `tools/apple_experience_test.py`: apenas se houver expectativa geométrica afetada demonstrada; não remover invariantes funcionais.
- `build-id.js` e `dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html`: somente `python3 tools/rebuild_monolith.py`.
- `docs/work/ACTIVE-TASK.md`: cabeçalho delimitado, histórico intacto.
- `docs/work/CHG-DASHBOARD-SURFACES-20260914.md`: este contrato.

Sem editar JS, index, manifest JS, logo/ativos, Settings, regras, dados, persistência, dependências, skills, Harness, gates/CI ou outras áreas. Sem staging/commit/push/PR/merge/deploy, reset/stash/limpeza ou atualização geral de contexto.

## Critérios fixados antes da mudança
1. Header e sidebar possuem separadores finos neutros coerentes, sem alterar largura da lateral ou rotas. Barra contextual Forex, modos lateral/superior e recolhimento preservados.
2. Logo cresce mantendo aspecto intrínseco, sem crop/distorção/novo ativo; continua acionável e acessível por teclado, sem colidir com controles no celular.
3. Quatro painéis de módulos empilhados em desktop/tablet/celular, brancos no claro e superfície distinta do canvas no escuro. Bordas discretas, raio e espaçamento com tokens existentes; layout interno horizontal no desktop e reflow no celular.
4. Mesmos dados/avisos/estados PARTIAL, UNAVAILABLE, BLOCKING; resumos/links e Sistema/Atalhos existentes; nenhuma preferência alterada ao navegar/renderizar. Sem widgets operacionais devolvidos ao Dashboard.
5. Sem overflow da página nem controles/textos cortados; foco visível e ações funcionais, navegação repetida e logo já no Dashboard preservados. Conteúdo vazio/sintético e textos longos pertinentes.

## Validação e recuperação
Antes: executar o contrato de domínio atual na baseline e capturar geometria/screenshots; fixar as novas expectativas de apresentação antes do CSS. Depois: focal Dashboard com dados sintéticos e recursos locais/simulados existentes; desktop/mobile, temas, modos de navegação/recolhimento, zoom e CTA/foco. Regressões próximas de navegação/Apple/proporção conforme delta; tier standard obrigatório N0-V. FULL é gate de futura integração, não repetir FULL local apenas por formalidade nesta entrega nem apagar sua falha remota herdada. Não modificar gates ou expectativas funcionais para aprovar.

Usar Python/Playwright/Chromium existentes, sem dados reais ou APIs econômicas ao vivo, sandbox loopback e fixtures já existentes. Operações Git internas de testes apenas em fixtures descartáveis próprias sem remoto/hooks, jamais no produto. Derivados oficiais, revisão independente focal, freeze com hashes/modos/fingerprint e diff; recuperação por snapshot fiel externo e conferência de hashes. Rollback limitado ao próprio delta a partir de HEAD e snapshot, nunca restaurar/resetar outras tarefas. Manifestos e resultados anteriores não sobrescritos. Candidate final só será apresentado ao proprietário, sem aceite presumido.

## Fontes e limites
AGENTS/CONTEXT-MAP; Harness §§0.3,3–4,31 e qualidade; X1 em IMPLEMENTAR e filosofia composição/componentes/adaptação; preflight/change-control/post-change-audit. Código real: app.css, index e 25-dash-macro.js; NAVIGATION-HIERARCHY e suíte Dashboard. Hashes das fontes no registro externo. Capturas fornecidas são referência anatômica, sem incorporar dados/ativos pessoais ou financeiros da FxPro. Benefício esperado é separação e leitura visual; nenhuma medição de usabilidade/performance alegada. A12 parcial, OPEN-05/V11/FCR/FEO, AUD-05/P2 e dívidas anteriores permanecem.
