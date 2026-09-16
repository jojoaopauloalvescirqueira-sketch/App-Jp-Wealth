# Banco de testes de backup — execução autorizada

Pedido: implementar plano aprovado de bases fictícias + bateria automática + relatório por nove metas. Complemento do candidate `codex/complete-backup-20260916`, HEAD 9c60d988; as 28 alterações preexistentes pertencem ao backup autorizado desta sessão e serão preservadas. O bloqueio de árvore suja do preflight foi reconciliado por essa identidade; não houve limpeza. Harness e contratos: mesma revisão registrada em CHG-COMPLETE-BACKUP-20260916; STATE-SCHEMA, DB-STORAGE-GOVERNANCE, DATA-RECOVERY e SECURITY-MODEL mantêm autoridade.

O app protege registros financeiros locais; os testes verificam portabilidade, não regras financeiras. Hoje há testes focados separados; a entrega reúne execução, dados importáveis, comparação e evidência manual. Escrita delimitada a tools/backup_test_bank.py e documentação/evidência; nenhum código de produto, schema, gate, norma ou dependência será alterado. Saídas em diretório novo externo; perfis Chromium descartáveis. Base Git e hashes antes/depois preservam rollback e identidade. Nenhum dado real será usado. Sucesso exige nove metas aprovadas e fontes idênticas durante execução; falhas de ambiente separadas das de produto. Publicação fora do escopo.

## Resultado

Banco executado com Python 3.12 + Playwright 1.60.0 no ambiente externo já existente. Comando: `/tmp/jpw-backup-venv/bin/python tools/backup_test_bank.py --output /Users/joaopauloalves/.codex/complete-backup/20260916/test-bank-verified`. Reexecuções exigem outro diretório novo para não sobrescrever evidências.

Build 718d5af075e33e02: 372 entradas PASS (comparações por campo/cenário e três execuções de suítes), nove metas PASS. Suítes incorporadas: complete_backup_test, backup_reliability_test (26 casos) e finalize_session_test (modular/portátil, reload, callbacks e duas abas). Relatório JSON registra esperado/observado/diferenças e hashes de todas as fontes antes/depois; identidade preservada. Produto não foi modificado por esta tarefa. A suíte FULL 57 do candidate anterior não é apresentada como nova execução.

Entrega externa `../test-bank-verified/`: três backups válidos, dois inválidos, esperado.json, ROTEIRO.md, relatório HTML/JSON, logs e oito capturas. Revisão visual de 390 claro e 1440 escuro concluída; diálogos contidos na viewport. Observação: pouco contraste no botão secundário de excluir rascunhos na captura escura; não declarar acabamento visual integralmente aprovado. O teste passou a aplicar o tema explicitamente e resolver assets da prévia portátil antes das capturas finais. As fotos são decodificadas em navegador e preferências reaplicadas após reload.

Comparação: exclui state.dataGovernance (auditoria/checkpoint gerados pela importação) e state.workspaceRecovery (journal), com conteúdo de rascunhos comparado separadamente; todos os demais campos são comparados recursivamente após reload e reexportação. Simulações de quota/API de pasta são sintéticas, não certificam hardware. Apenas Chromium foi executado; não há alegação de teste em Safari/Firefox.

AGENTIC IMPACT CHECK: NO AGENTIC IMPACT

BASIS: a entrega acrescenta ferramenta de teste opt-in e evidências; não modifica runtime, schema, contratos de armazenamento, AGENTS, skills, roteamento, registry, gates ou sua lista obrigatória. Os contratos continuam representando o mesmo comportamento já documentado. O registro local deste CHG identifica resultados sem declarar nova versão publicada. Não há reconciliação agêntica ou reindexação necessária para esta adição de evidência.

Sem commit, push, merge, deploy ou aceite humano atribuído.
