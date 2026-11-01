# Orçamento da matriz visual — 01/11/2026

N3/control plane com novo A4 específico: “Aprovar 1.800s apenas na matriz visual”, question call_431e8f0401b7437cb1db8b8aa1cacfad. Aprovação anterior preservava900; não foi reutilizada para ampliar este recurso. Branchcodex/backup-unificado-20261031,base21db450. Mantido waiver humano dos contratos versionados para esta implementação, sem reconstruir Harness externo.

A matriz acumulada de413casos deve concluir inteira; não basta passar um subconjunto. LinuxFULL anterior114PASS/2PRODUCT_FAIL interrompeu a matriz aos900.015s, contendo também falha visual real; as falhas de fonte/scroll são corrigidas em deltaN1 separado. Não se presume que o timeout sozinho explique as falhas.

Aplicação literal do patch revisado: somente run_check(name='ui-visual-quality') recebe1800s; todos outros nomes recebem900s. Mensagem de timeout reporta o budget real. Job global90min e retenção7dias preservados; nativezoom200%,2px/alvos44px, oráculos, casos, comandos, memberships e classificação não mudam. Nenhum efeito em dados, motor, persistência ou runtime do app.

AntesSHA25651fae2e0a9b25972d68c9d8e70023d28536fb4f590e386e8a518eecc568ab84d; depois75e0eaf082f2fe99ea3f6f0a87a2c67340e76f578fa4e8aafbe0032fb838a0b4. Revisão independente estática aprovou esse fingerprint sem Critical/Important. Prova controlada executa o run_check real com spy de subprocesso:117nomes (116existentes+unknown); original registra o único mismatch UI900 contra1800; proposta nenhum mismatch e duas mensagens TimeoutExpired corretas. Não é execução de browser, wall-clock1800 ou aprovação Linux. Primeira falha de setup do probe foi corrigida e preservada externamente; não foi contada comoRED.

Escopo: tools/quality_gate.py, esteCHG, recibos, memória/contexto focal. FonteAGENTS e CHANGE-PROCESS classificam gatesN3/A4; QUALITY-GATES exigeFull. Testes acumulados existentes continuam sendo a proteção end-to-end: matriz integral, inclusive no Linux, sem skip. Probe controlado é evidência de engenharia adicional, não nova entrada no runner116. Critério de promoção: FULL local e Linux do SHA final, todos os116checks e413casos executados/aprovados, incluindo orçamento e fontes auditados. Não garantir conclusão dentro90min antes de executá-la.

Rollback: reverter somente este budget/diagnóstico; preservar dados e primeiras falhas. Securityreview: nenhum segredo, permissões, pins, scripts remotos ou dependência nova. Git/publicação continuam gates separados com autorização anterior; sem site/exclusões. AGENTIC IMPACT CHECK: AGENTIC IMPACT DETECTED. BASIS: orçamento do gate consumido pelo pipeline muda, portanto tarefa/estado/CHG/memória recebem registro focal. AGENTS, routing, skills, norma, índices e toda matriz de comandos permanecem; sem reconciliação global/reindex.


Focais concluídos: revisão tipográfica1caso/6cenáriosPASS, Capitalmodoall9PASS/0FAIL(inclui48matrizoriginal), fontes estáveis. Rebuild oficial executado, buildce3e56f9e69fc5cc. Revisão independente semCritical/Important, única frase documental stale corrigida. Nãoequivale aFULLfinal/LINUXPASS; próximo gate completo em candidate congelado.


FULL local final:116/116PASS eUI413/413PASS, fontes estáveis, builde65a0f5397d4553c. Recibos em docs/validation/ci-matrix-budget-20261101/. Resultado antigoLinux114/2 preservado em validation/ui-font-geometry. Próximo gate: LinuxFULL/Host no SHA final antes do merge; não fechar incidenteLinux por prova local.
