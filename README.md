# JP Wealth Risk Terminal V9.1

Aplicação web **local-first** (PWA, sem backend obrigatório) para governança de risco e gestão operacional de capital. O terminal aplica o **Estatuto JP Wealth** — fases operacionais, perfis de risco, limites de drawdown, stops, poda e quarentena — como regra executável no navegador, mantendo os dados do operador exclusivamente na máquina dele.

O repositório foi estruturado a partir do HTML portátil preservado do JP Wealth: HTML, CSS e JavaScript foram separados **sem reescrever as regras financeiras nem alterar a ordem de execução** do código original.

## Propósito

O sistema opera sobre dados financeiros e credenciais de leitura. Por isso, três riscos são tratados como de primeira ordem: **perda silenciosa de dados**, **cálculo divergente da norma** e **falsa evidência de teste**. Tudo no projeto — arquitetura, testes, governança de agentes — existe para conter esses três riscos. O código não se torna normativo por estar em produção: a autoridade vive no Estatuto (`docs/normative/`) e nas decisões formais (`docs/decisions/`).

## Prioridade do projeto

1. Preservação do capital e integridade dos dados.
2. Aderência ao Estatuto JP Wealth e às decisões formais aprovadas.
3. Correção dos cálculos normativos.
4. Rastreabilidade de cada alteração.
5. Evolução da interface e da arquitetura somente depois dos itens anteriores.

## Funcionalidades

### Estado da migração de navegação

- **TARGET CANÔNICO:** Dashboard, Forex, Finanças Pessoais, Research e Alladin.
- **CHECKPOINTS NAV-01/NAV-02:** Forex possui exatamente seis destinos — Visão Geral,
  Preparação, Conta, Operação, Apuração e Planejamento — sobre as telas físicas
  existentes e sem `section#forex`. Operação, Apuração e Planejamento exibem
  terceiro nível contextual.
- **CANDIDATO NAV-03:** Research possui Forex, Ações, Stocks, REITs e Others.
  Forex reúne Calendário, NoCoda e Pivots; Ações abre Brasil/B3 e os demais
  destinos permanecem empty states neutros. NAV-03 é o primeiro candidato
  potencialmente publicável, ainda sujeito a gate humano separado.

### Capacidades funcionais

- **Dashboard** — visão consolidada com grade de widgets personalizável (layout persistido separadamente do estado financeiro) e o widget **Notícias de alto impacto · hoje**, alimentado por calendário econômico público via `infra/ff-news-feed` (dados servidos com CORS por repositório auxiliar; nenhum dado do operador sai da máquina).
- **Contas** — cadastro e acompanhamento de contas com credenciais de leitura; a senha de investidor vive **apenas em memória de sessão**, nunca em `localStorage`, checkpoint ou backup.
- **Execução** — registro de ordens sob as regras do Estatuto: fases, risco programado, classificação de stops (2 ATR, Raiz-N), alavancagem.
- **Research** — ownership visual de Calendário Econômico, Estudos NoCoda e Estudos dos Pivots sob Forex, sem duplicar telas ou domínio.
- **Contabilidade** — ledger de fechamentos, retorno acumulado e drawdown; sem série demonstrativa: os indicadores permanecem vazios (`—`) até existir fechamento real.
- **Planejamento FX** — planejamento patrimonial temporal para Forex: baseline congelado, rolling forecast e realizado, com ledger cambial e painel normativo de reservas (ver seção própria abaixo).
- **Finanças Pessoais** — orçamento doméstico em centavos (`BRL_CENTS`), com Visão Geral consolidada, Orçamento Mensal (receitas, despesas e destino da sobra), Dívidas & Crédito, Comparativo Mensal e Cenários. Tudo derivado do estado vivo: totais, coberturas, sobras e utilização nunca são persistidos, e mês só nasce por ato de edição — abrir não materializa. Inventário e Patrimônio **não** pertencem a este domínio — são o domínio próprio **Alladin** (roadmap `ALD-*`; agregado `S.alladin` em schema v2 com as quatro entidades cadastrais — Instrument, Asset, Account, CashAccount. O **cadastro (C3) está concluído**: leitura, criação, edição e ciclo de status pela interface, sem nenhuma camada econômica — transações, posições, valuation e performance não iniciadas. Contrato em `docs/architecture/ALLADIN.md`).

### Onboarding e período operacional

Questionário de início em etapas — parâmetros, calibração e a etapa **Base de Dados**, com termo de responsabilidade obrigatório. Simulação estatística de suporte à calibração. Revisão posterior pelo resumo seguro em `Configurações → Parâmetros e Calibração`, que reabre o onboarding em modo de edição sem duplicar campos ou credenciais.

### Notas operacionais

Painel de notas com CRUD, pastas, filtros, Markdown e **Trace ID** rastreável, funcionando em desktop, mobile e no HTML portátil; incluídas no backup.

### Central de Configurações

Modal aberta pela engrenagem do cabeçalho, preservando a tela operacional ao fundo:
Aparência, Interface, Editor, base **educacional local pesquisável** (Forex,
glossário, FAQ — sem sinais nem recomendações), Estatuto Operacional, Parâmetros,
Laboratório de Probabilidade e Backup. A pesquisa é declarativa e **não indexa dados
operacionais** do usuário.

### Laboratório de Probabilidade — Galton Board

Em `Configurações → Laboratório de Probabilidade → Galton Board`, uma placa física
2D permite observar como um histograma empírico emerge de colisões reais. O motor
Planck.js 1.5.0 está vendorizado localmente; a simulação usa passo fixo de `1/120 s`,
seed determinística, pinos triangulares, `linhas + 1` compartimentos, controles de
fila/velocidade/inclinação e comparação binomial somente quando as premissas de
simetria estão satisfeitas.

Canvas não é a única representação: estatísticas e detalhes por compartimento ficam
em DOM acessível. Corpos assentados são removidos e conservados apenas como contagens
agregadas. O laboratório é educacional, isolado do motor financeiro e **não é um
modelo de retorno de Forex, previsão de mercado ou promessa de desempenho**.

### Planejamento FX

Na tela física própria `#fxplan`, filha semântica de Forex no candidato NAV-02
e ainda preservada pelo alias legado `fxplan`, o Planejamento FX é o
motor de planejamento patrimonial temporal para Forex: separa **planejado**
(premissas do operador),
**realizado** (fechamentos mensais e ledger cambial de aportes) e **normativo**
(FCR/FEO do Estatuto, pela mesma função usada no onboarding). O baseline
aprovado é congelado; o forecast vigente recalcula o futuro a partir do último
fechamento real (rolling forecast) e as três séries são comparáveis. O custo
médio do dólar usa média ponderada (`Σ BRL ÷ Σ USD`) e créditos USD-nativos não
o contaminam. Rentabilidade planejada é premissa do usuário — nunca deriva de
perfis de risco nem constitui promessa de retorno. Contrato em
`docs/architecture/FX-PLANNING.md`.

### Base de Dados e backups

Exportação com nomenclatura sequencial `JP_WEALTH_DB_NNNNNN_AAAA-MM-DD_HHmm.json`, sequência incrementada só após sucesso confirmado e proteção contra sobrescrita. Pasta padrão via File System Access API (Chrome/Edge desktop) com reautorização explícita; demais navegadores usam download tradicional com a mesma nomenclatura. Importação **transacional**: o arquivo é lido, validado, normalizado e confirmado atomicamente — backup adulterado não executa script, não injeta DOM e não persiste marcação.

### Privacidade e encerramento

`Finalizar sessão` (ícone no cabeçalho) executa checkpoint determinístico, exige backup confirmado quando necessário e remove **apenas** as chaves locais do JP Wealth — incluindo a preferência auxiliar do Galton Board — sem `localStorage.clear()`, preservando outras aplicações. Confirmação textual `APAGAR TUDO` para a limpeza completa.

### PWA e distribuição

Instalável como PWA com service worker e precache versionado (`sw.js`); o validador
exige que os 77 scripts do manifest também estejam no precache. Durante uma
atualização, o worker novo aguarda o fechamento dos clientes antigos; cada aba
continua usando um build integral, sem combinar HTML novo com scripts cacheados de
outro build. O ícone tem variantes
`Claro` e `Escuro` em `Configurações → Ícone do app` (no iOS é preciso reinstalar o
atalho após trocar). O HTML portátil em `dist/` é **derivado** — destinado a
distribuição de arquivo único, reconstruído por `tools/rebuild_monolith.py`, nunca
editado diretamente.

## Em desenvolvimento e decisões pendentes

- **Dez pendências normativas N3** aguardam decisão formal humana — cada uma tem um ADR aberto em `docs/decisions/` (fatores dos perfis conservadores, fonte canônica de equity do drawdown, gate combinado da Ordem Gênese, bloqueio de stop < 2 ATR, histerese de fase, poda LIFO compulsória, rito da Fase 4, gatilho de quarentena, fator Raiz-N, projeções MEI). **Nenhuma é corrigida silenciosamente**: exigem decisão N3 e branch própria.
- **Dívida estrutural conhecida**: `openOnboardingModal()` concentra ~2 mil linhas; escopo global legado compartilhado; CSP não documentada; cobertura automatizada mais forte nos fluxos recentes que no núcleo financeiro. Detalhes e estado vigente em `docs/governance/CURRENT-STATE.md`.
- Explorações de interface (redesign de telas, consolidações de UI) ocorrem em branches dedicadas e só entram na `main` por integração autorizada.
- Hipóteses guiadas de experimento e áudio do Galton Board ficam deliberadamente para
  uma Fase 2; não fazem parte do candidato atual.

## Início rápido

```bash
python3 tools/agent_preflight.py --mode audit
python3 tools/quality_gate.py --tier standard
python3 tools/serve.py
```

Acesse `http://127.0.0.1:8000`. O PWA precisa ser servido por HTTP/HTTPS; abrir o `index.html` por `file://` não registra o service worker.

## Qualidade e verificação

Três tiers cumulativos de gate (`tools/quality_gate.py`): **fast** (4 verificações —
preflight, estrutura, diff-check, teste do frescor de contexto), **standard** (37 —
inclui a navegação NAV-01..NAV-03, smoke, Central de Configurações, Galton
Board, Planejamento FX, cotação USD/BRL, as nove suítes de Finanças Pessoais,
as três do Alladin e o protocolo de geração da base e a serialização cross-tab de escrita e a superfície cadastral do Alladin (leitura e manutenção) em Chromium real) e **full** (48 verificações, incluindo segurança de importação/XSS, senha de
investidor, recuperação transacional, reprodutibilidade de build e ciclo do service
worker). O cenário longo
de 10.000 bolas fica em `tools/galton_board_benchmark.py`, fora do tier cumulativo.
Taxonomia e composição em `docs/governance/QUALITY-GATES.md`.

O preflight (`tools/agent_preflight.py`) verifica dois sinais independentes de frescor do contexto: **temporal** (idade da fotografia) e **material** (alterações posteriores à source revision fora dos caminhos de reconciliação contextual), com resultado tri-state em que `UNKNOWN` nunca é tratado como `FALSE`.

## Regra de segurança

Nenhuma IA deve alterar constantes financeiras, fórmulas normativas, migrações de estado, regras de exclusão ou dados reais sem uma tarefa explicitamente delimitada e revisão humana.

## Trabalho com agentes

Todo agente começa por `AGENTS.md`, executa o preflight e usa o mapa em `docs/governance/CONTEXT-MAP.md`. O estado confirmado e as pendências vigentes ficam em `docs/governance/CURRENT-STATE.md`; conversas e handoffs nunca substituem esses arquivos. O roteamento de skills está em `docs/governance/SKILL-ROUTING.md` — oito skills `jpw-*` de procedimento local e duas skills genéricas instaladas project-scoped (`repository-architecture`, `agentic-evolution-governance`). O fechamento de toda mudança material exige veredito explícito de impacto agêntico, conforme `skills/jpw-post-change-audit/SKILL.md`.

## Persistência

O estado operacional é mantido no `localStorage` sob a chave
`jpwealth_v9_state`; estados antigos passam por `migrate()` e nunca são substituídos
silenciosamente por `DEFAULTS`. Preferências úteis do Galton Board usam a chave
isolada `jpwealth_galton_preferences_v1`; bolas, fila, histograma e resultados nunca
são persistidos nem entram no backup financeiro. O código está no repositório; os
dados reais do operador precisam ser exportados do navegador e guardados
separadamente em `data/backups/` — nunca versionar dados reais ou credenciais.

O fingerprint de alterações inclui `instruments[].preco` e `instruments[].updated`. Uma atualização automática de câmbio pode, portanto, produzir um falso positivo deliberado de alteração; esta versão prioriza evitar perda silenciosa de dados e não tenta distinguir origem manual de automática.

## Estrutura principal

- `index.html` — composição da interface e contratos DOM estáticos.
- `src/styles/app.css` — design system, temas e responsividade do terminal.
- `src/js/` — lógica em domínios (`00-core` → `10-domain` → `20-ui` → `30-accounting` → `40-app`); a ordem em `manifest.json` é parte do runtime.
- `src/js/40-app/18-galton-board/` — seis módulos clássicos isolados da feature.
- `src/js/30-accounting/05-fx-planning/` — cinco módulos do Planejamento FX;
  `src/js/10-domain/07-reserve-requirements.js` — FCR/FEO compartilhado;
  `src/js/10-domain/08-usd-brl-quote.js` — cotação corrente USD/BRL e cache técnico.
- `src/vendor/planck/` — Planck.js 1.5.0 pinado, licença e proveniência.
- `assets/`, `manifests/`, `sw.js` — superfície PWA (ícones, manifesto único, service worker com precache).
- `infra/ff-news-feed/` — documentação do alimentador do widget de notícias (repositório auxiliar, só dados públicos).
- `docs/normative/` — Estatuto e organograma, fontes de autoridade.
- `docs/decisions/` — ADRs: decisões formais e pendências N3.
- `docs/architecture/` — arquitetura, schema de estado e mapa do código.
- `docs/governance/` — regras para trabalho humano e por IA, estado atual, gates.
- `skills/` — procedimentos locais obrigatórios para agentes do projeto.
- `tests/`, `tools/` — validação, gates, servidor, benchmark e reconstrução do portátil.
- `archive/original/` — original imutável para comparação e recuperação.
- `data/backups/` — backups JSON locais; não versionar dados reais.
- `dist/` — HTML portátil reconstruído (derivado).
