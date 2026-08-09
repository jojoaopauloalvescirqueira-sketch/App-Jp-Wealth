# Tarefa ativa - Governanca multiagente e qualidade

- Data: 2026-08-09
- Baseline: `f722eb3`
- Branch: `audit/governanca-multiagente`
- Nivel: N0-D e correcoes N0-V/N1 estritamente cobertas pelos gates
- Autoridade: implementacao solicitada pelo gestor; commit/push/merge nao autorizados
- Estado: implementacao concluida, em validacao final e revisao humana

## Objetivo

Transformar as filosofias fornecidas em regras locais, skills acionaveis, contexto duravel e gates de qualidade reproduziveis para prevenir desalinhamento entre agentes.

## Dentro do escopo

- governanca e mapa de contexto;
- skills locais;
- preflight e orquestrador de testes;
- documentacao de seguranca e auditoria;
- correcao de expectativas comprovadamente obsoletas no harness;
- correcao dos bloqueios N0-V/N1 descobertos pelo novo gate (cabecalho, Notas, precache e orientacao de contingencia);
- automacao de CI sem publicacao.

## Fora do escopo

- alteracao de regra financeira, perfil, MDD, DD, fase, LIFO, stop ou MEI;
- mudanca de schema/persistencia;
- correcao do fluxo de importacao/recuperacao N2;
- commit, push, merge ou deploy.

## Invariantes

- `jpwealth_v9_state`, `DEFAULTS`, `migrate()` e formulas permanecem intactos.
- Nenhuma credencial ou backup real entra no Git.
- Testes nao sao enfraquecidos para esconder defeito de produto.
- Falhas remanescentes sao registradas com categoria e evidencia.

## Criterios

- novo agente encontra contexto e stop conditions sem conversa anterior;
- preflight detecta branch/dirty/contexto/manifest/sensiveis;
- quality gate registra resultados sem falso PASS;
- skills sao concisas e roteadas;
- documentacao e handoff refletem o repositorio real;
- diff final e testes sao apresentados ao gestor.

## Resultado atual

- `quality_gate.py --tier standard`: PASS 5/5.
- `quality_gate.py --tier full`: PASS 9/11; dois `PRODUCT_FAIL` N2 documentados.
- `mvp_notes_test.py`: PASS integral apos reconciliacao do harness e correcoes N0/N1.
- oito skills aprovadas pelo validador oficial; Python e YAML validos.
- nenhuma regra N3 ou schema foi alterado.
