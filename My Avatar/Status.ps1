$ErrorActionPreference = 'Stop'
$statusFile = Join-Path $env:LOCALAPPDATA 'TeamsWake\status.json'
if (-not (Test-Path -LiteralPath $statusFile)) { Write-Output 'Nessuno stato disponibile.'; return }
$snapshot = Get-Content -LiteralPath $statusFile -Raw | ConvertFrom-Json
$snapshot | Format-List
$runningProcess = Get-Process -Id $snapshot.pid -ErrorAction SilentlyContinue
Write-Output ('Processo vivo: ' + [bool]($runningProcess -and $runningProcess.ProcessName -eq 'TeamsWake'))
