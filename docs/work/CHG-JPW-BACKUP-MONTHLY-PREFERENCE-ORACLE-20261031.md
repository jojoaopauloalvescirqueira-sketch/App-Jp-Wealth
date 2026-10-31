# CHG — oráculo de backup da preferência mensal — 31/10/2026

N3/control plane, A4 delimitado recebido do proprietário pelo coordenador nesta conversa: corrigir somente o oráculo obsoleto após o plano aprovado de pacote único/workspace3. Este documento registra a autorização, não a concede. Branch `codex/backup-unificado-20261031`, base `69b6cb677de2486be5c30681e4b2e02d4180d704`; alterações anteriores conhecidas preservadas. A rodada FULL da worktree foi interrompida pelo coordenador antes da edição, com recibo próprio. Sem commit, merge, push, publicação, mudança de produto ou do runner.

## Compreensão e fontes

O JP Wealth preserva dados financeiros confirmados e suas cópias recuperáveis. O backup aprovado agora transporta preferências separadas dos fatos. Planejamento produz a preferência visual mensal; o core workspace é seu transportador, sem torná-la fato ou lançamento financeiro. O teste anterior exigia ausência da chave em todo JSON e contradizia a inclusão explícita aprovada em workspace3. O comportamento do produto já atendia ao requisito novo; somente teste/documentação são alterados.

Fontes examinadas: `docs/architecture/COMPLETE-BACKUP.md` (seção atual workspace3, inclusão da preferência mensal); `docs/architecture/PLANNING.md` (cláusula histórica fora de S e Backup Completo, substituída exclusivamente quanto ao backup); `docs/governance/UI-VISUAL-QUALITY.md` (casos/2px/44px/zoom nativo200%); `CHG-JPW-PLANNING-INLINE-TESTS-20261021.md` (oráculos e contraprovas permanentes); `tools/planning_monthly_inline_test.py` (`backup_isolation`, `preferences`, contraprova de preferência); exportador real `dgBuildBackupBlob` e allowlist workspace3. Hashes/preimagens constam no manifesto da rodada4, fora do repositório.

O recibo anterior executou os413IDs com source_unchanged:true e classificou somente `inline-preferences-isolation` e `inline-counterproof-preference-finance-backup` como PRODUCT_FAIL pela exclusão total obsoleta. Esse resultado bruto permanece preservado. Não é falha financeira corrigida, nem PASS histórico reaproveitado.

## Delta mínimo e critérios

Arquivos permitidos: `tools/planning_monthly_inline_test.py`, este CHG, atualização factual em `docs/architecture/PLANNING.md` e nova entrada em `tools/regression-memory.json`. Proibidos: produto, cálculos/escritores, stores, AGENTS, gates/quality_gate, fontes de outras branches, quantidade/identidade de casos e tolerâncias. O mesmo oráculo deve aceitar a preferência serializada real somente em `workspace.preferences`, com valor raw confirmado exato ou null explícito quando ausente; deve recusá-la em estado financeiro, rascunhos e qualquer outro local, assim como ausência do slot, valor diferente ou objeto em lugar do raw.

A contraprova existente conserva a contaminação financeira sintética e seu oráculo de igualdade dos fatos. Acrescenta seis mutações da serialização real: estado, rascunhos, inscrição na raiz, slot ausente, valor divergente e tipo divergente. Positivo antes/depois e ausência de novas gravações financeiras continuam obrigatórios. As mutações são subcasos dentro do mesmo ID, sem aumentar ou reduzir os413casos ou alterar2px,44px e zoom nativo200%.

## Evidência, revisão e rollback

RED: o oráculo anterior rejeita um snapshot workspace3 válido com a preferência exata; recibo UI anterior contém as duas falhas. GREEN: o mesmo ponto de entrada aceita raw/null válidos e recusa as seis mutações; o focal inline integral executa regressões/contraprovas com IDs preservados. Os recibos devem registrar fonte/teste/configuração, exit code e hashes. Depois do congelamento: revisão independente somente leitura, UI completo fresco e FULL integrado pelo coordenador; nenhum resultado é presumido antes da execução. Teste humano/aceite permanecem separados.

Rollback limitado: restaurar preimagem dos quatro arquivos desta rodada; não alterar dados, stores ou código de produto. Um rollback do oráculo repõe a incompatibilidade conhecida com o contrato workspace3, que deve continuar explícita. Nenhuma dependência instalada ou dado real acessado.
