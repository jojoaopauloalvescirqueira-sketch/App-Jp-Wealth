# Leitura analítica das famílias da referência

Análise das aberturas e contratos de família, com consultas aprofundadas registradas nos capítulos e notas. Não propaga leitura para todos os métodos descendentes nem declara leitura integral de 7.284 páginas.

## REF-0002 Language Basics

Página de abertura consultada 77; família 77–318. Tipos, funções, lifetime e namespaces estruturam contratos; semântica de C++ não pode ser transferida sem conferir MQL5.

## REF-0085 Constants, Enumerations and Structures

Página de abertura consultada 319; família 319–1040. Constantes têm domínios funcionais e estruturas definem mensagens; conta, trade e gráfico não compartilham semântica apenas por representarem inteiros.

## REF-0199 MQL5 programs

Página de abertura consultada 1041; família 1041–1096. EA, indicador, script, serviço e biblioteca têm handlers e persistência de execução diferentes; o limite de um EA por gráfico fundamenta dois gráficos do Stoikus.

## REF-0207 Predefined Variables

Página de abertura consultada 1097; família 1097–1108. Símbolo e período descrevem o gráfico atual; não devem substituir identidade explícita de uma coleção multicurrency.

## REF-0218 Common Functions

Página de abertura consultada 1109; família 1109–1192. Recursos, logs, temporizadores e erros são mecanismos técnicos; sucesso da chamada não prova aceite do resultado financeiro.

## REF-0251 Array Functions

Página de abertura consultada 1193; família 1193–1286. Indexação começa em zero; resize e cópia têm restrições. Precisão, ownership e arrays com membros complexos exigem contratos específicos.

## REF-0277 Matrix and Vector Methods

Página de abertura consultada 1287; família 1287–1878. Dimensões, tipo e orientação resultam do contexto; memória dinâmica e interfaces de buffer exigem shapes explícitos. Uso no produto seria evolução.

## REF-0566 Conversion Functions

Página de abertura consultada 1879; família 1879–1924. Conversão de representação, arredondamento e conversão monetária são problemas distintos. ARGB e texto têm contratos próprios.

## REF-0588 Math Functions

Página de abertura consultada 1925; família 1925–2014. Operações podem ser elementwise em arrays matemáticos; finitude e domínio matemático antecedem interpretação financeira.

## REF-0621 String Functions

Página de abertura consultada 2015; família 2015–2043. Comparação e índices representam texto; número de caracteres não mede pixels. Serialização e unidade não devem depender de legenda traduzida.

## REF-0641 Date and Time

Página de abertura consultada 2044; família 2044–2057. Tempo de cotação, relógio civil e duração monotônica têm papéis diferentes e precisam ser identificados nos registros.

## REF-0650 Account Information

Página de abertura consultada 2058; família 2058–2062. Propriedades são valores da conta corrente; snapshot contextual deve verificar identidade e atualidade.

## REF-0654 Checkup

Página de abertura consultada 2063; família 2063–2076. Verificações de ambiente e erro são instrumentação; registrar motivo sem atribuir causa que o retorno não demonstra.

## REF-0667 Event Handling

Página de abertura consultada 2077; família 2077–2137. Assinatura exata seleciona handler. Fila e orçamento de execução moldam aquisição cooperativa e recuperação.

## REF-0682 Market Info

Página de abertura consultada 2138; família 2138–2164. Informação de símbolo precisa de existência, seleção e sincronização; usar um tick evita misturar campos de chamadas independentes.

## REF-0698 Economic Calendar

Página de abertura consultada 2165; família 2165–2195. APIs usam timezone de servidor e trazem eventos; o calendário é pesquisa adicional, não condição já implementada no Monitor.

## REF-0709 Timeseries and Indicators Access

Página de abertura consultada 2196; família 2196–2297. Retorno de quantidade e preparação assíncrona obrigam validar janela completa, ordem e barra ainda aberta.

## REF-0744 Custom Symbols

Página de abertura consultada 2298; família 2298–2373. Permitem construir fontes controladas em terminal isolado. Metadados artificiais não validam automaticamente um contrato real de corretora.

## REF-0760 Chart Operations

Página de abertura consultada 2374; família 2374–2440. Comandos são enfileirados; retornos aceitos e aparência final são provas distintas. Preservar interação temporariamente alterada.

## REF-0793 Trade Functions

Página de abertura consultada 2441; família 2441–2546. Ordem, negócio e posição são entidades distintas. Leitura contábil precisa reconciliação; envio de ordens pertence a executor separado.

## REF-0827 Trade Signals

Página de abertura consultada 2547; família 2547–2559. Gerência de cópia é capacidade da plataforma; não é aprendizado neural nem autorização para assinatura/cópia nesta entrega.

## REF-0840 Network Functions

Página de abertura consultada 2560; família 2560–2623. Sockets/WebRequest dependem de permissões configuradas pelo usuário. Não acrescentar rede ao Monitor por conveniência do harness.

## REF-0859 Global Variables of the Terminal

Página de abertura consultada 2624; família 2624–2650. Globais do terminal diferem do escopo global do programa e são compartilhadas entre aplicações; lifetime documentado não equivale a banco de auditoria.

## REF-0871 File Functions

Página de abertura consultada 2651; família 2651–2762. Sandbox e diretório Common são fronteiras distintas; formatar path não concede ownership nem permissão para sobrescrever dados.

## REF-0912 Custom Indicators

Página de abertura consultada 2763; família 2763–2894. Buffers/plots pertencem a indicadores. Painel por objetos pode ser indicador analítico; não implica execução de trades.

## REF-0941 Object Functions

Página de abertura consultada 2895; família 2895–2967. Propriedades são comandos de gráfico. Ownership, geometria e hit targets precisam de testes específicos além de pixels.

## REF-0960 Technical Indicators

Página de abertura consultada 2968; família 2968–3174. Handles representam cálculos cacheados; criar handle não garante buffer pronto. Aquisição/liberação precisam de ciclo de vida.

## REF-1000 Working with Optimization Results

Página de abertura consultada 3175; família 3175–3186. Frames agregam resultados de agentes. Ordem de chegada e optimização não justificam seleção pós-hoc do melhor resultado sem trilha.

## REF-1008 Working with Events

Página de abertura consultada 3187; família 3187–3196. Timer e eventos customizados organizam trabalho; pedir frequência alta não garante execução com periodicidade rígida.

## REF-1013 Working with OpenCL

Página de abertura consultada 3197; família 3197–3237. Benefício depende de dispositivo, precisão e tamanho do trabalho. Disponibilidade de GPU e double devem ser testadas antes de assumir aceleração.

## REF-1033 Working with databases

Página de abertura consultada 3238; família 3238–3317. SQLite oferece transações e consultas. Integridade financeira depende também de esquema, ownership, snapshot e auditoria de aplicação.

## REF-1060 Working with DirectX

Página de abertura consultada 3318; família 3318–3346. API 3D depende de capacidades gráficas; não há benefício demonstrado para o painel informativo atual. Classificar como referência, sem ampliar dependências.

## REF-1083 Python Integration

Página de abertura consultada 3347; família 3347–3437. Integração consulta terminal por comunicação entre processos. Uma bancada Python independente não é execução MQL5 ou inferência neural dentro do Monitor.

## REF-1116 ONNX models

Página de abertura consultada 3438; família 3438–3483. Modelo e shapes têm sessão e tipos próprios. Carga e execução precisam de identidade e erro explícitos; converter modelo não valida a previsão.

## REF-1136 Standard Library

Página de abertura consultada 3484; família 3484–7007. Wrappers e classes organizam acesso, mas seus métodos não eliminam contratos das APIs subjacentes. Versão da biblioteca faz parte das dependências.

## REF-4126 Moving from MQL4

Página de abertura consultada 7008; família 7008–7010. Migração exige revisar handlers, inicialização, índices e operações de negociação. Renomear extensões não migra semântica.

## REF-4127 List of MQL5 Functions

Página de abertura consultada 7011; família 7011–7044. Índice alfabético auxilia localização e identificação de família; não é uma explicação completa dos parâmetros ou prova de execução.

## REF-4128 List of MQL5 Constants

Página de abertura consultada 7045; família 7045–7284. Catálogo alfabético não demonstra regra de domínio. Domínio da constante e API correspondente precisam de consulta antes de uso.
