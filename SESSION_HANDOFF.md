## Recorte local — campanha de refatoração 20260910

Esta seção representa somente a branch `codex/refactor-campaign-20260910`,
base `e770e1b66a87e93f52f40eab83479d7a26be2cd4`, build local `e5caefeada66ab35`.
Quatro lotes N1 foram implementados: protocolo inline de PF, rótulos cadastrais
Alladin, seleção da busca de Configurações e ativação visual do overview FX.
A caracterização fixada na baseline e reaplicada produziu 93 observações idênticas
(PF58, Alladin7, Configurações10, FX18); não é prova de integração dos consumidores.
O registro [da campanha](docs/work/REFACTOR-CAMPAIGN-20260910.md) define escopo, fontes, limites e recuperação.
Gates finais, auditoria do conjunto e recuperação serão registrados fora dos inputs
congelados em `/Users/joaopauloalves/.codex/refactor-campaigns/20260910/evidence`; consulte seus recibos, não antecipe aprovação por este texto.

NAV-REF-01 já integra a base via PR #11; não foi refeito. O candidate documental
`8bd6d028…85e098c` permanece separado em `codex/nav-ref-context`; seu fast foi
verificado em cópia fiel (4/4 PASS), sem aceite ou integração. Main, stash e outras
worktrees são alvos protegidos. Nenhum commit/publicação autorizado nesta campanha.
AUD-05/P2, estrutural V4, Galton, FCR/FEO e demais dívidas anteriores continuam abertas.
Este recorte não avança a revisão global/last_verified abaixo, não atualiza índices,
não homologou fórmulas, nem registra teste manual, aceite ou integração.

---

Fotografia anterior preservada integralmente; suas branches, permissões e resultados
pertencem ao período indicado, não à autorização desta campanha.

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
