# Revisão independente — FULL6

Parecer factual de 28/10/2026, após conclusão da tentativa 6. Revisão A0 de arquivos, hashes, recibos e declarações do catálogo; nenhum teste, navegador, operação Git, gerador ou controle de processos foi executado por esta revisão. A única escrita é este arquivo novo. As revisões anteriores permanecem preservadas.

## Conclusão delimitada

**A tentativa 6 terminou com 116/116 PASS e saída 0.** Não foram encontradas divergências entre o recibo, o catálogo congelado, as fontes atuais e as evidências abaixo. Essa conclusão confirma o resultado automatizado desta execução; não declara prontidão integral, aprovação universal, aceite humano ou resolução das causas históricas.

Início: 28/10/2026 às 10:21:39; término: 11:15:24, America/Sao_Paulo. Branch registrada `codex/mesas-proprietarias-hedge-20261027`, HEAD `3e24f60f8cfe87f79335f40e95a0927379a9f834`, build `09cfa4f7b8a8dbed`.

## Recibo e catálogo

- `full-final.json` e `full-attempt6-116pass.json` são idênticos. SHA-256: `71e550b99f2a3b2ca58eea8d183ceb1e6bf1a99c20c9e376b2e87bdd9353b80f`.
- Foram conferidos os 116 IDs únicos, todos com resultado PASS e returncode 0. Os 113 IDs anteriores permanecem na mesma ordem, com as três adições Hedge aprovadas.
- Os 116 comandos, incluindo argumentos, caminhos de evidência e opções de zoom nativo, correspondem exatamente às declarações FAST/STANDARD/FULL do `quality_gate.py` congelado, após substituir somente os caminhos do runtime e do diretório de evidência registrados na execução. A comparação avaliou apenas essas declarações por AST; não executou o runner.
- `full6-exit.json` confirma saída 0 e conclusão às 11:15:24.723826. Comando e PIDs de supervisor, gate e guard correspondem à supervisão registrada.
- `full6-supervision.json` documenta as asserções de prevenção de suspensão ociosa do sistema/tela antes do gate, vinculadas ao supervisor. Isso não equivale a observação contínua de todos os estados do sistema.

## Integridade e preservação

Confronto direto com os arquivos atuais:

- **1.621 inputs de `freeze-attempt6.json`: nenhuma divergência.**
- **86 caminhos protegidos: nenhuma divergência.**
- **3.310 arquivos do baseline: nenhum ausente.** Os 28 caminhos com bytes alterados correspondem exatamente à lista já auditada no FULL5; não apareceu alteração adicional em arquivo baseline.
- Os hashes das cópias documentadas em `full6-evidence/preservation.json` e dos **1.144 arquivos de evidência** no diretório da tentativa foram conferidos sem divergências. O manifesto referencia o diretório completo; não significa que todos os 1.144 arquivos foram duplicados dentro de docs.

SHA-256 do freeze: `5a682d917f76bc9cd759611972d335ab7429f70a0d73cf60243e3f8110967384`. SHA-256 da supervisão: `a9c4850dc6e38469832fc54f52196ee69510cd7949cc55dca1fdc833584e5701`.

## Evidências técnicas conferidas

- Engine Hedge: o stdout desta rodada registra **15/15 casos e 4/4 contraprovas**.
- Browser Hedge: **12 grupos, 80 combinações, cinco contraprovas rejeitadas e oito combinações de zoom nativo 200% aprovadas**. Medição nativa outer=1440, inner=720, CSS zoom=1. Fontes e bytes estáveis.
- Distribuição Hedge: quatro casos aprovados — HTTP, arquivo local, portátil e PWA controlada offline. Fontes e bytes estáveis.
- Qualidade visual: **413/413 casos PASS**, IDs exigidos exatos e únicos, tolerância de 2 CSS px preservada, fontes inalteradas e zoom nativo registrado. Os hashes registrados correspondem aos arquivos atuais.
- Recibo HTTP `preview-identity-final6.json`: quatro recursos com HTTP 200 e igualdade local registrados pelo executor. Seus hashes correspondem ao candidato; esta revisão não repetiu a requisição nem declara disponibilidade futura do servidor.

Essas evidências não homologam toque físico, leitores de tela, Safari ou uso operacional real. A revisão matemática e de produto anterior mantém seu recorte próprio; este parecer não a substitui por mera contagem de testes.

## Histórico e limites causais

FULL4 conserva 113 PASS/3 PRODUCT_FAIL; FULL5 conserva 114 PASS/1 PRODUCT_FAIL/1 TEST_HARNESS_FAIL. Seus recibos brutos não foram reclassificados. No FULL5, W6 falhou em goto/load; isso é distinto do clique I4/I5 do FULL4. A suspensão documentada em Planejamento não comprova automaticamente o mecanismo de todos os timeouts.

**Epoch e Alladin permanecem OPEN_CAUSE_UNCONFIRMED quanto às ocorrências históricas.** O sucesso desta rodada e dos focais anteriores não identifica essas causas, não constitui correção demonstrada e não aplica exceção retrospectiva. Aceite visual humano continua pendente. Não houve declaração de prontidão geral, commit, merge, push ou publicação nesta revisão.

## Revisão do gerador documental

Examinado estaticamente `/private/tmp/jpw-hedge-prop-20261027/prepare-delivery-attempt6-corrected.py`, SHA-256 `01a8574cd35493f76942d376cb82fe3dd96754e6ecf040b8f875f3b49501830f`. Não executado, inclusive sem `--write`.

Não foi encontrado bloqueador para sua geração documental delimitada sobre os recibos auditados. Ele verifica identidade da tentativa, saída do supervisor, contagem/classificações, congelamento, protegidos, presença do baseline e histórico antes de escrever somente README.md e FINAL-AUDIT.json. O conteúdo proposto mantém `overallReadiness=NOT_DECLARED`, aceite humano pendente e incidentes históricos abertos. Esta conferência não transforma o script em certificador genérico; a comparação exata dos 116 comandos e a auditoria das evidências foram realizadas separadamente nesta revisão.

Observação documental não impeditiva: a versão examinada ainda não inclui este parecer FULL6 na lista de links/hashes; convém ligá-lo na entrega final para distinguir a auditoria atual da revisão preliminar.
