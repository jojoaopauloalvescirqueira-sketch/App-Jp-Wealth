# Stoikus Continuity Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement task-by-task. Preserve independent review and failed evidence.

**Goal:** Corrigir isolamento de objetos NoCuda, manter Histórico Pessoal utilizável com auditoria integral e tornar estados do Monitor acionáveis; validar o candidato exato nos ambientes disponíveis.

**Architecture:** Guardas de admissão nos objetos; auditoria integral retomável de geração consistente sem truncar o diário; mensagens de transição sem alterar status financeiro. Plataforma nativa e participante iniciante são provas externas distintas.

**Tech Stack:** MQL5, SQLite via MT5, Python/C++ host seams, geradores oficiais; Windows/MetaEditor para provas nativas.

## Global Constraints

- Base0037bd3c8a7ab2b4e21f7fdcb60f66ed93230874; branchcodex/stoikus-continuity-20261014.
- Nenhumreset/deletehistórico/relaxamentooráculo/fórmula/trade/armamento.
- Cálculo1.9.0 preservado; candidato produto1.22.2/MQL1.222, históricos1.22.1 preservados.
- Commit/push/merge/publicação separados; preservar instaladorbetaR2 e ZIPshistóricos.
- Ausência de teste nativo/participante não se converte em PASS; registrar NOT_RUN e limitação concreta.

## Task1 — NoCuda lifecycle/ownership

Files: JPW_NoCuda_Channels.mq5, JPW_NoCuda_{Render,UI,Fibo_UI,Fibo_Controller}.mqh conforme impacto; tools/jpw_nocuda_lifecycle_test.py novo. Outros arquivos não autorizados ao worker.

- [x] RED reproduz INIT_PARAMETERS_INCORRECT/INIT_FAILED antesdeprefixo seguidoOnDeinit, com FC_/UI_/DRAW_ alheios e preferência previamenteexistente intactos; códigoextraídoreal, terminaisobjeto substituídos.
- [x] GREEN admissão explícita+guardaprefixovazio, cleanup apenas recursos adquiridos; cleanup normal continua removendo seus objetos, nunca de outra instância.
- [x] Rodar testes NoCuda pertinentes, salvar logs/hash e revisar deltaindependentemente.

## Task2 — PersonalHistory continuity

Files: Store/Controller/Export e consumidores pertinentes identificados em design-personal.md; testecomSQLitereal.

- [x] Congelar API/desenho seguro: snapshot/generation/ownership/cancel/resume/EOF, sem mudar autoridadefinanceira.
- [x] RED diário100001linhas íntegro; corrupçãotardia, clock/timebudget, geração concorrente, readers e escritor, export/restore e reincício.
- [x] GREEN auditoria integral retomável, progressovisível, snapshots coerentes e invalidação quando geração muda; dadosantigos bytepreservados.
- [x] RegressãoSQLitetypedEnvelope+owner/processrecovery e crítica independente do desenho/implementação.

## Task3 — Monitor state and logs

Files: Monitor.mq5 e helper puro de mensagem se necessário; novo teste comportamental.

- [x] RED attachfalse não anuncia produtorativo; retries repetidos não inundamlog; recuperação e troca decontexto notificam.
- [x] GREEN transições aguardandoidentidade/titularidade→ativo→degradado/conflito, sem mexerlease/statusfinanceiro/freshness.
- [x] Verificar mensagens essenciais não ocultadas e relógio/conta/loopretry.

## Task4 — integração/provas nativas

- [ ] Revisão independente integral do delta; freezeinputs, hashes e reprodução dospacotes pelosgeradoresoficiais.
- [x] leverage_suite.py --scope all e quality_gate.py --tier full sobrecandidato congelado; fixtures não substituem MT5.
- [x] Revalidar canais Windowsx64 eARMParallelslegítimos; não contornarlicenciamento/nemabrirserviços. Ensaio no terminal demoisolado apenas se acesso confirmado.
- [ ] Registrar build/versão do MetaEditor/MT5, logs e quatroEX5exatos; testar casos nativos aprovados.
- [ ] Roteiro cominiciante real e registro separado instalado/compilado/abertura/aceite.

## Task5 — contexto/grafo e entrega

- [x] Reconciliar documentação apenas delta corrente, preservar snapshots/histórico.
- [x] Atualizar coberturaGraphify em trilha separada se extraçãoMQ5/MQHsegura e runtime disponível; preservar grafo17ago, marcarINFERRED/AMBIGUOUS euso não medido.
- [ ] Exportar candidato/fontes/recibos duráveis; worktreepreservada, nenhuma publicação implicada.

## Registro de execução — 2026-10-14

Tasks1–3: fontes/host aprovados individualmente; Task2 freeze02 e Task3 R3. Recibo integrado R2: all47/47 e full57/57, inputs1023 sem drift. Revalidação dos canais nativos concluída como diagnóstico: acesso guest não estabelecido, x64 independente indisponível; não significa ensaio nativo aprovado. Grafo focal extraído de104MQL+2docs, com inventário de9BMP e limitações explícitas. Kit PowerShell de compilação apenas: fonte K1–3 e identidade final aprovados; execução/51 fixtures Windows NOT_RUN. Entrega durável e parecer integral em fechamento. Compilação, ensaio nativo e iniciante continuam pendentes.
