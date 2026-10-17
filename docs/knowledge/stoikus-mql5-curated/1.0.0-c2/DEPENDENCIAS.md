# Disponibilidade e uso das referências

Os caminhos relativos deste pacote são descritos por `MANIFESTO_CURADO.json`. A existência de uma citação em um arquivo histórico não garante que o arquivo citado esteja nesta seleção. Use o mapa de origem e o inventário de referências; não crie arquivos substitutos para satisfazer hashes antigos.

| Uso | Disponível nesta edição | Dependência externa ou limite |
|---|---|---|
| Ler manual | Markdown, Word, PDF, capítulos e figuras | Leitor correspondente. Os formatos foram conservados, não regenerados aqui. |
| Consultar títulos e notas | `research/`, `tools/query_sources.py` | Python 3 com biblioteca padrão. A busca não lê os PDFs nem prova a interpretação da API. |
| Retornar às fontes bibliográficas | Identidades, páginas e notas | Três PDFs originais em SOURCES, ver tabela abaixo. Não incluídos. |
| Conferir o kit candidato | `harness-candidato/` completo | REPO e SOURCES externos; código produtivo não incluído nesta edição. |
| Reconstruir cobertura histórica | Ledgers, matriz, resumo e ferramenta | Corpus privado por página, índices e lotes brutos externos. `consolidate_coverage.py` grava saídas e produz hashes novos; não executar sobre esta pasta congelada. |
| Regerar MD/Word/figuras | Entradas editoriais e ferramentas preservadas | Python, python-docx, Pillow, fonte compatível (padrão do script é Arial do macOS), diretório `validation/` de saída; usar cópia de trabalho. O builder editorial escreve artefatos. |
| Conferir publicação histórica | Ferramenta e formatos finais | pypdf e pdfplumber; nova execução tem resultado próprio. Não ocorreu nesta montagem. |
| Auditar recibos de piloto/visuais | Resumos e revisões legíveis em `validation/` | Tentativas, dispatch, logs, infraestrutura, recortes e renders externos ao pacote. Sem os brutos, a prova não é reapresentada integralmente. |
| Verificar esta seleção | Manifesto, guia e, após Task 2, `verificar_edicao.py` | Python 3 com biblioteca padrão; não requer REPO, SOURCES, rede ou execução do EA. |

| Fonte externa em SOURCES | Páginas | SHA-256 esperado |
|---|---:|---|
| `MQL5 Language REFERENCE.pdf` | 7.284 | `9ae05ce748d23ce0de9b230fc6c7093a2af0adc3ce3544244a74e1c7d628d499` |
| `MQL5 Programming for Traders.pdf` | 2.047 | `9ff6c55090527afa0efce722d67760805ee335fc64dad3c83638a89e6c79a145` |
| `Neural Networks for Algorithmic Trading with MQL5.pdf` | 690 | `850e21e204f296b4c661895fcea4893ab263c81c7a0ead242a22234716611287` |

SOURCES e REPO são nomes de raízes a fornecer pelo leitor, não subpastas prometidas nesta edição. Os caminhos produtivos exatos exigidos pelo kit estão em `harness-candidato/manifest.json`, sob `references` com `root: repo`. Documentação oficial online citada nos textos também é externa; nenhuma consulta de rede foi feita na montagem.

Paths temporários absolutos que permanecem nos registros autorais designam o ambiente histórico: corpus, lotes de leitura e checkout examinado. Não são caminhos portáteis ou requisitos presentes. `curadoria/REFERENCIAS_EXTERNAS.json` os lista com a classe HISTORICAL_EXTERNAL_NOT_BUNDLED; os três caminhos pessoais foram generalizados nas cópias. Falta do corpus, dos lotes ou dos brutos é uma dependência ausente para reproduzir a etapa correspondente.

O resumo original de cobertura conserva hashes de arquivos históricos. Quando um registro foi sanitizado, o hash antigo continua válido para seu original privado; o índice atual fornece o hash da cópia e as referências afetadas. Recalcular um arquivo e trocar esses hashes silenciosamente fabricaria um recibo que nunca foi produzido pelo pesquisador original.

Para analisar o estado atual do produto, obtenha um checkout e valide sua revisão independentemente. Os recibos preservados descrevem a fotografia original, não a instalação, execução ou aceitação atual do Stoikus.
