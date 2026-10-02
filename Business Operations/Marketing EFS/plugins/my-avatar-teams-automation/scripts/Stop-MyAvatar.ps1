[CmdletBinding()]
param([string]$InstallRoot = (Split-Path -Parent $PSScriptRoot))

$ErrorActionPreference = 'Stop'
$root = [IO.Path]::GetFullPath((Resolve-Path -LiteralPath $InstallRoot).Path)
$statePath = Join-Path $root 'data\processes.json'
if (-not (Test-Path -LiteralPath $statePath -PathType Leaf)) {
    Write-Host 'Nessun processo registrato.'
    return
}
$state = Get-Content -LiteralPath $statePath -Raw | ConvertFrom-Json
foreach ($id in @($state.bridgePid, $state.watcherPid)) {
    if ($id -is [int] -or $id -match '^\d+$') {
        $process = Get-Process -Id ([int]$id) -ErrorAction SilentlyContinue
        if ($process -and $process.ProcessName -match '^python') {
            Stop-Process -Id $process.Id
        }
    }
}
Remove-Item -LiteralPath $statePath -Force
Write-Host 'My Avatar arrestato.'
