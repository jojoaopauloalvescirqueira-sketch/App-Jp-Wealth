# Fluxo de trabalho com IA

## Contexto mínimo para uma tarefa

Fornecer à IA:

- objetivo concreto;
- arquivos permitidos;
- regra normativa aplicável;
- comportamento esperado;
- dados de teste anonimizados;
- critérios de aceitação;
- proibição explícita de alterações fora do escopo.

## Prompt-base

```text
Leia AGENTS.md e os documentos indicados. Não altere regras financeiras.
Analise a tarefa, apresente plano, modifique somente os arquivos autorizados,
execute validate e smoke test, mostre o diff e registre riscos residuais.
Não faça commit sem revisão humana.
```

## Tarefas adequadas para IA

- localizar código e dependências;
- documentar comportamento existente;
- criar testes de caracterização;
- implementar mudança delimitada;
- revisar diff;
- detectar inconsistências e risco de regressão.

## Tarefas que permanecem humanas

- definir regra financeira;
- declarar qual cálculo é normativo;
- autorizar migração ou exclusão de dados;
- aprovar publicação;
- decidir conflito entre Estatuto, decisões e código.
