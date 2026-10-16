# Versionamento GitHub e revisioni

## Regole riprese da Marketing EFS

Fonti lette il 15 ottobre 2026: `.gitignore`, `README.md`, `AGENTS.md` e sezione
«Organizzazione del progetto» di `docs/rules.md` del workspace Marketing EFS.

- Versionare documentazione, procedure e strumenti riutilizzabili.
- Escludere `input/`, `output/` e `.local/`: originali, risultati, evidenze e stato
  operativo sono conservati separatamente da Git.
- Escludere credenziali locali, database, bytecode e artefatti del sistema
  operativo secondo il `.gitignore`, copiato senza modifiche dal modello.
- Conservare master, originali e revisioni; usare nomi descrittivi e versionati
  per le consegne. Non riscrivere le evidenze storiche.
- Una copia Git non ricrea dati esclusi, accessi, plugin, servizi o automazioni;
  verificare il nuovo ambiente e recuperare i dati dalle fonti documentate.

Queste sono le regole effettivamente individuate nel modello; non vi è stata
trovata una policy specifica per branch, pull request o approvazione dei commit.

## Repository già esistente

Radice locale: `C:/Users/Operations/Documents/AI_Workspace`.
Remote origin: `https://github.com/ElectrofitSystems/AI_Workspace.git`.
Virgilio EFS è una cartella di questo repository, senza repository Git annidato.
Branch rilevato alla predisposizione: `main`, con upstream `origin/main`.
Nessun commit o push è stato eseguito per la predisposizione iniziale.

## Convenzioni iniziali di Virgilio

Queste convenzioni integrano il modello; non sono attribuite a Marketing EFS:

- Per nuovi branch usare il prefisso `codex/`, salvo indicazione dell'utente.
- Prima di stage e commit leggere stato e diff; includere solo le modifiche
  pertinenti, preservando quelle degli altri progetti. Evitare `git add .`
  dalla radice del repository condiviso.
- Usare commit descrittivi e verificare che non contengano dati operativi o
  segreti. Non forzare in Git i file esclusi.
- La richiesta di copiare le regole non equivale a una richiesta di push.
- Per le consegne locali usare `<nome>-YYYYMMDD-vNN.<estensione>` e dichiarare
  lo stato. Una nuova revisione non implica approvazione automatica.
- Le procedure canoniche in `docs/` mantengono nomi stabili: la loro cronologia
  è in Git; non occorre duplicarle come v01/v02 a ogni modifica.

## Cartelle escluse su un nuovo host

Eseguire `scripts/maintenance/initialize-workspace.ps1` per ricreare le directory
vuote. Recuperare separatamente documenti e dati; non inserire dati dimostrativi
al posto di fonti o approvazioni mancanti. I link e i limiti del recupero vanno
documentati in `docs/company/sources.md`.
