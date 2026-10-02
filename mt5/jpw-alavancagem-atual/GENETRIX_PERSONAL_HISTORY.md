# GENETRIX 1.18.0 — Histórico Pessoal

Candidato observador, em revisão. Base: 1.17.0 RC2 preservada. Implementação em fontes, testes locais, compilação nativa e aceite operacional são etapas distintas. Este arquivo não concede autorização para negociar, instalar em conta operacional ou publicar.

## O que acompanha

O EA `JPW_Alavancagem_Observer` acompanha todas as posições abertas e entradas pendentes da conta: compras e vendas, ordens manuais e de outros EAs, inclusive stop-limit. Não usa filtro por MagicNumber. Identifica posições pelo `POSITION_IDENTIFIER`; mudanças de ticket ou volume não criam uma identidade artificial. Pendentes usam seu próprio ticket. A análise é prospectiva desde a ativação, por conta e instalação do MT5; não importa períodos antigos nem consolida terminais.

Apenas uma leitura válida de `SL == 0` abre ocorrência e solicita aviso: **“sem SL registrado na corretora”**. O programa não avalia stops virtuais nem transforma o aviso em certificado de infração estatutária. O primeiro aviso é solicitado após confirmação; reavisos são solicitados a cada 60 segundos, com revalidação antes de cada chamada. O intervalo usa relógio monotônico na sessão e horários persistidos após reinício; não reproduz avisos atrasados em fila. Alertas simultâneos são agrupados em uma janela e uma solicitação de som, com identidades individuais no registro.

Colocar SL resolve o episódio; retirar depois abre outro. Fechar a janela de alerta não resolve a ocorrência. Desaparecimento confirmado encerra o acompanhamento; fechamento, cancelamento ou execução só recebem classificação específica com evidência do histórico do MT5. Uma pendente parcialmente executada e a posição resultante permanecem sujeitos distintos; o vínculo exige evidência.

O EA não coloca SL, não altera ordens, não fecha posições e não arma o supervisor 7x. Fechar ou ocultar o Cockpit não encerra o observador; remover/parar o EA, fechar o terminal ou desconectar interrompe a cobertura. Uma janela de um segundo é solicitada ao timer, sem garantia de despacho nesse prazo.

## Recordes de alavancagem

`Alavancagem utilizada = nocional bruto de todas as posições abertas / equity`.

Reutiliza o cálculo financeiro existente. Pendentes aparecem na fotografia, mas não entram no nocional efetivamente aberto. O máximo é inicializado na primeira leitura elegível; somente aumento estrito sem arredondamento substitui o recorde. Empate preserva a primeira ocorrência. Queda da equity pode gerar recorde sem nova entrada. `Current` e `Estimated` mantêm máximos separados. Equity não positiva, conversão incompleta, contrato não suportado ou captura instável não viram zero nem atualizam o máximo. Universo aberto validamente vazio pode produzir zero.

A fotografia registra janela e origem da captura, versão, qualidade, saldo, equity, crédito, resultado flutuante, margens e nível de margem; posições e pendentes com identidade, tipo, direção, volume, preços, SL/TP; contratos, contribuições e cotações usadas nas conversões. Campos indisponíveis ficam explícitos. USC mantém a unidade monetária original e exige perfil contratual verificado quando aplicável. O registro não infere fase, aderência normativa ou estado psicológico.

A tela usa **“Maior alavancagem observada desde…”**. Picos entre capturas, antes da ativação e em períodos sem cobertura permanecem desconhecidos. Esta métrica não substitui a alavancagem estatutária nem o saldo inicial formal do ciclo.

## Consulta pelo Cockpit

1. Abra GENETRIX e selecione **Histórico Pessoal**.
2. **Próxima seção** percorre resumo, ocorrências, solicitações de aviso, recordes, sessões, cobertura e detecção/desfechos (incluindo o contexto da primeira observação). Setas percorrem registros; cada linha abre o detalhe. Textos extensos têm paginação própria.
3. **Conta … próxima** consulta outro histórico da mesma instalação. A indicação **Conta histórica · consulta somente** não troca a conta operacional do terminal. As identidades são opacas; o prefixo exibido permite conferir a seleção.
4. **Atualizar consulta** solicita nova leitura ao coordenador. O desenho da interface não faz SQL nem grava dados financeiros.
5. **Exportar… → Salvar CSV** gera consulta tabular. **Backup JSON** gera envelope versionado integral dentro da capacidade declarada. O pedido conserva a conta selecionada no clique, mesmo se a consulta mudar enquanto aguarda processamento; um segundo pedido aguarda a conclusão do primeiro. A tela identifica a conta exportada e informa sucesso somente após confirmação da escrita/verificação disponível, ou informa falha/incompletude. Não existe restauração automática de dados reais.

O resumo histórico e a evidência recente do produtor são separados. Um registro antigo não prova que o EA esteja ativo. Durante mudança de identidade operacional, a consulta fica indisponível até nova confirmação; o rótulo anterior não permanece como conta atual. O Cockpit destaca leitura desconhecida, avisos e **“histórico incompleto — gravação não confirmada”**. A máscara visual V3 das sete métricas permanece preservada, inclusive a preferência de ocultar todas; a aba não muda fórmulas nem preferências anteriores.

## Armazenamento e cópias

Novo namespace exclusivo: `MQL5/Files/JPWealth/Genetrix/PersonalHistory/`. Identidade estável derivada de servidor, conta, moeda/unidade e diretório da instalação, sem versão do produto. Não grava credenciais. SQLite contém metadados, titularidade, journal sequencial, episódios e máximos; os registros de MDD, Stop Risk, Diagnostics e ledger não são reutilizados.

Cada máximo e sua fotografia são gravados na mesma transação. Projeções apontam para testemunhos imutáveis do journal; hashes e sequência são conferidos. Escritor único combina arquivo de exclusão da instalação e titularidade SQLite verificada. Instâncias adicionais ficam em espera. A semântica do lock nativo ainda exige teste em MT5.

Corrupção, schema futuro, banco ocupado e falha de escrita não autorizam reset nem recriação silenciosa. O monitor pode continuar em memória com aviso explícito de incompletude, quando a titularidade está comprovada. Registros financeiros não são apagados por retenção automática. Falhas de capacidade ficam visíveis; não existe garantia de armazenamento ilimitado. Auditoria inicial do escritor limita varredura a 100.000 linhas ou 2 segundos; exceder recusa escrita e preserva a base. Episódios sem mudanças materiais não geram journal por segundo. O resumo verifica projeções e objetos lidos; não sela todas as páginas históricas. Captura limita inventário a 1024 sujeitos e é incremental; excesso ou timeout produz indisponibilidade. Backup JSON limita o corpo a 32 Mi caracteres nesta versão; exceder recusa exportação, preservando a base.

Exports ficam em `PersonalHistory/Exports/` com nomes distintos; arquivos existentes são preservados. IDs/tickets são texto, inclusive acima de 2^53. CSV possui colunas legíveis e payload canônico; texto potencialmente executável em planilhas recebe proteção. JSON preserva bytes em campos hexadecimais UTF-8, IDs numéricos como texto, SHA-256 por payload e integridade global. A reconstrução só aceita **novo arquivo em PersonalHistorySandbox**, nunca o banco real ou arquivo existente. Testes usam somente dados sintéticos.

Guarde o backup fora do terminal e preserve a pasta completa antes de qualquer manutenção. Exportação gravada não prova que exista uma segunda cópia independente. O arquivo contém dados financeiros e exige cuidado no compartilhamento.

## Aviso: solicitação versus recepção

Detecção, intenção, chamada da função e resultado conhecido são registrados separadamente. `Alert()` não retorna confirmação; `PlaySound()` não prova audição. Ausência de estágio após interrupção fica como entrega incerta. Não se afirma que o operador viu ou ouviu. [Alert](https://www.mql5.com/en/docs/common/alert) e [PlaySound](https://www.mql5.com/en/docs/common/playsound) não funcionam no Strategy Tester. Popup, som e inspeção visual exigem terminal isolado.

Atrasos entre prazo e solicitação são registrados; [OnTimer](https://www.mql5.com/en/docs/event_handlers/ontimer) não garante pontualidade. Callback `OnTradeTransaction` apenas sinaliza trabalho; captura, escrita e alertas acontecem no timer. Risco dos stops mantém sua prioridade anterior no orçamento do observador. Se ele consumir repetidamente o orçamento de 500 ms, o Histórico pode ser adiado; a cobertura e a contagem ficam desconhecidas. Medir essa concorrência no MT5 é requisito pendente, e esta versão não recebe aceite operacional por isso.

## Validação e retorno

Os critérios `HIS-AC01…20` foram congelados antes da implementação; três processos novos por caso preservam todas as tentativas. Os recibos descrevem separadamente núcleo, SQLite, exportação/recuperação, UI adaptada e escopo nativo. PASS local não constitui aprovação integral do caso nem garantia futura. Revisão independente não é autovalidação.

Compilação MQL5, arquivos `.ex5`, concorrência nativa, reinícios de MT5, popup/som e inspeção no gráfico permanecem `NOT_RUN` enquanto não houver ambiente nativo isolado. O script MQL5 sintético está nos fontes, sem alegação de execução nativa. Falhas preexistentes e de desenvolvimento permanecem nas evidências.

Rollback: interromper somente o observador candidato no ambiente de teste e voltar aos fontes/binários **1.17.0 RC2 comprovados**. Preservar toda a pasta PersonalHistory e seus backups; o componente anterior simplesmente não lê esse namespace. Não apagar bancos, locks ou registros como parte do rollback. Instalação operacional, publicação e integração ao site exigem revisão do candidato concreto e autorização própria. O site paralelo e o kit anterior permanecem preservados.

Estados normativos como `PENDING`, `NOT_HOMOLOGATED` e `BLOCKED` não são alterados por esta memória observacional.

## Roteiro de validação nativa pendente

Usar instalação MT5 isolada e conta de teste dedicada. Antes de executar, congelar os mesmos fontes, fixture e critérios; registrar conta/servidor de teste, versão do terminal, sistema, diretório de instalação e permissões. Compilar indicador, observador e script sintético no MetaEditor, conservando logs completos, avisos, erros e hashes dos `.mq5/.mqh/.ex5`. Um binário herdado ou compilado de outra revisão não comprova este candidato.

Executar os 20 casos conforme o fixture, conservando também falhas e interrupções. Para os percursos críticos abaixo, abrir três sessões novas de terminal; não reutilizar um resultado como três tentativas. Registrar início/fim, fonte/binário, sujeito/ticket como texto, banco antes/depois, logs, captura da interface e resultado por critério. O julgador deve ser diferente do autor do módulo.

| Percurso crítico | Evidência necessária no terminal |
|---|---|
| Primeira ausência e reaviso | SL efetivamente zero, posição e pendente, janela/som fora do Tester, horário devido/solicitado e atraso real; fechar a janela não resolve o episódio. |
| Stop colocado/retirado e execução parcial | Resolvido e novo episódio distintos, identidade estável da posição e vínculo da pendente somente com deal demonstrado. |
| Desconexão, reinício e conta alterada | Revalidação, nenhuma fila atrasada, cobertura explícita, sem aviso da conta anterior nem rótulo atual desatualizado. |
| Concorrência e disputa de orçamento | Duas instâncias, escritor único, ausência de duplicação; Stop Risk sob carga sem ocultar atraso/desconhecimento do Histórico. |
| Pico e fotografia | Comparação sem arredondar, equity em queda, Current/Estimated separados, fotografia idêntica à captura e dados inválidos indisponíveis. |
| Banco ocupado, corrompido ou futuro | Arquivo preservado, escrita recusada/incompleta visível; nenhuma recriação silenciosa. Fazer corrupção apenas em cópia sintética. |
| Interrupção durante aviso | INTENT/CALLED/RESULT separados; entrega incerta conservada após recuperação, sem alegar recepção humana. |
| Cockpit e exportação | Acompanhamento com janela fechada, consulta histórica sem trocar conta, pedido de exportação mantém a conta do clique, preferências preservadas. |
| Backup e reconstrução | CSV com IDs exatos e JSON com integridade; reconstrução exclusivamente em novo sandbox e comparação independente das linhas. |

Qualquer critério obrigatório violado impede aprovação do escopo. Resultado inconclusivo não vira PASS. Três rodadas sem aprendizado novo exigem diagnóstico antes de novas tentativas. Não instalar na conta operacional nem publicar com base apenas nos testes locais. A documentação primária utilizada também inclui [propriedades das posições](https://www.mql5.com/en/docs/constants/tradingconstants/positionproperties), [propriedades das ordens](https://www.mql5.com/en/docs/constants/tradingconstants/orderproperties) e [transações SQLite](https://www.mql5.com/en/docs/database/databasetransactionbegin).
