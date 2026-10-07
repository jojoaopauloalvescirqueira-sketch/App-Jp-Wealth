# Matriz de salvamento, backup e recuperação

Candidate local 2026-10-06. A [matriz CSV](SAVING-COVERAGE.csv) possui 139 atributos/grupos explícitos. Caminhos funcionais resumem famílias; não constituem novos schemas. O Backup Completo exporta o documento confirmado integral, inclusive extensões compatíveis desconhecidas, e sua cobertura enumera as chaves efetivamente presentes.

| Camada | Fonte e responsabilidade | Recuperação |
|---|---|---|
| Fatos confirmados | documento localStorage jpwealth_v9_state; único escritor verificado | Backup Completo v2 com checksum e cobertura; legacy explícito |
| Preferências | 21 chaves auxiliares e tema na base | workspace separado; validação, journal e readback |
| Edição pendente | mapas do módulo e campos rastreados, contexto e base original | captura separada; revisão e reabertura sem comando quando compatível |
| Originais importados | IndexedDB jpwealth_evidence_v1, por SHA-256 | ZIP separado; manifesto, limites e transação |
| Autorização de pasta | handle IndexedDB e permissão do navegador | não portável; conceder novamente |
| Recursos do programa | documentos normativos, fontes e ZIP MT5 distribuídos | pertencem à distribuição, não aos dados pessoais |

CONFIRMED exige releitura exata. REFUSED comprova ausência da escrita pretendida. UNKNOWN representa escrita possível sem conferência, impede retry cego e não prova preservação da base anterior. O adaptador booleano save retorna true/false apenas para confirmado/recusado; UNKNOWN é erro tipado.

A matriz cobre conta, período, operação, ordem, SL/TP, moeda, fase, histórico, revisão, lançamentos, reservas, planejamento, realizados/finalizações/reaberturas, Finanças Pessoais, Alladin, estudos, Notas, perfil/foto, navegação/widgets, notícias, laboratório, governança e recibos. Projeções e estatísticas derivadas não se tornam fatos novos durante captura.

Rascunhos de perfil, Notas, planejamento, Board, navegação, widgets, campos PF e transferência NoCuda têm adaptadores próprios. Estudos Research possuem captura estruturada; formulários que não possam ser reconstruídos com segurança ficam para consulta/cópia, com motivo. Fragmentos de RAM não confirmada e preferências incompatíveis nunca são aplicados automaticamente. Um reload comum não promete recuperar memória que não foi exportada.

Não entram: senha em texto, handle/permissão, caches públicos, foco/rolagem, bolas/simulação em andamento, abas do navegador. Originais ausentes antes desta revisão não são inventados; o usuário pode reassociar uma cópia cujo hash coincida. Histórico normativo de consentimento é um fato armazenado; abrir/baixar documentos ou importar backup não cria novo aceite.

O endereço/origem define o espaço de dados. Portas localhost, file:// e hospedagem não compartilham automaticamente a base. Web Locks serializa somente participantes da mesma origem; UUID nos nomes reduz colisões entre origens que usem a mesma pasta. Quotas e possível remoção pelo navegador exigem cópias externas.

Testes e limites ficam nos recibos externos do candidate, separados das evidências anteriores. Physical folder, Safari/Firefox e transferência hospedada sem execução própria permanecem NOT_RUN. A matriz é documentação de cobertura, não afirma que cada combinação de atributos foi testada individualmente.
