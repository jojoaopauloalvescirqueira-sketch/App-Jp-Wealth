# Perfil/Dante — recibo focal final5

Build **b7990f8c828e8d6f**, resultado **PASS**, orquestrador exit0. Execução sequencial, Chromium headless, contextos descartáveis. Nenhuma fonte/teste alterado por esta execução.

| Focal | Exit | Duração | Recibo |
|---|---:|---:|---|
| gallery | 0 | 14.83s | profile-final5-gallery.log |
| settings | 0 | 45.99s | profile-final5-settings.log |
| header | 0 | 18.82s | profile-final5-header.log |
| dante | 0 | 4.79s | profile-final5-dante.log |

Identidade: **22 inputs** de fontes, testes, asset e distribuições com hashes antes/depois iguais; `source_unchanged=true`, `inputsStable=true` em todas as etapas. Fingerprint do mapa canônico do recorte: `6d69fc16813e8045c4646275b0f83be0ea7b0b3c312862f685d3c5076f525532`. O mapa completo e os comandos exatos estão em `profile-final5-summary.json`. Este fingerprint identifica somente o recorte listado, não o conjunto global do FULL.

Provas observadas:

- Galeria:20entradas, imagens256×256/JPEG/limite válido, nomes/ordem/categorias, escolha em rascunho, Salvar/Cancelar, preservação do nome, leitura/gravação incompatível, conflito real entre abas, callbacks de upload atrasados, locks/session guards, layout1440/390 nos dois temas. Servido, portátilHTML copiado isoladamente (zero recurso ausente) e reload offline pelo Service Worker real PASS. `profile-final5-gallery/report.json`.
- Perfil/Settings: contrato completo original executado, incluindo limites5MiB/16MP positivos/negativos, MIME/WebP/corrupção, normalização, futura metadata, falhas de readback, concorrência, preservação de S/preferências e reparo deliberado de foto inválida. Identidade interna antes/depois também igual; `profile-final5-settings.log`.
- Header:34cenários (ações e capturas servido/portátil, quatro larguras320/390/768/1440, sidebar/topbar e dois temas). Foto confirmada, rascunho/cancelamento, galeria/upload/remover, erro→iniciais, foco/teclado e entrada de finalização preservados. Alvos44px/geometrias mantidas. `profile-final5-header/results.json`.
- Dante/Welcome: fallback sem materializar nome/perfil, foto pessoal prevalece, nome-only não grava avatar, remover/cancelar/erro e escolha explícita do mascote; API tardia, navegação recusada, tentativa falha, host alheio preservado, aceite único e startJourney real ainda com steps vazio; S e chave de perfil sem escrita por entrada. `profile-final5-dante.log`.

Não executado neste recorte: headed, zoom nativo, Safari, leitor de tela, toque físico, aceite visual humano e FULL global. Testes do agente não substituem essas provas. O defeito de calendário e sua proposta permanecem separados; este focal não os altera nem aprova.
