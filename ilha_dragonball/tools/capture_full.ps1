param([double]$Seconds = 45, [string]$OutDir, [int]$X = 0, [int]$Y = 0, [int]$W = 1920, [int]$H = 1080)
# grava quadros JPEG da TELA (retangulo X,Y,W,H) o mais rapido possivel por $Seconds segundos; imprime o fps medio.
# Usado para o video dentro do jogo (Studio na frente, em Play). ffmpeg monta depois com o fps impresso.
Add-Type -AssemblyName System.Drawing
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$enc = [System.Drawing.Imaging.ImageCodecInfo]::GetImageEncoders() | Where-Object { $_.MimeType -eq 'image/jpeg' }
$ep = New-Object System.Drawing.Imaging.EncoderParameters 1
$ep.Param[0] = New-Object System.Drawing.Imaging.EncoderParameter([System.Drawing.Imaging.Encoder]::Quality, [long]88)
$bmp = New-Object System.Drawing.Bitmap $W, $H
$g = [System.Drawing.Graphics]::FromImage($bmp)
$sw = [System.Diagnostics.Stopwatch]::StartNew()
$n = 0
while ($sw.Elapsed.TotalSeconds -lt $Seconds) {
    $g.CopyFromScreen($X, $Y, 0, 0, $bmp.Size)
    $bmp.Save((Join-Path $OutDir ("f_{0:D4}.jpg" -f $n)), $enc, $ep)
    $n++
}
$fps = $n / $sw.Elapsed.TotalSeconds
"QUADROS $n em $([math]::Round($sw.Elapsed.TotalSeconds,1)) s = $([math]::Round($fps,2)) fps"
