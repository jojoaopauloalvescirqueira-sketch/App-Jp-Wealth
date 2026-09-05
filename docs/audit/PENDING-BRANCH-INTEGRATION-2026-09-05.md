# Auditoria de integração seletiva de branches pendentes — 2026-09-05

## Escopo e decisão

Base `c9104b167944e52bb9b71a7439f1573a053704bb`. Autorização humana delimitada:
integrar Dashboard Macro (`3502331`, `03eda18`) e avaliar o workflow da PR #1
(`045c264`), com commits locais; sem `push`, deploy, exclusão ou merge em
`main`. A norma V11 e a Visão Geral antiga de Finanças Pessoais foram excluídas.

## Integração

- `3502331` → `ce225c4`; conflito apenas em `ACTIVE-TASK.md`, resolvido mantendo
  o contrato de integração atual.
- `03eda18` → `f752776`; mesmo conflito documental e mesma resolução.
- `045c264` não reaplicado: seu arquivo é subconjunto estrito do workflow atual,
  que já possui todos os passos e acrescenta gatilho em `main`, `fetch-depth: 0`
  e `cache-dependency-path`. Reaplicá-lo seria regressão.

## Invariantes e impacto

- N1 + N0-D; nenhum domínio financeiro, fórmula, schema ou persistência mudou.
- `src/js/manifest.json` recebeu apenas o módulo clássico autorizado do
  Dashboard; ordem validada pelo gate.
- `dist/` foi regenerado por `tools/rebuild_monolith.py` e a reprodução passou.
- Segurança: nenhum input, endpoint, dependência, segredo, credencial ou writer
  de storage foi introduzido; os cards apenas consomem fronteiras existentes.

`AGENTIC IMPACT CHECK: AGENTIC IMPACT DETECTED`

`BASIS:` a integração altera a superfície de Dashboard, o manifest, a composição
dos tiers e representações de estado consumidas por agentes. Foram examinados
AGENTS, skills/routing, contexto operacional, arquitetura, contratos, gate,
manifest, changelog e handoff. Ação local foi necessária em `CURRENT-STATE`,
`ACTIVE-TASK`, changelog, handoff e nesta auditoria; agentes, skills, routing,
autoridade, contratos de dados e arquitetura de domínio ficaram
`NOT_AFFECTED / LOCAL ACTION: NOT_REQUIRED`.

## Evidência

- `python tools/dashboard_macro_test.py` (Python 3.12.14): `PASS`.
- `python tools/quality_gate.py --tier full` (Python 3.12.14): `PASS=54`;
  `PRODUCT_FAIL=0`, `TEST_HARNESS_FAIL=0`, `ENVIRONMENT_ERROR=0`,
  `BASELINE_FAIL=0`, `NOT_RUN=0`.
- Navegador real, origem limpa: desktop escuro e mobile `390×844` nos temas
  escuro e claro; grade 2×2/coluna única, conteúdo sem sobreposição e navegação
  para `Forex > Visão Geral` com gráficos, metodologia e atalhos confirmados.
- Tentativa anterior em Python 3.9: `ENVIRONMENT_ERROR` — o runtime não aceita
  `tarfile.extractall(filter=...)`; repetição isolada e gate completo no Python
  3.12 exigido pelo CI passaram.

## Risco residual e próximo gate

Não houve execução remota de CI porque não houve `push`. O candidato permanece
em branch isolada. Próximo gate humano: merge local em `main`; publicação e
limpeza de branches continuam decisões separadas.
