# Estado atual do projeto

- Data da fotografia: 2026-08-13
Source revision representada: `af229ad62e043569dd51b83c2674423c26841d84`
- Branch atual: `main`
- Commit material: `c3c5f21` na branch `feature/exec-nocoda-studies`
- Commit de integração: `af229ad62e043569dd51b83c2674423c26841d84`
- Estado de integração: Estudos NoCoda commitados e integrados localmente em
  `main` com autorização do gestor. **Push não executado nesta sessão** — o
  gestor fará a publicação. O teste manual do workspace continua pendente:
  a autorização de commit foi dada antes dessa inspeção.
- Nota sobre o remoto: o segundo nível do Execution Board (`d2ad73f`, merge
  `83a18dd`, reconciliação `60070a2`) foi para `origin/main` por push externo a
  esta sessão — GitHub Desktop ou outra sessão no mesmo checkout. Nenhum `git
  push` foi executado aqui.
- Build local: `7751a049cfd23dab`.
- Validade: qualquer mudança posterior em fonte, manifest, worker, testes ou
  gerados invalida as evidências afetadas e exige repetir o gate proporcional.

## Estado confirmado no disco

- A aplicação continua estática, local-first, sem framework e sem backend
  obrigatório. O runtime permanece em scripts clássicos e globais.
- `src/js/manifest.json` contém 63 scripts: os 61 anteriores mais
  `src/js/10-domain/09-nocoda-geometry.js` (62) e
  `src/js/20-ui/14-nocoda-studies.js` (63). `sw.js`, o HTML e o portátil
  permanecem reconciliados, e o precache cobre os 63.
- As cinco telas principais compartilham o shell horizontal do protótipo:
  Dashboard, Execution Board, Contas, Contabilidade e Planejamento FX. A
  navegação clássica por sublinhado é o padrão; abaixo de 900 px ela vira uma
  gaveta vertical com os mesmos cinco destinos.
- Dashboard: aviso de governança e cockpit ocupam largura total; Status, VRM,
  Notícias e Ações rápidas formam a faixa P2; Evolução e Ritmo usam razão 3:2;
  motivos, métricas, acompanhamento mensal, drawdown e comparação mensal ficam
  preservados em um único disclosure metodológico.
- Execution Board: segundo nível com quatro workspaces — Visão Geral
  (estrutural), Painel Operacional, Estudos NoCoda e Estudos dos Pivots
  (reservado). O Painel Operacional é o próprio `#execWidgetGrid`: clearance
  compacto com quatro fatos, Grade e monitor LIFO, com indicadores
  complementares e ATR/VRM em disclosure. Nenhum nó foi movido, os 67 ids
  internos e a ordem normativa foram preservados, e os quatro widgets continuam
  filhos diretos da grade. A troca de workspace é `hidden` + `inert`, sem
  desmontar DOM e sem persistir nada.
- Contas: leitura primária em dez colunas, credenciais consolidadas em chip e
  editor completo expansível por conta. As duas tabelas rolam internamente no
  mobile; adicionar uma conta abre o editor e leva o foco ao nome.
- Contabilidade: quatro indicadores no topo, Real vs Projetado e Fechamento
  Diário em razão 3:2, lançamentos em largura total e funções secundárias
  preservadas em disclosures.
- Planejamento FX: o estado vazio é um cartão central de 936 px com formulário
  linear. Os quatro modos agora são selecionados exclusivamente pela segunda
  faixa estrutural do header; as tabs duplicadas saíram do conteúdo sem remover
  renderizadores ou funcionalidades.
- A faixa hierárquica é única e compartilhada (`#navSubShell`), hospedando o
  painel de Planejamento e o do Execution Board; só um módulo fica aberto por
  vez e o aberto é identificado por `aria-expanded` no próprio acionador. Ela
  abre transitoriamente por hover e fica fixada por clique/Enter/Espaço. Enquanto fixada, não fecha por saída do ponteiro, resize,
  novo clique no acionador ou seleção interna; clique externo e Escape fecham.
  Seu terceiro tom é distinto do header e do contexto em claro/escuro.
- A política PWA não permite mais um cliente utilizável com HTML novo e scripts
  cacheados do build anterior. Enquanto o worker novo está em `waiting`, o
  controller antigo entrega seu próprio `index.html`; a troca só ocorre após o
  fechamento de todos os clientes antigos.
- Estudos NoCoda: workspace do Execution Board que guarda três âncoras por
  instrumento e deriva o range −1→0 e o da subdivisão 0,125. Os instrumentos vêm
  de `instrumentCatalog()`, derivado de `S.instruments` — não há catálogo
  próprio. A identidade é `instrumentId()`, o `name` normalizado que já era a
  chave de facto; **nenhum campo novo entrou no catálogo**. O agregado
  `S.nocoda` guarda somente causas; geometria nunca persiste. Contrato em
  `docs/architecture/NOCODA-STUDIES.md`.
- `build-id.js` e `dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html` foram
  regenerados somente por `tools/rebuild_monolith.py`.

## Escopo e autoridade

- N1 + N0-V + N0-D, autoridade A2: domínio NoCoda, workspaces do Execution
  Board, faixa contextual compartilhada, CSS, interações de apresentação, teste
  e documentação arquitetural.
- `DEFAULTS` e `migrate()` receberam o agregado ADITIVO `S.nocoda` com guarda
  estrutural própria — chave nova com default vazio, sem tocar nenhum agregado
  existente e sem migração de dado do operador. A identidade de instrumento foi
  formalizada em função (`instrumentId`) sem acrescentar campo ao catálogo,
  decisão tomada justamente para não entrar em faixa N2.
- N2/N3: fora do escopo. Chaves de storage existentes, fórmulas, perfis, fases,
  DD/MDD, lote, LIFO, stops, quarentena, contabilidade, MEI-JP e regras do
  Planejamento FX não mudaram semanticamente.
- Nenhum dado real, backup, token ou credencial entrou no worktree ou nas
  evidências. Não houve dependência, endpoint ou integração de rede nova.
- Git/publicação: branch, implementação, commit e merge autorizados e
  executados. Push e deploy ficam com o gestor.

## Evidência deste candidato

| Verificação | Resultado | Escopo/observação |
|---|---|---|
| `python3 tools/nocoda_test.py` | PASS | Teste novo: fixture canônica da especificação, rejeição explícita de `abs(P3−P1)` e `abs(P3−P2)`, invariantes P0(T1)=P1 / P0(T2)=P2 / P(−1,T3)=P3, canal horizontal, âncora sobre a linha, interpolação e extrapolação, sinais, seis casos de validação com caso de controle, NaN/Infinity, escala de 65 níveis sem deriva, contagem 8/9, identidade de instrumento, ausência de símbolo hardcoded, seletor derivado, cálculo sem persistir, salvar/recarregar, segundos preservados, `updatedAt`, isolamento entre instrumentos, ciclo de backup, ausência de mutação operacional, estudo preservado após remoção do instrumento e três formas de estado antigo ou malformado. |
| `python3 tools/exec_submenu_test.py` | PASS | Quarto workspace integrado sem regressão do segundo nível. |
| `python3 tools/fx_planning_test.py` | PASS | Planejamento inalterado. |
| `python3 tools/validate_project.py` | PASS | 63 scripts, 393 IDs estáticos, zero duplicados, hashes/ordem coerentes e portátil reconstruído. |
| `python3 tools/quality_gate.py --tier full` | PASS 21/21 | Candidato final, com `nocoda` registrado no tier `standard`. Zero falha e zero `NOT_RUN`; relatório `tools/.artifacts/quality-20260813T223459-full.json`. |
| Navegador real | NOT_RUN | O gestor ainda não inspecionou o workspace; toda a evidência é programática. |
| `git diff --check` | PASS | Dentro do gate. |
| Build reproduzível | PASS dentro do full | `build-id.js` e portátil derivam das fontes oficiais. |

Relatórios locais ficam em `tools/.artifacts/` e são ignorados pelo Git. Usar
somente o artefato cuja árvore corresponda ao estado examinado.

## Impacto agêntico e reconciliação

`AGENTIC IMPACT CHECK: AGENTIC IMPACT DETECTED`

`BASIS:` o changeset cria um contrato arquitetural reutilizável de navegação,
altera o shell descrito no mapa do código e muda a representação operacional
consumida por preflight, skills e agentes. Portanto a camada agêntica é
alcançada mesmo sem alterar agente, skill ou routing.

Naturezas do changeset:

- **MATERIAL:** runtime visual e interação hierárquica de navegação.
- **RECONCILIAÇÃO:** contrato arquitetural, contexto, changelog e handoff.

| Categoria | Impacto | Ação local | Evidência/estado |
|---|---|---|---|
| `AGENTS.md`, `CLAUDE.md` e autoridade | AFFECTED | NOT_REQUIRED | As regras existentes já exigem preflight, escopo, browser real, gate e reconciliação; nenhuma instrução contradiz o contrato novo. |
| Skills e routing | AFFECTED | NOT_REQUIRED | `jpw-browser-verification`, `jpw-test-triage`, `jpw-post-change-audit` e `agentic-evolution-governance` já cobrem o fluxo e herdam o contexto canônico. |
| Bootstrap/preflight e manifest | AFFECTED | REQUIRED | Manifest preserva lista/ordem e atualiza somente hashes dos scripts de UI modificados. |
| Contexto operacional | AFFECTED | REQUIRED | `ACTIVE-TASK`, este `CURRENT-STATE` e `SESSION_HANDOFF` representam o candidato. |
| Arquitetura/contratos de interface | AFFECTED | REQUIRED | `NAVIGATION-HIERARCHY.md`, `CONTEXT-MAP.md` e `CODE-MAP.md` registram o padrão. |
| Gates e evidência | AFFECTED | REQUIRED | Teste focal cobre os estados transitório/fixado, estrutura, acessibilidade e mobile. |
| Changelog e inventário | AFFECTED | REQUIRED | Entrada Unreleased e `PROJECT-FILES.txt` registram o novo contrato. |
| Norma, schema e ADRs N3 | NOT_AFFECTED | NOT_REQUIRED | Nenhuma regra financeira, estado persistido ou decisão normativa mudou. |
| Índice/vetor/memória de projeto | NOT_AFFECTED | NOT_REQUIRED | `INDEX NOT REQUIRED`: o projeto não usa índice/vetor derivado para esses documentos. |

Resultado: `SYSTEM RECONCILED` para o blast radius estrito deste changeset. Não
há propagação multi-projeto nem reindexação a executar. Permanecem drifts
documentais preexistentes em `ARCHITECTURE.md` e `SECURITY-MODEL.md` (contagens
anteriores de scripts) e na tabela de superfície de `FX-PLANNING.md`; esses
arquivos não foram autorizados nesta tarefa e não descrevem o novo lifecycle
nem a nova composição visual.

## Contratos N2 vigentes e inalterados

- A chave financeira principal continua `jpwealth_v9_state`; estados antigos
  passam por `migrate()` e não são substituídos silenciosamente por `DEFAULTS`.
- `investorPassword` permanece apenas em memória da sessão.
- Preferência Galton continua isolada em `jpwealth_galton_preferences_v1`.
- O agregado aditivo `S.fxPlanning` e sua auditoria permanecem inalterados;
  derivados não são persistidos e campos desconhecidos são preservados.
- O service worker não limpa `localStorage`, não força takeover e não remove
  caches de outras aplicações.

## Pendências normativas bloqueantes

Não corrigir silenciosamente. Cada item exige decisão/confirmação N3 e branch própria:

1. Perfis conservadores no código usam fatores revogados (66/50/33) em conflito com a tabela V10 (53/40/27).
2. `compute()` deriva drawdown do risco programado e perdas realizadas, não da equity oficial ao vivo.
3. Ordem Gênese não aplica de forma combinada o teto de risco e o de alavancagem.
4. Stop abaixo de 2 ATR é classificado, mas não bloqueado.
5. Downgrade não aplica integralmente histerese de 0,50 ponto percentual e confirmação H4.
6. Gatilho compulsório de poda LIFO em +1,00 ponto percentual não está implementado.
7. Fase 4 permite inclusão operacional sem todo o rito de salvaguarda previsto.
8. Quarentena/guilhotina depende de formalização manual e não de uma fonte autoritativa de equity.
9. Fator padrão do Stop Raiz-N aparece como 1,8, enquanto a norma atual indica 1,25.
10. Projeções MEI por perfil precisam de decisão sobre memória de cálculo e aderência normativa.

## Dívida e riscos residuais

- A primeira atualização partindo de um worker publicado antes da nova política
  ainda obedece ao código antigo já instalado; fechar todas as abas/clientes da
  origem conclui essa transição. Não limpar storage nem dados financeiros.
- A verificação visual manual usou o estado vazio; os quatro modos com plano e
  a remoção das tabs duplicadas são cobertos por `fx_planning_test.py`, sem dados
  reais.
- `openOnboardingModal()` continua concentrando aproximadamente duas mil linhas;
  o escopo global legado e a CSP não documentada permanecem dívidas anteriores.
- A cobertura automatizada continua mais forte nos fluxos recentes do que no
  núcleo financeiro legado.

## Regra de atualização

Quem alterar fonte, teste, manifest, worker ou gerado depois deste checkpoint
deve repetir as verificações afetadas. Não remover uma falha porque deixou de
aparecer em um teste; registrar causa, comando, candidato e evidência.
