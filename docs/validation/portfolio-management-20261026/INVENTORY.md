# Inventário da entrega e dos achados

Este documento descreve o candidato local `abbcd8b5e67be657`, na branch autorizada `codex/portfolio-gerenciamento-20261026`, base `3e24f60`. O resultado do pacote deve ser lido no [relatório](README.md); existência de implementação ou focal aprovado não substitui o FULL.

## Produto

| Superfície | Mudança | Preservação |
|---|---|---|
| Portfólio → Análise | Renomeia Research e retira destinos públicos vazios; ficam Estudos Nocuda e Estudos de Pivots | Identidades internas, estudos e progresso; não reintroduz Nocuda Tool |
| Gerenciamento | Disponibilidade própria e posição padrão depois de Portfólio | Ordem relativa personalizada; Forex pode permanecer congelado |
| Reservas | Transfere a interface e usa seleção própria em memória | Cálculos, comandos e writer anteriores; contexto operacional do Forex independente |
| Contabilidade | Substitui a tela anterior pela projeção anual e realizado lado a lado, com edição diária revisada | Ledger canônico, registros observados, auditoria e backups anteriores |
| Calendário anual | Ano civil, dias elegíveis e exclusões explícitas; subtotais semanais | Não pressupõe feriados de bolsa ou trabalho realizado |
| Fechamento anual | Retratos versionados e reconferência após correções | Não encerra operações nem o período operacional; é acréscimo aprovado do site |
| Telas estreitas | Três colunas e detalhes expansíveis em vez de reduzir ou cortar valores | Mesmos valores e comandos; controles e rascunhos preservados |
| Integrações | Dashboard, busca/navegação, Notas, notificações e guia Dante recebem os destinos atuais | Serviços compartilhados e histórico anterior |

## Defeitos confirmados e corrigidos

| Achado | Correção e prova |
|---|---|
| Identificação de período e moeda em contexto de Gerenciamento | Contexto explícito e regressões de estado; nenhuma seleção operacional implícita |
| Troca de contexto recusada mantinha o valor visual proposto em um seletor nativo | Restaurar o valor efetivamente aceito, preservando o próprio controle e rascunhos; RED/GREEN em `recovery/reserves-*.txt` |
| Declaração de ausência fora da programação não aparecia na grade | União das datas de fatos e declarações; caso MGT-35, sem capitalização adicional |
| Cancelar configuração perdia o retorno de foco | Retorno ao acionador real e teste de jornada; não simular foco por coordenadas |
| Cabeçalho e alinhamentos herdavam estilos globais inadequados | Regras locais e medição dos componentes, além da caixa externa |
| Dashboard perdeu seu consumidor econômico anterior durante a reorganização | Restaurar o consumidor existente e acesso ao calendário; 184 casos FF passaram no focal, com contraprovas da integração |
| Inicialização falhava em contexto que não fornecia `crypto.randomUUID` | Mesmo fallback local já usado por Agenda e Planejamento; MANSTATE-32 demonstrou RED/GREEN. IDs locais não são credenciais |

As falhas originais continuam nos recibos anteriores; as correções não encerram incidentes históricos não examinados.

## Adaptações dos verificadores

As expectativas antigas de sete menus, posição de Finanças Pessoais, host contábil e destinos retirados foram substituídas somente pelos contratos aprovados. Os controles de navegação recusada, ausência de gravação, persistência, XSS e downloads permaneceram exigidos.

A recuperação também corrigiu uma prova que tentava acionar um botão coberto pela gaveta modal: o teste agora usa a folha visível real, verifica seu destino e o fechamento da gaveta. Não utiliza clique forçado nem aumenta o timeout.

O scanner de credenciais ganhou duas exceções literais limitadas ao texto das expressões de proteção; contraprovas continuam rejeitando credenciais reais. A prova XSS preserva os casos de importação anteriores e verifica o renderer compartilhado e a nova tela de Gerenciamento. Os patches, escopos e críticas independentes estão em `evidence/`.

Dois checks da primeira rodada foram classificados pelo runner como `PRODUCT_FAIL`, mas seus tracebacks demonstraram ausência da variável obrigatória de navegador. A nova invocação fornece o ambiente necessário, sem alterar esses dois testes. O resultado bruto anterior não foi reclassificado ou apagado.

## Limites e residual

- Possível confirmação redundante de trabalho do Forex ao usar um formulário compartilhado aberto por Gerenciamento. O proprietário, o writer e as proteções do formulário permanecem corretos; residual P3 descrito no contrato, sem correção adjacente nesta entrega.
- O Harness foi localizado em uma cópia preservada, idêntica por SHA-256 ao arquivo encontrado na lixeira do iCloud. Não se moveu arquivo nem se alterou a referência das instruções.
- A proposta de atualizar um ponteiro geral de contexto está registrada e **não aplicada**. A cadeia atual até o contrato da nova área continua acessível; não se declara reconciliação de todo o projeto.
- Comparação nativa no Excel, Safari, leitor de tela real, toque físico e aceite visual/compreensão do usuário não são comprovados pelos testes automatizados.
- Sem importação de valores pessoais do Excel, dependências novas, mudança de V11/Reservas, exclusão de registros, commit, merge, push ou publicação.
