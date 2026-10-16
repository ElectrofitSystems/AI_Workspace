# Crea le categorie locali escluse da Git, anche dopo una nuova copia del repo.
[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$workspaceRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '../..')).Path
$workspaceFolders = @(
    'input/Technical documentation'
    'input/Forms'
    'input/References'
    'output/Documentation/Guides'
    'output/Navigation/Maps'
    'output/Automations/Drafts'
    'output/Automations/Reviews'
    'output/Automations/Deliveries'
    'output/Statistics/coordination'
    '.local/maintenance/temporary'
)

foreach ($relativeFolder in $workspaceFolders) {
    $targetFolder = Join-Path $workspaceRoot $relativeFolder
    [System.IO.Directory]::CreateDirectory($targetFolder) | Out-Null
}

Write-Output "Workspace pronto: $workspaceRoot"
Write-Output "Categorie locali verificate: $($workspaceFolders.Count)"
