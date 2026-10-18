using System.IO.Compression;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using System.Text.Json.Nodes;
using Stoikus.Installer.Core;

var tests = new (string, Func<Task>)[]
{
    ("reject tampered archive", async () =>
    {
        using var f = new Fixture();
        var zip = f.Zip.ToArray();
        zip[20] ^= 1;
        Throws(() => new InstallerService(zip, f.Manifest, f.State, f.Platform));
        await Task.CompletedTask;
    }),
    ("reject traversal and forbidden files", async () =>
    {
        foreach (var p in new[]
        {
            "../escape",
            "MQL5/Files/account.dat",
            "MQL5/Include/Other/a.mqh",
            "MQL5/Experts/JPWealth/../evil.mq5"
        }

        )
        {
            using var f = new Fixture(p);
            Throws(() => f.Service());
        }

        await Task.CompletedTask;
    }),
    ("reject case collision", async () =>
    {
        using var f = new Fixture("MQL5/Include/JPWealth/X.mqh", "MQL5/Include/JPWealth/x.mqh");
        Throws(() => f.Service());
        await Task.CompletedTask;
    }),
    ("unknown first install source protected", async () =>
    {
        using var f = new Fixture();
        f.Write(Fixture.Source, "user");
        Check(!f.Service().Inspect(f.Target, InstallAction.Install).CanProceed, "unknown source accepted");
        await Task.CompletedTask;
    }),
    ("unknown first install binary protected", async () =>
    {
        using var f = new Fixture();
        f.Write(Fixture.Output, "user binary");
        Check(!f.Service().Inspect(f.Target, InstallAction.Install).CanProceed, "unknown binary accepted");
        await Task.CompletedTask;
    }),
    ("stage drift after a prior compilation is rejected before target writes", async () =>
    {
        var failures = new List<string>();
        foreach (var changed in new[] { "source", "output", "product include", "standard include", "log" })
        {
            using var f = new Fixture();
            string? priorSource = null, priorLog = null;
            var installProgress = 0;
            f.Platform.OnStart = request =>
            {
                if (f.Platform.Calls == 1) { priorSource = request.Source; priorLog = request.Log; }
                if (f.Platform.Calls != 2) return;
                var path = changed switch
                {
                    "source" => priorSource!,
                    "output" => Path.ChangeExtension(priorSource!, ".ex5"),
                    "product include" => Path.Combine(request.Include, "Include", "JPWealth", "common.mqh"),
                    "standard include" => Path.Combine(request.Include, "Include", "Canvas", "Canvas.mqh"),
                    _ => priorLog!
                };
                File.AppendAllText(path, "\n// changed regular stage file");
            };
            var before = f.Snapshot();
            var result = await f.Service().ExecuteAsync(f.Target, InstallAction.Install, [], new ImmediateProgress(p => { if (p.Stage == "install") installProgress++; }));
            if (result.Success || before != f.Snapshot() || installProgress != 0 || File.Exists(result.ReceiptPath)) failures.Add(changed);
            Console.WriteLine("STAGE_DRIFT " + changed + " success=" + result.Success + " targetUnchanged=" + (before == f.Snapshot()) + " installedCallbacks=" + installProgress);
        }
        Check(failures.Count == 0, "accepted stage drift: " + string.Join(", ", failures));
    }),
    ("source changed while compiler runs is rejected", async () =>
    {
        using var f = new Fixture();
        f.Platform.OnStart = request => File.AppendAllText(request.Source, "\n// unapproved source");
        var before = f.Snapshot();
        var result = await f.Service().ExecuteAsync(f.Target, InstallAction.Install, []);
        Check(!result.Success && before == f.Snapshot(), "source drift during compilation accepted");
    }),
    ("stage drift after compilation and during installation is rolled back", async () =>
    {
        var failures = new List<string>();
        foreach (var boundary in new[] { "compiled", "first installed" })
        {
            using var f = new Fixture();
            string? source = null;
            f.Platform.OnStart = request => { if (f.Platform.Calls == 1) source = request.Source; };
            var changed = false;
            var effectiveChange = false;
            var before = f.Snapshot();
            var result = await f.Service().ExecuteAsync(f.Target, InstallAction.Install, [], new ImmediateProgress(p =>
            {
                if (changed || !(boundary == "compiled" ? p.Stage == "compile" && p.Completed == 4 : p.Stage == "install" && p.Completed == 1)) return;
                // A Windows read-sharing lease may reject the write itself. The
                // attempted mutation still must fail the operation and preserve bytes.
                changed = true;
                File.AppendAllText(Path.ChangeExtension(source!, ".ex5"), "\nchanged after evidence");
                effectiveChange = true;
            }));
            if (!changed || result.Success || before != f.Snapshot() || File.Exists(result.ReceiptPath)) failures.Add(boundary);
            Console.WriteLine("STAGE_BOUNDARY " + boundary + " attempted=" + changed + " effective=" + effectiveChange + " success=" + result.Success + " targetUnchanged=" + (before == f.Snapshot()));
        }
        Check(failures.Count == 0, "stage drift accepted at boundary: " + string.Join(", ", failures));
    }),
    ("repair stage drift preserves prior installation and receipt", async () =>
    {
        using var f = new Fixture();
        var service = f.Service();
        var installed = await service.ExecuteAsync(f.Target, InstallAction.Install, []);
        Check(installed.Success, installed.Message);
        var receipt = File.ReadAllBytes(installed.ReceiptPath);
        var before = f.Snapshot();
        f.Platform.Calls = 0;
        string? priorOutput = null;
        f.Platform.OnStart = request =>
        {
            if (f.Platform.Calls == 1) priorOutput = Path.ChangeExtension(request.Source, ".ex5");
            if (f.Platform.Calls == 2) File.AppendAllText(priorOutput!, "modified during next compile");
        };
        var result = await service.ExecuteAsync(f.Target, InstallAction.Repair, []);
        Check(!result.Success && before == f.Snapshot(), "repair stage drift accepted or target changed");
        Check(receipt.SequenceEqual(File.ReadAllBytes(installed.ReceiptPath)), "prior receipt changed on refusal");
    }),
    ("temporary copy verifies approved bytes before atomic publication", async () =>
    {
        using var f = new Fixture();
        var source = Path.Combine(f.Root, "changed-source.bin");
        var destination = Path.Combine(f.Data, "preserved.bin");
        File.WriteAllText(source, "unapproved replacement bytes");
        File.WriteAllText(destination, "original user bytes");
        var method = typeof(InstallerService).GetMethod("AtomicCopy", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Static)!;
        var published = false;
        try
        {
            method.Invoke(null, [source, destination, Fixture.Hash(Encoding.UTF8.GetBytes("approved bytes")), (Action)(() => published = true)]);
            throw new Exception("mismatched temporary copy accepted");
        }
        catch (System.Reflection.TargetInvocationException error) when (error.InnerException is InvalidDataException) { }
        Check(!published && File.ReadAllText(destination) == "original user bytes", "unapproved bytes reached destination");
        Check(!Directory.EnumerateFiles(f.Data, "*.stoikus-*.tmp").Any(), "temporary copy leaked");
        await Task.CompletedTask;
    }),
    ("third compilation failure preserves target", async () =>
    {
        using var f = new Fixture();
        f.Platform.FailAt = 3;
        var before = f.Snapshot();
        var r = await f.Service().ExecuteAsync(f.Target, InstallAction.Install, []);
        Check(!r.Success, "failed compile accepted");
        Check(before == f.Snapshot(), "target changed");
    }),
    ("old EX5 cannot satisfy build", async () =>
    {
        using var f = new Fixture();
        f.Platform.NoOutput = true;
        f.Write(Fixture.Output, "old known binary");
        f.Known(Fixture.Output, "old known binary");
        var r = await f.Service().ExecuteAsync(f.Target, InstallAction.Install, []);
        Check(!r.Success, "missing output accepted");
    }),
    ("bad logs rejected", async () =>
    {
        foreach (var log in new[]
        {
            "Result: 1 errors, 0 warnings",
            "Result: 0 errors, 1 warnings",
            "Result: 0 errors, 0 warn",
            "Result: 0 errors, 0 warnings\ntruncated"
        }

        )
        {
            using var f = new Fixture();
            f.Platform.Log = log;
            Check(!(await f.Service().ExecuteAsync(f.Target, InstallAction.Install, [])).Success, "bad log accepted: " + log);
        }
    }),
    ("native exit one with complete own-source evidence accepted and retained", async () =>
    {
        using var f = new Fixture(); f.Platform.ExitCode = 1;
        var r = await f.Service().ExecuteAsync(f.Target, InstallAction.Install, []);
        Check(r.Success, "observed native MetaEditor success convention rejected: " + r.Message);
        var report = JsonNode.Parse(File.ReadAllText(r.ReportPath))!;
        Check(report["buildEvidence"]!.AsArray().Count == 4, "four attempt receipts missing");
        Check(report["buildEvidence"]!.AsArray().All(a => a!["exit"]!.GetValue<int>() == 1), "raw native exit was normalized");
    }),
    ("native source-bound include log admits only the same stage", async () =>
    {
        const string source = "C:\\isolado\\MQL5\\Experts\\JPWealth\\Monitor.mq5";
        const string include = "C:\\isolado\\MQL5\\Include\\JPWealth\\Core.mqh";
        string Log(string dependency) => source + " : information: compiling " + source + "\n" +
            source + " : information: including " + dependency + "\n : information: generating code 100%\n : information: code generated\nResult: 0 errors, 0 warnings, 123 ms elapsed, cpu='X64 Regular'";
        Check(InstallerService.ValidCompileLog(Encoding.UTF8.GetBytes(Log(include)), source), "valid native transitive include rejected");
        Check(!InstallerService.ValidCompileLog(Encoding.UTF8.GetBytes(Log("C:\\foreign\\Core.mqh")), source), "foreign include accepted");
        Check(!InstallerService.ValidCompileLog(Encoding.UTF8.GetBytes(Log("C:\\isolado\\MQL5\\..\\private\\Core.mqh")), source), "traversal include accepted");
        await Task.CompletedTask;
    }),
    ("native bitmap diagnostics bind stage path basename and resource identity", async () =>
    {
        const string source = @"C:\isolado\MQL5\Indicators\JPWealth\Conta.mq5";
        const string bitmap = @"C:\isolado\MQL5\Images\JPWealth\Logo.bmp";
        string Log(string path, string basename, string resource) => source + " : information: compiling " + source + "\n" +
            path + " : information: resource '" + basename + "' as resource \"" + resource + "\"\n : information: code generated\nResult: 0 errors, 0 warnings, 123 ms elapsed, cpu='X64 Regular'";
        Check(InstallerService.ValidCompileLog(Encoding.UTF8.GetBytes(Log(bitmap, "Logo.bmp", @"::Images\JPWealth\Logo.bmp")), source), "native logo diagnostic refused");
        foreach (var invalid in new[] {
            Log(bitmap, "Other.bmp", @"::Images\JPWealth\Logo.bmp"),
            Log(bitmap, "Logo.bmp", @"::Images\JPWealth\Other.bmp"),
            Log(@"C:\foreign\Logo.bmp", "Logo.bmp", @"::Images\JPWealth\Logo.bmp"),
            Log(@"C:\isolado\MQL5\Images\..\private\Logo.bmp", "Logo.bmp", @"::Images\..\private\Logo.bmp") })
            Check(!InstallerService.ValidCompileLog(Encoding.UTF8.GetBytes(invalid), source), "unbound bitmap diagnostic accepted");
        await Task.CompletedTask;
    }),
    ("native exit one with error or missing output cannot install", async () =>
    {
        foreach (var missing in new[] { false, true })
        {
            using var f = new Fixture(); f.Platform.ExitCode = 1;
            f.Platform.NoOutput = missing; if (!missing) f.Platform.FailAt = 2;
            var before = f.Snapshot();
            Check(!(await f.Service().ExecuteAsync(f.Target, InstallAction.Install, [])).Success, "invalid native artifacts accepted");
            Check(before == f.Snapshot(), "failure changed target");
        }
    }),
    ("unknown process failure with apparent successful artifacts rejected", async () =>
    {
        using var f = new Fixture(); f.Platform.ExitCode = 2;
        var before = f.Snapshot();
        Check(!(await f.Service().ExecuteAsync(f.Target, InstallAction.Install, [])).Success, "unrecognized process failure accepted");
        Check(before == f.Snapshot(), "unknown failure changed target");
    }),
    ("foreign or missing source log and unknown body cannot prove compilation", async () =>
    {
        foreach (var shape in new[] { "foreign", "missing", "unknown", "duplicate" })
        {
            using var f = new Fixture();
            if (shape == "foreign") f.Platform.LogSourceOverride = "OtherProgram.mq5";
            if (shape == "missing") f.Platform.OmitProgramHeader = true;
            if (shape == "unknown") f.Platform.Log = "unrecognized compiler message\nResult: 0 errors, 0 warnings, 20 msec elapsed";
            if (shape == "duplicate") f.Platform.Log = "Result: 0 errors, 0 warnings, 1 ms elapsed\nResult: 0 errors, 0 warnings, 20 ms elapsed";
            var before = f.Snapshot();
            Check(!(await f.Service().ExecuteAsync(f.Target, InstallAction.Install, [])).Success, "unbound or incomplete log accepted: " + shape);
            Check(before == f.Snapshot(), "unbound log changed target");
        }
    }),
    ("missing dependency leaves target intact", async () =>
    {
        using var f = new Fixture();
        File.Delete(Path.Combine(f.Data, "MQL5/Include/Canvas/Canvas.mqh"));
        var before = f.Snapshot();
        Check(!(await f.Service().ExecuteAsync(f.Target, InstallAction.Install, [])).Success, "missing dependency accepted");
        Check(before == f.Snapshot(), "target changed");
    }),
    ("escaped include rejected", async () =>
    {
        using var f = new Fixture();
        f.Write("MQL5/Include/Canvas/Canvas.mqh", "#include \"../../../../outside.mqh\"");
        Check(!(await f.Service().ExecuteAsync(f.Target, InstallAction.Install, [])).Success, "escaped dependency accepted");
    }),
    ("open terminal blocks", async () =>
    {
        using var f = new Fixture();
        f.Platform.Open = true;
        Check(!f.Service().Inspect(f.Target, InstallAction.Install).CanProceed, "open process accepted");
        await Task.CompletedTask;
    }),
    ("cancellation leaves target intact", async () =>
    {
        using var f = new Fixture();
        using var c = new CancellationTokenSource();
        c.Cancel();
        var before = f.Snapshot();
        Check(!(await f.Service().ExecuteAsync(f.Target, InstallAction.Install, [], cancellationToken: c.Token)).Success, "cancel accepted");
        Check(before == f.Snapshot(), "target changed");
    }),
    ("install repeat repair remove preserve unrelated", async () =>
    {
        using var f = new Fixture();
        f.Write("MQL5/Files/account.dat", "private");
        var before = f.Snapshot();
        var s = f.Service();
        var installed = await s.ExecuteAsync(f.Target, InstallAction.Install, []);
        Check(installed.Success, "install failed: " + installed.Message);
        Check(File.Exists(Path.Combine(f.Data, Fixture.Output)), "missing EX5");
        Check(!File.Exists(Path.Combine(f.Data, "LEIA_PRIMEIRO.md")), "guide leaked");
        Check((await s.ExecuteAsync(f.Target, InstallAction.Install, [])).Success, "repeat failed");
        File.Delete(Path.Combine(f.Data, Fixture.Output));
        Check((await s.ExecuteAsync(f.Target, InstallAction.Repair, [])).Success, "missing repair failed");
        Check((await s.ExecuteAsync(f.Target, InstallAction.Remove, [])).Success, "remove failed");
        Check(before == f.Snapshot(), "remove did not restore original");
    }),
    ("modified owned file protected from repair and remove", async () =>
    {
        using var f = new Fixture();
        var s = f.Service();
        var installed = await s.ExecuteAsync(f.Target, InstallAction.Install, []);
        Check(installed.Success, "install failed: " + installed.Message);
        f.Write(Fixture.Output, "edited");
        Check(!s.Inspect(f.Target, InstallAction.Repair).CanProceed, "repair overwrites edit");
        Check(!(await s.ExecuteAsync(f.Target, InstallAction.Remove, [])).Success, "remove overwrites edit");
        Check(File.ReadAllText(Path.Combine(f.Data, Fixture.Output)) == "edited", "edit lost");
    }),
    ("real generated payload validates", async () =>
    {
        var root = FindRoot();
        _ = new InstallerService(File.ReadAllBytes(Path.Combine(root, "generated/payload.zip")), File.ReadAllBytes(Path.Combine(root, "generated/payload.json")), "/private/tmp/real-payload-state", new FakePlatform());
        await Task.CompletedTask;
    }),
    ("target reparse blocked", async () =>
    {
        using var f = new Fixture();
        Directory.CreateDirectory(Path.Combine(f.Root, "outside"));
        Directory.CreateSymbolicLink(Path.Combine(f.Data, "MQL5/Experts"), Path.Combine(f.Root, "outside"));
        Check(!f.Service().Inspect(f.Target, InstallAction.Install).CanProceed, "target symlink accepted");
        await Task.CompletedTask;
    }),
    ("missing compiler and false association rejected", async () =>
    {
        using var f = new Fixture();
        File.Delete(f.Target.MetaEditorExe);
        Check(!f.Service().Inspect(f.Target, InstallAction.Install).CanProceed, "missing compiler accepted");
        await Task.CompletedTask;
    }),
    ("standard dependency closure excludes private files", async () =>
    {
        using var f = new Fixture();
        f.Write("MQL5/Include/Canvas/Canvas.mqh", "#include <Math/Math.mqh>");
        f.Write("MQL5/Include/Math/Math.mqh", "// math");
        f.Write("MQL5/Include/private-secret.mqh", "secret");
        var r = await f.Service().ExecuteAsync(f.Target, InstallAction.Install, []);
        Check(r.Success, r.Message);
        Check(Directory.GetFiles(f.State, "Math.mqh", SearchOption.AllDirectories).Length == 1, "closure missing");
        Check(Directory.GetFiles(f.State, "private-secret.mqh", SearchOption.AllDirectories).Length == 0, "private dependency copied");
    }),
    ("known original restored after repeated install", async () =>
    {
        using var f = new Fixture();
        f.Write(Fixture.Source, "official prior");
        f.Known(Fixture.Source, "official prior");
        var before = f.Snapshot();
        var s = f.Service();
        Check((await s.ExecuteAsync(f.Target, InstallAction.Install, [])).Success, "known install failed");
        Check((await s.ExecuteAsync(f.Target, InstallAction.Install, [])).Success, "repeat failed");
        var r = await s.ExecuteAsync(f.Target, InstallAction.Remove, []);
        Check(r.Success, r.Message);
        Check(before == f.Snapshot(), "original bytes lost");
    }),
    ("legacy exact known optional restored", async () =>
    {
        using var f = new Fixture();
        const string path = "MQL5/Experts/JPWealth/Legacy.mq5";
        f.Write(path, "official legacy");
        f.Known(path, "official legacy", true);
        f.Write("MQL5/Experts/JPWealth/Unknown.mq5", "custom");
        var before = f.Snapshot();
        var s = f.Service();
        Check(s.Inspect(f.Target, InstallAction.Install).LegacyCandidates.Count == 1, "legacy identity mismatch");
        var r = await s.ExecuteAsync(f.Target, InstallAction.Install, [path]);
        Check(r.Success, r.Message);
        Check(!File.Exists(Path.Combine(f.Data, path)), "legacy not organized");
        Check((await s.ExecuteAsync(f.Target, InstallAction.Remove, [])).Success, "remove failed");
        Check(before == f.Snapshot(), "legacy not restored");
    }),
    ("modified legacy never organized", async () =>
    {
        using var f = new Fixture();
        const string p = "MQL5/Experts/JPWealth/Legacy.mq5";
        f.Write(p, "user modified");
        f.Known(p, "official legacy", true);
        var s = f.Service();
        Check(s.Inspect(f.Target, InstallAction.Install).LegacyCandidates.Count == 0, "unknown listed");
        Check(!(await s.ExecuteAsync(f.Target, InstallAction.Install, [p])).Success, "unknown organized");
    }),
    ("cancel after first mutation rolls back", async () =>
    {
        using var f = new Fixture();
        using var c = new CancellationTokenSource();
        var before = f.Snapshot();
        var r = await f.Service().ExecuteAsync(f.Target, InstallAction.Install, [], new ImmediateProgress(p =>
        {
            if (p.Stage == "install")
                c.Cancel();
        }), c.Token);
        Check(!r.Success, "cancel succeeded");
        Check(before == f.Snapshot(), "rollback lost original");
    }),
    ("rollback preserves concurrent user edit", async () =>
    {
        using var f = new Fixture();
        using var c = new CancellationTokenSource();
        var r = await f.Service().ExecuteAsync(f.Target, InstallAction.Install, [], new ImmediateProgress(p =>
        {
            if (p.Stage == "install")
            {
                f.Write(Fixture.Source, "concurrent edit");
                c.Cancel();
            }
        }), c.Token);
        Check(!r.Success && r.Message.Contains("manual"), "manual conflict not reported");
        Check(File.ReadAllText(Path.Combine(f.Data, Fixture.Source)) == "concurrent edit", "user edit overwritten");
        var retry = await f.Service().ExecuteAsync(f.Target, InstallAction.Install, []);
        Check(!retry.Success, "unresolved journal ignored");
    }),
    ("operation lock prevents mutation", async () =>
    {
        using var f = new Fixture();
        var home = f.Home();
        Directory.CreateDirectory(home);
        using var locked = new FileStream(Path.Combine(home, "operation.lock"), FileMode.OpenOrCreate, FileAccess.ReadWrite, FileShare.None);
        var before = f.Snapshot();
        Check(!(await f.Service().ExecuteAsync(f.Target, InstallAction.Install, [])).Success, "lock ignored");
        Check(before == f.Snapshot(), "target changed with lock");
    }),
    ("backup tamper protects original", async () =>
    {
        using var f = new Fixture();
        f.Write(Fixture.Source, "official prior");
        f.Known(Fixture.Source, "official prior");
        var s = f.Service();
        var r = await s.ExecuteAsync(f.Target, InstallAction.Install, []);
        Check(r.Success, r.Message);
        var receipt = JsonNode.Parse(File.ReadAllText(r.ReceiptPath))!;
        var backup = receipt["files"]!.AsArray().First(x => x!["path"]!.GetValue<string>() == Fixture.Source)!["backup"]!.GetValue<string>();
        File.WriteAllText(backup, "tamper");
        var before = f.Snapshot();
        Check(!(await s.ExecuteAsync(f.Target, InstallAction.Remove, [])).Success, "bad backup accepted");
        Check(before == f.Snapshot(), "target changed with bad backup");
    }),
    ("interrupted journal recovers through explicit action", async () =>
    {
        using var f = new Fixture();
        var home = f.Home();
        var backup = Path.Combine(home, "runs", "interrupted", "backups", "file.bak");
        Directory.CreateDirectory(Path.GetDirectoryName(backup)!);
        File.WriteAllText(backup, "original");
        f.Write(Fixture.Source, "interrupted");
        var journal = new
        {
            target = Path.GetFullPath(f.Data).ToUpperInvariant(),
            receiptPath = Path.Combine(home, "receipt.json"),
            previousReceipt = (string? )null,
            phase = "mutating",
            run = Path.GetDirectoryName(Path.GetDirectoryName(backup)),
            files = new[]
            {
                new
                {
                    path = Fixture.Source,
                    beforeHash = Fixture.Hash(Encoding.UTF8.GetBytes("original")),
                    afterHash = Fixture.Hash(Encoding.UTF8.GetBytes("interrupted")),
                    backup,
                    afterFile = (string? )null,
                    status = "writing"
                }
            }
        };
        File.WriteAllText(Path.Combine(home, "journal.json"), JsonSerializer.Serialize(journal));
        var r = await f.Service().ExecuteAsync(f.Target, InstallAction.Recover, []);
        Check(r.Success, r.Message);
        Check(File.ReadAllText(Path.Combine(f.Data, Fixture.Source)) == "original", "journal did not restore");
        var j = JsonNode.Parse(File.ReadAllText(Path.Combine(home, "journal.json")))!;
        Check(j["phase"]!.GetValue<string>() == "rolled-back", "journal not finalized");
    }),
    ("compiler terminal formats", async () =>
    {
        Check(InstallerService.ValidCompileLog(Encoding.Unicode.GetPreamble().Concat(Encoding.Unicode.GetBytes("compiling\n0 errors, 0 warnings, 20 msec elapsed")).ToArray()), "terminal log without Result rejected");
        Check(InstallerService.ValidCompileLog(Encoding.UTF8.GetBytes("Result: 0 errors, 0 warnings, 20 msec elapsed")), "UTF8 result rejected");
        await Task.CompletedTask;
    }),
    ("recovery requires closed processes", async () =>
    {
        using var f = new Fixture();
        var s = f.Service();
        var installed = await s.ExecuteAsync(f.Target, InstallAction.Install, []);
        Check(installed.Success, installed.Message);
        var journalPath = Path.Combine(f.Home(), "journal.json");
        var journal = JsonNode.Parse(File.ReadAllText(journalPath))!;
        journal["phase"] = "mutating";
        File.WriteAllText(journalPath, journal.ToJsonString());
        var before = f.Snapshot();
        f.Platform.Open = true;
        Check(!(await s.ExecuteAsync(f.Target, InstallAction.Install, [])).Success, "open accepted");
        Check(before == f.Snapshot(), "recovery wrote to open terminal");
    }),
    ("truncated terminal suffix rejected", async () =>
    {
        Check(!InstallerService.ValidCompileLog(Encoding.UTF8.GetBytes("Result: 0 errors, 0 warnings, trunc")), "truncated terminal suffix accepted");
        await Task.CompletedTask;
    }),
    ("copy failure rolls prior writes back", async () =>
    {
        using var f = new Fixture();
        var before = f.Snapshot();
        bool changed = false;
        var r = await f.Service().ExecuteAsync(f.Target, InstallAction.Install, [], new ImmediateProgress(p =>
        {
            if (p.Stage == "install" && !changed)
            {
                changed = true;
                Directory.CreateDirectory(Path.Combine(f.Data, Fixture.Sources[1]));
            }
        }));
        Check(!r.Success, "directory collision ignored");
        Check(before == f.Snapshot(), "copy failure retained prior writes");
    }),
    ("ZIP symlink rejected", async () =>
    {
        using var f = new Fixture();
        using var ms = new MemoryStream();
        using (var zip = new ZipArchive(ms, ZipArchiveMode.Create, true))
        {
            using var input = new ZipArchive(new MemoryStream(f.Zip));
            foreach (var old in input.Entries)
            {
                var entry = zip.CreateEntry(old.FullName);
                entry.ExternalAttributes = old.FullName == Fixture.Source ? (0xa000 << 16) : 0;
                using var from = old.Open();
                using var to = entry.Open();
                from.CopyTo(to);
            }
        }

        f.Zip = ms.ToArray();
        var node = JsonNode.Parse(f.Manifest)!;
        node["archiveBytes"] = f.Zip.Length;
        node["archiveSha256"] = Fixture.Hash(f.Zip);
        f.Manifest = Encoding.UTF8.GetBytes(node.ToJsonString());
        Throws(() => f.Service());
        await Task.CompletedTask;
    }),
    ("exact daily program identity enforced", async () =>
    {
        const string extra = "MQL5/Experts/JPWealth/Unexpected.mq5";
        using var f = new Fixture(extra);
        var m = JsonNode.Parse(f.Manifest)!;
        m["programs"]![0]!["source"] = extra;
        m["programs"]![0]!["output"] = Path.ChangeExtension(extra, ".ex5");
        f.Manifest = Encoding.UTF8.GetBytes(m.ToJsonString());
        Throws(() => f.Service());
        await Task.CompletedTask;
    }),
    ("backup creation failure does not mutate target", async () =>
    {
        using var f = new Fixture();
        f.Write(Fixture.Source, "official prior");
        f.Known(Fixture.Source, "official prior");
        var before = f.Snapshot();
        var r = await f.Service().ExecuteAsync(f.Target, InstallAction.Install, [], new ImmediateProgress(p =>
        {
            if (p.Stage == "compile" && p.Completed == 4)
            {
                var run = Directory.GetDirectories(Path.Combine(f.Home(), "runs")).Single();
                File.WriteAllText(Path.Combine(run, "backups"), "collision");
            }
        }));
        Check(!r.Success, "backup failure ignored");
        Check(before == f.Snapshot(), "target changed without backup");
    }),
    ("selected legacy edited during compile remains in place", async () =>
    {
        using var f = new Fixture();
        const string p = "MQL5/Experts/JPWealth/Legacy.mq5";
        f.Write(p, "official");
        f.Known(p, "official", true);
        string? edited = null;
        var r = await f.Service().ExecuteAsync(f.Target, InstallAction.Install, [p], new ImmediateProgress(x =>
        {
            if (x.Stage == "compile" && x.Completed == 4)
            {
                f.Write(p, "USER MODIFIED WHILE COMPILING");
                edited = f.Snapshot();
            }
        }));
        Check(!r.Success, "modified legacy accepted");
        Check(edited == f.Snapshot(), "legacy edit removed or other target mutated");
    }),
    ("desired identity cannot change to another catalog version during compile", async () =>
    {
        using var f = new Fixture();
        f.Write(Fixture.Source, "official1");
        f.Known(Fixture.Source, "official1");
        f.Known(Fixture.Source, "official2");
        string? edited = null;
        var r = await f.Service().ExecuteAsync(f.Target, InstallAction.Install, [], new ImmediateProgress(x =>
        {
            if (x.Stage == "compile" && x.Completed == 4)
            {
                f.Write(Fixture.Source, "official2");
                edited = f.Snapshot();
            }
        }));
        Check(!r.Success, "changed desired identity silently adopted");
        Check(edited == f.Snapshot(), "changed desired bytes overwritten");
    }),
    ("third compile failure report retains complete attempts", async () =>
    {
        using var f = new Fixture();
        f.Platform.FailAt = 3;
        var r = await f.Service().ExecuteAsync(f.Target, InstallAction.Install, []);
        Check(!r.Success, "compile accepted");
        var report = JsonNode.Parse(File.ReadAllText(r.ReportPath))!;
        Check(report["run"] is not null, "report lacks run association");
        var run = report["run"]!.GetValue<string>();
        var attempts = report["buildEvidence"]!.AsArray();
        Check(attempts.Count == 3, "attempt evidence lost");
        foreach (var a in attempts)
        {
            var source = a!["sourcePath"]!.GetValue<string>();
            var log = a["log"]!.GetValue<string>();
            Check(source.StartsWith(run) && log.StartsWith(run), "attempt outside run");
            Check(a["sourceSha256"]!.GetValue<string>() == Fixture.Hash(File.ReadAllBytes(source)), "source hash lost");
            Check(a["editorSha256"]!.GetValue<string>() == Fixture.Hash(File.ReadAllBytes(f.Target.MetaEditorExe)), "editor hash lost");
            Check(a.AsObject().ContainsKey("editorVersion"), "editor version absent");
            Check(a["arguments"]!.AsArray().Count == 3 && a["dependencies"]!.AsArray().Count >= 2, "command/dependencies lost");
            Check(a["logSha256"]!.GetValue<string>() == Fixture.Hash(File.ReadAllBytes(log)), "log hash lost");
            Check(a["timeoutSeconds"]!.GetValue<double>() > 0 && a["exit"]!.GetValue<int>() == 0, "process metadata lost");
            Check(a["finished"] is not null, "attempt not finalized");
        }

        Check(attempts[0]!["status"]!.GetValue<string>() == "succeeded" && attempts[2]!["status"]!.GetValue<string>() == "failed", "outcomes lost");
        Check(attempts[2]!["diagnostic"]!.GetValue<string>().Length > 0, "failure diagnostic lost");
    }),
    ("cancel active compile retains evidence without target writes", async () =>
    {
        using var f = new Fixture();
        f.Platform.WaitForCancellation = true;
        using var c = new CancellationTokenSource();
        var before = f.Snapshot();
        var task = f.Service().ExecuteAsync(f.Target, InstallAction.Install, [], cancellationToken: c.Token);
        await f.Platform.Started.Task.WaitAsync(TimeSpan.FromSeconds(10));
        c.Cancel();
        var r = await task;
        Check(!r.Success && before == f.Snapshot(), "active cancel mutated target");
        var report = JsonNode.Parse(File.ReadAllText(r.ReportPath))!;
        Check(report["buildEvidence"]?[0]?["status"]?.GetValue<string>() == "cancelled", "active cancellation evidence lost");
    }),
    ("timeout retains attempt diagnostic", async () =>
    {
        using var f = new Fixture();
        f.Platform.Timeout = true;
        var before = f.Snapshot();
        var r = await f.Service().ExecuteAsync(f.Target, InstallAction.Install, []);
        Check(!r.Success && before == f.Snapshot(), "timeout mutated target");
        var report = JsonNode.Parse(File.ReadAllText(r.ReportPath))!;
        Check(report["buildEvidence"]?[0]?["status"]?.GetValue<string>() == "timeout", "timeout evidence lost");
    }),
    ("recovery after receipt publication restores previous receipt", async () =>
    {
        using var f = new Fixture();
        var before = f.Snapshot();
        var s = f.Service();
        var r = await s.ExecuteAsync(f.Target, InstallAction.Install, []);
        Check(r.Success, r.Message);
        var jp = Path.Combine(f.Home(), "journal.json");
        var j = JsonNode.Parse(File.ReadAllText(jp))!;
        j["phase"] = "mutating";
        File.WriteAllText(jp, j.ToJsonString());
        var recovery = await s.ExecuteAsync(f.Target, InstallAction.Recover, []);
        Check(recovery.Success, recovery.Message);
        Check(before == f.Snapshot() && !File.Exists(r.ReceiptPath), "receipt publication window not recovered");
    }),
    ("restore interruption resumes and retries safely", async () =>
    {
        foreach (bool alreadyRestored in new[]
        {
            false,
            true
        }

        )
        {
            using var f = new Fixture();
            var backup = f.SeedInterrupted("restoring", alreadyRestored ? "original" : "interrupted");
            var r = await f.Service().ExecuteAsync(f.Target, InstallAction.Recover, []);
            Check(r.Success, r.Message);
            Check(File.ReadAllText(Path.Combine(f.Data, Fixture.Source)) == "original", "restoring window not recovered");
            var before = f.Snapshot();
            await f.Service().ExecuteAsync(f.Target, InstallAction.Recover, []);
            Check(before == f.Snapshot(), "repeat recovery changed bytes");
        }
    }),
    ("restore missing backup stays recoverable", async () =>
    {
        using var f = new Fixture();
        var backup = f.SeedInterrupted("restoring", "interrupted");
        File.Delete(backup);
        var r = await f.Service().ExecuteAsync(f.Target, InstallAction.Recover, []);
        Check(!r.Success && File.ReadAllText(Path.Combine(f.Data, Fixture.Source)) == "interrupted", "missing backup lost target");
        File.WriteAllText(backup, "original");
        await f.Service().ExecuteAsync(f.Target, InstallAction.Recover, []);
        Check(File.ReadAllText(Path.Combine(f.Data, Fixture.Source)) == "original", "retry did not restore");
    }),
    ("nonportable origin encodings and association", async () =>
    {
        foreach (var encoding in new Encoding[]
        {
            Encoding.UTF8,
            Encoding.Unicode
        }

        )
        {
            using var f = new Fixture();
            var data = Path.Combine(f.Root, "appdata");
            Directory.CreateDirectory(Path.Combine(data, "MQL5"));
            File.WriteAllText(Path.Combine(data, "origin.txt"), f.Data, encoding);
            var t = f.Target with
            {
                DataDirectory = data,
                Portable = false
            };
            Check(f.Service().Inspect(t, InstallAction.Install).CanProceed, "valid origin rejected");
            File.WriteAllText(Path.Combine(data, "origin.txt"), f.Root, encoding);
            Check(!f.Service().Inspect(t, InstallAction.Install).CanProceed, "wrong origin accepted");
            var other = Path.Combine(f.Root, "other", "metaeditor64.exe");
            Directory.CreateDirectory(Path.GetDirectoryName(other)!);
            File.WriteAllText(other, "editor");
            Check(!f.Service().Inspect(f.Target with { MetaEditorExe = other }, InstallAction.Install).CanProceed, "mixed editor accepted");
        }

        await Task.CompletedTask;
    }),
    ("transitive include symlink blocked", async () =>
    {
        using var f = new Fixture();
        var outside = Path.Combine(f.Root, "outside.mqh");
        File.WriteAllText(outside, "private");
        f.Write("MQL5/Include/Canvas/Canvas.mqh", "#include <Transitive.mqh>");
        File.CreateSymbolicLink(Path.Combine(f.Data, "MQL5/Include/Transitive.mqh"), outside);
        var before = f.Snapshot();
        var r = await f.Service().ExecuteAsync(f.Target, InstallAction.Install, []);
        Check(!r.Success && before == f.Snapshot(), "transitive link accepted");
    }),
    ("state and receipt backup reparse blocked", async () =>
    {
        using (var f = new Fixture())
        {
            var outside = Path.Combine(f.Root, "outside");
            Directory.CreateDirectory(outside);
            Directory.CreateSymbolicLink(f.State, outside);
            var before = f.Snapshot();
            Check(!(await f.Service().ExecuteAsync(f.Target, InstallAction.Install, [])).Success && before == f.Snapshot(), "state link accepted");
        }

        using (var f = new Fixture())
        {
            f.Write(Fixture.Source, "official");
            f.Known(Fixture.Source, "official");
            var s = f.Service();
            var r = await s.ExecuteAsync(f.Target, InstallAction.Install, []);
            Check(r.Success, r.Message);
            var receipt = JsonNode.Parse(File.ReadAllText(r.ReceiptPath))!;
            var backup = receipt["files"]!.AsArray().First(x => x!["path"]!.GetValue<string>() == Fixture.Source)!["backup"]!.GetValue<string>();
            var outside = Path.Combine(f.Root, "outside");
            File.WriteAllText(outside, "official");
            File.Delete(backup);
            File.CreateSymbolicLink(backup, outside);
            var before = f.Snapshot();
            Check(!(await s.ExecuteAsync(f.Target, InstallAction.Remove, [])).Success && before == f.Snapshot(), "backup link accepted");
        }
    }),
    ("compile attempt metadata exists before process invocation", async () =>
    {
        using var f = new Fixture();
        int seen = 0;
        f.Platform.OnStart = r =>
        {
            var report = JsonNode.Parse(File.ReadAllText(Directory.GetFiles(Path.Combine(f.Home(), "reports")).Single()))!;
            var a = report["buildEvidence"]!.AsArray().Last()!;
            Check(a["status"]!.GetValue<string>() == "running" && a["sourcePath"]!.GetValue<string>() == r.Source, "attempt was not persisted before process");
            Check(a["sourceSha256"] is not null && a["editorSha256"] is not null, "preinvoke identity missing");
            seen++;
        };
        var result = await f.Service().ExecuteAsync(f.Target, InstallAction.Install, []);
        Check(result.Success && seen == 4, result.Message);
    }),
    ("stage reparse cannot supply installed outputs", async () =>
    {
        using var f = new Fixture();
        var before = f.Snapshot();
        bool changed = false;
        f.Platform.OnStart = r =>
        {
            if (changed)
                return;
            changed = true;
            var stage = Path.GetDirectoryName(r.Include)!;
            var outside = Path.Combine(f.Root, "moved-stage");
            Directory.Move(stage, outside);
            Directory.CreateSymbolicLink(stage, outside);
        };
        var result = await f.Service().ExecuteAsync(f.Target, InstallAction.Install, []);
        Check(!result.Success && before == f.Snapshot(), "stage reparse accepted");
        var report = JsonNode.Parse(File.ReadAllText(result.ReportPath))!;
        Check(report["buildEvidence"]![0]!["status"]!.GetValue<string>() == "failed", "unsafe stage output labeled succeeded");
    }),
    ("recovery replaces published receipt with prior exact bytes", async () =>
    {
        using var f = new Fixture();
        var s = f.Service();
        var first = await s.ExecuteAsync(f.Target, InstallAction.Install, []);
        Check(first.Success, first.Message);
        var originalReceipt = File.ReadAllBytes(first.ReceiptPath);
        var before = f.Snapshot();
        var second = await s.ExecuteAsync(f.Target, InstallAction.Install, []);
        Check(second.Success, second.Message);
        var journalPath = Path.Combine(f.Home(), "journal.json");
        var j = JsonNode.Parse(File.ReadAllText(journalPath))!;
        j["phase"] = "mutating";
        File.WriteAllText(journalPath, j.ToJsonString());
        var changed = JsonNode.Parse(File.ReadAllText(first.ReceiptPath))!;
        changed["productVersion"] = "interrupted-publication";
        File.WriteAllText(first.ReceiptPath, changed.ToJsonString());
        var calls = f.Platform.Calls;
        var next = await s.ExecuteAsync(f.Target, InstallAction.Recover, []);
        Check(next.Success && f.Platform.Calls == calls, next.Message);
        Check(File.ReadAllBytes(first.ReceiptPath).SequenceEqual(originalReceipt), "old receipt not restored byte for byte");
        Check(before == f.Snapshot(), "recovery changed preexisting bytes");
    }),
    ("pending first-install recovery preview is readonly and reachable", async () =>
    {
        using var f = new Fixture();
        var before = f.Snapshot();
        f.SeedPending(Fixture.Output, null, "partial EX5");
        var journal = File.ReadAllBytes(Path.Combine(f.Home(), "journal.json"));
        var partial = f.Snapshot();
        var service = f.Service();
        Check(service.HasPendingRecovery(f.Target), "pending journal undiscoverable");
        Check(!service.Inspect(f.Target, InstallAction.Install).CanProceed, "normal install allowed pending journal");
        var preview = service.Inspect(f.Target, InstallAction.Recover);
        Check(preview.CanProceed && preview.Changes.Any(c => c.RelativePath == Fixture.Output), "no recovery preview");
        Check(journal.SequenceEqual(File.ReadAllBytes(Path.Combine(f.Home(), "journal.json"))) && partial == f.Snapshot(), "readonly preview mutated files");
        var result = await service.ExecuteAsync(f.Target, InstallAction.Recover, []);
        Check(result.Success, result.Message);
        Check(before == f.Snapshot() && f.Platform.Calls == 0, "recovery compiled/installed instead of rollback");
        Check(!service.HasPendingRecovery(f.Target) && service.Inspect(f.Target, InstallAction.Install).CanProceed, "fresh install cannot be inspected after recovery");
    }),
    ("explicit recovery restores partial repair and receipt", async () =>
    {
        using var f = new Fixture();
        var s = f.Service();
        var install = await s.ExecuteAsync(f.Target, InstallAction.Install, []);
        Check(install.Success, install.Message);
        var before = f.Snapshot();
        var receipt = File.ReadAllBytes(install.ReceiptPath);
        var old = File.ReadAllText(Path.Combine(f.Data, Fixture.Output));
        f.SeedPending(Fixture.Output, old, "partial repair", Convert.ToBase64String(receipt));
        Check(s.HasPendingRecovery(f.Target) && !s.Inspect(f.Target, InstallAction.Repair).CanProceed, "repair partial not gated");
        Check(s.Inspect(f.Target, InstallAction.Recover).CanProceed, "repair recovery not available");
        var calls = f.Platform.Calls;
        var result = await s.ExecuteAsync(f.Target, InstallAction.Recover, []);
        Check(result.Success && calls == f.Platform.Calls, result.Message);
        Check(before == f.Snapshot() && receipt.SequenceEqual(File.ReadAllBytes(install.ReceiptPath)), "repair original or receipt not restored");
    }),
    ("already-cancelled pending recovery never writes target or journal", async () =>
    {
        foreach (var action in new[]
        {
            InstallAction.Install,
            InstallAction.Recover
        }

        )
        {
            using var f = new Fixture();
            f.SeedPending(Fixture.Output, null, "partial");
            var before = f.Snapshot();
            var jp = Path.Combine(f.Home(), "journal.json");
            var journal = File.ReadAllBytes(jp);
            using var cancel = new CancellationTokenSource();
            cancel.Cancel();
            var result = await f.Service().ExecuteAsync(f.Target, action, [], cancellationToken: cancel.Token);
            Check(!result.Success && before == f.Snapshot() && journal.SequenceEqual(File.ReadAllBytes(jp)), "pre-cancelled action recovered files");
            Check(f.Platform.Calls == 0, "pre-cancelled action compiled");
        }
    }),
    ("journal appearing after normal preview requires explicit consent", async () =>
    {
        using var f = new Fixture();
        var s = f.Service();
        Check(s.Inspect(f.Target, InstallAction.Install).CanProceed, "initial preview failed");
        f.SeedPending(Fixture.Output, null, "partial");
        var before = f.Snapshot();
        var jp = Path.Combine(f.Home(), "journal.json");
        var journal = File.ReadAllBytes(jp);
        var r = await s.ExecuteAsync(f.Target, InstallAction.Install, []);
        Check(!r.Success && r.Message.Contains("Recuper", StringComparison.OrdinalIgnoreCase), "implicit recovery happened");
        Check(before == f.Snapshot() && journal.SequenceEqual(File.ReadAllBytes(jp)), "normal execute silently recovered");
    }),
    ("recovery without journal cannot install", async () =>
    {
        using var f = new Fixture();
        var s = f.Service();
        Check(!s.HasPendingRecovery(f.Target) && !s.Inspect(f.Target, InstallAction.Recover).CanProceed, "empty recovery allowed");
        var before = f.Snapshot();
        var r = await s.ExecuteAsync(f.Target, InstallAction.Recover, []);
        Check(!r.Success && f.Platform.Calls == 0 && before == f.Snapshot(), "empty recovery installed files");
    }),
    ("recovery detects edits and invalid backup without mutation", async () =>
    {
        foreach (bool edit in new[]
        {
            false,
            true
        }

        )
        {
            using var f = new Fixture();
            var backup = f.SeedPending(Fixture.Source, "before", "after");
            if (edit)
                f.Write(Fixture.Source, "user edit");
            else
                File.WriteAllText(backup, "tampered");
            var before = f.Snapshot();
            var jp = Path.Combine(f.Home(), "journal.json");
            var journal = File.ReadAllBytes(jp);
            var s = f.Service();
            Check(s.HasPendingRecovery(f.Target), "conflicted journal hidden");
            Check(!s.Inspect(f.Target, InstallAction.Recover).CanProceed, "unsafe recovery preview allowed");
            var r = await s.ExecuteAsync(f.Target, InstallAction.Recover, []);
            Check(!r.Success && r.Message.Contains("manual", StringComparison.OrdinalIgnoreCase), "manual recovery not reported");
            Check(before == f.Snapshot() && journal.SequenceEqual(File.ReadAllBytes(jp)), "conflicted recovery changed target/journal");
        }
    }),
    ("recovery journal target identity is scoped", async () =>
    {
        using var f = new Fixture();
        f.SeedPending(Fixture.Output, null, "partial");
        var jp = Path.Combine(f.Home(), "journal.json");
        var j = JsonNode.Parse(File.ReadAllText(jp))!;
        j["target"] = Path.Combine(f.Root, "other");
        File.WriteAllText(jp, j.ToJsonString());
        var before = f.Snapshot();
        var s = f.Service();
        Check(!s.HasPendingRecovery(f.Target) && !s.Inspect(f.Target, InstallAction.Recover).CanProceed, "foreign journal accepted");
        Check(!(await s.ExecuteAsync(f.Target, InstallAction.Recover, [])).Success && before == f.Snapshot(), "foreign recovery changed target");
    }),
    ("recovery still requires closed processes and same lock", async () =>
    {
        using var f = new Fixture();
        f.SeedPending(Fixture.Output, null, "partial");
        var before = f.Snapshot();
        f.Platform.Open = true;
        var s = f.Service();
        Check(s.HasPendingRecovery(f.Target) && !s.Inspect(f.Target, InstallAction.Recover).CanProceed, "open process preview permitted");
        Check(!(await s.ExecuteAsync(f.Target, InstallAction.Recover, [])).Success && before == f.Snapshot(), "open recovery mutated files");
        f.Platform.Open = false;
        using var held = new FileStream(Path.Combine(f.Home(), "operation.lock"), FileMode.OpenOrCreate, FileAccess.ReadWrite, FileShare.None);
        Check(!(await s.ExecuteAsync(f.Target, InstallAction.Recover, [])).Success && before == f.Snapshot(), "recovery ignored lock");
    }),
    ("readonly verify truthful", async () =>
    {
        using var f = new Fixture();
        var s = f.Service();
        var before = f.Snapshot();
        Check(s.Verify(f.Target).Contains("recibo", StringComparison.OrdinalIgnoreCase), "verify lacks missing receipt");
        Check(!Directory.Exists(f.State), "verify wrote state");
        Check(before == f.Snapshot(), "verify wrote target");
        await Task.CompletedTask;
    })
};
int failed = 0;
foreach (var(name, run)in tests)
{
    try
    {
        await run();
        Console.WriteLine("PASS " + name);
    }
    catch (Exception ex)
    {
        failed++;
        Console.WriteLine("FAIL " + name + ": " + ex.Message);
    }
}

Console.WriteLine($"{tests.Length - failed}/{tests.Length} passed");
return failed == 0 ? 0 : 1;
static string FindRoot()
{
    var path = AppContext.BaseDirectory;
    while (path is not null)
    {
        if (Directory.Exists(Path.Combine(path, "generated")))
            return path;
        path = Path.GetDirectoryName(path)!;
    }

    throw new Exception("installer root not found");
}

static void Check(bool c, string message)
{
    if (!c)
        throw new Exception(message);
}

static void Throws(Action a)
{
    try
    {
        a();
    }
    catch (InvalidDataException)
    {
        return;
    }

    throw new Exception("expected InvalidDataException");
}

sealed class ImmediateProgress(Action<InstallProgress> callback) : IProgress<InstallProgress>
{
    public void Report(InstallProgress p) => callback(p);
}

sealed class FakePlatform : IInstallerPlatform
{
    public bool Open, NoOutput, WaitForCancellation, Timeout;
    public Action<CompileRequest>? OnStart;
    public TaskCompletionSource Started = new(TaskCreationOptions.RunContinuationsAsynchronously);
    public int FailAt, Calls, ExitCode;
    public string? LogSourceOverride;
    public bool OmitProgramHeader;
    public string Log = "Result: 0 errors, 0 warnings, 20 msec elapsed";
    public bool IsProcessRunning(string path) => Open;
    public async Task<int> CompileAsync(CompileRequest r, CancellationToken c)
    {
        c.ThrowIfCancellationRequested();
        Calls++;
        OnStart?.Invoke(r);
        Started.TrySetResult();
        if (WaitForCancellation)
            await Task.Delay(System.Threading.Timeout.Infinite, c);
        if (Timeout)
            throw new TimeoutException("Fake process timeout");
        Directory.CreateDirectory(Path.GetDirectoryName(r.Log)!);
        var identity = LogSourceOverride ?? r.Source;
        var header = OmitProgramHeader ? "" : identity + " : information: compiling " + identity + "\n";
        File.WriteAllText(r.Log, header + " : information: code generated\n" + (Calls == FailAt ? "Result: 1 errors, 0 warnings" : Log), Encoding.Unicode);
        if (!NoOutput)
            File.WriteAllText(Path.ChangeExtension(r.Source, ".ex5"), "compiled:" + File.ReadAllText(r.Source));
        return ExitCode;
    }
}

sealed class Fixture : IDisposable
{
    public const string Source = "MQL5/Experts/JPWealth/JPW_Stoikus_Monitor.mq5", Output = "MQL5/Experts/JPWealth/JPW_Stoikus_Monitor.ex5";
    public static readonly string[] Sources = [Source, "MQL5/Indicators/JPWealth/JPW_Alavancagem_Atual.mq5", "MQL5/Indicators/JPWealth/JPW_NoCuda_Channels.mq5", "MQL5/Scripts/JPWealth/JPW_Stoikus_Abrir_Paineis.mq5"];
    public string Root = Path.Combine(OperatingSystem.IsMacOS() ? "/private/tmp" : Path.GetTempPath(), "stoikus-tests-" + Guid.NewGuid().ToString("N"));
    public string Data => Path.Combine(Root, "terminal");
    public string State => Path.Combine(Root, "state");

    public FakePlatform Platform = new();
    public byte[] Zip, Manifest;
    public TerminalTarget Target;
    public Fixture(params string[] extras)
    {
        Directory.CreateDirectory(Data);
        Write("terminal64.exe", "terminal");
        Write("metaeditor64.exe", "editor");
        Write("MQL5/Include/Canvas/Canvas.mqh", "// canvas");
        Write("MQL5/Include/Math/Stat/Normal.mqh", "// normal");
        Target = new(Path.Combine(Data, "terminal64.exe"), Data, Path.Combine(Data, "metaeditor64.exe"), true);
        var files = new Dictionary<string, byte[]>();
        foreach (var source in Sources)
            files[source] = Encoding.UTF8.GetBytes("// program " + source);
        files["MQL5/Include/JPWealth/common.mqh"] = Encoding.UTF8.GetBytes("// owned");
        files["LEIA_PRIMEIRO.md"] = Encoding.UTF8.GetBytes("guide");
        foreach (var e in extras)
            files[e] = Encoding.UTF8.GetBytes("extra");
        using var ms = new MemoryStream();
        using (var z = new ZipArchive(ms, ZipArchiveMode.Create, true))
            foreach (var(p, b)in files)
            {
                using var stream = z.CreateEntry(p).Open();
                stream.Write(b);
            }

        Zip = ms.ToArray();
        Manifest = JsonSerializer.SerializeToUtf8Bytes(new { schemaVersion = 1, installerVersion = "1.0.0-beta.1", productVersion = "1.22.1", calculationVersion = "1.9.0", archiveSha256 = Hash(Zip), archiveBytes = Zip.Length, files = files.Select(x => new { path = x.Key, sha256 = Hash(x.Value), bytes = x.Value.Length }), programs = Sources.Select(source => new { source, output = Path.ChangeExtension(source, ".ex5"), role = "daily" }), knownFiles = Array.Empty<object>(), legacyFiles = Array.Empty<object>() });
    }

    public string Home() => Path.Combine(State, Hash(Encoding.UTF8.GetBytes(Path.GetFullPath(Data).ToUpperInvariant())));
    public void Known(string path, string content, bool legacy = false)
    {
        var json = JsonNode.Parse(Manifest)!;
        var entry = JsonSerializer.SerializeToNode(new { path, sha256 = Hash(Encoding.UTF8.GetBytes(content)), bytes = Encoding.UTF8.GetByteCount(content), version = "old" })!;
        json["knownFiles"]!.AsArray().Add(entry.DeepClone());
        if (legacy)
            json["legacyFiles"]!.AsArray().Add(entry.DeepClone());
        Manifest = Encoding.UTF8.GetBytes(json.ToJsonString());
    }

    public string SeedPending(string path, string? before, string after, string? priorReceipt = null)
    {
        var home = Home();
        var backup = Path.Combine(home, "runs", "pending", "backups", "file.bak");
        Directory.CreateDirectory(Path.GetDirectoryName(backup)!);
        if (before is not null)
            File.WriteAllText(backup, before);
        Write(path, after);
        var j = new
        {
            target = Path.GetFullPath(Data).ToUpperInvariant(),
            receiptPath = Path.Combine(home, "receipt.json"),
            previousReceipt = priorReceipt,
            phase = "mutating",
            run = Path.GetDirectoryName(Path.GetDirectoryName(backup)),
            files = new[]
            {
                new
                {
                    path,
                    beforeHash = before is null ? null : Hash(Encoding.UTF8.GetBytes(before)),
                    afterHash = Hash(Encoding.UTF8.GetBytes(after)),
                    backup,
                    afterFile = (string? )null,
                    status = "written"
                }
            }
        };
        File.WriteAllText(Path.Combine(home, "journal.json"), JsonSerializer.Serialize(j));
        return backup;
    }

    public string SeedInterrupted(string status, string content)
    {
        var home = Home();
        var backup = Path.Combine(home, "runs", "interrupted", "backups", "file.bak");
        Directory.CreateDirectory(Path.GetDirectoryName(backup)!);
        File.WriteAllText(backup, "original");
        Write(Source, content);
        var j = new
        {
            target = Path.GetFullPath(Data).ToUpperInvariant(),
            receiptPath = Path.Combine(home, "receipt.json"),
            previousReceipt = (string? )null,
            phase = "mutating",
            run = Path.GetDirectoryName(Path.GetDirectoryName(backup)),
            files = new[]
            {
                new
                {
                    path = Source,
                    beforeHash = Hash(Encoding.UTF8.GetBytes("original")),
                    afterHash = Hash(Encoding.UTF8.GetBytes("interrupted")),
                    backup,
                    afterFile = (string? )null,
                    status
                }
            }
        };
        File.WriteAllText(Path.Combine(home, "journal.json"), JsonSerializer.Serialize(j));
        return backup;
    }

    public InstallerService Service() => new(Zip, Manifest, State, Platform);
    public void Write(string p, string s)
    {
        var path = Path.Combine(Data, p);
        Directory.CreateDirectory(Path.GetDirectoryName(path)!);
        File.WriteAllText(path, s);
    }

    public string Snapshot() => string.Join("\n", Directory.GetFiles(Data, "*", SearchOption.AllDirectories).Order().Select(p => Path.GetRelativePath(Data, p) + ":" + Hash(File.ReadAllBytes(p))));
    public static string Hash(byte[] b) => Convert.ToHexString(SHA256.HashData(b)).ToLowerInvariant();
    public void Dispose()
    {
        try
        {
            Directory.Delete(Root, true);
        }
        catch
        {
        }
    }
}
