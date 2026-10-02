[CmdletBinding()]
param(
    [string]$InstallRoot = (Split-Path -Parent $PSScriptRoot),
    [string]$Python = 'python'
)

$ErrorActionPreference = 'Stop'
$root = [IO.Path]::GetFullPath((Resolve-Path -LiteralPath $InstallRoot).Path)
$secretPath = Join-Path $root 'config\secrets.dpapi.json'
if (-not (Test-Path -LiteralPath $secretPath -PathType Leaf)) {
    throw 'Segreti mancanti. Eseguire Save-MyAvatarSecrets.ps1.'
}

function Unprotect([string]$CipherText) {
    $secure = $CipherText | ConvertTo-SecureString
    $pointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
    try { return [Runtime.InteropServices.Marshal]::PtrToStringBSTR($pointer) }
    finally { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($pointer); $secure = $null }
}

$encrypted = Get-Content -LiteralPath $secretPath -Raw | ConvertFrom-Json
$env:MYAVATAR_MCP_TOKEN = Unprotect $encrypted.mcp
$env:MYAVATAR_INGRESS_TOKEN = Unprotect $encrypted.ingress
$env:MYAVATAR_EVENT_SALT = Unprotect $encrypted.eventSalt

try {
    $bridge = Start-Process -FilePath $Python -ArgumentList @((Join-Path $root 'runtime\src\bridge.py'),'--root',$root) -WindowStyle Hidden -PassThru
    Start-Sleep -Milliseconds 500
    if ($bridge.HasExited) { throw 'Il bridge non è rimasto in esecuzione.' }
    $watcher = Start-Process -FilePath $Python -ArgumentList @((Join-Path $root 'runtime\src\watch_onedrive_events.py'),'--root',$root) -WindowStyle Hidden -PassThru
    Start-Sleep -Milliseconds 500
    if ($watcher.HasExited) { Stop-Process -Id $bridge.Id -ErrorAction SilentlyContinue; throw 'Il watcher non è rimasto in esecuzione.' }
    [ordered]@{bridgePid=$bridge.Id;watcherPid=$watcher.Id;started=(Get-Date).ToString('o')} |
        ConvertTo-Json | Set-Content -LiteralPath (Join-Path $root 'data\processes.json') -Encoding UTF8
    Write-Host "My Avatar avviato. Bridge PID $($bridge.Id), watcher PID $($watcher.Id)."
} finally {
    Remove-Item Env:MYAVATAR_MCP_TOKEN,Env:MYAVATAR_INGRESS_TOKEN,Env:MYAVATAR_EVENT_SALT -ErrorAction SilentlyContinue
}
