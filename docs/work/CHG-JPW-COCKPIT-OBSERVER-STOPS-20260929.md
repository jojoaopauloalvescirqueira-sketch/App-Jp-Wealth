# CHG-JPW-COCKPIT-OBSERVER-STOPS-20260929 — produto 1.10.1

Status: implementação autorizada pelo pedido `PLEASE IMPLEMENT THIS PLAN` de 2026-09-29; auditoria e aceite pendentes.
Risco/autoridade: N3/A4 pelo estado de uma métrica financeira e seu publicador, sem mudança de fórmula. Branch `codex/jpw-alavancagem-atual-20260926`; HEAD `f5145b25e86af6b4ccbfef847cba0d84d74e7c8a`.

Base: candidate 1.10.0/r17 preservado em `outputs/jpw-cockpit-v1100-20260929/final-r17/candidate/` com `CANDIDATE.json`; 113/113 hashes conferidos contra a worktree antes da escrita; fingerprint `54044877713dd3e4909a85dbf4b07c91c850f5adafd2833149970f5d5aaac223`. A árvore suja existente corresponde a esse snapshot. Recibos históricos r17: suíte específica 16 PASS / 1 PRODUCT_FAIL e full geral 54 PASS / 3 PRODUCT_FAIL; não são reclassificados. Compilação/execução nativa `NOT_RUN` e prontidão `BLOCKED` não são herdadas como aprovação.

Objetivo: distinguir ausência de confirmação do EA observador de publicação pendente/falho, mantendo Stop risk `N/A` sem amostra íntegra atual; tornar a tabela Stops acessível com paginação compacta e motivo real antes do fallback geométrico. O usuário confirmou que o EA estava desativado na sessão mostrada. A imagem da tabela mostra “Amplie para ler a tabela”; não identifica bytes do EX5 instalado.

Escopo de produto: `mt5/jpw-alavancagem-atual/MQL5/**`, `mt5/jpw-alavancagem-atual/README.md`, seção Alavancagem Atual de `index.html`, testes focais de observador/Stops/painel/página/pacote e derivados oficiais de `downloads/jpw-alavancagem-atual/`, portátil e cache. `docs/work/ACTIVE-TASK.md` e este CHG podem registrar o estado. O guia local para IAs tem CHG separado `CHG-JPW-COCKPIT-OBSERVER-STOPS-AI-GUIDE-20260929` e só será editado após congelar o produto.

Invariantes: sem mudança das fórmulas, do critério de `Current` financeiro, dos schemas financeiros MDD/Gênese/USC/Raiz N/Stop risk, do risco consolidado ou das outras cinco métricas. Estado antigo no menu é `LAST · NOT ACTIVE`, nunca número atual no gráfico. A presença temporária do EA não é prova de cobertura contínua e não substitui a amostra de risco. Sem negociação, leitura de conta real pelo agente, instalação operacional, commit, push, merge ou publicação.

Compreensão e dependências: o indicador desenha amostras aceitas; o EA usa `OrderCalcProfit` e publica Stop risk localmente. Uma posição com SL não prova que o EA está anexado nem que publicou. O site ensina instalação e diagnóstico, sem ler dados de conta. A nova informação técnica de presença deve ser separada dos registros financeiros. O layout deve priorizar o motivo real de ausência antes de bloquear a tabela por fonte/DPI.

Validação: reproduzir a falta do EA e a geometria da captura (~32 px de texto, janela de até 620 px), testar estados de observador, primeira amostra, falha/desativação/reinício/troca de conta, amostra atual/antiga/ausente, seis posições e pendentes, fontes 9–24, quatro cantos, gráficos estreitos, DPI 100–200%, cliques e teclado. Executar focais, pacote/estrutura, full bruto sem reclassificação e auditoria independente. Compilar e inspecionar bytes exatos em MT5 isolado se disponível; caso contrário `NOT_RUN`, sem EX5 ou prontidão alegada.

Rollback: restaurar fontes/docs a partir do r17 verificado e regenerar derivados pelos geradores oficiais; não apagar registros locais de usuário. Este CHG não autoriza qualquer gate posterior.
