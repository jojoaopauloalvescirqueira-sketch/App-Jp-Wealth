# Recheck independente R2 — B1 resolvido

**B1_RESOLVED_FOCAL_PASS**, sem novo achado neste delta.

Quatro contextos novos do Chromium 148.0.7778.96 abriram os HTMLs locais, em 1440 × 1000. Em cada mapa foi buscado e selecionado `JPW_PersonalHistory_Controller.mqh`, reproduzindo o caminho longo da contraprova R1.

As 24 verificações focais passaram (seis por mapa): seleção correta, Source completo, comunidade correspondente, texto dos campos dentro dos limites, sufixo `JPW_PersonalHistory_Controller.mqh` inteiramente visível e ausência de erros de página/console. Os quatro screenshots foram inspecionados. O caminho passa a quebrar em linhas, com nome e comunidade legíveis.

Identidade/delta: snapshots R1 autenticados pelos hashes originais; remover apenas as duas linhas adicionadas (comentário + regra CSS `overflow-wrap:anywhere; word-break:normal`) reproduz byte a byte cada HTML R1. Portanto o JavaScript e os datasets embutidos permanecem idênticos. Os quatro graph.json também mantêm os hashes R1.

Freeze R2 SHA-256: `aeb487a3e29f25621873e9d85fe8d23fd7fe802df8ce26bfa18e2929940ce667`. **51/51 hashes conferidos antes e depois**, nenhuma divergência.

Os **64 checks funcionais são evidência R1 preservada**, não foram repetidos nem reclassificados como execução R2. Esta rodada cobre somente a correção B1 e seus efeitos imediatos no painel. Nativo MT5/Windows: **NOT_RUN**; eficiência de IAs: **não mensurada**.

Evidências: `BROWSER-SMOKE-R2.json`, roteiro `BROWSER-SMOKE-R2.py` e quatro `BROWSER-SMOKE-R2-*.png`. Nenhum arquivo de produto/mapa foi modificado por esta revisão; somente esses registros foram criados.
