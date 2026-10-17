# Stoikus Engenharia em MQL5 e programação com IA

Manual técnico avançado elaborado para o JP Wealth. Revisão editorial 1.0.0 candidata. Harness 0.1.0 CANDIDATE. Data de referência 15 de outubro de 2026.

## Tese e propósito

O desenvolvimento confiável do Stoikus exige contratos explícitos, controle do ciclo de vida, integridade dos dados e evidências reproduzíveis. A programação com IA deve operar dentro dessas condições. Essa proposição orienta o estudo: cada mecanismo da plataforma é relacionado às decisões que um engenheiro precisa justificar, aos erros que pode demonstrar e às provas que faltam para aceitar uma alteração.

O objeto principal é a suíte atual, composta pelo EA Monitor, indicadores Conta e NoCuda e script Abrir Painéis. O Monitor é um programa observacional dirigido por eventos; sua classificação como EA não o obriga a enviar ordens. O Supervisor é separado e possui responsabilidades e permissões próprias. Redes neurais e execução adicional pertencem a propostas de evolução. O estudo não instala componentes nem altera regras financeiras do produto.

Os três livros fornecidos constituem o corpus primário: MQL5 Reference, MQL5 Programming for Traders e Neural Networks for Algorithmic Trading with MQL5. As edições locais totalizam 10.021 páginas. Os respectivos hashes, o catálogo de 4.821 entradas de sumário e os registros de leitura ficam nos anexos de pesquisa. Consulta oficial online é identificada à parte, porque uma página atual pode divergir da edição PDF e um exemplo não comprova comportamento em qualquer build futuro do terminal.

A leitura crítica conserva quatro origens distintas. Contratos da plataforma descrevem tipos, APIs e condições documentadas pela MetaQuotes. O código examinado demonstra comportamento observado de uma revisão do Stoikus. Regras do JP Wealth dependem de suas fontes competentes; um trecho de programação não lhes confere vigência. Propostas deste manual são recomendações de engenharia para avaliação. Misturar essas origens transforma inferência em obrigação e dificulta a revisão.

Este manual organiza a síntese por problemas de engenharia. Os anexos permitem retornar ao livro, à seção e ao intervalo consultado. Uma página extraída não é automaticamente uma página analisada. A matriz separa extração, leitura semântica, consulta parcial e inspeção visual; eventuais lacunas ficam explícitas e impedem alegação de revisão integral do corpus. O texto pode ser usado como guia técnico, mas sua extensão não comprova a cobertura das fontes.

## Como utilizar o manual e o kit

O leitor deve começar pela arquitetura e pelos contratos, identificar o módulo envolvido na sua tarefa e consultar os capítulos correspondentes. Antes de uma alteração, o kit pede uma especificação que fixe saída, limites, unidade, contexto, ownership, comportamento de falha e prova esperada. A implementação produz um delta pequeno e uma contraprova demonstrável. Um revisor separado verifica os resultados com os critérios previamente definidos.

Exemplos neste documento são originais e sintéticos, salvo atribuição expressa. Trechos MQL5 não foram compilados nesta entrega; diagramas representam relações conceituais e não eventos nativos observados. Exemplos do livro discutidos criticamente permanecem identificados por referência. O leitor encontra estados separados para fonte, bancada, compilação, terminal, instalação e aceite. Não deve transferir o resultado de um deles para outro.

O Markdown é a fonte editorial. Word e PDF são derivados conferidos, com equações nativas editáveis no Word. O kit conserva sua própria identidade e seu resultado estrutural não significa adoção. Os resultados históricos do harness GENETRIX permanecem históricos; o piloto do novo candidato tem contrato e recibos próprios, descritos no relatório de validação que acompanha a entrega.
