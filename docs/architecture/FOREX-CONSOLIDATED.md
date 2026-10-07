# Consolidado FX — análise local por conta e origem

Base da implementação `01c08241ccb7bc229a05779a52f577ee55a69ae7`.
Contratos: CHG-FOREX-CONSOLIDATED-20260914 e complemento PDF/build.
O lote inicial foi integrado em `b2f0e54993ff79f7eaab62eba5b37510af43013c`.
Revisão cadastral local N2: CHG-FX-ACCOUNT-REGISTRATION-20260915; ainda sem aceite ou integração. Sem homologação financeira.

## Responsabilidades e fontes

Na revisão de navegação local, Forex → Consolidado FX é a primeira entrada.
O painel à direita mostra o contexto da Conta operacional; o seletor principal
identifica a Conta em análise. Expandir o contexto conserva filtros e importação
e não persiste preferência. Contrato: CHG-FOREX-NAVIGATION-JOURNEY-20260915.
A seleção continua analítica:
não chama `JPWForex.state.selectAccount`, não altera a conta operacional e não
registra observações financeiras. Configurações → Forex → Conta padrão do
Consolidado salva explicitamente a preferência. Sem preferência, somente uma
conta MESTRE inequívoca é selecionada; indisponibilidade/ambiguidade exigem escolha.

`S.operationHistory` é a única fonte Manual. `S.fxConsolidated` schema1 contém
`accounts[]` (identidade, ordens, execuções, snapshots de posições e resumos),
`receipts[]`, `revisions[]`, `defaultAccountId`. Não armazena arquivo original,
credenciais nem duplicata da fonte Manual. Conta histórica não reativa operação.
As fontes MT5 e Manual nunca são somadas automaticamente.

| Componente | Responsabilidade |
|---|---|
| `src/js/10-domain/17-fx-consolidated-model.js` | Parser HTML inerte, validação, comparação/revisão e projeção descritiva pura |
| `src/js/40-app/24-fx-consolidated-import.js` | Prévia em RAM; comandos explícitos sob writer lock, epoch, revisão e confirmação do escritor existente |
| `src/js/40-app/25-fx-consolidated-pdf.js` | PDF.js local, texto de resumo reconhecido, cancelamento e liberação de worker |
| `src/js/20-ui/28-fx-consolidated.js` | Quatro abas, filtros/conta, prévia/confirmação, gráficos e valores indisponíveis |

Namespace interno `window.JPWFXConsolidated`: `emptyState`, `validateState`,
`parseHTML`, `previewImport`, `applyImport`, `project`; `accounts`, `prepareImport`,
`confirmImport`, `saveDefaultAccount`, `cancelImport`; `parsePDF`, `disposePDF`;
`render`, `settingsMarkup`, `bindSettings`, `reset`; `validateReport`,
`inspectRegistration`, `beginRegistration`, `saveRegistration`,
`cancelRegistration`, `openAccountRegistration`.

## Importação e identidade

Relatório normalizado: `{format, identity:{login,broker,currency,server},
period:{from,to,declared,timezone}, generatedAt, orders, deals, positions,
summary, issues, coverage}`. Tickets/logins são strings. Campos não observados
são null, nunca zero inferido. HTML clássico reconhece tabelas PT/EN. PDF digital
reconhecido é resumo de uma página, sem gerar execuções a partir de estatísticas.
Sem OCR, upload, API de corretora, CDN ou preços ao vivo.

Número ausente/divergente bloqueia confirmação. Cadastro de destino e vínculo
anterior são conferidos; outras ausências de identidade são explicitadas.
A confirmação humana não substitui o número ausente nem autentica o arquivo.
Não há troca automática de destino. Mudança de vínculo incompatível é recusada;
não há nesta revisão um assistente para transferir um histórico entre identidades.

A leitura do arquivo pode ocorrer sem destino selecionado. `inspectRegistration`
reutiliza a validação do modelo antes de oferecer qualquer ficha. Preparação e
confirmação (sob lock) exigem cadastro **atual** em `S.accounts`, com login textual
e plataforma MT5; não utilizam o preenchimento histórico do catálogo de consulta
como prova de cadastro atual. Identificadores presentes de corretora/moeda/servidor
precisam ser compatíveis com relatório e vínculo histórico. Metadados opcionais
ausentes mantêm sua limitação; senha não participa dessa conferência.

Estados distintos: outra conta correspondente (seleção explícita), cadastro
incompleto (completar), documento desconhecido/divergente (nova ficha sem alterar
a conta selecionada), histórico (recadastro) e ambiguidade (revisão dos cadastros).
O formulário também é acessível por Adicionar Conta. Rascunho em memória e
salvamento explícito pelo comando Forex existente, com lock, epoch e releitura;
a confirmação cadastral não confirma importação. Após salvar, o documento é
revalidado e uma confirmação própria da importação continua obrigatória.

Nome/tipo e identificadores são cadastrais. `platformCurrency` e `platformServer`
em `S.accounts[]` são metadados opcionais salvos pela ficha; não equivalem a
observações financeiras em `S.forex.accounts`. Nenhum saldo, equity ou risco do
relatório preenche o cadastro. Completar preserva campos existentes; novo cadastro
e recadastro usam os defaults cadastrais legados sem ativar conta ou restaurar
fatos operacionais. Recadastro histórico exige confirmação e reutiliza o ID.
Duplicatas e vínculos históricos incompatíveis são recusados. Backup inclui esses
campos pelo mecanismo existente, sem migração. Finalizar Sessão conserva o histórico
mas encerra a ficha/prévia e retira os cadastros atuais: importar novamente exige
recadastro explícito. A captura da finalização conserva metadados explicitamente
cadastrados no catálogo mínimo; preenche apenas lacunas compatíveis de catálogos
sem conteúdo importado. Não mistura identidades divergentes nem preenche moeda
ou servidor ausentes de relatórios passados com o cadastro atual. Cancelar descarta o rascunho; recusa comprovada mantém a ficha
para retry explícito; UNKNOWN impede repetir antes de conferir a base.

Prévia não grava. Confirmação revalida conta/estado/epoch, usa `save()` existente
e exige releitura; recusa comprovada reverte apenas o delta próprio. UNKNOWN
preserva o tratamento existente e bloqueia retry cego. Mesmo conteúdo é no-op;
conflito de ticket/resumo exige revisão explícita e mantém antes/depois.
Ausência em relatório parcial não apaga fatos. Recibos incluem hash SHA-256 do
arquivo, parser, período, contagens, avisos e reconciliação quando calculável.
Originais são necessários para futura reinterpretação e devem ser guardados
pelo proprietário fora do aplicativo.

## Metodologia descritiva `fx-descriptive-v1`

`project` exige conta e fonte. Primeiro filtra conta, moeda e período; depois
calcula. Cada métrica contém valor, unidade, disponibilidade, motivo/metodologia;
importadas incluem período do snapshot. O cabeçalho cadastral não atribui moeda
ou contexto atual a fatos históricos. Registros Manual sem accountId superior
ficam em Não conciliados, visíveis sem totais monetários; aliases legados somente
em contextos aninhados não são reinterpretados nesta revisão.

MT5: resultado líquido soma componentes assinados uma vez, com comissões avulsas
identificadas; depósitos/retiradas ficam fora do lucro. Lucro/perda brutos e Profit
Factor calculados usam profit antes dos custos; isso não promete identidade com
todos os métodos do MT5. Vitórias/médias/sequências usam deals de saída, incluindo
saída parcial, reversão e Close By, sem fingir uma posição completa. Direção da
execução e direção encerrada são distintas. Manual usa resultado líquido capturado
por operação finalizada; não converte operação JP Wealth em deal.

Saldo/crescimento/drawdown calculados exigem um relatório completo preservado
com período, conjunto e conteúdo de execuções suficientes, abertura conhecida,
moeda única e componentes calculáveis. Uma atualização parcial não estende essa
prova. Crescimento compõe fatores ajustados aos fluxos; mensal/anual não somam
percentuais. Com filtro de datas, a curva de crescimento é um recorte do
acumulado desde abertura; a métrica informa o retorno do período. Drawdown importado
permanece informado como base do relatório, sem presumir saldo ou equity. Drawdown de saldo é descritivo e inclui lançamentos de caixa, não
é equity nem DD normativo. Divergência saldo informado/ledger produz aviso e
preserva ambos. Snapshots sobrepostos não são somados; importação antiga não
substitui silenciosamente a fotografia mais recente.

Equity histórica, carga, MFE/MAE e radar ficam indisponíveis quando faltam as
séries/eixos necessários. Sharpe e outros resumos só são apresentados como
importados quando reconhecidos. Não há fórmulas de elegibilidade na UI, nem
mudança em fases, limites, reservas, FCR/FEO ou parâmetros do motor V11.

## Persistência, encerramento e distribuição

Backup completo inclui o agregado pelo clone existente de S; restore valida
forma suportada e preserva versões futuras opacas. Finalizar Sessão preserva
operationHistory e fxConsolidated confirmados, incluindo catálogo mínimo e
preferência; encerra trabalho de importação, esvazia contas operacionais e não
recria saldos. Exclusão total explícita continua removendo a base.

PDF.js 6.3.289 e worker oficiais, licença/proveniência e hashes são declarados em
`manifest.runtimeAssets`, separados de scripts clássicos. O gerador oficial
inclui recursos no fingerprint e leitor no portátil. O portátil também transporta os bytes da licença e proveniência. PWA precacheia module/worker;
nenhuma configuração global é necessária. O parsing não executa ações/JavaScript
embutidos no documento; HTML é processado em template inerte por allowlist textual.

## Evidência e limites de aceitação

Fixtures/gabaritos sintéticos: `tools/fixtures/mt5-consolidated/`. Testes focais:
`fx_consolidated_model_test.py`, `fx_consolidated_storage_test.py`,
`fx_consolidated_pdf_test.py`, `fx_consolidated_ui_test.py`,
`fx_account_registration_test.py` (cadastro, escrita e interface). FULL existente e
revisão independente complementam, não substituem importação real/revisão humana.
Relatórios, hashes, contraprovas, comparador e recovery ficam no diretório externo
`/Users/joaopauloalves/.codex/forex-consolidated/20260914/evidence/`.

O PDF fornecido teve compatibilidade de resumo examinada localmente, sem cópia
ou upload de dados reais. Não foi fornecido HTML detalhado do exportador do
proprietário: sua homologação permanece NÃO VERIFICADA. Outros navegadores,
leitor de tela e fidelidade visual humana ao MQL5 não são aprovação automática.
A12 parcial, OPEN-05/V11/FCR/FEO, AUD-05/P2 e demais dívidas anteriores continuam
separadas. Esta documentação não concede aceite ou permissão de publicação.


## Contas e Período — candidate 2026-09-23

CHG-FOREX-CONTAS-PERIODO-20260923 centraliza gestão no destino interno preservado `forex-management-accounts`, rotulado Contas e Período. `S.accounts` continua fonte cadastral; `S.fxConsolidated.accounts` é identidade/histórico importado, não catálogo concorrente. O wizard de cinco etapas usa `beginRegistration/saveRegistration`, agora com ambiente real/demo opcional e perfil explícito nos novos cadastros. Editar lacunas e nome preserva vínculos históricos; troca de identidade conhecida é recusada. Perfil confirmado e cadastro são salvos juntos. Alteração deliberada exige motivo, preserva a fricção local de perfil e vale apenas em período posterior confirmado.

Preparação e observação continuam em `beginAccountSetup/saveSetupPeriod/saveSetupObservation`, com confirmação por etapa, recusa e UNKNOWN distintos. Reabrir usa a mesma conta. Consulta não seleciona operacionalmente: `JPWForex.accountsUI.useContext` passa pelas guardas antes de aplicar o par. Importação usa as mesmas APIs, nenhum ticket é transformado em ordem manual. O candidate anterior de onboarding não foi integrado nem copiado.

O gesto explícito de iniciar cadastro/preparação estabelece somente uma geração de sessão ausente usando `sessionEpochCurrent()` e sua releitura canônica. Consulta não inicializa geração. Valor vazio, leitura indisponível, UNKNOWN, recuperação ou sessão bloqueada continuam recusados; geração existente não é rotacionada. Isso não reinicia o aplicativo nem altera dados financeiros.

## Candidate visual — 2026-10-05

Contrato CHG-JPW-FOREX-VISUAL-RISK-20261005, base ac3a2fa. A conta consultada continua independente da seleção operacional; MT5 e Manual usam suas projeções existentes e separadas. Três indicadores antecedem uma única curva principal (crescimento/saldo MT5 ou resultado realizado manual). Radar, distribuições e comparações permanecem em Estatísticas, sem miniatura duplicada de crescimento. Histórico de equity ausente não produz curva substituta.

O componente visual recebe observações prontas. Datas completas e coerentes usam distância temporal proporcional; referências ambíguas ou incompatíveis são explicitamente sequência de registros. Horários sem zona não recebem conversão presumida. Lacunas interrompem segmentos; uma observação produz ponto, não tendência. Mouse, toque e teclado consultam valores exatos; a tabela permanece acessível. Não há suavização, preenchimento de dados nem gravação financeira na interação.

A plotagem tem altura estável de aproximadamente 320px ou 240px em área estreita. Textos são HTML separado da geometria SVG. Fonte, cobertura e importação qualificam a série; resize apenas ajusta apresentação. Validação desta revisão fica no relatório externo do candidate, sem promover evidências antigas.

## Candidate profissional — painel integrado (2026-10-05)

Contratos JPW-FOREX-PROFESSIONAL de apresentação, projeção e testes; candidate isolado derivado do visual 0b165ab8911f1f3b. Não representa integração, publicação ou aceite financeiro.

As quatro áreas preservam IDs `account/history/statistics/risks` e passam a exibir Painel, Movimentos, Estatísticas e Risco. Painel reúne KPI do período, curva principal e drawdown histórico do saldo com domínio temporal e consulta sincronizados. O DD é desenhado para baixo mantendo seu valor percentual original positivo. A ausência de série não cria uma curva. Saldo/equity informados conservam período/origem; não são apresentados como observações ao vivo.

Filtros All/12m/3m/custom consultam `project`, sem novo motor. Atalhos usam a última data efetivamente disponível. KPI de crescimento pertence ao período; curva MT5 permanece acumulada desde a origem, recortada sem rebase. Resumo sem eventos não fornece novos subperíodos. Datas incompatíveis usam sequência declarada; leituras coincidentes distinguem evento/ticket. As tabelas alternativas preservam valores sem arredondamento e lacunas.

Mapa mensal usa exclusivamente `breakdowns.monthly/years`, com unidade selecionada, zero distinto de ausência e total observado produzido pelo modelo. Clique em mês/instrumento/direção filtra somente Movimentos. Resumos sem eventos explicam a impossibilidade de abrir os registros. A busca da tabela não altera os indicadores. Marcas de caixa vêm de lançamentos efetivos de balance, sem alterar crescimento ou resultado.

Distribuições mostram somente resultado líquido por instrumento/direção, em escala homogênea. Estatísticas identificam deals de saída, incluindo parcial/reversão/Close By; Manual identifica operações locais finalizadas. Custos e caixa têm grupos próprios e não são novamente adicionados ao líquido. Detalhe de movimento separa identificação, execução, resultado/custos e proveniência, com dados técnicos expansíveis.

Estado de apresentação permanece em RAM: filtros, consulta, seleção, expansão e ordenação não escrevem fatos. Conta em análise e conta operacional mantêm fontes independentes. As explicações distinguem drawdown de saldo (inclui caixa), drawdown informado no relatório e DD operacional. Os produtores financeiros, importadores, schemas e comandos existentes permanecem inalterados. Limite conhecido DD14 não é corrigido por esta interface.

## Delta de apresentação por tarefa — 2026-10-05

A rota forex-consolidated continua canônica; seu nome visível é Desempenho. Contexto separa Em análise/Em operação, conserva fonte/moeda/cobertura e apresenta datas sem conversão implícita de fuso. Cobertura conserva os horários declarados. Painel/Movimentos/Estatísticas/Risco usam os mesmos produtores; os quatro controles ocupam duas linhas estreitas. Estatísticas agrupam disponibilidade e desenham negativos à esquerda do zero, sem alterar netProfit. O aviso de importação é dispensável em RAM; a ação de preparar conta continua acessível.

O Histórico local mantém a rota forex-history e histState.archiveScope como consulta RAM de qualquer conta/período conhecido. Ausência explícita recusa resultados, não troca pela operacional. IDs, filtros e foco permanecem estáveis. O menu se organiza com títulos sem novo nível interativo.
