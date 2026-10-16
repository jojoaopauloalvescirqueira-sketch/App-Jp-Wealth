# Ensaio da interface Stoikus 1.23.0 — R5

Candidato privado, somente fontes. Este roteiro registra o que foi observado; não presume aprovação financeira. Faça o ensaio exclusivamente no MT5 separado de testes e numa conta demo. Trocar de conta no terminal de uso não separa arquivos.

## Preparar os mesmos bytes

1. Na entrega R5, extraia `Kit_Windows_Stoikus_Janelas_R5.zip` numa pasta local nova. Mantenha `root-pin-R5.json` separado, fora do ZIP. Leia `LEIA-PRIMEIRO.md` antes de executar os comandos; ele informa verificações, argumentos e destino temporário.
2. Confira o hash do ZIP e o pin com a identidade entregue. Execute as fixtures e o verificador do kit conforme o guia. Uma recusa exige diagnóstico; não contorne a verificação.
3. Execute somente a compilação em staging. Guarde `results.zip`, a pasta de evidências, build/versão do MetaEditor e MT5 e os hashes dos quatro EX5. O kit não instala nem abre gráficos. Quatro EX5 novos e logs sem erros/avisos inesperados são pré-requisito para instalar no terminal demo; não aprovam o funcionamento da interface.
4. Antes de copiar qualquer arquivo para o MT5 de testes, confira o recibo contra o pin e preserve os arquivos anteriores. Copie apenas o conjunto inventariado da mesma compilação, sem substituir arquivos desconhecidos ou modificados. Não copie arquivos para `MQL5/Files`.

## Reconhecer os componentes

| Componente | Local e função |
| --- | --- |
| Monitor | EA no gráfico de apoio reservado; acompanha os dados e deve permanecer aberto. Retire produtores antigos Observer/Accountant de todos os gráficos antes de iniciá-lo. |
| Conta | Indicador no gráfico de trabalho; resumo sobre o gráfico e janela de consulta. |
| NoCuda | Segundo indicador no gráfico de trabalho; desenhos e estudos. Pode coexistir com Conta. |
| Abrir Painéis | Script pontual que acrescenta os indicadores ausentes. Terminar é normal. Não inicia o Monitor. |

Confira Conta e NoCuda em Ctrl+I e mensagens em Experts. Se faltarem dados, Sistema deve informar estado, motivo e próxima ação; N/A não significa zero.

## Roteiro de aceite iniciante

Registre **PASS**, **FAIL** ou **NOT_RUN**, captura e observação para cada item. Não registre PASS apenas porque o componente compilou.

| Item | Ação e resultado esperado |
| --- | --- |
| Primeiro olhar | Localizar Conta, alavancagem da conta inteira, risco do grupo por símbolo/direção e disponibilidade dos dados. Identificar a unidade e o escopo sem adivinhação. |
| Ocupação do gráfico | Resumo novo inicia Compacto, largura 280 pixels lógicos, fundo 30% transparente. Sete métricas ficam acessíveis em Conta; opções permitem Completo. Configuração anterior válida e métricas ocultas devem continuar respeitadas. |
| Recolher resumo | Clicar −; aparece Conta pequeno e visível. Restaurar não altera o desenho nem aplica rascunhos. A janela de consulta e o resumo têm estados independentes. |
| Fundo transparente | Em ⋯, conferir 0%, 30% e 100%. Somente o fundo muda. Texto legível e cliques funcionam também em 100%. |
| Mover e redimensionar | Arrastar cabeçalho e alça/borda das janelas e a largura do resumo. Soltar e testar rolagem do gráfico; pressionar Esc durante um gesto deve cancelar e restaurar a interação anterior. Nenhuma janela deve ficar irrecuperável fora do gráfico. |
| Conta | Conferir as seis seções, sete métricas e atalhos 1–7. Ler títulos/valores/motivos sem sobreposição; detalhes mostram valores e escopos completos. Paginação fica separada de aplicar/cancelar. |
| Minimizar consulta | Editar um rascunho sem aplicar, minimizar Conta ou NoCuda e restaurar. O texto continua na sessão e não foi salvo como fato. Histórico/Monitor seguem trabalhando. Desenhos permanecem. |
| Histórico | Conferir leitura em preparação, auditoria ativa, resultado concluído sem registros e falha com orientação. Minimizar e restaurar durante auditoria; nenhum histórico deve ser apagado. |
| NoCuda | No modo manual, editar sem aplicar e minimizar/restaurar. No Fibonacci, selecionar Canal Fibonacci de três âncoras, conferir prévia e vínculo. Trocar conta/fonte antes de confirmar deve continuar recusando contexto inválido. |
| Reabrir/template | Após ação visual concluída, reabrir ou carregar template e conferir posição/tamanho/recolhimento. Abrir/redesenhar sozinho não deve gravar preferências. Máscara sem métricas continua sem métricas. |
| Gráfico pequeno | Diminuir o gráfico; quando não houver área legível, localizar o botão Conta para recuperar a consulta. O lançador NoCuda deve evitar a área ocupada pelo resumo, inclusive recolhido ou transparente. |
| DPI e temas | Repetir em Windows 100/125/150/200%, temas claro/escuro e fonte configurada. Conferir valores grandes, símbolo longo, estimativas e indisponibilidade. Guardar capturas sem dados privados. |

Falha gráfica deve deixar alternativa opaca identificada e permitir recuperação. Testes de falha por injeção pertencem à bancada técnica; não altere dados de uso para simulá-los.

## Registro mínimo

Data; Windows/arquitetura; build do MT5/MetaEditor; caminho do terminal e pasta de dados de testes; conta **demo** (identificador pode ser mascarado); produto/MQL/cálculo; hash do pin/freeze/ZIP/fontes/EX5; logs de compilação; capturas; itens acima e parecer do proprietário.

Estados distintos: **compilado**, **instalado**, **interação verificada** e **aceito pelo proprietário**. Windows ARM no Parallels não substitui Windows x64 independente. Enquanto esses registros não existirem, os respectivos estados permanecem NOT_RUN.
