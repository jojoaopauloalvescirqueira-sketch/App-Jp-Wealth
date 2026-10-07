# Correção dos PRODUCT_FAIL pendentes — 2026-10-06

Pedido humano atual: “Solucione todos os product fail pendentes”. Candidate isolado na cópia jpw-product-fail-repair-20261006/candidate, branch herdada codex/saving-reliability-20261006, HEAD ac3a2faffeb398357ff105adbf1d47f70ca309bd. Base 1db5b703ca56d26c, 749 arquivos/fingerprint ce450e0ba50b51388794e52a0840c830f3934b0bbf40d1945fd3701f8becfdb3 preservada, snapshot e recibos anteriores conservados. Preflight --allow-dirty somente após inventário dos deltas herdados. SOURCE REVISION UNKNOWN no contexto histórico permanece, não usado como realidade atual.

O objetivo é remover causas reproduzidas nas cinco falhas gerais e duas MT5 host; investigar intermitência do import e falha do executor de timeout. Não haverá alteração de norma/fórmulas, dados reais, configuração global, execução MT5, EX5, commit, branch, push, merge ou publicação.

## Control plane N3/A4 — contrato separado
Autorização de corrigir causas de testes falhos, não obter aprovação artificial. Cada expectativa adaptada exige reprodução, confronto com contrato humano já aprovado e auditoria independente. Preservar negativos, contagens, cenários e assertivas de domínio. Não remover verificações, mudar tiers/classificações, alargar timeout ou aceitar dados parciais. Não mudar runtime para satisfazer juiz obsoleto.

Arquivos possíveis: finpes_scenarios_test.py, alladin_finalize_preservation_test.py, storage_governance_test.py, import_xss_security_test.py, mvp_notes_test.py, complete_backup_test.py, leverage_package_test.py, leverage_page_test.py, quality_gate.py e regressão focal do executor. Timeout deverá preservar output bytes/string/null e produzir mesmo ENVIRONMENT_ERROR/124, sem interromper recibo; composição e 900s intactos.

Contratos: UNKNOWN é exceção tipada com barreira, não false. FULL exige documento durável completo; arquivo parcial negativo permanece. Exportação usa lock assíncrono, UUID e releitura física de bytes. Versão/tamanho do pacote vêm do manifesto atual. Recibos históricos não serão reclassificados; nova execução valida novos bytes. Gates brutos standard/full e MT5 host, nova auditoria, aceite humano posterior. Não invocar exceção de auditoria §19.1.

## Dívidas Forex reencontradas fora do full
As suítes forex_execution_market_test.py e forex_execution_workbook_test.py também estão no escopo: captura após seleção operacional explícita, recusa de contexto obsoleto, registros em accountContexts e ferramentas sob demanda são contratos aprovados nas revisões anteriores. Preservar todos os casos, snapshots e valores; fonte financeira não muda para permitir troca silenciosa. O núcleo v11 financeiro é verificado adicionalmente com Node já instalado, sem instalar dependência. Falha de despacho por PATH/argumento incorreto é separada da falha de produto.

## Integrações financeiras registradas e não incluídas no full
A auditoria de cobertura reencontrou forex_v11_read_model_test.py e forex_v11_ledger_planning_test.py inalterados desde contratos anteriores. Reproduzir com as camadas canônicas atuais e corrigir apenas fixtures incompatíveis: seleção operacional, contextos de conta/período, proteção de realizados finalizados e reabertura motivada. Preservar todos os cenários e oráculos de valor, ausência, zero, conciliação, rollback, UNKNOWN e leitura sem gravação. Qualquer defeito genuíno de produto será documentado e tratado separadamente; não flexibilizar uma barreira financeira para obter PASS.

Também reconferir forex_v11_state_test.py (41 jornadas históricas) e backup_reliability_test.py (26 jornadas). A leitura do inventário não comprova aprovação. Adaptações de fixtures de conta/período, arquivo FULL v2 com integridade, confirmação tipada UNKNOWN e readback de arquivo devem preservar cada jornada, valores e negativos. Revisões anteriores continuam nos recibos originais; novas evidências têm seus próprios hashes.

## Regressão da dependência de startup
Adicionar tools/reserve_startup_dependency_test.py como focal, sem modificar composição dos gates. Usar HTTP real e perfis sintéticos descartáveis; atrasar apenas a resposta de reservas para verificar a ordem declarada, ausência de pageerror e utilização do cadastro. Não ampliar timeout, suprimir erros ou substituir funções por stubs. O probe anterior permanece como reprodução independente.
