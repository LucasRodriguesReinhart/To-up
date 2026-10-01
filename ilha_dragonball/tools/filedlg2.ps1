param([string]$Folder, [string[]]$Files)
# preenche o dialogo "Open 3D File" do Roblox Studio (sem foco): acha os HWND por UI Automation e usa mensagens Win32
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type @"
using System; using System.Runtime.InteropServices;
public class FD {
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern IntPtr SendMessage(IntPtr h, uint m, IntPtr w, string l);
  [DllImport("user32.dll")] public static extern bool PostMessage(IntPtr h, uint m, IntPtr w, IntPtr l);
}
"@
$A = [System.Windows.Automation.AutomationElement]
$T = [System.Windows.Automation.TreeScope]
$studio = (Get-Process RobloxStudioBeta | Select-Object -First 1).Id
$main = $A::FromHandle((Get-Process -Id $studio).MainWindowHandle)
$cls = New-Object System.Windows.Automation.PropertyCondition($A::ClassNameProperty, "#32770")


function Get-Dlg { return $main.FindFirst($T::Children, $cls) }
$dlg = Get-Dlg
if (-not $dlg) { "SEM DIALOGO"; exit 1 }
"dialogo: " + $dlg.Current.Name
$hdlg = [IntPtr]$dlg.Current.NativeWindowHandle


function Get-Edit {
  $d = Get-Dlg
  $ids = $d.FindAll($T::Descendants, (New-Object System.Windows.Automation.PropertyCondition($A::AutomationIdProperty, "1148")))
  foreach ($e in $ids) { if ($e.Current.ClassName -eq "Edit") { return [IntPtr]$e.Current.NativeWindowHandle } }
  return [IntPtr]::Zero
}


function Submit([string]$text) {
  $he = Get-Edit
  if ($he -eq [IntPtr]::Zero) { "SEM CAMPO NOME"; exit 2 }
  [void][FD]::SendMessage($he, 0x000C, [IntPtr]::Zero, $text)
  Start-Sleep -Milliseconds 200
  [void][FD]::PostMessage($hdlg, 0x0111, [IntPtr]1, [IntPtr]::Zero)
}
if ($Folder) {
  Submit $Folder
  Start-Sleep -Milliseconds 1200
}
$val = ($Files | ForEach-Object { '"' + $_ + '"' }) -join ' '
Submit $val
Start-Sleep -Milliseconds 1500
if (Get-Dlg) { "DIALOGO AINDA ABERTO (arquivos nao aceitos?)" } else { "dialogo fechado: " + $Files.Count + " arquivos enviados" }
