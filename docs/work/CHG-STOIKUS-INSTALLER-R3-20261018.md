# Instalador Stoikus — atualização R3 — 18/10/2026

A autorização humana vigente é “Atualizar e concluir também o instalador antes da limpeza final”. O trabalho usa a branch `codex/stoikus-installer-20261014`, base `bf0b1e8a882c9cdf880129f68f7c111e06e6f0c4`. O protótipo R2 completo foi preservado nos backups independentes da consolidação antes de qualquer atualização. Esta etapa reconcilia os conflitos com a main e atualiza o instalador para os fontes Stoikus **1.23.0/R5**, preservando o cálculo **1.9.0**.

## Finalidade, responsabilidade e comportamento

O site JP Wealth distribui a suíte. O instalador Windows compila e copia os quatro programas de uso diário somente para o terminal escolhido, após prévia, conferência de conflitos e compilação integral. O Monitor observa a conta; Conta e NoCuda apresentam informações; Abrir Painéis é um script pontual. A abertura dos dois gráficos permanece manual. O instalador não ativa negociação ou Supervisor.

O protótipo anterior fixava o pacote 1.22.1. O candidato R3 usa o ZIP diário 1.23.0: 86 membros, quatro programas e fechamento transitivo de includes/recursos. Os bytes são conferidos contra o manifesto atual, os ZIPs e as fontes. O download público permanece indisponível até as provas exigidas. Compilação cruzada C# não comprova execução Windows, compilação MQL ou funcionamento no MT5.

## Fronteira e invariantes

Risco N2 para instalação/recuperação e N3 para validadores e testes, delimitados pelo plano humano. Não alterar fontes MQL, regras financeiras, fórmulas, schemas, bancos, locks, estudos, gráficos, preferências ou a edição documental curada. Não editar AGENTS, gates ou CI. Reconciliar apenas os conflitos explícitos e os consumidores do instalador. Derivados do site e pacotes são gerados pelos scripts oficiais.

Permitidos: `tools/stoikus-installer/`, `tools/stoikus_installer_test.py`, `tools/build_leverage_package.py`, `tools/rebuild_monolith.py`, `tools/stoikus_download_test.js`, as fixtures de pacotes em `tools/stoikus_interface_package_test.py` e `tools/stoikus_daily_package_test.py`, a apresentação em `src/js/20-ui/31-tools-services.js`, seu manifesto, `index.html`, `.gitignore` e documentação focal. As duas fixtures históricas retiram somente metadados opcionais do instalador atual ao reconstruir uma versão anterior; suas asserções e oráculos permanecem intactos.

A resolução de conflitos preserva o carregador compartilhado de downloads, os seis artefatos R5, a curadoria e o produto atual. Não portar manifestos ou portáteis 1.22.1. Stage serve à resolução de conflitos; commit, push, merge e limpeza final pertencem ao executor principal. Publicação de EXE/site e instalação no MT5 não estão sendo executadas nesta etapa.

## Regressões e evidências

Testar identidade da versão, nome de arquivo, quatro programas, adulteração, caminhos, inventário e exclusão do EXE do portátil. Executar o Core com filesystem sintético, a lógica da UI ligada ao Core, geração do payload e build WinForms autocontido x64. Preservar os oráculos financeiros e os recibos R1/R2.

Os recibos nativos anteriores demonstram MetaEditor com exit bruto 1, log completo zero erros/avisos e EX5 novo. A atualização conserva esse exit no relatório, admite somente 0/1 com evidência completa ligada à fonte exata e recusa erros, outputs ausentes, logs de outra fonte, mensagens desconhecidas e saídas de processo desconhecidas. Os novos testes têm RED/GREEN próprios; isso não transforma as execuções antigas em prova do instalador R3.

Usar `leverage_suite.py --scope host` e focais pertinentes. O full e o navegador do candidato combinado terão recibo do executor principal. Provas nativas de Windows x64, ARM/Parallels, acessibilidade, download real e iniciante são separadas. O usuário possui apenas Parallels ARM; Windows x64 não receberá aprovação presumida. O canal `prlctl exec` foi recusado pela edição disponível. Nenhum arquivo MT5 foi copiado nesta etapa.

## Fontes e recuperação

Fontes: AGENTS da base; README, PROJECT-CONTEXT e CONTEXT-MAP; plano aprovado do instalador; implementação e recibos R2; manifesto de distribuição 1.23.0; registros anteriores de caracterização do MetaEditor. Harness canônico: SHA-256 `b5680c22e44cf3f4a5cd3aa5deeb96f8b65c7908f14543e8c5d7f0c2f4e17b95`, §§12–14 e 36–48 consultados. Os documentos registram autoridade recebida; não a concedem.

O backup da consolidação recupera integralmente o delta R2. Os derivados R2 e a primeira tentativa R3 anterior à correção nativa permanecem em arquivo privado. Os 160 inputs protegidos de MQL, ZIPs e kit R5 têm manifesto antes/depois. Rollback reverte somente este delta e regenera derivados oficiais, preservando todos os arquivos e dados do usuário.

**AGENTIC IMPACT CHECK: AGENTIC IMPACT DETECTED.** A nova versão do instalador afeta a representação de instalação/distribuição e o contexto operacional. Modo IMPACT: README, estado, tarefa, handoff e rota focal exigem atualização; AGENTS, skills, gates, CI, norma financeira, grafo e curadoria congelados não exigem alteração local. Não existe reindexação automática nesta entrega. A coerência é verificada pelos contratos CHG/CTX e pela revisão independente, com os estados de código, build, execução e publicação separados.
