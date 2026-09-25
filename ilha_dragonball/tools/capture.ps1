param(
    [int]$Count = 1,
    [double]$IntervalSec = 0.3,
    [string]$Prefix = "f",
    [string]$OutDir = "C:\Users\lucas\AppData\Local\Temp\claude\C--Users-lucas-OneDrive-Desktop-To-up\47322845-c826-4095-8966-df3813237567\scratchpad\video_frames"
)
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
Add-Type @"
using System; using System.Runtime.InteropServices;
public struct RECT2 { public int Left; public int Top; public int Right; public int Bottom; }
public struct POINT2 { public int X; public int Y; }
public class W5 {
  [DllImport("user32.dll")] public static extern bool GetClientRect(IntPtr h, out RECT2 r);
  [DllImport("user32.dll")] public static extern bool ClientToScreen(IntPtr h, ref POINT2 p);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int c);
  [DllImport("user32.dll")] public static extern bool SetWindowPos(IntPtr h, IntPtr after, int x, int y, int cx, int cy, uint f);
  public const uint FLAGS = 0x0002 | 0x0001 | 0x0040;
  public static readonly IntPtr TOP = new IntPtr(-1);
  public static readonly IntPtr NOTOP = new IntPtr(-2);
}
"@
$proc = Get-Process RobloxStudioBeta -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -ne '' } | Select-Object -First 1
if (-not $proc) { Write-Error "Roblox Studio nao encontrado"; exit 1 }
$h = $proc.MainWindowHandle
[W5]::ShowWindow($h, 3) | Out-Null          # SW_MAXIMIZE (nunca usar 9/SW_RESTORE aqui: desmaximiza)
[W5]::SetWindowPos($h, [W5]::TOP, 0,0,0,0, [W5]::FLAGS) | Out-Null
[W5]::SetWindowPos($h, [W5]::NOTOP, 0,0,0,0, [W5]::FLAGS) | Out-Null
Start-Sleep -Milliseconds 150
$cr = New-Object RECT2
[void][W5]::GetClientRect($h, [ref]$cr)
$topLeft = New-Object POINT2
$topLeft.X = 0; $topLeft.Y = 0
[void][W5]::ClientToScreen($h, [ref]$topLeft)
$width = $cr.Right - $cr.Left
$height = $cr.Bottom - $cr.Top
if ($width -gt 1370) { $width = 1370 }  # evita a sobreposicao do painel do Claude Code (lado direito)
if (-not (Test-Path $OutDir)) { New-Item -ItemType Directory -Path $OutDir -Force | Out-Null }
$saved = @()
for ($i = 0; $i -lt $Count; $i++) {
    $bmp = New-Object System.Drawing.Bitmap $width, $height
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.CopyFromScreen($topLeft.X, $topLeft.Y, 0, 0, (New-Object System.Drawing.Size $width, $height))
    $ts = [DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds()
    $path = Join-Path $OutDir ("{0}_{1:D4}_{2}.png" -f $Prefix, $i, $ts)
    $bmp.Save($path, [System.Drawing.Imaging.ImageFormat]::Png)
    $g.Dispose(); $bmp.Dispose()
    $saved += $path
    if ($i -lt ($Count - 1)) { Start-Sleep -Milliseconds ([int]($IntervalSec * 1000)) }
}
$saved
