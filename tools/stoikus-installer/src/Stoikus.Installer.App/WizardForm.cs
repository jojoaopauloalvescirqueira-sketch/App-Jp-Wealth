using System.Diagnostics;
using System.IO.Compression;
using System.Reflection;
using System.Text;
using Stoikus.Installer.Core;

namespace Stoikus.Installer.App;

internal sealed class WizardForm : Form
{
    private static readonly string StateRoot = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "JPWealth", "StoikusInstaller");
    private readonly Panel _host = new() { Dock = DockStyle.Fill, AutoScroll = true, Padding = new Padding(22) };
    private readonly Label _steps = new() { AutoSize = true, MaximumSize = new Size(1000, 0), Padding = new Padding(22, 8, 22, 8) };
    private readonly Button _back = new() { Text = "&Voltar", AutoSize = true };
    private readonly Button _next = new() { Text = "&Continuar", AutoSize = true };
    private readonly Button _cancel = new() { Text = "&Fechar", AutoSize = true };
    private readonly ListBox _targets = new() { Height = 150, Dock = DockStyle.Top, AccessibleName = "Instalações MT5 encontradas", HorizontalScrollbar = true };
    private readonly RadioButton _install = new() { Text = "&Instalar os quatro programas", Checked = true, AutoSize = true };
    private readonly RadioButton _verify = new() { Text = "&Verificar; depois decidir se quer reparar", AutoSize = true };
    private readonly RadioButton _remove = new() { Text = "&Remover esta instalação do Stoikus", AutoSize = true };
    private readonly TextBox _targetDetails = TextView(105, "Caminhos da instalação selecionada");
    private readonly TextBox _inspectionText = TextView(240, "Resultado da conferência e prévia dos arquivos");
    private readonly CheckBox _organize = new() { Text = "&Quero organizar programas legados reconhecidos (opcional)", AutoSize = true, Checked = false };
    private readonly CheckedListBox _legacy = new() { Height = 190, Dock = DockStyle.Top, CheckOnClick = true, Enabled = false, AccessibleName = "Arquivos legados reconhecidos; selecione cada arquivo a organizar" };
    private readonly CheckBox _confirmed = new() { AutoSize = true, Text = "Conferi a prévia e o &destino desta ação." };
    private readonly TextBox _log = TextView(240, "Andamento e detalhes da operação");
    private readonly ProgressBar _progress = new() { Dock = DockStyle.Top, Height = 24, AccessibleName = "Progresso da operação" };
    private readonly Button _run = new() { AutoSize = true };
    private readonly Button _report = new() { AutoSize = true, Text = "Ler &relatório", Enabled = false };
    private readonly Label _outcome = new() { AutoSize = true, MaximumSize = new Size(1000, 0) };
    private readonly Button _manual = new() { Text = "Escolher pasta &manualmente…", AutoSize = true };
    private readonly Button _repair = new() { Text = "&Preparar reparo…", AutoSize = true };
    private readonly Button _recovery = new() { Text = "Ver &recuperação da operação interrompida…", AutoSize = true };
    private readonly Button _reinspect = new() { Text = "Re&inspecionar o destino", AutoSize = true };
    private readonly WizardOperationState _flow = new();
    private InstallerService? _service;
    private TerminalTarget? _target;
    private PreflightResult? _inspection;
    private OperationResult? _result;
    private byte[]? _payloadZip;
    private InstallAction _action;
    private bool _verifyOnly;
    private bool _busy;
    private bool _mutating;
    private bool _closeRequested;
    private int _page;
    private CancellationTokenSource? _cancellation;
    private string _verification = "";
    private bool _verificationCompleted;
    private bool _pendingRecovery;
    private InstallAction _returnAction = InstallAction.Install;
    private bool _returnVerifyOnly;
    private string? _startupError;

    public WizardForm()
    {
        Text = "Stoikus by JP Wealth · Assistente 1.0.0-beta.1";
        AccessibleName = Text;
        AutoScaleMode = AutoScaleMode.Dpi;
        Font = new Font("Segoe UI", 10);
        MinimumSize = new Size(760, 650);
        Size = new Size(960, 820);
        StartPosition = FormStartPosition.CenterScreen;
        var layout = new TableLayoutPanel { Dock = DockStyle.Fill, ColumnCount = 1, RowCount = 4 };
        layout.RowStyles.Add(new RowStyle(SizeType.AutoSize));
        layout.RowStyles.Add(new RowStyle(SizeType.AutoSize));
        layout.RowStyles.Add(new RowStyle(SizeType.Percent, 100));
        layout.RowStyles.Add(new RowStyle(SizeType.AutoSize));
        var identity = new TableLayoutPanel { AutoSize = true, Dock = DockStyle.Fill, ColumnCount = 1, Padding = new Padding(22, 16, 22, 8) };
        identity.Controls.Add(new SignaturePictureBox { Margin = new Padding(0, 0, 0, 8) });
        identity.Controls.Add(new Label { Text = "Produto 1.23.0  ·  BETA NÃO ASSINADA\nInstalação offline · Windows x64 · cálculo 1.9.0", AutoSize = true, Font = new Font(Font, FontStyle.Bold), Margin = new Padding(0) });
        layout.Controls.Add(identity);
        layout.Controls.Add(_steps);
        layout.Controls.Add(_host);
        var footer = new FlowLayoutPanel { AutoSize = true, Dock = DockStyle.Fill, FlowDirection = FlowDirection.RightToLeft, Padding = new Padding(16) };
        footer.Controls.AddRange([_cancel, _next, _back]);
        layout.Controls.Add(footer);
        Controls.Add(layout);
        AcceptButton = _next;
        _back.Click += (_, _) => ShowPage(_page == 4 && _verifyOnly ? 1 : Math.Max(0, _page - 1));
        _next.Click += async (_, _) => await NextAsync();
        _cancel.Click += (_, _) => RequestClose();
        _targets.SelectedIndexChanged += (_, _) => TargetChanged();
        _install.CheckedChanged += (_, _) => ActionChoiceChanged();
        _verify.CheckedChanged += (_, _) => ActionChoiceChanged();
        _remove.CheckedChanged += (_, _) => ActionChoiceChanged();
        _manual.Click += (_, _) => ChooseManualTarget();
        _repair.Click += async (_, _) =>
        {
            if (_busy || !_flow.CanChangeSelection) return;
            InvalidatePreview();
            _verifyOnly = false; _action = InstallAction.Repair;
            await InspectAsync();
        };
        _recovery.Click += async (_, _) =>
        {
            if (!_flow.CanOfferRecovery(_pendingRecovery, _busy)) return;
            _returnAction = _action; _returnVerifyOnly = _verifyOnly;
            InvalidatePreview();
            _action = InstallAction.Recover; _verifyOnly = false;
            await InspectAsync();
        };
        _reinspect.Click += async (_, _) => await ReinspectAfterRecoveryAsync();
        _organize.CheckedChanged += (_, _) =>
        {
            _legacy.Enabled = _organize.Checked;
            if (!_organize.Checked) for (int i = 0; i < _legacy.Items.Count; i++) _legacy.SetItemChecked(i, false);
        };
        _confirmed.CheckedChanged += (_, _) => UpdateNavigation();
        _run.Click += async (_, _) => await ExecuteAsync();
        _report.Click += (_, _) => ReadReport();
        FormClosing += OnFormClosing;
        Shown += async (_, _) => await LoadServiceAsync();
        ShowPage(0);
    }

    private static TextBox TextView(int height, string name) => new()
    {
        Multiline = true, ReadOnly = true, ScrollBars = ScrollBars.Both, WordWrap = false,
        Dock = DockStyle.Top, Height = height, AccessibleName = name, BackColor = SystemColors.Window
    };

    private static Label Paragraph(string text) => new() { Text = text, AutoSize = true, MaximumSize = new Size(1020, 0), Margin = new Padding(0, 5, 0, 10) };

    private static byte[] Resource(string name)
    {
        using var stream = Assembly.GetExecutingAssembly().GetManifestResourceStream(name)
            ?? throw new InvalidDataException($"O arquivo incorporado {name} está ausente. Obtenha novamente o instalador completo pela distribuição oficial.");
        using var memory = new MemoryStream();
        stream.CopyTo(memory);
        return memory.ToArray();
    }

    private async Task LoadServiceAsync()
    {
        SetBusy(true);
        try
        {
            var discovered = await Task.Run(() =>
            {
                _payloadZip = Resource("Stoikus.Payload.zip");
                _service = new InstallerService(_payloadZip, Resource("Stoikus.Payload.json"), StateRoot);
                return _service.DiscoverTargets();
            });
            foreach (var target in discovered) _targets.Items.Add(new TargetItem(target));
            _targets.SelectedIndex = -1;
            _targetDetails.Text = discovered.Count == 0
                ? "Nenhuma instalação encontrada. Use Escolher pasta manualmente e confira o destino no próprio MT5."
                : "Selecione uma instalação, mesmo que a lista contenha apenas uma.";
        }
        catch (Exception ex)
        {
            _startupError = "Não foi possível preparar o instalador. Nenhum programa foi instalado.\r\n" + ex.Message + "\r\nObtenha uma cópia íntegra da distribuição oficial. Se o problema persistir, envie estes detalhes ao suporte.";
            _targetDetails.Text = _startupError;
        }
        finally { SetBusy(false); ShowPage(0); }
    }

    private void TargetChanged()
    {
        _target = (_targets.SelectedItem as TargetItem)?.Target;
        InvalidatePreview();
        if (_target is not null)
            _targetDetails.Text = $"Pasta de dados (destino MQL5): {_target.DataDirectory}\r\nPrograma MT5: {_target.TerminalExe}\r\nMetaEditor: {_target.MetaEditorExe}\r\nModo portátil declarado: {(_target.Portable ? "sim" : "não")}";
        UpdateNavigation();
    }

    private void ActionChoiceChanged()
    {
        InvalidatePreview();
        _verifyOnly = _verify.Checked;
        _action = _remove.Checked ? InstallAction.Remove : _verifyOnly ? InstallAction.Repair : InstallAction.Install;
        UpdateNavigation();
    }

    private void InvalidatePreview()
    {
        _flow.InvalidateSelection();
        _inspection = null;
        _result = null;
        _verification = ""; _verificationCompleted = false;
        _pendingRecovery = false;
        _confirmed.Checked = false;
        _organize.Checked = false;
        _legacy.Items.Clear();
        _inspectionText.Clear();
    }

    private void ShowPage(int page)
    {
        _page = page;
        _host.Controls.Clear();
        _steps.Text = $"{page + 1} de 5  ·  " + new[] { "Escolher instalação", "Conferir a prévia", "Organizar e confirmar", _action == InstallAction.Recover ? "Recuperar operação" : _action == InstallAction.Remove ? "Aplicar remoção" : "Compilar e aplicar", "Guia e próximos passos" }[page];
        var body = new TableLayoutPanel { Dock = DockStyle.Top, AutoSize = true, ColumnCount = 1, Padding = new Padding(0), GrowStyle = TableLayoutPanelGrowStyle.AddRows };
        body.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 100));
        _host.Controls.Add(body);
        void Add(Control c)
        {
            c.Margin = new Padding(0, 5, 0, 10);
            if (c is TextBox or ListBox or ProgressBar) c.Width = Math.Max(540, _host.ClientSize.Width - 60);
            if (c is Label) c.MaximumSize = new Size(Math.Max(540, _host.ClientSize.Width - 70), 0);
            body.Controls.Add(c);
        }
        switch (page)
        {
            case 0:
                Add(Paragraph("Escolha a ação e a instalação MT5. No terminal, Arquivo → Abrir pasta de dados mostra a pasta que deve coincidir com o destino abaixo. Feche o terminal e o MetaEditor antes de aplicar alterações."));
                Add(_install); Add(_verify); Add(_remove);
                Add(Paragraph("Instalações encontradas — nenhuma é selecionada automaticamente:")); Add(_targets); Add(_targetDetails);
                Add(_manual);
                if (_startupError is not null) Add(Paragraph(_startupError));
                Add(Paragraph("Este assistente instala e compila quatro programas. Ele não abre o MT5, não anexa programas aos gráficos e não ativa negociação. Por ser beta não assinada, sua origem e os hashes publicados devem ser conferidos antes do uso."));
                break;
            case 1:
                Add(Paragraph(_verifyOnly ? "Verificação somente leitura: nenhum reparo foi aplicado." : "Confira o destino, os impedimentos e todos os arquivos previstos antes de continuar."));
                Add(_targetDetails); Add(_inspectionText);
                if (_action == InstallAction.Recover)
                    Add(Paragraph("Esta ação recupera somente a operação interrompida descrita no diário. Ela não compila nem instala novos programas. Confira os arquivos que serão restaurados ou retirados; conflitos permanecem protegidos. Depois da recuperação será necessária nova conferência para a ação original."));
                if (_pendingRecovery && _action != InstallAction.Recover)
                {
                    Add(Paragraph("Há uma operação interrompida neste destino. A recuperação possui prévia e confirmação próprias; ela está disponível mesmo quando a instalação, reparo ou remoção estiverem bloqueados."));
                    Add(_recovery);
                }
                if (_verifyOnly)
                {
                    Add(_repair);
                    Add(Paragraph("Preparar reparo produz outra prévia. A gravação exige confirmação nas próximas etapas. Você também pode continuar para o guia sem reparar."));
                }
                break;
            case 2:
                if (_action == InstallAction.Recover)
                    Add(Paragraph("Confirme apenas a recuperação da operação interrompida. Nenhum legado será organizado e nenhuma instalação será iniciada. A prévia da ação original será refeita depois."));
                else
                {
                    Add(Paragraph("Organização opcional: somente arquivos reconhecidos pelo catálogo podem ser selecionados. Cada seleção será enviada ao motor para validação e backup; arquivos desconhecidos não entram nesta lista."));
                    Add(_organize); Add(_legacy);
                    Add(Paragraph(_legacy.Items.Count == 0 ? "Nenhum candidato elegível nesta prévia." : "Nada está marcado por padrão. Espaço marca ou desmarca o item em foco."));
                }
                _confirmed.Text = _action == InstallAction.Recover ? "Conferi a prévia e o &destino da recuperação." : "Conferi a prévia e o &destino desta ação.";
                Add(_confirmed);
                Add(Paragraph("Os arquivos de dados, estudos, preferências e locks não fazem parte desta ação. Os relatórios e backups ficam fora do MQL5, na pasta local do assistente."));
                break;
            case 3:
                Add(Paragraph($"Ação: {ActionName()}. Destino: {_target?.DataDirectory}"));
                Add(_run); Add(_progress); Add(_outcome); Add(_log); Add(_report);
                if (_action == InstallAction.Recover) Add(_reinspect);
                Add(Paragraph("Durante uma alteração, Cancelar solicita uma parada segura ao motor. Aguarde a conclusão ou recuperação antes de fechar a janela. O resumo só informa sucesso quando o motor o confirma."));
                break;
            case 4:
                Add(Paragraph(_verifyOnly ? _verificationCompleted ? "A chamada de verificação terminou sem aplicar reparo. Use Voltar para reler o resultado, inclusive eventuais arquivos ausentes ou modificados." : "A verificação não foi concluída. Nenhum reparo foi aplicado." : _result?.Success == true ? _action == InstallAction.Remove ? "Remoção concluída segundo o motor. Os guias abaixo são referência para uma futura instalação; esta ação não preparou os programas para abertura." : "A ação foi concluída segundo o motor. Abertura, configuração e validação de uso no MT5 são etapas manuais separadas." : "Não há confirmação de instalação concluída nesta sessão. Resolva os detalhes antes de usar os programas."));
                if (_action != InstallAction.Remove)
                    Add(Paragraph("Após confirmar uma instalação íntegra:\n1. Abra manualmente o MT5 escolhido.\n2. Reserve um gráfico de apoio para o Monitor e mantenha-o aberto. Retire Observer e Accountant legados de TODOS os gráficos antes.\n3. No gráfico de trabalho, execute Abrir Painéis para acrescentar Conta + NoCuda ao mesmo gráfico.\n4. Confira Ctrl+I e Caixa de ferramentas → Experts. Um script loaded/removed pode ter terminado normalmente; isso não prova a saúde dos indicadores."));
                var guide = new Button { Text = "Abrir &guia ilustrado offline", AutoSize = true };
                guide.Click += (_, _) => OpenGuide(); Add(guide);
                var daily = new Button { Text = "Ler guia &detalhado do pacote", AutoSize = true, Enabled = _service is not null };
                daily.Click += (_, _) => ReadDailyGuide(); Add(daily);
                Add(Paragraph("No Monitor, mantenha Permitir negociação algorítmica desmarcado. Comece com cobertura false / false / evidência vazia. Presença do programa, qualidade da amostra e completude do histórico são fatos diferentes."));
                break;
        }
        UpdateNavigation();
    }

    private string ActionName() => _action switch { InstallAction.Recover => "Recuperar operação interrompida", InstallAction.Repair => "Reparar", InstallAction.Remove => "Remover", _ => "Instalar" };

    private void UpdateNavigation()
    {
        var selectionEnabled = !_busy && _flow.CanChangeSelection;
        _targets.Enabled = selectionEnabled;
        _install.Enabled = selectionEnabled; _verify.Enabled = selectionEnabled; _remove.Enabled = selectionEnabled;
        _manual.Enabled = selectionEnabled && _service is not null;
        _repair.Enabled = selectionEnabled;
        _recovery.Enabled = _flow.CanOfferRecovery(_pendingRecovery, _busy);
        _reinspect.Enabled = !_busy && _result is not null;
        _organize.Enabled = !_busy && _legacy.Items.Count > 0;
        _legacy.Enabled = !_busy && _organize.Checked;
        _confirmed.Enabled = !_busy;
        _back.Enabled = !_busy && _page > 0 && !(_page == 3 && _result is not null);
        _next.Text = _page == 3 && _action == InstallAction.Recover ? "Re&inspecionar destino" : _page == 4 ? "&Concluir" : _page == 1 && _verifyOnly ? "Continuar para o &guia" : "&Continuar";
        _next.Enabled = !_busy && (_page switch
        {
            0 => _service is not null && _target is not null,
            1 => _verifyOnly ? _flow.Preview is { VerifyOnly: true } : HasCurrentPreview(),
            2 => _confirmed.Checked && HasCurrentPreview(),
            3 => _action == InstallAction.Recover ? _result?.Success == true : _result is not null,
            _ => true
        });
        _cancel.Text = _mutating ? "&Cancelar com segurança" : "&Fechar";
        _run.Enabled = !_busy && _result is null && HasCurrentPreview();
        _run.Text = _action == InstallAction.Recover ? "Confirmar &recuperação…" : _action == InstallAction.Remove ? "Confirmar &remoção…" : "&Compilar e " + (_action == InstallAction.Repair ? "reparar…" : "instalar…");
        _report.Enabled = !_busy && _result is not null && !string.IsNullOrWhiteSpace(_result.ReportPath);
    }

    private void SetBusy(bool value) { _busy = value; UseWaitCursor = value; UpdateNavigation(); }

    private bool HasCurrentPreview() => _target is not null && _inspection?.CanProceed == true && _flow.CanExecute(_target, _action, _verifyOnly);

    private async Task NextAsync()
    {
        if (_busy || !_next.Enabled) return;
        if (_page == 0)
        {
            _verifyOnly = _verify.Checked;
            _action = _remove.Checked ? InstallAction.Remove : _verifyOnly ? InstallAction.Repair : InstallAction.Install;
            _verification = "";
            _verificationCompleted = false;
            _confirmed.Checked = false;
            _organize.Checked = false;
            _result = null;
            _log.Clear(); _outcome.Text = "Aguardando sua confirmação."; _progress.Value = 0;
            await InspectAsync();
        }
        else if (_page == 1 && _verifyOnly) ShowPage(4);
        else if (_page == 2 && _confirmed.Checked && HasCurrentPreview()) ShowPage(3);
        else if (_page == 3 && _action == InstallAction.Recover) await ReinspectAfterRecoveryAsync();
        else if (_page == 4) Close();
        else ShowPage(_page + 1);
    }

    private async Task InspectAsync()
    {
        if (_busy || !_flow.CanChangeSelection || _service is null || _target is null) return;
        var service = _service;
        var selection = _flow.BeginInspection(_target, _action, _verifyOnly);
        var accepted = false;
        SetBusy(true);
        try
        {
            var pendingRecovery = await Task.Run(() => service.HasPendingRecovery(selection.Target));
            var verification = selection.VerifyOnly ? await Task.Run(() => service.Verify(selection.Target)) : "";
            var inspection = selection.VerifyOnly ? null : await Task.Run(() => service.Inspect(selection.Target, selection.Action));
            accepted = _flow.CompleteInspection(selection, _target, _action, _verifyOnly);
            if (!accepted) return;
            _verification = verification; _verificationCompleted = selection.VerifyOnly;
            _pendingRecovery = pendingRecovery;
            _inspection = inspection;
            _inspectionText.Text = selection.VerifyOnly ? verification : FormatInspection(inspection!);
            _legacy.Items.Clear();
            if (!selection.VerifyOnly && selection.Action is not (InstallAction.Remove or InstallAction.Recover))
                foreach (var candidate in _inspection!.LegacyCandidates.Where(c => c.CanOrganize)) _legacy.Items.Add(new LegacyItem(candidate), false);
            _organize.Checked = false;
            _organize.Enabled = _legacy.Items.Count > 0;
        }
        catch (Exception ex)
        {
            accepted = _flow.Matches(selection, _target, _action, _verifyOnly);
            _flow.FailInspection(selection);
            _inspection = null; _verificationCompleted = false;
            if (accepted) _inspectionText.Text = "Conferência não concluída.\r\n" + ex.Message;
        }
        finally { SetBusy(false); ShowPage(accepted ? 1 : 0); }
    }

    private string FormatInspection(PreflightResult inspection)
    {
        var text = new StringBuilder($"{ActionName()}: {(inspection.CanProceed ? "prévia disponível" : "há impedimentos")}\r\n");
        foreach (var problem in inspection.Problems) text.AppendLine("• " + problem);
        text.AppendLine("\r\nArquivos previstos:");
        foreach (var file in inspection.Changes) text.AppendLine($"{file.Kind}: {file.RelativePath}\r\n  {file.Detail}");
        if (inspection.Changes.Count == 0) text.AppendLine("Nenhuma alteração listada pelo motor.");
        return text.ToString();
    }

    private async Task ExecuteAsync()
    {
        if (_busy || _service is null || _target is null || !HasCurrentPreview() || !_confirmed.Checked) return;
        var selection = _flow.Preview!;
        var service = _service;
        var selected = selection.Action != InstallAction.Recover && _organize.Checked ? _legacy.CheckedItems.Cast<LegacyItem>().Select(i => i.Change.RelativePath).ToArray() : [];
        if (MessageBox.Show(this, $"{ActionName()} no destino abaixo?\n\n{_target.DataDirectory}\n\nArquivos legados selecionados: {selected.Length}.\nConsulte a prévia antes de confirmar.", "Confirmar " + ActionName().ToLowerInvariant(), MessageBoxButtons.YesNo, MessageBoxIcon.Question, MessageBoxDefaultButton.Button2) != DialogResult.Yes) return;
        var confirmed = _flow.ConfirmedSelection(_target, _action, _verifyOnly, true, _inspection?.CanProceed == true);
        if (confirmed != selection) return;
        _cancellation = new CancellationTokenSource();
        _mutating = true; SetBusy(true);
        var progress = new Progress<InstallProgress>(p =>
        {
            _outcome.Text = p.Message;
            _log.AppendText($"[{p.Stage}] {p.Message}\r\n");
            _progress.Style = p.Total > 0 ? ProgressBarStyle.Continuous : ProgressBarStyle.Marquee;
            if (p.Total > 0) _progress.Value = (int)Math.Clamp((long)p.Completed * 100 / p.Total, 0, 100);
        });
        try
        {
            _result = await Task.Run(() => service.ExecuteAsync(selection.Target, selection.Action, selected, progress, _cancellation.Token));
            _outcome.Text = (_result.Success ? "Concluído: " : "Não concluído: ") + _result.Message;
            if (_flow.CompleteRecovery(selection.Action, _result))
            {
                _inspection = null; _confirmed.Checked = false; _pendingRecovery = false;
                _outcome.Text = "Recuperação concluída. Reinspecione o destino para decidir sobre a ação original; nenhuma nova instalação foi executada.";
            }
            _log.AppendText(_outcome.Text + "\r\n");
            if (_result.Success) _progress.Value = 100;
        }
        catch (OperationCanceledException) { _outcome.Text = "Cancelamento recebido. Sem confirmação final do motor: confira os relatórios e execute nova conferência antes de repetir."; }
        catch (Exception ex) { _outcome.Text = "O motor não confirmou a conclusão. Preserve os registros e confira a instalação antes de repetir.\r\n" + ex.Message; _log.AppendText(_outcome.Text + "\r\n"); }
        finally
        {
            _progress.Style = ProgressBarStyle.Continuous;
            _mutating = false; _cancellation.Dispose(); _cancellation = null; SetBusy(false);
            if (WizardOperationState.CanAutoClose(_closeRequested, _result)) BeginInvoke(new Action(Close));
            else if (_closeRequested)
            {
                _closeRequested = false; _cancel.Enabled = true;
                MessageBox.Show(this, "A operação não foi confirmada como concluída com sucesso. A janela permanecerá aberta para mostrar a falha e o relatório, inclusive eventual recuperação manual pendente. Leia os detalhes; depois você pode fechar explicitamente.", "Conclusão não confirmada", MessageBoxButtons.OK, MessageBoxIcon.Information);
            }
        }
    }

    private void RequestClose()
    {
        if (!_mutating) { if (!_busy) Close(); return; }
        if (_closeRequested) return;
        if (MessageBox.Show(this, "Solicitar cancelamento seguro? O assistente aguardará o motor concluir ou recuperar a operação antes de fechar.", "Cancelar operação", MessageBoxButtons.YesNo, MessageBoxIcon.Question, MessageBoxDefaultButton.Button2) != DialogResult.Yes) return;
        _closeRequested = true; _cancellation?.Cancel();
        _outcome.Text = "Cancelamento solicitado. Aguarde o motor terminar com segurança.";
        _cancel.Enabled = false;
    }

    private async Task ReinspectAfterRecoveryAsync()
    {
        if (_busy || _action != InstallAction.Recover || _result is null) return;
        InvalidatePreview();
        _action = _returnAction; _verifyOnly = _returnVerifyOnly;
        _outcome.Text = "Aguardando sua confirmação."; _log.Clear(); _progress.Value = 0;
        await InspectAsync();
    }

    private void OnFormClosing(object? sender, FormClosingEventArgs e)
    {
        if (_mutating) { e.Cancel = true; RequestClose(); }
        else if (_busy) e.Cancel = true;
    }

    private void ChooseManualTarget()
    {
        if (_busy || !_flow.CanChangeSelection) return;
        using var dialog = new ManualTargetForm();
        if (dialog.ShowDialog(this) != DialogResult.OK || dialog.Target is null) return;
        _targets.Items.Add(new TargetItem(dialog.Target));
        _targets.SelectedIndex = _targets.Items.Count - 1;
    }

    private void ShowText(string title, string content)
    {
        using var dialog = new Form { Text = title, Size = new Size(880, 680), MinimumSize = new Size(600, 400), StartPosition = FormStartPosition.CenterParent, AutoScaleMode = AutoScaleMode.Dpi };
        var view = TextView(500, title); view.Dock = DockStyle.Fill; view.Text = content;
        dialog.Controls.Add(view); dialog.ShowDialog(this);
    }

    private static bool IsSafeLocalFile(string path)
    {
        var root = Path.GetFullPath(StateRoot).TrimEnd(Path.DirectorySeparatorChar) + Path.DirectorySeparatorChar;
        var full = Path.GetFullPath(path);
        if (!full.StartsWith(root, StringComparison.OrdinalIgnoreCase) || !File.Exists(full)) return false;
        for (string? p = full; p is not null; p = Path.GetDirectoryName(p))
            if ((File.Exists(p) || Directory.Exists(p)) && (File.GetAttributes(p) & FileAttributes.ReparsePoint) != 0) return false;
        return new FileInfo(full).Length <= 10 * 1024 * 1024;
    }

    private void ReadReport()
    {
        try
        {
            var path = _result?.ReportPath;
            if (string.IsNullOrWhiteSpace(path) || !IsSafeLocalFile(path)) throw new IOException("O relatório não é um arquivo local regular da pasta de estado do assistente, ou excede o limite de leitura.");
            ShowText("Relatório da operação — somente leitura", File.ReadAllText(path));
        }
        catch (Exception ex) { MessageBox.Show(this, ex.Message, "Relatório indisponível", MessageBoxButtons.OK, MessageBoxIcon.Information); }
    }

    private void OpenGuide()
    {
        try
        {
            // Only fixed trusted embedded HTML can be opened; report contents never become navigation targets.
            var directory = Path.Combine(StateRoot, "guides", Guid.NewGuid().ToString("N"));
            for (string? p = directory; p is not null; p = Path.GetDirectoryName(p))
                if (Directory.Exists(p) && (File.GetAttributes(p) & FileAttributes.ReparsePoint) != 0) throw new IOException("Pasta do guia contém um redirecionamento de sistema.");
            Directory.CreateDirectory(directory);
            var path = Path.Combine(directory, "guia-primeiro-uso.html");
            using (var file = new FileStream(path, FileMode.CreateNew, FileAccess.Write, FileShare.None)) file.Write(Resource("Stoikus.Guide.html"));
            Process.Start(new ProcessStartInfo(new Uri(path).AbsoluteUri) { UseShellExecute = true });
        }
        catch (Exception ex) { MessageBox.Show(this, "Não foi possível abrir o guia no navegador.\n" + ex.Message, "Guia offline", MessageBoxButtons.OK, MessageBoxIcon.Information); }
    }

    private void ReadDailyGuide()
    {
        try
        {
            if (_payloadZip is null || _service is null) throw new IOException("O pacote ainda não foi validado.");
            using var archive = new ZipArchive(new MemoryStream(_payloadZip), ZipArchiveMode.Read);
            var entry = archive.GetEntry("LEIA_PRIMEIRO.md") ?? throw new IOException("O guia detalhado não foi encontrado no pacote.");
            if (entry.Length > 2 * 1024 * 1024) throw new IOException("Tamanho do guia inesperado.");
            using var reader = new StreamReader(entry.Open(), Encoding.UTF8);
            ShowText("Guia detalhado do pacote 1.23.0 — texto original", reader.ReadToEnd());
        }
        catch (Exception ex) { MessageBox.Show(this, ex.Message, "Guia detalhado indisponível", MessageBoxButtons.OK, MessageBoxIcon.Information); }
    }

    private sealed record TargetItem(TerminalTarget Target)
    {
        public override string ToString() => $"{Path.GetDirectoryName(Target.TerminalExe)}  →  {Target.DataDirectory}";
    }
    private sealed record LegacyItem(FileChange Change)
    {
        public override string ToString() => $"{Change.RelativePath} — {Change.Detail}";
    }
}
