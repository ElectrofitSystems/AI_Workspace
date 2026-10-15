param([switch]$Apply)
$ErrorActionPreference='Stop'
$projectRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$policy=Get-Content -LiteralPath (Join-Path $PSScriptRoot 'marketing-access.json') -Raw | ConvertFrom-Json
if(-not $policy.enabled -or $policy.allowed_domains -notcontains 'efitsys.com'){throw 'Marketing production policy is not enabled.'}
$localRoot=[IO.Path]::GetFullPath((Join-Path $projectRoot '.local'))
if($localRoot -ne (Join-Path $projectRoot '.local')){throw 'Unexpected repair target'}
$groupName="$env:COMPUTERNAME\CodexSandboxUsers"
$parentAcl=Get-Acl -LiteralPath $localRoot
$legacy=@($parentAcl.Access | Where-Object {$_.IdentityReference.Value -eq $groupName -and $_.AccessControlType -eq 'Deny' -and -not $_.IsInherited})
if(-not $Apply){[pscustomobject]@{Target=$localRoot;LegacyDenyCount=$legacy.Count;Applied=$false} | ConvertTo-Json;return}
if($legacy.Count -gt 0){
    $receiptRoot=Join-Path $localRoot 'maintenance/temporary/marketing-agent-restore-20261015'
    New-Item -ItemType Directory -Path $receiptRoot -Force | Out-Null
    $sddlPath=Join-Path $receiptRoot ('local-acl-before-'+(Get-Date -Format 'yyyyMMddTHHmmssfff')+'.txt')
    [IO.File]::WriteAllText($sddlPath,$parentAcl.Sddl)
    # Preserve explicit denial on private state before removing the obsolete parent deny.
    foreach($privateName in @('operations-teams','myavatar')){
        $privatePath=Join-Path $localRoot $privateName
        if(Test-Path -LiteralPath $privatePath){
            $privateAcl=Get-Acl -LiteralPath $privatePath
            $rule=[Security.AccessControl.FileSystemAccessRule]::new($groupName,'ReadAndExecute, Synchronize','ContainerInherit, ObjectInherit','None','Deny')
            $privateAcl.AddAccessRule($rule)
            Set-Acl -LiteralPath $privatePath -AclObject $privateAcl
        }
    }
    foreach($entry in $legacy){$parentAcl.RemoveAccessRuleSpecific($entry)}
    Set-Acl -LiteralPath $localRoot -AclObject $parentAcl
}
[pscustomobject]@{Target=$localRoot;RemovedLegacyDenyCount=$legacy.Count;Applied=$true} | ConvertTo-Json
