#!/usr/bin/env python3
"""Check archive extraction, determinism and fail-closed native packaging."""
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
import hashlib
import json
import zipfile

from build_leverage_package import ROOT, MANIFEST_PATH, COMPILED_ARTIFACT, VERSION_HEADER, build


def main() -> None:
    template = json.loads((ROOT / MANIFEST_PATH).read_text(encoding="utf-8"))
    assert template["version"] == "1.10.1"
    assert "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_MDD.mqh" in template["sourceFiles"]
    assert "mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth/JPW_Alavancagem_Metrics_Tests.mq5" in template["sourceFiles"]
    viewer = "mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth/JPW_Alavancagem_Consultar_MDD.mq5"
    assert viewer in template["sourceFiles"]
    genesis = "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_Genesis_Core.mqh"
    genesis_store = "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_Genesis_Store.mqh"
    genesis_tests = "mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth/JPW_Alavancagem_Genesis_Tests.mq5"
    genesis_store_tests = "mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth/JPW_Alavancagem_Genesis_Store_Tests.mq5"
    assert {genesis, genesis_store, genesis_tests, genesis_store_tests} <= set(template["sourceFiles"])
    raiz = "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_RaizN_Core.mqh"
    raiz_store = "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_RaizN_Store.mqh"
    raiz_tests = "mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth/JPW_Alavancagem_RaizN_Tests.mq5"
    raiz_store_tests = "mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth/JPW_Alavancagem_RaizN_Store_Tests.mq5"
    assert {raiz, raiz_store, raiz_tests, raiz_store_tests} <= set(template["sourceFiles"])
    current = {
        "mt5/jpw-alavancagem-atual/AGENTS.md",
        "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_Cockpit.mqh",
        "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_StopRisk_Core.mqh",
        "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_StopRisk_Store.mqh",
        "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_StopRisk_Terminal.mqh",
        "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_Observer_Presence.mqh",
        "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_RaizN_Config.mqh",
        "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_RaizN_Live.mqh",
        "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_RaizN_Horizon.mqh",
        "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_RaizN_Factor.mqh",
        "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_RaizN_Observer.mqh",
        "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_Panel.mqh",
        "mt5/jpw-alavancagem-atual/MQL5/Experts/JPWealth/JPW_Alavancagem_Observer.mq5",
        "mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth/JPW_Alavancagem_RaizN_Config_Tests.mq5",
        "mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth/JPW_Alavancagem_RaizN_Live_Tests.mq5",
        "mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth/JPW_Alavancagem_RaizN_Horizon_Tests.mq5",
        "mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth/JPW_Alavancagem_RaizN_Factor_Tests.mq5",
        "mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth/JPW_Alavancagem_Observer_Tests.mq5",
        "mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth/JPW_Alavancagem_Panel_Tests.mq5",
        "mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth/JPW_Alavancagem_StopRisk_Tests.mq5",
    }
    current.update("mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_" + name + ".mqh"
                   for name in ['Actions', 'Coordinator', 'Diagnostics', 'Diagnostics_Core', 'Presentation', 'Samples', 'Store_Result', 'Version'])
    current.add("mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth/JPW_Alavancagem_Diagnostics_Tests.mq5")
    assert current <= set(template["sourceFiles"])
    assert "mt5/jpw-alavancagem-atual/MQL5/AGENTS.md" not in template["sourceFiles"]
    assert not template["downloads"]["compiled"]["available"]
    assert template["nativeArtifact"] is None
    with TemporaryDirectory(prefix="jpw-leverage-package-") as directory:
        root = Path(directory)
        manifest_path = root / MANIFEST_PATH
        manifest_path.parent.mkdir(parents=True)
        manifest_path.write_text(json.dumps(template), encoding="utf-8")
        payloads = {}
        for relative in template["sourceFiles"]:
            content = ((ROOT / relative).read_bytes() if relative == VERSION_HEADER else
                       ("synthetic fixture: " + relative + "\n").encode("utf-8"))
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
            payloads[relative.removeprefix("mt5/jpw-alavancagem-atual/")] = content

        first = build(root)
        version_member = VERSION_HEADER.removeprefix("mt5/jpw-alavancagem-atual/")
        payloads[version_member] = (root / VERSION_HEADER).read_bytes()
        assert len(first["runtimeBuildId"]) == 64
        assert first["runtimeBuildId"].encode() in payloads[version_member]
        source = first["downloads"]["source"]
        assert source["available"] and not first["downloads"]["compiled"]["available"]
        content = (root / source["path"]).read_bytes()
        assert len(content) == source["bytes"]
        assert hashlib.sha256(content).hexdigest() == source["sha256"]
        with zipfile.ZipFile(BytesIO(content)) as archive:
            assert set(archive.namelist()) == set(payloads)
            assert all(archive.read(name) == expected for name, expected in payloads.items())
            assert "AGENTS.md" in archive.namelist()
            assert "MQL5/AGENTS.md" not in archive.namelist()
            assert "MQL5/Include/JPWealth/JPW_Alavancagem_Cockpit.mqh" in archive.namelist()
            assert "MQL5/Include/JPWealth/JPW_Alavancagem_StopRisk_Core.mqh" in archive.namelist()
            assert "MQL5/Include/JPWealth/JPW_Alavancagem_StopRisk_Store.mqh" in archive.namelist()
            assert "MQL5/Include/JPWealth/JPW_Alavancagem_StopRisk_Terminal.mqh" in archive.namelist()
            assert "MQL5/Include/JPWealth/JPW_Alavancagem_Observer_Presence.mqh" in archive.namelist()
            assert "MQL5/Scripts/JPWealth/JPW_Alavancagem_StopRisk_Tests.mq5" in archive.namelist()

        manifest_bytes = manifest_path.read_bytes()
        (root / "mt5/jpw-alavancagem-atual/.DS_Store").write_bytes(b"unrelated Finder file")
        second = build(root)
        assert second == first
        assert manifest_path.read_bytes() == manifest_bytes
        assert (root / source["path"]).read_bytes() == content

        # The build identity is about executable source, not documentation or
        # a self-referential stamp. Restore synthetic bytes after each trial.
        guide = root / "mt5/jpw-alavancagem-atual/AGENTS.md"
        old_guide = guide.read_bytes()
        guide.write_bytes(old_guide + b"synthetic documentation delta\n")
        assert build(root)["runtimeBuildId"] == first["runtimeBuildId"]
        guide.write_bytes(old_guide)
        program = root / "mt5/jpw-alavancagem-atual/MQL5/Indicators/JPWealth/JPW_Alavancagem_Atual.mq5"
        old_program = program.read_bytes()
        program.write_bytes(old_program + b"// synthetic source delta\n")
        modified = build(root)
        assert modified["runtimeBuildId"] != first["runtimeBuildId"]
        assert build(root)["runtimeBuildId"] == modified["runtimeBuildId"]
        program.write_bytes(old_program)
        restored = build(root)
        assert restored == first
        assert manifest_path.read_bytes() == manifest_bytes

        bad_version = (root / VERSION_HEADER).read_bytes()
        (root / VERSION_HEADER).write_bytes(bad_version.replace(b'#define JPW_PRODUCT_VERSION "1.10.1"', b'#define JPW_PRODUCT_VERSION "1.9.0"'))
        try:
            build(root)
        except ValueError as error:
            assert "vers" in str(error).lower()
        else:
            raise AssertionError("manifest accepted a different runtime product version")
        (root / VERSION_HEADER).write_bytes(bad_version)
        coordinator = "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_Coordinator.mqh"
        saved_program = program.read_bytes()
        program.write_bytes(saved_program + b"#include<JPWealth/JPW_Alavancagem_Coordinator.mqh>\n")
        missing_dependency = json.loads(manifest_path.read_text())
        missing_dependency["sourceFiles"].remove(coordinator)
        manifest_path.write_text(json.dumps(missing_dependency))
        try:
            build(root)
        except ValueError as error:
            assert "ausente" in str(error).lower() or "depend" in str(error).lower()
        else:
            raise AssertionError("caller accepted without its declared local include")
        program.write_bytes(saved_program)
        manifest_path.write_bytes(manifest_bytes)

        # Quoted includes resolve beside their caller and must be declared;
        # reject missing ones while preserving the existing Live -> Core form.
        program.write_bytes(saved_program + b'#include "missing-relative.mqh"\n')
        try:
            build(root)
        except ValueError as error:
            assert "ausente" in str(error).lower()
        else:
            raise AssertionError("quoted local include accepted without distribution mapping")
        program.write_bytes(saved_program)
        live = root / "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_RaizN_Live.mqh"
        saved_live = live.read_bytes()
        live.write_bytes(saved_live + b'#include "JPW_Alavancagem_Core.mqh"\n')
        assert build(root)["runtimeBuildId"] != first["runtimeBuildId"]
        live.write_bytes(saved_live)
        assert build(root) == first

        rogue = root / COMPILED_ARTIFACT
        rogue.write_bytes(b"not a compiler output" * 150)
        try:
            build(root)
        except ValueError as error:
            assert "sem evidencia nativa" in str(error)
        else:
            raise AssertionError("unverified .ex5 accepted")
        assert not (root / f"downloads/jpw-alavancagem-atual/JPW_Alavancagem_Atual_Compilado_v{template['version']}.zip").exists()
        rogue.unlink()

        # A compiler receipt must bind every executable to the exact MQL inputs,
        # including the USC verifier, MDD viewer and metrics tests, and require the portable CPU target.
        synthetic = json.loads(manifest_path.read_text())
        synthetic["validation"]["compilation"]["status"] = "passed"
        synthetic["nativeArtifact"] = {"sourceFingerprint": "0" * 64, "cpu": "AVX2", "artifacts": [], "compiler": "synthetic", "evidence": "synthetic"}
        manifest_path.write_text(json.dumps(synthetic))
        try:
            build(root)
        except ValueError as error:
            assert "fontes ou a arquitetura" in str(error)
        else:
            raise AssertionError("stale or non-Regular compiler receipt accepted")
        synthetic["nativeArtifact"]["sourceFingerprint"] = first["mqlSourceFingerprint"]
        synthetic["nativeArtifact"]["cpu"] = "X64 Regular"
        manifest_path.write_text(json.dumps(synthetic))
        try:
            build(root)
        except ValueError as error:
            assert "todos os scripts" in str(error)
        else:
            raise AssertionError("incomplete native bundle accepted")
        manifest_path.write_bytes(manifest_bytes)

        incomplete = json.loads(manifest_path.read_text())
        incomplete["sourceFiles"] = [name for name in incomplete["sourceFiles"] if not name.endswith("JPW_Alavancagem_Profile.mqh")]
        manifest_path.write_text(json.dumps(incomplete))
        try:
            build(root)
        except ValueError as error:
            assert "ausentes" in str(error)
        else:
            raise AssertionError("package accepted without its profile dependency")
        manifest_path.write_bytes(manifest_bytes)

        missing_metrics = root / "mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth/JPW_Alavancagem_Metrics_Tests.mq5"
        missing_metrics.unlink()
        try:
            build(root)
        except FileNotFoundError:
            pass
        else:
            raise AssertionError("archive built without the declared metrics script")
        missing_metrics.write_bytes(payloads["MQL5/Scripts/JPWealth/JPW_Alavancagem_Metrics_Tests.mq5"])

        missing_viewer = root / viewer
        missing_viewer.unlink()
        try:
            build(root)
        except FileNotFoundError:
            pass
        else:
            raise AssertionError("archive built without the declared MDD viewer")
        missing_viewer.write_bytes(payloads["MQL5/Scripts/JPWealth/JPW_Alavancagem_Consultar_MDD.mq5"])

        for required_genesis in (genesis, genesis_store, genesis_tests, genesis_store_tests):
            absent = root / required_genesis
            content = absent.read_bytes()
            absent.unlink()
            try:
                build(root)
            except (ValueError, FileNotFoundError):
                pass
            else:
                raise AssertionError(f"archive built without {required_genesis}")
            absent.write_bytes(content)

        for required_raiz in (raiz, raiz_store, raiz_tests, raiz_store_tests):
            absent = root / required_raiz
            content = absent.read_bytes()
            absent.unlink()
            try:
                build(root)
            except (ValueError, FileNotFoundError):
                pass
            else:
                raise AssertionError(f"archive built without {required_raiz}")
            absent.write_bytes(content)

        for required_current in current:
            absent = root / required_current
            content = absent.read_bytes()
            absent.unlink()
            try:
                build(root)
            except (ValueError, FileNotFoundError):
                pass
            else:
                raise AssertionError(f"archive built without {required_current}")
            absent.write_bytes(content)

        missing = root / template["sourceFiles"][2]
        missing.unlink()
        try:
            build(root)
        except FileNotFoundError:
            pass
        else:
            raise AssertionError("archive built without a declared include")

    print("LEVERAGE PACKAGE OK — deterministic bytes, exact extraction, missing include and unverified .ex5 refused")


if __name__ == "__main__":
    main()
