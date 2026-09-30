#!/usr/bin/env python3
"""Build deterministic MT5 archives from the one JPW leverage manifest.

Only files explicitly listed in the manifest enter an archive. The compiled
archive additionally requires a recorded native artifact with matching SHA-256
and a successful compilation state; an unverified .ex5 is never distributed.
"""
from __future__ import annotations

from io import BytesIO
from pathlib import Path, PurePosixPath
import hashlib
import json
import os
import re
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PRODUCT = "mt5/jpw-alavancagem-atual/"
OUTPUT = "downloads/jpw-alavancagem-atual/"
MANIFEST_PATH = OUTPUT + "manifest.json"
COMPILED_ARTIFACT = PRODUCT + "MQL5/Indicators/JPWealth/JPW_Alavancagem_Atual.ex5"
ZIP_DATE = (1980, 1, 1, 0, 0, 0)
VERSION_HEADER = PRODUCT + "MQL5/Include/JPWealth/JPW_Alavancagem_Version.mqh"
BUILD_MACRO = re.compile(rb'(?m)^#define JPW_BUILD_ID[ \t]+"[^"\r\n]*"[ \t]*$')


def checked_file(root: Path, relative: str, prefix: str) -> Path:
    if not isinstance(relative, str) or not relative.startswith(prefix):
        raise ValueError(f"Caminho fora da area autorizada: {relative!r}")
    parts = PurePosixPath(relative).parts
    if not parts or any(part in (".", "..") for part in parts) or relative != PurePosixPath(relative).as_posix():
        raise ValueError(f"Caminho invalido: {relative!r}")
    path = root / relative
    if path.is_symlink() or not path.is_file() or path.resolve() != root.resolve() / relative:
        raise FileNotFoundError(f"Arquivo declarado ausente ou inseguro: {relative}")
    return path


def write_changed(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_symlink():
        raise ValueError(f"Saida por link simbolico recusada: {path}")
    if path.is_file() and path.read_bytes() == content:
        return
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix=".jpw-leverage-", delete=False) as temporary:
        temporary.write(content)
        temporary_path = Path(temporary.name)
    try:
        temporary_path.chmod(0o644)
        os.replace(temporary_path, path)
    finally:
        temporary_path.unlink(missing_ok=True)


def make_archive(members: list[tuple[str, bytes]]) -> bytes:
    data = BytesIO()
    with zipfile.ZipFile(data, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, content in sorted(members):
            info = zipfile.ZipInfo(name, ZIP_DATE)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, content, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    return data.getvalue()


def download_record(relative: str, content: bytes) -> dict:
    return {
        "available": True,
        "path": relative,
        "filename": PurePosixPath(relative).name,
        "sha256": hashlib.sha256(content).hexdigest(),
        "bytes": len(content),
    }


def stamp_source_build(root: Path, sources: list[str], product_version: str) -> str:
    """Bind the runtime build to declared MQL bytes, with only its own ID masked.

    Financial/schema versions are not generated. The complete final header is
    subsequently covered by mqlSourceFingerprint and the native compiler receipt.
    """
    if VERSION_HEADER not in sources:
        raise ValueError("Cabecalho de versao ausente do manifesto")
    inputs = []
    version_content = b""
    for relative in sorted(sources):
        if PurePosixPath(relative).suffix not in (".mq5", ".mqh"):
            continue
        content = checked_file(root, relative, PRODUCT).read_bytes()
        if relative == VERSION_HEADER:
            version_content = content
            if len(BUILD_MACRO.findall(content)) != 1:
                raise ValueError("JPW_BUILD_ID ausente ou duplicado")
            versions = re.findall(rb'(?m)^#define JPW_PRODUCT_VERSION[ \t]+"([^"]+)"[ \t]*$', content)
            if versions != [product_version.encode("ascii")]:
                raise ValueError("Versao do produto diverge do manifesto")
            content = BUILD_MACRO.sub(b'#define JPW_BUILD_ID "NORMALIZED"', content)
        inputs.append(relative.encode() + b"\0" + hashlib.sha256(content).hexdigest().encode() + b"\n")
    build_id = hashlib.sha256(b"".join(inputs)).hexdigest()
    stamped = BUILD_MACRO.sub(b'#define JPW_BUILD_ID "' + build_id.encode() + b'"', version_content)
    write_changed(root / VERSION_HEADER, stamped)
    return build_id


def build(root: Path = ROOT) -> dict:
    manifest_file = checked_file(root, MANIFEST_PATH, OUTPUT)
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    if manifest.get("schemaVersion") != 1 or not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", str(manifest.get("version", ""))):
        raise ValueError("Manifesto de alavancagem sem schema ou versao valida")
    sources = manifest.get("sourceFiles")
    if not isinstance(sources, list) or len(sources) < 4 or len(sources) != len(set(sources)):
        raise ValueError("Lista de fontes incompleta ou duplicada")
    required = (
        PRODUCT + "README.md",
        PRODUCT + "AGENTS.md",
        PRODUCT + "MQL5/Indicators/JPWealth/JPW_Alavancagem_Atual.mq5",
        PRODUCT + "MQL5/Include/JPWealth/JPW_Alavancagem_Core.mqh",
        PRODUCT + "MQL5/Scripts/JPWealth/JPW_Alavancagem_Tests.mq5",
        PRODUCT + "MQL5/Include/JPWealth/JPW_Alavancagem_Terminal.mqh",
        PRODUCT + "MQL5/Include/JPWealth/JPW_Alavancagem_Profile.mqh",
        PRODUCT + "MQL5/Scripts/JPWealth/JPW_Alavancagem_Verificar_USC.mq5",
        PRODUCT + "MQL5/Scripts/JPWealth/JPW_Alavancagem_Profile_Tests.mq5",
        PRODUCT + "MQL5/Include/JPWealth/JPW_Alavancagem_Genesis_Core.mqh",
        PRODUCT + "MQL5/Include/JPWealth/JPW_Alavancagem_Genesis_Store.mqh",
        PRODUCT + "MQL5/Scripts/JPWealth/JPW_Alavancagem_Genesis_Tests.mq5",
        PRODUCT + "MQL5/Scripts/JPWealth/JPW_Alavancagem_Genesis_Store_Tests.mq5",
        PRODUCT + "MQL5/Include/JPWealth/JPW_Alavancagem_RaizN_Core.mqh",
        PRODUCT + "MQL5/Include/JPWealth/JPW_Alavancagem_RaizN_Store.mqh",
        PRODUCT + "MQL5/Scripts/JPWealth/JPW_Alavancagem_RaizN_Tests.mq5",
        PRODUCT + "MQL5/Scripts/JPWealth/JPW_Alavancagem_RaizN_Store_Tests.mq5",
        PRODUCT + "MQL5/Include/JPWealth/JPW_Alavancagem_RaizN_Config.mqh",
        PRODUCT + "MQL5/Include/JPWealth/JPW_Alavancagem_RaizN_Live.mqh",
        PRODUCT + "MQL5/Include/JPWealth/JPW_Alavancagem_RaizN_Horizon.mqh",
        PRODUCT + "MQL5/Include/JPWealth/JPW_Alavancagem_RaizN_Factor.mqh",
        PRODUCT + "MQL5/Include/JPWealth/JPW_Alavancagem_RaizN_Observer.mqh",
        PRODUCT + "MQL5/Include/JPWealth/JPW_Alavancagem_Panel.mqh",
        PRODUCT + "MQL5/Include/JPWealth/JPW_Alavancagem_Cockpit.mqh",
        PRODUCT + "MQL5/Include/JPWealth/JPW_Alavancagem_StopRisk_Core.mqh",
        PRODUCT + "MQL5/Include/JPWealth/JPW_Alavancagem_StopRisk_Store.mqh",
        PRODUCT + "MQL5/Include/JPWealth/JPW_Alavancagem_StopRisk_Terminal.mqh",
        PRODUCT + "MQL5/Include/JPWealth/JPW_Alavancagem_Observer_Presence.mqh",
        PRODUCT + "MQL5/Experts/JPWealth/JPW_Alavancagem_Observer.mq5",
        PRODUCT + "MQL5/Scripts/JPWealth/JPW_Alavancagem_RaizN_Config_Tests.mq5",
        PRODUCT + "MQL5/Scripts/JPWealth/JPW_Alavancagem_RaizN_Live_Tests.mq5",
        PRODUCT + "MQL5/Scripts/JPWealth/JPW_Alavancagem_RaizN_Horizon_Tests.mq5",
        PRODUCT + "MQL5/Scripts/JPWealth/JPW_Alavancagem_RaizN_Factor_Tests.mq5",
        PRODUCT + "MQL5/Scripts/JPWealth/JPW_Alavancagem_Observer_Tests.mq5",
        PRODUCT + "MQL5/Scripts/JPWealth/JPW_Alavancagem_Panel_Tests.mq5",
        PRODUCT + "MQL5/Scripts/JPWealth/JPW_Alavancagem_StopRisk_Tests.mq5",
        PRODUCT + "MQL5/Scripts/JPWealth/JPW_Alavancagem_Diagnostics_Tests.mq5",
    )
    if not set(required).issubset(sources):
        raise ValueError("Fontes, include, teste ou instrucoes ausentes do manifesto")
    validation = manifest.get("validation")
    if not isinstance(validation, dict) or any(
        not isinstance(validation.get(kind), dict)
        or validation[kind].get("status") not in ("pending", "passed")
        or not isinstance(validation[kind].get("detail"), str)
        for kind in ("mathematics", "compilation", "terminal")
    ):
        raise ValueError("Estados de validacao incompletos")
    # Validate all declared paths/types before updating even the generated ID.
    for relative in sources:
        if PurePosixPath(relative).suffix not in (".md", ".mq5", ".mqh"):
            raise ValueError(f"Tipo de fonte inesperado: {relative}")
        source = checked_file(root, relative, PRODUCT)
        if source.suffix in (".mq5", ".mqh"):
            source_text = source.read_text(encoding="utf-8")
            # MQL resolves quoted includes relative to the including source.
            # The dependency must itself be explicitly mapped in the manifest;
            # neither a missing file nor an undeclared local file can ship.
            for include in re.findall(r'^\s*#include\s*"([^"\r\n]+)"', source_text, re.MULTILINE):
                dependency = PurePosixPath(relative).parent.as_posix() + "/" + include.replace("\\", "/")
                if dependency not in sources:
                    raise ValueError(f"Include local ausente do manifesto: {include}")
                checked_file(root, dependency, PRODUCT)
            for include in re.findall(r'^\s*#include\s*<JPWealth/([^>]+)>', source_text, re.MULTILINE):
                dependency = PRODUCT + "MQL5/Include/JPWealth/" + include
                if dependency not in sources:
                    raise ValueError(f"Include JPWealth ausente do manifesto: {include}")
    manifest["runtimeBuildId"] = stamp_source_build(root, sources, manifest["version"])
    members = []
    for relative in sources:
        if PurePosixPath(relative).suffix not in (".md", ".mq5", ".mqh"):
            raise ValueError(f"Tipo de fonte inesperado: {relative}")
        source = checked_file(root, relative, PRODUCT)
        members.append((relative.removeprefix(PRODUCT), source.read_bytes()))
    manifest["sourceHashes"] = {name: hashlib.sha256(content).hexdigest() for name, content in sorted(members)}
    mql_hashes = {name: value for name, value in manifest["sourceHashes"].items() if name.endswith((".mq5", ".mqh"))}
    source_fingerprint = hashlib.sha256(json.dumps(mql_hashes, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    manifest["mqlSourceFingerprint"] = source_fingerprint
    version = manifest["version"]
    source_path = OUTPUT + f"JPW_Alavancagem_Atual_Fontes_v{version}.zip"
    source_zip = make_archive(members)
    downloads = {"source": download_record(source_path, source_zip)}

    native = manifest.get("nativeArtifact")
    expected_ex5 = [relative[:-4] + ".ex5" for relative in sources if relative.endswith(".mq5")]
    if native is None:
        if validation["compilation"]["status"] == "passed":
            raise ValueError("Compilacao marcada como concluida sem artefato nativo")
        if any((root / relative).exists() for relative in expected_ex5):
            raise ValueError(".ex5 encontrado sem evidencia nativa; nao distribuir")
        if (root / (OUTPUT + f"JPW_Alavancagem_Atual_Compilado_v{version}.zip")).exists():
            raise ValueError("Pacote compilado sem evidencia nativa; revisar antes do build")
        downloads["compiled"] = {
            "available": False, "path": None, "filename": None, "sha256": None,
            "bytes": None, "reason": validation["compilation"]["detail"],
        }
    else:
        if validation["compilation"]["status"] != "passed" or not isinstance(native, dict):
            raise ValueError("Artefato nativo exige compilacao comprovada")
        if native.get("sourceFingerprint") != source_fingerprint or native.get("cpu") != "X64 Regular":
            raise ValueError("Artefatos nativos nao correspondem aos fontes ou a arquitetura Regular")
        artifacts = native.get("artifacts")
        if not isinstance(artifacts, list) or sorted(a.get("path", "") for a in artifacts) != sorted(expected_ex5):
            raise ValueError("Pacote nativo deve conter indicador e todos os scripts declarados")
        if not native.get("compiler") or not native.get("evidence"):
            raise ValueError("Artefato nativo sem compilador e evidencia identificados")
        native_members = [("README.md", checked_file(root, required[0], PRODUCT).read_bytes())]
        for record in artifacts:
            artifact = checked_file(root, record["path"], PRODUCT)
            ex5 = artifact.read_bytes()
            if len(ex5) < 1024 or not re.fullmatch(r"[0-9a-f]{64}", str(record.get("sha256", ""))) or hashlib.sha256(ex5).hexdigest() != record["sha256"]:
                raise ValueError("Artefato nativo vazio ou diferente da evidencia")
            native_members.append((record["path"].removeprefix(PRODUCT), ex5))
        compiled_path = OUTPUT + f"JPW_Alavancagem_Atual_Compilado_v{version}.zip"
        compiled_zip = make_archive(native_members)
        downloads["compiled"] = download_record(compiled_path, compiled_zip)

    manifest["downloads"] = downloads
    write_changed(root / source_path, source_zip)
    if native is not None:
        write_changed(root / compiled_path, compiled_zip)
    write_changed(manifest_file, (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
    return manifest


if __name__ == "__main__":
    generated = build()
    print(generated["downloads"]["source"]["path"])
    if generated["downloads"]["compiled"]["available"]:
        print(generated["downloads"]["compiled"]["path"])
