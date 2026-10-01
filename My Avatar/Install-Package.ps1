# Pacchetto locale di sviluppo, non firmato. Richiede PowerShell amministratore.
# Non importa certificati e non cambia Developer Mode o policy di sistema.
$ErrorActionPreference = 'Stop'
$principal = [Security.Principal.WindowsPrincipal]::new([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    throw 'Esegui questo script da Windows PowerShell come amministratore: Windows lo richiede per questo MSIX di sviluppo.'
}
Add-AppxPackage -Path (Join-Path $PSScriptRoot 'artifacts\TeamsWake.msix') -AllowUnsigned
Write-Output 'Installato. Arresta la versione portatile, poi apri Teams Wake dal menu Start e concedi il permesso se richiesto.'
