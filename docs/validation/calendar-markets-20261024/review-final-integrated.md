# Auditoria final integrada — candidate congelado

A0 somente leitura durante o FULL2. Nenhum navegador, suíte pesada ou mutação de produto/teste/documento oficial foi executado nesta passagem. Relatório local autorizado. Branch codex/calendario-mercados-20261024, HEAD/base a4bf278, build3a9f6157481ae050.

## Conclusão

Nenhum novo gap material de produto ou enfraquecimento do juiz foi identificado no delta integral revisado. Os5P2 anteriores têm correção, RED/GREEN e recheck independente. A conclusão de prontidão integral permanece pendente do resultado real do FULL2 e das verificações finais declaradas abaixo; esta revisão não antecipa PASS nem aceite humano.

## Matriz de requisitos, evidência e limites

| Requisito aprovado | Evidência pertinente | Limite real |
|---|---|---|
| Entrada única Calendário e Mercados; alias antigo aceito após guardas | HTML/registry/compatibility diff; CM-HOST-01/02; navigation_ia; integração de distribuições; revisão NoCuda/MiniGames | selectView interno continua adapter físico; navegação autorizada atravessa JPWNavigation |
| Resumo3abertas/3próximas, contagens/unknown separados, ordem e horizonte24h | CM-SUM-01/02, CM-LIFE-02; engine de sessões intacto; contraprova horizonte exclusivo rejeitada | Calendário de ações, sem cotações/confirmação operacional; fontes reais mantêm cobertura original |
| Data selecionada da agenda distinta de Agora; hosts irmãos | CM-HOST-04 e composição DOM; painel/agenda preservados no tick/expansão | Prova sintética; compreensão humana da distinção ainda pendente |
| Exploração lazy e estado preservado ao recolher/retomar | CM-API-01/CM-EXP-01/CM-UI-03; fullDOM único, nós/filtros/seleção/scroll preservados | Estado de expansão é de sessão; recarga não promete persistência |
| Um catálogo/snapshot/scheduler; resumo por minuto/limites e full1s | 04-controller inspecionado, CM-LIFE-01/02, contraprova cadência1s rejeitada; repouso5/5/5→0/0/1consultas e5/5/5→0/0/0fullrenders |3amostras de~5100ms; não prova ganho global nem benchmark estatístico de latência |
| Renderer somente com mapa expandido/visível; pausa offscreen/dialog/blur/saída/descarte; câmera10s | CM-LIFE-03/04; integração dialogs/dispose; focais noon/lifecycle/lost-focus/macOS; loader/globo original intactos |20focaisPASS; fidelidade de referência original não recompilada por ambiente indisponível |
| Falhas explícitas, dados stale identificados, retry sem roubo de foco | CM-FAIL-01/02 e CM-P2-01/02; status/retry fora da região ocultada | Falhas de fonte não equivalem a ausência de sessões nem zero |
| Âncora e foco estáveis em entrada fria/atrasada/transições | CM-P2-03/04; revisão independente com catálogo controlado, abandono de foco e troca de navegação | Cancelamentos tardios são prova independente separada, explicitamente fora do caso permanente CM-P2-03 |
| Responsividade,44px,2px internos, teclado,4layouts/2temas, zoom200 | CM-UI-01/02/03, integração48apresentações/mode; contraprovas texto desalinhado e CSSzoom rejeitadas | Zoom nativo do motor Chromium headless em perfil sintético; Safari/leitor de tela/toque físico/aceite visual humano não comprovados |
| Agenda/rascunhos/Notas/Planejamento/sino/semanal/3jogos e ausência de escrita financeira | S/localStorage invariantes nos focais/integração; NoCuda130PASS e MiniGames guia/3distribuiçõesPASS; código financeiro/persistência inalterado | FULL1tem100PASS/2falhas de oráculo; FULL2emexecução, sem resultado antecipado |
| Distribuições e carregamento real | integração modular-file/portable-alone/PWAoffline PASS; manifest sósha256;8payloads vendor sóbuildID; bundle/globo/fontes sem delta | Recompilar globo de referência exige ferramentas originais ausentes; não declarar fidelityPASS |
| Juiz, rastreabilidade e autoridade preservados | Diffs de4testes legados delimitados ao submenu; novo focal21standalone;5regmem included=false; AGENTS/runner/CI intactos; CHGs/plano enumeram adaptações | Focal não entrou automaticamente no runner/CI; reexecutar explicitamente conforme contrato |

## Integridade e claims conferidos

481entradas de final-gate-inputs.json conferidas:drift0 no momento desta passagem. Fingerprint do produto também coincide integralmente. AGENTS.md, quality_gate.py, sw.js, calendário de bolsas e bundleaisol permanecem byte-idênticos ao baseline. Os8payloads vendor diferem somente pela substituição do buildID2627605be26c162c→3a9f6157481ae050; ordem/caminhos do manifest preservados, alterando somente hashes das5fontes esperadas.

O FULL1 em full-first.json conserva exatamente100PASS/2PRODUCT_FAIL; as falhas são nocuda-tools1.761s e minigames1.709s. Os REDs originais demonstram as listas antigas6vs5. A análise causal TEST_HARNESS_FAIL não reescreve o recibo bruto comoGREEN. O FULL2 requer resultado próprio após as adaptações auditadas.

O recibo de globe-fidelity conserva ENVIRONMENT_ERROR/exit1, FileNotFoundError do esbuild no caminho antigo. Bundle original SHA65d25e3fc43e00548e5a9db740a28c2f083031d5017b575b6118eff841c0f2cd intacto. O relatório explica versões/ferramentas ausentes e não converte essa lacuna emPASS. A tentativa engine com destinoCLI inadequado também permanece registrada separadamente da reexecuçãoPASS.

## Fechamento ainda necessário

1. Coletar resultado observado do FULL2 e conferir de novo os481inputs; não presumir êxito.
2. Reexecutar focal21 após FULL2, porque o plano em INPUTS recebeu apenas a explicação dos oráculos NoCuda/MiniGames. Todos os demais hashes do focal21 antigo ainda coincidem; conservar o recibo anterior e substituir o atual somente com a nova execução. O próprio executor já identificou e planejou este fechamento.
3. Performance3D após FULL2, sem carga concorrente, no ambiente disponível; sem inventar comparação se faltar base válida.
4. Reconciliar os pequenos registros finais: scope-audit ainda enumera24paths anteriores aos2testes tardios, e README/test-contract precisam refletir FULL1/FULL2 e as duas substituições. Isto é atualização de evidência, não necessidade de mudar produto.
5. Manter teste/aceite humano separado. Não há autorização implícita de commit, integração ou publicação nesta auditoria.

AGENTIC IMPACT CHECK:AGENTIC IMPACT DETECTED. BASIS: rota/contratos/guia/tarefa e registro factual das5regressões são representações consumidas por agentes. O delta reconcilia esses consumidores; mapa de caminhos e fontes normativas/skills/routing/gates permanecem intactos. Não há nova fonte financeira ou autoridade criada pelo relatório.

Fingerprint do arquivo final-gate-inputs.json nesta passagem:5dafcc41838e4fd71b5a32cae45b059eb0ce75e2694d9e28c59163c70e1b8209
