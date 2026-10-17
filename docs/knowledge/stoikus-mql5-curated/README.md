# Stoikus — edição documental curada 1.0.0-c2

Cópia documental opt-in, separada dos originais históricos. A edição é
**CANDIDATE**; o kit 0.1.0 CANDIDATE R3 permanece **NOT_ADOPTED**.
A presença dos prompts e ferramentas nesta pasta não os instala, registra ou
adota como instrução do projeto e não modifica o control plane ativo.

Leia o [manual Markdown](1.0.0-c2/MANUAL.md), o
[PDF](1.0.0-c2/publication/Stoikus_Engenharia_MQL5_Manual.pdf) ou o
[DOCX](1.0.0-c2/publication/Stoikus_Engenharia_MQL5_Manual.docx).
O [ponto de entrada](1.0.0-c2/COMECE_AQUI.md), a
[curadoria](1.0.0-c2/CURADORIA.md), as
[dependências](1.0.0-c2/DEPENDENCIAS.md) e o
[histórico](1.0.0-c2/HISTORICO.md) explicam a seleção e seus limites.

A pasta `1.0.0-c2/` contém **213 arquivos**: 212 conteúdos e o
[manifesto](1.0.0-c2/MANIFESTO_CURADO.json). Todos são bytes congelados da
edição `stoikus-documental-curada-1.0.0-c2`, derivada separadamente da C1 T2-R2.
A C2 corrige somente 13 marcadores de formatação em nove Markdown de pesquisa,
com guias e metadados necessários à nova identidade. A derivação está na seção
`revision_c2` de [TRANSFORMACOES.json](1.0.0-c2/curadoria/TRANSFORMACOES.json).
A C1 e a falha da primeira tentativa Git continuam preservadas externamente;
o parecer anterior não aprova os bytes alterados da C2. Este wrapper e
o [contrato da entrega](../../work/CHG-STOIKUS-DOCUMENTAL-CURATED-20261016.md)
ficam fora dessa seleção.

| Identidade | SHA-256 |
|---|---|
| Manifesto integral | `08746937fe7228b5ad7fddaeb052328e683e202a2e7613e23227c45afb3312fa` |
| Conteúdo canônico, excluindo somente o manifesto | `f43f50c9e800a3852f26841df89d52a30788d3b3ea212d26e7b6e7677bab4d17` |

A partir da raiz do repositório, confira a cópia com o pin acima:

```sh
python3 -B docs/knowledge/stoikus-mql5-curated/1.0.0-c2/verificar_edicao.py --edition-root docs/knowledge/stoikus-mql5-curated/1.0.0-c2 --manifest-sha256 08746937fe7228b5ad7fddaeb052328e683e202a2e7613e23227c45afb3312fa
python3 -B -m unittest discover -s docs/knowledge/stoikus-mql5-curated/1.0.0-c2/tests -p test_verificar_edicao.py
```

O verificador usa Python 3 e biblioteca padrão, somente lê e não usa rede.
Retornos: 0 para integridade, 1 para inconsistência, 2 para dependência,
capacidade de plataforma ou I/O indisponível. Os testes usam cópias descartáveis;
seus 37 casos verificam o checker documental. Integridade e testes do checker não
certificam compilação, execução, segurança financeira ou funcionamento do EA.
Um hash comprova identidade de bytes; sua confiança depende da fonte do pin.

Execução **nativa MT5 NOT_RUN**, novo piloto comportamental **NOT_RUN** e teste
do checker no Windows **NOT_RUN**. Resultados e recibos anteriores permanecem
**HISTORICAL_ONLY**; não são testes repetidos por esta cópia. Aceite humano
continua pendente. Commit, PR, merge, deploy e publicação têm estados próprios;
a existência desta pasta não demonstra essas ações.

Os 870 arquivos da origem `docs/knowledge/stoikus-mql5/` continuam preservados
fora deste lote. Livros-fonte, ZIPs, logs brutos, snapshots e provas históricas
externas não integram a seleção. A eventual consulta do kit exige escopo e
autorização próprios; seus textos não ampliam a autoridade do agente.
