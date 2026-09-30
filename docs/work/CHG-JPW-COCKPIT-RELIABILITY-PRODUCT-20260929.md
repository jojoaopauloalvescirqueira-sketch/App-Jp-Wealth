# CHG-JPW-COCKPIT-RELIABILITY-PRODUCT-20260929 — 1.10.0

Status: implementação autorizada pelo pedido PLEASE IMPLEMENT THIS PLAN de 2026-09-29; aceite do candidate pendente.
Risco: N3 / A4. Branch: codex/jpw-alavancagem-atual-20260926; HEAD f5145b25e86af6b4ccbfef847cba0d84d74e7c8a.
Base: 1.9.0/r15, 93/93 arquivos conferidos; fingerprint 1c623d727ed028d91a0d578ec37db0745a00959ae806309f8e3ae7ba224d3a91. Snapshot externo preservado em outputs/jpw-cockpit-v190-20260929/final-r15/candidate. Full histórico 52 PASS / 5 PRODUCT_FAIL; nativo NOT_RUN.

Objetivo: Contratos tipados, coordenador, versão central, trilha técnica de 30 dias/20 MiB, cobertura do observador e supervisão. Arquivos permitidos MQL5/** e README; testes sob CHG CONTROL.

Invariantes: preservar matemática, unidades e schemas financeiros MDD/Gênese/USC/Raiz N/Stops; ocultação visual não suspende coleta. Nenhuma negociação, leitura de conta real, instalação operacional, autoaprovação, commit, push, merge ou publicação. Preservar trabalho preexistente reconciliado com r15.

Compreensão: JP Wealth fornece diagnóstico de risco, sem substituir autoridade normativa. MT5 coleta/calcula localmente; site apenas distribui. A mudança separa coleta aceita da renderização, corrige proveniência e defeitos de UX, adiciona eventos técnicos sem séries financeiras e testes específicos. Dependências: indicador, observador, includes, scripts, manifest/geradores e página. Norma/Estatuto/Harness externo e P-21 não mudam.

Validação: caracterização e replay sintético, focais existentes e novos, pacote/página/estrutura, full bruto sem reclassificação, auditoria independente; bytes exatos em MT5 isolado somente se disponível. Ausência nativa NOT_RUN e prontidão BLOCKED.
Rollback: restaurar fontes r15 preservados e regenerar derivados; nunca apagar registros financeiros. Novos diagnósticos têm namespace próprio. Evidências desta revisão: outputs/jpw-cockpit-v1100-20260929.

Autoridade: plano humano vigente; este CHG não concede permissões adicionais. Preflight edit --allow-dirty PASS após conferência 93/93; divergência material encerra contrato.

Fechamento de implementação: fontes 1.10.0 derivados do r15; produto congelado antes da extensão do guia em `outputs/jpw-cockpit-v1100-20260929/product-r16`. Reparos de auditoria e todos os bytes finais serão identificados pelo recibo `final-r17/CANDIDATE.json`; os pareceres preservam achados e reavaliações. Suíte MT5 host e full web permanecem controles separados, com recibos brutos próprios. Nativo NOT_RUN; prontidão BLOCKED. Resultados definitivos e limitações em `outputs/jpw-cockpit-v1100-20260929/DELIVERY_REPORT.md`. Este fechamento não concede aceite nem promoção.

Revisão final r17: r16 e seu full bruto (54 PASS / 3 PRODUCT_FAIL) preservados. Correção adicional de auditoria: isolar marcadores de falha técnica por instância/componente, evitando que outro escritor no mesmo gráfico apague uma pendência; limpar somente após esvaziar a fila do contexto. Regressão sintética específica e nova suíte final; sem alteração de fórmulas ou schemas financeiros.
