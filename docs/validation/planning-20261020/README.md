# Correção atual — dinâmica da planilha — 20/10/2026

O proprietário pediu reprodução do percurso original após avaliar o candidato abaixo. A correção atual usa Comece aqui, formulário/revisão/confirmação e as quatro abas da planilha. [Engenharia reversa, provas e limites da correção](parity/README.md). Seus recibos são separados; **ff0f078f e FULL88/88 abaixo são históricos**.

---

## Fotografia anterior preservada

# Planejamento independente — validação do candidato local

Base `ea15afc9c6a9c30cc69c5b98a8b85c85211ffb34`, branch autorizada `codex/planejamento-patrimonial-20261020`. Implementação local; não houve commit, merge, push ou publicação. [Contrato](../../architecture/PLANNING.md), [CHG](../../work/CHG-JPW-PLANNING-20261020.md), [referência](../../decisions/2026-10-20-planning-reference.md).

## Estado da verificação

Candidato **ff0f078f70b9fb97**, verificação automática concluída: **FULL 88/88 PASS**, zero PRODUCT_FAIL/TEST_HARNESS_FAIL/ENVIRONMENT_ERROR/BASELINE_FAIL/NOT_RUN no runner final. [Comandos e resultados](FULL-CHECKS.md), [recibo compacto](FULL-RESULT.json), [397 inputs de runtime](RUNTIME-INPUTS.json) e [254 identidades de testes](TEST-INPUTS.json). Ambos os manifestos permaneceram estáveis. Aceite humano e comparação nativa integral Sheets continuam pendentes.

## Delimitação e referência

Menu principal após Forex, Consolidado/Mensal/Referência/Contas, contas independentes e calendário de120 meses por plano. Agregado opcional patrimonialPlanning; abertura/consulta não gravam. Legado fxPlanning preservado e exportável, sem migração automática. Três minigames, Bolsas Globais, norma Forex, fontes/pacotes MT5 e dados reais não foram substituídos.

Modelo original: planilha1Wo1Qwvfd7okSClnCwKateirerP77Z0fWGHmg51wG2EA; Formulario.verified.gs SHA1ab2401baced1d6a8534dfa2164ce6d905cb52fd2ccdd3268b9910d9650bce94. Prazos.gs SHA5188c9b07f2e03a6609e3b13c6bac46874a5b205876ec74f4e2311c995c7c62c e ParadaAportes.gs SHA3b4962446a2dccd9371cb60331b824fe43113f81d105667bc639fa282c48949a. Oráculos externos executam somente funções puras em VM; APIs do Sheets são bloqueadas. Testes permanentes não dependem desses arquivos externos.

Exceção aprovada: referência diária USD/BRL do site, com fonte e datas, em lugar do Google Finance. Meta BRL captura conversão; consulta corrente não reprifica o passado. Não se promete igualdade de cotação entre provedores.

## Revisões independentes e correções

Revisões financeiras R1/R2 encontraram média de aquisição ausente no Consolidado, carry com fechamento indevido, prévia que perdia dados da conta, contribuição corrente expirada cedo demais, parada retroativa divergente e sinalização anual provisória ausente. Correções foram confrontadas com o original e protegidas por testes permanentes; [R3 financeira](FINANCIAL-REVIEW-R3.md) não demonstrou bloqueio no escopo estático. Ela não executou produto/testes.

Revisão independente de segurança encontrou risco de confirmar RAM adjacente junto com o plano e entrada/saída de chaves de segredo no novo agregado. Foram corrigidos na fronteira do writer e na validação comum do backup; o caso sem base confirmada recebeu regressão adicional. [R3 de segurança](SECURITY-REVIEW-R3.md) sem bloqueio demonstrado no escopo estático; DP-3 continua sendo limite preexistente de concorrência, sem alegação de CAS atômico.

A [crítica de experiência](UX-REVIEW.md) usou interação real com dados sintéticos em1440 e390 px e apontou termos ambíguos de renda mensal/resultado, consequência de adiar parada e descoberta da prévia no celular. Ajustes de texto e foco/rolagem receberam recheck separado. Não houve teste de compreensão com pessoas.

## Cobertura substituída

[Mapa de proteção do legado](LEGACY-COVERAGE.md) distingue contratos aposentados dos que permanecem. O teste de seis menus foi atualizado para sete, PF passa à posição05 e Forex a seis filhos; não são regressões financeiras. A varredura textual de credenciais mantém todos os termos suspeitos, mascarando somente a palavra authorization nos spans exatos das próprias expressões de detecção revisadas. Ocorrências fora desses spans continuam rejeitadas.

## Rastreabilidade das falhas

Primeiro full foi uma execução iterativa:84PASS/4PRODUCT_FAIL brutos (contagem antiga de menus, posição antiga dePF, termoauthorization na própria expressão de detecção do backup e oráculo de startup que ainda exigia os cinco módulos retirados). Essas expectativas foram atualizadas para o contrato aprovado sem relaxar o hash das106 identidades ou a proibição de credenciais. Antes do respectivo check do FULL final, o mapeamento do guia foi corrigido e verificado também por cinco controles negativos; nenhum resultado já executado foi sobreposto. O runtime permaneceu congelado no segundo FULL inteiro. A primeira rodada não aprova o freeze final. Brutos e RED/GREEN ficam em `.superpowers/sdd/planning-20261020`, ignorado pelo Git. Chamadas focais iniciais sem argumentos obrigatórios são TEST_HARNESS_FAIL, antes da execução do produto; comandos completos foram repetidos. Não se atribuem essas falhas ao aplicativo.

Teste complementar de branding Stoikus R4: BASELINE_FAIL (bruto genérico PRODUCT_FAIL),4PASS/1FAIL; fixture espera1.22.3, manifesto atual já é1.23.0 e a guarda recusa antes do estímulo. Teste/builders/manifesto/kit envolvidos são idênticos à ea15afc. Não foi corrigido nem encerrado; não integra quality_gate FULL nem as seis suítes de distribuição. A ocorrência não concede exceção de integração.

## Impacto sobre contexto e agentes

AGENTIC IMPACT CHECK: AGENTIC IMPACT DETECTED.

BASIS: o contrato ativo retira um módulo/submenu antigo e introduz domínio, rotas, persistência e testes novos consumidos pelo bootstrap dos agentes. Avaliação IMPACT da skill agentic-evolution-governance: contratos/arquitetura/índices documentais e contexto operacional AFFECTED, ação local REQUIRED dentro do CHG; representações atualizadas com sucessor explícito, mantendo fotografias antigas. AGENTS, skills, CI, norma e autoridade NOT_AFFECTED, ação local NOT_REQUIRED: não mudam seus procedimentos nem precedência e continuam apontando aos contratos vigentes. Testes/gate AFFECTED apenas pela substituição explícita do produto retirado, preservando os demais checks. Memória factual do projeto AFFECTED; recebe somente regressões demonstradas. Grafo/índices externos não foram reconstruídos nem usados como fonte atual; memória global e wiki ai-memory não foram alteradas. Ferramentas ai-memory não estavam expostas nesta sessão; isso não é evidência de falha do servidor.

## Limites e recuperação

Paridade integral de cada interação nativa com Google Sheets: NOT_RUN. A comparação independente anônima alcançou a interface nativa, mas não havia sessão sintética autenticada com o menu Stoikus. Gauntlet heurístico/documental e percurso do site foram executados; comparação cega nativa e vitória medida não são declaradas. Aceite manual do proprietário e compreensão humana permanecem pendentes.

Safari/leitor de tela/aparelho físico não se inferem de Chromium. Compilação/runtime/instalação MT5 não são objeto desta implementação. Incidentes históricos permanecem abertos. A ausência de falhas no recorte testado não é homologação normativa nem aprovação de produção.

Baseline recuperável em `.superpowers/sdd/planning-20261020/baseline.tar.gz`, inventário e hashes em baseline-map.json e baseline-links.json;1568arquivos e8links. Reversão de dados reais não foi executada. O agregado novo é opcional e o legado permanece nos backups; restaurar fontes requer ação delimitada, sem reset de dados.

Revisão adicional de representações: [parecer independente](REPRESENTATIONS-REVIEW.md) conferiu o mapeamento do startup/guia, mantendo o hash de106 identidades e os controles existentes, e o mapa de contexto do novo domínio. O último ajuste CSS do header/footer tem RED geométrico real,110 checks UI GREEN e8 combinações com zoom nativo200% no build ff0f078f70b9fb97; os quatro P2 iniciais de UX permanecem documentados com mitigação no recorte.


## Verificações complementares fora do FULL

- Dez comandos focais finais aprovaram projeções financeiras/Reservas, independência do Forex, gráficos, rascunhos, apresentação, writer, clareza e navegação. Os oráculos financeiros não foram alterados para obter PASS.
- Disponibilidade:26 casos puros,30 contextos de UI, trabalho suspenso e backup/rollback em perfis sintéticos PASS. Ordem:5.040 permutações por controles reais e cinco grupos PASS. Quatro consumidores adicionais: desenho6/6 e280 visitas; jornadaV11 quatro apresentações; proporção5.346 observações; sidebar cinco grupos. O full da sidebar permanece com TEST_HARNESS_FAIL de preparação de MiniGames enquanto o checklist Forex está aberto. A guarda correta não foi removida.
- Seis suítes de distribuição Stoikus PASS, incluindo18 testes do pacote e40 de entrega R4/R5. O branding complementar permanece na limitação de baseline descrita acima. HOST48 e MT5 nativo não executados por não haver mudança das fontes/cálculos MQL.
- Bolsas Globais: integração com `--distributions` retornou PASS em arquivo modular, portátil isolado e PWAoffline;16 praças, instância única, finalização e estado financeiro intacto. O runner conserva18 observações marcadas BASELINE_FAIL no shell antes da ferramenta, em reflow aproximado por CSSzoom2 e390 px. Essa marca local significa que o overflow já existia antes de abrir a área no mesmo candidato; não comprova por si só comparação contra ea15afc. A área das bolsas permanece contida na largura disponível. Não foi confundida com zoom nativo200%, que recebeu prova própria de8 combinações no Planejamento. Esse limite de shell em reflow aproximado não foi resolvido incidentalmente.

O frescor dos quatro testes de navegação executados em5e8a1978a7ef3cb2 foi delimitado:120scripts idênticos, diferença CSS restrita a `flex-shrink:0` no header/footer de formulárioPlanning, que nenhum desses casos abre. A inversão das duas propriedades reproduz o SHA anterior. O formulário alterado foi verificado novamente em110 casos e zoom nativo. Não há transferência de resultados entre alterações de comportamento distintas.


Prévia local retomada na origem anterior: [abrir o site](http://127.0.0.1:53221/index.html?v=ff0f078f70b9fb97) → Planejamento. index/build/UI/CSS servidos foram conferidos contra os arquivos atuais; nenhum dado do navegador do proprietário foi lido ou migrado. Servidor local não é publicação. Finalização da tarefa aguarda avaliação manual do proprietário; Git e publicação não foram executados.

Conferência final de escopo: [SCOPE](SCOPE.json),213 arquivos protegidos inalterados,397 inputs de runtime e254 identidades de testes sem drift; nenhum caminho fora da allowlist. Preflight e diff-check finais PASS.
