# Campanha local vigente — refatoração finita 20260910

Contrato: [REFACTOR-CAMPAIGN-20260910](REFACTOR-CAMPAIGN-20260910.md). Quatro lotes N1 autorizados pelo objetivo ativo: PF inline, rótulos Alladin, seleção da busca e ativação overview FX. Branch `codex/refactor-campaign-20260910`, base `e770e1b66a87e93f52f40eab83479d7a26be2cd4`. Um escritor; fontes/testes/derivados e CTX delimitados no contrato. NAV-REF-01 integrado não é refeito. Sem staging/commit/publicação ou novo lote além dos quatro fixados.

Evidências externas: `/Users/joaopauloalves/.codex/refactor-campaigns/20260910/evidence`. Resultado para revisão humana após caracterização, gates, auditoria e recuperação; execução não concede aceite. Candidate documental de codex/nav-ref-context, main, stash e outras tarefas preservados. Todos os cabeçalhos/contratos abaixo são históricos, não autorização vigente desta campanha. Dívidas anteriores permanecem.

---

# Tarefa delimitada — NAV-REF-01: projeção da navegação local

Contrato: [CHG-NAV-LOCAL-PROJECTION-20260910](CHG-NAV-LOCAL-PROJECTION-20260910.md), CHG/CTX N1/A2. Escolha A do proprietário autoriza somente os sete caminhos e verificações delimitados, na branch `codex/nav-local-projection`, base `b3054e1da1a4a2f2a5ddefd8d715432d7719e636`. Criação/uso desta branch recebeu autorização específica; sem commit, tag, push, PR, merge ou deploy.

Objetivo: separar decisão local dos efeitos, preservando os contratos examinados, inclusive histórico Exec e visões PF sem canonical. Sem regras financeiras, persistência, layout ou contexto geral. Teste de contrato primeiro na baseline e depois no candidate; consumidores, standard, reprodutibilidade, PWA e auditoria focal. Resultados e recuperação em `tools/.artifacts/nav-local-projection-20260910/`; nenhuma aprovação é antecipada por este cabeçalho. Rollback somente do próprio delta após conferência, sem reset/stash/limpeza.

Todo o conteúdo abaixo é histórico preservado integralmente, não autorização para outras tarefas. Dívidas anteriores permanecem abertas.

---

# Tarefa delimitada — CUR-VIG-01: referências e vigência

Contrato: [CONTEXT-CURATION-20260910](CONTEXT-CURATION-20260910.md), CHG/CTX N3/A4. O proprietário escolheu A para o lote delimitado: AGENTS.md, README.md, este cabeçalho e o contrato próprio, na branch `codex/context-curation`, a partir de `8d6b156da6b22f3119471ca2a2c7f1a3524554b1`.

Implementação e validações focais/FULL/auditoria autorizadas; resultados e fingerprint devem ser conferidos nas evidências em `tools/.artifacts/context-curation-20260910/`. Isso não concede aceite nem commit, push, PR, merge ou deploy. Sem produto, novas skills, atualização geral de contexto, reindexação ou alteração de permissões.

A instalação X1 abaixo já foi integrada pelo PR #9 na base indicada; o texto original é preservado como registro da sua etapa de instalação. Todos os cabeçalhos e contratos abaixo são históricos, com autoridade limitada às respectivas decisões: não representam automaticamente a tarefa corrente. AUD-05/P2, limitações anteriores e a dívida estrutural V4 permanecem registradas, sem promoção de falha a PASS.

---

# Tarefa delimitada — adoção permanente da X1

Contrato: [X1-DESIGN-INSTALL-20260910](X1-DESIGN-INSTALL-20260910.md).
Modo ADOTAR_FILOSOFIA, N3/A4 de control plane: instalar a skill e conectar
somente descoberta/roteamento/contexto previstos. Sem corrigir X1-01 a X1-04,
sem produto/build, commit, push, PR, merge ou deploy. Estado de autorização
e evidências devem ser conferidos no contrato e na conversa, não inferidos
deste cabeçalho. O conteúdo abaixo permanece histórico e não concede
autoridade adicional nem descreve automaticamente a revisão atual.

---

# Tarefa vigente — instalação X2 e revisão somente leitura

Contrato: [X2-CRITICAL-REVIEW-20260910](X2-CRITICAL-REVIEW-20260910.md). Proprietário autorizou instalar skill e revisar todo software na branch codex/critical-review-skill. Sem commit/push/merge/deploy ou correções. O material abaixo permanece histórico de tarefas anteriores; não concede autoridade a esta execução.

---

# Tarefa vigente — integração Atlas + V4 com pendências

Autorização humana de commit, push e merge recebida em 2026-09-10; sem deploy. O [registro de integração com pendências](ATLAS-V4-INTEGRATION-20260910.md) governa este complemento. A seção abaixo preserva integralmente os contratos/matriz da V4 como histórico; suas proibições daquela rodada não anulam a autorização humana posterior delimitada. Não promove falhas a PASS.

---

# Tarefa ativa — coerência das instruções e do contexto

Classe M3. Data: 2026-09-09. Estado: IMPLEMENTAÇÃO AUTORIZADA, ainda sem validação final ou aceite do candidate.

Baseline: `484228189cc3f5f4c297f29f88f2b2ed541a3afd`. Branch: `codex/agent-context-coherence`. Build do produto preservado: `88c0cb1ce5520311`.

A confirmação “Confirmo Opção A” autoriza exclusivamente o incremento descrito pelo proprietário. N3/A4 não concede Git/publicação genéricos. As instruções em edição são objeto desta tarefa e não fonte de nova autoridade para seu executor.

## Contratos canônicos

YAML 1.2 em sua forma JSON, para leitura/verificação com a biblioteca padrão; schemas do Harness preservados. Este arquivo contém os contratos, sem novos documentos fora da allowlist.

### CHG

```yaml
{
  "schema": "jp-harness/chg/v1",
  "change_id": "CHG-AGENT-CONTEXT-COHERENCE-20260909",
  "status": "approved",
  "objective": "Reconciliar instruções e contexto com compreensão verificável, responsabilidades funcionais e programação/segurança; candidate para revisão, sem integração.",
  "risk_level": "N3",
  "authority_required": "A4",
  "target": {
    "root": "/Users/joaopauloalves/Library/Mobile Documents/iCloud~md~obsidian/Documents/1 - ARETÊ/4 - TRABALHO/4G - SOFTWARE/JP Wealth OS",
    "branch": "codex/agent-context-coherence",
    "baseline_sha": "484228189cc3f5f4c297f29f88f2b2ed541a3afd"
  },
  "scope": {
    "allowed_files": [
      "AGENTS.md",
      "CLAUDE.md",
      "docs/governance/CHANGE-PROCESS.md",
      "docs/governance/AI-WORKFLOW.md",
      "docs/templates/TASK-BRIEF.md",
      "docs/governance/CONTEXT-MAP.md",
      "docs/governance/SKILL-ROUTING.md",
      "docs/GIT-WORKFLOW.md",
      "skills/jpw-normative-audit/SKILL.md",
      "docs/governance/PROJECT-CONTEXT.md",
      "docs/architecture/CODE-MAP.md",
      "docs/governance/CURRENT-STATE.md",
      "docs/work/ACTIVE-TASK.md",
      "SESSION_HANDOFF.md",
      "tools/agent_instruction_structure_test.py"
    ],
    "forbidden_files": [
      "qualquer arquivo fora de allowed_files",
      "produto, interface, source, normas financeiras, dados e artefatos gerados",
      "Harness mestre, skills importadas congeladas, CI, configurações e permissões globais, grafo/índices"
    ],
    "allowed_actions": [
      "criar e usar somente codex/agent-context-coherence a partir da baseline revalidada",
      "editar somente a allowlist e formalizar CHG/CTX neste ACTIVE-TASK",
      "executar teste estrutural, cenários sintéticos, sessões novas disponíveis, gate full e auditoria independente focal"
    ],
    "forbidden_actions": [
      "commit no produto",
      "push",
      "PR",
      "merge",
      "deploy",
      "amend",
      "rebase",
      "force-push",
      "outra branch ou worktree",
      "alterar remoto ou proteções",
      "stash ou descarte de trabalho preexistente",
      "reindexar ou consultar Graphify com escrita",
      "mudar o próprio gate para aprovar"
    ],
    "regressions_forbidden": [
      "perder ou enfraquecer restrições existentes",
      "alterar produto, cálculos, schema, persistência ou preferências",
      "promover histórico, hipótese, grafo antigo ou aceite antigo a autoridade atual",
      "usar instruções novas para ampliar autoridade nesta execução"
    ]
  },
  "derived_artifacts": {
    "allowed": [
      "evidências e fixtures sintéticas isoladas em /private/tmp/jpw-agent-context-coherence-uuytlubj",
      "arquivos temporários e tools/.artifacts produzidos pelos testes existentes; não incluir no candidate"
    ],
    "generation_commands": [
      "Python existente: tools/agent_instruction_structure_test.py",
      "Python existente: tools/quality_gate.py --tier full --artifact <evidence>/quality-full.json",
      "geradores oficiais chamados pelo gate; outputs do produto devem permanecer byte a byte iguais"
    ],
    "manual_edit": "forbidden"
  },
  "external_side_effects": {
    "network": "allowed",
    "allowed_targets": [
      "loopback de testes",
      "serviços já autenticados de Codex/Claude apenas para as sessões de teste autorizadas com fixtures sintéticas; sem nova API paga, dados reais ou arquivos privados não pertinentes"
    ],
    "temporary_artifacts": "allowed",
    "cleanup_required": true
  },
  "data": {
    "test_policy": "synthetic_only",
    "approved_real_data": [],
    "schema_change": "forbidden"
  },
  "toolchain": {
    "dependency_changes": [],
    "allowed_processes": [
      "Python/Node/Chromium/Playwright já instalados usados pelo gate",
      "Codex/Claude existentes em sessões isoladas e somente leitura",
      "Git read-only no produto, salvo criação/uso da branch explicitamente autorizada",
      "git init/commits sintéticos apenas nas fixtures descartáveis necessárias"
    ]
  },
  "acceptance_criteria": [
    "matriz antes/depois preserva cada restrição",
    "finalidades, fontes, consumidores, limites e evidências constam do brief e roteamento",
    "carregamento seletivo e tratamento de histórico/contexto ausente/injeção/escopo verificados",
    "orientação, comportamento observado e bloqueio técnico distintos",
    "produto e dados inalterados",
    "candidate congelado por fingerprint e auditoria independente; indisponibilidade classificada, sem falsa aprovação"
  ],
  "approved_tests": [
    "teste focal estrutural com casos negativos em cópias sintéticas",
    "sete cenários comportamentais do diagnóstico e observação das fontes/ações",
    "sessões novas Codex e Claude quando disponíveis; indisponibilidade NOT_RUN",
    "gate full existente, sem mudança de expectativas ou CI",
    "auditoria independente focal do candidate congelado"
  ],
  "rollback": {
    "source": [
      "reverter somente o delta próprio com comparação ao baseline; remover somente o teste novo se necessário; nenhum reset/restore amplo"
    ],
    "application_state": [
      "não acessar nem modificar estado real"
    ],
    "data": [
      "nenhuma migração, reset ou descarte; preservar stash"
    ],
    "environment": [
      "encerrar somente processos de teste próprios; preservar evidências locais sintéticas para revisão; fixtures descartáveis não alteram configuração global"
    ],
    "verification": [
      "comparar hashes fora da allowlist, main/HEAD, worktree e stash com baseline; confirmar grafo intacto"
    ]
  },
  "approved_by": "proprietário — confirmação conversacional “Confirmo Opção A” para este incremento",
  "approved_at": "2026-09-09T19:37:08-03:00",
  "expires_on": [
    "raiz ou branch mudar",
    "baseline divergir materialmente",
    "escopo, risco ou autoridade mudar",
    "trabalho concorrente incompatível",
    "necessidade de editar fora da allowlist ou reduzir proteção",
    "novo efeito externo não coberto"
  ]
}
```

### CTX

```yaml
{
  "schema": "jp-harness/ctx/v1",
  "context_change_id": "CTX-AGENT-CONTEXT-COHERENCE-20260909",
  "status": "approved",
  "root": "/Users/joaopauloalves/Library/Mobile Documents/iCloud~md~obsidian/Documents/1 - ARETÊ/4 - TRABALHO/4G - SOFTWARE/JP Wealth OS",
  "mode": "SEQUENCIAL",
  "approved_branch": "codex/agent-context-coherence",
  "create": [
    "tools/agent_instruction_structure_test.py"
  ],
  "modify": [
    "AGENTS.md",
    "CLAUDE.md",
    "docs/governance/CHANGE-PROCESS.md",
    "docs/governance/AI-WORKFLOW.md",
    "docs/templates/TASK-BRIEF.md",
    "docs/governance/CONTEXT-MAP.md",
    "docs/governance/SKILL-ROUTING.md",
    "docs/GIT-WORKFLOW.md",
    "skills/jpw-normative-audit/SKILL.md",
    "docs/governance/PROJECT-CONTEXT.md",
    "docs/architecture/CODE-MAP.md",
    "docs/governance/CURRENT-STATE.md",
    "docs/work/ACTIVE-TASK.md",
    "SESSION_HANDOFF.md"
  ],
  "merge": [
    {
      "source": "CLAUDE.md",
      "target": "AGENTS.md",
      "source_must_remain": true
    }
  ],
  "preserve": [
    "normas financeiras e decisões",
    "auditorias e histórico Git",
    "produto/artefatos",
    "stash bfdb323f05f0df27c79fd11cb18d64352a5c5194"
  ],
  "do_not_touch": [
    "Harness mestre",
    "skills/repository-architecture/",
    "skills/agentic-evolution-governance/",
    "graphify-out/",
    "CI e configurações globais",
    "arquivos fora da allowlist CHG"
  ],
  "archive_requires_confirmation": [],
  "source_of_truth": {
    "autoridade_desta_execucao": "pedido delimitado e confirmação Opção A; este contrato registra, não amplia",
    "engenharia": "JP SOFTWARE ENGINEERING HARNESS - MASTER SPECIFICATION.md §28 e §36–48",
    "produto_observado": "código/contratos da baseline 484228189cc3f5f4c297f29f88f2b2ed541a3afd",
    "finalidades": "definições do proprietário e docs/governance/PROJECT-CONTEXT.md",
    "instrucoes": "AGENTS.md; CLAUDE.md importa e adapta sem permissões adicionais"
  },
  "information_promotion": [
    {
      "from": "diagnóstico A0/A1 e fontes verificadas na baseline",
      "to": "PROJECT-CONTEXT, CODE-MAP, CONTEXT-MAP, CURRENT-STATE, ACTIVE-TASK e SESSION_HANDOFF",
      "reason": "reconciliar finalidade, navegação integrada e instruções; não promover testes/aceites antigos"
    }
  ],
  "expiration_rules": [
    {
      "artifact": "CURRENT-STATE, ACTIVE-TASK e SESSION_HANDOFF",
      "event": "mudança material do Git/candidate, tarefa, contrato ou ambiente de validação"
    },
    {
      "artifact": "grafo existente",
      "event": "já STALE; nenhuma atualização autorizada"
    }
  ],
  "privacy_actions": [
    "fixtures sintéticas",
    "sem segredos/dados reais em evidências ou indexação",
    "sem leitura de conteúdo privado fora das fontes pertinentes"
  ],
  "acceptance_criteria": [
    "matriz antes/depois preserva cada restrição",
    "finalidades, fontes, consumidores, limites e evidências constam do brief e roteamento",
    "carregamento seletivo e tratamento de histórico/contexto ausente/injeção/escopo verificados",
    "orientação, comportamento observado e bloqueio técnico distintos",
    "produto e dados inalterados",
    "candidate congelado por fingerprint e auditoria independente; indisponibilidade classificada, sem falsa aprovação"
  ],
  "approved_by": "proprietário — confirmação conversacional “Confirmo Opção A” para este incremento",
  "approved_at": "2026-09-09T19:37:08-03:00",
  "expires_on": [
    "raiz ou branch mudar",
    "baseline divergir materialmente",
    "escopo, risco ou autoridade mudar",
    "trabalho concorrente incompatível",
    "necessidade de editar fora da allowlist ou reduzir proteção",
    "novo efeito externo não coberto"
  ]
}
```

## Compreensão e impacto

Fonte de engenharia examinada: JP Software Engineering Harness Master Specification
V2.0, SHA256 `d894384c88f414ace7b593c9dd88d299b882c5d78c7b3e144859d210aef2a770`.

Na conferência posterior, a fonte foi localizada como
`00 - HARNESS - JP Wealth MASTER SPECIFICATION.md`, no mesmo diretório externo.
O Core examinado corresponde exatamente aos primeiros 52.054 bytes desse arquivo:
o hash desse prefixo é o registrado acima. O arquivo integral tem SHA256
`c1b5ca9da4dfa2c9a9d1fa3d87a9f7ef9c4cb741fffeedee33d37978f5b800c8` e contém
mais 7.207 bytes de um pedido de estudo A0/A1, sem declaração de nova versão
canônica. A referência de AGENTS foi corrigida; a norma aplicada continua sendo
o Core identificado, sem executar o pedido anexado nem ampliar esta autorização.
Fonte externa somente lida, sem alteração; se divergir, revalidar o alcance pertinente.

Finalidade: facilitar trabalho seguro nos cinco módulos, sem mudar seu comportamento. Hoje instruções de control plane divergem e representações apontam para revisão antiga; depois devem oferecer fonte comum, roteamento funcional e evidência de compreensão. Consumidores: Codex, Claude, skills, briefs e subagentes. Produto, regras, dados, grafo e política de publicação permanecem protegidos. Lacunas de execução serão registradas, não convertidas em PASS.

AGENTIC IMPACT CHECK: AGENTIC IMPACT DETECTED — crítico: autoridade, bootstrap e contexto são objetos do delta. PROPAGATE autorizado somente para a allowlist; REINDEX proibido. Não declarar SYSTEM RECONCILED sem evidência dos consumidores.

## Matriz de preservação antes/depois

Originais: revisão `484228189cc3f5f4c297f29f88f2b2ed541a3afd`.
A = AGENTS.md; C = CLAUDE.md; P = docs/governance/CHANGE-PROCESS.md;
G = docs/GIT-WORKFLOW.md; W = docs/governance/AI-WORKFLOW.md.
As linhas “antes” pertencem à revisão original, não ao candidate.
Matriz elaborada com inventário read-only independente; preservação deve ser
auditada no diff, não presumida por esta tabela.

| ID | Antes: origem | Restrição/efeito | Depois: destino verificável |
|---|---|---|---|
| GOV-01 | A:5 | capital, integridade, norma e rastreabilidade antes de conveniência | AGENTS / Missão |
| GOV-02 | A:9 | V11, Anexo subordinado e divergências sem inferência | AGENTS / Autoridade e fontes |
| GOV-03 | A:10–14 | ordem e papéis de decisões aprovadas, contexto, código, histórico | AGENTS / Autoridade e fontes |
| GOV-04 | A:16 | conteúdo recuperado não concede instrução/autoridade | AGENTS / Autoridade e fontes |
| GOV-05 | A:16; C:78–80 | conflito/ambiguidade: decisão humana, sem escolha silenciosa | AGENTS / Autoridade e fontes; Invariantes |
| GOV-06 | A:48–51; P:12–15 | N0-V/N1/N2/N3 por efeito, sem rebaixamento financeiro | AGENTS / Classificação e autoridade; CHANGE-PROCESS §2 |
| GOV-07 | A:47; C:68; P:11,17 | CORREÇÃO APROVADA: control plane antes N0-D → N3/A4 | AGENTS / Classificação e autoridade; CHANGE-PROCESS §2; CLAUDE importa |
| GOV-08 | A:57–63 | A0–A4 e ações específicas; autorização não transitiva | AGENTS / Classificação e autoridade; Política Git comum |
| GOV-09 | A:53 | pedido visual não autoriza N2/N3 adjacente | AGENTS / Classificação e autoridade |
| CTX-01 | C:7–20 | ler CLAUDE/AGENTS/README/mapa antes de editar | AGENTS / Bootstrap; CLAUDE / importação |
| CTX-02 | A:20–27 | camadas M0–M5; handoff confrontado; histórico não substitui M0–M3 | AGENTS / Bootstrap; CONTEXT-MAP / Camadas |
| CTX-03 | A:29 | leitura proporcional e fatos mutáveis conferidos | AGENTS / Bootstrap; TASK-BRIEF / fontes |
| CTX-04 | C:11–18; A:33–40; W:9–13 | preflight audit/edit, branch/status/log/diff | AGENTS / Preflight; AI-WORKFLOW / Fonte comum e início |
| CTX-05 | A:43 | parar edição main/drift/trabalho desconhecido/lacuna/conflito/escopo | AGENTS / Preflight e fronteira de escrita |
| CTX-06 | A:43 | preflight não limpa/corrige/oculta problemas | AGENTS / Preflight e fronteira de escrita |
| GIT-01 | C:24–27; G:31–35 | main oficial; tarefa coerente em branch própria de main | AGENTS / Política Git comum |
| GIT-02 | C:28–30; G:11–12,40–41 | branch indicada; sem troca autônoma; divergência bloqueia | AGENTS / Política Git comum |
| GIT-03 | C:31; A:43 | parar/relatar mudanças não relacionadas; preservar autoria | AGENTS / Preflight; Política Git comum |
| GIT-04 | C:32 | sem múltiplas worktrees/pastas não autorizadas | AGENTS / Política Git comum |
| GIT-05 | C:34–49 | commit/push/pull/merge/rebase/reset/stash/force-push/branch/tag/remoto/worktree exigem autorização específica | AGENTS / Política Git comum; GIT-WORKFLOW referencia |
| GIT-06 | A:78 | Git destrutivo e reescrita só com autorização expressa | AGENTS / Política Git comum |
| GIT-07 | A:61–63,105; C:51; P:63 | edição, teste, revisão, commit, envio, integração e publicação separados | AGENTS / Classificação e autoridade; Encerramento |
| GIT-08 | P:63 | não commitar gate vermelho salvo pedido específico para preservar baseline vermelho | AGENTS / Política Git comum; CHANGE-PROCESS / Promover |
| GIT-09 | P:65–74 | modelo commit com nível/regra/dados/testes quando autorizado | CHANGE-PROCESS / Promover, preservado |
| FIN-01 | A:67 | não inventar/otimizar/reinterpretar regra financeira | AGENTS / Invariantes financeiros, dados e execução |
| FIN-02 | A:68 | percentuais/fatores/limites/fórmulas/artigos só A4 | AGENTS / Invariantes |
| FIN-03 | A:71 | não remover bloqueios instrumentos/quarentena/LIFO/MDD/governança | AGENTS / Invariantes |
| FIN-04 | A:53; P:15 | N3 financeiro: decisão, exemplos, caracterização, gestor/full | AGENTS / Classificação; CHANGE-PROCESS §2 |
| FIN-05 | C:78–80 | quadrifásico/Gênese/retração/NoCoda/validade: ambiguidades exigem decisão | AGENTS / Invariantes; roteamento normativo preservado |
| DATA-01 | A:69; C:85 | não apagar/migrar/normalizar real sem backup+A3/A4; sem apagar silencioso | AGENTS / Invariantes |
| DATA-02 | A:70 | erro não troca estado por DEFAULTS | AGENTS / Invariantes |
| DATA-03 | P:36–37 | DEFAULTS/migrate/import/exclusão N2; constantes/fórmulas N3 | AGENTS / Invariantes; CHANGE-PROCESS / Implementar |
| DATA-04 | A:53; P:14 | N2: backup anonimizado/fixture, compatibilidade, ida e volta, full e autorização | AGENTS / Classificação; CHANGE-PROCESS §2 |
| DATA-05 | C:86; P:26 | backup só muda autorizado; dados antigos preservados | AGENTS / Invariantes; TASK-BRIEF / Compatibilidade |
| SEC-01 | A:72 | não solicitar/armazenar/registrar/versionar senha master | AGENTS / Invariantes |
| SEC-02 | A:73 | sem credenciais/tokens/dados pessoais em código/testes/logs/docs | AGENTS / Invariantes; prompts/índices acrescentados sem revogar proibição |
| RUN-01 | A:74; C:84 | proibido localStorage.clear() | AGENTS / Invariantes |
| RUN-02 | A:75 | ordem de scripts exige manifest+carga no navegador | AGENTS / Invariantes |
| RUN-03 | A:76; C:87,96 | gerados só pelo gerador oficial quando aplicável | AGENTS / Invariantes |
| RUN-04 | C:88–89 | não sobrescrever PWA; preservar ciclo conservador SW | AGENTS / Invariantes |
| RUN-05 | A:122 | scripts clássicos; migração não incidental, projeto/mapa/regressão próprios | AGENTS / Invariantes |
| ENG-01 | C:55–62 | investigar código/dependências, plano, risco, autorização antes de edição | AGENTS / Preflight; autorização já recebida reaproveitada |
| ENG-02 | P:5; A:96–98 | raiz/branch/base/árvore/objetivo/arquivos; auditoria só leitura | AGENTS / Preflight; TASK-BRIEF |
| ENG-03 | P:21–28 | atual/desejado, invariantes, antigos, aceite, rollback | TASK-BRIEF; CHANGE-PROCESS / Definir contrato |
| ENG-04 | A:77,100; C:90; P:32–34 | menor diff, uma causa, sem refatoração/formatação/renomeação/correção adjacente | AGENTS / Práticas; CHANGE-PROCESS / Implementar |
| ENG-05 | A:99; P:35 | caracterização não coberta e regressão quando praticável | AGENTS / Programação e segurança aplicadas |
| ENG-06 | A:101–102; C:97; P:41 | focais durante iteração, gate no candidate final | AGENTS / Skills, validação e encerramento |
| ENG-07 | P:11–15 | tiers e verificações por risco, full N2/N3 | CHANGE-PROCESS §2; AGENTS / Classificação |
| ENG-08 | P:17 | expectativa alterada exige comportamento aprovado; não enfraquecer teste | AGENTS / Programação; CHANGE-PROCESS §2 |
| EVD-01 | A:109–116; C:123 | taxonomia única dos seis resultados | AGENTS / Skills, validação e encerramento |
| EVD-02 | A:118 | sem PASS por leitura/antigo/parcial; comando/candidate/ambiente | AGENTS / Evidência; AI-WORKFLOW / Verificação |
| EVD-03 | P:41 | mudança material invalida gate afetado | AGENTS / Encerramento; CHANGE-PROCESS / Verificar |
| EVD-04 | A:103; C:98–107; P:43–49 | status/diff-check/stat/lista/diff integral | AGENTS / Encerramento |
| EVD-05 | P:52–59; C:108–109 | causa/regra/dados/cenários/riscos/recuperação/NOT_RUN | AGENTS / Encerramento; TASK-BRIEF |
| EVD-06 | A:104 | contexto/auditoria/changelog/handoff afetados | AGENTS / Encerramento, subordinado ao CHG/CTX; sem escrita fora do escopo |
| EVD-07 | C:110,133; G:55–56 | aguardar teste manual do proprietário | AGENTS / Encerramento; CLAUDE importa; GIT-WORKFLOW |
| EVD-08 | A:126; C:127–134 | prontidão técnica, aceite/teste humano e autorização de commit distintos | AGENTS / Encerramento, nenhum gate eliminado nem commit imposto |
| SKL-01 | A:82–92 | todos os gatilhos obrigatórios de skills | SKILL-ROUTING; AGENTS referencia; change-control mantém toda tarefa por fase |
| AI-01 | W:5 | arquivos/Git compartilhados, memória não implícita; fonte atual | AI-WORKFLOW / Fonte comum e início |
| AI-02 | W:17–19 | tarefa coerente, sem sobreposição; principal revisa; sem transferência de autoridade | AI-WORKFLOW / Packet obrigatório |
| AI-03 | W:20–22 | saída não confiável até conferir; handoff vs disco; memória não vira norma | AI-WORKFLOW / Packet obrigatório |
| AI-04 | W:39–41 | não mascarar falha; escopo superior pede autorização; conflito bloqueia delta | AI-WORKFLOW / Execução e segurança |
| AI-05 | W:45–53 | handoff mínimo com base/ações/evidências/risco/limites sem segredos | AI-WORKFLOW / Handoff e encerramento |

## Impacto e reconciliação delimitada

| Categoria | Impacto | Ação local | Estado/limite |
|---|---|---|---|
| Instruções AGENTS/CLAUDE | AFFECTED | REQUIRED, allowlist | Fonte comum e adapter do candidate; carregamento deve ser testado |
| Skills locais | AFFECTED | REQUIRED só normative-audit; demais NOT_REQUIRED por referência | Gatilhos/limites financeiros preservados; imports congelados intocados |
| Routing e brief | AFFECTED | REQUIRED | Finalidade/consumidores/síntese e packet explícito |
| Contexto operacional | AFFECTED | REQUIRED | Produto base identificado; resultados anteriores não promovidos |
| Arquitetura | AFFECTED | REQUIRED só CODE-MAP/PROJECT-CONTEXT e rota | Contratos funcionais existentes preservados; nenhum runtime alterado |
| Harness/fonte financeira | AFFECTED como referências | NOT_REQUIRED | Fontes preservadas; correção do consumidor N0-D→N3 aprovada |
| Guards/gates/CI | AFFECTED como consumidores de docs | NOT_REQUIRED | Preflight/gates existentes não viram enforcement de autorização; teste focal separado |
| Subagentes executáveis | AFFECTED | NOT_REQUIRED criar agentes | Packet explícito; nenhum agente por pasta |
| Instruções globais/ancestrais | UNKNOWN quanto ao carregamento completo | NOT_REQUIRED nesta allowlist | Não editadas; teste isolado não prova todas as instalações |
| Índice/grafo | AFFECTED; drift anterior ao delta | FORBIDDEN | STALE na revisão a3052d2; INDEX BLOCKED por escopo; leitura direta permanece |
| Histórico e produto | NOT_AFFECTED em conteúdo | NOT_REQUIRED | Preservação por hashes/diff; histórico correto não reescrito |

Há mudança material de control plane no delta sem commit; não há nova revisão
material do produto financeiro. Reconciliação de fontes selecionadas não equivale
a SYSTEM RECONCILED nem atualização de todos os consumidores/índices.

## Evidências e candidate

Evidências isoladas: `/private/tmp/jpw-agent-context-coherence-uuytlubj`.
O manifest `candidate.json` identifica hashes completos do conjunto final e
baseline; `candidate.diff` contém o diff inclusive o teste novo.
Os relatórios de execução e auditoria ficam no mesmo diretório, fora do produto.
Este texto não antecipa seus resultados: a entrega deve confrontar fingerprint,
comandos e conclusões reais. Compromissos humanos de aceite/integração permanecem pendentes.

A prova estrutural é somente nível A: presença/referências/imports/contratos.
Sessões novas e ações observadas são nível B; barreira efetivamente testada é C.
O preenchimento de approved_by registra a confirmação conversacional e não é
validação técnica de identidade/autoridade humana.

Para as sessões sintéticas, a descoberta local identificou Codex CLI autenticado
e não localizou cliente Claude. Ausência de Claude será NOT_RUN, não uma declaração
de compatibilidade. Canários de sandbox ficam isolados; não se generaliza um
bloqueio de escrita para restrição de leitura ou para todas as ferramentas.
