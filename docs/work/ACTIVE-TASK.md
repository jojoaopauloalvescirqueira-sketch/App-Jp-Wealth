# Tarefa ativa — Segundo nível do Execution Board

- Data de abertura: 2026-08-13
- `BASE_SHA`: `19590249a47c` (`main` limpo, preflight `PASS`)
- Branch de implementação: `feature/nav-exec-submenu`
- Nível: **N0-V** (workspaces e composição) + **N1** (navegação, foco, teclado,
  destino inicial) + **N0-D** (teste, contrato arquitetural e reconciliação)
- Autoridade: **A2**, autorizada pelo gestor após auditoria e plano. Nenhuma
  alteração N2/N3 autorizada e nenhuma executada.
- Git/publicação: criação da branch e implementação autorizadas. **Commit,
  merge, push e deploy não foram executados.**
- Estado: implementação e validação técnica concluídas; aguardando teste manual
  do gestor.

## Estado observado antes da mudança

`section#exec` continha um único filho, `#execWidgetGrid`, com quatro widgets
`[data-layout-card]` e 67 ids internos. O Execution Board não tinha título
próprio, não tinha segundo nível e não expunha superfície pública de UI. A
faixa hierárquica existia só para Planejamento e era integralmente cravada em
`fx`: ids, classes, atributo de item, atributos de raiz, objeto de estado
singleton, `navigateToScreen('fxplan')` e a superfície `window.JPWFx.ui`.

## Divergências entre o pedido e o repositório

Registradas na auditoria prévia e decididas pelo gestor:

| Premissa do pedido | Realidade no disco | Decisão |
|---|---|---|
| "Estudos dos Pivots" existe | Não existe em lugar nenhum — nem tela, nem string, nem registro | Criar destino estrutural vazio |
| "Estudos NoCoda" existe | Grafia real é **Nocuda**; é folha `tool-check` da Central de Configurações | Fora desta branch |
| "Motor de Lote" é destino do Execution Board | Existe como `#motor`, mas foi removido da navegação por decisão registrada em `index.html` e vive na Central por transporte físico de DOM | Migração aprovada, **em branch própria** |

A migração de Motor de Lote e Checklist Nocuda reverte parcialmente uma decisão
registrada e alcança a Central de Configurações, as Ações Rápidas do Dashboard
e o intercept de `01-navigation.js`. Separá-la respeita a regra de uma tarefa
coerente por branch.

## Escopo autorizado e executado

1. Generalizar a faixa do segundo nível para uma superfície compartilhada,
   dirigida por registro, com renomeação para prefixo neutro.
2. Migrar Planejamento para o motor genérico sem mudança de comportamento.
3. Criar os três workspaces do Execution Board como irmãos diretos de
   `section#exec`, alternados por `hidden` + `inert`.
4. Definir Visão Geral como destino inicial do módulo.
5. Teste focado próprio e registro no tier `standard`.
6. Reconciliação documental.

## Fora de escopo — não tocado

Máquina de estados das ordens, `S.phases`, schema, `migrate()`, chaves de
storage, fórmulas, perfis, fases, DD/MDD, lote, LIFO, stops, quarentena,
contabilidade, MEI-JP, Motor de Lote, Checklist Nocuda, Central de
Configurações e regras do Planejamento FX.

## Decisões de implementação e por quê

- **Workspaces como irmãos da `.screen`, nunca `.screen` aninhada.** Quatro
  leitores resolvem `.screen.active` / `closest('.screen')` pelo primeiro nó em
  ordem de documento e passariam a apontar para o nó errado.
- **Fora da `.jp-widget-grid`.** O motor de layout reparenteia todo
  `[data-layout-card]` para filho direto da grade a cada boot e lê apenas
  `:scope > [data-layout-card]`; um wrapper ali seria desfeito em silêncio e
  invalidaria a preferência de layout — o que tornaria a mudança N2.
- **`#exec > [hidden]{display:none}` com especificidade de ID**, porque as
  regras de `.jp-widget-grid` declaram `display` e venceriam o `[hidden]` do
  agente de usuário.
- **Faixa única compartilhada** em vez de uma por módulo: o grid do `<body>`
  tem um slot só, e o estado de aberto no `<html>` acendia todos os
  acionadores. `aria-expanded` no próprio acionador resolve por construção.
- **Destino inicial por `MutationObserver` na classe `.active`**, e não por
  novo wrapper em `navigateToScreen`, que já tem duas camadas cuja ordem não
  deve crescer. Cobre também CTAs e chamadas por string.

## Evidência

| Verificação | Resultado | Observação |
|---|---|---|
| `python3 tools/agent_preflight.py --mode edit` | PASS | branch própria, árvore limpa na abertura |
| `python3 tools/validate_project.py` | PASS | 61 scripts, 392 ids estáticos, zero duplicados, portátil reconstruído |
| `python3 tools/exec_submenu_test.py` | PASS | teste novo, 10 blocos |
| `python3 tools/fx_planning_test.py` | PASS | Planejamento inalterado sob o motor genérico |
| `python3 tools/quality_gate.py --tier full` | PASS 19/19 | executado antes do registro do teste novo e da reconciliação documental; **repetir no candidato final** |
| `git diff --check` | PASS | dentro do gate |

## Riscos residuais

- O gestor ainda não inspecionou as telas renderizadas; toda a evidência é
  programática.
- As Notas do MVP derivam o contexto de tela de `.screen.active` e não conhecem
  sub-visões: uma nota aberta na Visão Geral é carimbada como "Execution
  Board", igual a uma aberta no Painel Operacional.
- Visão Geral e Estudos dos Pivots são superfícies sem conteúdo funcional, por
  decisão explícita — cada uma exige especificação própria.
