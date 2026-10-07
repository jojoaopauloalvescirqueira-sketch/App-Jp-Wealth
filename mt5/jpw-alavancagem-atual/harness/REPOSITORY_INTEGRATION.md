# Integração documental do harness GENETRIX no repositório

Registro de integração: 07/10/2026. Produto: **GENETRIX 1.20.0**; MQL **1.200**; cálculo **1.9.0**. Harness: **1.0.0 — CANDIDATE**. As versões são independentes.

## Alcance e ativação

Esta pasta distribui o protocolo de engenharia e seus contratos, preservando os bytes canônicos do pacote de origem. O arquivo [AGENTS local](../AGENTS.md) acrescenta o mapa atual e a instrução de leitura; suas referências anteriores permanecem identificadas como históricas. O [harness Markdown](JPW_GENETRIX_MT5_ENGINEERING_HARNESS_v1.0.md), o TXT equivalente, o PDF e o [manual](MANUAL_DE_ATIVACAO.md) não foram reescritos para adaptar caminhos.

A integração se aplica somente a `mt5/jpw-alavancagem-atual/`. Não substitui o AGENTS da raiz do repositório nem as instruções de desenvolvimento do site. Não instala IA no Cockpit, altera fontes MQL5, fórmulas, parâmetros, schemas, registros financeiros, preferências ou permissões. Não ativa o Supervisor.

Para usar, forneça o protocolo integral ao assistente, delimite a tarefa e seus limites, leia este mapa de caminhos, confira as dependências acessíveis e execute VERSION_CHECK. Dependência ausente permanece uma limitação; não alegue leitura, vigência ou aprovação que os arquivos distribuídos não demonstram.

## Mapa dos caminhos congelados do pacote

Os caminhos escritos no canônico partem da raiz original da entrega, onde `Fontes`, `sources`, `contracts` e `delivery-docs` são irmãos. Eles descrevem aquele pacote congelado. Nesta integração, use o mapeamento abaixo; os aliases não criam cópias normativas ou um manifesto de fontes inexistente.

| Referência no pacote original | Destino ou tratamento no repositório |
|---|---|
| `Fontes/AGENTS.md` | [../AGENTS.md](../AGENTS.md) |
| `Fontes/GENETRIX_CORE_1_20_0.md` | [../GENETRIX_CORE_1_20_0.md](../GENETRIX_CORE_1_20_0.md) |
| `Fontes/harness/JPW_GENETRIX_MT5_ENGINEERING_HARNESS_v1.0.md` | [Canônico local](JPW_GENETRIX_MT5_ENGINEERING_HARNESS_v1.0.md); TXT e PDF na mesma pasta |
| `Fontes/harness/MANUAL_DE_ATIVACAO.md` | [Manual local](MANUAL_DE_ATIVACAO.md) |
| `contracts/ENG-AC01-12.json` | [Contrato canônico dos 12 casos](contracts/ENG-AC01-12.json) |
| `contracts/TEMPLATES.md` | [Modelos de registro](contracts/TEMPLATES.md) |
| `sources/manifest.json` e `sources/CURRENT-SOURCE-LOCATIONS*.json` | Externos; permanecem na entrega do vault, não distribuídos nesta pasta |
| `sources/engineering_core.md`, `sources/governance.txt`, `sources/evaluator.txt` | Referências externas; obter as fontes competentes e registrar versão/hash antes de nova tarefa |
| `sources/annex.md`, `sources/statute.pdf`, `sources/nocuda_explanation.md`, `sources/nocuda_article.pdf` | Referências privadas externas; não redistribuídas nesta integração |
| `delivery-docs`, `sessions`, `fixtures*`, `oracles*`, `judgments`, `reviews`, `render` e `evidence` do piloto | Acervo externo de evidências; não incluído como código produtivo ou como suíte executada pelo repositório |

A entrega de origem foi conferida em:

`2 - TRABALHO/4D - GENERATRIX EA/Harness interno GENETRIX v1.0 - Candidato`.

O caminho é uma pista de localização sujeita a movimentação do vault. Seu `MANIFEST.json`, `DELIVERY-FINAL-QA.json`, `01 - Relatório do piloto e validação.md` e os pareceres registram identidade e alcance. O catálogo `downloads/jpw-alavancagem-atual/manifest.json` deste repositório lista os documentos distribuídos; não substitui o manifesto privado de fontes do piloto nem prova vigência do modelo. Documentos normativos já existentes em outras áreas do repositório só podem ser usados após confirmação explícita de identidade, autoridade e aplicabilidade; não constituem fallback automático para uma dependência ausente.

## Estado observado do piloto

O protocolo permanece **CANDIDATE**, sem aprovação comportamental integral. A rodada completa R2 executou e julgou **36/36 tentativas**, três por caso: **25 PASS / 7 FAIL / 4 INCONCLUSIVE**. Resultado da revisão completa: **FAIL**. Falhas e inconclusões não foram compensadas por uma média ou apagadas pela integração.

Os retestes R5 foram restritos: **ENG-AC03 FAIL** (T01 PASS, T02 FAIL, T03 FAIL) e **ENG-AC04 PASS** (três tentativas PASS). A suíte completa R5 de 36 sessões permanece **NOT_RUN**. Esses resultados não substituem o R2 nem aprovam a versão inteira. A proposta **1.0.1 — CANDIDATE / NOT_ADOPTED** permanece externa e não é carregada pelo AGENTS ou apresentada como novo canônico.

Os reparos do piloto ocorreram em fixtures controlados, sem propagação ao produto. A entrega documental preservou os **112 arquivos MQL5/recursos da base 1.20.0**; sua compilação e execução nativas próprias permanecem **NOT_RUN**. Compilações históricas comprovadas da base pertencem à revisão do produto e não demonstram execução do piloto, funcionamento do terminal, instalação operacional ou aprovação do harness. Estados do domínio, inclusive PENDING, NOT_HOMOLOGATED, BLOCKED e PRODUCT_FAIL, permanecem nas respectivas fontes.

## Consulta e conservação

Para julgar o piloto, consulte o relatório, todas as tentativas e os pareceres da entrega original. Esta nota oferece o resumo e o mapa; não reproduz os registros completos nem afirma que as 36 sessões foram executadas novamente durante a integração. O contrato dos casos permite preparar uma nova rodada, que precisará de entradas, ambiente, referências, hashes e recibos próprios. Exposição compartilhada dos revisores e ausência de segregação plena de três operadores independentes foram declaradas no relatório original.

Para rollback documental, preserve esta revisão, restaure apenas o AGENTS local da base 1.20.0 e remova os novos documentos numa cópia controlada; regenere manifesto e pacote coerentes. Não apague bancos, evidências, fontes originais ou instruções globais. Publicação GitHub, compilação, teste local, execução MT5, instalação e aceite são estados distintos.
