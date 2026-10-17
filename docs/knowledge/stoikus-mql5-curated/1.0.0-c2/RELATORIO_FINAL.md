# Relatório de entrega e validação

**Entrega documental candidata:** manual editorial 1.0.0 e Stoikus MQL5 AI Harness 0.1.0 CANDIDATE, revisão R3. Data: 15 de outubro de 2026. Base examinada: Stoikus 1.23.0/MQL 1.230, cálculo 1.9.0. O kit permanece NOT_ADOPTED.

## Resultado entregue

O manual argumenta que desenvolvimento confiável exige contratos explícitos, controle do ciclo de vida, integridade e evidência reproduzível. Relaciona esses fundamentos ao EA Monitor observacional, Conta, NoCuda e Abrir Painéis. Propõe evolução sem transformar estudo em alteração produtiva. Programação assistida por IA e uma eventual rede neural no terminal são problemas distintos.

O Markdown agregado tem 25.100 unidades na contagem por expressão regular de palavras; retirando blocos de código e equações, a contagem por espaços é 23.976. Isso atende ao intervalo editorial aproximado de 20–30 mil palavras, sem contar os anexos. Word e PDF resultam das mesmas entradas de `chapters/` e `editorial/`; o PDF tem 56 páginas. `COMECE_AQUI.md` orienta leitura, uso e reprodução.

O kit possui 45 arquivos operacionais, com entrada curta, mapa arquitetural, contexto por tarefa, modelos de contrato/teste/decisão/entrega, prompts de diagnóstico/construção/revisão/julgamento, receitas, fontes identificadas e 12 casos com projeções reservadas ao construtor. A cópia `harness-candidato/` conserva os bytes de `harness-next-r3/`, caminho usado nos ensaios. O manifesto SHA-256 congelado é `004f96cc9a4a094d1dfdeebd803c83ebaf4482d8af07a3d0e1984124ec0328b6`.

## Pesquisa e cobertura

Foram inventariadas e extraídas por página as **10.021 páginas**, sem página vazia ou erro de extração registrado: REF 7.284, TRD 2.047, NN 690. O catálogo tem **4.821 entradas**: REF 4.128, TRD 581, NN 112. Os livros originais foram preservados por hash. Manifesto, metadados, identidades de página, índice pesquisável, matriz e notas estão em `research/`.

A leitura semântica textual foi executada em lotes rastreáveis. As entregas parciais e complementos foram mantidos. A união final possui **REF 7.284/7.284, TRD 2.047/2.047 e NN 690/690**, sem intervalo textual pendente. O estado formal é COMPLETE_TEXTUAL_DECLARATIONS. A matriz verifica os intervalos de todas as entradas; não concede cobertura de filhos pela mera leitura da abertura do pai, nem conta sobreposições novamente.

A pesquisa distingue o contrato da plataforma, comportamento observado em arquivos identificados, regra JP Wealth e proposta. Uma API disponível, um exemplo oficial ou uma classe cujo nome pareça passivo não demonstram chamada atual no Stoikus. As notas classificam propostas e falta de uso atual demonstrado. Há observações concretas sobre precisão, arrays, prontidão de séries, filas de eventos, SQLite/arquivos, propriedade de recursos, wrappers, controles, modelos neurais e avaliação temporal. Anomalias bibliográficas permanecem qualificadas; não foram convertidas em bugs de produção sem prova.

Os lotes geralmente respeitam o alvo de até 30 mil caracteres. Exceções documentadas e saídas truncadas estão preservadas: as saídas incompletas foram reexpostas antes de receber crédito de leitura. Alguns lotes normalizaram somente espaços de diagramação, conservando o texto e os hashes da extração original. Isso não certifica fidelidade visual de equações como imagem ou linhas já cortadas no PDF.

Houve inspeção visual dirigida de **30 páginas originais**, com fórmulas, tabelas, diagramas, exemplos de código e trechos críticos. O recibo R2 registra identificação individual, hash da imagem e escopo; o R1 anterior permanece. **Não houve inspeção visual das 10.021 páginas nem verificação caractere a caractere de todos os códigos.** Esses limites não são supridos pela completude da leitura textual. Os 30 recortes de evidência são de consulta privada; os PDFs e seu texto integral extraído não são redistribuídos no kit.

Na extração de numeração, 10.018 páginas coincidem com o número físico, sem divergência detectada; três capas não tiveram número detectado. `pagination-map.json` informa o método, separado da inspeção visual. As citações usam documento, seção e página física. Consultas oficiais atuais foram identificadas à parte em `official-sources.json` e nos ledgers pertinentes.

A crítica independente final conferiu as 10.021 identidades textuais por recomputação de hash, as 4.821 entradas, a união das 40 entradas de evidência e seus hashes, além de 7.177 comparações de hashes de páginas em formatos de ledger reconhecidos. Confrontou integralmente **17 páginas de corpo**, escolhidas de REF/TRD/NN, com notas e afirmações do manual. Não encontrou novo P1/P2 nesse escopo e encerrou a lacuna documental global anterior. O parecer é **PASS de rastreabilidade e amostra textual dirigida**, sem certificação de segunda leitura integral independente ou da correção de cada interpretação.

Permanece uma melhoria opcional P3: acrescentar ponteiros diretos `note_file/note_heading` a cada linha da matriz. Hoje títulos, IDs, faixas, ledgers e `tools/query_sources.py` permitem localizar as notas. A ausência desse atalho não foi considerada lacuna de leitura demonstrada pelo crítico.

## Harness: testes, piloto e falhas preservadas

O checker `check_harness.py` usa a biblioteca padrão de Python, lê somente arquivos e emite JSON. Não modifica arquivos ou acessa a rede por padrão. Confere hashes, referências locais, campos e estados. Retorna 0 para integridade, 1 para inconsistência e 2 para dependência indisponível; inconsistência prevalece quando ambas estão presentes. O hash do próprio checker precisa ser conferido externamente. Um manifesto e um checker adulterados conjuntamente não se autenticam por conta própria.

O desenvolvimento preservou testes que falharam antes das correções. A revisão R3 terminou com **30/30 testes locais PASS**. Há controles de adulteração, caminhos absolutos/traversal, symlink/loop, arquivos ausentes, campos/tipos/estados inválidos, proveniência malformada, isolamento do construtor, hash de dispatch e não mutação dos arquivos. O checker real aplicado à cópia final retornou **0 / INTEGRITY_OK**. Os logs de falha e sucesso estão em `validation/evidence/`; revisão independente do kit precedeu o piloto.

Foram realizadas **duas rodadas novas de 36 tentativas**, totalizando 72 preservadas. São distintas das 36 tentativas históricas do GENETRIX, que não foram reexecutadas aqui.

| Rodada do kit novo | Resultado formal | Conteúdo isolado | Interpretação |
|---|---|---|---|
| R2 | 19 PASS, 17 INCONCLUSIVE; conjunto INCONCLUSIVE | 33 aderências e três conflitos S01 | Parte da captura legível preventiva faltou; entrada S01 não explicitava que o handle era obrigatório. Sem ocultar tentativas ou forçar aprovação. |
| R3 | 36 PASS, zero FAIL/INCONCLUSIVE; 12 casos com três aprovações | Todos 10/10 nos critérios obrigatórios | Nova rodada inteira após explicitar a precondição e reforçar a captura. Gabaritos dos 12 casos preservados. |

O julgador independente foi calibrado com controles correto, defeituoso e insuficiente antes das tentativas. Não participou da implementação do kit. Construtores receberam projeções sem gabaritos em contextos novos (`fork_turns=none`), com identidades diferentes. A R3 preservou dispatch legível completo, seus bytes de entrada e hash antes dos spawns, além de recibos de infraestrutura e horários. Critérios, fixtures, prompts e referências foram congelados previamente; o autor do kit não julgou suas próprias tentativas como crítico independente.

**O PASS R3 é restrito a esses 12 casos sintéticos.** Construtores usaram o destino solicitado gpt-6.1-sol; o juiz separado usou gpt-6-astra. O build efetivo do backend não foi exposto. O sistema de arquivos era compartilhado, com acesso aos gabaritos proibido. Logs de ferramentas por tentativa são SELF_RECORDED, vinculados à infraestrutura e à captura preventiva; não são exportação completa de todas as ferramentas da plataforma. Fixture e captura mudaram da R2 para a R3, impedindo inferência causal de ganho do modelo. Não há evidência de superioridade geral, redução de custo ou validade em tarefas abertas.

O manifesto interno permanece como snapshot **pré-piloto NOT_RUN**. Alterá-lo após o ensaio mudaria o hash testado. `harness-qualification-R3.json` é a qualificação posterior externa para esses bytes, com vínculo ao freeze, calibração, parecer e julgamentos. Relatórios anteriores de construção também conservam o estado que existia no momento em que foram escritos. O guia explica essa sequência.

## Manual, contraprovas e formatos

Revisões independentes do manual identificaram e levaram a corrigir duas afirmações técnicas: proteção da saída em uma diferença numérica sintética e a dependência da contagem de parâmetros multi-head da largura mantida fixa. A revisão de formato detectou perda de rótulos/transições e dos ramos de decisão nos diagramas convertidos. O parser foi substituído por extração que conserva todos os nós/arestas/rótulos e recusa sintaxe/topologia não prevista. As figuras reparadas foram reavaliadas contra o Markdown; os renders anteriores continuam disponíveis como histórico.

O laboratório original em `examples/contraprovas_matematicas.py` executou quatro controles locais: permutação de entradas com pesos fixos, correlação linear zero com dependência determinística, alteração da normalização por dado futuro e gradiente numérico que rejeita uma derivada defeituosa. Resultado **PASS_LOCAL_MATH_ONLY**, conferido também pelo crítico. Isso não reproduz os programas MQL5 dos livros ou valida uma estratégia financeira.

Na revisão final R7:

- **403 segmentos de prosa** encontrados em DOCX e PDF, com normalização alfanumérica explicitada no checker editorial.
- DOCX sem falha de integridade ZIP, três figuras, **13 equações de exibição e 17 objetos matemáticos nativos OMML** no total.
- Quatro trechos sintéticos de programação, 54 linhas lógicas, tipografia monoespaçada legível; estado nativo NOT_COMPILED/NOT_RUN.
- PDF com **56 páginas**, sem caracteres fora dos limites físicos detectados.
- Todas as páginas finais com recibo visual: crítico independente para 1–28 e coordenador para 29–56. Dezenove páginas 1–28 puderam reutilizar o parecer anterior por igualdade byte a byte dos PNGs; nove alteradas foram reinspecionadas. Sumário e destinos conferidos.
- Controles negativos do checker editorial detectaram remoção de parágrafo no DOCX e remoção de página no PDF. Originais não foram alterados por esses controles.

Presença de texto normalizado e contagem de equações não demonstram, sozinhas, equivalência semântica. A inspeção visual e as revisões de conteúdo fornecem evidência complementar com escopos explícitos. **Não foi realizada reabertura no Microsoft Word nativo.**

## Preservação, cópia e estados pendentes

O recibo `preservation-final.json` reconferiu **1.115 arquivos preexistentes**, sem alteração ou exclusão, e o HEAD Git permaneceu igual ao inicial. Os três PDFs originais tiveram SHA-256 reconferido, sem divergência. A entrega acrescenta somente documentação e artefatos próprios desta tarefa; não muda produto, fórmulas, bancos, histórico, harness antigo, site, instalador, AGENTS, CI ou gates. Não houve commit, push, merge ou publicação.

A cópia durável conserva a entrega, os formatos, as 72 tentativas do novo kit, versões R1/R2 preservadas, qualificação R3, pareceres, logs, render final, recortes dirigidos de fonte e hashes. Os diretórios privados de extração/lotes brutos permanecem como evidência de trabalho fora do pacote de distribuição. Os ZIPs são preparados de forma determinística, com ordem e metadados fixos; a integridade é conferida contra os arquivos de entrada e o teste de reprodução usa dois empacotamentos do mesmo conjunto.

| Estado | Resultado desta entrega |
|---|---|
| Pesquisa textual e rastreabilidade | Completa nas declarações consolidadas; crítica independente global de integridade e amostral de conteúdo |
| Manual e formatos | Entregues e conferidos no escopo descrito |
| Checker e laboratório matemático | PASS local |
| Piloto do harness R3 | PASS restrito aos casos sintéticos congelados |
| MetaEditor, exemplos MQL5, EX5, Strategy Tester e MT5 | NOT_RUN / NOT_COMPILED quando aplicável |
| Instalação Windows/Parallels, interação nativa e aceite do proprietário | NOT_RUN |
| Aprovação financeira ou operacional | NOT_RUN |
| Adoção do harness e superioridade geral | NOT_ADOPTED / NOT_ESTABLISHED |
| Publicação ou integração no site/instalador | Não realizada nesta entrega |

Esses estados permanecem independentes. O artigo e o kit fornecem um caminho verificável para futuras tarefas autorizadas; não tornam as etapas nativas ou a aprovação do proprietário fatos já ocorridos.
