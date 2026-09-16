# Consolidado FX — análise local por conta e origem

Base da implementação `01c08241ccb7bc229a05779a52f577ee55a69ae7`.
Contratos: CHG-FOREX-CONSOLIDATED-20260914 e complemento PDF/build.
O lote inicial foi integrado em `b2f0e54993ff79f7eaab62eba5b37510af43013c`.
Revisão cadastral local N2: CHG-FX-ACCOUNT-REGISTRATION-20260915; ainda sem aceite ou integração. Sem homologação financeira.

## Responsabilidades e fontes

Forex → Consolidado FX fica depois de Contabilidade. A seleção é analítica:
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
