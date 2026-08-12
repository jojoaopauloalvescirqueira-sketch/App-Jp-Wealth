# Tarefa ativa — Configuração inicial da nota (Notas do MVP, JPW-CBA987)

- Data de abertura: 2026-08-12
- `BASE_SHA`: `228daf9d2598` (`main`)
- Branch autorizada: `feature/mvp-notes-creation-modal`
- Nível: **N1** (fluxo de criação e interface) + **N0-D** (testes e documentação)
- Autoridade: A2 para o escopo N1. Nenhuma alteração N2/N3: o schema de
  `S.mvpNotes` permanece na versão 5, sem migração, sem novo campo persistido e
  sem alteração de backup/importação.
- Git: criação da branch autorizada e executada em 2026-08-12. Commit, push,
  merge e deploy permanecem pendentes de autorização separada.
- Tarefa anterior (Planejamento FX): concluída e integrada à `main`; registro em
  `CHANGELOG.md`, `docs/architecture/FX-PLANNING.md` e no histórico Git.

O estado Git corrente (branch, HEAD e árvore) deve ser confirmado pelo preflight.
Este contrato não substitui fatos mutáveis do disco.

> [!warning] Outra sessão opera o mesmo checkout
> Entre o preflight de abertura (`3c2b398`) e a criação da branch, o HEAD de
> `main` avançou sozinho para `228daf9` (`fc8d2a3` tokens + `228daf9` gitignore).
> Reconfirmar o estado Git antes de qualquer nova edição.

## Objetivo

Fazer os metadados da nota serem decididos **na origem**, não depois. O botão
"+" da gaveta de Notas passa a abrir um modal de configuração inicial ("Nova
Nota") com tipo, prioridade, status inicial, pasta e permissão de IA; o editor
abre em seguida, no mesmo lugar de sempre.

O problema real não era "nota vazia criada" — clicar "+" nunca criou nota: cria
um rascunho em memória, e a gravação sempre foi explícita. O problema é que os
cinco metadados viviam atrás do botão `[•••]` (inspector) e permaneciam no
padrão na prática.

## Decisões vinculantes

1. **Enums reutilizados, não substituídos.** O modal exibe os mesmos
   `MVP_NOTES_TYPE/PRIORITY/STATUS/POLICY_LABELS` já usados pelo inspector.
   Nenhuma categoria nova (Diário/Estudo/Projeto/Ideia não existem no módulo).
2. **Schema plano preservado.** Nenhum agregado `metadata:{}`. Os metadados
   continuam campos de primeiro nível do item, como leem a normalização, o
   backup, a exportação em Markdown e o Trace Reference.
3. **"Sem pasta" é resposta válida** para o campo obrigatório "Salvar em": é
   visão de primeira classe do módulo (`unfiled`) e uma instalação nova nasce
   com `folders: []` — exigir pasta real travaria o primeiro uso do aplicativo.
4. **Modal local à gaveta.** Não reutilizar `#modalOverlay`: irmão anterior de
   `#mvpNotesOverlay` com o mesmo `z-index` (200), renderizaria por baixo do
   drawer e ficaria fora do focus trap do módulo.
5. **A nota continua nascendo só ao Salvar.** "Criar Nota" monta o rascunho e
   abre o editor; `mvpNotesCreate()` segue exigindo a primeira linha como
   título. Cancelar não pode tocar o estado.

## Arquivos permitidos

- `index.html` (markup do modal, dentro de `#mvpNotesDrawer`)
- `src/styles/app.css` (bloco `.mvpn-new-*`)
- `src/js/40-app/14-mvp-notes.js`
- `tools/mvp_notes_test.py`, `tools/smoke_test.py`, `tools/finalize_session_test.py`
- Derivados oficiais: `build-id.js`, `dist/…PORTABLE.html`, `src/js/manifest.json`
- Documentação: `CHANGELOG.md`, este contrato

## Invariantes

- `S.mvpNotes.schemaVersion` permanece 5; nenhuma migração introduzida.
- Nota antiga abre, edita, exporta e importa sem alteração de comportamento.
- Cancelar / `Escape` / clique fora: zero escrita em `localStorage`.
- Escolher metadados no modal não marca o rascunho como sujo.
- O inspector continua sendo a superfície de edição pós-criação.
- Focus trap e `inert` da gaveta preservados; o modal é a camada mais interna.

## Critérios de aceite

- `+` abre o modal; abrir a gaveta ou selecionar nota existente, não.
- Os cinco campos vêm pré-preenchidos com os padrões canônicos.
- "Criar Nota" leva os cinco metadados ao rascunho e, ao Salvar, ao item.
- Desktop (1440×900) e mobile (375×812) verificados no navegador real.
- `python3 tools/quality_gate.py --tier full` sem `PRODUCT_FAIL`.

## Fora de escopo (deliberado)

- Criar pasta a partir do modal.
- Alterar rótulos, enums ou o padrão `analysis_only`.
- Mover metadados para fora do inspector ou removê-lo.
- Qualquer alteração em regra financeira, dashboard ou trading.

## Plano de rollback

Reverter os arquivos permitidos para `228daf9d2598` e reexecutar
`tools/rebuild_monolith.py`. Não há estado persistido novo para desfazer —
nenhuma base salva muda de forma por esta tarefa.

## Resultado do candidato (2026-08-12)

- `tools/quality_gate.py --tier full`: **PASS=19**, nenhum `PRODUCT_FAIL`,
  `TEST_HARNESS_FAIL`, `ENVIRONMENT_ERROR`, `BASELINE_FAIL` ou `NOT_RUN`.
- Defeito encontrado e corrigido durante a verificação: `.mvp-notes-head` é um
  `<header>` e herda `z-index:40` da regra global; com `z-index:4` o modal
  ficava por baixo do cabeçalho da gaveta, que seguia clicável. Corrigido para
  50, contido no contexto de empilhamento do drawer (`position:fixed`).
- Candidato local, não commitado, não enviado, não integrado, não publicado.
