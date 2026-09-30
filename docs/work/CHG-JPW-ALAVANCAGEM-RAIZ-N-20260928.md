# CHG-JPW-ALAVANCAGEM-RAIZ-N-20260928 — MT5 1.4.0

```yaml
schema: jp-harness/chg/v1
change_id: CHG-JPW-ALAVANCAGEM-RAIZ-N-20260928
status: approved_for_local_implementation
objective: Acrescentar o diagnóstico Raiz N ao indicador MT5 existente, com cenário declarado persistente e detalhes sob demanda no próprio gráfico.
risk_level: N3
authority_required: A4
target:
  root: /private/tmp/jpw-alavancagem-atual-20260926
  branch: codex/jpw-alavancagem-atual-20260926
  baseline_sha: f5145b25e86af6b4ccbfef847cba0d84d74e7c8a
  derived_from: jpw-alavancagem-atual-20260928-r7
  r7_build: 1ad26bf632734503
  r7_fingerprint: 456a5f807314ef70c54109fda1873e86d6aa0ba8c2e90a5a255338a37f3a81d2
scope:
  allowed_areas: [this CHG and ACTIVE-TASK, Raiz N MQL5 core/store/tests, existing MT5 indicator, tool README and package manifest, existing tool page and its focal tests, official generated ZIP/portable/cache, same external canonical tool specification, external evidence and audit]
  forbidden_areas: [docs/normative/, docs/decisions/, skills/, Harness, gates, tools/quality_gate.py, .github/, src/js/00-core/, src/js/10-domain/, existing MDD/USC/Genesis file formats]
  allowed_actions: [bounded local implementation, synthetic tests, official generation, isolated native validation if available, candidate freeze, independent audit]
  forbidden_actions: [real-account access by agent, operational MT5 installation, trading, modification of orders or stops, commit, push, merge, deploy, publication, r7 snapshot rewrite]
data:
  test_policy: synthetic_only
  persistence: new local MT5 Raiz N record, separated from MDD, Genesis and USC profile
  browser_state_change: forbidden
acceptance_criteria:
  - D_percent = 100 * ATR / P0 * sqrt(N) * F and D_price = ATR * sqrt(N) * F, with invalid or absent inputs unavailable rather than zero.
  - ATR source and time, H4 55-period variant, P0, N and F justifications remain explicit; no future bar enters a retrospective scenario.
  - One principal scenario per exact account/installation/symbol context is persistent; confirmation never rewrites its initial inputs.
  - The fifth compact gray line remains visible, and Apply/Cancel in an indicator-owned detail panel cannot alter the four existing metrics.
  - Explicit, verified position binding is needed for SL comparison; the diagnosis never trades or changes a stop or risk gate.
  - Site, README, manifest, source ZIP and generated derivatives identify the same version, without exporting account records.
approved_tests: [synthetic MQL5 math and persistence, focused panel/package/page/structure, full quality gate with raw classification, isolated native compile/run if available, independent adversarial audit]
rollback:
  source: Restore the externally frozen 45-file r7 snapshot by fingerprint; do not rewrite its evidence.
  data: Do not delete MDD/Genesis/USC records; Raiz N records are separate and remain available for later recovery.
  verification: Compare r7 hashes and confirm no account record or unverified EX5 entered the package.
approved_by: Proprietário, pedido expresso nesta conversa para implementar integralmente o plano JPW Alavancagem Atual 1.4.0.
approved_at: 2026-09-28 America/Sao_Paulo
```

## Task brief e fontes

O JP Wealth apoia preservação de capital e disciplina operacional; este indicador MT5 é informativo, não motor de admissão normativa nem executor de ordens. A ferramenta distribui fontes e instruções pelo site, mas só o MT5 calcula e guarda cenários locais. O delta autorizado acrescenta um diagnóstico de distância baseado em ATR, sem alterar nocional/equity, flutuante/saldo, DD/saldo, MDD observado, perfil USC ou a referência Gênese.

Fonte primária: `ARTIGO 9 - MODELO RAIZ N JP WEALTH.pdf`, SHA-256 `f32f7d36f27ea593debc375458ae1536ad7b8f679858d71a832fdf5a0831e20b`, pp. 2–6 (fórmulas e ATR), 9–13 (N H4 e exemplos), 13–15 (diagnóstico sem dimensionamento), 16–24 (limitações). O artigo não homologa N/F universais nem uma escolha única de suavização do ATR. A convenção de usar a última barra H4 concluída antes do instante declarado é engenharia identificada, não nova norma. `docs/normative/` e o catálogo Forex permanecem intactos; P-20/P-21/P-22 não recebem nova vigência ou veto.

Outras fontes: `AGENTS.md`, `README.md`, `docs/governance/CONTEXT-MAP.md`, `PROJECT-CONTEXT.md`, `CURRENT-STATE.md`, `FOREX-V11-ENGINE.md`, `CHANGE-PROCESS.md`, Harness externo SHA-256 `b5680c22e44cf3f4a5cd3aa5deeb96f8b65c7908f14543e8c5d7f0c2f4e17b95`, especificação canônica externa SHA-256 `6211682bcaf9d2af874b520f1d44133a1842c41834a52360e1be32c89d68f7f6` e `CANDIDATE.json` r7. A revisão r7 foi conferida em 45/45 arquivos; branch e HEAD são os indicados, staging vazio. Todas as entradas atuais de `git status --porcelain -uall` pertencem ao inventário r7. `agent_preflight.py --mode audit` passou; o modo edit recusou a árvore não commitada, e `--mode edit --allow-dirty` passou após essa conferência explícita de autoria/escopo. O aviso de frescor do contexto é histórico, não evidência de alteração desconhecida nesta worktree.

O r7 permanece `AUDIT_FAIL/BLOCKED`: full 53 PASS / 4 PRODUCT_FAIL, compilação e execução nativas NOT_RUN. A nova função não herda resultados favoráveis nem resolve por inferência seus bloqueios. Resultados do novo candidate serão classificados e preservados separadamente.

## Contrato e riscos

Cada cenário congela a versão diagnóstica de engenharia JPW-RAIZ-N/1.0, separada da versão do schema de armazenamento. Os nomes de arquivo usam prefixos curtos de hashes; a identidade completa continua validada dentro do conteúdo e colisões falham fechadas.

`D_percent` é expresso em pontos percentuais: `2` representa 2%. `D_price` está na unidade de preço do símbolo; não recebe conversão USC. P0/ATR/F finitos e positivos e N inteiro H4 positivo são obrigatórios. O cenário inicial confirmado é imutável; novo cenário tem ID próprio e comparação posterior não o altera. Registro local Raiz N é versionado, recuperável e separado dos formatos de MDD/Genesis/USC. Um conflito de gravação, corrupção, conta trocada ou histórico H4 insuficiente falha fechado e preserva os dados anteriores.

O painel do indicador acrescenta somente uma quinta linha e uma janela interna temporária para detalhes/edição explícita. Sem dados, mantém `N/D` com motivo. Vínculo com posição/SL requer escolha expressa, símbolo e direção coerentes; a distância atual de mercado ao SL Gênese é outra métrica. Nenhum valor Raiz N muda SL, lote, ordem, admissão, Estatuto ou política Forex.

AGENTIC IMPACT CHECK: AGENTIC IMPACT DETECTED. O guia público, especificação canônica, manifesto e ACTIVE-TASK são representações consumíveis por agentes. A implementação deverá reconciliar esses artefatos autorizados; não editar skill, Harness, routing ou documentos normativos por consequência.
