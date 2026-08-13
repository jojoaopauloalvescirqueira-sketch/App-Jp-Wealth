# Estado atual do projeto

- Data da fotografia: 2026-08-13
Source revision representada: `44bae5228d7df9bcd46ede0fa8a3d1a6210cfaff`
- Branch atual: `main`
- Commit de integração: `55d22671c3479b43762922ec01cad454d4e90ac0`
- Estado de integração: implementação commitada e integrada localmente em
  `main`; ainda não enviada ao remoto nem publicada.
- Build local: `4d9b36661c689c26`.
- Validade: qualquer mudança posterior em fonte, manifest, worker, testes ou
  gerados invalida as evidências afetadas e exige repetir o gate proporcional.

## Estado confirmado no disco

- A aplicação continua estática, local-first, sem framework e sem backend
  obrigatório. O runtime permanece em scripts clássicos e globais.
- `src/js/manifest.json` contém 60 scripts, na mesma lista e ordem da base. O
  candidato altera somente hashes dos dois scripts editados. `sw.js`, o HTML e o
  portátil permanecem reconciliados com esse manifest.
- As cinco telas principais compartilham o shell horizontal do protótipo:
  Dashboard, Execution Board, Contas, Contabilidade e Planejamento FX. A
  navegação clássica por sublinhado é o padrão; abaixo de 900 px ela vira uma
  gaveta vertical com os mesmos cinco destinos.
- Dashboard: aviso de governança e cockpit ocupam largura total; Status, VRM,
  Notícias e Ações rápidas formam a faixa P2; Evolução e Ritmo usam razão 3:2;
  motivos, métricas, acompanhamento mensal, drawdown e comparação mensal ficam
  preservados em um único disclosure metodológico.
- Execution Board: clearance compacto com quatro fatos, seguido por Grade e
  monitor LIFO. Indicadores complementares e ATR/VRM continuam acessíveis em
  disclosure. A ordem normativa e todos os IDs consumidos pelo runtime foram
  preservados.
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
- A faixa hierárquica abre transitoriamente por hover e fica fixada por
  clique/Enter/Espaço. Enquanto fixada, não fecha por saída do ponteiro, resize,
  novo clique no acionador ou seleção interna; clique externo e Escape fecham.
  Seu terceiro tom é distinto do header e do contexto em claro/escuro.
- A política PWA não permite mais um cliente utilizável com HTML novo e scripts
  cacheados do build anterior. Enquanto o worker novo está em `waiting`, o
  controller antigo entrega seu próprio `index.html`; a troca só ocorre após o
  fechamento de todos os clientes antigos.
- `build-id.js` e `dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html` foram
  regenerados somente por `tools/rebuild_monolith.py`.

## Escopo e autoridade

- N0-V + N1 + N0-D, autoridade A2: faixa contextual, CSS, responsividade,
  interações de apresentação, teste e documentação arquitetural.
- N2/N3: fora do escopo. `DEFAULTS`, `migrate()`, `schemaVersion`, chaves de
  storage, fórmulas, perfis, fases, DD/MDD, lote, LIFO, stops, quarentena,
  contabilidade, MEI-JP e regras do Planejamento FX não mudaram semanticamente.
- Nenhum dado real, backup, token ou credencial entrou no worktree ou nas
  evidências. Não houve dependência, endpoint ou integração de rede nova.
- Git/publicação: implementação commitada e mesclada em `main` com autorização.
  Push e deploy não foram executados.

## Evidência deste candidato

| Verificação | Resultado | Escopo/observação |
|---|---|---|
| `python3 tools/fx_planning_test.py` | PASS | Estrutura em fluxo, hover transitório, clique fixado, clique externo, teclado, terceiro tom, mobile, quatro modos e ausência de duplicidade. |
| `python3 tools/validate_project.py` | PASS | 60 scripts, 386 IDs estáticos, hashes/ordem coerentes e portátil reconstruído. |
| `python3 tools/quality_gate.py --tier full` | PASS 19/19 | Zero falha e zero `NOT_RUN`; relatório `tools/.artifacts/quality-20260813T160548-full.json`. |
| Navegador real | PASS | 1440×900 e 390×844, claro/escuro; três tons distintos; persistência após novo clique; fechamento externo; sem overflow e console limpo. |
| `git diff --check` | PASS | Sem whitespace errors no candidato congelado antes da reconciliação documental. |
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
