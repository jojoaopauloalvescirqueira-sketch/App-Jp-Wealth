# Correção dos PRODUCT_FAIL pendentes — 2026-10-06

Pedido humano atual: “Solucione todos os product fail pendentes”. Candidate isolado na cópia jpw-product-fail-repair-20261006/candidate, branch herdada codex/saving-reliability-20261006, HEAD ac3a2faffeb398357ff105adbf1d47f70ca309bd. Base 1db5b703ca56d26c, 749 arquivos/fingerprint ce450e0ba50b51388794e52a0840c830f3934b0bbf40d1945fd3701f8becfdb3 preservada, snapshot e recibos anteriores conservados. Preflight --allow-dirty somente após inventário dos deltas herdados. SOURCE REVISION UNKNOWN no contexto histórico permanece, não usado como realidade atual.

O objetivo é remover causas reproduzidas nas cinco falhas gerais e duas MT5 host; investigar intermitência do import e falha do executor de timeout. Não haverá alteração de norma/fórmulas, dados reais, configuração global, execução MT5, EX5, commit, branch, push, merge ou publicação.

## Produto N2/A3 e distribuição N1/A2
Autorização explícita de implementação das correções necessárias pelo proprietário, limitada aos achados. Mantidos CONFIRMED/REFUSED/UNKNOWN, integridade/limites dos backups, recusa de parcial, versões/fontes existentes e biblioteca oficial. Corrigir runtime apenas se contraprova mostrar defeito real. Rebuild oficial; nenhuma normalização em dados do usuário. Matriz antes/depois e rollback nas evidências externas. Full e focais dos bytes finais, prontidão nativa separada.

## Defeito real encontrado na contraprova de corrupção
Envelope accountContexts de versão futura e sem accounts provocava TypeError em operationalSelection antes da barreira de schema; accountProfileContext também dereferenciava antes da validação. Correção delimitada em 00-forex-state.js: validar suporte antes de consultar esses membros e devolver indisponibilidade, sem substituir, normalizar ou salvar o envelope. Fórmulas, valores, identidade persistida e comandos financeiros continuam protegidos. Probe do envelope incompleto e regressões de estado/leitura/ledger devem conferir RAM e gravações, além das versões completas já testadas. Hashes, reconstrução oficial e gates finais serão novos; recibos anteriores permanecem históricos.

## Corrida real na inicialização
Sete cargas sem atraso não falharam; três cargas com latência de 1,2 s somente na resposta de 07-reserve-requirements reproduziram reserveRequirementsCalc ausente no timer de onboarding. O HTTP retornou 200 e os bytes eram corretos. Corrigir a ordem em index.html e no manifesto: carregar reservas após o engine e antes de onboarding/boot. Preservar bytes dos cálculos, timer e verificações de erros. Rebuild oficial para portátil; contraprova com atraso, bootstrap e backup integral, seguida de nova congelação e gates. Os 8 PRODUCT_FAIL da rodada 4fdc2ca40d1ea69a ficam preservados, sem reclassificação.
