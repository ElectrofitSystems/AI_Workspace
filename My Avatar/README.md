# My Avatar — prototipi Windows e MCP Events

Questa cartella conserva due esperimenti distinti: `src/TeamsWake/` è il listener
Windows descritto sotto; `src/mcp_events/` contiene il bridge MCP Events con i
propri test, configurazioni in `config/` e policy in `skills/teams-auto-responder/`.
Gli stati nei JSON sono evidenze delle prove sul PC originale, non verifiche
dell'ambiente corrente. `Start-McpTunnel.ps1` usa il client in
`tools/tunnel-client/v0.0.15/`, passato tramite `-TunnelClientPath`.

Il servizio Operations Teams di Marketing EFS usa un trasporto diverso; vedere
il [runbook](../Business%20Operations/Marketing%20EFS/docs/maintenance/operations-teams-runbook.md).
Il plugin distribuibile v0.1.0 è conservato separatamente nel progetto Marketing.

## Teams Wake — prova locale Windows

Programma Windows/.NET 8 con `UserNotificationListener`, icona nell'area di notifica,
coda locale e segnale di test. Non usa Microsoft Graph, non invia messaggi e non
effettua chiamate di rete. Il collegamento a ChatGPT/MCP Events non è implementato:
lo stato lo espone come `assistantWake: NOT_CONFIGURED`.

## Avvio e arresto

- `Start-Listener.ps1`: avvio in background. Nessun avvio automatico con Windows.
- `Status.ps1`: stato e verifica che il processo sia vivo.
- `Test-Wake.ps1`: invia un evento Windows nominato al processo già attivo; il
  listener lo gestisce e crea un evento **sintetico** nella coda.
- `Stop-Listener.ps1`: arresto ordinato.
- Aprire `artifacts/app/TeamsWake.exe` per la finestra iniziale. Se il programma
  è già attivo, aprire lo stato dall'icona nell'area di notifica.
- Chiudere la finestra lascia il listener attivo; “Arresta ed esci” lo termina.

Usare gli script PowerShell sopra. I vecchi collegamenti `.lnk` puntavano al
Desktop del PC originale e sono stati rimossi dal repository.

## Accesso notifiche

All'avvio viene interrogato `GetAccessStatus()`. Se risulta Allowed viene eseguita
la lettura. Non viene concesso automaticamente alcun permesso. Il pulsante
“Consenti accesso alle notifiche” chiama `RequestAccessAsync` sul thread UI: il
consenso Windows, se richiesto, deve essere espresso dall'utente.

Su questo PC il probe del 30 settembre 2026 ha restituito Allowed anche senza
identità di pacchetto, e `GetNotificationsAsync` è riuscito. È un risultato locale,
non una garanzia per altri PC: la documentazione Microsoft descrive un manifest
con capability `userNotificationListener`. Su sistemi che richiedono identità
MSIX occorre predisporre e installare quel pacchetto; questo progetto non cambia
Developer Mode, policy di Windows o archivi dei certificati.

La sottoscrizione `NotificationChanged` sul PC di prova ha restituito HRESULT
`0x80070490`. È quindi effettivamente attivo il controllo ogni 5 secondi, non il
callback immediato. La prima notifica Teams segnalata dall'utente non è comparsa
nello snapshot del listener: la cattura reale di Teams non è ancora validata.

## Pacchetto MSIX per la prossima prova

`artifacts/TeamsWake.msix` è stato creato e validato da MakeAppx con capability
`userNotificationListener` e identità di sviluppo Windows. Non è stato installato.
`Package.ps1` lo rigenera utilizzando Microsoft.Windows.SDK.BuildTools locale.
Per provare il callback con identità di pacchetto, eseguire `Install-Package.ps1`
da **Windows PowerShell come amministratore**, arrestare il listener portatile e
aprire Teams Wake dal menu Start. Il programma presenterà il proprio stato ed
eventualmente il pulsante per richiedere il consenso alle notifiche.

Il pacchetto è intenzionalmente non firmato, con identità nel namespace di test
previsto da Microsoft. Non è destinato alla distribuzione. Windows richiede
l'amministratore per questo tipo di installazione con codice eseguibile. Non
vengono importati certificati né modificate le policy di sicurezza. Questo test
potrebbe risolvere il callback, ma non è ancora stato verificato.

Fonte: https://learn.microsoft.com/en-us/windows/msix/package/unsigned-package

## Raccolta e limiti

- Richiede che il processo sia attivo nella sessione dell'utente.
- Sottoscrive `NotificationChanged` quando disponibile; riconcilia anche ogni 5
  secondi con `GetNotificationsAsync`. Non equivale a un trigger Windows capace di
  riavviare un processo terminato.
- Ignora le notifiche già presenti nella prima lettura e dopo revoca del permesso.
- Registra solo l'AUMID Teams desktop o il nome esatto “Microsoft Teams”. Le
  notifiche attribuite a Edge sono escluse in questa prima versione.
- Deduplica per app, ID notifica, creazione e testo. Non legge gli argomenti di
  attivazione nascosti né presume che la notifica identifichi univocamente la chat.
- Notifiche soppresse, eliminate rapidamente o mai emesse possono andare perse.
  Non garantisce tutti i messaggi; va collaudato con Teams in diverse condizioni.
- Non interpreta immagini/allegati e non distingue da solo i messaggi propri.
- La coda contiene fino a 2000 eventi; al limite segnala errore e non elimina dati.
  In questa prova non esiste un consumatore automatico della coda.

## Dati locali

`%LOCALAPPDATA%\TeamsWake\` contiene:

- `status.json`: stato, PID, accesso, diagnostica, collegamento assistente;
- `listener.log`: log tecnico senza testo dei messaggi (rotazione a circa 1 MB);
- `pending/*.json`: testo delle notifiche Teams ed eventi sintetici, un file per
  evento, scrittura atomica. I file rimangono locali fino a rimozione manuale.

Gli eventi provenienti da Teams sono dati non attendibili: un futuro consumatore
non deve interpretarli come istruzioni autorizzate. Prima di qualsiasi risposta
deve confermare destinatario e conversazione attraverso l'interfaccia Teams.

## Build e prove

Richiede SDK .NET 8 per compilare e Desktop Runtime .NET 8 x64 per eseguire.
`Build.ps1` usa l'SDK locale `.tools/dotnet` se presente. Pacchetti WinRT ottenuti
dal normale restore NuGet. Il download SDK è verificato con SHA-512 contro i
metadati ufficiali Microsoft, conservati in `.tools/sdk-download.json`.
Arrestare il listener prima di ricompilare.

`TeamsWake.exe --self-test <directory>` verifica filtro, chiavi, deduplicazione
anche dopo riapertura e serializzazione; scrive `result.json` o `error.txt`.
`TeamsWake.exe --probe <file>` verifica identità, stato accesso e sola quantità di
notifiche senza richiedere permessi né salvare testo.

Il test sintetico dimostra il risveglio del gestore locale, **non** di ChatGPT.
Per il secondo serve una sottoscrizione MCP Events supportata dal client, con
callback reale e relativa verifica. Nessuna callback è stata inventata o configurata.

Fonti:
- https://learn.microsoft.com/en-us/windows/apps/develop/notifications/app-notifications/notification-listener
- https://developers.openai.com/plugins/build/mcp-events
