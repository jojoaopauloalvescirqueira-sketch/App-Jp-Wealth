# Backup completo e retomada — 2026-09-16

Contrato implementado por CHG-COMPLETE-BACKUP-20260916. O envelope continua `jpwealth_full_backup` / `V9.1`; o bloco opcional `workspace.schemaVersion: 1` amplia a cobertura sem mudar schemas financeiros. Backups anteriores continuam aceitos e preservam as preferências do destino.

| Meta | Conteúdo | Destino no arquivo |
|---|---|---|
| 1 | Contas, operações, períodos, históricos e Consolidado FX | `state` inteiro |
| 2 | Planejamento FX, Finanças Pessoais e Alladin | `state.fxPlanning`, `personalFinance`, `alladin` |
| 3 | Notas, pastas, NoCoda, Pivots e metadados | agregados completos em `state` |
| 4 | Tema | `state.theme` |
| 5 | Nome e imagem de perfil, própria ou da galeria | `workspace.preferences.jpwealth_local_profile_v1`; JPEG incorporado, sem depender do arquivo original |
| 6 | Layouts de widgets, ordem/estilo/posição da navegação, largura independente da Lateral em níveis, transparência Liquid Glass, fonte, ajuda e marca | `workspace.preferences`, allowlist `JPW_WORKSPACE_KEYS`; `jpw_nav_submenu_rail` aceita `expanded`/`collapsed` e `jpw_nav_glass_tint` aceita somente string inteira `0..100` |
| 7 | Aparência e posição do botão de Notas | chaves próprias em `workspace.preferences` |
| 8 | Preferências e configuração do Laboratório Galton | `workspace.preferences.jpwealth_galton_preferences_v1` |
| 9 | Edições pendentes de Notas/pastas, perfil, aparência, planejamento e Board; campos editados ainda presentes nos formulários | `workspace.drafts`, material para revisão, sem executar comandos financeiros |

`dgBuildBackupBlob` clona todo `state`, preservando extensões desconhecidas compatíveis, e incorpora o snapshot de workspace. O checkpoint da sessão inclui esse snapshot: mudar apenas a foto, por exemplo, também invalida a declaração de backup anterior. Senhas de investidor continuam suprimidas; campos de senha, tokens, PIN, arquivos e busca não são coletados como rascunhos.

## Importação e confirmação

A validação ocorre antes da primeira escrita: schema conhecido, allowlist de preferências, `jpw_nav_glass_tint` canônico entre `0` e `100`, `jpw_nav_submenu_rail` restrito a `expanded`/`collapsed`, limites de tamanho/profundidade, nomes sem controles e JPEG de até 256 × 256 pixels/200 KiB. Workspace até 4 milhões de caracteres JSON, no máximo 500 rascunhos de até 1 milhão de caracteres cada; exceder limites recusa, sem truncar. Backup workspace v1 antigo sem uma dessas chaves permanece válido e conserva a preferência correspondente do destino.

O documento importado recebe `state.workspaceRecovery = {schemaVersion:1,pending:true,snapshot}`. A importação utiliza o protocolo existente de lock, epoch e read-back do documento. Depois projeta as preferências, confirma as strings por releitura e grava `{schemaVersion:1,pending:false,drafts}`. O journal fica junto dos dados confirmados, sem chave paralela nova. Uma falha de projeção mantém a restauração pendente, exibe aviso e bloqueia gravações ordinárias; a recarga tenta concluir. Preserve sempre o arquivo de origem em caso de erro. Resultado de armazenamento desconhecido não equivale a sucesso.

Depois da importação, recarregue para que todos os controladores de apresentação adotem as preferências restauradas. O botão “Rascunhos recuperados” permite ler/copiar o material e excluí-lo explicitamente. Não registra ordens, não reconfirma lançamentos e não envia formulários. Campos de formulários que já foram fechados/descartados não são ressuscitados; adapters explícitos conservam as edições que o módulo ainda mantém em RAM.

## Finalização

`Finalizar Sessão` preserva o documento durável inteiro, incluindo campos novos e desconhecidos, além das preferências da allowlist. Guarda os rascunhos capturados no documento final. Encerra desbloqueios, senha em RAM, leitores/controladores e handles de pasta. O perfil salvo sobrevive; o editor de perfil é invalidado até recarregar. Fonte financeira da finalização é o documento confirmado em disco, nunca uma base obsoleta de outra aba. Zona de Perigo permanece um fluxo de exclusão distinto.

## Limites deliberados

O backup é de dados e preferências, não uma cópia executável do navegador: não contém permissões de pasta, credenciais, caches públicos, downloads originais, abas/scroll/foco ou trajetórias/bolas de uma simulação em execução. A marca restaurada não troca por si só o ícone de um PWA já instalado. Rascunhos são recuperados para revisão, não reabertos automaticamente em operações financeiras. Importação deve usar uma versão do aplicativo que compreenda este contrato; builds antigos desconhecem `workspace`.

## Verificação

`tools/complete_backup_test.py`: round-trip real Blob/FileReader em contextos Chromium isolados, modular e portátil, preferências/foto, recarga, rascunhos, preservação integral na finalização, backup legado, formato inválido, interrupção/quota e recuperação. Testes financeiros e de persistência existentes continuam necessários; relatório FULL e evidências locais são registrados no CHG. Nenhum dado real do usuário é necessário para os testes.


## Contas e Período — extensão opcional (2026-09-23)

O clone integral de `state` inclui ambiente real/demo, atribuição revisionada de perfil e referências documentais dos períodos/operações. Ausência em backup antigo é válida; não dispara cadastro, novo período ou preenchimento retroativo. Extensões incompatíveis são recusadas antes da escrita. IDs, vínculos e campos desconhecidos compatíveis permanecem preservados.

Rascunhos visíveis capturados pelo workspace continuam material para revisão, nunca confirmação automática de conta/período. Etapas ainda em RAM não equivalem a cadastro salvo. A avaliação de rollback lê o backup novo na versão anterior e executa sua gravação com fixture sintética, comparando essas extensões; o recibo do candidate informa o resultado real.


## Disponibilidade — candidate 2026-09-24
A preferência jpw_module_availability_v1 participa de workspace v1: ausência preserva destino, null retorna aos defaults; inválidos recusados. Consentimento informa mudanças de disponibilidade. Exportação de recuperação explicitamente consentida preserva raw inválido em drafts sem aplicação automática; dados financeiros completos. Contrato: [MODULE-AVAILABILITY](MODULE-AVAILABILITY.md). Decisão canônica: [Alladin congelado](../decisions/2026-09-24-alladin-congelado.md). Candidate isolado, ainda em validação.
