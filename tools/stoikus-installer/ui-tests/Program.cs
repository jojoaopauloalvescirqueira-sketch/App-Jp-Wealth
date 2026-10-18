using Stoikus.Installer.App;
using Stoikus.Installer.Core;

var a = new TerminalTarget("A/terminal64.exe", "A/data", "A/metaeditor64.exe", false);
var b = new TerminalTarget("B/terminal64.exe", "B/data", "B/metaeditor64.exe", false);
var failures = 0;
var total = 0;
async Task Test(string name, Func<Task> run)
{
    total++;
    try { await run(); Console.WriteLine("PASS " + name); }
    catch (Exception ex) { failures++; Console.WriteLine("FAIL " + name + ": " + ex.Message); }
}
void Check(bool value, string message) { if (!value) throw new Exception(message); }
Task Sync(Action action) { action(); return Task.CompletedTask; }

await Test("selection stays locked during delayed inspection", async () =>
{
    var state = new WizardOperationState();
    var snapshot = state.BeginInspection(a, InstallAction.Install, false);
    var release = new TaskCompletionSource(TaskCreationOptions.RunContinuationsAsynchronously);
    var finished = Task.Run(async () => { await release.Task; return state.CompleteInspection(snapshot, a, InstallAction.Install, false); });
    var selectionLocked = !state.CanChangeSelection;
    release.SetResult(); Check(await finished, "same selection should accept its result");
    Check(selectionLocked, "selection controls must remain unavailable while awaiting inspection");
    Check(state.CanChangeSelection, "selection unlocks after inspection");
});
await Test("delayed A cannot become preview of selected B", async () =>
{
    var state = new WizardOperationState();
    var snapshot = state.BeginInspection(a, InstallAction.Remove, false);
    var release = new TaskCompletionSource(TaskCreationOptions.RunContinuationsAsynchronously);
    var finished = Task.Run(async () => { await release.Task; return state.CompleteInspection(snapshot, b, InstallAction.Remove, false); });
    state.InvalidateSelection(); release.SetResult();
    Check(!await finished, "response from A must be discarded after selecting B");
    Check(!state.CanExecute(b, InstallAction.Remove, false), "B has no approved preview");
    Check(state.Preview is null, "stale preview must not remain available");
});
await Test("action change invalidates pending preview", () => Sync(() =>
{
    var state = new WizardOperationState(); var s = state.BeginInspection(a, InstallAction.Install, false);
    Check(!state.CompleteInspection(s, a, InstallAction.Remove, false), "install result cannot approve removal");
}));
await Test("A to B to A still invalidates old A response", () => Sync(() =>
{
    var state = new WizardOperationState(); var s = state.BeginInspection(a, InstallAction.Install, false);
    state.InvalidateSelection(); state.InvalidateSelection();
    Check(!state.CompleteInspection(s, a, InstallAction.Install, false), "revision must distinguish a newer A selection");
}));
await Test("concurrent inspections are rejected", () => Sync(() =>
{
    var state = new WizardOperationState(); state.BeginInspection(a, InstallAction.Install, false);
    var rejected = false; try { state.BeginInspection(b, InstallAction.Remove, false); } catch (InvalidOperationException) { rejected = true; }
    Check(rejected, "a second inspection must not start");
}));
await Test("accepted preview executes only same target action and mode", () => Sync(() =>
{
    var state = new WizardOperationState(); var s = state.BeginInspection(a, InstallAction.Repair, false);
    Check(state.CompleteInspection(s, a, InstallAction.Repair, false), "matching result should be accepted");
    Check(state.CanExecute(a, InstallAction.Repair, false), "matching repair may proceed");
    Check(!state.CanExecute(b, InstallAction.Repair, false), "another target cannot execute");
    Check(!state.CanExecute(a, InstallAction.Remove, false), "another action cannot execute");
    Check(!state.CanExecute(a, InstallAction.Repair, true), "readonly mode cannot execute");
    state.InvalidateSelection(); Check(!state.CanExecute(a, InstallAction.Repair, false), "selection changes discard approval");
}));
await Test("readonly result cannot authorize repair", () => Sync(() =>
{
    var state = new WizardOperationState(); var s = state.BeginInspection(a, InstallAction.Repair, true);
    Check(state.CompleteInspection(s, a, InstallAction.Repair, true), "readonly result accepted for display");
    Check(!state.CanExecute(a, InstallAction.Repair, false), "verification must not serve as repair preview");
}));
await Test("failed inspection unlocks but leaves no executable preview", () => Sync(() =>
{
    var state = new WizardOperationState(); var s = state.BeginInspection(a, InstallAction.Install, false);
    state.FailInspection(s);
    Check(state.CanChangeSelection && state.Preview is null && !state.CanExecute(a, InstallAction.Install, false), "failure must release lock and invalidate preview");
}));
await Test("cancel plus manual recovery failure keeps result visible", () => Sync(() =>
{
    var result = new OperationResult(false, "Recuperação manual necessária", "receipt.json", "report.json");
    Check(!WizardOperationState.CanAutoClose(true, result), "negative result cannot prove safe recovery");
}));
await Test("message text never upgrades failed recovery", () => Sync(() =>
{
    var result = new OperationResult(false, "Concluído com segurança", "", "report.json");
    Check(!WizardOperationState.CanAutoClose(true, result), "text must not override structured Success=false");
}));
await Test("missing result keeps window visible", () => Sync(() => Check(!WizardOperationState.CanAutoClose(true, null), "missing result is not safe confirmation")));
await Test("successful result closes only after explicit close request", () => Sync(() =>
{
    var result = new OperationResult(true, "", "receipt.json", "report.json");
    Check(WizardOperationState.CanAutoClose(true, result), "structured success permits requested close");
    Check(!WizardOperationState.CanAutoClose(false, result), "success alone must not close the window");
}));
foreach (var test in RecoveryIntegrationTests.All()) await Test(test.Name, test.Run);
Console.WriteLine($"{total - failures}/{total} PASS; {failures} FAIL");
return failures == 0 ? 0 : 1;
