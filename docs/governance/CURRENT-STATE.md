# Estado atual — candidate documental V11 isolado

Classe M1. Data da fotografia: 2026-09-08
last_verified: 2026-09-08
Source revision representada: `02d3a6991fe82569c1fe232722d9b8566fc62ecd`

A revisão acima identifica a base desta branch; o diff documental será identificado
por build/fingerprint na auditoria. Esta fotografia descreve o checkpoint local
da mudança, sem declarar publicação ou conformidade financeira. IDs posteriores
de commit/PR são verificáveis no histórico da branch e no relatório de entrega.

## Identidade e escopo

- Branch: `codex/statute-v11-documental`, criada da revisão exata acima.
- Origem `codex/dashboard-complete` preservada integralmente, somente leitura.
- Incluídos somente V11/Anexo, consulta/cache/download, consentimento por versão,
  referências e testes documentais. Os cálculos e a interface Dashboard da base
  permanecem; as melhorias locais anteriores do Dashboard foram excluídas.
- Pipeline: 78 scripts clássicos na ordem original; teste documental adicional,
  resultando em 44 verificações standard e 55 full, além de 4 fast.
- Build `1ee88bab37539798`: full 55/55 PASS, focal documental PASS e fast final 4/4.
  Identidade, evidências próprias e limites do checkpoint pré-freeze na
  [auditoria](../audit/STATUTE-V11-ISOLATION-2026-09-08.md).

## Normas

[Estatuto V11 e Anexo](../normative/README.md) foram copiados byte-idênticos às
fontes fornecidas. Vinte documentos anteriores foram removidos somente nesta
worktree e são recuperáveis pelos blobs/hash registrados na auditoria.
O leitor e os originais funcionam por mecanismos de consulta, sem alterar regras.
O aceite antigo conserva sua identificação: uma versão nova exige ato explícito.

FCR/FEO divergem entre PDF e Anexo; a operação de cópia não resolve a precedência
material desses trechos. CANONICAL não significa HOMOLOGATED e PENDING não admite
fallback zero. O motor financeiro permanece legado: fases/DD, admissão/TRA,
satélites, VRM, stop, quarentena e reservas não foram adaptados. Os ADRs anteriores
são propostas históricas a reavaliar, sem aprovação inferida.

## Git, topologia e limites

O proprietário confirmou que Netlify ainda não está em uso. O repositório contém
configuração declarativa; a única automação versionada é de qualidade. Site,
ambiente e SHA publicada não foram identificados; default branch não prova produção.
Está autorizado um único commit, push somente desta branch e Draft PR para main
apenas após os critérios e auditoria. Merge, marcar pronto e deploy são proibidos.

Falha intermitente anterior de Finalizar Sessão/Galton permanece documentada.
Não foi corrigida neste escopo e os resultados anteriores não validam esta branch.
Histórico anterior de estado permanece no Git da base, sem copiar contexto do
Dashboard para esta entrega. O próximo gate humano é revisão do Draft PR documental;
adequação financeira, resolução normativa, merge e deploy exigem trabalhos/atos próprios.
**Não READY_FOR_NEXT_DEVELOPMENT_CYCLE.**
