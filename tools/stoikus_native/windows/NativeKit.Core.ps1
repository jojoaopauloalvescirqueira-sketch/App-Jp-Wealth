#Requires -Version 5.1
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem

function Get-BytesSha256([byte[]]$Bytes) {
    $h=[Security.Cryptography.SHA256]::Create()
    try { return ([BitConverter]::ToString($h.ComputeHash($Bytes))).Replace('-','').ToLowerInvariant() }
    finally { $h.Dispose() }
}
function Assert-SafeRelativePath([string]$Name) {
    if ([string]::IsNullOrWhiteSpace($Name) -or $Name.Length -gt 240 -or $Name.Contains('\') -or $Name.StartsWith('/') -or $Name.EndsWith('/')) { throw "Unsafe ZIP path: $Name" }
    if ($Name -ne $Name.Normalize([Text.NormalizationForm]::FormC)) { throw "Noncanonical ZIP path: $Name" }
    foreach($part in $Name.Split('/')) {
        if ($part -in @('','.','..') -or $part -match '[\x00-\x1f<>:"|?*]' -or $part.EndsWith('.') -or $part.EndsWith(' ')) { throw "Unsafe ZIP component: $Name" }
        if ($part -match '^(?i:CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\.|$)') { throw "Windows reserved ZIP component: $Name" }
    }
    return $Name
}
function Get-PathUnderRoot([string]$Root,[string]$Relative) {
    $base=[IO.Path]::GetFullPath($Root)
    $prefix=$base.TrimEnd([char]'\')+'\'
    $full=[IO.Path]::GetFullPath([IO.Path]::Combine($base,$Relative))
    if (-not $full.StartsWith($prefix,[StringComparison]::OrdinalIgnoreCase)) { throw "Path escapes selected root: $Relative" }
    return $full
}
function Assert-LocalDriveAnchor($Anchor) {
    if($Anchor.drive_kind -notin @('Fixed','Removable') -or $Anchor.logical_count -ne 1 -or $Anchor.logical_type -notin @(2,3) -or -not [string]::IsNullOrEmpty($Anchor.provider_name)){throw 'Network/unknown/mapped logical drive is not accepted.'}
    if($Anchor.volume_count -ne 1 -or $Anchor.volume_type -notin @(2,3) -or $Anchor.volume_type -ne $Anchor.logical_type -or $Anchor.volume_letter -ine $Anchor.logical_letter){throw 'Drive does not bind directly to one local volume; mapped/substituted drives are refused.'}
    if($Anchor.volume_device_id -notmatch '^\\\\\?\\Volume\{[0-9a-fA-F-]{36}\}\\$'){throw 'A canonical local-volume identity is required.'}
}
function Assert-LocalWindowsPath([string]$Path) {
    $full=[IO.Path]::GetFullPath($Path)
    if($full -notmatch '^[A-Za-z]:\\'){throw 'Choose a local Windows path; UNC/network paths are not used by this kit.'}
    $drive=[IO.DriveInfo]::new([IO.Path]::GetPathRoot($full))
    if($drive.DriveType -notin @([IO.DriveType]::Fixed,[IO.DriveType]::Removable)){throw 'Network/unknown drive is not used by this kit.'}
    $letter=$drive.Name.Substring(0,2)
    $logical=@(Get-CimInstance Win32_LogicalDisk -Filter ("DeviceID='"+$letter+"'") -OperationTimeoutSec 5 -ErrorAction Stop)
    $volumes=@(Get-CimInstance Win32_Volume -Filter ("DriveLetter='"+$letter+"'") -OperationTimeoutSec 5 -ErrorAction Stop)
    $logicalType=0;$provider='UNKNOWN';$volumeType=0;$volumeLetter='UNKNOWN';$volumeId='UNKNOWN'
    if($logical.Count -eq 1){$logicalType=$logical[0].DriveType;$provider=[string]$logical[0].ProviderName}
    if($volumes.Count -eq 1){$volumeType=$volumes[0].DriveType;$volumeLetter=[string]$volumes[0].DriveLetter;$volumeId=[string]$volumes[0].DeviceID}
    Assert-LocalDriveAnchor ([pscustomobject]@{path_root=$drive.Name;drive_kind=$drive.DriveType.ToString();logical_count=$logical.Count;logical_letter=$letter;logical_type=$logicalType;provider_name=$provider;volume_count=$volumes.Count;volume_letter=$volumeLetter;volume_type=$volumeType;volume_device_id=$volumeId})
}
function Assert-NoReparsePath([string]$Path) {
    $current=[IO.Path]::GetFullPath($Path)
    while ($current) {
        if (Test-Path -LiteralPath $current) {
            $item=Get-Item -LiteralPath $current -Force
            if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw "Reparse path not accepted: $current" }
        }
        $parent=[IO.Path]::GetDirectoryName($current.TrimEnd([char]'\'))
        if ($parent -eq $current) { break }
        $current=$parent
    }
}
function Assert-SafeLocalTree([string]$Path,[switch]$RequireExisting) {
    Assert-LocalWindowsPath $Path
    Assert-NoReparsePath $Path
    if($RequireExisting -and -not [IO.Directory]::Exists($Path)){throw 'Existing regular local directory required.'}
}
function New-IsolatedRunDirectory([string]$TempParent) {
    # Validate caller-supplied parent, never change TEMP or create a missing parent.
    Assert-SafeLocalTree $TempParent -RequireExisting
    $run=Get-PathUnderRoot $TempParent ('JPW_STOIKUS_NATIVE_1_22_2_'+[guid]::NewGuid().ToString('N'))
    if(Test-Path -LiteralPath $run){throw 'Fresh staging GUID already exists.'}
    $created=$false
    try{
        [IO.Directory]::CreateDirectory($run)|Out-Null;$created=$true
        Assert-SafeLocalTree $run -RequireExisting
        $results=Get-PathUnderRoot $run 'results'
        [IO.Directory]::CreateDirectory($results)|Out-Null
        Assert-SafeLocalTree $results -RequireExisting
        return [pscustomobject]@{run_root=$run;results_dir=$results}
    }catch{
        $_.Exception.Data['candidate_run_root']=$run
        $_.Exception.Data['stage_created']=$created
        throw
    }
}
function Assert-FlatResultsDirectory([string]$Path) {
    Assert-SafeLocalTree $Path -RequireExisting
    foreach($item in Get-ChildItem -LiteralPath $Path -Force){
        if($item.PSIsContainer -or ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0){throw 'Result bundle may contain only regular files, never nested/reparse entries.'}
    }
}
function Get-BoundedEntryHash($Entry,[long]$ExpectedBytes) {
    if ($ExpectedBytes -lt 0 -or $ExpectedBytes -gt 8MB) { throw 'Entry inflate cap exceeded.' }
    $stream=$Entry.Open()
    $h=[Security.Cryptography.SHA256]::Create()
    $buffer=New-Object byte[] 81920
    [long]$counted=0
    try {
        while (($read=$stream.Read($buffer,0,$buffer.Length)) -gt 0) {
            $counted+=$read
            if ($counted -gt $ExpectedBytes -or $counted -gt 8MB) { throw 'Actual entry inflate cap/declared size exceeded.' }
            $null=$h.TransformBlock($buffer,0,$read,$buffer,0)
        }
        $null=$h.TransformFinalBlock([byte[]]@(),0,0)
        if ($counted -ne $ExpectedBytes) { throw 'Actual entry size differs from frozen inventory.' }
        return ([BitConverter]::ToString($h.Hash)).Replace('-','').ToLowerInvariant()
    } finally { $h.Dispose();$stream.Dispose() }
}
function Open-ValidatedPayload([string]$ZipPath,$Identity) {
    $fs=$null;$archive=$null
    try {
        Assert-LocalWindowsPath $ZipPath
        Assert-NoReparsePath $ZipPath
        $fs=[IO.File]::Open($ZipPath,[IO.FileMode]::Open,[IO.FileAccess]::Read,[IO.FileShare]::Read)
        if ($fs.Length -gt 16MB -or $fs.Length -ne [long]$Identity.zip.bytes) { throw 'ZIP size does not match freeze or exceeds 16 MiB.' }
        $h=[Security.Cryptography.SHA256]::Create()
        try { $zipHash=([BitConverter]::ToString($h.ComputeHash($fs))).Replace('-','').ToLowerInvariant() } finally { $h.Dispose() }
        if ($zipHash -ne [string]$Identity.zip.sha256) { throw 'ZIP SHA-256 differs from root freeze.' }
        $fs.Position=0
        $archive=[IO.Compression.ZipArchive]::new($fs,[IO.Compression.ZipArchiveMode]::Read,$true)
        $expected=[Collections.Generic.Dictionary[string,object]]::new([StringComparer]::OrdinalIgnoreCase)
        foreach($entry in @($Identity.entries)) {
            $name=Assert-SafeRelativePath ([string]$entry.path)
            if ($expected.ContainsKey($name) -or [string]$entry.sha256 -notmatch '^[a-f0-9]{64}$' -or [long]$entry.bytes -lt 0) { throw 'Invalid or duplicate frozen entry inventory.' }
            $expected.Add($name,$entry)
        }
        if ($archive.Entries.Count -eq 0 -or $archive.Entries.Count -gt 512 -or $archive.Entries.Count -ne $expected.Count) { throw 'ZIP entry count differs from frozen inventory or exceeds cap.' }
        $seen=[Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
        $records=[Collections.Generic.List[object]]::new()
        [long]$total=0
        foreach($e in $archive.Entries) {
            $name=Assert-SafeRelativePath $e.FullName
            if (-not $seen.Add($name)) { throw "Duplicate ZIP entry for Windows: $name" }
            $attrs=[BitConverter]::ToUInt32([BitConverter]::GetBytes([int]$e.ExternalAttributes),0)
            $kind=($attrs -shr 16) -band 0xF000
            if ($kind -notin @(0,0x8000) -or ($attrs -band 0x400) -ne 0) { throw "Symlink/reparse/nonregular ZIP entry: $name" }
            if ([IO.Path]::GetExtension($name) -in @('.ex5','.ex4','.log','.exe','.dll','.ps1','.bat','.cmd','.lnk')) { throw "Prior compiled/executable artifact forbidden in source ZIP: $name" }
            if ($name -match '^(?i:MQL5/Files)(?:/|$)') { throw 'MQL5/Files is forbidden in this compile-only kit.' }
            if (-not $expected.ContainsKey($name)) { throw "Unfrozen ZIP entry: $name" }
            if ($e.Length -gt 8MB -or $e.Length -ne [long]$expected[$name].bytes) { throw "Entry inflate size mismatch/cap: $name" }
            $total+=$e.Length
            if ($total -gt 64MB) { throw 'Total ZIP inflate cap exceeds 64 MiB.' }
            if ($e.Length -gt 0 -and ($e.CompressedLength -le 0 -or ($e.Length/[double]$e.CompressedLength) -gt 1000)) { throw "ZIP inflate ratio exceeds 1000:1: $name" }
            $actualHash=Get-BoundedEntryHash $e $e.Length
            if ($actualHash -ne [string]$expected[$name].sha256) { throw "Frozen entry SHA-256 mismatch: $name" }
            $records.Add([pscustomobject]@{path=$name;bytes=$e.Length;compressed_bytes=$e.CompressedLength;sha256=$actualHash})
        }
        foreach($name in $seen) {
            $parent=$name
            while($parent.Contains('/')) {
                $parent=$parent.Substring(0,$parent.LastIndexOf('/'))
                if($seen.Contains($parent)){throw "ZIP file/ancestor collision: $name"}
            }
        }
        return [pscustomobject]@{archive=$archive;stream=$fs;zip_sha256=$zipHash;entries=$records.ToArray();inflate_bytes=$total}
    } catch {
        if($archive){$archive.Dispose()}
        if($fs){$fs.Dispose()}
        throw
    }
}
function Expand-ValidatedPayload($Payload,[string]$Destination) {
    if (Test-Path -LiteralPath $Destination) { throw 'Staging destination must not exist before extraction.' }
    Assert-SafeLocalTree ([IO.Path]::GetDirectoryName($Destination)) -RequireExisting
    [IO.Directory]::CreateDirectory($Destination) | Out-Null
    Assert-SafeLocalTree $Destination -RequireExisting
    foreach($e in $Payload.archive.Entries) {
        $target=Get-PathUnderRoot $Destination $e.FullName.Replace('/','\')
        [IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($target)) | Out-Null
        $source=$e.Open()
        $dest=[IO.File]::Open($target,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
        [long]$written=0;$buffer=New-Object byte[] 81920
        try {
            while(($read=$source.Read($buffer,0,$buffer.Length)) -gt 0){
                $written+=$read
                if($written -gt $e.Length -or $written -gt 8MB){throw 'Extraction inflate cap exceeded.'}
                $dest.Write($buffer,0,$read)
            }
            if($written -ne $e.Length){throw 'Extraction size differs from validated entry.'}
        } finally {$dest.Dispose();$source.Dispose()}
        $row=@($Payload.entries | Where-Object {$_.path -ceq $e.FullName})[0]
        if((Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash.ToLowerInvariant() -ne $row.sha256){throw 'Extracted hash differs from pre-extraction validation.'}
    }
}
function Copy-ReferencedStandard([string]$Original,[string]$SelectedInclude,[string]$StageInclude,$OriginMap,$Records) {
    $source=[IO.Path]::GetFullPath($Original)
    $base=[IO.Path]::GetFullPath($SelectedInclude).TrimEnd([char]'\')
    if(-not $source.StartsWith($base+'\',[StringComparison]::OrdinalIgnoreCase)){throw 'Standard include escapes selected Include directory.'}
    $relative=$source.Substring($base.Length+1)
    if($relative.Split('\')[0] -ieq 'JPWealth' -or [IO.Path]::GetExtension($relative) -ine '.mqh'){throw 'Only referenced standard MQH outside JPWealth may be copied.'}
    Assert-NoReparsePath $source
    if((Get-Item -LiteralPath $source).Length -gt 8MB){throw 'Standard header size cap exceeded.'}
    $before=(Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash.ToLowerInvariant()
    $dest=Get-PathUnderRoot $StageInclude $relative
    if(Test-Path -LiteralPath $dest){throw "Refusing to overwrite staged include: $relative"}
    [IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($dest)) | Out-Null
    [IO.File]::Copy($source,$dest,$false)
    $copied=(Get-FileHash -LiteralPath $dest -Algorithm SHA256).Hash.ToLowerInvariant()
    if($copied -ne $before -or (Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash.ToLowerInvariant() -ne $before){throw 'Standard source changed while being copied.'}
    $OriginMap.Add($dest,$source)
    $Records.Add([pscustomobject]@{relative_path=$relative.Replace('\','/');source_path=$source;stage_path=$dest;bytes=(Get-Item -LiteralPath $source).Length;before_sha256=$before;copied_sha256=$copied;after_sha256='NOT_CHECKED'})
    if($Records.Count -gt 512 -or ($Records | Measure-Object -Property bytes -Sum).Sum -gt 64MB){throw 'Standard dependency closure cap exceeded.'}
    return $dest
}
function Copy-StandardClosure([string]$StageMql5,[string]$SelectedMql5,[string[]]$Programs,$Records) {
    Assert-LocalWindowsPath $SelectedMql5
    if([IO.Path]::GetFileName($SelectedMql5.TrimEnd([char]'\')) -ine 'MQL5'){throw 'Select the existing terminal MQL5 directory, not a data/account directory.'}
    $selected=Join-Path $SelectedMql5 'Include'
    $stage=Join-Path $StageMql5 'Include'
    Assert-NoReparsePath $selected
    if(-not (Test-Path -LiteralPath (Join-Path $selected 'Object.mqh') -PathType Leaf)){throw 'Selected MQL5/Include does not contain standard Object.mqh.'}
    $queue=[Collections.Generic.Queue[string]]::new()
    $seen=[Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
    $origins=[Collections.Generic.Dictionary[string,string]]::new([StringComparer]::OrdinalIgnoreCase)
    foreach($program in $Programs){$queue.Enqueue((Get-PathUnderRoot $StageMql5 $program.Substring(5).Replace('/','\')))}
    while($queue.Count -gt 0){
        $file=$queue.Dequeue()
        if(-not $seen.Add($file)){continue}
        $text=[IO.File]::ReadAllText($file)
        $text=[regex]::Replace($text,'(?s)/\*.*?\*/','')
        $resourceLines=[regex]::Matches($text,'(?m)^\s*#resource\s+([^\r\n]+)')
        foreach($resourceLine in $resourceLines){
            $literal=[regex]::Match($resourceLine.Groups[1].Value,'^"([^"\r\n]+)"')
            if(-not $literal.Success){throw 'Resource reference must be a static quoted payload path.'}
            $resourceValue=$literal.Groups[1].Value.Replace('\\','\').Replace('/','\')
            if($resourceValue.Contains(':') -or $resourceValue.StartsWith('\\')){throw 'Absolute/UNC resource reference is forbidden.'}
            if($resourceValue.StartsWith('\')){$resourcePath=Get-PathUnderRoot $StageMql5 $resourceValue.TrimStart([char]'\')}
            else{
                $resourcePath=[IO.Path]::GetFullPath((Join-Path ([IO.Path]::GetDirectoryName($file)) $resourceValue))
                if(-not $resourcePath.StartsWith($StageMql5.TrimEnd([char]'\')+'\',[StringComparison]::OrdinalIgnoreCase)){throw 'Resource reference escapes payload staging.'}
            }
            if(-not (Test-Path -LiteralPath $resourcePath -PathType Leaf)){throw 'Resource must already exist in frozen payload; installed/user resources are never read.'}
        }
        $refs=[regex]::Matches($text,'(?m)^\s*#include\s*(?:<(?<angle>[^>\r\n]+)>|"(?<quote>[^"\r\n]+)")')
        foreach($ref in $refs){
            $angle=$ref.Groups['angle'].Success
            $value=$ref.Groups['angle'].Value
            if(-not $angle){$value=$ref.Groups['quote'].Value}
            if($value -match '^[\\/]' -or $value.Contains(':')){throw 'Absolute/UNC/ADS include reference is forbidden.'}
            $value=$value.Replace('/','\')
            if($angle){$candidate=Get-PathUnderRoot $stage $value}
            else{
                $candidate=[IO.Path]::GetFullPath((Join-Path ([IO.Path]::GetDirectoryName($file)) $value))
                if(-not $candidate.StartsWith($StageMql5.TrimEnd([char]'\')+'\',[StringComparison]::OrdinalIgnoreCase)){throw 'Quoted include escapes isolated MQL5 staging.'}
            }
            if(-not (Test-Path -LiteralPath $candidate -PathType Leaf)){
                if($angle){
                    if($value.Split('\')[0] -ieq 'JPWealth'){throw "Frozen JPWealth dependency missing: $value"}
                    $original=Get-PathUnderRoot $selected $value
                } elseif($origins.ContainsKey($file)){
                    $original=[IO.Path]::GetFullPath((Join-Path ([IO.Path]::GetDirectoryName($origins[$file])) $value))
                } else {throw "Frozen local include missing: $value"}
                $candidate=Copy-ReferencedStandard $original $selected $stage $origins $Records
            }
            if([IO.Path]::GetExtension($candidate) -ine '.mqh'){throw 'Non-MQH include reference rejected.'}
            $queue.Enqueue($candidate)
        }
    }
}
function Test-CompileLog([string]$Text,[string]$FullSource) {
    # Known CLI grammar from preserved historical logs, never evidence for this candidate.
    $lines=@([regex]::Split($Text.TrimStart([char]0xfeff),'\r\n|\n|\r')|ForEach-Object{$_.Trim()}|Where-Object{-not [string]::IsNullOrWhiteSpace($_)})
    $escaped=[regex]::Escape($FullSource)
    $headerPattern='(?i)^'+$escaped+'[ \t]*:[ \t]*information:[ \t]*compiling[ \t]+'+$escaped+'$'
    $summaryPattern="(?i)^Result:[ \t]*(?<errors>\d+)[ \t]+errors?,[ \t]*(?<warnings>\d+)[ \t]+warnings?,[ \t]*(?<elapsed>\d+)[ \t]+ms elapsed(?:,[ \t]*cpu='(?<cpu>[^']+)')?$"
    $headerCount=@($lines|Where-Object{[regex]::IsMatch($_,$headerPattern)}).Count
    $allHeaderCount=@($lines|Where-Object{$_ -match '(?i):[ \t]*information:[ \t]*compiling(?:[ \t]|$)'}).Count
    $resultLineCount=@($lines|Where-Object{$_ -match '(?i)^Result\b'}).Count
    $summaries=@($lines|ForEach-Object{[regex]::Match($_,$summaryPattern)}|Where-Object{$_.Success})
    $accepted=$lines.Count -ge 2 -and $lines.Count -le 50000 -and $headerCount -eq 1 -and $allHeaderCount -eq 1 -and $resultLineCount -eq 1 -and $summaries.Count -eq 1
    $reason='UNKNOWN_OR_INCOMPLETE';$errors=$null;$warnings=$null;$cpu='UNKNOWN';$elapsed=$null
    if($summaries.Count -eq 1){
        $errors=[int]$summaries[0].Groups['errors'].Value;$warnings=[int]$summaries[0].Groups['warnings'].Value;$elapsed=[long]$summaries[0].Groups['elapsed'].Value
        if($summaries[0].Groups['cpu'].Success){$cpu=$summaries[0].Groups['cpu'].Value}
        $accepted=$accepted -and $errors -eq 0 -and $warnings -eq 0
    }
    if($accepted -and (-not [regex]::IsMatch($lines[0],$headerPattern) -or -not [regex]::IsMatch($lines[-1],$summaryPattern))){$accepted=$false;$reason='OPENING_OR_TERMINAL_SUMMARY_INVALID'}
    if($accepted){
        for($i=1;$i -lt $lines.Count-1;$i++){
            $info=[regex]::Match($lines[$i],'(?i)^(?<path>.*?)[ \t]*:[ \t]*information:[ \t]*(?<message>.+)$')
            $legal=$false
            if($info.Success){
                $parent=$info.Groups['path'].Value.Trim();$message=$info.Groups['message'].Value
                $parentIsSource=$parent -ieq $FullSource
                $parentIsHeader=$parent -match '^[A-Za-z]:\\[^\r\n]*\.mqh$'
                if(($parentIsSource -or $parentIsHeader) -and $message -match '(?i)^including[ \t]+[A-Za-z]:\\[^\r\n]*\.mqh$'){$legal=$true}
                elseif($parent -match '(?i)^[A-Za-z]:\\[^\r\n]*\.(bmp|wav|png)$' -and $message -match '^resource[ \t]+''[^'']+''[ \t]+as[ \t]+resource[ \t]+"[^"]+"$'){$legal=$true}
                elseif(($parentIsSource -or $parent -eq '') -and $message -match '(?i)^(generating code(?:[ \t]+(?:[0-9]|[1-9][0-9]|100)%)?|code generated)$'){$legal=$true}
            }
            if(-not $legal){$accepted=$false;$reason='UNRECOGNIZED_OR_FOREIGN_BODY_LINE';break}
        }
    }
    if($Text -match '(?im):[ \t]*(error|warning)\b'){$accepted=$false;$reason='ERROR_OR_WARNING_DIAGNOSTIC'}
    if($accepted){$reason='COMPLETE_EXCLUSIVE_ZERO_ERROR_ZERO_WARNING_LOG'}
    return [pscustomobject]@{accepted=[bool]$accepted;reason=$reason;program_header_count=$headerCount;all_program_header_count=$allHeaderCount;summary_count=$summaries.Count;result_line_count=$resultLineCount;significant_line_count=$lines.Count;errors=$errors;warnings=$warnings;elapsed_ms=$elapsed;compiler_cpu_label=$cpu;ex5_architecture='UNKNOWN'}
}
function Save-CompilerArtifact([string]$Source,[string]$ResultsDirectory,[long]$MaxBytes,[bool]$MayStillBeWriting) {
    $record=[ordered]@{source_path=$Source;result_path=$null;status='UNREADABLE_OR_LOCKED';evidence='PARTIAL_OR_UNVERIFIED';sha256=$null;captured_bytes=0;source_bytes_snapshot=$null;source_bytes_after=$null;source_last_write_utc=$null;error=$null;source_deleted_by_kit=$false}
    $reader=$null;$writer=$null;$hash=$null;$cancel=$null;$destination=$null;$copyStarted=$false;$total=0
    try{
        Assert-SafeLocalTree ([IO.Path]::GetDirectoryName($Source)) -RequireExisting
        Assert-FlatResultsDirectory $ResultsDirectory
        if(-not [IO.File]::Exists($Source)){$record.status='ABSENT';return [pscustomobject]$record}
        Assert-NoReparsePath $Source
        $share=[IO.FileShare]::Read
        if($MayStillBeWriting){$share=[IO.FileShare]::ReadWrite -bor [IO.FileShare]::Delete}
        $reader=[IO.FileStream]::new($Source,[IO.FileMode]::Open,[IO.FileAccess]::Read,$share,81920,[IO.FileOptions]::Asynchronous)
        $record.source_bytes_snapshot=$reader.Length
        $record.source_last_write_utc=[IO.File]::GetLastWriteTimeUtc($Source).ToString('o')
        if($reader.Length -gt $MaxBytes){$record.status='SIZE_CAP_EXCEEDED';$record.error='Diagnostic snapshot exceeds cap; original staging path preserved.';return [pscustomobject]$record}
        $destination=Get-PathUnderRoot $ResultsDirectory ([IO.Path]::GetFileName($Source))
        $writer=[IO.FileStream]::new($destination,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None,81920,[IO.FileOptions]::Asynchronous)
        $copyStarted=$true;$record.result_path=$destination
        $hash=[Security.Cryptography.SHA256]::Create()
        $cancel=[Threading.CancellationTokenSource]::new()
        $clock=[Diagnostics.Stopwatch]::StartNew();$cancel.CancelAfter(10000)
        $buffer=New-Object byte[] 81920
        while($total -lt $record.source_bytes_snapshot){
            if($clock.ElapsedMilliseconds -ge 10000){throw 'DIAGNOSTIC_IO_TIMEOUT'}
            $wanted=[int][Math]::Min($buffer.Length,$record.source_bytes_snapshot-$total)
            $readTask=$reader.ReadAsync($buffer,0,$wanted,$cancel.Token)
            if(-not $readTask.Wait(1000)){$cancel.Cancel();throw 'DIAGNOSTIC_READ_TIMEOUT'}
            $read=$readTask.Result
            if($read -le 0){throw 'Diagnostic source truncated during snapshot.'}
            if($total+$read -gt $MaxBytes){throw 'Diagnostic snapshot cap exceeded during read.'}
            $writeTask=$writer.WriteAsync($buffer,0,$read,$cancel.Token)
            if(-not $writeTask.Wait(1000)){$cancel.Cancel();throw 'DIAGNOSTIC_WRITE_TIMEOUT'}
            $null=$hash.TransformBlock($buffer,0,$read,$buffer,0);$total+=$read
        }
        $flushTask=$writer.FlushAsync($cancel.Token)
        if(-not $flushTask.Wait(1000)){$cancel.Cancel();throw 'DIAGNOSTIC_FLUSH_TIMEOUT'}
        $null=$hash.TransformFinalBlock([byte[]]@(),0,0)
        $record.sha256=([BitConverter]::ToString($hash.Hash)).Replace('-','').ToLowerInvariant()
        $record.captured_bytes=$total;$record.source_bytes_after=$reader.Length
        if(-not $MayStillBeWriting -and $reader.Length -eq $record.source_bytes_snapshot){$record.status='COPIED_STABLE'}
        else{$record.status='COPIED_PARTIAL_OR_UNVERIFIED'}
    }catch{
        $record.error=$_.Exception.Message
        $record.status=if($copyStarted){'COPIED_PARTIAL_OR_UNVERIFIED'}else{'UNREADABLE_OR_LOCKED'}
        $record.captured_bytes=$total
        # Interrupted async IO cannot prove the final file bytes: preserve it and
        # record the capture error instead of mislabelling a prefix hash as SHA-256.
        $record.sha256=$null
    }finally{
        if($cancel){$cancel.Cancel()}
        if($writer){try{$writer.Dispose()}catch{}}
        if($reader){try{$reader.Dispose()}catch{}}
        if($hash){$hash.Dispose()}
        if($cancel){$cancel.Dispose()}
    }
    return [pscustomobject]$record
}
function Save-CompilerOutputs([string]$Log,[string]$Ex5,[string]$ResultsDirectory,[bool]$MayStillBeWriting) {
    # Capture is evidence collection only; it never sets a compilation verdict.
    return [pscustomobject]@{
        log=(Save-CompilerArtifact $Log $ResultsDirectory 16MB $MayStillBeWriting)
        ex5=(Save-CompilerArtifact $Ex5 $ResultsDirectory 64MB $MayStillBeWriting)
    }
}

function Get-ExecutableIdentity([string]$Path) {
    Assert-LocalWindowsPath $Path
    Assert-NoReparsePath $Path
    $file=Get-Item -LiteralPath $Path
    if($file.PSIsContainer){throw 'Executable selection is a directory.'}
    $machine='UNKNOWN'
    $b=[IO.BinaryReader]::new([IO.File]::OpenRead($file.FullName))
    try{
        if($b.ReadUInt16() -ne 0x5A4D){throw 'Selected file is not PE/MZ.'}
        $b.BaseStream.Position=0x3c;$offset=$b.ReadInt32()
        if($offset -lt 64 -or $offset+6 -gt $b.BaseStream.Length){throw 'Malformed PE offset.'}
        $b.BaseStream.Position=$offset
        if($b.ReadUInt32() -ne 0x00004550){throw 'Selected file has no PE signature.'}
        $value=$b.ReadUInt16()
        if($value -eq 0x8664){$machine='X64'}elseif($value -eq 0xAA64){$machine='ARM64'}elseif($value -eq 0x014c){$machine='X86'}
    }finally{$b.Dispose()}
    return [pscustomobject]@{path=$file.FullName;sha256=(Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash.ToLowerInvariant();bytes=$file.Length;file_version=$file.VersionInfo.FileVersion;product_version=$file.VersionInfo.ProductVersion;company=$file.VersionInfo.CompanyName;pe_machine=$machine}
}
function Assert-NoRunningMetaEditor {
    $running=@(Get-Process -Name metaeditor,metaeditor64 -ErrorAction SilentlyContinue)
    if($running.Count -gt 0){throw 'MetaEditor is already open. Save your work and close MetaEditor manually, then run this kit again. No existing process was stopped.'}
}
function Stop-OwnedCompiler($Process,[string]$Compiler,[datetime]$RecordedStart) {
    if($Process.HasExited){return 'ALREADY_EXITED'}
    try{
        $current=[Diagnostics.Process]::GetProcessById($Process.Id)
        if($current.StartTime.ToUniversalTime() -ne $RecordedStart -or $current.MainModule.FileName -ine $Compiler){return 'NOT_STOPPED_IDENTITY_UNVERIFIED'}
        $current.Kill()
        $null=$current.WaitForExit(5000)
        return 'STOPPED_OWNED_VERIFIED_PID'
    }catch{return 'NOT_STOPPED_IDENTITY_UNVERIFIED'}
}

