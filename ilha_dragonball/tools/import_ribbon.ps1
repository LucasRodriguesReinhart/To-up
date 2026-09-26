param([string]$Folder, [string]$File, [int]$ImpX = 752, [int]$ImpY = 100, [int]$OkX = 1276, [int]$OkY = 857)
# importa UM FBX pelo botao Import do ribbon (Home) do Studio: traz o Studio para a frente (o Qt so trata o clique com a
# janela ativa), clica Import, preenche o dialogo "Open 3D File" por Win32 e confirma no Import Preview.
# Coordenadas de TELA com o Studio maximizado em 1920x1080 (2026-09-25: Import do ribbon em (752,100), botao Import do
# preview em (1276,857)).
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
Add-Type @"
using System; using System.Runtime.InteropServices;
public class FDI { [DllImport("user32.dll", CharSet=CharSet.Auto)] public static extern IntPtr FindWindow(string c, string t); }
"@
& powershell -ExecutionPolicy Bypass -File (Join-Path $here "activate.ps1") | Out-Null
& powershell -ExecutionPolicy Bypass -File (Join-Path $here "postclick.ps1") -SX $ImpX -SY $ImpY | Out-Null
$ok = $false
for ($i = 0; $i -lt 60; $i++) { Start-Sleep -Milliseconds 250; if ([FDI]::FindWindow("#32770", "Open 3D File (FBX, OBJ, GLB, GLTF)") -ne [IntPtr]::Zero) { $ok = $true; break } }
if (-not $ok) { "ERRO: o dialogo nao abriu ($File)"; exit 1 }
& powershell -ExecutionPolicy Bypass -File (Join-Path $here "filedlg2.ps1") -Folder $Folder -Files $File | Out-Null
Start-Sleep -Seconds 6
& powershell -ExecutionPolicy Bypass -File (Join-Path $here "activate.ps1") | Out-Null
& powershell -ExecutionPolicy Bypass -File (Join-Path $here "postclick.ps1") -SX $OkX -SY $OkY | Out-Null
"import disparado: $File"
