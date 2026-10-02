[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$TargetProject,
    [switch]$Force
)

$ErrorActionPreference = 'Stop'
$pluginRoot = Split-Path -Parent $PSScriptRoot
$project = [IO.Path]::GetFullPath((Resolve-Path -LiteralPath $TargetProject).Path)
$installRoot = Join-Path $project '.sources\My Avatar'

if ((Test-Path -LiteralPath $installRoot) -and -not $Force) {
    throw "Installazione già presente: $installRoot. Usare -Force soltanto dopo avere salvato la configurazione."
}

$directories = @('config','data','logs','queue','runtime','scripts','skills')
foreach ($relative in $directories) {
    New-Item -ItemType Directory -Path (Join-Path $installRoot $relative) -Force | Out-Null
}

Copy-Item -LiteralPath (Join-Path $pluginRoot 'runtime\src') -Destination (Join-Path $installRoot 'runtime') -Recurse -Force
Copy-Item -LiteralPath (Join-Path $pluginRoot 'runtime\tests') -Destination (Join-Path $installRoot 'runtime') -Recurse -Force
Get-ChildItem -LiteralPath (Join-Path $pluginRoot 'skills') -Directory | ForEach-Object {
    Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $installRoot 'skills') -Recurse -Force
}

$operationalScripts = @('Save-MyAvatarSecrets.ps1','Start-MyAvatar.ps1','Stop-MyAvatar.ps1','Status-MyAvatar.ps1','Test-MyAvatar.ps1')
foreach ($name in $operationalScripts) {
    Copy-Item -LiteralPath (Join-Path $PSScriptRoot $name) -Destination (Join-Path $installRoot 'scripts') -Force
}

$settingsTarget = Join-Path $installRoot 'config\settings.json'
if ($Force -or -not (Test-Path -LiteralPath $settingsTarget)) {
    Copy-Item -LiteralPath (Join-Path $pluginRoot 'config\settings.example.json') -Destination $settingsTarget -Force
}
$policyTarget = Join-Path $installRoot 'config\FILTER-POLICY.md'
if ($Force -or -not (Test-Path -LiteralPath $policyTarget)) {
    Copy-Item -LiteralPath (Join-Path $pluginRoot 'config\FILTER-POLICY.md') -Destination $policyTarget -Force
}

$oneDriveRoots = @()
if ($env:OneDriveCommercial) { $oneDriveRoots += $env:OneDriveCommercial }
if ($env:USERPROFILE) {
    $oneDriveRoots += Get-ChildItem -LiteralPath $env:USERPROFILE -Directory -Filter 'OneDrive - *' -ErrorAction SilentlyContinue | Select-Object -ExpandProperty FullName
}
if ($env:OneDrive) { $oneDriveRoots += $env:OneDrive }
if ($oneDriveRoots.Count -gt 0) {
    $queueRoot = Join-Path $oneDriveRoots[0] 'My Avatar\MCP Events'
    foreach ($name in @('Incoming','Processed','Rejected')) {
        New-Item -ItemType Directory -Path (Join-Path $queueRoot $name) -Force | Out-Null
    }
    Write-Host "Coda OneDrive preparata: $queueRoot"
} else {
    Write-Warning 'OneDrive non rilevato. Configurare oneDrive.queueRoot in settings.json.'
}

Write-Host "My Avatar v0.1 installato in: $installRoot"
Write-Host "Prossimo passo: compilare config\settings.json e config\FILTER-POLICY.md"
