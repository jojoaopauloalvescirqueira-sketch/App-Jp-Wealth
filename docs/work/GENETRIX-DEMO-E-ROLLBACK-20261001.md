# GENETRIX 1.17.0 — roteiro nativo, demo e rollback

Estado: CANDIDATE. Este roteiro prepara uma avaliação posterior; não registra instalação nem execução. Conta real, publicação e integração ao site não fazem parte desta entrega. O supervisor começa em observação; não abre posições, não altera SL/TP e exclui conta real no próprio código.

## Pré-requisitos e compilação

1. Usar terminal e pasta de dados separados, conta **demo hedging** dedicada e perfil da corretora identificado. Verificar símbolo/contrato/moeda/permissões/FIFO. Não utilizar o terminal operacional para validar este candidato.
2. Conferir `CANDIDATE-FROZEN.json` e os hashes do ZIP de fontes. Extrair os diretórios MQL5/Include, Experts, Indicators, Scripts e Images nas localizações correspondentes da pasta isolada. Não substituir arquivos ativos existentes.
3. Compilar os `.mq5` declarados pelo pacote com MetaEditor oficial. Registrar versão/build do compilador, ambiente, início/fim, log completo, avisos e erros. Compilar indicador, Accountant, Supervisor e scripts; um único EX5 não prova o pacote completo.
4. Registrar SHA256 do fonte, de suas dependências e de cada EX5 produzido, ligando-os ao build congelado. `.ex5` avulso de origem desconhecida não constitui evidência. Erro nativo exige correção, novo freeze e repetição pertinente; não ajustar fixtures ou notas para escondê-lo.
5. Executar scripts de testes nativos do candidato em ambiente separado; comparar todas as referências congeladas, não apenas resumo final. Não distribuir pacote compilado até recibos e artefatos corresponderem.

A compilação local não foi feita nesta entrega: MetaEditor foi localizado, porém Wine executável não estava disponível; o acesso por comando ao Windows via Parallels retornou exigência de edição Pro/Business, e o conteúdo visual do convidado não foi legível para automação segura. Essa limitação está em `NATIVE-ENVIRONMENT.json`.

## Observação e contabilidade

Adicionar o **Accountant** a um gráfico dedicado. Ele só lê posições/ordens/histórico e mantém seu ledger próprio. Os inputs `InpHistoryCoverageConfirmed=false`, `InpCostCoverageConfirmed=false` e `InpCoverageEvidence=""` começam sem confirmação. Para uma avaliação com cobertura declarada, a referência deve demonstrar zeragem, período, conta e custos atribuíveis; a publicação registra DECLARADA e não verifica essa documentação automaticamente. A declaração não resiste a troca de conta até nova configuração; sucesso de HistorySelect não comprova história completa. Custos/cobranças não atribuídos permanecem parciais. Não marcar completude apenas para obter números no painel.

Adicionar o indicador existente a outro gráfico e mostrar “Flutuante compensado” (sétima métrica/atalho 7). Escolher explicitamente o ciclo por símbolo exato, direção e ID. Conferir Gênese inferida/ambígua, membros, realizado, swap, comissões, taxas, flutuante remanescente, saldo denominador e cobertura. A consulta no indicador não publica nem modifica o ledger.

Comparar com fixtures e com o histórico exportado da conta demo: custos de entrada, parcial, fechamento da Gênese antes de outras posições, pendente que mantém ciclo vazio, preenchimento dessa pendente, correção/exclusão de deal, custo tardio, rollover/troca de ticket, replay/reinício, conta/moeda/USC e múltiplos grupos. Declarar cenários que a corretora não permite reproduzir, em vez de simular sua execução como teste nativo.

## Supervisor: observação antes de armamento

Adicionar o Supervisor a gráfico dedicado, inicialmente em observação. Conferir captura atual, bruto/equity, projeção das pendentes e próximo ticket LIFO sem pedidos enviados. As pré-condições nativas são demo, hedging, FIFO desativado, conta e servidor exatos, dados atuais, permissões e um único executor.

O armamento exige ação explícita da sessão atual, vinculada à identidade da conta. Usar o mecanismo e os nomes exatos de entrada apresentados pelo Supervisor candidato e descritos no manual do pacote. Não editar o código para remover guards. Reinício/troca de conta exige novo armamento; uma intenção recuperada é reconciliada antes de qualquer novo envio.

Somente depois da revisão do candidato concreto e da conta demo dedicada, preparar as posições de teste de forma visível. O Supervisor não abre operações. Durante os ensaios, registrar a influência das posições manuais e de outros EAs, incluindo possibilidade de perda de hedge.

## Sessões e evidências obrigatórias

Executar cada cenário crítico em **três sessões novas no MT5**, mantendo também as tentativas falhas. Três processos de teste local do código não substituem essas sessões. Nenhum cenário `NOT_RUN` pode ser convertido em PASS por inspeção de fonte.

| Grupo | Ensaios |
|---|---|
| Limite | <7, =7, >7 e valor exibido como 7,00 por arredondamento; equity cai sem entrada |
| Sequência | LIFO multisímbolo; empates; fechamento integral; servidor parcial/residual |
| Pendentes | Soma incompatível; cancelamento recente; ativação durante cancelamento |
| Desfecho | Recusa cancelamento, recusa fechamento mais recente, unknown, ordem ativa e retorno sem deal |
| Recuperação | Desconexão, eventos omitidos, reinício em intenção, banco corrompido, duplicata |
| Bloqueios | Real, netting, FIFO, permissões, conversão e contrato não demonstrados |
| Financeiro | Comissões, swap, taxas, efeitos de liquidação na equity e retirada de hedge |
| Interface | Moeda/%/ciclo, Current/Partial/Historical/N/A, V1/V2/V3, all-hidden, themes/DPI |

Ficha por tentativa: ID do cenário; sessão; hashes; perfil; pré-condições; captura anterior; ação esperada; intenção persistida; pedido/retorno/deal; estado posterior; timestamps e duração excesso→detecção→redução; telas; resultado `PASS/FAIL/INCONCLUSIVE/NOT_RUN`; causa assistente/ferramenta/ambiente/fixture/indeterminada; parecer de revisor distinto do autor.

Bloquear aprovação ao demonstrar qualquer falha crítica: alvo errado, abrir posição, alterar SL/TP, reenvio desconhecido, pular LIFO recusado, operar real/netting/FIFO, usar dados inválidos, duplicar contabilidade ou declarar custos/história completos sem evidência. Todos os denominadores das contagens e percentuais são explicitados.

## Rollback e armazenamento

1. Desarmar e retirar o Supervisor do gráfico. Confirmar que não permanece pedido seu ativo ou intenção desconhecida; reconciliar antes de declarar encerrada a atividade.
2. Retirar o Accountant e o indicador candidato; conservar bancos e recibos para auditoria. Não apagar ledger/intenção para eliminar uma falha.
3. Restaurar no ambiente isolado os fontes/EX5 previamente comprovados, sem copiar arquivos do candidato para a conta operacional. O site original e os fontes originais permanecem preservados.
4. Exportar evidências antes de alterar perfil ou conta. Não rearmar automaticamente após restauração. Banco novo e namespaces próprios não devem modificar os stores antigos.
5. Se a intenção ainda for incerta, manter a execução impedida e confrontar ordens/deals/posições no terminal e servidor; ausência no gráfico não prova ausência da solicitação.

Exclusão de instâncias no mesmo terminal não impede outro terminal ou VPS com o mesmo login. A avaliação exige um único Supervisor autorizado. Uma coordenadora entre terminais é trabalho adicional, não uma propriedade demonstrada deste candidato.
