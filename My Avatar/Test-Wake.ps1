$ErrorActionPreference = 'Stop'
$program = Join-Path $PSScriptRoot 'artifacts\app\TeamsWake.exe'
$process = Start-Process -FilePath $program -ArgumentList '--signal-test' -WindowStyle Hidden -Wait -PassThru
if ($process.ExitCode -ne 0) { throw 'Listener non attivo. Avvia Start-Listener.ps1.' }
Write-Output 'Segnale inviato al listener. Controlla pending e listener.log. Questo test NON risveglia ChatGPT.'
