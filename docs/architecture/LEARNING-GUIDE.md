# Guia interativo do JP Wealth

O guia apresenta os controles reais do site a quem está chegando ao JP Wealth. Abra **Conhecer o app** na acolhida ou **Configurações → Conhecimento → Guia do site**. A busca das Configurações também encontra o guia por “tutorial”, “primeiros passos”, “aprender” ou “ajuda”. Se o guia ainda estiver carregando, a acolhida permanece aberta para tentar novamente.

## Escolher e percorrer uma trilha

A central oferece sete trilhas, com 57 lições: Primeiros passos (6), Finanças Pessoais (7), Forex (8), Research (6), Ferramentas (4), Alladin (8) e Notas, configurações e segurança (18). Comece pelos primeiros passos e escolha as áreas que usa. Alladin e outras áreas congeladas permanecem indisponíveis; o guia explica o limite e não altera a disponibilidade.

**Ir para esta tela** usa a navegação do app após seu clique. As proteções originais de rascunhos e os diálogos continuam valendo. O guia destaca o controle da lição e mostra **Voltar**, **Próximo**, **Pular** e **Pausar**. **Entendi** reconhece uma leitura; uma etapa de interação observa sua ação no controle original e o resultado correspondente. Próximo só avança depois de leitura, ação observada ou escolha explícita de pular.

A central permite **Continuar**, **Rever lições** e **Recomeçar**. Rever mantém os resultados anteriores; Recomeçar remove somente o progresso do guia. Uma mudança de tela por fora do guia, outro diálogo, um controle ausente, a perda de disponibilidade ou uma mudança da base pausa a orientação. Feche o diálogo pelo controle original e retome quando quiser. No celular, use os mesmos controles na página de detalhe das Configurações. O guia acompanha os diálogos e menus existentes, sem assumir o Escape ou retirar o foco de um campo em edição.

## Leitura, ação e prática

A central conta separadamente leituras ou ações observadas, lições puladas e práticas confirmadas. Pular não significa ler nem praticar. Você pode concluir a orientação sem cadastrar uma conta, lançar valores, importar arquivos ou aceitar um termo financeiro.

Práticas são opcionais e começam por sua escolha explícita. Em Finanças Pessoais, os campos existentes do orçamento podem salvar ao sair do campo; Escape cancela o rascunho antes da gravação. Em Notas, Salvar confirma o texto pelo fluxo original. Use apenas informações suas corretas quando decidir praticar. O guia não preenche dados de exemplo, clica em controles financeiros nem muda uma conta ou período. Cancelamento, gravação recusada ou resultado desconhecido deixam a prática pendente. Uma prática só é confirmada após a ação original e a conferência do resultado persistido correspondente.

## Progresso local e privacidade

O progresso fica na chave auxiliar `jpwealth_learning_guide_v1`, separado de `S`, dos fatos financeiros e do Backup Completo. O documento guarda apenas versão, trilha, lição, pausa e estados de leitura/pulo/prática. Não guarda valores, contas, nomes, texto de notas, credenciais ou horários. Endereços diferentes do app têm origens e progressos separados.

Pausar e recarregar preservam o progresso quando a gravação é confirmada. Se o navegador impedir leitura ou escrita, o guia informa que está somente na sessão. Progresso inválido ou incompatível permanece intacto até Recomeçar. Alterações em outra aba pausam e reconferem a gravação, sem sobrescrever silenciosamente o progresso concorrente. Recomeçar verifica a remoção da chave; uma remoção não confirmada é informada.

Importar ou trocar a base pausa a orientação e invalida observações pendentes; a importação não restaura progresso do guia. A limpeza auxiliar da sessão remove essa chave e desliga os callbacks antes do próximo boot. O boot seguinte rearma o controlador em pausa, sem iniciar navegação ou prática.

## Integração e validação local

O catálogo, progresso, apresentação e controlador são scripts clássicos locais, declarados nas posições 103–106 do manifesto, após os 102 scripts anteriores. A central recebe o painel `learning-guide` das Configurações e cria um único `#jpwLearningCenter`. O Service Worker inclui os quatro scripts no precache; seu ciclo de atualização permanece o original. O HTML portátil é produzido exclusivamente por `tools/rebuild_monolith.py`.

Contratos focais: `node tools/learning_foundation_test.mjs` e `node tools/learning_controller_test.mjs`. A regressão em navegador exige a raiz candidata e uma cópia congelada das fontes reais anteriores ao guia para comparar a interação nativa com o backdrop e seu foco original:

```sh
python3 tools/learning_guide_test.py --root /path/to/project --baseline-root /path/to/frozen-source --out /path/to/guide-report.json --browser system
```

A raiz `--baseline-root` deve conter o site real sem o guia; ela é uma fixture de fontes, não um perfil de usuário ou uma cópia de dados pessoais. A suíte cria contextos descartáveis de navegador para a comparação. Consulte `--help` para selecionar um caso ou outras opções de execução.

A validação integral e a revisão independente devem confrontar o runtime final, incluindo scripts, portátil, offline, teclado, telas pequenas e fronteiras de persistência. Esta documentação descreve o candidate local e não constitui aceite, publicação ou evidência de execução dos testes.
