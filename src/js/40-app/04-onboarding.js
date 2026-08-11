// ============ QUESTIONÁRIO DE INÍCIO DE PERÍODO (SET 5b) ============
function onboardingEP(saldo, prKey){
  const pr=getActiveRiskProfile(prKey);
  return {ep:saldo*(1-pr.mdd), obj:saldo*(1+pr.anual), pr};
}
function equityProtectorEducationHTML(){
  return `<div class="risk-note">
    <b style="color:var(--ink)">Equity Protector.</b> Use como camada externa de defesa para limitar perdas automaticamente, proteger patrimônio, reduzir risco operacional e complementar a disciplina do painel. Traders Connect é um exemplo de plataforma que pode oferecer esse tipo de proteção operacional.
    <br><br>
    O Equity Protector não substitui a gestão de risco do JP Wealth, não garante proteção absoluta e deve ser configurado conforme a fase vigente, o perfil ativo e o limite máximo do sistema. Ele é uma barreira adicional; a exposição real continua limitada pelo Estatuto.
  </div>`;
}
function leverageEducationHTML(opts={}){
  const body = `
    <b style="color:var(--ink)">Alavancagem da corretora.</b> Alavancagem disponível é o limite que a corretora oferece; alavancagem utilizada é a exposição real aberta pela operação; margem livre é o espaço operacional restante; margin call ocorre quando a margem fica insuficiente; excesso de exposição é operar acima do limite do Estatuto ou do perfil, mesmo que a corretora ainda aceite margem.
    <br><br>
    <b style="color:var(--ink)">Referência operacional: trate 1:30 como marco mínimo de colchão de margem. Alavancagens acima de 1:30 podem reduzir pressão de margin call, mas nunca autorizam aumentar o risco real da ordem.</b>
    <br><br>
    Psicologicamente, margem sobrando pode gerar falsa sensação de segurança, excesso de confiança e tendência a aumentar lote após sequência positiva ou tentativa de recuperar perda. Use a alavancagem disponível para reduzir pressão operacional, não para expandir exposição. A disciplina é manter a exposição real abaixo dos limites da fase e do perfil, preservar margem livre e evitar que disponibilidade de margem vire decisão emocional.
  `;
  if(opts.interactive){
    return `<div class="risk-note">${body}</div>`;
  }
  return `<div class="risk-note">${body}</div>`;
}
function projectCycleEndISO(startIso){
  if(!startIso || !/^\d{4}-\d{2}-\d{2}$/.test(startIso)) return '—';
  const [y,m,d]=startIso.split('-').map(Number);
  const end=new Date(y,(m||1)-1,d||1);
  if(Number.isNaN(end.getTime())) return '—';
  end.setFullYear(end.getFullYear()+1);
  end.setDate(end.getDate()-1);
  const yy=end.getFullYear();
  const mm=String(end.getMonth()+1).padStart(2,'0');
  const dd=String(end.getDate()).padStart(2,'0');
  return `${yy}-${mm}-${dd}`;
}
function fmtDateEU(iso){
  if(!iso || !/^\d{4}-\d{2}-\d{2}$/.test(iso)) return '—';
  const [y,m,d]=iso.split('-');
  return `${d}/${m}/${y}`;
}
const ESTATUTO_V10_FULLTEXT = `===== PÁGINA 1 =====
JP WEALTH MANAGEMENT SYSTEM  
    
ESTATUTO OPERACIONAL E GESTÃO DE RISCO   
 
      Versão 10.0 — Consolidação Normativa Integral  Documento: JPW-GOV-001  ·  Classificação: Confidencial — Uso Interno Consolida e substitui: Estatuto Master V9.0 · Tese Diretrizes Quadrifásicas V9.0 · Carta Oficial de Função da Auditoria · Função de Gestor Geral · Regulamento de Alocação Patrimonial · Estatuto Normatizado para Mesas Proprietárias · Checklist Nocuda Data da consolidação: 03 de julho de 2026     
===== PÁGINA 2 =====
JP WEALTH HOLDING  ·  CÓDIGO DE GOVERNANÇA E GESTÃO DE RISCO  ·  V10.0 
JPW-GOV-001  ·  Confidencial — Uso Interno  ·  Página 2 
PREÂMBULO INSTITUCIONAL Este Código constitui o corpo normativo único e integral da JP Wealth Holding. Ele consolida, em documento unificado, hierarquizado e auditável, a totalidade das normas anteriormente dispersas em sete instrumentos, incorporando as correções identificadas pela Auditoria Estrutural de 03/07/2026 e as deliberações formais do Gestor Geral registradas no Anexo B. A JP Wealth opera sob a premissa de que a gestão não é um exercício de liberdade irrestrita, mas de limitação consciente. A sobrevivência precede o crescimento; a preservação de capital precede o retorno; o processo precede o resultado. Os mercados são inerentemente incertos, e a função deste Código não é prever seus movimentos, mas construir estruturas capazes de sobreviver a cenários adversos, controlar perdas e capturar oportunidades quando presentes. O mérito da gestão não é medido pela magnitude de seus ganhos, mas por sua capacidade de preservar capital, absorver períodos desfavoráveis, executar cortes de risco quando necessários e manter continuidade operacional ao longo de diferentes ciclos de mercado. Nenhum parâmetro deste Código possui caráter arbitrário: cada limite, mecanismo e procedimento responde a riscos previamente identificados e documentados.  CLÁUSULA PÉTREA FUNDAMENTAL A preservação do capital, a disciplina operacional e o respeito aos limites de risco possuem prioridade absoluta sobre qualquer expectativa de retorno financeiro. Lucro é consequência do processo. Sobrevivência é requisito para que o processo continue existindo.  
===== PÁGINA 3 =====
JP WEALTH HOLDING  ·  CÓDIGO DE GOVERNANÇA E GESTÃO DE RISCO  ·  V10.0 
JPW-GOV-001  ·  Confidencial — Uso Interno  ·  Página 3 
SUMÁRIO PREÂMBULO INSTITUCIONAL .......................................................................................................... 2 SUMÁRIO .............................................................................................................................................. 3 LIVRO I .............................................................................................................................................. 5 Disposições Fundamentais, Hierarquia Normativa e Definições ........................................................ 5 Título 1 — Natureza e Escopo ............................................................................................................ 5 Título 2 — Hierarquia Normativa e Resolução de Conflitos ............................................................. 5 Título 3 — Princípios e Cultura de Gestão ........................................................................................ 6 Título 4 — Definições Formais (Glossário Normativo) .................................................................... 7 LIVRO II ............................................................................................................................................ 9 Estatuto Operacional — Arquitetura Quadrifásica de Risco Vertical .................................................. 9 Título 5 — Estrutura Operacional ..................................................................................................... 9 Título 6 — Matriz Quadrifásica de Risco ........................................................................................... 9 Título 7 — Protocolo de Desalavancagem Tática (PDT / LIFO) ..................................................... 11 Título 8 — Dimensionamento e Métricas de Risco ......................................................................... 11 Título 9 — Construção Tática da Posição ........................................................................................ 12 Título 10 — Firewall Assimétrico e Replicação para Contas Satélites ............................................ 13 Título 11 — Protocolo de Emergência, Encerramento e Quarentena ............................................. 14 Título 12 — Regimes Patrimoniais do Ciclo .................................................................................... 15 Título 13 — Reservas Segregadas .................................................................................................... 15 LIVRO III ........................................................................................................................................ 17 Governança, Funções e Controles Humanos ...................................................................................... 17 Título 14 — Princípio Filosófico da Governança ............................................................................. 17 Título 15 — Compliance Board ........................................................................................................ 17 Título 16 — Função do Gestor Geral ................................................................................................ 17 Título 17 — Função de Auditoria e Supervisão (Kharen) ................................................................ 18 Título 18 — Continuidade, Canais e Ferramentas de Controle ....................................................... 19 LIVRO IV ......................................................................................................................................... 21 Regime de Mesas Proprietárias (Prop Firms) .................................................................................... 21 Título 19 — Adaptação do Modelo e Revogações ............................................................................ 21 Título 20 — Salvaguardas Internas ................................................................................................. 21 Título 21 — Estrutura de Contas e Perfis ........................................................................................ 22 Título 22 — Instrumentos, Tetos e Atividade ................................................................................. 22 LIVRO V .......................................................................................................................................... 24 Alocação Patrimonial, Tesouraria e Distribuição .............................................................................. 24 Título 23 — Missão Patrimonial ..................................................................................................... 24 Título 24 — Estrutura Macro e Micro de Alocação ........................................................................ 24 Título 25 — Rebalanceamento e Registros ...................................................................................... 25 Título 26 — Reservas: Reconciliação Normativa ............................................................................ 25 Título 27 — Caixa Institucional (Caixa Central) ............................................................................. 25 Título 28 — Política de Distribuição de Lucros .............................................................................. 26 
===== PÁGINA 4 =====
JP WEALTH HOLDING  ·  CÓDIGO DE GOVERNANÇA E GESTÃO DE RISCO  ·  V10.0 
JPW-GOV-001  ·  Confidencial — Uso Interno  ·  Página 4 
Título 29 — Corretoras e Diversificação .......................................................................................... 27 LIVRO VI ........................................................................................................................................ 28 Método e Execução Técnica (Nocuda®) ........................................................................................... 28 Título 30 — Status Doutrinário ...................................................................................................... 28 Título 31 — Checklist de Análise Técnica (Perfil Swing) ................................................................ 28 Título 32 — Referências Quantitativas de Planejamento .............................................................. 29 LIVRO VII ...................................................................................................................................... 30 Disposições Finais, Revisão e Ratificação .......................................................................................... 30 Título 33 — Revisão e Evolução ..................................................................................................... 30 Título 34 — Compromisso e Vigência ............................................................................................ 30 LIVRO — ANEXO A .................................................................................................................... 31 Tabela Mestra Consolidada de Fases .................................................................................................. 31 LIVRO — ANEXO B .................................................................................................................... 32 Registro de Deliberações e Alterações da Consolidação ..................................................................... 32 B.1 — Deliberações Formais do Gestor Geral (03/07/2026) ......................................................... 32 B.2 — Principais Alterações Frente aos Instrumentos Revogados ................................................. 32 LIVRO — ANEXO C ..................................................................................................................... 34 Itens Pendentes de Ratificação ........................................................................................................... 34   
===== PÁGINA 5 =====
JP WEALTH HOLDING  ·  CÓDIGO DE GOVERNANÇA E GESTÃO DE RISCO  ·  V10.0 
JPW-GOV-001  ·  Confidencial — Uso Interno  ·  Página 5 
 LIVRO I  Hierarquia Normativa e Definições Título 1 — Natureza e Escopo Artigo 1.1 — Objeto Este Código rege integralmente a atividade de gestão e alocação de capital da JP Wealth Holding nos mercados de Câmbio (Forex) e Contratos por Diferença (CFDs), abrangendo: princípios e filosofia de gestão; limites de risco e exposição; protocolos de execução, desalavancagem e proteção patrimonial; estrutura de governança e funções; regime de mesas proprietárias; alocação patrimonial e tesouraria; e método de análise e execução técnica. Artigo 1.2 — Vinculação Este documento constitui referência obrigatória para todas as decisões operacionais. Nenhuma convicção analítica, resultado isolado ou circunstância de mercado autoriza sua flexibilização. Em caso de conflito entre convicção e protocolo, prevalece o protocolo; entre lucro potencial e preservação patrimonial, prevalece a preservação. Título 2 — Hierarquia Normativa e Resolução de Conflitos Artigo 2.1 — Hierarquia Interna As normas deste Código organizam-se na seguinte ordem de precedência: – 1º — Livro I (Disposições Fundamentais e Definições) e Cláusulas Pétreas de qualquer Livro; – 2º — Livro II (Estatuto Operacional e Arquitetura Quadrifásica de Risco); – 3º — Livro III (Governança e Funções); – 4º — Livros IV e V (Mesas Proprietárias; Alocação Patrimonial e Tesouraria); – 5º — Livro VI (Método e Execução Técnica); – 6º — Anexos e documentos operacionais derivados (planilhas, painéis, templates de sinal).  §1º — Norma de nível superior prevalece sobre norma de nível inferior, sem exceção. §2º — Havendo conflito entre normas do mesmo nível, prevalece a interpretação mais restritiva em risco (menor exposição, menor alavancagem, encerramento mais rápido), até resolução formal pelo Compliance Board. §3º — Todo conflito identificado deverá ser registrado por escrito e resolvido por emenda formal na revisão seguinte deste Código. A existência de conflito não suspende a operação: aplica-se o §2º.    
===== PÁGINA 6 =====
JP WEALTH HOLDING  ·  CÓDIGO DE GOVERNANÇA E GESTÃO DE RISCO  ·  V10.0 
JPW-GOV-001  ·  Confidencial — Uso Interno  ·  Página 6 
Artigo 2.2 — Revogação dos Instrumentos Anteriores Ficam revogados, na data de ratificação deste Código, todos os instrumentos normativos anteriores da JP Wealth, cujo conteúdo vigente encontra-se integralmente incorporado a este documento. Referências externas a tais instrumentos entendem-se remetidas aos Livros correspondentes deste Código. Título 3 — Princípios e Cultura de Gestão Artigo 3.1 — Pilares Operacionais A consistência operacional é sustentada por quatro pilares:  1. Planejamento (definição prévia de cenários, critérios e objetivos);  2. Filosofia e Mindset (aceitação da incerteza e da natureza probabilística dos resultados);  3. Execução Operacional (reação disciplinada às informações do mercado, sem antecipações preditivas); e  4. Gerenciamento (aplicação rigorosa dos limites de risco).  Artigo 3.2 — Bússola Estratégica Operacional Toda alocação de risco direcional exige alinhamento simultâneo de quatro critérios:  1. Padrão (estrutura operacional clara e documentável compatível com o método);  2. Tendência (alinhamento ao fluxo predominante);  3. Amplitude (espaço técnico suficiente para relação risco-retorno adequada); e  4. Confluência (múltiplos fatores independentes de validação). Artigo 3.3 — Hierarquia Permanente de Prioridades Todas as decisões operacionais respeitarão a seguinte ordem:  I. Preservação do Capital;  II. Sobrevivência Operacional da Conta;  III. Cumprimento Integral dos Protocolos de Risco;  IV. Qualidade da Execução;  V. Consistência de Longo Prazo;  VI. Rentabilidade. Artigo 3.4 — Natureza Probabilística Nenhum modelo analítico é capaz de prever com certeza o comportamento futuro dos preços. Todas as operações constituem decisões probabilísticas. O objetivo da gestão não é eliminar perdas, mas controlar sua magnitude e preservar capacidade operacional ao longo de centenas de ciclos de decisão. Este Código não contém, e proíbe que documentos derivados contenham, afirmações quantitativas de probabilidade de ruína ou de retorno sem memória de cálculo formalmente publicada.  
===== PÁGINA 7 =====
JP WEALTH HOLDING  ·  CÓDIGO DE GOVERNANÇA E GESTÃO DE RISCO  ·  V10.0 
JPW-GOV-001  ·  Confidencial — Uso Interno  ·  Página 7 
Título 4 — Definições Formais (Glossário Normativo) Para todos os efeitos deste Código, aplicam-se as seguintes definições, vinculantes para interpretação humana e para implementação em sistemas automatizados: Artigo 4.1 — Drawdown Operacional (DD) Medida oficial de deterioração que rege a Matriz Quadrifásica: DD(t) = max( 0 ; ( Saldo_Inicial_Ciclo − Equity(t) ) / Saldo_Inicial_Ciclo )  Equity(t) = patrimônio flutuante da conta (saldo + resultado aberto), tick a tick  Saldo_Inicial_Ciclo = saldo de referência fixado na abertura do ciclo anual (Catraca Patrimonial)  §1º — O DD é medido sobre equity flutuante, em base contínua (tick a tick), tendo como referência exclusiva o Saldo Inicial do Ciclo. Lucros acumulados no ciclo não alteram a referência (regime DDC, Art. 12.3 do Livro II). §2º — A transição para fase mais restritiva é efetivada no instante em que o DD rompe o limite superior da fase vigente. A adequação de exposição deve iniciar imediatamente, observado o Protocolo de Desalavancagem Tática. §3º — Histerese de retorno: o retorno a uma fase menos restritiva somente ocorre quando o DD recuar para valor inferior ao limite da fase em pelo menos 0,50 ponto percentual, sustentado pelo fechamento de ao menos 1 (um) candle H4 completo.  A poda LIFO executada não é revertida; nova exposição somente por ordens novas, conformes aos limites da fase restaurada. Artigo 4.2 — Operação Conjunto de ordens pertencentes à mesma tese operacional, executadas no mesmo ativo e na mesma direção. Inicia-se com a execução da Ordem Gênese e encerra-se quando não houver qualquer posição aberta vinculada à tese, confirmado o encerramento pelo protocolo do Art. 4.4. Artigo 4.3 — Ordem Gênese Primeira ordem de uma Operação Única, identificada objetivamente pela conjunção de dois critérios:  (i) posição líquida do ativo igual a zero no momento da execução; e  (ii) sinalização expressa da flag GÊNESE no template de sinal. Ausente a flag, a ordem não será executada pela Auditoria até esclarecimento. Artigo 4.4 — Encerramento de Operação Estado em que a posição líquida do ativo retorna a zero E o Gestor confirma o encerramento mediante o protocolo de dupla confirmação (registro escrito “FECHADO” no template de saída).  Zeragem tática sem confirmação de encerramento não extingue a Operação; contudo, eventual reingresso permanece sujeito aos limites da fase vigente e não constitui nova Gênese.   
===== PÁGINA 8 =====
JP WEALTH HOLDING  ·  CÓDIGO DE GOVERNANÇA E GESTÃO DE RISCO  ·  V10.0 
JPW-GOV-001  ·  Confidencial — Uso Interno  ·  Página 8 
Artigo 4.5 — Alavancagem  Alavancagem(t) = Σ |exposição nocional das posições abertas| / Saldo_Inicial_Ciclo  Calculada sobre o valor nocional bruto, sem compensação entre posições, tendo por denominador o Saldo Inicial do Ciclo. Artigo 4.6 — Demais Definições  – Tese Operacional: hipótese técnica documentada que fundamenta a Operação, registrada no template de sinal. Para sistemas automatizados, a proxy observável da tese é o par {ativo, direção} sob regime de exclusividade. – Lucro Técnico: resultado obtido pela liquidação parcial de posições defensivas em movimentos corretivos favoráveis, utilizável para redução de exposição líquida, melhoria de preço médio, redução de margem ou encerramento parcial de posições deficitárias. – DDI (Drawdown Inicial): período em que a conta opera exclusivamente com o capital-base do ciclo, sem amortecimento de resultados acumulados. – DDC (Drawdown Compensado): situação em que resultados positivos do ciclo geram margem patrimonial sobre o saldo de referência. Natureza exclusivamente contábil; não amplia limites de risco. – Fase da Conta vs. Fase da Grade Ativa: a Fase da Conta decorre do DD nos termos do Art. 4.1; a Fase da Grade Ativa reflete a estrutura de posições remanescente após podas. A Fase da Conta rege limites; a Fase da Grade rege reconstrução. – VRM (Volatility Regime Metric): razão ATR(55)/ATR(660), calculada no gráfico H4, com recálculo semanal no fechamento de sexta-feira [parâmetro sujeito a ratificação — Anexo C].  
===== PÁGINA 9 =====
JP WEALTH HOLDING  ·  CÓDIGO DE GOVERNANÇA E GESTÃO DE RISCO  ·  V10.0 
JPW-GOV-001  ·  Confidencial — Uso Interno  ·  Página 9 
 LIVRO II   Estatuto Operacional — Arquitetura Quadrifásica de Risco Vertical  Título 5 — Estrutura Operacional  Artigo 5.1 — Modelo de Risco Vertical A gestão opera sob o regime de Operação Única Exclusiva: toda a exposição é concentrada em uma única tese operacional por vez, sujeita a mecanismos progressivos de controle, desalavancagem e proteção patrimonial. Fica revogado, em caráter definitivo, o modelo de risco horizontal (múltiplas operações simultâneas), bem como os indicadores de correlação ICCO e ICFO a ele associados. §1º — É permitida apenas uma Operação ativa por conta gerenciada. Enquanto houver Operação em andamento, é proibida a abertura de posições em qualquer outro ativo, ressalvada exclusivamente a Operação Simbólica de Atividade (Art. 22.5, Livro IV).  Artigo 5.2 — Horizonte Temporal O gráfico de 4 horas (H4) é o horizonte principal para análise estrutural, contexto e construção de teses, com gatilho de execução em H1, conforme Livro VI.  Artigo 5.3 — Ciclo Operacional e Catraca Patrimonial O ciclo de gestão possui duração de 12 meses, contados da fixação do Saldo Inicial de Referência. Lucros consolidados de exercícios anteriores integram reservas segregadas e não ampliam o risco do ciclo vigente. Risco máximo, limites de drawdown e dimensionamento são calculados exclusivamente sobre o Saldo Inicial de Referência do ciclo ativo.  Título 6 — Matriz Quadrifásica de Risco Artigo 6.1 — Limite Máximo e Fases O limite máximo de drawdown da Conta Mestre é fixado em 15,00%, distribuído em quatro fases operacionais: 
===== PÁGINA 10 =====
JP WEALTH HOLDING  ·  CÓDIGO DE GOVERNANÇA E GESTÃO DE RISCO  ·  V10.0 
JPW-GOV-001  ·  Confidencial — Uso Interno  ·  Página 10 
Fase Faixa de DD Alav. Máx. Regime e Diretrizes 1 — Exposição Inicial 0,00% – 4,00% 4,0x Ordem Gênese; construção da grade conforme critérios técnicos; execução da tese em parâmetros normais. 2 — Restrição Moderada 4,01% – 8,00% 2,0x Reconhecimento formal de deterioração; redução obrigatória de exposição; prioridade à proteção patrimonial e recuperação técnica. 3 — Restrição Avançada 8,01% – 12,00% 1,0x Tendência adversa confirmada; proibição de novas ampliações agressivas; correções usadas exclusivamente para reduzir exposição. Aciona o Protocolo de Emergência. 4 — Salvaguarda Final 12,01% – 15,00% 0,4x Congelamento da atividade discricionária; manutenção apenas da exposição residual; única exceção: Defesa Final (Art. 9.3). Preparação para encerramento compulsório.  §1º — Considera-se “ampliação agressiva”, para fins da Fase 3, qualquer ordem que eleve a exposição nocional total acima da exposição vigente no momento do ingresso na fase, ainda que dentro do teto de alavancagem. §2º — Protocolo de Gap: se abertura de mercado ou movimento descontínuo deslocar o DD através de uma ou mais fases sem janela de poda, aplica-se imediatamente o teto da fase efetivamente atingida, com adequação compulsória na primeira liquidez disponível. Se o gap conduzir o DD a nível igual ou superior a 15,00%, aplica-se o encerramento compulsório integral a mercado, executado pela Auditoria ou pelo Equity Protector, o que ocorrer primeiro. Artigo 6.2 — Hierarquia de Disjuntores  Nível Acionamento Medida 1 — Restrição Moderada DD > 4,00% Alavancagem máxima reduzida a 2,0x; início da poda LIFO. 2 — Emergência Operacional DD > 8,00% Alavancagem máxima 1,0x; ativação do Protocolo de Emergência. 3 — Congelamento Operacional DD > 12,00% Suspensão da atividade discricionária; exposição residual apenas; exceção única: Defesa Final (Art. 9.3). 4 — Encerramento Compulsório DD ≥ 15,00% Liquidação integral e imediata; início da Quarentena Operacional.    CLÁUSULA DE PENALIDADE FIDUCIÁRIA O descumprimento, hesitação ou tentativa de burla à Hierarquia de Disjuntores — incluindo remoção temporária de ordens stop no terminal ou atraso intencional da poda LIFO em janelas de pullback — constitui falta gravíssima de conformidade, sujeita ao Art. 17.6 (Livro III). 
===== PÁGINA 11 =====
JP WEALTH HOLDING  ·  CÓDIGO DE GOVERNANÇA E GESTÃO DE RISCO  ·  V10.0 
JPW-GOV-001  ·  Confidencial — Uso Interno  ·  Página 11 
 Título 7 — Protocolo de Desalavancagem Tática (PDT / LIFO) Artigo 7.1 — Regra Geral A transição para fase mais restritiva impõe redução imediata da exposição ao novo teto, pelo método LIFO (Last In, First Out): encerram-se prioritariamente as posições mais recentes da estrutura, preservando a eficiência do preço médio e reduzindo pressão sobre margem. §1º — Sempre que tecnicamente possível, a poda será executada em movimentos corretivos favoráveis (retrações observadas em M15/H1). §2º — Gatilho compulsório: inexistindo movimento corretivo, a poda torna-se compulsória e imediata quando o DD avançar 1,00 ponto percentual além do limite superior da fase rompida. A inexistência de retrações não suspende nem posterga a obrigação de adequação. §3º — Se o nível de margem da conta indicar risco de stop-out técnico (Tabela do Art. 18.4, Livro III) antes do gatilho do §2º, a proteção de margem prevalece: executa-se a redução necessária de imediato, mantendo a ordem LIFO. Artigo 7.2 — Revogação da Exceção Direcional Fica revogado qualquer mecanismo que permita manter posições além dos limites deste Código com base em convicções subjetivas ou expectativa de reversão. O limite máximo de drawdown é critério objetivo e definitivo de encerramento compulsório.  Título 8 — Dimensionamento e Métricas de Risco  Artigo 8.1 — Ordem Gênese: Dupla Restrição A Ordem Gênese está sujeita, cumulativamente, a duas restrições independentes: – Restrição de risco: o risco financeiro máximo (distância ao stop × volume) não excederá 1,00% do Saldo Inicial, equivalente a 25% da capacidade de absorção da Fase 1; – Restrição de alavancagem: a exposição nocional da Gênese não excederá 0,4x, preservando capacidade financeira para absorção de volatilidade e execução dos protocolos subsequentes.  Artigo 8.2 — Fatores do Lote Operacional O volume final de cada posição decorre de:  I — valor nominal do contrato (equivalência financeira entre ativos);  II — regime de volatilidade (VRM);  III — fase vigente da Matriz Quadrifásica;  IV — distância do stop estatístico.   
===== PÁGINA 12 =====
JP WEALTH HOLDING  ·  CÓDIGO DE GOVERNANÇA E GESTÃO DE RISCO  ·  V10.0 
JPW-GOV-001  ·  Confidencial — Uso Interno  ·  Página 12 
Artigo 8.3 — VRM e Regimes de Volatilidade VRM = ATR(55)/ATR(660) em H4 Regime Conduta < 1,20 Normal Parâmetros padrão da fase vigente. 1,20 – 1,50 Transição Cautela; revisão de amplitude e stop. > 1,50 Alta Volatilidade Redução obrigatória de exposição conforme parâmetros da gestão.  Artigo 8.4 — Validação do Stop O Stop Técnico deve observar simultaneamente estrutura de  Price Action, múltiplo de ATR e validação estatística.  A distância do stop, expressa em múltiplos do ATR(55): Distância do Stop (× ATR55) Classificação < 2,0 Estrutura inadequada — operação vedada. 2,0 – 3,5 Estrutura mínima aceitável. 3,5 – 5,0 Estrutura ideal. > 5,0 Estrutura conservadora.  Artigo 8.5 — Projeção Estatística de Sobrevivência (Raiz-N)  Stop_estatístico = ATR(55) × √N × F  N = horizonte projetado da operação, em candles H4  (padrão: 55) F = fator de segurança  (padrão: 1,25 — sujeito a ratificação, Anexo C)  §1º — Se o Stop Técnico for inferior ao Stop Estatístico, a operação é classificada como Estrutura de Vulnerabilidade Elevada, e todas as decisões de gestão priorizarão redução de risco. Título 9 — Construção Tática da Posição Artigo 9.1 — Estrutura Escalonada A posição poderá compor-se de Ordem Gênese, ordens intermediárias de ajuste e ordens de posicionamento estrutural, distribuídas em zonas técnicas previamente definidas. Toda ampliação permanece subordinada aos limites da fase vigente. Artigo 9.2 — Lucro Técnico O Lucro Técnico (Art. 4.6) será empregado exclusivamente para: redução da exposição líquida; melhoria do preço médio consolidado; redução de exigência de margem; ou encerramento parcial de posições deficitárias. É vedado seu uso para ampliar limites de risco.   
===== PÁGINA 13 =====
JP WEALTH HOLDING  ·  CÓDIGO DE GOVERNANÇA E GESTÃO DE RISCO  ·  V10.0 
JPW-GOV-001  ·  Confidencial — Uso Interno  ·  Página 13 
Artigo 9.3 — Defesa Final da Estrutura A Defesa Final é o mecanismo excepcional e único de exposição nova permitido na Fase 4, destinado exclusivamente à melhoria técnica das condições de encerramento — jamais à ampliação de risco direcional ou ao prolongamento indefinido da Operação. §1º — Exposição máxima: 1,00% do Saldo Inicial do Ciclo. §2º — Procedimento obrigatório:  (i) solicitação formal escrita do Gestor, com justificativa técnica, registrada no canal oficial;  (ii) execução exclusiva pela Auditoria — o Gestor não possui meios de execução direta;  (iii) direito de veto pleno da Auditoria, com fundamentação escrita;  (iv) limite de uma única Defesa Final por Operação;  (v) registro em ata do Compliance Board. §3º — O congelamento da Fase 4 permanece íntegro para qualquer outra forma de atividade discricionária. A Defesa Final não suspende o encerramento compulsório aos 15,00%.  Título 10 — Firewall Assimétrico e Replicação para Contas Satélites Artigo 10.1 — Fórmula Normativa de Replicação A replicação de ordens da Conta Mestre para contas satélites observará, obrigatoriamente, a normalização por saldo previamente à aplicação do fator de perfil: Lote_satélite = Lote_mestre × ( Saldo_satélite / Saldo_mestre ) × Fator_perfil DD%_satélite_projetado = DD%_mestre × Fator_perfil  §1º — É expressamente vedada a aplicação de fator de lote fixo sem normalização por saldo, por produzir risco proporcional incorreto entre contas de saldos distintos. A redação anterior (“fator de multiplicação de lote fixado em 1/3”) fica revogada e substituída pela fórmula deste artigo. Artigo 10.2 — Invariante de Segurança do Fator  Fator_perfil ≤ ( MaxLoss_conta − 2,00 p.p. ) / 15,00%  Nenhum perfil poderá adotar fator que, no cenário de utilização integral do limite de 15,00% da Conta Mestre, projete drawdown na conta satélite superior ao seu limite contratual de perda máxima deduzido de margem mínima de segurança de 2,00 pontos percentuais. Artigo 10.3 — Perfis de Correção por Função da Conta Por deliberação do Gestor Geral (Anexo B, D-3), o fator de correção é definido pela função estratégica da conta, observados o invariante do Art. 10.2 e o princípio de que quanto maior o fator de risco do perfil, menor o teto de participação da conta na carteira de satélites: 
===== PÁGINA 14 =====
JP WEALTH HOLDING  ·  CÓDIGO DE GOVERNANÇA E GESTÃO DE RISCO  ·  V10.0 
JPW-GOV-001  ·  Confidencial — Uso Interno  ·  Página 14 
Perfil Fator (novo) Fator revogado DDR-alvo DD no cenário 15% Alav./ordem Teto de participação* Longevity 53% 66% 8,0% 7,95% 0,21x ≤ 1/3 das contas satélites High Longevity 40% 50% 6,0% 6,00% 0,16x ≤ 1/2 das contas satélites High Longevity Plus 27% 33% 4,0% 4,05% 0,11x Sem teto; mínimo de 1 conta ativa * Tetos de participação: proposta em ratificação (Anexo C). Os fatores anteriores (66/50/33%) foram calibrados sobre o DDR de 12% da V8.0; sob o limite de 15% da V9.0, o fator de 66% projetaria 9,9% de drawdown na satélite — margem nula frente ao Maximum Loss contratual de 10% —, razão pela qual sua revogação é compulsória e não discricionária. Artigo 10.4 — Faixas de Fase nas Satélites As faixas de drawdown de cada fase nas contas satélites correspondem às faixas da Conta Mestre multiplicadas pelo Fator_perfil, conforme tabela consolidada no Anexo A. Artigo 10.5 — Rotatividade de Perfis Perfis não são fixos: são atribuídos pela função estratégica da conta no momento. Contas escaladas migram para perfis mais defensivos. Em caso de perda de conta-base por violação de drawdown, outra conta ativa poderá ser promovida ao papel de perfil-base, e nova conta adquirida no perfil mais conservador. Contas High Longevity Plus são estáticas por princípio, salvo esgotamento extremo das demais. Título 11 — Protocolo de Emergência, Encerramento e Quarentena Artigo 11.1 — Acionamento O Protocolo de Emergência é automaticamente acionado quando o DD atinge a Fase 3 (8,01%–12,00%), independentemente de interpretação ou convicção. Medidas obrigatórias: adequação imediata ao teto da fase; aplicação do PDT/LIFO; proibição de ampliações agressivas; suspensão de novas teses; reavaliação integral do contexto antes de qualquer ajuste permitido. Artigo 11.2 — Encerramento Compulsório e Quarentena Atingido DD ≥ 15,00%: liquidação integral e imediata das posições e suspensão da atividade, iniciando-se Quarentena Operacional mínima de 90 dias. §1º — Execução do encerramento: pela Auditoria, mediante alerta automático; e, em paralelo, pelo Equity Protector permanentemente armado (Art. 18.6, Livro III), prevalecendo o que ocorrer primeiro. O Gestor não executa o encerramento. §2º — Durante a quarentena, o Gestor elaborará relatório de incidente com análise de causas, avaliação de falhas e propostas de correção. §3º — Autoridade de retorno: o reinício das atividades exige deliberação conjunta e registrada do Compliance Board (Gestor Geral + Auditoria), lavrada em ata, após conclusão do relatório e revalidação dos protocolos. É vedada a auto-revalidação unilateral pelo Gestor.   
===== PÁGINA 15 =====
JP WEALTH HOLDING  ·  CÓDIGO DE GOVERNANÇA E GESTÃO DE RISCO  ·  V10.0 
JPW-GOV-001  ·  Confidencial — Uso Interno  ·  Página 15 
Artigo 11.3 — Recuperação de Estado Inválido Constatado erro de apuração de fase ou de DD (falha de dado, cálculo ou registro), a operação é imediatamente enquadrada na fase correta apurada; excessos de exposição são adequados pelo PDT na primeira liquidez; o incidente é registrado e reportado ao Compliance Board em até 48 horas. Título 12 — Regimes Patrimoniais do Ciclo Artigo 12.1 — DDI Durante o Drawdown Inicial, exige-se aderência integral aos critérios de validação operacional. O acionamento do limite máximo implica os protocolos do Título 11. Artigo 12.2 — Drawdown Compensado (DDC) O Drawdown Compensado possui natureza exclusivamente patrimonial e contábil. Lucro acumulado amplia a margem livre da fase, mas não autoriza ampliação de limites absolutos, alteração de tetos de alavancagem, flexibilização da Matriz .  AVISO DO AUDITOR — A ILUSÃO DO DDC O regime DDC não compra indulgência técnica. O DDC protege o saldo final e a estrutura; não protege egos feridos que se recusam a executar o corte tático LIFO.  Artigo 12.3 — Proibição Absoluta de Merge É terminantemente proibida a fusão de riscos ou compensação cruzada de saldos. Lucros de operações liquidadas ou margens livres de subcontas não estendem os limites verticais de fase. Cada ciclo da Operação Única nasce, respira e morre sob os limites matemáticos estritos de sua fase vigente.  Título 13 — Reservas Segregadas Artigo 13.1 — FCR (Fundo de Contingência e Reconstituição) Volume mínimo: 15,00% do capital nominal da Conta Mestre.  Finalidade exclusiva: recomposição do capital operacional após atingimento do limite máximo de drawdown.  Natureza: reserva segregada de liquidez imediata (D+0/D+1).  O acionamento do FCR não altera quarentena, auditoria ou revalidação. Após uso, todos os recursos líquidos gerados destinam-se prioritariamente à sua recomposição integral; enquanto não recomposto, é vedada distribuição de dividendos ou retiradas extraordinárias. Artigo 13.2 — FEO (Fundo de Estabilidade Operacional) Volume mínimo: 6 meses das despesas pessoais, operacionais e administrativas da estrutura.  Finalidade: continuidade financeira durante baixa rentabilidade, drawdowns prolongados, interrupções ou quarentena.  Liquidez de até D+2. Vedada a transferência de recursos do FEO para corretoras, prop firms ou ampliação de risco. 
===== PÁGINA 16 =====
JP WEALTH HOLDING  ·  CÓDIGO DE GOVERNANÇA E GESTÃO DE RISCO  ·  V10.0 
JPW-GOV-001  ·  Confidencial — Uso Interno  ·  Página 16 
Artigo 13.3 — Hierarquia de Capitalização Todo fluxo financeiro gerado pela atividade observará a ordem:  I — recomposição integral do FCR;  II — constituição/recomposição integral do FEO;  III — reservas estratégicas adicionais;  IV — distribuição de dividendos ou realocação patrimonial. A relação entre estes fundos e o bloco macro de 15% da alocação patrimonial rege-se pelo Art. 26.2 (Livro V).  CLÁUSULA PÉTREA DAS RESERVAS A manutenção do FCR e do FEO é requisito obrigatório para a continuidade do modelo de gestão. A preservação da estrutura financeira da Holding possui prioridade sobre qualquer expectativa de crescimento, retorno ou expansão.  
===== PÁGINA 17 =====
JP WEALTH HOLDING  ·  CÓDIGO DE GOVERNANÇA E GESTÃO DE RISCO  ·  V10.0 
JPW-GOV-001  ·  Confidencial — Uso Interno  ·  Página 17 
LIVRO III  Governança, Funções e Controles Humanos  Título 14 — Princípio Filosófico da Governança “O trader isolado é vulnerável. O trader vigiado é antifrágil.” O maior risco da atividade não é o mercado, mas a mente humana exposta à pressão constante da incerteza e da ambição. A arquitetura de governança existe para proteger o Gestor dele mesmo, assegurando o cumprimento das regras precisamente nos momentos em que o emocional poderia distorcê-las. O Gestor permanece livre para pensar e analisar; o sistema permanece blindado contra impulsos; a governança protege o capital, o método e a longevidade. Título 15 — Compliance Board Artigo 15.1 — Composição e Deliberação O Compliance Board é composto pelo Gestor Geral (João Paulo V. Cirqueira) e pela Auditoria (Kharen Luiza). Delibera por decisão conjunta, obrigatoriamente registrada em ata escrita e datada. [Composição sujeita a ratificação e à futura inclusão de terceiro membro independente — Anexo C.] Artigo 15.2 — Competências Exclusivas – Autorizar o retorno pós-quarentena (Art. 11.2, §3º); – Executar e documentar ajustes de alocação patrimonial e rebalanceamentos (Livro V); – Definir o regime de distribuição de lucros a cada Período de Gestão; – Resolver formalmente conflitos normativos identificados (Art. 2.1, §3º); – Homologar corretoras, prop firms e veículos de investimento; – Validar registros do Caixa Central e da Planilha de Resultados Mensais. Título 16 — Função do Gestor Geral Artigo 16.1 — Atribuições – Operação: análise, construção de teses, definição de entradas, defesas e parâmetros de risco da JP Wealth MAM, em estrita conformidade com este Código; envio de sinais pelo canal oficial; – Controles: preenchimento diário do Execution Board, do Período Contábil e do Diário de Trading; verificação de necessidade de ressincronização; – Supervisão estrutural: revisão periódica deste Código, do Manual Nocuda e dos documentos derivados; – Resultados e divulgação: relatórios semanais, trimestrais e anuais; artigos; – Relações e captação: white paper, questionários, termos de adesão e presença institucional — atividades sujeitas à cláusula suspensiva do Art. 16.3; – Alocação patrimonial: supervisão dos projetos externos e da alocação da Holding, cuja execução é competência exclusiva do Compliance Board (Art. 15.2).  
===== PÁGINA 18 =====
JP WEALTH HOLDING  ·  CÓDIGO DE GOVERNANÇA E GESTÃO DE RISCO  ·  V10.0 
JPW-GOV-001  ·  Confidencial — Uso Interno  ·  Página 18 
Artigo 16.2 — Vedações O Gestor não detém senhas mestre de operação, não executa ordens diretamente nas contas, não executa unilateralmente ajustes patrimoniais e não autoriza o próprio retorno de quarentena. Artigo 16.3 — Cláusula Suspensiva Regulatória Qualquer atividade de captação, gestão ou intermediação de capital de terceiros permanece suspensa até obtenção de parecer jurídico-regulatório formal quanto ao enquadramento aplicável (incluindo, no Brasil, a regulamentação da CVM), arquivado como anexo deste Código. Esta cláusula protege a Holding do único risco que nenhum protocolo de mercado mitiga: o risco regulatório. Título 17 — Função de Auditoria e Supervisão (Kharen) Artigo 17.1 — Natureza da Função A Auditoria é o eixo psicológico central de proteção e salvaguarda estrutural. Sua responsabilidade não reside na execução de estratégias de mercado, mas no rigor com que as proteções e controles são mantidos — inclusive, e principalmente, contra tentativas inconscientes do próprio Gestor de sabotá-los. Artigo 17.2 — Guardiã das Credenciais A Auditoria é exclusivamente responsável pelas senhas mestre (MetaTrader, sites de brokers e prop firms, administração do Traders Connect). O Gestor acessa as contas apenas em modo observador (investor password). A chave final de acesso não pode estar com quem sofre a pressão emocional da posição. Artigo 17.3 — Replicação de Ordens A Auditoria recebe as ordens do Gestor exclusivamente pelos canais oficiais (Art. 18.5), verifica a presença obrigatória de stop loss e take profit, aplica a fórmula normativa de replicação (Art. 10.1) com o fator do perfil de cada conta, e registra volume corrigido, stops e alvos no Painel de Execução de Ordens. Ordens sem stop/take ou sem os campos obrigatórios do template não são executadas: a Auditoria consulta, jamais preenche por presunção. Artigo 17.4 — Monitoramento Contínuo – Stops abertos, nominais e percentuais, dentro do regime de drawdown de cada conta; – Drawdown de Referência (DDR) de cada conta e proximidade dos limites diário e global; – Coerência da gestão com os limites deste Código; prevenção de “esticamento de risco”; – Conformidade diária com as regras contratuais das prop firms; – Accountability diário: resultado, saldo acumulado, documentação contábil íntegra. Artigo 17.5 — Poder de Veto e Procedimento A Auditoria detém autoridade de veto sobre qualquer ordem que ultrapasse limites de risco, careça de tese válida ou desalinhe-se dos parâmetros da conta-base. §1º — Todo veto será comunicado imediatamente e fundamentado por escrito em até 24 horas, com referência ao artigo deste Código que o ampara. §2º — Divergência entre Gestor e Auditoria sobre o que o Código exige: aplica-se, de imediato e provisoriamente, a interpretação mais restritiva em risco (Art. 2.1, §2º); a divergência é submetida ao registro do Compliance Board e resolvida por emenda ou nota interpretativa. 
===== PÁGINA 19 =====
JP WEALTH HOLDING  ·  CÓDIGO DE GOVERNANÇA E GESTÃO DE RISCO  ·  V10.0 
JPW-GOV-001  ·  Confidencial — Uso Interno  ·  Página 19 
§3º — O veto não alcança as obrigações compulsórias do próprio Código: a Auditoria não pode vetar a poda LIFO compulsória, o encerramento aos 15,00% ou o disparo do Equity Protector. Artigo 17.6 — Faltas Graves Constituem falta gravíssima de ambas as funções: burla ou tentativa de burla aos disjuntores; execução de ordem vetada; compartilhamento de senhas mestre com o Gestor; omissão dolosa de registro. Toda falta grave é lavrada em ata e tratada na revisão imediata dos protocolos. Título 18 — Continuidade, Canais e Ferramentas de Controle Artigo 18.1 — Protocolo de Contingência de Credenciais Para eliminar o ponto único de falha humano, institui-se estrutura de três camadas: – Camada 1 — Proteção automática: o Equity Protector do Traders Connect permanece permanentemente armado com os parâmetros da fase vigente e do limite de 15,00%, independendo de intervenção humana (Art. 18.6); – Camada 2 — Custódia de contingência: cópia lacrada e atualizada mensalmente das credenciais mestre, sob custódia de terceiro de confiança formalmente nomeado [NOMEAR — Anexo C], liberável exclusivamente mediante indisponibilidade comprovada da Auditoria superior a 24 horas com posição aberta; – Camada 3 — Acesso de emergência do Gestor: inexistindo terceiro custodiante, o acesso do Gestor às credenciais de contingência restringe-se, sob pena de falta gravíssima, a ENCERRAR ou REDUZIR posições — jamais abrir, ampliar ou modificar a favor do risco. Todo uso é registrado, reportado ao Compliance Board em 24 horas e seguido de troca obrigatória de todas as senhas. Artigo 18.2 — Indisponibilidade da Auditoria Indisponibilidade superior a 24 horas com posição aberta ativa a Camada 2 (ou 3). Indisponibilidade prolongada (superior a 15 dias) suspende a abertura de novas Operações até restabelecimento ou nomeação de auditoria substituta pelo Compliance Board. Artigo 18.3 — Frequência de Execução Máximo de 2 execuções de novas ordens por dia. Ordens adicionais somente se pré-aprovadas formalmente, por mensagem de exceção no grupo de acompanhamento, com registro de motivo. Artigo 18.4 — Monitoramento do Nível de Margem Nível de margem Significado Ação da supervisão Acima de 1000% Margem altamente segura Ordem pode ser liberada normalmente. 700% a 1000% Margem estável Verificar número de operações. 500% a 700% Nível moderado Cautela ao liberar novas ordens. 400% a 500% Alerta de exposição elevada Verificar todas as operações antes de novas aberturas. 
Abaixo de 400% Conta em risco Redução imediata pela ordem LIFO até restabelecer nível ≥ 500%; se insuficiente, estudar e executar fechamento da estrutura agressora (observado o Art. 7.1, §3º).  
===== PÁGINA 20 =====
JP WEALTH HOLDING  ·  CÓDIGO DE GOVERNANÇA E GESTÃO DE RISCO  ·  V10.0 
JPW-GOV-001  ·  Confidencial — Uso Interno  ·  Página 20 
Artigo 18.5 — Canais Oficiais e SLA Canal primário de sinais: grupo dedicado de WhatsApp. Canal secundário de contingência: [definir — e-mail institucional ou Telegram; Anexo C]. Todo sinal exige confirmação expressa de recebimento pela Auditoria; ausente a confirmação em 15 minutos durante sessão de mercado, o Gestor aciona o canal secundário. SLA de execução após confirmação: 30 minutos, salvo justificativa registrada. Artigo 18.6 — Checagem Dupla Automatizada As contas reais operam sob Equity Protector e Daily Drawdown do Traders Connect, com monitoramento 24/7, desarme automático das operações em caso de extrapolação e notificação imediata à Auditoria. Os parâmetros configurados (percentuais, contas, gatilhos) constam de ficha técnica anexa à ata de configuração, revisada pelo Compliance Board a cada alteração de fase estrutural do sistema.  
===== PÁGINA 21 =====
JP WEALTH HOLDING  ·  CÓDIGO DE GOVERNANÇA E GESTÃO DE RISCO  ·  V10.0 
JPW-GOV-001  ·  Confidencial — Uso Interno  ·  Página 21 
LIVRO IV  Regime de Mesas Proprietárias (Prop Firms)  Título 19 — Adaptação do Modelo e Revogações Artigo 19.1 — Migração Integral para a Arquitetura V9.0+ Este Livro substitui integralmente o Estatuto Normatizado para Mesas Proprietárias anterior. Ficam expressamente revogados, por incompatibilidade com a Arquitetura de Risco Vertical: o regime de DDR de 12%; a tolerância a duas ou três operações simultâneas; e os fatores de correção de 66%, 50% e 33% (substituídos pelo Título 10 do Livro II). As contas de prop firm operam sob a mesma Operação Única Exclusiva da Conta Mestre, replicada pelo Firewall Assimétrico. Artigo 19.2 — Regras Contratuais de Referência (FTMO / The5%ers / The Trading Pit) – Challenge em duas fases: meta de 10% (Fase 1) e 5% (Fase 2), com perda diária de 5% e perda máxima de 10%; mínimo de 4 dias operacionais; – Maximum Daily Loss: 5% do saldo inicial, recalculado diariamente sobre o maior valor entre balance e equity no início do dia — regra mais crítica do regime, cuja violação, mesmo por flutuação momentânea de equity, encerra a conta sem recurso; – Maximum Loss: 10% do saldo inicial, fixo; violação implica encerramento definitivo; – Saques a cada 15–30 dias, com reembolso da taxa após aprovação; divisão de lucros 80/20, elevável a 90/10; – Inatividade: ausência de operações por mais de 30 dias pode encerrar a conta; – Vedações comportamentais: variações abruptas de risco sem consistência histórica; comportamento de pass-through não institucional; padrões estatísticos incompatíveis com trading humano. Título 20 — Salvaguardas Internas Artigo 20.1 — Daily Loss Interno de 4% O limite interno de perda diária das contas financiadas é de 4% — mais rígido que o contratual de 5% —, implementado por monitoramento automatizado 24/7 (Traders Connect), com encerramento das operações e desativação automática do copy ao acionamento. Artigo 20.2 — Reingresso após Daily Loss §1º — Conta cortada por daily loss NÃO reingressa na Operação em andamento da Conta Mestre. Seu reacoplamento ao sistema de cópia ocorrerá somente na próxima Ordem Gênese. §2º — Se o corte decorreu de erro de gestão (e não de travessia ordenada de fases), aplica-se adicionalmente período de espera de 1 semana, destinado a reavaliação de estratégia, recomposição emocional e ajuste do plano. Artigo 20.3 — Retenção Estratégica de Lucros Política de represamento dos primeiros 3% de lucro de cada conta financiada, elevando o colchão efetivo frente ao Maximum Loss; retenção mínima mensal de 2% de lucro; revisão a cada ciclo. 
===== PÁGINA 22 =====
JP WEALTH HOLDING  ·  CÓDIGO DE GOVERNANÇA E GESTÃO DE RISCO  ·  V10.0 
JPW-GOV-001  ·  Confidencial — Uso Interno  ·  Página 22 
§1º — Esta política protege contra a eliminação contratual da conta satélite e não constitui, em hipótese alguma, autorização para ampliar alavancagem, alargar stops ou flexibilizar a Matriz Quadrifásica — vedação do Art. 12.2 integralmente aplicável. Artigo 20.4 — Ressincronização Técnica de realinhamento entre balance e equity (fechar e reabrir posições no mesmo ponto) para conter o descolamento contábil que fragiliza a conta frente ao daily loss recalculado. Política: ressincronizar sempre que o drawdown diário estiver abaixo de 4% no dia seguinte ao recálculo. Custos reconhecidos: slippage e spreads/comissões adicionais. Artigo 20.5 — Simulação Obrigatória Fases × Daily Loss Antes da ativação de qualquer conta em perfil Longevity, o Compliance Board validará simulação da interação entre travessia rápida de fases da Conta Mestre e o daily loss interno de 4%, certificando que a poda LIFO compulsória não colide com o corte automático de copy [Anexo C]. Título 21 — Estrutura de Contas e Perfis Artigo 21.1 — Segregação As contas não serão unificadas via merge account, preservando a diversificação tática entre perfis (Longevity, High Longevity, High Longevity Plus) conforme Título 10 do Livro II e o princípio deliberado: quanto maior o risco do perfil, menor o teto de participação na carteira. Artigo 21.2 — Estrutura Planejada de Adesão # Instituição Capital Perfil 1 FTMO $100.000 Longevity 2 FTMO $100.000 Longevity 3 FTMO $100.000 High Longevity 4 FTMO $100.000 High Longevity Plus 5 The5%ers $100.000 High Longevity 6 The Trading Pit $100.000 High Longevity  Título 22 — Instrumentos, Tetos e Atividade Artigo 22.1 — Tetos de Exposição por Instrumento (conta de referência JP Wealth MAM) Instrumento Teto (lote) Status EUR/USD 0,05 Ativo GBP/USD 0,04 Ativo AUD/USD 0,09 Ativo NZD/USD 0,09 Ativo USD/JPY 0,05 Ativo USD/CHF 0,05 Ativo 
===== PÁGINA 23 =====
JP WEALTH HOLDING  ·  CÓDIGO DE GOVERNANÇA E GESTÃO DE RISCO  ·  V10.0 
JPW-GOV-001  ·  Confidencial — Uso Interno  ·  Página 23 
Instrumento Teto (lote) Status USD/CAD 0,05 Ativo AUD/CAD 0,11 Ativo US500 — SUSPENSO — fora do escopo Forex vigente [ratificar exclusão definitiva, Anexo C] XAU/USD e demais metais — VEDADO — proibição permanente por decreto do Gestor (Art. 22.2)  §1º — Tabela revisada nesta consolidação (base anterior: 07/07/2025). A cada conta satélite aplica-se o fator do respectivo perfil sobre estes tetos, após normalização por saldo. Revisão obrigatória a cada alteração relevante de valor nominal dos contratos. Artigo 22.2 — Vedação Permanente de Metais Fica terminantemente proibida a operação de XAU/USD e demais metais, em qualquer conta da estrutura. Registro de fundamento: o histórico documentado da gestão demonstra que as perdas de mesas proprietárias e parcela relevante dos prejuízos pessoais decorreram da operação de ouro sob viés de teimosia (“o ouro me deve algo”). A vedação é comportamental e definitiva; sua remoção exigiria emenda formal com justificativa quantitativa, parecer da Auditoria e deliberação unânime do Compliance Board. Artigo 22.3 — Diferenças Estruturais Reconhecidas As mesas proprietárias impõem limites inflexíveis e absolutos que exigem: redução da alavancagem real frente ao padrão institucional; monitoramento da velocidade de flutuação (o risco de violação é temporal, não apenas financeiro); e aceitação do snapshot contábil diário, inexistente no ambiente institucional. Artigo 22.4 — Destino dos Saques Por deliberação do Gestor Geral (Anexo B, D-1), 100% dos saques líquidos das prop firms, após encargos, destinam-se ao Caixa Central da Holding, sob os critérios macro do Livro V. A Auditoria atua como custodiante e executora da transferência, sem poder de destinação. Fica revogada a autonomia de destinação anteriormente atribuída à supervisora. Artigo 22.5 — Operação Simbólica de Atividade A cada 15 dias sem novas ordens, a Auditoria executará operação simbólica de lote mínimo (0,01), aberta e imediatamente fechada, exclusivamente para reiniciar o contador de inatividade. §1º — Exceção formal à exclusividade do Art. 5.1: a operação simbólica é permitida mesmo com Operação ativa, desde que em ativo distinto, com duração inferior a 60 segundos e registro obrigatório. §2º — Para não constituir padrão estatístico detectável, horário, ativo e intervalo exato serão variados dentro da janela regulamentar.  
===== PÁGINA 24 =====
JP WEALTH HOLDING  ·  CÓDIGO DE GOVERNANÇA E GESTÃO DE RISCO  ·  V10.0 
JPW-GOV-001  ·  Confidencial — Uso Interno  ·  Página 24 
LIVRO V  Alocação Patrimonial, Tesouraria e Distribuição  Título 23 — Missão Patrimonial A JP Wealth Holding existe como estrutura patrimonial antifrágil de longo prazo: preserva capital frente a riscos sistêmicos; produz crescimento sustentável com base em estatística, governança e disciplina; diversifica fontes de receita; e minimiza fragilidades emocionais e operacionais, assegurando continuidade de gestão em cenários adversos. A organização do capital em camadas de exposição e assimetria segue o princípio da convexidade antifrágil. Título 24 — Estrutura Macro e Micro de Alocação Artigo 24.1 — Alocação Macro Segmento Proporção do Patrimônio Contas de Operação JP Wealth 65% Investimentos Externos 20% Caixa e Fundo de Resgate (FCR + FEO + liquidez) 15%  Artigo 24.2 — Contas de Operação (65%) Linha Proporção JP Wealth Base 60% JP Wealth Longevity 20% JP Wealth High Yield 20%  As contas Base e Longevity constituem o núcleo de estabilidade e repetição estatística; a High Yield é a camada de convexidade — menor alocação absoluta, exposta a ganhos assimétricos com risco limitado. Artigo 24.3 — Investimentos Externos (20%) Veículo Proporção Status Oracullus 34% Homologado Sollitus 33% Homologado FIIs 33% Homologado “Recovery”, Real Estate, Value Investing, ETFs, ouro patrimonial, Bitcoin — Candidatos NÃO homologados — sujeitos a deliberação do Compliance Board antes de qualquer aporte  
===== PÁGINA 25 =====
JP WEALTH HOLDING  ·  CÓDIGO DE GOVERNANÇA E GESTÃO DE RISCO  ·  V10.0 
JPW-GOV-001  ·  Confidencial — Uso Interno  ·  Página 25 
§1º — Ouro como reserva patrimonial de longo prazo é matéria distinta da vedação de trading do Art. 22.2 e somente poderá ser considerado mediante homologação expressa, com esta distinção lavrada em ata.  Título 25 — Rebalanceamento e Registros  Artigo 25.1 — Período de Gestão O rebalanceamento obedece à maturação dos ciclos técnicos: nenhum rebalanceamento será executado durante Período de Gestão ativo. O Período de Gestão corresponde ao ciclo anual de 12 meses do Art. 5.3; contas com ciclos dessincronizados são avaliadas individualmente ao fechamento de cada ciclo, e realocações entre blocos macro ocorrem no fechamento anual consolidado da Holding. Artigo 25.2 — Autoridade e Registro A execução de qualquer ajuste patrimonial é competência exclusiva do Compliance Board (Art. 15.2), documentada na Planilha de Resultados Mensais — repositório central e livro de prestação de contas da Holding, garantindo rastreabilidade integral de cada decisão patrimonial. Título 26 — Reservas: Reconciliação Normativa Artigo 26.1 — Composição do Bloco de 15% O bloco macro “Caixa e Fundo de Resgate” (15% do patrimônio total) comporta, em seu interior, o FCR e o FEO definidos no Título 13 do Livro II, além da liquidez operacional excedente. Artigo 26.2 — Prevalência dos Mínimos Absolutos Os mínimos absolutos — FCR ≥ 15% do capital nominal da Conta Mestre e FEO ≥ 6 meses de despesas — prevalecem sobre o percentual macro. Se a soma dos mínimos exceder 15% do patrimônio total, os mínimos serão integralmente constituídos e o excedente deduzido proporcionalmente dos blocos de Operação e Investimentos Externos até regularização orgânica. Artigo 26.3 — Liquidez FCR: liquidez imediata (D+0/D+1). FEO e demais recursos do bloco: liquidez de até D+2. Fica sanada a divergência entre as redações anteriores (“liquidez imediata” vs. “+2 dias”).  Título 27 — Caixa Institucional (Caixa Central) Artigo 27.1 — Núcleo Único de Movimentação Nenhuma movimentação patrimonial poderá ocorrer fora do Caixa Central. Fluxos abrangidos: saques de prop firms homologadas (destino obrigatório — Art. 22.4); aportes; transferências entre corretoras; envio de capital às contas ativas; retornos de investimentos externos; distribuições autorizadas; gestão do Fundo de Resgate.   
===== PÁGINA 26 =====
JP WEALTH HOLDING  ·  CÓDIGO DE GOVERNANÇA E GESTÃO DE RISCO  ·  V10.0 
JPW-GOV-001  ·  Confidencial — Uso Interno  ·  Página 26 
Artigo 27.2 — Segmentação Camada Proporção Descrição 
Caixa Patrimonial Principal — Interactive Brokers (IBKR) 50% Custódia bancária institucional em USD; movimentação internacional via SWIFT entre contas de mesma titularidade; inicialmente sob titularidade pessoal do fundador até formalização jurídica da Holding. 
Caixa Operacional Ágil — USDT custodial 50% Liquidez operacional imediata (paridade nominal 1:1 USD) para fluxo técnico entre prop firms, corretoras e plataformas; custódia em carteiras privadas controladas internamente, registrada em planilha de caixa.  Artigo 27.3 — Custódia de Chaves Privadas A posse e integridade das chaves privadas representam a titularidade real dos ativos em stablecoins. Procedimento mínimo obrigatório: backup físico da seed em dois locais geograficamente distintos; registro de titularidade e acesso na governança documental; [esquema de assinatura 2-de-2 entre Gestor e Auditoria — proposta em ratificação, Anexo C]. Reconhece-se o risco de emissor do USDT como risco residual aceito e monitorado. Artigo 27.4 — Governança Documental Toda movimentação será registrada na Planilha de Caixa Institucional (data, valor, natureza, contrapartes, plataformas), com validação formal do Compliance Board. A Planilha de Caixa constitui o livro-razão patrimonial oficial da Holding. Título 28 — Política de Distribuição de Lucros Artigo 28.1 — Regimes A cada encerramento de Período de Gestão, o Compliance Board deliberará o regime do ciclo subsequente: Regime Distribuição Critério I — Crescimento 0% ordinária; 100% do lucro líquido reinvestido. Exceções extraordinárias: até 20% do excedente, com aprovação formal. Fase de construção estrutural; prioridade ao efeito composto. II — Híbrido 30% a 50% do lucro líquido consolidado; saldo reinvestido. Transição patrimonial com robustez acumulada. III — Dividendos Até 70% do lucro líquido; mínimo de 30% de reinvestimento contínuo. Maturação plena e reservas estratégicas consolidadas.  §1º — Vedada qualquer distribuição enquanto FCR e FEO não estiverem integralmente constituídos (Art. 13.3).    
===== PÁGINA 27 =====
JP WEALTH HOLDING  ·  CÓDIGO DE GOVERNANÇA E GESTÃO DE RISCO  ·  V10.0 
JPW-GOV-001  ·  Confidencial — Uso Interno  ·  Página 27 
Título 29 — Corretoras e Diversificação Artigo 29.1 — Política de Diversificação A operação concentra-se em corretoras ECN/híbridas institucionais reguladas em jurisdições consolidadas (FCA, FINMA, ASIC). A dispersão deliberada de pontos de fragilidade protege contra riscos jurídicos, administrativos, falhas de custódia e eventos exógenos de jurisdição. Expansão escalonada: a cada USD 10.000 de capital efetivamente acumulado, ativa-se nova conta na corretora seguinte da lista homologada. Artigo 29.2 — Corretoras Homologadas – FxPro (FCA/CySEC/SCB) — ECN/STP híbrido de execução institucional; – Valutrades (FCA/SCB) — ECN puro, execução de alta velocidade; – Pepperstone (ASIC/FCA/BaFin/DFSA/CMA) — ECN/STP híbrido, liquidez robusta; – Key To Markets (FCA/FSC) — ECN puro com DMA; – IG (FCA/FINMA/ASIC/MAS) — vértice de estabilidade sistêmica; – Swissquote (FINMA — regulação bancária) — banco suíço institucional, custódia de altíssima confiabilidade; – Hantec — função mista: broker institucional da Conta Mestre e solução de estrutura de contas externas (classificação dual reconhecida). Artigo 29.3 — Contas Modelo (Track Record Puro) Mantêm-se contas modelo nas corretoras Vantage (Cent) e Hantec (Cent), sem aportes ou saques, sob capital fixo, com a única finalidade de gerar histórico técnico puro de performance para validação documental contínua do modelo.  
===== PÁGINA 28 =====
JP WEALTH HOLDING  ·  CÓDIGO DE GOVERNANÇA E GESTÃO DE RISCO  ·  V10.0 
JPW-GOV-001  ·  Confidencial — Uso Interno  ·  Página 28 
LIVRO VI  Método e Execução Técnica (Nocuda®) Título 30 — Status Doutrinário O Método Nocuda® fundamenta a filosofia técnica da gestão: observação do comportamento dos preços e do fluxo predominante de capital; tendências com propensão à continuidade até evidência objetiva de reversão; estruturas recorrentes exploráveis de forma probabilística. Os pilares e máximas do Nocuda possuem natureza doutrinária; sua definição operacional vinculante reside exclusivamente neste Livro e no Manual Nocuda, vedada a citação de material mnemônico (pôsteres, cartazes) como fonte normativa. Título 31 — Checklist de Análise Técnica (Perfil Swing) Âncoras: H4 e H1 (decisórios), com Diário (direcional). Gatilho de execução: H1, em confluência com as Linhas Nocuda. Etapa 1 — Contexto: “O mercado permite operar?” – Calendário econômico; ciclo de juros; dólar (DXY); posicionamento institucional (COT). Etapa 2 — Regime de Mercado: “Que tipo de mercado estou enfrentando?” Regime Característica Conduta Tendência limpa Impulsos consistentes Buscar continuação. Tendência agressiva Expansão sem pullback Evitar reversão. Range Reversão à média Comprar suporte / vender resistência. Compressão Baixa volatilidade Aguardar expansão. Expansão Volatilidade crescente Reduzir exposição. Caótico Ruído estrutural (proxy objetiva: VRM > 1,50 com falha estrutural) Vedado operar.  Etapa 3 — Análise Técnica: “O gráfico possui lógica operacional?” – Fluxo de leitura: tendência dominante; rompimentos (suporte, resistência, canal, Nocuda); tendência macro (D1), primária (H4) e secundária (H4/H1); lateralidade; – Zonas de liquidez: suportes/resistências, LTA, LTB, canais, Linhas Nocuda revalidadas (memória institucional); – Pivots: D1 e H1/H4; qualidade de rompimentos e retrações; – Estrutura: rompimento forte (fechamento fora, expansão, continuidade, sem rejeição forte); retração saudável (desaceleração, pavio, perda de momentum, defesa estrutural). Etapa 4 — Conformidade Estatutária: “A operação cabe dentro do sistema?” Etapa de verificação obrigatória e eliminatória, integrada nesta consolidação: – Fase vigente da Conta e da Grade Ativa — a operação respeita o teto de alavancagem da fase? 
===== PÁGINA 29 =====
JP WEALTH HOLDING  ·  CÓDIGO DE GOVERNANÇA E GESTÃO DE RISCO  ·  V10.0 
JPW-GOV-001  ·  Confidencial — Uso Interno  ·  Página 29 
– Exclusividade — existe Operação Única em andamento? Se sim, nova tese é vedada; – Regime de volatilidade (VRM) e conduta correspondente; – Gênese — risco ≤ 1,00% E alavancagem ≤ 0,4x (Art. 8.1); – Stop — distância ≥ 2,0 × ATR55 e validação Raiz-N (Arts. 8.4 e 8.5); – Instrumento — consta como Ativo na tabela do Art. 22.1? Metais: vedados; – Contexto da conta — desempenho do mês e do ano frente às referências, sem que resultado positivo autorize risco adicional (Art. 12.2). Etapa 5 — Execução: “Existe gatilho válido?” – Toques na Linha Nocuda a favor da tendência; – Toque nas bandas de canal; – Continuação de tendência (retração do pivot); – Rompimento de canal (retração do rompimento); – Rompimento da perna 2 em contexto de rompimento de canal (continuação); – Regra de ouro: NOCUDA + CONFLUÊNCIA. Cada gatilho carrega sua invalidação declarada no template de sinal. Etapa 6 — Registro Preenchimento integral do template de sinal (Gênese, defesas ou saída), sem campos omissos. Campo omisso interrompe a execução até esclarecimento (Art. 17.3). Título 32 — Referências Quantitativas de Planejamento Referência histórica de rentabilidade: 3,5% ao mês e 35%–40% ao ano — valores unificados nesta consolidação, prevalecendo sobre menções divergentes de instrumentos revogados. Tais referências não constituem promessa, garantia ou expectativa linear; servem exclusivamente ao dimensionamento e à avaliação de eficiência. Nas Fases 2 e 3, resultados próximos ao ponto de equilíbrio constituem desempenho satisfatório.  
===== PÁGINA 30 =====
JP WEALTH HOLDING  ·  CÓDIGO DE GOVERNANÇA E GESTÃO DE RISCO  ·  V10.0 
JPW-GOV-001  ·  Confidencial — Uso Interno  ·  Página 30 
LIVRO VII  Disposições Finais, Revisão e Ratificação Título 33 — Revisão e Evolução Artigo 33.1 — Natureza Evolutiva Alterações futuras exigem evidência operacional, análise estatística, auditoria documental e demonstração objetiva de benefício. Nenhuma alteração ampliará risco sem justificativa quantitativa formal. Toda revisão preservará os princípios de preservação patrimonial, disciplina e sobrevivência de longo prazo. Artigo 33.2 — Integridade Operacional É proibida a utilização de lucros realizados, margens livres ou recursos de estruturas paralelas para ampliar os limites de risco deste Código. A violação dos limites de dimensionamento constitui infração grave. Título 34 — Compromisso e Vigência A adoção deste Código representa o compromisso formal da gestão com a disciplina, a responsabilidade fiduciária e a execução baseada em processos. A longevidade operacional é construída pela repetição consistente de decisões corretas, não pela busca de resultados extraordinários isolados. Este documento entra em vigor na data de sua ratificação formal pelo Compliance Board, revogando integralmente os instrumentos listados na capa. Os itens do Anexo C permanecem com os valores-padrão indicados até ratificação ou substituição expressa.  CLÁUSULA PÉTREA FINAL A preservação do capital, a disciplina operacional e o respeito aos limites de risco possuem prioridade absoluta sobre qualquer expectativa de retorno financeiro. Não existe linha de chegada. Existe apenas o compromisso renovado, todos os dias, com a vigilância disciplinada.  
RATIFICAÇÃO _____________________________________________ João Paulo V. Cirqueira — Gestor Geral _____________________________________________ Kharen Luiza Felix Santos Lemos — Auditoria e Supervisão Local e data: ______________________________  
===== PÁGINA 31 =====
JP WEALTH HOLDING  ·  CÓDIGO DE GOVERNANÇA E GESTÃO DE RISCO  ·  V10.0 
JPW-GOV-001  ·  Confidencial — Uso Interno  ·  Página 31 
LIVRO — ANEXO A Tabela Mestra Consolidada de Fases Faixas de drawdown por fase, Conta Mestre e satélites por perfil (fatores do Art. 10.3 aplicados sobre as faixas mestre): Fase Mestre (100%) Longevity (53%) High Longevity (40%) HL Plus (27%) Alav. Máx. Mestre 1 — Exposição Inicial 0,00 – 4,00% 0,00 – 2,12% 0,00 – 1,60% 0,00 – 1,08% 4,0x 2 — Restrição Moderada 4,01 – 8,00% 2,12 – 4,24% 1,60 – 3,20% 1,08 – 2,16% 2,0x 3 — Restrição Avançada 8,01 – 12,00% 4,24 – 6,36% 3,20 – 4,80% 2,16 – 3,24% 1,0x 4 — Salvaguarda Final 12,01 – 15,00% 6,36 – 7,95% 4,80 – 6,00% 3,24 – 4,05% 0,4x  Nota de risco: no perfil Longevity, a Fase 3 da Mestre pode implicar variação satélite superior a 2 p.p. em janela curta; a interação com o daily loss interno de 4% exige a simulação do Art. 20.5 antes da ativação.  
===== PÁGINA 32 =====
JP WEALTH HOLDING  ·  CÓDIGO DE GOVERNANÇA E GESTÃO DE RISCO  ·  V10.0 
JPW-GOV-001  ·  Confidencial — Uso Interno  ·  Página 32 
LIVRO — ANEXO B Registro de Deliberações e Alterações da Consolidação B.1 — Deliberações Formais do Gestor Geral (03/07/2026) Ref. Matéria Deliberação D-1 Destino dos saques de prop firms (contradição Carta de Auditoria × Regulamento de Alocação 8.1) 100% ao Caixa Central, sob alocação macro. Auditoria passa a custodiante/executora da transferência, sem poder de destinação. Codificado no Art. 22.4. 
D-2 Defesa Final na Fase 4 (congelamento × Art. 9.3) Mantida, como exceção única: solicitação formal escrita do Gestor, execução exclusiva pela Auditoria, veto pleno, uma vez por Operação, registro em ata. Codificado no Art. 9.3. 
D-3 Modelo de correção das satélites (1/3 fixo × perfis) Fatores por função da conta, sob invariante de segurança e princípio “mais risco, menor teto de participação na carteira”. Codificado nos Arts. 10.2 e 10.3.  B.2 — Principais Alterações Frente aos Instrumentos Revogados – Hierarquia normativa e regra de conflito instituídas (Arts. 2.1–2.2) — inexistiam; – Definição formal de Drawdown Operacional, com base, referência, medição contínua e histerese de retorno (Art. 4.1); – Critérios objetivos de identificação de Gênese e de encerramento de Operação (Arts. 4.3–4.4); – Fórmula do Firewall corrigida com normalização por saldo; redação “lote × 1/3” revogada por erro matemático (Art. 10.1); – Fatores de perfil recalibrados de 66/50/33% para 53/40/27%, preservando os DDR-alvo de 8/6/4% sob o limite de 15% (o fator de 66% projetaria 9,9% — margem nula frente ao Maximum Loss de 10%); – Gênese: dupla restrição explícita — risco ≤ 1% E alavancagem ≤ 0,4x (Art. 8.1); – Gatilho compulsório de poda LIFO (+1,00 p.p.) promovido da Tese ao corpo estatutário (Art. 7.1, §2º); – Protocolo de Gap instituído (Art. 6.1, §2º); – Autoridade de retorno pós-quarentena definida: deliberação conjunta registrada do Compliance Board (Art. 11.2, §3º); – Compliance Board formalmente composto e com competências exclusivas (Título 15); – Procedimento de veto com fundamentação escrita, desempate pela interpretação mais restritiva e limite do veto frente a obrigações compulsórias (Art. 17.5); – Protocolo de contingência de credenciais em três camadas — eliminação do ponto único de falha humano (Art. 18.1); – Canais oficiais com SLA e contingência (Art. 18.5); – Conflito de autoridade sobre execução patrimonial resolvido: Gestor supervisiona; Compliance Board executa (Arts. 15.2 e 16.1); – Cláusula suspensiva regulatória para captação de terceiros (Art. 16.3); 
===== PÁGINA 33 =====
JP WEALTH HOLDING  ·  CÓDIGO DE GOVERNANÇA E GESTÃO DE RISCO  ·  V10.0 
JPW-GOV-001  ·  Confidencial — Uso Interno  ·  Página 33 
– Livro IV migrado integralmente à arquitetura vertical: revogados DDR 12%, multiplicidade de operações e fatores antigos; – Reingresso pós-daily-loss disciplinado: reacoplamento apenas na próxima Gênese (Art. 20.2); – Operação simbólica regulada como exceção formal à exclusividade, com anti-padrão (Art. 22.5); – Vedação permanente de metais codificada com fundamento registrado (Art. 22.2); US500 suspenso; – Reservas reconciliadas: FCR/FEO como mínimos absolutos dentro do bloco macro de 15%, com prevalência dos mínimos (Título 26); referência quebrada ao “Título XI” sanada; divergência de liquidez sanada (Art. 26.3); – Tabela de margem corrigida (faixa 700%–1000%) e ação da faixa crítica compatibilizada com o LIFO (Art. 18.4); – Notação do stop corrigida: “distância do stop em múltiplos de ATR(55)” (Art. 8.4); – Checklist renumerado (Etapas 1–6) e dotado de Etapa de Conformidade Estatutária eliminatória (Título 31); – Metas de referência unificadas em 3,5% a.m. / 35–40% a.a. (Título 32); – Projeções de retorno por perfil e afirmação de “probabilidade de ruína < 1% a.a.” removidas por ausência de memória de cálculo (Art. 3.4); – Investimentos externos: “Recovery” e classes não homologadas segregadas como candidatos sujeitos a deliberação (Art. 24.3).  
===== PÁGINA 34 =====
JP WEALTH HOLDING  ·  CÓDIGO DE GOVERNANÇA E GESTÃO DE RISCO  ·  V10.0 
JPW-GOV-001  ·  Confidencial — Uso Interno  ·  Página 34 
LIVRO — ANEXO C Itens Pendentes de Ratificação Parâmetros propostos nesta consolidação com valor-padrão vigente até deliberação expressa do Compliance Board: # Item Padrão proposto Referência 1 Fator de segurança F (Raiz-N) 1,25 Art. 8.5 2 Cronograma de recálculo do VRM Semanal, fechamento de sexta-feira, em H4 Art. 4.6 3 Canal secundário de sinais E-mail institucional ou Telegram Art. 18.5 4 Tetos de participação por perfil na carteira de satélites Longevity ≤ 1/3; High Longevity ≤ 1/2; Plus sem teto (mín. 1 conta) Art. 10.3 5 Terceiro custodiante das credenciais de contingência A nomear Art. 18.1 6 US500 — exclusão definitiva ou reativação futura Suspenso Art. 22.1 7 Custódia USDT — esquema de assinatura 2-de-2 Proposto Art. 27.3 8 Simulação Fases × Daily Loss (perfil Longevity) Obrigatória antes da ativação Art. 20.5 9 Terceiro membro independente do Compliance Board Avaliação futura Art. 15.1 10 Distinção ouro-trading (vedado) × ouro-patrimonial (homologável) Registrar em ata Arts. 22.2 e 24.3  `;
function openOnboardingModal(mode, initialStep){
  if(jpWealthPersistenceIsBlocked()) resumeJPWealthPersistence();
  const box=$('modalBox');
  $('modalOverlay').classList.add('show');
  box.classList.add('onboarding-modal');
  const isEditMode = mode==='edit' || (!mode && S.onboarding && S.onboarding.done);
  const ob=isEditMode ? (S.onboarding||{}) : structuredClone(DEFAULTS.onboarding);
  let profSel=isEditMode?((S.period&&S.period.profile)||'base'):null;
  let profListOpen=!profSel;
  let riskProfileAccepted=isEditMode && !!profSel;
  let simHorizon=12;
  let simCompareMode='current';
  let simMode='reference';
  let simCurveVisible={base:true, longevity:true, high_longevity:true, high_longevity_plus:true};
  let brokerSel=isEditMode ? (brokerFor(ob.corretora)?.key || null) : null;
  let institutionType=brokerSel?(isPropFirm(brokerFor(ob.corretora))?'prop':'broker'):null;
  let institutionListOpen=!brokerSel;
  let brokerLogin=String(ob.brokerLogin||'');
  let investorPassword=String(ob.investorPassword||'');
  let brokerServer=String(ob.brokerServer||'');
  let plataforma=String(ob.plataforma||'');
  let alavCorretora=String(ob.alavCorretora||'');
  let propDailyDrawdown=String(ob.propDailyDrawdown||'');
  let propMaxDrawdown=String(ob.propMaxDrawdown||'');
  let propTrailingRule=String(ob.propTrailingRule||'');
  let propTrailingDescription=String(ob.propTrailingDescription||'');
  let propProfitTarget=String(ob.propProfitTarget||'');
  let propMinTradingDays=String(ob.propMinTradingDays||'');
  let propAbsenceRules=String(ob.propAbsenceRules||'');
  let restrictiveRuleAccepted=Boolean(ob.restrictiveRuleAccepted);
  let reserveFcrCurrent=String(ob.reserveFcrCurrent||'');
  let reserveMonthlyExpenses=String(ob.reserveMonthlyExpenses||'');
  let reserveFeoCurrent=String(ob.reserveFeoCurrent||'');
  let reserveSegregationAccepted=Boolean(ob.reserveSegregationAccepted);
  let reserveDeficitAccepted=Boolean(ob.reserveDeficitAccepted);
  let reserveNotes=String(ob.reserveNotes||'');
  let centralCashStatus=String(ob.centralCashStatus||'');
  let centralCashCustody=String(ob.centralCashCustody||'');
  let centralCashCustodyOther=String(ob.centralCashCustodyOther||'');
  let centralCashMainPct=String(ob.centralCashMainPct||'');
  let centralCashAgilePct=String(ob.centralCashAgilePct||'');
  let centralCashLiquidityPct=String(ob.centralCashLiquidityPct||'');
  let centralCashExternalPct=String(ob.centralCashExternalPct||'');
  let centralCashOtherPct=String(ob.centralCashOtherPct||'');
  let fcrLiquidity=String(ob.fcrLiquidity||'');
  let feoLiquidity=String(ob.feoLiquidity||'');
  let cashLedgerStatus=String(ob.cashLedgerStatus||'');
  let centralCashPolicyAccepted=Boolean(ob.centralCashPolicyAccepted);
  let centralCashNoAccepted=Boolean(ob.centralCashNoAccepted);
  let centralCashNotes=String(ob.centralCashNotes||'');
  let epStatus=String(ob.epStatus||'');
  let epPlatform=String(ob.epPlatform||'');
  let epPlatformOther=String(ob.epPlatformOther||'');
  let epReference=String(ob.epReference||'');
  let epDailyLimit=String(ob.epDailyLimit||'');
  let epMaxDrawdown=String(ob.epMaxDrawdown||'');
  let epStatuteMatch=String(ob.epStatuteMatch||'');
  let epRestrictiveAccepted=Boolean(ob.epRestrictiveAccepted);
  let epPropDailyEnabled=String(ob.epPropDailyEnabled||'');
  let epPropDailyBase=String(ob.epPropDailyBase||'');
  let epPropDailyNotes=String(ob.epPropDailyNotes||'');
  let epTestStatus=String(ob.epTestStatus||'');
  let epNoConfigAccepted=Boolean(ob.epNoConfigAccepted);
  let epNotes=String(ob.epNotes||'');
  let summaryAccepted=false;
  const hasSelectedInstitution = ()=>!!brokerSel;
  const hasCompleteConnectionData = ()=>Boolean(String(brokerLogin||'').trim()) && Boolean(String(investorPassword||'').trim()) && Boolean(String(brokerServer||'').trim()) && Boolean(String(plataforma||'').trim()) && Boolean(String(alavCorretora||'').trim());
  const hasCompletePropRules = ()=> institutionType!=='prop' ? true :
    (Boolean(String(propDailyDrawdown||'').trim()) && Boolean(String(propMaxDrawdown||'').trim()) && restrictiveRuleAccepted===true);
  const canShowRiskProfileStep = ()=>hasSelectedInstitution() && hasCompleteConnectionData() && hasCompletePropRules();
  const canShowOnboardingSummary = ()=>{
    if(!canShowRiskProfileStep() || !profSel) return false;
    const saldoEl=$('obSaldo');
    const saldo=saldoEl ? (parseFloat(saldoEl.value)||0) : (S.params.saldoIni||0);
    if(!(saldo>0)) return false;
    const dateEl=$('obData');
    if(isEditMode){ if(!((dateEl && dateEl.value) || S.params.inicio)) return false; }
    else if(!(dateEl && dateEl.value)) return false;
    return true;
  };
  const canShowEquityProtectorStep = ()=>canShowOnboardingSummary();
  let obPlatformWrap=null, obPlatformEl=null, obPlatformTrigger=null, obPlatformPanel=null;
  let obAlavWrap=null, obAlavEl=null, obAlavTrigger=null, obAlavPanel=null;
  let obLeverageExplain=null, obLeverageExplainToggle=null;
  const leveragePresets=['1:30','1:50','1:100','1:200','1:400','1:500'];
  const platformPresets=TRADING_PLATFORMS.map(p=>p.name);
  const epStatusOptions=['Sim, vou utilizar.','Não vou utilizar.','Ainda vou configurar antes de iniciar o período.','Não se aplica a esta conta.'];
  const epPlatformOptions=['Traders Connect.','Account Protector.','KT Equity Protector.','Equity Guard.','Outra.','Nenhuma.'];
  const epStatuteMatchOptions=['Sim.','Não.','Ainda não configurei.','Não se aplica.'];
  const epTestOptions=['Sim, testei em conta demo.','Sim, testei com lote mínimo.','Ainda não testei.','Não se aplica.'];
  const epPropDailyEnabledOptions=['Sim.','Não.','Não informado pela mesa.'];
  const epPropDailyBaseOptions=['Saldo inicial.','Equity inicial do dia.','Balance do dia anterior.','Regra específica da mesa.'];
  const fld=(id,label,val,ph,type,note)=>`<div class="field" style="margin-bottom:10px">
    <label>${label}</label><input type="${type||'text'}" id="${id}" value="${esc(val)}" placeholder="${ph||''}">${note?`<span class="note">${note}</span>`:''}</div>`;
  const optList=(items,selected)=>items.map(o=>`<option value="${esc(o)}" ${selected===o?'selected':''}>${esc(o)}</option>`).join('');
  const numVal=v=>parseFloat(String(v||'').replace(',','.'))||0;
  const reserveCapitalValue=()=>{
    const saldoEl=$('obSaldo');
    return saldoEl ? (parseFloat(saldoEl.value)||0) : (isEditMode?(S.params.saldoIni||0):0);
  };
  // A matemática FCR/FEO vive em reserveRequirementsCalc() (10-domain/07) — fonte
  // única compartilhada com o Planejamento FX; não reimplementar aqui.
  const reserveCalc=()=>reserveRequirementsCalc({
    capital:reserveCapitalValue(),
    fcrCurrent:numVal(reserveFcrCurrent),
    monthlyExpenses:numVal(reserveMonthlyExpenses),
    feoCurrent:numVal(reserveFeoCurrent)
  });
  const cashSegTotal=()=>['centralCashMainPct','centralCashAgilePct','centralCashLiquidityPct','centralCashExternalPct','centralCashOtherPct']
    .reduce((sum,k)=>sum+numVal({centralCashMainPct,centralCashAgilePct,centralCashLiquidityPct,centralCashExternalPct,centralCashOtherPct}[k]),0);
  const liquidityTooSlow=(kind,val)=> kind==='fcr' ? (val==='D+2'||val==='Acima de D+2'||val==='Não definido') : (val==='Acima de D+2'||val==='Não definido');
  const liquidityLabel=(kind,val)=>{
    if(!val || val==='Não definido') return {label:'pendente', color:'var(--f4)'};
    if(kind==='fcr') return (val==='D+0'||val==='D+1') ? {label:'adequado', color:'var(--f1)'} : (val==='D+2'?{label:'atenção', color:'var(--f2)'}:{label:'inadequado', color:'var(--f4)'});
    return (val==='D+0'||val==='D+1'||val==='D+2') ? {label:'adequado', color:'var(--f1)'} : {label:val==='Acima de D+2'?'atenção':'pendente', color:val==='Acima de D+2'?'var(--f2)':'var(--f4)'};
  };
  const centralCashCalc=()=>{
    const total=cashSegTotal();
    const ledgerStrong=cashLedgerStatus==='Livro-razão patrimonial ativo'||cashLedgerStatus==='Planilha de caixa ativa'||cashLedgerStatus==='Planilha de Caixa Institucional ativa';
    const coherent=total>0 && Math.abs(total-100)<=3;
    let score=0;
    if(centralCashStatus==='Sim.') score+=30;
    else if(centralCashStatus==='Em implantação.') score+=15;
    if(centralCashCustody && (centralCashCustody!=='Outra'||String(centralCashCustodyOther||'').trim())) score+=20;
    if(centralCashPolicyAccepted) score+=20;
    if(ledgerStrong) score+=20;
    else if(cashLedgerStatus==='Registro parcial') score+=10;
    if(coherent) score+=10;
    const status=centralCashStatus==='Não.'?'Caixa Central ausente':((centralCashStatus==='Sim.'&&centralCashPolicyAccepted&&ledgerStrong)?'Caixa Central regular':'Caixa Central em implantação');
    const traceClass=score<40?'frágil':(score<70?'em implantação':(score<90?'funcional':'robusto'));
    return {total, coherent, ledgerStrong, score, status, traceClass,
      tone:status==='Caixa Central regular'?'var(--f1)':(status==='Caixa Central ausente'?'var(--f4)':'var(--f2)')};
  };
  const pctText=v=>(Number.isFinite(v)?v:0).toFixed(1).replace('.',',')+'%';
  const metricBar=(pct,color)=>`<div style="height:8px; border-radius:999px; background:var(--line); overflow:hidden"><div style="height:100%; width:${Math.min(100,Math.max(0,pct))}%; background:${color}; border-radius:999px"></div></div>`;
  const compareBars=(required,current,color)=> {
    const max=Math.max(required,current,1);
    return `<div style="display:grid; gap:8px">
      <div><div style="display:flex; justify-content:space-between; font-size:calc(10px * var(--fs-scale)); color:var(--ink-dim)"><span>Exigido</span><span>${fmtMoney2(required)}</span></div>${metricBar((required/max)*100,'var(--ink-faint)')}</div>
      <div><div style="display:flex; justify-content:space-between; font-size:calc(10px * var(--fs-scale)); color:var(--ink-dim)"><span>Constituído</span><span>${fmtMoney2(current)}</span></div>${metricBar((current/max)*100,color)}</div>
    </div>`;
  };
  const clearBrokerCredentials = ()=>{
    brokerLogin='';
    investorPassword='';
    brokerServer='';
    plataforma='';
    alavCorretora='';
  };
  const clearPropRules = ()=>{
    propDailyDrawdown='';
    propMaxDrawdown='';
    propTrailingRule='';
    propTrailingDescription='';
    propProfitTarget='';
    propMinTradingDays='';
    propAbsenceRules='';
    restrictiveRuleAccepted=false;
  };
  const brokerCredentialFields = ()=>`
    <div class="card" style="margin:8px 0 14px; padding:14px 16px; box-shadow:none; border-color:var(--line); background:var(--panel-2)" id="obBrokerCreds">
      <h2 style="margin-bottom:10px">Dados de Conexão <span class="art">somente leitura</span></h2>
      <div class="params-grid" style="grid-template-columns:1fr 1fr; gap:0 14px">
        ${fld('obBrokerLogin','Login da Conta', brokerLogin, 'Ex.: 12345678')}
        <div class="field" style="margin-bottom:10px">
          <label for="obInvestorPassword">Senha de Investidor</label>
          <div class="leverage-input-row">
            <input type="password" id="obInvestorPassword" value="${esc(investorPassword)}" placeholder="Somente leitura — válida só nesta sessão, não é armazenada" autocomplete="off">
            <button type="button" class="leverage-trigger" id="obInvestorToggle" aria-expanded="false">Mostrar</button>
          </div>
        </div>
        ${fld('obBrokerServer','Servidor da Corretora', brokerServer, 'Ex.: Broker-Demo, Broker-Live, FTMO-Server, MetaQuotes-Demo')}
        ${platformField(plataforma)}
        ${leverageField(alavCorretora)}
      </div>
      <div class="leverage-note" style="margin-top:2px">Use apenas a senha de investidor/leitura. Nunca informe a senha master de operação.</div>
      <div class="modal-err" id="obBrokerCredErr">Preencha todos os dados de conexão da conta antes de escolher o sistema de risco.</div>
    </div>`;
  const trailingOptions=['Não existe','Trailing intraday','Trailing end-of-day','Trailing por equity','Trailing por balance','Outro'];
  const propRulesFields = ()=>`
    <div class="card" style="margin:8px 0 14px; padding:14px 16px; box-shadow:none; border-color:var(--line); background:var(--panel-2)" id="obPropRules">
      <h2 style="margin-bottom:10px">Regras Externas da Mesa Proprietária <span class="art">obrigatório</span></h2>
      <div class="params-grid" style="grid-template-columns:1fr 1fr; gap:0 14px">
        ${fld('obPropDaily','Drawdown Diário Permitido (%)', propDailyDrawdown, 'Ex.: 5%')}
        ${fld('obPropMax','Drawdown Máximo Permitido (%)', propMaxDrawdown, 'Ex.: 10%')}
        ${fld('obPropProfitTarget','Meta de Lucro da Avaliação (%)', propProfitTarget, 'Ex.: 10%')}
        ${fld('obPropMinDays','Número Mínimo de Dias Operados', propMinTradingDays, 'Ex.: 5', 'number')}
      </div>
      <div class="field" style="margin-bottom:10px">
        <label for="obPropTrailingRule">Regra de Trailing Drawdown</label>
        <select id="obPropTrailingRule">${trailingOptions.map(o=>`<option value="${esc(o)}" ${propTrailingRule===o?'selected':''}>${esc(o)}</option>`).join('')}</select>
      </div>
      <div class="field" id="obPropTrailingDescWrap" style="margin-bottom:10px; display:${(propTrailingRule && propTrailingRule!=='Não existe')?'flex':'none'}">
        <label for="obPropTrailingDesc">Descrição da regra de trailing</label>
        <textarea id="obPropTrailingDesc" rows="2" placeholder="Descreva brevemente a regra de trailing drawdown desta mesa.">${esc(propTrailingDescription)}</textarea>
      </div>
      <div class="field" style="margin-bottom:10px">
        <label for="obPropAbsence">Regras de Ausência</label>
        <textarea id="obPropAbsence" rows="2" placeholder="Ex.: conta expira após 30 dias sem operar; mínimo de 5 dias operados; ausência máxima de 14 dias.">${esc(propAbsenceRules)}</textarea>
      </div>
      <label style="display:flex; gap:10px; align-items:flex-start; color:var(--ink); font-size:calc(12.5px * var(--fs-scale)); cursor:pointer; margin-top:4px">
        <input type="checkbox" id="obPropRestrictive" style="margin-top:3px; width:auto" ${restrictiveRuleAccepted?'checked':''}>
        <span>Em caso de conflito entre o Estatuto JP Wealth e a regra da corretora/prop firm, prevalecerá a regra mais restritiva.</span>
      </label>
      <div class="modal-err" id="obPropRestrictiveErr">Confirme que, em caso de conflito, prevalecerá a regra mais restritiva.</div>
      <div class="modal-err" id="obPropRulesErr">Preencha as regras externas obrigatórias da mesa proprietária antes de escolher o sistema de risco.</div>
      <div class="expl leverage-note" style="margin-top:10px">As regras externas da mesa proprietária não substituem o Estatuto JP Wealth. Quando houver conflito, o painel deve considerar a regra mais restritiva.</div>
    </div>`;
  const reservePanelHTML=()=>{
    const r=reserveCalc();
    const fcrColor=r.fcrCoverage>=100?'var(--f1)':(r.fcrCoverage>=75?'var(--f2)':'var(--f4)');
    const feoColor=r.feoCoverage>=100?'var(--f1)':(r.feoCoverage>=75?'var(--f2)':'var(--f4)');
    const monthsClass=r.feoMonths>=12?'robusto':(r.feoMonths>=6?'regular':(r.feoMonths>=3?'insuficiente':'crítico'));
    const monthsColor=r.feoMonths>=12?'var(--violet)':(r.feoMonths>=6?'var(--f1)':(r.feoMonths>=3?'var(--f2)':'var(--f4)'));
    return `
      <div class="card" style="margin:0 0 14px; padding:14px 16px; box-shadow:none; border-color:${r.generalTone}; background:var(--panel)">
        <h2 style="margin-bottom:10px">Painel de Cobertura das Reservas <span class="art">atualização ao vivo</span></h2>
        <div class="status-banner" style="margin:0 0 12px; border-color:${r.generalTone}; background:var(--panel-2)">
          <div class="status-ico" style="color:${r.generalTone}">${r.hasDeficit?'⚠':'✓'}</div>
          <div><b style="color:${r.generalTone}">${r.generalStatus}</b><div class="expl" style="font-size:calc(11px * var(--fs-scale)); color:var(--ink-dim); margin-top:2px">FCR recompõe capital operacional. FEO preserva continuidade financeira e psicológica.</div></div>
        </div>
        <div class="metrics" style="grid-template-columns:repeat(3,minmax(0,1fr)); margin-bottom:12px">
          <div class="metric"><div class="k">Cobertura FCR</div><div class="v sm" style="color:${fcrColor}">${pctText(r.fcrCoverage)}</div>${metricBar(r.fcrCoverage,fcrColor)}<div class="sub">Capacidade de recomposição após drawdown máximo.</div></div>
          <div class="metric"><div class="k">Cobertura FEO</div><div class="v sm" style="color:${feoColor}">${pctText(r.feoCoverage)}</div>${metricBar(r.feoCoverage,feoColor)}<div class="sub">Estabilidade financeira contra pressão operacional.</div></div>
          <div class="metric"><div class="k">Meses cobertos pelo FEO</div><div class="v sm" style="color:${monthsColor}">${(r.feoMonths||0).toFixed(1).replace('.',',')} meses</div><div class="sub">Classificação: ${monthsClass}</div></div>
        </div>
        <div class="params-grid" style="grid-template-columns:1fr 1fr; gap:12px">
          <div class="card" style="margin:0; padding:12px; box-shadow:none; background:var(--panel-2)">
            <h2 style="font-size:calc(13px * var(--fs-scale)); margin-bottom:8px">FCR — Exigido vs Constituído</h2>
            ${compareBars(r.fcrReq,r.fcrCur,fcrColor)}
            <div style="font-size:calc(11px * var(--fs-scale)); color:${r.fcrDiff>=0?'var(--f1)':'var(--f4)'}; margin-top:8px; font-weight:700">${r.fcrDiff>=0?'Excedente':'Déficit'} do FCR: ${fmtMoney2(Math.abs(r.fcrDiff))}</div>
          </div>
          <div class="card" style="margin:0; padding:12px; box-shadow:none; background:var(--panel-2)">
            <h2 style="font-size:calc(13px * var(--fs-scale)); margin-bottom:8px">FEO — Exigido vs Constituído</h2>
            ${compareBars(r.feoReq,r.feoCur,feoColor)}
            <div style="font-size:calc(11px * var(--fs-scale)); color:${r.feoDiff>=0?'var(--f1)':'var(--f4)'}; margin-top:8px; font-weight:700">${r.feoDiff>=0?'Excedente':'Déficit'} do FEO: ${fmtMoney2(Math.abs(r.feoDiff))}</div>
          </div>
        </div>
        <details style="margin-top:12px"><summary style="cursor:pointer; font-weight:700; color:var(--ink)">Por que o FCR existe?</summary><p style="font-size:calc(12px * var(--fs-scale)); color:var(--ink-dim); line-height:1.6; margin-top:8px">O FCR é a reserva de reconstituição. Ele existe para recompor o capital operacional após atingimento do limite máximo de drawdown. Ele não deve ser usado para aumentar lote, sustentar tese perdedora ou financiar revenge trade.</p></details>
        <details style="margin-top:8px"><summary style="cursor:pointer; font-weight:700; color:var(--ink)">Por que o FEO existe?</summary><p style="font-size:calc(12px * var(--fs-scale)); color:var(--ink-dim); line-height:1.6; margin-top:8px">O FEO é a reserva de estabilidade. Ele reduz pressão emocional e financeira durante períodos ruins. Sem FEO, o operador tende a buscar renda imediata no mercado, aumentando risco de indisciplina.</p></details>
        <details style="margin-top:8px"><summary style="cursor:pointer; font-weight:700; color:var(--ink)">Qual a diferença entre FCR e FEO?</summary><p style="font-size:calc(12px * var(--fs-scale)); color:var(--ink-dim); line-height:1.6; margin-top:8px">FCR recompõe capital operacional. FEO sustenta a vida financeira e administrativa da estrutura. Um protege a conta; o outro protege a continuidade do operador e da estrutura.</p></details>
      </div>`;
  };
  const centralCashPanelHTML=()=>{
    const c=centralCashCalc();
    const fcrL=liquidityLabel('fcr',fcrLiquidity);
    const feoL=liquidityLabel('feo',feoLiquidity);
    const scoreColor=c.score>=90?'var(--violet)':(c.score>=70?'var(--f1)':(c.score>=40?'var(--f2)':'var(--f4)'));
    const segs=[
      ['Patrimonial',numVal(centralCashMainPct),'var(--violet)'],
      ['Operacional',numVal(centralCashAgilePct),'var(--f1)'],
      ['Liquidez',numVal(centralCashLiquidityPct),'var(--f2)'],
      ['Externos',numVal(centralCashExternalPct),'var(--f3)'],
      ['Outros',numVal(centralCashOtherPct),'var(--ink-faint)']
    ];
    const segBars=segs.filter(s=>s[1]>0).map(s=>`<div title="${s[0]} ${pctText(s[1])}" style="width:${Math.max(0,s[1])}%; background:${s[2]}; min-width:${s[1]>0?4:0}px"></div>`).join('');
    const segLegend=segs.map(s=>'<span><b style="color:'+s[2]+'">■</b> '+s[0]+' '+pctText(s[1])+'</span>').join('');
    const segEmpty='<div style="width:100%; background:var(--panel)"> </div>';
    return `
      <div class="card" style="margin:0 0 14px; padding:14px 16px; box-shadow:none; border-color:${c.tone}; background:var(--panel)">
        <h2 style="margin-bottom:10px">Mapa de Liquidez e Rastreabilidade <span class="art">atualização ao vivo</span></h2>
        <div class="status-banner" style="margin:0 0 12px; border-color:${c.tone}; background:var(--panel-2)">
          <div class="status-ico" style="color:${c.tone}">${centralCashStatus==='Não.'?'!':'✓'}</div>
          <div><b style="color:${c.tone}">${c.status}</b><div style="font-size:calc(11px * var(--fs-scale)); color:var(--ink-dim); margin-top:2px">Liquidez não é rentabilidade. Reserva existe primeiro para sobreviver.</div></div>
        </div>
        <div class="metrics" style="grid-template-columns:repeat(3,minmax(0,1fr)); margin-bottom:12px">
          <div class="metric"><div class="k">Score de Rastreabilidade</div><div class="v sm" style="color:${scoreColor}">${c.score}/100</div>${metricBar(c.score,scoreColor)}<div class="sub">Classificação: ${c.traceClass}</div></div>
          <div class="metric"><div class="k">Liquidez FCR</div><div class="v sm" style="color:${fcrL.color}">${fcrLiquidity||'—'}</div><div class="sub">${fcrL.label} · FCR ideal D+0/D+1</div></div>
          <div class="metric"><div class="k">Liquidez FEO</div><div class="v sm" style="color:${feoL.color}">${feoLiquidity||'—'}</div><div class="sub">${feoL.label} · FEO até D+2</div></div>
        </div>
        <div class="card" style="margin:0; padding:12px; box-shadow:none; background:var(--panel-2)">
          <h2 style="font-size:calc(13px * var(--fs-scale)); margin-bottom:8px">Composição do Caixa Central</h2>
          <div style="height:16px; display:flex; overflow:hidden; border-radius:999px; background:var(--line); border:1px solid var(--line)">${segBars||segEmpty}</div>
          <div style="display:flex; flex-wrap:wrap; gap:8px; margin-top:10px; font-size:calc(10px * var(--fs-scale)); color:var(--ink-dim)">${segLegend}</div>
          <div class="risk-note" id="obCentralCashSegAlert" style="display:${c.total>0&&!c.coherent?'block':'none'}; margin:10px 0 0; border-color:var(--f2); color:var(--ink-dim)">A segmentação declarada não soma 100%. Verifique se os percentuais representam toda a estrutura patrimonial.</div>
        </div>
        <details style="margin-top:12px"><summary style="cursor:pointer; font-weight:700; color:var(--ink)">Por que existe Caixa Central?</summary><p style="font-size:calc(12px * var(--fs-scale)); color:var(--ink-dim); line-height:1.6; margin-top:8px">Porque sem caixa centralizado não há rastreabilidade patrimonial. O operador pode confundir lucro, reserva, capital de risco e dinheiro pessoal.</p></details>
        <details style="margin-top:8px"><summary style="cursor:pointer; font-weight:700; color:var(--ink)">O que não deve acontecer?</summary><p style="font-size:calc(12px * var(--fs-scale)); color:var(--ink-dim); line-height:1.6; margin-top:8px">Não misturar FCR com margem. Não usar FEO para operação. Não retirar lucro sem registrar. Não transferir capital para corretora sem controle. Não tratar liquidez excedente como licença para operar mais.</p></details>
        <details style="margin-top:8px"><summary style="cursor:pointer; font-weight:700; color:var(--ink)">Qual é a diferença entre liquidez e retorno?</summary><p style="font-size:calc(12px * var(--fs-scale)); color:var(--ink-dim); line-height:1.6; margin-top:8px">Liquidez é disponibilidade. Retorno é rentabilidade. Reservas de segurança existem primeiro para sobreviver, não para maximizar rendimento.</p></details>
      </div>`;
  };
  const reservesFields = ()=>{
    const r=reserveCalc();
    const fcrBad=r.fcrStatus==='Insuficiente';
    const feoBad=r.feoStatus==='Insuficiente';
    return `
    <div class="card" style="margin:0; padding:14px 16px; box-shadow:none; border-color:var(--line); background:var(--panel-2)" id="obReservesCard">
      <h2 style="margin-bottom:10px">Reservas Segregadas — FCR e FEO <span class="art">governança patrimonial</span></h2>
      <div style="font-size:calc(12.5px * var(--fs-scale)); color:var(--ink-dim); line-height:1.6; margin-bottom:12px">
        As Reservas Segregadas são a defesa patrimonial da estrutura JP Wealth. O FCR protege a recomposição do capital operacional após atingimento do limite máximo de drawdown. O FEO protege a continuidade financeira da estrutura durante baixa rentabilidade, quarentena, interrupções ou pressão emocional. Essas reservas não autorizam aumento de risco, não ampliam limite operacional e não substituem o Estatuto.
      </div>
      <div id="obReservePanel">${reservePanelHTML()}</div>
      <div class="params-grid" style="grid-template-columns:1fr 1fr; gap:0 14px">
        <div class="field" style="margin-bottom:10px"><label for="obReserveMasterCapital">Capital nominal da Conta Mestre</label><input type="text" id="obReserveMasterCapital" value="${fmtMoney2(r.capital)}" readonly><span class="note">Preenchido automaticamente a partir de "Saldo de Início do Período", na etapa 01 Identificação.</span></div>
        <div class="field" style="margin-bottom:10px"><label>FCR mínimo exigido</label><input type="text" id="obReserveFcrRequired" value="${fmtMoney2(r.fcrReq)}" readonly><span class="note">15% × capital nominal da Conta Mestre.</span></div>
        <div class="field" style="margin-bottom:10px"><label for="obReserveFcrCurrent">FCR atualmente constituído</label><input type="number" step="0.01" id="obReserveFcrCurrent" value="${esc(reserveFcrCurrent)}" placeholder="0.00"><span class="note">Valor separado para Fundo de Contingência e Reconstituição.</span></div>
        <div class="field" style="margin-bottom:10px"><label>Status do FCR</label><input type="text" id="obReserveFcrStatus" value="${r.fcrStatus}" readonly style="color:${fcrBad?'var(--f4)':'var(--f1)'}; font-weight:800"></div>
        <div class="field" style="margin-bottom:10px"><label for="obReserveMonthlyExpenses">Despesas mensais da estrutura</label><input type="number" step="0.01" id="obReserveMonthlyExpenses" value="${esc(reserveMonthlyExpenses)}" placeholder="0.00"><span class="note">Inclua despesas pessoais, operacionais e administrativas relevantes.</span></div>
        <div class="field" style="margin-bottom:10px"><label>FEO mínimo exigido</label><input type="text" id="obReserveFeoRequired" value="${fmtMoney2(r.feoReq)}" readonly><span class="note">Despesas mensais × 6.</span></div>
        <div class="field" style="margin-bottom:10px"><label for="obReserveFeoCurrent">FEO atualmente constituído</label><input type="number" step="0.01" id="obReserveFeoCurrent" value="${esc(reserveFeoCurrent)}" placeholder="0.00"><span class="note">Valor separado para Fundo de Estabilidade Operacional.</span></div>
        <div class="field" style="margin-bottom:10px"><label>Status do FEO</label><input type="text" id="obReserveFeoStatus" value="${r.feoStatus}" readonly style="color:${feoBad?'var(--f4)':'var(--f1)'}; font-weight:800"></div>
      </div>
      <div class="risk-note" id="obReserveFcrAlert" style="display:${fcrBad?'block':'none'}; margin:0 0 10px; border-color:var(--f4); color:var(--ink-dim)">FCR insuficiente. O Fundo de Contingência e Reconstituição está abaixo do mínimo estatutário de 15% do capital nominal da Conta Mestre. Enquanto não recomposto, o sistema deve tratar a estrutura como patrimonialmente vulnerável.</div>
      <div class="risk-note" id="obReserveFeoAlert" style="display:${feoBad?'block':'none'}; margin:0 0 10px; border-color:var(--f4); color:var(--ink-dim)">FEO insuficiente. O Fundo de Estabilidade Operacional está abaixo de 6 meses de despesas. Isso aumenta o risco de pressão financeira, decisões emocionais, necessidade de retirada prematura e quebra de disciplina.</div>
      <div class="risk-note" id="obReserveDeficitAlert" style="display:${r.hasDeficit?'block':'none'}; margin:0 0 10px; border-color:var(--f2); color:var(--ink-dim)">ATENÇÃO: reservas segregadas abaixo do mínimo estatutário. A operação pode continuar apenas com ciência formal, mas a estrutura está mais vulnerável a drawdown, quarentena, baixa rentabilidade e pressão emocional.</div>
      <label style="display:flex; gap:10px; align-items:flex-start; color:var(--ink); font-size:calc(12.5px * var(--fs-scale)); cursor:pointer; margin:8px 0">
        <input type="checkbox" id="obReserveSegregation" style="margin-top:3px; width:auto" ${reserveSegregationAccepted?'checked':''}>
        <span>Declaro que FCR e FEO são reservas segregadas, não são margem operacional, não autorizam aumento de risco e não devem ser transferidos para corretoras, prop firms ou operações sem deliberação formal.</span>
      </label>
      <label id="obReserveDeficitWrap" style="display:${r.hasDeficit?'flex':'none'}; gap:10px; align-items:flex-start; color:var(--ink); font-size:calc(12.5px * var(--fs-scale)); cursor:pointer; margin:8px 0">
        <input type="checkbox" id="obReserveDeficitAccepted" style="margin-top:3px; width:auto" ${reserveDeficitAccepted?'checked':''}>
        <span>Declaro ciência de que as reservas segregadas estão abaixo do mínimo estatutário e que isso aumenta o risco estrutural do período.</span>
      </label>
      <div class="field" style="margin-bottom:10px"><label for="obReserveNotes">Observações sobre reservas</label><textarea id="obReserveNotes" rows="3" placeholder="Ex.: reserva em formação, déficit temporário, plano de recomposição, localização da reserva, observações de liquidez.">${esc(reserveNotes)}</textarea></div>
      <div class="modal-err" id="obReserveErr">Complete a seção de Reservas Segregadas antes de prosseguir.</div>
    </div>`;
  };
  const centralCashFields = ()=>{
    const custodyOptions=['Interactive Brokers / IBKR','Conta bancária institucional','Conta bancária pessoal segregada','USDT custodial','Carteira própria / self-custody','Outra'];
    const liquidityOptions=['D+0','D+1','D+2','Acima de D+2','Não definido'];
    const ledgerOptions=['Livro-razão patrimonial ativo','Planilha de caixa ativa','Planilha de Caixa Institucional ativa','Registro parcial','Ainda não existe registro formal'];
    const cashNo=centralCashStatus==='Não.';
    const custodyOther=centralCashCustody==='Outra';
    const fcrSlow=liquidityTooSlow('fcr',fcrLiquidity);
    const feoSlow=liquidityTooSlow('feo',feoLiquidity);
    const ledgerWeak=cashLedgerStatus==='Ainda não existe registro formal'||cashLedgerStatus==='Registro parcial';
    const segTotal=cashSegTotal();
    return `
    <div class="card" style="margin:0; padding:14px 16px; box-shadow:none; border-color:var(--line); background:var(--panel-2)" id="obCentralCashCard">
      <h2 style="margin-bottom:10px">Caixa Central e Liquidez Institucional <span class="art">rastreabilidade patrimonial</span></h2>
      <div style="font-size:calc(12.5px * var(--fs-scale)); color:var(--ink-dim); line-height:1.6; margin-bottom:12px">O Caixa Central é o núcleo de rastreabilidade patrimonial da JP Wealth. Ele impede mistura entre capital operacional, reservas segregadas, investimentos externos e recursos pessoais. Toda movimentação relevante deve ser registrada, classificada e reconciliada.</div>
      <div id="obCentralCashPanel">${centralCashPanelHTML()}</div>
      <div class="params-grid" style="grid-template-columns:1fr 1fr; gap:0 14px">
        <div class="field" style="margin-bottom:10px"><label for="obCentralCashStatus">Existe Caixa Central definido?</label><select id="obCentralCashStatus"><option value="">Selecione...</option>${optList(['Sim.','Em implantação.','Não.'], centralCashStatus)}</select></div>
        <div class="field" style="margin-bottom:10px"><label for="obCentralCashCustody">Custódia principal do Caixa Central</label><select id="obCentralCashCustody"><option value="">Selecione...</option>${optList(custodyOptions, centralCashCustody)}</select></div>
        <div class="field" id="obCentralCashCustodyOtherWrap" style="margin-bottom:10px; display:${custodyOther?'flex':'none'}"><label for="obCentralCashCustodyOther">Outra custódia</label><input type="text" id="obCentralCashCustodyOther" value="${esc(centralCashCustodyOther)}" placeholder="Descreva a custódia"></div>
        <div class="field" style="margin-bottom:10px"><label for="obFcrLiquidity">Liquidez do FCR</label><select id="obFcrLiquidity"><option value="">Selecione...</option>${optList(liquidityOptions, fcrLiquidity)}</select></div>
        <div class="field" style="margin-bottom:10px"><label for="obFeoLiquidity">Liquidez do FEO</label><select id="obFeoLiquidity"><option value="">Selecione...</option>${optList(liquidityOptions, feoLiquidity)}</select></div>
        <div class="field" style="margin-bottom:10px"><label for="obCashLedgerStatus">Registro das movimentações patrimoniais</label><select id="obCashLedgerStatus"><option value="">Selecione...</option>${optList(ledgerOptions, cashLedgerStatus)}</select></div>
      </div>
      <div class="ql" style="font-size:calc(12px * var(--fs-scale)); margin:4px 0 8px">Segmentação do Caixa Central <span class="art" style="font-family:var(--mono); font-size:calc(10px * var(--fs-scale))">percentual ou referência interna</span></div>
      <div class="params-grid" style="grid-template-columns:repeat(auto-fit,minmax(130px,1fr)); gap:0 10px">
        ${fld('obCentralCashMainPct','Caixa patrimonial principal',centralCashMainPct,'%', 'number')}
        ${fld('obCentralCashAgilePct','Caixa operacional ágil',centralCashAgilePct,'%', 'number')}
        ${fld('obCentralCashLiquidityPct','Liquidez excedente',centralCashLiquidityPct,'%', 'number')}
        ${fld('obCentralCashExternalPct','Investimentos externos',centralCashExternalPct,'%', 'number')}
        ${fld('obCentralCashOtherPct','Outros',centralCashOtherPct,'%', 'number')}
      </div>
      <div class="note" id="obCentralCashSegNote" style="display:block; margin:-4px 0 10px">Soma declarada: ${segTotal.toFixed(1).replace('.',',')}%. Não é obrigatório fechar 100% se a estrutura estiver em implantação.</div>
      <div class="risk-note" id="obCentralCashNoAlert" style="display:${cashNo?'block':'none'}; margin:0 0 10px; border-color:var(--f4); color:var(--ink-dim)">Sem Caixa Central definido, a rastreabilidade patrimonial fica fragilizada. A ausência de Caixa Central aumenta o risco de mistura entre reserva, capital operacional, investimentos externos e retiradas pessoais.</div>
      <div class="risk-note" id="obFcrLiquidityAlert" style="display:${fcrSlow?'block':'none'}; margin:0 0 10px; border-color:var(--f2); color:var(--ink-dim)">O FCR deve ter liquidez imediata, preferencialmente D+0/D+1. Liquidez superior reduz a capacidade de recomposição rápida após drawdown máximo.</div>
      <div class="risk-note" id="obFeoLiquidityAlert" style="display:${feoSlow?'block':'none'}; margin:0 0 10px; border-color:var(--f2); color:var(--ink-dim)">O FEO deve preservar liquidez suficiente para continuidade financeira da estrutura. Liquidez acima de D+2 deve ser justificada.</div>
      <div class="risk-note" id="obCashLedgerAlert" style="display:${ledgerWeak?'block':'none'}; margin:0 0 10px; border-color:var(--f2); color:var(--ink-dim)">Movimentações sem livro-razão patrimonial reduzem rastreabilidade, aumentam risco contábil e dificultam auditoria.</div>
      <label id="obCentralCashNoAcceptedWrap" style="display:${cashNo?'flex':'none'}; gap:10px; align-items:flex-start; color:var(--ink); font-size:calc(12.5px * var(--fs-scale)); cursor:pointer; margin:8px 0">
        <input type="checkbox" id="obCentralCashNoAccepted" style="margin-top:3px; width:auto" ${centralCashNoAccepted?'checked':''}>
        <span>Declaro ciência de que iniciar o período sem Caixa Central definido fragiliza a rastreabilidade patrimonial.</span>
      </label>
      <label style="display:flex; gap:10px; align-items:flex-start; color:var(--ink); font-size:calc(12.5px * var(--fs-scale)); cursor:pointer; margin:8px 0">
        <input type="checkbox" id="obCentralCashPolicy" style="margin-top:3px; width:auto" ${centralCashPolicyAccepted?'checked':''}>
        <span>Declaro que aportes, saques, transferências entre corretoras, retornos de investimentos, recomposição de reservas e distribuições devem passar pelo Caixa Central ou ser registrados formalmente.</span>
      </label>
      <div class="field" style="margin-bottom:10px"><label for="obCentralCashNotes">Observações sobre Caixa Central</label><textarea id="obCentralCashNotes" rows="3" placeholder="Justificativas de liquidez, ausência de Caixa Central, registro parcial, localização do caixa e observações de auditoria.">${esc(centralCashNotes)}</textarea></div>
      <div class="modal-err" id="obCentralCashErr">Complete a seção de Caixa Central antes de prosseguir.</div>
    </div>`;
  };
  const equityProtectorFields = ()=>`
    <div class="card" style="margin:18px 0 0; padding:14px 16px; box-shadow:none; border-color:var(--line); background:var(--panel-2)" id="obEquityProtectorCard">
      <h2 style="margin-bottom:10px">Equity Protector / Proteção Externa de Conta <span class="art">controle operacional</span></h2>
      ${!canShowEquityProtectorStep()?`
        <div class="risk-note" style="margin:0">Preencha primeiro os dados da conta, corretora/mesa proprietária e perfil de risco para configurar a Proteção Externa de Conta.</div>
      `:`
      <div style="font-size:calc(12.5px * var(--fs-scale)); color:var(--ink-dim); line-height:1.6">
        <p style="margin-bottom:8px">Um Equity Protector é uma camada externa de proteção da conta. Ele monitora equity, saldo, drawdown, lucro/prejuízo flutuante e limites definidos pelo operador. Ao atingir uma regra, pode emitir alerta, bloquear novas operações, fechar posições abertas ou impedir que a conta ultrapasse limites críticos de perda.</p>
        <p style="margin-bottom:8px">Essa proteção funciona como freio operacional externo. Não substitui o Estatuto JP Wealth, o gerenciamento de risco nem a disciplina do operador, mas reduz risco de erro humano, tilt emocional, falha de execução, excesso de exposição e violação de drawdown.</p>
        <p style="margin-bottom:10px"><b style="color:var(--ink)">Exemplos:</b> Traders Connect; Account Protector; KT Equity Protector; Equity Guard; ou ferramenta equivalente compatível com MetaTrader 4, MetaTrader 5, cTrader ou plataforma usada pela conta.</p>
        <div class="risk-note" style="margin:0 0 12px; border-color:var(--f2); color:var(--ink-dim)">A JP Wealth não deve tratar o Equity Protector como garantia absoluta. A ferramenta depende de configuração correta, conexão, compatibilidade, latência, execução e disponibilidade técnica. O operador continua responsável por validar a configuração, testar e confirmar que os limites externos coincidem com o Estatuto e com as regras da corretora ou prop firm.</div>
      </div>
      <div class="params-grid" style="grid-template-columns:1fr 1fr; gap:0 14px">
        <div class="field" style="margin-bottom:10px"><label for="obEpStatus">Você utilizará Equity Protector / Proteção Externa de Conta neste período?</label><select id="obEpStatus"><option value="">Selecione...</option>${optList(epStatusOptions, epStatus)}</select></div>
        <div class="field" style="margin-bottom:10px"><label for="obEpPlatform">Plataforma escolhida</label><select id="obEpPlatform"><option value="">Selecione...</option>${optList(epPlatformOptions, epPlatform)}</select></div>
        <div class="field" id="obEpOtherWrap" style="margin-bottom:10px; display:${epPlatform==='Outra.'?'flex':'none'}"><label for="obEpOther">Nome da plataforma/ferramenta utilizada</label><input type="text" id="obEpOther" value="${esc(epPlatformOther)}" placeholder="Nome da ferramenta"></div>
        <div class="field" style="margin-bottom:10px"><label>Drawdown máximo estatutário do período</label><input type="text" id="obEpMax" value="${esc(fmtPct(getActiveRiskProfile(profSel||'base').mdd))}" disabled><span class="note">Valor calculado automaticamente a partir do perfil de risco escolhido.</span></div>
      </div>
      <div id="obEpPropWrap" style="display:${institutionType==='prop'?'block':'none'}; margin-top:4px">
        <div class="ql" style="font-size:calc(12px * var(--fs-scale)); margin:4px 0 8px">Limite de perda diária da mesa proprietária</div>
        <div class="risk-note" style="margin:0 0 10px">Mesas proprietárias frequentemente possuem limite de perda diária, limite de equity ou regra de violação intradiária. Esse limite deve ser registrado para que o programa alerte o operador antes de aproximação ou violação.</div>
        <div class="params-grid" style="grid-template-columns:1fr 1fr; gap:0 14px">
          <div class="field" style="margin-bottom:10px"><label for="obEpPropDailyEnabled">Existe limite de perda diária?</label><select id="obEpPropDailyEnabled"><option value="">Selecione...</option>${optList(epPropDailyEnabledOptions, epPropDailyEnabled)}</select></div>
          ${fld('obEpDaily','Valor do limite de perda diária', epDailyLimit, 'Ex.: 2% ao dia ou US$ 200')}
          <div class="field" style="margin-bottom:10px"><label for="obEpPropDailyBase">Base do cálculo</label><select id="obEpPropDailyBase"><option value="">Selecione...</option>${optList(epPropDailyBaseOptions, epPropDailyBase)}</select></div>
          <div class="field" style="margin-bottom:10px"><label for="obEpPropDailyNotes">Observações sobre a regra da mesa</label><textarea id="obEpPropDailyNotes" rows="2" placeholder="Descreva a regra externa da mesa proprietária.">${esc(epPropDailyNotes)}</textarea></div>
        </div>
      </div>
      <label style="display:flex; gap:10px; align-items:flex-start; color:var(--ink); font-size:calc(12.5px * var(--fs-scale)); cursor:pointer; margin-top:4px">
        <input type="checkbox" id="obEpRestrictive" style="margin-top:3px; width:auto" ${epRestrictiveAccepted?'checked':''}>
        <span>Declaro ciência de que, em caso de conflito entre o Estatuto JP Wealth, as regras da corretora/prop firm e a configuração do Equity Protector, deverá prevalecer sempre a regra mais restritiva.</span>
      </label>
      <div id="obEpNoConfigWrap" style="display:${(epStatus==='Não vou utilizar.'||epStatus==='Ainda vou configurar antes de iniciar o período.')?'block':'none'}; margin-top:10px">
        <div class="risk-note" id="obEpNoConfigAlert" style="margin:0 0 8px; color:var(--f4); border-color:var(--f4)">ATENÇÃO: você está iniciando ou mantendo um período operacional sem Equity Protector externo. Isso aumenta o risco de violação de drawdown, erro humano, tilt emocional, excesso de exposição, falha de disciplina e perda acima do planejado. A ausência de proteção externa não autoriza flexibilização do Estatuto JP Wealth.</div>
        <label style="display:flex; gap:10px; align-items:flex-start; color:var(--ink); font-size:calc(12.5px * var(--fs-scale)); cursor:pointer">
          <input type="checkbox" id="obEpNoConfigAccepted" style="margin-top:3px; width:auto" ${epNoConfigAccepted?'checked':''}>
          <span>Declaro ciência de que estou operando sem camada externa de proteção e que a responsabilidade pelo controle manual de risco é integralmente minha.</span>
        </label>
      </div>
      <div class="field" style="margin-top:10px"><label for="obEpNotes">Observações</label><textarea id="obEpNotes" rows="3" placeholder="Descreva limitações, pendências, configurações específicas ou riscos observados.">${esc(epNotes)}</textarea></div>
      <div class="risk-note" id="obEpPropAlert" style="display:${institutionType==='prop'&&(epStatus==='Não vou utilizar.'||epStatus==='Ainda vou configurar antes de iniciar o período.')?'block':'none'}; margin-top:10px; color:var(--f4); border-color:var(--f4)">Conta de prop firm/mesa proprietária possui regras externas de drawdown e violação. É altamente recomendável configurar um Equity Protector antes de iniciar o período.</div>
      <div class="risk-note" style="margin-top:10px">
        <b style="color:var(--ink)">Como configurar, em linhas gerais:</b><br>
        1. Criar conta na plataforma escolhida, como Traders Connect ou ferramenta equivalente.<br>
        2. Conectar a conta de trading ou plataforma utilizada.<br>
        3. Definir limites compatíveis com o Estatuto JP Wealth.<br>
        4. Configurar ações automáticas: alerta, bloqueio, fechamento de posições ou restrição de novas ordens.<br>
        5. Testar em conta demo ou com lote mínimo.<br>
        6. Confirmar que os limites configurados são iguais ou mais restritivos que os limites do período.
      </div>
      <div class="modal-err" id="obEpErr">Revise a seção Equity Protector antes de continuar.</div>
      `}
    </div>`;
  const platformField=(val)=>`<div class="field leverage-field" id="obPlatformWrap" style="margin-bottom:10px">
    <label for="obPlataforma">Plataforma</label>
    <div class="leverage-input-row">
      <input type="text" id="obPlataforma" value="${esc(normalizePlatformName(val||''))}" placeholder="MetaTrader 5" autocomplete="off">
      <button type="button" class="leverage-trigger" id="obPlatformTrigger" aria-expanded="false">Plataformas</button>
    </div>
    <div class="leverage-panel" id="obPlatformPanel">
      <div class="leverage-presets">
        ${platformPresets.map(v=>`<button type="button" class="preset-btn" data-platformpreset="${esc(v)}">${esc(v)}</button>`).join('')}
      </div>
      <div class="leverage-note">Selecione uma plataforma homologada ou digite manualmente outro nome, se necessário.</div>
    </div>
  </div>`;
  const periodDateField=(val)=>`<div class="field leverage-field" id="obDateWrap" style="margin-bottom:10px">
    <label for="obData">Data de início do período</label>
    <input type="date" id="obData" value="${esc(val||'')}">
    <div class="leverage-panel" id="obDatePanel">
      <div style="font-weight:800; font-size:calc(12px * var(--fs-scale)); color:var(--ink); margin-bottom:8px">Período estatutário</div>
      <div class="expl leverage-note" style="margin-bottom:12px">O período operacional é o intervalo de referência utilizado para organizar o ciclo contábil, metas, drawdown, auditoria e avaliação de desempenho. A data inicial define a âncora do ciclo; a data final projetada é calculada a partir dessa referência.</div>
      <div class="metrics" style="grid-template-columns:1fr; gap:8px">
        <div class="metric" style="padding:10px 12px"><div class="k">Início selecionado</div><div class="v sm" id="obDateStartTxt">—</div></div>
        <div class="metric" style="padding:10px 12px"><div class="k">Final projetado</div><div class="v sm" id="obDateEndTxt">—</div><div class="sub">Base: ciclo anual · Art. 3.4</div></div>
      </div>
      <div class="expl leverage-note" style="margin-top:12px; margin-bottom:0">A projeção organiza o ciclo operacional. Ela não altera limites de risco nem autoriza aumento de exposição.</div>
    </div>
  </div>`;
  const leverageField=(val)=>`<div class="field leverage-field" id="obAlavWrap" style="margin-bottom:10px">
    <label for="obAlav">Alavancagem da corretora</label>
    <div class="leverage-input-row">
      <input type="text" id="obAlav" value="${esc(val||'')}" placeholder="1:500" autocomplete="off">
      <button type="button" class="leverage-trigger" id="obAlavTrigger" aria-expanded="false">Opções</button>
    </div>
    <div class="leverage-panel" id="obAlavPanel">
      <div class="leverage-presets">
        ${leveragePresets.map(v=>`<button type="button" class="preset-btn" data-levpreset="${v}">${v}</button>`).join('')}
      </div>
      <div class="leverage-note">A alavancagem disponível da corretora não autoriza aumento de exposição real. A exposição continua limitada pelo Estatuto JP Wealth.</div>
      <button type="button" class="leverage-explain-btn" id="obLeverageExplainToggle" aria-expanded="false">Ver explicação sobre alavancagem</button>
      <div id="obLeverageExplain" style="display:none">${leverageEducationHTML({interactive:true})}</div>
    </div>
  </div>`;
  box.innerHTML=`
    <h3>📋 ${isEditMode?'Formulário de Início — Período Atual':'Início de Período — Parâmetros da Conta'}</h3>
    <div class="modal-sub">${isEditMode?'Visualize ou ajuste os dados salvos no início deste período. Salvar aqui não reinicia o ciclo operacional.':'Primeiro ato do ciclo: registre a estrutura antes da primeira ordem. Tudo fica visível em ⚙ Configurações.'}</div>
    <div class="onb-shell">
      <div class="onb-main">
        <section class="onb-step active" data-onbstep="ident">
          <div class="params-grid" style="grid-template-columns:1fr 1fr; gap:0 14px">
            ${fld('obOperador','Operador (gestor)', ob.operador||'', 'Preencher nome')}
            ${fld('obSupervisor','Supervisor(a)', ob.supervisor||'', 'Preencher nome')}
            ${periodDateField(isEditMode?(S.params.inicio||todayISO()):'')}
            ${fld('obSaldo','Saldo de início do período ($)', isEditMode?(S.params.saldoIni||''):'', '10000','number', 'Saldo da Conta Mestre no momento de início deste período operacional. Esse valor funciona como a base nominal de referência para os cálculos de risco, drawdown, metas e reservas do período. Ele não representa o saldo atual após lucros ou prejuízos. O Capital Nominal da Conta Mestre exibido na etapa 04 Reservas é preenchido automaticamente a partir deste valor.')}
            <div class="field" style="margin-bottom:10px">
              <label for="obMoedaBase">Moeda-base da conta</label>
              <select id="obMoedaBase">${accountCurrencyOptions(ob.moedaBase||'USD')}</select>
            </div>
          </div>
        </section>
        <section class="onb-step" data-onbstep="instit">
          <div class="ql" style="font-size:calc(13px * var(--fs-scale)); margin:6px 0 8px">Você irá trabalhar com corretora ou mesa proprietária? <span class="art" style="font-family:var(--mono);font-size:calc(10px * var(--fs-scale));color:var(--ink-faint)">somente instituições parceiras</span></div>
          <div id="obInstitutionTypes" style="display:flex; gap:8px; flex-wrap:wrap; margin-bottom:12px"></div>
          <div id="obBrokers" style="margin-bottom:16px"></div>
          <div id="obBrokerCredWrap"></div>
          <div id="obPropRulesWrap"></div>
          <div class="modal-err" id="obBrokerErr">Selecione a corretora/prop firm antes de prosseguir.</div>
        </section>
        <section class="onb-step" data-onbstep="risk">
          <div id="obRiskStepWrap"></div>
        </section>
        <section class="onb-step" data-onbstep="reserves">
          <div id="obReservesStepWrap"></div>
        </section>
        <section class="onb-step" data-onbstep="cash">
          <div id="obCentralCashStepWrap"></div>
        </section>
        <section class="onb-step" data-onbstep="protect">
          <div id="obEquityProtectorWrap"></div>
        </section>
        <section class="onb-step" data-onbstep="database">
          <div class="card" style="margin:0 0 14px; padding:14px 16px; box-shadow:none">
            <h2 style="margin-bottom:10px">🗄 Responsabilidade sobre a base de dados <span class="art">obrigatório</span></h2>
            <div style="font-size:calc(12.5px * var(--fs-scale)); color:var(--ink-dim); line-height:1.6">
              <p style="margin-bottom:8px">A base de dados do JP Wealth contém informações essenciais para o funcionamento e histórico do sistema.</p>
              <p style="margin-bottom:8px">O armazenamento, preservação e realização de cópias de segurança desta base são de responsabilidade do usuário. <b style="color:var(--ink)">O JP Wealth não deve ser considerado o único mecanismo de armazenamento ou backup dos dados.</b></p>
              <p style="margin-bottom:10px">Recomenda-se manter cópias periódicas da base em localização segura e independente.</p>
              <label style="display:flex; gap:10px; align-items:flex-start; color:var(--ink); font-size:calc(12.5px * var(--fs-scale)); cursor:pointer">
                <input type="checkbox" id="obDbResp" style="margin-top:3px; width:auto" ${isEditMode&&S.dataGovernance&&S.dataGovernance.responsibility&&S.dataGovernance.responsibility.accepted?'checked':''}>
                <span>Li e compreendo minha responsabilidade pelo armazenamento e backup da base de dados.</span>
              </label>
              <div class="modal-err" id="obDbRespErr">O aceite do termo de responsabilidade é obrigatório para concluir a configuração inicial.</div>
            </div>
          </div>
          <div class="card" style="margin:0; padding:14px 16px; box-shadow:none">
            <h2 style="margin-bottom:10px">Local de armazenamento da base <span class="art">opcional nesta etapa</span></h2>
            <div id="obDgFolderSlot" style="font-size:calc(12.5px * var(--fs-scale)); color:var(--ink-dim); line-height:1.6"></div>
          </div>
        </section>
        <section class="onb-step" data-onbstep="consent">
          <div class="card" style="margin:0; padding:14px 16px; border-color:var(--f4); background:var(--f4-bg); box-shadow:none">
            <h2 style="margin-bottom:10px; color:var(--f4)">🔒 Termo de Consentimento <span class="art" style="color:var(--f4)">obrigatório</span></h2>
            <div style="font-size:calc(12.5px * var(--fs-scale)); color:var(--ink-dim); line-height:1.6">
              <p style="margin-bottom:8px"><b style="color:var(--ink)">JP Wealth Management System</b> · Estatuto Operacional e Gestão de Risco · <b style="color:var(--ink)">Versão 10.0</b> · Documento <b style="color:var(--ink)">JPW-GOV-001</b>.</p>
              <p style="margin-bottom:10px">Antes de confirmar, revise os dados preenchidos acima. Ao iniciar ou reiniciar o período, o operador declara ciência de que as decisões do painel devem respeitar as diretrizes do Estatuto V10.0, incluindo preservação de capital, disciplina operacional, limites de risco e protocolos de auditoria.</p>
              <button type="button" class="reset-btn" id="obEstatutoToggle" style="color:var(--f4); border-color:var(--f4); margin-bottom:10px">▸ Ler o Estatuto V10.0 (texto completo, 34 páginas)</button>
              <div id="obEstatutoReader" style="display:none; max-height:340px; overflow-y:auto; background:var(--panel-2); border:1px solid var(--line); border-radius:8px; padding:12px 14px; margin-bottom:12px; white-space:pre-wrap; font-size:calc(11.5px * var(--fs-scale)); line-height:1.55; color:var(--ink-dim)"></div>
              <label style="display:flex; gap:10px; align-items:flex-start; color:var(--ink); font-size:calc(12.5px * var(--fs-scale)); cursor:pointer">
                <input type="checkbox" id="obConsent" style="margin-top:3px; width:auto" ${isEditMode&&ob.consentAccepted?'checked':''}>
                <span>Li integralmente o Estatuto JP Wealth V10.0 e concordo com suas diretrizes.</span>
              </label>
              <div style="font-size:calc(10.5px * var(--fs-scale)); color:var(--f4); margin-top:6px; font-weight:600">⚠ Você deve aceitar para continuar.</div>
              <div class="modal-err" id="obConsentErr">O aceite do Termo de Consentimento é obrigatório para iniciar ou reiniciar o período.</div>
            </div>
          </div>
        </section>
        <div class="onb-step-nav">
          <button type="button" class="modal-btn cancel" id="obStepPrev">Anterior</button>
          <button type="button" class="modal-btn confirm" id="obStepNext">Próxima</button>
        </div>
        <div class="modal-actions">
          <button class="modal-btn confirm" id="modalConfirm">${isEditMode?'Salvar alterações':'Iniciar período'}</button>
        </div>
        <div id="obSummaryModalHost"></div>
      </div>
      <aside class="onb-rail" aria-label="Etapas do Formulário de Início">
        <button type="button" class="onb-tab active" data-onbtab="ident"><span class="idx">01</span>Identificação</button>
        <button type="button" class="onb-tab" data-onbtab="instit"><span class="idx">02</span>Instituição</button>
        <button type="button" class="onb-tab" data-onbtab="risk"><span class="idx">03</span>Risco</button>
        <button type="button" class="onb-tab" data-onbtab="reserves"><span class="idx">04</span>Reservas</button>
        <button type="button" class="onb-tab" data-onbtab="cash"><span class="idx">05</span>Caixa Central</button>
        <button type="button" class="onb-tab" data-onbtab="protect"><span class="idx">06</span>Proteção</button>
        <button type="button" class="onb-tab" data-onbtab="database"><span class="idx">07</span>Base de Dados</button>
        <button type="button" class="onb-tab" data-onbtab="consent"><span class="idx">08</span>Consentimento</button>
        <div class="onb-progress"><i id="onbProgressBar"></i></div>
        <div class="onb-progress-cap"><span>Completude</span><b id="onbProgressCap">0/8</b></div>
      </aside>
    </div>
    `;
  const onbSteps=ONBOARDING_STEPS.map(s=>s.key);
  let onbStep=ONBOARDING_STEPS.some(s=>s.key===initialStep)?initialStep:'ident';
  // Status resumido por etapa (rail) — espelha as MESMAS condições dos validate*(),
  // sem alertas e sem gate: quem decide continua sendo a validação no confirmar.
  function getOnboardingStepStatus(step){
    switch(step){
      case 'ident': {
        const saldoOk=parseFloat(($('obSaldo')&&$('obSaldo').value)||'')>0;
        const dataOk=isEditMode || !!($('obData')&&$('obData').value);
        return (saldoOk&&dataOk)?'complete':'pending';
      }
      case 'instit': {
        if(!hasSelectedInstitution()) return 'pending';
        if(!hasCompleteConnectionData()) return 'warning';
        if(!hasCompletePropRules()) return 'warning';
        return 'complete';
      }
      case 'risk':
        if(!canShowRiskProfileStep()) return 'pending';
        if(!profSel) return 'warning';
        return riskProfileAccepted?'complete':'warning';
      case 'reserves': {
        if(!String(reserveFcrCurrent||'').trim() || !String(reserveMonthlyExpenses||'').trim()
          || !String(reserveFeoCurrent||'').trim() || !reserveSegregationAccepted) return 'pending';
        const r=reserveCalc();
        if(r.hasDeficit && !reserveDeficitAccepted) return 'critical';
        return r.hasDeficit?'warning':'complete';
      }
      case 'cash': {
        if(!centralCashStatus||!centralCashCustody||!fcrLiquidity||!feoLiquidity||!cashLedgerStatus||!centralCashPolicyAccepted) return 'pending';
        if(centralCashStatus==='Não.') return centralCashNoAccepted?'warning':'critical';
        if(centralCashStatus==='Em implantação.') return 'warning';
        return 'complete';
      }
      case 'protect': {
        if(!epStatus||!epRestrictiveAccepted) return 'pending';
        if(epStatus==='Ainda vou configurar antes de iniciar o período.') return 'critical';
        if(epStatus==='Não vou utilizar.') return epNoConfigAccepted?'warning':'critical';
        return 'complete';
      }
      case 'database':
        return ($('obDbResp')&&$('obDbResp').checked)?'complete':'pending';
      case 'consent':
        return ($('obConsent')&&$('obConsent').checked)?'complete':'pending';
    }
    return 'pending';
  }
  function paintOnboardingRailStatus(){
    const MARK={complete:'✓',warning:'!',critical:'✕',pending:'·'};
    let done=0, total=0;
    box.querySelectorAll('[data-onbtab]').forEach(el=>{
      const st=getOnboardingStepStatus(el.dataset.onbtab);
      total++; if(st==='complete') done++;
      el.classList.remove('mc-step-complete','mc-step-warning','mc-step-critical','mc-step-pending');
      el.classList.add('mc-step-'+st);
      let dot=el.querySelector('.mc-step-dot');
      if(!dot){ dot=document.createElement('span'); dot.className='mc-step-dot'; el.appendChild(dot); }
      dot.textContent=MARK[st];
    });
    // Barra de completude do setup — leitura agregada dos mesmos status, sem regra nova.
    const bar=box.querySelector('#onbProgressBar'), cap=box.querySelector('#onbProgressCap');
    if(bar) bar.style.width=(total?(done/total*100):0).toFixed(1)+'%';
    if(cap) cap.textContent=done+'/'+total;
  }
  function showOnboardingStep(step){
    if(!onbSteps.includes(step)) step='ident';
    onbStep=step;
    box.querySelectorAll('[data-onbstep]').forEach(el=>el.classList.toggle('active', el.dataset.onbstep===step));
    box.querySelectorAll('[data-onbtab]').forEach(el=>el.classList.toggle('active', el.dataset.onbtab===step));
    paintOnboardingRailStatus();
    const idx=onbSteps.indexOf(step);
    const prev=$('obStepPrev'), next=$('obStepNext');
    const confirmBtn=$('modalConfirm');
    const finalActions=box.querySelector('.modal-actions');
    if(prev) prev.disabled=idx===0;
    if(next) next.style.visibility=idx===onbSteps.length-1?'hidden':'visible';
    if(finalActions) finalActions.style.display=idx===onbSteps.length-1?'flex':'none';
    if(confirmBtn) confirmBtn.style.display=idx===onbSteps.length-1?'inline-block':'none';
    const summary=$('obSummaryModalHost');
    if(summary) summary.innerHTML='';
  }
  box.querySelectorAll('[data-onbtab]').forEach(btn=>btn.addEventListener('click',()=>showOnboardingStep(btn.dataset.onbtab)));
  $('obStepPrev').addEventListener('click',()=>showOnboardingStep(onbSteps[Math.max(0,onbSteps.indexOf(onbStep)-1)]));
  $('obStepNext').addEventListener('click',()=>showOnboardingStep(onbSteps[Math.min(onbSteps.length-1,onbSteps.indexOf(onbStep)+1)]));
  showOnboardingStep(onbStep);
  function clearRiskSelection(){
    profSel=null;
    profListOpen=true;
    riskProfileAccepted=false;
    simCompareMode='current';
  }
  function paintBrokers(){
    const propFirms=BROKER_PARTNERS.filter(isPropFirm);
    const corretoras=BROKER_PARTNERS.filter(b=>!isPropFirm(b));
    const typeWrap=$('obInstitutionTypes');
    if(typeWrap){
      const mk=(key,label)=>`<button type="button" data-obinsttype="${key}" style="flex:1; min-width:180px; text-align:left; padding:11px 14px; border-radius:10px; cursor:pointer; border:1.5px solid ${institutionType===key?'var(--violet)':'var(--line)'}; background:${institutionType===key?'var(--indigo-deep)':'var(--panel)'}; color:${institutionType===key?'var(--violet)':'var(--ink)'}; font-weight:700; font-size:calc(13px * var(--fs-scale))">${label}</button>`;
      typeWrap.innerHTML = mk('broker','Corretora') + mk('prop','Mesa Proprietária / Prop Firm');
      typeWrap.querySelectorAll('[data-obinsttype]').forEach(btn=>btn.addEventListener('click',()=>{
        const nextType=btn.dataset.obinsttype||null;
        if(nextType===institutionType) return;
        institutionType=nextType;
        const currentBroker=brokerSel?BROKER_PARTNERS.find(b=>b.key===brokerSel):null;
        if(currentBroker){
          const currentType=isPropFirm(currentBroker)?'prop':'broker';
          if(currentType!==institutionType){
            brokerSel=null;
            institutionListOpen=true;
            clearBrokerCredentials();
            clearPropRules();
            clearRiskSelection();
          }
        }
        $('obBrokerErr').classList.remove('show');
        paintBrokers();
        syncEquityProtectorUI();
      }));
    }
    if(!institutionType){
      $('obBrokers').innerHTML='<div class="risk-note" style="margin-top:0">Escolha primeiro o tipo de instituição para ver apenas as parceiras compatíveis.</div>';
      paintBrokerCredentials();
      return;
    }
    const lista = institutionType==='prop' ? propFirms : corretoras;
    const titulo = institutionType==='prop' ? 'Mesas Proprietárias (Prop Firms)' : 'Corretoras Institucionais';
    const selectedBroker=brokerSel?BROKER_PARTNERS.find(b=>b.key===brokerSel):null;
    if(selectedBroker && !institutionListOpen){
      $('obBrokers').innerHTML=`
        <div class="broker-section-heading">${esc(titulo)}</div>
        <div style="display:grid; gap:10px">${brokerBadge(selectedBroker, true)}</div>`;
      box.querySelectorAll('[data-obbroker]').forEach(btn=>btn.addEventListener('click',()=>{
        if((btn.dataset.obbroker||'')!==brokerSel) return;
        brokerSel=null;
        institutionListOpen=true;
        clearBrokerCredentials();
        clearPropRules();
        clearRiskSelection();
        $('obBrokerErr').classList.remove('show');
        paintBrokers();
      }));
      paintBrokerCredentials();
      return;
    }
    $('obBrokers').innerHTML=`
      <div class="broker-section-heading">${esc(titulo)}</div>
      <div class="broker-grid">${lista.map(b=>brokerBadge(b, b.key===brokerSel)).join('')}</div>`;
    box.querySelectorAll('[data-obbroker]').forEach(btn=>btn.addEventListener('click',()=>{
      const nextKey=btn.dataset.obbroker||'';
      if(nextKey===brokerSel){
        brokerSel=null;
        institutionListOpen=true;
        clearBrokerCredentials();
        clearPropRules();
        clearRiskSelection();
      } else {
        if(nextKey!==brokerSel){
          clearBrokerCredentials();
          clearPropRules();
          clearRiskSelection();
        }
        brokerSel=nextKey;
        institutionListOpen=false;
      }
      paintBrokers();
      $('obBrokerErr').classList.remove('show');
      syncEquityProtectorUI();
    }));
    paintBrokerCredentials();
  }
  function paintBrokerCredentials(){
    const wrap=$('obBrokerCredWrap');
    if(!wrap) return;
    if(!hasSelectedInstitution()){
      wrap.innerHTML='';
      paintPropRules();
      invalidateSummary();
      return;
    }
    wrap.innerHTML=brokerCredentialFields();
    const loginEl=$('obBrokerLogin');
    const passEl=$('obInvestorPassword');
    const serverEl=$('obBrokerServer');
    const toggleEl=$('obInvestorToggle');
    const errEl=$('obBrokerCredErr');
    const syncCredErr=()=>{ if(errEl && hasCompleteConnectionData()) errEl.classList.remove('show'); };
    if(loginEl) loginEl.addEventListener('input',()=>{
      brokerLogin=loginEl.value;
      if(!hasCompleteConnectionData()) clearRiskSelection();
      paintRiskStep();
      syncCredErr();
      invalidateSummary();
    });
    if(passEl) passEl.addEventListener('input',()=>{
      investorPassword=passEl.value;
      if(!hasCompleteConnectionData()) clearRiskSelection();
      paintRiskStep();
      syncCredErr();
      invalidateSummary();
    });
    if(serverEl) serverEl.addEventListener('input',()=>{
      brokerServer=serverEl.value;
      if(!hasCompleteConnectionData()) clearRiskSelection();
      paintRiskStep();
      syncCredErr();
      invalidateSummary();
    });
    if(toggleEl && passEl) toggleEl.addEventListener('click',()=>{
      const open=passEl.type==='text';
      passEl.type=open?'password':'text';
      toggleEl.textContent=open?'Mostrar':'Ocultar';
      toggleEl.setAttribute('aria-expanded', open?'false':'true');
    });
    bindPlatformLeverageFields(syncCredErr);
    paintPropRules();
    invalidateSummary();
  }
  function paintPropRules(){
    const wrap=$('obPropRulesWrap');
    if(!wrap) return;
    if(!(institutionType==='prop' && hasSelectedInstitution())){
      wrap.innerHTML='';
      return;
    }
    wrap.innerHTML=propRulesFields();
    const dailyEl=$('obPropDaily');
    const maxEl=$('obPropMax');
    const trailingSelEl=$('obPropTrailingRule');
    const trailingDescWrap=$('obPropTrailingDescWrap');
    const trailingDescEl=$('obPropTrailingDesc');
    const profitEl=$('obPropProfitTarget');
    const minDaysEl=$('obPropMinDays');
    const absenceEl=$('obPropAbsence');
    const restrictiveEl=$('obPropRestrictive');
    const restrictiveErrEl=$('obPropRestrictiveErr');
    const rulesErrEl=$('obPropRulesErr');
    const syncPropErr=()=>{
      if(rulesErrEl && Boolean(String(propDailyDrawdown||'').trim()) && Boolean(String(propMaxDrawdown||'').trim())) rulesErrEl.classList.remove('show');
      if(restrictiveErrEl && restrictiveRuleAccepted) restrictiveErrEl.classList.remove('show');
    };
    if(dailyEl) dailyEl.addEventListener('input',()=>{
      propDailyDrawdown=dailyEl.value;
      if(!hasCompletePropRules()) clearRiskSelection();
      paintRiskStep();
      syncPropErr();
      invalidateSummary();
    });
    if(maxEl) maxEl.addEventListener('input',()=>{
      propMaxDrawdown=maxEl.value;
      if(!hasCompletePropRules()) clearRiskSelection();
      paintRiskStep();
      syncPropErr();
      invalidateSummary();
    });
    if(trailingSelEl) trailingSelEl.addEventListener('change',()=>{
      propTrailingRule=trailingSelEl.value;
      if(trailingDescWrap) trailingDescWrap.style.display=(propTrailingRule && propTrailingRule!=='Não existe')?'flex':'none';
      invalidateSummary();
    });
    if(trailingDescEl) trailingDescEl.addEventListener('input',()=>{ propTrailingDescription=trailingDescEl.value; invalidateSummary(); });
    if(profitEl) profitEl.addEventListener('input',()=>{ propProfitTarget=profitEl.value; invalidateSummary(); });
    if(minDaysEl) minDaysEl.addEventListener('input',()=>{ propMinTradingDays=minDaysEl.value; invalidateSummary(); });
    if(absenceEl) absenceEl.addEventListener('input',()=>{ propAbsenceRules=absenceEl.value; invalidateSummary(); });
    if(restrictiveEl) restrictiveEl.addEventListener('change',()=>{
      restrictiveRuleAccepted=restrictiveEl.checked;
      if(!hasCompletePropRules()) clearRiskSelection();
      paintRiskStep();
      syncPropErr();
      invalidateSummary();
    });
  }
  function paintEquityProtectorStep(){
    const wrap=$('obEquityProtectorWrap');
    if(!wrap) return;
    wrap.innerHTML=equityProtectorFields();
    bindEquityProtectorFields();
  }
  function updateReservesUI(){
    const r=reserveCalc();
    const setVal=(id,val)=>{ const el=$(id); if(el) el.value=val; };
    setVal('obReserveMasterCapital',fmtMoney2(r.capital));
    setVal('obReserveFcrRequired',fmtMoney2(r.fcrReq));
    setVal('obReserveFeoRequired',fmtMoney2(r.feoReq));
    setVal('obReserveFcrStatus',r.fcrStatus);
    setVal('obReserveFeoStatus',r.feoStatus);
    const fcrStatus=$('obReserveFcrStatus'), feoStatus=$('obReserveFeoStatus');
    if(fcrStatus){ fcrStatus.style.color=r.fcrStatus==='Regular'?'var(--f1)':'var(--f4)'; fcrStatus.style.fontWeight='800'; }
    if(feoStatus){ feoStatus.style.color=r.feoStatus==='Regular'?'var(--f1)':'var(--f4)'; feoStatus.style.fontWeight='800'; }
    const fcrAlert=$('obReserveFcrAlert'), feoAlert=$('obReserveFeoAlert'), defAlert=$('obReserveDeficitAlert'), defWrap=$('obReserveDeficitWrap');
    if(fcrAlert) fcrAlert.style.display=r.fcrStatus==='Insuficiente'?'block':'none';
    if(feoAlert) feoAlert.style.display=r.feoStatus==='Insuficiente'?'block':'none';
    if(defAlert) defAlert.style.display=r.hasDeficit?'block':'none';
    if(defWrap) defWrap.style.display=r.hasDeficit?'flex':'none';
    if(!r.hasDeficit) reserveDeficitAccepted=false;
    const panel=$('obReservePanel');
    if(panel) panel.innerHTML=reservePanelHTML();
  }
  function bindReservesFields(){
    const bindInput=(id,fn)=>{ const el=$(id); if(el) el.addEventListener('input',()=>{ fn(el.value); updateReservesUI(); const err=$('obReserveErr'); if(err) err.classList.remove('show'); invalidateSummary(); }); };
    bindInput('obReserveFcrCurrent',v=>{ reserveFcrCurrent=v; });
    bindInput('obReserveMonthlyExpenses',v=>{ reserveMonthlyExpenses=v; });
    bindInput('obReserveFeoCurrent',v=>{ reserveFeoCurrent=v; });
    bindInput('obReserveNotes',v=>{ reserveNotes=v; });
    const seg=$('obReserveSegregation');
    if(seg) seg.addEventListener('change',()=>{ reserveSegregationAccepted=seg.checked; const err=$('obReserveErr'); if(err) err.classList.remove('show'); invalidateSummary(); });
    const def=$('obReserveDeficitAccepted');
    if(def) def.addEventListener('change',()=>{ reserveDeficitAccepted=def.checked; const err=$('obReserveErr'); if(err) err.classList.remove('show'); invalidateSummary(); });
    updateReservesUI();
  }
  function paintReservesStep(){
    const wrap=$('obReservesStepWrap');
    if(!wrap) return;
    wrap.innerHTML=reservesFields();
    bindReservesFields();
  }
  function syncCentralCashUI(){
    const otherWrap=$('obCentralCashCustodyOtherWrap');
    const noAlert=$('obCentralCashNoAlert');
    const noWrap=$('obCentralCashNoAcceptedWrap');
    const fcrAlert=$('obFcrLiquidityAlert');
    const feoAlert=$('obFeoLiquidityAlert');
    const ledgerAlert=$('obCashLedgerAlert');
    const segNote=$('obCentralCashSegNote');
    if(otherWrap) otherWrap.style.display=centralCashCustody==='Outra'?'flex':'none';
    if(noAlert) noAlert.style.display=centralCashStatus==='Não.'?'block':'none';
    if(noWrap) noWrap.style.display=centralCashStatus==='Não.'?'flex':'none';
    if(fcrAlert) fcrAlert.style.display=liquidityTooSlow('fcr',fcrLiquidity)?'block':'none';
    if(feoAlert) feoAlert.style.display=liquidityTooSlow('feo',feoLiquidity)?'block':'none';
    if(ledgerAlert) ledgerAlert.style.display=(cashLedgerStatus==='Ainda não existe registro formal'||cashLedgerStatus==='Registro parcial')?'block':'none';
    if(segNote) segNote.textContent='Soma declarada: '+cashSegTotal().toFixed(1).replace('.',',')+'%. Não é obrigatório fechar 100% se a estrutura estiver em implantação.';
    if(centralCashStatus!=='Não.') centralCashNoAccepted=false;
    const panel=$('obCentralCashPanel');
    if(panel) panel.innerHTML=centralCashPanelHTML();
  }
  function bindCentralCashFields(){
    const bindInput=(id,fn)=>{ const el=$(id); if(el) el.addEventListener('input',()=>{ fn(el.value); syncCentralCashUI(); const err=$('obCentralCashErr'); if(err) err.classList.remove('show'); invalidateSummary(); }); };
    const bindChange=(id,fn)=>{ const el=$(id); if(el) el.addEventListener('change',()=>{ fn(el.value); syncCentralCashUI(); const err=$('obCentralCashErr'); if(err) err.classList.remove('show'); invalidateSummary(); }); };
    bindChange('obCentralCashStatus',v=>{ centralCashStatus=v; });
    bindChange('obCentralCashCustody',v=>{ centralCashCustody=v; if(v!=='Outra') centralCashCustodyOther=''; });
    bindInput('obCentralCashCustodyOther',v=>{ centralCashCustodyOther=v; });
    bindInput('obCentralCashMainPct',v=>{ centralCashMainPct=v; });
    bindInput('obCentralCashAgilePct',v=>{ centralCashAgilePct=v; });
    bindInput('obCentralCashLiquidityPct',v=>{ centralCashLiquidityPct=v; });
    bindInput('obCentralCashExternalPct',v=>{ centralCashExternalPct=v; });
    bindInput('obCentralCashOtherPct',v=>{ centralCashOtherPct=v; });
    bindChange('obFcrLiquidity',v=>{ fcrLiquidity=v; });
    bindChange('obFeoLiquidity',v=>{ feoLiquidity=v; });
    bindChange('obCashLedgerStatus',v=>{ cashLedgerStatus=v; });
    bindInput('obCentralCashNotes',v=>{ centralCashNotes=v; });
    const policy=$('obCentralCashPolicy');
    if(policy) policy.addEventListener('change',()=>{ centralCashPolicyAccepted=policy.checked; const err=$('obCentralCashErr'); if(err) err.classList.remove('show'); invalidateSummary(); });
    const noAccepted=$('obCentralCashNoAccepted');
    if(noAccepted) noAccepted.addEventListener('change',()=>{ centralCashNoAccepted=noAccepted.checked; const err=$('obCentralCashErr'); if(err) err.classList.remove('show'); invalidateSummary(); });
    syncCentralCashUI();
  }
  function paintCentralCashStep(){
    const wrap=$('obCentralCashStepWrap');
    if(!wrap) return;
    wrap.innerHTML=centralCashFields();
    bindCentralCashFields();
  }
  function validateReserves(){
    const err=$('obReserveErr');
    const fail=(msg)=>{ if(err){ err.textContent=msg; err.classList.add('show'); } alert(msg); return false; };
    const r=reserveCalc();
    if(!String(reserveFcrCurrent||'').trim()) return fail('Informe o FCR atualmente constituído.');
    if(!String(reserveMonthlyExpenses||'').trim()) return fail('Informe as despesas mensais da estrutura.');
    if(!String(reserveFeoCurrent||'').trim()) return fail('Informe o FEO atualmente constituído.');
    if(!reserveSegregationAccepted) return fail('Confirme que FCR e FEO são reservas segregadas e não autorizam aumento de risco.');
    if(r.hasDeficit && !reserveDeficitAccepted) return fail('Confirme ciência formal sobre reservas segregadas abaixo do mínimo estatutário.');
    return true;
  }
  function validateCentralCash(){
    const err=$('obCentralCashErr');
    const fail=(msg)=>{ if(err){ err.textContent=msg; err.classList.add('show'); } alert(msg); return false; };
    if(!centralCashStatus) return fail('Informe se existe Caixa Central definido.');
    if(centralCashStatus==='Não.' && !centralCashNoAccepted) return fail('Confirme ciência de que operar sem Caixa Central definido fragiliza a rastreabilidade patrimonial.');
    if(!centralCashCustody) return fail('Informe a custódia principal do Caixa Central.');
    if(centralCashCustody==='Outra' && !String(centralCashCustodyOther||'').trim()) return fail('Descreva a custódia principal do Caixa Central.');
    if(!fcrLiquidity) return fail('Informe a liquidez do FCR.');
    if(!feoLiquidity) return fail('Informe a liquidez do FEO.');
    if(!cashLedgerStatus) return fail('Informe o status do registro das movimentações patrimoniais.');
    if((liquidityTooSlow('fcr',fcrLiquidity)||liquidityTooSlow('feo',feoLiquidity)) && !String(centralCashNotes||'').trim()){
      return fail('Justifique nas observações a liquidez do FCR/FEO quando estiver acima do padrão recomendado ou não definida.');
    }
    if(!centralCashPolicyAccepted) return fail('Aceite a política de movimentação pelo Caixa Central ou registro formal.');
    return true;
  }
  function syncEquityProtectorUI(){
    const otherWrap=$('obEpOtherWrap');
    const noConfigWrap=$('obEpNoConfigWrap');
    const propAlert=$('obEpPropAlert');
    const propWrap=$('obEpPropWrap');
    if(otherWrap) otherWrap.style.display=epPlatform==='Outra.'?'flex':'none';
    if(noConfigWrap) noConfigWrap.style.display=(epStatus==='Não vou utilizar.'||epStatus==='Ainda vou configurar antes de iniciar o período.')?'block':'none';
    if(propAlert) propAlert.style.display=(institutionType==='prop'&&(epStatus==='Não vou utilizar.'||epStatus==='Ainda vou configurar antes de iniciar o período.'))?'block':'none';
    if(propWrap) propWrap.style.display=institutionType==='prop'?'block':'none';
  }
  function bindEquityProtectorFields(){
    if(!canShowEquityProtectorStep()) return;
    const bindInput=(id,fn)=>{ const el=$(id); if(el) el.addEventListener('input',()=>{ fn(el.value); const err=$('obEpErr'); if(err) err.classList.remove('show'); invalidateSummary(); }); };
    const bindChange=(id,fn)=>{ const el=$(id); if(el) el.addEventListener('change',()=>{ fn(el); const err=$('obEpErr'); if(err) err.classList.remove('show'); syncEquityProtectorUI(); invalidateSummary(); }); };
    bindChange('obEpStatus',el=>{ epStatus=el.value; if(epStatus!=='Não vou utilizar.' && epStatus!=='Ainda vou configurar antes de iniciar o período.') epNoConfigAccepted=false; });
    bindChange('obEpPlatform',el=>{ epPlatform=el.value; if(epPlatform!=='Outra.') epPlatformOther=''; });
    bindInput('obEpOther',v=>{ epPlatformOther=v; });
    bindInput('obEpDaily',v=>{ epDailyLimit=v; });
    bindChange('obEpPropDailyEnabled',el=>{ epPropDailyEnabled=el.value; });
    bindChange('obEpPropDailyBase',el=>{ epPropDailyBase=el.value; });
    bindInput('obEpPropDailyNotes',v=>{ epPropDailyNotes=v; });
    bindInput('obEpNotes',v=>{ epNotes=v; });
    const restrictive=$('obEpRestrictive');
    if(restrictive) restrictive.addEventListener('change',()=>{ epRestrictiveAccepted=restrictive.checked; const err=$('obEpErr'); if(err) err.classList.remove('show'); invalidateSummary(); });
    const noConfig=$('obEpNoConfigAccepted');
    if(noConfig) noConfig.addEventListener('change',()=>{ epNoConfigAccepted=noConfig.checked; const err=$('obEpErr'); if(err) err.classList.remove('show'); invalidateSummary(); });
    syncEquityProtectorUI();
  }
  function validateEquityProtector(){
    const err=$('obEpErr');
    const fail=(msg)=>{ if(err){ err.textContent=msg; err.classList.add('show'); } alert(msg); return false; };
    if(!canShowEquityProtectorStep()) return fail('Preencha primeiro os dados da conta, corretora/mesa proprietária e perfil de risco para configurar a Proteção Externa de Conta.');
    if(!epStatus) return fail('Informe se o Equity Protector já foi configurado.');
    if(!epRestrictiveAccepted) return fail('Aceite a regra de prevalência da regra mais restritiva.');
    if(epStatus==='Sim, vou utilizar.'){
      if(!epPlatform || epPlatform==='Nenhuma.') return fail('Informe a plataforma escolhida para o Equity Protector.');
      if(epPlatform==='Outra.' && !String(epPlatformOther||'').trim()) return fail('Informe o nome da plataforma/ferramenta utilizada.');
    }
    if(epStatus==='Não vou utilizar.'){
      if(institutionType==='prop') alert('Conta de prop firm/mesa proprietária possui regras externas de drawdown e violação. É altamente recomendável configurar um Equity Protector antes de iniciar o período.');
      if(!epNoConfigAccepted) return fail('Confirme ciência de que iniciar o período sem Equity Protector aumenta o risco operacional e exige controle manual rigoroso.');
    }
    if(epStatus==='Ainda vou configurar antes de iniciar o período.') return fail('Conclua a configuração do Equity Protector antes de iniciar o período.');
    if(epStatus==='Não se aplica a esta conta.'){
      if(!String(epNotes||'').trim()) return fail('Justifique nas observações por que o Equity Protector não se aplica a esta conta.');
    }
    if(institutionType==='prop'){
      if(!epPropDailyEnabled) return fail('Informe se existe limite de perda diária da mesa proprietária.');
      if(epPropDailyEnabled==='Sim.'){
        if(!String(epDailyLimit||'').trim()) return fail('Informe o valor do limite de perda diária da mesa proprietária.');
        if(!epPropDailyBase) return fail('Informe a base de cálculo do limite de perda diária da mesa proprietária.');
      }
    }
    return true;
  }
  function invalidateSummary(){
    summaryAccepted=false;
    paintSummary();
    paintOnboardingRailStatus(); // status do rail acompanha cada alteração de campo
  }
  function paintSummary(){
    const host=$('obSummaryModalHost');
    if(host) host.innerHTML='';
  }
  function bindSummaryConfirmationModal(payload){
    const acceptEl=$('obSummaryAccept');
    const errEl=$('obSummaryErr');
    const closeBtn=$('obSummaryClose');
    const backBtn=$('obSummaryBack');
    const confirmBtn=$('obSummaryConfirm');
    const setState=()=>{
      if(confirmBtn) confirmBtn.disabled=!summaryAccepted;
      if(summaryAccepted && errEl) errEl.classList.remove('show');
    };
    if(acceptEl) acceptEl.addEventListener('change',()=>{
      summaryAccepted=acceptEl.checked;
      setState();
    });
    const closeSummary=()=>{ summaryAccepted=false; paintSummary(); };
    if(closeBtn) closeBtn.addEventListener('click', closeSummary);
    if(backBtn) backBtn.addEventListener('click', closeSummary);
    if(confirmBtn) confirmBtn.addEventListener('click',()=>{
      if(!summaryAccepted){
        if(errEl) errEl.classList.add('show');
        return;
      }
      commitOnboardingStart(payload);
    });
    setState();
  }
  function openSummaryConfirmationModal(payload){
    const host=$('obSummaryModalHost');
    if(!host || !canShowOnboardingSummary()) return;
    host.innerHTML=`
      <div id="obSummaryPanel" style="margin-top:14px; scroll-margin-top:24px">
        ${renderOnboardingFinalSummary()}
        <div class="modal-actions" style="margin-top:16px">
          <button class="modal-btn cancel" id="obSummaryBack">Voltar ao formulário</button>
          <button class="modal-btn confirm" id="obSummaryConfirm" disabled>${isEditMode?'Confirmar alterações':'Confirmar início do período'}</button>
        </div>
      </div>`;
    bindSummaryConfirmationModal(payload);
    const panel=$('obSummaryPanel');
    if(panel) panel.scrollIntoView({behavior:'smooth', block:'nearest'});
  }
  function commitOnboardingStart(payload){
    const {saldo, loginVal, passVal, serverVal, plataformaVal, alavVal, isPropFlow, propDailyVal, propMaxVal, propTrailingRuleVal, propTrailingDescVal, propProfitVal, propMinDaysVal, propAbsenceVal, restrictiveVal,
      reserveMasterCapitalVal, reserveFcrRequiredVal, reserveFcrCurrentVal, reserveFcrStatusVal, reserveMonthlyExpensesVal, reserveFeoRequiredVal, reserveFeoCurrentVal, reserveFeoStatusVal, reserveSegregationAcceptedVal, reserveDeficitAcceptedVal, reserveNotesVal,
      centralCashStatusVal, centralCashCustodyVal, centralCashCustodyOtherVal, centralCashMainPctVal, centralCashAgilePctVal, centralCashLiquidityPctVal, centralCashExternalPctVal, centralCashOtherPctVal, fcrLiquidityVal, feoLiquidityVal, cashLedgerStatusVal, centralCashPolicyAcceptedVal, centralCashNoAcceptedVal, centralCashNotesVal,
      epStatusVal, epPlatformVal, epPlatformOtherVal, epDailyLimitVal, epRestrictiveAcceptedVal, epPropDailyEnabledVal, epPropDailyBaseVal, epPropDailyNotesVal, epNoConfigAcceptedVal, epNotesVal}=payload;
    const pr=getActiveRiskProfile(profSel);
    const broker=BROKER_PARTNERS.find(b=>b.key===brokerSel);
    const dataInicio=$('obData').value || (isEditMode ? (S.params.inicio||todayISO()) : todayISO());
    const epMaxDrawdownAuto=fmtPct(pr.mdd);
    const reserveMetrics=reserveCalc();
    const cashMetrics=centralCashCalc();
    const consentOperator=$('obOperador').value.trim();
    const consentAcceptedAt=isEditMode ? (ob.consentAcceptedAt||localDateTimeISO()) : localDateTimeISO();
    // JPW-HJFGDE §5: registro do termo de responsabilidade da base. O gate no confirmar
    // garante que o checkbox está marcado — aqui NUNCA se registra aceite não dado. Um
    // aceite anterior é preservado com o carimbo original: re-salvar o formulário não
    // "renova" o termo. Aplicado dentro de cada ramo, junto do commit do restante.
    const aplicarTermoBase=()=>{
      if(!S.dataGovernance || !S.dataGovernance.responsibility) return;
      if(S.dataGovernance.responsibility.accepted) return;
      if(!($('obDbResp')&&$('obDbResp').checked)) return;
      S.dataGovernance.responsibility={accepted:true, acceptedAt:localDateTimeISO(),
        version:(typeof DG_RESPONSIBILITY_VERSION!=='undefined')?DG_RESPONSIBILITY_VERSION:1};
      if(typeof dgLogChange==='function') dgLogChange('database','responsibility_accepted','','Termo de responsabilidade da base aceito');
    };
    const nextOnboarding={done:true, operador:$('obOperador').value.trim(), supervisor:$('obSupervisor').value.trim(),
      corretora:broker.name, plataforma:plataformaVal, alavCorretora:alavVal, moedaBase:normalizeAccountCurrency($('obMoedaBase').value),
      brokerLogin:loginVal, investorPassword:passVal, brokerServer:serverVal,
      propDailyDrawdown:propDailyVal, propMaxDrawdown:propMaxVal, propTrailingRule:propTrailingRuleVal,
      propTrailingDescription:propTrailingDescVal, propProfitTarget:propProfitVal, propMinTradingDays:propMinDaysVal,
      propAbsenceRules:propAbsenceVal, restrictiveRuleAccepted:restrictiveVal,
      /* ||0, não ||'': mesma grafia canônica da derivação em DEFAULTS e na migrate —
         com capital zerado o campo deve dizer '0', nunca voltar ao '' pré-canônico. */
      reserveMasterCapital:String(reserveMasterCapitalVal||0), reserveFcrRequired:String(reserveFcrRequiredVal||0), reserveFcrCurrent:String(reserveFcrCurrentVal||''),
      reserveFcrStatus:reserveFcrStatusVal, reserveMonthlyExpenses:String(reserveMonthlyExpensesVal||''), reserveFeoRequired:String(reserveFeoRequiredVal||0),
      reserveFeoCurrent:String(reserveFeoCurrentVal||''), reserveFeoStatus:reserveFeoStatusVal,
      reserveFcrCoveragePct:String(reserveMetrics.fcrCoverage||0), reserveFeoCoveragePct:String(reserveMetrics.feoCoverage||0),
      reserveFeoMonthsCovered:String(reserveMetrics.feoMonths||0),
      reserveSegregationAccepted:!!reserveSegregationAcceptedVal, reserveDeficitAccepted:!!reserveDeficitAcceptedVal, reserveNotes:reserveNotesVal,
      centralCashStatus:centralCashStatusVal, centralCashCustody:centralCashCustodyVal, centralCashCustodyOther:centralCashCustodyOtherVal,
      centralCashMainPct:centralCashMainPctVal, centralCashAgilePct:centralCashAgilePctVal, centralCashLiquidityPct:centralCashLiquidityPctVal,
      centralCashExternalPct:centralCashExternalPctVal, centralCashOtherPct:centralCashOtherPctVal,
      centralCashCompositionMode:'percentual', centralCashCompositionTotal:String(cashMetrics.total||0),
      fcrLiquidity:fcrLiquidityVal, feoLiquidity:feoLiquidityVal, cashLedgerStatus:cashLedgerStatusVal,
      centralCashPolicyAccepted:!!centralCashPolicyAcceptedVal, centralCashNoAccepted:!!centralCashNoAcceptedVal,
      centralCashTraceabilityScore:String(cashMetrics.score||0), centralCashNotes:centralCashNotesVal,
      epStatus:epStatusVal, epPlatform:epPlatformVal, epPlatformOther:epPlatformOtherVal,
      epDailyLimit:epDailyLimitVal, epMaxDrawdown:epMaxDrawdownAuto,
      epRestrictiveAccepted:!!epRestrictiveAcceptedVal,
      epPropDailyEnabled:epPropDailyEnabledVal, epPropDailyBase:epPropDailyBaseVal, epPropDailyNotes:epPropDailyNotesVal,
      epNoConfigAccepted:!!epNoConfigAcceptedVal, epNotes:epNotesVal,
      summaryAccepted:true,
      consentAccepted:true, consentVersion:'V10.0', consentDocument:'Estatuto JP WEALTH UNIFICADO.pdf',
      consentAcceptedAt, consentOperator};
    if(isEditMode){
      S.onboarding=nextOnboarding;
      aplicarTermoBase();
      if(typeof dgLogChange==='function') dgLogChange('onboarding','updated','','Formulário de início editado');
      S.params.saldoIni=saldo;
      S.params.inicio=dataInicio;
      S.period=S.period||{}; S.period.profile=pr.key;
      S.params.refM=pr.mensal; S.params.refA=pr.anual;
      S.transitionLog.push({fase:'edição formulário de início', ts:new Date().toISOString(),
        resumo:{operador:S.onboarding.operador, supervisor:S.onboarding.supervisor, corretora:S.onboarding.corretora,
          plataforma:S.onboarding.plataforma, alavCorretora:S.onboarding.alavCorretora, brokerLogin:S.onboarding.brokerLogin,
          brokerServer:S.onboarding.brokerServer, investorPassword:'•••', saldoInicial:saldo, dataInicio, perfil:pr.name,
          equityProtector:S.onboarding.epStatus, epPlatform:S.onboarding.epPlatform}});
      save(); closeModal(); boot(); if(isOnboardingFullyComplete()) showOnboardingCompleteNotice();
      return true;
    }
    const nextPeriodMeta={inicio:dataInicio, saldoIni:saldo, profile:pr.key, profileName:pr.name};
    if(Array.isArray(S.ledger) && S.ledger.length>0){
      const ok=confirm('Existe fechamento diário do período atual. Ao iniciar um novo período, esses lançamentos serão arquivados e o ledger ativo será zerado para evitar mistura entre ciclos. O histórico continuará preservado no backup completo.');
      if(!ok) return false;
      archiveCurrentLedgerForNewPeriod(nextPeriodMeta);
    }
    // Novo período = CICLO ZERADO: perda/lucro arquivados (cycleRealizado), grades das fases e
    // destravamento das Fases 2-4 não podem vazar para o ciclo novo (senão o drawdown e a fase
    // vigente nascem contaminados sobre um saldo inicial novo). A QUARENTENA é PRESERVADA de
    // propósito: pelo Estatuto V10 ela não pode ser liberada unilateralmente pelo gestor, então
    // reiniciar o período não pode virar atalho para burlar os 90 dias.
    const tinhaEstadoDeCiclo = (S.cycleRealizado||0)!==0
      || (Array.isArray(S.phaseUnlocked) && S.phaseUnlocked.slice(1).some(Boolean))
      || (Array.isArray(S.phases) && S.phases.some(ph=>Array.isArray(ph.orders) && ph.orders.some(o=>o && o.status)));
    S.cycleRealizado=0;
    const cycleSizes=[5,4,3,2];
    S.phases.forEach((ph,pi)=>{ ph.orders=emptyOrders(cycleSizes[pi]||3); });
    S.phaseUnlocked=[true,false,false,false];
    // S.quarantine é intencionalmente NÃO tocada aqui (preservação da quarentena — Estatuto V10).
    if(tinhaEstadoDeCiclo){
      S.transitionLog.push({fase:'ciclo zerado (novo período)', ts:new Date().toISOString(),
        resumo:{motivo:'reinício de período', cycleRealizado:0, fasesRetravadas:true,
          quarentenaPreservada:!!S.quarantine}});
    }
    S.onboarding=nextOnboarding;
    aplicarTermoBase();
    if(typeof dgLogChange==='function') dgLogChange('onboarding','completed','','Período iniciado — configuração inicial concluída');
    S.params.saldoIni=saldo; S.params.saldoAtu=saldo;
    S.params.inicio=nextPeriodMeta.inicio;
    S.period=S.period||{}; S.period.profile=pr.key;
    S.params.refM=pr.mensal; S.params.refA=pr.anual;
    S.transitionLog.push({fase:'consentimento estatuto', ts:new Date().toISOString(),
      resumo:{consentAccepted:true, consentVersion:'V10.0', consentDocument:'Estatuto JP WEALTH UNIFICADO.pdf',
        consentAcceptedAt, consentOperator}});
    S.transitionLog.push({fase:'início de período', ts:new Date().toISOString(),
      resumo:{operador:S.onboarding.operador, supervisor:S.onboarding.supervisor, corretora:S.onboarding.corretora,
        plataforma:S.onboarding.plataforma, alavCorretora:S.onboarding.alavCorretora, brokerLogin:S.onboarding.brokerLogin,
        brokerServer:S.onboarding.brokerServer, investorPassword:'•••', saldo, perfil:pr.name,
        equityProtector:+onboardingEP(saldo,pr.key).ep.toFixed(2), epStatus:S.onboarding.epStatus,
        epPlatform:S.onboarding.epPlatform, objetivoAnual:+onboardingEP(saldo,pr.key).obj.toFixed(2)}});
    save(); closeModal(); boot(); if(isOnboardingFullyComplete()) showOnboardingCompleteNotice();
    return true;
  }
  function renderOnboardingFinalSummary(){
    const broker=BROKER_PARTNERS.find(b=>b.key===brokerSel);
    const saldo=parseFloat(($('obSaldo')&&$('obSaldo').value)||0)||0;
    const moeda=normalizeAccountCurrency(($('obMoedaBase')&&$('obMoedaBase').value)||'USD');
    const dataInicio=($('obData')&&$('obData').value)||S.params.inicio||todayISO();
    const dataFim=projectCycleEndISO(dataInicio);
    const pr=getActiveRiskProfile(profSel);
    const matrix=activeRiskMatrix(profSel);
    const riscoMax=saldo*pr.mdd;
    const estatutoAceito=!!($('obConsent') && $('obConsent').checked);
    const isProp=institutionType==='prop';
    const srow=(k,v,opts)=>`<tr><td style="color:var(--ink-dim); padding:5px 8px; white-space:nowrap">${k}</td><td class="hl" style="text-align:right; padding:5px 8px; ${opts&&opts.strong?'font-weight:800;':''}${opts&&opts.color?'color:'+opts.color+';':''}">${(v==null||v==='')?'—':v}</td></tr>`;
    const srowHead=(label)=>`<tr><td colspan="2" style="padding:10px 8px 4px; color:var(--ink-dim); font-size:calc(10px * var(--fs-scale)); text-transform:uppercase; letter-spacing:.04em; font-weight:700">${label}</td></tr>`;
    const grupo=(titulo,rows)=>`
      <div class="card" style="margin:8px 0 14px; padding:14px 16px; box-shadow:none; border-color:var(--line); background:var(--panel-2)">
        <h2 style="margin-bottom:8px">${titulo}</h2>
        <table class="dtable">${rows}</table>
      </div>`;
    const institConexao=grupo('Instituição e Conexão',
      srow('Tipo de ambiente', isProp?'Mesa Proprietária / Prop Firm':'Corretora')+
      srow('Instituição', esc(broker?broker.name:''))+
      srow('Login da Conta', esc(brokerLogin||''))+
      srow('Senha de Investidor', investorPassword.trim()?'preenchida':'não preenchida')+
      srow('Servidor da Corretora', esc(brokerServer||''))+
      srow('Plataforma', esc(plataforma||''))+
      srow('Alavancagem da Corretora', esc(alavCorretora||''))
    );
    const contaAmbiente=grupo('Conta e Ambiente',
      srow('Saldo Inicial do Período', fmtMoney2(saldo))+
      srow('Moeda-base da Conta', moeda)+
      srow('Data de início do período', fmtDateEU(dataInicio))+
      srow('Data final projetada', fmtDateEU(dataFim))
    );
    const matrixRows=matrix.map((row,i)=>srow('Fase '+(i+1), fmtPct(row.ddmin)+' a '+fmtPct(row.ddmax))).join('');
    const sistemaRisco=grupo('Sistema de Risco',
      srow('Perfil de Risco', esc(pr.name))+
      srow('Expectativa Mensal', fmtPct(pr.mensal))+
      srow('Expectativa Anual Composta', fmtPct(pr.anual))+
      srow('Máximo Drawdown do Perfil', fmtPct(pr.mdd), {strong:true, color:'var(--f4)'})+
      srow('Risco Máximo Permitido', fmtMoney2(riscoMax), {strong:true, color:'var(--f4)'})+
      srowHead('Matriz Ativa do Perfil ('+esc(pr.name)+')')+
      matrixRows
    );
    const propRows=isProp ? (
      srow('Drawdown Diário Permitido (externo)', esc(propDailyDrawdown), {strong:true})+
      srow('Drawdown Máximo Permitido (externo)', esc(propMaxDrawdown), {strong:true})+
      (propTrailingRule ? srow('Regra de Trailing', esc(propTrailingRule)) : '')+
      (propTrailingRule && propTrailingRule!=='Não existe' && propTrailingDescription ? srow('Descrição do Trailing', esc(propTrailingDescription)) : '')+
      (propProfitTarget ? srow('Meta de Lucro da Avaliação', esc(propProfitTarget)) : '')+
      (propMinTradingDays ? srow('Número Mínimo de Dias Operados', esc(propMinTradingDays)) : '')+
      (propAbsenceRules ? srow('Regras de Ausência', esc(propAbsenceRules)) : '')+
      srow('Regra mais restritiva prevalece', restrictiveRuleAccepted?'aceita':'não aceita', {strong:true, color:restrictiveRuleAccepted?'var(--f1)':'var(--f4)'})
    ) : srow('Regra Externa Aplicável', 'não informada / não aplicável');
    const regrasExternas=grupo('Regras Externas', propRows);
    const reservesNow=reserveCalc();
    const reservePending=reservesNow.hasDeficit;
    const summaryFcrColor=reservesNow.fcrCoverage>=100?'var(--f1)':(reservesNow.fcrCoverage>=75?'var(--f2)':'var(--f4)');
    const summaryFeoColor=reservesNow.feoCoverage>=100?'var(--f1)':(reservesNow.feoCoverage>=75?'var(--f2)':'var(--f4)');
    const reservasResumo=grupo('Reservas Segregadas — FCR e FEO',
      (reservePending ? srow('Pendência estatutária', 'reservas segregadas abaixo do mínimo', {strong:true, color:'var(--f4)'}) : '')+
      srow('Capital nominal da Conta Mestre', fmtMoney2(reservesNow.capital))+
      srow('FCR mínimo exigido', fmtMoney2(reservesNow.fcrReq))+
      srow('FCR atual', fmtMoney2(reservesNow.fcrCur))+
      srow('Cobertura FCR', pctText(reservesNow.fcrCoverage), {strong:true, color:summaryFcrColor})+
      srow('Status do FCR', reservesNow.fcrStatus, {strong:true, color:reservesNow.fcrStatus==='Regular'?'var(--f1)':'var(--f4)'})+
      srow('Despesas mensais da estrutura', fmtMoney2(reservesNow.monthly))+
      srow('FEO mínimo exigido', fmtMoney2(reservesNow.feoReq))+
      srow('FEO atual', fmtMoney2(reservesNow.feoCur))+
      srow('Cobertura FEO', pctText(reservesNow.feoCoverage), {strong:true, color:summaryFeoColor})+
      srow('Meses cobertos pelo FEO', (reservesNow.feoMonths||0).toFixed(1).replace('.',',')+' meses')+
      srow('Status do FEO', reservesNow.feoStatus, {strong:true, color:reservesNow.feoStatus==='Regular'?'var(--f1)':'var(--f4)'})+
      srow('Segregação das reservas aceita', reserveSegregationAccepted?'sim':'não', {strong:true, color:reserveSegregationAccepted?'var(--f1)':'var(--f4)'})+
      (reservePending ? srow('Ciência sobre déficit', reserveDeficitAccepted?'aceita':'pendente', {strong:true, color:reserveDeficitAccepted?'var(--f1)':'var(--f4)'}) : '')+
      (reserveNotes ? srow('Observações', esc(reserveNotes)) : '')
    );
    const centralCashPending=(centralCashStatus==='Não.'||cashLedgerStatus==='Ainda não existe registro formal'||cashLedgerStatus==='Registro parcial');
    const cashNow=centralCashCalc();
    const cashScoreColor=cashNow.score>=70?'var(--f1)':(cashNow.score>=40?'var(--f2)':'var(--f4)');
    const segmentation=[
      centralCashMainPct?`Patrimonial ${esc(centralCashMainPct)}%`:'',
      centralCashAgilePct?`Operacional ${esc(centralCashAgilePct)}%`:'',
      centralCashLiquidityPct?`Liquidez ${esc(centralCashLiquidityPct)}%`:'',
      centralCashExternalPct?`Externos ${esc(centralCashExternalPct)}%`:'',
      centralCashOtherPct?`Outros ${esc(centralCashOtherPct)}%`:''
    ].filter(Boolean).join(' · ');
    const caixaResumo=grupo('Caixa Central e Liquidez Institucional',
      (centralCashPending ? srow('Pendência de governança', 'Caixa Central ou registro patrimonial incompleto', {strong:true, color:'var(--f2)'}) : '')+
      srow('Status do Caixa Central', esc(centralCashStatus))+
      srow('Custódia principal', esc(centralCashCustody==='Outra'?(centralCashCustodyOther||'Outra'):centralCashCustody))+
      srow('Segmentação declarada', segmentation||'não informada')+
      srow('Liquidez do FCR', esc(fcrLiquidity), {strong:liquidityTooSlow('fcr',fcrLiquidity), color:liquidityTooSlow('fcr',fcrLiquidity)?'var(--f2)':''})+
      srow('Liquidez do FEO', esc(feoLiquidity), {strong:liquidityTooSlow('feo',feoLiquidity), color:liquidityTooSlow('feo',feoLiquidity)?'var(--f2)':''})+
      srow('Score de rastreabilidade', cashNow.score+'/100 · '+cashNow.traceClass, {strong:true, color:cashScoreColor})+
      srow('Registro patrimonial / livro-razão', esc(cashLedgerStatus))+
      srow('Política de movimentação aceita', centralCashPolicyAccepted?'sim':'não', {strong:true, color:centralCashPolicyAccepted?'var(--f1)':'var(--f4)'})+
      (centralCashNotes ? srow('Observações', esc(centralCashNotes)) : '')
    );
    const epRows=
      srow('Uso de proteção externa neste período', esc(epStatus||''), {strong:true})+
      srow('Plataforma', esc(epPlatform==='Outra.'?(epPlatformOther||'Outra'):epPlatform))+
      srow('Drawdown máximo estatutário do período', fmtPct(pr.mdd))+
      (isProp ? srow('Limite de perda diária da mesa', esc(epDailyLimit||'')) : '')+
      (isProp ? srow('Base do cálculo diário', esc(epPropDailyBase||'')) : '')+
      srow('Regra mais restritiva aceita', epRestrictiveAccepted?'sim':'não', {strong:true, color:epRestrictiveAccepted?'var(--f1)':'var(--f4)'});
    const equityProtectorResumo=grupo('Equity Protector / Proteção Externa', epRows);
    const confirmacoes=grupo('Confirmações',
      srow('Declarações estatutárias aceitas', estatutoAceito?'sim':'não', {strong:true, color:estatutoAceito?'var(--f1)':'var(--f4)'})+
      (isProp ? srow('Prevalência da regra mais restritiva', restrictiveRuleAccepted?'aceita':'não aceita') : '')
    );
    return `
      <div class="card" style="margin:18px 0 0; padding:14px 16px; border-color:var(--violet); background:var(--indigo-deep); box-shadow:none">
        <h2 style="margin-bottom:4px; color:var(--violet)">🧾 Resumo e Confirmação do Período <span class="art" style="color:var(--violet)">obrigatório</span></h2>
        <div class="modal-sub" style="margin-bottom:10px">Revise os parâmetros abaixo antes de iniciar o período. Esta é a última etapa de governança do onboarding.</div>
        ${institConexao}
        ${contaAmbiente}
        ${sistemaRisco}
        ${regrasExternas}
        ${reservasResumo}
        ${caixaResumo}
        ${equityProtectorResumo}
        ${confirmacoes}
        <label style="display:flex; gap:10px; align-items:flex-start; color:var(--ink); font-size:calc(12.5px * var(--fs-scale)); cursor:pointer; margin-top:6px">
          <input type="checkbox" id="obSummaryAccept" style="margin-top:3px; width:auto" ${summaryAccepted?'checked':''}>
          <span>Declaro que revisei os dados acima e confirmo que o período será iniciado com estes parâmetros. Reconheço que expectativa de retorno não é promessa de resultado e que, em caso de conflito entre regras, prevalecerá a regra mais restritiva.</span>
        </label>
        <div class="modal-err" id="obSummaryErr">Revise e confirme o resumo final antes de iniciar o período.</div>
      </div>`;
  }
  function paintRiskStep(){
    const wrap=$('obRiskStepWrap');
    if(!wrap) return;
    if(!canShowRiskProfileStep()){
      wrap.innerHTML='';
      paintEquityProtectorStep();
      return;
    }
    wrap.innerHTML=`
      <div class="card" style="margin:0 0 16px; padding:16px 18px; box-shadow:none; background:var(--panel-2)">
        <h2 style="margin-bottom:8px">Arquitetura de Risco</h2>
        <p style="font-size:calc(12.5px * var(--fs-scale)); color:var(--ink-dim); line-height:1.65">O perfil de risco define o comportamento operacional de toda a conta durante este período. Ele determina o Drawdown Máximo, a redução progressiva da exposição nas quatro fases, a alavancagem permitida e as referências de desempenho. Escolha o perfil pela capacidade de sobreviver ao drawdown, nunca apenas pela expectativa de retorno.</p>
      </div>
      <div class="ql" style="font-size:calc(13px * var(--fs-scale)); margin:4px 0 10px; font-weight:800">Escolha o perfil do período <span class="art" style="font-family:var(--mono);font-size:calc(10px * var(--fs-scale));color:var(--ink-faint)">comparativo essencial</span></div>
      <div id="obProfs" style="display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:12px; margin-bottom:14px"></div>
      <div class="modal-err" id="obProfErr">Selecione o sistema de risco do período antes de iniciar.</div>
      <div id="obRiskImpactWrap"></div>
      <div id="obRiskMatrixWrap"></div>
      <details id="obSimDetails" style="margin:16px 0">
        <summary style="cursor:pointer; font-weight:800; color:var(--ink); padding:12px 14px; border:1px solid var(--line); border-radius:10px; background:var(--panel-2)">Ver Simulação Patrimonial</summary>
        <div style="padding-top:12px">
          <div class="risk-note" style="margin:0 0 12px">As projeções apresentadas possuem finalidade exclusivamente educativa e estatística. Não representam promessa ou garantia de retorno.</div>
          <div id="obSimWrap" style="margin-bottom:16px"></div>
        </div>
      </details>
      <label style="display:flex; gap:10px; align-items:flex-start; color:var(--ink); font-size:calc(12.5px * var(--fs-scale)); cursor:pointer; margin:12px 0 4px; padding:12px 14px; border:1px solid var(--line); border-radius:10px; background:var(--panel-2)">
        <input type="checkbox" id="obRiskProfileAccept" style="margin-top:3px; width:auto" ${riskProfileAccepted?'checked':''}>
        <span>Declaro que escolhi este perfil considerando principalmente minha capacidade de suportar o drawdown e preservar o capital, e não apenas pela expectativa de retorno.</span>
      </label>
      <div class="modal-err" id="obRiskAcceptErr">Confirme a declaração de escolha consciente do perfil de risco.</div>`;
    paintProfs();
    bindRiskAccept();
    paintRiskImpact();
    paintRiskMatrix();
    paintEP();
    paintSim();
    paintEquityProtectorStep();
  }
  function bindRiskAccept(){
    const el=$('obRiskProfileAccept');
    if(el) el.onchange=()=>{
      riskProfileAccepted=el.checked;
      const err=$('obRiskAcceptErr'); if(err) err.classList.remove('show');
      invalidateSummary();
      paintOnboardingRailStatus();
    };
  }
  function paintProfs(){
    if(!canShowRiskProfileStep()) return;
    const list=acctProfiles();
    const visibleProfiles=(profSel && !profListOpen) ? list.filter(pr=>pr.key===profSel) : list;
    $('obProfs').innerHTML=visibleProfiles.map(pr=>{
      const on=pr.key===profSel;
      return `<button type="button" data-obprof="${pr.key}" style="position:relative; text-align:left; padding:16px; border-radius:14px; cursor:pointer;
        border:1.5px solid ${on?'var(--violet)':'var(--line)'}; background:${on?'linear-gradient(180deg,var(--indigo-deep),var(--panel))':'var(--panel)'}; box-shadow:${on?'0 0 0 1px var(--violet), 0 16px 34px rgba(53,101,232,.16)':'none'}; display:grid; gap:13px; min-height:245px; transition:.18s ease">
        ${on?'<span style="position:absolute; right:12px; top:12px; padding:4px 8px; border-radius:999px; background:var(--violet); color:#fff; font-size:calc(9px * var(--fs-scale)); font-weight:800; letter-spacing:.05em; text-transform:uppercase">Perfil selecionado</span>':''}
        <div style="font-weight:900; font-size:calc(15px * var(--fs-scale)); color:${on?'var(--violet)':'var(--ink)'}; padding-right:${on?'110px':'0'}">${pr.name}</div>
        <div style="display:grid; gap:10px">
          <div><div style="font-size:calc(10px * var(--fs-scale)); color:var(--ink-faint); text-transform:uppercase; letter-spacing:.08em">MDD</div><div style="font-family:var(--mono); font-size:calc(24px * var(--fs-scale)); font-weight:900; color:var(--f4); line-height:1.1">${fmtPct(pr.mdd)}</div></div>
          <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px">
            <div><div style="font-size:calc(9px * var(--fs-scale)); color:var(--ink-faint); text-transform:uppercase; letter-spacing:.06em">Alav./ordem</div><div style="font-family:var(--mono); font-size:calc(15px * var(--fs-scale)); color:var(--ink); font-weight:800">${pr.lev!=null?fmtX(pr.lev):'—'}</div></div>
            <div><div style="font-size:calc(9px * var(--fs-scale)); color:var(--ink-faint); text-transform:uppercase; letter-spacing:.06em">Fator</div><div style="font-family:var(--mono); font-size:calc(15px * var(--fs-scale)); color:var(--ink); font-weight:800">${Math.round(pr.pct*100)}%</div></div>
            <div><div style="font-size:calc(9px * var(--fs-scale)); color:var(--ink-faint); text-transform:uppercase; letter-spacing:.06em">Ref. mensal</div><div style="font-family:var(--mono); font-size:calc(15px * var(--fs-scale)); color:var(--ink); font-weight:800">${fmtPct(pr.mensal)}</div></div>
            <div><div style="font-size:calc(9px * var(--fs-scale)); color:var(--ink-faint); text-transform:uppercase; letter-spacing:.06em">Ref. anual</div><div style="font-family:var(--mono); font-size:calc(15px * var(--fs-scale)); color:var(--ink); font-weight:800">${fmtPct(pr.anual)}</div></div>
          </div>
        </div>
      </button>`;
    }).join('');
    box.querySelectorAll('[data-obprof]').forEach(b=>b.addEventListener('click',()=>{
      const nextKey=b.dataset.obprof||'';
      if(nextKey===profSel){
        clearRiskSelection();
      } else {
        profSel=nextKey;
        profListOpen=false;
        riskProfileAccepted=false;
        simCompareMode='current';
      }
      paintProfs();
      const riskAccept=$('obRiskProfileAccept'); if(riskAccept) riskAccept.checked=riskProfileAccepted;
      bindRiskAccept();
      paintRiskImpact();
      paintRiskMatrix();
      paintEP();
      paintSim();
      paintEquityProtectorStep();
      invalidateSummary();
      const profErr=$('obProfErr'); if(profErr && profSel) profErr.classList.remove('show');
    }));
  }
  function paintRiskImpact(){
    const wrap=$('obRiskImpactWrap'); if(!wrap) return;
    if(!profSel){ wrap.innerHTML=''; return; }
    const saldo=parseFloat($('obSaldo').value)||0;
    const pr=getActiveRiskProfile(profSel);
    const {ep,obj}=onboardingEP(saldo, profSel);
    const ddMoney=saldo*pr.mdd;
    const genesisRisk=saldo*(S.params.genRisk||0.01)*pr.pct;
    wrap.innerHTML=`
      <div class="card" style="margin:0 0 16px; padding:16px 18px; box-shadow:none; border-color:var(--violet); background:var(--panel)">
        <h2 style="margin-bottom:12px">Impacto do Perfil Selecionado <span class="art">${esc(pr.name)}</span></h2>
        <div class="metrics" style="grid-template-columns:repeat(auto-fit,minmax(135px,1fr)); gap:10px">
          <div class="metric"><div class="k">Drawdown Máximo</div><div class="v sm" style="color:var(--f4)">${fmtPct(pr.mdd)}</div><div class="sub">${fmtMoney2(ddMoney)}</div></div>
          <div class="metric"><div class="k">Equity mínima</div><div class="v sm" id="obEP" style="color:var(--f4)">${saldo>0?fmtMoney2(ep):'—'}</div><div class="sub">antes da guilhotina</div></div>
          <div class="metric"><div class="k">Ordem Gênese</div><div class="v sm">${fmtMoney2(genesisRisk)}</div><div class="sub">risco programado inicial</div></div>
          <div class="metric"><div class="k">Alavancagem</div><div class="v sm">${pr.lev!=null?fmtX(pr.lev):'—'}</div><div class="sub">por ordem</div></div>
          <div class="metric"><div class="k">Referência mensal</div><div class="v sm" style="color:var(--f1)">${fmtPct(pr.mensal)}</div><div class="sub">não é promessa</div></div>
          <div class="metric"><div class="k">Referência anual</div><div class="v sm" style="color:var(--f1)">${fmtPct(pr.anual)}</div><div class="sub">referência composta</div></div>
          <div class="metric"><div class="k">Objetivo projetado</div><div class="v sm" id="obObj" style="color:var(--f1)">${saldo>0?fmtMoney2(obj):'—'}</div><div class="sub">até o fim do período</div></div>
        </div>
      </div>`;
  }
  function paintRiskMatrix(){
    const wrap=$('obRiskMatrixWrap'); if(!wrap) return;
    if(!profSel){ wrap.innerHTML=''; return; }
    const matrix=activeRiskMatrix(profSel);
    const desc=['Construção da posição','Redução gradual','Proteção do capital','Salvaguarda final'];
    wrap.innerHTML=`
      <div class="card" style="margin:0 0 16px; padding:16px 18px; box-shadow:none; background:var(--panel-2)">
        <h2 style="margin-bottom:12px">Matriz Quadrifásica do Perfil <span class="art">faixas e alavancagem mudam com o perfil</span></h2>
        <div style="display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:10px">
          ${matrix.map((row,i)=>`<div style="border:1px solid var(--line); border-top:3px solid var(--f${i+1}); border-radius:10px; background:var(--panel); padding:12px">
            <div style="font-size:calc(11px * var(--fs-scale)); color:var(--ink-faint); text-transform:uppercase; letter-spacing:.07em">Fase ${i+1}</div>
            <div style="font-family:var(--mono); font-size:calc(15px * var(--fs-scale)); color:var(--ink); font-weight:900; margin-top:6px">${fmtPct(row.ddmin)}–${fmtPct(row.ddmax)}</div>
            <div style="font-family:var(--mono); font-size:calc(13px * var(--fs-scale)); color:var(--violet); font-weight:800; margin-top:6px">${fmtX(row.alav)}</div>
            <div style="font-size:calc(11.5px * var(--fs-scale)); color:var(--ink-dim); margin-top:8px">${desc[i]}</div>
          </div>`).join('')}
        </div>
      </div>`;
  }
  function paintEP(){
    if(!canShowRiskProfileStep()) return;
    const saldo=parseFloat($('obSaldo').value)||0;
    const {ep,obj}=onboardingEP(saldo, profSel||'base');
    if($('obEP')) $('obEP').textContent=saldo>0?fmtMoney2(ep):'—';
    if($('obObj')) $('obObj').textContent=saldo>0?fmtMoney2(obj):'—';
  }
  function onboardingSimSeries(pr, saldoIni, months){
    const mu=pr.anual;
    const sigma=pr.ddrTarget||0;
    const rows=[];
    for(let i=0;i<=months;i++){
      const t=i/12;
      const mean=saldoIni*Math.pow(1+mu,t);
      const st=sigma*Math.sqrt(t);
      rows.push({i, mean, pos:mean*(1+st), neg:mean*(1-st)});
    }
    const end=rows[rows.length-1];
    return {pr, saldoIni, months, mu, sigma, rows, esperado:end.mean, pos1:end.pos, neg1:end.neg, ddMax:pr.scenarioDD15||pr.ddrTarget||0};
  }
  function buildOnboardingSimHTML(saldo){
    const profiles=acctProfiles();
    const selectedKey=profSel||'base';
    const selectedProfile=getActiveRiskProfile(selectedKey);
    const colors={
      base:'var(--violet)',
      longevity:'var(--f1)',
      high_longevity:'var(--f2)',
      high_longevity_plus:'var(--f3)'
    };
    const compareAll=simCompareMode==='all';
    const visualKey=simCompareMode && simCompareMode!=='current' && simCompareMode!=='all' ? simCompareMode : selectedKey;
    const visualProfile=getActiveRiskProfile(visualKey);
    let series=compareAll
      ? profiles.filter(pr=>simCurveVisible[pr.key]!==false).map(pr=>onboardingSimSeries(pr, saldo, simHorizon))
      : [onboardingSimSeries(visualProfile, saldo, simHorizon)];
    if(compareAll && !series.length){
      simCurveVisible[selectedKey]=true;
      series=[onboardingSimSeries(selectedProfile, saldo, simHorizon)];
    }
    const summary=onboardingSimSeries(visualProfile, saldo, simHorizon);
    const W=760,H=270,L=CH.L,R=CH.R,T=CH.T,B=CH.B+10;
    const allVals=series.flatMap(s=>s.rows.map(r=>r.mean));
    const yminBase=Math.min(saldo,...allVals);
    const ymaxBase=Math.max(saldo,...allVals);
    let ymin=yminBase, ymax=ymaxBase;
    const pad=(ymax-ymin)*0.14||Math.max(1,ymax*0.04); ymin-=pad; ymax+=pad;
    const X=i=>L+(i/simHorizon)*(W-L-R);
    const Y=v=>T+(1-(v-ymin)/((ymax-ymin)||1))*(H-T-B);
    const path=rows=>rows.map((r,i)=>(i?'L':'M')+X(r.i).toFixed(1)+' '+Y(r.mean).toFixed(1)).join(' ');
    const lastLabel=s=>{
      const end=s.rows[s.rows.length-1];
      return `<circle cx="${X(end.i).toFixed(1)}" cy="${Y(end.mean).toFixed(1)}" r="${s.pr.key===selectedKey?3.5:2.5}" fill="${colors[s.pr.key]||'var(--violet)'}"/>
        ${compareAll?`<text x="${Math.max(L+80,W-R-4)}" y="${Y(end.mean).toFixed(1)}" text-anchor="end" font-size="9" fill="var(--ink-faint)">${esc(s.pr.name)}</text>`:''}`;
    };
    const mainLine=series.map(s=>{
      const actual=s.pr.key===selectedKey;
      const activeSingle=!compareAll || s.pr.key===visualKey;
      return `<path d="${path(s.rows)}" fill="none" stroke="${colors[s.pr.key]||'var(--violet)'}" stroke-width="${actual?3:1.6}" opacity="${actual||activeSingle?'.96':'.38'}" style="transition:opacity .24s ease, stroke-width .24s ease"/>${lastLabel(s)}`;
    }).join('');
    const hTicks=[0,Math.round(simHorizon/4),Math.round(simHorizon/2),Math.round(simHorizon*3/4),simHorizon].filter((v,i,a)=>a.indexOf(v)===i);
    const xLabels=hTicks.map(i=>`<text x="${X(i).toFixed(1)}" y="${H-10}" text-anchor="middle" font-size="10" fill="var(--ink-faint)">${i}m</text>`).join('');
    const yStart=Y(saldo).toFixed(1);
    const grid=CH.gridY(W,L,R,Y,CH.ticks(ymin,ymax,4),fmtMoney);
    // Área sob a curva do perfil em foco (não em modo comparação, onde poluiria).
    const focus=series.find(s=>s.pr.key===visualKey)||series[0];
    const focusArea=(!compareAll&&focus)
      ? `<path d="${CH.area(path(focus.rows),X(0),X(simHorizon),H-B)}" fill="${colors[focus.pr.key]||'var(--violet)'}" opacity=".14"/>` : '';
    const endFocus=focus?focus.rows[focus.rows.length-1]:null;
    const stats=endFocus?CH.stats(L,T,[
      {mark:'□', label:'Esperado', value:fmtMoney(endFocus.mean), color:colors[focus.pr.key]||'var(--violet)'},
      {mark:'–', label:'Inicial',  value:fmtMoney(saldo),         color:'var(--ink-dim)'},
      {mark:'↑', label:'Horizonte',value:simHorizon+' meses',     color:'var(--data-drv)'},
    ]):'';
    const svg=`<svg viewBox="0 0 ${W} ${H}" style="width:100%;height:auto;font-family:var(--mono);overflow:visible">
      <rect x="${L}" y="${T}" width="${W-L-R}" height="${H-T-B}" fill="var(--bg)"/>
      ${grid}
      <line x1="${L}" x2="${W-R}" y1="${yStart}" y2="${yStart}" stroke="var(--ink-faint)" stroke-dasharray="2 3" opacity=".7"/>
      ${focusArea}
      ${mainLine}
      ${xLabels}
      ${endFocus?CH.callout(W,R,Y(endFocus.mean),fmtMoney(endFocus.mean),colors[focus.pr.key]||'var(--violet)'):''}
      ${stats}
    </svg>`;
    const horizonBtns=[12,24,60,120].map(m=>`<button type="button" data-ob-sim-horizon="${m}" style="border:1px solid ${simHorizon===m?'var(--violet)':'var(--line)'}; background:${simHorizon===m?'var(--indigo-deep)':'var(--panel)'}; color:${simHorizon===m?'var(--violet)':'var(--ink-dim)'}; border-radius:999px; padding:7px 10px; font-weight:800; font-size:calc(11px * var(--fs-scale)); cursor:pointer">${m} meses</button>`).join('');
    const compareBtns=[
      {key:'current', label:'Perfil Atual'},
      ...profiles.map(pr=>({key:pr.key, label:pr.name})),
      {key:'all', label:'Comparar Todos'}
    ].map(item=>`<button type="button" data-ob-sim-profile="${item.key}" style="border:1px solid ${simCompareMode===item.key?'var(--violet)':'var(--line)'}; background:${simCompareMode===item.key?'var(--indigo-deep)':'var(--panel)'}; color:${simCompareMode===item.key?'var(--violet)':'var(--ink-dim)'}; border-radius:999px; padding:7px 10px; font-weight:800; font-size:calc(11px * var(--fs-scale)); cursor:pointer">${esc(item.label)}</button>`).join('');
    const legend=compareAll?`<div style="display:flex; gap:8px; flex-wrap:wrap; margin:10px 0 0">
      ${profiles.map(pr=>`<button type="button" data-ob-sim-legend="${pr.key}" style="display:flex; align-items:center; gap:6px; border:1px solid var(--line); background:${simCurveVisible[pr.key]===false?'rgba(255,255,255,.02)':'var(--panel)'}; color:${simCurveVisible[pr.key]===false?'var(--ink-faint)':'var(--ink-dim)'}; border-radius:999px; padding:6px 9px; font-size:calc(11px * var(--fs-scale)); cursor:pointer; opacity:${simCurveVisible[pr.key]===false?'.52':'1'}"><span style="width:8px;height:8px;border-radius:50%;background:${colors[pr.key]||'var(--violet)'}; display:inline-block"></span>${esc(pr.name)}${pr.key===selectedKey?' · atual':''}</button>`).join('')}
    </div>`:'';
    const growth=(summary.esperado/saldo)-1;
    const titleProfile=compareAll?'Todos os perfis':visualProfile.name;
    return `<div class="card" style="margin:0; padding:16px 18px; box-shadow:none; background:var(--panel)">
      <h2 style="margin-bottom:6px">Simulação Patrimonial <span class="art">${esc(titleProfile)} · ${simHorizon} meses</span></h2>
      <p style="font-size:calc(12.5px * var(--fs-scale)); color:var(--ink-dim); line-height:1.6; margin-bottom:14px">Esta simulação apresenta uma projeção matemática baseada no perfil de risco selecionado. Ela possui finalidade educativa e comparativa, não representa promessa ou garantia de retorno.</p>
      <div style="display:flex; flex-wrap:wrap; gap:8px; align-items:center; justify-content:space-between; margin-bottom:12px">
        <div style="display:flex; gap:7px; flex-wrap:wrap"><span style="align-self:center; color:var(--ink-faint); font-size:calc(10px * var(--fs-scale)); text-transform:uppercase; letter-spacing:.08em; font-weight:800">Horizonte</span>${horizonBtns}</div>
      </div>
      <div style="display:flex; gap:7px; flex-wrap:wrap; margin-bottom:14px"><span style="align-self:center; color:var(--ink-faint); font-size:calc(10px * var(--fs-scale)); text-transform:uppercase; letter-spacing:.08em; font-weight:800">Comparar Perfil</span>${compareBtns}</div>
      <div style="border:1px solid var(--line); border-radius:14px; background:linear-gradient(180deg,var(--panel-2),var(--panel)); padding:14px; transition:.24s ease">
        ${svg}
        ${legend}
      </div>
      <div class="metrics" style="grid-template-columns:repeat(auto-fit,minmax(140px,1fr)); gap:10px; margin-top:14px">
        <div class="metric"><div class="k">Saldo Inicial</div><div class="v sm">${fmtMoney2(saldo)}</div><div class="sub">base da projeção</div></div>
        <div class="metric"><div class="k">Patrimônio Projetado</div><div class="v sm">${fmtMoney2(summary.esperado)}</div><div class="sub">${esc(visualProfile.name)}</div></div>
        <div class="metric"><div class="k">Crescimento Percentual</div><div class="v sm" style="color:var(--f1)">${fmtPct(growth)}</div><div class="sub">${simHorizon} meses</div></div>
        <div class="metric"><div class="k">Rentabilidade Média</div><div class="v sm">${fmtPct(visualProfile.mensal)}</div><div class="sub">referência mensal do perfil</div></div>
      </div>
      <p style="font-size:calc(11px * var(--fs-scale));color:var(--ink-faint);line-height:1.6;margin-top:12px">As curvas apresentadas representam projeções matemáticas baseadas nos parâmetros do perfil selecionado. Elas não constituem promessa de rentabilidade nem previsão de desempenho futuro.</p>
    </div>`;
  }
  function buildOnboardingMEISimHTML(saldo){
    const profiles=acctProfiles(), selectedKey=profSel||'base';
    const visualKey=simCompareMode && simCompareMode!=='current' && simCompareMode!=='all' ? simCompareMode : selectedKey;
    const compareAll=simCompareMode==='all';
    const keys=compareAll?profiles.map(p=>p.key):[visualKey];
    const results=keys.map(key=>runMEIMonteCarlo({startingEquity:saldo,profileKey:key,horizonMonths:simHorizon})).filter(r=>r.enabled);
    const focus=results.find(r=>r.pr.key===visualKey)||runMEIMonteCarlo({startingEquity:saldo,profileKey:visualKey,horizonMonths:simHorizon});
    if(!focus.enabled) return `<div class="risk-note" style="margin:0;color:var(--f2);border-color:var(--f2)">${esc(focus.reason)}</div>`;
    const W=760,H=285,L=CH.L,R=CH.R,T=CH.T,B=CH.B+12, n=focus.horizonMonths;
    const allY=[saldo,saldo*(1-focus.pr.mdd),...focus.lowerBand,...focus.upperBand,...results.flatMap(r=>r.medianPath)];
    let ymin=Math.min(...allY),ymax=Math.max(...allY),pad=(ymax-ymin)*.10||Math.max(1,ymax*.04); ymin-=pad;ymax+=pad;
    const X=i=>L+(i/n)*(W-L-R), Y=v=>T+(1-(v-ymin)/((ymax-ymin)||1))*(H-T-B);
    const line=arr=>arr.map((v,i)=>(i?'L':'M')+X(i).toFixed(1)+' '+Y(v).toFixed(1)).join(' ');
    const area=(top,bot)=>line(top)+' '+bot.slice().reverse().map((v,i)=>'L'+X(n-i).toFixed(1)+' '+Y(v).toFixed(1)).join(' ')+' Z';
    const colors={base:'var(--violet)',longevity:'var(--f1)',high_longevity:'var(--f2)',high_longevity_plus:'var(--f3)'};
    const focusColor=colors[focus.pr.key]||'var(--violet)';
    const medians=results.map(r=>`<path d="${line(r.medianPath)}" fill="none" stroke="${colors[r.pr.key]||'var(--violet)'}" stroke-width="${r.pr.key===selectedKey?3:1.5}" opacity="${r.pr.key===selectedKey?'.96':'.5'}"/>`).join('');
    const mddEquity=saldo*(1-focus.pr.mdd), mddY=Y(mddEquity).toFixed(1);
    const endMed=focus.medianPath[focus.medianPath.length-1];
    const svg=`<svg viewBox="0 0 ${W} ${H}" style="width:100%;height:auto;font-family:var(--mono)">
      <rect x="${L}" y="${T}" width="${W-L-R}" height="${H-T-B}" fill="var(--bg)"/>
      ${CH.gridY(W,L,R,Y,CH.ticks(ymin,ymax,4),fmtMoney)}
      <path d="${area(focus.upperBand,focus.lowerBand)}" fill="${focusColor}" opacity=".10"/>
      <path d="${area(focus.upperInnerBand,focus.lowerInnerBand)}" fill="${focusColor}" opacity=".19"/>
      <line x1="${L}" x2="${W-R}" y1="${Y(saldo).toFixed(1)}" y2="${Y(saldo).toFixed(1)}" stroke="var(--ink-faint)" stroke-dasharray="2 3" opacity=".7"/>
      ${CH.limit(W,L,R,mddY,'MDD '+fmtPct(focus.pr.mdd),'var(--danger)')}
      ${medians}
      ${[0,Math.round(n/4),Math.round(n/2),Math.round(n*3/4),n].filter((v,i,a)=>a.indexOf(v)===i).map(i=>`<text x="${X(i).toFixed(1)}" y="${H-9}" text-anchor="middle" font-size="8.5" fill="var(--ink-faint)">${i}m</text>`).join('')}
      ${CH.callout(W,R,Y(endMed),fmtMoney(endMed),focusColor)}
      ${CH.stats(L,T,[
        {mark:'□', label:'Mediana',  value:fmtMoney(endMed),                                            color:focusColor},
        {mark:'↑', label:'Banda sup',value:fmtMoney(focus.upperBand[focus.upperBand.length-1]),         color:'var(--f1)'},
        {mark:'↓', label:'Banda inf',value:fmtMoney(focus.lowerBand[focus.lowerBand.length-1]),         color:'var(--f4)'},
        {mark:'–', label:'Piso MDD', value:fmtMoney(mddEquity),                                         color:'var(--danger)'},
      ])}
    </svg>`;
    const title=compareAll?'Comparar Todos':focus.pr.name;
    return `<div class="card" style="margin:0;padding:16px 18px;box-shadow:none;background:var(--panel)">
      <h2 style="margin-bottom:6px">Simulação de Risco — MEI-JP <span class="art">${esc(title)} · ${simHorizon} meses</span></h2>
      <p style="font-size:calc(12px * var(--fs-scale));color:var(--ink-dim);line-height:1.6;margin-bottom:12px">Mediana das trajetórias, banda interna de 25–75% e banda externa de ${Math.round((1-focus.confidenceLevel)*50)}–${Math.round((1+focus.confidenceLevel)*50)}%. A dispersão vem apenas do CID e/ou da curva patrimonial registrada.</p>
      <div style="border:1px solid var(--line);border-radius:14px;background:var(--panel-2);padding:12px">${svg}</div>
      <div class="metrics" style="grid-template-columns:repeat(auto-fit,minmax(145px,1fr));gap:10px;margin-top:14px">
        <div class="metric"><div class="k">Patrimônio mediano final</div><div class="v sm">${fmtMoney2(focus.finalMedian)}</div><div class="sub">${focus.simulationCount.toLocaleString('pt-BR')} trajetórias</div></div>
        <div class="metric"><div class="k">Faixa externa final</div><div class="v sm">${fmtMoney2(focus.finalLower)}–${fmtMoney2(focus.finalUpper)}</div><div class="sub">nível de confiança configurado</div></div>
        <div class="metric"><div class="k">Prob. abaixo do inicial</div><div class="v sm" style="color:var(--f2)">${fmtPct(focus.probabilityBelowInitial)}</div><div class="sub">na data final</div></div>
        <div class="metric"><div class="k">Prob. tocar MDD</div><div class="v sm" style="color:var(--f4)">${fmtPct(focus.probabilityTouchMDD)}</div><div class="sub">ao longo da trajetória</div></div>
        <div class="metric"><div class="k">DD máximo mediano</div><div class="v sm">${fmtPct(focus.medianMaxDrawdown)}</div><div class="sub">percentil alto ${fmtPct(focus.percentileMaxDrawdown)}</div></div>
        <div class="metric"><div class="k">Modelo</div><div class="v sm">${meiStageLabel(focus.modelStage)}</div><div class="sub">σ ${fmtPct(focus.sigmaUsed)} · amostra ${meiQuality(focus.stats.observations)}</div></div>
      </div>
      <p style="font-size:calc(11px * var(--fs-scale));color:var(--ink-dim);line-height:1.7;margin-top:12px;font-family:var(--mono)">Calibração: CID ${fmtPct(focus.cid)} (peso ${fmtPct(focus.institutionalWeight||0)}) · σ histórica ${focus.stats.observations>1?fmtPct(focus.historicalSigma):'—'} (peso ${fmtPct(focus.historicalWeight||0)}) → σ final ${fmtPct(focus.sigmaUsed)} · ${focus.stats.observations} retorno(s) válido(s)${focus.stats.excludedReturns?` · ${focus.stats.excludedReturns} excluído(s)`:''} · fluxos externos: ${focus.stats.flowsPresent?'sim (retornos ajustados)':'não'}${S.mei&&S.mei.lastCalibrationAt?` · última calibração ${String(S.mei.lastCalibrationAt).slice(0,10)}`:''}</p>
      ${focus.stats.flowsPresent?'<p style="font-size:calc(11px * var(--fs-scale));color:var(--f2);line-height:1.6;margin-top:8px">O histórico contém fluxos externos. Os retornos utilizados foram ajustados para evitar que aportes sejam interpretados como lucro e retiradas como prejuízo.</p>':''}
      ${focus.stats.excludedReturns?'<p style="font-size:calc(11px * var(--fs-scale));color:var(--f2);line-height:1.6;margin-top:8px">Existem registros históricos preservados que não foram utilizados na calibração por inconsistência matemática ou ausência de dados válidos.</p>':''}
      <p style="font-size:calc(11px * var(--fs-scale));color:var(--ink-faint);line-height:1.6;margin-top:8px">As projeções são exclusivamente educativas e estatísticas. Não representam promessa, recomendação ou garantia de retorno. Estimativas sujeitas a revisão conforme a amostra evolui.</p>
    </div>`;
  }
  // Simulação patrimonial ±1σ + linha de MDD hard-stop, em PREVIEW (perfil/saldo ainda não
  // confirmados) — usa o mesmo motor da Contabilidade (buildSimHTML/patrimonialSimCore).
  function paintSim(){
    const box2=$('obSimWrap'); if(!box2) return;
    if(!canShowRiskProfileStep()){
      box2.innerHTML='';
      return;
    }
    const saldo=parseFloat($('obSaldo').value)||0;
    if(!(saldo>0)){
      box2.innerHTML='<p class="muted" style="font-size:calc(12px * var(--fs-scale))">Informe o saldo de início do período para ver a simulação de retorno e drawdown deste perfil.</p>';
      return;
    }
    if(!profSel){
      box2.innerHTML='<p class="muted" style="font-size:calc(12px * var(--fs-scale))">Selecione um perfil de risco para visualizar a simulação patrimonial comparativa.</p>';
      return;
    }
    const calibration=meiCalibration(profSel);
    const modeButtons=`<div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px"><button type="button" data-ob-sim-mode="reference" style="border:1px solid ${simMode==='reference'?'var(--violet)':'var(--line)'};background:${simMode==='reference'?'var(--indigo-deep)':'var(--panel)'};color:${simMode==='reference'?'var(--violet)':'var(--ink-dim)'};border-radius:999px;padding:7px 11px;font-weight:800;font-size:calc(11px * var(--fs-scale));cursor:pointer">Referência</button><button type="button" data-ob-sim-mode="risk" ${calibration.enabled?'':'disabled'} title="${calibration.enabled?'':'Configure o CID do perfil no MEI-JP'}" style="border:1px solid ${simMode==='risk'?'var(--violet)':'var(--line)'};background:${simMode==='risk'?'var(--indigo-deep)':'var(--panel)'};color:${simMode==='risk'?'var(--violet)':'var(--ink-dim)'};border-radius:999px;padding:7px 11px;font-weight:800;font-size:calc(11px * var(--fs-scale));cursor:${calibration.enabled?'pointer':'not-allowed'};opacity:${calibration.enabled?'1':'.5'}">Risco — MEI-JP</button>${simMode==='risk'?'<button type="button" data-ob-mei-rerun="1" style="margin-left:auto;border:1px solid var(--line);background:var(--panel);color:var(--ink-dim);border-radius:999px;padding:7px 11px;font-weight:800;font-size:calc(11px * var(--fs-scale));cursor:pointer">Gerar nova simulação</button>':''}</div>`;
    box2.innerHTML=modeButtons+(simMode==='risk'?buildOnboardingMEISimHTML(saldo):buildOnboardingSimHTML(saldo));
    box2.querySelectorAll('[data-ob-sim-mode]').forEach(btn=>btn.addEventListener('click',()=>{ if(btn.disabled) return; simMode=btn.dataset.obSimMode; paintSim(); }));
    const rerun=box2.querySelector('[data-ob-mei-rerun]'); if(rerun) rerun.addEventListener('click',()=>paintSim());
    box2.querySelectorAll('[data-ob-sim-horizon]').forEach(btn=>btn.addEventListener('click',()=>{
      simHorizon=parseInt(btn.dataset.obSimHorizon,10)||12;
      paintSim();
    }));
    box2.querySelectorAll('[data-ob-sim-profile]').forEach(btn=>btn.addEventListener('click',()=>{
      simCompareMode=btn.dataset.obSimProfile||'current';
      paintSim();
    }));
    box2.querySelectorAll('[data-ob-sim-legend]').forEach(btn=>btn.addEventListener('click',()=>{
      const key=btn.dataset.obSimLegend||'';
      if(key) simCurveVisible[key]=simCurveVisible[key]===false;
      paintSim();
    }));
  }
  document.getElementById('obEstatutoToggle').addEventListener('click',()=>{
    const rd=document.getElementById('obEstatutoReader');
    const open=rd.style.display!=='none';
    if(!open && !rd.textContent) rd.textContent=ESTATUTO_V10_FULLTEXT;
    rd.style.display=open?'none':'block';
    document.getElementById('obEstatutoToggle').textContent=(open?'▸':'▾')+' Ler o Estatuto V10.0 (texto completo, 34 páginas)';
  });
  paintBrokers(); paintRiskStep(); paintReservesStep(); paintCentralCashStep(); paintEquityProtectorStep(); paintSummary();
  const obDateWrap = $('obDateWrap');
  const obDateEl = $('obData');
  const obDatePanel = $('obDatePanel');
  const obDateStartTxt = $('obDateStartTxt');
  const obDateEndTxt = $('obDateEndTxt');
  let obDateOutsideHandler = null;
  let obPlatformOutsideHandler = null;
  let obLevOutsideHandler = null;
  const syncDateInfo = ()=>{
    if(!obDateEl) return;
    const start = obDateEl.value || todayISO();
    if(obDateStartTxt) obDateStartTxt.textContent = fmtDateEU(start);
    if(obDateEndTxt) obDateEndTxt.textContent = fmtDateEU(projectCycleEndISO(start));
  };
  const syncDatePlacement = ()=>{
    if(!obDateWrap || !obDatePanel) return;
    obDateWrap.classList.remove('open-up');
    const wrapRect = obDateWrap.getBoundingClientRect();
    const panelHeight = obDatePanel.offsetHeight || 220;
    const roomBelow = window.innerHeight - wrapRect.bottom;
    const roomAbove = wrapRect.top;
    if(roomBelow < panelHeight + 14 && roomAbove > roomBelow){
      obDateWrap.classList.add('open-up');
    }
  };
  const setDateGuide = (open)=>{
    if(!obDateWrap) return;
    obDateWrap.classList.toggle('open', !!open);
    if(open){ syncDateInfo(); syncDatePlacement(); }
    else obDateWrap.classList.remove('open-up');
  };
  function syncPlatformPlacement(){
    if(!obPlatformWrap || !obPlatformPanel) return;
    obPlatformWrap.classList.remove('open-up');
    const wrapRect = obPlatformWrap.getBoundingClientRect();
    const panelHeight = obPlatformPanel.offsetHeight || 220;
    const roomBelow = window.innerHeight - wrapRect.bottom;
    const roomAbove = wrapRect.top;
    if(roomBelow < panelHeight + 14 && roomAbove > roomBelow){
      obPlatformWrap.classList.add('open-up');
    }
  }
  function setPlatformGuide(open){
    if(!obPlatformWrap || !obPlatformTrigger) return;
    obPlatformWrap.classList.toggle('open', !!open);
    if(open) syncPlatformPlacement();
    else obPlatformWrap.classList.remove('open-up');
    obPlatformTrigger.setAttribute('aria-expanded', open ? 'true' : 'false');
  }
  function syncLevPlacement(){
    if(!obAlavWrap || !obAlavPanel) return;
    obAlavWrap.classList.remove('open-up');
    const wrapRect = obAlavWrap.getBoundingClientRect();
    const panelHeight = obAlavPanel.offsetHeight || 250;
    const roomBelow = window.innerHeight - wrapRect.bottom;
    const roomAbove = wrapRect.top;
    if(roomBelow < panelHeight + 14 && roomAbove > roomBelow){
      obAlavWrap.classList.add('open-up');
    }
  }
  function setLevGuide(open){
    if(!obAlavWrap || !obAlavTrigger) return;
    obAlavWrap.classList.toggle('open', !!open);
    if(open) syncLevPlacement();
    else obAlavWrap.classList.remove('open-up');
    obAlavTrigger.setAttribute('aria-expanded', open ? 'true' : 'false');
  }
  function setLevExplain(open){
    if(!obLeverageExplain || !obLeverageExplainToggle) return;
    obLeverageExplain.style.display = open ? 'block' : 'none';
    obLeverageExplainToggle.textContent = open ? 'Ocultar explicação sobre alavancagem' : 'Ver explicação sobre alavancagem';
    obLeverageExplainToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
  }
  function bindPlatformLeverageFields(){
    obPlatformWrap=$('obPlatformWrap'); obPlatformEl=$('obPlataforma'); obPlatformTrigger=$('obPlatformTrigger'); obPlatformPanel=$('obPlatformPanel');
    obAlavWrap=$('obAlavWrap'); obAlavEl=$('obAlav'); obAlavTrigger=$('obAlavTrigger'); obAlavPanel=$('obAlavPanel');
    obLeverageExplain=$('obLeverageExplain'); obLeverageExplainToggle=$('obLeverageExplainToggle');
    if(obPlatformEl){
      obPlatformEl.addEventListener('focus',()=>setPlatformGuide(true));
      obPlatformEl.addEventListener('click',()=>setPlatformGuide(true));
      obPlatformEl.addEventListener('input',()=>{
        plataforma=obPlatformEl.value;
        setPlatformGuide(true);
        if(!hasCompleteConnectionData()) clearRiskSelection();
        paintRiskStep();
        invalidateSummary();
      });
      obPlatformEl.addEventListener('keydown',(e)=>{ if(e.key==='Escape') setPlatformGuide(false); });
    }
    if(obPlatformTrigger) obPlatformTrigger.addEventListener('click',()=>{
      const next = !obPlatformWrap.classList.contains('open');
      setPlatformGuide(next);
      if(next && obPlatformEl) obPlatformEl.focus();
    });
    if(obPlatformWrap) obPlatformWrap.addEventListener('focusout',()=>{
      requestAnimationFrame(()=>{
        if(!obPlatformWrap.contains(document.activeElement)) setPlatformGuide(false);
      });
    });
    if(obAlavEl){
      obAlavEl.addEventListener('focus',()=>setLevGuide(true));
      obAlavEl.addEventListener('click',()=>setLevGuide(true));
      obAlavEl.addEventListener('input',()=>{
        alavCorretora=obAlavEl.value;
        setLevGuide(true);
        if(!hasCompleteConnectionData()) clearRiskSelection();
        paintRiskStep();
        invalidateSummary();
      });
      obAlavEl.addEventListener('keydown',(e)=>{ if(e.key==='Escape'){ setLevGuide(false); setLevExplain(false); } });
    }
    if(obAlavTrigger) obAlavTrigger.addEventListener('click',()=>{
      const next = !obAlavWrap.classList.contains('open');
      setLevGuide(next);
      if(next && obAlavEl) obAlavEl.focus();
    });
    if(obAlavWrap) obAlavWrap.addEventListener('focusout',()=>{
      requestAnimationFrame(()=>{
        if(!obAlavWrap.contains(document.activeElement)){
          setLevGuide(false);
          setLevExplain(false);
        }
      });
    });
    if(obLeverageExplainToggle) obLeverageExplainToggle.addEventListener('click',()=>{
      const open = obLeverageExplain && obLeverageExplain.style.display !== 'none';
      setLevExplain(!open);
      setLevGuide(true);
    });
    box.querySelectorAll('[data-levpreset]').forEach(btn=>btn.addEventListener('click',()=>{
      const val = btn.dataset.levpreset || '';
      if(obAlavEl){
        obAlavEl.value = val;
        obAlavEl.dispatchEvent(new Event('input', { bubbles:true }));
      }
      setLevGuide(false);
      setLevExplain(false);
    }));
    box.querySelectorAll('[data-platformpreset]').forEach(btn=>btn.addEventListener('click',()=>{
      const val = btn.dataset.platformpreset || '';
      if(obPlatformEl){
        obPlatformEl.value = normalizePlatformName(val);
        obPlatformEl.dispatchEvent(new Event('input', { bubbles:true }));
      }
      setPlatformGuide(false);
    }));
  }
  syncDateInfo();
  if(obDateEl){
    obDateEl.addEventListener('focus',()=>setDateGuide(true));
    obDateEl.addEventListener('click',()=>setDateGuide(true));
    obDateEl.addEventListener('input',()=>{ syncDateInfo(); setDateGuide(true); paintEquityProtectorStep(); invalidateSummary(); });
    obDateEl.addEventListener('change',()=>{ syncDateInfo(); setDateGuide(true); paintEquityProtectorStep(); invalidateSummary(); });
    obDateEl.addEventListener('keydown',(e)=>{ if(e.key==='Escape') setDateGuide(false); });
  }
  if(obDateWrap) obDateWrap.addEventListener('focusout',()=>{
    requestAnimationFrame(()=>{
      if(!obDateWrap.contains(document.activeElement)) setDateGuide(false);
    });
  });
  obDateOutsideHandler = (e)=>{
    if(!obDateWrap || !obDateWrap.classList.contains('open')) return;
    if(obDateWrap.contains(e.target)) return;
    setDateGuide(false);
  };
  obPlatformOutsideHandler = (e)=>{
    if(!obPlatformWrap || !obPlatformWrap.classList.contains('open')) return;
    if(obPlatformWrap.contains(e.target)) return;
    setPlatformGuide(false);
  };
  obLevOutsideHandler = (e)=>{
    if(!obAlavWrap || !obAlavWrap.classList.contains('open')) return;
    if(obAlavWrap.contains(e.target)) return;
    setLevGuide(false);
    setLevExplain(false);
  };
  window.__cleanupOnboardingModalUI = ()=>{
    document.removeEventListener('pointerdown', obDateOutsideHandler);
    document.removeEventListener('pointerdown', obPlatformOutsideHandler);
    document.removeEventListener('pointerdown', obLevOutsideHandler);
    window.removeEventListener('resize', syncDatePlacement);
    window.removeEventListener('resize', syncPlatformPlacement);
    window.removeEventListener('resize', syncLevPlacement);
    window.removeEventListener('scroll', syncDatePlacement, true);
    window.removeEventListener('scroll', syncPlatformPlacement, true);
    window.removeEventListener('scroll', syncLevPlacement, true);
  };
  document.addEventListener('pointerdown', obDateOutsideHandler);
  document.addEventListener('pointerdown', obPlatformOutsideHandler);
  document.addEventListener('pointerdown', obLevOutsideHandler);
  window.addEventListener('resize', syncDatePlacement);
  window.addEventListener('resize', syncPlatformPlacement);
  window.addEventListener('resize', syncLevPlacement);
  window.addEventListener('scroll', syncDatePlacement, true);
  window.addEventListener('scroll', syncPlatformPlacement, true);
  window.addEventListener('scroll', syncLevPlacement, true);
  $('obSaldo').addEventListener('input', ()=>{ paintEP(); paintSim(); updateReservesUI(); paintEquityProtectorStep(); invalidateSummary(); });
  $('obMoedaBase').addEventListener('change', ()=>{ paintEquityProtectorStep(); invalidateSummary(); });
  $('obConsent').addEventListener('change',()=>{ if($('obConsent').checked) $('obConsentErr').classList.remove('show'); invalidateSummary(); });
  // Etapa Base de Dados (JPW-HJFGDE §5/§6): termo obrigatório + pasta padrão opcional.
  const obDbRespEl=$('obDbResp');
  if(obDbRespEl) obDbRespEl.addEventListener('change',()=>{ if(obDbRespEl.checked){ const e1=$('obDbRespErr'); if(e1) e1.classList.remove('show'); } invalidateSummary(); });
  const obDgSlot=$('obDgFolderSlot');
  if(obDgSlot && typeof renderDgFolderPanel==='function') renderDgFolderPanel(obDgSlot);
  if($('modalCancel')) $('modalCancel').addEventListener('click', closeModal);
  $('modalConfirm').addEventListener('click',()=>{
    const saldo=parseFloat($('obSaldo').value)||0;
    const loginVal=hasSelectedInstitution() ? String(($('obBrokerLogin')&&$('obBrokerLogin').value)||brokerLogin||'').trim() : '';
    const passVal=hasSelectedInstitution() ? String(($('obInvestorPassword')&&$('obInvestorPassword').value)||investorPassword||'').trim() : '';
    const serverVal=hasSelectedInstitution() ? String(($('obBrokerServer')&&$('obBrokerServer').value)||brokerServer||'').trim() : '';
    const plataformaVal=hasSelectedInstitution() ? normalizePlatformName(String(($('obPlataforma')&&$('obPlataforma').value)||plataforma||'').trim()) : '';
    const alavVal=hasSelectedInstitution() ? String(($('obAlav')&&$('obAlav').value)||alavCorretora||'').trim() : '';
    const isPropFlow = institutionType==='prop' && hasSelectedInstitution();
    const propDailyVal = isPropFlow ? String(($('obPropDaily')&&$('obPropDaily').value)||propDailyDrawdown||'').trim() : '';
    const propMaxVal = isPropFlow ? String(($('obPropMax')&&$('obPropMax').value)||propMaxDrawdown||'').trim() : '';
    const propTrailingRuleVal = isPropFlow ? String(($('obPropTrailingRule')&&$('obPropTrailingRule').value)||propTrailingRule||'').trim() : '';
    const propTrailingDescVal = isPropFlow ? String(($('obPropTrailingDesc')&&$('obPropTrailingDesc').value)||propTrailingDescription||'').trim() : '';
    const propProfitVal = isPropFlow ? String(($('obPropProfitTarget')&&$('obPropProfitTarget').value)||propProfitTarget||'').trim() : '';
    const propMinDaysVal = isPropFlow ? String(($('obPropMinDays')&&$('obPropMinDays').value)||propMinTradingDays||'').trim() : '';
    const propAbsenceVal = isPropFlow ? String(($('obPropAbsence')&&$('obPropAbsence').value)||propAbsenceRules||'').trim() : '';
    const restrictiveVal = isPropFlow ? ($('obPropRestrictive') ? $('obPropRestrictive').checked : restrictiveRuleAccepted) : false;
    // JPW-HJFGDE §5: sem o termo de responsabilidade da base, a configuração inicial não
    // conclui. O gate vem antes do consentimento porque a etapa 07 precede a 08 — o
    // operador é levado à primeira pendência na ordem do formulário.
    if(!($('obDbResp')&&$('obDbResp').checked)){ showOnboardingStep('database'); const e1=$('obDbRespErr'); if(e1) e1.classList.add('show'); return; }
    if(!$('obConsent').checked){ showOnboardingStep('consent'); $('obConsentErr').classList.add('show'); return; }
    if(!String(($('obOperador')&&$('obOperador').value)||'').trim()){ showOnboardingStep('ident'); alert('Informe o nome do operador.'); return; }
    if(!String(($('obSupervisor')&&$('obSupervisor').value)||'').trim()){ showOnboardingStep('ident'); alert('Informe o nome do supervisor(a).'); return; }
    if(!(saldo>0)){ showOnboardingStep('ident'); alert('Informe o saldo de início do período.'); return; }
    if(!isEditMode && !($('obData')&&$('obData').value)){ showOnboardingStep('ident'); alert('Informe a data de início do período.'); return; }
    if(!hasSelectedInstitution()){ showOnboardingStep('instit'); $('obBrokerErr').classList.add('show'); return; }
    if(hasSelectedInstitution() && !(loginVal && passVal && serverVal && plataformaVal && alavVal)){
      showOnboardingStep('instit');
      const credsErr=$('obBrokerCredErr');
      if(credsErr) credsErr.classList.add('show');
      alert('Preencha todos os dados de conexão da conta antes de escolher o sistema de risco.');
      return;
    }
    if(isPropFlow && !(propDailyVal && propMaxVal)){
      showOnboardingStep('instit');
      const rulesErr=$('obPropRulesErr');
      if(rulesErr) rulesErr.classList.add('show');
      alert('Preencha as regras externas obrigatórias da mesa proprietária antes de escolher o sistema de risco.');
      return;
    }
    if(isPropFlow && !restrictiveVal){
      showOnboardingStep('instit');
      const restrErr=$('obPropRestrictiveErr');
      if(restrErr) restrErr.classList.add('show');
      alert('Confirme que, em caso de conflito, prevalecerá a regra mais restritiva.');
      return;
    }
    if(!canShowRiskProfileStep()){
      showOnboardingStep('instit');
      alert('Preencha os dados de conexão da conta antes de escolher o sistema de risco.');
      return;
    }
    if(!profSel){
      showOnboardingStep('risk');
      const profErr=$('obProfErr');
      if(profErr) profErr.classList.add('show');
      alert('Selecione o sistema de risco do período antes de iniciar.');
      return;
    }
    if(!riskProfileAccepted){
      showOnboardingStep('risk');
      const riskErr=$('obRiskAcceptErr');
      if(riskErr) riskErr.classList.add('show');
      alert('Confirme a declaração de escolha consciente do perfil de risco.');
      return;
    }
    if(!validateReserves()){ showOnboardingStep('reserves'); return; }
    if(!validateCentralCash()){ showOnboardingStep('cash'); return; }
    if(!validateEquityProtector()){ showOnboardingStep('protect'); return; }
    const rCalc=reserveCalc();
    openSummaryConfirmationModal({
      saldo,
      loginVal,
      passVal,
      serverVal,
      plataformaVal,
      alavVal,
      isPropFlow,
      propDailyVal,
      propMaxVal,
      propTrailingRuleVal,
      propTrailingDescVal,
      propProfitVal,
      propMinDaysVal,
      propAbsenceVal,
      restrictiveVal,
      reserveMasterCapitalVal:rCalc.capital,
      reserveFcrRequiredVal:rCalc.fcrReq,
      reserveFcrCurrentVal:reserveFcrCurrent,
      reserveFcrStatusVal:rCalc.fcrStatus,
      reserveMonthlyExpensesVal:reserveMonthlyExpenses,
      reserveFeoRequiredVal:rCalc.feoReq,
      reserveFeoCurrentVal:reserveFeoCurrent,
      reserveFeoStatusVal:rCalc.feoStatus,
      reserveSegregationAcceptedVal:reserveSegregationAccepted,
      reserveDeficitAcceptedVal:reserveDeficitAccepted,
      reserveNotesVal:reserveNotes,
      centralCashStatusVal:centralCashStatus,
      centralCashCustodyVal:centralCashCustody,
      centralCashCustodyOtherVal:centralCashCustodyOther,
      centralCashMainPctVal:centralCashMainPct,
      centralCashAgilePctVal:centralCashAgilePct,
      centralCashLiquidityPctVal:centralCashLiquidityPct,
      centralCashExternalPctVal:centralCashExternalPct,
      centralCashOtherPctVal:centralCashOtherPct,
      fcrLiquidityVal:fcrLiquidity,
      feoLiquidityVal:feoLiquidity,
      cashLedgerStatusVal:cashLedgerStatus,
      centralCashPolicyAcceptedVal:centralCashPolicyAccepted,
      centralCashNoAcceptedVal:centralCashNoAccepted,
      centralCashNotesVal:centralCashNotes,
      epStatusVal:epStatus,
      epPlatformVal:epPlatform,
      epPlatformOtherVal:epPlatformOther,
      epDailyLimitVal:epDailyLimit,
      epRestrictiveAcceptedVal:epRestrictiveAccepted,
      epPropDailyEnabledVal:epPropDailyEnabled,
      epPropDailyBaseVal:epPropDailyBase,
      epPropDailyNotesVal:epPropDailyNotes,
      epNoConfigAcceptedVal:epNoConfigAccepted,
      epNotesVal:epNotes
    });
  });
}
function meiManualHTML(){
  const section=(title,body)=>`<section style="margin:14px 0"><h3 style="font-size:calc(13px * var(--fs-scale));color:var(--ink);margin:0 0 6px">${title}</h3><div style="font-size:calc(12.5px * var(--fs-scale));color:var(--ink-dim);line-height:1.75">${body}</div></section>`;
  const practical=body=>`<div style="margin:14px 0;padding:12px 14px;border-left:3px solid var(--violet);background:var(--panel-2);font-size:calc(12.5px * var(--fs-scale));color:var(--ink-dim);line-height:1.7"><b style="color:var(--ink)">Em termos práticos.</b> ${body}</div>`;
  const note=body=>`<div style="margin:12px 0;padding:10px 12px;border:1px solid var(--line);border-radius:8px;font-size:calc(11.5px * var(--fs-scale));color:var(--ink-dim);line-height:1.65"><b style="color:var(--ink)">Observação importante.</b> ${body}</div>`;
  const formula=body=>`<div style="margin:12px 0;padding:12px 14px;border:1px solid var(--line);border-radius:8px;background:var(--panel);font-family:var(--mono);font-size:calc(12px * var(--fs-scale));color:var(--ink);overflow:auto">${body}</div>`;
  const flow=items=>`<div style="display:flex;gap:7px;align-items:center;flex-wrap:wrap;margin:12px 0">${items.map((x,i)=>`<span style="padding:7px 9px;border:1px solid var(--line);border-radius:7px;background:var(--panel);font-size:calc(11px * var(--fs-scale));color:var(--ink)">${x}</span>${i<items.length-1?'<span style="color:var(--violet)">→</span>':''}`).join('')}</div>`;
  const chapter=(number,title,body)=>`<details class="mc-disclosure" style="margin-top:10px"><summary><span class="t">Capítulo ${number} — ${title}</span><span class="art">Manual institucional</span><span class="chev">▾</span></summary><div class="mc-disclosure-body">${body}</div></details>`;
  return `<details class="mc-disclosure" style="margin-top:16px" open><summary><span class="t">Manual Institucional do MEI-JP</span><span class="art">Documento 2 · referência metodológica oficial</span><span class="chev">▾</span></summary><div class="mc-disclosure-body" style="max-width:980px">
    <p style="font-size:calc(13px * var(--fs-scale));color:var(--ink-dim);line-height:1.75;margin:0 0 14px">Este manual descreve a arquitetura estatística da Simulação Patrimonial. Ele documenta uma decisão metodológica da JP Wealth: modelar a incerteza da curva patrimonial sem confundir o modelo com uma previsão de mercado ou com uma autorização para ampliar risco.</p>
    ${chapter('1','O Modelo Estatístico Institucional JP Wealth',
      section('1. Introdução intuitiva','O MEI-JP existe porque uma meta de retorno, sozinha, descreve apenas uma linha central. Ela não descreve o conjunto de caminhos pelos quais uma conta pode chegar, ou não chegar, a esse resultado. A gestão precisa enxergar dispersão, tempo, drawdown e incerteza; não apenas uma projeção linear.')+
      section('2. Desenvolvimento conceitual','Dentro do ecossistema JP Wealth, o Estatuto define limites operacionais, a matriz quadrifásica limita exposição e o MEI-JP descreve cenários patrimoniais compatíveis com um perfil. O modelo não altera MDD, não muda fases, não dimensiona ordens e não substitui o julgamento do operador. Ele organiza informação probabilística para que o risco seja compreendido antes da execução.')+
      section('3. Formalização matemática','A simulação parte de um saldo inicial, de um retorno de referência do perfil e de uma medida mensal de dispersão. Milhares de trajetórias são geradas por choques aleatórios; delas extraem-se percentis, mediana e estatísticas de drawdown. O objeto modelado é a distribuição de curvas possíveis, não um preço futuro.')+
      section('4. Aplicação ao JP Wealth','O perfil Base, Longevity, High Longevity ou High Longevity Plus fornece a referência de retorno. O CID e, com o tempo, a curva histórica da própria conta fornecem a dispersão. O Estatuto continua sendo a regra superior: uma banda estatística nunca flexibiliza limite de risco.')+
      practical('O MEI-JP responde “quais trajetórias patrimoniais são coerentes com estas premissas?”, e não “o que o mercado fará amanhã?”.')+
      note('Previsão afirma um resultado específico. Modelagem probabilística descreve uma família de resultados possíveis e a incerteza associada. A segunda é a finalidade deste módulo.')+
      section('7. Limitações','Nenhuma distribuição elimina incerteza. O modelo não mede probabilidade de ruína, não estima preço de ativos e não valida uma operação individual.'))}
    ${chapter('2','Por que utilizamos um modelo probabilístico',
      section('1. Introdução intuitiva','Duas contas que seguem a mesma estratégia podem terminar um ano com patrimônios diferentes. A sequência de ganhos e perdas, a duração das operações, o momento de drawdowns e a realização de lucros importam tanto quanto a média. Uma média mensal não informa o percurso.')+
      section('2. Desenvolvimento conceitual','Um modelo <b>determinístico</b> fixa uma única curva: dado o mesmo saldo e a mesma taxa, produz sempre o mesmo final. Um modelo <b>probabilístico</b> reconhece vários resultados e atribui pesos ou distribuições a eles. Um modelo <b>estocástico</b> é probabilístico no tempo: cada período recebe uma inovação aleatória, formando trajetórias completas.')+
      flow(['Saldo inicial','Retorno de referência','Dispersão mensal','Choques sucessivos','Distribuição de patrimônios'])+
      section('3. Formalização matemática','Se R é um retorno mensal aleatório, a média E[R] não determina sua variância Var(R), nem a ordem em que retornos ocorrem. Duas sequências podem compartilhar a mesma média e ter máximos drawdowns radicalmente diferentes. Por isso o MEI-JP produz uma distribuição de caminhos, e não apenas E[R].')+
      section('4. Aplicação ao JP Wealth','A referência mensal do perfil representa a direção média institucional usada na projeção. A dispersão mostra o quanto trajetórias podem se afastar dela. A decisão operacional continua conservadora: estar abaixo da mediana não autoriza recuperar atraso com maior exposição.')+
      practical('A mediana não é uma promessa, e a faixa inferior não é um “piso”. São instrumentos para calibrar expectativa e preservar disciplina.')+
      note('A qualidade do resultado depende das premissas. Quanto menor a base histórica, maior o peso institucional e menor a pretensão de inferência empírica.')+
      section('7. Limitações','O modelo não captura automaticamente mudança de regime, fluxo externo de caixa ou alteração de processo. Esses eventos exigem registro e revisão humana.'))}
    ${chapter('3','Da caminhada aleatória ao Processo de Wiener',
      section('1. Introdução intuitiva','Uma caminhada aleatória pode ser imaginada como passos pequenos em direções incertas. Robert Brown observou, no século XIX, partículas em suspensão movendo-se de modo irregular. Einstein mostrou como esse comportamento podia ser tratado probabilisticamente. Norbert Wiener formalizou, no século XX, o processo contínuo que se tornou base para grande parte da teoria moderna de processos estocásticos.')+
      section('2. Desenvolvimento conceitual','O processo não afirma que o mercado é literalmente uma partícula. Ele oferece uma linguagem para representar variações acumuladas sem direção determinística em cada instante. Sua utilidade está em organizar incerteza, não em declarar independência perfeita no mundo real.')+
      section('3. Formalização matemática',formula('W<sub>0</sub> = 0; &nbsp; W<sub>t</sub> − W<sub>s</sub> ∼ N(0, t−s), para 0 ≤ s &lt; t.'))+
      section('3. Formalização matemática — propriedades','Os incrementos em intervalos não sobrepostos são independentes; a média de um incremento é zero; sua variância cresce com o tempo; e as trajetórias são contínuas quase certamente. A notação N(0,t−s) indica distribuição normal com média zero e variância t−s. Essas propriedades criam a escala de raiz do tempo para dispersão.')+
      section('4. Aplicação ao JP Wealth','No MEI-JP, o incremento de Wiener não é um choque de EURUSD nem de qualquer ativo. É uma representação abstrata da inovação aleatória da curva patrimonial, condicionada ao perfil e à dispersão escolhida.')+
      practical('O termo aleatório evita fingir que uma conta crescerá em linha reta. Ele cria variações mensais possíveis ao redor da referência institucional.')+
      note('Independência e normalidade são aproximações úteis, não fatos garantidos. O próprio manual registra suas limitações no Capítulo 10.')+
      section('7. Limitações','Mercados e curvas de gestão podem exibir dependência temporal, caudas pesadas e mudanças de regime. Por isso o Processo de Wiener é ponto de partida, não descrição final da realidade.'))}
    ${chapter('4','Movimento Browniano Geométrico',
      section('1. Introdução intuitiva','Patrimônio cresce e cai por composição. Ganhar 10% e depois perder 10% não devolve o saldo inicial; a base de cálculo mudou. Um processo geométrico preserva essa natureza multiplicativa e impede valores negativos na trajetória teórica.')+
      section('2. Desenvolvimento conceitual','Na forma contínua, o Movimento Browniano Geométrico combina uma tendência média com ruído proporcional ao nível atual de patrimônio. Quanto maior o patrimônio, maior o valor monetário associado à mesma variação percentual.')+
      section('3. Formalização matemática','No MEI-JP a variável de estado é <b>V<sub>t</sub></b>, o patrimônio (equity) da conta — e não S<sub>t</sub>, notação tradicionalmente associada ao preço de um ativo. A equação contínua oficial é:')+
      formula('dV<sub>t</sub> = μ<sub>p</sub>V<sub>t</sub>dt + σ<sub>p</sub>V<sub>t</sub>dW<sub>t</sub>')+
      section('3. Formalização matemática — solução','A solução do processo é:')+
      formula('V<sub>t</sub> = V<sub>0</sub> · exp[(μ<sub>p</sub> − ½σ<sub>p</sub>²)t + σ<sub>p</sub>W<sub>t</sub>]')+
      section('3. Formalização matemática — discretização','No MEI-JP, o passo é mensal:')+
      formula('V<sub>t+1</sub> = V<sub>t</sub> · exp[ln(1+r<sub>p</sub>) − ½σ<sub>p</sub>² + σ<sub>p</sub>Z<sub>t</sub>], &nbsp; Z<sub>t</sub> ∼ N(0,1)')+
      section('Definições','<b>V<sub>t</sub></b>: patrimônio da conta no período t · <b>V<sub>0</sub></b>: patrimônio inicial · <b>r<sub>p</sub></b>: retorno mensal de referência do perfil · <b>μ<sub>p</sub></b>: drift patrimonial · <b>σ<sub>p</sub></b>: dispersão patrimonial mensal utilizada · <b>W<sub>t</sub></b>: Processo de Wiener · <b>Z<sub>t</sub></b>: variável normal padrão.')+
      section('4. Aplicação ao JP Wealth','r<sub>p</sub> é a referência mensal do perfil e σ<sub>p</sub> é a dispersão mensal utilizada pelo MEI-JP (CID e/ou σ histórica de retornos logarítmicos ajustados). A implementação usa ln(1+r<sub>p</sub>) como drift logarítmico para preservar, em média, o retorno aritmético configurado do perfil. O termo −½σ<sub>p</sub>² é a correção de Itô do GBM.')+
      practical('A forma geométrica faz a projeção trabalhar com percentuais compostos. Ela não transforma a referência mensal em garantia, apenas mantém coerência matemática na simulação.')+
      note('A correção de Itô reduz a mediana quando σ aumenta, mesmo que a média permaneça alinhada ao retorno de referência. Essa assimetria é uma característica matemática da composição, não um defeito do gráfico.')+
      section('7. Limitações','O GBM pressupõe dinâmica contínua e distribuição lognormal. Choques discretos, liquidez limitada e eventos extremos podem violar essas hipóteses.'))}
    ${chapter('5','A adaptação do modelo ao JP Wealth',
      section('1. Introdução intuitiva','Modelos tradicionais aplicam GBM ao preço de um ativo, tradicionalmente denotado S<sub>t</sub>. A JP Wealth não precisa de uma segunda previsão de preço dentro do painel de risco; precisa compreender como uma disciplina operacional se traduz em caminhos de patrimônio. Por isso a variável de estado do MEI-JP é <b>V<sub>t</sub></b> — o patrimônio (equity) da conta. A troca de notação não é cosmética: ela impede que o leitor confunda o objeto modelado (curva patrimonial condicionada a disciplina, stops e perfil) com uma teoria de formação de preços.')+
      section('2. Desenvolvimento conceitual','A adaptação não afirma que a conta é um ativo negociável. Ela usa a estrutura matemática de composição e dispersão para representar o resultado agregado de decisões, execução, stop, gestão de risco e sequência de operações. É uma decisão metodológica institucional.')+
      section('3. Formalização matemática','A mesma equação do GBM é mantida, mas os significados econômicos mudam. Isso deve ser lido como uma aproximação de trajetória patrimonial, não como uma teoria de formação de preços.')+
      section('4. Aplicação ao JP Wealth',`<table class="dtable" style="font-size:calc(11px * var(--fs-scale))"><thead><tr><th>Modelo clássico</th><th>MEI-JP</th></tr></thead><tbody><tr><td>μ: retorno esperado do ativo</td><td>μ: retorno de referência do perfil</td></tr><tr><td>σ: volatilidade do ativo</td><td>σ: CID e/ou volatilidade histórica da curva</td></tr><tr><td>dW: choque aleatório de preço</td><td>dW: dispersão aleatória da trajetória patrimonial</td></tr><tr><td>S<sub>t</sub>: preço do ativo</td><td>V<sub>t</sub>: patrimônio (equity) da conta</td></tr></tbody></table>`) +
      practical('O painel não pergunta se EURUSD ficará mais ou menos volátil. Ele pergunta como uma conta, obedecendo o perfil e a gestão definidos, pode evoluir ao longo do tempo.')+
      note('A matriz quadrifásica, o MDD e a Ordem Gênese são controles normativos externos ao simulador. O simulador observa cenários; não autoriza exceções.')+
      section('7. Limitações','A curva patrimonial agrega múltiplas causas. Sem registro de aportes, saques e mudanças de processo, uma parte da dispersão observada pode não ser estritamente operacional.'))}
    ${chapter('6','Coeficiente Institucional de Dispersão (CID)',
      section('1. Introdução intuitiva','O CID é a estimativa mensal inicial de quanto uma curva patrimonial disciplinada pode se afastar de sua trajetória de referência. Ele existe para que a simulação seja possível antes de haver uma amostra histórica longa e confiável. <b>O CID não é volatilidade de mercado. É um parâmetro institucional de dispersão patrimonial utilizado enquanto o histórico próprio ainda é insuficiente ou pouco representativo.</b>')+
      section('2. Desenvolvimento conceitual','Não utilizamos volatilidade de EURUSD, GBPUSD, DXY, volatilidade implícita ou outro indicador de mercado como substituto. A volatilidade de um ativo mede o ativo; a dispersão de uma conta depende também de exposição, stops, frequência, execução, redução de risco, perfil, disciplina e governança. São objetos estatísticos diferentes.')+
      section('3. Formalização matemática','Para um perfil p, o CID<sub>p</sub> é inserido como σ mensal no estágio institucional. A unidade é percentual mensal da equity, e não ATR, ponto de preço ou volatilidade anual de mercado.')+
      section('4. Aplicação ao JP Wealth','O CID deve representar uma conta que segue rigorosamente o Estatuto JP Wealth. O risco por ordem, o teto de fase e a redução progressiva de exposição influenciam a dispersão patrimonial esperada. Com acumulação de dados válidos, o CID deixa de ser a única fonte e passa a ser combinado com a volatilidade observada da própria curva.')+
      practical('Um CID alto não é sinal para reduzir limite estatutário automaticamente; é sinal de que a projeção reconhece maior incerteza. Um CID baixo não autoriza mais risco.')+
      note('Valores muito baixos ou muito altos são sinalizados para revisão técnica. O sistema não os corrige silenciosamente, pois a decisão de calibração exige responsável identificável e memória de cálculo.')+
      section('7. Limitações','CID não é uma constante física. Ele pode mudar com alteração de processo, corretora, perfil, regime de execução ou qualidade operacional.'))}
    ${chapter('7','Simulação de Monte Carlo',
      section('1. Introdução intuitiva','Monte Carlo é o procedimento de repetir uma experiência aleatória muitas vezes para observar a distribuição de resultados. Em vez de escolher uma única curva “provável”, o MEI-JP produz milhares de curvas coerentes com as mesmas premissas.')+
      section('2. Desenvolvimento conceitual',flow(['Saldo inicial','Retorno esperado','CID / sigma histórica','Processo de Wiener','Nova trajetória','Milhares de repetições','Distribuição estatística']))+
      section('3. Formalização matemática','A cada mês e para cada trajetória, o sistema sorteia z de uma normal padrão via transformação Box–Muller. A trajetória é atualizada pela equação discretizada do GBM. Ao final, os valores de cada mês são ordenados para calcular percentis 5/95 ou o nível configurado, 25/75 e mediana.')+
      section('4. Aplicação ao JP Wealth','O painel executa 1.000, 2.000, 5.000 ou 10.000 trajetórias. Ele não persiste trajetórias pesadas: apenas configurações e histórico. A seed fixa reproduz exatamente uma simulação; a seed aleatória produz nova amostra da mesma distribuição. Nenhuma delas é “o futuro correto”.')+
      practical('Uma única trajetória pode parecer dramática ou excelente por acaso. Muitas trajetórias revelam a forma da distribuição e reduzem a dependência de uma história isolada.')+
      note('Mais trajetórias reduzem erro de amostragem do Monte Carlo, mas não corrigem uma premissa errada de CID, retorno ou histórico. <b>A simulação representa trajetórias compatíveis com os parâmetros fornecidos. Ela não demonstra que a estratégia possui vantagem estatística e não substitui validação operacional.</b>')+
      section('7. Limitações','Monte Carlo amostra o modelo escolhido. Não descobre automaticamente um evento que não foi representado pelas hipóteses do modelo.'))}
    ${chapter('8','Como interpretar a Simulação Patrimonial',
      section('1. Introdução intuitiva','O gráfico não mostra previsão. O gráfico mostra distribuição provável sob as premissas registradas. Ler uma linha central como meta obrigatória é erro de interpretação.')+
      section('2. Desenvolvimento conceitual','A linha mediana separa metade das trajetórias acima e metade abaixo. A faixa interna 25–75% contém a região central de 50% das trajetórias. A faixa externa, por padrão 5–95% quando a confiança é 90%, mostra uma região mais ampla. Quanto maior a abertura das faixas, maior a incerteza modelada.')+
      section('3. Formalização matemática','Para cada mês t, o sistema calcula percentis Q<sub>p</sub>(V<sub>t</sub>) sobre o patrimônio simulado. A mediana é Q<sub>0,50</sub>; a faixa interna é [Q<sub>0,25</sub>,Q<sub>0,75</sub>]; e a externa é [Q<sub>(1−c)/2</sub>,Q<sub>(1+c)/2</sub>], onde c é o nível de confiança configurado.')+
      section('4. Aplicação ao JP Wealth','A linha de MDD representa o limite do perfil, não uma previsão de perda. A probabilidade de tocar MDD é calculada pelo máximo drawdown de cada trajetória simulada, medido contra seu pico acumulado. Ela é uma estatística de modelo e não substitui a regra estatutária de drawdown do ciclo.')+
      practical('Estar acima da mediana não justifica acelerar. Estar abaixo dela não justifica recuperar. O valor operacional do gráfico é disciplinar expectativa e reforçar preservação de capital.')+
      note('Faixas não são intervalos de confiança sobre um parâmetro desconhecido; são percentis de resultados gerados pela distribuição assumida.')+
      section('7. Limitações','A aparência suave do gráfico não torna o mundo suave. Eventos descontínuos e mudanças de regime podem produzir caminhos fora das faixas simuladas.'))}
    ${chapter('9','Evolução do Modelo',
      section('1. Introdução intuitiva','Uma conta nova não possui série suficiente para medir sua própria dispersão com estabilidade. Uma conta madura não deve ignorar seu histórico. O MEI-JP foi desenhado para trocar de fonte sem salto abrupto.')+
      section('2. Desenvolvimento conceitual',flow(['Institucional (0–5)','Evidência preliminar (6–11)','Híbrido inicial (12–23)','Híbrido avançado (24–35)','Empírico predominante (36+)'])+'Cinco estágios classificados pelo número n de retornos mensais válidos. Amostras patrimoniais curtas são vulneráveis a mudança de regime, concentração temporal, baixa frequência, eventos extraordinários, erros operacionais, quebra de disciplina e contaminação por fluxos externos — por isso 24 observações ainda não substituem integralmente o CID.')+
      section('3. Formalização matemática','Se n é o número de retornos mensais válidos, o peso histórico é:')+
      formula('w<sub>h</sub> = clip((n − 6)/(36 − 6), 0, 1)')+
      section('3. Formalização matemática — combinação','A dispersão usada é:')+
      formula('σ<sub>usada</sub> = (1 − w<sub>h</sub>)·σ<sub>CID</sub> + w<sub>h</sub>·σ<sub>hist</sub>')+
      practical('<b>Decisão metodológica (caixa de decisão).</b> A interpolação linear entre o CID e a volatilidade histórica é uma decisão institucional de engenharia da versão 1.0 do MEI-JP. Ela foi escolhida por simplicidade, transparência, continuidade e facilidade de auditoria. Não constitui uma lei estatística universal nem a única forma possível de combinar estimativas de dispersão.')+
      section('Alternativas futuras documentadas','Uma alternativa natural é a combinação por variâncias:')+
      formula('σ<sub>usada</sub> = √[(1 − w<sub>h</sub>)·σ<sub>CID</sub>² + w<sub>h</sub>·σ<sub>hist</sub>²]')+
      section('Alternativas futuras — continuação','Também são candidatas: shrinkage estatístico, abordagem bayesiana (CID como prior), ponderação exponencial das observações e modelos dependentes de regime. Nenhuma delas está implementada nesta versão — estão registradas para evolução com validação e governança.')+
      section('4. Aplicação ao JP Wealth','Os parâmetros padrão iniciam a transição em seis retornos e a predominância empírica completa (w<sub>h</sub>=1) ocorre somente a partir de trinta e seis. O desvio-padrão histórico é amostral, calculado sobre retornos logarítmicos ajustados por fluxo externo, em equivalente mensal inclusive quando houver lacuna entre registros válidos.')+
      practical('O modelo não “descobre” uma verdade estatística ao completar 36 meses. Ele apenas deixa de depender do CID porque a série própria atingiu o patamar institucional definido para esta versão — a estimativa permanece sujeita a revisão.')+
      note('A transição gradual é proteção contra overfitting: uma sequência curta, excepcionalmente boa ou ruim, não passa a governar imediatamente toda a simulação. Qualidade da amostra: 0–5 insuficiente · 6–11 preliminar · 12–23 limitada · 24–35 moderada · 36–59 relevante · 60+ consolidada.')+
      section('7. Limitações','Mesmo 36 observações são predominância empírica, não certeza. Qualidade de dados, consistência de processo e identificação de fluxos externos permanecem indispensáveis.'))}
    ${chapter('10','Hipóteses e Limitações',
      section('1. Introdução intuitiva','Todo modelo simplifica. O uso responsável começa quando suas hipóteses ficam visíveis, e não quando são escondidas atrás de um gráfico sofisticado.')+
      section('2. Desenvolvimento conceitual','O MEI-JP assume, para cada execução, dispersão aproximadamente constante, inovação normal condicional, composição mensal e continuidade entre pontos de observação. Também trata o perfil e o processo de gestão como estáveis no horizonte simulado.')+
      section('3. Formalização matemática','GBM implica retornos lognormais e incrementos gaussianos independentes. Na prática, curvas podem apresentar assimetria, caudas pesadas, autocorrelação, clusters de volatilidade, saltos e dependência entre meses.')+
      section('4. Aplicação ao JP Wealth','O modelo registra outliers por IQR, mas não os remove automaticamente. Esse cuidado evita confundir evento operacional legítimo, aporte, saque ou erro de registro. O operador deve revisar dados extraordinários antes de tratá-los como evidência da estratégia.')+
      practical('A utilidade do MEI-JP não vem de prometer precisão impossível; vem de tornar explícitas as premissas, a dispersão e o custo de conviver com a incerteza.')+
      note('Black swans, mudança de corretora, indisponibilidade técnica, alteração de perfil, erro de execução e decisões fora do Estatuto não são capturados de forma confiável por uma normal mensal.')+
      section('Registro de riscos residuais','Riscos que o operador deve manter em mente ao interpretar qualquer saída do MEI-JP: <b>contaminação por aportes/retiradas</b> não registrados (o ajuste por fluxo só funciona se os fluxos forem lançados); <b>amostra pequena</b> (estimativas preliminares, sujeitas a revisão); <b>autocorrelação</b> entre meses; <b>mudança de regime</b> de mercado ou de processo; <b>quebra de disciplina</b> operacional; <b>dados incorretos</b> de registro; <b>interpretação indevida</b> (ler mediana como meta ou banda como garantia); e <b>risco de modelo</b> — o próprio GBM é uma aproximação.')+
      section('7. Limitações','O modelo não é ferramenta de suitability, não é auditoria de performance, não substitui contabilidade e não elimina obrigação de cumprir hard stops e quarentena.'))}
    ${chapter('11','Evoluções Futuras',
      section('1. Introdução intuitiva','A versão atual é uma fundação auditável. Evoluir o modelo não significa adicionar complexidade por aparência; significa aumentar realismo apenas quando houver dados, validação e governança suficientes.')+
      section('2. Desenvolvimento conceitual',flow(['MEI-JP v1','Bootstrap histórico','Volatilidade por regime','Misturas de distribuições','Volatilidade estocástica','Hidden Markov Models','Validação contínua']))+
      section('3. Formalização matemática','Bootstrap poderá reamostrar retornos históricos; modelos por regime poderão condicionar μ e σ a estados observáveis; misturas poderão representar caudas mais pesadas; volatilidade estocástica poderá permitir σ variável; e HMMs poderão inferir estados latentes. Cada avanço exigirá memória de cálculo, teste fora da amostra e aprovação formal.')+
      section('4. Aplicação ao JP Wealth','Nenhuma dessas extensões está implementada nesta versão. O MEI-JP v1 usa GBM mensal com CID, volatilidade histórica progressiva e Monte Carlo. Essa limitação é deliberada: a simplicidade atual favorece auditabilidade e entendimento operacional.')+
      practical('A evolução correta é adicionar complexidade somente quando ela melhora decisão, validação e governança, e não apenas a aparência quantitativa do painel.')+
      note('Antes de uma nova versão substituir a atual, ela deverá ser comparada com dados históricos, documentada e submetida à governança institucional.')+
      section('7. Limitações','Modelos mais complexos também podem sobreajustar dados e reduzir transparência. A evolução futura não revoga o princípio de preservação de capital.'))}
    ${chapter('12','Retornos: simples, logarítmico e ajustado por fluxo',
      section('1. Introdução intuitiva','Uma mesma variação patrimonial pode ser lida de formas diferentes. Para o operador, “ganhei 5% no mês” é a leitura natural. Para o motor estatístico, retornos logarítmicos são preferíveis: somam-se no tempo, tornam a composição aditiva e alinham-se diretamente ao expoente do GBM. E, para ambos, aportes e retiradas precisam ser descontados — depósito não é lucro, saque não é prejuízo.')+
      section('2. Desenvolvimento conceitual','A interface exibe o retorno simples porque ele é intuitivo para leitura operacional. O motor calcula média, variância, desvio-padrão e calibração da volatilidade sobre retornos logarítmicos. As duas leituras descrevem o mesmo fenômeno em escalas diferentes.')+
      section('3. Formalização matemática — retorno simples (interface)',formula('R<sub>t</sub> = V<sub>t</sub>/V<sub>t−1</sub> − 1'))+
      section('3. Formalização matemática — fluxo externo',formula('F<sub>t</sub> = A<sub>t</sub> − W<sub>t</sub> &nbsp; (aportes − retiradas do período)'))+
      section('3. Formalização matemática — retorno ajustado',formula('R<sub>t</sub><sup>aj</sup> = (V<sub>t</sub> − V<sub>t−1</sub> − F<sub>t</sub>)/V<sub>t−1</sub>'))+
      section('3. Formalização matemática — retorno logarítmico ajustado (motor)',formula('r<sub>t</sub><sup>aj</sup> = ln(1 + R<sub>t</sub><sup>aj</sup>), &nbsp; válido somente quando 1 + R<sub>t</sub><sup>aj</sup> &gt; 0'))+
      section('4. Aplicação ao JP Wealth','O histórico do MEI-JP registra, por mês: patrimônio inicial (informativo), patrimônio final, aportes, retiradas e observações. A cadeia de retornos usa a equity final de meses consecutivos como V<sub>t−1</sub> e V<sub>t</sub>, com o fluxo do mês corrente descontado do numerador. Lacunas viram equivalente mensal em log (divisão do log do intervalo pelos meses). Observações com V ≤ 0, valor ausente, duplicidade não resolvida ou 1+R<sup>aj</sup> ≤ 0 são classificadas como inválidas e excluídas apenas do cálculo — nunca apagadas automaticamente do histórico.')+
      practical('Sem o ajuste, um aporte de 20% num mês neutro entraria na volatilidade como se fosse um mês espetacular — e a simulação inteira herdaria uma dispersão fictícia. O ajuste protege a honestidade estatística do modelo.')+
      note('O retorno ajustado da versão 1.0 assume o fluxo atribuído ao intervalo que termina no mês do registro, sem ponderação intra-mês (aproximação tipo Dietz simples com fluxo no fim). Fluxos muito grandes no meio do mês introduzem pequena imprecisão — registre a observação no campo apropriado.')+
      section('7. Limitações','O ajuste depende do registro fiel dos fluxos. Fluxos não lançados continuam contaminando a série, e nenhum algoritmo os detecta com segurança a posteriori.'))}
  </div></details>`;
}
function renderMEIConfig(){
  const el=$('meiConfig'); if(!el) return;
  const mei=S.mei||DEFAULTS.mei, profile=(S.period&&S.period.profile)||'base', cal=meiCalibration(profile), stats=cal.stats;
  const stageLabel=meiStageLabel(cal.modelStage);
  const stageColor=cal.enabled?'var(--f1)':'var(--f2)';
  const history=meiHistoryAllSorted(), usableHistory=meiHistorySorted(), historyDiag=meiHistoryDiagnostics();
  const monthlyReturnById=new Map(meiReturnRows().map(r=>[String(r.to.id),r]));
  const seenMonths=new Set();
  const lastCalib=mei.lastCalibrationAt?String(mei.lastCalibrationAt).slice(0,10):'—';
  const cidRows=RISK_PROFILES.map(pr=>`<div class="field" style="min-width:150px">
    <label>${esc(pr.name)} · CID mensal (%)</label>
    <input type="number" min="0" max="100" step="0.01" data-mei-cid="${pr.key}" value="${mei.cid[pr.key]===''?'':decimalToPercentInput(mei.cid[pr.key])}" placeholder="ex.: 3,50">
  </div>`).join('');
  const historyRows=history.length?history.map(r=>{
    const month=meiMonthKey(r.date), valid=!!month&&Number.isFinite(+r.endingEquity)&&(+r.endingEquity>0);
    const duplicate=valid&&seenMonths.has(month); if(valid) seenMonths.add(month);
    const ret=monthlyReturnById.get(String(r.id));
    const returnText=!valid?'<span style="color:var(--f4)">Corrigir</span>'
      :duplicate?'<span style="color:var(--f2)">Duplicado</span>'
      :!ret?'—'
      :!ret.valid?`<span style="color:var(--f4)" title="${esc(ret.invalidReason)}">Excluído</span>`
      :`${fmtPct(ret.returnPct)}${ret.months>1?` <span style="color:var(--ink-faint)">(${ret.months}m)</span>`:''}${ret.flow!==0?' <span style="color:var(--f2)" title="Retorno ajustado por fluxo externo">aj.</span>':''}`;
    return `<tr>
    <td><input type="month" data-mei-hdate="${esc(r.id)}" value="${esc(String(r.date).slice(0,7))}" style="min-width:120px"></td>
    <td><input type="number" min="0" step="0.01" data-mei-hstart="${esc(r.id)}" value="${(r.startingEquity===''||r.startingEquity==null||!Number.isFinite(+r.startingEquity))?'':r.startingEquity}" placeholder="opcional" title="Patrimônio inicial do mês — informativo, não entra no cálculo (a cadeia usa a equity final do mês anterior)" style="min-width:105px"></td>
    <td><input type="number" min="0.01" step="0.01" data-mei-hequity="${esc(r.id)}" value="${Number.isFinite(+r.endingEquity)?r.endingEquity:''}" style="min-width:115px"></td>
    <td><input type="number" min="0" step="0.01" data-mei-hcontrib="${esc(r.id)}" value="${(+r.contributions||0)===0?'':+r.contributions}" placeholder="0" style="min-width:90px"></td>
    <td><input type="number" min="0" step="0.01" data-mei-hwithdraw="${esc(r.id)}" value="${(+r.withdrawals||0)===0?'':+r.withdrawals}" placeholder="0" style="min-width:90px"></td>
    <td style="white-space:nowrap">${returnText}</td>
    <td><input type="text" data-mei-hnotes="${esc(r.id)}" value="${esc(r.notes||'')}" placeholder="Observação" style="min-width:140px"></td>
    <td><button class="reset-btn" type="button" data-mei-delete="${esc(r.id)}" style="color:var(--f4);border-color:var(--f4);padding:6px 8px">Excluir</button></td>
  </tr>`;}).join(''):'<tr><td colspan="8" style="color:var(--ink-faint);text-align:center;padding:18px">Nenhuma observação registrada.</td></tr>';
  const cidReview=RISK_PROFILES.filter(pr=>{ const v=+mei.cid[pr.key]; return v>0&&(v<.001||v>.20); }).map(pr=>pr.name);
  el.innerHTML=`
    <div class="risk-note" style="margin:0 0 14px">O MEI-JP modela a dispersão da <b>curva patrimonial</b>. Ele não usa volatilidade de pares, DXY ou volatilidade implícita como substituto da estratégia.</div>
    <details open class="mc-disclosure"><summary><span class="t">Status do modelo</span><span class="art">versão ${esc(mei.version)}</span><span class="chev">▾</span></summary>
      <div class="mc-disclosure-body">
        <div class="metrics" style="grid-template-columns:repeat(auto-fit,minmax(135px,1fr));gap:10px">
          <div class="metric"><div class="k">Estágio</div><div class="v sm" style="color:${stageColor}">${stageLabel}</div><div class="sub">perfil ${esc(cal.pr.name)}</div></div>
          <div class="metric"><div class="k">Sigma utilizada</div><div class="v sm">${cal.enabled?fmtPct(cal.sigmaUsed):'—'}</div><div class="sub">CID ${cal.cid?fmtPct(cal.cid):'—'} + σ hist ${stats.observations>1?fmtPct(stats.sigma):'—'}</div></div>
          <div class="metric"><div class="k">Histórico</div><div class="v sm">${stats.observations}</div><div class="sub">retornos válidos${stats.excludedReturns?` · ${stats.excludedReturns} excluído(s)`:''}</div></div>
          <div class="metric"><div class="k">Qualidade da amostra</div><div class="v sm">${meiQuality(stats.observations)}</div><div class="sub">informativa, não certificação</div></div>
          <div class="metric"><div class="k">Peso institucional</div><div class="v sm">${fmtPct(cal.institutionalWeight||0)}</div><div class="sub">CID</div></div>
          <div class="metric"><div class="k">Peso histórico</div><div class="v sm">${fmtPct(cal.historicalWeight||0)}</div><div class="sub">curva própria</div></div>
          <div class="metric"><div class="k">Fluxos externos</div><div class="v sm">${stats.flowsPresent?'Sim':'Não'}</div><div class="sub">${stats.flowsPresent?'retornos ajustados':'sem aportes/retiradas'}</div></div>
          <div class="metric"><div class="k">Outliers sinalizados</div><div class="v sm">${stats.outlierCount||0}</div><div class="sub">IQR · não removidos</div></div>
          <div class="metric"><div class="k">Última calibração</div><div class="v sm">${esc(lastCalib)}</div><div class="sub">alteração de parâmetros/histórico</div></div>
        </div>
        ${stats.flowsPresent?'<p style="font-size:calc(12px * var(--fs-scale));color:var(--f2);margin-top:12px">O histórico contém fluxos externos. Os retornos utilizados foram ajustados para evitar que aportes sejam interpretados como lucro e retiradas como prejuízo.</p>':''}
        ${(historyDiag.invalid||historyDiag.duplicates||stats.excludedReturns)?'<p style="font-size:calc(12px * var(--fs-scale));color:var(--f2);margin-top:8px">Existem registros históricos preservados que não foram utilizados na calibração por inconsistência matemática ou ausência de dados válidos.</p>':''}
        ${cal.enabled?'':`<p style="font-size:calc(12px * var(--fs-scale));color:var(--f2);margin-top:12px">${esc(cal.reason)}</p>`}
      </div>
    </details>
    <details class="mc-disclosure"><summary><span class="t">CID por perfil</span><span class="art">desvio mensal institucional</span><span class="chev">▾</span></summary>
      <div class="mc-disclosure-body"><div class="params-grid">${cidRows}</div><p id="meiCidNotice" style="font-size:calc(11px * var(--fs-scale));color:${cidReview.length?'var(--f2)':'var(--ink-faint)'};margin-top:10px">${cidReview.length?`Revisão técnica sugerida para: ${esc(cidReview.join(', '))}. CID abaixo de 0,10% ou acima de 20% ao mês não é bloqueado, mas pode tornar a simulação pouco informativa.`:'Valores são percentuais mensais. O painel aceita valores fora da faixa usual, mas sinaliza entradas abaixo de 0,10% ou acima de 20% para revisão técnica.'}</p></div>
    </details>
    <details class="mc-disclosure"><summary><span class="t">Histórico utilizado pelo MEI-JP</span><span class="art">${usableHistory.length} meses válidos</span><span class="chev">▾</span></summary>
      <div class="mc-disclosure-body"><p style="font-size:calc(12px * var(--fs-scale));color:var(--ink-dim);margin-bottom:10px">O retorno mensal exibido é o <b>retorno simples ajustado por fluxo externo</b>: R<sub>aj</sub> = (V<sub>t</sub> − V<sub>t−1</sub> − F<sub>t</sub>)/V<sub>t−1</sub>, com F = aportes − retiradas. O motor estatístico usa o equivalente logarítmico ln(1+R<sub>aj</sub>). Lacunas de meses viram equivalente mensal. Aportes e retiradas registrados deixam de contaminar a volatilidade histórica.</p>
        ${(historyDiag.invalid||historyDiag.duplicates||stats.excludedReturns)?`<p style="font-size:calc(12px * var(--fs-scale));color:var(--f2);margin:0 0 10px">${historyDiag.invalid?`${historyDiag.invalid} registro(s) inválido(s) não entram no cálculo.`:''}${historyDiag.invalid&&historyDiag.duplicates?' ':''}${historyDiag.duplicates?`${historyDiag.duplicates} mês(es) duplicado(s): apenas o primeiro registro válido entra no cálculo até correção.`:''}${stats.excludedReturns?` ${stats.excludedReturns} período(s) excluído(s) por retorno ajustado ≤ −100% (1+R ≤ 0) — preservados no histórico.`:''}</p>`:''}
        <div style="overflow:auto"><table class="dtable"><thead><tr><th>Mês</th><th>Equity inicial <span style="text-transform:none">(info.)</span></th><th>Equity final</th><th>Aportes</th><th>Retiradas</th><th>Retorno aj.</th><th>Observação</th><th></th></tr></thead><tbody>${historyRows}</tbody></table></div>
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:8px;margin-top:12px;align-items:end"><div class="field"><label>Mês</label><input id="meiNewDate" type="month"></div><div class="field"><label>Equity final</label><input id="meiNewEquity" type="number" min="0.01" step="0.01" placeholder="0,00"></div><div class="field"><label>Aportes</label><input id="meiNewContrib" type="number" min="0" step="0.01" placeholder="0,00"></div><div class="field"><label>Retiradas</label><input id="meiNewWithdraw" type="number" min="0" step="0.01" placeholder="0,00"></div><div class="field"><label>Observação</label><input id="meiNewNotes" type="text" placeholder="Opcional"></div><button class="reset-btn" type="button" id="meiAddHistoryBtn" style="color:var(--violet);border-color:var(--violet);height:38px">Adicionar</button></div>
      </div>
    </details>
    <details class="mc-disclosure"><summary><span class="t">Parâmetros e calibração</span><span class="art">Monte Carlo</span><span class="chev">▾</span></summary>
      <div class="mc-disclosure-body"><div class="params-grid">
        <div class="field"><label>Trajetórias</label><select id="meiSimulationCount">${[1000,2000,5000,10000].map(v=>`<option value="${v}" ${+mei.simulationCount===v?'selected':''}>${v.toLocaleString('pt-BR')}</option>`).join('')}</select></div>
        <div class="field"><label>Horizonte (meses)</label><select id="meiHorizonMonths">${[12,24,60,120].map(v=>`<option value="${v}" ${+mei.horizonMonths===v?'selected':''}>${v}</option>`).join('')}</select></div>
        <div class="field"><label>Confiança externa (%)</label><input id="meiConfidence" type="number" min="50" max="99" step="1" value="${Math.round((+mei.confidenceLevel||.9)*100)}"></div>
        <div class="field"><label>Seed</label><select id="meiSeedMode"><option value="random" ${mei.seedMode==='random'?'selected':''}>Aleatória</option><option value="fixed" ${mei.seedMode==='fixed'?'selected':''}>Fixa</option></select></div>
        <div class="field"><label>Valor da seed</label><input id="meiFixedSeed" type="text" value="${esc(mei.fixedSeed||'')}" ${mei.seedMode==='fixed'?'':'disabled'} placeholder="Ex.: ciclo-2026"></div>
      </div>
      <div class="metrics" style="grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin-top:12px"><div class="metric"><div class="k">Sigma institucional</div><div class="v sm">${cal.cid?fmtPct(cal.cid):'—'}</div><div class="sub">CID do perfil</div></div><div class="metric"><div class="k">Sigma histórica</div><div class="v sm">${stats.observations>1?fmtPct(stats.sigma):'—'}</div><div class="sub">retornos log ajustados por fluxo</div></div><div class="metric"><div class="k">Volatilidade anualizada</div><div class="v sm">${stats.observations>1?fmtPct(stats.annualizedVolatility):'—'}</div></div><div class="metric"><div class="k">Maior DD histórico</div><div class="v sm">${usableHistory.length?fmtPct(stats.maxDrawdown):'—'}</div></div><div class="metric"><div class="k">Cobertura observada</div><div class="v sm">${stats.coveredMonths||0} meses</div><div class="sub">${stats.positive} positivos · ${stats.negative} negativos</div></div></div>
      ${mei.seedMode==='fixed'&&!String(mei.fixedSeed||'').trim()?'<p style="font-size:calc(11px * var(--fs-scale));color:var(--f2);margin-top:10px">Seed fixa vazia: será usado o identificador padrão MEI-JP:v1. Informe um valor próprio para rastreabilidade explícita.</p>':''}
      </div>
    </details>
    ${meiManualHTML()}`;
  const persist=()=>{ S.mei.lastCalibrationAt=new Date().toISOString(); save(); renderMEIConfig(); };
  el.querySelectorAll('[data-mei-cid]').forEach(input=>input.addEventListener('change',()=>{ const raw=input.value.trim(); S.mei.cid[input.dataset.meiCid]=raw===''?'':percentInputToDecimal(raw); persist(); }));
  ['meiSimulationCount','meiHorizonMonths','meiConfidence','meiSeedMode','meiFixedSeed'].forEach(id=>{ const input=$(id); if(input) input.addEventListener('change',()=>{ if(id==='meiSimulationCount') S.mei.simulationCount=+input.value; if(id==='meiHorizonMonths') S.mei.horizonMonths=+input.value; if(id==='meiConfidence') S.mei.confidenceLevel=Math.max(.5,Math.min(.99,(+input.value||90)/100)); if(id==='meiSeedMode') S.mei.seedMode=input.value==='fixed'?'fixed':'random'; if(id==='meiFixedSeed') S.mei.fixedSeed=input.value; persist(); }); });
  const updateHistory=(id,field,value)=>{
    const r=S.mei.history.find(x=>String(x.id)===String(id)); if(!r) return;
    if(field==='date'){
      const nextDate=value?value+'-01':'', month=meiMonthKey(nextDate);
      if(month&&S.mei.history.some(x=>String(x.id)!==String(id)&&meiMonthKey(x.date)===month)){
        alert('Já existe um registro para este mês. A alteração não foi salva.'); renderMEIConfig(); return;
      }
      r.date=nextDate;
    } else if(field==='endingEquity') r.endingEquity=Number(value);
    else if(field==='startingEquity') r.startingEquity=(value===''||!Number.isFinite(+value))?'':Number(value);
    else if(field==='contributions') r.contributions=Math.max(0,Number(value)||0);
    else if(field==='withdrawals') r.withdrawals=Math.max(0,Number(value)||0);
    else r.notes=value;
    persist();
  };
  el.querySelectorAll('[data-mei-hdate]').forEach(i=>i.addEventListener('change',()=>updateHistory(i.dataset.meiHdate,'date',i.value)));
  el.querySelectorAll('[data-mei-hstart]').forEach(i=>i.addEventListener('change',()=>updateHistory(i.dataset.meiHstart,'startingEquity',i.value)));
  el.querySelectorAll('[data-mei-hequity]').forEach(i=>i.addEventListener('change',()=>updateHistory(i.dataset.meiHequity,'endingEquity',i.value)));
  el.querySelectorAll('[data-mei-hcontrib]').forEach(i=>i.addEventListener('change',()=>updateHistory(i.dataset.meiHcontrib,'contributions',i.value)));
  el.querySelectorAll('[data-mei-hwithdraw]').forEach(i=>i.addEventListener('change',()=>updateHistory(i.dataset.meiHwithdraw,'withdrawals',i.value)));
  el.querySelectorAll('[data-mei-hnotes]').forEach(i=>i.addEventListener('change',()=>updateHistory(i.dataset.meiHnotes,'notes',i.value)));
  el.querySelectorAll('[data-mei-delete]').forEach(b=>b.addEventListener('click',()=>{ S.mei.history=S.mei.history.filter(r=>String(r.id)!==b.dataset.meiDelete); persist(); }));
  const add=$('meiAddHistoryBtn'); if(add) add.addEventListener('click',()=>{ const month=$('meiNewDate').value, equity=+$('meiNewEquity').value; if(!month||!(equity>0)){ alert('Informe mês e equity final positiva.'); return; } if(S.mei.history.some(r=>String(r.date).slice(0,7)===month)){ alert('Já existe um registro para este mês.'); return; } S.mei.history.push({id:'mei_'+Date.now(),date:month+'-01',startingEquity:'',endingEquity:equity,contributions:Math.max(0,+$('meiNewContrib').value||0),withdrawals:Math.max(0,+$('meiNewWithdraw').value||0),notes:$('meiNewNotes').value.trim()}); persist(); });
}
function renderConfigOnboarding(){
  const el=$('configOnboarding'); if(!el) return;
  const ob=S.onboarding||{};
  const {ep,obj,pr}=onboardingEP(S.params.saldoIni||0,(S.period&&S.period.profile)||'base');
  const maskedInvestorPassword=ob.investorPassword ? '••••••••' : '';
  const row=(k,v)=>`<tr><td style="color:var(--ink-dim); padding:5px 8px">${k}</td><td class="hl" style="text-align:right; padding:5px 8px">${v||'—'}</td></tr>`;
  const completion=getOnboardingCompletionState();
  const statusMark={complete:'✓',warning:'!',critical:'✕',pending:'—'};
  const statusColor={complete:'var(--f1)',warning:'var(--f2)',critical:'var(--f4)',pending:'var(--ink-faint)'};
  const completionHTML=`<div class="card" style="max-width:560px; margin:0 0 12px; padding:12px 14px; box-shadow:none; background:var(--panel-2); border-color:${completion.complete?'var(--f1)':(completion.critical?'var(--f4)':'var(--f2)')}">
    <h2 style="margin-bottom:8px">Formulário de Início <span class="art">${completion.completed}/${completion.total} concluído</span></h2>
    <div style="display:grid; gap:6px; font-size:calc(12px * var(--fs-scale)); color:var(--ink-dim)">
      ${completion.steps.map(s=>`<div style="display:flex; justify-content:space-between; gap:12px"><span>${esc(s.label)}</span><b style="color:${statusColor[s.status]}">${statusMark[s.status]} ${s.status}</b></div>`).join('')}
    </div>
    ${completion.complete?'':'<button class="reset-btn" id="continueOnboardingConfigBtn" style="margin-top:10px; color:var(--violet); border-color:var(--violet)">Continuar preenchimento</button>'}
  </div>`;
  const brokerIsPropFirm=isPropFirm(brokerFor(ob.corretora)||{});
  const reserveFcrStatus=ob.reserveFcrStatus || ((+ob.reserveFcrCurrent||0)>=(+ob.reserveFcrRequired||0)?'Regular':'Insuficiente');
  const reserveFeoStatus=ob.reserveFeoStatus || ((+ob.reserveFeoCurrent||0)>=(+ob.reserveFeoRequired||0)?'Regular':'Insuficiente');
  const segmentation=[
    ob.centralCashMainPct?`Patrimonial ${esc(ob.centralCashMainPct)}%`:'',
    ob.centralCashAgilePct?`Operacional ${esc(ob.centralCashAgilePct)}%`:'',
    ob.centralCashLiquidityPct?`Liquidez ${esc(ob.centralCashLiquidityPct)}%`:'',
    ob.centralCashExternalPct?`Externos ${esc(ob.centralCashExternalPct)}%`:'',
    ob.centralCashOtherPct?`Outros ${esc(ob.centralCashOtherPct)}%`:''
  ].filter(Boolean).join(' · ');
  const propRulesRows=brokerIsPropFirm ? `
    ${row('Drawdown Diário Permitido (prop firm)', esc(ob.propDailyDrawdown))}
    ${row('Drawdown Máximo Permitido (prop firm)', esc(ob.propMaxDrawdown))}
    ${row('Regra de Trailing Drawdown', esc(ob.propTrailingRule))}
    ${ob.propTrailingDescription ? row('Descrição do Trailing', esc(ob.propTrailingDescription)) : ''}
    ${row('Meta de Lucro da Avaliação', esc(ob.propProfitTarget))}
    ${row('Nº Mínimo de Dias Operados', esc(ob.propMinTradingDays))}
    ${ob.propAbsenceRules ? row('Regras de Ausência', esc(ob.propAbsenceRules)) : ''}
    ${row('Regra mais restritiva prevalece', ob.restrictiveRuleAccepted?'aceito':'pendente')}` : '';
  el.innerHTML=`${completionHTML}<table class="dtable" style="max-width:560px">
    ${row('Operador', esc(ob.operador))}${row('Supervisor(a)', esc(ob.supervisor))}
    ${row('Corretora / Prop Firm', esc(ob.corretora))}${row('Plataforma', esc(ob.plataforma))}
    ${row('Alavancagem da corretora', esc(ob.alavCorretora))}
    ${row('Login da Conta', esc(ob.brokerLogin||''))}${row('Servidor da Corretora', esc(ob.brokerServer||''))}
    ${row('Senha de Investidor', maskedInvestorPassword)}
    ${row('Início do período', S.params.inicio||'—')}${row('Saldo inicial', fmtMoney2(S.params.saldoIni||0))}
    ${row('Moeda-base da conta', esc(normalizeAccountCurrency(ob.moedaBase)))}
    ${propRulesRows}
    ${row('Sistema de risco', pr.name+' · '+Math.round(pr.pct*100)+'%')}
    ${row('Capital nominal Conta Mestre', fmtMoney2(S.params.saldoIni||0))}
    ${row('FCR mínimo exigido', ob.reserveFcrRequired?fmtMoney2(+ob.reserveFcrRequired):'—')}
    ${row('FCR atual', ob.reserveFcrCurrent?fmtMoney2(+ob.reserveFcrCurrent):'—')}
    ${row('Cobertura FCR', ob.reserveFcrCoveragePct?pctText(+ob.reserveFcrCoveragePct):'—')}
    ${row('Status do FCR', '<span style="color:'+(reserveFcrStatus==='Regular'?'var(--f1)':'var(--f4)')+'">'+esc(reserveFcrStatus)+'</span>')}
    ${row('Despesas mensais estrutura', ob.reserveMonthlyExpenses?fmtMoney2(+ob.reserveMonthlyExpenses):'—')}
    ${row('FEO mínimo exigido', ob.reserveFeoRequired?fmtMoney2(+ob.reserveFeoRequired):'—')}
    ${row('FEO atual', ob.reserveFeoCurrent?fmtMoney2(+ob.reserveFeoCurrent):'—')}
    ${row('Cobertura FEO', ob.reserveFeoCoveragePct?pctText(+ob.reserveFeoCoveragePct):'—')}
    ${row('Meses cobertos FEO', ob.reserveFeoMonthsCovered?(+ob.reserveFeoMonthsCovered).toFixed(1).replace('.',',')+' meses':'—')}
    ${row('Status do FEO', '<span style="color:'+(reserveFeoStatus==='Regular'?'var(--f1)':'var(--f4)')+'">'+esc(reserveFeoStatus)+'</span>')}
    ${row('Segregação FCR/FEO', ob.reserveSegregationAccepted?'aceita':'pendente')}
    ${row('Caixa Central', esc(ob.centralCashStatus||''))}
    ${row('Custódia Caixa Central', esc(ob.centralCashCustody==='Outra'?(ob.centralCashCustodyOther||'Outra'):ob.centralCashCustody))}
    ${row('Segmentação Caixa Central', segmentation||'—')}
    ${row('Liquidez FCR', esc(ob.fcrLiquidity||''))}
    ${row('Liquidez FEO', esc(ob.feoLiquidity||''))}
    ${row('Livro-razão patrimonial', esc(ob.cashLedgerStatus||''))}
    ${row('Score rastreabilidade', ob.centralCashTraceabilityScore?esc(ob.centralCashTraceabilityScore)+'/100':'—')}
    ${row('Política Caixa Central', ob.centralCashPolicyAccepted?'aceita':'pendente')}
    ${row('Equity Protector (hard stop)', '<span style="color:var(--f4)">'+fmtMoney2(ep)+'</span>')}
    ${row('Objetivo do período', '<span style="color:var(--f1)">'+fmtMoney2(obj)+'</span>')}
    ${row('Uso de Equity Protector', esc(ob.epStatus||''))}
    ${row('Plataforma Equity Protector', esc(ob.epPlatform==='Outra.'?(ob.epPlatformOther||'Outra'):ob.epPlatform))}
    ${brokerIsPropFirm ? row('Limite diário da mesa', esc(ob.epDailyLimit||'')) : ''}
    ${brokerIsPropFirm ? row('Base do cálculo diário', esc(ob.epPropDailyBase||'')) : ''}
    ${row('Limite DD estatutário do período', esc(ob.epMaxDrawdown||''))}
    ${row('Regra mais restritiva (EP)', ob.epRestrictiveAccepted?'aceita':'pendente')}
    ${row('Consentimento Estatuto V10.0', ob.consentAccepted?'aceito':'pendente no próximo reinício')}
    ${row('Resumo e Confirmação do Período', ob.summaryAccepted?'confirmado':'pendente no próximo reinício')}
    ${row('Documento de consentimento', esc(ob.consentDocument||'Estatuto JP WEALTH UNIFICADO.pdf'))}
    ${row('Aceite registrado em', esc(ob.consentAcceptedAt||''))}
    ${row('Operador do aceite', esc(ob.consentOperator||''))}
  </table>
  ${brokerIsPropFirm ? '<p class="expl" style="font-size:calc(11px * var(--fs-scale)); color:var(--ink-faint); margin-top:10px">As regras externas da mesa proprietária não substituem o Estatuto JP Wealth. Quando houver conflito, o painel deve considerar a regra mais restritiva.</p>' : ''}
  <p class="expl" style="font-size:calc(11px * var(--fs-scale)); color:var(--ink-faint); margin-top:10px">Senha de investidor exibida de forma mascarada por segurança. Nunca use nem registre a senha master de operação neste painel.</p>
  ${equityProtectorEducationHTML()}
  ${leverageEducationHTML()}
  <button class="reset-btn" id="redoOnboardingBtn" style="margin-top:12px; color:var(--violet); border-color:var(--violet)">📋 Visualizar / Editar Formulário de Início</button>`;
  const continueBtn=$('continueOnboardingConfigBtn');
  if(continueBtn) continueBtn.addEventListener('click',openFirstIncompleteOnboarding);
  $('redoOnboardingBtn').addEventListener('click',()=>openOnboardingModal((S.onboarding&&S.onboarding.done)?'edit':'new'));
}
