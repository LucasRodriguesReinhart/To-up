param([int]$SX, [int]$SY, [switch]$Double)
# clique por mensagem de janela no Roblox Studio MESMO COBERTO por outra janela: parte da janela principal do Studio e
# desce pelos filhos com ChildWindowFromPointEx (nao usa WindowFromPoint, que pega a janela de cima). SX/SY = ponto de
# TELA com o Studio maximizado (o mesmo referencial do capture.ps1).
Add-Type @"
using System; using System.Runtime.InteropServices; using System.Text;
public struct PT2 { public int X; public int Y; }
public class PM2 {
  [DllImport("user32.dll")] public static extern IntPtr ChildWindowFromPointEx(IntPtr h, PT2 p, uint f);
  [DllImport("user32.dll")] public static extern bool ScreenToClient(IntPtr h, ref PT2 p);
  [DllImport("user32.dll")] public static extern bool PostMessage(IntPtr h, uint m, IntPtr w, IntPtr l);
  [DllImport("user32.dll")] public static extern int GetClassName(IntPtr h, StringBuilder s, int n);
}
"@
$proc = Get-Process RobloxStudioBeta -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -ne '' } | Select-Object -First 1
if (-not $proc) { "ERRO: Studio nao encontrado"; exit 1 }
$h = $proc.MainWindowHandle
for ($i = 0; $i -lt 8; $i++) {
  $c = New-Object PT2; $c.X = $SX; $c.Y = $SY
  [void][PM2]::ScreenToClient($h, [ref]$c)
  $k = [PM2]::ChildWindowFromPointEx($h, $c, 1 -bor 4)     # CWP_SKIPINVISIBLE | CWP_SKIPTRANSPARENT
  if ($k -eq [IntPtr]::Zero -or $k -eq $h) { break }
  $h = $k
}
$sb = New-Object System.Text.StringBuilder 256; [void][PM2]::GetClassName($h, $sb, 256)
$c = New-Object PT2; $c.X = $SX; $c.Y = $SY
[void][PM2]::ScreenToClient($h, [ref]$c)
"alvo hwnd=$h classe=$($sb.ToString()) cliente=($($c.X),$($c.Y))"
$l = [IntPtr](($c.Y -shl 16) -bor ($c.X -band 0xFFFF))
[void][PM2]::PostMessage($h, 0x0200, [IntPtr]0, $l)          # WM_MOUSEMOVE
Start-Sleep -Milliseconds 60
[void][PM2]::PostMessage($h, 0x0201, [IntPtr]1, $l)          # WM_LBUTTONDOWN
Start-Sleep -Milliseconds 60
[void][PM2]::PostMessage($h, 0x0202, [IntPtr]0, $l)          # WM_LBUTTONUP
if ($Double) {
  Start-Sleep -Milliseconds 60
  [void][PM2]::PostMessage($h, 0x0203, [IntPtr]1, $l)        # WM_LBUTTONDBLCLK
  Start-Sleep -Milliseconds 60
  [void][PM2]::PostMessage($h, 0x0202, [IntPtr]0, $l)
}
