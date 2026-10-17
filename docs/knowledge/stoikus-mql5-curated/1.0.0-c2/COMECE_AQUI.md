# Stoikus — edição documental curada

Esta é a edição `stoikus-documental-curada-1.0.0-c2`, preparada em 16 de outubro de 2026. Reúne o manual 1.0.0, a pesquisa documental e o kit 0.1.0 CANDIDATE R3. O kit permanece **NOT_ADOPTED**; execução nativa MT5 e novo piloto comportamental nesta edição permanecem **NOT_RUN**.

A C2 deriva da C1 selada e remove somente sete espaços finais e seis linhas vazias de EOF em nove Markdown de pesquisa, para cumprir o gate de formatação Git. A derivação e os hashes estão na seção `revision_c2` de [TRANSFORMACOES.json](curadoria/TRANSFORMACOES.json). Manual, PDF, DOCX, figuras e os 45 arquivos do kit permanecem idênticos. A C1 e sua primeira falha de formatação continuam no histórico externo; a aprovação anterior não é transferida automaticamente para os bytes alterados.

Para ler, abra [MANUAL.md](MANUAL.md), o [PDF](publication/Stoikus_Engenharia_MQL5_Manual.pdf) ou o [Word](publication/Stoikus_Engenharia_MQL5_Manual.docx). Os três formatos e as três figuras foram preservados byte a byte. Os capítulos em `chapters/` e a abertura e referências em `editorial/` também foram conservados.

Para entender a seleção, leia [CURADORIA.md](CURADORIA.md), [DEPENDENCIAS.md](DEPENDENCIAS.md) e [HISTORICO.md](HISTORICO.md). O [manifesto desta edição](MANIFESTO_CURADO.json) identifica seus arquivos. O manifesto de 865 entradas do snapshot original continua externo; a seleção atual tem manifesto próprio e não promete incluir os 866 arquivos históricos não-cache.

Para consultar a pesquisa, comece por [research/LEIA_ME.md](research/LEIA_ME.md) e [research/INDEX.md](research/INDEX.md). São documentos históricos: suas declarações de leitura não foram refeitas na curadoria. A edição conserva os 92 arquivos da pesquisa e seus localizadores; retira 83 campos de extratos de `neural-coverage.json` e substitui três caminhos pessoais por localizadores genéricos. Veja [o índice atual](curadoria/INDICE_PESQUISA_ATUAL.json) e [as transformações](curadoria/TRANSFORMACOES.json). Os hashes nos recibos de pesquisa preservados identificam originais históricos, inclusive quando a cópia curada foi alterada.

A consulta abaixo usa somente o catálogo e as notas locais, com Python 3 e biblioteca padrão. Execute a partir da raiz desta edição:

```sh
python3 -B tools/query_sources.py OnInit --book REF
```

Para conhecer o kit, leia [LEIA_ME_KIT.md](LEIA_ME_KIT.md). Seus 45 arquivos são bytes congelados; prompts e instruções ali presentes são material documental opt-in. A entrega desta pasta não os ativa em projeto algum.

Os arquivos selecionados em `validation/`, `RELATORIO_FINAL.md` e `IMPLEMENTATION_PLAN.md` são **HISTORICAL_ONLY**. Registram o contexto, resultados, falhas e limites da entrega anterior. As tentativas, logs, registros opacos, capturas, snapshots, recortes e renders citados neles permanecem fora desta edição. Um resultado histórico, incluindo 36/36 PASS declarado na R3, não equivale a um piloto executado ou auditado novamente aqui. O produto 1.23.0/R5 integrado separadamente não qualifica esta edição documental.

O verificador específico desta edição está incluído em `verificar_edicao.py`. Seus critérios são os da C1; somente o identificador esperado foi atualizado para C2. Os 37 testes foram preservados byte a byte. Execute na raiz desta edição:

```sh
python3 -B verificar_edicao.py --edition-root .
python3 -B -m unittest discover -s tests -p test_verificar_edicao.py
```

O verificador usa biblioteca padrão, somente lê e não usa rede: 0 significa integridade, 1 inconsistência, 2 dependência ou I/O indisponível. Por padrão a raiz é a pasta do próprio script. Para conferir o manifesto contra um recibo externo confiável, acrescente `--manifest-sha256 HASH_DO_RECIBO`. Um hash confere identidade de bytes; não autentica sozinho autoria ou confiança. Integridade estrutural não comprova compilação, operação do EA, adoção, publicação ou aceite humano.
