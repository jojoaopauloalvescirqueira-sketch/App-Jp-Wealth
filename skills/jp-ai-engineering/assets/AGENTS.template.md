# Instruções do projeto

Modelo para adaptar às fontes atuais; integre ao conteúdo existente. Nenhuma regra de produto é criada por este modelo.

## Padrões e fontes

Registre linguagem, arquitetura, estilo, contratos e documentos aprovados; preserve instruções por diretório e overrides. Identifique regras propostas separadamente das vigentes.

## Comandos

Documente preparo, testes focais, comando único da suíte obrigatória completa e matriz/CI real. Registre requisitos de ambiente e timeout. Comando local e CI aplicam os mesmos critérios.

## Desenvolvimento e validação

- Cada bug corrigido deixa caso de regressão permanente: falha pelo defeito e passa corrigido, mantendo estímulo e expectativa.
- Cada regra nova/alterada tem fonte, escopo, oráculo e teste que aceita caso válido e rejeita violação representativa.
- Rode focais durante edição e toda a suíte obrigatória acumulada antes de concluir correção, melhoria ou versão.
- Zero casos, proteção obrigatória pulada, evidência antiga, runtime ausente e falha anterior não são aprovação. Preserve primeira falha e tentativas.
- Não remova nem enfraqueça proteção para obter verde. Mudança de contrato autorizada exige fonte, histórico e proteção substituta pertinente.
- Preserve trabalho e dados existentes; não invente normas ou autorização. Testes ficam versionados e executam sem modelo.

## Índice das proteções e legado

Vincule o registro existente ou manifesto junto aos testes: ID → fonte → escopo → resultado esperado → casos → comando/CI → estado. Inventarie todas as regras identificadas; cobertura antiga migra progressivamente e permanece explicitamente pendente até demonstrada. Não duplique especificações extensas.

## Limites atuais

Registre falhas anteriores, cobertura pendente, ambientes não executados e estado observado de descoberta de instruções/CI/proteção de integração. Criar configuração não comprova carregamento, execução ou imposição remota.

## Integração e entrega
- Entrada completa (runner + descoberta + gates + artefato final): comando real.
- CI chama a mesma entrada; bloqueio remoto: verificado ou pendente.
- Inventário de jornadas/proteções e pendências: referência única.
- Personas: cobertura inicial ou lacuna nova.
- Contraprovas pelo comando completo e fingerprint: referência do recibo.
