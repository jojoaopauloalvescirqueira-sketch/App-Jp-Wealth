# Brief — NoCuda diário 1.12.0

Objetivo: desenho assistido mais direto e consulta geométrica por dia, sem prever cotação ou enviar ordens. O NoCuda é independente do Cockpit/EA; coleta candles, calcula geometria pura, desenha e mantém revisões imutáveis próprias. A/B=0,C=1; malha65 níveis,-4..4,passo0,125; Close colocado na abertura. Futuros por sequência H1, não horas civis indiscriminadas.

Base: worktree codex/jpw-cockpit-ui-20260930, HEAD deffc5061fe2eff3d83b6f6e742fa105ac9c5b06, candidate 1.11.0. 571 arquivos e ZIP preservados em outputs/jpw-nocuda-daily-v1120-20260930/BASELINE.json, baseline.tar.gz e baseline.patch. Há 77 caminhos preexistentes modificados/não rastreados; não são deste delta. Full anterior57PASS/0PRODUCT_FAIL e nativoNOT_RUN permanecem históricos.

Autoridade: pedido humano explícito deste plano, N1/A2 para projeção geométrica e UX; nenhuma migração/schema ou norma. Fonte: docs/architecture/JPW-NOCUDA-CHANNELS.md e fontes atuais, conferidos nesta sessão. Harness externo localizado em 2 - TRABALHO/99A -   SOFTWARE DEV/99 - PROMPTS SOFTWARE DEV/A0 - HARNESS - JP Wealth MASTER SPECIFICATION.md, hash b5680c22e44cf3f4a5cd3aa5deeb96f8b65c7908f14543e8c5d7f0c2f4e17b95, preservado sem edição.

Critérios: início00h,meio12h,fim24h,média extremos e faixa; qualidade de geometria separada da cotação; calendário semanal Estimated; horizonte30dias+7somente delimitador; histórico/coerência insuficienteN/A. MarcaçãoABC sequencial e seleção da linha; consultas/redesenhos nunca gravam estudos. Sem raio infinito, canal livre, novos sinais, conta real ou terminal operacional.

Validação: novos testes sintéticos do mesmo núcleo/adaptador/controlador; regressões NoCuda e Cockpit; guia,pacote,full bruto,auditoria. Compilação/interaction nativa depende de ambienteisolado; NOT_RUN sem prova. Rollbackrestaura bounded delta do snapshot e mantém bancos existentes.
