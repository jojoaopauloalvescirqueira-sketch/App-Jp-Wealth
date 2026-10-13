# Stoikus Usage Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement task-by-task. This session uses separate builders and independent Gauntlet critics.

**Goal:** Corrigir a instalação, as Entradas e a abertura conjunta do Stoikus sem alterar contratos financeiros ou dados.

**Architecture:** Manter um Monitor em gráfico de apoio e dois indicadores no trabalho. Acrescentar abertura conjunta idempotente e distribuição de uso separada da engenharia; não consolidar produtores nem aplicar templates sobre gráficos existentes.

**Tech Stack:** MQL5, geradores Python oficiais, HTML/JS existentes e testes host/browser.

## Global Constraints

- Produto 1.22.1; MQL 1.221; cálculo 1.9.0 preservado.
- Preservar defaults, APIs, IDs, nomes persistidos, schemas, locks, preferências, estudos, recursos institucionais e todos os pacotes anteriores.
- Supervisor e Fibonacci não recebem novas permissões ou homologação.
- Sem commit, push, merge, publicação ou instalação no terminal do proprietário.

### Task 1: Entradas e abertura conjunta

**Files:** três programas principais; novo `MQL5/Scripts/JPWealth/JPW_Stoikus_Abrir_Paineis.mq5`; testes host em `tools/stoikus_startup_test.py`.

**Interfaces:** conservar todos os inputs públicos existentes. O novo script usa caminhos enraizados em MQL5/Indicators/JPWealth para Conta e NoCuda, sem parâmetros obrigatórios; reconhece nomes novos e legados antes de criar indicadores. A presença por nome não comprova versão, compatibilidade ou funcionamento.

- [x] Congelar/assertar defaults e estudar efeitos de iCustom/ChartIndicatorAdd/IndicatorRelease nas fontes primárias.
- [x] Registrar RED para ferramenta ausente, repetição e falhas parciais usando execução host do código de decisão real com seams inevitáveis do MT5.
- [x] Implementar grupos/rótulos/mensagens e abertura que preserve o EA e indicadores já presentes; cobrir mistura legado/novo e erros sem ocultar estado parcial.
- [x] Registrar GREEN e submeter código e experiência a crítico separado.

### Task 2: Distribuição de uso e controle de integridade

**Files:** `tools/build_leverage_package.py`, verificadores de pacote, manifesto, versão central e `.gitignore`; downloader em `src/js/20-ui/31-tools-services.js`.

**Interfaces:** conservar `downloads.source` como SDK de engenharia; acrescentar `downloads.dailySource`, com o mesmo contrato available/path/filename/sha256/bytes. SDK inclui o novo script e `STOIKUS_USO_DIARIO.md`; pacote de uso admite somente os quatro programas definidos e a dependência completa, sem EX5 sem prova nativa.

- [x] Registrar RED: baseline não possui dailySource nem separação do inventário operacional.
- [x] Criar oráculo independente para quatro entradas de uso, ausência de testes/legados, fechamento de includes/resources, igualdade de membros, reprodução e idempotência.
- [x] Atualizar versão e gerador preservando casos negativos e recibos nativos estritos; produzir pacote de uso com guia `LEIA_PRIMEIRO.md`.
- [x] Integrar download verificado por tamanho/SHA-256, compatibilidade com manifesto antigo e recusa de dados corruptos.
- [x] Registrar GREEN e preservar hashes históricos.

### Task 3: Guia e site

**Files:** `index.html`, `mt5/jpw-alavancagem-atual/STOIKUS_USO_DIARIO.md`, prefixo atual do README e testes da página afetados.

**Interfaces:** botão `data-jpw-leverage-download="dailySource"`; manter source e compiled; preservar IDs/rotas existentes, cinco abas e inventário de engenharia sob seção explícita.

- [x] Registrar falhas dos percursos atuais: não há instalação operacional separada nem instrução de abertura conjunta.
- [x] Escrever guia curto, tabela de papéis, explicações de cobertura e auxílio para falta de Monitor/duplicatas/parametrização/Fibonacci pendente.
- [x] Priorizar pacote de uso no site; colocar inventário e ensaios de engenharia sob disclosure acessível.
- [x] Verificar navegação, layout, downloads, clareza e comparação A/B com a referência escolhida.

### Task 4: Fecho e revisão Gauntlet

**Files:** suite registration, documentos focais de contexto/handoff/changelog, novos recibos em `docs/validation/stoikus-1.22.1/`.

- [x] Regenerar manifesto e derivados pelos geradores oficiais após encerradas as escritas dos construtores.
- [x] Rodar os testes focais e `leverage_suite.py --scope all`; depois `quality_gate.py --tier full`.
- [x] Dar pacotes A/B a críticos com contexto novo; manter mapeamento de autoria privado e relatar pistas reconhecíveis. Corrigir rejeições e repetir a verificação afetada até vencer ou encontrar limite do ambiente.
- [x] Verificar delta contra baseline, hashes históricos, fórmulas/IDs/defaults/locks e integridade final. Tentar provas nativas somente se houver ferramenta/ambiente apropriado; nunca inventar EX5 ou homologação.
- [x] Salvar entrega local revisável e informar com precisão o que mudou, testes executados e pendências nativas. Git e publicação ficam separados.


Fecho local: host/all 44/44 e full 57/57 no freeze R4. Revisões independentes de código/distribuição e clareza documental/web aprovadas. O ensaio MT5 permanece NOT_RUN por limitação da edição do Parallels; não integra o PASS sintético. Commit, integração, publicação e instalação operacional não foram executados.
