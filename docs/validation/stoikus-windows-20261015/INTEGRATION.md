# Stoikus 1.23.0 — alinhamento e controle de janelas — R5

Candidato local de fontes, derivado da base 1.22.3. MQL **1.230**, cálculo **1.9.0**. Base Git `0037bd3c8a7ab2b4e21f7fdcb60f66ed93230874`, worktree existente `/private/tmp/jpw-stoikus-continuity-20261014`. O delta anterior foi preservado; esta tarefa não criou commit nem alterou site/instalador/publicação.

## Escopo e evidências

[Plano autorizado](../../superpowers/plans/2026-10-15-stoikus-window-controls.md), [estudo visual](DESIGN.md), [prévia com dados fictícios](../../preview/stoikus-window-controls/index.html), [roteiro de aceite](GUIA_ENSAIO.md) e [guia de uso diário](../../../mt5/jpw-alavancagem-atual/STOIKUS_USO_DIARIO.md).

A revisão acrescenta um resumo Compacto com largura inicial de 280 pixels lógicos, fundo ARGB transparente e métricas com escopos explícitos. Conta e NoCuda recebem alinhamento e paginação compartilhados, movimento, redimensionamento e minimização. As preferências visuais são versionadas e separadas dos contratos anteriores; carregar/redesenhar não grava. Rascunhos ficam em memória ao minimizar, sem aplicar. Recursos da assinatura aprovada, fórmulas, índices, atalhos, máscaras e dados permanecem preservados.

Os relatórios por entrega e pareceres independentes ficam no ledger `.superpowers/sdd/2026-10-15-stoikus-window-controls/`; uma cópia acompanha a entrega durável. Tentativas anteriores e falhas demonstradas são preservadas. A revisão dos adaptadores host tem trilha própria: as chamadas reais de apresentação são extraídas e a bancada substitui APIs nativas com observáveis sintéticos; os oráculos financeiros não são alterados para aceitar resultados.

## Estados de validação

A identidade e os recibos finais do candidato acompanham a entrega. Nenhum resultado R4, de outra versão ou de ensaio transitório aprova os novos bytes. Os testes novos complementam `leverage_suite.py --scope host`; testes de browser da prévia verificam apenas a maquete.

| Prova | Estado e limite |
| --- | --- |
| Baseline congelada | 48/48 host PASS; recibo `baseline-frozen-host.json`. A tentativa inicial preservada teve checks comportamentais PASS, mas falhou na estabilidade dos inputs por edição concorrente; não é promovida a aprovação. |
| Host integrado, mesmos inputs | **48/48 PASS**, `final-host-r2.json`, estabilidade de inputs confirmada. |
| Regressões novas de janelas/pacotes | **6/6 grupos PASS**, `final-extra-host.json`, inputs estáveis; HUD inclui 1.920 cenários / 55.540 verificações. Medidas de fonte e eventos são sintéticos. |
| Prévia navegável | **PASS** nas matrizes de 320/640/1280 px, claro/escuro, estados e controles, mais contraprovas R2/R3. Dados fictícios; não executa fórmulas nem programas MT5. |
| Identidade e reprodução dos pacotes | **PASS**: 139 fontes SDK / 86 fontes de uso; duas gerações byte-idênticas do candidato e kit; stamp idempotente; verificador do kit `STATIC_BYTES_PASS`. Sem EX5. |
| Revisão independente consolidada | **APPROVED** para fonte/host/pacotes; nenhum P1/P2 pendente nesse escopo. Parecer `final-review.md`, SHA-256 `4cdf3555215f1ec41739e006c68d45d4fb8edc7485326b5c847c293f4572d348`. |
| MetaEditor / quatro EX5 desta revisão | **NOT_RUN**. |
| Instalação e interação no MT5 demo | **NOT_RUN**. |
| DPI/eventos/alpha e empilhamento reais | **NOT_RUN**. |
| Aceite iniciante pelo proprietário | **NOT_RUN**; roteiro próprio. |
| Windows x64 independente | **NOT_RUN**; ambiente não disponível. |

A VM Windows 11 ARM está em execução com Parallels Tools. O acesso automático por `prlctl exec` foi recusado pela edição **Standard**, que exige Pro/Business para esse comando. Não foi uma recusa de autorização automática. A inspeção de acessibilidade não disponibilizou janela do guest, inclusive após abrir o console. Não houve execução de comandos no Windows, instalação nem uso de dados reais. Build do MT5, pasta de testes e EX5 exatos ainda não foram comprovados. O kit R5 deixa a compilação isolada preparada para execução manual e emissão de recibos novos.

## Identidade final e tentativas preservadas

A entrega corrente é **R5, selo R3**, construída em `candidate-r5-r3/` e `native-kit-r5-r3/`. Tentativas `candidate-r5/` e `candidate-r5-final/` são **SUPERSEDED** e não devem ser instaladas.

- Runtime build: `c1298741ec9673c2644cfaad83e6444b06a4ae7e0a5ec78f85f2c65d2781ea31`.
- Fingerprint MQL: `62c9bb7d36aed866983449c4327fb529b994464cb1422bf9516c639ea4fb94ac`.
- SHA-256 do SDK: `65ed7e2cb6f9fe680695ef67e47eb9aa873a66e2bfd214c1ebd71a41367fcf63`.
- SHA-256 do pacote de uso: `0bc6c856410b576ebf0412aa341056e8e02463c8f848fe34d2bd4e983ae5f7a3`.
- SHA-256 do kit: `5c32d1a5bf3ff2e2023c2c0e7b29c6425d1cc1bd5169f5fdf03f277d8fc9f8f4`.

O host final tem fingerprint `83986416b6677d9f969e17f1df547439c59f4c45c69234c674ed22ce220f9117`; os extras ampliam o inventário para fixtures e geradores, com fingerprint `ff2ca750cf1768df2299d43fa86e81cdbe32b4a3eb3482581c7059969a14b3b2`. Esses fingerprints têm inventários diferentes. Os 9 testes de pacote e os 15 do kit incluem casos herdados; não devem ser somados como 24 testes distintos.

A primeira execução final (`final-host.json`) registrou 42/48 PASS, três falhas de produto e três de bancada. A investigação distinguiu um defeito real de geometria do HUD em DPI alto e expectativas/adaptadores de UI desatualizados. Corrigiram-se a reserva do cabeçalho, dependências reais, observação dos textos, navegação adaptativa, launcher e vínculo ao manifesto local verificado. Os oráculos financeiros permaneceram intactos. A revisão também demonstrou e corrigiu Esc durante gesto Fibonacci com editor focado. As tentativas RED, pareceres e resultados substituídos acompanham as evidências; somente `final-host-r2.json` e os extras aprovam os inputs finais.

Os logs host contêm avisos do Clang sobre `codecvt` obsoleto e constantes não usadas na bancada sintética. São registrados, não confundidos com logs MetaEditor ou compilação MQL. Não houve redução dos oráculos financeiros nem aumento do limite original de 60 s do teste de 8.192 combinações; este terminou em 56,92 s no host final.

## Entrega e preservação

O gerador local `tools/build_stoikus_window_candidate.py` reutiliza funções oficiais de inventário, dependências, stamp e ZIP determinístico em staging. Não modifica o manifesto público R4. `tools/build_stoikus_window_native_kit.py` conserva o núcleo PowerShell histórico byte a byte e renova somente versão, hashes e bindings de identidade. O pin R5 permanece **externo** ao ZIP do kit e vincula seu tamanho/hash; não é assinatura digital.

- `JPW_Stoikus_Fontes_v1.23.0.zip`: SDK de fontes.
- `JPW_Stoikus_Uso_Fontes_v1.23.0.zip`: os quatro programas de uso com dependências e guia.
- `Kit_Windows_Stoikus_Janelas_R5.zip` + `root-pin-R5.json`: preparação de compilação temporária, sem instalação/abertura de terminal.
- Prévia, guia e evidências: permitem revisar apresentação e conferir a origem do candidato.

A preservação é comparada com a baseline de 1.079 arquivos do início da tarefa, que inclui alterações anteriores autorizadas. A conferência final `final-preservation.json` aprovou 8 ZIPs históricos, 157 arquivos de site/distribuição, 93 fontes financeiros/não visuais, 11 ativos da marca e 245 ferramentas anteriores fora dos adaptadores aprovados; todos byte-idênticos. Nenhum arquivo da baseline foi apagado. O novo código visual tem inventário próprio; não há migração de bancos, locks, estudos ou permissões. Nenhum arquivo do terminal de uso foi manipulado.

Para rollback, reverta somente os arquivos do delta desta tarefa usando a baseline e retire os novos arquivos inventariados; preserve o trabalho anterior, dados e recibos. A identidade do instalador beta e o site publicado mantêm entregas independentes. Instalação, compilação, aceite humano e publicação são estados distintos.
