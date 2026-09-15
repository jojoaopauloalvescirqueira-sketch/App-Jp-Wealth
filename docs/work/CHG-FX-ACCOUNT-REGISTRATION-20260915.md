# Cadastro obrigatório antes da importação MT5

CHG-FX-ACCOUNT-REGISTRATION-20260915 · CTX-FX-ACCOUNT-REGISTRATION-20260915

## Autoridade, base e compreensão

N2 / A3 para implementação especificamente aprovada pelo proprietário; criação/uso desta branch autorizada separadamente por “Autorizo”. Não concede aceite nem publicação. Raiz: `/Users/joaopauloalves/.codex/forex-consolidated/20260914/product`. Branch: `codex/fx-import-account-registration`. BASE_SHA: `b2f0e54993ff79f7eaab62eba5b37510af43013c`, main remota conferida. Árvore inicialmente limpa e equivalente ao pacote anterior integrado; evidências e recuperação anteriores preservadas em `../evidence/`.

O JP Wealth registra fatos financeiros localmente, com elegibilidade normativa separada. O Consolidado projeta MT5 e Manual sem somá-los. Hoje o catálogo analítico reúne contas atuais e históricas e preenche identificadores ausentes com o histórico; esse catálogo não pode comprovar cadastro atual para uma nova importação. A UI deve permitir ler o documento sem destino, explicar a pendência e salvar uma ficha explicitamente, antes de qualquer confirmação de importação. A implementação atua na fronteira de comandos cadastrais e importação, sem tocar nas fórmulas ou usar cadastro para registrar observações financeiras.

Fontes examinadas no BASE_SHA: `AGENTS.md`; mapas e contexto pertinentes; `17-fx-consolidated-model.js` (validação e vínculos), `24-fx-consolidated-import.js` (prévia, lock e escritor), `28-fx-consolidated.js` (arquivo e confirmação), `08-input-bindings.js`/`04-stop-statistics.js` (cadastros), `00-forex-state.js` (mutação explícita), contratos de persistência/backup/finalização. Harness: Master Specification indicada em AGENTS, SHA-256 `c1b5ca9da4dfa2c9a9d1fa3d87a9f7ef9c4cb741fffeedee33d37978f5b800c8`, §§12–15, 24, 28–30, 36–48. Sem nova decisão normativa.

## Caminhos permitidos

Todos os caminhos abaixo são relativos à raiz absoluta acima (caminho completo = raiz + `/` + entrada):

- `src/js/00-core/04-persistence.js` — somente captura cadastral em fxConsolidatedLongitudinalSnapshot
- `src/js/10-domain/17-fx-consolidated-model.js`
- `src/js/40-app/24-fx-consolidated-import.js`
- `src/js/20-ui/28-fx-consolidated.js`
- `src/js/20-ui/08-input-bindings.js`
- `src/styles/app.css`
- `src/js/manifest.json`
- `build-id.js`
- `dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html`
- `tools/fx_account_registration_test.py`
- `docs/architecture/FOREX-CONSOLIDATED.md`
- `docs/work/ACTIVE-TASK.md`
- `docs/work/CHG-FX-ACCOUNT-REGISTRATION-20260915.md`

O modelo apenas expõe sua validação de relatório já existente para o consumidor cadastral. Matemática intacta. Manifest somente hashes de fontes alteradas, sem reordenação. Derivados exclusivamente por `python3 tools/rebuild_monolith.py`. CTX limita-se a este contrato, cabeçalho ACTIVE-TASK e arquitetura do Consolidado; aviso de contexto histórico não autoriza curadoria geral. Não alterar skills, políticas, Harness, CI, gates ou dependências.

## Invariantes e critérios

- Cadastro atual em S.accounts obrigatório na preparação e sob lock na confirmação. Login textual e plataforma MT5 obrigatórios; demais identificadores quando declarados devem ser compatíveis com documento e vínculo histórico. Ausência opcional mantém a confirmação/limitação existente; não é preenchida por cadastro histórico como prova de cadastro atual.
- Identificação/formato ilegíveis nunca contornados por formulário. Senha não participa.
- Outra conta exige seleção explícita; ambiguidade não escolhe primeiro resultado. Nenhum destino operacional muda.
- Ficha em memória, salvar/cancelar explícitos. Completar somente lacunas; não sobrescrever identificador divergente. Recadastro histórico reutiliza ID mediante confirmação e não restaura saldos ou fatos operacionais.
- Salvar cadastro não importa; confirmação da importação é nova ação. Duplicatas e revisões conservam protocolo existente.
- Recusa comprovada preserva rascunho e reverte somente o ato; UNKNOWN bloqueia retry cego. Lock, epoch, recuperação e escritor existente preservados.
- Campos cadastrais auxiliares de moeda/servidor, quando explicitamente salvos, não são observações financeiras. Sem arquivos originais, senhas, schema/migração, APIs externas ou dados reais.

## Validação fixada antes da transformação

`../evidence/registration-baseline-proof.json`: PRODUCT_FAIL contra o novo requisito (login ausente e conta só histórica aceitos na prévia), sem gravar. Preservar o resultado. Teste focal novo deve repetir esses oráculos, cobrir cadastro válido/ausente/incompleto/divergente, outra conta, múltiplas correspondências, recadastro com mesma identidade/dedupe, cancelamento, quota/retry, UNKNOWN, recarga e alterações concorrentes. Conferir memória, storage, histórico e ausência de importação antes da confirmação. UI: formulário/retorno, foco, teclado e móvel. Reutilizar fixtures e ferramentas existentes.

Depois: regressões Consolidado modelo/storage/UI/PDF e consumidores pertinentes; FULL obrigatório por mecanismo existente, com rede econômica bloqueada e dados sintéticos. Reprodutibilidade/portátil/PWA conforme impacto. Auditoria independente focal antes do freeze final, sem substituir teste por autorrelato. Não repetir evidência válida por formalidade.

## Preservação, recovery e parada

Rollback somente próprio delta desta branch a partir de BASE_SHA e snapshot final externo identificado. Sem reset/stash/limpeza geral; main, worktrees alheias, stash e seis documentos Forex concorrentes preservados. Artefatos sintéticos/evidências em `../evidence/registration-*`; não sobrescrever históricos. Congelar hashes/modos/diff/build, demonstrar recuperação e preparar revisão humana sem inferir aceite.

Parar parte afetada diante de ampliação material, conflito, necessidade normativa, migração ou mudança de protocolo crítico não coberta. A12 parcial, OPEN-05/V11/FCR/FEO, AUD-05/P2 e ausência de HTML real do exportador não são encerrados. Sem staging/commit/tag/push/PR/merge/deploy.

## Complemento focal V2 — identificação na finalização

O plano aprovado inclui preservação de identificadores, backup e finalização. A auditoria F02 demonstrou perda dos novos `platformCurrency`/`platformServer` ao finalizar antes da primeira importação, inclusive quando havia catálogo mínimo criado pela preferência. O candidate V1 `add4aa73f721c9f7d20a95994183941d3734754120e6477d976b35a7f438f190`, seus testes/diff/recovery e AUDIT_FAIL ficam preservados. FULL V1 interrompido após achado, sem ser apresentado como aprovação completa.

Acrescenta-se exclusivamente `src/js/00-core/04-persistence.js:fxConsolidatedLongitudinalSnapshot` à allowlist: transportar metadados textuais explicitamente cadastrados (nome/tipo/login/corretora/moeda/servidor) para catálogo novo ou preencher lacunas compatíveis de catálogo mínimo sem conteúdo importado. Os quatro primeiros já eram capturados para IDs novos; completar lacunas de IDs mínimos preexistentes preserva também o recadastro vindo do histórico Manual. Não substituir valores conhecidos; não enriquecer retrospectivamente a moeda/servidor de relatórios já importados. Nenhuma leitura de saldo ou fatos financeiros. Escritor, protocolos, migrações e schema intactos. Gabaritos antes/depois e finalização real; novos build/fingerprint, FULL e revisão focal. É consumidor diretamente necessário ao plano N2 aprovado, sem ampliação normativa ou de control plane.
