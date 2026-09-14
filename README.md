# JP Wealth Risk Terminal V9.1

Completion pass local em avaliação: Dashboard de orientação, bancadas NoCoda/Pivots, orçamento com resumo e registros, Laboratório com palco e análise, coleções Alladin e escrita focada. Rotas e dados preservados. Evidências e limites: [direção Apple→JP Wealth](docs/architecture/APPLE-EXPERIENCE-DIRECTION.md).
Preserva módulos, contratos financeiros, preferências e a navegação superior
opcional. Estado e limites em [CURRENT-STATE](docs/governance/CURRENT-STATE.md);
a presença destes arquivos não demonstra integração ou aceite humano.

Aplicação web **local-first** (PWA, sem backend obrigatório) para governança de risco e gestão operacional de capital. O motor financeiro ainda executa regras legadas; a documentação normativa foi atualizada para o **Estatuto JP Wealth V11** e o Anexo Paramétrico. A adaptação dos cálculos permanece pendente e esta versão não é declarada conforme à V11. Os dados do operador permanecem na máquina dele.

O repositório foi estruturado a partir do HTML portátil preservado do JP Wealth: HTML, CSS e JavaScript foram separados **sem reescrever as regras financeiras nem alterar a ordem de execução** do código original.

## Propósito

O sistema opera sobre dados financeiros e credenciais de leitura. Por isso, três riscos são tratados como de primeira ordem: **perda silenciosa de dados**, **cálculo divergente da norma** e **falsa evidência de teste**. Tudo no projeto — arquitetura, testes, governança de agentes — existe para conter esses três riscos. O código não se torna normativo por estar em produção: a autoridade vive no Estatuto (`docs/normative/`) e nas decisões formais (`docs/decisions/`).

## Fontes normativas atuais

- [Estatuto V11 — PDF integral](docs/normative/Estatuto_JP_WEALTH_UNIFICADO.pdf).
- [Anexo Paramétrico Canônico — JPW-ANNEX-T03](docs/normative/ANEXO_PARAMETRICO_CANONICO.md).
- [Identificação, precedência e divergências documentais](docs/normative/README.md).

Os arquivos foram incorporados sem reescrever valores, preencher PENDING ou homologar
parâmetros. Os documentos antigos foram removidos do worktree; o histórico Git os preserva.

## Prioridade do projeto

1. Preservação do capital e integridade dos dados.
2. Aderência ao Estatuto JP Wealth e às decisões formais aprovadas.
3. Correção dos cálculos normativos.
4. Rastreabilidade de cada alteração.
5. Evolução da interface e da arquitetura somente depois dos itens anteriores.

## Funcionalidades

### Navegação integrada e histórico da migração

Na revisão integrada `8d6b156da6b22f3119471ca2a2c7f1a3524554b1`, a navegação lateral é padrão e a barra superior anterior permanece como opção no Editor. Destinos, aliases e limites estão no [contrato de navegação](docs/architecture/NAVIGATION-HIERARCHY.md). Integração não comprova deploy.

**Registro histórico NAV-01/NAV-02/NAV-03:** os checkpoints abaixo preservam o estado e os gates daquela etapa. A expressão “candidato potencialmente publicável” pertence a esse histórico; não descreve uma pendência atual nem autoriza publicação.

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

- **Dashboard** — visão consolidada dos módulos, inclusive o resumo de Forex; a seção inferior **Sistema e atalhos** reúne somente **Status do Sistema** e **Ações rápidas**, com personalização aplicável e layout persistido separadamente do estado financeiro. O calendário operacional fica em **Forex → Visão Geral**, junto dos demais componentes operacionais realocados; a agenda completa permanece em **Research → Forex → Calendário**. O feed de notícias de alto impacto usa calendário econômico público via `infra/ff-news-feed` (dados servidos com CORS por repositório auxiliar; nenhum dado do operador sai da máquina). A distribuição dos componentes e suas fontes está no [mapa de contexto](docs/governance/CONTEXT-MAP.md).
- **Contas** — cadastro e acompanhamento de contas com credenciais de leitura; a senha de investidor vive **apenas em memória de sessão**, nunca em `localStorage`, checkpoint ou backup.
- **Execução** — registro de ordens com fases, risco programado, classificação de stops e alavancagem do motor legado; a adequação ao V11 está pendente.
- **Research** — ownership visual de Calendário Econômico, Estudos NoCoda e Estudos dos Pivots sob Forex, sem duplicar telas ou domínio.
- **Contabilidade** — ledger de fechamentos, retorno acumulado e drawdown; sem série demonstrativa: os indicadores permanecem vazios (`—`) até existir fechamento real.
- **Planejamento FX** — planejamento patrimonial temporal para Forex: baseline congelado, rolling forecast e realizado, com ledger cambial e painel normativo de reservas (ver seção própria abaixo).
- **Finanças Pessoais** — orçamento doméstico em centavos (`BRL_CENTS`), com Visão Geral consolidada, Orçamento Mensal (receitas, despesas e destino da sobra), Dívidas & Crédito, Comparativo Mensal e Cenários. Tudo derivado do estado vivo: totais, coberturas, sobras e utilização nunca são persistidos, e mês só nasce por ato de edição — abrir não materializa. Inventário e Patrimônio **não** pertencem a este domínio — são o domínio próprio **Alladin** (roadmap `ALD-*`; agregado `S.alladin` em schema **v6**. O **cadastro está concluído** para Instrument, Asset, Account e CashAccount — leitura, criação, edição e ciclo de status pela interface. O **ledger econômico está iniciado**: `DEPOSIT`, `WITHDRAWAL`, `TRANSFER`, `REVERSAL`, `BUY`, `SELL`, as despesas standalone `FEE` e `TAX` e os ajustes de reconciliação `ADJUSTMENT_CREDIT` e `ADJUSTMENT_DEBIT` (diferença de caixa sem contraparte econômica, com justificativa obrigatória), com saldos de caixa **derivados** do ledger, nunca persistidos. **Existe posição por quantidade derivada** do ledger (`leitura.posicoes()`, identidade instrumento+conta, ALD-04 S1). **Lançamentos, Saldos e Posições já são visíveis na aplicação** (ALD-05 S1): a interface projeta os read-models sem recalcular nada, e um agregado que o domínio recusa aparece como indisponível — nunca como zero ou lista vazia. **Registrar lançamento pela interface existe** (ALD-05 S2): os nove tipos de evento num modal único, validados e gravados exclusivamente pelo domínio — a interface não calcula nada e não inventa campos. **Estornar pela interface existe** (ALD-05 S3): ação por linha nos lançamentos efetivados, com o fato original exibido em somente leitura e toda a economia do estorno copiada pelo domínio — a interface não inverte valor nem quantidade. Editar lançamento não existe e não existirá: o ledger é append-only, e correção se faz por estorno. Holding persistido/consolidado, cost basis, valuation, patrimônio consolidado, P&L e performance **ainda não existem**. Contrato em `docs/architecture/ALLADIN.md`).

### Onboarding e período operacional

Questionário de início em etapas — parâmetros, calibração e a etapa **Base de Dados**, com termo de responsabilidade obrigatório. Simulação estatística de suporte à calibração. Revisão posterior pelo resumo seguro em `Configurações → Parâmetros e Calibração`, que reabre o onboarding em modo de edição sem duplicar campos ou credenciais.

### Notas operacionais

Janela central de Notas com CRUD, pastas, filtros, Markdown e **Trace ID** rastreável, acessível pelo botão flutuante e pelas Configurações, inclusive no HTML portátil. O mesmo controlador apresenta três regiões no desktop, duas progressivas no tablet e uma etapa por vez no celular; uma janela estreita no desktop também usa duas regiões. Notas, pastas e larguras existentes continuam incluídas no backup. O salvamento permanece explícito, com os mesmos contratos de recusa e nova tentativa; rascunhos ficam apenas em memória, com confirmação ao descartá-los e aviso ao sair da página, sem recuperação prometida após recarregar.

A posição proporcional do botão fica em uma preferência local separada, `jpwealth_notes_launcher_position_v1`, com `schemaVersion: 1` e coordenadas `x`/`y` entre 0 e 1. Movimentos e ajustes concluídos confirmam a gravação por releitura; recarregar restaura a posição, e redimensionar apenas a projeta na área disponível. **Restaurar posição** remove somente essa preferência. **Finalizar sessão** também a remove, preservando notas, pastas e larguras; ela não integra o backup financeiro. Contrato local em [NIGHT PENDING RECONCILIATION](docs/work/CHG-NIGHT-PENDING-RECONCILIATION-20260914.md), com cobertura focal em [notes_experience_test.py](tools/notes_experience_test.py).

A apresentação local **APPLE NOTES EXPERIENCE MATCH** mantém o editor único, com toolbars por coluna, lista contínua e área de escrita sem card. Em Configurações → Interface → Notas, Aparência oferece tema próprio ou seguir app, densidade, prévia, sidebar desktop, área de leitura e presets de texto. A prévia é temporária: Salvar aparência confirma por releitura; Cancelar/sair retorna à preferência confirmada. Recusa preserva a prévia para retry, e resultado desconhecido/conflito exige releitura explícita. A chave auxiliar `jpwealth_notes_appearance_v1` não altera `S.mvpNotes` nem o backup, e segue a limpeza auxiliar de Finalizar sessão; notas/pastas/larguras permanecem. Restaurar aparência prepara uma prévia; Restaurar larguras é uma ação separada sobre os três valores canônicos. A sidebar pode ser alternada só nesta abertura pelo botão do cabeçalho. Contrato e limites: [APPLE NOTES MATCH](docs/work/CHG-APPLE-NOTES-MATCH-20260914.md). Esta descrição registra a revisão local em validação, sem antecipar aceite ou integração.


### Central de Configurações

Modal aberta pela engrenagem do cabeçalho, preservando a tela operacional ao fundo:
Aparência, Interface, Editor, base **educacional local pesquisável** (Forex,
glossário, FAQ — sem sinais nem recomendações), Estatuto Operacional, Parâmetros,
e Backup. A pesquisa é declarativa e **não indexa dados
operacionais** do usuário.

### Laboratório de Probabilidade — Galton Board

Em `Research → Laboratório de Probabilidade → Galton Board`, uma placa física
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
(FCR/FEO calculados pela função legada usada no onboarding, ainda divergente do V11). O baseline
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
exige que todos os scripts do [manifest](src/js/manifest.json) também estejam no precache. Durante uma
atualização, o worker novo aguarda o fechamento dos clientes antigos; cada aba
continua usando um build integral, sem combinar HTML novo com scripts cacheados de
outro build. O ícone tem variantes
`Claro` e `Escuro` em `Configurações → Ícone do app` (no iOS é preciso reinstalar o
atalho após trocar). O HTML portátil em `dist/` é **derivado** — destinado a
distribuição de arquivo único, reconstruído por `tools/rebuild_monolith.py`, nunca
editado diretamente.

## Em desenvolvimento e decisões pendentes

- **Dez propostas N3 legadas**, anteriores à adoção documental da V11, aguardam reavaliação formal humana — cada uma tem um ADR aberto em `docs/decisions/` (fatores dos perfis conservadores, fonte canônica de equity do drawdown, gate combinado da Ordem Gênese, bloqueio de stop < 2 ATR, histerese de fase, poda LIFO compulsória, rito da Fase 4, gatilho de quarentena, fator Raiz-N, projeções MEI). **Nenhuma é corrigida silenciosamente**: exigem decisão N3 e branch própria.
- **Dívida estrutural conhecida**: `openOnboardingModal()` concentra ~2 mil linhas; escopo global legado compartilhado; endurecimento CSP ainda pendente de projeto compatível com scripts/PWA; cobertura automatizada mais forte nos fluxos recentes que no núcleo financeiro. Detalhes e estado vigente em `docs/governance/CURRENT-STATE.md`.
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
preflight, estrutura, diff-check, teste do frescor de contexto), **standard** (44 —
inclui a adoção documental V11, navegação NAV-01..NAV-03, smoke, Central de Configurações, Galton
Board, Planejamento FX, cotação USD/BRL, as nove suítes de Finanças Pessoais,
as suítes do Alladin — incluindo o ledger econômico (ALD-03 S1/S2/S3/S4), a posição derivada (ALD-04 S1) e a superfície econômica com criação e estorno de lançamento (ALD-05 S1/S2/S3) — e o protocolo de geração da base e a serialização cross-tab de escrita e a superfície cadastral do Alladin (leitura e manutenção) em Chromium real) e **full** (55 verificações, incluindo segurança de importação/XSS, senha de
investidor, recuperação transacional, reprodutibilidade de build e ciclo do service
worker). O cenário longo
de 10.000 bolas fica em `tools/galton_board_benchmark.py`, fora do tier cumulativo.
Taxonomia e composição em `docs/governance/QUALITY-GATES.md`.

O preflight (`tools/agent_preflight.py`) verifica dois sinais independentes de frescor do contexto: **temporal** (idade da fotografia) e **material** (alterações posteriores à source revision fora dos caminhos de reconciliação contextual), com resultado tri-state em que `UNKNOWN` nunca é tratado como `FALSE`.

## Regra de segurança

Nenhuma IA deve alterar constantes financeiras, fórmulas normativas, migrações de estado, regras de exclusão ou dados reais sem uma tarefa explicitamente delimitada e revisão humana.

## Trabalho com agentes

Todo agente começa por `AGENTS.md`, executa o preflight e usa o mapa em `docs/governance/CONTEXT-MAP.md`. O estado e as pendências registrados em `docs/governance/CURRENT-STATE.md` correspondem à fotografia e à `Source revision` declaradas ali; confronte-as com a revisão examinada antes de tratá-las como atuais. Conversas e handoffs nunca substituem essas fontes. Consulte o inventário e o roteamento em [SKILL-ROUTING](docs/governance/SKILL-ROUTING.md): procedimentos locais `jpw-*` e skills genéricas instaladas no projeto (`repository-architecture`, `agentic-evolution-governance`), com seus limites e fontes preservados. O fechamento de toda mudança material exige veredito explícito de impacto agêntico, conforme `skills/jpw-post-change-audit/SKILL.md`.

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
- `docs/normative/` — Estatuto V11, Anexo Paramétrico e índice de autoridade; organograma auxiliar.
- `docs/decisions/` — ADRs: decisões formais e pendências N3.
- `docs/architecture/` — arquitetura, schema de estado e mapa do código.
- `docs/governance/` — regras para trabalho humano e por IA, estado atual, gates.
- `skills/` — procedimentos locais obrigatórios para agentes do projeto.
- `tests/`, `tools/` — validação, gates, servidor, benchmark e reconstrução do portátil.
- `archive/original/` — original imutável para comparação e recuperação.
- `data/backups/` — backups JSON locais; não versionar dados reais.
- `dist/` — HTML portátil reconstruído (derivado).


A consulta V11 inclui PDF e Anexo no cache da versão do PWA e incorpora seus
originais no HTML portátil. O teste `tools/statute_documentary_test.py` verifica
leitor, consentimento por versão e entrega online/offline com dados sintéticos.

## Dashboard executivo

A visão executiva reúne Forex (risco, apuração e planejamento), Finanças Pessoais
(orçamento, dívida e comparação mensal), Research (estudos e agenda) e Alladin
(contas, saldos por moeda e último lançamento). Atalhos abrem as vistas dos
módulos. Os resumos se atualizam com o render geral e a agenda, sem persistir
dados. A seção inferior “Sistema e atalhos” contém Status do Sistema e Ações rápidas;
onboarding, Estado Operacional, VRM e calendário ficam em Forex > Visão Geral.
Identidades e preferências v6 são preservadas. Áreas ainda não implementadas
são identificadas como tais. A apresentação não homologa o motor financeiro V11.


### Candidate local A10–A13

O default visual dos cinco módulos passa a Dashboard → Research → Forex →
Finanças Pessoais → Alladin. Aparência e Interface → Editor permite qualquer
ordem por Subir/Descer, com prévia, Salvar ordem, Cancelar e restauração só dessa
preferência. Os modos lateral/superior/mobile compartilham a escolha.
A faixa de metadados operacionais aparece exclusivamente no Forex.

O Consolidado e o detalhe do Histórico oferecem **Copiar operação** em texto
puro, como **entrega parcial A12**. A operação pode reunir várias ordens. A cópia distingue entrada/andamento
e finalização e apresenta somente fatos disponíveis; não envia mensagens,
não executa ordens e não muda o estado financeiro. Campos normativos conflitantes
e contexto final não capturado ficam fora da projeção, sem preenchimento fictício.
Lucro Técnico, alavancagem, DD/fase e risco/clearance permanecem pendentes nos
conflitos registrados; saldo book não é equity flutuante, base de retorno não é
saldo final, e cadastro atual não preenche histórico ausente.
Research possui destino próprio para o Laboratório de Probabilidade, cujo jogo
atual é Galton Board. Ao trocar subdestino/módulo ou cobrir o Lab com Configurações,
a mesma simulação fica pausada em memória; voltar exige **Continuar**. Recarregar
não recupera a simulação, somente as preferências persistidas. Contrato e limites em
[CHG-PRODUCT-IMPROVEMENTS-20260911](docs/work/CHG-PRODUCT-IMPROVEMENTS-20260911.md).
Essas mudanças são candidate local, sem aceite humano nem integração nesta etapa.

### Candidate local DESIGN & EXPERIENCE 01

O Comparativo Mensal de Finanças Pessoais apresenta uma curva de 12 meses,
seletores de métrica/mês e leitura textual, preservando a tabela completa.
Meses não registrados ou incompletos permanecem lacunas; zero declarado e
valores negativos permanecem fatos. Alladin permite buscar Lançamentos após
validar o ledger integral, com contagem de resultados e sem mudar a ordem ou
a elegibilidade de estorno. As curvas ligadas ao inspetor do Forex oferecem
seletor de observação, setas no gráfico e toque; cada série informa a data
do ponto consultado, distinguindo expectativa de realizado.

Os acessos dos cards do Dashboard ficam junto aos títulos. Em Forex > Visão
Geral, a prontidão aparece antes das ferramentas de preparação. A busca de
Configurações dispõe de espaço responsivo e, ao abrir um resultado, conserva
a consulta e leva o foco ao conteúdo. No Lab, os comandos principais precedem
o Canvas; os ajustes permanecem abaixo. Essas mudanças de apresentação
preservam A10–A13, incluindo a cópia parcial A12 e a pausa em memória A13.
Não acrescentam métricas financeiras, persistência de domínio ou 3D e não
homologam o motor V11. O estado é candidate local, sem declarar aceite humano,
integração ou publicação; escopo e gates em
[CHG-DESIGN-EXPERIENCE-01-20260912](docs/work/CHG-DESIGN-EXPERIENCE-01-20260912.md).

### Backup local e avisos

Configurações → Dados e Segurança → Backup e Recuperação explica a base local e a pasta de exportação. O JSON completo preserva os dados dos módulos, com cobertura e exclusões descritas; ele não transporta perfil/foto nem todas as personalizações do navegador. Exportação, confirmação humana de backup e gravação local têm estados separados. Falhas do calendário permanecem visíveis nas superfícies que consomem seu cache. A aplicação não promete notificações quando estiver fechada. [Contrato](docs/architecture/DB-STORAGE-GOVERNANCE.md).

### Comunicação in-app reconciliada

O sino reúne as condições existentes dos módulos sem substituir seus avisos ou bloqueios. Backup usa o mesmo estado canônico do Dashboard/Configurações, inclusive data inválida e UNKNOWN. Leitura/histórico da central são transitórios; ler um item não resolve sua causa. Notas mantém posição auxiliar persistente e janela própria. [Contrato da central](docs/architecture/NOTIFICATION-CENTER.md).
