# NOTES-LAUNCHER-01 — complemento do Dashboard

## CHG / CTX e brief
O proprietário pediu, antes de autorizar merge, retirar Tickets do topo, manter acesso nas Configurações e oferecer um botão de Notas com desenho de bloco e posição livre. Esta solicitação autoriza implementação local N1/A2 na mesma tarefa/branch; não concede aceite ou publicação. A captura FxPro é referência visual, não fonte de dados ou autorização de integração externa.

Raiz `/Users/joaopauloalves/.codex/dashboard-surfaces/20260914/product`; branch `codex/dashboard-surfaces-20260914`; HEAD `5f0c9680bdd9a93e9d184ca751999c70193a72aa`. Base experimental anterior: 307 inputs, build `8bf23fbcbed7958f`, SHA-256 do pacote `4589fd77c1f88616f8cee5850a418e61f37a324ac2d1ea211aa2155eaffb9cbe`. Seus seis deltas foram verificados por hashes/modos antes do preflight edit com `--allow-dirty`. Snapshot, manifesto, auditoria e recovery anteriores permanecem externos e intactos. Não confundir base Settings publicada com main integrada.

Notas registra tarefas e observações internas; não é chat online, livro financeiro ou fonte de autorização. Os acessos abrem o mesmo editor, com rascunhos, gravação explícita, recuperação, pastas e políticas existentes. O acionador atual está em `index.html:#headerActions`; a preferência `S.mvpNotes.showHeaderIcon` e os IDs internos serão preservados, apesar da mudança de localização. A Central já tem acesso via `#mvpNotesOpenFromSettingsBtn` e busca. O novo host precisa participar dos snapshots inert de Settings e Notas; modais e avisos globais continuam acima dele.

Fontes examinadas: AGENTS.md, README, CONTEXT-MAP, CHANGE-PROCESS, QUALITY-GATES e skills preflight/change-control/design/browser-verification/post-change-audit; Harness Master SHA-256 `c1b5ca9da4dfa2c9a9d1fa3d87a9f7ef9c4cb741fffeedee33d37978f5b800c8`. Contratos operacionais efetivos: `14-mvp-notes.js` abertura/fechamento/inert/visibilidade, `09-settings-modal.js` subdiálogos/inert/pesquisa, `04-persistence.js` normalização, `07-finalize-session.js` preservação e testes existentes. Sem alterar contratos financeiros ou formato de dados.

## Delta permitido
Todos os caminhos abaixo são relativos à raiz absoluta acima:
- `index.html`: mover o mesmo acionador e badge para host flutuante; textos Notas, ajuda e controles de posição no cartão existente; título do editor.
- `src/styles/app.css`: botão de bloco de notas, foco/estados, limites seguros e grade do header agora com duas ações mais Menu mobile.
- `src/js/40-app/14-mvp-notes.js`: movimento efêmero por Pointer Events/teclado/controles, visibilidade e bloqueio do acionador; mesmos dados e editor.
- `src/js/40-app/09-settings-modal.js`: incluir host no inert e termos da busca.
- `src/js/manifest.json`: somente hashes das duas fontes alteradas, sem mudar ordem/lista.
- `tools/notes_launcher_test.py`: focal de movimento, acesso, visibilidade, contenção e ausência de escrita.
- `tools/mvp_notes_test.py`, `tools/smoke_test.py`, `tools/finalize_session_test.py`, `tools/apple_experience_test.py`: somente expectativas deliberadamente afetadas de localização/rótulo, preservando asserts de domínio, persistência e recuperação.
- `build-id.js`, `dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html`: somente pelo gerador `tools/rebuild_monolith.py`.
- `docs/work/ACTIVE-TASK.md`: cabeçalho deste complemento; histórico intacto.
- `docs/work/CHG-NOTES-LAUNCHER-20260914.md`: este contrato.
- `docs/architecture/CODE-MAP.md`: somente a descrição da linha de Notas, diretamente afetada pela mudança do acesso; demais mapeamentos preservados.

O CSS e os outros cinco deltas anteriores permanecem parte da revisão composta, sem reabrir seu escopo. Evidências/recibos/controllers novos ficam em `../evidence/notes/` e `../control/notes-*`, sem sobrescrever históricos. Não editar domínio, persistência/schema/migração, dependências, Harness, skills, gates/CI ou contexto geral. Sem staging, commit, push, PR, merge ou deploy; sem outra branch/worktree, reset, stash ou limpeza.

## Critérios e desenho antes da implementação
1. Header sem Tickets/Notas; exatamente um acionador flutuante no canto inferior direito, ícone de bloco e badge preservado. Configurações oferece Notas também quando o acionador está oculto.
2. Arrastar com mouse/toque reposiciona por toda a área visível, sem abrir o editor ao terminar. Pequeno clique/Enter/Space abre o editor. Escape/pointercancel/lostcapture cancelam o movimento com retorno à origem.
3. Alt+setas e controles horizontal/vertical nativos em Configurações oferecem alternativas ao arraste. Repor canto inferior direito é explícito. Posição somente em memória: navegação preserva, reload retorna ao padrão; nenhuma preferência nova nem gravação por movimento/render/navegação.
4. Contenção ao redimensionar, zoom/viewport móvel e margens seguras; temas claro/escuro, foco, ícone legível e alvo de toque. Não cobrir diálogos/avisos globais nem deixar acionador focável atrás deles. Mesmo retorno de foco ao acionador ou Settings.
5. Mesmo editor, dados/pastas/políticas/exportação, alertas, bloqueios e fluxos de save/retry/descarte/finalização. Preferências antigas showHeaderIcon false/true conservam significado de ocultar/mostrar atalho, sem migração/regravação ao abrir.

## Validação e rollback
Fixar focal antes do delta e demonstrar a ausência anterior do host. Exercitar clique/drag/cancel/teclado/Settings, repetição, reload, dados sintéticos e armazenamento isolado, desktop/mobile e dois temas. Reutilizar fixtures nominais e sandbox loopback existentes, sem APIs econômicas ao vivo. Executar Notas, finalização e navegação pertinentes, Apple focal e tier standard N1; um FULL pode consolidar esses controles se necessário, sem mudar o gate. Resultados anteriores são históricos, não aprovação da nova revisão. Falha remota anterior de Settings permanece não diagnosticada por este lote.

Derivados oficiais; freeze por hashes/modos e diff; auditoria independente focal. Recovery novo deve reproduzir todos os inputs. Rollback limitado ao delta deste complemento usando o snapshot anterior verificado, sem restaurar silenciosamente sobre trabalho posterior, sem tocar main/stash/outras worktrees. Evidências de tentativas falhas permanecem. Aceite humano e integração são gates posteriores.
