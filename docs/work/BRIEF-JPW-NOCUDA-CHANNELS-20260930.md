# Brief — JPW NoCuda Channels

## Identidade e fronteira

Em 2026-09-30 o proprietário aprovou expressamente a implementação do plano “JPW NoCuda Channels”. Raiz `/private/tmp/jpw-cockpit-ui-20260930`, branch `codex/jpw-cockpit-ui-20260930`, HEAD de base `deffc5061fe2eff3d83b6f6e742fa105ac9c5b06`. Há 20 caminhos preexistentes modificados pela revisão local 1.10.2. O snapshot externo `outputs/jpw-nocuda-channels-20260930/baseline/BASELINE.json` guardou esses bytes e confirmou 48/48 fontes do pacote, antes do primeiro código novo. Risco N2/A3 pela nova persistência SQLite, autorizado pelo pedido atual; CHG `CHG-JPW-NOCUDA-CHANNELS-20260930` delimita o produto. Nenhuma ação Git ou instalação operacional foi autorizada.

## Compreensão e fontes

1. JP Wealth fornece ferramentas locais de análise e disciplina de risco; o NoCuda solicitado ajuda a desenhar e medir uma geometria de estudo no MT5, sem afirmar eficácia ou autorizar negociação. Fonte: `docs/governance/PROJECT-CONTEXT.md` §Produto (revisão histórica identificada ali) e pedido humano vigente.
2. O novo indicador pertence a `mt5/jpw-alavancagem-atual/MQL5/Indicators/JPWealth/`; núcleo, leitor de candles, desenho e SQLite ficam em `MQL5/Include/JPWealth/`. O site `index.html` e o manifesto distribuem fontes; `tools/build_leverage_package.py` gera ZIP determinístico. Fonte: estrutura/gerador lidos na base acima.
3. Hoje há `downloads/nocuda/Nocuda_Tool.mq5` com malha antiga A/B=1, C=0, preço livre e gravação em redesenho. O novo indicador usa A/B=0, C=1, Close H1 por padrão, rascunhos confirmados e revisões imutáveis; não migra nem altera o tool antigo. Fonte: leitura do arquivo antigo e plano aprovado.
4. Afetados: apenas estudos geométricos locais, objetos próprios do novo indicador, README/site/pacote. O Cockpit e EA coexistem mas seus cálculos/objetos/dados permanecem independentes.
5. Invariantes: 65 níveis de −4 a +4 em 1/8, deslocamento com sinal, barra fonte concluída, horário/fechamento verificável, sem horas confundidas com contagem de candles; C não é confirmação independente, não há sinais/probabilidades. Tratar ausente/corrupto/incompatível como indisponível, sem zerar ou regravar. Nenhum USC em preço/distância.
6. Evidência: testes do núcleo de produção para casos M/G e extremos; testes de SQLite e ciclo criar/editar/cancelar/conflito; site/manifesto/ZIP; regressões Cockpit e full bruto. Compilação, interação, DPI e template dependem de MT5 isolado; sem ele `NOT_RUN`.

| Fonte | Revisão ou hash | Acesso e uso |
|---|---|---|
| Artigo `artigo_nocuda_integral copy.pdf` | SHA-256 `274a8921796eb9824816db9a21dd6be9299f68ae166b0b06c6346ef332fd6168` | Lido como fundamento de construção H1; equações e experimentos não são validação de eficácia. |
| Harness externo no caminho atual `2 - TRABALHO/99A -   SOFTWARE DEV/99 - PROMPTS SOFTWARE DEV/` | SHA-256 `b5680c22e44cf3f4a5cd3aa5deeb96f8b65c7908f14543e8c5d7f0c2f4e17b95` | §§12–16, 24, 28–30, 36–48 lidas para contrato, freeze e testes. O link antigo em `AGENTS.md` está desatualizado; este brief não o altera. |
| `downloads/jpw-alavancagem-atual/manifest.json` | versão 1.10.2, 48/48 hashes conferidos | Fonte para arquivos distribuídos; compilado indisponível. |
| `docs/architecture/NOCUDA-TRANSFER.md` e `downloads/nocuda/Nocuda_Tool.mq5` | HEAD deffc506 | Contrato antigo incompatível; preservar. |

## Delta e rollback

Separar cálculo puro, leitura H1/TF explícito, interação, desenho e SQLite. `Confirmar` é a única ação que cria revisão; `Cancelar`, tick, zoom, scroll e mudança de período não gravam. O servidor/feed, símbolo exato e período-fonte compõem a identidade; mudança de contexto invalida a apresentação anterior. A futura revisão fica oculta até seleção explícita. Pips exigem símbolo/tamanho configurados.

Usar dados sintéticos e diretórios isolados nos testes. Contrato de dados novo e exclusivo, sem migração de estudos antigos. Em falha, manter rascunho e última revisão confirmada, apresentar causa e não anunciar salvamento. O rollback restaura fontes/derivados da baseline externa e deixa registros financeiros e estudos do usuário intactos.

Delegação: núcleo/testes, SQLite/testes e README/site em arquivos disjuntos; integração e renderer são responsabilidade da tarefa principal. Nenhum agente delegado pode alterar AGENTS, gates, arquivos financeiros ou executar Git mutável.
