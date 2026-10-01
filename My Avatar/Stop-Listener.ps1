$ErrorActionPreference = 'Stop'
$program = Join-Path $PSScriptRoot 'artifacts\app\TeamsWake.exe'
$process = Start-Process -FilePath $program -ArgumentList '--stop' -WindowStyle Hidden -Wait -PassThru
if ($process.ExitCode -eq 2) { Write-Output 'Listener non attivo.' }
elseif ($process.ExitCode -ne 0) { throw "Errore arresto: $($process.ExitCode)" }
else {
    $deadline = [DateTime]::UtcNow.AddSeconds(5)
    do {
        $active = Get-Process -Name TeamsWake -ErrorAction SilentlyContinue
        if (-not $active) { Write-Output 'Listener arrestato.'; return }
        Start-Sleep -Milliseconds 100
    } while ([DateTime]::UtcNow -lt $deadline)
    throw 'Arresto richiesto, ma il processo non e ancora terminato.'
}
