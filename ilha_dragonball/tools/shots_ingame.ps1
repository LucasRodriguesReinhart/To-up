param([string]$OutDir, [int]$Count = 6, [double]$Every = 2.2, [int]$X = 524, [int]$Y = 204, [int]$W = 1090, [int]$H = 640)
# tira $Count fotos do viewport do Studio (Studio na frente), uma a cada $Every segundos, sincronizado com um passeio
# de camera que o cliente faz (1 plano por foto). Retangulo = viewport do Play com o Studio maximizado.
Add-Type -AssemblyName System.Drawing
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$bmp = New-Object System.Drawing.Bitmap $W, $H
$g = [System.Drawing.Graphics]::FromImage($bmp)
Start-Sleep -Milliseconds 1500
for ($i = 0; $i -lt $Count; $i++) {
    Start-Sleep -Milliseconds ([int]($Every * 1000))
    $g.CopyFromScreen($X, $Y, 0, 0, $bmp.Size)
    $bmp.Save((Join-Path $OutDir ("shot_{0:D2}.png" -f $i)))
}
"FOTOS $Count"
