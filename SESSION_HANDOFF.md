# Handoff — adoção documental V11 isolada

M4. Fotografia de2026-09-08; expira com drift de source ou alteração da autorização.
Branch `codex/statute-v11-documental`, base02d3a6991fe82569c1fe232722d9b8566fc62ecd.
Origem `codex/dashboard-complete` permanece intacta; não limpar, resetar ou sobrescrever.

A nova branch contém somente o pacote documental V11, leitor, downloads/cache,
consentimento por versão e testes necessários. Não contém as melhorias locais
anteriores do Dashboard; o Dashboard já integrado na base foi preservado.
PDF e Anexo têm bytes originais. Motor legado, conflitos FCR/FEO e PENDING continuam
explicitamente registrados. Galton/finalização não foram alterados.

Checkpoint de testes: build 1ee88bab37539798, full 55/55 PASS, focal documental PASS
e fast final 4/4. Freeze e auditoria independente têm registros externos posteriores.

Candidate e evidências próprias: [auditoria](docs/audit/STATUTE-V11-ISOLATION-2026-09-08.md).
Contrato e limites: [ACTIVE-TASK](docs/work/ACTIVE-TASK.md).
Estado: [CURRENT-STATE](docs/governance/CURRENT-STATE.md).

Commit único/push da branch/Draft PR são condicionados aos testes e auditoria.
O proprietário confirmou Netlify ainda não utilizado. Sem merge, sem marcar PR
pronto e sem deploy. Não declarar baseline operacional V11 pronta. IDs finais
de Git/PR devem ser consultados no histórico e no relatório da entrega, separados
do checkpoint pré-commit deste documento.
