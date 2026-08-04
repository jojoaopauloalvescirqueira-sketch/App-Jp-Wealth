# Testes

A base inicial contém dois níveis:

1. `tools/validate_project.py`: integridade estrutural, hashes, sintaxe, ordem e reconstrução portátil.
2. `tools/smoke_test.py`: inicialização real em Chromium, carregamento do estado e navegação pelas oito telas.
3. `tools/finalize_session_test.py`: checkpoint após reload, preço manual, exportação confirmada, gate contra corrida assíncrona, exclusão isolada de chaves, frase final, importação, coordenação entre abas, caches externos, captura de console/pageerror e responsividade, sobre fonte e monólito quando possível.

Próxima etapa recomendada: testes de caracterização para `compute()`, migrações, backup/importação, perfis, matriz quadrifásica, LIFO e contabilidade.
