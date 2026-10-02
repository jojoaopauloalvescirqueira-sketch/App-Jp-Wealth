# Parecer independente sobre o módulo Risk — 2026-10-01

## Escopo e conclusão

Revisão de leitura do Core, adaptador Terminal, Store, EA Supervisor, script MQL de testes e ferramenta de execução no host, no checkout isolado `/private/tmp/jpw-genetrix-risk-ledger-20261001`. O revisor é autor da UI consumidora, mas não escreveu os módulos Risk examinados. Este parecer não aprova a própria UI, não homologa o modelo ou a execução financeira e não certifica independência externa.

O primeiro congelamento tinha um achado material de apresentação do estado do supervisor. A correção apareceu durante a revisão; o EA foi relido no novo hash. Os caminhos de recusa agora centralizam a apresentação, distinguem OBSERVE de READY desarmado e não renovam a data da captura financeira por mera persistência. Essa constatação é documental, sem execução do EA. Não identifiquei outro defeito P1/P2 de execução demonstrado nesta leitura limitada; isso não é um veredito de funcionamento completo.

A divergência entre promessa do dossiê e campos realmente registrados sobre o efeito de remover uma perna de hedge foi corrigida no texto após o achado, com atribuição ao protocolo demo e reconhecimento da limitação do código. O supervisor é candidato para testes posteriores, com compilação nativa, orquestração do EA, corretora, reconciliação e visualização MT5 ainda `NOT_RUN` nesta revisão.

## Identidade antes e depois

Todos os caminhos abaixo são relativos ao checkout isolado. Os hashes iniciais foram conferidos com os informados pelo autor. A mudança do EA ocorreu pelo autor; o revisor não alterou código, testes, fixtures ou regras.

| Arquivo | SHA-256 inicial | SHA-256 após releitura |
|---|---|---|
| `mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Genetrix_Risk_Core.mqh` | `8541070cd2544cd44eb083fbca27ea82b3bba201c21ea75b46ab7cacbdf42f5e` | igual |
| `mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Genetrix_Risk_Terminal.mqh` | `7a2de90a6b429a514653c1bba309272aab0944f42d6f18a057f2c400ce0cb68f` | igual |
| `mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Genetrix_Risk_Store.mqh` | `fc5a858e2a28a67613734d12e266acb082b5b94100104e8246fb65375e20b442` | igual |
| `mt5/jpw-alavancagem-atual/MQL5/Experts/JPWealth/JPW_Genetrix_Supervisor.mq5` | `f252f047e17690d17ce9c545950376e0f8e60d4b327d6f926b59b0892c6bbf7b` | `49f5500c94df132d218dbb426310c39ab9481e2dec54cbfd40280b3008a04bd1` |
| `mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth/JPW_Genetrix_Risk_Tests.mq5` | `53056a0025cb359cc19ea202d4312921a2348bb1fb1e4c63e91e97482f60c41b` | igual |
| `tools/jpw_genetrix_risk_test.py` | `4f71259e738035c69d5531cc844976526c4d5c542a7ff87ab731a794992d1454` | igual |

## Achados e encaminhamento

1. **RISK-R01 — P1 de comunicação do estado de segurança, corrigido documentalmente no novo hash; comportamento nativo NOT_RUN.** No EA inicial, `Comment()` era atualizado somente no caminho bem-sucedido de planejamento, linhas 389–394. Retornos por captura inválida/planejamento recusado, linhas 384–386, UNKNOWN, linhas 376–380, e troca de conta, linhas 350–352, preservavam a mensagem anterior. Depois de enviar uma intenção, a persistência passava a UNKNOWN sem atualizar essa mensagem. Isso podia deixar leitura Current, estado anterior e proposta anterior na tela embora o executor estivesse bloqueado ou aguardando reconciliação. No EA novo, `JPWSupervisorPresent`, linhas 52–78, é chamado por `JPWSupervisorPersist`, linha 82; N/A oculta números, intenção ativa é rotulada sem conclusão e a proposta é zerada a cada timer, linha 396. Os ramos de contexto, captura e UNKNOWN persistem/apresentam seu motivo, linhas 401–444. Recomenda-se executar transições do EA com prova de texto final, inclusive UNKNOWN após OrderSend, captura inválida, contexto, falha de store e permissões. Não basta testar o núcleo puro.

2. **RISK-R02 — P2, corrigido documentalmente no novo hash; comportamento nativo NOT_RUN.** No EA inicial, a perda de permissão fazia `armed=false`, mas mantinha fase READY, traduzida como READY_DEMO. No novo EA, `RefreshView`, linhas 40–41, traduz READY desarmado em OBSERVE; a perda de permissão faz desarme, N/A, aviso persistente de rearme explícito e retorno, linhas 407–414. Guards em `Send`, linhas 264–271 e 287–317, preservam a recusa posterior. UNKNOWN e intenção não são apagados para aparentar normalidade. A validação observável deve checar simultaneamente `phase`, `armed`, view e mensagem, antes/depois de reconectar.

3. **RISK-R03 — P2 documental, corrigido no dossiê; apuração demo NOT_RUN.** A redação inicial de `docs/work/GENETRIX-PESQUISA-7X-COMPENSADO-20261001.md`, linha 55, declarava que o supervisor deveria registrar o aumento da exposição líquida direcional quando LIFO remove uma perna do hedge. `JPWRiskView`, Store linhas 10–33, e o payload/receipt, linhas 57–80 e 193–208, não contêm exposição líquida antes/depois nem inventário integral que demonstre esse efeito. A leitura permite registrar gross/equity e a ação, mas não o registro automático prometido. Após o achado, o root ajustou a linha 55: o protocolo demo registra esse efeito com inventário antes/depois e histórico; o código candidato não calcula nem registra automaticamente a variação do líquido direcional. O revisor conferiu essa redação salva. Não houve ampliação de escopo, mudança de LIFO ou otimização de hedge por inferência.

4. **Alerta retirado — erro de inferência do revisor, sem defeito confirmado.** Durante o delta, o revisor inferiu que a remoção da renovação de `observed_utc` em `RefreshView` faria o primeiro save falhar por timestamp zero. Essa inferência misturou a inicialização antiga com o helper novo. A leitura direta do EA `49f5500c…`, linhas 341–347, confirmou timestamp para o envelope inicial N/A, antes do primeiro save; capturas válidas renovam a data em 423–424, e mera persistência não o faz. O alerta foi retirado e comunicado ao root/autor. Nenhum teste de inicialização do EA foi executado.

## Contratos observados na fonte

- O Core compara `sample.leverage > 7.0` sem arredondamento de apresentação; usa soma bruta, equity da captura e prefixo de pendentes mais recentes. Reconciliamento aritmético usa tolerância somente para integridade, não para deslocar o gatilho (Core 141–174 e 202–228).
- Poda fecha o volume integral da posição mais recente; empate pelo identificador é convenção declarada. Recusa do fechamento pausa/desarma sem pular para uma posição antiga; parcial confirmado mantém intenção do remanescente, mesmo abaixo de 7x; UNKNOWN impede nova intenção (Core 183–200, 215–225 e 231–255).
- Pendentes usam preço de entrada condicional, quotes de conversão e equity congelados; não constituem garantia de exposição futura. O adaptador requer captura estável e reconciliação de linhas, specs e equity (Terminal 73–171). Quote/mercado podem mudar após essas verificações; o próprio EA registra a ausência de atomicidade de servidor.
- Execução tem uma única chamada `OrderSend`, EA novo 321, precedida de identidade demo exata, hedging sem FIFO, permissões, reselect, composição e equity depois do save durável e depois de OrderCheck. Conta real é recusada por Terminal 174–186. Nenhum código de abertura/reversão, alteração de SL/TP ou CloseBy foi localizado no construtor de requisição 233–256.
- Resultado de envio não prova execução. A reconciliação exige estado histórico terminal e portfólio coerente; ausência/tempo não liberam UNKNOWN (EA 125–231). Reabertura consome/rotaciona desafio; UNKNOWN não permite rearme/replay (EA 349–377). Os custos já incorporados à equity não são subtraídos outra vez do denominador.
- Store novo usa namespace e chave por política/conta/instalação, checksum e roundtrip canônico, intenção persistida antes de enviar, slot interrompido sem fallback silencioso. A API consumidora observa estado datado; não certifica executor ativo (Store 36–42, 82–141, 152–218). Lock de arquivo local não fornece coordenação entre instalações nem veto a ordens manuais/outros EAs.
- 7x adicional não substitui tetos/denominador por fase da V11, RC, orçamento ou Operação formal. Nenhuma homologação ou alteração estatutária resulta desses testes.

## Evidência e limites

Executado nesta revisão: `python3 tools/jpw_genetrix_risk_test.py`, sem evidence-dir, somente em APIs/arquivos sintéticos temporários. Resultado **38 PASS / 0 FAIL**, sendo 26 checks do Core/script e 12 de codec/store/lock sintético. O compilador C++ concluiu sem falha. Esta execução usa corpos reais de Core/Store e fixtures do autor; o JSON independente de oráculos é referência de auditoria, não alimenta esses 38 checks. Não foram alterados expected, fixtures ou critérios.

**NOT_RUN:** compilação MQL nativa, EX5, EA lifecycle/OnTimer/OnTradeTransaction/OrderSend, permissões de corretora, race de pendente preenchida, reconciliação de retorno incerto, crash durability, lock nativo, UI/Comment no MT5 e conta demo. Os casos RIS-AC14/15 não são executados por esse host; RIS-AC16 testa só a primitiva sintética de lock. Nenhuma rodada da revisão própria UI integra este parecer.

É necessário refreeze e testes pertinentes se código mudar novamente. O resultado host e esta leitura não demonstram aplicabilidade operacional, operabilidade contínua ou conformidade normativa integral.
