# CTX — camada focal Stoikus

A aprovacao do plano abrange nomes/paths/versao e a reconciliacao focal. README e CHANGELOG sao representacoes informativas complementares cobertas no CHG de produto; este par verifica os documentos aceitos pelo validador de instrucoes/contexto existente, sem altera-lo.

```yaml
{
  "schema": "jp-harness/chg/v1",
  "change_id": "CHG-STOIKUS-CONTEXT-20261012",
  "status": "approved",
  "objective": "Reconciliar exclusivamente a camada focal Stoikus de nomes, paths, versao e evidencias novas",
  "risk_level": "N3",
  "authority_required": "A4",
  "target": {
    "root": "/private/tmp/jpw-stoikus-renaming-20261012",
    "branch": "codex/stoikus-renaming-20261012",
    "baseline_sha": "0f247215cc20829fdba40c3b33458ee976c17ea1"
  },
  "scope": {
    "allowed_files": [
      "SESSION_HANDOFF.md",
      "docs/governance/CONTEXT-MAP.md",
      "docs/governance/CURRENT-STATE.md",
      "docs/validation/stoikus-1.22.0/INTEGRATION.md",
      "docs/work/ACTIVE-TASK.md",
      "docs/work/BRIEF-STOIKUS-RENAMING-20261012.md",
      "docs/work/CHG-STOIKUS-CONTROL-20261012.md",
      "docs/work/CHG-STOIKUS-RENAMING-20261012.md",
      "docs/work/CTX-STOIKUS-RENAMING-20261012.md",
      "docs/work/HISTORY-STOIKUS-CURRENT-STATE-20261012.md"
    ],
    "forbidden_files": [
      "docs/normative/**",
      "docs/decisions/**",
      "docs/validation/genetrix-*/**",
      "mt5/jpw-alavancagem-atual/harness/**",
      "mt5/jpw-alavancagem-atual/GENETRIX_*.md",
      ".github/**",
      "tools/quality_gate.py",
      "AGENTS.md",
      "CLAUDE.md"
    ],
    "allowed_actions": [
      "Adicionar camada focal informativa conforme plano aprovado",
      "Preservar fotografias historicas sem ampliar autoridade",
      "Registrar apenas resultados observados no candidate"
    ],
    "forbidden_actions": [
      "commit",
      "push",
      "merge",
      "deploy",
      "instalar noMT5",
      "armarSupervisor",
      "migrar/apagar dados",
      "alterar formulas/unidades/limites"
    ],
    "regressions_forbidden": [
      "Perder historico/persistencia/locks/preferencias",
      "Tratar fonte como compilado/aceite",
      "Afrouxar criterios ou reinterpretar comprovacao antiga"
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
      "localhost sintetico"
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
      "C++host",
      "Chromiumdescartavel",
      "Gitlocal somenteacoesautorizadas"
    ]
  },
  "acceptance_criteria": [
    "Marca publicaStoikus;NoCuda conserva nome",
    "Mapaexato34arquivos atualizado sem colisao",
    "Namespaces, schemas, guardsfinanceiros, formulas e locks preservados",
    "Antigosaliasesreconhecidosna admissao dosindicadores",
    "ZIPshistoricosbyte-identicos",
    "Pacotenovo/version/build/hashes coesos semEX5",
    "Hostall/full e revisaoindependente dofreeze final"
  ],
  "approved_tests": [
    "python3 tools/leverage_suite.py --scope all",
    "python3 tools/quality_gate.py --tier full",
    "python3 tools/jpw_stoikus_oracle_test.py",
    "Focais marca/guards/package/page;controlesnegativosisolados",
    "Conferencia hashes/links/diff/recursos/renames/reprodutibilidade"
  ],
  "rollback": {
    "source": [
      "Repor apenas os prefixos e documentos focais desta tarefa, preservando o historico"
    ],
    "application_state": [
      "Nenhum dado real ouMT5 foi alterado"
    ],
    "environment": [
      "Encerrar processosdescartaveis proprios"
    ],
    "verification": [
      "Comparar fontes eZIPshistoricos comBASELINE.json"
    ],
    "data": []
  },
  "approved_by": "Proprietario nesta conversa",
  "approved_at": "2026-10-12T23:03:30.659505+00:00",
  "authorization_evidence": "PLEASE IMPLEMENT THIS PLAN: Renomeacao deGENETRIXpara Stoikus, incluindo gerador/verificadoresemtrilhapropria; resposta Autorizarbranch eworktree isolada",
  "expires_on": [
    "root/branch/HEAD ouescopodivergir",
    "Novaalteracaomaterialnaoautorizada"
  ]
}
```

```yaml
{
  "schema": "jp-harness/ctx/v1",
  "context_change_id": "CTX-STOIKUS-RENAMING-20261012",
  "status": "approved",
  "root": "/private/tmp/jpw-stoikus-renaming-20261012",
  "mode": "CONCORRENTE",
  "approved_branch": "codex/stoikus-renaming-20261012",
  "create": [
    "docs/work/BRIEF-STOIKUS-RENAMING-20261012.md",
    "docs/validation/stoikus-1.22.0/INTEGRATION.md",
    "docs/work/CHG-STOIKUS-CONTROL-20261012.md",
    "docs/work/CTX-STOIKUS-RENAMING-20261012.md",
    "docs/work/HISTORY-STOIKUS-CURRENT-STATE-20261012.md"
  ],
  "modify": [
    "SESSION_HANDOFF.md",
    "docs/governance/CURRENT-STATE.md",
    "docs/governance/CONTEXT-MAP.md",
    "docs/work/ACTIVE-TASK.md"
  ],
  "merge": [],
  "preserve": [
    "Pacotes/harness/manuais/recibos GENETRIX originais",
    "Historico preexistente da integracao"
  ],
  "do_not_touch": [
    "Norma/decisoes/instrucoesglobais",
    "Memoriaglobal",
    "Grafo/indicesprivados",
    "Dadosreais"
  ],
  "archive_requires_confirmation": [],
  "source_of_truth": {
    "human": "Plano Stoikus aprovado nesta conversa",
    "engineering": "Master2.0 SHA256b5680c22e44cf3f4a5cd3aa5deeb96f8b65c7908f14543e8c5d7f0c2f4e17b95 +AGENTS vigente",
    "product": "Fontes/proveniencia Stoikus candidate nesta branch"
  },
  "information_promotion": [
    {
      "from": "Fontes e recibos novos Stoikus 1.22.0",
      "to": "Camada focal Stoikus do contexto operacional",
      "reason": "Representar somente fatos comprovados; nao transferir aceite historico"
    }
  ],
  "expiration_rules": [
    {
      "artifact": "docs/governance/CURRENT-STATE.md",
      "event": "Mudanca material posterior do candidato ou fonte"
    }
  ],
  "privacy_actions": [
    "Dadossinteticos somente"
  ],
  "acceptance_criteria": [
    "Resumos atuais apontam Stoikus e nomesnovos sem reescrever historicopreservado",
    "Nenhuma autoridade/regra/gate relaxado"
  ],
  "approved_by": "Proprietario nesta conversa",
  "expires_on": [
    "Escopo oubranchdivergir"
  ],
  "approved_at": "2026-10-12T23:03:30.659505+00:00",
  "supporting_informational_documents": [
    "README.md",
    "CHANGELOG.md"
  ]
}
```

Correção de enumeração no fecho: o registro CHG de produto acima, criado antes da implementação dentro do plano humano aprovado, estava omitido da allowlist deste CTX. O diagnóstico original permanece em `scope-R2-first-attempt.json`. A inclusão registra trabalho já autorizado; não concede ação ou autoridade nova.
