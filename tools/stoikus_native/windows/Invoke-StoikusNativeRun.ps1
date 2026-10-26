#Requires -Version 5.1
# Stoikus native cycle agent. Runs inside the interactive session of the lab user
# (scheduled task created by tools/stoikus_native_runner.py), never in the SSH session:
# NativeKit.Core validates local paths through WMI, which the SSH logon cannot reach.
#
# Contract: docs/architecture/STOIKUS-NATIVE-CYCLE.md. Writes only under C:\MT5Lab\runs\<RunId>.
# The golden terminal is copied, never started or written; no orders, no login.
param(
    [Parameter(Mandatory = $true)][ValidatePattern('^[A-Za-z0-9_-]{1,64}$')][string]$RunId,
    [ValidateSet('compile', 'tests', 'all')][string]$Scope = 'all'
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$Lab = 'C:\MT5Lab'
$Golden = Join-Path $Lab 'golden'
$Run = Join-Path $Lab ('runs\' + $RunId)
$Inbox = Join-Path $Run 'inbox'
$Work = Join-Path $Run 'work'
$Terminal = Join-Path $Run 'terminal'
$Results = Join-Path $Run 'results'
$PinnedCoreSha256 = '2dba568c184e31f1e28814c706d3e6a9459fe4e45524e33b52db14c0776ed542'
$CompileTimeoutMs = 240000
$TestTimeoutMs = 300000

$receipt = [ordered]@{
    schema = 'JPW_STOIKUS_NATIVE_AGENT_RECEIPT_V1'; run_id = $RunId; scope = $Scope
    started_utc = [DateTime]::UtcNow.ToString('o'); finished_utc = $null
    agent_sha256 = (Get-FileHash -LiteralPath $PSCommandPath -Algorithm SHA256).Hash.ToLowerInvariant()
    core_sha256 = $null; environment = $null; payload = $null; standard_includes = @()
    golden = [ordered]@{ before_sha256 = $null; after_sha256 = $null; files = $null }
    compile = @(); tests = @(); error = $null
}

function Get-TreeFingerprint([string]$Root) {
    # Content fingerprint of a directory tree: sorted relative path + SHA-256 of every file.
    $rows = Get-ChildItem -LiteralPath $Root -Recurse -File -Force | Sort-Object FullName | ForEach-Object {
        $_.FullName.Substring($Root.Length).TrimStart('\') + "`t" + (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
    }
    $bytes = [Text.Encoding]::UTF8.GetBytes(($rows -join "`n"))
    $sha = [Security.Cryptography.SHA256]::Create()
    try { return [pscustomobject]@{ sha256 = ([BitConverter]::ToString($sha.ComputeHash($bytes))).Replace('-', '').ToLowerInvariant(); files = @($rows).Count } }
    finally { $sha.Dispose() }
}

function Get-OwnLabProcesses {
    # Only processes of this session started from C:\MT5Lab; the owner's daily MT5 is never touched.
    $session = (Get-Process -Id $PID).SessionId
    @(Get-CimInstance Win32_Process -Filter "Name='terminal64.exe' OR Name='metaeditor64.exe' OR Name='MetaEditor64.exe'" |
        Where-Object { $_.SessionId -eq $session -and $_.ExecutablePath -and $_.ExecutablePath.StartsWith($Lab + '\', [StringComparison]::OrdinalIgnoreCase) })
}

function Read-NewLines([hashtable]$Before, [string]$Directory) {
    # Lines appended to the *.log files of a directory since the $Before line counts.
    $lines = New-Object Collections.Generic.List[string]
    if (-not (Test-Path -LiteralPath $Directory)) { return $lines }
    foreach ($file in Get-ChildItem -LiteralPath $Directory -Filter '*.log' -File | Sort-Object Name) {
        $content = @(Get-Content -LiteralPath $file.FullName -Encoding Unicode)
        $skip = 0
        if ($Before.ContainsKey($file.Name)) { $skip = $Before[$file.Name] }
        for ($i = $skip; $i -lt $content.Count; $i++) { $lines.Add($content[$i]) }
    }
    return $lines
}

function Get-LineCounts([string]$Directory) {
    $counts = @{}
    if (Test-Path -LiteralPath $Directory) {
        foreach ($file in Get-ChildItem -LiteralPath $Directory -Filter '*.log' -File) {
            $counts[$file.Name] = @(Get-Content -LiteralPath $file.FullName -Encoding Unicode).Count
        }
    }
    return $counts
}

function Write-Utf8([string]$Path, [string]$Text) {
    [IO.File]::WriteAllText($Path, $Text, (New-Object Text.UTF8Encoding($false)))
}

function Get-Sha256([string]$Path) { (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant() }

# A used or unprepared run is left exactly as it is: no receipt, no zip, no done.json.
# This keeps a stray re-trigger of the task from overwriting earlier evidence.
if (-not (Test-Path -LiteralPath $Inbox -PathType Container)) { exit 2 }
foreach ($used in $Work, $Terminal, $Results, (Join-Path $Run 'results.zip'), (Join-Path $Run 'done.json')) {
    if (Test-Path -LiteralPath $used) { exit 3 }
}

try {
    $corePath = Join-Path $PSScriptRoot 'NativeKit.Core.ps1'
    $receipt.core_sha256 = Get-Sha256 $corePath
    if ($receipt.core_sha256 -ne $PinnedCoreSha256) { throw 'NativeKit.Core.ps1 differs from the sealed kit pin.' }
    . $corePath

    if (@(Get-OwnLabProcesses).Count -gt 0) { throw 'A lab MetaEditor or terminal is already running in this session.' }
    foreach ($required in "$Golden\terminal64.exe", "$Golden\MetaEditor64.exe", "$Golden\MQL5\Include\Object.mqh") {
        if (-not (Test-Path -LiteralPath $required -PathType Leaf)) { throw "Golden terminal incomplete: $required" }
    }
    $before = Get-TreeFingerprint $Golden
    $receipt.golden.before_sha256 = $before.sha256
    $receipt.golden.files = $before.files

    $identity = Get-Content -LiteralPath (Join-Path $Inbox 'identity.json') -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($identity.kind -cne 'JPW_STOIKUS_NATIVE_CYCLE_IDENTITY') { throw 'Unexpected identity kind.' }
    $payload = Open-ValidatedPayload (Join-Path $Inbox 'payload.zip') $identity
    try {
        New-Item -ItemType Directory -Path $Work | Out-Null
        Expand-ValidatedPayload $payload (Join-Path $Work 'stage')
        $receipt.payload = [ordered]@{ zip_sha256 = $payload.zip_sha256; entries = @($payload.entries).Count; inflate_bytes = $payload.inflate_bytes; validation = 'PASS' }
    } finally { $payload.archive.Dispose(); $payload.stream.Dispose() }
    $stageMql5 = Join-Path $Work 'stage\MQL5'
    $records = New-Object Collections.Generic.List[object]
    Copy-StandardClosure $stageMql5 (Join-Path $Golden 'MQL5') @($identity.programs) $records
    $receipt.standard_includes = @($records | ForEach-Object { [ordered]@{ path = $_.relative_path; sha256 = $_.copied_sha256 } })

    # Every tool runs from this run's own copy, so the golden stays unwritten.
    & robocopy $Golden $Terminal /E /COPY:DAT /R:1 /W:1 /NFL /NDL /NJH /NJS /NP | Out-Null
    if ($LASTEXITCODE -ge 8) { throw "robocopy of the golden terminal failed with code $LASTEXITCODE" }
    $metaEditor = Join-Path $Terminal 'MetaEditor64.exe'
    $terminalExe = Join-Path $Terminal 'terminal64.exe'
    $receipt.environment = [ordered]@{
        os = [Environment]::OSVersion.VersionString; powershell = $PSVersionTable.PSVersion.ToString()
        user = [Security.Principal.WindowsIdentity]::GetCurrent().Name; session_id = (Get-Process -Id $PID).SessionId
        metaeditor = Get-ExecutableIdentity $metaEditor; terminal = Get-ExecutableIdentity $terminalExe
    }

    $compileResults = Join-Path $Results 'compile'
    New-Item -ItemType Directory -Force -Path $compileResults | Out-Null
    $compiled = @{}
    foreach ($program in @($identity.programs)) {
        $source = Get-PathUnderRoot (Join-Path $Work 'stage') ($program.Replace('/', '\'))
        $name = [IO.Path]::GetFileNameWithoutExtension($source)
        $log = [IO.Path]::ChangeExtension($source, '.log')
        $ex5 = [IO.Path]::ChangeExtension($source, '.ex5')
        $started = [DateTime]::UtcNow
        $process = Start-Process -FilePath $metaEditor -ArgumentList ('/compile:"' + $source + '"'), ('/include:"' + $stageMql5 + '"'), '/log' -WorkingDirectory $Terminal -WindowStyle Hidden -PassThru
        $recordedStart = $process.StartTime.ToUniversalTime()
        $exited = $process.WaitForExit($CompileTimeoutMs)
        $timeoutAction = $null
        if (-not $exited) { $timeoutAction = Stop-OwnedCompiler $process $metaEditor $recordedStart }
        $logResult = $null
        if (Test-Path -LiteralPath $log -PathType Leaf) { $logResult = Test-CompileLog ([IO.File]::ReadAllText($log)) $source }
        $fresh = (Test-Path -LiteralPath $ex5 -PathType Leaf) -and ([IO.File]::GetLastWriteTimeUtc($ex5) -ge $started)
        $saved = Save-CompilerOutputs $log $ex5 $compileResults (-not $exited)
        if (-not $exited) { $status = 'TIMEOUT' }
        elseif ($logResult -and $logResult.accepted -and $fresh -and $saved.ex5.sha256) { $status = 'COMPILED' }
        else { $status = 'FAILED' }
        $compiled[$program] = ($status -eq 'COMPILED')
        $exitCode = $null
        if ($exited) { $exitCode = $process.ExitCode }
        $logRelative = $null
        if ($saved.log.result_path) { $logRelative = 'compile/' + [IO.Path]::GetFileName($saved.log.result_path) }
        $receipt.compile += [ordered]@{
            path = $program; source_sha256 = Get-Sha256 $source; status = $status; exit_code = $exitCode
            timeout_action = $timeoutAction; log = $logRelative; log_sha256 = $saved.log.sha256
            log_result = $(if ($logResult) { [ordered]@{ accepted = $logResult.accepted; reason = $logResult.reason; errors = $logResult.errors; warnings = $logResult.warnings; elapsed_ms = $logResult.elapsed_ms; cpu = $logResult.compiler_cpu_label } } else { $null })
            ex5_sha256 = $(if ($status -eq 'COMPILED') { $saved.ex5.sha256 } else { $null })
            ex5_bytes = $(if ($status -eq 'COMPILED') { $saved.ex5.captured_bytes } else { $null })
        }
    }

    if ($Scope -ne 'compile') {
        $testResults = Join-Path $Results 'tests'
        New-Item -ItemType Directory -Force -Path $testResults | Out-Null
        $scripts = Join-Path $Terminal 'MQL5\Scripts\JPWealth'
        New-Item -ItemType Directory -Force -Path $scripts | Out-Null
        $expertsDir = Join-Path $Terminal 'MQL5\Logs'
        $journalDir = Join-Path $Terminal 'logs'
        foreach ($test in @($identity.tests)) {
            $name = [IO.Path]::GetFileNameWithoutExtension($test)
            if (-not $compiled[$test]) { $receipt.tests += [ordered]@{ script = $name; status = 'SKIPPED'; reason = 'not compiled' }; continue }
            $ex5 = Get-PathUnderRoot (Join-Path $Work 'stage') ([IO.Path]::ChangeExtension($test, '.ex5').Replace('/', '\'))
            Copy-Item -LiteralPath $ex5 -Destination (Join-Path $scripts ($name + '.ex5')) -Force
            $ini = Join-Path $Work ($name + '.ini')
            [IO.File]::WriteAllText($ini, "[StartUp]`r`nSymbol=EURUSD`r`nPeriod=H1`r`nScript=JPWealth\$name`r`nShutdownTerminal=1`r`n", [Text.Encoding]::Unicode)
            $expertsBefore = Get-LineCounts $expertsDir
            $journalBefore = Get-LineCounts $journalDir
            $started = Get-Date
            $process = Start-Process -FilePath $terminalExe -ArgumentList '/portable', ('/config:"' + $ini + '"') -WorkingDirectory $Terminal -PassThru
            $exited = $process.WaitForExit($TestTimeoutMs)
            if (-not $exited) {
                $null = $process.CloseMainWindow()
                if (-not $process.WaitForExit(20000)) { Stop-Process -Id $process.Id -Force }
            }
            $excerpt = Join-Path $testResults ($name + '.log')
            $journal = Join-Path $testResults ($name + '.journal.log')
            Write-Utf8 $excerpt ((Read-NewLines $expertsBefore $expertsDir) -join "`n")
            Write-Utf8 $journal ((Read-NewLines $journalBefore $journalDir) -join "`n")
            $receipt.tests += [ordered]@{
                script = $name; status = $(if ($exited) { 'RAN' } else { 'TIMEOUT' })
                exit_code = $(if ($exited) { $process.ExitCode } else { $null })
                duration_seconds = [math]::Round(((Get-Date) - $started).TotalSeconds, 1)
                excerpt = 'tests/' + $name + '.log'; excerpt_sha256 = Get-Sha256 $excerpt
                journal = 'tests/' + $name + '.journal.log'; journal_sha256 = Get-Sha256 $journal
            }
        }
    }
    $after = Get-TreeFingerprint $Golden
    $receipt.golden.after_sha256 = $after.sha256
} catch {
    $receipt.error = $_.Exception.Message + ' | ' + $_.InvocationInfo.PositionMessage
} finally {
    foreach ($leftover in @(Get-OwnLabProcesses)) {
        if ($leftover.ExecutablePath.StartsWith($Run + '\', [StringComparison]::OrdinalIgnoreCase)) { Stop-Process -Id $leftover.ProcessId -Force -ErrorAction SilentlyContinue }
    }
    $receipt.finished_utc = [DateTime]::UtcNow.ToString('o')
    New-Item -ItemType Directory -Force -Path $Results | Out-Null
    Write-Utf8 (Join-Path $Results 'agent-receipt.json') ($receipt | ConvertTo-Json -Depth 8)
    # Zip with forward-slash entry names; the Mac refuses backslashes, absolute paths and '..'.
    Add-Type -AssemblyName System.IO.Compression, System.IO.Compression.FileSystem
    $zipPath = Join-Path $Run 'results.zip'
    $zipStream = [IO.File]::Open($zipPath, [IO.FileMode]::CreateNew)
    try {
        $archive = New-Object IO.Compression.ZipArchive($zipStream, [IO.Compression.ZipArchiveMode]::Create)
        try {
            foreach ($file in Get-ChildItem -LiteralPath $Results -Recurse -File) {
                $entry = $file.FullName.Substring($Results.Length + 1).Replace('\', '/')
                [IO.Compression.ZipFileExtensions]::CreateEntryFromFile($archive, $file.FullName, $entry) | Out-Null
            }
        } finally { $archive.Dispose() }
    } finally { $zipStream.Dispose() }
    $done = [ordered]@{ results = ($zipPath.Replace('\', '/')); sha256 = Get-Sha256 $zipPath; error = $receipt.error }
    $temporary = Join-Path $Run 'done.json.tmp'
    Write-Utf8 $temporary ($done | ConvertTo-Json -Compress)
    Move-Item -LiteralPath $temporary -Destination (Join-Path $Run 'done.json')
}
