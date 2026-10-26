#Requires -Version 5.1
# Self-test of the Stoikus native agent with synthetic fixtures only; runs in the lab
# user's interactive session like the agent. Writes only under C:\MT5Lab\runs\<RunId>.
param([Parameter(Mandatory = $true)][ValidatePattern('^[A-Za-z0-9_-]{1,64}$')][string]$RunId)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$Lab = 'C:\MT5Lab'
$Golden = Join-Path $Lab 'golden'
$Run = Join-Path $Lab ('runs\' + $RunId)
$PinnedCoreSha256 = '2dba568c184e31f1e28814c706d3e6a9459fe4e45524e33b52db14c0776ed542'
$checks = New-Object Collections.Generic.List[object]

function Check([string]$Name, [scriptblock]$Body) {
    try { $ok = [bool](& $Body); $checks.Add([ordered]@{ name = $Name; result = $(if ($ok) { 'PASS' } else { 'FAIL' }) }) }
    catch { $checks.Add([ordered]@{ name = $Name; result = 'FAIL'; error = $_.Exception.Message }) }
}

function Write-Utf8([string]$Path, [string]$Text) { [IO.File]::WriteAllText($Path, $Text, (New-Object Text.UTF8Encoding($false))) }

# A finished self-test is never redone into the same folder (stray re-trigger of the task).
if (Test-Path -LiteralPath (Join-Path $Run 'done.json')) { exit 3 }
New-Item -ItemType Directory -Force -Path $Run | Out-Null
try {
    $corePath = Join-Path $PSScriptRoot 'NativeKit.Core.ps1'
    Check 'core matches the sealed kit pin' { (Get-FileHash -LiteralPath $corePath -Algorithm SHA256).Hash.ToLowerInvariant() -eq $PinnedCoreSha256 }
    . $corePath
    Check 'interactive session reaches WMI for local-path checks' { Assert-LocalWindowsPath $Lab; $true }
    Check 'golden terminal, MetaEditor and standard library present' {
        (Test-Path "$Golden\terminal64.exe") -and (Test-Path "$Golden\MetaEditor64.exe") -and (Test-Path "$Golden\MQL5\Include\Object.mqh") }

    $source = 'C:\MT5Lab\runs\x\work\stage\MQL5\Scripts\JPWealth\JPW_Fixture_Tests.mq5'
    $clean = @("$source : information: compiling $source",
               "$source : information: including C:\MT5Lab\runs\x\work\stage\MQL5\Include\JPWealth\JPW_Fixture.mqh",
               ' : information: generating code 100%', ' : information: code generated',
               "Result: 0 errors, 0 warnings, 1200 ms elapsed, cpu='X64 Regular'") -join "`r`n"
    Check 'compile log with 0 errors and 0 warnings is accepted' { (Test-CompileLog $clean $source).accepted }
    Check 'compile log with a warning is refused' {
        $warned = $clean.Replace(' : information: code generated', "$source(10,5) : warning 43: possible loss of data") -replace '0 warnings', '1 warnings'
        -not (Test-CompileLog $warned $source).accepted }
    Check 'compile log with an error is refused' { -not (Test-CompileLog ($clean -replace '0 errors', '1 errors') $source).accepted }
    Check 'truncated compile log is refused' { -not (Test-CompileLog "$source : information: compiling $source" $source).accepted }

    Check 'tampered payload is refused before any extraction' {
        $fixture = Join-Path $Run 'fixture'
        New-Item -ItemType Directory -Force -Path $fixture | Out-Null
        $zip = Join-Path $fixture 'payload.zip'
        Add-Type -AssemblyName System.IO.Compression, System.IO.Compression.FileSystem
        $stream = [IO.File]::Open($zip, [IO.FileMode]::Create)
        try {
            $archive = New-Object IO.Compression.ZipArchive($stream, [IO.Compression.ZipArchiveMode]::Create)
            try {
                $writer = New-Object IO.StreamWriter($archive.CreateEntry('MQL5/Scripts/JPWealth/JPW_Fixture_Tests.mq5').Open())
                try { $writer.Write('void OnStart(){}') } finally { $writer.Dispose() }
            } finally { $archive.Dispose() }
        } finally { $stream.Dispose() }
        $bytes = (Get-Item $zip).Length
        $sha = (Get-FileHash $zip -Algorithm SHA256).Hash.ToLowerInvariant()
        $path = 'MQL5/Scripts/JPWealth/JPW_Fixture_Tests.mq5'
        $real = [BitConverter]::ToString([Security.Cryptography.SHA256]::Create().ComputeHash([Text.Encoding]::UTF8.GetBytes('void OnStart(){}'))).Replace('-', '').ToLowerInvariant()
        $identity = [pscustomobject]@{ kind = 'JPW_STOIKUS_NATIVE_CYCLE_IDENTITY'; programs = @($path)
            zip = [pscustomobject]@{ bytes = $bytes; sha256 = $sha }; entries = @([pscustomobject]@{ path = $path; bytes = 16; sha256 = $real }) }
        # Positive control: the same fixture with the true entry hash is accepted.
        $payload = Open-ValidatedPayload $zip $identity; $payload.archive.Dispose(); $payload.stream.Dispose()
        # Tamper only the entry hash: the refusal must come from the entry SHA-256 check.
        $identity.entries[0].sha256 = ('0' * 64)
        $message = ''
        try { $payload = Open-ValidatedPayload $zip $identity; $payload.archive.Dispose(); $payload.stream.Dispose() } catch { $message = $_.Exception.Message }
        $message -like '*Frozen entry SHA-256 mismatch*' }
} catch {
    $checks.Add([ordered]@{ name = 'self-test harness'; result = 'FAIL'; error = $_.Exception.Message })
} finally {
    $failed = @($checks | Where-Object { $_.result -ne 'PASS' }).Count
    $done = [ordered]@{ selftest = $true; result = $(if ($failed -eq 0 -and $checks.Count -gt 0) { 'PASS' } else { 'FAIL' }); checks = $checks }
    $temporary = Join-Path $Run 'done.json.tmp'
    Write-Utf8 $temporary ($done | ConvertTo-Json -Depth 4 -Compress)
    Move-Item -LiteralPath $temporary -Destination (Join-Path $Run 'done.json')
}
