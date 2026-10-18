# Harness 0.1.0 CANDIDATE — revisão R3

Nova pasta: `/private/tmp/jpw-stoikus-continuity-20261014/docs/knowledge/stoikus-mql5/harness-next-r3`. Cópia controlada da R2; `harness-candidato` não foi alterado. Hash de seu manifesto conferido com harness-freeze-R2.json, coincidência mantida. Capítulo 10 não foi modificado nesta revisão.

## Alterações

1. S01 input agora explicita `handle_required: true`, tanto em cases quanto builder-inputs. Isso remove a ambiguidade da precondição; expected permanece semanticamente idêntico. Conferência programática de expected de todos os 12 casos contra R2: igualdade integral. Demais inputs idênticos. Nenhuma resposta de caso foi construída nesta contribuição.
2. Proveniência R3 exige dispatch_log, dispatch_sha256 e infrastructure_record. Antes de qualquer spawn, operador grava payload externo COMPLETO legível (wrapper, ENTRY, input projetado, target/model, configuração fresh/infraestrutura), calcula SHA-256 e registra horários de gravação/spawn com recibos. Reconstrução posterior não atende. Guia e prompt juiz explicitam que hash sozinho não demonstra anterioridade.
3. `validate_provenance(receipt, evidence_root)` valida conteúdo real do dispatch contra SHA-256 e existência do registro de infraestrutura sob raiz declarada; rejeita caminhos absolutos, traversal, symlink e erros de filesystem de forma controlada. Forma de um argumento continua validação estrutural, claramente identificada. Juiz verifica completude e anterioridade com recibos reais; função não inventa essa prova.
4. Recibos não objeto, unavailable_reasons null/lista, metadados opcionais de tipo indevido e tools_used com elementos malformados retornam erros controlados. Campos desconhecidos opcionais continuam null + justificativa; obrigatórios ausentes continuam INCONCLUSIVE.
5. PILOT exige rodada completa de 36 sessões NOVAS. Resultados R2, incluindo ambiguidade e ausência de captura preventiva em parte da rodada, continuam preservados. Não há aprovação comportamental R3, nem retestes seletivos apresentados como conjunto completo.

## TDD

- `harness-R3-red.log`: 28 testes, três falhas e quatro erros antes das correções. Demonstra fixture sem precondição, dispatch ausente/hash inválido aceitos, AttributeError em razões null/recibos malformados e assinatura sem verificação de bytes.
- `harness-R3-red-types.log`: 30 testes, duas falhas adicionais antes do reforço de tipos de metadados/ferramentas.
- `harness-R3-green.log`: **30/30 PASS**, 0,695s.
- Checker real após novo manifesto: **exit 0 INTEGRITY_OK**, contra os três PDFs originais e repositório declarado.

Testes originais de adulteração, traversal, symlink/loop, dependência ausente, estado inválido e não mutação continuam presentes. Novos testes conferem hash do dispatch por bytes reais, adulteração e escape, além de isolamento das projeções builder e igualdade dos expected.

## Freeze

Recibo externo: `/private/tmp/stoikus-mql5-research-20261015/harness-freeze-R3.json`.
Manifest SHA-256: `004f96cc9a4a094d1dfdeebd803c83ebaf4482d8af07a3d0e1984124ec0328b6`.
Estado: versão 0.1.0, revisão R3, state_revision 1, CANDIDATE / NOT_ADOPTED / native NOT_RUN / behavioral_pilot NOT_RUN.

## Limites e próximo passo

Aguarda revisão independente antes de piloto. Nenhuma tentativa R3 executada; nenhum resultado de modelo fabricado. Integridade estrutural não comprova fresh, independência, sequência temporal dos spawns, julgamento ou comportamento MT5. Logs e recibos reais continuam obrigatórios. Não houve alteração produtiva, fórmula, AGENTS, CI, gates, instalação, autorização operacional, commit, publicação ou capítulo 10.
