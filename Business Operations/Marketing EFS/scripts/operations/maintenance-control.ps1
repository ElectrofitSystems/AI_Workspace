param([ValidateSet('Run','Install','Status')][string]$Action='Status')
$ErrorActionPreference='Stop'
$projectRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$taskName='EFitsys Marketing EFS - Compatibility 06-18'
$description='EFitsys: controlli e recupero compatibilita Marketing EFS alle 06:00 e 18:00, autorizzati il 15 ottobre 2026.'
switch($Action){
    'Install' {
        $existing=Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
        if($existing -and $existing.Description -ne $description){throw 'Task omonimo con altro mandato: non sostituito.'}
        $arguments='-NoProfile -NonInteractive -WindowStyle Hidden -ExecutionPolicy Bypass -File "{0}" -Action Run' -f $PSCommandPath
        $taskAction=New-ScheduledTaskAction -Execute 'powershell.exe' -Argument $arguments -WorkingDirectory $projectRoot
        $triggers=@((New-ScheduledTaskTrigger -Daily -At '06:00'),(New-ScheduledTaskTrigger -Daily -At '18:00'))
        # Offset-free boundaries follow the Windows Rome timezone through DST changes.
        $localDate=Get-Date -Format 'yyyy-MM-dd'
        $triggers[0].StartBoundary=$localDate+'T06:00:00'
        $triggers[1].StartBoundary=$localDate+'T18:00:00'
        $identity=[Security.Principal.WindowsIdentity]::GetCurrent().Name
        $principal=New-ScheduledTaskPrincipal -UserId $identity -LogonType Interactive -RunLevel Limited
        $settings=New-ScheduledTaskSettingsSet -StartWhenAvailable -WakeToRun -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit ([TimeSpan]::FromMinutes(30)) -MultipleInstances IgnoreNew
        Register-ScheduledTask -TaskName $taskName -Action $taskAction -Trigger $triggers -Principal $principal -Settings $settings -Description $description -Force | Select-Object TaskName,State
    }
    'Run' {
        $pythonPath=Join-Path $env:USERPROFILE '.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
        if(-not (Test-Path -LiteralPath $pythonPath -PathType Leaf)){
            $pythonPath=(Get-Command python.exe -CommandType Application -ErrorAction Stop | Select-Object -First 1).Source
        }
        Push-Location -LiteralPath $projectRoot
        try {& $pythonPath (Join-Path $PSScriptRoot 'maintenance.py') --model-check --allow-agent-repair;exit $LASTEXITCODE}
        finally {Pop-Location}
    }
    'Status' {
        $task=Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
        $info=if($task){Get-ScheduledTaskInfo -TaskName $taskName}
        $report=Join-Path $projectRoot '.local/operations-teams/maintenance-status.json'
        [pscustomobject]@{Task=$task.TaskName;State=$task.State;LastRun=$info.LastRunTime;NextRun=$info.NextRunTime;LastResult=$info.LastTaskResult;TimeZone=(Get-TimeZone).Id;Checks=if(Test-Path -LiteralPath $report){Get-Content -LiteralPath $report -Raw | ConvertFrom-Json}} | ConvertTo-Json -Depth 12
    }
}
