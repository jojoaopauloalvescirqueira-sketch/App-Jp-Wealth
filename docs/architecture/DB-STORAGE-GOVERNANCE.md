# Governança de armazenamento da base (JPW-HJFGDE)

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
7. **Termo de responsabilidade** (§5): etapa 07 do onboarding; sem o aceite o
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
