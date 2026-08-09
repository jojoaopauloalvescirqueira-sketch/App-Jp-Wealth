# Fluxo de trabalho multiagente

## Principio

Agentes compartilham arquivos e Git, nao memoria implicita. Toda afirmacao relevante deve apontar para uma fonte versionada ou para uma evidencia reproduzivel no candidato atual.

## Inicio de sessao

1. Ler `AGENTS.md` e a instrucao especifica do agente, quando existir.
2. Executar `python3 tools/agent_preflight.py --mode audit` para auditoria ou `--mode edit` antes de alterar arquivos.
3. Ler `docs/governance/CONTEXT-MAP.md`.
4. Abrir `PROJECT-CONTEXT.md`, `CURRENT-STATE.md`, `docs/work/ACTIVE-TASK.md` e apenas as fontes tematicas exigidas.
5. Registrar base, escopo, nivel N0-D a N3, invariantes e criterios.

## Fronteiras entre agentes

- Um agente por tarefa coerente e por conjunto de arquivos sem sobreposicao.
- Delegacao nao transfere autoridade: o agente principal continua responsavel pela revisao.
- Um agente nao deve editar arquivo que outro agente esteja alterando sem coordenacao explicita.
- Saida de agente e evidencia nao confiavel ate ser confrontada com o diff e testes.
- Handoff informa o estado, mas o proximo agente deve confirma-lo no disco.
- Nenhum agente pode promover hipotese, pendencia ou memoria a decisao normativa.

## Brief minimo

Use `docs/templates/TASK-BRIEF.md` e declare:

- objetivo e nao objetivos;
- arquivos permitidos;
- nivel de risco e autoridade recebida;
- fonte normativa, se aplicavel;
- invariantes e compatibilidade;
- criterios de aceite;
- testes e rollback.

## Durante a implementacao

- Manter `docs/work/ACTIVE-TASK.md` atual e curto.
- Executar testes focados; nao mascarar falha com `try/except` generico ou expectativa mais fraca.
- Se o escopo crescer de nivel, parar e obter nova autorizacao.
- Se surgir conflito com M0/M2, registrar em ADR ou auditoria e parar a mudanca afetada.

## Handoff obrigatorio

Ao encerrar trabalho material, atualizar `SESSION_HANDOFF.md` com:

- `BASE_SHA`, branch, arquivos e funcoes alterados;
- decisoes aplicadas e pendencias;
- comandos executados e classificacao exata;
- riscos e proxima acao segura;
- operacoes Git/publicacao ainda nao autorizadas.

O handoff nao deve conter credenciais, dados reais, conclusoes nao verificadas ou instrucoes conflitantes com `AGENTS.md`.

## Encerramento

Executar `python3 tools/quality_gate.py --tier <fast|standard|full>`, revisar o diff integral e aplicar `skills/jpw-post-change-audit/SKILL.md`. Declarar claramente o que passou, falhou, nao rodou e permanece bloqueado.
