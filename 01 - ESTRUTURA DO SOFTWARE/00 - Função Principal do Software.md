# JP Wealth — filosofia de produto e estrutura funcional

## Propósito e público

**CONFIRMADO — definição do proprietário:** o JP Wealth se organiza em Dashboard, Research, Forex, Finanças Pessoais e Alladin. Esta é a **visão declarada pelo proprietário neste pedido**, registrada em 2026-09-09; não se atribui a ela uma data histórica de decisão não comprovada.

O conjunto pretende conectar estudo, planejamento, gestão de risco e acompanhamento dos investimentos. Clareza, preservação de capital, disciplina, decisões fundamentadas e simplicidade operacional orientam essa finalidade. O software apoia o julgamento do usuário: não promete resultados nem substitui sua responsabilidade por decisões e registros.

**INFERÊNCIA — interpretação de produto:** o público principal é a pessoa que organiza a vida financeira pessoal ou familiar e acompanha investimentos, podendo também atuar em Forex. Ter cinco módulos permite aprofundamentos distintos; não pressupõe que todo usuário opere derivativos. Perfis comerciais de público, trabalho simultâneo de várias pessoas e gestão de carteiras de terceiros não estão estabelecidos por este pedido.

O problema comum é a fragmentação: estudar uma possibilidade, planejar recursos, controlar uma operação e acompanhar o que se possui são tarefas relacionadas, mas representam fatos diferentes. A organização proposta torna essas diferenças compreensíveis, sem exigir um único saldo ou registro para conceitos distintos.

## Papel dos módulos

| Módulo | Finalidade declarada pelo proprietário | Fronteira principal |
|---|---|---|
| [Dashboard](<05 - Dashboard.md>) | Sintetizar as demais áreas e orientar o acesso | Resumo transversal; não substitui os módulos especializados |
| [Research](<06 - Research.md>) | Estudar modelos, analisar ativos e fundamentar seleção, inclusive possibilidades futuras | Estudo não equivale a investimento detido ou ordem autorizada |
| [Forex](<07 - Forex.md>) | Trabalho ativo em derivativos e gerenciamento de risco; finalidade de “Estatuto JP Wealth Vivo” | Intenção de aderência não comprova conformidade do motor com a V11 |
| [Finanças Pessoais](<08 - Finanças Pessoais.md>) | Planejamento pessoal/familiar, despesas e organização financeira | Orçamento não é patrimônio consolidado nem capital automaticamente transferido |
| [Alladin](<09 - Alladin.md>) | Consolidação completa dos investimentos e visão integrada da carteira | A profundidade patrimonial pertence aqui; sua implementação ainda é parcial |

**INFERÊNCIA — relação de uso:** estudar em Research pode fundamentar uma decisão; Finanças Pessoais ajuda a avaliar suas consequências no orçamento; Forex apoia a operação e o risco quando aplicável; Alladin registra e acompanha os fatos patrimoniais suportados; Dashboard permite retomar o panorama. Esse percurso é uma interpretação funcional, não uma sequência obrigatória ou automação existente.

## Fronteiras e mapa textual das relações

**CONFIRMADO — código e contratos consultados:** a aplicação é local/PWA, sem backend obrigatório. A infraestrutura comum de estado, backup e navegação não significa sincronização econômica entre módulos. Cada área mantém responsabilidade semântica sobre seus registros; o usuário responde pela qualidade das informações inseridas.

| Origem → destino | Situação e informação | Limite |
|---|---|---|
| Forex → Dashboard | Existente: derivação de risco/veredito, último fechamento e resumo do plano | Leitura; não cria ordens ou uma segunda apuração |
| Finanças Pessoais → Dashboard | Existente: métricas mensais, crédito vigente e comparação | Completude e competência continuam próprias do módulo |
| Research → Dashboard | Existente: contagens de estudos e agenda pelo domínio/cache compartilhado | Cobertura de estudo não mede qualidade de uma tese |
| Alladin → Dashboard | Existente: posições por quantidade, cadastros, saldos por conta e último lançamento | Não é valuation ou patrimônio total; apenas três contas de caixa no resumo |
| Dashboard → demais módulos | Existente: navegação e atalhos para telas específicas | Navegar não transfere dados ou recursos |
| Catálogo de instrumentos → Forex e estudos Research | Existente: identidade compartilhada pelos consumidores | Não unifica esse catálogo ao cadastro patrimonial do Alladin |
| Feed de notícias → calendário Research e widget/resumo Dashboard | Existente: leitura/cache compartilhado | Disponibilidade e atualização do serviço real não verificadas nesta tarefa |
| Fonte de referência USD/BRL → Planejamento Forex | Existente: referência diária distinta de premissa futura | Não comprova conversão cambial no Alladin |
| Resultado Forex → orçamento pessoal | Manual: pode ser informado pelo usuário como receita pessoal | O contrato de Finanças Pessoais exclui integração automática; não importar todo lucro como caixa disponível |
| Research → decisão de investimento | Manual: interpretação pelo usuário | Não há evidência de envio automático de ordens ou de ativos ao Alladin |
| Forex/Planejamento → Alladin; dívida pessoal → passivo patrimonial | Contratos futuros pendentes, não integração existente | Fronteiras HD-1/HD-2/HD-3 registradas no contrato Alladin; sem aprovação nova aqui |
| Research → referência de tese no Alladin | RECOMENDAÇÃO, não implementada | Depende de identidade e vínculo explícitos, sem duplicar cadastro ou investimento |

Dashboard versus Alladin: o primeiro reúne sínteses de áreas heterogêneas; o segundo deve aprofundar a carteira e seus fatos patrimoniais. Research versus Alladin: possibilidade estudada não prova posse. Finanças Pessoais versus capital de investimento/operação: intenção de alocação e despesa pessoal não provam depósito, transferência ou posição econômica.

Somar o saldo Forex a um registro Alladin que represente os mesmos recursos pode duplicar patrimônio. Registrar uma transferência como nova receita em ambos os lados pode duplicar fluxo. Somar montantes em moedas diferentes sem base de conversão comprovada gera um total indevido. Estas são advertências de interpretação, não novas fórmulas financeiras ou autorização para implementar integrações.

## Como ler as evidências e o estado implementado

- **CONFIRMADO:** distingue-se definição explícita do proprietário de fato sustentado por documento, código ou resultado de teste identificado.
- **INFERÊNCIA:** interpretação fundamentada, ainda não estabelecida como decisão.
- **NÃO VERIFICADO:** evidência insuficiente; não significa automaticamente inexistência.
- **RECOMENDAÇÃO:** proposta, sem aprovação de implementação, prazo ou compromisso.

“Completo no recorte” nos documentos de módulo significa fluxo delimitado identificado em código e coberto por evidência específica; não significa módulo inteiro concluído. “Parcial” indica que a finalidade é mais ampla que as funções disponíveis. Uma tela vazia é evidência de um destino de navegação, não de análise financeira funcional.

Fotografia consultada em **2026-09-09**: branch local `codex/dashboard-official`, HEAD `5393e4abfd4af5c8e83344914088c260a1cbfe76`. A main consultada está em `8c43fdbb6e300628501ebce1f5b009a1011bb0f4`, merge do [PR #4](https://github.com/jojoaopauloalvescirqueira-sketch/App-Jp-Wealth/pull/4); as duas revisões possuem a mesma árvore versionada (`32df3e8de11b7a2eb37635f40b9e788542db7411`) antes desta escrita documental. Build identificado: `9cf89998aa453da4`.

**CONFIRMADO — execução existente:** o [CI pós-merge 34303594511](https://github.com/jojoaopauloalvescirqueira-sketch/App-Jp-Wealth/actions/runs/34303594511) executou em main no SHA acima, evento `push`, tier `standard`, conclusão `success`. O log registra `PASS=44` e zero falhas/não executados. Os documentos citam os checks pertinentes; esta tarefa não repetiu testes nem validou dados reais. O full local 55/55 e o CI anterior ao merge são registros distintos, não a contagem deste CI.

A fonte canônica de estado permanece [CURRENT-STATE](../docs/governance/CURRENT-STATE.md), em conjunto com [PROJECT-CONTEXT](../docs/governance/PROJECT-CONTEXT.md) e os contratos de arquitetura. Estes textos são uma explicação de produto datada, não outro registro operacional concorrente. CURRENT-STATE explicita ser um checkpoint anterior à integração e remete ao PR; o merge e seu CI foram consultados diretamente. O mapa de código ainda cita 77 scripts em sua fotografia histórica; o manifest da revisão consultada possui 78. Nenhum desses documentos foi alterado.

## Fontes e limites documentais

A visão definida acima provém do pedido do proprietário de 2026-09-09. As referências históricas consultadas não documentam sua cronologia completa. Os cinco arquivos desta pasta e o arquivo “# O que esperar do Jp Wealth Software?” estavam vazios; títulos isolados não foram usados como evidência de funcionalidade.

Fontes de implementação: [navegação](../src/js/40-app/01-navigation.js), [contrato de navegação](../docs/architecture/NAVIGATION-HIERARCHY.md), [manifest](../src/js/manifest.json), [contrato Finanças Pessoais](../docs/architecture/PERSONAL-FINANCE.md), [contrato Alladin](../docs/architecture/ALLADIN.md), [Planejamento FX](../docs/architecture/FX-PLANNING.md), [NoCoda](../docs/architecture/NOCODA-STUDIES.md), [Pivots](../docs/architecture/PIVOT-STUDIES.md) e fontes específicas nos cinco documentos. Contratos com seções históricas são lidos junto às suas atualizações e ao código.

O [índice normativo V11](../docs/normative/README.md) registra divergências ainda abertas e motor legado. Não se fez auditoria financeira nem releitura normativa para homologação. O PDF não rastreado “Estatuto de Gestão de Risco.pdf”, em outra pasta, foi preservado e não foi promovido a fonte vigente por este trabalho.

## Registro proporcional do Harness

Escopo N0-D, escrita autorizada somente nesta pasta: um documento de visão geral e cinco de módulo. Demais arquivos, contexto, normas, runtime e artefatos preservados. O contrato desta tarefa é o pedido do proprietário; sua restrição de destino prevalece sobre a rotina genérica de atualizar ACTIVE-TASK e handoff.

O preflight inicialmente apontou o PDF preexistente não rastreado. Após delimitar esse arquivo como alheio à tarefa e preservá-lo, a execução com `--allow-dirty` aprovou estrutura/manifest e manteve visível o aviso contextual. Isso não declara a árvore limpa nem autoriza incluir o PDF.

AGENTIC IMPACT CHECK: AGENTIC IMPACT DETECTED

BASIS: a explicação de produto passa a informar usuários e agentes, sem mudar contratos executáveis. Em IMPACT: documentos estruturais e seus leitores são AFFECTED; ação local limitada aos seis textos autorizados. Agentes/bootstrap recebem a referência se consultarem esta pasta; suas instruções não precisam mudar. Skills, routing, registries, normas, arquitetura de memória e contratos de dados são NOT_AFFECTED, sem ação local. A fotografia de contexto anterior ao merge é preexistente; eventual atualização permanece RECOMENDAÇÃO fora desta tarefa. Nenhuma propagação ou indexação foi executada.

Validação documental: conferir os seis tópicos por módulo, coerência das fronteiras, referências locais, estados de evidência e diff limitado ao destino. A conferência não certifica conformidade V11 nem encerra o projeto. Evoluções sugeridas nos módulos dependem de decisão específica; esta documentação não autoriza desenvolvimento ou operações Git.
