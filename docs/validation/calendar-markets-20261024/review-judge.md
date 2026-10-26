# Addendum — auditoria final dos novos verificadores

A0 somente leitura; fonte do produto preservada e fingerprint de produto conferido contra todos os arquivos enumerados. Nenhum FULL foi executado por este revisor.

Resultado focal: PASS, sem achado material aberto no delta do juiz revisado. CM-UI-02 mede o conteúdo por Range e exige centralização de toggle/união texto-seta do quicklink até2CSSpx, alinhamento declarado à esquerda dos nomes e ausência de sobreposição. CM-UI-03 usa perfil temporário separado, preferências do Chromium, headless e no_viewport; exige razão outerWidth/innerWidth2 com CSSzoom1 e percorre4layouts×2temas em resumo/exploração, seleção/foco, preservação de nós e ausência de escrita de S/storage.

Execução independente nos bytes de teste957319a3159232db4c5a01af5f6422612e26e99198ccd1d937ba2cd87d3f4bb5:
- final-judge-alignment/report.json: CM-UI-02 PASS, stableInputs true, zero pageerrors.
- final-judge-native200/report.json: CM-UI-03 PASS,8combinações, outer1440/inner720/CSS1/dpr2 em todas, stableInputs true, zero pageerrors.
- final-judge-counter-alignment/report.json: PRODUCT_FAIL esperado com caixa44px e desvio interno vertical5.703125px; stableInputs true, zero pageerrors.
- final-judge-counter-csszoom/report.json: PRODUCT_FAIL esperado ao substituir browserzoom por CSSzoom2 (outer1440/inner1440/CSS2/dpr1); stableInputs true, zero pageerrors.

Regressões locais:5entradas novas, IDs/casos identificáveis, full_gate.included=false e check_id=null em todas, sem mudança em quality_gate.py/.github. Evidências final21 existem, PASS21checks, stableInputs true e hash de teste atual. A descrição inicial ampla de cold-alias foi estreitada: o caso permanente cobre entrada fria390/1440+âncora após montagem; cancelamentos por foco/navegação são explicitamente atribuídos à exploração independente separada. A distinção cobertura permanente/observação manual agora está correta.

Limites: oráculos geométricos focais não constituem revisão visual humana, leitor de tela, Safari ou toque físico. Browserzoom demonstrado é do motor Chromium headless em perfil sintético, não operação do navegador pessoal do proprietário. Matriz integral/distribuições/FULL permanecem sob recibos próprios do executor.
