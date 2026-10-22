> **Fase posterior — integração C5/D1 autorizada em 21/10/2026:** o proprietário autorizou commit, push e merge e, separadamente, o [lote de distribuição D1](CHG-STOIKUS-C5-D1-DISTRIBUTION-20261021.md), aplicado pelos hashes aprovados e reproduzido pelos geradores oficiais. Os 119 inputs executáveis/recursos C5 e os 15 ZIPs históricos foram preservados; os downloads novos têm nomes próprios. A suíte `leverage_suite.py --scope all` desta fase registrou **62 PASS, zero falhas**, com inputs estáveis. A autorização Git não dispensa o FULL e os checks do PR: seus resultados e as operações efetivas devem ser conferidos nos recibos `stoikus-painel-personalizavel-20261021/git-integration-20261021/authorized-D1/` e no histórico Git; esta nota não os antecipa. O Planejamento da primária permanece fora do escopo. Compilação, execução/instalação MT5 e aceite humano nativo continuam **NOT_RUN**; nenhum EX5 foi gerado. Não houve alteração do instalador nem publicação no GPT Sites. **Todo o conteúdo abaixo é a fotografia anterior à fase D1 e deve ser lido como histórico, inclusive seus resultados vermelhos e limites Git então vigentes.**

> **Candidato local — 21/10/2026:** [painel personalizável do Stoikus](CHG-STOIKUS-PAINEL-PERSONALIZAVEL-20261021.md), branch `codex/stoikus-painel-personalizavel-20261021`, base `ea15afc9c6a9c30cc69c5b98a8b85c85211ffb34`. C5 preserva cálculo 1.9.0 e permite seleção/ordem das sete métricas, Aplicar/Cancelar e acessos Conta–NoCuda. Os lotes de validação, ajuste de composição e kit nativo foram aplicados após seus aceites específicos e revisão independente. Rodada pós-lote com arquivos congelados: MT5-all: 58 PASS, 3 PRODUCT_FAIL; FULL: 73 PASS, 4 PRODUCT_FAIL, 4 ENVIRONMENT_ERROR. Seis focais separados passaram após informar navegador/Node ao processo; não substituem nem reclassificam o FULL bruto, que registrou essas ocorrências de ambiente. As 55 verificações host passaram; falhas de distribuição permanecem brutas e bloqueiam aprovação integral. Build `406f16e7265f93dbd76f1c2b063090fa05520fdafc4322ca13ab5e0e0ae82161`. O proprietário decidiu encerrar sem ensaio MT5 e verificar manualmente: compilação, instalação C5, execução nativa e aceite permanecem **NOT_RUN**; nenhum EX5 novo foi gerado, e Windows x64 está sem ambiente. Inventário instalado é parcial, com duas entradas Conta e duas NoCuda observadas; identidade exata e propriedade dos objetos não comprovadas, sem remoção de resíduos. A prévia é um modelo parcial (transparência 0–90/passo 5 versus MQL 0–100/passo 10), não prova de paridade nativa. Site, instalador, Planejamento e pacotes públicos não foram alterados. Sem commit/push/merge/publicação nesta tarefa. Guia e recibos privados: `stoikus-painel-personalizavel-20261021/PARA-TESTAR-MANUALMENTE.md` e `post-native-batch-validation-C5/`. O conteúdo abaixo é a fotografia histórica da integração precedente.

# Integração das pendências JP Wealth — 18/10/2026

[Contrato e limites](CHG-JPW-CONSOLIDACAO-INTEGRAL-20261018.md). F01, site e instalador têm provas focais; o conjunto exige gate novo. A autorização provém das mensagens do proprietário. Publicação de site/EXE, runtime MT5 e aceite humano permanecem separados.

```yaml
{
  "schema": "jp-harness/chg/v1",
  "change_id": "CHG-JPW-CONSOLIDACAO-INTEGRAL-CONTEXT-20261018",
  "status": "approved",
  "objective": "Reconciliar contexto factual de site, F01 e instalador com preservação histórica e provas próprias",
  "risk_level": "N3",
  "authority_required": "A4",
  "target": {
    "root": "/private/tmp/jpw-stoikus-installer-20261014",
    "branch": "codex/stoikus-installer-20261014",
    "baseline_sha": "bf0b1e8a882c9cdf880129f68f7c111e06e6f0c4"
  },
  "scope": {
    "allowed_files": [
      "docs/work/ACTIVE-TASK.md",
      "docs/governance/CURRENT-STATE.md",
      "docs/governance/CONTEXT-MAP.md",
      "SESSION_HANDOFF.md",
      "docs/work/CHG-JPW-CONSOLIDACAO-INTEGRAL-20261018.md",
      "docs/work/HISTORY-CONSOLIDATION-INSTALLER-ACTIVE-TASK-20261018.md",
      "docs/work/HISTORY-CONSOLIDATION-INSTALLER-CURRENT-STATE-20261018.md",
      "docs/work/HISTORY-CONSOLIDATION-INSTALLER-SESSION_HANDOFF-20261018.md",
      "docs/work/HISTORY-CONSOLIDATION-SITE-ACTIVE-TASK-20261018.md",
      "docs/work/HISTORY-CONSOLIDATION-SITE-CURRENT-STATE-20261018.md",
      "docs/work/HISTORY-CONSOLIDATION-SITE-SESSION_HANDOFF-20261018.md",
      "docs/work/HISTORY-CONSOLIDATION-SECURITY-ACTIVE-TASK-20261018.md",
      "docs/work/HISTORY-CONSOLIDATION-SECURITY-CURRENT-STATE-20261018.md",
      "docs/work/HISTORY-CONSOLIDATION-SECURITY-SESSION_HANDOFF-20261018.md"
    ],
    "forbidden_files": [
      "AGENTS.md",
      "CLAUDE.md",
      "tools/quality_gate.py",
      "tools/agent_instruction_structure_test.py",
      "docs/normative/",
      "docs/decisions/"
    ],
    "allowed_actions": [
      "Reconciliar somente representações factuais da integração autorizada",
      "Conservar integralmente as fotografias de cada trilha"
    ],
    "forbidden_actions": [
      "Criar autoridade, mudar critérios ou apresentar estados pendentes como aprovados",
      "Publicar site, EXE ou dados privados"
    ],
    "regressions_forbidden": [
      "Apagar histórico ou alterar a edição documental curada",
      "Confundir gate host com execução Windows/MT5"
    ]
  },
  "derived_artifacts": {
    "allowed": [],
    "generation_commands": [],
    "manual_edit": "forbidden"
  },
  "external_side_effects": {
    "network": "forbidden",
    "allowed_targets": [],
    "temporary_artifacts": "allowed",
    "cleanup_required": false
  },
  "data": {
    "test_policy": "synthetic_only",
    "approved_real_data": [],
    "schema_change": "forbidden"
  },
  "toolchain": {
    "dependency_changes": [],
    "allowed_processes": [
      "Python padrão",
      "Git leitura"
    ]
  },
  "acceptance_criteria": [
    "Contexto atual identifica versão e limites, histórico preservado",
    "Estrutura CHG/CTX e referências válidas"
  ],
  "approved_tests": [
    "python3 tools/agent_instruction_structure_test.py",
    "python3 tools/quality_gate.py --tier full",
    "python3 tools/leverage_suite.py --scope host"
  ],
  "rollback": {
    "source": [
      "Restaurar documentos da fotografia preservada"
    ],
    "application_state": [
      "Nenhuma escrita em dados do aplicativo"
    ],
    "data": [
      "Preservar originais e backups"
    ],
    "environment": [
      "Nenhuma mudança global"
    ],
    "verification": [
      "Conferir hashes originais"
    ]
  },
  "expires_on": [
    "Ampliação de escopo ou mudança material sem revalidação"
  ],
  "approved_by": "Proprietário: pedido direto de resolver todas as pendências, commit, push, merge e limpeza; atualização do instalador e patch visual especificamente autorizados",
  "approved_at": "2026-10-18T17:32:50.482185+00:00",
  "authorization_evidence": "Atualizar e concluir também o instalador antes da limpeza final; registro do aceite, não timestamp original da fala",
  "approval_timestamp_note": "Horário de registro; não é timestamp recuperado da mensagem humana"
}
```

```yaml
{
  "schema": "jp-harness/ctx/v1",
  "context_change_id": "CTX-JPW-CONSOLIDACAO-INTEGRAL-20261018",
  "status": "approved",
  "root": "/private/tmp/jpw-stoikus-installer-20261014",
  "mode": "CONCORRENTE",
  "approved_branch": "codex/stoikus-installer-20261014",
  "create": [
    "docs/work/CHG-JPW-CONSOLIDACAO-INTEGRAL-20261018.md",
    "docs/work/HISTORY-CONSOLIDATION-INSTALLER-ACTIVE-TASK-20261018.md",
    "docs/work/HISTORY-CONSOLIDATION-INSTALLER-CURRENT-STATE-20261018.md",
    "docs/work/HISTORY-CONSOLIDATION-INSTALLER-SESSION_HANDOFF-20261018.md",
    "docs/work/HISTORY-CONSOLIDATION-SITE-ACTIVE-TASK-20261018.md",
    "docs/work/HISTORY-CONSOLIDATION-SITE-CURRENT-STATE-20261018.md",
    "docs/work/HISTORY-CONSOLIDATION-SITE-SESSION_HANDOFF-20261018.md",
    "docs/work/HISTORY-CONSOLIDATION-SECURITY-ACTIVE-TASK-20261018.md",
    "docs/work/HISTORY-CONSOLIDATION-SECURITY-CURRENT-STATE-20261018.md",
    "docs/work/HISTORY-CONSOLIDATION-SECURITY-SESSION_HANDOFF-20261018.md"
  ],
  "modify": [
    "docs/work/ACTIVE-TASK.md",
    "docs/governance/CURRENT-STATE.md",
    "docs/governance/CONTEXT-MAP.md",
    "SESSION_HANDOFF.md"
  ],
  "merge": [],
  "preserve": [
    "Todos os originais e recibos; novos snapshots privados das três trilhas",
    "Fontes MQL e pacotes históricos; edição curada C2 e oráculos financeiros"
  ],
  "do_not_touch": [
    "AGENTS.md",
    "CLAUDE.md",
    "tools/quality_gate.py",
    "tools/agent_instruction_structure_test.py",
    "docs/normative/",
    "docs/decisions/"
  ],
  "archive_requires_confirmation": [],
  "source_of_truth": {
    "human": "Pedidos diretos desta conversa; documentos não concedem autoridade",
    "baseline": "bf0b1e8a882c9cdf880129f68f7c111e06e6f0c4",
    "product": "docs/work/CHG-JPW-CONSOLIDACAO-INTEGRAL-20261018.md"
  },
  "information_promotion": [
    {
      "from": "Deltas revisados e provas individuais",
      "to": "Contexto da combinação",
      "reason": "Distinguir provas focais e gate novo do conjunto"
    }
  ],
  "expiration_rules": [
    {
      "artifact": "Provas do conjunto",
      "event": "Mudança material de qualquer input correspondente"
    }
  ],
  "privacy_actions": [
    "Somente fixtures sintéticas; nenhum dado de conta"
  ],
  "acceptance_criteria": [
    "Referências válidas e limites explícitos"
  ],
  "expires_on": [
    "Ampliação de escopo ou mudança material sem revalidação"
  ],
  "approved_by": "Proprietário: pedido direto de resolver todas as pendências, commit, push, merge e limpeza; atualização do instalador e patch visual especificamente autorizados",
  "approved_at": "2026-10-18T17:32:50.482185+00:00",
  "approval_timestamp_note": "Horário de registro; não é timestamp recuperado da mensagem humana"
}
```
