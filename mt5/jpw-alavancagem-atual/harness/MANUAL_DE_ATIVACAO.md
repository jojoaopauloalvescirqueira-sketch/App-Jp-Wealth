# Como usar o harness interno GENETRIX

Edição candidata 1.0.0 · 06/10/2026

## 1. O que você está ativando

O harness é uma instrução de engenharia para o assistente que trabalha nos fontes. Ele organiza desenvolvimento de EAs, indicadores, scripts e bibliotecas, com fontes, limites e testes. Não é um EA, não vai dentro de `MQL5` para execução, não instala IA no Cockpit e não treina o modelo de linguagem.

O arquivo principal é [JPW_GENETRIX_MT5_ENGINEERING_HARNESS_v1.0.md](JPW_GENETRIX_MT5_ENGINEERING_HARNESS_v1.0.md). A cópia TXT reproduz seu conteúdo; o PDF serve para leitura. Forneça o conteúdo integral e o Core de engenharia aplicável ao assistente, ou autorize que ele leia esses arquivos na cópia de trabalho. Um link sem leitura comprovada não ativa conhecimento por si só.

## 2. Escolha a tarefa

| Sua necessidade | Modo |
|---|---|
| Entender um erro ou ausência de painel | `INVESTIGAR_DIAGNOSTICAR` |
| Definir uma melhoria antes de alterar fontes | `PLANEJAR_DESENVOLVIMENTO` |
| Desenvolver uma mudança delimitada e autorizada | `IMPLEMENTAR_MUDANCA_AUTORIZADA` |
| Revisar o candidato produzido por outro autor | `AUDITAR_CANDIDATO_CONGELADO` |
| Tentar falsificar critérios e registrar tentativas | `EXECUTAR_GAUNTLET` |
| Melhorar o protocolo após descoberta comprovada | `ATUALIZAR_HARNESS_CANDIDATO` |

## 3. Exemplos prontos para preencher

### Investigar problema no programa

> Adote o harness GENETRIX v1.0.0 e o Core aplicável. Modo INVESTIGAR_DIAGNOSTICAR. Na cópia [caminho/candidato], investigue [sintoma]. Tenho [log/screenshot/build]. Confira identidade dos arquivos e dependências. Diferencie causa demonstrada de hipótese. Preserve os fontes e entregue reprodução, diagnóstico e reparo proposto. Não instale componentes nem altere o terminal operacional.

### Desenvolver uma melhoria delimitada

> Adote o harness GENETRIX. Quero [comportamento], no componente [nome], partindo de [candidato]. Autorizei alterações apenas em [escopo], em cópia isolada. Preserve [fórmulas/bancos/objetos/preferências]. Defina critérios e referências antes do código, prepare CHG compatível com o Core e execute o que esta instrução cobre. Separe autoria e revisão; preserve todas as tentativas e entregue candidato e rollback.

### Avaliar outra entrega

> Modo AUDITAR_CANDIDATO_CONGELADO. Revise [candidato/hash] contra [contrato e critérios]. Leia as evidências de todas as tentativas. Não corrija os arquivos durante a auditoria. Repita as verificações aprovadas e procure falso positivo, regressão e alegação sem evidência. Informe exposição anterior ao contexto e dê conclusão por critério.

### Preparar pesquisa Nocuda

> Modo PLANEJAR_DESENVOLVIMENTO. Investigue [questão] nas fontes Nocuda e JP Wealth atuais acessíveis. Preserve o canal manual, passo 0,125 e nomes −1→1, 0→9, 1→17. Diferencie definição do autor, proposta de formalização e hipótese sem teste. Entregue dados necessários e protocolo; não transforme reação visual retrospectiva em sinal validado ou parâmetro homologado.

## 4. O que fornecer e exigir

Forneça objetivo, candidato/caminho, logs ou dados pertinentes, comportamento esperado e limites da autorização. Para consulta histórica, informe período e fuso disponíveis. Prefira fixtures sintéticos; contas e registros reais só entram quando expressamente autorizados para o escopo.

Exija manifesto de fontes e hashes, `VERSION_CHECK`, critérios congelados, registros de ações, arquivos reabertos e evidência do resultado. Você não precisa pedir exposição de raciocínio interno; justificativa verificável basta. Se o ambiente faltar, o assistente deve concluir módulos independentes e identificar precisamente o restante.

## 5. Como interpretar a entrega

Compilação prova que aqueles fontes foram compilados no ambiente indicado. Teste local prova somente as propriedades e condições exercitadas. Funcionamento no MT5 exige execução e evidência nativa; instalação e aceite operacional são etapas próprias.

`PASS` no comportamento de respeitar um parâmetro `PENDING` mantém o parâmetro pendente. `Partial` ou `N/A` não viram zero. Falha crítica reprova a revisão no escopo avaliado, mesmo com muitos acertos. Recibo histórico `PRODUCT_FAIL` permanece preservado.

O piloto desta edição prevê 12 casos com três sessões novas cada: **36 tentativas por revisão**. Consulte os recibos e o parecer da revisão exata para saber quantas foram realizadas e julgadas; previsão não é execução. Três processos determinísticos e três sessões de assistente são registros distintos.

## 6. Integração, manutenção e retorno

Na cópia candidata, `AGENTS.md` aponta para o harness e para o mapa atual. Monitor reúne conta/histórico/contabilidade no gráfico de apoio; os indicadores Conta e NoCuda ficam nos gráficos de trabalho; Supervisor é separado e opcional. Os produtores antigos permanecem para rollback, sem concorrência sobre os mesmos registros.

Antes de novo uso, confira origens, versões, vigências e hashes. Fonte alterada exige comparação, sem substituir norma pelo arquivo mais recente. Melhoria do harness gera revisão candidata e preserva a anterior.

Para desfazer a integração documental, restaure os arquivos de instrução anteriores a partir da cópia preservada e gere manifesto coerente. Não apague bancos financeiros, locks de outros escritores ou fontes originais. Esta entrega não instala, negocia, arma Supervisor ou publica automaticamente.
