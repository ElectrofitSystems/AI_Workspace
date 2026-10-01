$ErrorActionPreference = 'Stop'
$program = Join-Path $PSScriptRoot 'artifacts\app\TeamsWake.exe'
if (-not (Test-Path -LiteralPath $program)) { throw 'Eseguibile assente. Esegui prima Build.ps1.' }
Start-Process -FilePath $program -ArgumentList '--background' -WindowStyle Hidden
Write-Output 'Avvio richiesto. Verifica lo stato con Status.ps1; icona Teams Wake nella barra di sistema.'
