# Testes do motor

Harness sem pacotes externos, `net10.0`, sobre arquivos temporários reais. `FakePlatform` substitui somente processos/MetaEditor; nenhum teste afirma validação nativa MQL5.

```sh
dotnet restore Stoikus.Installer.Tests --configfile NuGet.Config -p:NuGetAudit=false
dotnet build Stoikus.Installer.Tests --no-restore --disable-build-servers -p:UseSharedCompilation=false
dotnet Stoikus.Installer.Tests/bin/Debug/net10.0/Stoikus.Installer.Tests.dll
```

Execute da pasta `tests`. O teste de payload real requer `../generated/payload.zip` e `payload.json` gerados pelo script de empacotamento. Saída diferente de zero indica falha. A compilação nativa e ensaios de interrupção real do sistema precisam ser executados separadamente no Windows isolado.
