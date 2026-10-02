[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$InstallRoot
)

$ErrorActionPreference = 'Stop'
$root = [IO.Path]::GetFullPath((Resolve-Path -LiteralPath $InstallRoot).Path)
$config = Join-Path $root 'config'
New-Item -ItemType Directory -Path $config -Force | Out-Null

$mcp = Read-Host 'Token bearer MCP (almeno 32 caratteri)' -AsSecureString
$ingress = Read-Host 'Token bearer ingress distinto (almeno 32 caratteri)' -AsSecureString
$saltBytes = New-Object byte[] 32
[Security.Cryptography.RandomNumberGenerator]::Fill($saltBytes)
$salt = [Convert]::ToBase64String($saltBytes) | ConvertTo-SecureString -AsPlainText -Force

try {
    $payload = [ordered]@{
        mcp = $mcp | ConvertFrom-SecureString
        ingress = $ingress | ConvertFrom-SecureString
        eventSalt = $salt | ConvertFrom-SecureString
    }
    $payload | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $config 'secrets.dpapi.json') -Encoding UTF8
    Write-Host 'Segreti cifrati per questo utente Windows.'
} finally {
    $mcp = $null
    $ingress = $null
    $salt = $null
    [Array]::Clear($saltBytes, 0, $saltBytes.Length)
}
