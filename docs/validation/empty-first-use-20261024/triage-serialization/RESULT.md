# Session write serialization — triagem causal somente leitura

Candidate: `1b695b809fe80c26`; branch `codex/primeiro-acesso-vazio-20261024`; HEAD `a4bf278cd4dc38bbaa5b905ed17a79e33684fb67`.

## Resultado

**TEST_HARNESS_FAIL por fixture implícita**, sem defeito de produto demonstrado neste focal. O runner bruto classificou `PRODUCT_FAIL`; conservar esse resultado histórico bruto e registrar a reconciliação causal separadamente. Não se concede PASS à suíte completa.

O focal injeta somente o agregado Alladin, mas seis asserções dependem de `S.accounts.length > 0`. Antes da tarefa aprovada, essas contas vinham dos quatro exemplos de DEFAULTS. A nova base explicitamente vazia tem zero contas desde antes da ação. Logo, essa contagem não demonstra perda, finalização ou falha enquanto não se instala uma conta sintética como pré-condição.

Locais: `abrir` linhas60–83 não cria conta; setup Alladin linha190/277 e sondas343–345 não criam conta; sentinelasSK204, SH266, SH2 300 e SI353. Demais asserções foram exercitadas sem falhar.

## Reprodução bruta

Com runtimePython existente3.12.14, Nodev24.19.0 no PATH e Chrome1223 (headless), executar `python3 tools/session_write_serialization_test.py`. Saída completa em `raw-current.log` (exit1):

- SK: `{'contas':0,'alladinDisco':True}`.
- SH e SH2: acusação baseada unicamente em contagem0, com documento anterior preservado e recusa/read-back corretos pelas demais asserções.
- SI: geracao antiga/doc ausente/doc ilegivel acusados pela mesma contagem0; guardas de persistência e recusa de save não falharam.

## Prova diferencial sem editar arquivos do projeto

`run-disposable.py fixture-only` carrega o teste original sem editar seus bytes e envolve apenas `abrir`: após o boot real adiciona em RAM uma conta sintética declarada (`SERIALIZATION-SYNTHETIC`), antes dos saves já existentes. Asserções, sequência, prazos, APIAlladin, produto e fixtures originais permanecem intactos. Os snapshots do recibo confirmam `accounts:0` e storage principal ausente antes da instalação sintética.

Resultado: **PASS integral**, exit0, `fixture-only.log` e `fixture-only-receipt.json`.

## Contraprova

`run-disposable.py counter-destructive` utiliza a mesma conta sintética e, exclusivamente na memória das páginas descartáveis, substitui o handler de finalização remota por um handler destrutivo que apaga `S.accounts`. Nenhum arquivo de produto ou teste é alterado.

Resultado: **rejeição**, exit1; SI acusa precisamente os três cenários destrutivos. `counter-destructive.log` e recibo documentam a detecção. A fixture explícita restaura a pré-condição; não torna o juiz permissivo à perda de contas.

## Menor delta recomendado

Somente no setup de `tools/session_write_serialization_test.py`, instalar uma conta sintética explicitamente nomeada antes dos saves existentes, para que as sentinelas tenham objeto a preservar. Preferir também conferir a pré-condição instalada. Preservar todas as asserções atuais e os testes de lost-update, locks, degraded, read-back, broadcast, documentos, recuperação e epoch. Não alterar o produto; não repor exemplos em DEFAULTS; não enfraquecer contagens para aceitar0.

O novo teste de primeiro acesso continuará sem fixture de estado, protegendo o contrato vazio de forma independente.

## Integridade

`frozen-input-recheck.json`: **664/664 entradas sem divergência**; teste originalSHA256 `a3595c0c4a60c38c07287f55bbfb6b87b0fbf54b0428c95f652268a7a481f32e`. Nenhuma edição de produto/teste/Git, rebuild, waiver, skip ou ampliação de timeout. Artefatos de triagem ficam somente neste diretório temporário. A suíteFULL em andamento permanece sendo avaliada pelos seus bytes congelados.
