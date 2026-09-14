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

As chaves auxiliares auditadas sao `jpw_rail`, `jpw_expl`, `jpw_fs`, `jpwealth_v9_icon_choice`, a chave legada `jpwealth_v9_icon_theme`, as preferencias isoladas do laboratorio em `jpwealth_galton_preferences_v1`, o perfil local em `jpwealth_local_profile_v1` e o sinal temporario `jpwealth_session_wipe_signal_v1`; o checkpoint fica em `sessionStorage` como `jpwealth_session_checkpoint_v1`. A limpeza nao usa `localStorage.clear()`.

## Perfil local — JP Wealth Account

O nome de exibição e a foto configurados em Configurações pertencem somente a
este navegador/origem. A chave `jpwealth_local_profile_v1` guarda um envelope
`schemaVersion: 1` com `displayName` e `avatarDataUrl` (JPEG compacto ou `null`).
Não há autenticação, envio da foto, vínculo com contas financeiras ou armazenamento
de arquivo original, EXIF, caminho ou nome de arquivo. O raster gerado tem até
256 × 256 pixels e a representação persistida da imagem até 200 KiB. A seleção
aceita PNG, JPEG e WebP estáticos de até 5 MiB e 16 megapixels. O nome permite até
120 caracteres Unicode, sem controles; vazio corresponde a “Seu perfil”.

Salvar é explícito e confirma, por releitura exata, nome e foto em uma única
gravação. Abrir, navegar e recarregar não gravam. Falha comprovada conserva o
perfil anterior e o rascunho; desfecho desconhecido bloqueia novas tentativas até
recarregar e conferir. JSON incompatível ou falha de leitura não provoca
reescrita automática. Uma foto indisponível mostra o monograma sem apagar o
conteúdo original; sua substituição ou remoção exige edição e salvamento.
Campos desconhecidos de um envelope v1 compatível permanecem preservados.

Reload e importação de base mantêm esse perfil. O backup financeiro não inclui
essa preferência, e a Zona de Perigo preserva-a junto às preferências locais.
**Finalizar sessão remove o perfil** pela allowlist auxiliar existente, descarta
fotos/rascunhos em memória e invalida leituras de imagem pendentes, inclusive nas
outras abas alcançadas pelo protocolo de sessão. Falha de remoção é reportada
pelo aviso já existente; não deve ser tratada como exclusão confirmada. A próxima
configuração do perfil exige novo carregamento após a finalização.

Os saves utilizam o lock existente da sessão quando o navegador oferece Web
Locks, além da comparação da preferência anterior e do epoch auxiliar. Sem Web
Locks, permanece a limitação de concorrência entre abas do armazenamento local;
uma releitura isolada não é apresentada como transação entre abas. Imagens de
teste e evidência devem ser sintéticas; fotos pessoais não entram em Git,
screenshots automatizadas ou relatórios sem autorização específica.
