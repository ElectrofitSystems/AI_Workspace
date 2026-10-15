param(
    [ValidateSet('Start','Stop','Restart','Status','Watchdog','InstallStartup')][string]$Action='Status',
    [string]$PythonPath=$env:OPERATIONS_PYTHON,
    [string]$CodexPath=$env:OPERATIONS_CODEX
)
$ErrorActionPreference='Stop'
$projectRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$statePath=Join-Path $projectRoot '.local/operations-teams'
$enabledPath=Join-Path $statePath 'service.enabled'
$healthPath=Join-Path $statePath 'health.json'
$watchdogPath=Join-Path $PSScriptRoot 'watchdog.py'
$taskName='EFitsys Operations Teams'
function Resolve-RuntimePath([string]$ExplicitPath,[string]$CommandName) {
    if($ExplicitPath){
        if(-not (Test-Path -LiteralPath $ExplicitPath -PathType Leaf)){
            throw "Eseguibile non trovato: $ExplicitPath"
        }
        return (Resolve-Path -LiteralPath $ExplicitPath).Path
    }
    $command=Get-Command $CommandName -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
    if(-not $command){throw "Specificare il percorso di $CommandName tramite -PythonPath o -CodexPath."}
    return $command.Source
}
if($Action -in @('Start','Watchdog','InstallStartup')){
    if(-not (Test-Path -LiteralPath (Join-Path $statePath 'config.json') -PathType Leaf)){
        throw 'Configurazione locale assente: recuperare .local/operations-teams/config.json prima di avviare il servizio.'
    }
    if(-not $PythonPath){
        $bundledPython=Join-Path $env:USERPROFILE '.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
        if(Test-Path -LiteralPath $bundledPython -PathType Leaf){$PythonPath=$bundledPython}
    }
    $PythonPath=Resolve-RuntimePath $PythonPath 'python.exe'
    if(-not $CodexPath){
        $CodexPath=(& $PythonPath (Join-Path $PSScriptRoot 'runtime_paths.py') | Select-Object -Last 1)
        if($LASTEXITCODE -ne 0){throw 'Nessun runtime Codex valido individuato.'}
    }
    $CodexPath=Resolve-RuntimePath $CodexPath 'codex.exe'
    $pythonWindowless=Join-Path (Split-Path $PythonPath) 'pythonw.exe'
    if($Action -ne 'Watchdog' -and -not (Test-Path -LiteralPath $pythonWindowless -PathType Leaf)){
        throw "Python senza console non trovato: $pythonWindowless"
    }
    $watchdogArguments='"{0}"' -f $watchdogPath
}
function Read-ServiceHealth {
    if(Test-Path -LiteralPath $healthPath){Get-Content -LiteralPath $healthPath -Raw | ConvertFrom-Json}
}
switch($Action){
    'Restart' {
        & $PSCommandPath -Action Stop
        for($attempt=0;$attempt -lt 60;$attempt++){
            $health=Read-ServiceHealth
            $oldProcess=if($health){Get-CimInstance Win32_Process -Filter "ProcessId=$($health.pid)" -ErrorAction SilentlyContinue}
            if(-not $oldProcess -or $oldProcess.CommandLine -notlike '*teams_service.py*'){break}
            Start-Sleep -Milliseconds 500
        }
        if($oldProcess -and $oldProcess.CommandLine -like '*teams_service.py*'){
            throw 'Servizio ancora attivo dopo arresto richiesto: non avvio un secondo processo.'
        }
        for($attempt=0;$attempt -lt 30;$attempt++){
            $oldWatchdogs=@(Get-CimInstance Win32_Process -Filter "Name='pythonw.exe'" | Where-Object {$_.CommandLine -and $_.CommandLine.Contains($watchdogPath)})
            if($oldWatchdogs.Count -eq 0){break}
            Start-Sleep -Milliseconds 500
        }
        if($oldWatchdogs.Count -gt 0){throw 'Watchdog ancora attivo: non avvio un secondo monitor.'}
        & $PSCommandPath -Action Start -PythonPath $PythonPath -CodexPath $CodexPath
    }
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
        & $PythonPath $watchdogPath --codex $CodexPath
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
        Start-Process -FilePath $pythonWindowless -ArgumentList $watchdogArguments -WorkingDirectory $projectRoot -WindowStyle Hidden
        'Servizio avviato; verificare Status dopo il primo controllo Teams.'
    }
    'InstallStartup' {
        $existing=Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
        if($existing -and $existing.Description -ne 'EFitsys: servizio locale autorizzato Operations nelle chat individuali Teams.'){
            throw 'Esiste già un task con questo nome e un altro mandato; non sostituito.'
        }
        $startupAction=New-ScheduledTaskAction -Execute $pythonWindowless -Argument $watchdogArguments -WorkingDirectory $projectRoot
        $identity=[Security.Principal.WindowsIdentity]::GetCurrent().Name
        $trigger=New-ScheduledTaskTrigger -AtLogOn -User $identity
        $principal=New-ScheduledTaskPrincipal -UserId $identity -LogonType Interactive -RunLevel Limited
        $settings=New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit ([TimeSpan]::Zero) -MultipleInstances IgnoreNew
        Register-ScheduledTask -TaskName $taskName -Action $startupAction -Trigger $trigger -Principal $principal -Settings $settings -Description 'EFitsys: servizio locale autorizzato Operations nelle chat individuali Teams.' -Force | Select-Object TaskName,State
    }
}
