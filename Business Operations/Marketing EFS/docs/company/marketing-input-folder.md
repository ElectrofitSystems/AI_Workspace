# Marketing Inputs - collegamenti e approvazioni

Correzione esplicita dell'utente del 5 ottobre 2026: in SharePoint Marketing/Inputs usare collegamenti nativi ai documenti originali, equivalenti al comando Nuovo > Collegamento in Teams/SharePoint. Le copie create nella prima esecuzione erano errate e vengono sostituite. Questa regola prevale sui riferimenti storici a copie e sulla lista come fonte primaria, anche nelle skill e ricorrenze.

## Cartelle e perimetro

Cartella: https://efitsys.sharepoint.com/sites/Documentation/Shared%20Documents/General/Marketing/Inputs

La selezione resta limitata ai 68 materiali del piano del 2 ottobre: 25 collegamenti in Technical Documentation, 36 in Media/Pictures, 6 in Media/Videos e il kit 3.4 EN già presente in Brand Identity. Il kit è un originale preesistente, da conservare senza duplicarlo o creare un collegamento a se stesso. Anche prova.c.url preesistente è escluso dalla correzione e resta intatto. Non importare automaticamente altri materiali.

I 67 collegamenti hanno nome originale con suffisso .url. Il formato nativo è InternetShortcut con URL dell'originale; il primo è stato creato con il comando SharePoint e letto come campione, gli altri mediante il connettore nello stesso formato. Contenuto e QuickXorHash cloud verificati per tutti i link; apertura di un collegamento verificata verso l'archivio originale. Non copiare i documenti e non usare link alle copie generate per errore.

Gli originali rimangono nei rispettivi archivi, con contenuto, ID e permessi conservati. La rimozione riguarda soltanto le 67 copie identificate in output/Linkedin/input-approvals/inputs-folder-migration-20261005-v02.json, dopo verifica di ID, nome, dimensione e hash e creazione del collegamento corretto. Usare il cestino recuperabile, senza cancellazione definitiva o svuotamento. Non rimuovere altri file, lista, scheda Teams o storico.

## Review del collegamento e dell'originale

Approvazioni moderne abilitate nella libreria Documenti di Documentation; nessun approvatore predefinito impostato per l'intera libreria. Funzionalità opzionale, nessuna modifica ai permessi o approvazione obbligatoria degli altri documenti.

Per review manuali selezionare il collegamento .url e usare Richiedi approvazione oppure la cella Non inviata nella colonna Stato approvazione. Scegliere soltanto revisori autorizzati e verificati in Microsoft o indicati dall'utente. Nessun reinvio massivo dei materiali già presenti o destinatario dedotto da ricevute storiche. Per le nuove aggiunte vale il flusso automatico autorizzato qui sotto.

Nei dettagli indicare URL, nome, drive/item ID, revisione/versione/eTag/hash del documento originale, ambito uso come fonte per LinkedIn e newsletter e limiti di riuso. La richiesta riguarda un riferimento preciso e il suo contenuto alla revisione indicata. Il collegamento è di pochi byte: approvarne soltanto lo stato NON approva successive modifiche dell'originale. Verificare sempre il target prima della richiesta e prima del riuso, anche quando la revisione .url non cambia. Una modifica al target o al link richiede riconciliazione e nuova review del contenuto modificato.

Per leggere i materiali, recuperare l'URL o gli ID dell'originale; fetch del .url può restituire soltanto il testo InternetShortcut. Non usare questa risposta come lettura del documento. Un link non concede nuovi permessi: dichiarare access_blocked se revisore o agente non può leggere il target; non creare link anonimi o ampliare accessi.

## Decisioni e registro

La decisione Microsoft autentica sulla revisione e nell'ambito preciso è autoritativa; la cache non autentica approvazioni. Conservare la lista e le decisioni pregresse come storico. Riconciliare review già avviate nel servizio originario, senza duplicarle; non segnare Approved manualmente. Un nuovo collegamento non eredita automaticamente uno stato Lists o del documento originale.

LinkedIn e newsletter selezionano i riferimenti in Inputs. Nuovi input o revisioni pending/rejected/revoked/unknown restano esclusi da claim/media; autorizzazioni esplicite pregresse conservano il proprio ambito. Approvazione input e approvazione del derivato restano distinte. Outputs mantiene il flusso dei derivati; nessun manifest input aggiuntivo in Outputs.

Cache comune: output/Linkedin/config/input-approvals.json. Conservare source_url/drive_id/item_id e tutti i campi delle decisioni pregresse; marketing_input_shortcut identifica il riferimento, preferred_input_url apre l'originale e input_review_url identifica il collegamento in Inputs. I riferimenti marketing_input_copy vengono conservati come storico della correzione e marcati rimossi, senza usarli per letture o review. Usare lock esclusivo e merge atomico senza sovrascrivere aggiornamenti concorrenti della Newsletter.

Registro corrente: output/Linkedin/input-approvals/inputs-folder-shortcuts-correction-20261005-v01.json. Il registro delle copie precedenti resta prova storica dell'errore; non è la selezione corrente. Registri, ricevute e verifiche restano locali. Il PDF di consultazione già consegnato viene corretto per aprire gli originali.

## Richiesta automatica sui nuovi input — 5 ottobre 2026

L'utente ha richiesto che ogni nuova aggiunta in Inputs avvii automaticamente la richiesta di approvazione. Flusso cloud dedicato **EFS Marketing - Inputs - Automatic Approvals**, ID `d566e7c1-4941-77a4-abcc-752887b781dc`, salvato e attivo nell'ambiente EFitsys. Configurazione e stato del collaudo in `output/Linkedin/config/input-approval-automation.json`. Il flusso è indipendente dal PC e da Codex.

Trigger SharePoint **When a file is created (properties only)** sulla libreria Documents di Documentation, filtrato al prefisso `Shared Documents/General/Marketing/Inputs/`, incluse le sottocartelle; cartelle escluse. La soglia Created dal 05/10/2026 09:30:55 UTC evita l'invio retroattivo dei materiali già presenti. L'azione nativa SharePoint **Create an approval request for an item or file** crea la richiesta sullo stesso elemento e il servizio Microsoft ne gestisce lo stato. Approvers e regola risiedono soltanto nel flusso Microsoft, riusati dalla configurazione Marketing LinkedIn verificata nell'editor; non dalle ricevute storiche. Nessun approvatore predefinito per l'intera libreria.

La richiesta automatica è una review di ingresso: include elemento, percorso, revisione del riferimento e data di creazione, ambito LinkedIn/newsletter e richiesta esplicita al revisore di verificare l'originale e registrare versione/data e limiti di riuso nella risposta. Per un .url lo stato Approved da solo non prova la revisione dell'originale: prima del riuso l'agente deve riconciliare la risposta autentica e identificare/verificare il target esatto. Revisioni mancanti o accessi bloccati rimangono unknown/access_blocked. Non pubblicare né approvare come agente. Il flusso avvia la richiesta; non autentica il contenuto del target al posto del revisore.

Il trigger è di sola creazione: non avvia nuove richieste per modifiche dell'originale, né assicura di intercettare un file già esistente spostato nella cartella. Questi casi richiedono riconciliazione e una nuova review della revisione interessata. Non reinviare ciecamente una run fallita: verificare prima la richiesta nel servizio originale. Il retry dell'azione di creazione è disabilitato per limitare richieste duplicate dopo esiti ambigui. La latenza dipende da SharePoint/Power Automate; non promettere risposte in pochi secondi senza prova.

Questa nuova autorizzazione riguarda il flusso cloud Inputs; non crea nuove schedule Codex e non modifica il flusso Outputs dei derivati.

Collaudo verificato: un solo collegamento esplicitamente denominato `Test-approvazione-automatica-NON-USARE.url` caricato in Technical Documentation alle 09:34:29 UTC; run `08584104139849401329964467508CU23` riuscita, HTTP 200, approval ID `be8b80d8-2f4e-4a62-8a14-92e3e55cc286` restituito alle 09:35:12 UTC. Tempo dalla creazione del file: 43 secondi, senza garanzia SLA. Titolo, destinatari Microsoft, awaitAll=false e versione 1.0 verificati nei risultati della run; stato Requested osservato nella libreria. Nessuna decisione approvata dall'agente. Il test non è una fonte editoriale.

## Ricorrenze

Aggiornare soltanto il riferimento agli input nelle tre ricorrenze esistenti, preservando ID, cadenze, destinazioni, stato, modelli, notifiche e gli aggiornamenti di altre chat. Nessun nuovo monitor o calendario. Per la Newsletter conservare l'attuale canale LinkedIn definito in docs/newsletter/workflow.md.

## Riferimento Microsoft

[Nuovo collegamento nella raccolta documenti](https://support.microsoft.com/en-us/sharepoint/documents-and-library/add-a-link-in-a-document-library): il comando crea un file .url. La presenza in Inputs, la copia o il collegamento non costituiscono approvazione.

## Esito verificato

Correzione completata il 5 ottobre: 67 collegamenti verificati e 67 copie generate rimosse; nessuna copia residua nelle tre categorie tecniche/media. Kit e prova.c.url preesistenti conservati. Registro aggiornato con lock/merge, preservando le due decisioni approvate e i 66 stati unreviewed. Tre ricorrenze aggiornate senza alterare altri campi o gli aggiornamenti della Newsletter. PDF corrente corretto agli originali, 68 link verificati e hash cloud uguale al locale; revisione precedente locale conservata. Prove in output/Linkedin/input-approvals/inputs-workflow-shortcuts-update-20261005-v01.json e inputs-links-pdf-delivery-20261005-v02.json.
