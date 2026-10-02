# Electrofit Systems — gestione commenti LinkedIn

Versione 1.1 — 2026-10-01. Destinazione di revisione aggiornata su richiesta dell'utente.

Skill locale: `C:/Users/Operations/.codex/skills/efs-linkedin-comments/SKILL.md`. Riutilizza `docs/company/context.md` e le fonti aziendali del workspace.

## Perimetro e fonti

Risposte sotto post pubblicati dalla Pagina Electrofit Systems. Un post Electrofit su Nova Energia rientra nel perimetro; un'altra Pagina autrice richiede identità e ambito verificati separatamente. Engagement sui post di altre aziende e inbox privata restano flussi distinti.

Analizzare la domanda prima di preparare la risposta. Per il retrofit consultare prima **nova-energia.it**, in particolare la FAQ, leggendo la risposta completa e le condizioni. Per le domande B2B consultare **efitsys.com** e i documenti originali **SharePoint** pertinenti nel perimetro del registro fonti. Per richieste miste usare entrambi, senza estendere le risposte Panda ad altri veicoli. Registrare link, versione/data, sezione e condizioni; se manca una risposta o le fonti discordano, chiedere input tecnico a Francesco/Mohammad senza inventare il claim.

## Applicazione

Acquisire il post pubblicato e il thread pertinente; verificare risposte della Pagina già presenti; scegliere se rispondere, chiarire, raccogliere dati o lasciare senza risposta. Preparare e revisionare in italiano, poi adattare nella lingua del commentatore.

Salvare copie versionate e note interne in `output/linkedin/comments/`. Usare `docs/linkedin/templates/linkedin-comment-review.md` quando utile. Un ringraziamento breve non richiede l'intero processo dei post.

L'utente ha autorizzato l'invio delle richieste di approvazione delle risposte a **LinkedIn Engagement**, ID `19:c4dbd9af1e9e4dc29330f3a56be992bc@thread.v2`, con commento originale, contesto, link e risposta esatta. Destinazione e membri Francesco, Mohammad e Operations verificati con il connettore Teams il 01/10/2026. Inviare nuovi pacchetti completi in questo ambito senza richiedere nuovamente il permesso; nessun invio di test o vuoto. Questa scelta sostituisce LinkedIn Post Approval per i commenti, mentre i post originali conservano il proprio flusso. Una approvazione autenticata di Francesco Lucherini o Mohammad Taffal basta per la revisione esatta. L'approvazione del post non approva le risposte; l'invio pubblico richiede una richiesta esplicita distinta, senza ripetere autorizzazioni già valide nello stesso ambito. La condivisione del gruppo con l'engagement non trasferisce le autorizzazioni di esecuzione fra i due flussi.

Prima dell'invio verificare conversazione aggiornata, risposte di altri amministratori, revisione e autorizzazione. Registrare intento, risultato e verifica; riconciliare esiti incerti prima di riprovare. Moderazione e messaggi privati richiedono un ambito distinto.

## Monitor programmato — aggiornamento 2026-10-01

Su richiesta esplicita dell'utente è attiva l'automazione locale **ElectroFit — commenti sui nostri post LinkedIn**, ID `electrofit-commenti-sui-nostri-post-linkedin`, collegata alla chat `01a0f7b6-54f3-7681-969b-70114ff4266c`.

Controlli **lunedì–venerdì alle 10:30 e 16:30 Europe/Rome**, con primo controllo previsto il 1 ottobre 2026 alle 16:30. Gli orari sono sfalsati rispetto a inbox ed engagement. Recuperare i nuovi commenti del weekend al controllo del lunedì e quelli arrivati durante interruzioni; registrare la copertura effettiva senza dichiarare complete scansioni parziali.

Configurazione: `output/linkedin/comments/monitor-config.json`. Individuare i post realmente pubblicati da Electrofit negli ultimi 90 giorni, aggiungendo post indicati dall'utente e thread più vecchi già pendenti. Acquisire una baseline dei commenti precedenti all'attivazione senza richieste di revisione retroattive automatiche; raccogliere i nuovi dall'attivazione. Conservare checkpoint, revisioni, prove e deduplicazione con lock esclusivo.

La ricorrenza prepara risposte e richieste di revisione/input tecnico nel gruppo **LinkedIn Engagement** e controlla le decisioni. L'approvazione verificata della revisione esatta porta a `approved_pending_execution`: questa richiesta di programmazione non autorizza risposte pubbliche, reazioni, moderazione o messaggi privati. Il live resta disabilitato. Notificare soltanto nuove proposte utili, cambiamenti materiali e nuovi problemi che richiedono intervento; evitare avvisi invariati.

Automazione creata e attiva; lettura effettiva dei commenti da verificare alla prima esecuzione. Nessuna scansione LinkedIn o richiesta Teams è stata eseguita durante la configurazione. I controlli richiedono computer acceso, Codex in esecuzione e accessi necessari disponibili.

## Notifiche obbligatorie per le risposte preparate — aggiornamento 2026-10-01

L’utente ha richiesto esplicitamente in questa chat che ogni risposta preparata venga notificata a Mohammad e Francesco per approvazione. Consegnare ogni proposta completa nel gruppo **LinkedIn Engagement**, menzionando entrambi dopo verifica dei membri e dell’account Operations. Se mancano fatti indispensabili, chiedere input tecnico anziché approvazione finale. Non lasciare una risposta completa soltanto in un file locale; se Teams è indisponibile conservare la consegna pendente e segnalare il nuovo blocco.

La regola include le bozze per commenti storici già individuati: la data precedente all’attivazione non blocca la consegna di una risposta preparata. Sostituisce il precedente hold di recupero per tali bozze, conservandone lo storico. Non impone risposte o notifiche per ogni commento storico e non ripete pacchetti già consegnati. Cadenza invariata: lunedì–venerdì, 10:30 e 16:30 Europe/Rome. Una approvazione autenticata di Francesco oppure Mohammad resta sufficiente per il contenuto esatto; nessuna nuova autorizzazione all’invio pubblico LinkedIn.

Prima proposta recuperata: **EFS-COM-20261001-001 r01**, domanda di Benedetto Moro su Lancia Ypsilon. Testo r01 e fingerprint conservati; contesto riletto prima della consegna. Ricevuta e registri in `output/linkedin/comments/deliveries/`.

## Formato delle notifiche — aggiornamento 2026-10-01

Il corpo della notifica contiene soltanto quattro campi, con etichette esatte nell’ordine richiesto dall’utente:

1. **LinkedIn Post:** link cliccabile al post verificato, eventualmente con il titolo come testo del link.
2. **Commentator name:** nome del commentatore.
3. **Comment body:** testo originale del commento.
4. **Suggested Reply:** risposta pubblica esatta proposta nella lingua del commentatore.

Usare paragrafi distinti ed etichette in grassetto tramite HTML Teams. Conservare le menzioni di Mohammad e Francesco tramite il connettore; nessun titolo, introduzione o campo aggiuntivo. Fonti, contesto interno, ID/revisione, fingerprint e prove di approvazione restano nei registri locali collegati al messaggio Teams. Modello: `docs/linkedin/templates/linkedin-comment-notification.txt`. Questo formato prevale sulla precedente presentazione estesa; non cambia la revisione del testo pubblico o le autorizzazioni. Non rinviare automaticamente notifiche già consegnate per il solo cambio formato; il reinvio della proposta sulla Ypsilon applica la richiesta esplicita riferita alla notifica corrente e conserva lo storico.

## Stato iniziale alla creazione della skill (storico)

Skill locale creata. Nessun monitor o nuova ricorrenza attivati, nessuna richiesta Teams o risposta pubblica inviata con questa attività. Non è stata costruita un'integrazione commenti.

Alla creazione, i tool esposti del publisher non includono lettura commenti o risposte. Il live richiede integrazione commenti e gestione autenticata delle approvazioni verificate, secondo la regola del progetto. In loro assenza consegnare proposta locale o passaggio manuale con stato corretto. I controlli dettagliati restano nella skill.
