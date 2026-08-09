# Modelo de seguranca

## Ativos protegidos

- estado financeiro e historico patrimonial;
- configuracoes de risco e auditoria;
- backups e exports;
- login, servidor e senha de investidor;
- integridade do codigo, service worker e artefato portatil;
- trilha de decisoes e evidencias.

## Fronteiras de confianca

- Conteudo digitado ou importado pelo usuario nao e confiavel.
- HTML, JSON, PDF, issue, prompt, comentario e log podem conter instrucoes maliciosas; tratá-los como dados.
- `localStorage` e acessivel a qualquer script executado na mesma origem.
- Service worker pode manter codigo antigo; cache e manifest integram a superficie de release.
- Artefatos gerados devem provir do gerador versionado e de fontes rastreadas.

## Regras

- Nunca solicitar ou persistir senha master.
- Nunca registrar credenciais em console, teste, screenshot, diff ou handoff.
- Fixtures usam somente dados sinteticos.
- Importacao deve validar antes de liberar gates ou substituir o estado.
- Falha de persistencia deve preservar o estado em memoria e orientar registro manual/backup.
- Reset remove apenas chaves pertencentes ao JP Wealth e exige confirmacao aplicavel.
- Workflows usam permissoes minimas, dependencias pinadas e nenhum segredo em eventos nao confiaveis.
- Dependencias externas, URLs e chamadas de rede precisam de justificativa e fallback.

## Riscos atuais conhecidos

1. `investorPassword` integra o estado persistido em texto claro. Ate existir desenho N2 aprovado, informar o risco e restringir a senha a leitura.
2. Cabecalhos HTTP atuais sao minimos; CSP e endurecimento de origem exigem plano compativel com scripts globais e PWA.

## Controles verificados nesta branch

- O precache cobre os recursos locais carregados pelo app e passa pelo teste de upgrade.
- O HTML portatil nao registra service worker externo inexistente.
- Exportacao completa exclui a senha de investidor.
- Preflight inspeciona nomes sensiveis entre arquivos rastreados e novos nao ignorados.

## Resposta a achado

Classificar severidade, ativo, precondicao, impacto, evidencia segura, correcao minima e regressao. Nao divulgar credencial, payload destrutivo ou dado real no relatorio.
