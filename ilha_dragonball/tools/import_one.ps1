param([string]$Folder, [string]$File, [int]$FolderX = 20, [int]$FolderY = 890, [int]$ImportX = 1275, [int]$ImportY = 855)
# importa UM FBX pelo 3D Importer do Studio sem foco: clique (mensagem) no "Add file" -> dialogo (Win32) -> Import
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
$A = [System.Windows.Automation.AutomationElement]
$T = [System.Windows.Automation.TreeScope]
$main = $A::FromHandle((Get-Process RobloxStudioBeta | Select-Object -First 1).MainWindowHandle)
$cls = New-Object System.Windows.Automation.PropertyCondition($A::ClassNameProperty, "#32770")
& powershell -ExecutionPolicy Bypass -File (Join-Path $here "postclick.ps1") -SX $FolderX -SY $FolderY | Out-Null
$ok = $false
for ($i = 0; $i -lt 30; $i++) { Start-Sleep -Milliseconds 300; if ($main.FindFirst($T::Children, $cls)) { $ok = $true; break } }
if (-not $ok) { "ERRO: o dialogo nao abriu"; exit 1 }
& powershell -ExecutionPolicy Bypass -File (Join-Path $here "filedlg2.ps1") -Folder $Folder -Files $File
Start-Sleep -Seconds 4
& powershell -ExecutionPolicy Bypass -File (Join-Path $here "postclick.ps1") -SX $ImportX -SY $ImportY
"import disparado: $File"
