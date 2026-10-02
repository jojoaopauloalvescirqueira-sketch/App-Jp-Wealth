# Histórico Pessoal — contrato do núcleo e armazenamento

Estado: implementação candidata 1.18.0, sem aceite operacional. Este contrato explica os arquivos, não concede autoridade financeira ou permissão de instalação. Base e fronteira estão no CHG desta revisão.

## Responsabilidades e isolamento

`JPW_PersonalHistory_Core.mqh` é puro: recebe capturas e sujeitos tipados, reconcilia episódios, decide prazos e máximos; não lê o terminal, grava arquivos, negocia ou mostra avisos. Posição é identificada pelo identificador estável e a pendente pelo ticket, ambos como texto decimal. Tipo e conta fazem parte do contexto. `SL == 0` somente cria episódio com leitura válida; SL ilegível permanece desconhecido.

`JPW_PersonalHistory_Store.mqh` possui SQLite e namespace próprios: `MQL5/Files/JPWealth/Genetrix/PersonalHistory/history_<chave opaca>.sqlite`. Não usa FILE_COMMON, não altera os registros de MDD, Diagnostics, Stop Risk ou ledger. A chave recebida deve ser o hash estável do contexto conta/servidor/moeda/instalação; versão do produto não participa da identidade. Token de escritor é uma cerca de titularidade, distinto da chave da conta.

`JPW_PersonalHistory_Export.mqh` fornece consulta CSV e backup JSON versionado. Exportação é explícita e exclusivamente local; nenhum destino existente é substituído. Recuperação aceita apenas um novo nome sob `PersonalHistorySandbox`, nunca uma base operacional. Não há exclusão automática de dados financeiros.

## Estado puro e relógios

Um episódio permanece ativo até SL positivo ou inventário integral demonstrar desaparecimento. Remover novamente o SL abre novo episódio. O controlador pode acrescentar motivo de fechamento/cancelamento/execução somente com evidência; `NO_LONGER_PRESENT` não presume o motivo. A ausência de conexão ou inventário instável rejeita a reconciliação. Perda de leitura do SL de um sujeito não cria falso aviso nem resolve seu episódio.

Aviso inicial é devido no primeiro encontro válido. Durante a sessão o prazo usa tempo monotônico, 60.000 ms; estado restaurado revalida pelo UTC persistido e converte o prazo restante ao relógio monotônico. Prazo vencido ou relógio incoerente produz no máximo uma solicitação após revalidação, seguida de novo prazo de 60 segundos. Fechar popup não modifica episódio. `MarkRequested` é chamado independentemente do sucesso da persistência, impedindo uma rajada quando o banco falha.

Pico = nocional bruto aberto/equity; pendentes não fazem parte do numerador. Captura instável, denominador não positivo ou cálculo incompleto não atualizam máximos. Current e Estimated têm picos independentes. Comparação usa o double completo, sem arredondar; empate conserva primeira fotografia. Snapshot e pico são uma única carga transacional.

## SQLite e trilha

Schema próprio v1: `ph_meta` conserva identidade, versão, sequência, início e último evento; `ph_owner` conserva titular e clocks de lease; `ph_rows` é diário imutável de sequência contígua; `ph_episodes` e `ph_peaks` são projeções auditáveis apontando para linhas testemunhas. As categorias SESSION e COVERAGE registram sessões/lacunas, EPISODE mudanças de sujeitos, EVENT fatos da reconciliação, ALERT fases de aviso, PEAK recordes e sua fotografia.

Cada gravação verifica titularidade dentro da transação. Lease viva impede segundo escritor; takeover expirado muda o token e cerca chamadas do titular anterior. O adapter conserva ainda handle de arquivo exclusivo para evitar alertas duplicados quando o SQLite está indisponível. Esse comportamento de exclusividade requer prova nativa; host SQLite não certifica a implementação do filesystem do MT5.

Avisos possuem fases imutáveis INTENT, CALLED e RESULT compartilhando identificador de grupo. Intenção não prova chamada, chamada não prova exibição, som solicitado não prova audição. Interrupção conserva o estado incerto; não há promessa de entrega exatamente uma vez. Corrupção, schema futuro, ocupação e erro não autorizam recriação/reset. Falha de gravação exige estado explícito de histórico incompleto no controlador/Cockpit.

Ao recuperar o banco, reconciliar estado persistido e prazos mantidos em memória antes de emitir avisos. Um máximo alterado cuja transação falhou permanece pendente de gravação; não descartar o recorde só porque a próxima captura é menor. Após gravação confirmada, retirar apenas episódios encerrados da memória; o diário financeiro permanece no banco.

## Exportação e recuperação

CSV traz símbolo, estado, qualidade e IDs textuais; IDs têm apóstrofo deliberado para evitar perda de precisão em planilhas. O payload canônico adicional conserva os dados originais, incluindo tickets acima de 2^53. Conteúdo que possa iniciar fórmula recebe proteção; aspas são duplicadas. UTF-8 e CRLF são explícitos, seguindo FileWriteString nativo.

Backup JSON usa campos numéricos identificadores como strings e payloads hexadecimais UTF-8 reversíveis. Cada linha possui SHA-256 e a raiz conserva SHA-256 da representação canônica, chave, sequência, início e fim. Formato diferente, linha alterada/truncada, sequência divergente ou contexto errado é recusado. O limite de capacidade de construção/parsing é 32 Mi caracteres: recusa de exportação é explícita e não exclui o banco. O checksum detecta alteração; não é autenticação criptográfica de terceiros.

A reconstrução isolada repõe diário e projeções em transação, confere sua integridade e preserva sandbox parcial diante de erro. Não restaura titularidade operacional nem arma monitor ou supervisor. Releitura do JSON exportado verifica os bytes normalizados e conteúdo antes de anunciar confirmação.

## Fronteira de evidência

Oráculo e testes usam referências independentes, SQLite real no host e tradução dos mesmos headers MQL. Não demonstram compilação MetaEditor, .ex5, popups, som, timer pontual, exclusividade de FileOpen nativo ou corretora. Esses itens permanecem NOT_RUN até evidências nativas vinculadas aos fontes exatos.

Referências primárias: [MetaQuotes — FileWriteString](https://www.mql5.com/en/docs/files/filewritestring), [DatabaseTransactionBegin](https://www.mql5.com/en/docs/database/databasetransactionbegin), [Alert](https://www.mql5.com/en/docs/common/alert), [PlaySound](https://www.mql5.com/en/docs/common/playsound).

### Auditoria integral e capacidade

Antes de habilitar um escritor, `JPWPersonalAuditRows` verifica hashes e sequência de todo o diário disponível. A primeira versão limita essa auditoria a 100.000 linhas e 2.000 ms por tentativa; exceder o limite produz IO_ERROR com indisponibilidade explícita, preserva a base e não comprova corrupção. O limite protege o terminal e não autoriza apagar/rotacionar história; acervos que o excedam precisam de evolução candidata para auditoria incremental.

O Cockpit não repete o hashing integral a cada abertura de leitura. Schema, integridade SQLite, relações de projeção e os objetos efetivamente lidos são verificados; um resumo válido não certifica todas as páginas históricas. O backup verifica cada payload e sua sequência durante a exportação, e a reconstrução isolada repete a auditoria antes da confirmação.
