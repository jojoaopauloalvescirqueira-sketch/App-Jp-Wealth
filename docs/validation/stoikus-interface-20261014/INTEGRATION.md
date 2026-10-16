# Stoikus — interface MT5 — candidato local R3

Plano aprovado em 2026-10-14. Fontes **1.22.2**, MQL **1.222**, cálculo **1.9.0**. Revisão privada **1.22.2-interface**; não representa versão publicada. Base Git `0037bd3c8a7ab2b4e21f7fdcb60f66ed93230874`, mais o delta não commitado na branch `codex/stoikus-continuity-20261014`, em `/private/tmp/jpw-stoikus-continuity-20261014`. A base efetiva da UI é o snapshot do candidato de continuidade já autorizado, não o Git HEAD isolado.

## Mudanças e evidência

Conta recebe resumo com prioridade para alavancagem e risco, áreas clicáveis dimensionáveis, detalhes por seção e adaptação a gráficos estreitos. Alavancagem descreve a conta inteira; risco ao stop descreve o grupo atribuído por símbolo e direção, com percentual sobre saldo e origem conservada. Histórico oferece seletores explícitos e estados distintos de leitura, auditoria, vazio concluído e falha. NoCuda inicia em Compacta para novas configurações e apresenta estado, motivo e próxima ação fora da rolagem, com fluxo selecionar canal → conferir prévia → confirmar vínculo. Recolher mantém indicador e desenho. Preferências válidas, máscara 0, índices, teclas 1–7 e gates são preservados.

A prévia autocontida tem dados fictícios, dois temas e dois gráficos representados; **51/51** verificações de browser R2. Não é screenshot nem execução MT5. A tipografia planejada usa 10 pt no resumo e 11 pt nos painéis; geometria medida, DPI aplicado uma vez e regiões de 36 lógicas são conferidos por testes host. Renderização, foco e cliques reais dependem do ensaio nativo.

Revisões por entrega e revisão integral são independentes da implementação, com contexto e identidade conhecidos; não são avaliações cegas. R1 encontrou dois P2 e um Minor; todos foram corrigidos e o parecer final R3 registra **spec/qualidade de fonte PASS**, sem novo defeito demonstrado. NoCuda agora orienta Conferir fonte com justificativa durante conflito histórico; Retomar conserva a recusa existente. HUD usa botões nativos nos IDs antigos, com regiões reais, fallback sem valor numérico quando não cabe, migração de tipo e limpeza de objetos próprios.

| Evidência | Resultado e limite |
| --- | --- |
| Host baseline anterior à UI | 42/42 PASS, histórico deste trabalho |
| Host R1 | 46 PASS / 1 PRODUCT_FAIL; expectativa antiga de fonte 8; preservado |
| Host R2 | 47 PASS / 1 PRODUCT_FAIL; expectativa lexical antiga de espaçamento/âncora; preservado |
| Host final R3 | **48/48 PASS**, 413 inputs da suíte e 415 do freeze estáveis; oráculos financeiros preservados |
| HUD novo | 8.192 cenários, 366.634 verificações / 0 falhas; quatro DPIs, fontes 8/10/24/40, 128 máscaras e quatro tamanhos de gráfico sintéticos |
| NoCuda focal | controller 41/41 e UI 68/68; 13 corpos críticos byte-idênticos |
| NoCuda anterior | controller 85/85; UI 549.062 verificações / 0 falhas em 1.536 cenários sintéticos |
| Adaptador lexical | original aceito e nove mutações recusadas; replay financeiro/geométrico mantido |
| Preservação | 196 arquivos protegidos, incluindo 8 ZIPs anteriores; dados, oráculos, site e downloads públicos não mudaram neste escopo |
| ZIP privado de uso | 83 entradas; identidade, hashes e reprodução local conferidos; não contém EX5 |
| Kit Windows/PowerShell | fonte/bytes exatos aprovados na revisão independente R4; execução Windows NOT_RUN |
| MetaEditor, MT5 e instalação demo ARM | **NOT_RUN** |
| Windows x64 independente | **NOT_RUN**, ambiente indisponível |
| Aceite do proprietário | **NOT_RUN**, ensaio dos dois gráficos pendente |
| Site, instalador, commit/push/merge/publicação | fora desta entrega; sem novas ações |

## Identidade exata R3

- Runtime build: `1bc02d97bdf034e824df726debb7087193a9fbb7cc1ebbad3c15dc7e83894100`.
- Fingerprint MQL: `33a981e42cd741a2c3db57e496ad63f36465180f08f166649e10b897cd21c15b`.
- Fingerprint interface: `7855ecbb158fbfcdd017449943371570349caa929979c279c9bea4b07fd2a63e`.
- Freeze R3 SHA-256: `735acfe5c7413b8e261506d35a4379bda0b12b9e6dcdfd19628ce0e0937650e6`.
- Recibo host R3 SHA-256: `7ddcafc6fc42f494a8c9987410c00efad243e35a0973d21a64ca58401de1c9ef`.
- ZIP de uso privado SHA-256: `30399033a29403ab2d9c84cb799ae872a1acf312b7e2bcb0e10a6dacce70b183`.

R2→R3 mudou somente o adaptador de teste versionado: todos os MQL e o ZIP privado ficaram byte-idênticos. O hash de interface/host mudou por incluir esse teste. Não houve promoção do manifesto público. Recibos anteriores 1.22.2, grafo focal e pacotes publicados representam seus próprios bytes; não aprovam a UI nova. A versão financeira 1.9.0 é preservada neste escopo, sem declarar homologação operacional.

## Ensaiar no Parallels

O proprietário confirmou MT5 separado para testes e fará o ensaio como iniciante. Caminhos exatos, build, pasta de dados separada e conta demo continuam por conferir. A licença usada não permite `prlctl exec`; não houve contorno nem acesso automático comprovado ao guest.

O kit usa a sequência pin externo e SHA-256 → fixtures PowerShell sintéticas → compilação dos quatro programas em staging temporário → revisão do `results.zip` → ensaio na instalação demo separada. Não inicia terminal, envia ordens ou instala EX5. O guia interno do ZIP privado direciona a essa sequência e contextualiza as instruções genéricas do pacote padrão. O proprietário deverá observar identificação dos quatro componentes, Monitor no gráfico de apoio, Conta+NoCuda no gráfico de trabalho, sete métricas, seletores do Histórico, bloqueios, vínculo do Canal Fibonacci de três âncoras, foco/teclado/DPI e recolhimento com desenho preservado. Windows ARM sob emulação não substitui um Windows x64 independente.

## Arquivos e continuidade

Ledger, snapshots, RED/GREEN, três freezes, logs completos e pareceres ficam em `.superpowers/sdd/2026-10-14-stoikus-interface/`. A entrega durável copia fontes/testes, prévia, kit e evidências para `/Users/joaoalvescirqueira/.codex/visualizations/2026/10/12/01a13231-0786-7d03-82d0-0eb0231584dd/stoikus-interface-20261014/`. O relatório de entrega e os pins do kit têm hashes próprios. O fechamento documental é registrado em `documentation-final-delta.json`; não altera os inputs da suíte. Fotografias anteriores dos documentos focais permanecem completas após o separador.

## Kit final para entrega local

O parecer independente `native-kit-review-R4.md` aprova somente fontes e bytes exatos do kit. NK01–04 foram corrigidos: guia interno contextualizado, comandos completos de hash, fixtures Windows antes da compilação e vínculo obrigatório do recibo à origem/freeze/ZIP/quatro fontes antes de copiar EX5. O código PowerShell ainda não foi executado no Windows. Os testes de predicados do guia são modelos host declarados, não prova do intérprete PowerShell.

- Kit final, nove arquivos: `c584076a3b1450bb5c0e0a17aaefce903291737a2c245833860942d10286ef97`.
- Pin externo R3, entregue fora do ZIP: `2a5efa5843b9f54304db3a99dd04ed64ec32e4b7d8800e53dd48b4e0c7a502e3`.
- Parecer independente do kit: `df01b13c860d3c436b61a869ee4cc91b200727e187536941f1873439d4aa3b23`.

O pin registra o momento da selagem; a revisão posterior acima conserva esses bytes e tem prova própria. O selo anterior ao vínculo do recibo está preservado em `R3-pre-receipt-binding/`. A entrega contém o kit corrigido. Não contém EX5 nem executou instalação.
