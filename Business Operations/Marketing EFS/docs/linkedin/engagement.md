# Electrofit — LinkedIn engagement ricorrente

1 ottobre 2026 — versione 1.

Richiesta: ricercare post e interagire come pagina Electrofit ogni giorno alle 10:00, 14:00 e 17:00, Europe/Rome, weekend inclusi. Ricorrenza gestita tramite heartbeat di questa chat; configurazione operativa in `output/linkedin/engagement/config.json`.

La richiesta costituisce autorizzazione ricorrente di esecuzione nel perimetro concordato. Non serve una seconda richiesta di esecuzione per ciascuna interazione già esattamente approvata e tecnicamente eseguibile. L'utente ha scelto esplicitamente «Revisione di commenti e reazioni (consigliata per iniziare)». È quindi confermata la revisione di commenti e reazioni da parte di Francesco oppure Mohammad, senza necessità di entrambi.

Raccomandazione formulata: automatizzare ricerca e preparazione; mantenere la revisione dei commenti, valutando separatamente eventuali reazioni automatiche limitate a contenuti pertinenti e verificati. Nessuna quota di engagement o nuova geografia imposta.

Finché API, azione come pagina su post di terzi e integrazione delle approvazioni non sono verificati, i passaggi producono ricerca e bozze. L'istruzione successiva dell'utente autorizza gli invii delle richieste di approvazione al gruppo Teams LinkedIn Engagement, verificato con Francesco, Mohammad e Operations; configurazione v3 e nota destinazione v02 contengono ID e prove. Gli upload SharePoint restano esclusi. Nessuna modifica al publisher o alle altre automazioni.

Le esecuzioni preservano uno storico unico, deduplicano target e azioni, riconciliano esiti incerti e notificano solo novità utili o nuovi problemi. Nessuna attività viene considerata completata sulla sola base di una bozza o della ricorrenza.

Automazione creata tramite strumento dell'app, stato ACTIVE, ID `electrofit-linkedin-engagement-giornaliero`, collegata a questa chat. Unica ricorrenza giornaliera con i tre orari richiesti, senza data di avvio ancorata: lo strumento applica l'orario locale del dispositivo, verificato come W. Europe Standard Time (Roma). La scheda è stata richiamata con automation_update view. Nessuna interazione LinkedIn eseguita durante la configurazione.

La documentazione ufficiale delle [automazioni](https://learn.chatgpt.com/docs/automations?surface=app) è stata consultata. Verificare disponibilità del computer, dell'app e degli accessi per l'esecuzione locale; la pianificazione non realizza da sola l'integrazione LinkedIn.


# LinkedIn Engagement — destinazione delle approvazioni

1 ottobre 2026 — versione 2 del flusso di consegna.

L'utente ha autorizzato in questa chat l'invio delle richieste di approvazione nel gruppo Teams **LinkedIn Engagement**, che include Mohammad e Francesco. Destinazione specifica per engagement: sostituisce il precedente riferimento a LinkedIn Post Approval soltanto in questa skill. Un'approvazione verificata di uno dei due resta sufficiente per la revisione esatta.

Account connettore verificato: Operations, operations@efitsys.com, ID `74ea6b2b-69f5-48dd-95bd-5edb7a4aad38`. La ricerca del target, la risoluzione per topic/partecipanti e l'elenco delle chat accessibili non hanno trovato il gruppo richiesto. Risultano accessibili LinkedIn Messages, LinkedIn Post Approval e Noi & Operations: nessuno è stato usato come sostituto.

Alla richiesta successiva «try now», il gruppo è risultato accessibile. Topic esatto LinkedIn Engagement, tipo group, ID `19:c4dbd9af1e9e4dc29330f3a56be992bc@thread.v2`. Membri verificati tramite get_chat_members: Francesco Lucherini (francesco.lucherini@efitsys.com), Operations (operations@efitsys.com), Mohammad Taffal (mohammad.taffal@efitsys.com). Lettura dei messaggi verificata; il contenuto «..» non è un'approvazione. Link canonico ottenuto da list_chats, conservato nella configurazione v3. Verifica completata il 1 ottobre 2026 alle 12:09 ora di Roma. Non è stato creato un gruppo e non sono stati modificati membri.

Configurazione, skill e heartbeat esistente aggiornati per invii autorizzati al gruppo esatto, lettura delle approvazioni nei passaggi giornalieri, legame con batch/revisione/target/copy e deduplicazione delle consegne. La destinazione è ora verificata; le nuove proposte complete possono essere inviate nel gruppo con l'autorizzazione ricevuta. Nessun pacchetto di interazione era presente al momento della modifica: non è stata inviata una richiesta vuota o un messaggio di test.

Orari conservati: tutti i giorni 10:00, 14:00 e 17:00 Europe/Rome. Live LinkedIn invariato e disabilitato fino a integrazione verificata. Gli invii Teams autorizzati non equivalgono all'abilitazione del publisher.


## Priorità geografica — 2 ottobre 2026

Preferenza confermata dall’utente: cercare principalmente post di potenziali aziende pertinenti in Europa, inclusi Regno Unito, Svizzera e Norvegia. Avviare la ricerca da OEM, integratori, fornitori e partner tecnici con sede europea o entità/attività europee verificate e pertinenti al post. Annotare paese o presenza europea e fonte, senza dedurli dalla lingua del post o dalla sede di un evento. Questa preferenza sostituisce l’assenza di priorità geografica indicata nella configurazione iniziale.

La selezione resta basata su contenuto verificabile e contributo utile. Post extraeuropei possono essere proposti quando particolarmente pertinenti, con motivazione esplicita; nessuna quota per paese e nessun vincolo alla sola UE. La modifica riguarda le ricerche future; non riscrive pacchetti o approvazioni esistenti.
