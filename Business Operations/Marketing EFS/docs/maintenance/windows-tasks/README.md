# Backup task Windows Marketing EFS

Esportazione verificata il 15 ottobre 2026 del task installato **EFitsys Marketing EFS - Compatibility 06-18**. Un solo task contiene entrambe le ricorrenze giornaliere, alle **06:00 e 18:00** nel fuso Windows di Roma. Il file XML e questa nota sono versionati in Git.

- Backup: `EFitsys-Marketing-EFS-Compatibility-06-18.xml`.
- Esecuzione: `scripts/operations/maintenance-control.ps1 -Action Run`.
- Identità: sessione interattiva Operations, senza password nel backup.
- Conservati avvio al ritorno della disponibilità, risveglio consentito e prevenzione delle esecuzioni sovrapposte.

Il backup conserva la configurazione del task, non certifica il buon esito dei controlli. Per lo stato corrente consultare `.local/operations-teams/maintenance-status.json` e la procedura `../marketing-availability.md`.

## Ripristino

Sul PC originale, da PowerShell nella cartella Marketing EFS:

```powershell
$taskDefinition = Get-Content -LiteralPath 'docs/maintenance/windows-tasks/EFitsys-Marketing-EFS-Compatibility-06-18.xml' -Raw
Register-ScheduledTask -TaskName 'EFitsys Marketing EFS - Compatibility 06-18' -Xml $taskDefinition
```

Il comando non forza la sostituzione di un task già presente. Su un altro PC verificare prima account/SID, percorso del progetto, runtime e fuso orario; preferire la ricostruzione con `scripts/operations/maintenance-control.ps1 -Action Install`, che usa account e percorsi locali. Non importare alla cieca l'identità del PC originale.

Questo backup riguarda il controllo 06:00/18:00; il distinto task al login del servizio Operations mantiene la propria procedura.
