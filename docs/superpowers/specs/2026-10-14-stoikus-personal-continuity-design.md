# Histórico Pessoal — continuidade de auditoria integral

Data: 2026-10-14. Estado: **DESIGN_FROZEN / IMPLEMENTATION_NOT_RUN**.

Base informada pelo root: `0037bd3c8a7ab2b4e21f7fdcb60f66ed93230874`; workspace `/private/tmp/jpw-stoikus-continuity-20261014`. Esta autoria leu os fontes e escreveu apenas esta proposta. Não alterou fontes, banco, Git, dependências ou MT5.

## Decisão e critério de sucesso

Implementar a opção A: **auditoria integral retomável, com conexão, cursor e transação conservados entre fatias; nenhum cache de leitores**. Toda conexão nova começa não autorizada e permanece `JPW_STORE_BUSY`, com fase `PREPARING`, até auditar todas as projeções, todos os envelopes/payloads e o EOF real do journal. O tamanho do diário determina quantidade de trabalho, nunca uma capacidade total que invalida um diário íntegro.

Preservar schema SQLite 1, nomes/path persistidos, hashes legados, histórico existente, SQL com binds, fórmula de alavancagem, máximos Current/Estimated separados, frequência de reaviso de 60 s, testemunhas INTENT/CALLED/RESULT, cobertura explicitamente incompleta e ausência de trading. Não excluir, resetar, converter, arquivar ou reparar automaticamente registros.

As decisões de prontidão inicial, locks e JSON descritas abaixo foram confirmadas pelo root nesta sessão. O design deve passar por crítica independente antes de um agente novo implementar.

## Causa e alcance comprovados por leitura

`JPW_PersonalHistory_Store.mqh` possui um limite total de 100000 linhas e 2000 ms em `JPWPersonalAuditRows`; `Open` exige a auditoria em toda abertura. Um diário íntegro maior ou mais lento falha com IO_ERROR. Os dados permanecem no arquivo, mas resumo/página/detalhe, reabertura e exportação ficam indisponíveis pelo mesmo caminho.

Há quatro aspectos acoplados que a correção precisa tratar:

1. `JPWPersonalIntegrity` também percorre todas as projeções e executa agregações/join/count sobre o journal de uma só vez. Fatiar apenas `AuditRows` não fatiaria toda a validação de conteúdo.
2. `ControllerEnsureStore` fecha o contexto antes do retry de 5 s e o fallback usa um reader local descartado; um contexto parcial seria reiniciado indefinidamente sem modificar esses callers.
3. A UI abre resumo e página/detalhe separadamente. Mesmo quando ambos passam, podem pertencer a gerações distintas. O pedido deve produzir um único conjunto dentro de um snapshot auditado.
4. `BackupBuild`, CSV e restauração usam loops síncronos e a restauração chama `AuditRows` novamente. Eles precisam consumir o protocolo retomável e preservar a confirmação integral.

O `Open` escritor atual faz COMMIT após auditar e inicia outra transação para adquirir `ph_owner`. Existe uma janela entre a auditoria e a titularidade. O novo caminho não pode autorizar uma geração usando aquela auditoria e escrever em outra.

O relatório de causa é `/private/tmp/stoikus-core-market-review-20261014/CORE-REVIEW.md`. A extrapolação de crescimento do relatório não é medição MT5 de desempenho ou de 100k linhas.

## Duas opções comparadas

| Opção | Prova de integridade | Vantagem | Custo/risco |
| --- | --- | --- | --- |
| **A — snapshot e auditoria integral retomável por abertura** | Todos os registros da mesma transação são auditados até EOF; consumo usa essa transação. Nenhuma abertura usa recibo de outra conexão. | Resolve o limite com mínima nova raiz de confiança; preserva schema e detector de corrupção tardia. | Cada consulta nova custa O(N); snapshot longo retém locks/páginas. `quick_check` não é preemptível pela interface pública atual. |
| B — A mais cache process-local ligado à conexão e geração | Primeira abertura audita integralmente; reutilização exigiria mesma conexão, `data_version`, confirmação dentro da transação e certificação de todos os commits próprios. | Reduz reauditorias em refresh. | `data_version` ignora commits próprios, não é comparável entre conexões e não é digest. Todas as mutações/cancelamentos/TOCTOU precisam de recibos adicionais. A confiança deixa de ser somente o snapshot. |

**Recomendação congelada: A.** B fica adiada; não introduzir cache por path, conta, sequência, tamanho/mtime ou arquivo sidecar. Igualdade de `ph_meta.sequence` não detecta alteração de uma linha histórica com a mesma sequência.

A guarda de geração do escritor descrita abaixo é somente uma invalidação do contexto já vivo contra commits externos. Ela nunca permite pular uma auditoria em conexão nova, nem autoriza readers em outra conexão.

## Contratos primários e limites de evidência

- Uma transação explícita SQLite conserva sua visão histórica até COMMIT/ROLLBACK. Um SELECT preparado ainda não fixa a leitura; a execução começa no primeiro step/read. [SQLite transactions](https://www.sqlite.org/lang_transaction.html), [MetaQuotes DatabasePrepare](https://www.mql5.com/en/docs/database/databaseprepare).
- `DatabaseRead` avança um cursor; `DatabaseFinalize` encerra o cursor e `DatabaseClose` invalida consultas da conexão. Não há expiração por fim de evento documentada. Conservar handles entre timers é compatível com esses contratos, mas continua exigindo ensaio MT5. [DatabaseRead](https://www.mql5.com/en/docs/database/databaseread), [DatabaseFinalize](https://www.mql5.com/en/docs/database/databasefinalize), [DatabaseClose](https://www.mql5.com/en/docs/database/databaseclose).
- A documentação de `DatabaseTransactionBegin` não declara DEFERRED/IMMEDIATE/EXCLUSIVE. Se o desenho depende da reserva de escrita, usar SQL explícito `BEGIN IMMEDIATE` via `DatabaseExecute`; não atribuir essa garantia ao helper atual. [MetaQuotes transactions](https://www.mql5.com/en/book/advanced/sqlite/sqlite_transactions), [SQLite isolation](https://www.sqlite.org/isolation.html).
- `PRAGMA data_version` muda por commits de outras conexões e não por commits da própria. Comparar apenas na mesma conexão viva. É inválido persistir o valor para confiar após reabrir. [SQLite data_version](https://www.sqlite.org/pragma.html#pragma_data_version).
- Escritas na mesma conexão em tabela percorrida por SELECT parcial têm visibilidade indefinida. Nenhuma escrita, inclusive heartbeat, ocorrerá na conexão auditada enquanto os cursores de auditoria estiverem parcialmente abertos. [SQLite isolation](https://www.sqlite.org/isolation.html).
- VACUUM normal é escrita; VACUUM INTO preserva a fonte. Mudanças externas via SQL e VACUUM devem invalidar qualquer guarda de geração, sem inferir suporte MQL nativo a partir do host. [SQLite VACUUM](https://www.sqlite.org/lang_vacuum.html).

Pesquisa oficial sustenta o desenho SQLite; não confirma compilação MQL, vida de handles entre eventos, comportamento do filesystem/locks MT5 ou latência nativa. Essas facetas ficam NOT_RUN até ensaio próprio.

## Estado e APIs exatos

Manter discriminantes `JPWStoreResult` existentes. `BUSY` é o resultado de trabalho incompleto ou lock ocupado, diferenciados por `phase/preparing/reason`, sem acrescentar um discriminante financeiro.

Expandir `JPWPersonalStoreContext` com estado explícito inicializado: `requested_writer`, `transaction_active`, `audit_complete`, `phase`, `query`, `expected_sequence`, `snapshot_sequence`, `started_wall`, `last_wall`, contadores do resumo, dois peaks auditados e valor de `data_version` da conexão escritora. `writer` continua false até auditoria integral, titularidade e COMMIT confirmados. Todo handle começa INVALID_HANDLE. Nenhum contexto é copiado/reutilizado como certificado para outra conexão.

APIs propostas, com nomes ajustáveis apenas se todos os callers e testes forem migrados no mesmo candidato:

```cpp
void JPWPersonalContextReset(JPWPersonalStoreContext &ctx);
JPWStoreResult JPWPersonalOpenBegin(const string key,const bool writer,
   const string token,const long wall,const ulong mono,JPWPersonalStoreContext &ctx);
JPWStoreResult JPWPersonalOpenStep(JPWPersonalStoreContext &ctx,
   const ulong timer_started,const int budget_ms,const int max_rows,
   const long wall,const ulong mono);
bool JPWPersonalPreparing(JPWPersonalStoreContext &ctx);
bool JPWPersonalReady(JPWPersonalStoreContext &ctx);
void JPWPersonalOpenCancel(JPWPersonalStoreContext &ctx);

// Reutilizáveis na transação já aberta de um sandbox de restauração.
bool JPWPersonalAuditBegin(JPWPersonalStoreContext &ctx);
JPWStoreResult JPWPersonalAuditStep(JPWPersonalStoreContext &ctx,
   const ulong timer_started,const int budget_ms,const int max_rows);

// Só consomem o snapshot já auditado; jamais abrem outro DB.
bool JPWPersonalReadSummaryFrom(JPWPersonalStoreContext &ctx,JPWPersonalSummary &summary);
bool JPWPersonalReadPageFrom(JPWPersonalStoreContext &ctx,const string category,
   const long before_seq,const int limit,JPWPersonalRow &rows[],string &reason);
bool JPWPersonalReadDetailFrom(JPWPersonalStoreContext &ctx,const long seq,
   JPWPersonalRow &row,string &reason);
```

`OpenBegin` não drena o diário; sucesso de inicialização ainda retorna BUSY/PREPARING. `OpenStep` não fecha/reabre a conexão a cada chamada. Somente a transição final retorna VALID. Funções públicas de leitura/Load/Commit/Notify/Coverage recusam ctx incompleto; consultas técnicas para schema/owner não autorizam dados financeiros.

Retirar callers de produção dos wrappers síncronos por chave `Open/ReadSummary/ReadPage/ReadDetail/Export/BackupBuild`. Remover esses wrappers ou mantê-los estritamente fora do runtime; não deixar um wrapper com loop de drenagem no timer e chamá-lo de correção retomável. Helpers de drenagem podem existir somente no harness para dirigir as mesmas APIs reais sob um limite de iterações do teste.

`JPWPersonalReadFinish(ctx,complete)` permanece a fronteira de consumo: só é válido para reader READY e transação auditada ativa. Finalizar qualquer query de consumo antes; COMMIT apenas com complete=true; falha/cancelamento faz ROLLBACK e invalida o resultado. `Close/OpenCancel` devem finalizar todas as queries, reverter qualquer transação ativa (inclusive auditoria inicial de writer), fechar a conexão e zerar certificação. Close não pode depender apenas do antigo `read_snapshot` para limpar uma auditoria parcial.

## Auditoria por fases

Orçamento inicial de implementação: no máximo **1024 unidades de linha e 25 ms por fatia**, limitado também pelo orçamento restante do ciclo de 500 ms. São limites de trabalho por chamada, não capacidade total do arquivo. Consultar o relógio antes de cada nova linha/phase; se relógio recuar, adiar a fatia sem declarar EOF. O contexto contém contadores long; não armazenar todo o journal em RAM.

1. **META:** fixar a leitura e validar schema 1, conta exata, tipos INTEGER dos scalars, sequence>=0, started>0 e last>=started. Guardar `snapshot_sequence=N`. Não usar metadados lidos fora da transação como autorização.
2. **SQLITE:** preservar `PRAGMA quick_check`; exigir apenas resultados `ok` e EOF normal. A primeira chamada DatabaseRead pode executar o trabalho inteiro internamente. Rodar essa fase uma vez por abertura, não em cada fatia. Não remover o check para cumprir um orçamento artificial.
3. **EPISODES:** cursor ORDER BY episode_id percorre todas as projeções, inclusive resolvidas e excluídas de state=1. Validar tipos do state/sequence, state 1..3, codec canônico, hash de payload, account/id/state do envelope e testemunha ph_rows ligada por sequence: EPISODE, item_id, payload e digest idênticos. Acumular total/active do resumo. Opcionalmente preparar apenas as até20000 ocorrências ativas para recuperação, mantendo o limite de inventário existente.
4. **PEAKS:** cursor por quality valida tipo/qualidade 1/2, sequence, hash, codec, conta e a testemunha PEAK/item_id/qualidade/payload/digest. Guardar os dois peaks auditados do resumo. Não chamar a fórmula novamente, arredondar valores ou trocar Current por Estimated.
5. **ROWS:** cursor ORDER BY sequence lê TODOS os envelopes/payloads, sem filtros. Reutilizar `JPWPersonalReadRow` e assertivas SQL incondicionais de storage class para todos os scalars, independentemente de conversões do getter nativo. Exigir sequence==expected+1, incrementar expected só depois de validar a linha. Para EPISODE/PEAK, conferir que existe projeção do item com sequence>=sequence da linha e <=N. As testemunhas verificadas nas fases3/4 provam que essa projection sequence pertence ao item correto. Ao percorrer todas as versões, essa desigualdade prova que a projeção aponta para a última versão, substituindo a agregação MAX/GROUP BY sem enfraquecê-la. Pode fazer LEFT JOIN por PK ao cursor do journal; não usar OFFSET nem pular linhas já desconhecidas.
6. **EOF:** aceitar DatabaseRead=false somente com `ERR_DATABASE_NO_MORE_DATA`, expected==N, todas as fases encerradas e nenhuma falha. Esta sequência estrita prova count==N e max(sequence)==N, substituindo COUNT/MAX de varredura completa. Antes disso `audit_complete=false`, result BUSY e nenhuma publicação financeira.

Se usar outra implementação de latest/count, ela deve conservar essas mesmas propriedades e ser testada com journal antigo corrompido, projeção ausente, testemunha faltante e projeção desatualizada. Não declarar integralidade por validar somente os payloads retornados pelo filtro.

Erro SQL real não é EOF. Mapear ERR_DATABASE_BUSY/LOCKED para BUSY; CORRUPT/NOTADB para CORRUPT; schema futuro para INCOMPATIBLE; falha de prepare/column/hash/memória para estado explícito correspondente. Na interrupção de um cursor por erro SQL não conservar uma falsa posição certificada: rollback/finalize e reiniciar a auditoria integral em nova tentativa. Preservar motivos e tentativas anteriores.

## Escritor, ownership e geração

O lock local exclusivo existente continua pertencendo ao runtime/controller e nunca é apagado. `ph_owner` continua sendo fence SQL por token. Nenhum dos dois comprova integridade de rows.

Caminho recomendado de aquisição:

1. Abrir a conexão uma vez. Verificar owner técnico sem reservar o banco por um audit longo quando houver outro lease comprovadamente ativo. Se houver espera de owner, liberar a transação técnica, conservar fase WAIT_OWNER e repetir só essa tentativa no backoff; reader de recuperação independente pode progredir.
2. Quando há possibilidade de aquisição, executar `BEGIN IMMEDIATE`, revalidar schema/conta/owner na própria transação reservada e iniciar auditoria. Não fazer COMMIT por fatia. A reserva impede outro commit de escrita durante auditoria/aquisição.
3. Depois de EOF, finalizar cursores, revalidar owner com wall/mono atuais (não os da primeira chamada), recuperar os estados auditados e atualizar ph_owner no mesmo contexto reservado. COMMIT confirma titularidade. Só então ctx.writer=true e o produtor publica prontidão de persistência.
4. Se COMMIT estiver BUSY por readers em rollback journal, ficar na fase OWNER_COMMIT_WAIT, sem canais/escrita concorrente nem falso VALID. SQLite conserva a transação após esse BUSY: tentar o mesmo COMMIT após backoff. Outro erro encerra a tentativa. Cancelamento/detach sempre reverte essa reserva.

Também é aceitável promover a transação reader após auditoria, mas a promoção deve acontecer na MESMA transação. Se falhar BUSY/BUSY_SNAPSHOT, abandonar a transação e auditar novamente; nunca COMMIT a auditoria e começar uma escrita presumindo equivalência. A reserva inicial explicitada é preferida por permitir avanço determinístico quando já existe fence local exclusivo.

Para transações subsequentes do contexto escritor vivo:

- Usar BEGIN IMMEDIATE antes de ler owner e iniciar append. Dentro dela, consultar data_version e comparar com o valor da MESMA conexão observado na transação da auditoria. Se mudou, não heartbeat/append/notify/coverage: invalidar prontidão e encaminhar para reauditoria integral.
- Não adotar um valor amostrado depois do COMMIT como certificado; um commit externo pode ocorrer nessa janela. O valor da transação reservada é conservado porque commits próprios não alteram data_version.
- Own commits continuam passando pelos únicos append/projection APIs, que validam conta, codec/envelope, payload digest e sequência; após erro/reopen zerar o recibo em memória. Nenhum SQL raw de mutação histórica deve existir fora desses APIs no runtime.
- Esta guarda detecta commits SQL externos, não adulteração de arquivo fora do protocolo SQLite; não anunciá-la como criptografia de envelope. Caso o PRAGMA não esteja disponível/retorne tipo inválido, fail closed com motivo explícito; nunca presumir geração igual.

A guarda de geração da mesma conexão é obrigatória, com contraprova host e ensaio nativo separados. Sua ausência não satisfaz este design nem CONT-07; não há alternativa de omissão por documentação.

Locks: em rollback journal readers longos podem atrasar commits; em WAL uma leitura pode conservar snapshot antigo e páginas no WAL. Não trocar o modo de journaling de um banco existente. Não prometer tempo máximo de resposta para quick_check ou uma chamada SQL/FS indivisível sem API de interrupção. Medir máximos observados por fase e informar a limitação.

## Controller e cooldown

`g_ph_store` conserva PREPARING entre ticks; adicionar reader de recuperação durável em memória de processo, em vez da variável local descartada. `g_ph_next_open` serve para retry de falha/owner/lock, não impede progresso de uma auditoria já ativa e não causa Close a cada5s.

Enquanto a auditoria inicial avança: observation/reconcile podem coletar memória/fila existente, mas não consultar projeções não auditadas nem publicar Current do histórico. Antes dos primeiros canais da ativação, aguardar recuperação auditada do cooldown. Não reinterpretar uma espera de auditoria como falha permanente de IO.

Preservar fallback existente para **erro real persistente de armazenamento**, sob fence local e sem conflito explícito de token: aviso local pode ocorrer com mensagem de histórico incompleto, mantendo o cooldown local de 60s e nenhum recibo durable inventado. Essa exceção não é usada para PREPARING que avança; a prontidão/falha precisa ser um estado, não uma comparação de texto localizado. Se houver perda comprovada de titularidade SQL, suspender canais/escrita como hoje.

Recuperação bem-sucedida usa MergeRestored: conservar primeiro episódio, pendências de máximos mais altos e contagem/prazo local; preservar vínculo RECOVERY_EPISODE_LINK quando IDs divergem. `g_ph_restored_once` só após Load confirmado; não usar um bool indevido para concluir que um leitor parcial recuperou dados. Revalidar ticket/identifier/SL ao chamar canal; depois de downtime vencido emitir no máximo um reaviso, sem replay de intervalos. MarkRequested continua usando relógio do pedido real.

Emitir SESSION_START/GAP/RESUMED somente por Store pronto e transação com token. A auditoria comprova integridade do arquivo, não continuidade de cobertura passada. Detach cancela ambos os contextos antes de fechar o fence, preservando GAP/SESSION_END apenas quando há writer autorizado como hoje.

## Pedido de UI e consumo

Criar um job de leitura persistente na UI contendo contexto e tuple congelada `(request_id,scope,category,before,detail_seq,operating_key)`. Callbacks continuam sinalizando pedidos, sem SQL/file IO. Um novo request_id solicita cancelamento; a limpeza real ocorre no coordinator antes do próximo step. OnDeinit pode fazer cleanup direto.

Um job por seleção: ListAccounts permanece disponível mesmo quando o histórico selecionado está ausente/corrompido; abrir reader uma vez, auditar até EOF e então preencher summary + page OU detail no MESMO ctx. Não chamar Readers por chave que abrem segundo snapshot. Summary usa metadados, counts e peaks da auditoria; evitar uma segunda Integrity/Load completa no fim.

Não consumir dado parcial. g_personal_available permanece false, peaks inválidos e botões antigos vazios durante PREPARING. Publicar o pacote só após queries de consumo, ReadFinish(true) e validação final da tuple, identidade operacional e conta. Em falha/cancelamento, limpar saída preparada; não deixar summary novo junto a página antiga.

O refresh automático de5s é medido a partir da conclusão do pedido. Enquanto um job está ativo, não criar refresh que o cancele/recomece. Navegação explícita cancela o pedido antigo e inicia outro; nenhum resposta velha promove uma seleção nova. Liberar a transação tão logo o pacote seja concluído, em vez de mantê-la enquanto o usuário lê a tela.

Adicionar `JPWPersonalUICancelPending()` para fechar jobs no OnDeinit do indicador e invalidação de contexto. Diferenciar cancelamento de leitura por seleção de exportação, cujo pedido tem conta histórica congelada e não é retargetado pela navegação.

## Exportação, backup e restauração

Exportar é um job com conta/kind/path capturados pelo gesto, contexto reader próprio, phase, cursor, count, file handle e motivo. APIs: `JPWPersonalExportBegin(key,backup,job)`, `JPWPersonalExportStep(job,started,budget_ms,max_rows)`, `JPWPersonalExportCancel(job)`. Retornar BUSY enquanto ativo e VALID somente após confirmação final. A UI mantém o pedido ocupado até término; segunda ação não substitui kind/scope. Navegar A→B não transforma a exportação de A em B.

Auditar integralmente antes de abrir o arquivo de saída. Manter o snapshot auditado até EOF da exportação. CSV escreve header/linhas em fatias, conta sequence1..N, valida novamente ReadRow e termina com EOF normal. Flush/close e ReadFinish confirmados antecedem a mensagem de sucesso. Uma falha depois de criar arquivo deixa-o parcial e explicitamente não confirmado, sem apagar ou substituir destinos anteriores. Cancelamento fecha query/file/db e reverte transação; parcial permanece com motivo. Ações/cliques e render não fazem IO.

JSON mantém esquema `jpw-personal-history/v1`, canonicalização, UTF8/CRLF, IDs como texto, SHA global e validação de releitura. Body pode ser montado em fatias na memória e só entregue após EOF/count/hash. **O contrato de32*1024*1024 caracteres do corpo canônico permanece**; não prometer backup ilimitado. Hash global, FileWriteString grande e StringSplit/parse podem ser chamadas indivisíveis nesse contrato, cuja latência/memória precisa ser informada. Corpo canônico acima de JPW_PERSONAL_BACKUP_MAX_CHARS é capacidade própria de JSON, não CORRUPT nem falha da auditoria. O CSV integral continua acessível sem teto total de linhas.

Restauração continua apenas para um novo arquivo PersonalHistorySandbox; nunca o history_<account>.sqlite operacional e nunca arquivo existente. Parse global/linha/seq/contexto deve passar antes de confirmar reconstrução. Recomenda-se job Begin/Step/Cancel para replay: gravar em uma única transação do sandbox; depois de TODOS os inserts finalizar cursores de escrita e chamar AuditBegin/AuditStep no mesmo DB/transação, sem outra abertura nem COMMIT por fatia. Só EOF integral permite COMMIT de reconstrução. Em cancelamento/erro reverter e preservar arquivo de sandbox para diagnóstico. Não saltar auditoria SQL porque os bytes JSON passaram.

Um helper público síncrono de restauração sem caller no timer pode permanecer como compatibilidade explícita, mas o caminho de auditoria deve dirigir as mesmas fases até EOF, sem MAX100000/MAX2000 ou validação parcial. Tests exercitam esse protocolo; não atribuir-lhe orçamento nativo estrito.

## Plano de implementação por arquivos

### Task PH-1 — protocolo Store e provas de integridade

Arquivos: `JPW_PersonalHistory_Store.mqh`; `tools/personal_history_host/compat.hpp`; `tools/personal_history_host/store_cases.cpp`; novo `tools/personal_history_host/continuity_cases.cpp`; `tools/jpw_personal_history_test.py` para incluir a nova faceta e hashes. Criar fixtures/runner específicos de continuidade em `tests/fixtures/genetrix-personal-history/continuity-v1.json` e `tools/jpw_personal_history_continuity_test.py` se necessário para não alterar os20oráculos congelados.

Primeiro red: 100001linhas válidas não abrem no baseline e corrupções antigas excluídas do filtro são recusadas. Depois estado/Begin/Step/Cancel, fases integrais, APIs From, reserva writer sem janela, error mapping e cleanup; geração writer guardada mesma conexão. Preservar Core sem alteração e schema/dados anteriores. Adaptar helpers de harness para drenar APIs reais; não inserir algoritmos de domínio no shim.

### Task PH-2 — Controller, recuperação e UI

Arquivos: `JPW_PersonalHistory_Controller.mqh`; `JPW_PersonalHistory_UI.mqh`; `JPW_Alavancagem_Atual.mq5` somente cleanup de jobs no OnDeinit; `tools/personal_history_host/controller_cases.cpp`, `controller_seams.cpp`, `ui_cases.cpp`, `ui_seams.cpp`; runner para extrair funções novas e compilar callers reais.

Implementar contexts retidos, espera inicial versus IO fallback, recovery reader e cooldown, job/tuple único para summary+page/detail, progress/retry/cancel/refresh5s e cleanup. Exercitar EnsureStore/Tick/CollectUI de produção, não apenas stubs que retornam sucesso em uma chamada. Stub somente primitivas terminal, relógio, file fence e notification channels declaradas.

### Task PH-3 — export/restore e integração de evidência

Arquivos: `JPW_PersonalHistory_Export.mqh`; `JPW_PersonalHistory_UI.mqh` no contrato export; `tools/personal_history_host/export_cases.cpp`; `continuity_cases.cpp`; runners necessários. Atualizar somente documentação atual relevante de capacidade/estados em `mt5/jpw-alavancagem-atual/README.md` e documentos atuais encontrados pela busca focal; preservar registros históricos de versões e tentativas.

CSV/JSON retomáveis, conta capturada, integridade da releitura, capacidade32*1024*1024 caracteres do corpo canônico explícita, restore audit no mesmo contexto. Não editar a aceitação financeira original ou marcar facetas nativas como executadas.

O builder fresco pode executar PH1→PH2→PH3 no mesmo subescopo para evitar interfaces concorrentes; root integra as outras correções independentes. Sem Git/deps/globalDB/MT5 neste passo de design. Nenhuma montagem de pacote/desenvolvimento implica publicação/aceite.

## Matriz obrigatória de testes

Todos os bancos são sintéticos e isolados por tentativa. Manter tentativas red/falhas e recibos com hashes. Testes devem executar os corpos reais com SQLite real; host não comprova MQL nativo.

| ID | Prova e resultado exigido |
| --- | --- |
| CONT-01 — fronteira/tamanho | Diários0,1,100000,100001 e pelo menos200003linhas, com eventos válidos, episódios e peaks anteriores preservados. 100001 deve exigir múltiplas fatias; context/query não mudam entre fatias. Antes do EOF summary/page/detail/load/write não autorizam. Após EOF Open writer/read, resumo e página/detalhe passam e contagem/sequence antigas são exatas. |
| CONT-02 — prazo por fatia | Relógio sintético avança por read; usar orçamento pequeno que força yield antes de terminar. Mesmo depois de>2000ms totais, um diário íntegro termina. Nenhuma iteração ultrapassa max_rows; não transformar tempo total em incapacidade. Medir/relatar separadamente SQL quick_check indivisível. |
| CONT-03 — corrupção tardia | Corromper linha100001 (digest, codec, account, category, item, wall/type) mantendo metaseq e, nos casos de envelope, mantendo digest payload válido. Uma consulta que filtraria essa linha deve falhar CORRUPT após alcançá-la. Também corromper linha1, uma linha no meio e antiga EPISODE/PEAK que não é a projeção atual. Sem reset, escrita, arquivo de sucesso ou dados parciais publicados. |
| CONT-04 — projeções/latest | Projeção ausente, orphan, state divergente0/2/3/99/text/real, payload/digest/conta/id inválido, latest atrasada, witness errado/faltante e peak quality/item incoerente. Validar resolved/inactive também. Falha não pode ser mascarada pelo filtro state=1. |
| CONT-05 — snapshot concorrente | Conexão B atualiza journal/projeção/meta de modo transacional entre duas fatias de reader A. A deve consumir inteiramente a geração antiga ou reiniciar/recusar, nunca mix. Depois fechar A, a nova abertura deve ver a mutação/corrupção. Executar DELETE-journal e WAL em fixtures distintas, sem alterar DB de usuário. Mutation só depois de AuditEOF antes de consume também permanece na geração auditada. |
| CONT-06 — writer/reserva/TOCTOU | B tenta modificar depois de AuditEOF e antes do owner commit. Reserva ou promoção na mesma transação impede aceitar outra geração; failed promotion reinicia full audit. Active owner não recebe lease roubado. Commit BUSY por reader conserva PREPARING e não libera canais; release reader permite retry sem falso success. Teste entre processos para lease/takeover/fence. |
| CONT-07 — guarda do writer vivo | data_version same-connection muda com commit externo e permanece com commit próprio. Não comparar conexãoC; reopen zera certificação. Depois de commit externo que conserva sequence, KeepAlive/Commit/Notify/Coverage não sobrescrevem; passam para audit completo e corrupção é recusada. Race externa imediatamente após owner COMMIT deve ser detectada no próximo BEGIN IMMEDIATE, sem adotar versão póscommit. |
| CONT-08 — conta/pedido/cancel | Auditoria de A parcial; selecionar B ou mudar operating_key; jobA é cancelado, handles zerados, nenhuma saída de A promovida em B. Voltar a A começa linha1 em conexão nova. Navegar página/detalhe mantém tuple exata. Refresh5s não cancela job ativo. Catalog continua disponível sob corrupção selecionada. |
| CONT-09 — restart | Cancel/close/crash real no meio da auditoria e entre EOF/owner commit. Processo novo audita do início, banco original/journal/projeções preservados. Cooldown1030 após pedido1000 não chama;1120 permite no máximo um. Retomar mantém RECOVERY_EPISODE_LINK e peaks pendentes mais altos. |
| CONT-10 — storage/fallback | Inject BUSY/LOCKED, erro prepare/read/column, CORRUPT, schema futuro, falha de commit/flush/disco cheio. Erro não é EOF; PREPARING não é IO definitivo. Erro IO persistente habilita fallback local incompleto existente sob fence, sem rajada e sem falsas linhas durable; SQL owner conflict suspende canais. |
| CONT-11 — CSV100001 | Após múltiplas fatias auditar/exportar100001linhas válidas sem cap total. Header e Nlinhas, ordem1..N, hashes/payloads/contexto e IDs>2^53/UTF8/CSV formula-neutralization corretos. Mutação concorrente não cria captura híbrida. Falha/cancel/flush deixa parcial não confirmado; colisão preserva destino anterior. |
| CONT-12 — JSON/restore | JSON100001 com payloads pequenos e size medido<32MiB pode construir, reabrir/parse e restaurar sandbox com schema1/projeções/sequência exatas. Restore percorre auditoria integral. Fixture>32MiB falha com motivo de capacidade JSON, dados intactos e CSV acessível; não computar como corrupção nem PASS de backup. Corromper checksum global/tardia/template/key/sequence/linha recusa. Sandbox existente e banco operacional ficam intocados. |
| CONT-13 — API/ownership cleanup | Repeated Begin sem cancel é recusado; invalid ctx nunca permite read/write. Cancel em toda fase finaliza queries/rollback/close sem leak. Old Close não libera token novo; holder crash e takeover preservam cooldown. Nenhum callback/render executa IO; nenhum caminho novo usa OrderSend/trading. |
| CONT-14 — regressão original | Rodar20HIS-AC facetas host originais depois da alteração, incluindo cross-process HIS-AC11/16/18, exports HIS-AC19 e UI HIS-AC20. Oráculos financeiros/cooldown/cobertura não mudam. Testes host Ledger/Risk/Observer pertinentes ao integration callsites apenas uma vez após freeze; broaden/repetir somente se novo erro/edição justificar. |

Não medir benchmark100k artificial por chamadas a reimplementação Python do domínio. O shim pode contar reads/queries, injetar relógio/erros e adaptar sintaxe; não pode validar auditoria no lugar do fonte de produção. Atualizar `ui_source/controller_source` do harness para incluir contexts e novos helpers reais, evitando que macros antigas desviem os leitores novos para sucesso sintético e escondam o protocolo.

## Verificação, crítica e saída

Antes de declarar capacidade resolvida: crítico independente confere todos os paths de abertura, cada transição BUSY→VALID, todos os SQL de mutação, locks/owner/geração, cancel/cleanup e que nenhuma corrupção em filtro excluído passa. Fazer source freeze/hashes após últimas edições e antes do conjunto largo; preservar red anteriores e não reutilizar diretórios de tentativas.

Aceite host da correção exige CONT01..14 pertinentes PASS e todas as facetas originais antes PASS permanecendo PASS. O relatório separa `HOST_SQLITE_PASS` de `NATIVE_MQL_NOT_RUN`, `MT5_HANDLES/LOCKS_NOT_RUN`, `PERFORMANCE_NATIVE_NOT_RUN`, `INSTALLATION_NOT_RUN`, `OWNER_ACCEPTANCE_NOT_RUN`. Não converter esse resultado em aceite operacional/publicação.

Sem evidência nativa, conclusão permitida: limite total100000/2000 removido como incapacidade e substituído por processamento integral retomável nos fontes/testes host; dados/validações preservados. Não afirmar ausência de limites de tempo/memória, nem JSON ilimitado.

## Ledger de leitura/freeze desta proposta

Leitura integral: Store, Controller, Export, Core, UI; harness principal e funções pertinentes de Store/Controller/UI/Export; compatibilidade SQLite;20casos de aceitação. Leitura focal de callers Observer Runtime, Coordinator e deinit do indicador. Pesquisa oficial foi delegada a sqlite_semantics, somente leitura, concluída. Memória foi usada apenas para disciplina de escopo/evidência; fatos atuais vêm dos fontes e do diagnóstico fornecido.

SHA256 observados na leitura (não são freeze final de implementação):

| Arquivo | SHA256 |
| --- | --- |
| JPW_PersonalHistory_Store.mqh | 742e384fee457ff6429218e395993a1485e77f3a44ae9d0a3ed5c8ef0ed585e8 |
| JPW_PersonalHistory_Controller.mqh | 10985c149620f98c93d15f1896fb56bfbe05de716b75d1b4ae1675d38073de6d |
| JPW_PersonalHistory_Export.mqh | fe65d13bfec4b147e743ab6ec8d3ea482e5329a9e71ec8ef9f31587d74613eec |
| JPW_PersonalHistory_Core.mqh | 247a7d99b51a7fb63620edec9c92d7338924c73a4967b88e2f68eb4ae814c3e6 |
| JPW_PersonalHistory_UI.mqh | b4c2041a60eb304bce59c7689c4e52850146cc5fd36209af06f91733ccfd2168 |
| tools/jpw_personal_history_test.py | 5f75d53b48f801bc2d9f72323946817fc3bb0faa0b88c4776438420758133eb2 |
| store_cases.cpp | d2bacbced4c96aa71e8f05e2015d740639bcbbdcd1064f1dae0285da8a171548 |
| controller_cases.cpp | 83239ae3dcdd17e516fbcc90f824af0a99b4a6c0dbceffe3148d650cd0ac9fb6 |
| export_cases.cpp | 35b59c1f13f63674d1a13a36475fb9bcb76e986a6493358a9f02e6db99ee0d4e |
| ui_cases.cpp | 9a2fe4b8d01b73d384f696d81f3c9b91754c61fa6e3273cdc0f7a4af102938f9 |
| compat.hpp | feb38dbe9edd589e837a8292e7a44ed8cdadada44cd76dac5a919ba58f2455ed |

Auto-revisão do design: causa→protocolo→callers→testes encadeados; ausência de placeholders; nenhuma autorização parcial; schema1 e JSON MAX_CHARS explícito; preempção/locks/prova nativa limitados. Uma alternativa de writer sem guarda de geração deve ser rejeitada pelo crítico: a guarda e CONT-07 são obrigações deste candidato.


## Emenda R2 — resolução da crítica independente D-01..D-04

R1 preservado em design-personal-R1.md; parecer inicial em task-2-design-review.md. Esta emenda é normativa para a implementação técnica aprovada pelo usuário, sem mudança de regra financeira.

### D-01 — geração obrigatória

Todo início de transação de mutação do writer vivo usa BEGIN IMMEDIATE e compara data_version com a amostra da MESMA conexão registrada dentro da reserva de auditoria. Nenhum heartbeat/append/projeção/Notify/Coverage pode anteceder essa checagem. Commit próprio não muda a certificação; valor pós-COMMIT nunca substitui a amostra. Reopen exige auditoria integral do zero. Ausência, tipo inválido ou mudança do PRAGMA invalida a prontidão e bloqueia mutações; nenhuma alternativa documentada permite omitir a guarda.

### D-02 — geração diferente é distinta de token perdido

Adicionar estados técnicos explícitos ao contexto, por exemplo bool generation_changed e bool owner_lost, ambos false no Reset. APIs interrogativas: bool JPWPersonalNeedsReaudit(JPWPersonalStoreContext &ctx) e bool JPWPersonalOwnerLost(JPWPersonalStoreContext &ctx). O primeiro é true quando a certificação foi invalidada por mudança de geração; o segundo somente quando token/ownership efetivamente diverge. Nomes podem ajustar juntamente com TODOS callers/testes, mas os estados não podem depender de texto localizado.

EnsureStore, NotifyDue, Tick e caminho de Coverage distinguem as duas causas de writer=false. Generation_changed suspende canais/escrita, fecha/cancela a conexão certificada, invalida g_ph_loaded e começa nova auditoria retida sem armar g_ph_owner_conflict. Não publica Current nem usa fallback de IO definitivo durante essa revalidação. Owner_lost conserva a suspensão por conflito e não rouba lease. Um commit externo íntegro deve poder recuperar após múltiplas fatias; um token novo ativo permanece suspenso. Mudança detectada depois do heartbeat, em Notify/Commit/Coverage, tem a mesma transição segura.

### D-03 — recuperação preparada só é aplicada após confirmação

O contexto guarda APENAS as projeções ativas para recuperação (respeitando o limite existente de20000 sujeitos), dois peaks e metadados auditados da sua abertura; não mantém o journal nem compartilha certificado com outra conexão. Esses valores são preparados enquanto o snapshot auditado/reserva writer ainda estão abertos.

Adicionar getter de staging com a mesma assinatura de Load: bool JPWPersonalLoadAuditedFrom(JPWPersonalStoreContext &ctx,JPWPersonalEpisode &episodes[],JPWPersonalPeak &current,JPWPersonalPeak &estimated). Ele copia SOMENTE a preparação integral da mesma abertura/conta; não executa novo SELECT depois de COMMIT e não autoriza publicação. Antes de audit_complete recusa. Nenhum caminho usa cópia de contexto como recibo para outro handle.

Reader de recuperação: OpenBegin/Step até EOF → LoadAuditedFrom em temporários → finalizar queries → ReadFinish(true) confirmado → MergeRestored/flags/picos/cooldown. Qualquer falha no consumo/COMMIT descarta temporários; g_ph_restored_once continua false.

Writer: preparar recuperação durante fases integrais, enquanto a transação reservada está ativa → adquirir/verificar token e COMMIT do owner → somente com sucesso o Controller usa staging daquela abertura para MergeRestored/flags/picos/cooldown. Não chamar Load com SQL novo entre owner COMMIT e a publicação do estado inicial. BUSY de owner COMMIT conserva preparo mas não o aplica; erro/cancelamento descarta preparo. Eventual commit externo logo após owner COMMIT será detectado na próxima transação antes de qualquer mutation/canal durable; nunca adotar o data_version desse commit como certificado.

### D-04 — tipos pertencem ao fonte de produção

Verificar storage classes no SELECT/auditor por typeof(...) ou DatabaseColumnType com contrato equivalente; getters Integer/Long/Text, inclusive os do harness, não são o validador de domínio. Predicados fazem a linha inválida retornar e falhar; nunca excluí-la no WHERE. META: id/schema_version/sequence/started_wall/last_wall INTEGER e account_key TEXT. OWNER: id/mono/wall INTEGER e token TEXT. ROWS: sequence/wall INTEGER e category/item_id/payload/digest TEXT. EPISODES/PEAKS: IDs TEXT, discriminantes/sequence INTEGER, payload/digest TEXT, além de witness/meta associados com tipos correspondentes. NULL/orphan ou classe diferente é falha explícita, não zero/filtro/EOF.

CONT-03/04 incluem REAL/TEXT para wall/sequence/state/quality e BLOB para category/item/payload/digest com getters de teste deliberadamente permissivos (conversão nativa plausível). Se recusar apenas porque o shim antigo é estrito, o teste não comprova D-04. Os testes normais e oráculos anteriores mantêm suas validações.

### Capacidade JSON — precisão de unidade

JPW_PERSONAL_BACKUP_MAX_CHARS permanece32*1024*1024 caracteres do corpo canônico, como definido no fonte atual. Não declarar um teto exato de bytes do arquivo final: header/footer/CRLF e codificação compõem tamanho próprio. CONT-12 mede a condição real do corpo e preserva erros de capacidade; CSV continua a alternativa integral sem limite total de linhas.

### Latest eficiente

Evitar subquery MAX por item ou mapa de todo journal em RAM. Usar witness por PK da projeção e, no cursor ROWS, LEFT JOIN por PK de ph_episodes/quality ph_peaks para conferir projectedSequence>=cada versão e<=N. A fase de projeções já confere que a testemunha projetada pertence ao mesmo item. Todas as versões são lidas, inclusive antigas; não criar índice/migração necessária para fazer essa prova.
