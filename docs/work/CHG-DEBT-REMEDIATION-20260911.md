# CHG-DEBT-REMEDIATION-20260911 — correções técnicas de dívidas identificadas

## Autoridade, identidade e compreensão

Pedido vigente do proprietário: “resolva todas as dívidas abertas”. Este contrato
delimita a implementação técnica; não escolhe regras financeiras nem concede
aceite ou publicação. A branch de trabalho `codex/debt-resolution-20260911` foi
criada na mesma worktree limpa, preservando o checkpoint commitado e a branch
`codex/functional-reliability-20260911`. Não há outra worktree criada.

Raiz: `/Users/joaopauloalves/.codex/reliability-campaigns/20260911/product`.
BASE_SHA: `fcbb25767073a4ab08a9f0ac2ac16069a3008bfe`; build inicial
`01947ca576fa8048`. Baseline recuperável e recibo dos 286 inputs rastreados:
`../evidence/debt-resolution-20260911/baseline.tar` e `preservation-before.json`.
Preflight edit PASS antes da escrita; nenhum trabalho local desconhecido.

O JP Wealth é uma PWA financeira local. Esta tarefa preserva confirmação de
gravação, acesso a controles e veracidade da informação: a UI de recorrências PF
edita atos por APIs existentes; Alladin lê um ledger append-only; a finalização
remove apenas dados JP Wealth após seus gates. A melhoria desejada é eliminar
barreiras verificadas de interação e evitar classificar dados históricos inválidos
como íntegros. Não se calculam novos valores nem se normalizam fatos históricos.

Fontes lidas: AGENTS, README, PROJECT-CONTEXT, CONTEXT-MAP, CHANGE-PROCESS,
auditoria X1 de 20260910, relatório da campanha de confiabilidade, relatórios
normativos e noturnos pertinentes. Harness v2.0 SHA-256
`c1b5ca9da4dfa2c9a9d1fa3d87a9f7ef9c4cb741fffeedee33d37978f5b800c8`.
Auditorias são evidências históricas, não novas execuções nem autorizações.

## Escopo por causa

**UI N1/A2 — X1-01 a X1-04.** Corrigir foco/semântica/erros acessíveis da
recorrência PF; contraste textual do cartão Forex no Dashboard; reflow do filtro
de moedas no calendário. Não alterar validações financeiras ou controles globais.

**Qualidade de dados N2/A3 — residual Alladin histórico.** Reutilizar validação
civil existente na fronteira de leitura de qualidade. Ledger inválido fica
indisponível de forma explícita conforme o contrato já existente, sem apagar,
reescrever datas, produzir saldo zero fictício ou modificar importação/schema.

**Finalização N2/A3 — diagnóstico focal Galton/CI.** A execução direta intacta
`finalization-focal-01.json` passou localmente no BASE_SHA. A falha remota
34644415770 continua preservada. Só alterar lifecycle após contraprova causal;
não modificar expectativas para obter PASS. Física Galton permanece fora do lote.

Arquivos de produto/testes permitidos, relativos à raiz acima:

- `src/js/20-ui/18-finpes-budget.js`
- `src/styles/app.css`
- `tools/pf_recurrence_accessibility_test.py`
- `src/js/10-domain/13-alladin.js`
- `tools/alladin_civil_date_test.py`
- `src/js/40-app/18-galton-board/06-controller.js`
- `tools/finalize_session_test.py`
- `src/js/manifest.json`: somente hashes de fontes alteradas
- `build-id.js` e `dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html`: somente geração oficial
- `docs/work/ACTIVE-TASK.md`: cabeçalho, histórico integral preservado
- `docs/work/CHG-DEBT-REMEDIATION-20260911.md`: contrato e vínculo das evidências

A allowlist limita permissões: não obriga alterar todos esses arquivos. Eventual
delta de control plane exige contrato próprio N3/A4, validação negativa e auditoria
separada. Não se altera o juiz do produto para aceitar defeito. Reservas OPEN-05 e
homologação V11 aguardam decisão material própria, já solicitada ao proprietário.

## Critérios e testes definidos antes do patch

1. Recorrência PF: abertura, labels, primeiro erro, Tab/Shift+Tab, Escape,
   cancelamento, sucesso e retorno de foco após render, sem alterar valores.
2. Dashboard/calendário: desktop e 320/390px, claro/escuro, contraste medido,
   filtros acessíveis e ausência de overflow; capturas sintéticas como complemento.
3. Alladin: data civil inválida preexistente, ano bissexto, vazios e datas válidas;
   diagnóstico de qualidade e consumidores; bytes do estado/armazenamento
   preservados na leitura; novos lançamentos/estornos continuam cobertos.
4. Galton: contraprova determinística para reset entre abas antes de qualquer
   correção. Resultado local positivo não apaga o resultado remoto incompleto.
5. Oráculos e testes focais antes/depois, regressões próximas, FULL existente
   no candidate final, build reprodutível, freeze e auditoria independente.

Ferramentas existentes, dados sintéticos, perfis descartáveis próprios, fixtures
nominais e barreira `loopback-only.sb`. Nenhuma API econômica ao vivo, dependência
nova ou configuração global. Git sintético somente em fixtures próprias sem
remotos/hooks externos. Derivados via `python3 tools/rebuild_monolith.py`;
nenhuma edição manual. Temporários/evidências ficam em
`../evidence/debt-resolution-20260911/` ou nos destinos já usados pelas suítes.

## Preservação, rollback e CTX

CTX-DEBT-REMEDIATION-20260911: sequencial; cria este contrato e acrescenta somente
o cabeçalho da tarefa ativa. Mantém todos os contratos, recibos e resultados
anteriores. Não promover datas históricas a vigência atual. Dívidas já corrigidas
só serão reconciliadas por referência à evidência, nunca por exclusão do histórico.

Recuperação: aplicar apenas o inverso do delta deste lote em cópia após conferir
identidade; comparar com `baseline.tar`. Não executar reset/stash nem restaurar
globalmente. Preservar main, checkpoint, stash, outras worktrees e nav-ref-context.
Nenhum dado do proprietário entra nos testes. Rollback não requer migração de dados.

Parar somente a parte dependente de conflito normativo, necessidade de mudar
schema/dados reais/proteções, descoberta material fora da allowlist ou hipótese
sem prova. Sem commit, push, PR, merge ou deploy nesta implementação; aceite antigo
não é transferido ao novo candidate. Entrega deve manter resultados brutos,
limitações, fingerprints e auditoria, sem declarar todas as capacidades provadas.

## Complemento V2 — contratos preservados e banner de retentativa

V1 preservada em `candidate-v1.*`, fingerprint
`c39002f414e3db4144a6b0058112a8f8c70346ae5f73c9677e24eccd3a40ee42`,
build `4ab8b1307acf8445`. Seu FULL registrou 54 PASS/1 PRODUCT_FAIL:
`galton-board` exige retorno síncrono da chamada direta do hook. Não alterar
essa expectativa. Conservar o comportamento padrão; a finalização deve pedir
explicitamente o remount adiado, mantendo destruição/epoch anteriores à limpeza.
Acrescenta-se à allowlist `src/js/40-app/07-finalize-session.js`, apenas o argumento
dessa chamada. Os gates de commit/clear/UNKNOWN e a suíte Galton ficam intactos.

A reprodução única `banner-pointer-probe.json` demonstrou retentativa por mouse
inteiramente coberta pelo aviso global, mesmo após scrollIntoView. O pedido
vigente de resolver dívidas abrange esse defeito técnico. Risco N2 conservador
pelo arquivo compartilhado de persistência, apesar do delta ser de apresentação.
Acrescentam-se à allowlist:

- `src/js/00-core/04-persistence.js`: somente medição/observação de layout dos avisos;
- `tools/studies_notes_persistence_contract_test.py`: focal de banner e retentativa.

`src/styles/app.css`, já permitido, reserva no drawer de Notas a altura efetiva
dos avisos e permite rolagem dos avisos altos quando necessária. Preservar texto,
estado, botões, z-index, timers, exportação, recuperação e bloqueios; não ocultar,
rebaixar o aviso ou atravessá-lo com pointer-events. Nenhuma nova gravação, mudança
de schema ou refatoração de save(). Dimensões devem acompanhar resize e mudança
de conteúdo, sem polling nem observadores duplicados.

Testes: oráculo por mouse antes/depois, rascunho e retry único, avisos simples/duplos,
resize, 390x568/640x360, claro/escuro, botões de recuperação/backup acessíveis e
ausência de escrita pela composição. Preservar teste de teclado; executar Galton,
finalização, persistence-failure/recovery e focais afetados antes do novo FULL.
Nova identidade V2 e recuperação próprias; V1 não é renomeada nem sobrescrita.
Rollback continua restrito ao delta e à cópia; não transferir aceite anterior.
