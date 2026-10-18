namespace Stoikus.Installer.Core;
public enum InstallAction
{
    Install,
    Repair,
    Remove,
    Recover
}

public sealed record TerminalTarget(string TerminalExe, string DataDirectory, string MetaEditorExe, bool Portable);
public sealed record FileChange(string RelativePath, string Kind, string Detail, bool CanOrganize = false);
public sealed record PreflightResult(bool CanProceed, IReadOnlyList<string> Problems, IReadOnlyList<FileChange> Changes, IReadOnlyList<FileChange> LegacyCandidates);
public sealed record InstallProgress(string Stage, string Message, int Completed, int Total);
public sealed record OperationResult(bool Success, string Message, string ReceiptPath, string ReportPath);
public sealed record CompileRequest(string Editor, string Source, string Include, string Log, TimeSpan Timeout);
public interface IInstallerPlatform
{
    bool IsProcessRunning(string executable);
    Task<int> CompileAsync(CompileRequest request, CancellationToken cancellationToken);
}
