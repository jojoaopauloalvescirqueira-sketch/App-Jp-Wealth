# Estado persistido — visão inicial

## Chave principal

```text
jpwealth_v9_state
```

## Agregados principais de `S`

- `params`: saldo, datas, MDD, alarme, gênese, VRM e referências.
- `matrix`: matriz quadrifásica base.
- `instruments`: instrumentos, preços, contratos, tetos e bloqueios.
- `profiles`: perfis de risco derivados da fonte central.
- `accounts`: parque de contas e dados operacionais.
- `phases`: grades e ordens da operação única.
- `ledger`: fechamentos diários do período.
- `ledgerArchive`: snapshots de períodos anteriores.
- `transitionLog`: auditoria de transições e eventos.
- `period`: identificação e perfil do período.
- `onboarding`: formulário de início e governança.
- `mei`: configuração e histórico do modelo estatístico.
- `quarantine`: intervalo de quarentena operacional.

## Regras de evolução

1. Toda chave nova entra em `DEFAULTS`.
2. `migrate()` deve aceitar estados anteriores sem perda silenciosa.
3. Migração nunca pode apagar campo desconhecido sem autorização formal.
4. Antes de mudança de schema, criar fixture anonimizada e teste de ida/volta de backup.
5. Credenciais não devem integrar fixtures, repositório ou commits.
