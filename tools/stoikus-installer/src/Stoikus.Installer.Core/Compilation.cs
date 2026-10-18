using System.Diagnostics;
using System.IO.Compression;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using System.Text.RegularExpressions;

namespace Stoikus.Installer.Core;
public sealed partial class InstallerService
{
    static void CaptureCompileOutputs(CompileEvidence attempt)
    {
        try
        {
            attempt.LogSha256 ??= FileHash(attempt.Log);
        }
        catch (Exception error)when (Expected(error))
        {
            attempt.Diagnostic += "\nNão foi possível conferir log: " + error.Message;
        }

        try
        {
            attempt.OutputSha256 ??= FileHash(attempt.OutputPath);
        }
        catch (Exception error)when (Expected(error))
        {
            attempt.Diagnostic += "\nNão foi possível conferir EX5: " + error.Message;
        }
    }

    StagedDependency[] StageIncludes(TerminalTarget t, string stage)
    {
        var sourceRoot = Path.Combine(t.DataDirectory, "MQL5", "Include");
        var stagedRoot = Path.Combine(stage, "MQL5", "Include");
        var visited = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
        var evidence = new List<StagedDependency>();
        var scanned = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
        void Visit(string relative)
        {
            relative = relative.Replace('\\', '/');
            if (relative.StartsWith('/') || relative.Contains(':'))
                throw new InvalidDataException("Include absoluto.");
            var source = SafePath(sourceRoot, relative);
            var canonical = Path.GetRelativePath(sourceRoot, source).Replace('\\', '/');
            if (!visited.Add(canonical))
                return;
            var dest = SafePath(stagedRoot, canonical);
            if (canonical.StartsWith("JPWealth/", StringComparison.OrdinalIgnoreCase))
            {
                if (!File.Exists(dest))
                    throw new InvalidDataException("Include JPWealth fora do payload: " + canonical);
            }
            else
            {
                if (!File.Exists(source))
                    throw new InvalidDataException("Biblioteca padrão ausente: " + canonical);
                Directory.CreateDirectory(Path.GetDirectoryName(dest)!);
                File.Copy(source, dest, false);
            }

            evidence.Add(new(canonical, FileHash(dest) ?? throw new InvalidDataException("Include preparado ausente: " + canonical)));
            Scan(dest, canonical);
        }

        void Scan(string file, string? relative)
        {
            if (!scanned.Add(Path.GetFullPath(file)))
                return;
            var code = File.ReadAllText(file);
            code = Regex.Replace(code, @"/\*[\s\S]*?\*/|//[^\r\n]*", "");
            foreach (Match m in Regex.Matches(code, @"(?m)^\s*#include\s+([^\r\n]+)"))
            {
                var directive = m.Groups[1].Value.Trim();
                var literal = Regex.Match(directive, "^[<\"]([^>\"]+)[>\"]\\s*$");
                if (!literal.Success)
                    throw new InvalidDataException("Include não literal não permitido: " + directive);
                var name = literal.Groups[1].Value.Replace('\\', '/');
                if (directive.StartsWith('<'))
                    Visit(name);
                else if (relative is not null)
                    Visit(Path.Combine(Path.GetDirectoryName(relative) ?? "", name));
                else
                {
                    var local = Path.GetFullPath(Path.Combine(Path.GetDirectoryName(file)!, name));
                    if (!local.StartsWith(Path.GetFullPath(stage) + Path.DirectorySeparatorChar, StringComparison.Ordinal) || !File.Exists(local))
                        throw new InvalidDataException("Include local ausente ou escapou do stage: " + name);
                    Scan(local, null);
                }
            }
        }

        Visit("Canvas/Canvas.mqh");
        Visit("Math/Stat/Normal.mqh");
        foreach (var p in payload.Programs)
            Scan(SafePath(stage, p.Source), null);
        foreach (var p in contents.Keys.Where(p => p.StartsWith("MQL5/Include/JPWealth/", StringComparison.OrdinalIgnoreCase)))
            Visit(p[13..]);
        return evidence.ToArray();
    }

    // The raw process exit is retained separately. A complete log must belong to
    // this exact source; a trailing success sentence alone is not build evidence.
    public static bool ValidCompileLog(byte[] bytes, string expectedSource)
    {
        if (!ValidCompileLog(bytes)) return false;
        try
        {
            string s;
            if (bytes.Length >= 2 && bytes[0] == 0xff && bytes[1] == 0xfe)
                s = new UnicodeEncoding(false, true, true).GetString(bytes, 2, bytes.Length - 2);
            else if (bytes.Length >= 2 && bytes[0] == 0xfe && bytes[1] == 0xff)
                s = new UnicodeEncoding(true, true, true).GetString(bytes, 2, bytes.Length - 2);
            else s = new UTF8Encoding(false, true).GetString(bytes).TrimStart('\uFEFF');
            var lines = s.Split(['\r', '\n'], StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries);
            string Normalize(string path) => Regex.Replace(path.Replace('\\', '/'), "/+", "/");
            var expected = Normalize(expectedSource);
            var opening = Regex.Match(lines[0], @"^(.+\.mq5) : information: compiling (.+\.mq5)$", RegexOptions.IgnoreCase);
            if (!opening.Success || !string.Equals(Normalize(opening.Groups[1].Value), expected, StringComparison.OrdinalIgnoreCase)
                || !string.Equals(Normalize(opening.Groups[2].Value), expected, StringComparison.OrdinalIgnoreCase)) return false;
            var mqlIndex = expected.LastIndexOf("/MQL5/", StringComparison.OrdinalIgnoreCase);
            if (mqlIndex < 0) return false;
            var stageRoot = expected[..(mqlIndex + "/MQL5/".Length)];
            bool SameStage(string path)
            {
                var normalized = Normalize(path);
                return normalized.StartsWith(stageRoot, StringComparison.OrdinalIgnoreCase) &&
                    !normalized.Split('/').Any(part => part is "." or "..");
            }
            var generated = false;
            foreach (var line in lines.Skip(1).Take(lines.Length - 2))
            {
                if (line.Equals(": information: code generated", StringComparison.OrdinalIgnoreCase))
                {
                    if (generated) return false;
                    generated = true; continue;
                }
                if (generated) return false;
                if (Regex.IsMatch(line, @"^: information: generating code(?: (?:[0-9]|[1-9][0-9]|100)%)?$", RegexOptions.IgnoreCase)) continue;
                var resource = Regex.Match(line, @"^(.+\.bmp) : information: resource '([^'\r\n]+\.bmp)' as resource ""(::[^""\r\n]+\.bmp)""$", RegexOptions.IgnoreCase);
                if (resource.Success)
                {
                    var bitmap = Normalize(resource.Groups[1].Value);
                    var resourceName = Normalize(resource.Groups[3].Value[2..]).TrimStart('/');
                    if (!SameStage(bitmap) || !bitmap.StartsWith(stageRoot + "Images/JPWealth/", StringComparison.OrdinalIgnoreCase)
                        || !string.Equals(bitmap.Split('/')[^1], resource.Groups[2].Value, StringComparison.OrdinalIgnoreCase)
                        || !string.Equals(bitmap[stageRoot.Length..], resourceName, StringComparison.OrdinalIgnoreCase)) return false;
                    continue;
                }
                var include = Regex.Match(line, @"^(.+\.mq[5h]) : information: including (.+\.mqh)$", RegexOptions.IgnoreCase);
                if (!include.Success || !SameStage(include.Groups[1].Value)
                    || !SameStage(include.Groups[2].Value)) return false;
            }
            return generated;
        }
        catch (DecoderFallbackException) { return false; }
    }

    public static bool ValidCompileLog(byte[] bytes)
    {
        try
        {
            string s;
            if (bytes.Length >= 2 && bytes[0] == 0xff && bytes[1] == 0xfe)
                s = new UnicodeEncoding(false, true, true).GetString(bytes, 2, bytes.Length - 2);
            else if (bytes.Length >= 2 && bytes[0] == 0xfe && bytes[1] == 0xff)
                s = new UnicodeEncoding(true, true, true).GetString(bytes, 2, bytes.Length - 2);
            else
                s = new UTF8Encoding(false, true).GetString(bytes).TrimStart('\uFEFF');
            var lines = s.Split(['\r', '\n'], StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries);
            if (lines.Length == 0 || !Regex.IsMatch(lines[^1], @"^(?:Result:\s*)?0 errors?,\s*0 warnings?(?:,\s*\d+\s+(?:msec|ms)\s+elapsed(?:,\s*cpu='[^'\r\n]+')?)?$", RegexOptions.IgnoreCase))
                return false;
            return !lines.Take(lines.Length - 1).Any(l => Regex.IsMatch(l, @"\b(?:error|warning)\b\s*(?:\d+\s*)?:", RegexOptions.IgnoreCase));
        }
        catch (DecoderFallbackException)
        {
            return false;
        }
    }
}
