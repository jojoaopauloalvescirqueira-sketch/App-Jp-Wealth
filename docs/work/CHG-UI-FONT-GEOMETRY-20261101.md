# Geometria com fontes de fallback — 01/11/2026

Correção N1 de falhas visuais sob a solicitação vigente de continuar a entrega/CI. Branch codex/backup-unificado-20261031, base21db450, árvore limpa antes deste delta. RuntimeN3 anteriormente aprovado permanece; o orçamento específico de1800segundos recebeu novo A4 na conversa (call_431e8f0401b7437cb1db8b8aa1cacfad) e foi aplicado literalmente, em deltaN3 separado.

Responsabilidade: apresentação de Planejamento e Correntes de Capital. A confirmação deve focar seu título e mantê-lo completamente visível no painel e na viewport; texto do cabeçalho do campo deve caber sem overflow no zoom/largura aprovados. São regras de UI existentes, não novas regras financeiras.

LinuxFULL:114PASS/2PRODUCT_FAIL; Hedge/Management nativos corrigidos pelo runtime, UI900.015s e Capital390px/CSSzoom2 root155/scroll168 falham. Diagnóstico sintético Mac com Arial: mesma propriedade de Planejamento falha(bottom844.3125 em viewport844, limite844.25); campo root155/scroll158. Não se afirma que Arial seja a fonte efetiva do Linux nem que toda a falha UI seja lentidão.

Antes de alterar produto: ampliar fixtures tipográficas mantendo todas as assertivas/tolerâncias para reproduzir RED permanente. Intervenção proposta N1: alinhar o título de revisão ao centro do scroll em vez de nearest, e permitir quebra de palavras no cabeçalho do campo em containerestreito. Manter foco no título não interativo, confirmação deliberada, min44px, canvas mínimo, armazenamento, animação/lifecycle, fonte/cor e cálculos.

Arquivos: src/js/30-accounting/06-planning/03-ui.js apenas stageInline foco/scroll; src/styles/app.css apenas cabeçalho Capital estreito; tools/planning_monthly_inline_test.py e tools/capital_currents_browser_test.py apenas fixtures adicionais com oráculos existentes; derivados pelo tools/rebuild_monolith.py; CHG/recibos/memória/contexto focais. Source engine, params, política, schemas e dados não mudam. Nenhum dado real acessado; contextos descartáveis e escrita financeira monitorada.

Fontes: docs/governance/UI-VISUAL-QUALITY.md e contrato PLANNING.md (revisão visível/foco explícito), docs/architecture/CAPITAL-CURRENTS.md (canvas/controles e isolamento), implementações de stageInline/capital-field-header e testes existentes. Risco N1 sem persistência nova. Teste funcional permanece N1 conforme CHANGE-PROCESS, preservando os critérios de higher-level controls.

Verificação: RED das novas fixtures no produto anterior; GREEN após menor correção; rebuild oficial, testes focais e FULL final acumulado, auditoria independente, comparação de fontes financeiros/AGENTS/normas. CI Linux do SHA final antes de merge do novo delta. Nunca fechar incidente por retry. UI413 casos obrigatórios permanecem e a configuração de timeout exige gate A4 separado.

Rollback: reverter somente este delta e reconstruir derivados, preservando stores/progressos/originais. AGENTIC IMPACT CHECK: AGENTIC IMPACT DETECTED. BASIS: correção de apresentação e novas fixtures refletem contrato já aprovado; registrar fatos/provas nos contextos focais. Autoridade, routing, AGENTS, skills, normas e índices preservados; sem reconciliação global/reindex.


Focais concluídos: revisão tipográfica1caso/6cenáriosPASS, Capitalmodoall9PASS/0FAIL(inclui48matrizoriginal), fontes estáveis. Rebuild oficial executado, buildce3e56f9e69fc5cc. Revisão independente semCritical/Important, única frase documental stale corrigida. Nãoequivale aFULLfinal/LINUXPASS; próximo gate completo em candidate congelado.


Inspeção da captura e métricas confirmou efeito local do seletor genérico header: padding-inline20px reduzia o conteúdo do cabeçalho de139para99px. No mesmocontainerestreito foi declarado padding-inline0 e o primeiro grupo recebeu flex-basis100%, com quebra como fallback. A declaração de padding é sobreposta no shellTesla observado, conforme nota de cascata abaixo. Não alterar tipografia, paddingvertical, cabeçalho global, dados ou controles. Ajuste de geometria responsiva restrito à causa observada.


Candidate final congelado: builde65a0f5397d4553c, CSS5a6cf370..., Planning031a2880..., Gate75e0eaf... eworkflowe9d5dcbd.... Focais finais6cenários revisãoPASS/Capital9gruposPASS com48matrizpreservada, fontesestáveis. Revisão independente final semCritical/Important/Minor. FullfinalenovoLinuxaindapendentes; não promover resultados anteriores.


Nota de cascata verificada: no shellTesla capturado, o seletor genérico html[data-ui-version=tesla-inspired]:not([data-active-screen=dash])header em app.css3063/3787 tem especificidade0,2,2 e mantém padding6px20px4 sobre a declaração local0,2,0. Não afirmar remoção efetiva desses20px nesse contexto. A quebra/fullrow corrigiu o overflow(root155/scroll155) e a revisão permanece visível; limpeza global de header fica fora deste delta. Reviewclassificou apenas a descrição anterior comoMinor, resolvida por esta correção factual; código/testes/oráculos não mudaram pósFULL.


FULL local final:116/116PASS eUI413/413PASS, fontes estáveis, builde65a0f5397d4553c. Recibos em docs/validation/ci-matrix-budget-20261101/. Resultado antigoLinux114/2 preservado em validation/ui-font-geometry. Próximo gate: LinuxFULL/Host no SHA final antes do merge; não fechar incidenteLinux por prova local.
