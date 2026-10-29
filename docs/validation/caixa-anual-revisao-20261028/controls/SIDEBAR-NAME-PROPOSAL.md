# Quarta expectativa literal — trilha de navegação

A busca final localizou uma expectativa adicional em tools/contextual_sidebar_test.py:363. Ela exige o breadcrumb Gerenciamento/Contabilidade para a rota antiga forex-reconciliation. O produto renomeado mantém a rota e apresenta Gerenciamento/Caixa Anual.

Patch de uma linha: trocar somente a palavra esperada Contabilidade por Caixa Anual, preservando rota, outraspalavras, asserção all(word in location), IDs, grupos, timeout, tolerâncias e proteção de estado. Nenhuma alteração de aplicativo.

Este quarto arquivo não estava listado na autorização dos três juízes iniciais; por AGENTS requer autorização específica N3, revisão independente e contraprova antes da aplicação. Rodar o mesmo caso antes/depois e confirmar que o nome contrário ainda é rejeitado. O patch é SIDEBAR-NAME.patch. Demais critérios e contagens do gate permanecem.
