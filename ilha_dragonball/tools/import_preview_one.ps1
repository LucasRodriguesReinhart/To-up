param([string]$Folder, [string]$File, [int]$StartX = 1867, [int]$StartY = 891, [int]$OkX = 1275, [int]$OkY = 856)
# importa UM FBX quando o Studio abre o "Import Preview" para cada arquivo (2026-10-08, copia Champions):
# File > Import -> dialogo Win32 -> Import Queue "Start Import" -> espera o Import Preview ficar visivel -> botao Import.
# Com varios arquivos na fila o Preview do ultimo fica escondido e a fila trava em "N-1 of N": por isso 1 arquivo por vez.
# Use $env:STUDIO_TITLE para escolher o Studio quando houver mais de um aberto.
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
Add-Type @"
using System; using System.Runtime.InteropServices; using System.Text; using System.Collections.Generic;
public class IPO {
  public delegate bool P(IntPtr h, IntPtr l);
  [DllImport("user32.dll")] public static extern bool EnumWindows(P f, IntPtr l);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll", CharSet=CharSet.Auto)] public static extern IntPtr FindWindow(string c, string t);
  public static bool PreviewVisible(){ bool v=false; EnumWindows((h,l)=>{ var s=new StringBuilder(64); GetWindowText(h,s,64); if(s.ToString()=="Import Preview" && IsWindowVisible(h)){ v=true; return false;} return true; }, IntPtr.Zero); return v; }
}
"@
& powershell -ExecutionPolicy Bypass -File (Join-Path $here "activate.ps1") | Out-Null
Start-Sleep -Milliseconds 600
& powershell -ExecutionPolicy Bypass -File (Join-Path $here "postclick.ps1") -SX 17 -SY 33 | Out-Null
Start-Sleep -Milliseconds 1200
& powershell -ExecutionPolicy Bypass -File (Join-Path $here "postclick.ps1") -SX 42 -SY 182 | Out-Null
$ok = $false
for ($i = 0; $i -lt 40; $i++) { Start-Sleep -Milliseconds 250; if ([IPO]::FindWindow("#32770", "Open 3D File (FBX, OBJ, GLB, GLTF)") -ne [IntPtr]::Zero) { $ok = $true; break } }
if (-not $ok) { "ERRO: o dialogo nao abriu ($File)"; exit 1 }
& powershell -ExecutionPolicy Bypass -File (Join-Path $here "filedlg2.ps1") -Folder $Folder -Files $File | Out-Null
$prev = $false
for ($k = 0; $k -lt 6 -and -not $prev; $k++) {
  Start-Sleep -Seconds 4
  & powershell -ExecutionPolicy Bypass -File (Join-Path $here "activate.ps1") | Out-Null
  Start-Sleep -Milliseconds 1000
  & powershell -ExecutionPolicy Bypass -File (Join-Path $here "postclick.ps1") -SX $StartX -SY $StartY | Out-Null
  for ($i = 0; $i -lt 20; $i++) { Start-Sleep -Milliseconds 500; if ([IPO]::PreviewVisible()) { $prev = $true; break } }
}
if (-not $prev) { "ERRO: Import Preview nao apareceu ($File)"; exit 2 }
Start-Sleep -Seconds 2
& powershell -ExecutionPolicy Bypass -File (Join-Path $here "postclick.ps1") -SX $OkX -SY $OkY | Out-Null
"import confirmado: $File"
