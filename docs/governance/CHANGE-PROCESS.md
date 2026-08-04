# Processo de mudança controlada

## Antes de editar

- Classificar a mudança em N0, N1, N2 ou N3 conforme `AGENTS.md`.
- Identificar artigos, decisões e funções afetadas.
- Criar branch ou cópia de segurança.
- Registrar comportamento atual com teste quando a área não estiver coberta.

## Durante a edição

- Um objetivo por commit.
- Menor diff possível.
- Não misturar formatação maciça com lógica.
- Não renomear identificadores globais sem mapa de dependências.
- Não alterar `DEFAULTS` e `migrate()` sem testar backups anteriores.

## Revisão

A revisão deve responder:

1. Qual problema foi resolvido?
2. Qual regra normativa foi tocada?
3. O que mudou no estado persistido?
4. Quais cenários foram testados?
5. Como reverter?
6. Há risco de perda de dados ou alteração silenciosa de cálculo?

## Commit recomendado

```text
<tipo>(<área>): descrição objetiva

Regra afetada: nenhuma | Art. X | decisão YYYY-MM-DD
Dados: sem mudança | schema vX -> vY
Testes: validate + smoke + casos específicos
```
