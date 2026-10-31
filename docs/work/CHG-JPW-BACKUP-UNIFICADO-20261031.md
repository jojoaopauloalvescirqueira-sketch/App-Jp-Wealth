# Backup unificado — autorização delimitada de 31/10/2026

Base `69b6cb677de2486be5c30681e4b2e02d4180d704`, branch `codex/backup-unificado-20261031`. Produto N2/A3 autorizado pelo proprietário no plano de quatro frentes; uso dos contratos versionados autorizado enquanto a fonte externa não está disponível na migração. Não altera autoridade, instruções ou gates. Sem commit/merge/push/publicação.

Objetivo: um pacote ZIP STORE com documento confirmado, preferências/progresso e originais PDF/HTML. Corrigir quatro famílias omitidas do workspace, preservar progresso legado opaco e manter importação JSON/ZIP de evidências legados. Hedge contém somente plano didático/progresso confirmado; nenhum comando de operação financeira.

Fontes: `docs/architecture/COMPLETE-BACKUP.md`, `DB-STORAGE-GOVERNANCE.md`, `STATE-SCHEMA.md`, `docs/recovery/DATA-RECOVERY.md`; código base do workspace, ledger e arquivo de evidências. O programa local mantém dados por origem; o pacote externo recuperável, e não o Git, protege esses dados.

Arquivos permitidos: workspace/evidence core, orquestração de backup no ledger, apresentação/inputs de backup, contrato, novos testes focais e memória factual. Gerados exclusivamente pelo gerador oficial. Preservar o escritor financeiro, epochs, locks, UNKNOWN, segredos excluídos, formatos legados, dados reais e todos os gates existentes.

Critérios: workspace3 inclui progresso Dante/Gêmeos/Correntes e preferências Mensal; ZIP168MiB/203entradas STORE; JSON32MiB, original32MiB, total128MiB/200originais, manifestos2MiB cada. Validar pacote inteiro antes de gravar; IDB aditivo transacional antes da adoção financeira; journal/falha parcial explícitos. Ausências de originais exigem confirmação, sem inventar cobertura.

Validação: regressão sintética RED/GREEN de omissões, roundtrip integrado com IndexedDB, limites/hash/caminhos, recusa/UNKNOWN/retomada; suítes existentes e FULL pelo coordenador no candidato integrado. Nada de testes em armazenamento real.

Rollback: preservar pacote e leitor compatível; reverter somente o delta de código autorizado sem apagar stores ou normalizar estado; workspace3 é recusado por versões antigas. Exportação/declaração de arquivo conferido permanecem gestos distintos.
