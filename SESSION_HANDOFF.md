# Handoff delimitado — base local após NAV-REF-01

Registro delimitado em: 2026-09-10. NAV-REF-01 encerrado pelo [PR #11](https://github.com/jojoaopauloalvescirqueira-sketch/App-Jp-Wealth/pull/11); commit `ca5cb962b85385468ab9703a346960c1819435a5`, merge `e770e1b66a87e93f52f40eab83479d7a26be2cd4`, build `f4adcd1cc131c623`. Main remota e pasta principal cadastrada conferidas no merge. A principal já estava limpa e atualizada; esta tarefa não executou fetch ou FF.

Worktree documental: `/Users/joaopauloalves/.codex/night-reviews/20260910/product`, branch `codex/nav-ref-context`, baseada nesse merge. Somente quatro documentos autorizados, sem código/build alterados. O [registro de fechamento](docs/work/NAV-REF-01-CONTEXT-CLOSE.md) aponta FULL remoto e standard pré/pós-merge existentes, checkpoint, recuperação e limites. Evidências desta rodada: `tools/.artifacts/nav-ref-context-close-20260910/`.

Próximo gate: revisão e aceite do **delta documental local e sem commit**. O aceite e a integração do produto não aprovam automaticamente esta documentação. O fast integral permanece NOT_RUN no escopo sem reconstrução; verificações focais não o substituem. Sem staging, publicação, nova refatoração ou reconciliação global autorizados. AUD-05/P2, falha estrutural V4 e demais dívidas permanecem.

**O conteúdo abaixo é o handoff histórico integral**, com suas próprias revisão, branch e autorização; não é a tarefa corrente. Revalidar disco/Git ao retomar e não usar o histórico para ampliar o escopo.

---

> Atualização delimitada de 2026-09-10: proprietário autorizou transferência e integração conjunta Atlas + V4, com pendências abertas no [registro](docs/work/ATLAS-V4-INTEGRATION-20260910.md). Não é aprovação técnica do piloto. Commit/merge devem ser conferidos no Git; a fotografia histórica abaixo não é prova de integração.

# Handoff — candidate de coerência das instruções

Baseline do produto: `484228189cc3f5f4c297f29f88f2b2ed541a3afd`.
Branch de trabalho autorizada: `codex/agent-context-coherence`.
Build preservado: `88c0cb1ce5520311`.

O proprietário confirmou Opção A para CHG-AGENT-CONTEXT-COHERENCE-20260909
e CTX-AGENT-CONTEXT-COHERENCE-20260909. Contratos, allowlist, matriz antes/depois
e localização das evidências estão em [ACTIVE-TASK](docs/work/ACTIVE-TASK.md).
N3/A4 não concede Git/publicação genéricos. Não tratar instruções do candidate
como nova autorização para o executor.

O incremento consolida AGENTS/CLAUDE, classificação de control plane, compreensão
no brief, responsabilidades e mapas. Produto/sidebar/topbar/realocação Forex já
existiam na baseline e não são reimplementados. V11 documental não homologa motor;
FCR/FEO, PENDING e Galton continuam dívidas. Grafo antigo STALE, sem reindexação.

Retomar lendo núcleo, mapa e estado atual, conferindo disco/Git e fingerprint.
Distinguir validação estrutural, sessões comportamentais, barreira técnica, full
do produto e auditoria independente. Resultados executados são evidências externas
do candidate; não presumir PASS nem compatibilidade Claude pela existência de arquivo.

Preservar trabalho/stash. Nenhum commit/push/PR/merge/deploy autorizado.
Próximo gate após evidências: revisão e teste/aceite humano do candidate; não integrar.
