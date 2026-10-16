# Strumenti Virgilio EFS

Gli strumenti di progetto riutilizzabili vivono qui e possono essere versionati.
Dati di esecuzione, log, credenziali, ricevute e temporanei restano in `output/`
o `.local/`, esclusi da Git.

## Inizializzare le cartelle locali

Da PowerShell, nella radice di Virgilio EFS:

```powershell
./scripts/maintenance/initialize-workspace.ps1
```

Il comando crea solo cartelle mancanti sotto questo workspace. È ripetibile e
non sovrascrive file, non contatta servizi e non installa automazioni.
