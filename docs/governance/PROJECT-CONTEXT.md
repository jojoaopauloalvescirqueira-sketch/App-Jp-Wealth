# Contexto canonico do projeto

Atualizado em: 2026-09-09
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
| Forex | Apoiar a operação em derivativos e a gestão de risco | Visão Geral, Preparação, Conta, Operação, Apuração e Planejamento, com onboarding, cálculo de risco, histórico e simulação estatística. Motor financeiro legado; adoção documental V11 não é homologação financeira. |
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

A adoção documental da V11 não adapta o motor legado quadrifásico. As diferenças
financeiras e de fontes permanecem em `CURRENT-STATE.md`, sem migração automática.

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
