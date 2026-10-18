# Integração com personas

## Entrada e inventário
Use este modo para cobertura inicial ou lacuna nova de jornada, estado ou fronteira. Entrada: objetivo autorizado, snapshot, fontes vigentes, comandos e cobertura existente. Resultado: proteções complementares úteis, recibos e pendências. O projeto determina linguagem, runner e ferramentas; não instalar framework por hábito.

Registre jornada/regra → fonte → propriedade/fronteira → estados → IDs → comando obrigatório → evidência atual. Reutilize o registro vigente. Mesma regra com outro nome não justifica teste duplicado; teste de cálculo não dispensa UI que envia a unidade errada ou persistência que perde dados. Legado sem prova suficiente fica pendente. Comportamento observado não é contrato aprovado; conflito normativo bloqueia a expectativa dependente.

## Equipe por missão
O coordenador seleciona lacunas e separa escrita. Operador informado recebe fontes aprovadas; iniciante recebe objetivo, UI e documentação pública; operador de situações adversas conhece riscos pertinentes. Conceda somente conhecimento/ações necessários. Personas não são usuários humanos reais nem independência estatística. Instrução de persona não cria sandbox: configure isolamento pelas ferramentas e registre o que foi apenas instruído.

Exploradores usam sessões e storage separados, sem receber achados alheios. Retornam estado inicial, ações executadas, resultado observado, expectativa/fonte quando conhecida, evidência e hipótese. Iniciante sem oráculo registra dificuldade; coordenador verifica contrato antes de promover a bug. Engenheiro deduplica, escolhe o menor nível que reproduz a lacuna e é único escritor de testes. Crítico recebe contratos, saída e evidência, sem justificativa persuasiva do autor; busca contraprovas em cópias. Respeite vagas e escale fases; não simule revisão independente.

Modelos em ../assets/personas são definições de agentes de projeto. Confirme interface, descoberta e execução no runtime. Se nome customizado não for invocável, passe o papel a subagente genérico disponível e declare fallback. Sem delegação, não afirmar múltiplos agentes. agents/openai.yaml descreve a skill, não executa personas.

## Explorar e converter
1. Execute software real em ambiente descartável com dados sintéticos. Declare alvo, versão, storage e integrações substituídas. UI/CLI/API reais conforme fronteira; fixture prepara dados sem substituir a ação avaliada. Nunca perfil ou credencial de produção.
2. Cubra jornadas críticas, estados, equivalência, limites e combinações por risco. Concorrência exige ações realmente concorrentes. PWA exige SW/offline quando esse ciclo é o risco; bloquear SW nos demais casos não comprova upgrade.
3. Converta achado útil em teste isolado: ID estável, preparação, ação, assertiva de contrato, limpeza, comando e evidência. Prefira seletores semânticos e espera por condição; reabertura/leitura independente para persistência.
4. Demonstre PASS correto e rejeição de violação representativa em cópia, preservando trabalho e primeira falha. Mutação seletiva, sem pontuação universal. Fixe expectativa antes de julgar a implementação.
5. Integre casos na entrada completa, verificando descoberta/IDs obrigatórios. Depois execute código sem modelo; personas somente para lacuna nova, risco ou exploração solicitada.

## Entrega e correção
Uma entrada versionada executa source checks, builder oficial, suíte e artefato distribuído. Focais aceleram edição; não substituem aceite final. Não exigir teste de executável inexistente antes do build. Registre SHA/fingerprint de bytes, configuração, IDs/status por ambiente, primeira falha e duração. Se teste gerar artefato de novo, confira drift. Validador de JSON fornecido não executa nem autentica a suíte.

Contraprovas pela entrada permanente: vazio; obrigatório removido/filtrado/pulado; relatório parcial/antigo/replay; alteração pós-teste; timeout/ambiente ausente; mutação real; falha anterior. Legado opaco não ganha granularidade inventada. Skip/neutral de CI não comprova execução. Gate preparado, CI executado, bloqueio de integração e publicação são estados separados.

Com tarefa ativa autorizada, Codex investiga regressão introduzida, preserva caso e corrige código mínimo. Falha de teste/ambiente recebe reparo próprio sem ocultar falha do produto. Contrato novo exige fonte/autorização. Dívida anterior não autoriza manutenção adjacente. Build/CI sem agente detectam e bloqueiam. Limite ou falha persistente encerra tentativa pendente; repetir até verde não comprova correção.

## Eficiência
Meça proteções úteis aceitas, defeitos únicos, falsos alarmes, redundância, instabilidade, tempo e tokens incluindo coordenação/revisão/retrabalho. Separe adoção e manutenção, cache como parcela da entrada, execução determinística sem modelo. Compare agente único e tentativas genéricas equivalentes; mais orçamento não comprova técnica melhor. Sem ganho demonstrado, reserve a equipe aos riscos em que agregar. Nunca prometer todas as entradas/estados ou ausência de bugs.
