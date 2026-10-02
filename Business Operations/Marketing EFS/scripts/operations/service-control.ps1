param([ValidateSet('Start','Stop','Status','Watchdog','InstallStartup')][string]$Action='Status')
$ErrorActionPreference='Stop'
$projectRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$statePath=Join-Path $projectRoot '.local/operations-teams'
$enabledPath=Join-Path $statePath 'service.enabled'
$healthPath=Join-Path $statePath 'health.json'
$servicePath=Join-Path $PSScriptRoot 'teams_service.py'
$pythonPath='C:/Users/Operations/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
$pythonWindowless=Join-Path (Split-Path $pythonPath) 'pythonw.exe'
$watchdogPath=Join-Path $PSScriptRoot 'watchdog.py'
$codexPath='C:/Users/Operations/AppData/Local/OpenAI/Codex/bin/a51e250fa15c740a/codex.exe'
$taskName='EFitsys Operations Teams'
function Read-ServiceHealth {
    if(Test-Path -LiteralPath $healthPath){Get-Content -LiteralPath $healthPath -Raw | ConvertFrom-Json}
}
switch($Action){
    'Status' {
        $health=Read-ServiceHealth
        $running=$false
        if($health){
            $process=Get-CimInstance Win32_Process -Filter "ProcessId=$($health.pid)" -ErrorAction SilentlyContinue
            $running=$process -and $process.CommandLine -like '*scripts/operations/teams_service.py*'
            if(-not $running -and $process){$running=$process.CommandLine -like '*scripts\operations\teams_service.py*'}
        }
        [pscustomobject]@{Enabled=(Test-Path -LiteralPath $enabledPath);Running=[bool]$running;Health=$health} | ConvertTo-Json -Depth 5
    }
    'Stop' {
        if(Test-Path -LiteralPath $enabledPath){Remove-Item -LiteralPath $enabledPath}
        'Arresto richiesto. Il servizio verifica il blocco anche prima di ogni invio.'
    }
    'Watchdog' {
        & $pythonPath $watchdogPath
    }
    'Start' {
        New-Item -ItemType File -Path $enabledPath -Force | Out-Null
        $health=Read-ServiceHealth
        if($health -and $health.status -eq 'running'){
            $process=Get-CimInstance Win32_Process -Filter "ProcessId=$($health.pid)" -ErrorAction SilentlyContinue
            if($process -and $process.CommandLine -like '*teams_service.py*'){
                'Il servizio è già in esecuzione.';return
            }
        }
        $watchdog=Get-CimInstance Win32_Process -Filter "Name='pythonw.exe'" | Where-Object {
            $_.CommandLine -and $_.CommandLine.Contains($watchdogPath)
        }
        if($watchdog){'Il watchdog è già attivo; il servizio riparte al prossimo controllo.';return}
        Start-Process -FilePath $pythonWindowless -ArgumentList ('"'+$watchdogPath+'"') -WorkingDirectory $projectRoot -WindowStyle Hidden
        'Servizio avviato; verificare Status dopo il primo controllo Teams.'
    }
    'InstallStartup' {
        $existing=Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
        if($existing -and $existing.Description -ne 'EFitsys: servizio locale autorizzato Operations nelle chat individuali Teams.'){
            throw 'Esiste già un task con questo nome e un altro mandato; non sostituito.'
        }
        $startupAction=New-ScheduledTaskAction -Execute $pythonWindowless -Argument ('"'+$watchdogPath+'"') -WorkingDirectory $projectRoot
        $identity=[Security.Principal.WindowsIdentity]::GetCurrent().Name
        $trigger=New-ScheduledTaskTrigger -AtLogOn -User $identity
        $principal=New-ScheduledTaskPrincipal -UserId $identity -LogonType Interactive -RunLevel Limited
        $settings=New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit ([TimeSpan]::Zero) -MultipleInstances IgnoreNew
        Register-ScheduledTask -TaskName $taskName -Action $startupAction -Trigger $trigger -Principal $principal -Settings $settings -Description 'EFitsys: servizio locale autorizzato Operations nelle chat individuali Teams.' -Force | Select-Object TaskName,State
    }
}
