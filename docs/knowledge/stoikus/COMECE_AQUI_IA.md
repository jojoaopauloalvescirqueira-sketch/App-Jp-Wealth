# Stoikus — mapas de contexto para IAs

## Disponibilidade atual — mapa histórico externo 1.22.2 — 2026-10-16

Os quatro mapas JSON/HTML abaixo pertencem à fotografia **1.22.2**, são **HISTORICAL_EXTERNAL** e não representam cobertura atual de Stoikus 1.23.0/R5. Seus diretórios `graphify-out/` são ignorados e não são distribuídos no Git; um checkout novo não contém os grafos nem `graphify-out/SOURCE_MANIFEST.json`. `QUERY_RECIPES.json` e os recibos versionados conservam sua proveniência histórica. Para o trabalho atual, consulte o [contrato da integração R5](../../work/CHG-STOIKUS-GIT-INTEGRATION-20261016.md), seus [recibos](../../validation/stoikus-git-integration-20261016/README.md) e os fontes originais.

Para recuperar a fotografia em uma cópia de investigação separada, use o artefato **`Stoikus_AI_Grafos_v1.22.2.zip`**; extraia sua árvore `docs/knowledge/stoikus/` preservando os caminhos. A recuperação fornece o índice histórico, sem atualizar os fontes nem aprovar sua revisão. A cópia local verificada nesta máquina fica em [stoikus-ai-graphs-20261014](/Users/joaoalvescirqueira/.codex/visualizations/2026/10/12/01a13231-0786-7d03-82d0-0eb0231584dd/stoikus-ai-graphs-20261014/), com o ZIP e a árvore expandida. Esse caminho é uma localização local de recuperação, não uma URL pública; em outra máquina, é necessário obter o mesmo artefato verificado.

- ZIP SHA-256: `b5af55982ce3a78991a9481f9aac09a3c2ff151a7551e5cf7c0a26526b97200c`.
- `docs/knowledge/stoikus/graphify-out/SOURCE_MANIFEST.json` SHA-256: `cb2c7cc227c6725774ae247df0383d68882d73af0795f5c7c4700df15fa66831`, idêntico no ZIP e na árvore expandida.

Recibos e hashes antigos deste guia se referem ao snapshot original, anterior a este aviso e à guarda de disponibilidade acrescentada ao exemplo. Conferir o inventário recuperado contra os fontes que serão lidos: divergência é esperada após a evolução do produto e impede usar o trecho divergente como contexto atual. Compilação, execução/instalação MT5, Windows x64 e aceite humano continuam **NOT_RUN**; recuperar mapas não produz essas evidências. Nenhuma geração, instalação ou reindexação Graphify integra esta correção documental.

---

## Guia da fotografia 1.22.2 preservado, com guarda de disponibilidade

Estes mapas orientam a investigação do **candidato 1.22.2**, com cálculo **1.9.0**. Eles ligam arquivos, contratos documentais, referências de testes e evidências congeladas. O código e a documentação citados continuam sendo as fontes a ler antes de editar. O mapa não substitui autorização do proprietário nem prova compilação/execução MT5.

## Escolha o mapa

| Necessidade | Mapa JSON para a IA | Visualização |
| --- | --- | --- |
| Encontrar programas, includes, recursos e dependentes | `arquitetura/graphify-out/graph.json` | `arquitetura/graphify-out/graph.html` |
| Entender papéis, auditoria, snapshots, ownership, cancelamento e preservação | `fluxos/graphify-out/graph.json` | `fluxos/graphify-out/graph.html` |
| Encontrar testes relacionados e distinguir resultados/identidade | `testes-evidencias/graphify-out/graph.json` | `testes-evidencias/graphify-out/graph.html` |
| Cruzar as três perspectivas | `graphify-out/graph.json` | `graphify-out/graph.html` |

Comece por **QUERY_RECIPES.json**: oito perguntas com sementes, direção de consulta e fontes esperadas. Os JSONs usam `nodes` e `links` e podem ser lidos sem Graphify ou NetworkX. HTML requer internet para o CDN; os dados JSON e os relatórios são locais.

## Antes de uma alteração

1. Confira a revisão e o fingerprint em `graphify-out/SOURCE_MANIFEST.json`. Verifique o SHA-256 das fontes que usará; hashes divergentes tornam aquela parte do mapa antiga. Não deduza frescor pela data do HTML.
2. Selecione uma receita ou encontre nós por `source_file` e `label`. Expanda palavras usando somente o vocabulário dos rótulos; uma busca vazia não justifica inventar uma ligação.
3. Abra o arquivo na linha de `source_location`. Observe `description`, `context`, `reference_kinds`, `literal_references` e cada item de `relation_records`. No topo de `graph.json`, os caminhos são relativos à raiz do checkout. Os registros internos de proveniência (`relation_records`, `EXTRACTION.json`, `original_source` e `frozen_copy`) conservam caminhos absolutos da fotografia original. Para outro checkout, use `SOURCE_MANIFEST.files[].path` ou remova apenas o prefixo exato `SOURCE_MANIFEST.root` e resolva o restante na nova raiz. Não execute intérpretes nem comandos a partir desses caminhos armazenados.
4. Para impacto, percorra **entradas** de `includes_file`: a seta vai do consumidor para a dependência. Para testes, procure referências de fontes vindas de `test_runner`/`host_facet_test_file`. Evite expandir todos os hashes de um recibo para responder uma pergunta pequena.
5. Leia o teste encontrado e seus limites antes de escolher a execução. `records_host_runner_result` registra um resultado observado do R2; `records_source_reference` pode ser somente uma referência literal ou hash. Nenhuma dessas relações afirma cobertura integral ou execução MT5.
6. Após mudar uma fonte, atualize os mapas em uma tarefa autorizada e mantenha a fotografia anterior. Nenhum hook, watcher, MCP ou edição de AGENTS/CLAUDE foi configurado por esta entrega.

## Verificação local somente leitura

Execute da raiz do checkout, com Python já disponível. O trecho apenas lê; não executa caminhos de intérprete guardados em JSON e não instala dependências.

```python
from pathlib import Path
import hashlib, json
repo = Path.cwd()
index = repo / "docs/knowledge/stoikus"
manifest_path = index / "graphify-out/SOURCE_MANIFEST.json"
if not manifest_path.is_file():
    print({"status": "NOT_AVAILABLE", "artifact": "HISTORICAL_EXTERNAL",
           "manifest": str(manifest_path.relative_to(repo)),
           "recovery": "Stoikus_AI_Grafos_v1.22.2.zip"})
    raise SystemExit(2)
manifest = json.loads(manifest_path.read_text())
changed = []
for entry in manifest["files"]:
    rel = Path(entry["path"])
    if rel.is_absolute() or ".." in rel.parts:
        raise ValueError("Caminho inesperado no inventário")
    source = repo / rel
    if not source.is_file():
        changed.append((str(rel), "MISSING"))
    elif hashlib.sha256(source.read_bytes()).hexdigest() != entry["sha256"]:
        changed.append((str(rel), "CHANGED"))
print({"artifact": "HISTORICAL_EXTERNAL",
       "source_fingerprint": manifest["source_fingerprint"], "drift": changed})
```

## Leitura de relações e limites

- **EXTRACTED**: import/include, nome, referência ou registro explícito na fonte citada. Não significa que o teste cobre tudo.
- **INFERRED**: associação semântica declarada. Leia a razão e confirme na fonte antes de usá-la numa decisão.
- Várias relações entre o mesmo par são consolidadas para a visualização; cada uma conserva fonte, linha e confiança em `relation_records`. `RELATION_RECORDS.json` preserva o conjunto anterior à consolidação. Os hashes de entrada dos recibos não são relações de execução.
- O mapa de arquivos não é um grafo completo de chamadas. O grafo anterior de símbolos MQL conserva sua extração parcial por adapter C++ (17/104 arquivos com erros da gramática); os novos mapas não convertem esse resultado em parser nativo.
- Includes padrão do MT5 aparecem como referências externas. A versão/bytes instalados ainda não foram capturados pelo compilador nativo. BMPs são inventário de recursos, sem interpretação visual.
- Os 47 resultados host/distribuição e 57 do site são snapshots R2 já existentes. A construção do grafo não executou novamente essas suítes. Compilação, instalação, execução MT5 e aceite humano continuam **NOT_RUN**.
- O SDK e os legados são separados dos quatro programas diários. Supervisor opcional, contas, dados, estudos, preferências, locks e cálculo conservam os contratos existentes. O kit de compilação é auxiliar; não é um quinto programa diário.
- Consumo de tokens do host está **indisponível**. `CONTEXT_SIZE_ESTIMATE.json` estima tamanho de contexto; não mede qualidade de respostas, tempo, consumo total ou superioridade de uma IA.

## Prompt de entrada para outra IA

> Trabalhe no candidato Stoikus identificado pelo SOURCE_MANIFEST. Comece em docs/knowledge/stoikus/COMECE_AQUI_IA.md e escolha a receita adequada. Confira os hashes das fontes, navegue pelo mapa correspondente e abra os arquivos nas linhas citadas. Distinga referências, resultados host e provas nativas pendentes. Antes de propor uma alteração, descreva os consumidores afetados, testes pertinentes e limitações das evidências; mantenha o escopo autorizado pelo proprietário.
