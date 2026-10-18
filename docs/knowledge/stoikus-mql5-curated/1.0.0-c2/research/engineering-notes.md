# Notas de pesquisa — arquitetura, eventos, persistência e testes

Data da pesquisa: 2026-10-15. Escopo editorial exclusivo: capítulos 01, 03, 05 e 07. Pesquisa informativa; nenhuma alteração produtiva MQL5, fórmula, schema, banco, instalação ou Git. Os caminhos de produto abaixo são relativos à raiz do repositório. A leitura do estado atual foi estática; compilação e execução nativas: **NOT_RUN**.

## Método e limite central

Os PDFs fornecidos são as fontes primárias técnicas. As primeiras consultas usaram `corpus/{TRD,REF}/pages.jsonl`; para páginas TRD ainda não extraídas, o Python incluído no runtime abriu o PDF pelo `PdfReader` e imprimiu páginas físicas específicas. Quando a extração rápida ficou pronta, as leituras seguintes usaram `corpus-fast/TRD/pages.jsonl` e `corpus-fast/REF/pages.jsonl`. A página indicada é física, começando em 1. Não se inferiu leitura de extração concluída.

Algumas saídas longas foram truncadas. Os intervalos essenciais foram consultados novamente em lotes menores: TRD 619–622, 413–415, 465–466, 482–485, 488–491, 499 e 623. A primeira saída truncada não é usada como prova de leitura integral dos intervalos omitidos. As páginas 483–484 foram repetidas pela extração rápida para recuperar completamente o trecho. Esta nota registra leitura técnica das páginas e dos excertos declarados; não registra inspeção visual de todas as páginas dos PDFs.

**Não foi feita, por este pesquisador, leitura integral das 2.047 páginas TRD nem das 7.284 páginas REF.** A expansão final percorreu aberturas dos capítulos de segundo nível: excertos iniciais de até 1.250 caracteres para fundamentos/OOP/alguns capítulos e até 2.000 para as famílias restantes. Isso produz orientação temática parcial, não leitura dos exemplos internos, filhos ou de todos os contratos. A matriz JSON preserva essa distinção e mantém os filhos não examinados com `NOT_REVIEWED_BY_THIS_WORKER`.

## Leitura aprofundada e uso nos capítulos

| Fonte e páginas efetivamente consultadas | Conteúdo compreendido | Aplicação e lacuna |
|---|---|---|
| TRD 66–67, 74–75 | Escopo, duração e estáticas locais; reduzir visibilidade do estado | Cap.01: cursor persistente entre callbacks; não representa estudo de todo 2.3 |
| TRD 141–143 | Valor, referência, `const`, alterações observáveis pelo chamador e arrays | Cap.01: fronteiras de leitura e saída; não abrange todas as funções/overloads |
| TRD 154 | Inclusão textual e resolução de caminhos | Cap.01 e07: conjunto exato de dependências; não cobre todo preprocessor |
| TRD 180–183 | Abstração, encapsulação, herança, polimorfismo e composição/agregação | Cap.01: interfaces e propriedade; 3.2.5 continua em página seguinte, portanto parcial |
| TRD 404–407, 412–415 | Sandbox, texto/binário, representação, abertura, truncamento, posição e compartilhamento | Cap.05: flags e identidade; exemplos de 416–424 não examinados integralmente |
| TRD 465–466 | Buffers, flush e exemplo de dois processos | Cap.05: flush não comprova publicação completa; resto do exemplo não lido |
| TRD 482–485, 488–491, 499 | Globais do terminal, `double`, nomes, duração, temporárias, corrida check/create e CAS | Cap.05: namespace e coordenação; exemplos longos de 492–498 não lidos |
| TRD 612–628 | Tipos de programa, threads, tabela de callbacks, fila, ciclo de vida e reinicialização | Cap.01/03: estudo aprofundado do núcleo 5.1.1–5.1.6; 5.1.6 começa no fim628 e continua em629, logo esse filho é parcial |
| TRD 631–636 | Scripts e serviços, entradas, diálogos, restauração e exemplo de serviço de contas | Cap.03: utilitário pontual versus produtor; o exemplo de criptografia é descrito como exemplo do livro, não recomendado como política de segurança |
| TRD 837–838, 847–848 | Um timer nativo por programa, fila, timers lógicos, dependentes sem timer, milissegundos | Cap.03: callback cooperativo; classes e exemplos intermediários839–846 não lidos |
| TRD 1450–1453,1458–1460 | Sandbox de agentes, ticks reais/gerados/OHLC/abertura, tempo e visualização | Cap.07: ambiente de prova e seus limites; detector de modo1454–1457 não lido |
| TRD 1478–1479 | `OnTester`, critério customizado e seleção pelo usuário | Cap.07: otimização não substitui critérios binários; restante do exemplo1480–1488 não lido |
| TRD 1496–1497 | Eventos de controle da otimização, instância de serviço e frames | Pesquisa de contexto: distinguir passagem única e otimização; não implementação de frames |
| TRD 1506–1507 | Diretivas do tester e arquivos presentes na compilação | Cap.07: fixture ausente não corrigida por aparecer depois; resto1508–1509 não lido |
| TRD 1511–1514 | Ocultação de indicadores e emulação de depósito/saque | Contexto de teste; exemplo de carry trade não é proposta nem norma JPW; nenhuma negociação executada |
| TRD 1558–1561 | Cálculo matemático, depuração, profiling e funções/eventos limitados no tester | Cap.07: ausência de interação real e diferença de binários; apenas página1558 finaliza exemplo anterior |
| TRD 1839–1841,1870–1871,1885–1886,1893–1896 | SQLite, handles, binding, ORM parcial e transações | Cap.05: unidades de alteração e retorno; não estudo completo de SQL/ORM |
| TRD 1775,1941,2046–2047 | Contexto de transformações, organização de projetos e conclusão editorial | Ampliar mapa temático sem habilitar recurso futuro; conclusão não é evidência funcional |

## REF: páginas de API verificadas

| Família | Páginas lidas | Compreensão e limite |
|---|---|---|
| Program Running | 1042–1048 | Threads, eventos, restrições, reinicialização e tipos; usado no cap.01/03 |
| OnInit/OnDeinit | 2082–2086 | Retornos, EA descarregado versus indicador inoperante, motivos e exemplo parcial; 2087 não lida |
| OnTimer | 2098 | Coalescência, um timer e resolução condicionada; exemplo continua depois |
| OnTradeTransaction | 2106–2108 | Solicitação/result por tipo, ordem não garantida, fila1024, exemplo parcial; 2109–2111 não lidas |
| OnTester | 2122–2123 | Contrato e começo do exemplo; não reproduz código de negociação |
| GlobalVariableDel/Get | 2630–2633 | Expiração, falha versus zero e overload com sucesso explícito |
| GlobalVariablesFlush/Temp/SetOnCondition | 2639–2644 | Temporárias não persistem, CAS atômico e exemplo parcial; 2645–2647 não lidas |
| FileOpen | 2665–2667 | Sandbox, flags, encoding, handle e exemplo completo dessas páginas |
| FileFlush | 2676–2677 | Buffer e custo de frequência; não prova transação multirregistro |
| EventSetTimer | 3189 | Retorno, um timer e coalescência |
| DatabaseOpen | 3241–3242 | Flags, temporário, memória, retorno e caminhos |
| DatabaseTransactionBegin/Commit/Rollback | 3302,3307–3308 | Retornos, confirmação e desfazimento; exemplo3303–3306 não lido |

As consultas foram aos PDFs locais com metadados 2026; este pesquisador não abriu novas URLs. Verificações web atuais feitas por outros integrantes, se integradas, devem conservar seu próprio registro. Não há URLs alegadas como visitadas nesta nota.

## Varredura semântica parcial das demais aberturas TRD

As linhas abaixo descrevem somente o material exibido nos excertos, com relevância editorial e lacuna explícita. Não propagam leitura aos filhos.

- **1.1–1.2, p16/p19:** edição/compilação gera binário e Wizard inicia um script. Relevância: separar preparação e execução; não foi repetido o tutorial visual.
- **1.3–1.4, p22/p24:** blocos, função e exemplo `OnStart`/log. Relevância: entrada de script e Experts como saída comum; restante do tutorial não revisado.
- **1.5–1.7, p26/p28/p29:** funções próprias, tipos, identificadores e arrays indexados desde zero. Relevância: contratos dos exemplos; exemplos internos não estudados integralmente.
- **1.8–1.9, p31/p33:** entradas no escopo apropriado e diferença entre erros de compilação e runtime. Relevância: plano de prova por camada; detalhes de depuração iniciais não esgotados.
- **1.10–1.12, p37/p39/p41:** saídas no gráfico/log, formatação e recapitulação. Relevância: logs não são painel e aparência não muda semântica; imagens não auditadas.
- **2.1–2.2, p43/p44:** identificadores e significado/tamanho dos tipos. Relevância: não transportar identidades e quantidades em tipos escolhidos só por conveniência; subtipos permanecem fora desta varredura.
- **2.3–2.4, p64/p81:** mapa de declaração/duração e arrays. Relevância: estados entre fatias; aprofundamento somente nos intervalos já declarados.
- **2.5–2.7, p88/p108/p113:** expressões, conversões e statements de controle. Relevância: revisar cálculo e fluxo em sua própria semântica; exemplos e prioridades não receberam cobertura integral.
- **2.8–2.9, p137/p153:** funções como entradas e interfaces, preprocessor anterior à compilação. Relevância: unit de compilação; somente referências/`include` aprofundados.
- **3.1–3.3, p166/p180/p251:** estruturas, classes e templates como organização/reuso. Relevância: estruturas para fotografias e composição; templates completos não examinados.
- **4.1, p281:** conversões explícitas para strings, datas, cores e enums. Relevância: exportação e detalhes; não valida fórmulas por formatação.
- **4.2, p304:** famílias de manipulação de strings e retorno de status por API. Relevância: verificar retorno concreto, sem convenção universal presumida.
- **4.3, p335:** alocação de arrays, operações comuns e indexação. Relevância: falha de alocação/ordem temporal; contratos de cada função não lidos nesta abertura.
- **4.4, p387:** funções matemáticas e propagação de NaN. Relevância: disponibilidade numérica exige validação; não nova regra financeira.
- **4.7, p500:** funções temporais e decomposição de datetime. Relevância: diferenciar calendário, servidor e duração; DST interno não lido aqui.
- **4.8, p513:** entrada/saída, mensagens e entradas que reinicializam. Relevância: motivo de evento e canais de log; não prova alerta nativo.
- **4.9, p529:** propriedades de terminal/programa e permissões combinadas. Relevância: contexto explícito dos ensaios; não habilitar DLL ou negociação.
- **4.10, p574:** matrizes/vetores para álgebra, ML e gráficos. Relevância: pesquisa futura, sem ML atual inferido; métodos internos não auditados.
- **5.3, p637:** séries e direções de indexação sem mudar disposição física. Relevância: leitura temporal e barra atual/fechada; cópias não aprofundadas aqui.
- **5.4, p675:** indicadores como cálculo/visualização, buffers e possibilidade de objetos/UI sem plots. Relevância direta a Conta e NoCuda; detalhes nativos ficam com pesquisa específica.
- **5.5, p762:** instâncias e buffers de indicadores consumidos por programas. Relevância: indicador anexado versus dependente; handles e prontidão exigem consulta adicional.
- **5.7, p849:** gráficos, janelas/subjanelas e índices que mudam com remoção. Relevância: não tratar índice de subjanela como identidade permanente.
- **5.8, p921:** objetos gráficos por gráfico, estudos e controles. Relevância a NoCuda e interface; tabela de propriedades não integralmente lida.
- **5.9, p1020:** eventos de tamanho, teclas, mouse e objetos. Relevância: provas interativas distintas do tester; catálogo de códigos não integralmente lido.
- **6.1, p1049:** símbolos, Market Watch e dados do broker/customizados. Relevância: identidade e disponibilidade; não mudar seleção em conta real.
- **6.2, p1135:** livro de ofertas agregado por níveis. Relevância contextual; não é fonte de equivalência para histórico completo nem recurso Stoikus comprovado.
- **6.3, p1155:** propriedades de conta fornecidas pelo servidor e uma conta ativa por terminal. Relevância: invalidação ao trocar contexto; APIs internas não esgotadas.
- **6.4, p1169:** ordens/deals/posições e mecanismos para EAs. Relevância: compreender eventos, sem conferir negociação ao Monitor; conteúdo extenso restante não estudado por este trabalhador.
- **7.1, p1562:** recursos incorporados e imagens dinâmicas. Relevância: recursos fazem parte da compilação; canvas e alfa detalhados por outro pesquisador.
- **7.2, p1624:** símbolos locais customizados e história importada. Relevância: fixtures futuras; nenhum símbolo criado.
- **7.3, p1689:** calendário e tempo do servidor. Relevância: integração futura depende de origem/fuso; sem calendário atual presumido.
- **7.4, p1774–1775:** distinção entre cifragem, hash e transformações. Relevância: hash identifica bytes, não homologa conteúdo; texto do livro não adotado como projeto criptográfico.
- **7.5, p1795:** funções de envio, WebRequest e sockets, permissões de destino. Relevância: limites do tester e de comunicação; nenhuma mensagem enviada.
- **7.6:** abertura e trechos aprofundados já relacionados. SQL e ORM completos continuam parciais.
- **7.7, p1910:** importação/exportação binária e ligação por protótipos. Relevância: dependência externa precisa identidade; nenhuma DLL habilitada.
- **7.8, p1940–1941:** projeto como conjunto de fontes, recursos e bibliotecas ao longo do ciclo. Relevância: manifesto do pacote, sem migração para novo formato de projeto.
- **7.9, p1998:** pacote Python como integração entre processos com o terminal. Relevância: pesquisa futura; não há Python/ML ativado no Stoikus por esta pesquisa.
- **7.10, p2038:** OpenCL exige tarefa divisível e não acelera automaticamente passagem sequencial de mercado. Relevância: medir antes de propor GPU; nenhuma promessa de ganho.

## Confronto das fontes e estado do produto

Há divergência de formulação interna: TRD p490 descreve thread de indicadores pela combinação símbolo/período; TRD p616 e REF p1042 descrevem compartilhamento por símbolo. Os capítulos usam a formulação da referência específica REF1042 e não propagam a afirmação de p490. Essa opção é documentada e não prova comportamento observado no terminal atual.

Foram lidos o README do módulo, o arquivo principal do Monitor no trecho de inicialização/callbacks/agendamento, os trechos localizados de locks/leases dos runtimes e o mapa documental do harness. Busca de texto nos runtimes não foi registrada como leitura integral desses arquivos. As descrições do fluxo têm esse alcance estático. A fonte do estado atual é `mt5/jpw-alavancagem-atual/README.md`; o harness histórico é `mt5/jpw-alavancagem-atual/harness/REPOSITORY_INTEGRATION.md`; o contrato de desenho é `harness/contracts/ENG-AC01-12.json` nessa pasta.

O mapa do harness declara R2 com 36 tentativas, 25 PASS / 7 FAIL / 4 INCONCLUSIVE e resultado FAIL; R5 restrito não substitui suíte inteira. A leitura foi documental, não nova execução. Todos esses números permanecem históricos. Regras financeiras JPW não foram reconstruídas dos exemplos do livro nem adicionadas aos capítulos.
