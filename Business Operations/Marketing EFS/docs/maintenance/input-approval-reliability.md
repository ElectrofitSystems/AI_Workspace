# Affidabilità delle approvazioni Marketing Inputs

Aggiornamento autorizzato dall'utente il 15 ottobre 2026. Stato cloud:
**live_verified_controlled_tests**. La versione `1.0.1.1` è importata, attiva e
operativa nei test controllati di acquisizione, creazione seriale e riesecuzione
senza duplicati. Non è una garanzia di assenza di errori futuri. Il collaudo del
5 ottobre rimane una prova storica distinta.

## Stato concreto — 15 ottobre 2026

- **Locale validato:** skill `efs-approval-operations`, procedure e definizioni
  dell'agente aggiornate. Skill validator e parsing delle due definizioni TOML
  superati; questo non dimostra un'esecuzione cloud corretta.
- **Cloud `live_verified_controlled_tests`:** stesso flusso Inputs, ID
  `d566e7c1-4941-77a4-abcc-752887b781dc`, ora Scheduled ogni 5 minuti, concorrenza
  1 e acquisizione/dispatch in due fasi della stessa run. Versione `1.0.1.1`
  importata e attiva; non è stato creato un secondo flusso inviante.
- Creata soluzione unmanaged **EFS Marketing Approval Reliability**, unique name
  `EFSMarketingApprovalReliability`, ID `3c29e105-9cc8-f111-a059-e4fb1ef6bee7`.
  I primi tentativi di download dell'export `1.0.0.2` non avevano restituito lo
  ZIP. Successivamente acquisito il backup originale `1.0.0.3`, CRC verificato,
  SHA256 `a651b8b238bad1d7bd3ed9d8c74b3dd0a7a4e91b34b6fcd5c8d84e4ebcf89e14`.
  Rimangono lo stesso workflow GUID `90ba7edd-9fc0-f111-aaad-70a8a57edd59`, la
  connection reference `new_sharedsharepointonline_d0d97`, approvatori e awaitAll
  dell'originale. Pacchetti, builder, test e rollback sono in
  `docs/maintenance/power-automate/input-approvals-20261015/`.
- Creata lista SharePoint **EFS Marketing Approval Queue**, ID
  `db240db6-c151-40f6-8851-3773be6091f3`, ora collegata al flusso: `Title` univoco
  e indicizzato, `DispatchState` e `Payload` JSON in campo multilinea plaintext.
  Bootstrap `1.0.1.0` riuscito, run `08584095338416461887125515450CU14` alle
  14:04 UTC: schema verificato e checkpoint `__cursor__` creato con `lastId=0`,
  cutover persistito `2026-10-15T14:01:21Z`.
- Run live `08584095333550505814206822293CU02`, avviata alle 14:12 UTC,
  **Succeeded**, durata 90 secondi: acquisiti i due file test esplicitamente
  NON USARE `656` e `657`, caricati alle 14:10 UTC, revisione 1.0. Cursor `657`,
  righe queue 2 e 3 entrambe `approval_created`, tentativo 1. ApprovalId autentici
  verificati; stato Microsoft `_ApprovalStatus=1` Requested, nessuna decisione
  umana espressa o simulata. I due test restano esclusi dalle fonti editoriali.
- Riesecuzione `08584095332359662866147049326CU00` alle 14:14 UTC,
  **Succeeded**, durata 5 secondi: sempre tre righe totali (cursor e due test),
  cursor `657`, stessi due ApprovalId e tentativo 1. Nessuna nuova richiesta.
- Il recupero corrente dell'elemento storico `648` restituisce 404, quindi non
  permette di ricostruire richiesta e revisione originali. Il kit 4.1 ZIP,
  elemento `652`, mostra invece `_ApprovalStatus = 1` (Requested): una richiesta è
  già presente e non va ricreata. Nessuno dei due controlli autentica da solo una
  decisione umana o completa la riconciliazione dei 34 errori della notifica.

La correzione è operativa per i nuovi input nel perimetro configurato. La riconciliazione
eseguita prima dei due nuovi test copre 69 file in Inputs: i soli due successivi alla soglia storica sono
il vecchio test NON USARE e il kit 4.1 già Requested; non risultano richieste di
produzione correnti mancanti da reinviare. L'elemento storico 648 non è recuperabile
e questo non equivale alla riconciliazione integrale di tutte le run del 7 ottobre.
Dettagli e prove: `output/Linkedin/config/input-approval-automation.json` e
`output/Statistics/maintenance/input-approval-repair-20261015/`.

### Risultati e limiti del collaudo controllato

Tutti i timestamp seguenti sono UTC del 15 ottobre 2026.

| Item / revisione | ApprovalId | Inizio creazione | Risposta e registrazione |
| --- | --- | --- | --- |
| 656 / 1.0 | `bff107bd-64cf-423b-be3e-87c25e2f09ca` | 14:12:18.021 | 14:12:29.685 |
| 657 / 1.0 | `7a57df33-ca4a-4683-8d88-2d8be4d3a4fa` | 14:13:01.896 | 14:13:06.344 |

La seconda creazione è iniziata 32,21 secondi dopo la conclusione della prima,
coerentemente con il pacing di 30 secondi. Sono dimostrati acquisizione persistita,
cursor, due creazioni seriali e riesecuzione senza nuove richieste sugli stessi
elementi. **Non sono stati provati live** replay forzato del cursor, crash durante
il lease, scadenza reale di una riga processing o un nuovo throttling 429. Le
protezioni corrispondenti sono presenti nel workflow e coperte dalle verifiche
locali della struttura, ma non vanno descritte come scenari live già osservati.
Non provocare un 429 nel servizio per ottenere una prova. La ricostruzione di tutte
le 34 run storiche resta distinta dall'audit dei file correnti.

## Errore accertato e perimetro

La notifica Outlook del 7 ottobre segnala 34 errori del flusso **EFS Marketing -
Inputs - Automatic Approvals**, ID `d566e7c1-4941-77a4-abcc-752887b781dc`.
Nella run `08584102195153076959048008794CU11`, per
`EFITSYS_Business_Letter_A4.docx`, list item `648`, l'azione SharePoint
`CreateApprovalRequest` restituisce `502 BadGateway`; il dettaglio contiene
`500` e `(429) Too Many Requests`. Più run sono partite nello stesso minuto;
concorrenza del trigger disattivata e retry dell'azione impostato a None.
Il numero della notifica non prova che manchino 34 approvazioni distinte.

Restano invariati origine Marketing/Inputs, esclusione delle cartelle e filtro
di percorso. La soglia storica `2026-10-05T09:30:55Z` resta il riferimento della
riconciliazione; il nuovo polling acquisisce solo `Created` dal cutover persistito
`2026-10-15T14:01:21Z`, senza reinviare il pregresso. Per il riuso editoriale applicare
`../company/marketing-input-folder.md` e `../company/input-approvals.md`.
Il flusso Outputs dei derivati, gli approvatori configurati in Microsoft e le
autorizzazioni di pubblicazione restano nei rispettivi ambiti.

## Coda persistente e creazione seriale

Il singolo flusso Scheduled ogni 5 minuti, concorrenza 1, svolge due fasi:
acquisizione persistente e dispatch seriale. Legge al massimo 100 elementi per
pagina, ordinati per ID, con filtri server-side `Id > lastId`, `Created` dal
cutover, percorso Inputs e `FSObjType=0`. Aggiorna il cursor con ETag soltanto dopo
che tutte le acquisizioni sono riuscite o già presenti. La coda conserva gli
eventi durante riavvii; non si affida alla coda limitata del precedente trigger
SharePoint con SplitOn.

Nel sito fisso Documentation la chiave `Title` è
`libraryId:itemId:refVersion:input-reference-review`; una ripetizione riusa la voce
esistente. La versione assente entra in `unknown`, senza inventarla. Il payload
conserva snapshot del riferimento e `targetRevisionVerified=false`: il worker
non risolve né certifica automaticamente la revisione dell'originale di un `.url`.
Il revisore la identifica nella review di ingresso; prima del riuso l'agente
deve verificarla insieme alla decisione autentica. Uno stato del link non basta.

La coda deve conservare almeno chiave, identità e revisione osservate, ambito,
stato, `attempts`, eventuale `nextAttemptAt`, ultimo errore, riferimenti alle run e alla
richiesta Microsoft, date di aggiornamento. URL e prove appartengono al record;
non inserire credenziali o copie dell'intero contenuto. Imporre unicità della
chiave nel servizio, acquisire la voce con aggiornamento condizionale/lease e
impedire creazioni concorrenti. Il lease registra run, inizio e scadenza dopo
15 minuti. Righe `processing` rimaste tali oltre 15 minuti diventano `unknown`
con ETag e richiesta di riconciliazione; non tornano automaticamente `queued`.
Il dispatch elabora al massimo 3 righe `queued` per run, una alla volta, con
30 secondi di attesa dopo ogni tentativo di creazione. Prima della creazione
rilegge revisione, percorso, tipo file e stato nativo. Lo stato moderno è il
campo Integer `_ApprovalStatus`, REST `OData__ApprovalStatus`, verificato nel
bootstrap: 1 corrisponde a Requested sul kit 652, 0 a NotSubmitted sul test
storico. Non confonderlo con `_ModerationStatus`.

Gli stati di consegna sono distinti dalla decisione umana:

| Stato | Significato e passo consentito |
| --- | --- |
| `queued` | Evento persistito; verificare revisione e richiesta preesistente. |
| `processing` | Un worker detiene il lease; nessun secondo creatore. |
| `approval_created` | Richiesta autentica osservata con ID o riferimento verificabile. |
| `existing_request` | Stato nativo già presente: conservare riferimento e riconciliare; nessuna nuova creazione. |
| `unknown` | Esito ambiguo o servizio non leggibile; riconciliare prima di creare. |
| `manual_review` | Limite tentativi/tempo raggiunto o impedimento non transitorio. |
| `superseded` | Revisione superata; conservare storia e trattare separatamente la nuova. |
| `source_missing` | Rilettura della fonte restituisce 404; nessuna creazione o sostituzione automatica. |

Il limite è 5 tentativi; non è una politica di reinvio automatico degli unknown.
L'azione nativa ha retry None e registra `approval_created` soltanto con ApprovalId
non vuoto. Una risposta vuota rimane `unknown` anche se HTTP riuscito. Il flusso
non attende la decisione umana e non approva contenuti come agente.

## Throttling, retry e risultati ambigui

Leggere anche il corpo degli errori annidati: un wrapper 502 può nascondere 429.
Per throttling rispettare `Retry-After` quando disponibile; altrimenti applicare
backoff esponenziale con limite e jitter, persistendo `nextAttemptAt`.
Il pacchetto conserva anche `retryAfterRaw`: secondi numerici alimentano l'attesa;
una data HTTP rimane nella prova originale, da rispettare prima del recupero.
Non è convertita in un permesso di reinvio automatico. Il fallback registrato
è limitato e con jitter; le righe ambigue restano in quarantena.
Non aggiungere il retry automatico alla creazione non idempotente senza controllo
dei duplicati. Timeout, 5xx, errore annidato o perdita della risposta possono
avvenire dopo che il servizio ha creato la richiesta: iniziare da `unknown`.

Prima di un nuovo tentativo, leggere il servizio originale e le run correlate:
se esiste già una richiesta sulla stessa revisione/ambito, collegarla e non
ricrearla. Se la richiesta è definitivamente assente e l'errore è transitorio,
ammettere il tentativo successivo con attesa. Se l'assenza non è verificabile,
lasciare `unknown`; non trattare un elenco parziale o un errore di accesso come
prova di assenza. Errori di autenticazione, autorizzazione o revisione non si
risolvono con retry ripetuti. Segnalare il limite concreto senza cambiare accessi
o scegliere altri destinatari.

## Recupero e verifica della correzione

1. Salvare una copia versionata della configurazione osservata prima della
   modifica; conservare ID dei flussi, run e prove, senza segreti.
2. Riconciliare ogni esecuzione fallita nel periodo effettivamente coperto con
   elemento, revisione e richiesta Microsoft. Separare richieste esistenti,
   mancanti verificate, esiti ambigui e revisioni superate.
3. Rimettere in coda soltanto le richieste mancanti verificate e ancora pertinenti
   nel perimetro autorizzato; conservare i conteggi e gli esclusi. Non usare
   Resubmit in massa, non ricreare richieste riuscite e non approvare come agente.
4. Verificare nel servizio salvataggio, stato attivo e filtri; provare con evento
   controllato dichiarato NON USARE o con elemento reale già autorizzato. Un test
   non diventa una fonte editoriale e non richiede una risposta umana simulata.
5. Verificare acquisizione persistente, serialità e ripetizione senza duplicati.
   Per recupero dopo riavvio e gestione 429/timeout distinguere protezioni presenti,
   verifiche locali/simulate e casi live effettivamente osservati. Non provocare
   throttling reale né dichiarare eseguiti scenari soltanto previsti dal codice.
6. Controllare ID/revisione della richiesta autentica e assenza di duplicati;
   aggiornare stato, ID dei componenti effettivamente creati, configurazione e
   limiti in `output/Linkedin/config/input-approval-automation.json`. Backup e
   specifiche riusabili restano nel progetto; diagnostica temporanea in `.local/`.

Se mancano strumenti o accesso di modifica al servizio, completare skill, regole
e specifica verificabile e dichiarare il punto cloud ancora da applicare; non
registrare la migrazione come attiva o gli errori come risolti. Le ricorrenze
Marketing esistenti riconciliano le decisioni come prima, senza nuove schedule
Codex, messaggi Teams, invii o pubblicazioni aggiuntive.

## Riferimenti Microsoft

- [Limiti di Power Automate](https://learn.microsoft.com/en-us/power-automate/limits-and-config): concorrenza, code delle run e SplitOn.
- [Ottimizzazione dei trigger](https://learn.microsoft.com/en-us/power-automate/guidance/coding-guidelines/optimize-power-automate-triggers): filtri e concorrenza dei trigger.
- [Throttling SharePoint e Retry-After](https://learn.microsoft.com/en-us/sharepoint/dev/general-development/how-to-avoid-getting-throttled-or-blocked-in-sharepoint-online): gestione di 429/503 e attese.
