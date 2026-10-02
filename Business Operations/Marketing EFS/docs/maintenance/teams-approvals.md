# Teams Approvazioni — procedura unica Marketing EFS

Aggiornamento richiesto dall'utente il 02/10/2026. Tutte le nuove richieste di revisione marketing usano la cartella Outputs e Approvazioni native. Nessun destinatario personale, email, Entra ID o gruppo/chat di revisione è codificato nel progetto. Approvatore e regola applicabile sono gestiti nella configurazione del flusso Microsoft: verificarli nella richiesta autentica, senza dedurli da vecchie ricevute.

## Flusso esistente e destinazione

Flusso **EFS Marketing - SharePoint Outputs - Teams Approvals**, ID `bb8897f8-00c8-53f1-0473-6662fdf71cb4`, ambiente `Default-3b97374b-4a43-4588-a04f-4c94edc33cf3`. [Dettagli del flusso](https://make.powerautomate.com/environments/Default-3b97374b-4a43-4588-a04f-4c94edc33cf3/flows/bb8897f8-00c8-53f1-0473-6662fdf71cb4/details).

Attivo, salvato e collaudato il 02/10/2026 fino alla creazione dell'approvazione e alla ricevuta SharePoint. Usa la libreria Documentation, percorso `General/Marketing/Outputs/`. Per post, commenti, engagement, shortlist e segnalazioni inbox usare la sottocartella esistente [Outputs/LinkedIn](https://efitsys.sharepoint.com/sites/Documentation/Shared%20Documents/General/Marketing/Outputs/LinkedIn). Per gli altri materiali usare le categorie esistenti indicate in `docs/company/sources.md`. Le copie locali rimangono nelle relative sottocartelle di `output/`.

1. Preparare un pacchetto reale, completo e versionato localmente: testo, target, contesto, fonti, azione proposta e note interne; media e anteprime quando necessari. Per la consegna cloud applicare docs/company/output-delivery.md: solo la revisione leggibile e gli asset essenziali, senza Markdown, note interne o registri di verifica. Le informazioni necessarie alla decisione umana vanno nella richiesta o nel documento leggibile. Le lacune tecniche vanno presentate come richiesta di input, senza chiedere approvazione finale di contenuto incompleto.
2. Ispezionare la destinazione cloud, caricare i file e verificare metadata e contenuto. Nessuna cartella parallela e nessun percorso locale presentato come file accessibile su Teams.
3. Generare il manifest `*-approval-request.json` con `scripts/maintenance/prepare_approval_request.py`, titolo, revisione, categoria, azione e SHA256 di tutti i file. Caricarlo **per ultimo**, nella stessa sottocartella cloud. Il suffisso segnala il pacchetto completo; un asset singolo non crea una richiesta.
4. Il flusso legge il manifest e crea/attende un'Approvazione nativa con link e digest. Non creare gruppi Teams, non aggiungere membri, non inviare richieste alternative in chat, DM o email e non inserire menzioni personali. I riferimenti a destinatari e gruppi nelle skill facoltative precedenti sono superati da questa procedura.
5. Dopo la risposta umana, il flusso salva `*-approval-receipt.json` accanto al manifest. Verificare risposta originale Microsoft, identità autorizzata secondo la richiesta, regola, revisione, target e hash; la ricevuta locale o un hash non autenticano da soli la decisione. Controllare rifiuti, revoche e modifiche prima dell'esecuzione.
6. Registrare separatamente consegna (`prepared`, `uploaded`, `request_submitted`, `approval_created`, `unknown`), decisione e azione LinkedIn. Dichiarare `approval_created` soltanto dopo osservazione della richiesta nel servizio/flusso. Un timeout richiede riconciliazione sul servizio originale, senza reinvio cieco.

## Autorizzazioni e carico

Nuovo ambito del 02/10/2026, aggiornato dopo chiarimento dell'utente: i nuovi input comuni per LinkedIn/newsletter si approvano nella voce dell'elenco Teams Marketing Inputs, secondo docs/company/marketing-input-list.md e docs/company/input-approvals.md. Non duplicare la richiesta con un manifest Outputs; conservare/reconciliare i pacchetti pregressi nel loro percorso. Le newsletter finali mantengono manifest in Outputs/Newsletter, categoria newsletter, review_only, secondo docs/newsletter/workflow.md. Sono due decisioni distinte. Daily operations riconcilia anche queste decisioni. La ricorrenza newsletter prepara un'edizione mensile; approvazione finale non autorizza automaticamente l'invio ai destinatari.

I pacchetti di questo canale usano `requested_action=review_only` quando chiedono revisione o input. L'azione proposta (pubblicazione, risposta, reazione o follow) e l'eventuale autorizzazione precedente sono descritte esplicitamente nel materiale; non interpretare review_only come un nuovo permesso di esecuzione. Il generatore richiede `--authorization` per altre azioni supportate. Le autorizzazioni precedenti restano limitate al proprio ambito:

- Post originali: preparazione e review, poi `approved_pending_publisher`; pubblicare o programmare richiede richiesta esplicita dell'utente e integrazione verificata.
- Risposte sotto i nostri post: `approved_pending_execution`; invio pubblico richiede richiesta esplicita distinta. `live_replies_enabled=false`.
- Engagement su post esterni: l'autorizzazione ricorrente già ricevuta copre solo commenti/reazioni esatti approvati, con accesso Pagina e integrazione operativi; il live resta disabilitato fino a verifica.
- Prospect: follow delle sole aziende esattamente approvate, secondo autorizzazione già ricevuta e verifica dell'identità ElectroFit; nessun contatto commerciale, invito, unfollow o sostituzione di target.
- Inbox: segnalazioni/input nella stessa cartella; nessuna risposta commerciale automatica. Conservare la sola eccezione già autorizzata delle nuove candidature chiare indirizzate agli annunci lavoro, con i controlli del workflow.

Due schedule autonome: controlli lun–ven 11:00 Europe/Rome e preparazione/analisi ogni 14 giorni il lunedì 09:00 dal 05/10/2026. Un solo nuovo post bilingue per periodo; riprendere le review pendenti senza accumulare proposte. Non aggiungere richieste amministrative per ogni report informativo; creare revisioni soltanto per proposte complete o decisioni/input necessari. Deduplicare avvisi e richieste invariate.

## Storico e stato tecnico

Conservare bozze, baseline, checkpoint, batch, prove e ricevute originali. I nomi/ID contenuti in una ricevuta o consegna storica descrivono l'evento e non sono una configurazione destinatari. Nessuna nuova consegna usa quei riferimenti. Riconciliare le richieste pregresse nel loro servizio originale mediante i riferimenti salvati, senza duplicarle per il solo cambio canale e senza ereditare i loro approvatori per nuove richieste.

Prova preesistente verificata: approval ID `d5531920-9f76-466a-901f-472432aa1db8`, run ID `08584106617972095678573697754CU24`, ricevuta `efs-teams-approvals-test-v01-approval-receipt.json` creata il 02/10/2026 alle 12:46:29Z. Risposte native simultanee, esito aggregato `Approve, Approve`: verificare le singole risposte e la regola effettiva, non solo una stringa aggregata.

Il flusso termina con la ricevuta: non pubblica né risponde su LinkedIn. Bridge autenticato verso publisher non configurato; API in revisione; live disabilitato. Non creare firme o record di approvazione come agente, non cambiare credenziali o impostazioni live. Il servizio Operations Teams rimane distinto.
