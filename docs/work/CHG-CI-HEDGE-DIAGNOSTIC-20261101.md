# Proposta: diagnóstico focal manual de Hedge no CI

Status A1: proposta, sem aplicação ou autorização implícita. Risco N3/control plane. Base caa439d0d5d539a8af5ad5cab301f5178ee70986; branch codex/backup-unificado-20261031; main9e050a1.

A execução FULL41358195387 do candidato registra PRODUCT_FAIL em hedge-prop-browser105.591s. O detalhe só é publicado ao fim dos116checks. Os fontes de Hedge e o motor estão preservados; causa ainda não estabelecida. FULL local116/UI413PASS não apaga a falhaLinux.

Proposta: adicionar ao workflow MT5 já registrado um input booleano hedge_diagnostic, defaultfalse, e um job manual adicional. Job MT5 atual, permissões, concorrência, gatilhos e todos os passos ficam idênticos. Quality Gate e seus116checks/413casos continuam intactos. A escolha desse workflow evita cancelar o Quality FULL atual; o dispatch focal aguardará o Host atual terminar.

O job adicional reutiliza quality_gate.run_check, mesmos nomes/comandos de Hedge/motor e orçamento900s de cada check. Xvfb/Chromium do Playwright seguem o runtime aprovado. Job20min, diagnóstico7dias, recibo atômico incremental antes/depois de cada check com completude explícita, ações pinadas e contents:read. Sem credenciais/dados reais; artefatos limitados às fixtures sintéticas. O diagnóstico não substitui o FULL nem habilita merge.

A4 pedido separadamente para aplicar este patch e realizar commit/push SOMENTE na branch, explicitamente identificado como snapshot de diagnóstico com gateLinux vermelho. Esta autorização de preservação do baseline vermelho é necessária pelo AGENTS.md; a autorização genérica Git não cobre esse caso. A4 também cobre disparar o workflow manual com hedge_diagnostic=true. Não integrar main enquanto houver falha obrigatória. Nenhum bypass, exceçãoHarness19.1, mudança financeira, engine, teste, critério, limite ou proteção.

Validação proposta: diff/objetos YAML comparados, job MT5 original idêntico, sintaxeBash/Python e contraprovas de propagação PASS/PRODUCT_FAIL do orquestrador; auditoria independente. Esses ensaios não executam browser nem aprovam runtimeLinux novo. CI diagnóstico produzirá evidência do SHA exato; validação FULL posterior permanece requerida para integrar o candidato final.

Arquivos delimitados: .github/workflows/mt5-host.yml e este CHG. Demais registros de aprovação/recibos ficam fora do checkout até nova necessidade explícita. Sem fonte/produto ou judge alterado. Rollback: remover somente input/job acrescentados e preservar todos os diagnósticos; operaçãoGit reversora exige autorização própria. AGENTIC IMPACT DETECTED, escopo focal, sem mudar autoridade, instruções, política ou memória histórica.

## Aplicação autorizada — 01/11/2026

O proprietário respondeu “Autorizar diagnóstico e snapshot vermelho” à pergunta call_d9352274d8ad48319f5bf5e2f9f7825c. A autorização cobre este patch revisado, commit/push somente na branch como snapshot de diagnóstico com CI vermelho conhecido e dispatch manual de Hedge. O registro A1 acima permanece como histórico da proposta; esta seção registra a autorização efetivamente recebida, sem conceder autoridade adicional.

Patch SHA256: 4d8f7d4efcd096a728f09cfe3ee9b44032c0ad6debc20ff3ed4c7a67218391cf. Workflow aplicado SHA256: b53d61df55a0a4a4f156057aa7a45f2326648ce0248d86d404ea96a1c9cfe88f. A suíte FULL 41358195387 continua independente no SHA caa439d; PRODUCT_FAIL de Hedge mantém o merge bloqueado. O diagnóstico é focal, não substitui FULL nem transforma o baseline vermelho em PASS.
