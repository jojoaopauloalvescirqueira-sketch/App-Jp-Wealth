# Validação da integração Stoikus 1.23.0/R5

O candidato mantém cálculo 1.9.0 e os mesmos 139 fontes da entrega selada R5. Web build: `a4672bde6f6e8965`. Base main: `2b22175a4f3f47b1f289deca65366c4dc0445dca`.

## Resultado local

- `leverage_suite.py --scope all`: **54/54 PASS**, nenhum outro resultado.
- `quality_gate.py --tier full`: **75/75 PASS**, nenhum outro resultado.
- MiniGames: interface, guia, arquivo local, portátil e PWA offline aprovados.
- Regressões complementares R5 de HUD, janelas, texto, pacote e kit aprovadas; compilação e interação nativa não foram inferidas da bancada host.
- Distribuição R4/R5: 18 controles positivos/negativos; entrega web 40/40; carregador 26/26; guarda de recursos externos 84/84.
- SDK e uso diário reproduzidos byte a byte; checkout limpo reconstruído; históricos e oráculos financeiros preservados.
- Revisões independentes de distribuição, web e integração realizadas; duas pendências documentais corrigidas e verificadas. Cinco avisos históricos de whitespace permanecem documentados, sem alterar arquivos selados por estética.

[Resumo verificável](local-gates-summary.json) registra nomes, resultados e hashes dos recibos. A árvore testada é `a82726bbe41274a5b92eaf05007f09afd8485152`, com 1.149 arquivos regulares congelados. Depois dos gates, somente este diretório informativo de evidências é atualizado; fontes, testes, pacotes e build permanecem idênticos.

## Tentativas e limites

As primeiras execuções registraram 53/54 por timeout de HUD sob carga concorrente e 73/75 pela ausência da variável de Chromium. Os resultados brutos foram preservados; a aprovação vem das novas execuções completas, com critérios originais. O atraso observado no Dashboard terminou em PASS; sua causa não foi determinada. Um recibo de congelamento recebeu correção rastreada do fingerprint agregado, sem mudança de seu mapa de arquivos.

SDK SHA-256: `65ed7e2cb6f9fe680695ef67e47eb9aa873a66e2bfd214c1ebd71a41367fcf63`. Uso diário: `0bc6c856410b576ebf0412aa341056e8e02463c8f848fe34d2bd4e983ae5f7a3`.

Compilação, instalação, execução/interação MT5, aceite humano e Windows x64: **NOT_RUN**. GitHub CI e merge têm provas próprias posteriores ao commit. Esta entrega não publica GPT Sites nem altera instalador. A correção F01 e o manual/corpus MQL5 permanecem separados. Evidências completas e tentativas preservadas na entrega durável `stoikus-integracao-git-20261016` fora do repositório.
