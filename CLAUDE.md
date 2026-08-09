# CLAUDE.md — Instruções permanentes para o Claude Code no JP Wealth

Este arquivo orienta o Claude Code neste repositório. Ele trata especificamente de **Git, branches e limites operacionais**. Para regras financeiras, normativas e de dados, a fonte de autoridade é `AGENTS.md` — este arquivo não repete essas regras, apenas as referencia.

## Leitura obrigatória antes de trabalhar

1. Ler este `CLAUDE.md`.
2. Ler `AGENTS.md`.
3. Ler `README.md`.
4. Ler `docs/governance/CONTEXT-MAP.md` e consultar somente as fontes relacionadas à tarefa.
5. Executar:

```bash
python3 tools/agent_preflight.py --mode audit
git branch --show-current
git status --short
git log -1 --oneline
```

Nenhuma edição começa antes desses cinco passos.

## Política de branches

- `main` representa a versão oficial, estável e aprovada.
- Nunca desenvolver diretamente em `main`.
- Cada funcionalidade, melhoria ou correção deve possuir uma branch própria criada a partir de `main`.
- Uma branch deve conter somente uma tarefa coerente.
- Trabalhar exclusivamente na branch ativa indicada pelo usuário.
- Nunca trocar de branch por iniciativa própria.
- Caso a branch ativa não seja a branch indicada pelo usuário, interromper e relatar antes de alterar qualquer arquivo.
- Caso existam alterações não relacionadas já pendentes na árvore, interromper e relatar.
- Não criar múltiplos worktrees ou pastas do projeto sem autorização expressa.

## Operações Git proibidas sem autorização

O Claude não pode executar autonomamente:

- commit;
- push;
- pull;
- merge;
- rebase;
- reset;
- stash;
- force-push;
- criação ou exclusão de branch;
- exclusão de tag;
- alteração de remoto;
- remoção de worktree.

Commit, push e integração à `main` dependem de autorização humana expressa, dada na conversa, para aquela ação específica.

## Processo antes da implementação

Antes de editar:

1. confirmar branch e estado Git (ver "Leitura obrigatória" acima);
2. auditar o código relevante;
3. identificar arquivos e dependências;
4. classificar o risco da mudança (ver abaixo);
5. apresentar um plano;
6. aguardar autorização humana.

## Classificação de risco

A classificação de risco N0–N3 é definida em `AGENTS.md` (seção "Classificação de mudanças") e detalhada em `docs/governance/CHANGE-PROCESS.md`. Resumo:

- `N0-D`: documentacao, governanca e harness sem mudanca de runtime.
- `N0-V`: mudanca exclusivamente visual.
- `N1`: comportamento não normativo.
- `N2`: persistência, backup, recuperação ou integridade operacional.
- `N3`: regras financeiras, cálculos, risco, Estatuto ou parâmetros normativos.

Mudanças N2 e N3 exigem testes reforçados e autorização específica, conforme já estabelecido em `AGENTS.md`.

## Restrições financeiras e normativas

A lista completa de proibições (fórmulas financeiras, perfis de risco, MDD, alavancagem, matriz quadrifásica, Ordem Gênese, poda LIFO, retração favorável, parâmetros do método NoCoda, regras do Estatuto, schema da base, formato do backup, critérios de exclusão de dados, critérios de validade operacional) está definida em `AGENTS.md` (seção "Proibições") e é vinculante para este arquivo também — não é repetida aqui para evitar duplicação e divergência futura entre os dois documentos.

Em caso de ambiguidade sobre qualquer uma dessas áreas, interromper e solicitar decisão humana.

## Preservação

- Nunca usar `localStorage.clear()`.
- Nunca apagar dados silenciosamente.
- Nunca alterar o formato do backup sem autorização.
- Nunca editar manualmente arquivos gerados quando existir ferramenta oficial de reconstrução (`tools/rebuild_monolith.py`).
- Não sobrescrever a arquitetura da PWA.
- Preservar o ciclo conservador do service worker (`docs/architecture/PWA-UPDATE-LIFECYCLE.md`).
- Não misturar correções adjacentes à tarefa autorizada.

## Processo após a implementação

Depois de implementar:

1. reconstruir os artefatos derivados, quando aplicável;
2. executar os testes aplicáveis;
3. apresentar:

```bash
git status --short
git diff --stat
git diff --check
git diff --name-only
```

4. apresentar o diff relevante;
5. informar testes executados e não executados;
6. informar riscos residuais;
7. aguardar teste manual do usuário;
8. não criar commit sem autorização.

## Testes disponíveis

Quando aplicável:

```bash
python3 tools/quality_gate.py --tier fast
python3 tools/quality_gate.py --tier standard
python3 tools/quality_gate.py --tier full
```

Uma falha ou impossibilidade deve receber a classificação definida em `docs/governance/QUALITY-GATES.md`. Não declarar sucesso sem evidência do candidato atual.

## Critério de conclusão

Uma tarefa somente estará pronta quando:

- o escopo tiver sido respeitado;
- os testes aplicáveis tiverem passado;
- o diff tiver sido apresentado;
- nenhuma alteração estranha estiver misturada;
- o usuário tiver testado manualmente;
- o usuário tiver autorizado o commit.

## Ver também

- `AGENTS.md` — protocolo de IA, hierarquia de autoridade, proibições financeiras/normativas, classificação de risco.
- `docs/governance/AI-WORKFLOW.md` — contexto mínimo e tarefas adequadas para IA.
- `docs/governance/CHANGE-PROCESS.md` — processo de mudança controlada e modelo de commit.
- `docs/governance/PROJECT-CONTEXT.md` — contexto estável e contratos centrais.
- `docs/governance/CURRENT-STATE.md` — fotografia mutável, falhas e bloqueios atuais.
- `docs/governance/SKILL-ROUTING.md` — skills obrigatórias por tipo de tarefa.
- `docs/GIT-WORKFLOW.md` — fluxo Git explicado em linguagem simples.
