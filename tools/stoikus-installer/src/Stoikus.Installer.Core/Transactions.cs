using System.Diagnostics;
using System.IO.Compression;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using System.Text.RegularExpressions;

namespace Stoikus.Installer.Core;
public sealed partial class InstallerService
{
    Dictionary<string, FileIdentity> CaptureApprovedIdentities(TerminalTarget target, InstallAction action, string[] selected, Receipt? receipt)
    {
        var identities = new Dictionary<string, FileIdentity>(StringComparer.OrdinalIgnoreCase);
        var paths = action == InstallAction.Remove ? receipt!.Files.Select(f => f.Path) : DesiredPaths().Concat(selected);
        foreach (var path in paths.Distinct(StringComparer.OrdinalIgnoreCase))
        {
            var disk = TargetPath(target, path);
            if (Directory.Exists(disk))
                throw new InvalidDataException("Diretório ocupa arquivo: " + path);
            var hash = FileHash(disk);
            long? bytes = hash is null ? null : new FileInfo(disk).Length;
            var prior = receipt?.Files.FirstOrDefault(f => Eq(f.Path, path));
            if (selected.Contains(path, StringComparer.OrdinalIgnoreCase))
            {
                if (hash is null || !payload.LegacyFiles.Any(f => Eq(f.Path, path) && Eq(f.Sha256, hash) && f.Bytes == bytes))
                    throw new InvalidDataException("Legado selecionado não corresponde à identidade oficial: " + path);
            }
            else if (hash is not null && (prior is not null ? !Eq(prior.InstalledHash, hash) : !Known(path, hash, bytes!.Value)))
                throw new InvalidDataException("Identidade do arquivo não autorizada: " + path);
            identities.Add(path, new(path, hash, bytes));
        }

        return identities;
    }

    void RequireIdentity(TerminalTarget target, FileIdentity accepted)
    {
        var disk = TargetPath(target, accepted.Path);
        var hash = FileHash(disk);
        if (Directory.Exists(disk) || !Eq(hash, accepted.Hash) || (accepted.Bytes is not null && (!File.Exists(disk) || new FileInfo(disk).Length != accepted.Bytes)))
            throw new InvalidDataException("Arquivo mudou desde a identidade aprovada: " + accepted.Path);
    }

    static bool Expected(Exception e) => e is IOException or UnauthorizedAccessException or InvalidDataException or ArgumentException or JsonException or NotSupportedException or System.ComponentModel.Win32Exception or InvalidOperationException or TimeoutException;
    IEnumerable<string> DesiredPaths() => contents.Keys.Where(p => p.StartsWith("MQL5/", StringComparison.Ordinal)).Concat(payload.Programs.Select(p => p.Output));
    bool Known(string path, string hash, long bytes) => payload.KnownFiles.Any(f => Eq(f.Path, path) && Eq(f.Sha256, hash) && f.Bytes == bytes);
    static bool Eq(string? a, string? b) => string.Equals(a, b, StringComparison.OrdinalIgnoreCase);
    internal static string Hash(byte[] b) => Convert.ToHexString(SHA256.HashData(b)).ToLowerInvariant();
    static string? FileHash(string p)
    {
        CheckLinks(p);
        if (!File.Exists(p))
            return null;
        using var stream = File.OpenRead(p);
        return Convert.ToHexString(SHA256.HashData(stream)).ToLowerInvariant();
    }

    static string Canonical(string p) => Path.GetFullPath(p).TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar).ToUpperInvariant();
    string Home(TerminalTarget t) => Path.Combine(stateRoot, Hash(Encoding.UTF8.GetBytes(Canonical(t.DataDirectory))));
    string TargetPath(TerminalTarget t, string path)
    {
        ValidatePath(path);
        return SafePath(t.DataDirectory, path);
    }

    static string SafePath(string root, string relative)
    {
        var full = Path.GetFullPath(Path.Combine(root, relative.Replace('/', Path.DirectorySeparatorChar)));
        if (!full.StartsWith(Path.GetFullPath(root).TrimEnd(Path.DirectorySeparatorChar) + Path.DirectorySeparatorChar, OperatingSystem.IsWindows() ? StringComparison.OrdinalIgnoreCase : StringComparison.Ordinal))
            throw new InvalidDataException("Caminho escapou da raiz.");
        CheckLinks(full);
        return full;
    }

    static void ValidatePath(string path, bool guide = false)
    {
        if (guide && path == "LEIA_PRIMEIRO.md")
            return;
        if (string.IsNullOrWhiteSpace(path) || path.Contains('\\') || path.Contains(':') || path.StartsWith('/') || path.Split('/').Any(s => s is "" or "." or ".." || s.TrimEnd('.', ' ') != s || s.Any(char.IsControl)) || !Regex.IsMatch(path, @"^MQL5/(Experts|Indicators|Scripts|Images|Include)/JPWealth/.+", RegexOptions.CultureInvariant))
            throw new InvalidDataException("Caminho fora do escopo: " + path);
    }

    static void CheckLinks(string path)
    {
        for (string? p = Path.GetFullPath(path); p is not null; p = Path.GetDirectoryName(p))
        {
            if ((File.Exists(p) || Directory.Exists(p)) && (File.GetAttributes(p) & FileAttributes.ReparsePoint) != 0)
                throw new InvalidDataException("Link/reparse point não permitido: " + p);
        }
    }

    static void ValidateTarget(TerminalTarget t)
    {
        CheckLinks(t.DataDirectory);
        CheckLinks(t.TerminalExe);
        CheckLinks(t.MetaEditorExe);
        if (!File.Exists(t.TerminalExe) || !File.Exists(t.MetaEditorExe) || !Directory.Exists(Path.Combine(t.DataDirectory, "MQL5")))
            throw new InvalidDataException("Terminal, MetaEditor ou pasta MQL5 ausente.");
        if (!Eq(Path.GetFileName(t.TerminalExe), "terminal64.exe") || !Eq(Path.GetFileName(t.MetaEditorExe), "metaeditor64.exe") || !Eq(Canonical(Path.GetDirectoryName(t.TerminalExe)!), Canonical(Path.GetDirectoryName(t.MetaEditorExe)!)))
            throw new InvalidDataException("Executáveis não correspondem à instalação.");
        var installation = Canonical(Path.GetDirectoryName(t.TerminalExe)!);
        if (t.Portable)
        {
            if (!Eq(installation, Canonical(t.DataDirectory)))
                throw new InvalidDataException("Modo portátil exige pasta de dados junto ao terminal.");
        }
        else
        {
            var origin = Path.Combine(t.DataDirectory, "origin.txt");
            CheckLinks(origin);
            if (!File.Exists(origin) || !Eq(Canonical(File.ReadAllText(origin).Trim().Trim('\uFEFF')), installation))
                throw new InvalidDataException("origin.txt não associa a pasta ao terminal selecionado.");
        }
    }

    void EnsureStateOutsideTarget(TerminalTarget t)
    {
        var data = Canonical(t.DataDirectory);
        var state = Canonical(stateRoot);
        if (state == data || state.StartsWith(data + Path.DirectorySeparatorChar, StringComparison.Ordinal))
            throw new InvalidDataException("Estado e backups devem ficar fora da pasta do terminal.");
        if (OperatingSystem.IsWindows() && stateRoot.StartsWith(@"\\", StringComparison.Ordinal))
            throw new InvalidDataException("Stage deve residir em disco local.");
        CheckLinks(stateRoot);
    }

    Receipt? ReadReceipt(TerminalTarget t)
    {
        var p = Path.Combine(Home(t), "receipt.json");
        CheckLinks(p);
        return File.Exists(p) ? JsonSerializer.Deserialize<Receipt>(File.ReadAllBytes(p), Json) ?? throw new InvalidDataException("Recibo inválido.") : null;
    }

    void ValidateReceipt(TerminalTarget t, Receipt r)
    {
        if (!Eq(r.Target, Canonical(t.DataDirectory)))
            throw new InvalidDataException("Recibo pertence a outro terminal.");
        var paths = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
        foreach (var f in r.Files)
        {
            ValidatePath(f.Path);
            if (!paths.Add(f.Path))
                throw new InvalidDataException("Recibo duplicado.");
            if (f.Backup is not null)
                ValidateStateFile(t, f.Backup);
        }
    }

    void ValidateStateFile(TerminalTarget t, string path)
    {
        var home = Path.GetFullPath(Home(t)) + Path.DirectorySeparatorChar;
        if (!Path.GetFullPath(path).StartsWith(home, OperatingSystem.IsWindows() ? StringComparison.OrdinalIgnoreCase : StringComparison.Ordinal))
            throw new InvalidDataException("Backup fora do estado do terminal.");
        CheckLinks(path);
    }

    static void ValidateBackup(string? path, string hash)
    {
        if (path is null || !Eq(FileHash(path), hash))
            throw new InvalidDataException("Backup/arquivo de origem ausente ou adulterado.");
    }

    static void CopyDurable(string source, string dest)
    {
        CheckLinks(source);
        CheckLinks(dest);
        using var input = File.OpenRead(source);
        using var output = new FileStream(dest, FileMode.CreateNew, FileAccess.Write, FileShare.None);
        input.CopyTo(output);
        output.Flush(true);
    }

    sealed class PinnedFiles(List<FileStream> streams) : IDisposable
    {
        public void Dispose()
        {
            foreach (var stream in streams)
                stream.Dispose();
        }
    }

    static IDisposable OpenPinnedFiles(IReadOnlyDictionary<string, string> pins)
    {
        var streams = new List<FileStream>();
        try
        {
            foreach (var (path, expected) in pins)
            {
                CheckLinks(path);
                var stream = new FileStream(path, FileMode.Open, FileAccess.Read, FileShare.Read);
                streams.Add(stream);
                var actual = Convert.ToHexString(SHA256.HashData(stream)).ToLowerInvariant();
                if (!Eq(actual, expected))
                    throw new InvalidDataException("Arquivo preparado mudou de identidade: " + path);
            }
            return new PinnedFiles(streams);
        }
        catch
        {
            foreach (var stream in streams)
                stream.Dispose();
            throw;
        }
    }

    static void AtomicCopy(string source, string destination, string? expectedHash = null, Action? beforePublish = null)
    {
        Directory.CreateDirectory(Path.GetDirectoryName(destination)!);
        CheckLinks(destination);
        var temp = destination + ".stoikus-" + Guid.NewGuid().ToString("N") + ".tmp";
        try
        {
            CopyDurable(source, temp);
            // Verify the actual temporary bytes, closing the source-hash/copy gap.
            // Recheck destination ownership after copying, immediately before publish.
            using var publication = new FileStream(temp, FileMode.Open, FileAccess.Read, FileShare.Read | FileShare.Delete);
            if (expectedHash is not null && !Eq(Convert.ToHexString(SHA256.HashData(publication)).ToLowerInvariant(), expectedHash))
                throw new InvalidDataException("Cópia temporária não corresponde aos bytes aprovados.");
            beforePublish?.Invoke();
            CheckLinks(destination);
            File.Move(temp, destination, true);
        }
        finally
        {
            if (File.Exists(temp))
                File.Delete(temp);
        }
    }

    static void AtomicJson(string path, object value) => AtomicBytes(path, JsonSerializer.SerializeToUtf8Bytes(value, Json));
    static void AtomicBytes(string path, byte[] value)
    {
        CheckLinks(path);
        Directory.CreateDirectory(Path.GetDirectoryName(path)!);
        var temp = path + "." + Guid.NewGuid().ToString("N") + ".tmp";
        try
        {
            using (var s = new FileStream(temp, FileMode.CreateNew, FileAccess.Write, FileShare.None))
            {
                s.Write(value);
                s.Flush(true);
            }

            File.Move(temp, path, true);
        }
        finally
        {
            if (File.Exists(temp))
                File.Delete(temp);
        }
    }

    static void SaveJournal(string home, Journal j) => AtomicJson(Path.Combine(home, "journal.json"), j);
    Journal? ReadPendingRecovery(TerminalTarget target)
    {
        var home = Home(target);
        var file = Path.Combine(home, "journal.json");
        CheckLinks(file);
        if (!File.Exists(file))
            return null;
        var journal = JsonSerializer.Deserialize<Journal>(File.ReadAllBytes(file), Json) ?? throw new InvalidDataException("Diário inválido.");
        if (!Eq(journal.Target, Canonical(target.DataDirectory)) || !Eq(journal.ReceiptPath, Path.Combine(home, "receipt.json")))
            throw new InvalidDataException("Diário não corresponde ao terminal selecionado.");
        ValidateStateFile(target, journal.Run);
        if (!new[]
        {
            "planned",
            "mutating",
            "manual-recovery",
            "committed",
            "rolled-back"
        }.Contains(journal.Phase))
            throw new InvalidDataException("Fase do diário desconhecida.");
        var paths = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
        if (journal.Files is null)
            throw new InvalidDataException("Diário sem lista de arquivos.");
        foreach (var row in journal.Files)
        {
            ValidatePath(row.Path);
            if (!paths.Add(row.Path))
                throw new InvalidDataException("Diário com caminho duplicado.");
            ValidateStateFile(target, row.Backup);
            if (row.AfterFile is not null)
                ValidateStateFile(target, row.AfterFile);
            if (!new[]
            {
                "planned",
                "backed-up",
                "writing",
                "written",
                "restoring",
                "restored"
            }.Contains(row.Status))
                throw new InvalidDataException("Transição do diário desconhecida.");
            foreach (var hash in new[]
            {
                row.BeforeHash,
                row.AfterHash
            }

            )
                if (hash is not null && !Regex.IsMatch(hash, "^[a-fA-F0-9]{64}$"))
                    throw new InvalidDataException("Hash do diário inválido.");
        }

        if (journal.PreviousReceipt is not null)
        {
            try
            {
                var previous = JsonSerializer.Deserialize<Receipt>(Convert.FromBase64String(journal.PreviousReceipt), Json) ?? throw new InvalidDataException("Recibo anterior inválido.");
                if (previous.Files is null)
                    throw new InvalidDataException("Recibo anterior sem arquivos.");
                ValidateReceipt(target, previous);
            }
            catch (FormatException error)
            {
                throw new InvalidDataException("Recibo anterior inválido.", error);
            }
        }

        return journal.Phase is "committed" or "rolled-back" ? null : journal;
    }

    PreflightResult InspectRecovery(TerminalTarget target, Journal? journal)
    {
        var problems = new List<string>();
        var changes = new List<FileChange>();
        if (journal is null)
            return new(false, ["Não há operação interrompida para recuperar."], [], []);
        foreach (var row in journal.Files)
        {
            try
            {
                var destination = TargetPath(target, row.Path);
                if (Directory.Exists(destination))
                    throw new InvalidDataException("Diretório ocupa arquivo: " + row.Path);
                var actual = FileHash(destination);
                if (row.Status is not ("writing" or "written" or "restoring"))
                {
                    changes.Add(new(row.Path, "preservar", "Sem gravação pendente para este arquivo; bytes atuais serão preservados."));
                    continue;
                }

                if (Eq(actual, row.BeforeHash))
                {
                    changes.Add(new(row.Path, "preservar", "Arquivo já corresponde ao estado anterior da operação."));
                    continue;
                }

                if (!Eq(actual, row.AfterHash))
                    throw new InvalidDataException("Arquivo modificado protegido; recuperação manual: " + row.Path);
                if (row.BeforeHash is not null)
                    ValidateBackup(row.Backup, row.BeforeHash);
                changes.Add(new(row.Path, row.BeforeHash is null ? "remover criado" : "restaurar backup", "Identidade conferida pelo diário; apenas os bytes da operação serão revertidos."));
            }
            catch (Exception error)when (Expected(error))
            {
                problems.Add(error.Message);
            }
        }

        return new(problems.Count == 0, problems, changes, []);
    }

    void Rollback(TerminalTarget t, string home, Journal j)
    {
        if (!Eq(j.Target, Canonical(t.DataDirectory)) || !Eq(j.ReceiptPath, Path.Combine(home, "receipt.json")))
            throw new InvalidDataException("Diário não corresponde ao terminal.");
        var conflicts = new List<string>();
        foreach (var row in j.Files.AsEnumerable().Reverse())
        {
            ValidatePath(row.Path);
            ValidateStateFile(t, row.Backup);
            if (row.Status is not ("writing" or "written" or "restoring"))
                continue;
            var destination = TargetPath(t, row.Path);
            var actual = FileHash(destination);
            if (Eq(actual, row.BeforeHash))
            {
                row.Status = "restored";
                SaveJournal(home, j);
                continue;
            }

            if (!Eq(actual, row.AfterHash))
            {
                conflicts.Add(row.Path);
                continue;
            }

            row.Status = "restoring";
            SaveJournal(home, j);
            if (row.BeforeHash is null)
            {
                if (File.Exists(destination))
                    File.Delete(destination);
            }
            else
            {
                ValidateBackup(row.Backup, row.BeforeHash);
                AtomicCopy(row.Backup, destination);
            }

            row.Status = "restored";
            SaveJournal(home, j);
        }

        if (conflicts.Count > 0)
        {
            j.Phase = "manual-recovery";
            SaveJournal(home, j);
            throw new InvalidDataException("Arquivos alterados preservados: " + string.Join(", ", conflicts));
        }

        if (j.PreviousReceipt is null)
        {
            if (File.Exists(j.ReceiptPath))
                File.Delete(j.ReceiptPath);
        }
        else
            AtomicBytes(j.ReceiptPath, Convert.FromBase64String(j.PreviousReceipt));
        j.Phase = "rolled-back";
        SaveJournal(home, j);
    }
}
