# traz o Roblox Studio para a frente (TOPMOST -> NOTOPMOST, maximizado) sem mexer no mouse: o Qt do Studio so trata
# cliques por mensagem no ribbon/Import Queue com a janela ativa
Add-Type @"
using System; using System.Runtime.InteropServices;
public class W8 {
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int c);
  [DllImport("user32.dll")] public static extern bool SetWindowPos(IntPtr h, IntPtr after, int x, int y, int cx, int cy, uint f);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  public static readonly IntPtr TOP = new IntPtr(-1);
  public static readonly IntPtr NOTOP = new IntPtr(-2);
}
"@
$proc = Get-Process RobloxStudioBeta -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -ne '' } | Select-Object -First 1
if (-not $proc) { "ERRO: Studio nao encontrado"; exit 1 }
$h = $proc.MainWindowHandle
[W8]::ShowWindow($h, 3) | Out-Null            # SW_MAXIMIZE (nunca 9)
[W8]::SetWindowPos($h, [W8]::TOP, 0, 0, 0, 0, 0x0043) | Out-Null
[W8]::SetWindowPos($h, [W8]::NOTOP, 0, 0, 0, 0, 0x0043) | Out-Null
[W8]::SetForegroundWindow($h) | Out-Null
Start-Sleep -Milliseconds 250
"ativo"
