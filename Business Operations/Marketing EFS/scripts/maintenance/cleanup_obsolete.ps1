[CmdletBinding(SupportsShouldProcess = $true)]
param()

$workspacePath = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$expectedTarget = [System.IO.Path]::GetFullPath((Join-Path $workspacePath 'output/_cleanup-pending'))
if (-not (Test-Path -LiteralPath (Join-Path $workspacePath 'AGENTS.md') -PathType Leaf)) {
    throw 'This is not the Marketing EFS workspace.'
}
if (-not $expectedTarget.StartsWith($workspacePath.TrimEnd('\') + '\', [System.StringComparison]::OrdinalIgnoreCase)) {
    throw 'Cleanup target is outside the workspace.'
}
if (-not (Test-Path -LiteralPath $expectedTarget -PathType Container)) {
    Write-Output 'No obsolete files remain to remove.'
    return
}
$resolvedTarget = (Resolve-Path -LiteralPath $expectedTarget).Path
if ($resolvedTarget -ne $expectedTarget) { throw 'Unexpected cleanup target.' }
if ((Get-Item -LiteralPath $resolvedTarget -Force).Attributes -band [System.IO.FileAttributes]::ReparsePoint) {
    throw 'The cleanup folder must not be a junction or symbolic link.'
}
if ($PSCmdlet.ShouldProcess($resolvedTarget, 'Delete only the identified obsolete files')) {
    Remove-Item -LiteralPath $resolvedTarget -Recurse -Force -ErrorAction Stop
    Write-Output 'Obsolete files removed. Current materials, inputs and operational records preserved.'
}
