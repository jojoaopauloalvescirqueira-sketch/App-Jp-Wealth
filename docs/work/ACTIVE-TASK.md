# Tarefa ativa — Estudos NoCoda (MVP)

- Data de abertura: 2026-08-13
- `BASE_SHA`: `60070a2` (`main` limpo, após a integração do segundo nível)
- Branch de implementação: `feature/exec-nocoda-studies`
- Nível: **N1** (domínio novo, navegação, formulário) + **N0-V** (workspace e
  estilo) + **N0-D** (teste, contrato arquitetural e reconciliação)
- Autoridade: **A2**. Nenhuma alteração N2/N3 autorizada e nenhuma executada —
  ver a decisão de identidade abaixo, que evitou deliberadamente a faixa N2.
- Git/publicação: branch e implementação autorizadas. **Commit, merge, push e
  deploy não foram executados.**
- Estado: implementação e validação técnica concluídas; aguardando teste manual
  do gestor.

## Divergências entre o pedido e o repositório

| Premissa | Realidade encontrada | Decisão |
|---|---|---|
| A fonte canônica dos instrumentos é `Configurações → Operação → Motor de Lote` (§6) | O Motor de Lote é apenas um renderizador acoplado a `#motorBody`; a fonte em runtime é `S.instruments`, semeado por `DEFAULTS.instruments` e persistido | Ler o domínio, não a tela. Criada `instrumentCatalog()` como provedor mínimo — sem cópia, sem cadastro próprio |
| Associar o estudo ao "identificador estável canônico" do instrumento (§7) | **Não existe campo `id`.** A identidade é o `name` normalizado por `toUpperCase().replace(/[^A-Z0-9]/g,'')` dentro de `instFor()` | Ver abaixo |
| Verificar metadados de precisão/dígitos por instrumento (§25) | Não existem em lugar nenhum do repositório; o único sinal é um `step="0.00001"` fixo no HTML, igual para EURUSD e XAUUSD | Formatter neutro de até 8 casas, como o próprio §25 prevê. Nenhuma tabela de precisão criada |

### Decisão sobre a identidade

O gestor pediu "implemente também o id de instrumento". Foram apresentadas três
formas; a escolhida foi **formalizar o `name` como id canônico**, extraindo a
normalização que já existia para `instrumentId()`.

Justificativa: acrescentar um campo `id` tocaria `DEFAULTS`, `migrate()` e o
estado persistido — faixa **N2**, que exige autoridade A3, backup anonimizado e
teste de compatibilidade —, e criaria **duas** identidades coexistindo, já que
`o.par` das ordens, `QUOTE_CCY`, `FX_MAP` e `usdPerBase()` continuariam
chaveando por `name`. Isso é exatamente a segunda fonte de verdade que o §35 do
próprio pedido proíbe. A formalização entrega identidade explícita e testável
com zero mudança de schema e zero migração.

## Escopo executado

1. Núcleo matemático puro (`10-domain/09-nocoda-geometry.js`) validado contra a
   fixture canônica antes de qualquer código de interface.
2. `instrumentId()` e `instrumentCatalog()` em `10-domain/01-risk-instruments.js`.
3. Agregado `S.nocoda` + `nocodaNormalizeState()` em `migrate()`.
4. Workspace `#execNocoda` e módulo de interface `20-ui/14-nocoda-studies.js`.
5. Quarto destino no submenu do Execution Board, pela faixa genérica existente.
6. `tools/nocoda_test.py` e atualização de `tools/exec_submenu_test.py`.
7. Contrato arquitetural `docs/architecture/NOCODA-STUDIES.md`.

## Fora de escopo — não tocado

Máquina de estados das ordens, `S.phases`, fórmulas, perfis, fases, DD/MDD,
lote, LIFO, stops, quarentena, contabilidade, MEI-JP, Planejamento FX, Motor de
Lote (além de expor a fonte canônica), Central de Configurações. Pips, ATR,
VRM, valor monetário, sinais, scanner, previsão e desenho das 65 linhas ficaram
fora por exigência explícita do pedido.

## Evidência

| Verificação | Resultado | Observação |
|---|---|---|
| `python3 tools/nocoda_test.py` | PASS | Fixture canônica, invariantes, validação, escala, identidade, persistência, backup e não regressão |
| `python3 tools/exec_submenu_test.py` | PASS | Quarto workspace integrado sem regressão |
| `python3 tools/validate_project.py` | PASS | 63 scripts, 393 IDs estáticos, zero duplicados |
| `python3 tools/quality_gate.py --tier full` | ver `CURRENT-STATE.md` | Candidato final |
| Navegador real | NOT_RUN | O gestor ainda não inspecionou a tela |

## Riscos residuais

- A interface do workspace nunca foi inspecionada visualmente por um humano.
- `datetime-local` com `step="1"` normaliza segundos zero para `HH:MM`; é
  comportamento padrão do campo e não perde informação, mas a exibição difere
  levemente do que o MetaTrader mostra.
- Estudos de instrumentos removidos ficam preservados e inacessíveis pela
  interface — por decisão do §8, que dispensa tela de arquivados no MVP.
- As Notas do MVP derivam contexto de `.screen.active` e continuam carimbando
  qualquer workspace do módulo como "Execution Board".
