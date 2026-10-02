# Marketing Inputs — elenco comune in Teams

Versione 1.1 — 2 ottobre 2026. Richiesta dell'utente: gli input devono essere un elenco Teams con file direttamente o link al file; destinazione confermata Documentation / General.

## Riferimento permanente

- Elenco Microsoft Lists: [Marketing Inputs](https://efitsys.sharepoint.com/sites/Documentation/Lists/Marketing%20Inputs/AllItems.aspx).
- Scheda Teams Marketing Inputs nel team Documentation, canale General (visualizzato Generale nell'interfaccia italiana).
- Team ID ebd6475d-5e44-45a1-8454-5ab368f8bbc7; channel ID 19:hjl1vVz8iph8zVFhUFbg40NSibTgDF3ncrCQj5iqLgY1@thread.tacv2; tab ID 9d8ec944-31b5-4d0d-b534-a153676d8b22.
- Fonte primaria di selezione per LinkedIn e newsletter: questo elenco. Marketing/Inputs resta l'archivio degli originali già presente; un file nella cartella non entra automaticamente nella coda editoriale.

## Cosa inserire

Una voce per materiale o revisione da valutare. Compilare Titolo, Link fonte oppure Allegati, Contesto, Tema e Versione fonte. Contesto comprende utilità, claim documentati, divulgabilità/diritti e limiti. Tema: B2B / Efitsys, Nova Energia, Brand e azienda, Altro. Autore e data sono tracciati dal servizio Microsoft. Lo Stato approvazione è nativo e non va sostituito con una scelta manuale Approved.

Per file già su SharePoint usare Link fonte verso l'originale, conservando versione e posizione. Gli allegati diretti sono disponibili nel modulo Nuovo elemento per materiali caricati dal team. Evitare copie aggiuntive di presentazioni/master già presenti. File grandi e versionati si referenziano con link. La voce deve contenere almeno un allegato accessibile o un link verificato; la creazione della lista non applica una convalida tecnica di questa alternativa.

L'elenco è stato creato e aggiunto al canale, con approvazioni moderne abilitate e modulo allegati verificato. Su conferma dell'utente sono stati configurati gli stessi due approvatori del ramo LinkedIn del flusso Microsoft corrente, verificato nella configurazione attiva, con regola primo a rispondere, senza sequenza e senza sovrascrittura dei predefiniti. Nomi e account restano nel servizio Microsoft. Inizialmente vuoto: nessun materiale dimostrativo o decisione umana creata dall'agente.

## Come approvare e usare

Primo popolamento completato il 02/10/2026 su richiesta dell'utente, limitato agli archivi aziendali EFS e Nova Energia: 68 voci (10 B2B / Efitsys, 57 Nova Energia, 1 Brand e azienda), selezionate fra 111 file osservati nelle cartelle pertinenti. Esclusi 43 duplicati, versioni superate o materiali personali, commercialmente riservati o non pertinenti. Non è una scansione di tutti i siti aziendali. Ogni voce ha titolo, link all'originale, contesto con limiti, tema e versione; tutte le 68 voci sono state verificate nella scheda Teams senza duplicati o differenze nei campi. Gli originali sono rimasti nella posizione esistente.

Lo stato nativo delle nuove voci è Non inviata / Not submitted; nella cache comune è unreviewed. Il popolamento non crea una richiesta né una decisione di approvazione. Foto, video e documenti senza estratto sono indicizzati da metadata e vanno consultati prima della richiesta pertinente; per i media verificare qualità, diritti, persone/targhe e audio. L'approvazione di un input identificato vale per LinkedIn e newsletter nel perimetro indicato. Il registro locale conserva il piano di selezione e la verifica; non caricare questi rapporti interni in Outputs.

Le nuove voci e revisioni si approvano direttamente nell'elenco, con Richiedi approvazione o la cella Stato approvazione. La richiesta identifica «uso come fonte per LinkedIn e newsletter», elenco/voce, versione del file e limiti. I revisori sono configurati/selezionati nel servizio Microsoft. Verificare i dettagli della decisione originale e la regola; non cambiare nomi, membri o permessi per creare una richiesta. La preparazione delle richieste pertinenti è autorizzata dal mandato di review, ma richiede destinatari configurati e materiale completo.

L'approvazione nativa della voce è il percorso corrente degli input. Non inviare in parallelo un secondo manifest in Outputs per approvare lo stesso input. Le eventuali review già pendenti nel percorso manifest storico si riconciliano nel servizio originario e si mantengono nel proprio ambito.

Solo dopo decisione autenticata e verifica della revisione esatta l'input alimenta i contenuti. Se si modifica la voce durante una richiesta, Microsoft annulla la richiesta; una modifica del file collegato va controllata separatamente tramite versione/eTag/hash, perché la voce può restare immutata. Una nuova revisione richiede nuova approvazione. Non modificare una voce approvata soltanto per annotarvi il riuso; tracciare gli utilizzi nei pacchetti finali e nel registro locale per mantenere stabile l'oggetto approvato.

`output/Linkedin/config/input-approvals.json` conserva la cache comune di revisioni, riferimenti alle decisioni e riusi, non sostituisce la fonte Microsoft. Applicare `docs/company/input-approvals.md`. Un input respinto, revocato, in attesa o non verificabile è escluso da claim/media; le attività indipendenti possono continuare con fonti già esplicitamente autorizzate nel loro ambito.

## Accesso delle ricorrenze

I connettori esposti in questa sessione lavorano sui file SharePoint e non espongono CRUD degli elenchi Lists. Lettura, configurazione e scheda Teams sono state verificate tramite interfaccia web autenticata. Le ricorrenze devono leggere l'elenco e i dettagli delle approvazioni tramite il browser disponibile; i file collegati si leggono con SharePoint quando possibile. Non inventare API, token o approvazioni e non usare endpoint nascosti tramite script nel browser. Se l'accesso all'elenco o alla decisione non è disponibile, salvare copertura parziale e stato awaiting_input_approval/access_blocked, senza considerare la cache una nuova verifica.

Il flusso Outputs → Approvazioni resta il percorso dei contenuti finali; non è un trigger della lista. LinkedIn ogni 14 giorni e newsletter mensile leggono il medesimo elenco. Daily operations riconcilia le decisioni senza un altro monitor. La prima review di un input reale e il riuso nei derivati restano da verificare: l'abilitazione delle approvazioni non è una decisione umana né un collaudo end-to-end.
