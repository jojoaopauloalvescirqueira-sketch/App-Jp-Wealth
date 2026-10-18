# Atualização R4 — 18/10/2026

Pacote incorporado **1.23.0/R5**: 86 membros, quatro programas, cálculo **1.9.0**. O R4 fixa a identidade do stage e da cópia publicada; seus [recibos e limites](../../docs/validation/stoikus-installer-1.0.0-beta.1/R4/INTEGRATION.md) são novos. R1/R2/R3 permanecem históricos, incluindo a falha transacional reproduzida no R3. Build e testes host não aprovam execução Windows.

# Instalador Stoikus — candidato local

Assistente Windows 11 x64, versão **1.0.0-beta.1**, produto **1.23.0**, cálculo **1.9.0**. O EXE é autocontido e não assinado. Precisa de MT5 e MetaEditor instalados para compilar os quatro programas de uso. O SDK completo continua separado.

## Gerar e verificar o payload

Na raiz do repositório:

```sh
python3 tools/stoikus_installer_test.py
python3 tools/stoikus-installer/prepare_payload.py
```

O gerador verifica hashes/tamanhos do manifesto corrente, fontes, identidade de todos os membros dos ZIPs corrente/diário, fechamento das dependências e quatro programas. Depois copia o ZIP diário **sem alterar seus bytes** para `generated/payload.zip` e escreve `generated/payload.json`. O guia `LEIA_PRIMEIRO.md` está no payload e fica fora do terminal.

Os ZIPs oficiais históricos possuem hashes congelados no gerador. O catálogo deduplica caminho/hash; somente fontes e binários de programas fora do conjunto diário podem aparecer na organização opcional. Includes, imagens, dados, locks e saídas EX5 dos programas diários não entram na limpeza.

Para registrar o estado indisponível pela geração oficial dos pacotes:

```sh
python3 tools/stoikus-installer/prepare_payload.py --record-unavailable
```

## Gerar o EXE local

Use o SDK oficial **.NET 10.0.402**, fixado em `global.json`. No ambiente desta implementação foi preparado em `/private/tmp/jpw-dotnet10/dotnet`. Pode apontar outra instalação da mesma versão com `--dotnet`; sem esse argumento, o helper usa `JPW_DOTNET` ou procura `dotnet` no PATH:

```sh
python3 tools/stoikus-installer/build.py --dotnet /private/tmp/jpw-dotnet10/dotnet
```

O helper executa restore/publish para Windows x64, autocontido, arquivo único, sem trimming/AOT, em diretório temporário limpo. Respeita `DOTNET_CLI_HOME` e `NUGET_PACKAGES` quando definidos. Caso contrário, usa subpastas `jpw-dotnet-home` e `jpw-nuget` no diretório temporário da plataforma. Para reproduzir o cache desta implementação no Mac, defina `DOTNET_CLI_HOME=/private/tmp/jpw-dotnet-home` e `NUGET_PACKAGES=/private/tmp/jpw-nuget` na chamada. Restore pode precisar de conexão aos feeds oficiais NuGet.

O resultado fica em `artifacts/Stoikus_Setup_1.0.0-beta.1_win-x64.exe`, com hash, tamanho, versão do SDK e identidade do payload em `artifacts/installer-candidate.json`. Esses arquivos e `generated`, `bin`, `obj` são derivados ignorados pelo Git. O helper mantém `publicDownloadAvailable:false` e testes nativos `NOT_RUN`; executar publish não prova execução Windows ou compilação MQL5.

## Distribuição e limites

A página exibe o instalador beta como indisponível. Os downloads existentes de fontes diário/engenharia preservam seus caminhos. Cada download permitido exige tamanho, SHA-256, caminho e MIME compatíveis. O EXE nunca é incorporado no HTML portátil.

Uma distribuição futura depende de evidências dos mesmos bytes em Windows x64, Parallels ARM e navegador, vinculadas pelo SHA-256 do EXE e recibos de cada etapa. A validação de metadados aceita apenas URL HTTPS explícita de release no repositório `jojoaopauloalvescirqueira-sketch/App-Jp-Wealth`. Nenhuma URL de release foi criada nesta implementação. Recibos dos quatro programas compilados pelo instalador não substituem o contrato `nativeArtifact` do SDK completo.

Provas nativas, uso no terminal, teste manual e aceite operacional permanecem separados dos testes de geração/host. Commit, push, publicação, instalação em MT5 e ativação de negociação não fazem parte deste helper.
