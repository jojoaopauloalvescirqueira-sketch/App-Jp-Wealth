# A0 — filho Z direto durante preparação do FULL

**Veredito: APROVADO no recorte de configuração de saída** para o wrapper SHA `5eadae0f21b03835df0ba63270f95869a49dd4fca59f08eb7f8bac28ad523754`. Sem achado P0–P3 aberto. O delta não altera produto, gate, 102 checks, timeout de 900 s, fixtures ou oráculos. Não constitui aprovação do futuro FULL.

## Evidência e significado

Li as duas tentativas: pai 96962 / filho 96963 e pai 97203 / filho 97204, sempre pai Ts + filho Z, mapping null e679 inputs intactos; preparação abortada em 2,596 s / 2,767 s. Preservar esses recibos como abortos de setup, sem convertê-los em FULL executado.

O manual oficial do [ps da Apple](https://github.com/apple-oss-distributions/adv_cmds/blob/main/ps/ps.1) define T como parado, Z como morto, e `<defunct>` como processo encerrado cujo pai ainda não recolheu o status. O [manual de _exit da Apple](https://developer.apple.com/library/archive/documentation/System/Conceptual/ManPages_iPhoneOS/man2/_exit.2.html) documenta o fechamento dos descritores; [wait](https://developer.apple.com/library/archive/documentation/System/Conceptual/ManPages_iPhoneOS/man2/wait.2.html) distingue encerramento normal, por sinal e parada. Portanto, um Z não é escritor retomável; seu estado sozinho não informa exit0 nem a causa do encerramento.

`preflight-zombie-probe.json`, lido sem repetir execução, demonstra o caso legítimo: preflight real já encerrado mas não recolhido, pai Ts + filho Z direto e `preflightExit=0` após retomada. O probe comparativo none/group-stop/parent-stop também registrou exit0. Isso demonstra compatibilidade, sem determinar a causa dos dois abortos.

Não há base para atribuir esses Z a posix_spawn/vfork: no `subprocess.py` local 3.12, Popen usa close_fds=True por padrão; o ramo posix_spawn exige close_fdsFalse e cwdNone, incompatíveis com run_check(cwd=ROOT). O [C de CPython 3.12.14](https://github.com/python/cpython/blob/v3.12.14/Modules/_posixsubprocess.c#L41-L46) condiciona VFORK_USABLE a Linux. Não foi conduzido rastreamento causal dos processos históricos.

## Delta e contraprovas

Comparei com 58a: `redirect` e `selftest` permanecem AST-idênticos. Só foram acrescentados `inert_group` e a validação pós-retomada. O helper exige presença do paiT e mesmo PGID; permite Z somente se PPID = gate e args exato `<defunct>`; demais membros continuam T e passam pela allowlist preflight/git. A pausa de grupo, pipe binário sem status extra, inode/dev, diretórios vazios, resolve/samefile, rollback e cleanup próprios permanecem.

O candidato foi importado em memória. **46/46 controles independentes PASS, exit0**:14 de filesystem anteriores preservados e 32 controles de grupo/etapa. A guarda real foi extraída por AST, com ps/select/sinais/sleep simulados. Pai Z rejeitado; Z direto / <defunct> aceito; Z indireto, Z com consumidor identificado, pai ativo, grupo incorreto, consumidor ativo e status adicional rejeitados. PASS preflight oficial aceito; FAIL/ENV/HARNESS, outrocheck, prefixo parecido e EOF sem PASS rejeitados. Nenhum gate/browser/processo do produto ou sinal real foi iniciado pelo revisor. **679/679 inputs congelados conferidos, sem divergência.**

A identidade do executável se perde quando ps mostra apenas `<defunct>`. Logo, a segurança do Z direto desconhecido depende do protocolo conjunto: primeira linha RUN preflight, stdout sem prefetch/sem status extra, gate serial parado e saída nova vazia. O teste de consumidor Z identificado rejeita seu argv; ele não recupera identidade ausente no `<defunct>`.

## Alternativa e limites

Pausar só o pai poderia ser seguro com prova de que toda a árvore ativa pertence apenas ao preflight/git e não usa full_evidence, mas ampliaria a política para filhos ativos e exigiria validar parentesco e eventual fork durante a troca. Os probes não demonstraram corrupção pelo SIGSTOP de grupo. Recomendo o delta mínimo revisado, mantendo todos os membros ativos parados.

O próximo `[PASS] preflight` confirma o resultado oficial e evita tratar um Z como sucesso presumido. **Essa linha não é uma barreira de agendamento:** o gate pode lançar `structure` antes de o wrapper consumir um eventual FAIL. Em aborto, não afirmar que nenhum check seguinte iniciou sem snapshot; abortar e preservar o bruto. O handshake real dessa versão e o FULL completo ainda precisam de seus próprios recibos. Nenhuma conclusão causal sobre CloudDocs/I/O ou interferência humana é sustentada por esta revisão.

## Identidades

- Wrapper: `5eadae0f21b03835df0ba63270f95869a49dd4fca59f08eb7f8bac28ad523754`
- Verificador `verify_zombie_guard.py`: `cc8ae935b6b4612942d60f881867db367804ac4761ad3eceab6d8d970f4d3305`
- Recibo `zombie-guard-proof.json`: `995b3212d91a6e2ffcae70b89cc25749f33d309c1659824632be32440ee59079`
- Probe real do construtor `preflight-zombie-probe.json`: `a8497a0cb343dc3d2de48258d2d59058565def80dfdba1b4cac5b0afa0b6b0f8`

Escritas limitadas a este diretório scratch; sem alteração de fonte/teste/contrato, sinal real, teste concorrente ou navegação.
