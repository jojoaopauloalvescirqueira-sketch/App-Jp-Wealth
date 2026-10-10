# GENETRIX 1.21.1 — guia da revisão e rollback

## Finalidade

Revisão candidata do 1.21.0 para tornar a interface mais previsível e tratar falhas de memória sem aparentar dados válidos. Não redefine o JP Wealth nem o NoCuda, não homologa o harness e não altera fórmulas, unidades, limites ou schemas financeiros.

## Uso habitual

1. Reserve um gráfico para `JPW_Genetrix_Monitor`. Mantenha seus dois módulos conforme configuração validada. Não anexe Observer ou Accountant antigos ao mesmo tempo.
2. No gráfico em que trabalha, use o indicador `JPW_Alavancagem_Atual`. **Genetrix · Conta** abre os detalhes das sete leituras. Valores indisponíveis têm motivo; algumas dependem de histórico, cobertura ou seleção de ciclo.
3. Se quiser estudar um canal, adicione `JPW_NoCuda_Channels`. **NoCuda · Gráficos** abre as ferramentas técnicas. Importe, confira e confirme explicitamente o estudo antes de salvar observações ou retomar seu acompanhamento.
4. Ao alternar Conta e NoCuda, a janela anterior libera os campos de edição. O rascunho não é salvo por essa alternância. Volte ao módulo e use a ação explícita de salvamento quando tiver conferido o conteúdo.
5. Para preparar uma mensagem, selecione uma posição ou pendente. Confira todas as páginas da prévia. O programa prepara texto; não envia mensagens automaticamente.
6. O Supervisor é opcional e separado. Ele não é requisito do resumo, do Histórico Pessoal ou do flutuante compensado. Esta entrega não o arma.

## Quando houver um problema

| Mensagem ou situação | Próximo passo |
| --- | --- |
| Conta sem contexto disponível | Aguarde a próxima captura; confira a conexão e os registros de inicialização. Não substitua o EA do gráfico de apoio. |
| Memória insuficiente / lista indisponível | Feche e reabra a seção após liberar recursos. Não trate a lista parcial como inventário completo. Os estudos e bancos não são apagados. |
| Histórico incompleto / gravação não confirmada | Preserve os registros e examine a falha de armazenamento; não conclua que o aviso foi visto ou que a gravação ocorreu. |
| NoCuda pede um estudo | Abra Registro para escolher um estudo, ou importe um canal e confira antes de confirmar. |
| NoCuda pede um vínculo | Confira o canal e confirme o vínculo antes de ocultar a origem ou acompanhar suas mudanças. |
| Conteúdo com várias páginas | Use as setas de paginação; a contagem vale também para a apresentação alternativa, sem campo de seleção de texto. |
| Indicador desapareceu após trocar o EA | O resumo pertence ao indicador Conta. Confira Ctrl+I e o resultado de compilação; use um gráfico de apoio para o Monitor. |

## Conferência em ambiente isolado

A compilação deve usar todas as bibliotecas e recursos do pacote, com os hashes do manifesto. Os 4 EAs, 2 indicadores e 27 scripts são alvos distintos. Um retorno do compilador, sozinho, não prova sucesso: conferir logs, executáveis novos e identidade dos fontes.

A confirmação visual e comportamental exige terminal isolado: abrir Conta/NoCuda, editar um campo, alternar módulos, voltar e conferir o rascunho; navegar uma prévia longa; reiniciar preservando preferências; conferir as sete leituras e seus estados. Não copiar credenciais nem dados da conta operacional para montar esse ensaio. Negociação permanece desativada. Popup/som e interação real não são demonstrados pelos testes C++ locais.

## Instalação futura e rollback

Esta entrega não aplica a revisão no terminal operacional. Antes de uma migração autorizada, identificar a pasta de dados do terminal correto; guardar o conjunto anterior de fontes, recursos, executáveis, configurações e preferências. Não apagar bancos ou registros financeiros. Não sobrescrever apenas um include isolado: usar um pacote coerente.

Para reverter código, remover os componentes candidatos do ambiente de teste e recuperar o conjunto anterior correspondente, preservado com seus hashes. Não executar produtores antigos e Monitor em paralelo; primeiro interromper o produtor substituído. Como não há migração de schema nesta revisão, o rollback de código não requer substituir o histórico por uma cópia antiga.

## Limites

Compilação não equivale a aceite operacional. Contraprovas locais verificam comportamentos delimitados e usam dados sintéticos. Não demonstram eficácia financeira, ausência universal de defeitos ou funcionamento em toda corretora. Normas, estados pendentes, falhas históricas e restrições do Supervisor permanecem preservados.
