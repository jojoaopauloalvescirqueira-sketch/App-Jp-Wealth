# Roteamento de skills do projeto

As skills locais sao procedimentos versionados, nao agentes autonomos. O agente abre somente as skills acionadas pela tarefa e continua subordinado a `AGENTS.md`.

| Gatilho | Skill obrigatoria | Saida minima |
|---|---|---|
| Toda nova tarefa | `jpw-preflight` | base, branch, risco, contexto e bloqueios |
| Qualquer edicao | `jpw-change-control` | escopo, invariantes, diff e rollback |
| Regra financeira/Estatuto | `jpw-normative-audit` | matriz norma-codigo-teste e conflitos |
| Estado, backup, senha, importacao | `jpw-data-safety` | contrato, compatibilidade e recuperacao |
| Falha ou alteracao de teste | `jpw-test-triage` | classificacao PASS/FAIL/ERROR/NOT_RUN |
| UI, modal, responsividade | `jpw-browser-verification` | fluxos reais e viewports testados |
| Credenciais, dependencias, PWA, CI | `jpw-security-audit` | ameacas, evidencias e severidade |
| Estrutura do repositorio: organizacao de pastas, localizacao de novos arquivos, reorganizacao | `repository-architecture` | inventario, auditoria (interna + cold-start), mapa de migracao; escrita somente com plano aprovado |
| Mudanca material com potencial de alterar comportamento, contrato, arquitetura, fonte canonica ou representacao consumida pela camada agentica | `agentic-evolution-governance` | blast radius agentico com impacto separado de acao local, estado de coerencia quando houver reconciliacao; escrita somente com plano delimitado aprovado |
| Final de toda mudanca | `jpw-post-change-audit` | revisao do candidato, gates e riscos |

## Adaptacao das skills externas

- `repository-architecture` v1.1 PRODUCTION-READY (producao propria; fonte canonica no acervo 7A2 SKILLS) e a primeira skill externa **instalada integralmente** como skill local: governa a arquitetura fisica do repositorio em cinco modos (DISCOVERY/AUDIT/DESIGN/MIGRATION/GUARD); somente MIGRATION escreve, com plano aprovado, e operacoes Git exigem autorizacao separada. Conteudo congelado: atualizacoes somente por nova versao vinda do acervo, nunca por edicao local.
- `agentic-evolution-governance` PRODUCTION-READY (producao propria; fonte canonica no acervo 7A2 SKILLS) e a segunda skill generica instalada integralmente como skill local: governa a coerencia evolutiva da camada agentica em seis modos (DISCOVERY/IMPACT/RECONCILE/PROPAGATE/REINDEX/GUARD), separando alcance semantico de necessidade de acao local. Somente PROPAGATE e REINDEX escrevem, e apenas com plano delimitado aprovado; operacoes Git e publicacao exigem autorizacao separada. Nao substitui `jpw-post-change-audit`, que continua responsavel pelo fechamento tecnico do candidato: mudanca sem impacto agentico encerra em `NO AGENTIC RECONCILIATION REQUIRED`. Conteudo congelado: atualizacoes somente por nova versao vinda do acervo, nunca por edicao local.
- `security-audit`, `pr-audit`, `iss-audit` e `pr-post-audit` inspiram a fronteira de confianca, a verificacao de afirmacoes e a auditoria do candidato final.
- `pr-bump` nao e adotada como skill local: o repositorio nao possui fluxo de dependencias compativel com seu foco em Bundler/Dependabot.
- `ai-memory-main` nao e incorporado como runtime. Adotamos apenas os principios de autoridade, contexto em camadas, frescor, handoff e exclusao de dados sensiveis. Qualquer runtime de memoria exigira piloto separado e avaliacao de privacidade.

## Regra anti-desalinhamento

Se uma skill sugerir acao contraria ao Estatuto, a uma decisao aprovada, a `AGENTS.md` ou ao escopo humano, a skill perde. Registrar a divergencia e parar a acao afetada.
