# Tarefa ativa — entrega GitHub Stoikus — 2026-10-13

Data da fotografia: 2026-10-13

Source revision representada: `0f247215cc20829fdba40c3b33458ee976c17ea1`

Base Git acima mais delta na branch `codex/stoikus-renaming-20261012`, raiz `/private/tmp/jpw-stoikus-renaming-20261012`. O proprietário autorizou registrar commits, enviar a branch, abrir PR, conferir testes GitHub e integrar na main: “realize esse passo 1, 2 3”; “execute”. Operações em preparação nesta fotografia; provas finais externas em `/private/tmp/jpw-stoikus-github-20261013`.

Entrega: auditoria AUD-01..10, Stoikus 1.22.1 / MQL 1.221 / cálculo 1.9.0. Candidato GitHub web `6455102de8b5f1fa`. A correção de espaço excedente no guia e o destino portátil de evidências Linux alteram sete entradas do freeze de 402 arquivos; MQL build/fingerprint e cálculos conservados. O Site versão 3 conserva o build anterior `e570a26ad6fd096a`; seus recibos são históricos dessa publicação. Site GPT/Sites versão 3 publicado em https://jp-wealth-software.jojoaopauloalvescirq.chatgpt.site, commit interno Sites 4cdff1d563b36229561b008b4fb99fd655001f48; publicação e GitHub são destinos separados. Verificações anteriores próprias: full 57/57, host 44/44; serão conferidas novamente antes do commit.

Compilação/execução MT5, instalação e aceite operacional **NOT_RUN**; sem EX5 atual ou armamento. Trabalho simultâneo de Guia de Aprendizagem permanece no checkout principal CloudDocs e não integra esta entrega. As instruções AGENTS antigas foram revogadas; documentos e contratos históricos conservam seus bytes, sem nova autoridade.

[Registro contextual](CHG-STOIKUS-GITHUB-CONTEXT-20261013.md) · [Fotografia anterior](HISTORY-BEFORE-STOIKUS-GITHUB-docs__work__ACTIVE-TASK.md)

```yaml
{
  "status": "approved",
  "approved_by": "Proprietário nesta conversa; pedido explícito de commit, push, PR e merge",
  "approved_at": "2026-10-13T19:11:10.641872+00:00",
  "authorization_evidence": "realize esse passo 1, 2 3; execute",
  "schema": "jp-harness/chg/v1",
  "change_id": "CHG-STOIKUS-GITHUB-CONTEXT-20261013",
  "objective": "Registrar a entrega GitHub autorizada da auditoria e Stoikus 1.22.1 já publicada, mantendo limites nativos",
  "risk_level": "N3",
  "authority_required": "A4",
  "target": {
    "root": "/private/tmp/jpw-stoikus-renaming-20261012",
    "branch": "codex/stoikus-renaming-20261012",
    "baseline_sha": "0f247215cc20829fdba40c3b33458ee976c17ea1"
  },
  "scope": {
    "allowed_files": [
      "docs/work/CHG-STOIKUS-GITHUB-CONTEXT-20261013.md",
      "docs/work/ACTIVE-TASK.md",
      "docs/governance/CURRENT-STATE.md",
      "docs/governance/CONTEXT-MAP.md",
      "SESSION_HANDOFF.md",
      "docs/validation/stoikus-site-20261013/INTEGRATION.md"
    ],
    "forbidden_files": [
      "AGENTS.md",
      "CLAUDE.md",
      "docs/normative/",
      "docs/decisions/",
      "tools/quality_gate.py",
      ".github/"
    ],
    "allowed_actions": [
      "Documentar commits, push, PR, checks e merge realmente executados",
      "Preservar fotografias históricas e limites MT5",
      "Vincular provas do candidato exato"
    ],
    "forbidden_actions": [
      "Alterar normas, dados, esquemas ou relaxar gates",
      "Atribuir homologação MT5 inexistente",
      "Incluir Guia de Aprendizagem concorrente no delta"
    ],
    "regressions_forbidden": [
      "Apagar histórico",
      "Transferir aprovação de outro candidate",
      "Fingir execução nativa ou cegamento completo"
    ]
  },
  "derived_artifacts": {
    "allowed": [],
    "generation_commands": [],
    "manual_edit": "allowed"
  },
  "external_side_effects": {
    "network": "allowed",
    "allowed_targets": [
      "Repositório GitHub jojoaopauloalvescirqueira-sketch/App-Jp-Wealth",
      "Loopback de testes sintéticos"
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
      "Python",
      "Chromium descartável",
      "C++ host",
      "Node bundled",
      "Git commit/fetch/push",
      "GitHub PR/checks/merge"
    ]
  },
  "acceptance_criteria": [
    "Estado focal correto e mesmo SHA base",
    "Históricos byte-idênticos preservados",
    "Sem conclusão nativa ou publicação simulada"
  ],
  "approved_tests": [
    "agent_instruction_structure_test.py com controles negativos",
    "preflight_context_test.py",
    "quality_gate.py --tier full"
  ],
  "rollback": {
    "source": [
      "Reverter somente delta de integração com snapshots originais e versão Sites2"
    ],
    "application_state": [],
    "data": [],
    "environment": [
      "Encerrar apenas processos próprios de testes"
    ],
    "verification": [
      "Conferir hashes da baseline e Source revision"
    ]
  },
  "expires_on": [
    "Mudança dos bytes publicados ou projeto/audiência alvo"
  ]
}
```

```yaml
{
  "status": "approved",
  "approved_by": "Proprietário nesta conversa; pedido explícito de commit, push, PR e merge",
  "approved_at": "2026-10-13T19:11:10.641872+00:00",
  "authorization_evidence": "realize esse passo 1, 2 3; execute",
  "schema": "jp-harness/ctx/v1",
  "context_change_id": "CTX-STOIKUS-GITHUB-20261013",
  "root": "/private/tmp/jpw-stoikus-renaming-20261012",
  "mode": "CONCORRENTE",
  "approved_branch": "codex/stoikus-renaming-20261012",
  "create": [
    "docs/work/CHG-STOIKUS-GITHUB-CONTEXT-20261013.md"
  ],
  "modify": [
    "docs/work/ACTIVE-TASK.md",
    "docs/governance/CURRENT-STATE.md",
    "docs/governance/CONTEXT-MAP.md",
    "SESSION_HANDOFF.md",
    "docs/validation/stoikus-site-20261013/INTEGRATION.md"
  ],
  "merge": [],
  "preserve": [
    "Fotografias históricas e patches AUD byte-idênticos",
    "Gates/normas e limites nativos"
  ],
  "do_not_touch": [
    "AGENTS.md",
    "CLAUDE.md",
    "docs/normative/",
    "docs/decisions/",
    "tools/quality_gate.py",
    ".github/"
  ],
  "archive_requires_confirmation": [],
  "source_of_truth": {
    "human": "realize esse passo 1, 2 3; execute",
    "product": "downloads/jpw-alavancagem-atual/manifest.json",
    "site": "https://jp-wealth-software.jojoaopauloalvescirq.chatgpt.site",
    "evidence": "/private/tmp/jpw-stoikus-github-20261013"
  },
  "information_promotion": [
    {
      "from": "Recibos concretos e resultado nativo Sites succeeded",
      "to": "Estado factual da integração",
      "reason": "Não herdar PASS ou instalar/armar MT5"
    }
  ],
  "expiration_rules": [
    {
      "artifact": "Estado/publicação1.22.1",
      "event": "Alteração posterior dos bytes"
    }
  ],
  "privacy_actions": [
    "Somente fixtures sintéticas; não ler dados de conta para testes"
  ],
  "acceptance_criteria": [
    "Um estado focal corrente sem herança de PASS",
    "Histórico preservado em arquivos próprios",
    "Contrato estrutural não apresentado como prova de autorização humana"
  ],
  "expires_on": [
    "Escopo/raiz/branch divergirem"
  ]
}
```
