Parecer independente: **REVIEW_PASS no escopo de código, contratos e distribuição de fontes, com MT5 compile/runtime NOT_RUN**. Não encontrei defeito bloqueante nas correções examinadas. A solução atende à clareza pretendida para identificar os componentes, configurar as Entradas e abrir Conta + NoCuda. Este parecer não comprova funcionamento nativo, instalação, aceite humano ou publicação.

Revisão somente leitura do candidate em `/private/tmp/jpw-stoikus-renaming-20261012`, vinculada ao freeze R3 e aos bytes abaixo. Não li o mapeamento privado nem pareceres/recibos de outros críticos. Escrevi apenas recibos próprios e fixtures temporárias de auditoria, sem editar software, Git ou instalar ferramentas.

| Artefato | Arquivos / programas MQ5 | Bytes | SHA-256 |
| --- | --- | --- | --- |
| SDK 1.22.1 | 135 / 34 | 773801 | `03ccb37824175511108b36e9abb5c9fa0dc28d89a338caea1dc7bf02508b9cae` |
| Uso diário 1.22.1 | 82 / 4 | 441516 | `5b2c7ca40736dda976fe97a91a2677d190eb1ccfdf9527703fd471ee702a11e5` |

Os dois ZIPs têm CRC íntegro, nomes únicos, caminhos seguros e igualdade byte a byte com os fontes correspondentes. O SDK corresponde exatamente aos 133 membros históricos da 1.22.0 mais o abridor e o guia. Recalculei separadamente o fechamento de dependências do pacote diário: quatro programas, 69 includes, oito imagens e o guia. O pacote diário não contém Tests, laboratório, Supervisor, EAs legados nem EX5; não há chamadas OrderSend/OrderSendAsync em seu fechamento runtime. Os históricos GENETRIX 1.21.2 e Stoikus 1.22.0 conservam seus tamanhos e hashes literais anteriores.

A revisão do abridor encontrou os seguintes controles coerentes com o objetivo:

- `JPW_Stoikus_Abrir_Paineis.mq5:24–57` percorre todas as janelas; falhas de descoberta impedem a criação de handles. `:122–136` verifica ambos os papéis antes de iniciar qualquer um.
- `:80–82` usa caminhos enraizados em `MQL5`, com `\\Indicators\\JPWealth`, e o símbolo/período do gráfico alvo. A resolução enraizada evita a busca anterior na pasta do chamador; omitir parâmetros usa os defaults dos indicadores. A semântica está documentada em [iCustom](https://www.mql5.com/en/docs/indicators/icustom).
- `:68–74` preserva os indicadores reconhecidos, inclusive legados e cópias em sub-janelas. Informa o nome encontrado, a janela e a necessidade de conferir versão/dados. `:141–147` diz explicitamente que listagem não confirma saúde ou compatibilidade.
- `:93–119` distingue criação, anexação e confirmação da listagem. Uma falha parcial conserva o componente que abriu e permite repetir a abertura do ausente. As condições nativas de símbolo/período e o retorno de sucesso da anexação estão em [ChartIndicatorAdd](https://www.mql5.com/en/docs/chart_operations/chartindicatoradd).
- `:100–106` preserva o aviso de liberação e o código de erro na mensagem do papel correspondente; não apaga indicadores por nome. A documentação de [IndicatorRelease](https://www.mql5.com/en/docs/series/indicatorrelease) distingue remoção do handle da eliminação do bloco de cálculo ainda referenciado. A implementação da propriedade de referências no teste é simulada e precisa de confirmação nativa.

Comparei os inputs diretamente com o ZIP imutável 1.22.0, sem usar o array do teste como oráculo: os 20 nomes, tipos, ordem e valores padrão permanecem idênticos (Monitor 3, Conta 12, NoCuda 5). Todos têm rótulos explicativos em português e agrupamento. O maior comentário de Entrada tem 62 caracteres, abaixo do limite de 63 documentado em [Input Variables](https://www.mql5.com/en/docs/basis/variables/inputvariables). Os comentários acrescentam unidades, intervalos e significado de zero/vazio. Os erros de inicialização oferecem a ação de correção em Entradas, Ctrl+I ou Diário.

Todas as 13 bibliotecas `JPW_NoCuda_*.mqh` e os cinco núcleos `JPW_Alavancagem_*Core.mqh` conferidos são byte-identical à 1.22.0; a lista completa está no recibo independente. A comparação exaustiva dos membros MQL históricos mostra alterações somente nos três entrypoints Monitor/Conta/NoCuda e no cabeçalho de versão. O cabeçalho conserva cálculo 1.9.0 e o indicador NoCuda conserva `#property version "1.30"`. Não identifiquei mudança de matemática ou de núcleo NoCuda.

Consultei os trechos pertinentes dos fontes primários completos locais do Position Sizer (`reference-full-source.mq5`, grupos de Inputs e OnInit; `reference-full-portuguese.mqh`, grupos e rótulos). A referência usa agrupamento funcional e nomes legíveis em português. O candidate aplica esse princípio de clareza às 20 Entradas sem ampliar seu contrato. O guia acrescenta um caminho curto: dois gráficos, três componentes permanentes, um script pontual e quatro compilações. Distingue F7 do MetaEditor e F7 do EA, lista de indicadores e atividade nativa, e ZIP de uso versus SDK. Não afirmo equivalência visual ou operacional completa com o Position Sizer.

Executei os quatro focais com `/private/tmp/jpw-quality-audit-20261012-01a131dc/runtime/bin/python`, recebendo exit 0 em todos: `stoikus_startup_test.py` (29 cenários), `stoikus_daily_package_test.py`, `leverage_package_test.py` e `stoikus_download_test.py`. A captura de hashes antes/depois confirma que os fontes, ferramentas e artefatos auditados não foram alterados pelos testes. O downloader foi exercitado com SHA-256 real, incluindo online/offline, metadados inválidos, corrupção de tamanho/hash, botão ausente e entradas duplicadas do mesmo papel. DOM/rede continuam sendo seams.

Também executei um auditor independente de inputs históricos, inventários e dependências e quatro mutantes temporários do abridor contra o teste entregue:

| Mutante próprio | Resultado observado |
| --- | --- |
| Trocar iCustom enraizado por relativo | Rejeitado em `caller_shadow` |
| Ignorar a detecção de instância presente | Rejeitado em `inactive_listed`, por alteração indevida de objetos/preferências |
| Retirar a frase que separa listagem de saúde | Rejeitado em `inactive_listed` |
| Retirar o aviso de release do resultado visível | Rejeitado em `release_fail` |

Houve uma falha inicial no meu leitor independente de dependências: ele não normalizava barras duplicadas dos literais `#resource`. Corrigi somente esse leitor de auditoria e repeti a execução com PASS. Não foi defeito do produto.

**Limite material:** o teste de abertura compila o fluxo de decisões MQL como C++ e substitui APIs MT5 por seams. Ele não executa os verdadeiros OnInit/OnDeinit dos indicadores, timers, desenho, DPI, I/O de conta, ciclo de vida dos gráficos ou referência nativa dos handles. Nome curto reconhecido não prova versão exata nem handlers ativos. A compilação MetaEditor e a interação MT5 dos mesmos bytes permanecem **NOT_RUN**. O ensaio nativo isolado precisa confirmar abertura, repetição, falhas, permanência dos indicadores após encerramento do script e a integridade de estudos/preferências. A evidência entregue não elimina essa etapa.

Recibos próprios: `independent-audit.json`, `independent_audit.py`, `startup-official-final.json` e `commands-official-final.json`, todos na mesma pasta deste parecer.
