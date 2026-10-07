param([string]$Folder, [string]$Pattern)
# importa VARIOS FBX pelo Import Queue do Studio (versao 2026-10 sem ribbon visivel):
#  1. traz o Studio do AMS para a frente e SO envia Ctrl+M se ele estiver mesmo em primeiro plano (SendKeys em outra
#     janela digita no que estiver em foco - ja caiu no chat do Claude);
#  2. preenche o dialogo nativo "Open 3D File" por WM_SETTEXT no Edit id 1148 (pasta + IDOK, depois os nomes + IDOK).
# O dialogo pode vir como janela de topo (#32770) ou filho de uma janela Qt, e demorar ~10-20 s para abrir.
# Depois do "Parsing files" e preciso clicar em "Start Import" no painel Import Queue.
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
Add-Type -AssemblyName System.Windows.Forms
Add-Type @"
using System; using System.Text; using System.Collections.Generic; using System.Runtime.InteropServices;
public class IQ {
  public delegate bool P(IntPtr h, IntPtr l);
  [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
  [DllImport("user32.dll")] public static extern int GetWindowThreadProcessId(IntPtr h, out int pid);
  [DllImport("user32.dll")] static extern bool EnumWindows(P f, IntPtr l);
  [DllImport("user32.dll")] static extern bool EnumChildWindows(IntPtr p, P f, IntPtr l);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] static extern int GetClassName(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll")] static extern int GetDlgCtrlID(IntPtr h);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern IntPtr SendMessage(IntPtr h, uint m, IntPtr w, string l);
  [DllImport("user32.dll")] public static extern bool PostMessage(IntPtr h, uint m, IntPtr w, IntPtr l);
  public static IntPtr Dlg(int pid) { IntPtr r = IntPtr.Zero;
    EnumWindows((h,l)=>{ int p; GetWindowThreadProcessId(h,out p); if(p!=pid) return true;
      var tt=new StringBuilder(128); GetWindowText(h,tt,128); var tc=new StringBuilder(64); GetClassName(h,tc,64);
      if(tc.ToString()=="#32770" && tt.ToString().StartsWith("Open 3D File")) { r=h; return false; }   // dialogo de topo
      EnumChildWindows(h,(c,l2)=>{ var cn=new StringBuilder(64); GetClassName(c,cn,64); var t=new StringBuilder(128); GetWindowText(c,t,128);
        if(cn.ToString()=="#32770" && t.ToString().StartsWith("Open 3D File")) { r=c; return false; } return true; },IntPtr.Zero);
      return r==IntPtr.Zero; },IntPtr.Zero); return r; }
  public static IntPtr Edit(IntPtr dlg) { IntPtr r=IntPtr.Zero;
    EnumChildWindows(dlg,(c,l)=>{ var cn=new StringBuilder(64); GetClassName(c,cn,64); if(cn.ToString()=="Edit" && GetDlgCtrlID(c)==1148){ r=c; return false;} return true; },IntPtr.Zero); return r; }
}
"@
$studio = Get-Process RobloxStudioBeta | Where-Object { $_.MainWindowTitle -like 'Anime Mining Simulator*' } | Select-Object -First 1
if (-not $studio) { "ERRO: Studio do AMS nao encontrado"; exit 1 }
& powershell -ExecutionPolicy Bypass -File (Join-Path $here "activate.ps1") | Out-Null
$fpid = 0; [IQ]::GetWindowThreadProcessId([IQ]::GetForegroundWindow(), [ref]$fpid) | Out-Null
if ($fpid -ne $studio.Id) { "ERRO: Studio nao ficou em primeiro plano (pid $fpid) - nada foi digitado"; exit 2 }
[System.Windows.Forms.SendKeys]::SendWait("^m")
$dlg = [IntPtr]::Zero
for ($i = 0; $i -lt 120 -and $dlg -eq [IntPtr]::Zero; $i++) { Start-Sleep -Milliseconds 250; $dlg = [IQ]::Dlg($studio.Id) }
if ($dlg -eq [IntPtr]::Zero) { "ERRO: dialogo Open 3D File nao abriu"; exit 3 }
$edit = [IQ]::Edit($dlg)
[IQ]::SendMessage($edit, 0x000C, [IntPtr]::Zero, $Folder) | Out-Null
Start-Sleep -Milliseconds 200
[IQ]::PostMessage($dlg, 0x0111, [IntPtr]1, [IntPtr]::Zero) | Out-Null
Start-Sleep -Milliseconds 1500
$files = (Get-ChildItem $Folder -Filter $Pattern | ForEach-Object { '"' + $_.Name + '"' })
[IQ]::SendMessage($edit, 0x000C, [IntPtr]::Zero, ($files -join ' ')) | Out-Null
Start-Sleep -Milliseconds 200
[IQ]::PostMessage($dlg, 0x0111, [IntPtr]1, [IntPtr]::Zero) | Out-Null
"enviados $($files.Count) arquivos ao Import Queue"
