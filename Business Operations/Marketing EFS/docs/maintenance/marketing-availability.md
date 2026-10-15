# Marketing EFS — disponibilità e compatibilità

Mandato del 15 ottobre 2026: mantenere l'Agente marketing EFS e i suoi strumenti
operativi per tutti i membri interni verificati efitsys.com, e controllare due
volte al giorno (06:00 e 18:00 Europe/Rome) che gli aggiornamenti non blocchino il lavoro.

Il servizio usa Codex app-server locale, le connessioni esistenti e il watchdog
Windows; l'elaborazione principale non richiede che la finestra desktop resti aperta.
Il watchdog individua il CLI installato funzionante con il relativo helper Windows
ad ogni riavvio, senza fissare la cartella hash di una vecchia versione.

Il task Windows «EFitsys Marketing EFS - Compatibility 06-18» esegue
`scripts/operations/maintenance-control.ps1 -Action Run`. È distinto dalle quattro
ricorrenze editoriali, che non cambiano. Task al login per il servizio e task
06/18 restano indipendenti dall'apertura della chat; nessuna password salvata.
Richiede PC disponibile e sessione Windows Operations attiva. Recupera un orario
saltato al ritorno della disponibilità; WakeToRun non garantisce il risveglio di
qualsiasi dispositivo. Browser e strumenti che richiedono una sessione desktop
attiva possono avere limiti propri: il controllo non simula una verifica UI.

Controlli: CLI/helper correnti, TOML dell'agente, profilo di produzione, scrittura
e rilettura in sandbox, skill richieste caricate senza errori, strumenti MCP,
lettura SharePoint e disponibilità del ruolo esatto tramite una delega di prova.
Non pubblica, non invia messaggi di prova e non carica file diagnostici nel cloud.
Le prove di ruolo nelle ricorrenze sono autorizzate per questo solo collaudo.

Ripara automaticamente percorsi runtime e il preciso ACL obsoleto sulla radice
.local che impediva l'accesso ai temporanei; mantiene negati dati ERP, credenziali
e stato privato del servizio. Riavvia un servizio interrotto soltanto quando
`service.enabled` esiste. Un arresto esplicito resta rispettato. Nessun secondo
monitor simultaneo e nessun reinvio cieco di richieste con esito incerto.

Se un aggiornamento rimuove il runtime Node del connettore, ricerca una copia
installata completa e aggiorna soltanto i suoi riferimenti MCP, con backup e
confronto semantico per preservare tutta la configurazione non pertinente.
Le 06:00 e 18:00 seguono il fuso Windows di Roma anche nel cambio ora legale/solare.

Per guasti di compatibilità tecnici, dopo snapshot dei file, può eseguire una
manutenzione Codex limitata a codice Operations, definizioni Marketing e riferimenti
alle skill/plugin già installati. Verifica con i test e ripete il collaudo prima di
segnare sano. Non cambia identità, controlli ERP, approvazioni, brand, modello,
cadenze o permessi; non installa plugin nuovi e non altera pacchetti firmati.
Per login scaduti, consensi nuovi, revoche, quote o indisponibilità esterne registra
`attention_required` senza aggirare i controlli. Non forza aggiornamenti o riavvii
dell'app desktop mentre si lavora: seleziona le versioni installate e controlla
la compatibilità. Una riparazione non verificata non viene dichiarata riuscita.

Stato locale: `.local/operations-teams/maintenance-status.json`. Prove e backup in
`.local/maintenance/temporary/marketing-maintenance/`; nessuna cronologia Teams
nei rapporti. Comandi: `maintenance-control.ps1 -Action Install|Run|Status`.
