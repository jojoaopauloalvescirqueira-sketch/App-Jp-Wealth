# Roteamento de skills do projeto

As skills locais sao procedimentos versionados, nao agentes autonomos. O agente abre somente as skills acionadas pela tarefa e continua subordinado a `AGENTS.md`.

| Gatilho | Skill obrigatoria | Saida minima |
|---|---|---|
| Toda nova tarefa | `jpw-preflight` | base, branch, risco, contexto e bloqueios |
| Toda tarefa, conforme a fase; contrato antes de qualquer edição | `jpw-change-control` | escopo, invariantes, diff e rollback; em A0/A1 não autoriza escrita |
| Regra financeira/Estatuto, inclusive N3 financeiro | `jpw-normative-audit` | matriz norma-codigo-teste e conflitos; N3 exclusivamente de control plane segue o Harness/AGENTS, mantendo A4/full/auditoria independente |
| Estado, backup, senha, importacao | `jpw-data-safety` | contrato, compatibilidade e recuperacao |
| Testes ou falha, inclusive execução e alteração de testes | `jpw-test-triage` | classificação dos resultados conforme AGENTS, sem inferir aprovação |
| Interface e fluxo, incluindo UI, modal e responsividade | `jpw-browser-verification` | fluxos reais e viewports testados |
| Superfície de ataque, incluindo entradas/saídas, injeção, credenciais, dependências, PWA e CI | `jpw-security-audit` | ameaças, evidências e severidade |
| Estrutura do repositorio: organizacao de pastas, localizacao de novos arquivos, reorganizacao | `repository-architecture` | inventario, auditoria (interna + cold-start), mapa de migracao; escrita somente com plano aprovado |
| Mudanca material com potencial de alterar comportamento, contrato, arquitetura, fonte canonica ou representacao consumida pela camada agentica | `agentic-evolution-governance` | blast radius agentico com impacto separado de acao local, estado de coerencia quando houver reconciliacao; escrita somente com plano delimitado aprovado |
| Final de toda mudanca | `jpw-post-change-audit` | revisao do candidato, gates e riscos |

## Carregamento e mecanismos

Este roteamento exige abrir os arquivos `skills/<nome>/SKILL.md` pertinentes;
não afirma registro nativo automático. No Codex, verificar as skills realmente
oferecidas pelo ambiente; no Claude, importar o núcleo via `CLAUDE.md` e ler as
skills roteadas. Não criar cópias, agentes por pasta ou permissões para suprir
ausência de carregamento. Subagentes recebem packet explícito conforme
[AI-WORKFLOW.md](AI-WORKFLOW.md). Referência, skill e agente executável são distintos.

A harmonização de `jpw-change-control` preserva a exigência mais restritiva de
AGENTS anterior (toda tarefa); sua execução respeita a fase e não concede escrita.
N3 de control plane usa auditoria de engenharia; alcance financeiro também exige
o caminho normativo. As demais skills e seus gatilhos permanecem obrigatórios.

## Adaptação e preservação das skills externas

- `repository-architecture` v1.1 PRODUCTION-READY (producao propria; fonte canonica no acervo 7A2 SKILLS) e a primeira skill externa **instalada integralmente** como skill local: governa a arquitetura fisica do repositorio em cinco modos (DISCOVERY/AUDIT/DESIGN/MIGRATION/GUARD); somente MIGRATION escreve, com plano aprovado, e operacoes Git exigem autorizacao separada. Conteudo congelado: atualizacoes somente por nova versao vinda do acervo, nunca por edicao local.
- `agentic-evolution-governance` PRODUCTION-READY (producao propria; fonte canonica no acervo 7A2 SKILLS) e a segunda skill generica instalada integralmente como skill local: governa a coerencia evolutiva da camada agentica em seis modos (DISCOVERY/IMPACT/RECONCILE/PROPAGATE/REINDEX/GUARD), separando alcance semantico de necessidade de acao local. Somente PROPAGATE e REINDEX escrevem, e apenas com plano delimitado aprovado; operacoes Git e publicacao exigem autorizacao separada. Nao substitui `jpw-post-change-audit`, que continua responsavel pelo fechamento tecnico do candidato: mudanca sem impacto agentico encerra em `NO AGENTIC RECONCILIATION REQUIRED`. Conteudo congelado: atualizacoes somente por nova versao vinda do acervo, nunca por edicao local.
- `security-audit`, `pr-audit`, `iss-audit` e `pr-post-audit` inspiram a fronteira de confianca, a verificacao de afirmacoes e a auditoria do candidato final.
- `pr-bump` nao e adotada como skill local: o repositorio nao possui fluxo de dependencias compativel com seu foco em Bundler/Dependabot.
- `ai-memory-main` nao e incorporado como runtime. Adotamos apenas os principios de autoridade, contexto em camadas, frescor, handoff e exclusao de dados sensiveis. Qualquer runtime de memoria exigira piloto separado e avaliacao de privacidade.

## Regra anti-desalinhamento

Se uma skill sugerir acao contraria ao Estatuto, a uma decisao aprovada, a `AGENTS.md` ou ao escopo humano, a skill perde. Registrar a divergencia e parar a acao afetada.


## Feature Atlas parcial, com pendências

Para explicar finalidade/fluxo de uma feature ou investigar consumidores e impacto, usar `skills/jpw-feature-atlas/SKILL.md`, consultando somente a ficha pertinente em `docs/architecture/FEATURE-ATLAS.md` e depois os originais. Descoberta local usa links em `.agents/skills/` e `.claude/skills/` para a mesma skill dentro da raiz Git em consulta; disponibilidade efetiva depende de validação do ambiente. O Atlas não é agente autônomo nem fonte de autorização. Nenhuma restrição acima é substituída. Contrato histórico do piloto em `docs/work/FEATURE-ATLAS-PILOT.md`; transferência conjunta V4/Atlas autorizada com pendências em `docs/work/ATLAS-V4-INTEGRATION-20260910.md`; AUD-05/P2 aberto.

## X2 — revisão crítica de jornadas

Ao solicitar revisão de finalidade, integração funcional, código ou experiência, abrir `skills/jpw-critical-review/SKILL.md`. A0/A1: diagnóstico e recomendação, sem corrigir produto ou atualizar contexto. O modo lógico usa referência própria. Escopo integral somente se solicitado; reportar cobertura/lacunas. Links `.agents/skills/jpw-critical-review` e `.claude/skills/jpw-critical-review` apontam à fonte única local; não são prova de acionamento automático. Instalação regida por `docs/work/X2-CRITICAL-REVIEW-20260910.md`.
