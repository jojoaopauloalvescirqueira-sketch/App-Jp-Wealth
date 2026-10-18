# Kit candidato preservado nesta edição

O Stoikus MQL5 AI Harness 0.1.0 CANDIDATE R3 está em `harness-candidato/`, com seus 45 arquivos idênticos aos originais. O manifesto interno conserva **CANDIDATE**, **NOT_ADOPTED**, piloto pré-ensaio **NOT_RUN** e nativo MT5 **NOT_RUN**. Não altere esses bytes para adequá-los a uma narrativa posterior.

Leia [ENTRY.md](harness-candidato/ENTRY.md), [ARCHITECTURE.md](harness-candidato/ARCHITECTURE.md) e [recipes.md](harness-candidato/recipes.md). Contextos, modelos, casos, projeções de entrada e prompts são parte do candidato preservado. Usá-los em uma tarefa exige o escopo e a autorização dessa tarefa; esta edição não instala nem adota o kit.

O checker histórico do kit depende de três raízes. Somente KIT está nesta edição. REPO é um checkout externo com os caminhos de código listados em `harness-candidato/manifest.json`. SOURCES é uma pasta externa contendo os três PDFs com os nomes e hashes de `source-identities.json`; esses PDFs não são distribuídos aqui. Substitua os exemplos por caminhos reais antes de executar:

```sh
KIT='/caminho/da/edicao/harness-candidato'
REPO='/caminho/do/checkout'
SOURCES='/caminho/dos/tres/PDFs'
python3 -B "$KIT/check_harness.py" --kit-root "$KIT" --repo-root "$REPO" --sources-root "$SOURCES"
```

Conforme seu contrato preservado, esse checker usa biblioteca padrão, somente lê e não usa rede: 0 significa integridade estrutural, 1 inconsistência, 2 dependência indisponível. Ele não é o verificador do manifesto curado. Sua execução produz recibo próprio e não constitui novo piloto; a montagem da Task 1 não executou scripts do alvo, o EA ou um novo piloto.

O manifesto congelado do kit tem SHA-256 `004f96cc9a4a094d1dfdeebd803c83ebaf4482d8af07a3d0e1984124ec0328b6`. O manifesto curado autentica também esse arquivo. O resultado posterior registrado em `validation/harness-qualification-R3.json` é **HISTORICAL_ONLY**: os 36 ensaios declarados e seus julgamentos não foram repetidos aqui. A prova bruta completa, os ensaios R2 e os snapshots estão no histórico privado, conforme [HISTORICO.md](HISTORICO.md).

A cópia histórica `harness-next-r3/` e o ZIP antigo do kit foram omitidos. Referências a eles nos arquivos congelados permanecem localizadores históricos externos; não representam caminhos disponíveis nesta pasta. Um futuro piloto exige nova captura e seus próprios recibos conforme o protocolo preservado, sem copiar respostas antigas.
