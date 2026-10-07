param([string]$Folder, [string]$File, [int]$StartX = 1867, [int]$StartY = 891)
# importa UM FBX pelo menu File > Import (2026-10-06: o ribbon esta recolhido e o botao Import dele nao abre o dialogo).
# File em (17,33), item Import em (42,182), dialogo "Open 3D File" por Win32, e o arquivo cai no painel Import Queue;
# o botao "Start Import" do painel (1867,891) so responde com postclick2 (o painel e uma janela Qt filha).
# CUIDADO: durante a importacao o mesmo botao vira "Stop Import" - so chame com a fila anterior concluida.
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
Add-Type @"
using System; using System.Runtime.InteropServices;
public class FDM { [DllImport("user32.dll", CharSet=CharSet.Auto)] public static extern IntPtr FindWindow(string c, string t); }
"@
& powershell -ExecutionPolicy Bypass -File (Join-Path $here "activate.ps1") | Out-Null
& powershell -ExecutionPolicy Bypass -File (Join-Path $here "postclick.ps1") -SX 17 -SY 33 | Out-Null
Start-Sleep -Milliseconds 1200
& powershell -ExecutionPolicy Bypass -File (Join-Path $here "postclick.ps1") -SX 42 -SY 182 | Out-Null
$ok = $false
for ($i = 0; $i -lt 40; $i++) { Start-Sleep -Milliseconds 250; if ([FDM]::FindWindow("#32770", "Open 3D File (FBX, OBJ, GLB, GLTF)") -ne [IntPtr]::Zero) { $ok = $true; break } }
if (-not $ok) { "ERRO: o dialogo nao abriu ($File)"; exit 1 }
& powershell -ExecutionPolicy Bypass -File (Join-Path $here "filedlg2.ps1") -Folder $Folder -Files $File | Out-Null
Start-Sleep -Seconds 5
& powershell -ExecutionPolicy Bypass -File (Join-Path $here "activate.ps1") | Out-Null
Start-Sleep -Milliseconds 500
# 2 cliques: o 1o (WindowFromPoint) so da foco/hover no painel; o 2o (ChildWindowFromPointEx) aperta o botao
& powershell -ExecutionPolicy Bypass -File (Join-Path $here "postclick.ps1") -SX $StartX -SY $StartY | Out-Null
Start-Sleep -Milliseconds 800
& powershell -ExecutionPolicy Bypass -File (Join-Path $here "postclick2.ps1") -SX $StartX -SY $StartY | Out-Null
"import disparado: $File"
