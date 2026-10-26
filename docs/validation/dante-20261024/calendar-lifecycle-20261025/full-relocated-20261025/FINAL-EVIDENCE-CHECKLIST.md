# Preparação A0 do fechamento — FULL com outputs redirecionados

Estado desta revisão: **rodada em execução; resultado FULL ainda pendente**. Esta lista não executa testes nem concede aprovação por herança.

## Mapeamento já conferido

- Wrapper: `5eadae0f21b03835df0ba63270f95869a49dd4fca59f08eb7f8bac28ad523754` (5eada revisado; 46 controles independentes).
- Path lógico: `/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/tools/.artifacts/app-efficiency-full-20261025T153333156784`.
- Destino físico: `/private/tmp/jpw-dante-calendar-20261025/full-relocated-evidence`.
- Link próprio, destino diretório real, `resolve` e `samefile` conferidos por leitura. Mapping SHA `34982b80f667f904fa22d20c06cde8876cf3eaceaa949770d006f9e5ad507b8d`.
- Grupo 97957: pai Ts e filho 97958 Z direto/`<defunct>`; pausa registrada 0,419864 s. Primeiras linhas do log: RUN preflight e PASS preflight 0,421 s. Não foram enviados sinais nem iniciado teste/browser pelo revisor.
- 679/679 inputs conferidos nesta passagem, zero ausências/divergências. Candidato esperado: build 8c127c2f92de375e, branch codex/dante-guia-20261024, HEAD a4bf278cd4dc38bbaa5b905ed17a79e33684fb67.

## Conferências após mensagem de conclusão

| Bloco | Recibo/critério a conferir | Estado agora |
|---|---|---|
| Comando real | `full-relocated-command.json`: argv do runtime Python existente, gate oficial `--tier full --artifact .../full-relocated.json`, exit observado 0, mapping desta rodada, sourceUnchanged=true, preflightVerified=true e 679 inputs | PENDENTE |
| Agregado | `full-relocated.json`: exatamente 102 IDs únicos e na ordem histórica de `full-final.json`; todos returncode 0/PASS; sem classe de falha ou NOT_RUN. Comparar argv por shlex, normalizando somente o prefixo de saída FULL antigo/novo | PENDENTE |
| Corpo do preflight | Check bruto com returncode 0 e output_tail contendo PREFLIGHT PASS e branch/HEAD esperados. O PASS externo sozinho deriva de exit 0. Confirmar corpo fresco, sem inferir falha pela proximidade entre pausa e duração | PENDENTE |
| Fonte e juiz | Recalcular 679 SHA do freeze e confrontar arquivo-a-arquivo; wrapper exato 5eada; gate 074fd1d63154b50a1eefcbc3feac4c9f41e1d6356615bc089e04b5adffb2cd2a. Tiers / 102 IDs / cap 900 e oráculos sem delta | PENDENTE |
| UI desta execução | Destino real `ui-visual-quality/ui-visual-quality-results.json`: PASS 413/413 exigidos e executados, IDs antigos exatos, sem duplicados/skips/extras; closure 8 + coverage control PASS; source_unchanged=true; test_sha256 e 160 source_sha256 iguais aos bytes congelados. Timestamps dentro da janela desta rodada | PENDENTE |
| Calendário e demais saídas | `calendar-agenda.json`: default 14/14 e lifecycle exatamente 1x; edges preservado. Conferir recibos próprios de recovery/distribution e os 24 consumidores full_evidence, vinculando-os aos checks/outputs desta rodada; não usar focais antigos como substitutos | PENDENTE |
| Preservação e evidências | Mapear agregado/log/recibo/mapping/inputs e cópias documentais com SHA; não sobrescrever históricos; manter destino real acessível. Registrar processos/cleanup só por evidência efetiva, sem inferir ausência por exit 0 | PENDENTE |

Para o conjunto dos 102 checks, o critério continua o próprio runner oficial, seus resultados brutos e os oráculos existentes. Não acrescentar tolerância, timeout, seleção de casos ou classificação para fechar a rodada. Leituras de recibos pelo revisor são auditoria de identidade/cobertura, não execução paralela.

## Reconciliação documental após o fim

Não encontrei aprovação FULL indevida. Há snapshots desatualizados: README/STATUS ainda mostram NOT_RUN/janela pendente e wrapper 58a / 26 controles; indexar a rodada 5eada e 46 controles com o seu parecer e recibos. Preservar os arquivos 58a como históricos delimitados por hash.

Registrar as duas preparações como SETUP_ABORT sem reescrever suas classificações brutas: tentativa 1 ENVIRONMENT_ERROR; tentativa 2 TEST_HARNESS_FAIL com estado SETUP_ABORT. O primeiro FULL completo 101 PASS / 1 ENV permanece bruto; a repetição interrompida 130 permanece INCOMPLETE; o focal 413 PASS continua separado. `input-integrity-current.json` com noRunningFull=true é fotografia anterior e precisa de contexto temporal.

`ACTIVE-TASK.md` integra os 679 inputs e deve permanecer congelado durante a suíte. Após o fim, qualquer atualização de documento dentro do freeze deve ser declarada como delta documental posterior; não alegar679 bytes atuais idênticos se algum deles for editado. Diferenciar os bytes testados das cópias/índices posteriores.

Mesmo um FULL verde nesta configuração não comprova causa do timeout anterior ou ganho causal de CloudDocs/I/O. Aceite humano, Safari, leitor de tela e toque físico permanecem nos limites já registrados. Sem commit, merge, push ou publicação por esta revisão.

Única escrita desta etapa: este checklist scratch. Aguardar o consolidado do coordenador; sem polling do progresso, browser, teste ou sinal concorrente.
