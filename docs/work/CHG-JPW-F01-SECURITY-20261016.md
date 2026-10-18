# CHG-JPW-F01-SECURITY-20261016 — segurança da Contabilidade

A autorização é a resposta humana **“Autorizar primeiro lote, branch e worktree”** à proposta delimitada de F01. Este registro descreve essa aprovação, não a cria. A fotografia inicial excluía commit, push, merge e publicação. Em 18/10/2026 o proprietário autorizou explicitamente commit, push, merge e limpeza das worktrees na consolidação; publicação do site continua separada.

## Compreensão e contrato

1. **Finalidade:** JP Wealth organiza registros e apoia decisões financeiras; esta mudança protege a fronteira entre um arquivo externo e a interface, conforme SECURITY-MODEL e COMPLETE-BACKUP.
2. **Responsabilidade:** `00-forex-state.js` valida o ledger ativo por conta/período; `01-daily-ledger.js` normaliza a importação e projeta seus valores no DOM. A interface não deve interpretar dados como código.
3. **Antes/depois:** uma versão contendo marcação atravessa o schema e executa no HTML. Depois, tipos conhecidos inválidos são recusados antes da escrita, e o renderer permanece defensivo caso receba texto hostil.
4. **Impacto:** importação e leitura do ledger contextual, apresentação de revisão e testes dos artefatos modular/portátil. A inspeção do checksum não autentica autoria; a recusa de tipo ocorre no normalizador/importador real que chama `supported`.
5. **Limites:** preservar versão ausente/null como base legada segura, 0 e inteiros numéricos seguros não negativos; não converter strings nem reescrever registros. Preservar extensões compatíveis, snapshots históricos e `source.version` textual da prévia mensal. Não corrigir IDs duplicados, dívida PF, cronologia ou perda de extensões neste lote. Fórmulas, schema, stores, migração, locks e permissões intactos.
6. **Prova:** o novo caso permanente deve falhar no baseline pelo defeito real e passar sem alterar estímulo/oráculo, com FileReader/DOM/storage reais. Validar controles legítimos, recarga, recusa antes de consentimento/gravação e defesa isolada do sink, identificada como tal. Executar full vigente e revisão independente, preservando tentativas/falhas.

## Plano aprovado, execução delimitada

- [ ] Acrescentar testes F01 à suíte existente e registrar RED no baseline.
- [ ] Aplicar o menor delta ao predicado da linha e ao escape do badge.
- [ ] Reconstruir pelos geradores oficiais; registrar GREEN modular/portátil e compatibilidade.
- [ ] Executar focais relacionados e full vigente, sem alterar gates/CI ou expectativas anteriores.
- [ ] Congelar fontes/derivados/testes, revisar independentemente e apresentar resultado/limites para aceite humano.

Regressões entram no `import-xss` já selecionado pelo full; não haverá novo runner nem alteração de quantidade/seleção. O índice informativo em AGENTS foi uma proposta da fotografia16/10, não transportada para a revisão18/10. As referências atuais são os contratos F01; AGENTS permanece byte-idêntico à main, sem nova autoridade ou exceção. A trilha de validação acrescenta casos e mantém os oráculos existentes; não altera o juiz para aprovar o produto.

## Fontes e identidade

Base e hashes anteriores em `/private/tmp/jpw-seguranca-evidencias-20261016/baseline-sources.json`. Harness externo 2.0 localizado no acervo atual `2 - TRABALHO/99 - Prompts&Skills/9 - SOFTWARE`, com hash registrado. Fontes: AGENTS; README/PROJECT-CONTEXT/CONTEXT-MAP; SECURITY-MODEL; STATE-SCHEMA §§3 e contexto Forex; COMPLETE-BACKUP; FOREX-V11-ENGINE; DB-STORAGE-GOVERNANCE/DATA-RECOVERY; writers e leitores auditados em `contrato-version.md`. Históricos e o aviso material de 225 caminhos permanecem; este lote não reconcilia G02.

## Contrato de execução

```yaml
{
  "schema": "jp-harness/chg/v1",
  "change_id": "CHG-JPW-F01-SECURITY-20261016",
  "status": "approved",
  "objective": "Corrigir somente o XSS F01 da Contabilidade, sua validacao de version e a regressao permanente",
  "risk_level": "N3",
  "authority_required": "A4",
  "target": {
    "root": "/private/tmp/jpw-seguranca-contabilidade-20261016",
    "branch": "codex/jpw-seguranca-contabilidade-20261016",
    "baseline_sha": "bf0b1e8a882c9cdf880129f68f7c111e06e6f0c4"
  },
  "scope": {
    "allowed_files": [
      "src/js/10-domain/00-forex-state.js",
      "src/js/30-accounting/01-daily-ledger.js",
      "tools/import_xss_security_test.py",
      "docs/work/ACTIVE-TASK.md",
      "docs/work/CHG-JPW-F01-SECURITY-20261016.md",
      "CHANGELOG.md",
      "docs/audit/F01-SECURITY-20261016.md",
      "tools/forex_v11_ledger_planning_test.py",
      "docs/work/CHG-JPW-F01-CONTEXT-20261018.md",
      "SESSION_HANDOFF.md",
      "docs/governance/CURRENT-STATE.md",
      "docs/governance/CONTEXT-MAP.md"
    ],
    "forbidden_files": [
      "docs/normative/",
      "docs/decisions/",
      "mt5/",
      "tools/quality_gate.py",
      "tools/agent_preflight.py",
      ".github/",
      "src/js/00-core/00-forex-policy.js",
      "src/js/10-domain/00-forex-engine.js",
      "src/js/00-core/04-persistence.js"
    ],
    "allowed_actions": [
      "Criar a branch exata e uma worktree isolada aprovadas",
      "Validar version das linhas ativas e escapar sua apresentacao",
      "Acrescentar casos permanentes a suite import-xss existente, preservando casos anteriores",
      "Registrar o escopo/evidencias nos contratos F01, preservando AGENTS e autoridades vigentes",
      "Gerar artefatos oficiais derivados e executar focais/full/revisao independente",
      "Reconciliar à main atual antes de concluir a correção existente",
      "Concluir P2 de incremento de revisão nos dois escritores, com regressão de rollback sem mudar fórmula ou formato",
      "Commit, push e merge após os gates aprovados, conforme pedido humano de 18/10/2026"
    ],
    "forbidden_actions": [
      "deploy",
      "Alterar dados reais, schema, formulas ou regras financeiras",
      "Corrigir F02-F06 ou G01/G02",
      "Mudar criterios/seletores do runner, CI, autoridade ou excecoes"
    ],
    "regressions_forbidden": [
      "Perda de extensoes compativeis",
      "Normalizacao silenciosa de versoes",
      "Escrita antes de recusa de importacao",
      "Interpretacao de texto como HTML executavel",
      "Enfraquecer assercoes anteriores"
    ]
  },
  "derived_artifacts": {
    "allowed": [
      "src/js/manifest.json",
      "build-id.js",
      "src/vendor/pdfjs/runtime-assets.js",
      "src/vendor/statute/*",
      "src/vendor/downloads/*",
      "dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html",
      "downloads/jpw-alavancagem-atual/manifest.json",
      "downloads/jpw-alavancagem-atual/*.zip"
    ],
    "generation_commands": [
      "python3 tools/rebuild_monolith.py"
    ],
    "manual_edit": "forbidden"
  },
  "external_side_effects": {
    "network": "allowed",
    "allowed_targets": [
      "Loopback sintetico",
      "PyPI somente para runtime temporario de testes previamente autorizado"
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
      "Python3.12",
      "Playwright1.60.0 temporario",
      "Chromium1223 descartavel",
      "Node bundled",
      "Compiladores de testes existentes",
      "Git para as ações de consolidação expressamente solicitadas: commit, push e merge após validação"
    ]
  },
  "acceptance_criteria": [
    "RED pelo XSS/aceitacao indevida, nao por ambiente",
    "GREEN dos mesmos casos no modular e portatil",
    "Versoes ausente/null/0/inteiros seguros>=0 preservadas sem coercoes",
    "Tipos invalidos recusados antes de confirmar/aplicar o backup; RAM/disco intactos",
    "Renderer trata versao hostil como texto inerte",
    "Extensoes e snapshots historicos preservados",
    "Full vigente executado e classificado sem omissoes; achados independentes resolvidos no escopo"
  ],
  "approved_tests": [
    "python3 tools/import_xss_security_test.py",
    "python3 tools/forex_v11_state_test.py",
    "python3 tools/forex_v11_ledger_planning_test.py",
    "python3 tools/financial_projection_audit_test.py",
    "python3 tools/quality_gate.py --tier full",
    "python3 tools/agent_instruction_structure_test.py",
    "git diff --check"
  ],
  "rollback": {
    "source": [
      "Reverter somente o delta desta branch; restaurar derivados pelos geradores oficiais"
    ],
    "application_state": [
      "Nenhuma alteracao de dados reais; fixtures sinteticas descartaveis"
    ],
    "data": [
      "Preservar arquivos rejeitados e backups existentes; nao migrar/limpar/renumerar"
    ],
    "environment": [
      "Encerrar processos de testes e descartar perfis; runtime temporario permanece fora do projeto"
    ],
    "verification": [
      "Hashes da main e ZIPs historicos preservados; casos focais originais mantidos"
    ]
  },
  "approved_by": "Proprietario: resposta explicita nesta conversa",
  "approved_at": "2026-10-16T18:35:26.299904+00:00",
  "authorization_evidence": "Autorizar primeiro lote, branch e worktree",
  "timestamp_note": "approved_at registra a documentacao do aceite; timestamp da resposta humana nao foi exposto",
  "expires_on": [
    "Mudanca de branch/alvo/base material",
    "Ampliacao para outros achados, regras, migracao ou publicacao"
  ],
  "authorization_renewal_20261018": {
    "evidence": "essa outra arvore está com muitos outros arquivos, eu quero resolver todas as pendencias do jp welath, realizar commit push, merge e limpar todas as worktress",
    "scope": "Correção F01 existente e P2 demonstrado pela revisão; reconciliar baseline e contexto factual, preservar dados e gates",
    "recorded_at": "2026-10-18T16:40:33.399195+00:00",
    "original_base": "2b22175a4f3f47b1f289deca65366c4dc0445dca"
  }
}
```

## Reconciliação de 18/10/2026 — revisão dos incrementos

Base atual bf0b1e8a882c9cdf880129f68f7c111e06e6f0c4 na mesma branch autorizada. O delta F01 foi reaplicado por três vias; derivados antigos não foram copiados. Backups completos e patch original estão em jpw-consolidacao-worktrees-20261018, fora do repositório.

O P2 independente foi reproduzido com testes novos antes da correção: incremento além de MAX_SAFE e recálculo de revisão ausente. Apenas os dois escritores de versão usam agora o mesmo sucessor seguro. A leitura/importação conserva ausente, null e todos os inteiros seguros não negativos; nenhum dado é normalizado durante consulta. Uma revisão esgotada que precisaria avançar recusa o comando inteiro e restaura RAM, eventos, auditoria e revisões antes de qualquer save. Linhas sem incremento continuam utilizáveis. Fórmulas e schema permanecem iguais.

TDD local: três casos negativos falharam no diagnóstico anterior ao fix, sem erro de ambiente; o focal oficial passou31/31 após a correção. Casos de XSS modular/portátil, full, revisão final e Git da revisão atual ainda terão evidências próprias. O GREEN de16/10 é histórico e não aprova este delta.
