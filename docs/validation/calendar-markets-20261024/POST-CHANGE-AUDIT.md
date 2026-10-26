# Auditoria pós-alteração — Calendário e Mercados

Candidate local: `codex/calendario-mercados-20261024`, HEAD/base `a4bf278cd4dc38bbaa5b905ed17a79e33684fb67`, build `3a9f6157481ae050`.

O delta foi revisado por composição/navegação, resumo/controlador, apresentação, fontes/artefatos e testes. Os contratos PRODUCT/TESTS separam implementação N1 e verificadores N3 autorizados. A revisão independente está nos relatórios desta pasta.

| Fronteira | Evidência |
|---|---|
| Produto | Sete fontes HTML/CSS/JS de apresentação/navegação; uma instância e consulta compartilhada; catálogo/globo/motor preservados |
| Financeiro e persistência | Escritores, contas, regras, schemas, backup e dados reais sem alteração; invariantes sintéticos nos testes |
| Entrada/saída | Textos de catálogo/erro via nós e textContent; nenhuma nova fonte de rede, persistência, dependência ou execução externa |
| Distribuição | Gerador oficial; hashes do manifesto sem reordenação; oito envelopes alteram somente buildID; portátil e distribuições reais testados |
| Juízes | Quatro testes legados substituem somente o submenu superado; novo focal executado explicitamente, sem mudar runner/CI/gates |
| Resultado atual | FULL102/102 PASS; UI370/370 PASS; focal21/21 PASS; performance isolada PASS; 481inputs sem drift |

`git diff --check` PASS. Status e diff integral conferidos; patch de trabalho preservado fora do corpus em `/private/tmp/jpw-calendar-markets-20261024/final-change.diff` (somente arquivos rastreados). Novos arquivos de plano, CHG, evidência e focal constam no inventário da tarefa; fontes do focal têm fingerprint nos recibos.

Primeira execução completa permanece 100PASS/2PRODUCT_FAIL brutos por expectativas obsoletas; a segunda foi interrompida após ENVIRONMENT_ERROR de tempo e não tem PASS integral. A terceira fornece o resultado final atual. As tentativas não foram apagadas ou reescritas.

Limites abertos: recompilação da fidelidade original do globo em ENVIRONMENT_ERROR por ferramentas antigas ausentes, sem alteração do bundle; Safari, leitor de tela, toque físico, compreensão e preferência visual humana não demonstrados. Teste humano e autorização Git/publicação são gates posteriores. Nenhum commit, merge, push, publicação ou exclusão foi executado.

AGENTIC IMPACT CHECK: AGENTIC IMPACT DETECTED. BASIS: a consolidação altera rota, registro de navegação, guia e contratos consumidos por agentes. Reconciliados contratos, tarefa ativa, brief e registro factual das cinco regressões; fontes normativas, AGENTS, skills, routing e gates permanecem intactos. Contextos oficiais antigos conservam validade histórica; não aprovam este candidato. INDEX NOT REQUIRED.

Rollback: reverter somente o delta desta tarefa sobre a base registrada e regenerar artefatos pelo processo oficial; não há dados persistidos a migrar. Nenhum comando de rollback foi executado.
