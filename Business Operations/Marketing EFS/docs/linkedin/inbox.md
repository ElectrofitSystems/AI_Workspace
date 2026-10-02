# ElectroFit LinkedIn Inbox — triage e risposte candidature

Versione 04 — 1 ottobre 2026. Stato: skill/configurazione installate e automazione esistente aggiornata; nessun nuovo invio LinkedIn o Teams durante questa modifica.

Obiettivo: distinguere le richieste entranti e rendere le notifiche più utili al team. Destinatari delle notifiche: Francesco Lucherini e Mohammad Taffal nella chat Teams LinkedIn Messages già verificata. Controlli invariati: lunedì–venerdì, 09:30 e 17:00 Europe/Rome.

## Comportamento configurato

| Contenuto | Azione |
| --- | --- |
| Richiesta cliente o potenziale cliente: preventivo, fattibilità, integrazione, supporto, consegna | Priorità alta; notifica prima delle attività di ricerca sui fornitori. Nessuna risposta commerciale automatica. |
| Offerta di componenti o servizi da potenziale fornitore | Verifica della pagina aziendale LinkedIn; prima valutazione di pertinenza rispetto a sottosistemi/applicazioni EFS, fonti e lacune tecniche. Nessuna approvazione acquisti o compatibilità garantita. |
| Richiesta chiara di lavorare presso ElectroFit | Risposta di cortesia come Page con link agli annunci, una volta per thread, per nuove richieste successive all'attivazione della policy. |
| Recruiting venduto come servizio, lavoro offerto a un nostro dipendente, messaggi misti o ambigui | Nessuna risposta automatica candidatura; classificazione e notifica fattuale. |

Le informazioni aggiunte restano dentro «Contenuto del Messaggio». Titolo e tre etichette del formato v02 sono conservati. Il testo ricevuto e la valutazione dell'assistente sono distinti. Code di scansione, review, risposte Page e consegna Teams sono separate; invii incerti restano da riconciliare, senza ritentativi alla cieca. Storico, baseline e digest già consegnati non vengono ripetuti.

## Risposte candidature autorizzate

Autorizzazione: richiesta esplicita dell'utente del 1 ottobre 2026 di rispondere alle richieste di lavoro indirizzando agli annunci LinkedIn. Eccezione limitata al precedente divieto di risposta. Nessuna promessa di assunzione, raccolta CV o valutazione del candidato.

Italiano:

> Grazie per il tuo interesse per ElectroFit Systems. Per eventuali posizioni disponibili, ti invitiamo a consultare gli annunci di lavoro sulla nostra pagina LinkedIn: https://www.linkedin.com/company/efitsys/jobs/

Inglese:

> Thank you for your interest in ElectroFit Systems. Please check the job posts on our LinkedIn page for any available positions: https://www.linkedin.com/company/efitsys/jobs/

Il link è stato osservato nella scheda Lavoro della pagina pubblica ElectroFit Systems S.r.l., con identità aziendale 103544667. Durante la verifica del 1 ottobre la pagina mostrava «Al momento non ci sono offerte di lavoro». Questa è un'osservazione datata; la skill ricontrolla il link prima degli invii senza assumere che lo stato delle offerte resti invariato. Nessuna risposta retroattiva alle candidature dello storico. La data/ora di attivazione è in config.json.

## Fonti e risorse

- Skill installata: `C:\Users\Operations\.codex\skills\efs-linkedin-inbox\SKILL.md`.
- Dettaglio decisionale: `references/triage-and-replies.md`; registri operativi: `references/operations.md`.
- Contesto applicativo: `.agents/product-marketing.md`, tre sottosistemi e tutti gli otto settori obiettivo documentati dalla v12; regole evidenze in `docs/linkedin/editorial.md`.
- Configurazione e attivazione: `output/Linkedin/inbox/config.json`; registri persistenti: state.json, reviews/, replies/, digests/.
- Automazione aggiornata: `electrofit-messaggi-linkedin-e-notifiche-teams`, ACTIVE, stessa ricorrenza e stessa chat Codex.

## Verifica e limiti

Revisione dei casi: richiesta tecnica/quote → alta; offerta componenti → review; candidatura chiara nuova → link annunci; proposta recruiting → fornitore/altro; cliente+candidatura misti → alta senza risposta automatica; vecchia candidatura baseline → nessuna risposta; esito invio unknown → riconciliazione senza duplicazione.

Validazione della skill e controlli di consistenza su configurazione, prompt dell'automazione, conservazione dello storico e ricorrenza sono registrati nel completamento locale. L'invio effettivo della nuova risposta Page non è stato collaudato su una candidatura reale durante questa modifica. La prima esecuzione eleggibile deve verificare il messaggio uscente come ElectroFit prima di segnare sent. Nessun potenziale fornitore è stato valutato in questa attività di configurazione.

Punti da verificare per ogni offerta: identità del fornitore, capacità dichiarate, interfacce e requisiti effettivi dell'applicazione, documentazione e qualifica tecnica. LinkedIn fornisce una prima ricognizione, non la qualifica del fornitore.

Verifica completata: quick_validate superato; storico preesistente identico; automazione ACTIVE e prompt aggiornato; due esecuzioni per giorno feriale anche attraverso il cambio ora legale/solare di ottobre.


# Notifica Teams — formato v02

Aggiornamento richiesto dall'utente il 1 ottobre 2026, dopo la ricezione della prima notifica. Applicato alla skill e al prompt dell'automazione per i nuovi digest. Destinatari: Francesco Lucherini e Mohammad Taffal. Orari: 09:30 e 17:00, lunedì–venerdì, Europe/Rome.

Modello visibile:

**Electrofit - Nuovi Messaggi.**

**Mittente:** [nome]

**Contenuto del Messaggio:**
[testo ricevuto, se breve; sintesi fedele se lungo o con dettagli personali non necessari]

**Link of conversation:**
[link verificato]

Note interne: titolo e tre etichette nell'ordine richiesto; corretto il refuso Messagi in Messaggi. Paragrafi HTML semplici per conservare spaziatura su Teams e link cliccabile. Date, argomento e ID tecnici restano nel registro locale. Nessuna nuova notifica del messaggio già consegnato a entrambi. Digest precedenti conservati immutabili; riconciliazione di nuovi invii incerti tramite corpo, mittente, destinazione e finestra del tentativo.

Fonte dell'esempio ricevuto: prima conversazione monitorata con Matteo Ravera, 1 ottobre 2026 alle 09:30. L'utente ha confermato la ricezione su Teams. Il nuovo formato verrà verificato nella consegna del prossimo nuovo messaggio effettivo.


# ElectroFit — destinazione notifiche Teams v03

1 ottobre 2026. Richiesta dell'utente: notificare il gruppo esistente LinkedIn Messages, che include Francesco e Mohammad.

Obiettivo e destinatari: una sola notifica per digest nel gruppo Teams LinkedIn Messages. Membri verificati: Operations, Francesco Lucherini e Mohammad Taffal, con email efitsys.com. Chat ID: `19:6f4f3e1a2c9c4ec3b39ac69e4aa40d4d@thread.v2`. Identità del gruppo verificata con resolve_chat, membri con get_chat_members e account mittente con get_profile il 1 ottobre 2026.

Decisione: sostituisce le due chat individuali per i nuovi messaggi. Formato v02 con titolo, Mittente, Contenuto del Messaggio e Link of conversation; controlli lunedì–venerdì alle 09:30 e 17:00 Europe/Rome.

Consegna: ogni parte del digest viene inviata una volta nel gruppo; una consegna confermata nel gruppo soddisfa la notifica a entrambi. Registro con ID messaggio, chat, corpo esatto e orario. Invii incerti da riconciliare prima di ritentare. Nessun invio aggiuntivo nelle chat individuali.

Stato al cambio: nessun digest pendente. Storico delle due notifiche già consegnate conservato immutabile; nessun reinvio automatico nel gruppo. Nessun messaggio di test inviato durante questo aggiornamento. Skill, configurazione e prompt dell'automazione aggiornati per la destinazione verificata.

Punti aperti: la prima consegna effettiva nel gruppo sarà verificata al prossimo nuovo messaggio o a un reinvio esplicitamente richiesto. Se identità/accesso o membri del gruppo cambiano, il workflow conserva il lavoro pendente e segnala il problema.

Verifica successiva: su richiesta esplicita dell'utente, notifica di Matteo Ravera reinviata per test nel gruppo LinkedIn Messages il 1 ottobre 2026 alle 10:09 Europe/Rome. Consegna confermata dal connettore Teams, message ID 1790842189182. Il contenuto restituito conserva titolo/etichette in grassetto, paragrafi e link alla conversazione. Nessuna copia inviata in DM.
