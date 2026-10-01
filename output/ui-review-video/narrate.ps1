$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Speech
$reviewRoot = $PSScriptRoot
$reviewChapters = Get-Content -LiteralPath (Join-Path $reviewRoot 'chapters.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$reviewSpeaker = New-Object System.Speech.Synthesis.SpeechSynthesizer
$reviewSpeaker.SelectVoice('Microsoft Maria Desktop')
$reviewSpeaker.Rate = 1
$reviewSpeaker.Volume = 100
foreach ($chapter in $reviewChapters) {
    $reviewSpeaker.SetOutputToWaveFile((Join-Path $reviewRoot ('audio/' + $chapter.id + '.wav')))
    $reviewSpeaker.Speak($chapter.narration)
    $reviewSpeaker.SetOutputToNull()
    Write-Output ('Narrado: ' + $chapter.title)
}
$reviewSpeaker.Dispose()
