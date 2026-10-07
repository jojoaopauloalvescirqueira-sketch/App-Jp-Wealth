#!/usr/bin/env python3
"""Check archive extraction, determinism and fail-closed native packaging."""
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
import hashlib
import json
import re
import shutil
import zipfile

from build_leverage_package import ROOT, MANIFEST_PATH, COMPILED_ARTIFACT, VERSION_HEADER, build


# Explicit release contract, frozen independently of the generated manifest.
# Do not derive this oracle from sourceFiles: same-count substitutions must fail.
EXPECTED_MEMBERS = {
    "AGENTS.md",
    "GENETRIX_7X_LEDGER.md",
    "GENETRIX_PERSONAL_HISTORY.md",
    "GENETRIX_REPAIR_1_18_1.md",
    "GENETRIX_COMPILE_FIX_1_18_2.md",
    "GENETRIX_UI_1_19_0.md",
    "GENETRIX_CORE_1_20_0.md",
    "MQL5/Experts/JPWealth/JPW_Genetrix_Monitor.mq5",
    "MQL5/Include/JPWealth/JPW_Genetrix_Monitor_Core.mqh",
    "MQL5/Include/JPWealth/JPW_Genetrix_Monitor_Status.mqh",
    "MQL5/Include/JPWealth/JPW_Genetrix_Monitor_UI.mqh",
    "MQL5/Include/JPWealth/JPW_Genetrix_Observer_Runtime.mqh",
    "MQL5/Include/JPWealth/JPW_Genetrix_Accountant_Runtime.mqh",
    "MQL5/Include/JPWealth/JPW_Genetrix_Ledger_Preparation.mqh",
    "MQL5/Include/JPWealth/JPW_UI_Design.mqh",
    "harness/JPW_GENETRIX_MT5_ENGINEERING_HARNESS_v1.0.md",
    "harness/JPW_GENETRIX_MT5_ENGINEERING_HARNESS_v1.0.txt",
    "harness/JPW_GENETRIX_MT5_ENGINEERING_HARNESS_v1.0.pdf",
    "harness/MANUAL_DE_ATIVACAO.md",
    "harness/contracts/ENG-AC01-12.json",
    "harness/contracts/TEMPLATES.md",
    "harness/REPOSITORY_INTEGRATION.md",
    "MQL5/Experts/JPWealth/JPW_Alavancagem_Observer.mq5",
    "MQL5/Experts/JPWealth/JPW_Genetrix_Accountant.mq5",
    "MQL5/Experts/JPWealth/JPW_Genetrix_Supervisor.mq5",
    "MQL5/Images/JPWealth/JPW_Genetrix_Logo.provenance.md",
    "MQL5/Images/JPWealth/JPW_Genetrix_Logo_Dark_100.bmp",
    "MQL5/Images/JPWealth/JPW_Genetrix_Logo_Dark_125.bmp",
    "MQL5/Images/JPWealth/JPW_Genetrix_Logo_Dark_150.bmp",
    "MQL5/Images/JPWealth/JPW_Genetrix_Logo_Dark_200.bmp",
    "MQL5/Images/JPWealth/JPW_Genetrix_Logo_Light_100.bmp",
    "MQL5/Images/JPWealth/JPW_Genetrix_Logo_Light_125.bmp",
    "MQL5/Images/JPWealth/JPW_Genetrix_Logo_Light_150.bmp",
    "MQL5/Images/JPWealth/JPW_Genetrix_Logo_Light_200.bmp",
    "MQL5/Images/JPWealth/JPW_NoCuda_Logo.bmp",
    "MQL5/Include/JPWealth/JPW_Alavancagem_Actions.mqh",
    "MQL5/Include/JPWealth/JPW_Alavancagem_Cockpit.mqh",
    "MQL5/Include/JPWealth/JPW_Alavancagem_Coordinator.mqh",
    "MQL5/Include/JPWealth/JPW_Alavancagem_Core.mqh",
    "MQL5/Include/JPWealth/JPW_Alavancagem_Diagnostics.mqh",
    "MQL5/Include/JPWealth/JPW_Alavancagem_Diagnostics_Core.mqh",
    "MQL5/Include/JPWealth/JPW_Alavancagem_Genesis_Core.mqh",
    "MQL5/Include/JPWealth/JPW_Alavancagem_Genesis_Store.mqh",
    "MQL5/Include/JPWealth/JPW_Alavancagem_MDD.mqh",
    "MQL5/Include/JPWealth/JPW_Alavancagem_Observer_Presence.mqh",
    "MQL5/Include/JPWealth/JPW_Alavancagem_Panel.mqh",
    "MQL5/Include/JPWealth/JPW_Alavancagem_Positions.mqh",
    "MQL5/Include/JPWealth/JPW_Alavancagem_Presentation.mqh",
    "MQL5/Include/JPWealth/JPW_Alavancagem_Profile.mqh",
    "MQL5/Include/JPWealth/JPW_Alavancagem_RaizN_Config.mqh",
    "MQL5/Include/JPWealth/JPW_Alavancagem_RaizN_Core.mqh",
    "MQL5/Include/JPWealth/JPW_Alavancagem_RaizN_Factor.mqh",
    "MQL5/Include/JPWealth/JPW_Alavancagem_RaizN_Horizon.mqh",
    "MQL5/Include/JPWealth/JPW_Alavancagem_RaizN_Live.mqh",
    "MQL5/Include/JPWealth/JPW_Alavancagem_RaizN_Observer.mqh",
    "MQL5/Include/JPWealth/JPW_Alavancagem_RaizN_Store.mqh",
    "MQL5/Include/JPWealth/JPW_Alavancagem_Samples.mqh",
    "MQL5/Include/JPWealth/JPW_Alavancagem_StopRisk_Core.mqh",
    "MQL5/Include/JPWealth/JPW_Alavancagem_StopRisk_Store.mqh",
    "MQL5/Include/JPWealth/JPW_Alavancagem_StopRisk_Terminal.mqh",
    "MQL5/Include/JPWealth/JPW_Alavancagem_Store_Result.mqh",
    "MQL5/Include/JPWealth/JPW_Alavancagem_Terminal.mqh",
    "MQL5/Include/JPWealth/JPW_Alavancagem_Version.mqh",
    "MQL5/Include/JPWealth/JPW_Genetrix_Brand.mqh",
    "MQL5/Include/JPWealth/JPW_Genetrix_Ledger_Bridge.mqh",
    "MQL5/Include/JPWealth/JPW_Genetrix_Ledger_Core.mqh",
    "MQL5/Include/JPWealth/JPW_Genetrix_Ledger_Store.mqh",
    "MQL5/Include/JPWealth/JPW_Genetrix_Ledger_Terminal.mqh",
    "MQL5/Include/JPWealth/JPW_Genetrix_Risk_Core.mqh",
    "MQL5/Include/JPWealth/JPW_Genetrix_Risk_Store.mqh",
    "MQL5/Include/JPWealth/JPW_Genetrix_Risk_Terminal.mqh",
    "MQL5/Include/JPWealth/JPW_Genetrix_UI.mqh",
    "MQL5/Include/JPWealth/JPW_NoCuda_Core.mqh",
    "MQL5/Include/JPWealth/JPW_NoCuda_Fibo_Controller.mqh",
    "MQL5/Include/JPWealth/JPW_NoCuda_Fibo_Core.mqh",
    "MQL5/Include/JPWealth/JPW_NoCuda_Fibo_Store.mqh",
    "MQL5/Include/JPWealth/JPW_NoCuda_Fibo_Sync.mqh",
    "MQL5/Include/JPWealth/JPW_NoCuda_Fibo_Terminal.mqh",
    "MQL5/Include/JPWealth/JPW_NoCuda_Fibo_UI.mqh",
    "MQL5/Include/JPWealth/JPW_NoCuda_Projection.mqh",
    "MQL5/Include/JPWealth/JPW_NoCuda_Projection_Core.mqh",
    "MQL5/Include/JPWealth/JPW_NoCuda_Render.mqh",
    "MQL5/Include/JPWealth/JPW_NoCuda_Store.mqh",
    "MQL5/Include/JPWealth/JPW_NoCuda_Terminal.mqh",
    "MQL5/Include/JPWealth/JPW_NoCuda_UI.mqh",
    "MQL5/Include/JPWealth/JPW_PersonalHistory_Controller.mqh",
    "MQL5/Include/JPWealth/JPW_PersonalHistory_Core.mqh",
    "MQL5/Include/JPWealth/JPW_PersonalHistory_Export.mqh",
    "MQL5/Include/JPWealth/JPW_PersonalHistory_Store.mqh",
    "MQL5/Include/JPWealth/JPW_PersonalHistory_Terminal.mqh",
    "MQL5/Include/JPWealth/JPW_PersonalHistory_UI.mqh",
    "MQL5/Include/JPWealth/JPW_SignalCopy_Controller.mqh",
    "MQL5/Include/JPWealth/JPW_SignalCopy_Core.mqh",
    "MQL5/Include/JPWealth/JPW_SignalCopy_Terminal.mqh",
    "MQL5/Include/JPWealth/JPW_SignalCopy_Types.mqh",
    "MQL5/Include/JPWealth/JPW_SignalCopy_UI.mqh",
    "MQL5/Include/JPWealth/JPW_UI_Focus.mqh",
    "MQL5/Indicators/JPWealth/JPW_Alavancagem_Atual.mq5",
    "MQL5/Indicators/JPWealth/JPW_NoCuda_Channels.mq5",
    "MQL5/Scripts/JPWealth/JPW_Alavancagem_Consultar_MDD.mq5",
    "MQL5/Scripts/JPWealth/JPW_Alavancagem_Diagnostics_Tests.mq5",
    "MQL5/Scripts/JPWealth/JPW_Alavancagem_Genesis_Store_Tests.mq5",
    "MQL5/Scripts/JPWealth/JPW_Alavancagem_Genesis_Tests.mq5",
    "MQL5/Scripts/JPWealth/JPW_Alavancagem_Metrics_Tests.mq5",
    "MQL5/Scripts/JPWealth/JPW_Alavancagem_Observer_Tests.mq5",
    "MQL5/Scripts/JPWealth/JPW_Alavancagem_Panel_Tests.mq5",
    "MQL5/Scripts/JPWealth/JPW_Alavancagem_Positions_Tests.mq5",
    "MQL5/Scripts/JPWealth/JPW_Alavancagem_Profile_Tests.mq5",
    "MQL5/Scripts/JPWealth/JPW_Alavancagem_RaizN_Config_Tests.mq5",
    "MQL5/Scripts/JPWealth/JPW_Alavancagem_RaizN_Factor_Tests.mq5",
    "MQL5/Scripts/JPWealth/JPW_Alavancagem_RaizN_Horizon_Tests.mq5",
    "MQL5/Scripts/JPWealth/JPW_Alavancagem_RaizN_Live_Tests.mq5",
    "MQL5/Scripts/JPWealth/JPW_Alavancagem_RaizN_Store_Tests.mq5",
    "MQL5/Scripts/JPWealth/JPW_Alavancagem_RaizN_Tests.mq5",
    "MQL5/Scripts/JPWealth/JPW_Alavancagem_StopRisk_Tests.mq5",
    "MQL5/Scripts/JPWealth/JPW_Alavancagem_Tests.mq5",
    "MQL5/Scripts/JPWealth/JPW_Alavancagem_Verificar_USC.mq5",
    "MQL5/Scripts/JPWealth/JPW_Genetrix_Ledger_Tests.mq5",
    "MQL5/Scripts/JPWealth/JPW_Genetrix_Risk_Tests.mq5",
    "MQL5/Scripts/JPWealth/JPW_NoCuda_Core_Tests.mq5",
    "MQL5/Scripts/JPWealth/JPW_NoCuda_Fibo_Lab.mq5",
    "MQL5/Scripts/JPWealth/JPW_NoCuda_Fibo_Tests.mq5",
    "MQL5/Scripts/JPWealth/JPW_NoCuda_Projection_Tests.mq5",
    "MQL5/Scripts/JPWealth/JPW_NoCuda_Store_Tests.mq5",
    "MQL5/Scripts/JPWealth/JPW_PersonalHistory_Tests.mq5",
    "MQL5/Scripts/JPWealth/JPW_SignalCopy_Tests.mq5",
    "README.md",
}


def assert_release_inventory(manifest: dict) -> None:
    expected = {"mt5/jpw-alavancagem-atual/" + member for member in EXPECTED_MEMBERS}
    assert len(EXPECTED_MEMBERS) == 127
    assert len(manifest["sourceFiles"]) == len(set(manifest["sourceFiles"])) == 127
    assert set(manifest["sourceFiles"]) == expected, "source inventory differs from the explicit release contract"


NATIVE_EVIDENCE = Path("docs/validation/genetrix-1.20.0/evidence")


def assert_native_evidence(root: Path, manifest: dict) -> None:
    """Link current sources, artifacts and raw logs to the frozen compilation.

    This checks the retained compilation evidence, without claiming terminal
    execution. A coherent artifact/manifest pair alone is not provenance.
    """
    evidence = root / NATIVE_EVIDENCE
    receipt = json.loads((evidence / "NATIVE-ROOT-RECEIPT-R1.json").read_text(encoding="utf-8"))
    input_freeze = json.loads((evidence / "NATIVE-INPUT-FREEZE-R1.json").read_text(encoding="utf-8"))
    review = json.loads((evidence / "NATIVE-INDEPENDENT-REVIEW-R1-PARSER-R2.json").read_text(encoding="utf-8"))
    product = root / "mt5/jpw-alavancagem-atual"
    expected_targets = {member.removeprefix("MQL5/") for member in EXPECTED_MEMBERS
                        if member.endswith(".mq5")}
    assert len(expected_targets) == 33
    assert receipt["status"] == "COMPILATION_PASS"
    assert receipt["targets_required"] == receipt["targets_observed"] == 33
    assert len(receipt["targets"]) == 33
    assert {row["target"] for row in receipt["targets"]} == expected_targets
    assert receipt["inputs_unchanged"] is True
    assert receipt["runtime"] == receipt["operational_migration"] == "NOT_RUN"
    assert receipt["native_critical_sessions"] == "0/3"
    assert receipt["cpu"] == manifest["nativeArtifact"]["cpu"] == "X64 Regular"
    assert receipt["mqlSourceFingerprint"] == input_freeze["mqlSourceFingerprint"] == review["mqlSourceFingerprint"] == manifest["mqlSourceFingerprint"]
    assert receipt["runtimeBuildId"] == review["runtimeBuildId"] == manifest["runtimeBuildId"]
    compiler_hash = receipt["compiler_sha256"]
    assert re.fullmatch(r"[0-9a-f]{64}", compiler_hash)
    assert compiler_hash == input_freeze["compiler_sha256"] == review["compiler"]["sha256"]
    assert compiler_hash in manifest["nativeArtifact"]["compiler"]
    assert review["classification"] == "NATIVE_COMPILATION_DEMONSTRATED_33_OF_33"
    assert all(review["gates"].values())
    runtime_members = {member for member in EXPECTED_MEMBERS
                       if Path(member).suffix in (".mq5", ".mqh", ".bmp")}
    assert len(runtime_members) == 111
    hashes = {member: hashlib.sha256((product / member).read_bytes()).hexdigest()
              for member in sorted(runtime_members)}
    fingerprint = hashlib.sha256(json.dumps(hashes, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    assert fingerprint == manifest["mqlSourceFingerprint"]
    for member, source_hash in hashes.items():
        assert input_freeze["files"][member] == source_hash
    artifacts = manifest["nativeArtifact"]["artifacts"]
    assert len(artifacts) == 33
    artifact_hashes = {record["path"]: record["sha256"] for record in artifacts}
    assert len(artifact_hashes) == 33
    for row in receipt["targets"]:
        target = row["target"]
        source = product / "MQL5" / target
        artifact_relative = "mt5/jpw-alavancagem-atual/MQL5/" + target[:-4] + ".ex5"
        artifact = root / artifact_relative
        log = evidence / "native-R1/MQL5" / (target[:-4] + ".log.txt")
        assert hashlib.sha256(source.read_bytes()).hexdigest() == row["source_sha256"]
        assert hashlib.sha256(artifact.read_bytes()).hexdigest() == row["ex5_sha256"] == artifact_hashes[artifact_relative]
        assert artifact.stat().st_size == row["bytes"] >= 1024
        raw_log = log.read_bytes()
        assert hashlib.sha256(raw_log).hexdigest() == row["log_sha256"]
        text = raw_log.decode("utf-16")
        assert " : information: code generated" in text
        assert re.findall(r"^Result: ([^\r\n]+)\r?$", text, re.MULTILINE) == [
            "0 errors, 0 warnings, " + str(row["elapsed_ms"]) + " ms elapsed, cpu='X64 Regular'"]
        assert row["errors"] == row["warnings"] == 0


def main() -> None:
    template = json.loads((ROOT / MANIFEST_PATH).read_text(encoding="utf-8"))
    expected_sources = {"mt5/jpw-alavancagem-atual/" + member for member in EXPECTED_MEMBERS}
    assert len(EXPECTED_MEMBERS) == 127
    assert len(template["sourceFiles"]) == len(set(template["sourceFiles"])) == 127
    assert set(template["sourceFiles"]) == expected_sources, "source inventory differs from the explicit release contract"
    assert_release_inventory(template)
    for mutation in ("duplicate", "substitute"):
        rejected = json.loads(json.dumps(template))
        if mutation == "duplicate":
            rejected["sourceFiles"][-1] = rejected["sourceFiles"][0]
        else:
            rejected["sourceFiles"][-1] = "mt5/jpw-alavancagem-atual/rogue-replacement.md"
        try:
            assert_release_inventory(rejected)
        except AssertionError:
            pass
        else:
            raise AssertionError("explicit inventory accepted " + mutation)
    assert template["version"] == "1.20.0"
    version_source = (ROOT / VERSION_HEADER).read_text(encoding="utf-8")
    assert '#define JPW_PRODUCT_VERSION "1.20.0"' in version_source
    assert '#define JPW_PRODUCT_MQL_VERSION "1.200"' in version_source
    assert '#define JPW_CALCULATION_VERSION "1.9.0"' in version_source
    nocuda_source = (ROOT / "mt5/jpw-alavancagem-atual/MQL5/Indicators/JPWealth/JPW_NoCuda_Channels.mq5").read_text(encoding="utf-8")
    assert '#property version   "1.30"' in nocuda_source
    readme = (ROOT / "mt5/jpw-alavancagem-atual/README.md").read_text(encoding="utf-8")
    assert re.search(r"\bMQL\s*`?1\.200`?(?![\d.])", readme), "README MQL version must be 1.200"
    readme_plain = re.sub(r"[*`]", "", readme)
    nocuda_version_pattern = r"\bNoCuda\s+(?:declara\s+)?1\.30(?!\d|\.\d)"
    for declaration, expected in (("NoCuda 1.30.", True),
                                  ("NoCuda declara 1.30.", True),
                                  ("NoCuda 1.300.", False),
                                  ("NoCuda 1.30.7.", False)):
        assert bool(re.search(nocuda_version_pattern, declaration)) == expected
    assert re.search(nocuda_version_pattern, readme_plain), "README NoCuda version must be 1.30"
    for phrase in ('fontes MT5 v1.20.0',
                   'cálculo financeiro continua **1.9.0**', 'NOT_RUN'):
        assert phrase in readme, phrase
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
    signal = {"mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_SignalCopy_" + name + ".mqh"
              for name in ("Types", "Core", "Terminal", "Controller", "UI")}
    signal.add("mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth/JPW_SignalCopy_Tests.mq5")
    signal.add("mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_Positions.mqh")
    signal.add("mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth/JPW_Alavancagem_Positions_Tests.mq5")
    assert signal <= set(template["sourceFiles"])
    assert template["validation"]["clipboard"]["status"] == "pending"
    assert "NOT_RUN" in template["validation"]["clipboard"]["detail"]
    assert current <= set(template["sourceFiles"])
    nocuda = {
        "mt5/jpw-alavancagem-atual/MQL5/Indicators/JPWealth/JPW_NoCuda_Channels.mq5",
        *("mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_NoCuda_" + name + ".mqh"
          for name in ("Core", "Store", "Terminal", "Render", "UI", "Projection_Core", "Projection")),
        "mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth/JPW_NoCuda_Core_Tests.mq5",
        "mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth/JPW_NoCuda_Store_Tests.mq5",
        "mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth/JPW_NoCuda_Projection_Tests.mq5",
    }
    fibo = {
        *("mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_NoCuda_Fibo_" + name + ".mqh"
          for name in ("Core", "Terminal", "Store", "Sync", "Controller", "UI")),
        "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_UI_Focus.mqh",
        "mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth/JPW_NoCuda_Fibo_Tests.mq5",
        "mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth/JPW_NoCuda_Fibo_Lab.mq5",
        "mt5/jpw-alavancagem-atual/MQL5/Images/JPWealth/JPW_NoCuda_Logo.bmp",
    }
    nocuda |= fibo
    # Versioned expectations are independent of the generated ZIP/manifest.
    # Preserve all earlier contracts and require each new observer component.
    personal_history = {
        "mt5/jpw-alavancagem-atual/GENETRIX_PERSONAL_HISTORY.md",
        *("mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_PersonalHistory_" + name + ".mqh"
          for name in ("Controller", "Core", "Export", "Store", "Terminal", "UI")),
        "mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth/JPW_PersonalHistory_Tests.mq5",
    }
    assert len(template["sourceFiles"]) == len(set(template["sourceFiles"])) == 127
    assert personal_history <= set(template["sourceFiles"])
    assert nocuda <= set(template["sourceFiles"])
    brands = {"mt5/jpw-alavancagem-atual/MQL5/Images/JPWealth/JPW_Genetrix_Logo_" +
              theme + "_" + str(scale) + ".bmp" for theme in ("Light", "Dark")
              for scale in (100,125,150,200)}
    assert brands <= set(template["sourceFiles"])
    assert "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Genetrix_Brand.mqh" in template["sourceFiles"]
    assert template["productName"] == "JPW GENETRIX"
    assert '#define JPW_PRODUCT_NAME "JPW GENETRIX"' in version_source
    assert '#define JPW_PRODUCT_TAGLINE "Da origem da operação à leitura do risco."' in version_source
    for phrase in ("CANDIDATE 1.20.0", "33/33", "NOT_RUN"):
        assert phrase in template["coverage"], phrase
    for phrase in ("Fibonacci acompanhado", "UNVERIFIED_NATIVE", "| 5 | −0,50 |", "H1 e H4", "não prevê"):
        assert phrase in readme, phrase
    assert not any(name.endswith("Nocuda_Tool.mq5") for name in template["sourceFiles"])
    assert "mt5/jpw-alavancagem-atual/MQL5/AGENTS.md" not in template["sourceFiles"]
    assert template["validation"]["compilation"]["status"] == "passed"
    for gate in ("mathematics", "terminal"):
        assert template["validation"][gate]["status"] == "pending"
    assert "NOT_RUN" in template["validation"]["terminal"]["detail"]
    assert template["downloads"]["compiled"]["available"]
    native = template["nativeArtifact"]
    assert native["sourceFingerprint"] == template["mqlSourceFingerprint"]
    assert native["cpu"] == "X64 Regular" and native["compiler"] and native["evidence"]
    expected_native = {"mt5/jpw-alavancagem-atual/" + name[:-4] + ".ex5"
                       for name in EXPECTED_MEMBERS if name.endswith(".mq5")}
    assert len(expected_native) == 33
    assert len(native["artifacts"]) == 33
    assert {item["path"] for item in native["artifacts"]} == expected_native
    for item in native["artifacts"]:
        native_bytes = (ROOT / item["path"]).read_bytes()
        assert len(native_bytes) >= 1024
        assert hashlib.sha256(native_bytes).hexdigest() == item["sha256"]
    compiled = template["downloads"]["compiled"]
    compiled_bytes = (ROOT / compiled["path"]).read_bytes()
    assert hashlib.sha256(compiled_bytes).hexdigest() == compiled["sha256"]
    assert len(compiled_bytes) == compiled["bytes"]
    with zipfile.ZipFile(BytesIO(compiled_bytes)) as archive:
        expected_compiled = {name.removeprefix("mt5/jpw-alavancagem-atual/")
                             for name in expected_native} | {"README.md"}
        assert len(archive.namelist()) == len(set(archive.namelist())) == 34
        assert set(archive.namelist()) == expected_compiled
        assert archive.read("README.md") == readme.encode("utf-8")
        for item in native["artifacts"]:
            assert hashlib.sha256(archive.read(item["path"].removeprefix(
                "mt5/jpw-alavancagem-atual/"))).hexdigest() == item["sha256"]
    actual_source = template["downloads"]["source"]
    actual_source_bytes = (ROOT / actual_source["path"]).read_bytes()
    assert hashlib.sha256(actual_source_bytes).hexdigest() == actual_source["sha256"]
    assert len(actual_source_bytes) == actual_source["bytes"]
    assert set(template["sourceHashes"]) == EXPECTED_MEMBERS
    with zipfile.ZipFile(BytesIO(actual_source_bytes)) as archive:
        assert len(archive.namelist()) == len(set(archive.namelist())) == 127
        assert set(archive.namelist()) == EXPECTED_MEMBERS
        for member, expected_hash in template["sourceHashes"].items():
            source_bytes = (ROOT / "mt5/jpw-alavancagem-atual" / member).read_bytes()
            assert hashlib.sha256(source_bytes).hexdigest() == expected_hash
            assert archive.read(member) == source_bytes
    assert_native_evidence(ROOT, template)
    # Falsify provenance using the same native receipt. Mutating both EX5 and
    # manifest SHA coherently must still fail; do not rewrite the old receipt.
    with TemporaryDirectory(prefix="jpw-native-provenance-controls-") as directory:
        evidence_root = Path(directory)
        for member in EXPECTED_MEMBERS:
            if Path(member).suffix in (".mq5", ".mqh", ".bmp"):
                relative = Path("mt5/jpw-alavancagem-atual") / member
                (evidence_root / relative).parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / relative, evidence_root / relative)
        for item in native["artifacts"]:
            relative = Path(item["path"])
            shutil.copyfile(ROOT / relative, evidence_root / relative)
        shutil.copytree(ROOT / NATIVE_EVIDENCE, evidence_root / NATIVE_EVIDENCE)
        assert_native_evidence(evidence_root, template)
        selected = sorted(expected_native)[0]
        victim = evidence_root / selected
        old_artifact = victim.read_bytes()
        victim_log = evidence_root / NATIVE_EVIDENCE / "native-R1/MQL5" / (
            selected.removeprefix("mt5/jpw-alavancagem-atual/MQL5/")[:-4] + ".log.txt")
        old_log = victim_log.read_bytes()
        for mutation in ("missing-log", "corrupt-log", "coherent-fake-ex5"):
            rejected = json.loads(json.dumps(template))
            if mutation == "missing-log":
                victim_log.unlink()
            elif mutation == "corrupt-log":
                victim_log.write_bytes(b"corrupt native log")
            else:
                victim.write_bytes(b"fake executable with coherent manifest SHA" * 150)
                for item in rejected["nativeArtifact"]["artifacts"]:
                    if item["path"] == selected:
                        item["sha256"] = hashlib.sha256(victim.read_bytes()).hexdigest()
            try:
                assert_native_evidence(evidence_root, rejected)
            except (AssertionError, FileNotFoundError):
                pass
            else:
                raise AssertionError("native provenance accepted " + mutation)
            victim.write_bytes(old_artifact)
            victim_log.write_bytes(old_log)
        assert_native_evidence(evidence_root, template)
    # Synthetic builder controls are source-only until their own complete
    # temporary receipt is constructed; never borrow the actual native receipt.
    fixture_template = json.loads(json.dumps(template))
    fixture_template["nativeArtifact"] = None
    fixture_template["validation"]["compilation"]["status"] = "pending"
    fixture_template["validation"]["compilation"]["detail"] = "Synthetic builder control; native NOT_RUN"
    with TemporaryDirectory(prefix="jpw-leverage-package-") as directory:
        root = Path(directory)
        manifest_path = root / MANIFEST_PATH
        manifest_path.parent.mkdir(parents=True)
        manifest_path.write_text(json.dumps(fixture_template), encoding="utf-8")
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
        assert source["filename"] == "JPW_Genetrix_Fontes_v1.20.0.zip"
        content = (root / source["path"]).read_bytes()
        assert len(content) == source["bytes"]
        assert hashlib.sha256(content).hexdigest() == source["sha256"]
        with zipfile.ZipFile(BytesIO(content)) as archive:
            assert len(archive.namelist()) == len(set(archive.namelist())) == len(payloads)
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
            assert {name.removeprefix("mt5/jpw-alavancagem-atual/") for name in nocuda} <= set(archive.namelist())

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

        nocuda_indicator = root / "mt5/jpw-alavancagem-atual/MQL5/Indicators/JPWealth/JPW_NoCuda_Channels.mq5"
        old_nocuda_indicator = nocuda_indicator.read_bytes()
        nocuda_indicator.write_bytes(old_nocuda_indicator + b"// synthetic NoCuda source delta\n")
        assert build(root)["runtimeBuildId"] != first["runtimeBuildId"]
        nocuda_indicator.write_bytes(old_nocuda_indicator)
        assert build(root) == first

        # Each new public brand resource is an executable input, including DPI
        # and theme variants; documentation remains outside the runtime identity.
        for resource in sorted(brands):
            target = root / resource
            before = target.read_bytes()
            target.write_bytes(before + b"synthetic brand resource change")
            changed = build(root)
            assert changed["runtimeBuildId"] != first["runtimeBuildId"]
            assert changed["mqlSourceFingerprint"] != first["mqlSourceFingerprint"]
            target.write_bytes(before)
            assert build(root) == first

        # The bitmap is incorporated by #resource, so it belongs to the exact
        # executable identity even though README/AGENTS do not.
        bitmap = root / "mt5/jpw-alavancagem-atual/MQL5/Images/JPWealth/JPW_NoCuda_Logo.bmp"
        old_bitmap = bitmap.read_bytes()
        bitmap.write_bytes(old_bitmap + b"synthetic resource delta")
        resource_changed = build(root)
        assert resource_changed["runtimeBuildId"] != first["runtimeBuildId"]
        assert resource_changed["mqlSourceFingerprint"] != first["mqlSourceFingerprint"]
        bitmap.write_bytes(old_bitmap)
        assert build(root) == first

        bad_version = (root / VERSION_HEADER).read_bytes()
        valid_version = ('#define JPW_PRODUCT_VERSION "' + template["version"] + '"').encode()
        assert bad_version.count(valid_version) == 1, "runtime-version mutation must change exactly one declaration"
        mismatched_version = bad_version.replace(b'#define JPW_PRODUCT_VERSION "1.20.0"',
                                                b'#define JPW_PRODUCT_VERSION "1.9.0"')
        assert mismatched_version != bad_version, "negative version fixture did not mutate the input"
        (root / VERSION_HEADER).write_bytes(mismatched_version)
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

        # Local #resource paths must be declared just like local includes.
        ui = root / "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Genetrix_Brand.mqh"
        saved_ui = ui.read_bytes()
        resource_declaration = next(line for line in (ROOT / ui.relative_to(root)).read_bytes().splitlines()
                                    if line.startswith(b"#resource"))
        ui.write_bytes(saved_ui + resource_declaration + b"\n")
        undeclared_resource = json.loads(manifest_path.read_text())
        resource_path = "mt5/jpw-alavancagem-atual/MQL5/Images/JPWealth/JPW_Genetrix_Logo_Light_100.bmp"
        undeclared_resource["sourceFiles"].remove(resource_path)
        manifest_path.write_text(json.dumps(undeclared_resource))
        try:
            build(root)
        except ValueError as error:
            assert "ausente" in str(error).lower() or "recurso" in str(error).lower()
        else:
            raise AssertionError("embedded bitmap accepted without explicit distribution mapping")
        ui.write_bytes(saved_ui)
        manifest_path.write_bytes(manifest_bytes)
        assert build(root) == first

        unlisted_bitmap = root / "mt5/jpw-alavancagem-atual/MQL5/Images/JPWealth/unapproved.bmp"
        unlisted_bitmap.write_bytes(b"synthetic unapproved bitmap")
        wrong_resource = json.loads(manifest_path.read_text())
        wrong_resource["sourceFiles"].append(unlisted_bitmap.relative_to(root).as_posix())
        manifest_path.write_text(json.dumps(wrong_resource))
        try:
            build(root)
        except ValueError as error:
            assert "tipo" in str(error).lower() or "recurso" in str(error).lower()
        else:
            raise AssertionError("unapproved arbitrary bitmap entered the source bundle")
        manifest_path.write_bytes(manifest_bytes)
        unlisted_bitmap.unlink()

        # The harness JSON is explicitly allowed; that never approves another
        # JSON, PDF or TXT just because its suffix matches a documented format.
        for suffix in ("json", "pdf", "txt"):
            unapproved = root / ("mt5/jpw-alavancagem-atual/harness/unapproved." + suffix)
            unapproved.write_bytes(b"unapproved document control")
            unapproved_manifest = json.loads(manifest_bytes)
            unapproved_manifest["sourceFiles"].append(unapproved.relative_to(root).as_posix())
            manifest_path.write_text(json.dumps(unapproved_manifest))
            try:
                build(root)
            except ValueError as error:
                assert "tipo" in str(error).lower() or "recurso" in str(error).lower()
            else:
                raise AssertionError("arbitrary harness document accepted: " + suffix)
            unapproved.unlink()
            manifest_path.write_bytes(manifest_bytes)

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

        # Full synthetic positive control followed by adversarial receipt and
        # byte mutations. These files are temporary fixture bytes, never native
        # compilation evidence for the product.
        valid_receipt = json.loads(manifest_bytes)
        valid_receipt["validation"]["compilation"]["status"] = "passed"
        valid_receipt["nativeArtifact"] = {
            "sourceFingerprint": first["mqlSourceFingerprint"],
            "cpu": "X64 Regular", "compiler": "synthetic fixture only",
            "evidence": "synthetic fixture; not a native execution claim", "artifacts": [],
        }
        native_payloads = {}
        for relative in sorted(expected_native):
            native_bytes = ("synthetic executable fixture: " + relative).encode() * 32
            (root / relative).write_bytes(native_bytes)
            native_payloads[relative] = native_bytes
            valid_receipt["nativeArtifact"]["artifacts"].append({
                "path": relative, "sha256": hashlib.sha256(native_bytes).hexdigest(),
            })
        manifest_path.write_text(json.dumps(valid_receipt))
        valid_compiled = build(root)
        assert valid_compiled["downloads"]["compiled"]["available"]
        synthetic_path = root / valid_compiled["downloads"]["compiled"]["path"]
        with zipfile.ZipFile(synthetic_path) as archive:
            assert len(archive.namelist()) == len(set(archive.namelist())) == 34
            assert set(archive.namelist()) == expected_compiled
            for relative, native_bytes in native_payloads.items():
                assert archive.read(relative.removeprefix("mt5/jpw-alavancagem-atual/")) == native_bytes
        assert build(root) == valid_compiled
        for mutation in ("duplicate", "substitution", "stale", "cpu", "compiler", "evidence", "unproved"):
            rejected = json.loads(json.dumps(valid_receipt))
            receipt = rejected["nativeArtifact"]
            if mutation == "duplicate":
                receipt["artifacts"][-1] = receipt["artifacts"][0]
            elif mutation == "substitution":
                receipt["artifacts"][-1]["path"] = "mt5/jpw-alavancagem-atual/MQL5/Experts/JPWealth/rogue.ex5"
            elif mutation == "stale":
                receipt["sourceFingerprint"] = "0" * 64
            elif mutation == "cpu":
                receipt["cpu"] = "AVX2"
            elif mutation in ("compiler", "evidence"):
                receipt[mutation] = ""
            else:
                rejected["validation"]["compilation"]["status"] = "pending"
            manifest_path.write_text(json.dumps(rejected))
            try:
                build(root)
            except ValueError:
                pass
            else:
                raise AssertionError("invalid native receipt accepted: " + mutation)
        victim = root / sorted(expected_native)[0]
        for mutation in (b"tampered" * 250, b"short"):
            victim.write_bytes(mutation)
            manifest_path.write_text(json.dumps(valid_receipt))
            try:
                build(root)
            except ValueError as error:
                assert "diferente" in str(error).lower() or "vazio" in str(error).lower()
            else:
                raise AssertionError("tampered or undersized native artifact accepted")
        for relative in expected_native:
            (root / relative).unlink()
        synthetic_path.unlink()
        manifest_path.write_bytes(manifest_bytes)
        assert build(root) == first

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

        for required_component in nocuda | personal_history:
            absent = root / required_component
            content = absent.read_bytes()
            absent.unlink()
            try:
                build(root)
            except (ValueError, FileNotFoundError):
                pass
            else:
                raise AssertionError(f"archive built without {required_component}")
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
