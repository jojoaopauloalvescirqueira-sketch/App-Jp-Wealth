# Tarefa ativa — Exportar e copiar notas em massa (JPW-436587)

- Data de abertura: 2026-08-12
- `BASE_SHA`: `b286610c8b89` (`main`, com JPW-CBA987 integrado)
- Branch autorizada: `feature/mvp-notes-bulk-export-copy`
- Nível: **N1** (ações de leitura e interface) + **N0-D** (testes e documentação)
- Autoridade: A2. Nenhuma alteração N2/N3 — `S.mvpNotes` permanece na versão 5,
  sem migração, sem campo novo e sem qualquer escrita de estado.
- Git: criação da branch autorizada e executada em 2026-08-12. Commit, push,
  merge e deploy permanecem pendentes de autorização separada.
- Tarefa anterior (JPW-CBA987, modal de configuração inicial): concluída,
  integrada em `b286610`. Os dois commits ainda **não foram enviados** ao
  `origin` — `git push` falha neste checkout por ausência de credencial no
  chaveiro; o envio sai pelo GitHub Desktop.

O estado Git corrente deve ser confirmado pelo preflight. Este contrato não
substitui fatos mutáveis do disco.

## Objetivo

Exportar e copiar notas em lote, reduzindo trabalho manual em backup por
contexto, migração, auditoria e processamento por IA.

## Decisões do gestor (2026-08-12, vinculantes)

1. **"Arquivada" = Concluída + Descartada.** O campo `archived` do ticket não
   existe no módulo (auditado: todas as ocorrências de *archived/arquivado* no
   repositório pertencem a operações de trading). Mapeado para
   `status ∈ {done, discarded}`, que ficam de fora.
2. **Markdown, não JSON.** O arquivo não é restaurável e isso é característica
   declarada, não defeito: o único importador existente
   (`normalizeImportedState`) exige um backup completo e rejeitaria um arquivo
   só de notas. Restauração continua sendo função do backup completo da base.
3. **Preâmbulo de governança do lote** (opção 3 da análise): cada nota mantém a
   própria instrução de IA, e o lote abre com a regra de leitura que impede uma
   autorização de atravessar para outra nota.
4. **Escopo = recorte visível**, não a pasta bruta. Decorre do pedido de "ou com
   determinado filtro": `mvpNotesFiltered()` já é esse recorte.

## Decisão técnica assumida (registrada)

**Visão "Concluído" é exceção ao critério 1.** Ali o recorte é inteiramente
concluído e aplicar a exclusão devolveria sempre zero — a ação seria morta numa
visão inteira. As duas ações operam sobre o que está visível, e a contagem no
rótulo e na confirmação torna a diferença explícita.

## Arquivos permitidos

- `index.html` (ações na `.mvp-notes-toolbar`)
- `src/styles/app.css` (bloco `.mvpn-bulk-*` e `align-items` da toolbar)
- `src/js/40-app/14-mvp-notes.js`
- `tools/mvp_notes_test.py`
- Derivados oficiais: `build-id.js`, `dist/…PORTABLE.html`, `src/js/manifest.json`
- Documentação: `CHANGELOG.md`, este contrato

## Invariantes

- Exportar e copiar são **leitura pura**: `S.mvpNotes` idêntico antes e depois.
- Nenhuma chamada de rede.
- `schemaVersion` permanece 5; nenhuma migração.
- Nota legada (sem campos do v5) exporta pelos fallbacks da normalização.
- Rascunho sujo bloqueia as duas ações, como já bloqueia a exportação individual.
- O serializador por nota (`mvpNotesMarkdown`) e o Trace Reference
  (`mvpNotesReferenceBlock`) não são alterados — são reutilizados.

## Critérios de aceite

- Só notas do recorte entram; concluídas e descartadas ficam de fora.
- Contagem no rótulo = contagem levada; confirmação declara visível × levado.
- Casos vazios distinguem "não há nota" de "todas excluídas pelo critério".
- Desktop (1440×900) e mobile (375×812) verificados no navegador real.
- `python3 tools/quality_gate.py --tier full` sem `PRODUCT_FAIL`.

## Fora de escopo (deliberado)

- Importador de arquivo de notas (seria N2 — merge, colisão de `id`/`ticket`,
  resolução de `folderId`). Ticket próprio.
- Formato ZIP: exigiria encoder próprio ou a primeira dependência externa.
- Exportação assíncrona com barra de progresso: `content` é limitado a 20.000
  caracteres e todo o estado vive em `localStorage`; o volume não justifica.
- Campo `archived` real no schema.

## Plano de rollback

Reverter os arquivos permitidos para `b286610c8b89` e reexecutar
`tools/rebuild_monolith.py`. Não há estado persistido novo para desfazer.

## Resultado do candidato (2026-08-12)

- `tools/quality_gate.py --tier full`: **PASS=19**, nenhuma falha.
- Defeito encontrado e corrigido na verificação visual: empate de especificidade
  com a regra de botões do tema `tesla-inspired` (0,3,1) fazia os botões saírem
  em tamanho de controle pleno e truncava o rótulo da visão. Ver `CHANGELOG.md`.
- Candidato local, não commitado, não enviado, não integrado, não publicado.
