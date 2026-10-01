[CmdletBinding()]
param(
    [string]$CredentialPath = "$env:LOCALAPPDATA\MyAvatarMcpEvents\control-plane-api-key.dpapi"
)

$ErrorActionPreference = 'Stop'
$directory = Split-Path -Parent $CredentialPath
New-Item -ItemType Directory -Path $directory -Force | Out-Null

$secret = Read-Host 'Incolla la runtime API key del tunnel OpenAI' -AsSecureString
try {
    $secret | ConvertFrom-SecureString | Set-Content -LiteralPath $CredentialPath -Encoding utf8 -NoNewline
    Write-Host "Credenziale cifrata per l'utente Windows corrente: $CredentialPath"
}
finally {
    $secret = $null
}

