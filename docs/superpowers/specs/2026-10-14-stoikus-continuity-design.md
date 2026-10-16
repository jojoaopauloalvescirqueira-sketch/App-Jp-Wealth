# Stoikus — lifecycle, continuidade e diagnóstico — design autorizado

Autorização humana: “Autorizo ordem recomendada”, 14/10/2026, reproduzindo os quatro passos da revisão. Fonte do desenho e achados: relatório REVISAO-STOIKUS.md entregue na área de visualizações/stoikus-review-20261014. Base0037bd3c8a7ab2b4e21f7fdcb60f66ed93230874. Branchcodex/stoikus-continuity-20261014, worktreeisolada/private/tmp/jpw-stoikus-continuity-20261014.

## Contrato

NoCuda: admissão e namespace são pré-condições da limpeza; prefixo vazio não autoriza remover objetos nem preferências compartilhadas. Regressões exercitam funções atuais e falhasOnInit, mantendo objetos alheios e dados salvos.

Histórico Pessoal: continuidade requer auditoria integral de todos envelopes e sequência de uma geração coerente, incluindo dados antigos e corrupção depois da antiga barreira100000. Trabalhar em fatias retomáveis ou solução equivalente com progressão verificável; somente geração integralmente auditada pode liberar consultas/escrita/exportação. Nenhum parcial viraVALID/Current. Cache persistido não pode conceder autoridade. A proposta concreta será congelada após avaliar APIs e snapshot/ownership; especificação detalhada fica em .superpowers/sdd/stoikus-continuity-20261014/design-personal.md, mantendo estes critérios como invariantes.

Monitor: timer ativo não significa produtor admitido. Informar aguardando identidade/titularidade, produtorativo, conflito, perda delease e recuperação; log por transição com supressão de repetição periódica. Status financeiro e timestamps de captura continuam independentes das mensagens.

## Preservação

Sem alterar cálculo1.9.0, oráculos, alertas60s, trading, armarSupervisor, schemas/dados históricos por reset ou migração destrutiva. Não instalar/ensaiar em pasta de dados existente. BaselineMQL eZIPs preservada até delta autorizado. Semcommit/push/merge/publicação nesta tarefa.

## Provas

RED→GREEN em comportamento real, SQLitereal quando pertinente, apenasAPIs nativas indisponíveis substituídas. Candidato congelado comhash, build oficial e revisoresindependentes; hostall+webfull pertinentes. NativeWindowsx64 eWindowsARM são provas distintas. Ensaio demoisolado e logs/EX5não homologam regrasfinanceiras. Validação cominiciante depende de participante real; preparação do roteiro não é aceitação. Atualização de grafo/documentação fica separada das correções de runtime e preserva grafo anterior.
