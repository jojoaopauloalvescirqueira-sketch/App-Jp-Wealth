# Galeria de avatares — 2026-09-16

Pedido: disponibilizar os 19 retratos enviados como fotos de perfil, com nomes e grupos. A associação entre arquivos e nomes foi fornecida e confirmada pelo proprietário; não decorre de reconhecimento facial.

## Contrato e compreensão

- Base: `056c4690f41170e5deaa3a5037a949a2174b9203`; branch `codex/jp-wealth-profile-gallery-20260916`; raiz `/Users/joaopauloalves/.codex/jp-wealth-profile-gallery/20260916/product`.
- Autoridade: pedido de implementação e confirmação do catálogo nesta conversa; escopo local reversível. Sem commit, push, merge ou deploy. N1 funcional: nova fonte de prévia para o editor existente, sem alteração de schema, escritor, backup, migração ou limpeza.
- O JP Wealth organiza a vida financeira localmente. Esta tarefa personaliza apenas a identidade visual do usuário em Configurações → perfil. `09-settings-modal.js` já oferece upload, rascunho, Salvar/Cancelar, conflito entre abas e invalidação no encerramento. A galeria alimentará o mesmo rascunho e escritor, mantendo o nome de exibição.
- Fontes relidas na base: `AGENTS.md` (preflight e invariantes), `docs/governance/PROJECT-CONTEXT.md` (produto local/PWA), `docs/governance/CONTEXT-MAP.md` (Settings), `docs/governance/SECURITY-MODEL.md` (entradas/cache), `docs/architecture/STATE-SCHEMA.md` (perfil fora do backup), `src/js/40-app/09-settings-modal.js` (perfil), `tools/rebuild_monolith.py` (scripts incorporados), `sw.js` (precache), Harness mestre §§12–14, 28–29, 36–48.
- Consumidores: perfil da sidebar, prévia da conta, fluxo de upload, navegação/rascunho Settings, arquivo portátil e PWA. A galeria contém dados locais estáticos; nenhuma requisição externa ou chave nova.
- Escopo permitido: novo `src/js/40-app/09-profile-avatar-catalog.js`; editor `09-settings-modal.js`; `src/styles/app.css`; registro do script em `index.html`, `src/js/manifest.json`, `sw.js`; teste focal `tools/profile_gallery_test.py`; este contrato e ponteiro em `docs/work/ACTIVE-TASK.md`. Derivados `build-id.js` e `dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html` somente pelo gerador oficial. Evidência e utilitário de ingestão fora do produto.
- Localização: catálogo de dados no mesmo módulo de aplicação do perfil; teste conforme convenção `tools/*_test.py`. KEEP da arquitetura; nenhuma migração de pastas. Gerador, validadores, gates, CI, domínio financeiro, credenciais e outras worktrees preservados.
- Assets: importar os PNG fornecidos pelo mesmo normalizador raster do upload existente (256px JPEG), conservando composição. Armazenar o resultado estático no catálogo para file://, portátil e cache offline. Hash de origem por arquivo no relatório de ingestão. Nomes e categorias são metadados editoriais; não mudam o nome do usuário.
- Critérios: 19 imagens decodificáveis/nomeadas; filtro por grupo e busca; seleção visível e acessível; prévia sem gravação; Cancelar restaura; Salvar/reabrir/recarregar preservam; upload/remoção seguem disponíveis; corrida com upload e encerramento não ressuscita prévia; dados financeiros inalterados; desktop/mobile, claro/escuro, teclado, portátil e offline.
- Verificação: novo teste de galeria; `settings_modal_test.py --only profile`; `finalize_session_test.py --only profile`; estrutura, build reproduzível e tier standard (N1), revisão independente. Resultados registrados separadamente e sem enfraquecer testes.
- Rollback: descartar apenas este delta local a partir da base identificada, após preservar evidência; perfil confirmado usa o formato antigo e continua legível pela base. Nenhum dado real é usado em testes.

## Frescor e gates

Preflight audit/edit: PASS, árvore inicial limpa. O aviso de contexto refere-se a 178 caminhos integrados após a fotografia M1 `fafb228`; este recorte foi cotejado com a base real acima. Histórico de outras campanhas permanece histórico. Candidate local, validação, aceite, commit, integração e publicação são estados separados.

## Catálogo confirmado

Prefixo dos originais: `ChatGPT Image 15 de set. de 2026, `; extensão `.png`, em Downloads.

| Ordem | Arquivo (horário) | Nome | Grupo |
|---|---|---|---|
| 1 | 23_41_47 | Jeremy Siegel | Economia |
| 2 | 23_36_19 | Charlie Munger | Investimentos |
| 3 | 23_40_16 | Peter Lynch | Investimentos |
| 4 | 23_38_43 | Jerome Powell | Economia |
| 5 | 23_58_02 | Murray Rothbard | Economia |
| 6 | 23_48_43 | Donato Bramante | Artes e literatura |
| 7 | 23_37_32 | George Soros | Investimentos |
| 8 | 23_55_13 | J. Robert Oppenheimer | Ciência |
| 9 | 23_42_59 | Nassim Nicholas Taleb | Filosofia e pensamento |
| 10 | 23_47_35 | Dante Alighieri | Artes e literatura |
| 11 | 23_46_07 | Michelangelo | Artes e literatura |
| 12 | 23_53_19 | Ludwig von Mises | Economia |
| 13 | 23_34_43 | Warren Buffett | Investimentos |
| 14 | 23_33_42 | Napoleão Bonaparte | História |
| 15 | 23_32_23 | Adam Smith | Economia |
| 16 | 23_30_49 | Friedrich Nietzsche | Filosofia e pensamento |
| 17 | 23_51_44 | Albert Einstein | Ciência |
| 18 | 23_50_19 | Isaac Newton | Ciência |
| 19 | 23_44_27 | Leonardo da Vinci | Artes e literatura |

## Auditoria e contexto do candidate

AGENTIC IMPACT CHECK: AGENTIC IMPACT DETECTED

BASIS: avaliação IMPACT delimitada à nova fonte de avatar, sem mudar responsabilidades financeiras ou o contrato persistido. O registro da tarefa ativa e o catálogo de scripts passam a representar a galeria; foram atualizados. O ponto de entrada de Settings continua `09-settings-modal.js`, com a fonte estática registrada antes dele. `AGENTS.md`, skills, routing, autoridade e gates não mudam de semântica ou procedimento. `STATE-SCHEMA.md`, `DB-STORAGE-GOVERNANCE.md` e `DATA-RECOVERY.md` continuam corretos quanto ao JPEG v1, limites, backup e encerramento. As fotografias datadas de `CURRENT-STATE.md`, CODE-MAP e handoffs anteriores não são reescritas como se descrevessem esta feature; a tarefa atual é descoberta pelo ponteiro ACTIVE-TASK e por este contrato. Nenhum mecanismo de memória/vetor é alterado ou reindexado. INDEX NOT REQUIRED para este recorte; o aviso histórico de frescor não é tratado como reconciliação global.

| Representação | Impacto | Ação local |
|---|---|---|
| Tarefa ativa/contrato | AFFECTED | Atualizados com escopo e base desta feature |
| Manifest de scripts, HTML e precache | AFFECTED | Catálogo registrado; ordem relativa dos 90 scripts anteriores preservada |
| Bootstrap e mapa de Settings | AFFECTED | NOT_REQUIRED: entrada Settings preservada, catálogo descoberto pelo manifest vigente |
| Contratos de perfil/backup/recuperação | NOT_AFFECTED | NOT_REQUIRED: mesmo envelope, rasterizador, escritor e limpeza |
| Agentes, skills, routing, normas e gates | NOT_AFFECTED | NOT_REQUIRED: nenhuma alteração de autoridade, procedimento ou cálculo |
| Fotografias históricas e índices de memória | NOT_AFFECTED | NOT_REQUIRED: história preservada, sem reindexação |

Revisão independente verificou a associação dos 19 arquivos pelos hashes dos originais e dos JPEGs normalizados. Encontrou um P2: Enter na busca submetia implicitamente o formulário. Correção limitada à tecla Enter no campo de busca; reprodução posterior confirmou prévia pendente e armazenamento intacto. Nenhum achado pendente no recorte auditado. SHA-256 final do editor: `e01bf29378bc2577986650da27c407566f35565bcfac0569147ed651ce081298`.

Build final do runtime: `19edc0b793b93e83`. A suíte focal `profile_gallery_test.py` passou com fingerprint estável em `../evidence/gallery-final/report.json`, incluindo portátil isolado, PWA offline, conflitos, uploads atrasados, teclado e quatro combinações viewport/tema. O portátil mantém uma limitação preexistente de URLs relativas de marca; os retratos da galeria são autossuficientes. Gate geral registrado separadamente em `../evidence/standard.log`, com eventual revalidação focal após mudança material. Este registro não atribui aceite humano, integração ou publicação.
