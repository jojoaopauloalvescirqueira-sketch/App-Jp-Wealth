# Contexto canonico do projeto

Atualizado em: 2026-09-08
Natureza: contexto estavel (M1). Mudancas frequentes pertencem a `CURRENT-STATE.md`.

## Produto

O JP Wealth Risk Terminal V9.1 e uma aplicacao web local/PWA para governanca de risco, execucao, contas, contabilidade, onboarding e simulacao estatistica. O sistema opera sobre dados financeiros e credenciais de leitura; portanto, perda silenciosa, calculo divergente e falsa evidencia de teste sao riscos de primeira ordem.

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

## Contratos que devem permanecer estaveis

- Chave principal: `jpwealth_v9_state`.
- Estados antigos passam por `migrate()`; nunca sao substituidos silenciosamente por `DEFAULTS`.
- A ordem de `src/js/manifest.json` e parte do runtime.
- O monolito em `dist/` e derivado, nao fonte de edicao.
- Backup/exportacao nao deve conter senha master.
- Preferencias visuais separadas nao redefinem o estado financeiro.
- Regras N3 dependem de decisao normativa explicita.

## Modelo de entrega

`main` representa o estado integrado. Trabalho ocorre em branch delimitada. Validacao local, teste no navegador, revisao de diff, commit, push, merge e deploy sao etapas independentes. As politicas Git especificas estao em `CLAUDE.md` e `docs/GIT-WORKFLOW.md`.

## Definicao institucional de qualidade

Qualidade significa: regra correta, dados recuperaveis, comportamento verificavel, superficie de ataque controlada, contexto rastreavel e manutencao possivel por outro agente sem depender da conversa anterior.
