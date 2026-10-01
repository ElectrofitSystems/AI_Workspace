$ErrorActionPreference = 'Stop'
$env:DOTNET_CLI_TELEMETRY_OPTOUT = '1'
$active = Get-Process -Name TeamsWake -ErrorAction SilentlyContinue
if ($active) { throw 'Arresta il listener con Stop-Listener.ps1 prima di ricompilare.' }
$sdk = Join-Path $PSScriptRoot '.tools\dotnet\dotnet.exe'
if (-not (Test-Path -LiteralPath $sdk)) { $sdk = 'dotnet' }
& $sdk publish (Join-Path $PSScriptRoot 'src\TeamsWake\TeamsWake.csproj') -c Release -r win-x64 --self-contained false -o (Join-Path $PSScriptRoot 'artifacts\app')
if ($LASTEXITCODE -ne 0) { throw 'Compilazione fallita.' }
