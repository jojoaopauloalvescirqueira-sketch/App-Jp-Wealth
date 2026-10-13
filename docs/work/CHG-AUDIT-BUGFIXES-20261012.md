# CHG — correções AUD-01..AUD-10 — 12/10/2026

Fonte: auditoria local do proprietário, REPORT.md, alvo0f247215cc20829fdba40c3b33458ee976c17ea1. Pedidos humanos atuais: “corrija os bugs encontrados na auditoria” e “Autorizar essa branch e as correções delimitadas”. Estas declarações autorizam implementação/tests na branch citada; não há autorização de commit/push/merge/deploy nem alteração de norma/juiz.

## Compreensão e limites

1. JP Wealth é aplicação local/PWA para organização financeira, análise, planejamento e risco (PROJECT-CONTEXT.md@BASE_SHA, seção Produto). Esta tarefa elimina falhas demonstradas de restauração, leitura e interação sem ampliar suas capacidades financeiras.
2. Persistência/import preservam documento confirmado e workspace separado; PF/Forex projetam fatos/unidades; Pivots/Notas mantêm edição explícita; SW/build entregam uma versão coerente. Consumidores compartilhados: boot/backup/finalização, Dashboard/PF/Planejamento/MEI/onboarding, Research/recuperação e Configurações/PWA/portátil.
3. Antes: profundidade do workspace recusa histórico válido; checklist inválido é adotado; inválidos/unidades/PENDING são projetados incorretamente; primeira observação ignora abertura; reabertura/pasta/foco/documentos divergem de seus contratos. Depois: recusa anterior a escrita para estruturas inválidas, round-trip suportado, valores canônicos com unidade/indisponibilidade, cronologia UTC já vigente, draft/view e ações de UI coerentes, documentos preservados online/offline.
4. Dados e regras: não truncar previous, inventar montante/taxa/conversão, reatribuir conta/período nem limpar dados. Comparação temporal usa dataUTC de observedAt, convenção já presente em recordAccountFacts e conciliação histórica. Campos desconhecidos continuam preservados. Checklist malformado já salvo deve entrar recovery com raw intocado; não corrigi-lo com DEFAULTS.
5. Política/engine/norma/params/defaults, schemas, CI/gates e autoridade intactos. Câmbio/financeiro não têm fórmula nova; FCR/FEO permanecem abertos. Nenhuma negociação, dado real, publicação ou migração.
6. Provas: FileReader/export/recarga reais comfixtures; controle26/27/35; checksum/chaves perigosas/tamanho/workspace; PF valores inválidos/zero/null; reservas MestreUSD/EUR/BRL/SATELITE/PROPRIA; MEIreferênciaausente/zero; limitesUTC; UIcancelar/aceitar/reativar/foco; PWAdocumentonline/offline/upgrade eportátil; focais e full final congelados + auditoria independente.

N2: AUD01/02/06/07 por backup/importação/recuperação/ato factual. N1: correção de projeção/apresentação/disponibilidade de dados sem alterar regra, AUD03/04/05/08/09/10. Após rejeição da primeira tentativa documental, o proprietário respondeu “Autorizar esses registros delimitados”. Registros factuais autorizados; sem alterar autoridade/gates/controle. Se a implementação precisar mudar fórmula, política ou contrato normativo, interromper apenas a ação dependente e solicitar decisão específica.

Fontes: AGENTS, README, CONTEXT-MAP, PROJECT-CONTEXT, CURRENT-STATE/ACTIVE-TASK históricos, AI-WORKFLOW/SKILL-ROUTING/CHANGE-PROCESS, STATE-SCHEMA, DB-STORAGE-GOVERNANCE, DATA-RECOVERY, PERSONAL-FINANCE, FOREX-V11-ENGINE, FX-PLANNING, PIVOT-STUDIES, PWA-UPDATE-LIFECYCLE e originais. Todos delimitados àBASE_SHA e caminhos/hashes registrados em fontes.json. Harness real localizado no acervo renomeado3 - Prompts&Skills/9 - SOFTWARE/A0 - HARNESS - JP Wealth MASTER SPECIFICATION.md, SHA256b5680c22e44cf3f4a5cd3aa5deeb96f8b65c7908f14543e8c5d7f0c2f4e17b95; fonte já lida nesta conversa e hash revalidado, sem reconstrução por memória. Histórico de contextos anteriores permanece recuperável em BASE_SHA.

Planos auditados por área: segurança AUD01/02; domínio AUD03..06; UI AUD07..09; principal AUD10. Um escritor por arquivo; principal coordena contratos, outputs, full e freeze. Revisor final não corrige o próprio delta. Evidência gerada fora do produto em /private/tmp/jpw-audit-bugfixes-20261012 e relatório final delimitado em docs/audit.

O campo approved_at registra a hora de documentação do aceite já recebido; a interface não expôs o timestamp da resposta humana.

## Contrato de produto

```yaml
{
  "schema": "jp-harness/chg/v1",
  "change_id": "CHG-AUDIT-BUGFIXES-20261012",
  "status": "approved",
  "approved_by": "Proprietario — resposta explicita nesta conversa",
  "approved_at": "2026-10-12T23:01:01.811277+00:00",
  "authorization_evidence": "corrija os bugs encontrados na auditoria; Autorizar essa branch e as correções delimitadas; Autorizar esses registros delimitados",
  "objective": "Corrigir somente AUD-01..AUD-10 da auditoria 12/10, preservando dados, historia e regras existentes",
  "risk_level": "N2",
  "authority_required": "A3",
  "target": {
    "root": "/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/99B - SOFTWARES & EAS/JP Wealth OS",
    "branch": "codex/audit-bugfixes-20261012",
    "baseline_sha": "0f247215cc20829fdba40c3b33458ee976c17ea1"
  },
  "scope": {
    "allowed_files": [
      "src/js/00-core/04-persistence.js",
      "src/js/30-accounting/01-daily-ledger.js",
      "src/js/10-domain/12-personal-finance.js",
      "src/js/10-domain/00-forex-state.js",
      "src/js/10-domain/02-risk-calculations.js",
      "src/js/30-accounting/05-fx-planning/03-fx-state.js",
      "src/js/30-accounting/05-fx-planning/05-fx-ui.js",
      "src/js/30-accounting/03-mei-jp.js",
      "src/js/40-app/04-onboarding.js",
      "src/js/20-ui/15-pivot-studies.js",
      "src/js/20-ui/33-module-work.js",
      "src/js/40-app/14-mvp-notes.js",
      "sw.js",
      "tools/rebuild_monolith.py",
      "tools/fx_consolidated_pdf_test.py",
      "tools/backup_import_audit_test.py",
      "tools/financial_projection_audit_test.py",
      "tools/audit_ui_recovery_test.py",
      "tools/pwa_document_navigation_test.py",
      "docs/architecture/FX-PLANNING.md",
      "docs/architecture/PERSONAL-FINANCE.md",
      "CHANGELOG.md",
      "docs/architecture/PWA-UPDATE-LIFECYCLE.md",
      "docs/audit/AUDIT-BUGFIXES-20261012.md",
      "docs/work/CHG-AUDIT-BUGFIXES-20261012.md"
    ],
    "forbidden_files": [
      "AGENTS.md",
      "CLAUDE.md",
      "docs/normative/",
      "docs/decisions/",
      "src/js/00-core/00-forex-policy.js",
      "src/js/10-domain/00-forex-engine.js",
      "src/js/10-domain/07-reserve-requirements.js",
      "tools/quality_gate.py",
      "tools/agent_preflight.py",
      "tools/agent_instruction_structure_test.py",
      ".github/",
      "mt5/"
    ],
    "allowed_actions": [
      "Criar e usar a branch nomeada pelo proprietario",
      "Validar checklist antes da adocao/import e diagnosticar base invalida preservando raw",
      "Compatibilizar export/import profundidade sem truncar historico",
      "Reutilizar read-model/validadores existentes e preservar unidade/indisponibilidade",
      "Reconstruir somente rascunhos/views/confirmacoes/foco dos fluxos indicados",
      "Entregar README/CHANGELOG como documentos coerentes online/offline, preservando lifecycle SW",
      "Acrescentar regressoes funcionais sem alterar gates",
      "Atualizar contexto e registro factual desta tarefa delimitada",
      "Executar gerador oficial apenas para outputs derivados pertinentes",
      "Documentar fatos da correção no CHG/CHANGELOG/PWA/relatório de auditoria aprovados"
    ],
    "forbidden_actions": [
      "Commit/push/merge/publicacao ou outra operacaoGit nao solicitada",
      "Alterar percentual/formula/politica/Estatuto ou resolver conflitos FCR/FEO",
      "Alterar dados reais/schema/defaults ou normalizar historico",
      "Alterar autoridade/gates/juizes de aprovacao",
      "Refatoracao ampla ou correcoes fora dos10 IDs"
    ],
    "regressions_forbidden": [
      "Perda/truncamento de fato ou rascunho",
      "Null/invalido virar zero conhecido",
      "Excecao generica ou teste enfraquecido para passar",
      "Takeover/skipWaiting/recarga PWA forcada"
    ]
  },
  "derived_artifacts": {
    "allowed": [
      "src/js/manifest.json",
      "build-id.js",
      "dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html",
      "src/vendor/pdfjs/runtime-assets.js",
      "src/vendor/normative/statute-payload.js"
    ],
    "generation_commands": [
      "python tools/rebuild_monolith.py",
      "python tools/validate_project.py"
    ],
    "manual_edit": "forbidden"
  },
  "external_side_effects": {
    "network": "allowed",
    "allowed_targets": [
      "Loopback sintético",
      "GitHub configurado — somente leitura"
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
      "Python temporario Playwright ja autorizado",
      "Node bundled",
      "Chromium temporario ja autorizado",
      "git — branch autorizada e leitura"
    ]
  },
  "acceptance_criteria": [
    "10 IDs corrigidos ou lacuna material explicitamente identificada",
    "Regressoes reproduzem baseline vermelho e passam no candidate",
    "Estado/drafts desconhecidos preservados; escrita recusada sem sucesso falso",
    "Canonicos de politica/engine e normativa com hashes originais",
    "Full final57 checks e focais pertinentes sem enfraquecimento",
    "Auditoria independente final; teste manual/aceite do proprietario pendentes antes de Git"
  ],
  "approved_tests": [
    "Regressoes AUD01-10",
    "Focais backup/PF/Forex/MEI/Notas/Pivots/module-work/PWA/PDF",
    "quality_gate full",
    "build reproducibility/sintaxe/manifest/security sweep"
  ],
  "rollback": {
    "source": [
      "Backup externo dos fontes preexistentes e BASE_SHA; reverter somente patch desta tarefa mediante pedido"
    ],
    "application_state": [
      "Nenhum dado real acessado; fixtures sinteticas"
    ],
    "data": [
      "Nenhuma migracao ou reescrita historica"
    ],
    "environment": [
      "Encerrar servidores/processos descartaveis"
    ],
    "verification": [
      "Hashes e status do candidate final"
    ]
  },
  "expires_on": [
    "Mudanca material de escopo",
    "Fim da tarefa"
  ]
}
```

[CHG/CTX de contexto dedicado](CHG-AUDIT-BUGFIXES-CONTEXT-20261012.md).

Nota de geração: src/js/manifest.json é o catálogo canônico de ordem e hashes, não output de rebuild_monolith.py. Os 11 hashes de fontes alteradas são reconciliados automaticamente por refresh_source_manifest.py, com 102 paths/ordem/runtimeAssets iguais à BASE_SHA; o gerador oficial continua responsável por build-id/portátil. Não foi alterado nenhum validador.

Aceite adicional específico recebido nesta conversa: “Autorizar essas duas atualizações descritivas”, após a proposta com dois diffs. Scope acrescenta somente docs/architecture/FX-PLANNING.md e PERSONAL-FINANCE.md para reconciliar descrições dos resultados/validadores existentes. Nenhuma regra, fórmula, parâmetro, schema, código, instrução ou gate foi alterado por esta emenda. Classificação descritiva N0-D; operações Git continuam sem autorização.
