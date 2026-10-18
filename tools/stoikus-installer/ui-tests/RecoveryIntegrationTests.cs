using System.IO.Compression;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using System.Text.Json.Nodes;
using Stoikus.Installer.App;
using Stoikus.Installer.Core;

internal static class RecoveryIntegrationTests
{
    public static IEnumerable<(string Name, Func<Task> Run)> All()
    {
        yield return ("integrated first install interruption exposes recovery before receipt", FirstInstall);
        yield return ("integrated partial repair restores receipt and requires new preview", PartialRepair);
        yield return ("integrated recovery conflict preserves user bytes and report", Conflict);
        yield return ("integrated open process blocks recovery preview", OpenProcess);
        yield return ("integrated already cancelled recovery leaves target and journal intact", AlreadyCancelled);
        yield return ("integrated recovery requires explicit confirmation and matching snapshot", Confirmation);
    }

    private static void Check(bool condition, string message) { if (!condition) throw new Exception(message); }

    private static async Task FirstInstall()
    {
        using var f = new RecoveryFixture(); f.Interrupt(null);
        var core = f.Service(); var state = new WizardOperationState();
        Check(!File.Exists(f.Receipt), "interrupted first install unexpectedly has receipt");
        foreach (var action in new[] { InstallAction.Install, InstallAction.Repair, InstallAction.Remove })
        {
            var normal = state.BeginInspection(f.Target, action, false);
            var blocked = core.Inspect(normal.Target, normal.Action);
            Check(state.CompleteInspection(normal, f.Target, action, false), "normal snapshot changed unexpectedly");
            Check(!blocked.CanProceed, "normal action must remain blocked: " + action);
            Check(state.ConfirmedSelection(f.Target, action, false, true, blocked.CanProceed) is null, "blocked normal preview can execute");
        }
        var before = f.Snapshot(); var journal = File.ReadAllBytes(f.Journal);
        Check(state.CanOfferRecovery(core.HasPendingRecovery(f.Target), false), "UI cannot offer recovery while normal previews are blocked");
        var preview = InspectRecovery(core, state, f.Target);
        Check(preview.CanProceed, string.Join(";", preview.Problems));
        Check(f.Snapshot() == before && journal.SequenceEqual(File.ReadAllBytes(f.Journal)), "recovery preview mutated files");
        var selection = state.ConfirmedSelection(f.Target, InstallAction.Recover, false, true, preview.CanProceed);
        Check(selection is not null, "confirmed recovery is inaccessible");
        var result = await core.ExecuteAsync(selection!.Target, selection.Action, []);
        Check(result.Success, result.Message);
        Check(state.CompleteRecovery(selection.Action, result), "success did not route to reinspection");
        Check(!File.Exists(f.OutputPath) && !core.HasPendingRecovery(f.Target), "partial binary or pending journal remains");
        Check(f.Platform.Calls == 0, "recovery must not compile");
        Check(!state.CanExecute(f.Target, InstallAction.Install, false), "recovery implicitly approved installation");
        Check(core.Inspect(f.Target, InstallAction.Install).CanProceed, "fresh install reinspection must be possible");
    }

    private static async Task PartialRepair()
    {
        using var f = new RecoveryFixture(); var core = f.Service();
        var installed = await core.ExecuteAsync(f.Target, InstallAction.Install, []);
        Check(installed.Success, installed.Message);
        var original = File.ReadAllText(f.OutputPath); var receipt = File.ReadAllBytes(f.Receipt);
        f.Interrupt(original, receipt); var beforeCalls = f.Platform.Calls;
        var state = new WizardOperationState();
        var normal = state.BeginInspection(f.Target, InstallAction.Repair, false);
        var blocked = core.Inspect(normal.Target, normal.Action);
        Check(state.CompleteInspection(normal, f.Target, InstallAction.Repair, false), "repair snapshot changed unexpectedly");
        Check(!blocked.CanProceed, "partial repair must not approve repair directly");
        Check(state.ConfirmedSelection(f.Target, InstallAction.Repair, false, true, blocked.CanProceed) is null, "partial repair can execute without recovery");
        Check(state.CanOfferRecovery(core.HasPendingRecovery(f.Target), false), "partial repair has no recovery route");
        var preview = InspectRecovery(core, state, f.Target);
        Check(preview.CanProceed, string.Join(";", preview.Problems));
        var selected = state.ConfirmedSelection(f.Target, InstallAction.Recover, false, true, preview.CanProceed)!;
        var result = await core.ExecuteAsync(selected.Target, selected.Action, []);
        Check(result.Success, result.Message);
        Check(state.CompleteRecovery(selected.Action, result), "success did not route to reinspection");
        Check(File.ReadAllText(f.OutputPath) == original && receipt.SequenceEqual(File.ReadAllBytes(f.Receipt)), "repair recovery lost previous installed bytes or receipt");
        Check(f.Platform.Calls == beforeCalls, "recovery compiled instead of restoring");
        Check(state.Preview is null && !state.CanExecute(f.Target, InstallAction.Repair, false), "new repair did not require a new preview");
        Check(core.Inspect(f.Target, InstallAction.Repair).CanProceed, "normal repair reinspection should be possible after restore");
    }

    private static async Task Conflict()
    {
        using var f = new RecoveryFixture(); f.Interrupt(null); File.WriteAllText(f.OutputPath, "user modified bytes");
        var core = f.Service(); var state = new WizardOperationState();
        Check(state.CanOfferRecovery(core.HasPendingRecovery(f.Target), false), "conflict must not hide recovery review");
        var preview = InspectRecovery(core, state, f.Target);
        Check(!preview.CanProceed && preview.Problems.Count > 0, "conflict recovery should be blocked with a reason");
        Check(state.ConfirmedSelection(f.Target, InstallAction.Recover, false, true, preview.CanProceed) is null, "blocked recovery was confirmed");
        var result = await core.ExecuteAsync(f.Target, InstallAction.Recover, []);
        Check(!state.CompleteRecovery(InstallAction.Recover, result), "failed recovery routed to completed reinspection state");
        Check(!result.Success && !WizardOperationState.CanAutoClose(true, result), "recovery failure closed its report");
        Check(File.ReadAllText(f.OutputPath) == "user modified bytes", "conflicting user bytes were replaced");
        Check(core.HasPendingRecovery(f.Target) && File.Exists(result.ReportPath), "failure lost pending state or report");
        Check(f.Platform.Calls == 0, "conflict recovery compiled");
    }

    private static Task OpenProcess()
    {
        using var f = new RecoveryFixture(); f.Interrupt(null); f.Platform.Open = true;
        var core = f.Service(); var state = new WizardOperationState();
        Check(state.CanOfferRecovery(core.HasPendingRecovery(f.Target), false), "open process must not hide recovery review");
        var preview = InspectRecovery(core, state, f.Target);
        Check(!preview.CanProceed && preview.Problems.Count > 0, "open terminal was accepted for recovery");
        Check(state.ConfirmedSelection(f.Target, InstallAction.Recover, false, true, preview.CanProceed) is null, "open process recovery approved");
        return Task.CompletedTask;
    }

    private static async Task AlreadyCancelled()
    {
        using var f = new RecoveryFixture(); f.Interrupt(null); var core = f.Service(); var state = new WizardOperationState();
        Check(state.CanOfferRecovery(core.HasPendingRecovery(f.Target), false), "recovery route missing");
        var preview = InspectRecovery(core, state, f.Target);
        var selected = state.ConfirmedSelection(f.Target, InstallAction.Recover, false, true, preview.CanProceed);
        Check(selected is not null, "recovery confirmation unavailable");
        var before = f.Snapshot(); var journal = File.ReadAllBytes(f.Journal);
        using var cancellation = new CancellationTokenSource(); cancellation.Cancel();
        var result = await core.ExecuteAsync(selected!.Target, selected.Action, [], cancellationToken: cancellation.Token);
        Check(!state.CompleteRecovery(selected.Action, result), "cancelled recovery became successful reinspection state");
        Check(!result.Success && !WizardOperationState.CanAutoClose(true, result), "cancelled recovery must remain visible");
        Check(before == f.Snapshot() && journal.SequenceEqual(File.ReadAllBytes(f.Journal)), "already cancelled recovery changed target or journal");
        Check(core.HasPendingRecovery(f.Target) && f.Platform.Calls == 0, "cancelled recovery consumed pending state or compiled");
    }

    private static Task Confirmation()
    {
        using var f = new RecoveryFixture(); f.Interrupt(null); var core = f.Service(); var state = new WizardOperationState();
        var preview = InspectRecovery(core, state, f.Target); Check(preview.CanProceed, "fixture recovery preview invalid");
        Check(state.ConfirmedSelection(f.Target, InstallAction.Recover, false, false, true) is null, "recovery skipped explicit confirmation");
        Check(state.ConfirmedSelection(f.Target, InstallAction.Install, false, true, true) is null, "recovery preview approved install");
        Check(!state.CanOfferRecovery(true, true), "UI allowed selection while busy");
        state.InvalidateSelection();
        Check(state.ConfirmedSelection(f.Target, InstallAction.Recover, false, true, true) is null, "stale recovery preview executed");
        Check(f.Platform.Calls == 0, "preview compiled");
        return Task.CompletedTask;
    }

    private static PreflightResult InspectRecovery(InstallerService core, WizardOperationState state, TerminalTarget target)
    {
        var snapshot = state.BeginInspection(target, InstallAction.Recover, false);
        var preview = core.Inspect(snapshot.Target, snapshot.Action);
        Check(state.CompleteInspection(snapshot, target, InstallAction.Recover, false), "recovery snapshot was discarded unexpectedly");
        return preview;
    }
}

internal sealed class RecoveryFixture : IDisposable
{
    public const string Output = "MQL5/Experts/JPWealth/JPW_Stoikus_Monitor.ex5";
    private static readonly string[] Sources = ["MQL5/Experts/JPWealth/JPW_Stoikus_Monitor.mq5", "MQL5/Indicators/JPWealth/JPW_Alavancagem_Atual.mq5", "MQL5/Indicators/JPWealth/JPW_NoCuda_Channels.mq5", "MQL5/Scripts/JPWealth/JPW_Stoikus_Abrir_Paineis.mq5"];
    private readonly string _root = Path.Combine(OperatingSystem.IsMacOS() ? "/private/tmp" : Path.GetTempPath(), "stoikus-ui-recovery-" + Guid.NewGuid().ToString("N"));
    private string Data => Path.Combine(_root, "terminal");
    private string State => Path.Combine(_root, "state");
    private string Home => Path.Combine(State, Hash(Encoding.UTF8.GetBytes(Path.GetFullPath(Data).ToUpperInvariant())));
    public string OutputPath => Path.Combine(Data, Output);
    public string Receipt => Path.Combine(Home, "receipt.json");
    public string Journal => Path.Combine(Home, "journal.json");
    public TerminalTarget Target { get; }
    public RecoveryPlatform Platform { get; } = new();
    private readonly byte[] _zip;
    private readonly byte[] _manifest;

    public RecoveryFixture()
    {
        Directory.CreateDirectory(Data);
        Write("terminal64.exe", "synthetic terminal"); Write("metaeditor64.exe", "synthetic editor");
        Write("MQL5/Include/Canvas/Canvas.mqh", "// standard fixture"); Write("MQL5/Include/Math/Stat/Normal.mqh", "// standard fixture");
        Write("MQL5/Files/preserved.fixture", "unrelated synthetic data");
        Target = new(Path.Combine(Data, "terminal64.exe"), Data, Path.Combine(Data, "metaeditor64.exe"), true);
        var files = Sources.ToDictionary(p => p, p => Encoding.UTF8.GetBytes("// synthetic " + p));
        files.Add("LEIA_PRIMEIRO.md", Encoding.UTF8.GetBytes("fixture guide"));
        using var memory = new MemoryStream();
        using (var archive = new ZipArchive(memory, ZipArchiveMode.Create, true))
            foreach (var file in files) { using var stream = archive.CreateEntry(file.Key).Open(); stream.Write(file.Value); }
        _zip = memory.ToArray();
        _manifest = JsonSerializer.SerializeToUtf8Bytes(new { schemaVersion = 1, installerVersion = "1.0.0-beta.1", productVersion = "1.22.1", calculationVersion = "1.9.0", archiveSha256 = Hash(_zip), archiveBytes = _zip.Length, files = files.Select(f => new { path = f.Key, sha256 = Hash(f.Value), bytes = f.Value.Length }), programs = Sources.Select(source => new { source, output = Path.ChangeExtension(source, ".ex5"), role = "daily" }), knownFiles = Array.Empty<object>(), legacyFiles = Array.Empty<object>() });
    }

    public InstallerService Service() => new(_zip, _manifest, State, Platform);
    public void Interrupt(string? previous, byte[]? previousReceipt = null)
    {
        var run = Path.Combine(Home, "runs", "interrupted"); var backup = Path.Combine(run, "backups", "output.bak");
        Directory.CreateDirectory(Path.GetDirectoryName(backup)!);
        if (previous is not null) File.WriteAllText(backup, previous);
        Write(Output, "partial interrupted binary");
        File.WriteAllText(Journal, JsonSerializer.Serialize(new { target = Path.GetFullPath(Data).ToUpperInvariant(), receiptPath = Receipt, previousReceipt = previousReceipt is null ? null : Convert.ToBase64String(previousReceipt), phase = "mutating", run, files = new[] { new { path = Output, beforeHash = previous is null ? null : Hash(Encoding.UTF8.GetBytes(previous)), afterHash = Hash(Encoding.UTF8.GetBytes("partial interrupted binary")), backup, afterFile = (string?)null, status = "written" } } }));
    }
    private void Write(string relative, string value) { var path = Path.Combine(Data, relative); Directory.CreateDirectory(Path.GetDirectoryName(path)!); File.WriteAllText(path, value); }
    public string Snapshot() => string.Join("\n", Directory.GetFiles(Data, "*", SearchOption.AllDirectories).Order().Select(p => Path.GetRelativePath(Data, p) + ":" + Hash(File.ReadAllBytes(p))));
    private static string Hash(byte[] value) => Convert.ToHexString(SHA256.HashData(value)).ToLowerInvariant();
    public void Dispose() { try { Directory.Delete(_root, true); } catch (IOException) { } }
}

internal sealed class RecoveryPlatform : IInstallerPlatform
{
    public bool Open { get; set; }
    public int Calls { get; private set; }
    public bool IsProcessRunning(string executable) => Open;
    public Task<int> CompileAsync(CompileRequest request, CancellationToken cancellationToken)
    {
        cancellationToken.ThrowIfCancellationRequested(); Calls++;
        File.WriteAllText(request.Log, request.Source + " : information: compiling " + request.Source + "\n : information: code generated\nResult: 0 errors, 0 warnings, 1 msec elapsed", Encoding.Unicode);
        File.WriteAllText(Path.ChangeExtension(request.Source, ".ex5"), "synthetic compiled " + File.ReadAllText(request.Source));
        return Task.FromResult(0);
    }
}
