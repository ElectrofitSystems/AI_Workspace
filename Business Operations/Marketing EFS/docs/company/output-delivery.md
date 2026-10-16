# Outputs — consegna essenziale

Regola permanente richiesta dall'utente il 02/10/2026; vale per qualsiasi attività marketing EFS, assistente e ricorrenza, anche da chat esterne al progetto. Ha precedenza sulle istruzioni precedenti di caricare pacchetti interni completi.

## Consegna richiesta tramite Teams — 16 ottobre 2026

Per una richiesta Marketing ricevuta da Operations, caricare e verificare il file
prima di rispondere con il collegamento. Usare la destinazione canonica nota;
**datasheet e schede tecniche vanno in
`General/Marketing/Outputs/Documentation/Brochures`**, nella libreria Documentation
/ Shared Documents. Conservare copia e revisione locali in
`output/Documentation/Brochures/`. Le altre categorie mantengono le destinazioni
esistenti di `sources.md`; non chiedere una cartella già documentata.

Soltanto quando la destinazione esatta è ignota, preferire OneDrive Operations/Chat con efitsys
con richiedente efitsys verificato; i file della chat Teams pertinente sono ammessi
quando la loro cartella è stata effettivamente identificata. Dichiarare nel messaggio
questa collocazione alternativa. Verificare cartella e drive reali prima di
caricare; non inventare un URL o una destinazione. Una restrizione sulla cartella
nota non autorizza a eluderla tramite un'altra destinazione. Non duplicare un
upload già riuscito per il solo cambio di canale.

La consegna deve essere accessibile al richiedente interno verificato mediante
tenant, ID Teams/Entra ed email/UPN con dominio **esattamente `efitsys.com`**.
L'autorizzazione del 16 ottobre permette di verificare e, quando necessario e
supportato, concedere a quella identità accesso nominativo in lettura/scrittura
**solo ai file prodotti per la richiesta**. Non estendere permessi a cartelle,
siti, altre richieste, intera organizzazione o altri utenti; nessun link pubblico,
anonimo o «chiunque abbia il link». Non modificare accessi delle fonti o dati ERP.
Se identità, accesso o funzione di condivisione non sono verificabili, dichiarare
la consegna incompleta e il limite concreto, senza promettere accessi inesistenti.

Nel servizio Operations il worker produce e carica il file; è il trasporto a
rileggere `get_drive_item` e ACL e, se necessario, concedere `write` nominativo al
richiedente già verificato, senza email e preservando i permessi ereditati. Il
worker non effettua un secondo grant. Questa operazione non cambia approvatori,
membership o accessi generali.

Prima della chiamata di upload registrare persistentemente l'intento nel journal
locale della richiesta (revisione/hash, destinazione e chiave di correlazione).
Verificare metadata, contenuto/revisione, URL e permesso nominativo effettivo;
registrare ricevuta locale con destinazione, file ID, revisione/hash, identità
destinataria verificata ed esito della consegna. Non basta il solo successo
dell'upload. Dopo timeout riconciliare file e permessi nel servizio prima di
ritentare: `unknown` non equivale a file assente.

Il worker restituisce `response` breve e un array `deliveries` di file già
caricati/verificati. Ogni voce contiene esattamente
`{drive_id,item_id,web_url,e_tag,label,kind}`, con valori reali e `kind` fra
`datasheet|document|presentation|visual|statistics|other`. Non inserire link a file
consegnati senza la corrispondente voce; un percorso locale non è una consegna.
Markdown link opzionali in `response` possono riferirsi solo a questi file.

Il messaggio Teams finale è breve e usa **`html_content` con veri anchor**
`<a href="https://...">Nome del documento</a>`, con URL e testo correttamente
escapati. Il trasporto ricostruisce HTML sicuro da `response` e `deliveries`, senza
fidarsi di HTML arbitrario del worker; eventuale `html_content` dello specialista
non sostituisce questa validazione. Non inviare Markdown o percorsi locali come
sostituti del link Teams.
Concludere la risposta Marketing con la firma esatta
**`- by Agente Marketing EFS`**. Congelare destinatario e payload prima dell'invio,
poi verificare ricevuta/readback e deduplicare; un esito incerto non autorizza un
secondo messaggio. Archiviazione, permesso sul file, approvazione del contenuto e
pubblicazione restano decisioni distinte.

In SharePoint Marketing/Outputs caricare soltanto ciò che il destinatario deve leggere, approvare o usare, nel formato direttamente fruibile. Per un catalogo il PDF è la consegna standard. Un DOCX/PPTX o altro editabile si aggiunge solo quando richiesto o necessario al lavoro del destinatario. Per LinkedIn consegnare la revisione leggibile del testo, l'anteprima necessaria e il visual finale effettivamente usato; un PDF può contenere testo bilingue e anteprime senza duplicarle in altri file. Per la newsletter preparare una versione PDF leggibile per la review; HTML per mailing soltanto quando richiesto/necessario alla piattaforma concordata. Non produrre formati aggiuntivi soltanto per riempire un pacchetto.

Markdown, note interne, blueprint, estrazioni, sorgenti di lavoro, script, cache, configurazioni, inventari, log, screenshot di verifica, JSON editoriali e rapporti tecnici di controllo restano nel workspace locale, nelle categorie output/ o nei temporanei previsti. Non caricare nuovi .md in Outputs. Non caricare report amministrativi di configurazione o questo documento di regole per farli leggere al team. Se una lacuna o un limite cambia la decisione umana, riportarlo nella richiesta di approvazione o nella nota leggibile essenziale, senza inviare il registro tecnico.

Eccezione funzionale limitata: il manifest *-approval-request.json e la ricevuta *-approval-receipt.json sono necessari al flusso Microsoft attivo e restano nel percorso richiesto. Il manifest elenca solo i file realmente consegnati e ne preserva hash e revisione; non rinvia a note/sorgenti locali come se fossero accessibili nel cloud. Altri file tecnici sono ammessi solo quando un'integrazione concordata li richiede effettivamente, come il registro commerciale nella sua destinazione specifica, oppure su richiesta esplicita dell'utente. La richiesta di semplificare non interrompe approvazioni né ne elimina prove necessarie.

Prima dell'upload definire una lista esplicita dei file necessari e motivare internamente ogni aggiunta. Non caricare automaticamente un'intera cartella. Verificare il contenuto visibile, i collegamenti e il readback della consegna. Conservare localmente originali, master, revisioni, note, fonti e ricevute per ripresa e audit. Gli archivi cloud esistenti restano conservati: questa regola non autorizza cancellazioni o spostamenti retroattivi.
