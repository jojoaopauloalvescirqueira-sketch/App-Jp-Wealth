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
DAILY_GUIDE = PRODUCT + "STOIKUS_USO_DIARIO.md"
DAILY_PROGRAMS = frozenset(PRODUCT + relative for relative in (
    "MQL5/Experts/JPWealth/JPW_Stoikus_Monitor.mq5",
    "MQL5/Indicators/JPWealth/JPW_Alavancagem_Atual.mq5",
    "MQL5/Indicators/JPWealth/JPW_NoCuda_Channels.mq5",
    "MQL5/Scripts/JPWealth/JPW_Stoikus_Abrir_Paineis.mq5",
))


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


# Sealed, approved R4 files are distribution inputs, never native proof. Only
# these three local files may enter the optional interface release contract.
INTERFACE_ARTIFACTS = {
    "nativeKit": ("Kit_Windows_Stoikus_Assinatura_R4.zip", "86b9fb52e811c953f2e142f7670327685748bf75848c0ce2bea644eaa664d474"),
    "nativePin": ("root-pin-R4.json", "009cd46d458a4a85c14a0cae0c76ea9d730b47656304d36dfb7552fb952e8932"),
    "preview": ("Previa_Stoikus_Interface_R4.html", "b1e44151cc4acf5fa96fb0bb0a349b2ecab0ca631e59649629c253adb83f70f2"),
}
INTERFACE_RELEASE_VALUES = {
    "revision": "R4", "candidate": "1.22.3-interface", "archiveVariant": "interface",
    "state": "SOURCE_ONLY_NATIVE_PENDING", "nativeCompilation": "NOT_RUN",
    "nativeRuntime": "NOT_RUN", "humanAcceptance": "NOT_RUN", "windowsX64": "NOT_RUN",
}
INTERFACE_BUILD_ID = "45beb82e9366197542bfa5c7084a28bc05dd6b155f5a3777fdaa95f15b67239d"
INTERFACE_MQL_FINGERPRINT = "b2b0afc9535816685decb8d5860a90fee35642b1ea3e6720523ecd8145c00d81"
INTERFACE_DAILY_SHA256 = "0b3d6b2ba9897a04262baf703282dfe84abdeb19ab26e39c3da21bf31e5855ef"


# Bounded approved release catalog: selecting a version never relaxes its pins.
SEALED_RELEASES = {
    ("1.22.3", "R4"): dict(values=INTERFACE_RELEASE_VALUES, artifacts=INTERFACE_ARTIFACTS,
                   build=INTERFACE_BUILD_ID, fingerprint=INTERFACE_MQL_FINGERPRINT,
                   daily=INTERFACE_DAILY_SHA256),
    ("1.23.0", "R5"): dict(
        values=dict(INTERFACE_RELEASE_VALUES, revision="R5", candidate="1.23.0-interface", archiveVariant=""),
        artifacts={
            "nativeKit": ("Kit_Windows_Stoikus_Janelas_R5.zip", "5c32d1a5bf3ff2e2023c2c0e7b29c6425d1cc1bd5169f5fdf03f277d8fc9f8f4"),
            "nativePin": ("root-pin-R5.json", "bb6ad986db99b3f9dca2437e83f9fd928f4df7830a9866da5d2b0b7bc731447a"),
            "preview": ("Previa_Stoikus_Janelas_R5.html", "90fd6a0d542ce9abb538d61f0b5b8e5470d364eae1dd47ceed4504f6b67cbfd7"),
        },
        build="c1298741ec9673c2644cfaad83e6444b06a4ae7e0a5ec78f85f2c65d2781ea31",
        fingerprint="62c9bb7d36aed866983449c4327fb529b994464cb1422bf9516c639ea4fb94ac",
        daily="0bc6c856410b576ebf0412aa341056e8e02463c8f848fe34d2bd4e983ae5f7a3",
        sdk="65ed7e2cb6f9fe680695ef67e47eb9aa873a66e2bfd214c1ebd71a41367fcf63"),
    ("1.23.0", "C5"): dict(
        values=dict(INTERFACE_RELEASE_VALUES, revision="C5", candidate="1.23.0-interface", archiveVariant="painel-C5"),
        artifacts={'nativeKit': ('Kit_Windows_Stoikus_Painel_C5_D1.zip', '92a05d3198fcae3dcbea2558f07cf13a20fbdddac63f1c8902e6dd4ac6b28983'), 'nativePin': ('root-pin-Painel-C5-D1.json', 'e0bf392d17e4a28efda316fdc13593101bbb25775be578e8b5f0abec8ef0101d'), 'preview': ('Previa_Stoikus_Painel_C5.html', '380cfe50b26dd6b438e9d5e374482406fe56b86e124e478fcafd05ebebb18afa')},
        build='406f16e7265f93dbd76f1c2b063090fa05520fdafc4322ca13ab5e0e0ae82161',
        fingerprint='26473298967abb055d077c3cc440cab1efc9f92e5e8f54f06bcc30ef2dc8f347',
        daily='0d323ea010c21e043922a318252911262ea2dbf9b4b0217d67b0b9a1fe0242b5',
        sdk='aa20c1f65f7b3dbc883eadf6babe312c8f30d9944ea787e89e686fe8aac7bbb2'),
}


def sealed_release_contract(manifest: dict):
    release = manifest.get("interfaceRelease")
    revision = release.get("revision") if isinstance(release, dict) else None
    if not isinstance(revision, str):
        return None
    return SEALED_RELEASES.get((manifest["version"], revision))


def validate_interface_release(root: Path, manifest: dict) -> str:
    """Validate the bounded sealed-input contract before any generated writes."""
    if "interfaceRelease" not in manifest:
        return ""
    release = manifest["interfaceRelease"]
    contract = sealed_release_contract(manifest)
    if contract is None:
        raise ValueError("Versao sem contrato selado")
    values, artifacts_contract = contract["values"], contract["artifacts"]
    if (not isinstance(release, dict)
            or set(release) != set(values) | {"artifacts"}
            or any(release.get(key) != value for key, value in values.items())):
        raise ValueError("Contrato interfaceRelease invalido ou estado nativo promovido")
    if (manifest.get("nativeArtifact") is not None
            or any(manifest["validation"][kind]["status"] != "pending" for kind in ("compilation", "terminal"))):
        raise ValueError("Release selada exige validacao nativa pendente")
    artifacts = release["artifacts"]
    if not isinstance(artifacts, dict) or set(artifacts) != set(artifacts_contract):
        raise ValueError("Inventario de artifacts da interface invalido")
    verified = {}
    for kind, (filename, approved_digest) in artifacts_contract.items():
        record = artifacts[kind]
        if (not isinstance(record, dict)
                or set(record) != {"available", "path", "filename", "sha256", "bytes"}
                or record.get("available") is not True
                or record.get("path") != OUTPUT + filename
                or record.get("filename") != filename
                or record.get("sha256") != approved_digest
                or type(record.get("bytes")) is not int or record["bytes"] <= 0):
            raise ValueError(f"Metadata da interface invalida: {kind}")
        raw = checked_file(root, record["path"], OUTPUT).read_bytes()
        regenerated = download_record(OUTPUT + filename, raw)
        if regenerated != record:
            raise ValueError(f"Bytes/hash da interface divergem da release aprovada: {kind}")
        verified[kind] = regenerated
    # Bind executable bytes independently of stale generated manifest metadata.
    mql_hashes = {relative.removeprefix(PRODUCT): hashlib.sha256(
        checked_file(root, relative, PRODUCT).read_bytes()).hexdigest()
        for relative in manifest["sourceFiles"] if runtime_source(relative)}
    fingerprint = hashlib.sha256(json.dumps(mql_hashes, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    if fingerprint != contract["fingerprint"]:
        raise ValueError("Fontes da interface divergem do fingerprint aprovado")
    release["artifacts"] = verified
    variant = values["archiveVariant"]
    return "_" + variant if variant else ""


NOCUDA_LOGO = PRODUCT + "MQL5/Images/JPWealth/JPW_NoCuda_Logo.bmp"
# Every embedded resource is explicitly approved; arbitrary images cannot ship.
GENETRIX_LOGOS = frozenset(PRODUCT + "MQL5/Images/JPWealth/JPW_Stoikus_Logo_" +
    theme + "_" + str(scale) + ".bmp" for theme in ("Light", "Dark")
    for scale in (100, 125, 150, 200))
EMBEDDED_RESOURCES = GENETRIX_LOGOS | {NOCUDA_LOGO}


def runtime_source(relative: str) -> bool:
    """MQL code and the single explicitly declared embedded product resource."""
    canonical = relative if relative.startswith(PRODUCT) else PRODUCT + relative
    return PurePosixPath(relative).suffix in (".mq5", ".mqh") or canonical in EMBEDDED_RESOURCES


def stamp_source_build(root: Path, sources: list[str], product_version: str) -> str:
    """Bind the runtime build to declared MQL and embedded-resource bytes, with only its own ID masked.

    Financial/schema versions are not generated. The complete final header is
    subsequently covered by mqlSourceFingerprint and the native compiler receipt.
    """
    if VERSION_HEADER not in sources:
        raise ValueError("Cabecalho de versao ausente do manifesto")
    inputs = []
    version_content = b""
    for relative in sorted(sources):
        if not runtime_source(relative):
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


# Documentation formats are allowed only for these declared harness documents.
# This does not broaden runtime resources or admit arbitrary JSON/PDF/TXT files.
HARNESS_DOCUMENTS = frozenset({
    PRODUCT + "harness/JPW_GENETRIX_MT5_ENGINEERING_HARNESS_v1.0.txt",
    PRODUCT + "harness/JPW_GENETRIX_MT5_ENGINEERING_HARNESS_v1.0.pdf",
    PRODUCT + "harness/contracts/ENG-AC01-12.json",
})


def local_dependencies(relative: str, source_text: str) -> set[str]:
    """Resolve project-local includes/resources without consulting the filesystem.

    Standard MT5 includes remain supplied by MetaEditor. Every project-local
    dependency is validated against the SDK's declared inventory by build().
    """
    dependencies = set()
    for resource in re.findall(r'^\s*#resource\s*"([^"\r\n]+)"', source_text, re.MULTILINE):
        normalized = re.sub(r"/+", "/", resource.replace("\\", "/"))
        if not normalized.startswith("/Images/") or ".." in PurePosixPath(normalized).parts:
            raise ValueError(f"Recurso local inesperado: {resource}")
        dependency = PRODUCT + "MQL5" + normalized
        if dependency not in EMBEDDED_RESOURCES:
            raise ValueError(f"Recurso local inesperado: {resource}")
        dependencies.add(dependency)
    for include in re.findall(r'^\s*#include\s*"([^"\r\n]+)"', source_text, re.MULTILINE):
        dependencies.add(PurePosixPath(relative).parent.as_posix() + "/" + include.replace("\\", "/"))
    for include in re.findall(r'^\s*#include\s*<([^>\r\n]+)>', source_text, re.MULTILINE):
        normalized = include.replace("\\", "/")
        if normalized.startswith("JPWealth/"):
            dependencies.add(PRODUCT + "MQL5/Include/" + normalized)
    return dependencies


def daily_inventory(sources: list[str], dependencies: dict[str, set[str]]) -> set[str]:
    """Close only the four authorized usage entrypoints over local dependencies."""
    if not (DAILY_PROGRAMS | {DAILY_GUIDE}).issubset(sources):
        raise ValueError("Programas de uso diario ou guia ausentes do manifesto")
    selected = set()
    pending = list(DAILY_PROGRAMS)
    while pending:
        relative = pending.pop()
        if relative in selected:
            continue
        if (relative not in DAILY_PROGRAMS
                and PurePosixPath(relative).suffix != ".mqh"
                and relative not in EMBEDDED_RESOURCES):
            raise ValueError(f"Dependencia fora do pacote de uso diario: {relative}")
        selected.add(relative)
        pending.extend(dependencies.get(relative, set()))
    return selected | {DAILY_GUIDE}



INSTALLER_FILENAME = "Stoikus_Setup_1.0.0-beta.1_win-x64.exe"
INSTALLER_RELEASE_PREFIX = "https://github.com/jojoaopauloalvescirqueira-sketch/App-Jp-Wealth/releases/download/"


def validate_installer_record(root: Path, record: dict, product_version: str) -> None:
    """Installer evidence is separate from the SDK's nativeArtifact contract."""
    if (not isinstance(record, dict) or type(record.get("available")) is not bool
            or record.get("installerVersion") != "1.0.0-beta.1"
            or record.get("productVersion") != product_version or record.get("platform") != "win-x64"
            or record.get("filename") != INSTALLER_FILENAME or record.get("unsigned") is not True):
        raise ValueError("Metadados do instalador invalidos")
    stages = record.get("nativeTests")
    if not isinstance(stages, dict) or set(stages) != {"windowsX64", "parallelsArm", "browser"}:
        raise ValueError("Estados nativos do instalador ausentes")
    if any(value not in ("PASS", "NOT_RUN", "PRODUCT_FAIL", "ENVIRONMENT_ERROR") for value in stages.values()):
        raise ValueError("Estado nativo do instalador invalido")
    if record["available"]:
        sha = record.get("sha256")
        if not re.fullmatch(r"[a-f0-9]{64}", str(sha)) or not all(value == "PASS" for value in stages.values()):
            raise ValueError("Instalador publico exige provas do mesmo EXE")
        relative = record.get("path")
        if relative != OUTPUT + INSTALLER_FILENAME:
            raise ValueError("Caminho do instalador invalido")
        raw = checked_file(root, relative, OUTPUT).read_bytes()
        if (type(record.get("bytes")) is not int or not 0 < record["bytes"] <= 9007199254740991
                or len(raw) != record["bytes"] or hashlib.sha256(raw).hexdigest() != sha):
            raise ValueError("EXE diverge dos metadados")
        url = record.get("releaseUrl")
        if not isinstance(url, str) or not re.fullmatch(re.escape(INSTALLER_RELEASE_PREFIX) + r"[A-Za-z0-9._-]+/" + re.escape(INSTALLER_FILENAME), url):
            raise ValueError("Release URL do instalador nao autorizada")
        evidence = record.get("nativeEvidence")
        if not isinstance(evidence, dict) or set(evidence) != set(stages):
            raise ValueError("Recibos nativos do instalador ausentes")
        for stage, item in evidence.items():
            if (not isinstance(item, dict) or not isinstance(item.get("path"), str)
                    or not re.fullmatch(r"docs/validation/[A-Za-z0-9_./-]+\.json", item["path"])):
                raise ValueError("Recibo nativo invalido")
            receipt_raw = checked_file(root, item.get("path"), "docs/validation/").read_bytes()
            if hashlib.sha256(receipt_raw).hexdigest() != item.get("sha256"):
                raise ValueError("Hash do recibo nativo diverge")
            receipt = json.loads(receipt_raw)
            if receipt.get("candidateSha256") != sha or receipt.get("stage") != stage or receipt.get("status") != "PASS":
                raise ValueError("Recibo nativo pertence a outro candidato ou etapa")
    else:
        if any(record.get(key) is not None for key in ("path", "releaseUrl", "sha256", "bytes", "nativeEvidence")):
            raise ValueError("Instalador indisponivel nao deve anunciar artefato publico")
        if not isinstance(record.get("reason"), str) or not record["reason"]:
            raise ValueError("Instalador indisponivel exige motivo")


def build(root: Path = ROOT, *, installer_record: dict | None = None) -> dict:
    manifest_file = checked_file(root, MANIFEST_PATH, OUTPUT)
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    if manifest.get("schemaVersion") != 1 or not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", str(manifest.get("version", ""))):
        raise ValueError("Manifesto de alavancagem sem schema ou versao valida")
    installer = installer_record if installer_record is not None else manifest.get("downloads", {}).get("installer")
    if installer is not None:
        validate_installer_record(root, installer, manifest["version"])
    sources = manifest.get("sourceFiles")
    if (not isinstance(sources, list) or len(sources) < 4
            or not all(isinstance(relative, str) for relative in sources)
            or len(sources) != len(set(sources))):
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
    dependencies = {}
    for relative in sources:
        if (PurePosixPath(relative).suffix not in (".md", ".mq5", ".mqh")
                and relative not in EMBEDDED_RESOURCES
                and relative not in HARNESS_DOCUMENTS):
            raise ValueError(f"Tipo de fonte inesperado: {relative}")
        source = checked_file(root, relative, PRODUCT)
        if source.suffix in (".mq5", ".mqh"):
            source_text = source.read_text(encoding="utf-8")
            dependencies[relative] = local_dependencies(relative, source_text)
            for dependency in dependencies[relative]:
                if dependency not in sources:
                    kind = "Recurso" if dependency in EMBEDDED_RESOURCES else "Include"
                    raise ValueError(f"{kind} local ausente do manifesto: {dependency}")
                checked_file(root, dependency, PRODUCT)
    archive_suffix = validate_interface_release(root, manifest)
    daily_sources = daily_inventory(sources, dependencies)
    manifest["runtimeBuildId"] = stamp_source_build(root, sources, manifest["version"])
    members = []
    for relative in sources:
        if (PurePosixPath(relative).suffix not in (".md", ".mq5", ".mqh")
                and relative not in EMBEDDED_RESOURCES
                and relative not in HARNESS_DOCUMENTS):
            raise ValueError(f"Tipo de fonte inesperado: {relative}")
        source = checked_file(root, relative, PRODUCT)
        members.append((relative.removeprefix(PRODUCT), source.read_bytes()))
    manifest["sourceHashes"] = {name: hashlib.sha256(content).hexdigest() for name, content in sorted(members)}
    mql_hashes = {name: value for name, value in manifest["sourceHashes"].items() if runtime_source(name)}
    source_fingerprint = hashlib.sha256(json.dumps(mql_hashes, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    manifest["mqlSourceFingerprint"] = source_fingerprint
    version = manifest["version"]
    source_path = OUTPUT + f"JPW_Stoikus_Fontes_v{version}{archive_suffix}.zip"
    source_zip = make_archive(members)
    downloads = {"source": download_record(source_path, source_zip)}
    daily_path = OUTPUT + f"JPW_Stoikus_Uso_Fontes_v{version}{archive_suffix}.zip"
    daily_members = [
        ("LEIA_PRIMEIRO.md" if relative == DAILY_GUIDE else relative.removeprefix(PRODUCT),
         checked_file(root, relative, PRODUCT).read_bytes())
        for relative in daily_sources
    ]
    daily_zip = make_archive(daily_members)
    downloads["dailySource"] = download_record(daily_path, daily_zip)
    contract = sealed_release_contract(manifest) if "interfaceRelease" in manifest else None
    if contract and (downloads["dailySource"]["sha256"] != contract["daily"]
            or manifest["runtimeBuildId"] != contract["build"]
            or ("sdk" in contract and downloads["source"]["sha256"] != contract["sdk"])):
        raise ValueError("Pacote ou build da interface diverge da release aprovada")

    native = manifest.get("nativeArtifact")
    expected_ex5 = [relative[:-4] + ".ex5" for relative in sources if relative.endswith(".mq5")]
    if native is None:
        if validation["compilation"]["status"] == "passed":
            raise ValueError("Compilacao marcada como concluida sem artefato nativo")
        if any((root / relative).exists() for relative in expected_ex5):
            raise ValueError(".ex5 encontrado sem evidencia nativa; nao distribuir")
        if (root / (OUTPUT + f"JPW_Stoikus_Compilado_v{version}.zip")).exists():
            raise ValueError("Pacote compilado sem evidencia nativa; revisar antes do build")
        if archive_suffix and (root / (OUTPUT + f"JPW_Stoikus_Compilado_v{version}{archive_suffix}.zip")).exists():
            raise ValueError("Pacote compilado da interface sem evidencia nativa")
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
        compiled_path = OUTPUT + f"JPW_Stoikus_Compilado_v{version}.zip"
        compiled_zip = make_archive(native_members)
        downloads["compiled"] = download_record(compiled_path, compiled_zip)

    if installer is not None:
        downloads["installer"] = installer
    manifest["downloads"] = downloads
    write_changed(root / source_path, source_zip)
    write_changed(root / daily_path, daily_zip)
    if native is not None:
        write_changed(root / compiled_path, compiled_zip)
    write_changed(manifest_file, (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
    return manifest


if __name__ == "__main__":
    generated = build()
    print(generated["downloads"]["dailySource"]["path"])
    print(generated["downloads"]["source"]["path"])
    if generated["downloads"]["compiled"]["available"]:
        print(generated["downloads"]["compiled"]["path"])
