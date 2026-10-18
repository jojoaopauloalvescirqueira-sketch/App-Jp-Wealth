using System.Diagnostics;
using System.IO.Compression;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using System.Text.RegularExpressions;

namespace Stoikus.Installer.Core;
public sealed partial class InstallerService
{
    internal static readonly JsonSerializerOptions Json = new()
    {
        PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
        PropertyNameCaseInsensitive = true,
        WriteIndented = true
    };
    static readonly string[] DailySources = ["MQL5/Experts/JPWealth/JPW_Stoikus_Monitor.mq5", "MQL5/Indicators/JPWealth/JPW_Alavancagem_Atual.mq5", "MQL5/Indicators/JPWealth/JPW_NoCuda_Channels.mq5", "MQL5/Scripts/JPWealth/JPW_Stoikus_Abrir_Paineis.mq5"];
    readonly Payload payload;
    readonly Dictionary<string, byte[]> contents = new(StringComparer.OrdinalIgnoreCase);
    readonly string stateRoot;
    readonly IInstallerPlatform platform;
    public InstallerService(byte[] payloadZip, byte[] payloadManifest, string stateRoot) : this(payloadZip, payloadManifest, stateRoot, new WindowsInstallerPlatform())
    {
    }

    public InstallerService(byte[] payloadZip, byte[] payloadManifest, string stateRoot, IInstallerPlatform platform)
    {
        this.platform = platform;
        this.stateRoot = Path.GetFullPath(stateRoot);
        try
        {
            payload = JsonSerializer.Deserialize<Payload>(payloadManifest, Json) ?? throw new InvalidDataException("Manifesto vazio.");
            if (payload.SchemaVersion != 1 || payload.Programs.Count != 4 || payload.ArchiveBytes != payloadZip.LongLength || !Eq(payload.ArchiveSha256, Hash(payloadZip)))
                throw new InvalidDataException("Integridade do pacote inválida.");
            var expected = new Dictionary<string, PayloadFile>(StringComparer.OrdinalIgnoreCase);
            foreach (var f in payload.Files)
            {
                ValidatePath(f.Path, true);
                if (!expected.TryAdd(f.Path, f))
                    throw new InvalidDataException("Caminho duplicado no manifesto.");
            }

            using var stream = new MemoryStream(payloadZip);
            using var zip = new ZipArchive(stream, ZipArchiveMode.Read);
            foreach (var e in zip.Entries)
            {
                ValidatePath(e.FullName, true);
                if (((e.ExternalAttributes >> 16) & 0xf000) == 0xa000 || (e.ExternalAttributes & 0x400) != 0)
                    throw new InvalidDataException("Link no arquivo ZIP.");
                if (!expected.TryGetValue(e.FullName, out var f) || e.Length != f.Bytes || e.Length > 64 * 1024 * 1024)
                    throw new InvalidDataException("Entrada inesperada ou tamanho inválido.");
                using var es = e.Open();
                using var b = new MemoryStream();
                es.CopyTo(b);
                var bytes = b.ToArray();
                if (!Eq(Hash(bytes), f.Sha256) || !contents.TryAdd(e.FullName, bytes))
                    throw new InvalidDataException("Hash ou caminho duplicado inválido.");
            }

            if (contents.Count != expected.Count)
                throw new InvalidDataException("Pacote incompleto.");
            var outputs = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            var sources = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            foreach (var p in payload.Programs)
            {
                ValidatePath(p.Source);
                ValidatePath(p.Output);
                if (!p.Source.EndsWith(".mq5", StringComparison.OrdinalIgnoreCase) || !Eq(Path.ChangeExtension(p.Source, ".ex5"), p.Output) || !contents.ContainsKey(p.Source) || !sources.Add(p.Source) || !outputs.Add(p.Output) || contents.ContainsKey(p.Output))
                    throw new InvalidDataException("Programas inválidos; EX5 pré-compilado proibido.");
            }

            if (!DailySources.All(sources.Contains))
                throw new InvalidDataException("O pacote deve conter exatamente os quatro programas daily oficiais.");
            foreach (var f in payload.KnownFiles.Concat(payload.LegacyFiles))
            {
                ValidatePath(f.Path);
                if (f.Bytes < 0 || !Regex.IsMatch(f.Sha256, "^[a-fA-F0-9]{64}$"))
                    throw new InvalidDataException("Catálogo inválido.");
            }

            foreach (var f in payload.LegacyFiles)
                if (!payload.KnownFiles.Any(k => Eq(k.Path, f.Path) && Eq(k.Sha256, f.Sha256)) || !new[]
                {
                    ".mq5",
                    ".ex5"
                }.Contains(Path.GetExtension(f.Path), StringComparer.OrdinalIgnoreCase) || f.Path.StartsWith("MQL5/Include/", StringComparison.OrdinalIgnoreCase) || payload.Programs.Any(p => Eq(p.Source, f.Path) || Eq(p.Output, f.Path)))
                    throw new InvalidDataException("Legado inválido.");
        }
        catch (InvalidDataException)
        {
            throw;
        }
        catch (Exception e)when (e is JsonException or ArgumentException or IOException)
        {
            throw new InvalidDataException("Pacote inválido.", e);
        }
    }

    public IReadOnlyList<TerminalTarget> DiscoverTargets()
    {
        var results = new List<TerminalTarget>();
        var root = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData), "MetaQuotes", "Terminal");
        if (!Directory.Exists(root))
            return results;
        foreach (var dir in Directory.EnumerateDirectories(root))
        {
            try
            {
                CheckLinks(dir);
                var origin = Path.Combine(dir, "origin.txt");
                if (!File.Exists(origin))
                    continue;
                var install = File.ReadAllText(origin).Trim().Trim('\uFEFF');
                var t = new TerminalTarget(Path.Combine(install, "terminal64.exe"), dir, Path.Combine(install, "metaeditor64.exe"), false);
                ValidateTarget(t);
                results.Add(t);
            }
            catch (Exception e)when (e is IOException or UnauthorizedAccessException or InvalidDataException)
            {
            }
        }

        return results;
    }

    public bool HasPendingRecovery(TerminalTarget target)
    {
        try
        {
            ValidateTarget(target);
            EnsureStateOutsideTarget(target);
            return ReadPendingRecovery(target)is not null;
        }
        catch (Exception error)when (Expected(error))
        {
            return false;
        }
    }

    public PreflightResult Inspect(TerminalTarget target, InstallAction action)
    {
        var problems = new List<string>();
        var changes = new List<FileChange>();
        var legacy = new List<FileChange>();
        try
        {
            ValidateTarget(target);
            EnsureStateOutsideTarget(target);
            if (platform.IsProcessRunning(target.TerminalExe) || platform.IsProcessRunning(target.MetaEditorExe))
                throw new InvalidDataException("Feche o terminal e o MetaEditor selecionados.");
            if (action == InstallAction.Recover)
                return InspectRecovery(target, ReadPendingRecovery(target));
            if (ReadPendingRecovery(target)is not null)
                throw new InvalidDataException("Há operação interrompida. Use Recuperar operação interrompida e confira novamente a instalação.");
            var receipt = ReadReceipt(target);
            if (action != InstallAction.Install && receipt is null)
                throw new InvalidDataException("Não há recibo de propriedade para esta instalação.");
            if (receipt is not null)
            {
                ValidateReceipt(target, receipt);
                foreach (var f in receipt.Files)
                {
                    var path = TargetPath(target, f.Path);
                    var actual = FileHash(path);
                    if (actual is not null && !Eq(actual, f.InstalledHash))
                        problems.Add("Arquivo instalado modificado: " + f.Path);
                    if (f.OriginalHash is not null)
                        ValidateBackup(f.Backup, f.OriginalHash);
                }
            }

            if (action == InstallAction.Remove)
            {
                foreach (var f in receipt!.Files)
                    changes.Add(new(f.Path, "remover/restaurar", "Apenas arquivo inalterado do recibo."));
            }
            else
                foreach (var path in DesiredPaths())
                {
                    var disk = TargetPath(target, path);
                    if (Directory.Exists(disk))
                        problems.Add("Diretório ocupa arquivo: " + path);
                    var hash = FileHash(disk);
                    var owned = receipt?.Files.FirstOrDefault(f => Eq(f.Path, path));
                    if (hash is not null && owned is null && !Known(path, hash, new FileInfo(disk).Length))
                        problems.Add("Arquivo desconhecido protegido: " + path);
                    changes.Add(new(path, hash is null ? "criar" : "atualizar", "Compilação local e backup antes da gravação."));
                }

            foreach (var f in payload.LegacyFiles)
            {
                var disk = TargetPath(target, f.Path);
                if (File.Exists(disk) && Eq(FileHash(disk), f.Sha256) && new FileInfo(disk).Length == f.Bytes)
                    legacy.Add(new(f.Path, "organizar", "Arquivo oficial conhecido; backup fora de MQL5.", true));
            }
        }
        catch (Exception e)when (Expected(e))
        {
            problems.Add(e.Message);
        }

        return new(problems.Count == 0, problems, changes, legacy);
    }

    public string Verify(TerminalTarget target)
    {
        try
        {
            ValidateTarget(target);
            var receipt = ReadReceipt(target);
            if (receipt is null)
                return "Sem recibo: instalação local não verificada.";
            ValidateReceipt(target, receipt);
            var lines = receipt.Files.Select(f => $"{f.Path}: {(Eq(FileHash(TargetPath(target, f.Path)), f.InstalledHash) ? "íntegro" : File.Exists(TargetPath(target, f.Path)) ? "MODIFICADO" : "AUSENTE")}");
            return "Verificação somente leitura; recibo local dos quatro programas, sem comprovação nativa global/CPU/SDK.\n" + string.Join("\n", lines);
        }
        catch (Exception e)when (Expected(e))
        {
            return "Verificação inconclusiva: " + e.Message;
        }
    }

    public async Task<OperationResult> ExecuteAsync(TerminalTarget target, InstallAction action, IReadOnlyList<string> organizePaths, IProgress<InstallProgress>? progress = null, CancellationToken cancellationToken = default)
    {
        string receiptPath = "", reportPath = "", run = "", stage = "";
        var buildEvidence = new List<CompileEvidence>();
        Journal? journal = null;
        Journal? pendingRecovery = null;
        FileStream? operationLock = null;
        IDisposable? stageLease = null;
        var stagePins = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
        try
        {
            cancellationToken.ThrowIfCancellationRequested();
            ValidateTarget(target);
            EnsureStateOutsideTarget(target);
            var home = Home(target);
            CheckLinks(home);
            Directory.CreateDirectory(home);
            receiptPath = Path.Combine(home, "receipt.json");
            reportPath = Path.Combine(home, "reports", DateTime.UtcNow.ToString("yyyyMMddTHHmmssfffffff") + "-" + Guid.NewGuid().ToString("N") + ".json");
            Directory.CreateDirectory(Path.GetDirectoryName(reportPath)!);
            operationLock = new FileStream(Path.Combine(home, "operation.lock"), FileMode.OpenOrCreate, FileAccess.ReadWrite, FileShare.None);
            if (platform.IsProcessRunning(target.TerminalExe) || platform.IsProcessRunning(target.MetaEditorExe))
                throw new InvalidDataException("Feche o terminal e o MetaEditor antes da recuperação/instalação.");
            cancellationToken.ThrowIfCancellationRequested();
            pendingRecovery = ReadPendingRecovery(target);
            if (action == InstallAction.Recover)
            {
                if (organizePaths.Count != 0)
                    throw new InvalidDataException("A recuperação não aceita organização de arquivos.");
                var recoveryPreview = InspectRecovery(target, pendingRecovery);
                if (!recoveryPreview.CanProceed)
                    throw new InvalidDataException("Recuperação manual necessária: " + string.Join("\n", recoveryPreview.Problems));
                progress?.Report(new("recover", "Restaurando a operação interrompida.", 0, 1));
                cancellationToken.ThrowIfCancellationRequested();
                // After this boundary recovery completes a consistent rollback; cancellation is deferred.
                Rollback(target, home, pendingRecovery!);
                AtomicJson(reportPath, new { success = true, action = action.ToString(), target, journal = pendingRecovery, message = "Operação anterior recuperada; confira novamente a ação desejada.", compiled = false, nativeValidation = "NOT_RUN" });
                progress?.Report(new("recover", "Recuperação concluída; confira novamente a ação desejada.", 1, 1));
                return new(true, "Operação interrompida recuperada. Faça uma nova conferência antes de instalar, reparar ou remover.", receiptPath, reportPath);
            }

            if (pendingRecovery is not null)
                throw new InvalidDataException("Há operação interrompida. Use Recuperar operação interrompida antes de continuar.");
            cancellationToken.ThrowIfCancellationRequested();
            var preflight = Inspect(target, action);
            if (!preflight.CanProceed)
                throw new InvalidDataException(string.Join("\n", preflight.Problems));
            var selected = organizePaths.Distinct(StringComparer.OrdinalIgnoreCase).ToArray();
            if (selected.Any(p => !preflight.LegacyCandidates.Any(f => Eq(f.RelativePath, p))))
                throw new InvalidDataException("Organização contém arquivo sem identidade oficial comprovada.");
            var old = ReadReceipt(target);
            var approved = CaptureApprovedIdentities(target, action, selected, old);
            run = Path.Combine(home, "runs", Guid.NewGuid().ToString("N"));
            Directory.CreateDirectory(run);
            Dictionary<string, string> desired = new(StringComparer.OrdinalIgnoreCase);
            if (action != InstallAction.Remove)
            {
                progress?.Report(new("compile", "Preparando compilação isolada.", 0, 4));
                stage = Path.Combine(run, "stage");
                Directory.CreateDirectory(stage);
                foreach (var(p, b)in contents.Where(k => k.Key.StartsWith("MQL5/", StringComparison.Ordinal)))
                {
                    var file = SafePath(stage, p);
                    Directory.CreateDirectory(Path.GetDirectoryName(file)!);
                    File.WriteAllBytes(file, b);
                    desired[p] = file;
                    stagePins.Add(file, Hash(b));
                }

                var dependencies = StageIncludes(target, stage);
                foreach (var dependency in dependencies)
                {
                    var file = SafePath(stage, "MQL5/Include/" + dependency.Path);
                    if (stagePins.TryGetValue(file, out var expected) && !Eq(expected, dependency.Sha256))
                        throw new InvalidDataException("Include não corresponde ao payload: " + dependency.Path);
                    stagePins[file] = dependency.Sha256;
                }
                foreach (var p in payload.Programs)
                {
                    cancellationToken.ThrowIfCancellationRequested();
                    var source = SafePath(stage, p.Source);
                    var output = SafePath(stage, p.Output);
                    if (File.Exists(output))
                        throw new InvalidDataException("EX5 preexistente no stage.");
                    var log = Path.Combine(run, "logs", Path.GetFileNameWithoutExtension(source) + ".log");
                    Directory.CreateDirectory(Path.GetDirectoryName(log)!);
                    var request = new CompileRequest(target.MetaEditorExe, source, Path.Combine(stage, "MQL5"), log, TimeSpan.FromMinutes(3));
                    var attempt = new CompileEvidence
                    {
                        Source = p.Source,
                        SourcePath = source,
                        Output = p.Output,
                        OutputPath = output,
                        Log = log,
                        Editor = target.MetaEditorExe,
                        Arguments = ["/compile:" + source, "/include:" + request.Include, "/log"],
                        Dependencies = dependencies,
                        TimeoutSeconds = request.Timeout.TotalSeconds,
                        Started = DateTime.UtcNow,
                        Status = "preparing"
                    };
                    buildEvidence.Add(attempt);
                    try
                    {
                        // Read-sharing leases deny ordinary Windows writes/deletes while the
                        // compiler reads its inputs; every hash is fixed before this invocation.
                        using var compilerInputs = OpenPinnedFiles(stagePins);
                        attempt.SourceSha256 = stagePins[source];
                        attempt.EditorSha256 = FileHash(target.MetaEditorExe);
                        attempt.EditorVersion = FileVersionInfo.GetVersionInfo(target.MetaEditorExe).FileVersion;
                        attempt.Status = "running";
                        // Persist the attempt before invoking a process, including in-flight cancellation/crash evidence.
                        AtomicJson(reportPath, new { success = false, status = "compiling", action = action.ToString(), target, run, stage, buildEvidence, scope = "local-four", nativeValidation = "NOT_RUN" });
                        attempt.Exit = await platform.CompileAsync(request, cancellationToken);
                        cancellationToken.ThrowIfCancellationRequested();
                        CheckLinks(log);
                        CheckLinks(output);
                        if ((attempt.Exit != 0 && attempt.Exit != 1) || !File.Exists(log) || File.GetLastWriteTimeUtc(log) < attempt.Started.AddSeconds(-2) || !File.Exists(output) || new FileInfo(output).Length == 0 || File.GetLastWriteTimeUtc(output) < attempt.Started.AddSeconds(-2))
                            throw new InvalidDataException("Compilação sem prova válida (EX5/log/zero erros e avisos): " + p.Source);
                        var logBytes = File.ReadAllBytes(log);
                        if (!ValidCompileLog(logBytes, source))
                            throw new InvalidDataException("Log completo não corresponde à fonte compilada: " + p.Source);
                        // Recheck all prior inputs/outputs, not merely the latest source.
                        using (OpenPinnedFiles(stagePins)) { }
                        attempt.LogSha256 = Hash(logBytes);
                        attempt.OutputSha256 = FileHash(output) ?? throw new InvalidDataException("EX5 desapareceu.");
                        stagePins.Add(log, attempt.LogSha256);
                        stagePins.Add(output, attempt.OutputSha256);
                        using (OpenPinnedFiles(stagePins)) { }
                        attempt.Status = "succeeded";
                        desired[p.Output] = output;
                    }
                    catch (Exception error)
                    {
                        attempt.Status = error is OperationCanceledException ? "cancelled" : error is TimeoutException ? "timeout" : "failed";
                        attempt.Diagnostic = error.ToString();
                        throw;
                    }
                    finally
                    {
                        attempt.Finished = DateTime.UtcNow;
                        CaptureCompileOutputs(attempt);
                    }

                    progress?.Report(new("compile", "Compilado: " + p.Source, buildEvidence.Count, 4));
                }
            }

            cancellationToken.ThrowIfCancellationRequested();
            if (platform.IsProcessRunning(target.TerminalExe) || platform.IsProcessRunning(target.MetaEditorExe))
                throw new InvalidDataException("Terminal/MetaEditor abriu durante a preparação.");
            var fresh = Inspect(target, action);
            if (!fresh.CanProceed)
                throw new InvalidDataException(string.Join("\n", fresh.Problems));
            if (selected.Any(p => !fresh.LegacyCandidates.Any(f => Eq(f.RelativePath, p))))
                throw new InvalidDataException("Legado selecionado mudou de identidade durante a preparação.");
            foreach (var identity in approved.Values)
                RequireIdentity(target, identity);
            // Hold the validated stage through the transaction. An arbitrary current
            // stage hash can never become the identity authorized for installation.
            stageLease = OpenPinnedFiles(stagePins);
            var rows = new List<TransactionFile>();
            var next = new Receipt
            {
                Target = Canonical(target.DataDirectory),
                ProductVersion = payload.ProductVersion,
                Files = []
            };
            var paths = action == InstallAction.Remove ? old!.Files.Select(f => f.Path) : desired.Keys.Concat(selected);
            int index = 0;
            foreach (var path in paths.Distinct(StringComparer.OrdinalIgnoreCase))
            {
                var destination = TargetPath(target, path);
                var accepted = approved[path];
                RequireIdentity(target, accepted);
                var before = accepted.Hash;
                var previous = old?.Files.FirstOrDefault(f => Eq(f.Path, path));
                string? afterFile = null;
                string? after = null;
                if (action == InstallAction.Remove)
                {
                    if (previous!.OriginalHash is not null)
                    {
                        ValidateBackup(previous.Backup, previous.OriginalHash);
                        afterFile = previous.Backup;
                        after = previous.OriginalHash;
                    }
                }
                else if (desired.TryGetValue(path, out var staged))
                {
                    afterFile = staged;
                    after = stagePins[staged];
                }

                var backup = Path.Combine(run, "backups", (index++).ToString("D5") + ".bak");
                rows.Add(new() { Path = path, BeforeHash = before, BeforeBytes = accepted.Bytes, AfterHash = after, Backup = backup, AfterFile = afterFile });
                if (action != InstallAction.Remove)
                    next.Files.Add(new() { Path = path, InstalledHash = after, OriginalHash = previous is not null ? previous.OriginalHash : before, Backup = previous is not null ? previous.Backup : before is not null ? backup : null });
            }

            // Keep prior organized legacy ownership on repeat/repair, so removal can restore it.
            if (action != InstallAction.Remove && old is not null)
                foreach (var prior in old.Files.Where(f => !next.Files.Any(n => Eq(n.Path, f.Path))))
                    next.Files.Add(prior);
            journal = new()
            {
                Target = Canonical(target.DataDirectory),
                ReceiptPath = receiptPath,
                PreviousReceipt = File.Exists(receiptPath) ? Convert.ToBase64String(File.ReadAllBytes(receiptPath)) : null,
                Run = run,
                Files = rows,
                Phase = "planned"
            };
            SaveJournal(home, journal);
            foreach (var row in rows)
            {
                if (row.BeforeHash is not null)
                {
                    var destination = TargetPath(target, row.Path);
                    RequireIdentity(target, new FileIdentity(row.Path, row.BeforeHash, row.BeforeBytes));
                    Directory.CreateDirectory(Path.GetDirectoryName(row.Backup)!);
                    CopyDurable(destination, row.Backup);
                    ValidateBackup(row.Backup, row.BeforeHash);
                }

                row.Status = "backed-up";
                SaveJournal(home, journal);
            }

            journal.Phase = "mutating";
            SaveJournal(home, journal);
            foreach (var row in rows)
            {
                cancellationToken.ThrowIfCancellationRequested();
                var destination = TargetPath(target, row.Path);
                RequireIdentity(target, new FileIdentity(row.Path, row.BeforeHash, row.BeforeBytes));
                row.Status = "writing";
                SaveJournal(home, journal);
                if (row.AfterHash is null)
                {
                    if (File.Exists(destination))
                        File.Delete(destination);
                }
                else
                {
                    ValidateBackup(row.AfterFile, row.AfterHash);
                    AtomicCopy(row.AfterFile!, destination, row.AfterHash,
                        () => RequireIdentity(target, new FileIdentity(row.Path, row.BeforeHash, row.BeforeBytes)));
                }

                if (!Eq(FileHash(destination), row.AfterHash))
                    throw new IOException("Verificação pós-gravação falhou: " + row.Path);
                row.Status = "written";
                SaveJournal(home, journal);
                progress?.Report(new("install", "Aplicado: " + row.Path, rows.IndexOf(row) + 1, rows.Count));
            }

            cancellationToken.ThrowIfCancellationRequested();
            if (action == InstallAction.Remove)
            {
                if (File.Exists(receiptPath))
                    File.Delete(receiptPath);
            }
            else
                AtomicJson(receiptPath, next);
            journal.Phase = "committed";
            SaveJournal(home, journal);
            AtomicJson(reportPath, new { success = true, action = action.ToString(), target, run, stage, buildEvidence, scope = "local-four", nativeValidation = "NOT_RUN" });
            return new(true, action == InstallAction.Remove ? "Remoção concluída; originais restaurados." : "Instalação local concluída; validação operacional manual pendente.", receiptPath, reportPath);
        }
        catch (Exception e)when (Expected(e) || e is OperationCanceledException)
        {
            var message = e is OperationCanceledException ? "Operação cancelada." : e.Message;
            if (journal is not null && journal.Phase != "committed")
                try
                {
                    Rollback(target, Home(target), journal);
                }
                catch (Exception rollback)when (Expected(rollback))
                {
                    message += " Recuperação manual necessária: " + rollback.Message;
                }

            if (reportPath.Length > 0)
                try
                {
                    AtomicJson(reportPath, new { success = false, message, error = e.ToString(), action = action.ToString(), target, run, stage, buildEvidence, journal = journal ?? pendingRecovery, scope = "local-four", nativeValidation = "NOT_RUN" });
                }
                catch (Exception report)when (Expected(report))
                {
                    message += " Não foi possível persistir relatório: " + report.Message;
                }

            return new(false, message, receiptPath, reportPath);
        }
        finally
        {
            stageLease?.Dispose();
            operationLock?.Dispose();
        }
    }
}
