namespace Stoikus.Installer.Core;
internal sealed class Payload
{
    public int SchemaVersion { get; set; }
    public string ProductVersion { get; set; } = "";
    public string ArchiveSha256 { get; set; } = "";
    public long ArchiveBytes { get; set; }
    public List<PayloadFile> Files { get; set; } = [];
    public List<ProgramFile> Programs { get; set; } = [];
    public List<PayloadFile> KnownFiles { get; set; } = [];
    public List<PayloadFile> LegacyFiles { get; set; } = [];
}

internal sealed class PayloadFile
{
    public string Path { get; set; } = "";
    public string Sha256 { get; set; } = "";
    public long Bytes { get; set; }
}

internal sealed class ProgramFile
{
    public string Source { get; set; } = "";
    public string Output { get; set; } = "";
}

internal sealed class Receipt
{
    public string Target { get; set; } = "";
    public string ProductVersion { get; set; } = "";
    public List<OwnedFile> Files { get; set; } = [];
}

internal sealed class OwnedFile
{
    public string Path { get; set; } = "";
    public string? InstalledHash { get; set; }
    public string? OriginalHash { get; set; }
    public string? Backup { get; set; }
}

internal sealed class Journal
{
    public string Target { get; set; } = "";
    public string ReceiptPath { get; set; } = "";
    public string? PreviousReceipt { get; set; }
    public string Run { get; set; } = "";
    public string Phase { get; set; } = "";
    public List<TransactionFile> Files { get; set; } = [];
}

internal sealed class TransactionFile
{
    public string Path { get; set; } = "";
    public string? BeforeHash { get; set; }
    public long? BeforeBytes { get; set; }
    public string? AfterHash { get; set; }
    public string Backup { get; set; } = "";
    public string? AfterFile { get; set; }
    public string Status { get; set; } = "planned";
}

internal sealed record FileIdentity(string Path, string? Hash, long? Bytes);
internal sealed class CompileEvidence
{
    public string Source { get; set; } = "";
    public string SourcePath { get; set; } = "";
    public string? SourceSha256 { get; set; }
    public string Output { get; set; } = "";
    public string OutputPath { get; set; } = "";
    public string? OutputSha256 { get; set; }
    public string Log { get; set; } = "";
    public string? LogSha256 { get; set; }
    public string Editor { get; set; } = "";
    public string? EditorSha256 { get; set; }
    public string? EditorVersion { get; set; }
    public string[] Arguments { get; set; } = [];
    public object[] Dependencies { get; set; } = [];
    public DateTime Started { get; set; }
    public DateTime? Finished { get; set; }
    public double TimeoutSeconds { get; set; }
    public int? Exit { get; set; }
    public string Status { get; set; } = "";
    public string? Diagnostic { get; set; }
    public string Scope { get; set; } = "local-four";
    public string Cpu { get; set; } = "NOT_PROVEN";
    public string NativeSdk { get; set; } = "NOT_RUN";
}

internal sealed record StagedDependency(string Path, string Sha256);
