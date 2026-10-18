using System.Reflection;

namespace Stoikus.Installer.App;

/// <summary>Approved 240×28 signature, using a 2× raster for DPI scaling.</summary>
internal sealed class SignaturePictureBox : PictureBox
{
    private readonly Image? _light;
    private readonly Image? _dark;

    public SignaturePictureBox()
    {
        Size = new Size(240, 28);
        SizeMode = PictureBoxSizeMode.Zoom;
        AccessibleName = "Stoikus by JP Wealth";
        AccessibleRole = AccessibleRole.Graphic;
        TabStop = false;
        _light = ReadImage("Stoikus.Brand.Light.png");
        _dark = ReadImage("Stoikus.Brand.Dark.png");
        ApplyTheme();
    }

    private static Image ReadImage(string name)
    {
        using var stream = Assembly.GetExecutingAssembly().GetManifestResourceStream(name)
            ?? throw new InvalidDataException("Assinatura incorporada ausente: " + name);
        using var image = Image.FromStream(stream);
        return new Bitmap(image); // Detach the bitmap from its resource stream before disposal.
    }

    private void ApplyTheme() => Image = BackColor.GetBrightness() < .5f ? _dark : _light;

    protected override void OnBackColorChanged(EventArgs e)
    {
        base.OnBackColorChanged(e);
        ApplyTheme();
    }

    protected override void OnSystemColorsChanged(EventArgs e)
    {
        base.OnSystemColorsChanged(e);
        ApplyTheme();
    }

    protected override void Dispose(bool disposing)
    {
        if (disposing)
        {
            Image = null;
            _light?.Dispose();
            _dark?.Dispose();
        }
        base.Dispose(disposing);
    }
}
