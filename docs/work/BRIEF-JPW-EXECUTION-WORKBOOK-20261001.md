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
