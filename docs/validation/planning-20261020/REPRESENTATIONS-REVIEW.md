# Revisão A0 final — representações e oráculos — 20/10/2026

Resultado: **SEM BLOQUEIO DEMONSTRADO NO RECORTE ESTÁTICO SOLICITADO**.

Escopo: ajuste do oráculo de carga/cache em `tools/learning_guide_test.py`, rota descritiva em `docs/governance/CONTEXT-MAP.md` e inspeção de semântica financeira evidente nos textos atuais da UI. Não é nova auditoria integral, aceite humano ou homologação da planilha.

## Evidência direta

- Comparei integralmente o teste e o mapa atuais com seus membros originais em `.superpowers/sdd/planning-20261020/baseline.tar.gz`, usando extração somente para stdout e diff. Não executei código do produto, o teste ou os controles negativos.
- Em `learning_guide_test.py:677–719`, a igualdade scripts reais/manifest continua obrigatória. Os três novos caminhos formam bloco único, completo e ordenado após o guia; as cinco identidades aposentadas são proibidas. Após retirar somente os novos três, os cinco antigos são reconstruídos no slot original depois do serviço USD/BRL para aplicar o mesmo SHA de 106 caminhos (`40a619eac3b449f7e0704d8aa2be46f38280902d0340f961e898057d22b36c82`). Ordem/identidade dos demais scripts e guardas de download/jogos/market-hours permanecem verificadas. O ajuste das contagens corresponde à retirada explícita dos cinco; não há exceção genérica por pasta nem remoção do hash legado.
- `SOURCES` passou a incluir os três arquivos patrimoniais no registro antes/depois. Em `offline():743–745`, a presença do novo namespace exige os três caminhos no cache, mantendo a verificação dos quatro módulos do guia. A condição conserva a execução sobre a distribuição anterior; não foi removido o oráculo legado.
- O diff integral do mapa mantém as demais seções. A rota Forex conserva leitura M0/M2, a ausência de homologação V11 e proteção de bloqueios/unidades/histórico/estados. A nova rota descreve contrato PLANNING, agregado independente e ausência de migração automática; não promove perfil hipotético a norma nem confere autorização. A atualização de cabeçalho marca a fotografia anterior como histórica e o candidate local como tal. O build descritivo `ff0f078f70b9fb97` coincide com a linha de identificação de `build-id.js` lida. O CHG lista o teste e o mapa no escopo permitido; essa lista não foi usada como autorização adicional.
- Nos trechos UI atuais, “Renda mensal” corresponde às metas por primeiro resultado mensal; o resultado é descrito como total USD que substitui o anterior e exclui fluxos; adiar a parada não restaura os zeros. Essas descrições são coerentes com os motores/fonte já revisados. O foco da prévia e `flex-shrink:0` nos controles não introduzem regra financeira evidente. Esta revisão não afirma uma comparação exata de todo o delta UI/CSS contra os bytes R3, pois esse snapshot anterior não foi usado no diff.

## Identidades observadas

| Entrada | SHA-256 |
|---|---|
| learning_guide_test.py atual | 0fa600b379eb0f5e13ee831da66efeedbdf45e0586173e188e5bae0b0c17894b |
| learning_guide_test.py no archive | 029cae60d7bf127dede8ae35b5a8388c8a50ce56186b2844215f3fd1a2881b68 |
| CONTEXT-MAP.md atual | 6c264f6b28c115d72997f2775491fa7c39c8d8da79b0340d0c87ae036ded8f60 |
| CONTEXT-MAP.md no archive | 196b8a1860bd43b3886ae30e283d5c0d04428c68d3e28b8c18d9cdfdd23803fc |
| baseline.tar.gz | 6222a8f92927d2198ce4f277c0b411deaac5028bc1d31f76ed2d6cf2773a2165 |
| 03-ui.js atual | 29cb17e80a677ad768e77c3f402c96b8122b86b1d9ac5e5c144d83c77a55e7d7 |
| app.css atual | b45711801a1a89b14abf798f1f19bd58e46cd189adadc9dadf0c481b9a2326b8 |

Os quatro alvos atuais mantiveram esses hashes entre início e fim da leitura. Engine `4ee816dc6f1e1e12517a62bdc104fe49c03cffcd7aaad6eb0fcafe1cbca03953` e state `c3df0b959be15a83e119f01c69fe8a8ade5d48292a24efcde855c8695e060f0f` permanecem idênticos à revisão financeira R3.

## Limites

Doutrina de revisão local pr-audit1.4.1 e referências efetivamente carregadas nas rodadas anteriores continuam aplicáveis. A leitura do archive fornece uma comparação de bytes; não é prova independente de sua origem Git.

Execuções próprias nesta rodada: **NOT_RUN**. Os cinco controles negativos, as contagens UI/combinações e os FULL da raiz não foram tratados como execuções deste auditor. Primeiras falhas, novos resultados e validade do gate completo devem permanecer nos recibos próprios da raiz. Sem Gitops, rede, alteração de fontes/testes ou delegação. Única escrita: este recibo ignorado. Aceite humano, operação nativa Sheets e publicação não observados.
