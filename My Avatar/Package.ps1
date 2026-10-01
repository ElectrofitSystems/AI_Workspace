$ErrorActionPreference = 'Stop'
$toolsRoot = Join-Path $PSScriptRoot '.tools\sdk-buildtools'
$makeappx = Get-ChildItem -LiteralPath $toolsRoot -Filter makeappx.exe -Recurse | Where-Object { $_.FullName -match '\\x64\\' } | Select-Object -First 1
if (-not $makeappx) { throw 'Microsoft.Windows.SDK.BuildTools non trovato in .tools\sdk-buildtools.' }
$stage = Join-Path $PSScriptRoot 'artifacts\package'
New-Item -ItemType Directory -Path (Join-Path $stage 'Assets') -Force | Out-Null
$sdk = Join-Path $PSScriptRoot '.tools\dotnet\dotnet.exe'
if (-not (Test-Path -LiteralPath $sdk)) { $sdk = 'dotnet' }
$env:DOTNET_CLI_TELEMETRY_OPTOUT = '1'
& $sdk publish (Join-Path $PSScriptRoot 'src\TeamsWake\TeamsWake.csproj') -c Release -r win-x64 --self-contained false -o $stage
if ($LASTEXITCODE -ne 0) { throw 'Compilazione pacchetto fallita.' }
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'packaging\AppxManifest.xml') -Destination $stage -Force
Add-Type -AssemblyName System.Drawing
@(@{Name='StoreLogo.png'; Size=50}, @{Name='SmallLogo.png'; Size=44}, @{Name='Logo.png'; Size=150}) | ForEach-Object {
    $bitmap = New-Object System.Drawing.Bitmap($_.Size, $_.Size)
    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
    $graphics.Clear([System.Drawing.Color]::FromArgb(36,88,120))
    $font = New-Object System.Drawing.Font('Segoe UI', ($_.Size * 0.28), [System.Drawing.FontStyle]::Bold)
    $graphics.DrawString('TW', $font, [System.Drawing.Brushes]::White, ($_.Size * 0.06), ($_.Size * 0.19))
    $bitmap.Save((Join-Path $stage ('Assets\' + $_.Name)), [System.Drawing.Imaging.ImageFormat]::Png)
    $font.Dispose()
    $graphics.Dispose()
    $bitmap.Dispose()
}
& $makeappx.FullName pack /d $stage /p (Join-Path $PSScriptRoot 'artifacts\TeamsWake.msix') /o
if ($LASTEXITCODE -ne 0) { throw 'Creazione MSIX fallita.' }
