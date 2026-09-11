## Recorte local — campanha de refatoração 20260910

Esta seção representa somente a branch `codex/refactor-campaign-20260910`,
base `e770e1b66a87e93f52f40eab83479d7a26be2cd4`, build local `e5caefeada66ab35`.
Quatro lotes N1 foram implementados: protocolo inline de PF, rótulos cadastrais
Alladin, seleção da busca de Configurações e ativação visual do overview FX.
A caracterização fixada na baseline e reaplicada produziu 93 observações idênticas
(PF58, Alladin7, Configurações10, FX18); não é prova de integração dos consumidores.
O registro [da campanha](../work/REFACTOR-CAMPAIGN-20260910.md) define escopo, fontes, limites e recuperação.
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

> Atualização delimitada de 2026-09-10: proprietário autorizou transferência e integração conjunta Atlas + V4, com pendências abertas no [registro](../work/ATLAS-V4-INTEGRATION-20260910.md). Não é aprovação técnica do piloto. Commit/merge devem ser conferidos no Git; a fotografia histórica abaixo não é prova de integração.

# Estado atual — produto integrado e candidate de instruções

Classe M1. Data da fotografia: 2026-09-09
last_verified: 2026-09-09
Source revision representada: `484228189cc3f5f4c297f29f88f2b2ed541a3afd`

A revisão acima identifica o **produto integrado examinado**, não um commit novo.
O delta de instruções/contexto está sem commit em `codex/agent-context-coherence`,
sob CHG/CTX identificados em [ACTIVE-TASK](../work/ACTIVE-TASK.md).
Esta fotografia não antecipa validação, aceite ou integração desse delta.
A autorização vigente limita-se ao incremento confirmado pela Opção A.

## Produto comprovado por leitura na baseline

- Build `88c0cb1ce5520311`; 78 scripts clássicos na mesma ordem do manifest.
- Navegação lateral padrão e composição superior opcional no Editor integradas
  pelo PR #6, merge `9094ab342f7506c64d6052bdcc4f65f7c10b6b73`, ancestral da revisão.
- Dashboard mantém resumos superiores e “Sistema e atalhos”; operação, onboarding,
  Estado Operacional, VRM e calendário ficam em Forex > Visão Geral.
- Preferências de layout v6 e escolha lateral/superior permanecem contratos de
  apresentação; esta tarefa não altera código, schema ou armazenamento.
- Research entrega Calendário, NoCoda e Pivots; quatro áreas permanecem placeholders.
- Finanças Pessoais mantém orçamento, dívidas, comparação e cenários.
- Alladin entrega cadastro, ledger/estorno, caixa e quantidade de posições;
  não entrega valuation, cost basis, performance ou patrimônio consolidado completo.
- Finalidades/contratos atuais: [PROJECT-CONTEXT](PROJECT-CONTEXT.md),
  [CONTEXT-MAP](CONTEXT-MAP.md) e [CODE-MAP](../architecture/CODE-MAP.md).

## Invariantes e dívidas preservadas

V11 é adoção documental. PDF, Anexo, leitor e consentimento não são alterados.
Motor financeiro quadrifásico permanece legado; FCR/FEO e PENDING não foram
arbitrados. Fórmulas, schema, migração, persistência e dados operacionais estão
fora desta mudança. A intermitência histórica Galton permanece registrada;
PASS isolado não encerra essa dívida.

README, QUALITY-GATES e SECURITY-MODEL contêm trechos/contagens anteriores;
não integram a allowlist desta rodada. Para localização/capacidade atual usar os
contratos e mapas examinados; para comandos/contagens efetivamente executados,
usar o gate e sua evidência. Não promover esses trechos antigos a estado vigente.
O texto auxiliar do calendário que ainda cita Dashboard também permanece dívida
de produto fora do escopo.

## Contexto e recuperação

AGENTIC IMPACT CHECK: AGENTIC IMPACT DETECTED — delta crítico de control plane.
AGENTS/CLAUDE, roteamento, brief e mapas são consumidores afetados; o CHG permite
reconciliação delimitada. As skills importadas congeladas e o Harness mestre
permanecem intactos; referências às fontes não autorizam editar os consumidores.

O grafo existente representa `a3052d2314ab3f8c01b1cff0a1d08790cd416c6d`, anterior
à navegação atual: **STALE**. Nenhuma reindexação ou consulta que grave metadados
está autorizada. Recuperação direta em arquivos atuais continua disponível.
Não declarar SYSTEM RECONCILED nem carregamento universal sem prova dos consumidores.

## Evidências e limites deste checkpoint

A entrada foi revalidada: main/HEAD esperados, uma worktree, árvore limpa e
stash `bfdb323f05f0df27c79fd11cb18d64352a5c5194` preservado. Só a criação/uso da
branch indicada foi autorizada como mutação Git; commit/push/PR/merge/deploy não.

Validação da implementação é registrada em evidências sintéticas isoladas
referidas na tarefa ativa, identificadas por SHA/fingerprint. Este arquivo não
transporta PASS de testes locais/CI de entregas anteriores. Testes das instruções,
full do produto, auditoria e aceite humano têm alcances distintos. Nenhuma
publicação é autorizada por este checkpoint.
