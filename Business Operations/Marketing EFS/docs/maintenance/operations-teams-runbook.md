# Operations in Teams — servizio locale

Mandato del 02/10/2026: chat individuali con operations@efitsys.com per colleghi
interni verificati di efitsys.com. Operations coordina gli agenti; oggi il ruolo
personalizzato marketing è «Agente marketing EFS». Dal 05/10/2026 è disponibile
anche «Agente ERP EFS» per il pilota scadenzario fornitori.

## Trasporto ed esecuzione

`scripts/operations/teams_service.py` usa il Codex app-server locale su stdio e il
connettore Teams già collegato. Nessun nuovo token Microsoft, applicazione Entra,
tunnel pubblico, Power Automate o coda OneDrive.

Il servizio controlla le chat con intervallo obiettivo di 2 secondi. La durata
effettiva include le chiamate al connettore e può superare l'intervallo. I controlli
non generano turni di modello; Operations e gli specialisti lavorano solo quando
arriva una richiesta. Tre worker con assegnazione stabile per chat separano i
contesti e conservano l'ordine dei messaggi di ogni collega. Le letture delle chat
sono concorrenti, con massimo tre richieste in corso.

Il modello resta quello configurato nell'account Codex. Il servizio usa effort low
per la conversazione; non cambia le preferenze delle altre chat. Le richieste
Marketing attivano il ruolo personalizzato, la cui identità è verificata con
thread/read. Lo stesso specialista viene riutilizzato nella sua chat. Le menzioni
testuali `@Marketing` e `Marketing, ...` sono riconosciute; non creano un nuovo
utente Teams o il selettore agenti di ChatGPT. Operations può scegliere lo
specialista anche in base al contenuto della richiesta.

## Perimetro

Dal 15 ottobre 2026 il proprietario autorizza strumenti di produzione e file Marketing
per tutti i colleghi interni verificati con dominio esatto efitsys.com. Dopo la
verifica di tenant, oneOnOne, membri e identità Entra, le richieste non ERP usano
una sessione distinta per chat con profilo `operations_marketing_internal` e
coordinatore `scripts/operations/marketing-coordinator.md`. Policy nominativa di
dominio e account Operations in `scripts/operations/marketing-access.json`.
Le richieste del collega non possono modificare questa policy.

Il profilo eredita le skill, i plugin e i connettori installati e abilita shell,
ricerca e produzione di file in input/, output/ e .local/maintenance/temporary/.
Configurazioni e codice restano in sola lettura; dati ERP, file di autenticazione,
cronologie Codex e stato del servizio Operations restano negati. Il profilo ERP
separato conserva i propri limiti e l'accesso finanziario nominativo.

L'agente può creare documenti, presentazioni, visual e animazioni reali, verificarli
e consegnare i soli risultati utili nelle categorie esistenti SharePoint
Marketing/Outputs secondo le regole del progetto. Il trasporto restituisce testo
e link verificati nella stessa chat: l'assenza di allegati binari Teams non limita
la produzione e consegna del file. Non dichiarare un asset realizzato o riprodotto
senza prova; precisare se è PPTX con effetti, media incorporato o video esportato.
La prima istanza del ruolo registrato e la sua ricreazione dopo riavvio sono
autorizzate; non confonderle con la registrazione di un agente nuovo.

Il servizio non pubblica su LinkedIn, non concede permessi e non acquisisce
automaticamente allegati. Review del contenuto, revisione esatta e autorizzazione
di pubblicazione restano distinte. Il vecchio recupero limitato a testo/storyboard
non definisce le capacità del nuovo profilo. Gli altri controlli del trasporto,
claim, deduplicazione e readback rimangono obbligatori.

Estensione ERP del 05/10/2026: progetto canonico ERP EFS, accesso finanziario
limitato al solo Francesco Lucherini tramite confronto user ID + email + tenant.
La policy è ERP EFS/config/access.json. Il trasporto legge lo snapshot validato
solo dopo il controllo; lo ricontrolla prima dell'invio insieme alla versione
e alla scadenza dei dati. Gli altri colleghi ricevono un diniego deterministico.
I worker ERP adottano il profilo operations_teams con rete comandi disabilitata,
Apps/MCP/plugin/browser disabilitati e cartelle ERP input/output/.local negate.
Le istruzioni pubbliche sono leggibili. Il sandbox nativo richiede root read:
il profilo protegge esplicitamente i dati, senza dichiarare una whitelist globale.
Il runtime verificato è codex 0.160.0 (f544b3844e0f14e9).
Le richieste ERP sono elaborate in sessioni nuove per non riutilizzare importi
obsoleti; la conversazione Marketing conserva la propria sessione.
Fonte iniziale: esportazione EC742 manuale, senza aggiornamento automatico.
Lo snapshot scade al cambio della data Europe/Rome o dopo 24 ore. Nessuna
ricorrenza ERP, messaggio proattivo o scrittura contabile è stata attivata.
Prove locali e stato corrente: ERP EFS/docs/status.md; il collaudo reale ERP
in Teams va eseguito da Francesco con una sua richiesta nella chat individuale.

L'account e le connessioni sono quelli locali esistenti. Il PC Operations deve
rimanere acceso, con sessione Windows attiva e accesso Internet. Il servizio usa
il runtime Codex anche fuori dalla chat desktop; scadenza della sessione, limiti
d'uso, indisponibilità del connettore e sospensione del PC ne interrompono il
funzionamento. Non è un backend cloud con disponibilità garantita.

## Stato, avvio e arresto

Aggiornamento del 15 ottobre 2026: disponibilità e compatibilità sono controllate
anche dal task Windows alle 06:00 e 18:00 Europe/Rome secondo
`docs/maintenance/marketing-availability.md`. Runtime e helper vengono individuati
dinamicamente ad ogni riavvio, senza fissare vecchie cartelle hash di aggiornamento.
Il comando `service-control.ps1 -Action Restart` attende l'arresto del servizio
e del watchdog prima di ripartire, senza creare monitor concorrenti.

Da PowerShell nella cartella canonica:

```powershell
& scripts/operations/service-control.ps1 -Action Status
& scripts/operations/service-control.ps1 -Action Start
& scripts/operations/service-control.ps1 -Action Stop
```

`Status` verifica sia il processo sia health.json, con ora dell'ultima scansione.
Su una nuova copia Git la configurazione `.local/operations-teams/config.json`
deve essere recuperata dall'installazione autorizzata; la sua assenza blocca
Start, Watchdog e InstallStartup prima di creare il file di abilitazione.
I percorsi degli eseguibili non dipendono più dal PC Operations: Python viene
cercato nel runtime dell'utente corrente e poi nel PATH; `codex.exe` nel PATH.
Si possono specificare `-PythonPath` e `-CodexPath`, oppure le variabili
`OPERATIONS_PYTHON` e `OPERATIONS_CODEX`. Per Start e InstallStartup è richiesto
anche `pythonw.exe` accanto a `python.exe`. Dopo uno spostamento, l'eventuale task
Windows preesistente conserva i vecchi percorsi: aggiornarlo esplicitamente con
InstallStartup nella configurazione operativa. La pulizia del repository non
installa né avvia task. Nel registro `scripts/operations/agents.json`, workspace
`.` indica la radice Marketing EFS, non la directory del registro.

`Stop` rimuove soltanto `.local/operations-teams/service.enabled`; il blocco viene
ricontrollato anche prima degli invii. Il watchdog riavvia un processo terminato
solo finché il file di abilitazione esiste. Non riavviare prima che il precedente
processo sia arrestato. Il task Windows «EFitsys Operations Teams» avvia il
watchdog al login di Operations, con privilegi normali e senza password salvate.

Percorsi locali: config.json, state.sqlite3, service.jsonl e health.json in
`.local/operations-teams/`. Configurazione e registro agenti non sono credenziali.
I log conservano ID, stati e tempi, senza corpi dei messaggi. Le conversazioni
restano in Teams; le sessioni di modello sono separate per collega. Dopo un
riavvio vengono recuperati gli ultimi messaggi pertinenti della sola chat, a
partire dall'attivazione. Non caricare log o cronologie private in SharePoint.

## Controlli prima di rispondere

Verificare account Operations, URL/tenant Teams, tipo oneOnOne, esattamente due
membri e corrispondenza email/UPN con identità Entra risolte. Escludere ospiti,
esterni, gruppi, bot, messaggi del proprietario, cancellati e precedenti ad
activated_at. Non usare il solo indicatore unread. Chat e message ID legano ogni
richiesta al destinatario.

Il database conserva claim e lease. L'acknowledgement ha un proprio stato;
la risposta finale passa per prepare prima dell'invio e sent dopo il readback.
Un esito ambiguo con response_hash rimane needs_review: nessun secondo invio
automatico. Un claim senza preparazione di invio può essere rielaborato al
riavvio, dopo una nuova verifica; i messaggi modificati rimangono da rivedere.
La verifica di copertura evita di avanzare se la lista raggiunge i limiti.

## Tempi e prove

Non promettere risposte complete in cinque secondi. La presa in carico e il
risultato dello specialista sono due misure distinte. Registrare entrambi usando
i timestamp Teams e il tempo locale del modello, senza usare il solo intervallo
di polling come misura di latenza.

La prima scansione aggressiva ha ricevuto HTTP 429 Microsoft. `appserver.py`
condivide cooldown.json fra i processi e impedisce nuove chiamate prima del
Retry-After. Il monitor legge il dettaglio dei messaggi quando cambia l'anteprima
e comunque ogni minuto per recupero. L'intervallo obiettivo di polling non
garantisce cinque secondi; una sospensione imposta dal server prevale.

Una prova locale di riuso dello stesso ruolo ha richiesto 13,4 secondi di
elaborazione. Non comprende il trasporto Teams. Il runtime vieta turn/start
diretto sui sottoagenti: il coordinatore riutilizza lo specialista tramite
gli strumenti di collaborazione, senza aggirare questo vincolo.

Il 02/10/2026 il test manuale del referente configurato nel flusso Microsoft è stato risposto dal vero Marketing
tramite Operations. Il secondo test interamente automatico («retrofit») ha
ricevuto acknowledgement in 14,9 secondi e risposta completa in 52,7 secondi,
con identità dello specialista e readback verificati. Letture concorrenti e
riuso dello specialista sono miglioramenti successivi: non attribuire loro una
latenza misurata finché non si ripete il test reale.

Test locali: `python -m unittest discover -s scripts/operations -p 'test_*.py'`.
Controllano esclusioni, destinatario, duplicati, esiti incerti, acknowledgement,
arresto e separazione di due chat. È verificata anche una richiesta reale di un
secondo collega in una chat diversa: acknowledgement 10,9 secondi, risposta
Operations 42,0 secondi. I 13 test locali e queste due chat non dimostrano un
collaudo di tutti gli utenti dell'organizzazione.

## Riferimenti verificati

- [Codex app-server](https://learn.chatgpt.com/docs/app-server): JSON-RPC,
  mcpServer/tool/call, thread/start e turn/start.
- [Configurazione Codex](https://learn.chatgpt.com/docs/config-file/config-reference).

## Correzione instradamento e verifica destinatari - 13/10/2026

Il dominio dei destinatari deve essere esattamente efitsys.com, sia nei membri
Teams sia nelle identità Entra risolte con corrispondenza esatta di email, UPN e
ID. Domini simili, sottodomini, ospiti, identità mancanti o ambigue non ricevono
risposte. Il testo dei messaggi e i nomi visualizzati non attribuiscono identità
né autorizzazioni. Restano invariati tenant, account Operations, filtro oneOnOne,
policy ERP nominativa e autorizzazioni Marketing/LinkedIn.

L'instradamento ERP considera la richiesta corrente e solo continuazioni
esplicite di una conversazione ERP del collega. Report e dinieghi di Operations
non attivano il routing; una domanda generale interrompe il contesto ERP.
Scadenza della sessione e fornitore del plugin non indicano fatture. I veri
follow-up restano soggetti agli stessi controlli di identità, accesso, snapshot
valido e verifica della destinazione prima dell'invio.

Se il readback incontra un rate limit, viene ripetuta soltanto la lettura della
ricevuta già ottenuta: nessuna nuova generazione o secondo invio. Un esito
ambiguo continua a richiedere riconciliazione con messaggio e hash esatti.
Il saluto Mohammad del 12/10, ID 1791820983544, è stato riconciliato senza
reinviarlo. Le due richieste Francesco in recovery_held restano in attesa;
un inoltro Lucia privo di testo leggibile è anch'esso trattenuto per verifica.
Queste modifiche non attestano il collaudo di una nuova domanda generale in
Teams: registrare richiesta, risposta pertinente, tempi e readback prima di
confermare il ripristino funzionale.

Collaudo reale del 13/10/2026: Matteo Ravera, verificato tramite email, UPN e
ID Entra esatti, ha inviato TEST-OPS-INTERNO-13OTT alle 13:35:37.239 UTC
(ID 1791898537239). Operations ha risposto in modo pertinente alle
13:36:00.493 UTC (ID 1791898560493): acknowledgement 2,928 s, risposta
23,254 s, modello 7,484 s. Readback, hash e stato sent verificati; una sola
risposta finale e un solo acknowledgement, senza duplicati nel controllo
successivo. Prove locali: .local/maintenance/temporary/operations-routing-20261013/e2e-evidence.json.
L'utente riferisce che Teams blocca il contatto dall'account esterno; nessun
aggiramento. Il filtro applicativo esterno è collaudato nei test locali, mentre
questa prova non certifica un test esterno end-to-end dell'applicazione.
