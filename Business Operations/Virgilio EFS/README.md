# Virgilio EFS

Assistente per gli ingegneri di Electrofit Systems: orientamento nelle cartelle
SharePoint e Microsoft Teams e supporto alla compilazione delle automazioni.

Workspace predisposto il **15 ottobre 2026**, sul modello di Marketing EFS.
Leggere [regole](docs/rules.md), [mandato](docs/company/mandate.md),
[contesto](docs/company/context.md) e [fonti](docs/company/sources.md).

## Mandato corrente

**Guida agli ingegneri, senza ristrutturazione e senza file di output.**
Virgilio fornisce percorsi, link e aiuto alla compilazione direttamente nelle chat
personali Teams, solo per ingegneri interni verificati `@efitsys.com` e richieste
specifiche con `@Virgilio`. Ogni conversazione conserva il proprio contesto.

Di norma l'ingegnere verifica e invia. Su sua richiesta esplicita Virgilio può
completare e avviare flussi concordati e inoltrare richieste di approvazione.
**Virgilio non può approvare.** Non riorganizza SharePoint o Teams.

Il primo ambito è **Engineering - Powertrain**; la prima automazione, ancora in
sviluppo, è **Test Request**, prevista con **Power Apps in Teams**. I dettagli
funzionali saranno raccolti più avanti. [Regole Teams](docs/maintenance/teams-guidance.md).

## Flusso di lavoro

1. Capire l'attività, il progetto e il risultato richiesto dall'ingegnere.
2. Individuare team, canale, libreria, cartella e documento corretti.
3. Verificare la revisione della fonte e i campi richiesti dall'automazione.
4. Guidare la compilazione e preparare eventuali bozze nella conversazione.
5. Lasciare all'ingegnere verifica e invio, oppure eseguire l'azione concordata
   esplicitamente richiesta, verificandone l'esito senza assumere approvazioni.

Procedure: [navigazione](docs/navigation/workflow.md) e
[automazioni](docs/automations/workflow.md).

## Cartelle

| Cartella | Uso |
| --- | --- |
| `docs/company/` | Mandato, contesto, fonti, decisioni e modelli |
| `docs/navigation/` | Procedure per orientarsi in SharePoint e Teams |
| `docs/automations/` | Istruzioni e schede delle automazioni concordate |
| `docs/maintenance/` | Versionamento, struttura e stato del progetto |
| `scripts/` | Strumenti riproducibili, senza dati operativi o segreti |
| `input/Technical documentation/` | Copie delle fonti tecniche necessarie |
| `input/Forms/` | Moduli originali e istruzioni di compilazione |
| `input/References/` | Riferimenti acquisiti per le attività |
| `output/` | Cartelle dello scaffold iniziale, non usate per consegne nel mandato corrente |
| `.local/maintenance/temporary/` | Temporanei e verifiche |

`input/`, `output/` e `.local/` sono esclusi da Git. Una nuova copia del repository
non li recupera: eseguire `scripts/maintenance/initialize-workspace.ps1` per le
cartelle vuote, poi recuperare i dati dalle fonti effettive. Il comando non installa
servizi né configura connessioni.

La struttura riprende la separazione di Marketing EFS, con categorie adatte a
Virgilio. Materiali, flussi e configurazioni Marketing restano nel loro progetto.

## Stato iniziale

Struttura locale e regole di versionamento predisposte. Team Engineering - Powertrain,
canali e primi livelli della libreria Documents verificati in lettura il 15/10/2026;
presente la lista Test Requests. L'app e il flusso non sono stati collaudati.
Il registro Operations consultato contiene Marketing ed ERP, senza Virgilio:
l'accesso ai connettori in questa chat non dimostra un servizio `@Virgilio` attivo.

Le istruzioni permanenti sono in [AGENTS.md](AGENTS.md); regole GitHub e convenzioni
di revisione in [versionamento](docs/maintenance/versioning.md).
Punti aperti e prossimo passo: [stato](docs/maintenance/status.md).
