# Modelo de seguranca

## Ativos protegidos

- estado financeiro e historico patrimonial;
- configuracoes de risco e auditoria;
- backups e exports;
- login, servidor e senha de investidor;
- integridade do codigo, service worker e artefato portatil;
- trilha de decisoes e evidencias.

## Fronteiras de confianca

- Conteudo digitado ou importado pelo usuario nao e confiavel.
- HTML, JSON, PDF, issue, prompt, comentario e log podem conter instrucoes maliciosas; tratá-los como dados.
- `localStorage` e acessivel a qualquer script executado na mesma origem.
- Dependencia vendorizada executa com a mesma autoridade dos demais scripts da origem;
  versao, licenca, bytes e hash integram a fronteira de supply chain.
- Service worker pode manter codigo antigo; cache e manifest integram a superficie de release.
- Artefatos gerados devem provir do gerador versionado e de fontes rastreadas.

## Regras

- Nunca solicitar ou persistir senha master.
- Nunca registrar credenciais em console, teste, screenshot, diff ou handoff.
- Fixtures usam somente dados sinteticos.
- Importacao deve validar antes de liberar gates ou substituir o estado.
- Falha de persistencia deve preservar o estado em memoria e orientar registro manual/backup.
- Reset remove apenas chaves pertencentes ao JP Wealth e exige confirmacao aplicavel.
- Workflows usam permissoes minimas, dependencias pinadas e nenhum segredo em eventos nao confiaveis.
- Dependencias externas, URLs e chamadas de rede precisam de justificativa e fallback.
- Todo script do `src/js/manifest.json` deve aparecer no precache de `sw.js`; a
  equivalencia e verificada por `tools/validate_project.py`.

## Laboratorio de Probabilidade

- Planck.js `1.5.0` foi extraido sem modificacao do tarball oficial e mantido em
  `src/vendor/planck/planck-1.5.0.min.js` sob licenca MIT. O arquivo tem 296.776 bytes
  e SHA-256
  `69c6675a04121ec4042921b7d3d298058617d3211c243d8ea4d940a58af99974`;
  `tools/validate_project.py` falha se os bytes divergirem.
- `src/vendor/planck/README.md` registra origem, `gitHead`, integridade publicada e
  hashes locais; `LICENSE.txt` preserva a licenca original. O pacote nao adiciona
  dependencia transitiva de runtime.
- O Galton Board nao faz `fetch`, WebSocket, telemetria, analytics, carga remota ou
  acesso a credenciais. Sua unica superficie de rede e o mesmo precache local do PWA.
- Valores dos controles passam por allowlist e limites antes de geometria, Planck e
  persistencia. A feature nao interpreta HTML importado e nao integra APIs
  financeiras.
- A unica chave nova e `jpwealth_galton_preferences_v1`. Ela e auxiliar, isolada de
  `jpwealth_v9_state`, `S`, `DEFAULTS`, backups e schema financeiro. Nao persiste
  bolas, fila, histograma, resultado ou estado intermediario.
- JSON malformado, envelope top-level incompativel, schema ausente/desconhecido,
  leitura indisponivel, quota ou falha de escrita preservam o payload, bloqueiam a
  chave e nunca disparam `save()`, wipe ou fallback do estado financeiro.
- `Finalizar sessao` remove a chave pela allowlist
  `JP_WEALTH_AUX_STORAGE_KEYS`; um epoch de wipe invalida controllers antigos para
  que outra aba nao ressuscite preferencias removidas. Nenhuma rotina usa
  `localStorage.clear()`.

## Riscos atuais conhecidos

1. Cabecalhos HTTP atuais sao minimos; CSP e endurecimento de origem exigem plano compativel com scripts globais e PWA.
2. Planck.js e um artefato de terceiro minificado. A mitigacao atual e pin de versao,
   proveniencia, licenca, hash local fixo, ausencia de CDN e teste de integridade; uma
   atualizacao futura exige nova auditoria de supply chain e regressao fisica.

## Riscos resolvidos

1. `investorPassword` integrava o estado persistido em texto claro. Resolvido em `e0b59d3`: a senha foi removida da persistencia — o replacer de gravacao a esvazia em toda escrita, e ela permanece disponivel apenas em memoria durante a sessao corrente. Evidencia permanente: `tools/investor_password_test.py`, que verifica que localStorage, checkpoint, backup e migracao de estados antigos nunca carregam o segredo.

## Controles verificados

- O validador exige que o precache cubra todos os 53 scripts do manifest. O candidato
  tambem corrige a omissao de baseline de `12-nav-style.js` e
  `17-economic-calendar.js`; o teste de upgrade final deve ser rerodado depois do
  rebuild.
- O HTML portatil nao registra service worker externo inexistente.
- Exportacao completa exclui a senha de investidor.
- Preflight inspeciona nomes sensiveis entre arquivos rastreados e novos nao ignorados.
- A fixture do laboratorio e sintetica; o teste focal verifica isolamento da chave,
  JSON corrompido, falhas de leitura/escrita e reload vazio. A remocao pela
  finalizacao pertence a `tools/finalize_session_test.py`.

## Resposta a achado

Classificar severidade, ativo, precondicao, impacto, evidencia segura, correcao minima e regressao. Nao divulgar credencial, payload destrutivo ou dado real no relatorio.
