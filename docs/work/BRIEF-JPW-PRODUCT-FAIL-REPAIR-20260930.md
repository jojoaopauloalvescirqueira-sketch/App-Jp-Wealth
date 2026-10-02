# Brief — correção dos PRODUCT_FAIL registrados

Raiz `/private/tmp/jpw-cockpit-ui-20260930`, branch `codex/jpw-cockpit-ui-20260930`, HEAD `deffc5061fe2eff3d83b6f6e742fa105ac9c5b06`. 34 caminhos preexistentes preservados em `/Users/joaopauloalves/.codex/.chatgpt-projects/g-p-6a4fc0aa51dc8191af013579f37179a3/outputs/jpw-product-fail-repair-20260930`. Pedido atual autoriza corrigir todas as falhas registradas; não autoriza promoção/Git ou alterações financeiras.

1. Finalidade: JP Wealth apoia gestão de risco e registros financeiros; os controles precisam avaliar o aplicativo efetivamente carregado.
2. Responsabilidade: runtime realiza navegação e domínio; fixtures servem os bytes reais ao navegador isolado.
3. Observado: 55/57 no último full, Galton perde `07-workspace-backup.js` por ERR_CONNECTION_RESET, navegação timeout; várias falhas antigas compartilham perda de scripts. Esperado: bootstrap íntegro e fluxos corretos sem afrouxar asserções.
4. Impacto: compartilhamento de servidor local de testes, consumidores do full, navegação contextual; não mudar fórmula, schema, fontes MT5 ou feed simulado.
5. Limites: preservação do delta 1.11.0 e registros históricos; timeouts/asserts/gate intactos; sem dados reais.
6. Evidência: confronto baseline/candidate da fila com burst e hashes, controles negativos de arquivo ausente e erro JS, full bruto, suíte MT5, auditoria separada.

Fontes lidas: AGENTS.md, README, CONTEXT-MAP, PROJECT-CONTEXT, CURRENT-STATE (histórico; revisões antigas não comprovam estado atual), QUALITY-GATES, CHANGE-PROCESS, skills preflight/change-control/test-triage/browser-verification/post-change-audit/security-audit, Harness §§12–16/28–30.

CHGs: produto N1/A2 e fixture control-plane N3/A4 separados. Antes/depois preservar hashes e patch; nenhuma exceção histórica será usada para obter aprovação. Rollback restaura apenas os arquivos do delta atual da cópia, não reset/stash. Plano: inventário → reproduções → menor correção → derivados → congelamento → full/suítes complementares → auditoria independente.
