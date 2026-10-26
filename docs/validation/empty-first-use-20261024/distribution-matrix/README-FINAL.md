# Matriz final — primeiro acesso vazio

Build `1b695b809fe80c26`: **43/43 PASS**.

- HTTP: quatro layouts × dois temas × 320/390/900/1440 px (32 casos).
- Modular file://, portátil isolado em HTML único, PWA precache/offline real (3 casos).
- Zoom nativo200% headless por ChromePreferences: quatro layouts × dois temas (8 casos); outer1440/inner720 e CSSzoom1.
- Cadastro iniciado/digitado/cancelado com confirmação explícita de descarte. Checklist aberto por clique e fechado por Escape com retorno de foco.
- Nenhuma injeção inicial de S/storage/fixtures; contas/períodos/histórico vazios e respostasnull, saldos/ATR/exposição/lote ausentes. Nenhuma gravação financeira.
- Zero pageerrors e zero falhas de recursos locais. 215 fontes idênticas antes/depois.
- Corte anterior do progresso #chClass em320/390: reproduzido antes; eliminado após CSSdo root. Agora 43/43 casos verificam scrollWidth/clientWidth e scrollHeight/clientHeight, além de capturas e inspeção4larguras. Conteúdo de Fechar: dx0/dy−0,875px, altura44px.

Tentativas anteriores preservadas: Cancelar exigia descartar explicitamente a ficha preenchida; foi erro do teste, sem bypass no produto. PROD_FAILvisual anterior permanece registrado em RESULT.json e layout-inspection/.

Rede pública bloqueada; não valida cotações ao vivo. Testes automatizados e inspeção do agente não substituem aceite humano. Nenhum arquivo do projeto, Git, dependência ou dado real foi alterado. Todos os browsers estão encerrados.
