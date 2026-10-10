# Fotografias anteriores à integração de 2026-10-09

## Site validado

# Tarefa ativa — JPW Scenario Fan

Pedido humano corrente: refinar a semelhança visual com a referência renderizada, mantendo o plano completo de trajetórias patrimoniais e identidade visual já implementado.

Produto: [N1/A2](CHG-JPW-SCENARIO-FAN-UI-20261008.md). Descoberta para agentes: [N3/A4 separado](CHG-JPW-SCENARIO-FAN-CONTROL-20261008.md). Skill: [N3/A4 separado](CHG-JPW-SCENARIO-FAN-SKILL-20261008.md). Provas: [contrato focal](CHG-JPW-SCENARIO-FAN-TESTS-20261008.md). Base `1591f527ada923d4`; 104 deltas conhecidos preservados. CHGs do refinamento visual e catálogo informativo fora dos fontes em `reference-revision/CHG.json` e `CHG-CATALOG.json`. Não houve novas permissões, consumidores ou alteração das fences aprovadas.

Revisão visual corrente concluída no candidate local `363e2e7b56a86ced`. 57/57 PASS no full bruto; 46/46 PASS no subconjunto STANDARD da mesma execução FULL (não execução CLI separada). Renderer/CSS exatos passaram focal 16/16, regressão gráfica mensal 8/8 e contraprova independente 8/8 mais preservação de cursor. HTTP, file, portátil e PWA offline passaram 4/4 na distribuição corrigida; zoom nativo Chrome 200% e demonstração em 1440/390/320 px também conferidos. Integridade independente verificou manifesto, 102 scripts, quatro assets e réplica fiel de 899 caminhos. Evidências externas em `/private/tmp/jpw-scenario-fan-20261008/reference-revision`.

Histórico preservado: a entrega inicial `ffa80ce18f1e7e5d` passou seu escopo técnico, mas o proprietário rejeitou a semelhança visual. A build intermediária `4cded3c51310acf0` teve 54 PASS e 3 PRODUCT_FAIL brutos: preflight/structure por hash declarado antigo e pivot-studies por erro de inicialização. O manifesto foi corrigido mecanicamente, seguido dos geradores e validadores oficiais. Três replays iguais de Pivôs passaram, sem esclarecer a causa inicial; o recibo anterior permanece inalterado. Gates parciais interrompidos e erros dos probes externos também foram preservados, sem inferir PASS.

O refinamento aproxima a anatomia do PriceTargetFan mantendo dados mensais exatos, lacunas, consulta acessível e fallback estreito. No produto nenhum cenário é escolhido automaticamente; somente a demonstração fictícia começa com duas hipóteses. Fórmulas, writers, schemas, MT5, julgadores e autoridade permanecem iguais à base desta campanha. Aceite estético humano, integração e publicação são separados e pendentes. Safari, tecnologia assistiva nativa, toque físico, hospedagem operacional e MT5 nativo NOT_RUN. Notas de encerramento são o único delta documental posterior ao gate; runtime preservado.

```yaml
{
  "schema": "jp-harness/chg/v1",
  "change_id": "CHG-JPW-SCENARIO-FAN-CONTROL-20261008",
  "status": "approved",
  "approved_by": "Proprietario — pedido humano corrente: PLEASE IMPLEMENT THIS PLAN",
  "approved_at": "2026-10-08T19:38:30.687129+00:00",
  "authorization_evidence": "Plano completo de trajetorias patrimoniais e identidade visual aprovado nesta conversa; reconhecimento da autorizacao, nao aceite do candidate final.",
  "objective": "Registrar componente e descoberta focal sem alterar autoridade/juiz",
  "risk_level": "N3",
  "authority_required": "A4",
  "target": {
    "root": "/private/tmp/jpw-scenario-fan-20261008/candidate",
    "branch": "codex/onboarding-first-access-20261007",
    "baseline_sha": "7f0828488b2fc0ea62dc7c421174799cda47a34a"
  },
  "scope": {
    "allowed_files": [
      "docs/design/SCENARIO-FAN.md",
      "docs/governance/SKILL-ROUTING.md",
      "docs/architecture/FEATURE-ATLAS.md",
      "docs/governance/CONTEXT-MAP.md",
      "docs/governance/CURRENT-STATE.md",
      "SESSION_HANDOFF.md",
      "docs/work/ACTIVE-TASK.md",
      "docs/work/CHG-JPW-SCENARIO-FAN-UI-20261008.md",
      "docs/work/CHG-JPW-SCENARIO-FAN-CONTROL-20261008.md",
      "docs/work/CHG-JPW-SCENARIO-FAN-TESTS-20261008.md",
      "docs/work/CHG-JPW-SCENARIO-FAN-SKILL-20261008.md",
      "docs/work/HISTORY-ACTIVE-SCENARIO-FAN-BASELINE-20261008.md",
      "docs/work/HISTORY-STATE-SCENARIO-FAN-BASELINE-20261008.md"
    ],
    "forbidden_files": [
      "docs/normative/",
      "docs/decisions/",
      "tools/quality_gate.py",
      "tools/validate_project.py",
      "tools/agent_instruction_structure_test.py",
      "tools/feature_atlas_test.py",
      ".github/",
      "downloads/ — alteracoes manuais",
      "src/js/30-accounting/05-fx-planning/01-fx-model.js",
      "src/js/30-accounting/05-fx-planning/02-fx-engine.js",
      "src/js/30-accounting/05-fx-planning/03-fx-state.js"
    ],
    "allowed_actions": [
      "Editar somente delta delimitado em copia isolada",
      "Testes sinteticos, revisao independente e geradores oficiais"
    ],
    "forbidden_actions": [
      "Git mutation",
      "publicacao",
      "dados reais",
      "schema/formula financeira",
      "alterar gates ou classificadores",
      "Graphify/reindexacao"
    ],
    "regressions_forbidden": [
      "Ampliar autoridade ou enfraquecer gates",
      "Falsificar validacao ou homologacao",
      "Reescrever historico"
    ]
  },
  "derived_artifacts": {
    "allowed": [],
    "generation_commands": [],
    "manual_edit": "forbidden"
  },
  "external_side_effects": {
    "network": "allowed",
    "allowed_targets": [
      "loopback para perfis sinteticos"
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
      "python3",
      "node",
      "Chromium descartavel",
      "git read-only"
    ]
  },
  "acceptance_criteria": [
    "Valores iguais aos produtores, lacunas preservadas, zero escrita por consulta",
    "Selecao grafica independente da edicao, ate dois cenarios",
    "Teclado/toque/temas/adaptacao e alternativas textuais",
    "Evidencia independente sem alegar homologacao ou integracao"
  ],
  "approved_tests": [
    "scenario_fan_test",
    "fx_monthly_chart_test",
    "fx_planning_test",
    "fx_planning_monthly_test",
    "quality_gate standard/full",
    "feature_atlas_test",
    "agent_instruction_structure_test"
  ],
  "rollback": {
    "source": [
      "Restaurar somente delta desta tarefa de /private/tmp/jpw-scenario-fan-20261008/baseline"
    ],
    "application_state": [],
    "data": [],
    "environment": [
      "Encerrar processos descartaveis desta tarefa"
    ],
    "verification": [
      "Hashes originais e ausencia de schema alterado"
    ]
  },
  "expires_on": [
    "Fim da tarefa",
    "Mudanca material de escopo"
  ]
}
```

```yaml
{
  "schema": "jp-harness/ctx/v1",
  "context_change_id": "CTX-JPW-SCENARIO-FAN-20261008",
  "status": "approved",
  "approved_by": "Proprietario — plano integral corrente",
  "approved_at": "2026-10-08T19:38:30.687129+00:00",
  "authorization_evidence": "Registrar componente e descoberta para programadores/agentes no plano aprovado.",
  "root": "/private/tmp/jpw-scenario-fan-20261008/candidate",
  "mode": "CONCORRENTE",
  "approved_branch": "codex/onboarding-first-access-20261007",
  "create": [
    "docs/design/SCENARIO-FAN.md",
    "docs/work/CHG-JPW-SCENARIO-FAN-UI-20261008.md",
    "docs/work/CHG-JPW-SCENARIO-FAN-CONTROL-20261008.md",
    "docs/work/CHG-JPW-SCENARIO-FAN-TESTS-20261008.md",
    "docs/work/HISTORY-ACTIVE-SCENARIO-FAN-BASELINE-20261008.md",
    "docs/work/HISTORY-STATE-SCENARIO-FAN-BASELINE-20261008.md",
    "docs/work/CHG-JPW-SCENARIO-FAN-SKILL-20261008.md"
  ],
  "modify": [
    "docs/governance/SKILL-ROUTING.md",
    "docs/architecture/FEATURE-ATLAS.md",
    "docs/governance/CONTEXT-MAP.md",
    "docs/governance/CURRENT-STATE.md",
    "SESSION_HANDOFF.md",
    "docs/work/ACTIVE-TASK.md"
  ],
  "merge": [],
  "preserve": [
    "104 alteracoes herdadas",
    "Historicos e classificacoes anteriores",
    "Normas, formulas, schemas, MT5 e gates"
  ],
  "do_not_touch": [
    "AGENTS.md",
    "docs/normative/",
    "docs/decisions/",
    "tools/quality_gate.py",
    "tools/agent_instruction_structure_test.py",
    "tools/feature_atlas_test.py",
    ".github/"
  ],
  "source_revision": "7f0828488b2fc0ea62dc7c421174799cda47a34a",
  "archive_requires_confirmation": [],
  "source_of_truth": {
    "human": "Plano integral aprovado nesta conversa",
    "engineering": "AGENTS.md e Harness existentes",
    "design": "docs/design/SCENARIO-FAN.md"
  },
  "information_promotion": [{"from":"Plano integral aprovado nesta conversa","to":"docs/design/SCENARIO-FAN.md","reason":"Registrar somente contrato visual e referencia de reutilizacao; nao promover resultados de testes ou autoridade"}],
  "expiration_rules": [
    {
      "artifact": "docs/governance/CURRENT-STATE.md",
      "event": "Novo delta material ou mudanca de candidate"
    }
  ],
  "privacy_actions": [
    "Somente dados sinteticos; nenhuma base real consultada"
  ],
  "acceptance_criteria": [
    "Fontes atuais ligadas sem declarar runtime por documentacao",
    "Descoberta independente do componente e limites",
    "Gates sem enfraquecimento"
  ],
  "expires_on": [
    "Fim desta tarefa",
    "Mudanca material de escopo"
  ]
}
```

[Historico anterior](HISTORY-ACTIVE-SCENARIO-FAN-BASELINE-20261008.md), sem autoridade corrente.

## Genetrix integrado anteriormente

# Tarefa ativa focal — integrar GENETRIX 1.21.2 — 2026-10-08

Contrato/brief: [CHG-GENETRIX-1-21-2-SITE-20261008](CHG-GENETRIX-1-21-2-SITE-20261008.md), com trilha dedicada N3 dos juízes. Pedido: “integre esse a última versão do site”; Git já autorizado por “Execute commit, push e merge”, sob gates separados. Sem hosting externo, instalação MT5, negociação, armamento ou homologação.

Raiz `/private/tmp/jpw-genetrix-site-1-21-2-20261008`, branch `codex/genetrix-1-21-2-site-20261008`, base `7f0828488b2fc0ea62dc7c421174799cda47a34a`. Esta árvore representa os fontes 1.21.2. Conferir o estágio atual de gates, commit, push e merge e seu recibo Git/PR em INTEGRATION; a presença dos arquivos não demonstra essas ações. Fontes canônicas 132 membros preservadas, cálculo 1.9.0 e sete leituras Conta; Monitor recomendado e Supervisor opcional separado. Não interpretar os cabeçalhos históricos do pacote como estado atual.

Entrega atual: ZIP fontes 1.21.2 SHA256 `a9a77be170036747fec8322fdba7d80bd6256fbcae87e4c6dadb1348ff916261`, 760092 bytes; fingerprint 111 fontes/recursos `9650de7a8573566f3532e3a3ecb2806d0a0e62e2afe7b8130f1331045c06a4b6`. Compilado 1.21.2 indisponível: compilação NOT_RUN, runtime BLOCKED / NOT_RUN conforme percurso, instalação NOT_RUN. Harness 1.0 CANDIDATE, R2 FAIL/R5 parcial históricos conservados. EX5/provas 1.20 ficam no acervo histórico.

Escopo documental deste autor: CHG, esta nota, blocos focais CURRENT-STATE/CONTEXT-MAP, topo do CHANGELOG e [INTEGRATION](../validation/genetrix-1.21.2/INTEGRATION.md). Normas, fórmulas, schemas, dados e 132 membros não são editados. MT5 host final R3 foi conferido: 40/40 PASS, inputs atuais íntegros; web full R3 57/57 PASS; revisão independente em registro próprio. Nenhum resultado de versões anteriores é transferido.

Rollback e critérios no contrato. Expira quando raiz/branch/base/inventário/objetivo ou autoridade mudar materialmente. As tarefas abaixo conservam suas datas e evidências; não descrevem esta integração.

## Histórico anterior preservado

# Correção dos PRODUCT_FAIL pendentes — 2026-10-06

Pedido humano atual: “Solucione todos os product fail pendentes”. Candidate isolado na cópia jpw-product-fail-repair-20261006/candidate, branch herdada codex/saving-reliability-20261006, HEAD ac3a2faffeb398357ff105adbf1d47f70ca309bd. Base 1db5b703ca56d26c, 749 arquivos/fingerprint ce450e0ba50b51388794e52a0840c830f3934b0bbf40d1945fd3701f8becfdb3 preservada, snapshot e recibos anteriores conservados. Preflight --allow-dirty somente após inventário dos deltas herdados. SOURCE REVISION UNKNOWN no contexto histórico permanece, não usado como realidade atual.

O objetivo é remover causas reproduzidas nas cinco falhas gerais e duas MT5 host; investigar intermitência do import e falha do executor de timeout. Não haverá alteração de norma/fórmulas, dados reais, configuração global, execução MT5, EX5, commit, branch, push, merge ou publicação.

Contratos: CHG-JPW-PENDING-FAIL-PRODUCT/TEST e BRIEF-JPW-PENDING-FAIL de 20261006.

## Histórico preservado

# Tarefa corrente — salvamento, backup e recuperação (2026-10-06)

Implementação explícita autorizada pelo proprietário. Contratos CHG-JPW-SAVING-INTEGRITY, SAVING-UI e SAVING-TEST-CONTRACT de 20261006; brief correspondente. Base 4525c1f0755a2ec8 e 63 alterações anteriores preservadas externamente. Candidate isolado, dados sintéticos, sem Git/publicação/MT5. Preflight edit com --allow-dirty após inventário e confirmação da origem das alterações herdadas. Achados e resultados anteriores permanecem separados.

## Histórico preservado

# Tarefa vigente — correção da precisão financeira do DD

Contrato: [CHG-JPW-DD-BOUNDARY-FIX-20261006](CHG-JPW-DD-BOUNDARY-FIX-20261006.md). Autorização do proprietário: “Corrija a falha financeira conhecida”. Compreensão, fontes, escopo e rollback: [brief](BRIEF-JPW-DD-BOUNDARY-FIX-20261006.md). Candidate isolado; norma, política, persistência e testes existentes preservados.

## Histórico anterior preservado

# Tarefa corrente — rastreamento e correção de bugs de interface (2026-10-06)

Pedido humano explícito: rastrear e corrigir bugs da interface. CHG-JPW-INTERFACE-BUGFIX-20261006, N1/A2; base3ea4d24e6b8c3bf7 preservada, escopo somente UI. Fontes financeiras, MT5, persistência e juízes não são alterados. Evidências externas em jpw-interface-bugfix-20261006. Sem Git/publicação.

## Histórico preservado

# Tarefa corrente — Forex por tarefa (2026-10-05)

CHG-JPW-FOREX-TASK-DESIGN-20261005 e contrato separado de testes. Candidate local; base df2caa32013cb2cc preservada. Não representa integração ou publicação.

## Histórico preservado

# Tarefa ativa — painel profissional Forex (2026-10-05)

Candidate isolado; objetivo/autoridade/escopo e testes nos três CHGs JPW-FOREX-PROFESSIONAL e brief correspondente. Baseline preservada em outputs/jpw-forex-professional-panel-20261005/baseline.* fora do candidate. Somente dados sintéticos; sem fórmulas, escrita financeira, MT5 ou integração. Delta implementado; candidate em validação local, com fingerprint, recibos brutos, auditoria e limitações na entrega externa. Resultados anteriores não validam os novos bytes. Aceite manual e integração permanecem separados.

# Tarefa ativa — evolução da conta e risco visual

Base ac3a2fa; candidate local codex/forex-visual-risk-20261005. Produto N1/A2 e testes N3/A4 nos CHGs FOREX-VISUAL-RISK de 20261005. Autorização: implementação do plano; sem Git/publicação, dados reais ou alteração financeira. Candidate implementado para avaliação local. Recibos brutos, auditoria, fingerprint e rollback permanecem no diretório externo outputs/jpw-forex-visual-risk-20261005. A conclusão de cada verificação deve ser lida nesses recibos, sem inferir aprovação pela presença desta interface. DD14 herdado permanece; promoção e publicação não estão autorizadas nesta etapa.

---

## Contexto anterior preservado

# Tarefa ativa local — Operação com proporções de planilha

Candidate local de 2026-10-05, base a47ebee, branch codex/operation-proportions-20261005.

Contratos: [produto](CHG-JPW-OPERATION-PROPORTIONS-20261005.md), [testes](CHG-JPW-OPERATION-PROPORTIONS-TEST-20261005.md), [brief](BRIEF-JPW-OPERATION-PROPORTIONS-20261005.md).

Autorização: implementação do plano pelo proprietário; sem commit, push, merge ou publicação. Invariantes financeiros, dados e MT5 preservados. Resultados históricos permanecem no Git e no snapshot; esta tarefa não os reclassifica.

---

## Fotografia anterior preservada — histórica, não autoridade desta tarefa

# Tarefa ativa — navegação, Estatuto e clareza Forex

Implementação N1/A2 do plano completo aprovado pelo proprietário. Três CHGs NAVIGATION-AVAILABILITY, NORMATIVE-READER e FOREX-CLARITY de 20261001; brief BRIEF-JPW-SITE-CLARITY-20261001.

Base deffc5061fe2eff3d83b6f6e742fa105ac9c5b06; fingerprint bd0894b36d0fa8ff696e9bf5f7833fc654326466999127b70e95e8d4b0e8390e; snapshot externo /Users/joaopauloalves/.codex/.chatgpt-projects/g-p-6a4fc0aa51dc8191af013579f37179a3/outputs/jpw-navigation-normative-forex-20261001. Preservar 149 entradas anteriores. Sem commit/publicação, MT5 ou dados reais. SOURCE REVISION UNKNOWN herdado permanece; candidate local concluído; full final57PASS/0falhas, regressão host MT517PASS. Aceite humano e publicação permanecem separados.

Runtime estabilizado no build 83369b5cffa50c58. Três P2 Forex e a colisão do leitor com Notas em zoom200% foram reproduzidos e corrigidos. Pareceres/evidências, fingerprint final e rollback ficam no diretório externo citado. Aceite humano e publicação continuam separados; MT5 nativo herdado permanece NOT_RUN.


## Tarefa corrente 2026-10-01 — Execution Board adaptado

# Brief — Execution Board adaptado

## Identidade e compreensão

2026-10-01. Raiz /private/tmp/jpw-cockpit-ui-20260930; branch codex/jpw-cockpit-ui-20260930. Aprovação: pedido atual do proprietário para implementar o plano completo. CHGs N1/A2 EXECUTION-WORKBOOK e N3/A4 LOT-REFERENCES. Sem Git, publicação, MT5 ou dados reais.

1. JP Wealth organiza risco e fatos financeiros; esta tarefa torna a operação comparável transversalmente à planilha sem alterar a política.
2. Domínio produz resultados; UI mantém rascunhos RAM, navegação e representação. Comandos existentes são únicos escritores.
3. Base observada: sete colunas com campos empilhados e fases em accordions. Candidate: grade única com vinte campos e três ferramentas no contexto.
4. Consumidores: Board, risk adapter, Header/Dashboard, rotas motor e exec; alterar somente projeções de referência explicitamente autorizadas.
5. Preservar identidade, unidades, schemas, LEGACY, drafts, preferences, pending policy e pacote MT5. Não converter células/cache do Excel em oráculo financeiro.
6. Evidência: tarefas sintéticas, equivalência dos cálculos existentes, bases SI/equity diferentes, zero writes na edição/navegação, guards e audits independentes.

## Fontes e limites

AGENTS e FOREX-V11-ENGINE lidos. Estatuto e Anexo conferidos na pesquisa da proposta; P12b fornece fatores 0,50/0,25; Art3.19 (PDF pp.46–47) fundamenta a referência inicial sobre SI; Art4.5 §8 (PDF p.36) fundamenta o teto corrente sobre min(SI,E). Aprovação atual confirma mostrar ambas sem usar a primeira como limite corrente. Planilha 8.1 é referência visual e contém convenções legadas (fases, ATR1200 e rótulos pips); não importar suas regras. Contratos FOREX-EXECUTION-BOARD e FOREX-EXPERIENCE regem contexto/comandos. Harness localizado em 2 - TRABALHO/6C - SOFTWARE (caminho antigo em AGENTS é histórico), hash nos CHGs. Skills preflight/change-control/design IMPLEMENTAR aplicadas.

## Implementação e segurança

Uma fonte de cálculo; nenhuma fórmula financeira no renderer. grade com vinte colunas; campos completos, scroll local, ID/instrument congelados; abaixo de 768px de área útil lista com o mesmo DOM. Ferramentas conservam DOM, scroll e drafts. Preview de geometria/ATR/Raiz N é distinto do risco salvo. Erros em detalhe abrem/focam campo. Referência SI e teto corrente são métricas teóricas com base/fonte explícitas; normal/restrictive anteriores continuam como teto corrente.

Dados sintéticos, servidor/contextos descartáveis. Testes completos e focais autorizados, sem editar gates/fixtures para aprovar. Auditoria independente após freeze; mudanças posteriores invalidam evidência afetada. Entrega candidate e rollback, aceite manual separado.

Baseline SHA: deffc5061fe2eff3d83b6f6e742fa105ac9c5b06
Fingerprint: e6d2d9cdfc61e2e908474b090b60222b73e3470f746c530eb27b94aba2326c32
Snapshot: /Users/joaopauloalves/.codex/.chatgpt-projects/g-p-6a4fc0aa51dc8191af013579f37179a3/outputs/jpw-execution-board-20261001/baseline.tar.gz

Contratos: CHG-JPW-EXECUTION-WORKBOOK-20261001.md e CHG-JPW-LOT-REFERENCES-20261001.md. Esta seção sucede a tarefa anterior sem reescrever sua evidência.

## Fechamento do candidate Execution Board

Runtime final `7125b6ef17f60623`, fontes funcionais congeladas; site local e portátil regenerados oficialmente. Standard final: **46 PASS / 0 falhas**. Full bruto dos bytes congelados: **56 PASS / 1 PRODUCT_FAIL** — timeout de ativação do Laboratório Galton em research-navigation. O mesmo focal passou no standard e na repetição isolada; o full não foi reclassificado. A rodada full anterior conserva 57 PASS, mas atravessou a última correção CSS e não constitui aceite dos bytes finais.

Focais financeiros: referências do Motor 34/34 PASS; projeção 116/116 PASS; Market 30/31, com 1 PRODUCT_FAIL também reproduzido no snapshot. Workbook source7/8 e portátil6/7, ambos com a mesma falha herdada DD14 (14.000000000000002 provoca fase5 em vez de4). Board 15/15 PASS; tabela e Clarity PASS. Auditoria independente do delta: AUDIT_PASS_WITH_DEBT, sem aprovação financeira global. Regressão MT5 host 17 PASS nos bytes finais; compilação/execução nativa herdadas NOT_RUN e pacote 1.16.1 íntegro.

**Aceite bloqueado** por DD14, divergência de captura inicial no focal Market e intermitência Galton no gate obrigatório. Policy, engine, state, Estatuto/Anexo, gates e fixtures canônicas permanecem iguais ao snapshot. As falhas não foram escondidas no renderer nem removidas dos testes. As 182 alterações preexistentes permanecem preservadas; SOURCE REVISION UNKNOWN herdado continua explícito.

Relatório, recibos, capturas comparativas, fingerprint e rollback: `/Users/joaopauloalves/.codex/.chatgpt-projects/g-p-6a4fc0aa51dc8191af013579f37179a3/outputs/jpw-execution-board-20261001/REPORT.md` e `CANDIDATE.json`. Não houve commit, integração, publicação, alteração do MT5 ou acesso a perfil financeiro real.
