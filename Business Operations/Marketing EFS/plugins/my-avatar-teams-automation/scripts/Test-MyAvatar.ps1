[CmdletBinding()]
param([string]$InstallRoot = (Split-Path -Parent $PSScriptRoot))

$ErrorActionPreference = 'Stop'
$root = [IO.Path]::GetFullPath((Resolve-Path -LiteralPath $InstallRoot).Path)
$settings = Get-Content -LiteralPath (Join-Path $root 'config\settings.json') -Raw | ConvertFrom-Json
$queue = $settings.oneDrive.queueRoot
if ($queue -eq 'auto') {
    $candidate = @($env:OneDriveCommercial,$env:OneDrive) | Where-Object { $_ } | Select-Object -First 1
    if (-not $candidate -and $env:USERPROFILE) {
        $candidate = Get-ChildItem -LiteralPath $env:USERPROFILE -Directory -Filter 'OneDrive - *' -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty FullName
    }
    if (-not $candidate) { throw 'OneDrive non rilevato.' }
    $queue = Join-Path $candidate 'My Avatar\MCP Events'
}
$incoming = Join-Path ([Environment]::ExpandEnvironmentVariables($queue)) 'Incoming'
New-Item -ItemType Directory -Path $incoming -Force | Out-Null
$id = [Guid]::NewGuid().ToString('N')
@{conversationId="TEST-CONVERSATION-$id";messageId="TEST-MESSAGE-$id"} |
    ConvertTo-Json -Compress | Set-Content -LiteralPath (Join-Path $incoming "$id.json") -Encoding UTF8
Write-Host "Evento sintetico accodato: $id"
