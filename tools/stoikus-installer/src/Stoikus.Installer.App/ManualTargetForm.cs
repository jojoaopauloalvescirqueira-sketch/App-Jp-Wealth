using Stoikus.Installer.Core;

namespace Stoikus.Installer.App;

internal sealed class ManualTargetForm : Form
{
    private readonly TextBox _data = new() { ReadOnly = true, Dock = DockStyle.Fill, AccessibleName = "Pasta de dados selecionada" };
    private readonly TextBox _terminal = new() { ReadOnly = true, Dock = DockStyle.Fill, AccessibleName = "Executável MT5 selecionado" };
    private readonly CheckBox _portable = new() { Text = "Esta instalação usa explicitamente o modo &portátil (/portable).", AutoSize = true };
    public TerminalTarget? Target { get; private set; }

    public ManualTargetForm()
    {
        Text = "Selecionar instalação MT5 manualmente";
        Size = new Size(820, 430); MinimumSize = new Size(680, 400); StartPosition = FormStartPosition.CenterParent;
        AutoScaleMode = AutoScaleMode.Dpi; Font = new Font("Segoe UI", 10);
        var body = new TableLayoutPanel { Dock = DockStyle.Fill, ColumnCount = 1, AutoScroll = true, Padding = new Padding(20) };
        void Add(Control control) { control.Margin = new Padding(0, 4, 0, 8); body.Controls.Add(control); }
        Add(new Label { AutoSize = true, MaximumSize = new Size(740, 0), Text = "No MT5 correto, use Arquivo → Abrir pasta de dados. Escolha essa pasta e o terminal64.exe correspondente. O MetaEditor deve existir ao lado desse executável. Feche ambos antes de continuar." });
        var dataButton = new Button { Text = "Escolher pasta de &dados…", AutoSize = true };
        dataButton.Click += (_, _) => { using var picker = new FolderBrowserDialog { Description = "Pasta mostrada pelo MT5 em Arquivo → Abrir pasta de dados", UseDescriptionForTitle = true, ShowNewFolderButton = false }; if (picker.ShowDialog(this) == DialogResult.OK) _data.Text = picker.SelectedPath; };
        Add(dataButton); Add(_data);
        var terminalButton = new Button { Text = "Escolher &terminal64.exe…", AutoSize = true };
        terminalButton.Click += (_, _) => { using var picker = new OpenFileDialog { Filter = "Terminal MT5|terminal64.exe", CheckFileExists = true, Title = "Executável do MT5 correspondente à pasta de dados" }; if (picker.ShowDialog(this) == DialogResult.OK) _terminal.Text = picker.FileName; };
        Add(terminalButton); Add(_terminal); Add(_portable);
        Add(new Label { AutoSize = true, MaximumSize = new Size(740, 0), Text = "Modo portátil exige dados e executáveis na mesma pasta. Uma escolha manual não contorna a verificação de associação nem os impedimentos do motor." });
        var accept = new Button { Text = "&Conferir esta instalação", AutoSize = true };
        accept.Click += (_, _) => AcceptTarget(); Add(accept); AcceptButton = accept;
        var cancel = new Button { Text = "&Cancelar", DialogResult = DialogResult.Cancel, AutoSize = true }; Add(cancel); CancelButton = cancel;
        Controls.Add(body);
    }

    private void AcceptTarget()
    {
        try
        {
            if (!Directory.Exists(_data.Text) || !Directory.Exists(Path.Combine(_data.Text, "MQL5"))) throw new IOException("Escolha a pasta de dados que contém MQL5.");
            if (!File.Exists(_terminal.Text) || !Path.GetFileName(_terminal.Text).Equals("terminal64.exe", StringComparison.OrdinalIgnoreCase)) throw new IOException("Escolha o terminal64.exe dessa instalação.");
            var installation = Path.GetDirectoryName(Path.GetFullPath(_terminal.Text))!;
            var editor = Path.Combine(installation, "metaeditor64.exe");
            if (!File.Exists(editor)) throw new IOException("metaeditor64.exe não foi encontrado ao lado do terminal escolhido.");
            if (_portable.Checked && !Path.GetFullPath(_data.Text).TrimEnd(Path.DirectorySeparatorChar).Equals(installation.TrimEnd(Path.DirectorySeparatorChar), StringComparison.OrdinalIgnoreCase)) throw new IOException("No modo portátil, a pasta de dados deve ser a mesma dos executáveis.");
            Target = new TerminalTarget(Path.GetFullPath(_terminal.Text), Path.GetFullPath(_data.Text), editor, _portable.Checked);
            DialogResult = DialogResult.OK; Close();
        }
        catch (Exception ex) { MessageBox.Show(this, ex.Message, "Confira o destino", MessageBoxButtons.OK, MessageBoxIcon.Information); }
    }
}
