# Planejamento — contrato visual e jornada de três abas

A finalidade e os cálculos permanecem no [contrato Planejamento](../architecture/PLANNING.md). A correção de21/10 exige centralização, alinhamento moeda/valor, cabeçalhos responsivos, previsão sem repetição e legenda/data da Parada; [plano aprovado](../superpowers/plans/2026-10-21-planning-proportions.md). O [estado operacional e provas](CURRENT-STATE.md) identifica a revisão realmente validada. Não altera perguntas, perfis, escritores, finanças, backup ou norma. Históricos preservados abaixo.

## Fotografia anterior preservada

# Correção funcional de Planejamento — 20/10/2026

Contrato vigente: [Planejamento](../architecture/PLANNING.md) tem somente Comece aqui, Consolidado e Preenchimento mensal, menu Stoikus operacional separado e referência inicial interna. Formulário sempre acessível e dois marcos de renda durante o preenchimento. Padrão editável após Research; Notas globais com Mostrar ativo, ocultas em modais. [Plano humano](../superpowers/plans/2026-10-20-planning-three-tabs.md). Motor/estado/backup preservados;91checks anteriores não aprovam o novo delta. Sem dados reais, norma, instruções, Git ou publicação.

## Fotografia anterior preservada

# Execução atual — Planejamento — 20/10/2026

Base main `ea15afc9c6a9c30cc69c5b98a8b85c85211ffb34`; branch especificamente autorizada `codex/planejamento-patrimonial-20261020`. Candidato preserva três minigames e Bolsas Globais. Implementa o plano aprovado de menu independente, sem migração de legado. Fontes e oráculos sintéticos fixados; suítes/revisões finais em execução. Sem Git final/publicação autorizados. [Contrato](../architecture/PLANNING.md). Fotografias anteriores permanecem abaixo.

# Contexto canonico do projeto

Revisão geral histórica: 2026-09-09
Atualização focal Forex: base integrada `01c08241ccb7bc229a05779a52f577ee55a69ae7`, build `9f236bf4a421a1bf`. Somente os trechos Forex abaixo refletem essa revisão; as demais áreas conservam sua data e limites originais.
Natureza: contexto estavel (M1). Mudancas frequentes pertencem a `CURRENT-STATE.md`.

Base material desta reconciliação: `484228189cc3f5f4c297f29f88f2b2ed541a3afd`,
build `88c0cb1ce5520311`. As capacidades abaixo foram cotejadas com os contratos
e o código dessa revisão; não constituem nova validação de runtime ou aceite.

## Produto

O JP Wealth é uma aplicação web local/PWA para organizar a vida financeira e
apoiar análise, planejamento e gestão de risco. O identificador técnico legado
Risk Terminal V9.1 permanece no produto. O sistema opera sobre dados financeiros
e credenciais de leitura; perda silenciosa, cálculo divergente e falsa evidência
de teste são riscos de primeira ordem.

As finalidades definidas pelo proprietário orientam a evolução; a coluna de
capacidade descreve somente o que existe na revisão acima. Finalidade não é
funcionalidade entregue, promessa de retorno ou autorização de implementação.

| Módulo | Finalidade | Capacidade e limite atuais |
|---|---|---|
| Dashboard | Sintetizar o sistema e dar acesso às áreas | Resumos de Forex, Finanças Pessoais, Research e Alladin; abaixo, Status do Sistema e Ações rápidas. Consome valores canônicos e não cria um domínio financeiro próprio. |
| Research | Organizar estudos e análises para apoiar decisões de investimento | Calendário Econômico, Estudos NoCoda e Estudos dos Pivots. Ações, Stocks, REITs e Others têm placeholders explícitos. Estudos não geram ordens nem autorizam operação. |
| Forex | Apoiar a operação em derivativos e a gestão de risco | Motor central orientado por Parâmetros, registro factual separado da elegibilidade, Reservas e Contabilidade; compatibilidade legada e limites em FOREX-V11-ENGINE. Integração V11 não é homologação financeira. |
| Finanças Pessoais | Apoiar o planejamento financeiro pessoal e familiar | Orçamento mensal, dívidas/crédito, comparação, cenários e síntese. Domínio fechado; não inclui inventário/patrimônio nem integração automática com trading. |
| Alladin | Consolidar investimentos e registros patrimoniais | Cadastro, ledger, saldos de caixa e posições por quantidade, com criação e estorno de lançamentos. Consolidação parcial: não há valuation, cost basis, P&L/performance ou patrimônio completo; integrações Trading/PF/FX continuam pendentes. |

Fontes por responsabilidade e consumidores estão no [mapa de contexto](CONTEXT-MAP.md)
e no [mapa do código](../architecture/CODE-MAP.md). A leitura deve alcançar os
contratos compartilhados pertinentes, mesmo quando atravessam pastas ou módulos.

## Fontes de autoridade

- Norma vigente indicada pelo proprietário: `docs/normative/Estatuto_JP_WEALTH_UNIFICADO.pdf` (V11).
- Anexo recebido: `docs/normative/ANEXO_PARAMETRICO_CANONICO.md` (JPW-ANNEX-T03), limitado aos elementos delegados; estados PENDING não são valores. Identidade e divergências entre as fontes em `docs/normative/README.md`.
- Decisoes humanas aprovadas: `docs/decisions/`.
- Regras de agentes: `AGENTS.md`.
- Arquitetura: `docs/architecture/`.
- Estado atual e divida conhecida: `docs/governance/CURRENT-STATE.md`.

O motor central Forex já foi integrado na revisão focal acima. Seu catálogo de Parâmetros (`src/js/00-core/00-forex-policy.js`) alimenta o executor (`src/js/10-domain/00-forex-engine.js`); o estado/read-model e a UI consomem essa política sem definir regras concorrentes. Contrato: [FOREX-V11-ENGINE](../architecture/FOREX-V11-ENGINE.md). A política ativa permanece imutável; propostas não a ativam. Registro de fatos não autoriza operação; lacunas, conflitos FCR/FEO, dimensionamento indisponível e A12 parcial permanecem. Dados legados não são reinterpretados nem migrados silenciosamente.

O codigo nao se torna normativo por estar em producao. Um teste nao torna correta uma regra que conflita com o Estatuto.

## Arquitetura atual

- Aplicacao estatica, sem framework e sem backend obrigatorio.
- `index.html` contem a composicao e os contratos DOM estaticos.
- `src/styles/app.css` concentra os estilos.
- `src/js/manifest.json` define a ordem dos scripts classicos globais.
- `src/js/00-core` a `40-app` organizam estado, dominio, UI e inicializacao.
- `tools/rebuild_monolith.py` gera o HTML portatil em `dist/`.
- `sw.js` e `manifests/` formam a superficie PWA.
- Testes Python usam Chromium/Playwright para comportamento real.

A navegação integrada usa lateral contextual por padrão e oferece a composição
superior no Editor. Reutiliza o resolver e os mesmos nós, sem segunda navegação
persistida. Dashboard mantém síntese e Sistema/Atalhos; onboarding operacional,
Estado Operacional, fase/DD/risco/alavancagem, VRM e widget de calendário ficam em
Forex > Visão Geral. A agenda analítica pertence a Research e compartilha o
pipeline de dados do widget. Contrato: [NAVIGATION-HIERARCHY.md](../architecture/NAVIGATION-HIERARCHY.md).

## Contratos que devem permanecer estaveis

- Chave principal: `jpwealth_v9_state`.
- Estados antigos passam por `migrate()`; nunca sao substituidos silenciosamente por `DEFAULTS`.
- A ordem de `src/js/manifest.json` e parte do runtime.
- O monolito em `dist/` e derivado, nao fonte de edicao.
- Backup/exportacao nao deve conter senha master.
- Preferencias visuais separadas nao redefinem o estado financeiro.
- Regras financeiras N3 dependem de decisão normativa explícita. Mudanças N3 de
  control plane (autoridade, instruções ou contexto) também exigem A4 delimitada,
  mas leem suas fontes de engenharia; não ganham permissão financeira por isso.
  Classificação, autorização e obrigação de compreensão seguem `AGENTS.md`.

## Modelo de entrega

`main` representa o estado integrado. Trabalho ocorre em branch delimitada. Validacao local, teste no navegador, revisao de diff, commit, push, merge e deploy sao etapas independentes. A política comum está em `AGENTS.md`; o procedimento Git está em `docs/GIT-WORKFLOW.md`, com adaptação de ferramenta em `CLAUDE.md` sem autoridade adicional.

## Definicao institucional de qualidade

Qualidade significa: regra correta, dados recuperaveis, comportamento verificavel, superficie de ataque controlada, contexto rastreavel e manutencao possivel por outro agente sem depender da conversa anterior.
