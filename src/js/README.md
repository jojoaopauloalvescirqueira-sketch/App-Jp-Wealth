# JavaScript

Os arquivos foram separados nos mesmos pontos de seção do script original. Nenhuma função foi transformada em módulo nesta etapa.

## Ordem

A ordem de carregamento está em `manifest.json` e é reproduzida em `index.html`. Ela não é estética: faz parte do contrato de execução do sistema legado.

## Diretórios

- `00-core`: fontes centrais, estado, persistência e helpers.
- `10-domain`: regras de risco e operação.
- `20-ui`: renderização e interação visual.
- `30-accounting`: contabilidade, MEI-JP e projeções.
- `40-app`: inicialização e orquestração.

Antes de mover uma função entre arquivos, crie teste de caracterização e execute a validação completa.
