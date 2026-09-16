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

`Finalizar sessão` exige confirmação progressiva e frase `ENCERRAR SESSÃO`. Este fluxo preserva no navegador cadastros, períodos, lançamentos, observações e operações Forex confirmadas para retomada; encerra processos temporários, desbloqueios e dados de acesso. Para remover a base do computador, use o fluxo explícito da Zona de Perigo depois de exportar uma cópia de recuperação. Em computador de terceiros, Finalizar Sessão por si só não elimina os históricos preservados.

Após a exclusão pela Zona de Perigo, a persistência fica bloqueada para a geração anterior da base. Atualizações assíncronas, importações iniciadas antes da exclusão e outras abas não podem recriar o estado antigo; uma nova base pode ser iniciada por novo carregamento, onboarding ou importação explícita. O service worker remove somente caches com prefixo `jp-wealth-`.

As chaves da allowlist auxiliar são `jpw_rail`, `jpw_expl`, `jpw_fs`, `jpwealth_v9_icon_choice`, a chave legada `jpwealth_v9_icon_theme`, as preferências isoladas do laboratório em `jpwealth_galton_preferences_v1`, o perfil local em `jpwealth_local_profile_v1`, a posição do botão de Notas em `jpwealth_notes_launcher_position_v1` e o sinal temporário `jpwealth_session_wipe_signal_v1`; o checkpoint fica em `sessionStorage` como `jpwealth_session_checkpoint_v1`. A limpeza não usa `localStorage.clear()`.

## Notas — posição local e rascunho

A posição do botão flutuante pertence somente a este navegador/origem. A chave
`jpwealth_notes_launcher_position_v1` contém `schemaVersion: 1` e coordenadas
numéricas finitas `x` e `y` entre 0 e 1. Essa preferência fica fora de `S`, do
schema de dados e do backup financeiro; notas, pastas e as três larguras já
persistidas continuam no agregado existente. A apresentação central adapta as
regiões de Pastas, Lista e Editor ao espaço disponível, sem regravar larguras
por resize.

Concluir um movimento ou ajuste pode gravar a posição uma vez, confirmada por
releitura exata. Cancelar, abrir, navegar, redimensionar e recarregar não gravam
essa preferência. Reload restaura a última posição confirmada; a projeção usa
as coordenadas proporcionais e os limites disponíveis. **Restaurar posição**
remove somente essa chave e volta ao canto inferior direito. JSON incompatível
é preservado, com posição padrão em memória e novas gravações bloqueadas até
conferência ou restauração explícita. Falha comprovada conserva o valor anterior
e o movimento vale apenas na sessão; desfecho desconhecido exige recarregar e
conferir. Campos desconhecidos de um envelope v1 compatível são preservados.

**Finalizar sessão remove essa preferência**, invalida movimentos e gravações
pendentes pela geração auxiliar da sessão e preserva notas, pastas e larguras.
A nova configuração da posição exige recarregar após finalizar. Importação e
a limpeza de dados da Zona de Perigo preservam a preferência local. As gravações
utilizam o lock existente quando há Web Locks, além da comparação do valor
anterior e do epoch; sem Web Locks, permanece a limitação de concorrência entre
abas do armazenamento local, sem promessa de transação entre abas.

O rascunho de Notas permanece apenas em memória. Salvar continua explícito, com
os mesmos contratos de recusa, rollback e nova tentativa. Fechar ou trocar a
seleção com alterações mantém a confirmação de descarte; o aviso nativo ao sair
da página não salva o rascunho nem promete recuperá-lo após reload.

Contrato em [CHG-NIGHT-PENDING-RECONCILIATION-20260914](../work/CHG-NIGHT-PENDING-RECONCILIATION-20260914.md).
Os focais `notes_experience_test.py`, `notes_launcher_test.py`,
`mvp_notes_test.py` e `finalize_session_test.py`, em `tools/`, cobrem esses
limites com dados sintéticos; este texto não substitui os resultados de execução.

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

## Backup: interpretar o resultado

A pasta escolhida é destino de exportação; a base ativa permanece no perfil/origem do navegador. Em `file://`, não se promete portabilidade entre caminhos/navegadores. Mantenha a origem em que os dados foram usados.

“Download iniciado” exige conferir o arquivo no navegador. Um arquivo entregue e um registro local recusado são resultados distintos: preserve o arquivo antes de repetir. Resultado desconhecido não prova ausência de arquivo e não libera Finalizar. Confirmação de backup é declaração explícita do operador, distinta da exportação; não se consolida após recusa comprovada.

Importar substitui os dados da base, preservando preferências locais deliberadamente excluídas. A porta recusa contêiner presente incompatível; ausência legítima em backup antigo segue o contrato legado. Em recusa de gravação, o estado anterior é preservado. Em desfecho desconhecido, pare novas gravações e examine a recuperação; não repita às cegas.

Perfil/foto, layouts/navegação, posição do launcher, caches, permissões de pasta e rascunhos não salvos não acompanham a cópia financeira. Não prometa recuperação desses itens a partir do JSON de dados.

## Recovery do Execution Board (2026-09-15)

O checkpoint externo da campanha fica em `/Users/joaopauloalves/.codex/forex-execution-board/20260915/evidence/`: baseline.json, baseline-recovery.tar.gz, manifest/fingerprint/diff e relatório do candidate. Restaurar código somente nos caminhos próprios, por cópia seletiva verificada; não usar reset/stash ou tocar outras worktrees.

Rascunhos de linhas/observações e lotes recusados de cotação existem somente em memória. Cancelar relê confirmação; recarga não promete recuperá-los. Backup guarda observações/referências confirmadas e snapshots históricos. UNKNOWN mantém recuperação existente contra retry cego. Nova geração/finalização invalida solicitações de cotações, e resposta tardia não recria dados. Consulte [Execution Board](../architecture/FOREX-EXECUTION-BOARD.md).
