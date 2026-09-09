# Tarefa ativa — Dashboard oficial

Classe M3. Data: 2026-09-09.
Base: 1e7911d9b3620e24eeb66961dd3a337e34fad7ac.
Branch: codex/dashboard-official.
Autoridade: proprietário autorizou preparar a versão oficial e integrar à main.
Classificação: N1 (apresentação e navegação); integração A4 autorizada.

## Objetivo e limites
Transpor seletivamente as melhorias da worktree Dashboard sobre a main com V11.
Quatro resumos, atalhos profundos, atualização por render/feed/visibilidade e
ferramentas expansíveis. A origem permanece preservada.
Não alterar fórmulas, schema, persistência, Galton, documentos/aceite V11,
infraestrutura ou parâmetros. Nenhum deploy.

## Arquivos permitidos
index.html; src/styles/app.css; src/js/20-ui/03-main-render.js;
src/js/20-ui/25-dash-macro.js; src/js/40-app/15-ff-news.js;
src/js/manifest.json; build-id.js; portátil gerado;
tools/dashboard_macro_test.py; tools/exec_three_column_test.py;
README, CHANGELOG, CURRENT-STATE, SESSION_HANDOFF, esta tarefa e auditoria.
Contratos arquiteturais somente se a apresentação exigir descrição atualizada.

## Critérios e validação
Resumos consomem derivação canônica; ausência/recusa não vira zero.
Nenhuma escrita ao consultar; preferências de widgets preservadas.
Atalhos reais coerentes com navegação local e foco.
Desktop/mobile claro/escuro sem overflow; leitor/download/aceite V11 preservados.
Build oficial, focal Dashboard, full e CI do candidate; revisar diff e topologia
antes do merge, sem auto-merge e sem bypass de proteção.

## Estado
Implementação seletiva validada localmente: full 55/55 PASS; build 9cf89998aa453da4.
Focal, visual e teclado aprovados. CI e integração devem ser consultados no PR
da branch, pois este registro é o checkpoint anterior ao commit.
Rollback: descartar somente a branch delimitada antes da integração, ou revert
formal posterior; nunca modificar a worktree de origem.
