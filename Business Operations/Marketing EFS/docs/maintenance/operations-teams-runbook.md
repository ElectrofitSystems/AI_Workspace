# Operations in Teams — servizio locale

Mandato del 02/10/2026: chat individuali con operations@efitsys.com per colleghi
interni verificati di efitsys.com. Operations coordina gli agenti; oggi il ruolo
personalizzato disponibile è «Agente marketing EFS».

## Trasporto ed esecuzione

`scripts/operations/teams_service.py` usa il Codex app-server locale su stdio e il
connettore Teams già collegato. Nessun nuovo token Microsoft, applicazione Entra,
tunnel pubblico, Power Automate o coda OneDrive. My Avatar 0.1 resta installato e
conservato; il suo bridge non esegue questo servizio.

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

Conversazione, spiegazioni, analisi e bozze testuali. L'esecutore degli agenti ha
sandbox read-only e connettori Apps disabilitati: gli invii della risposta sono
eseguiti soltanto dal trasporto verificato. Il servizio non pubblica su LinkedIn,
non concede permessi e non acquisisce automaticamente allegati. Le azioni ulteriori
richiedono gli strumenti e le autorizzazioni del progetto. Non dichiarare allegati,
upload o operazioni che il servizio non ha eseguito.

L'account e le connessioni sono quelli locali esistenti. Il PC Operations deve
rimanere acceso, con sessione Windows attiva e accesso Internet. Il servizio usa
il runtime Codex anche fuori dalla chat desktop; scadenza della sessione, limiti
d'uso, indisponibilità del connettore e sospensione del PC ne interrompono il
funzionamento. Non è un backend cloud con disponibilità garantita.

## Stato, avvio e arresto

Da PowerShell nella cartella canonica:

```powershell
& scripts/operations/service-control.ps1 -Action Status
& scripts/operations/service-control.ps1 -Action Start
& scripts/operations/service-control.ps1 -Action Stop
```

`Status` verifica sia il processo sia health.json, con ora dell'ultima scansione.
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
- [My Avatar: audit locale](myavatar.md), con problemi della versione originale.
