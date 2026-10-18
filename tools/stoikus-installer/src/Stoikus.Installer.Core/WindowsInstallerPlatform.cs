using System.Diagnostics;

namespace Stoikus.Installer.Core;
public sealed class WindowsInstallerPlatform : IInstallerPlatform
{
    public bool IsProcessRunning(string executable)
    {
        if (!OperatingSystem.IsWindows())
            throw new PlatformNotSupportedException("Execução real do instalador exige Windows.");
        var name = Path.GetFileNameWithoutExtension(executable);
        foreach (var process in Process.GetProcessesByName(name))
        {
            using (process)
            {
                try
                {
                    var file = process.MainModule?.FileName;
                    if (file is null || string.Equals(Path.GetFullPath(file), Path.GetFullPath(executable), StringComparison.OrdinalIgnoreCase))
                        return true;
                }
                catch (System.ComponentModel.Win32Exception)
                {
                    return true;
                }
                catch (InvalidOperationException)
                {
                }
            }
        }

        return false;
    }

    public async Task<int> CompileAsync(CompileRequest request, CancellationToken cancellationToken)
    {
        if (!OperatingSystem.IsWindows())
            throw new PlatformNotSupportedException("MetaEditor nativo exige Windows.");
        var start = new ProcessStartInfo(request.Editor)
        {
            UseShellExecute = false,
            CreateNoWindow = true,
            WorkingDirectory = Path.GetDirectoryName(request.Source)!
        };
        start.ArgumentList.Add("/compile:" + request.Source);
        start.ArgumentList.Add("/include:" + request.Include);
        start.ArgumentList.Add("/log");
        var nativeLog = Path.ChangeExtension(request.Source, ".log");
        if (File.Exists(nativeLog) || File.Exists(request.Log))
            throw new InvalidDataException("Log preexistente no stage.");
        using var process = Process.Start(start) ?? throw new IOException("Falha ao iniciar MetaEditor.");
        using var timeout = new CancellationTokenSource(request.Timeout);
        using var linked = CancellationTokenSource.CreateLinkedTokenSource(cancellationToken, timeout.Token);
        try
        {
            await process.WaitForExitAsync(linked.Token);
            if (File.Exists(nativeLog))
            {
                Directory.CreateDirectory(Path.GetDirectoryName(request.Log)!);
                File.Move(nativeLog, request.Log, false);
            }

            return process.ExitCode;
        }
        catch (OperationCanceledException)
        {
            if (!process.HasExited)
                process.Kill(true);
            await process.WaitForExitAsync(CancellationToken.None);
            if (cancellationToken.IsCancellationRequested)
                throw;
            throw new TimeoutException("MetaEditor excedeu o tempo de compilação.");
        }
    }
}
