# Revisão independente A0 — calendário, correção autorizada25/10/2026

**Sem achados bloqueantes P0–P3 no delta examinado.** A aplicação coincide exatamente com product.patch/regression.patch autorizados. O novo lifecycle foi efetivamente executado pelo runner padrão sem filtro: 14/14 PASS, incluindo uma ocorrência de calendar-lifecycle-320-light. **FULL novo e aceite humano continuam separados e pendentes neste parecer.**

Raiz real: `/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS`. Branch `codex/dante-guia-20261024`, HEAD `a4bf278cd4dc38bbaa5b905ed17a79e33684fb67`, build aplicado `8c127c2f92de375e`. Escopo recebido: revisão A0; somente este relatório pode ser escrito pelo revisor. Li os CHGs PRODUCT/CONTROLS CALENDAR-LIFECYCLE-20261025, que registram a autorização específica de25/10; os textos de proposta24/10 permanecem históricos e não são usados como autorização nova.

## Aplicação e preservação conferidas

- Os patches em docs/validation/dante-20261024/calendar-fix-proposal são byte-exatos aos já revisados em scratch24/10. Reconferi a fonte e o teste após receber os hashes novos do principal; ambos coincidem com as cópias candidatas completas.
- Confrontei a aplicação com before-calendar-pending.zip: no módulo19, a única alteração é `if(dialog.open)return;` no listener close. Não há alteração de regra de backup, domínio, escritor, schema, foco ou rascunho.
- Comparação AST do teste com essa base: oito funções anteriores preservadas, nenhuma removida; três helpers novos (lifecycle_setup, lifecycle_close_controls, lifecycle); somente main muda entre as funções antigas, para descobrir/configurar o novo caso. O corpo de edges é idêntico, inclusive a expectativa de zero marcador em1/nov. Não foi alterada tolerância, timeout ou expectativa antiga para obter verde.
- O ZIP334 arquivos passou verificação própria de CRC e SHA-256 de todos os entries contra before-calendar.json; SHA do arquivo ZIP também confere. Nenhum arquivo da base foi encontrado ausente. A wave-delta14 informada pelo principal contém fonte/teste/registro factual e gerados oficiais; as mudanças documentais/CHGs têm trilha própria.
- O registro factual atual preserva exatamente as110 entradas da base e acrescenta somente calendar-20261025-delayed-close-after-reopen, total111, com RED/GREEN e check calendar-agenda vinculados.

## Causa e correção

Close já invalida a request e limpa o timer sincronamente. Open reativa o mesmo host e solicita refresh novo. O evento close antigo, entregue após a reabertura, executava o listener incondicional e desativava essa abertura nova; invalidate então excluía a instância e preservava o marcador anterior na UI.

O guard consulta o estado atual desse mesmo diálogo, que é reutilizado pelo controlador. Se aberto, conserva a abertura nova. Se fechado, mantém exatamente active=false, incremento de request, limpeza do timer e aria-expanded=false. Nenhum caminho passa a gravar dados ou alterar os30dias/DST do backup. A recusa de timestamp futuro já existia; a correção restaura o refresh que precisa remover a representação antiga.

Executei unidade independente com o ensureDialog real aplicado em VM: aberto preservou active=true/request7/timer1/expanded=true; fechado produziu active=false/request8/timer removido/expanded=false. Ambas as asserções passaram. Essa unidade não simula a fila nativa; os recibos reais abaixo exercitam essa fronteira.

## Descoberta e execução permanente

quality_gate.py permanece inalterado e inclui calendar-agenda em STANDARD, herdado por FULL, chamando tools/calendar_agenda_test.py sem --case. O main padrão usa path=index.html, sem baseline/filtro, e contém14casos: seis UI e oito adicionais; lifecycle ocorre uma vez. Não há runner paralelo ou função nova sem consumidor.

Conferi focused-commands.json: o comando calendar-all usa o teste real, somente --artifact, exit0 em46,04s. calendar-all.json contém os14IDs esperados/14PASS e lifecycle exatamente uma vez. Isso demonstra execução real pelo runner padrão, além do wiring lido. O JSON focal lifecycle-green também veio do main permanente, sem o pacote econômico artificial que o replay24/10 instalava para todos os casos; a limitação de divergência do replay anterior está resolvida para o estímulo atual.

## RED, GREEN e contraprovas

Evidências de browser executadas pelo principal, lidas pelo revisor — não reruns próprios:

| Recibo | Observado |
|---|---|
| lifecycle-red.json | PRODUCT_FAIL esperado, CAL-LIFECYCLE-01 no main→lifecycle; exit1 informado pelo principal, antes do guard |
| lifecycle-green.json | edges + lifecycle PASS após guard; evento antigo registrado com open=true, host ativo, timer único e marcador futuro removido |
| calendar-all.json + focused-commands.json | 14/14PASS no comando padrão, exit0 |

O GREEN exige estado financeiro completo igual ao esperado, permitindo apenas a alteração explícita do timestamp sintético em memória; bytes persistidos ficam iguais. A leitura unknown e o zero marcador são mantidos. Não há tratamento de dado real.

A contraprova RED mostra que remover o guard reintroduz a falha causal na proteção permanente. Os controles de Fechar original, Escape e native-close verificam host fechado, timer0, refresh0 e expanded=false; Fechar/Escape também exigem retorno de foco. Isso protege o lado que um guard amplo demais ou listener vazio poderia quebrar. No fechamento nativo direto, refresh0 sozinho não provaria cleanup (o filtro também consulta open); as asserções adicionais de timer e aria-expanded evitam essa falsa suficiência. Os UI antigos mantêm rascunho/backdrop e foram executados na rodada padrão.

Também conferi logs/recibos adicionais do principal: calendar-recovery exit0, backup-freshness PASS/build8c127c2f92de375e/exit0 e calendar-distribution4modos PASS/exit0. Esses focais são evidência complementar; não substituem FULL. O focal guide-Dante ainda estava em andamento no aviso de fechamento.

## Riscos e limites

Nenhum risco adicional demonstrado exige ampliar o patch. Guard por open é suficiente para a transição observada do host reutilizado; não há necessidade demonstrada de novo token ou refatoração. Os controles delimitam reabertura e fechamento real, mas não cobrem todas as ordens possíveis de eventos, navegadores ou integrações.

Timers são observados por instrumentação do stack armClock, restrita a estes contextos sintéticos; a contagem não é auditoria universal de timers. A prova de efeito real também depende de refresh, marcador, host e acessibilidade observados. Safari, toque físico, leitor de tela, ensaio humano e execução headed não foram feitos por este revisor.

Preflight audit passou com os avisos esperados de árvore pendente/material freshness; isso não é autorização ou aprovação de produto. `git diff --check` executado nesta revisão passou. Nenhum browser foi iniciado pelo revisor. Nenhuma fonte/teste/contrato foi editado por ele.

Antes de declarar a entrega integral pronta, exigir recibo FULL atual com identidade estável, checks/casos efetivamente executados e classificação bruta. Falhas anteriores permanecem históricas, sem aprovação por herança. Commit, push, merge, publicação e aceite humano não são concedidos por este parecer.

## Identidades reconferidas ao gravar

- `src/js/40-app/19-calendar-agenda.js`: `da6c6738fe5776c5c75e9728176cb47812d2c594f130f9c3025a31969870a53c`
- `tools/calendar_agenda_test.py`: `c19fe3272601bfb6816fe4a0ed1d7b01bca04905d878a4fbba56065490181a6e`
- `tools/quality_gate.py`: `074fd1d63154b50a1eefcbc3feac4c9f41e1d6356615bc089e04b5adffb2cd2a`
- `build-id.js`: `0569ce3aceda803f7fe78388262b4e1ede107a5f57ca5e5e06481d4270e95d6c`
- `src/js/manifest.json`: `9aaa09edb0e035b95f84f155c90d85ff1e3ebce22e6719243474416ea7054430`
- Proposta `product.patch`: `7d66165a2f8c8fc52d53663cff8b91d82385b7fd5cf57546b3c91f179f5d0295`
- Proposta `regression.patch`: `a32f742875b63794401c8224435a7c9450d5c707ba52d98d4076cb89612d57eb`
- Proposta `proposal.patch`: `f754f0e71a3adb54cdf83ec93e540d2ed50c77582d321ac89f29b43310df7599`
- Recibo `before-calendar.json`: `ab841bf7930343e7df8de2219f73aa6e754af91fc252a093e79d6104bd2cc6bc`
- Recibo `before-calendar-pending.zip`: `1f04fecf0416d079455df20aee6b154bdcb7f61be1864bae52f6d68719d80d36`
- Recibo `lifecycle-red.json`: `25cdf60853679e443d944008cae81fd8743c029edd55936b98686877abebbce6`
- Recibo `lifecycle-green.json`: `f503dcbb96fa1f01967e6f1ecd299c6d57136a537ec07d839e2eb057edfe14df`
- Recibo `calendar-all.json`: `f2544aab64f1fe35abe9a2c5014c559cb66891816c8dcc50e77de1ea0a3afe5d`
- Recibo `focused-commands.json`: `c2a5e10169fd9102558bb62a46e16fb067bb50a790b3453dcd486af50079c937`

Única escrita do revisor nesta etapa: `/private/tmp/jpw-dante-calendar-20261025/INDEPENDENT-REVIEW.md`. Alteração posterior de inputs materiais invalida a parte afetada deste parecer.
