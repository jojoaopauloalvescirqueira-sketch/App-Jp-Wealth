# Recuperação e preservação de dados

## Programa versus dados

O repositório contém o programa. Os dados reais normalmente permanecem no navegador, vinculados à origem onde o sistema foi usado.

## Prioridade

1. Preservar o perfil do navegador.
2. Abrir o mesmo domínio/origem anterior.
3. Exportar o backup completo pelo próprio aplicativo.
4. Guardar duas cópias fora do repositório.
5. Inserir apenas cópia anonimizada em `data/samples/` para testes.

## Local de backups

`data/backups/` é ignorado pelo Git. Não versionar backups reais, senhas de investidor ou dados pessoais.

## Chave do estado

```text
jpwealth_v9_state
```

Não limpar dados de site, histórico de armazenamento ou perfil do navegador antes da exportação.

Para encerrar o uso em computador de terceiros, utilize `Finalizar sessão`. A função exige confirmação progressiva, usa o backup completo existente quando necessário, preserva chaves de outras aplicações na mesma origem e remove as chaves locais do JP Wealth somente depois da frase final `APAGAR TUDO`.

Após a exclusão, a persistência fica bloqueada para a geração anterior da sessão. Atualizações assíncronas, importações iniciadas antes do encerramento e outras abas não podem recriar o estado antigo; uma nova sessão pode ser iniciada por novo carregamento, onboarding ou importação explícita. O service worker remove somente caches com prefixo `jp-wealth-`.

As chaves auxiliares auditadas sao `jpw_rail`, `jpw_expl`, `jpw_fs`, `jpwealth_v9_icon_choice`, a chave legada `jpwealth_v9_icon_theme` e o sinal temporario `jpwealth_session_wipe_signal_v1`; o checkpoint fica em `sessionStorage` como `jpwealth_session_checkpoint_v1`. A limpeza nao usa `localStorage.clear()`.
