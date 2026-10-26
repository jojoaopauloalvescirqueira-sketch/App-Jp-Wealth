# Revisão A0 — redirecionamento apenas dos outputs efêmeros do FULL

**Veredito:** configuração reversível de saída **viável e aprovada no recorte A0**, na versão identificada abaixo, mantendo as guardas na execução real. Nenhum achado P0–P3 aberto nessa versão. O wrapper ainda não foi executado contra o FULL nesta revisão; não há aprovação de resultado FULL ou aceite humano.

A alternativa sem edição de fonte foi preferida pela coordenação. **Não foi produzido nem aplicado patch para `quality_gate.py`**. A hipótese `JPW_FULL_EVIDENCE_ROOT` fica desnecessária para esta tentativa e exigiria avaliação separada se retomada.

## Rota e escopo preservados

Não há opção oficial existente que mova os outputs internos: `--artifact` move apenas o JSON agregado; o sidecar de infraestrutura controla telemetria. O gate fixa sua raiz pelo `__file__.resolve()`, portanto `cwd`, `TMPDIR` ou symlink do script não alteram `full_evidence`.

A configuração externa troca somente o diretório **novo e vazio** `tools/.artifacts/app-efficiency-full-<timestamp>` desta tentativa por um symlink para o destino novo em scratch. Não altera `.artifacts` inteiro, diretórios antigos, fontes ou contratos. O gate oficial e seus comandos continuam idênticos. Análise AST confirmou FAST4, STANDARD59 e FULL102, com 102 identidades únicas; 24 checks utilizam `full_evidence`. O primeiro é `calendar-agenda`, check7, após seis checks anteriores. O mkdir do FULL precede o primeiro `[RUN] preflight` com flush. Timeout de900s, classificação, sequência, tiers, IDs, CI e oráculos permanecem nos mesmos bytes. O cap da UI começa depois da pausa inicial do preflight.

A rota move os outputs centralizados por `full_evidence`, incluindo os perfis e screenshots visuais. **Outros outputs incidentais de scripts sem argumento de saída continuam conforme os próprios scripts.** Alguns consumidores fazem `.resolve()`; outros registram o caminho lógico. Por isso, o recibo deve preservar ambos os caminhos e manter o symlink estável até o fim da execução e da coleta.

## Janela e proteção dos dados

A primeira linha de stdout, isoladamente, não provava que o gate ainda estivesse no primeiro check. Essa lacuna da versão inicial foi corrigida: stdout binário sem prefetch; grupo novo próprio (`start_new_session` e PGID=PID); SIGSTOP; snapshot até todos os membros estarem T; permissão somente para pai/preflight/git; rejeição de qualquer status adicional disponível no pipe. Não se redireciona se um consumidor posterior já estiver ativo. A execução real ainda precisa produzir essa evidência de handshake; os controles abaixo a exercitam por simulação.

`redirect` exige um único path novo, nome estrito, diretório real do usuário, parent canônico esperado, vazio, inode/dev estáveis e destino real vazio. Só então faz rmdir desse diretório vazio próprio e cria o link sem overwrite, verificando resolve e samefile. Se symlink falhar, restaura o diretório vazio. A troca rmdir→symlink não é atômica; a pausa comprovada e a janela sem outra suíte concorrente são condições da rota, não otimizações opcionais. Falha aborta a tentativa; não migrar conteúdo já escrito para fazê-la continuar. Cleanup de abort usa SIGCONT se necessário e SIGINT15→TERM15→KILL15 somente no grupo próprio.

## Contraprovas independentes

`verify_redirect.py` importa os bytes do wrapper em memória sem chamar `run`, `selftest` ou o gate. Resultado: **26/26 PASS**, exit0, sem navegador ou processo de teste do produto.

- 14 provas de filesystem: escrita/leitura pelos caminhos lógico e físico; `mkdtemp` de perfil filho e limpeza sem remover o symlink FULL; rejeição de origem não vazia, preexistente, symlink, arquivo, nome incorreto, múltiplas/nenhuma origens; destino não vazio/symlink/arquivo; UID indevido; inode alterado; falha simulada de symlink com restauração do diretório vazio. Conteúdo KEEP preservado.
- 12 provas da **guarda real extraída por AST**, com ps/select/sinais/sleep simulados: grupo próprio parado aceito; calendar/browser ativos rejeitados; pai ou filho não parados, grupo ausente/incorreto, status adicional, primeira linha posterior e zombie rejeitados; grupo externo ignorado sem receber sinal; transição para parado aceita. Nenhum sinal real foi enviado pelo revisor.

O selftest do construtor, lido separadamente, registra7 PASS; sua primeira falha por alias macOS `/var`→`/private/var` está preservada. A correção atual compara parent canônico, sem relaxar o requisito de origem dentro do parent esperado.

Conferência independente final: **679/679 inputs congelados intactos**, sem ausência ou divergência. Hash do gate continua `074fd1d63154b50a1eefcbc3feac4c9f41e1d6356615bc089e04b5adffb2cd2a`. Nenhuma fonte, teste ou contrato foi editado.

## Identidades e limites

- Wrapper revisado `../redirect_full.py`: `58a1b44639f54398be8addbced847a13fc2da144f9a9e84471e722195fa15195`
- Verificador independente `verify_redirect.py`: `ef34a9f87f8b4846ac8e9e375ca25552d204c722bd3de74ec22c10753d3e7853`
- Recibo `independent-proof.json`: `769a54fe2324026f828004a46aada999bcbeec455ad04b69034926984e2bd76f`

Usar o runtime Python existente com Playwright ao chamar o wrapper real: ele repassa `sys.executable` ao gate e mantém Node, Chrome e baseline já configurados. Não reutilizar target/receipt de tentativa anterior. Preservar o mapeamento e o destino real ao coletar os recibos; remover o link posteriormente sem uma rota verificável quebraria as referências lógicas do agregado. Esta revisão não executou a janela nativa/sinais reais. O FULL futuro precisa completar os102 checks e provar novamente seus679 inputs; os resultados anteriores mantêm suas classificações originais. Um eventual PASS com outputs em scratch não demonstra causalidade de CloudDocs, I/O, congelamento ou interferência humana no timeout anterior.

Escritas desta revisão limitadas a este diretório scratch; sem testes concorrentes, fonte control plane, operações Git de mutação ou browser.
