[CmdletBinding()]
param([string]$InstallRoot = (Split-Path -Parent $PSScriptRoot))

$root = [IO.Path]::GetFullPath((Resolve-Path -LiteralPath $InstallRoot).Path)
$statePath = Join-Path $root 'data\processes.json'
$enabled = Test-Path -LiteralPath (Join-Path $root 'config\auto-reply.enabled')
if (-not (Test-Path -LiteralPath $statePath)) {
    [pscustomobject]@{running=$false;autoReplyEnabled=$enabled;installRoot=$root}
    return
}
$state = Get-Content -LiteralPath $statePath -Raw | ConvertFrom-Json
$bridge = Get-Process -Id ([int]$state.bridgePid) -ErrorAction SilentlyContinue
$watcher = Get-Process -Id ([int]$state.watcherPid) -ErrorAction SilentlyContinue
[pscustomobject]@{
    running=[bool]($bridge -and $watcher)
    bridgePid=$state.bridgePid
    watcherPid=$state.watcherPid
    autoReplyEnabled=$enabled
    installRoot=$root
}
