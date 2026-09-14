# Governança de armazenamento da base (JPW-HJFGDE)

## Confiabilidade e cobertura — NIGHT PENDING RECONCILIATION

A base ativa é `localStorage[jpwealth_v9_state]`, isolada por perfil do navegador e origem. O aplicativo identifica store/chave, mas não conhece um caminho físico estável do banco do navegador. A pasta configurada recebe exportações, não saves contínuos.

`dgBackupCoverage` em `src/js/30-accounting/01-daily-ledger.js` informa as chaves efetivamente incluídas no clone integral de `S`, build e exclusões no envelope existente `jpwealth_full_backup`/`V9.1`. Não há novo schema financeiro, hash criptográfico do arquivo ou promessa de exportar todo o perfil do navegador. Dados e históricos registrados de Forex, PF, Alladin, NoCoda, Pivots e Notas são incluídos. A remoção de `investorPassword` também cobre extensões que usem esse nome de campo.

| Classe | Fonte | Tratamento |
|---|---|---|
| BACKUP DATA | `S` / `jpwealth_v9_state` | Clone integral; senhas removidas; desconhecidos preservados proporcionalmente |
| AUXILIARY PREFERENCE | perfil/foto, launcher, navegação/layout/ícone, Laboratório e associação local da pasta | Não transportadas pelo backup de dados; capacidade de pasta exige autorização local |
| EPHEMERAL | caches públicos, código offline, controles entre abas, rascunhos/simulação em memória | Fora do backup; controles podem ser duráveis, embora não sejam dados de domínio |
| UNRESOLVED | portabilidade de override técnico da fonte econômica | Continua local/excluído; nenhuma nova integração |

Confirmação explícita e registro de exportação usam `dgCommitGovernance`: recusa comprovada restaura somente a seção de governança e seu log. Releitura divergente/indisponível levanta UNKNOWN, sem tentar resolver por nova gravação. A apresentação `dgPersistenceStatus` distingue disponibilidade de gravação de prova de que rascunhos estão salvos. `dgBackupStatus` é compartilhado por Dashboard/Settings/reminder, mantendo o prazo existente de 30 dias e separando confirmação histórica de atualidade. O log é resumido, limitado a 400 registros; não conta toda edição nem prova ausência de mudanças.

Download iniciado não é confirmação física do arquivo. Pasta mock/nativa com `close` resolvido é separada do registro local da exportação. Se a escrita na pasta lança, seu resultado pode ser desconhecido: não há fallback automático nem autorização para finalizar a sessão. O aviso exige conferir o destino antes de repetir. A camada de filesystem e seu protocolo não foram alterados.

Importação valida formato/versão quando informados, objeto de estado e contêineres presentes incompatíveis antes da aplicação. Agregados ausentes em legado continuam aceitos pelo normalizador existente; campos desconhecidos não são descartados por uma whitelist. O schema futuro Alladin continua sob seu contrato fail-closed. Recusa comprovada da aplicação preserva o estado anterior; UNKNOWN preserva a barreira, sem checkpoint de sucesso ou retry cego. Importar substitui a base principal, não as preferências auxiliares do destino.

## Princípio arquitetural

Separação obrigatória entre duas coisas que nunca se misturam:

```text
METADADOS LÓGICOS DA PASTA          DIRETÓRIO REAL + PERMISSÃO
(S.dataGovernance.storage)          (FileSystemDirectoryHandle)
viajam na base e no backup    ≠     vive SÓ neste navegador,
                                    em IndexedDB (jpwealth_fs)
```

Um caminho gravado como texto **nunca** concede acesso ao filesystem. Um backup
importado em outra máquina informa qual pasta *era* usada ("Pasta anteriormente
configurada") e a reassociação exige novo gesto do operador ("Localizar esta pasta").

## Schema — agregado `S.dataGovernance` (v1)

```json
{
  "schemaVersion": 1,
  "responsibility": {"accepted": false, "acceptedAt": "", "version": 1},
  "storage": {"configured": false, "folderName": "", "folderDisplayPath": "", "configuredAt": ""},
  "export": {"lastSequence": 0, "lastExportAt": "", "lastExportFile": ""},
  "backup": {"lastConfirmedAt": "", "lastConfirmedExportSequence": 0},
  "changeLog": []
}
```

- Migração: `dgNormalizeState()` (04-persistence.js), chamada por `migrate()`. Base
  antiga sem o agregado recebe os defaults acima — sem perda, sem invenção de dado.
- `changeLog`: auditoria RESUMIDA `{id, ts, entity, action, recordId, label}`, podada
  em 400 entradas. Não guarda snapshots. O `transitionLog` normativo continua intacto.
- O envelope do backup (`tipo`, `versao`, `localStorageKey`, `state`…) **não mudou**.

## Módulos

| Arquivo | Papel |
|---|---|
| `src/js/00-core/03-default-state.js` | `DEFAULTS.dataGovernance` + `DEFAULT_START_ROUTE='dash'` |
| `src/js/00-core/04-persistence.js` | `dgNormalizeState`, `dgLogChange`, `dgChangesSinceLastBackup`, `dgBackupAgeDays/Due`, `dgConfirmBackup`, `dgExportFileName` |
| `src/js/00-core/06-storage-fs.js` | IndexedDB do handle, `dgFsSupported/Status/PickFolder/VerifyAccess/FileExists/WriteFile`, permissões |
| `src/js/30-accounting/01-daily-ledger.js` | `exportFullBackup()` async orquestrado + `buildFullBackupPayload` + `dgRegisterExportSuccess` |
| `src/js/40-app/16-storage-governance.js` | cartão da Central, diálogo de recuperação, painel do onboarding, aviso de 30 dias |

## Regras centrais

1. **Nomenclatura progressiva** (§8): `JP_WEALTH_DB_NNNNNN_AAAA-MM-DD_HHmm.json`.
   Sequência de 6 dígitos, ordenável, data/hora local.
2. **Sucesso ⇒ estado** — nunca o contrário: `lastSequence` só avança depois de
   `createWritable().close()` (pasta) ou do disparo do download (Downloads). Falha não
   deixa rastro de sucesso.
3. **Colisão nunca sobrescreve** (§8.3): `getFileHandle({create:false})` sonda o nome;
   em colisão a sequência avança até nome livre.
4. **Nunca fallback silencioso** (§7): pasta configurada inacessível → diálogo com
   *Reautorizar pasta* / *Escolher outra pasta* / *Exportar excepcionalmente para
   Downloads* / *Cancelar*. Downloads só por escolha explícita.
5. **Exportação ≠ backup confirmado** (§9): confirmar exige gesto + `confirm()`.
   Aviso após 30 dias sem confirmação (`dgBackupDue`), com contagem de alterações.
6. **Estado sem base** (§12): wipe, Finalizar Sessão e base vazia navegam para
   `DEFAULT_START_ROUTE` — fonte única, sem hardcode espalhado. O handle local é
   removido junto com a base (nunca reassocia sozinho uma base futura).
7. **Não-prova ≠ prova de ausência.** Quando uma gravação pode ter ocorrido e não
   é possível provar nem que ocorreu nem que não ocorreu, o desfecho é `UNKNOWN`
   — um terceiro estado, e não um `false`. É a contrapartida da regra 2: se
   "sucesso ⇒ estado" impede declarar sucesso sem prova, esta impede declarar
   fracasso sem prova. A equivalência implícita *"não consegui confirmar que
   gravou" = "não gravou"* produzia perda silenciosa: o disco ficava com a
   finalização, a memória era revertida, e a gravação seguinte apagava o que
   havia sido persistido.
   No `UNKNOWN` nada é revertido, nada é declarado e **toda gravação futura é
   vetada** por barreira própria (`jpWealthPersistenceOutcomeUnknown`), separada
   do portão genérico e **não liberável** por `resumeJPWealthPersistence()` — que
   é reaberto por importação e por onboarding, e nenhum dos dois pode decidir
   sobre um desfecho que ninguém conhece. Não existe função pública de liberação:
   o desempate é humano, com o disco à vista. A barreira não é persistida, porque
   persisti-la exigiria justamente a gravação vetada.
8. **Termo de responsabilidade** (§5): etapa 07 do onboarding; sem o aceite o
   confirmar não conclui. Registro em `responsibility` com carimbo original
   preservado em reedições.

## Estados da pasta (`dgFsStatus`)

`unsupported` · `unconfigured` · `authorized` · `prompt` (reautorizar) ·
`denied` · `missing` (metadado sem handle local, ou nome divergente — base importada
de outro dispositivo).

## Compatibilidade de navegador

`showDirectoryPicker` + handles persistentes: **Chrome/Edge desktop apenas**.
Safari (macOS/iOS) e Firefox caem no fallback: exportação tradicional para Downloads
com nomenclatura progressiva, sequência e controle de backup preservados; a interface
declara a limitação. Dentro de Downloads o navegador sufixa `" (1)"` em colisão de
nome (comportamento nativo; nunca sobrescreve).

## Testes

- `tools/storage_governance_test.py` (Playwright): schema, gate do termo, sequência
  só-após-sucesso, colisão (mock), diálogo de recuperação, Escape, 30 dias, banner,
  migração legada, wipe→rota e persistência entre sessões.
- O seletor nativo de pasta não é automatizável — checklist manual abaixo.

### Checklist manual (Chrome/Edge desktop)

1. Nova base → etapa 07: marcar o termo; **Selecionar pasta** e escolher um diretório.
2. Exportar backup → arquivo `JP_WEALTH_DB_000001_…` aparece NA PASTA, não em Downloads.
3. Exportar de novo → `000002`, sem sobrescrever.
4. Recarregar o app → Central mostra *Acesso autorizado* sem novo prompt (mesma máquina).
5. Nas permissões do site, remover o acesso ao filesystem → exportar → diálogo de
   reautorização (não vai para Downloads sozinho).
6. Renomear/mover a pasta no Finder → *Verificar acesso* acusa falha; exportar abre o
   diálogo.
7. Importar o backup em OUTRO navegador/perfil → Central mostra *Pasta anteriormente
   configurada* + *Localizar esta pasta*.
8. Cancelar o seletor de pasta → nada muda de estado.
9. Safari: cartão declara a incompatibilidade; exportação cai em Downloads com nome
   progressivo.

## Política de segredos (2026-08-09)

A senha de investidor (`investorPassword`) **não é persistida em nenhum armazenamento
do JP Wealth**. Ela pode existir em memória durante a sessão para as validações de
conexão; some no recarregamento.

Proibido, por implementação (não por convenção):

- `localStorage` — `save()` grava o campo sempre vazio (replacer no stringify);
- `sessionStorage` — o fingerprint/checkpoint de Finalizar Sessão exclui o campo;
- backup — `dgBuildBackupBlob()` remove incondicionalmente; `segredosIncluidos:false`
  é permanente e a antiga pergunta "incluir senhas?" foi removida;
- estados/backups antigos — `migrate()` aceita a estrutura e descarta o segredo no
  carregamento, sem eco, sem changeLog, sem console;
- IndexedDB, URL e Git — nenhum caminho de escrita existe.

Não há criptografia caseira: ausência de persistência foi escolhida no lugar de
cifra sem gerenciamento de chave. Qualquer retorno de persistência exige desenho
N2 aprovado com secret store real.

### Regra para futuras integrações MT5/cloud

| superfície | segredo MT5 |
|---|---|
| navegador (qualquer armazenamento) | ✕ nunca |
| backup JP Wealth | ✕ nunca |
| contexto de IA (Claude/agentes) | ✕ nunca |
| banco analítico futuro | ✕ nunca |

Integração futura com MetaTrader/corretora deverá manter credenciais exclusivamente
em secret store/backend/VPS dedicados, fora do app e fora deste repositório.

## Inventário focal de stores/chaves (2026-09-14)

`EPHEMERAL` designa runtime/cache/controle fora do backup, não garante volatilidade física; o epoch é durável. Associação local de pasta é classificada como AUXILIARY PREFERENCE com capacidade não portátil.

| Store / chave real | Classe | Produtor e consumidor no código | Inclusão/exclusão por contrato | Limites |
|---|---|---|---|---|
| localStorage · `jpwealth_v9_state` | BACKUP DATA | [src/js/00-core/04-persistence.js](../../src/js/00-core/04-persistence.js:2) produtor `save()`/`load()`; [src/js/30-accounting/01-daily-ledger.js](../../src/js/30-accounting/01-daily-ledger.js:179) export/import; [src/js/40-app/07-finalize-session.js](../../src/js/40-app/07-finalize-session.js:626) substituição de sessão; [src/js/40-app/09-settings-modal.js](../../src/js/40-app/09-settings-modal.js:445) diagnóstico; [src/js/10-domain/11-operation-lifecycle.js](../../src/js/10-domain/11-operation-lifecycle.js:289) sonda de confirmação | Incluído: clone completo de S em `state`, com exclusão das senhas de investidor e carimbo da própria exportação na cópia. | Banco primário do aplicativo. Pasta de exportação não o substitui; transação/normalização/importação não foram executadas neste mapa. |
| localStorage · `jpwealth_v9_state_corrompido_<Date.now()>` | BACKUP DATA | [src/js/00-core/04-persistence.js](../../src/js/00-core/04-persistence.js:71) produtor recuperação/cópia bruta; [src/js/00-core/04-persistence.js](../../src/js/00-core/04-persistence.js:1482) download explícito; [src/js/40-app/07-finalize-session.js](../../src/js/40-app/07-finalize-session.js:474) consumidor limpeza autorizada | Excluído do backup completo; download da cópia de recuperação é fluxo próprio. | Pode ser JSON inválido/legado; não equivale a S validado. Falha ao duplicar mantém raw em RAM; não promete cópia durável. Não ler nenhum raw real. |
| localStorage · `jpw_rail` | AUXILIARY PREFERENCE | [src/js/20-ui/02-sidebar.js](../../src/js/20-ui/02-sidebar.js:3) leitura/controle da barra; [src/js/40-app/07-finalize-session.js](../../src/js/40-app/07-finalize-session.js:5) limpeza | Excluído de S e backup. | Escolha collapsed/expanded por navegador; Finalizar inclui na allowlist. |
| localStorage · `jpw_expl` | AUXILIARY PREFERENCE | [src/js/20-ui/09-contextual-help.js](../../src/js/20-ui/09-contextual-help.js:40) leitura/controle de ajuda; [src/js/40-app/07-finalize-session.js](../../src/js/40-app/07-finalize-session.js:5) | Excluído de S e backup. | Ajuda on/off; erro de storage é tratado localmente, sem prova de backup. |
| localStorage · `jpw_fs` | AUXILIARY PREFERENCE | [src/js/20-ui/10-font-scale.js](../../src/js/20-ui/10-font-scale.js:6) leitura/escala tipográfica; [src/js/40-app/07-finalize-session.js](../../src/js/40-app/07-finalize-session.js:5) | Excluído de S e backup. | Escala visual; não confundir com IndexedDB jpwealth_fs. |
| localStorage · `jpw_nav` | AUXILIARY PREFERENCE | [src/js/20-ui/12-nav-style.js](../../src/js/20-ui/12-nav-style.js:17) navStyleValue/controle da Central | Excluído por contrato explícito no cabeçalho do módulo. | Estilo visual. Não aparece na allowlist atual de Finalizar. |
| localStorage · `jpw_nav_layout` | AUXILIARY PREFERENCE | [src/js/20-ui/12-nav-style.js](../../src/js/20-ui/12-nav-style.js:172) initNavLayoutChoice/mountNavigationLayout | Excluído: composição por navegador, fora de S. | sidebar/topbar; valor inválido preservado enquanto se exibe fallback. Não incluído na allowlist de Finalizar. |
| localStorage · `jpw_nav_order` | AUXILIARY PREFERENCE | [src/js/20-ui/12-nav-style.js](../../src/js/20-ui/12-nav-style.js:200) navOrderRead/ato de save com releitura | Excluído: ordem visual por navegador, fora de S e do envelope de widgets. | Identidades dos mesmos cinco primários. Não incluído na allowlist de Finalizar. |
| localStorage · `jpwealth_v9_icon_choice` | AUXILIARY PREFERENCE | [src/js/40-app/06-app-icons.js](../../src/js/40-app/06-app-icons.js:8) ícone da aplicação; [src/js/40-app/07-finalize-session.js](../../src/js/40-app/07-finalize-session.js:5) | Excluído de S e backup. | Escolha primary/secondary válida; Finalizar remove. |
| localStorage · `jpwealth_v9_icon_theme` (legada) | AUXILIARY PREFERENCE | [src/js/40-app/07-finalize-session.js](../../src/js/40-app/07-finalize-session.js:5) somente limpeza atual; sem produtor/leitor ativo encontrado | Excluído; chave legada mantida na allowlist. | Não inventar reativação ou migração a partir do nome. |
| localStorage · `jpwealth_local_profile_v1` | AUXILIARY PREFERENCE | [src/js/40-app/09-settings-modal.js](../../src/js/40-app/09-settings-modal.js:61) perfil/foto locais, leitura151 e escrita306; [src/js/40-app/07-finalize-session.js](../../src/js/40-app/07-finalize-session.js:5) | Excluído: perfil e foto não pertencem a S/backup financeiro. | Envelope local versionado, validação/releitura; Finalizar invalida controlador e remove chave. Nenhuma foto foi acessada. |
| localStorage · `jpwealth_notes_launcher_position_v1` | AUXILIARY PREFERENCE | [src/js/40-app/14-mvp-notes.js](../../src/js/40-app/14-mvp-notes.js:759) read/persist/reset; [src/js/40-app/07-finalize-session.js](../../src/js/40-app/07-finalize-session.js:5) limpeza e invalidação | Excluído: schemaVersion1,x/y entre0 e1 fora de S. | Movimento concluído confirma por releitura; reset remove só a chave. Cancel/resize/reopen não devem gravar. Preserva extensão v1 compatível; bloqueia leitura/desfecho desconhecido. Guardas epoch/mainraw usam protocolo existente. |
| localStorage · `jpwealth_galton_preferences_v1` | AUXILIARY PREFERENCE | [src/js/40-app/18-galton-board/06-controller.js](../../src/js/40-app/18-galton-board/06-controller.js:5) adaptador target.getItem/setItem em52–71; [src/js/40-app/07-finalize-session.js](../../src/js/40-app/07-finalize-session.js:5) | Excluído: parâmetros do Laboratório, fora de S. | Não contém bolas, trajetórias/histograma em execução. O call-sites literal não capturava este adaptador; incluído por busca ampliada. |
| localStorage · `jpwealth.ui.widgetLayouts.v6` | AUXILIARY PREFERENCE | [src/js/40-app/13-dashboard-layout.js](../../src/js/40-app/13-dashboard-layout.js:196) chave; save311/load421; consumidor projeção visual das telas | Excluído: envelope local version6/screens/widgets. | Layout visual não é dado financeiro. Save existente não é promessa de backup; não faz parte da allowlist de Finalizar. |
| localStorage · `jpwealth.ui.widgetLayouts.v5` | AUXILIARY PREFERENCE | [src/js/40-app/13-dashboard-layout.js](../../src/js/40-app/13-dashboard-layout.js:197) leitor de migração437/remoção456; reset315 | Excluído; legado consumido pela migração para v6. | Sem escrita nova no formato v5; preservar a política existente, sem propor alteração de migração. |
| localStorage · `jpwealth.ui.widgetLayouts.v4` | AUXILIARY PREFERENCE | [src/js/40-app/13-dashboard-layout.js](../../src/js/40-app/13-dashboard-layout.js:198) leitor de migração437/remoção456; reset315 | Excluído; legado para v6. | Plural widgetLayouts; não confundir nomes por semelhança. |
| localStorage · `jpwealth.ui.widgetLayouts.v3` | AUXILIARY PREFERENCE | [src/js/40-app/13-dashboard-layout.js](../../src/js/40-app/13-dashboard-layout.js:199) leitor de migração437/remoção456; reset315 | Excluído; legado para v6. | Não há novo escritor v3. |
| localStorage · `jpwealth.ui.widgetLayout.v2` | AUXILIARY PREFERENCE | [src/js/40-app/13-dashboard-layout.js](../../src/js/40-app/13-dashboard-layout.js:200) leitor459/migração/remoção468; reset315 | Excluído; legado para v6. | Singular widgetLayout. Não há novo escritor v2; eventual comportamento de migração não foi testado aqui. |
| localStorage · `jpwealth.ui.ffNews.v1` | EPHEMERAL | [src/js/40-app/15-ff-news.js](../../src/js/40-app/15-ff-news.js:10) ffNewsReadCache54/write68; consumidores [src/js/40-app/17-economic-calendar.js](../../src/js/40-app/17-economic-calendar.js:27) e [src/js/20-ui/25-dash-macro.js](../../src/js/20-ui/25-dash-macro.js:254) | Excluído explicitamente: cache público fora de S/backup. | Persistência física local, conteúdo técnico reobtenível. payload sanitizado+fetchedAt; TTL30min. Cache ausente/ilegível não significa zero eventos. |
| localStorage · `jpwealth.ui.ffNews.sourceUrl` | AUXILIARY PREFERENCE | [src/js/40-app/15-ff-news.js](../../src/js/40-app/15-ff-news.js:13) ffNewsSourceUrl29; produtor documentado manual/DevTools, sem controle escritor runtime | Excluído: configuração local da fonte; não entra em S. | URL substitui o endpoint padrão. Nenhum endpoint/override foi aberto ou executado; presença de comentário não prova uso real. |
| localStorage · `jpwealth.market.usdbrl.v1` | EPHEMERAL | [src/js/10-domain/08-usd-brl-quote.js](../../src/js/10-domain/08-usd-brl-quote.js:24) cache técnico/read62/write74; [src/js/30-accounting/05-fx-planning/04-fx-charts.js](../../src/js/30-accounting/05-fx-planning/04-fx-charts.js:1) consome API pública de leitura | Excluído explicitamente: não entra no plano, baseline ou backup. | Taxa de referência externa corrente; referenceDate difere de fetchedAt. TTL6h; stale não equivale a valor zero. Fonte não consultada. |
| localStorage · `jpwealth_base_epoch_v1` | EPHEMERAL | [src/js/40-app/07-finalize-session.js](../../src/js/40-app/07-finalize-session.js:20) sessionEpochRead/WriteAndConfirm/Current; consumidores [src/js/40-app/14-mvp-notes.js](../../src/js/40-app/14-mvp-notes.js:788) e perfil local | Excluído: metadado de coordenação, não dado de domínio restaurável. | É controle DURÁVEL entre abas, apesar da classe técnica EPHEMERAL neste mapa. Não apagar/regenerar por conveniência. Sentinel BASE-V0-LEGACY e Web Lock existentes; nada disso foi modificado. |
| localStorage · `jpwealth_session_wipe_signal_v1` | EPHEMERAL | [src/js/40-app/07-finalize-session.js](../../src/js/40-app/07-finalize-session.js:4) produtor set/remove251,343,398; listener storage449 | Excluído: sinal temporário de finalização, wipe/import entre abas. | Mensagem removida após publicação; não é inbox durável nem notificação do SO. Canal BroadcastChannel `jpwealth_session_events_v1` também só coordena abas. |
| sessionStorage · `jpwealth_session_checkpoint_v1` | EPHEMERAL | [src/js/40-app/07-finalize-session.js](../../src/js/40-app/07-finalize-session.js:2) fingerprint/checkpoint read198/write201/remove204 | Excluído: controle de sessão/aba, sem senhas de investidor. | Pode sobreviver a reload da aba; não é backup de dados nem registro de toda edição. Finalizar remove. |
| IndexedDB · DB `jpwealth_fs` v1 / store `handles` / key `exportDir` | AUXILIARY PREFERENCE | [src/js/00-core/06-storage-fs.js](../../src/js/00-core/06-storage-fs.js:15) open/get/put/delete; [src/js/40-app/16-storage-governance.js](../../src/js/40-app/16-storage-governance.js:145) UI; [src/js/30-accounting/01-daily-ledger.js](../../src/js/30-accounting/01-daily-ledger.js:269) export usa handle | Excluído expressamente; somente S.dataGovernance.storage (metadados lógicos) viaja. | Associação/capacidade local, não preferência JSON comum. Permissão deve ser consultada/pedida por gesto; texto do caminho não concede acesso. Wipe/Finalizar chamam dgFsClearHandle. Durabilidade física/commit IDB não atestada por leitura. |
| CacheStorage · cache `jp-wealth-${JP_WEALTH_BUILD_ID}` / requests de PRECACHE_URLS | EPHEMERAL | [sw.js](../../sw.js:1) install70/activate77/fetch85–101 | Excluído: cópias do shell, JS/CSS, ícones e documentos normativos do build. | Sem dados S. Remove caches antigos do próprio prefixo na ativação; requests externos são pass-through. Não há push/Notification neste SW. |
| Filesystem/Downloads · `JP_WEALTH_DB_NNNNNN_AAAA-MM-DD_HHmm.json` | BACKUP DATA | [src/js/00-core/04-persistence.js](../../src/js/00-core/04-persistence.js:448) nome; [src/js/30-accounting/01-daily-ledger.js](../../src/js/30-accounting/01-daily-ledger.js:179) blob/export255/import; [src/js/00-core/06-storage-fs.js](../../src/js/00-core/06-storage-fs.js:151) getFileHandle/createWritable/write/close | Destino do backup completo; não é storage primário nem base sincronizada automaticamente. | Pasta requer associação/permissão. Download disparado não prova arquivo salvo fisicamente; exportação não confirma backup. Cópia exportada sem senha, com identidade própria. |
| Arquivos explícitos de auditoria/Markdown de Notas | BACKUP DATA | [src/js/30-accounting/01-daily-ledger.js](../../src/js/30-accounting/01-daily-ledger.js:136) exportAudit; [src/js/40-app/14-mvp-notes.js](../../src/js/40-app/14-mvp-notes.js:189) export individual e487 em massa | Exportações parciais, não substituem o envelope completo de restauração. | Artefatos resultantes de gesto; não são stores adicionais do runtime. Nenhum arquivo exportado/usuário foi lido. |
| RAM · rascunhos Notes/perfil/ordem, simulação Galton, estado ecal, flags de erro, investorPassword | EPHEMERAL | [src/js/40-app/14-mvp-notes.js](../../src/js/40-app/14-mvp-notes.js:2290) instância/draft; [src/js/40-app/09-settings-modal.js](../../src/js/40-app/09-settings-modal.js:61) draft; [src/js/20-ui/12-nav-style.js](../../src/js/20-ui/12-nav-style.js:203) draft; [src/js/40-app/18-galton-board/06-controller.js](../../src/js/40-app/18-galton-board/06-controller.js:1) simulação; [src/js/40-app/17-economic-calendar.js](../../src/js/40-app/17-economic-calendar.js:22) ecalState; [src/js/00-core/04-persistence.js](../../src/js/00-core/04-persistence.js:53) UNKNOWN | Excluído: rascunho não salvo não entra em S; senha conhecida é eliminada pelo persist/export/migrate. | beforeunload/confirm avisam; não salvam o rascunho. UNKNOWN vive em RAM porque persistir a barreira exigiria a gravação vetada. Não observar memória real. |
| Outras chaves do mesmo origin não declaradas pelo runtime | UNRESOLVED | Nenhum produtor/consumidor JP Wealth identificado por esta inspeção de código. | Não incluir automaticamente nem presumir autorização para limpar. | Não foram enumerados dados de navegador. Extensões, experimentos externos ou outras aplicações não são inferíveis pelo repositório. |

A enumeração inclui **23 chaves/famílias localStorage identificadas**, um checkpoint sessionStorage, um store IndexedDB e um namespace CacheStorage; as linhas de filesystem/exports/RAM delimitam destinos e exclusões. A chave corrompido é uma família dinâmica. A classe UNRESOLVED final não representa chave encontrada. A lista de Finalizar não é um inventário total: caches, layouts e preferências de navegação não constam da allowlist auxiliar atual. Importação e Zona de Perigo não devem ser tratados como “limpar todo storage”; observar seus parâmetros e contratos específicos. Nenhum `localStorage.clear()` do produto foi encontrado/introduzido.
