param([int]$SX, [int]$SY, [switch]$Double)
# clique por mensagem de janela (sem foco / sem mouse real) no ponto de TELA (SX, SY) do Roblox Studio
Add-Type @"
using System; using System.Runtime.InteropServices; using System.Text;
public struct PT { public int X; public int Y; }
public class PM {
  [DllImport("user32.dll")] public static extern IntPtr WindowFromPoint(PT p);
  [DllImport("user32.dll")] public static extern bool ScreenToClient(IntPtr h, ref PT p);
  [DllImport("user32.dll")] public static extern bool PostMessage(IntPtr h, uint m, IntPtr w, IntPtr l);
  [DllImport("user32.dll")] public static extern int GetClassName(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
}
"@
$pt = New-Object PT; $pt.X = $SX; $pt.Y = $SY
$h = [PM]::WindowFromPoint($pt)
$pid2 = 0; [void][PM]::GetWindowThreadProcessId($h, [ref]$pid2)
$sb = New-Object System.Text.StringBuilder 256; [void][PM]::GetClassName($h, $sb, 256)
$proc = (Get-Process -Id $pid2).ProcessName
"alvo hwnd=$h classe=$($sb.ToString()) processo=$proc"
if ($proc -ne "RobloxStudioBeta") { "ABORTADO: o ponto nao e do Roblox Studio"; exit 1 }
$c = New-Object PT; $c.X = $SX; $c.Y = $SY
[void][PM]::ScreenToClient($h, [ref]$c)
$l = [IntPtr](($c.Y -shl 16) -bor ($c.X -band 0xFFFF))
[void][PM]::PostMessage($h, 0x0200, [IntPtr]0, $l)          # WM_MOUSEMOVE
Start-Sleep -Milliseconds 60
[void][PM]::PostMessage($h, 0x0201, [IntPtr]1, $l)          # WM_LBUTTONDOWN
Start-Sleep -Milliseconds 60
[void][PM]::PostMessage($h, 0x0202, [IntPtr]0, $l)          # WM_LBUTTONUP
if ($Double) {
  Start-Sleep -Milliseconds 60
  [void][PM]::PostMessage($h, 0x0203, [IntPtr]1, $l)        # WM_LBUTTONDBLCLK
  [void][PM]::PostMessage($h, 0x0202, [IntPtr]0, $l)
}
"clique postado em cliente ($($c.X), $($c.Y))"
