# Disponibilidade reversível de módulos

CHG-MODULE-AVAILABILITY-20260924, N2/A3. Base inspecionada ad5c23e7884be108ceaf35acd26fb1c3b28b57db. Candidate isolado, sem integração nem aceite. Decisão de produto: [fonte única](../decisions/2026-09-24-alladin-congelado.md).

## Fonte e alcance

`JPWModuleAvailability` lê `localStorage.jpw_module_availability_v1`: `{schemaVersion:1,modules:{alladin:"frozen"}}`. Mapa sparse dos IDs research/forex/personal-finance/alladin; enum active/frozen. Defaults em memória: Alladin frozen e os demais active. Nenhuma escrita inicial, migração de S ou normalização automática. Ativo significa disponível, não módulo completo. Preferência por navegador/perfil/origem; portas diferentes não se sincronizam. Não é autenticação nem barreira contra DevTools.

`inspect` conserva escolhas individualmente válidas em v1, aplicando fallback só aos campos inválidos; JSON/top-level/versão incompatível mantém raw e usa defaults de apresentação. `validate` recusa qualquer incompatibilidade no import. Escritas ficam bloqueadas com raw inválido/ilegível; exportação recupera o bruto. Falha de leitura conserva último estado confirmado da sessão; inicialmente defaults. `setState` compara raw observado, escreve e relê; falha comprovada conserva estado, resultado desconhecido bloqueia tentativas até releitura segura. Não há atomicidade garantida entre abas: eventos storage convergem para o raw observado, conflitos não reaplicam intenção antiga.

## Interface e acessos

Seção única Módulos e disponibilidade no Editor, movida pelo host existente da Central de Configurações. Busca e links administrativos apontam para ela. Dashboard/apoio não congeláveis. A ordem canônica conserva os seis IDs e os mesmos nós/listeners; só a projeção operacional é filtrada. navApply consulta política antes de render; shell consulta antes de explorar; notificações consultam antes de fechar/trocar conta/período e novamente em callbacks adiados. Aliases permanecem. Não há router URL ou tela persistida nova.

Congelar localmente exige ausência de trabalho pendente, confirmação humana e readback. Cancelamento/falha não congela. Se o destino estiver aberto e seguro, vai ao Dashboard. Descongelar restaura acesso sem navegar. Política bloqueia novas ações de superfícies suspensas; confirmações já iniciadas não são abandonadas. Suporte e gestão permanecem disponíveis.

## Trabalho e dados

`JPWModuleWork` é adaptador de apresentação dos quatro módulos, não escritor financeiro. Alladin declara estado de modal; Research expõe drafts existentes; Forex usa guards/estados existentes; PF preserva seus formulários. Pendência impede congelamento local; storage remoto preserva RAM/DOM, suspende interação e apresenta retomada explícita/backup. Providers capturam texto de rascunhos, incluindo formulários suspensos, sem senha/PIN/arquivo e sem replay. Memória não é gravação durável. SUBMITTING/COMMITTED_WARNING Alladin continua seu fluxo iniciado.

Não alterar S.alladin, ledger, cálculos, datas, totais ou serviços compartilhados. Dashboard e Notificações mantêm readmodels. Scripts permanecem com ordem relativa original; leitores Alladin continuam carregados. Só apresentação operacional/entrada é condicionada, não toda execução do módulo.

## Backup e recuperação

Nova chave allowlisted em workspace.schemaVersion 1. Ausente em backup antigo preserva destino; null remove override e adota default. Valor importado inválido/futuro recusa antes de escrever. Consentimento lista mudanças, inclusive descongelamento; preferência mudada entre consentimento e execução recusa import. Journal/readback existentes continuam; projeção parcial reconsulta disponibilidade do disco sem declarar restore completo. Finalizar preserva preferência nos fluxos existentes; allowlist remove-a somente onde auxiliares são explicitamente removidos.

Raw local inválido não é omitido silenciosamente: Backup Completo oferece confirmação de exportação de recuperação. Conserva bruto como texto em workspace.drafts, omite só aplicação automática dessa preferência; dados financeiros completos. Na restauração conserva disponibilidade do destino. Não é round-trip integral da preferência; limites existentes continuam, sem truncamento. Conteúdo recuperado não executa script/comando. Leitura de armazenamento indisponível não inventa raw recuperado.

## Reversão e limites

Descongelar explicitamente reverte a disponibilidade. Rollback de código para base preserva a chave, mas aquele build a ignora e não impõe congelamento; importador antigo rejeita backup com chave nova. Preserve backup anterior compatível e backups novos separados; use build compatível para restaurar o novo formato. Não apague chave nem dados para abrir código antigo, não converta arquivos silenciosamente. Testes sintéticos e recibos externos demonstram o comportamento verificado; não há aceite humano automático.

## Evidência e consumidores

Focais module_availability_core_test, module_availability_test, module_availability_work_test, module_availability_backup_test; suites internas Alladin com fixture active explicitamente isolada; suites de preservação com defaults. Full, PWA e auditoria permanecem obrigatórios; resultados exatos no DELIVERY.md do diretório externo /Users/joaopauloalves/.codex/module-availability/20260924/evidence. Nenhuma classificação anterior é reescrita.
