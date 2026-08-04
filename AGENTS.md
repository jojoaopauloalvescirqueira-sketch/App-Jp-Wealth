# AGENTS.md — Protocolo para agentes de IA

## Missão

Trabalhar no JP Wealth Risk Terminal como sistema financeiro crítico de contabilidade, risco e execução. Não tratar este repositório como protótipo descartável.

## Hierarquia de autoridade

1. `docs/normative/Estatuto_JP_WEALTH_UNIFICADO.pdf`.
2. Decisões formais e atas aprovadas pelo gestor, quando adicionadas em `docs/decisions/`.
3. Regras documentadas em `docs/architecture/` e `docs/governance/`.
4. Código vigente e testes.
5. Texto de interface e comentários informais.

Quando houver conflito, não escolher silenciosamente. Registrar o conflito e pedir decisão humana.

## Proibições

- Não inventar, otimizar ou reinterpretar regra financeira.
- Não alterar percentuais, fatores, limites, fórmulas ou artigos por iniciativa própria.
- Não apagar, migrar ou normalizar dados reais sem backup e autorização.
- Não substituir o estado salvo por `DEFAULTS` em caso de erro.
- Não remover bloqueios de instrumentos, quarentena, LIFO, MDD ou validações de governança.
- Não armazenar senha master.
- Não inserir credenciais reais em código, testes, commits ou documentação.
- Não reordenar arquivos JavaScript sem validar `src/js/manifest.json` e executar todos os testes.
- Não fazer uma refatoração ampla junto com mudança de regra financeira.

## Fluxo obrigatório de alteração

1. Ler esta instrução e os documentos pertinentes.
2. Identificar a regra afetada e os arquivos envolvidos.
3. Criar plano pequeno e delimitado.
4. Criar backup ou branch antes da mudança.
5. Implementar o menor diff possível.
6. Executar `python3 tools/validate_project.py`.
7. Executar `python3 tools/smoke_test.py`.
8. Mostrar diff e riscos residuais para revisão humana.
9. Atualizar `CHANGELOG.md` e documentação afetada.
10. Somente então criar commit rastreável.

## Classificação de mudanças

- **N0 — Visual:** CSS, texto e layout sem impacto funcional.
- **N1 — Funcional não normativo:** navegação, acessibilidade, exportação, experiência do usuário.
- **N2 — Dados:** schema, migração, backup, importação, localStorage.
- **N3 — Normativo:** risco, lote, DD, alavancagem, perfis, LIFO, quarentena, contabilidade.

Mudanças N2 e N3 exigem backup, testes específicos e aprovação explícita do gestor.

## Modelo de execução JavaScript

Os arquivos são scripts clássicos executados na ordem de `src/js/manifest.json`. Eles compartilham o escopo global legado do HTML original. Não converter para ES Modules em uma mudança casual. Essa conversão é um projeto próprio, com testes de regressão e mapa completo de dependências.

## Definição de concluído

Uma tarefa só está concluída quando o código funciona, os testes passam, o diff está explicado, a documentação foi atualizada e nenhuma regra financeira foi alterada sem autorização formal.
