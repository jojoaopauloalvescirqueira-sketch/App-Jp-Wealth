# Brief — JPW MT5 Design 1.13.0

O pacote MT5 apoia leitura e estudo, sem negociar. A tarefa melhora a compreensão de NoCuda e Cockpit, derivando do candidate1.12.0 preservado. As duas revisões somente leitura encontraram: NoCuda recria controles, mistura ações e dados e bloqueia toda leitura em janela baixa; Cockpit já possui dimensões estáveis, mas cartões e ações têm hierarquia pouco distinta.

Contrato: CHG-JPW-MT5-DESIGN-20260930, N1/A2, pedido humano vigente. Raiz/branch/HEAD e fingerprint estão na baseline externa. Não deduzir aprovação de EX5 de capturas. Math1.9.0, schemas, store, preferênciaV2, calendário e fonte de dados não mudam.

Plano autorizado: preservar os IDs de ações, construir hierarquia neutra claro/escuro, orientação das etapas/estados, resultados rotulados e completos, medidas/paginação; preservar campos antes de updates e controles focáveis. Cockpit recebe acabamento nos componentes de apresentação, sem coleta ou novas capacidades. Nenhum salto de barra/zoom confirma estudo.

Fontes: AGENTS raiz/local, arquitetura NoCuda, README, X1 jpw-design IMPLEMENTAR (filosofia §§1–11,14–17), change-control/preflight/test-triage/post-change-audit. Harness localizado em `/Users/joaopauloalves/Library/Mobile Documents/iCloud~md~obsidian/Documents/2 - TRABALHO/5C - SOFTWARE/A0 - HARNESS - JP Wealth MASTER SPECIFICATION.md`, SHA256 b5680c22e44cf3f4a5cd3aa5deeb96f8b65c7908f14543e8c5d7f0c2f4e17b95, §§12–14/19/24/28–31. Referências antigas deslocadas e AGENTS local antigo são dívida preexistente; não serão reescritos neste escopo.

Consumo: indicadorNoCuda/controller/UI e CockpitPanel/Presentation → ações existentes e modelo aceito → objetos de gráfico. Cálculos/calendários/stores são protegidos. UI, página, README, manifesto e ZIP precisam concordar. Host replay e previews não são runtimeMT5. Suíte explícita, full bruto e auditoria independentes; native NOT_RUN se ambiente ausente.

Saída: candidate1.13.0 + fontes + página + recibos e limites em `outputs/jpw-mt5-design-v1130-20260930` no projetoChatGPT. Rollback restaura só o delta sobre1.12.0 sem apagar estudos ou mudanças preexistentes.
