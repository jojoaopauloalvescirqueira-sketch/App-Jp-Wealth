# JP Engenharia — instalação local delimitada — 16/10/2026

O pedido humano autoriza implementar esta integração reversível e decidir detalhes rotineiros, preservando o candidato completo. N3/A4 limitado à instalação local, sem autorização financeira, Git, publicação ou memória global. Os contratos abaixo registram essa autorização recebida; não a produzem.

```yaml
{
  "schema": "jp-harness/chg/v1",
  "change_id": "CHG-JPW-ENGINEERING-INSTALL-20261016",
  "status": "approved",
  "objective": "Instalar localmente a skill JP Engenharia1.3.0, conectada às instruções existentes e memória factual de regressões; sem enfraquecer proteções.",
  "risk_level": "N3",
  "authority_required": "A4",
  "target": {
    "root": "/private/tmp/jpw-time-twins-20261015",
    "branch": "codex/bolsas-globais-aisol-20261015",
    "baseline_sha": "2b22175a4f3f47b1f289deca65366c4dc0445dca"
  },
  "scope": {
    "allowed_files": [
      "skills/jp-ai-engineering/SKILL.md",
      "skills/jp-ai-engineering/agents/openai.yaml",
      "skills/jp-ai-engineering/assets/AGENTS.template.md",
      "skills/jp-ai-engineering/assets/personas/critico-integracao.toml",
      "skills/jp-ai-engineering/assets/personas/engenheiro-integracao.toml",
      "skills/jp-ai-engineering/assets/personas/operador-adversidades.toml",
      "skills/jp-ai-engineering/assets/personas/operador-informado.toml",
      "skills/jp-ai-engineering/assets/personas/usuario-iniciante.toml",
      "skills/jp-ai-engineering/assets/protections.example.json",
      "skills/jp-ai-engineering/assets/report.example.json",
      "skills/jp-ai-engineering/references/contratos.md",
      "skills/jp-ai-engineering/references/diagnostico.md",
      "skills/jp-ai-engineering/references/fronteiras.md",
      "skills/jp-ai-engineering/references/integracao-personas.md",
      "skills/jp-ai-engineering/references/jp-wealth.md",
      "skills/jp-ai-engineering/references/orquestracao.md",
      "skills/jp-ai-engineering/references/provenance.json",
      "skills/jp-ai-engineering/references/regras-regressoes.md",
      "skills/jp-ai-engineering/references/validacao.md",
      "skills/jp-ai-engineering/scripts/verify_protections.py",
      "skills/jp-ai-engineering.lock.json",
      ".agents/skills/jp-ai-engineering",
      ".claude/skills/jp-ai-engineering",
      "tools/regression-memory.json",
      "tools/jp_engineering_integration_test.py",
      "docs/work/CHG-JPW-ENGINEERING-INSTALL-20261016.md",
      "AGENTS.md",
      "docs/governance/SKILL-ROUTING.md",
      "docs/governance/CONTEXT-MAP.md",
      "docs/governance/CURRENT-STATE.md",
      "docs/work/ACTIVE-TASK.md",
      "SESSION_HANDOFF.md"
    ],
    "forbidden_files": [
      "CLAUDE.md",
      "tools/quality_gate.py",
      "tools/agent_instruction_structure_test.py",
      ".github/",
      "src/",
      "index.html",
      "build-id.js",
      "sw.js",
      "README.md",
      "CHANGELOG.md",
      "dist/",
      "mt5/",
      "downloads/",
      "docs/normative/",
      "other_skills",
      "global_settings",
      "global_memory"
    ],
    "allowed_actions": [
      "copy_frozen_skill_package",
      "create_two_relative_discovery_links",
      "append_bounded_project_routing",
      "create_partial_factual_regression_index",
      "add_focal_structural_checker_with_negative_controls",
      "update_factual_task_pointers",
      "run_existing_full_unchanged",
      "independent_readonly_review"
    ],
    "forbidden_actions": [
      "commit",
      "push",
      "merge",
      "deploy",
      "new_branch",
      "change_branch",
      "new_worktree",
      "modify_gates",
      "install_dependencies",
      "memory_runtime",
      "read_real_browser_state"
    ],
    "regressions_forbidden": [
      "preserve1105preexistingfiles_except6approvedinstruction_context_appendices",
      "nofinancialorapplicationchanges",
      "noauthorityweakening",
      "noinventedbugclosure"
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
      "loopback_synthetic_tests",
      "official_documentation_only"
    ],
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
      "python3",
      "node",
      "existingPlaywrightChromium",
      "readonlyGit"
    ]
  },
  "acceptance_criteria": [
    "20sourcefilesbyteidentical",
    "aliasesresolveinsideproject",
    "newroutingpreservesallpriorinstructions",
    "memoryrecordsverifiedstatesandpartialgatecoverage",
    "focalcheckerrejectsrepresentativeinvalidinstallation",
    "fullrawresultpreserved",
    "independentreviewofexactcandidate",
    "clientautoloadseparatefromexplicitread"
  ],
  "approved_tests": [
    "tools/jp_engineering_integration_test.py",
    "officialquick_validate_ifbundleddependenciesavailable",
    "tools/agent_instruction_structure_test.py(defaultlegacycoreonly)",
    "tools/quality_gate.py --tier full",
    "git diff --check"
  ],
  "rollback": {
    "source": [
      "/private/tmp/jpw-time-twins-20261015/.superpowers/sdd/jpw-engineering-install-20261016/before.tar.gz",
      "restoreonly6modifiedfilesandremoveonly26newinstallpathsafterreview"
    ],
    "application_state": [
      "unchanged"
    ],
    "data": [
      "noaccessormigration"
    ],
    "environment": [
      "noglobalsettingschanged"
    ],
    "verification": [
      "comparebefore-mapandpreservedlinks"
    ]
  },
  "approved_by": "Proprietário nesta conversa: faz isso sozinho, referente à instalação local do JP Engenharia e registro de bugs/memória do projeto. Autoridade delimitada a essa integração reversível; não é aceite do candidato ou autorização Git.",
  "approved_at": "2026-10-16T17:51:23.663100+00:00",
  "expires_on": [
    "rootorbranchchanges",
    "unknownconcurrentchange",
    "product/gates/globalmemoryscopeexpansion"
  ],
  "approval_time_note": "Timestamp do registro local da autorização conversacional recebida; horário nativo da mensagem humana não fornecido."
}
```

```yaml
{
  "schema": "jp-harness/ctx/v1",
  "context_change_id": "CTX-JPW-ENGINEERING-INSTALL-20261016",
  "status": "approved",
  "root": "/private/tmp/jpw-time-twins-20261015",
  "mode": "SEQUENCIAL",
  "approved_branch": "codex/bolsas-globais-aisol-20261015",
  "create": [
    "skills/jp-ai-engineering/SKILL.md",
    "skills/jp-ai-engineering/agents/openai.yaml",
    "skills/jp-ai-engineering/assets/AGENTS.template.md",
    "skills/jp-ai-engineering/assets/personas/critico-integracao.toml",
    "skills/jp-ai-engineering/assets/personas/engenheiro-integracao.toml",
    "skills/jp-ai-engineering/assets/personas/operador-adversidades.toml",
    "skills/jp-ai-engineering/assets/personas/operador-informado.toml",
    "skills/jp-ai-engineering/assets/personas/usuario-iniciante.toml",
    "skills/jp-ai-engineering/assets/protections.example.json",
    "skills/jp-ai-engineering/assets/report.example.json",
    "skills/jp-ai-engineering/references/contratos.md",
    "skills/jp-ai-engineering/references/diagnostico.md",
    "skills/jp-ai-engineering/references/fronteiras.md",
    "skills/jp-ai-engineering/references/integracao-personas.md",
    "skills/jp-ai-engineering/references/jp-wealth.md",
    "skills/jp-ai-engineering/references/orquestracao.md",
    "skills/jp-ai-engineering/references/provenance.json",
    "skills/jp-ai-engineering/references/regras-regressoes.md",
    "skills/jp-ai-engineering/references/validacao.md",
    "skills/jp-ai-engineering/scripts/verify_protections.py",
    "skills/jp-ai-engineering.lock.json",
    ".agents/skills/jp-ai-engineering",
    ".claude/skills/jp-ai-engineering",
    "tools/regression-memory.json",
    "tools/jp_engineering_integration_test.py",
    "docs/work/CHG-JPW-ENGINEERING-INSTALL-20261016.md"
  ],
  "modify": [
    "AGENTS.md",
    "docs/governance/SKILL-ROUTING.md",
    "docs/governance/CONTEXT-MAP.md",
    "docs/governance/CURRENT-STATE.md",
    "docs/work/ACTIVE-TASK.md",
    "SESSION_HANDOFF.md"
  ],
  "merge": [],
  "preserve": [
    "allpriorinstructionprose",
    "threecompletedminigames",
    "C8redesignproductanditsunapprovedglobalgate",
    "historicalcorrectrecords"
  ],
  "do_not_touch": [
    "CLAUDE.md",
    "tools/quality_gate.py",
    "tools/agent_instruction_structure_test.py",
    ".github/",
    "src/",
    "index.html",
    "build-id.js",
    "sw.js",
    "README.md",
    "CHANGELOG.md",
    "dist/",
    "mt5/",
    "downloads/",
    "docs/normative/",
    "other_skills",
    "global_settings",
    "global_memory"
  ],
  "archive_requires_confirmation": [],
  "source_of_truth": {
    "authority": "currenthumanautonomouslocalinstallationrequest",
    "plugin_version": "jp-ai-engineering1.3.0",
    "master_sha256": "b5680c22e44cf3f4a5cd3aa5deeb96f8b65c7908f14543e8c5d7f0c2f4e17b95",
    "master_sections": "12–14,24,28–30,36–40,52–57",
    "source_hashes": "skills/jp-ai-engineering.lock.json"
  },
  "information_promotion": [
    {
      "from": "pacote instalado do plugin JP Engenharia1.3.0",
      "to": "skills/jp-ai-engineering com lock por SHA256",
      "reason": "instalação local solicitada pelo proprietário; fonte congelada, sem promover histórico a autoridade"
    }
  ],
  "expiration_rules": [
    {
      "artifact": "tools/regression-memory.json",
      "event": "newsource/testorreceiptinvalidateslast_verified;neverauto-close"
    }
  ],
  "privacy_actions": [
    "syntheticonly",
    "projectmemoryfactualandnoaccountdata",
    "noglobalmemorywrite"
  ],
  "acceptance_criteria": [
    "20sourcefilesbyteidentical",
    "aliasesresolveinsideproject",
    "newroutingpreservesallpriorinstructions",
    "memoryrecordsverifiedstatesandpartialgatecoverage",
    "focalcheckerrejectsrepresentativeinvalidinstallation",
    "fullrawresultpreserved",
    "independentreviewofexactcandidate",
    "clientautoloadseparatefromexplicitread"
  ],
  "approved_by": "Proprietário nesta conversa: faz isso sozinho, referente à instalação local do JP Engenharia e registro de bugs/memória do projeto. Autoridade delimitada a essa integração reversível; não é aceite do candidato ou autorização Git.",
  "approved_at": "2026-10-16T17:51:23.663100+00:00",
  "expires_on": [
    "rootorbranchchanges",
    "unknownconcurrentchange",
    "product/gates/globalmemoryscopeexpansion"
  ],
  "approval_time_note": "Timestamp do registro local da autorização conversacional recebida; horário nativo da mensagem humana não fornecido."
}
```

## Diagnóstico e desenho

O projeto já possui núcleo AGENTS, skills roteadas, gates e contexto em camadas. Falta a fonte local do JP Engenharia. Importar20arquivos congelados, com lock por hash e dois links locais; instruções raiz remetem à fonte única e a um índice factual parcial junto aos testes. Manter allow_implicit_invocation:false do pacote; roteamento explícito em AGENTS não equivale a autodisparo nativo. Nenhum serviço, banco, embedding, segundo runner ou nova dependência.

O índice inicial registrou três correções de UI e três pendências existentes, com teste/oráculo/vínculo real ao gate. O gate desta instalação acrescentou uma sétima entrada factual de incidente em Gêmeos do Tempo, sem correção aplicada. Não promete cobertura integral do legado. O full atual usa lista fixa e não inclui todos os testes versionados. Não modificar seu juiz nem a safe_target do validador legado para aprovar a instalação: esse validador continua limitado ao seu núcleo. O checker novo comprova integridade/referências, não comportamento do produto ou carregamento do cliente.

## Impacto e localização

AGENTIC IMPACT CHECK: AGENTIC IMPACT DETECTED. BASIS: nova skill local e leitura obrigatória roteada afetam agentes, routing, descoberta e contexto; o pacote permanece imutável, consumidores apontam à mesma fonte e o índice factual não muda norma. AGENTS/routing/mapa/contexto requerem ação local; CLAUDE herda AGENTS e não requer edição; outras skills/gates/CI/produto não requerem alteração. Sem índice vetorial existente a operar: INDEX NOT REQUIRED. Estrutura física segue a convenção skills + links; não há reorganização do repositório.

## Registro operacional inicial — fotografia da preparação

Em implementação naquele registro inicial. Baseline1105arquivos identificado por mapa e backup no workspaceSDD. Critérios, falhas brutas, revisão e mapa final serão registrados no relatório local do mesmo workspace. O Build ID C8 deve permanecer idêntico. Aceite humano, descoberta automática em nova sessão e integração Git são estados distintos e posteriores.
