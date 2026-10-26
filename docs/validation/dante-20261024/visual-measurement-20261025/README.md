# Medição visual — resultado final de 25/10/2026

**Validação técnica aprovada: FULL com 102/102 checks PASS, todos returncode 0 e processo exit 0.** A matriz visual desta mesma execução concluiu **413/413 casos**, em **868,509 s**, dentro do limite original de 900 s. Não houve dispensa, redução de critérios ou combinação de focais para aprovar o FULL.

Produto `8c127c2f92de375e`; branch `codex/dante-guia-20261024`; HEAD `a4bf278cd4dc38bbaa5b905ed17a79e33684fb67`. O recorte de otimização não alterou bytes do aplicativo, dados ou regras financeiras. As alterações anteriores do candidato foram preservadas.

## Provas e critérios

| Evidência | Resultado observado |
|---|---|
| [FULL oficial](full-relocated.json), [log](full-relocated.log), [comando e exit](full-relocated-command.json) | 102 PASS, zero falhas/NOT_RUN, exit 0; 2.789,102 s no total. Todos os IDs, ordem e comandos anteriores foram preservados, normalizando apenas a raiz de saída. |
| [Matriz visual própria do FULL](full-ui-visual-results.json) | 413 PASS; mesmos IDs, ordem, matriz e tolerância de 2 px. O próprio gate continuou limitado a 900 s por check. |
| [Focal completo](visual-all-results.json) | 413 PASS, exit 0 em 878,249 s; execução independente do FULL. |
| [Integridade de execução](execution-integrity.json) | 681 inputs congelados sem divergências; 161 fontes visuais iguais entre focal, FULL e disco. |
| [Revisão independente final](FINAL-INDEPENDENT-REVIEW.md), [auditoria](final-independent-audit.json) | PASS técnico do recorte, sem achados Critical/Important materiais; não equivale ao aceite humano. |
| [Delta e focais](task-1-report.md), [revisão do patch](task-1-independent-review.md) | Coleta agrupada após os mesmos scroll e dois frames; medidas e decisões equivalentes. Quatorze contraprovas permanentes e os critérios anteriores preservados. |

A comparação controlada mediu **8 → 4 chamadas ao navegador por botão**, em três controles sintéticos e doze controles reais do Planejamento. O RED do orçamento foi observado antes do patch; o GREEN posterior e as contraprovas foram executados em navegador real. Digitação e consultas de teste não acionaram writers financeiros. A nova fonte do helper entrou no fingerprint visual: 160 → 161, sem remover fontes.

O focal histórico anterior levou 853,471 s. Portanto, a redução de chamadas está comprovada, mas **não foi demonstrado ganho garantido no tempo total**, nem causa no CloudDocs/I/O. [Medições descritivas](performance-descriptive.json). O uso do snapshot é privado, imediato e restrito a controles estáveis do documento principal; não é uma autenticação pública de dicionários arbitrários.

## Execução, preservação e limites

A [autorização específica e o contrato](../../../work/CHG-JPW-VISUAL-MEASUREMENT-CONTROLS-20261025.md) delimitam os dois arquivos de ferramentas e estes registros. O runner oficial permaneceu intacto. O [mapeamento temporário revisado](redirection-mapping.json) atingiu somente a pasta nova, vazia e própria desta execução; os artefatos anteriores foram preservados. [Avaliação de impacto](AGENTIC-IMPACT.md).

A correção de ciclo de vida do calendário e o Dante passaram novamente no FULL: agenda 14 casos, recuperação 8, distribuição 4 e guia 66, incluindo 14 do Dante. HTTP, offline, arquivo local e portátil têm recibos nos checks correspondentes; isso não estabelece aceitação visual universal.

As rodadas anteriores com timeout, a interrupção deliberada, o RED comportamental e os erros de preparação continuam nos seus arquivos originais, com classificações brutas. [Estado anterior desta onda](README-before-final.md). O novo resultado não encerra automaticamente incidentes históricos nem promete ausência de futuros timeouts.

**Mac liberado após o encerramento das janelas.** Prévia local: [abrir JP Wealth](http://127.0.0.1:51629/index.html?v=8c127c2f92de375e). Aceite visual, reconhecimento/fidelidade do Dante, compreensão das falas, Safari, leitor de tela real e toque físico permanecem pendentes. A entrega continua local, sem commit, merge, push, publicação ou configuração de memória global.
