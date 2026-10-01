[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$TunnelClientPath,

    [string]$Profile = 'my-avatar-events',

    [string]$CredentialPath = "$env:LOCALAPPDATA\MyAvatarMcpEvents\control-plane-api-key.dpapi"
)

$ErrorActionPreference = 'Stop'

if (-not (Test-Path -LiteralPath $TunnelClientPath -PathType Leaf)) {
    throw "tunnel-client non trovato: $TunnelClientPath"
}
if (-not (Test-Path -LiteralPath $CredentialPath -PathType Leaf)) {
    throw "Credenziale cifrata non trovata. Esegui prima Save-TunnelCredential.ps1."
}

$secure = Get-Content -Raw -LiteralPath $CredentialPath | ConvertTo-SecureString
$pointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
try {
    $env:CONTROL_PLANE_API_KEY = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($pointer)
    & $TunnelClientPath run --profile $Profile
}
finally {
    Remove-Item Env:CONTROL_PLANE_API_KEY -ErrorAction SilentlyContinue
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($pointer)
    $secure = $null
}

