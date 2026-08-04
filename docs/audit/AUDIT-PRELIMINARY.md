# Auditoria preliminar do artefato original

```text
JP WEALTH RISK TERMINAL V9.1 — AUDITORIA PRELIMINAR
Data: 2026-08-03

Integridade
- Arquivo HTML UTF-8 válido, 854.732 bytes e 7.855 linhas.
- SHA-256: 9095174aee1954c204d2ecf98c029d4499aa5c587d21dcac84fa129a64223b7e
- Um bloco CSS interno e um bloco JavaScript interno.
- Nenhuma dependência externa de CSS ou JavaScript.
- Logotipos de corretoras incorporados em base64.

Teste técnico
- JavaScript aprovado em verificação sintática pelo Node.js.
- Inicialização testada em Chromium isolado, sem erros JavaScript.
- Oito telas de navegação acessíveis: Dashboard, Execution Board, Parâmetros,
  Motor de Lote, Contas, Checklist, Contabilidade e Configurações.
- Funções de cálculo e backup foram carregadas.

Persistência
- Estado principal salvo em localStorage sob a chave: jpwealth_v9_state.
- Preferências de interface usam outras chaves locais.
- O HTML contém o programa e um estado DEFAULTS, mas o histórico real do operador
  normalmente permanece no armazenamento do navegador e não é incorporado ao HTML.

Dependência de rede
- Atualização automática das oito cotações FX usa Frankfurter API.
- Falha de rede mantém os últimos preços salvos.

Riscos prioritários
- Preservar o perfil do navegador e a origem/domínio onde o aplicativo era usado.
- Não substituir o deploy original antes de exportar o estado existente.
- Senhas de investidor podem existir em texto simples no localStorage e em backups
  quando o usuário escolhe incluí-las.
```
