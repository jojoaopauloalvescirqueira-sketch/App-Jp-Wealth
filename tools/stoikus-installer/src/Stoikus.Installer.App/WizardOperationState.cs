using Stoikus.Installer.Core;

namespace Stoikus.Installer.App;

internal sealed record InspectionSelection(long Revision, TerminalTarget Target, InstallAction Action, bool VerifyOnly)
{
    public long Request { get; init; }
}

internal sealed class WizardOperationState
{
    private long _revision;
    private long _request;
    private InspectionSelection? _running;
    public InspectionSelection? Preview { get; private set; }
    public bool CanChangeSelection => _running is null;

    // Recovery discovery is independent of the normal installation/repair/removal preview.
    public bool CanOfferRecovery(bool pendingRecovery, bool busy) => pendingRecovery && !busy && CanChangeSelection;

    public InspectionSelection? ConfirmedSelection(TerminalTarget target, InstallAction action, bool verifyOnly, bool confirmed, bool previewCanProceed) =>
        confirmed && previewCanProceed && CanExecute(target, action, verifyOnly) ? Preview : null;

    public bool CompleteRecovery(InstallAction action, OperationResult result)
    {
        if (action != InstallAction.Recover || !result.Success) return false;
        InvalidateSelection();
        return true;
    }

    public void InvalidateSelection()
    {
        _revision++;
        Preview = null;
    }

    public InspectionSelection BeginInspection(TerminalTarget target, InstallAction action, bool verifyOnly)
    {
        if (_running is not null) throw new InvalidOperationException("Já existe uma conferência em andamento.");
        Preview = null;
        _running = new InspectionSelection(_revision, target, action, verifyOnly) { Request = ++_request };
        return _running;
    }

    public bool CompleteInspection(InspectionSelection snapshot, TerminalTarget? target, InstallAction action, bool verifyOnly)
    {
        if (_running != snapshot) return false;
        _running = null;
        if (!Matches(snapshot, target, action, verifyOnly)) return false;
        Preview = snapshot;
        return true;
    }

    public void FailInspection(InspectionSelection snapshot)
    {
        if (_running != snapshot) return;
        _running = null;
        Preview = null;
    }

    public bool CanExecute(TerminalTarget target, InstallAction action, bool verifyOnly) =>
        _running is null && !verifyOnly && Preview is { VerifyOnly: false } preview && Matches(preview, target, action, verifyOnly);

    public bool Matches(InspectionSelection snapshot, TerminalTarget? target, InstallAction action, bool verifyOnly) =>
        snapshot.Revision == _revision && snapshot.Target == target && snapshot.Action == action && snapshot.VerifyOnly == verifyOnly;

    // The API has no structured safe-rollback state. A negative or missing result must remain visible.
    public static bool CanAutoClose(bool requested, OperationResult? result) => requested && result?.Success == true;
}
