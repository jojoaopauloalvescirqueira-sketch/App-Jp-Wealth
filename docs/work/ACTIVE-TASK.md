# Tarefa ativa local — Operação com proporções de planilha

Candidate local de 2026-10-05, base a47ebee, branch codex/operation-proportions-20261005.

Contratos: [produto](CHG-JPW-OPERATION-PROPORTIONS-20261005.md), [testes](CHG-JPW-OPERATION-PROPORTIONS-TEST-20261005.md), [brief](BRIEF-JPW-OPERATION-PROPORTIONS-20261005.md).

Autorização: implementação do plano pelo proprietário; sem commit, push, merge ou publicação. Invariantes financeiros, dados e MT5 preservados. Resultados históricos permanecem no Git e no snapshot; esta tarefa não os reclassifica.

---

## Fotografia anterior preservada — histórica, não autoridade desta tarefa

# Tarefa ativa — navegação, Estatuto e clareza Forex

Implementação N1/A2 do plano completo aprovado pelo proprietário. Três CHGs NAVIGATION-AVAILABILITY, NORMATIVE-READER e FOREX-CLARITY de 20261001; brief BRIEF-JPW-SITE-CLARITY-20261001.

Base deffc5061fe2eff3d83b6f6e742fa105ac9c5b06; fingerprint bd0894b36d0fa8ff696e9bf5f7833fc654326466999127b70e95e8d4b0e8390e; snapshot externo /Users/joaopauloalves/.codex/.chatgpt-projects/g-p-6a4fc0aa51dc8191af013579f37179a3/outputs/jpw-navigation-normative-forex-20261001. Preservar 149 entradas anteriores. Sem commit/publicação, MT5 ou dados reais. SOURCE REVISION UNKNOWN herdado permanece; candidate local concluído; full final57PASS/0falhas, regressão host MT517PASS. Aceite humano e publicação permanecem separados.

Runtime estabilizado no build 83369b5cffa50c58. Três P2 Forex e a colisão do leitor com Notas em zoom200% foram reproduzidos e corrigidos. Pareceres/evidências, fingerprint final e rollback ficam no diretório externo citado. Aceite humano e publicação continuam separados; MT5 nativo herdado permanece NOT_RUN.


## Tarefa corrente 2026-10-01 — Execution Board adaptado

# Brief — Execution Board adaptado

## Identidade e compreensão

2026-10-01. Raiz /private/tmp/jpw-cockpit-ui-20260930; branch codex/jpw-cockpit-ui-20260930. Aprovação: pedido atual do proprietário para implementar o plano completo. CHGs N1/A2 EXECUTION-WORKBOOK e N3/A4 LOT-REFERENCES. Sem Git, publicação, MT5 ou dados reais.

1. JP Wealth organiza risco e fatos financeiros; esta tarefa torna a operação comparável transversalmente à planilha sem alterar a política.
2. Domínio produz resultados; UI mantém rascunhos RAM, navegação e representação. Comandos existentes são únicos escritores.
3. Base observada: sete colunas com campos empilhados e fases em accordions. Candidate: grade única com vinte campos e três ferramentas no contexto.
4. Consumidores: Board, risk adapter, Header/Dashboard, rotas motor e exec; alterar somente projeções de referência explicitamente autorizadas.
5. Preservar identidade, unidades, schemas, LEGACY, drafts, preferences, pending policy e pacote MT5. Não converter células/cache do Excel em oráculo financeiro.
6. Evidência: tarefas sintéticas, equivalência dos cálculos existentes, bases SI/equity diferentes, zero writes na edição/navegação, guards e audits independentes.

## Fontes e limites

AGENTS e FOREX-V11-ENGINE lidos. Estatuto e Anexo conferidos na pesquisa da proposta; P12b fornece fatores 0,50/0,25; Art3.19 (PDF pp.46–47) fundamenta a referência inicial sobre SI; Art4.5 §8 (PDF p.36) fundamenta o teto corrente sobre min(SI,E). Aprovação atual confirma mostrar ambas sem usar a primeira como limite corrente. Planilha 8.1 é referência visual e contém convenções legadas (fases, ATR1200 e rótulos pips); não importar suas regras. Contratos FOREX-EXECUTION-BOARD e FOREX-EXPERIENCE regem contexto/comandos. Harness localizado em 2 - TRABALHO/6C - SOFTWARE (caminho antigo em AGENTS é histórico), hash nos CHGs. Skills preflight/change-control/design IMPLEMENTAR aplicadas.

## Implementação e segurança

Uma fonte de cálculo; nenhuma fórmula financeira no renderer. grade com vinte colunas; campos completos, scroll local, ID/instrument congelados; abaixo de 768px de área útil lista com o mesmo DOM. Ferramentas conservam DOM, scroll e drafts. Preview de geometria/ATR/Raiz N é distinto do risco salvo. Erros em detalhe abrem/focam campo. Referência SI e teto corrente são métricas teóricas com base/fonte explícitas; normal/restrictive anteriores continuam como teto corrente.

Dados sintéticos, servidor/contextos descartáveis. Testes completos e focais autorizados, sem editar gates/fixtures para aprovar. Auditoria independente após freeze; mudanças posteriores invalidam evidência afetada. Entrega candidate e rollback, aceite manual separado.

Baseline SHA: deffc5061fe2eff3d83b6f6e742fa105ac9c5b06
Fingerprint: e6d2d9cdfc61e2e908474b090b60222b73e3470f746c530eb27b94aba2326c32
Snapshot: /Users/joaopauloalves/.codex/.chatgpt-projects/g-p-6a4fc0aa51dc8191af013579f37179a3/outputs/jpw-execution-board-20261001/baseline.tar.gz

Contratos: CHG-JPW-EXECUTION-WORKBOOK-20261001.md e CHG-JPW-LOT-REFERENCES-20261001.md. Esta seção sucede a tarefa anterior sem reescrever sua evidência.

## Fechamento do candidate Execution Board

Runtime final `7125b6ef17f60623`, fontes funcionais congeladas; site local e portátil regenerados oficialmente. Standard final: **46 PASS / 0 falhas**. Full bruto dos bytes congelados: **56 PASS / 1 PRODUCT_FAIL** — timeout de ativação do Laboratório Galton em research-navigation. O mesmo focal passou no standard e na repetição isolada; o full não foi reclassificado. A rodada full anterior conserva 57 PASS, mas atravessou a última correção CSS e não constitui aceite dos bytes finais.

Focais financeiros: referências do Motor 34/34 PASS; projeção 116/116 PASS; Market 30/31, com 1 PRODUCT_FAIL também reproduzido no snapshot. Workbook source7/8 e portátil6/7, ambos com a mesma falha herdada DD14 (14.000000000000002 provoca fase5 em vez de4). Board 15/15 PASS; tabela e Clarity PASS. Auditoria independente do delta: AUDIT_PASS_WITH_DEBT, sem aprovação financeira global. Regressão MT5 host 17 PASS nos bytes finais; compilação/execução nativa herdadas NOT_RUN e pacote 1.16.1 íntegro.

**Aceite bloqueado** por DD14, divergência de captura inicial no focal Market e intermitência Galton no gate obrigatório. Policy, engine, state, Estatuto/Anexo, gates e fixtures canônicas permanecem iguais ao snapshot. As falhas não foram escondidas no renderer nem removidas dos testes. As 182 alterações preexistentes permanecem preservadas; SOURCE REVISION UNKNOWN herdado continua explícito.

Relatório, recibos, capturas comparativas, fingerprint e rollback: `/Users/joaopauloalves/.codex/.chatgpt-projects/g-p-6a4fc0aa51dc8191af013579f37179a3/outputs/jpw-execution-board-20261001/REPORT.md` e `CANDIDATE.json`. Não houve commit, integração, publicação, alteração do MT5 ou acesso a perfil financeiro real.
