# Parecer técnico independente final — primeiro acesso vazio

**PASS técnico no escopo auditado; candidato pronto para teste e aceite humano.** Não restou achado impeditivo de produto ou verificador aberto após as correções verificadas. Esta conclusão não concede aceite humano, publicação, integração ou autorização Git.

Candidato `1b695b809fe80c26`; branch `codex/primeiro-acesso-vazio-20261024`; HEAD base `a4bf278cd4dc38bbaa5b905ed17a79e33684fb67`, working tree deliberadamente não commitada. Revisão independente dos autores do produto/testes, limitada ao delta autorizado e consumidores pertinentes. Nenhum browser/teste foi repetido durante este fechamento; foram conferidos código/diffs já auditados, recibos, logs, hashes, escopo e links.

## Gates e identidade confirmados

- `full-confirmed.json`: tier full, **102 checks distintos**, todos PASS e returncode0; mesmos102 identificadores do FULL2. Início15:49:54 e término16:28:34 de24/10/2026 (-03:00).
- `full-confirmed-runner.json`: comando oficial `quality_gate.py --tier full`, exit0,2.320,141s,664 inputs e zero mudanças. Sumário possui zero PRODUCT_FAIL, TEST_HARNESS_FAIL, ENVIRONMENT_ERROR, BASELINE_FAIL e NOT_RUN.
- Auditor refez a comparação de **664/664 hashes contra os arquivos atuais**: todos iguais ao freeze `full-confirmed-inputs.json`. Os19 arquivos do fingerprint próprio também conferem. Entre FULL2 e FULL3, somente os dois testes de sessão mudaram; produto/build permanecem iguais.
- Cópias dos três recibos FULL em `docs/validation/empty-first-use-20261024/` conferem byte a byte com os originais externos.
- Focal adicional final16/16 PASS, sete contraprovas de fonte carregada rejeitadas e matriz43/43 PASS já conferidos no mesmo build. Matriz preservou215 fingerprints; inclui HTTP, modular-file, portátil isolado, PWA offline e zoom nativo200% em headless. Aceite de rede/feed público não faz parte dessas provas.
- Dois focais integrais de sessão nos patches exatos passaram; as contraprovas desses mesmos arquivos continuam detectando apagamento e igualdade violada. Não houve perda de oráculos, runner, thresholds, skips ou ampliação de timeout.
- `git diff --check`: PASS. Fonte real do Harness confere com hash autorizado `b5680c22e44cf3f4a5cd3aa5deeb96f8b65c7908f14543e8c5d7f0c2f4e17b95`.

## Escopo e preservação

Conferi diretamente `baseline.json`, o ZIP preexistente e os arquivos atuais: **153 arquivos anteriores presentes**, sem perda; somente14 alterações preexistentes listadas como autorizadas no scope audit. CSS anterior permanece prefixo integral; texto anterior de ACTIVE-TASK permanece integral;96 registros anteriores de regressão permanecem iguais e cinco novos foram acrescentados. AGENTS, runner FULL, política e engine Forex estão byte a byte iguais ao HEAD. Fontes de Calendário/Mercados preexistentes mantidas; sua autoria não foi atribuída ao delta novo.

READMEs/ACTIVE-TASK foram reconciliados para o resultado efetivo, mantendo o histórico. Links locais do README resolvem. Correção editorial da lista de contraprovas conferida no README final: `accept-missing-checklist` trata resposta do checklist sem chave v; a rejeição de saldoIni ausente aparece explicitamente como caso distinto. A rastreabilidade agora corresponde ao mutante real. Nenhum input de código/teste foi alterado por essa reconciliação documental.

## Achados e falhas históricas

P2 de agregação de taxonomia: resolvido e contraprovas da classificação verificadas. Corte de classificação em320/390px: resolvido por CSS local #chClass; RED real preservado,16 estados visuais e contraprova CSS conferidos. As três expectativas de cadastro0→null correspondem ao contrato aprovado e conservaram controles de identidade, histórico e deduplicação. As adaptações de fixtures de Alladin/backup/senha/sessão tornam explícitas as pré-condições antes herdadas das contas de demonstração; igualdade integral foi acrescentada onde pertinente.

FULL1 parcial permanece8PASS/94NOT_RUN. FULL2 permanece100PASS/2PRODUCT_FAIL brutos; triagem causal demonstrou fixtures sem conta prévia usando accounts.length0 como sentinela. As duas correções conservaram os asserts e foram seguidas por focais, contraprovas e **nova FULL inteira**, sem waiver. Resultado verde atual não apaga os anteriores.

## Aceite humano separado

**NOT_RUN / PENDENTE:** teste e aceite do proprietário, clareza para pessoas reais, Safari, leitor de tela e toque físico. Chromium sintético/headless e inspeção de capturas não equivalem a essas provas. Não houve acesso/mutação de base pessoal pelo auditor; atualização de código não autoriza limpar dados existentes. Leitores antigos podem recusar os novos null.

Parecer final permite apresentar o candidato ao proprietário para teste. Nenhum commit, merge, push ou publicação foi executado ou autorizado por esta auditoria. A prontidão técnica refere-se exclusivamente aos bytes/escopo identificados; mudança material posterior exige revalidação afetada.
