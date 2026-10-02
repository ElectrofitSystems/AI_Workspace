# ElectroFit — misurazione, segnali e passaggio commerciale

Versione 1.1 — 2026-10-01. Stato: configurazione operativa iniziale richiesta dall'utente; registro condiviso caricato nella destinazione scelta dall'utente, definizioni di qualificazione proposte per uso interno, da validare con il team. Non approva copy, contatti, offerte o cambiamenti commerciali.

## Capacità e perimetri

| Priorità | Capacità | Skill / integrazione | Frequenza |
| --- | --- | --- | --- |
| 1 | Performance e miglioramento contenuti | efs-linkedin-performance | Report settimanale e revisione mensile attivati in questa chat |
| 2 | Richieste inbound | efs-linkedin-inbox + efs-linkedin-comments | Ricorrenze esistenti; nessun monitor duplicato |
| 3 | Segnali/opportunità dei prospect | efs-prospect-opportunities | Monitor settimanale attivato in questa chat |
| 4 | Intelligence concorrenti/fornitori/associazioni | efs-industry-intelligence | Skill disponibile; ogni due settimane proposto, lista da selezionare |
| 5 | Registro e passaggio a vendite/engineering | efs-lead-handoff | Registro SharePoint caricato/verificato; revisione settimanale proposta |
| 6 | Revisione Pagina | efs-company-page-review | Skill disponibile; trimestrale proposto |

Le ricorrenze effettive e gli ID sono in `output/Linkedin/config/automations.json`. Tutti gli orari sono Europe/Rome. Le frequenze di analisi non cambiano il ciclo editoriale 6 B2B/4 Nova Energia, né programmano pubblicazioni. Report di performance esplicitamente previsti; monitor opportunità silenzioso se invariato. Nessun nuovo invio Teams autorizzato da questa configurazione: i flussi precedenti conservano i rispettivi invii già autorizzati.

## Misure da tenere separate

| Livello | Evidenza necessaria | Conteggio / limite |
| --- | --- | --- |
| Visibilità / engagement | Analytics originali: impressioni, eventuale reach, clic, reazioni, commenti, diffusioni, follower | Non sono lead. Impressioni ≠ utenti unici. Clic LinkedIn ≠ visite al sito |
| Contesto / segnale pubblico | Annuncio datato, progetto, partnership, evento, hiring da fonte primaria | Elemento di ricerca. Non dimostra bisogno di comprare da ElectroFit |
| Richiesta ricevuta | Messaggio/commento reale e contesto verificato | Dedupe per conversazione+intento; separare commerciale, tecnico, fornitore e candidatura |
| Richiesta qualificata | Identità sufficientemente verificata + bisogno/applicazione pertinente + domanda commerciale concreta | Convenzione iniziale; dati mancanti restano espliciti. Nessun budget inventato |
| Opportunità commerciale | Progetto/bisogno concreto + accettazione di un owner umano e del prossimo passo | Non nasce da un follow, click o lancio. Non coincide con approvazione di copy |
| Vendita / closed-won | Conferma commerciale documentata | Ricavi soltanto da fonte commerciale accessibile; non dai dati LinkedIn |

I livelli non sono un funnel attribuibile automaticamente: una richiesta può provenire da un canale diverso o non avere post d'origine noto. Se mancano CRM, attribuzione o copertura sorgenti usa N.D., non zero. Il registro iniziale vuoto non dimostra assenza di inbound. Le definizioni sono operative iniziali, non criteri commerciali già ratificati dal team.

## Registro commerciale

Registro condiviso canonico: [ElectroFit-Commercial-Register.json](https://efitsys.sharepoint.com/sites/Administration/Shared%20Documents/Operations/Marketing/Commercial%20Register/ElectroFit-Commercial-Register.json), nella cartella scelta dall'utente Administration / Shared Documents / Operations / Marketing / Commercial Register. Creazione e lettura di verifica riuscite il 01/10/2026; revisione 2, nessuna richiesta ancora importata. Cartella verificata anche tramite GUID SharePoint del link utente `98ea91bc-ec76-4270-993a-acbaeb4427e3`.

Copia locale: `output/Linkedin/sales/lead-register-v01.json`; ricevuta con drive/folder/item ID, URL, eTag e hash locale in `output/Linkedin/sales/sharepoint-register-delivery-v01.json`. Prima di aggiornare leggere la versione condivisa, riconciliare lo stato locale e preservare record/eventi/ID esistenti. La copia locale non è una pipeline parallela; in caso di accesso indisponibile conserva le modifiche come pending_sync. Non includere CV, contatti privati non necessari o dettagli personali estranei.

Campi di ogni record:

- `record_id`, `revision`, `created_at`, `updated_at`, `actor_organization_id`;
- `entity_name`, `entity_website`, `entity_linkedin_url`, `entity_organization_id`, `relationship_type` (`potential_customer`, `existing_customer`, `supplier`, `partner`, `uncertain`); relazione esistente verificata con evidenza;
- `origin_type` (`inbox`, `own_post_comment`, `public_signal`, `manual`), `origin_event_id`, `origin_url`, `origin_evidence`, `source_verified_at`;
- `content_stream` (`B2B`, `Nova Energia`, `mixed`, `unknown`), `intent`, `application_or_need`, `qualification_basis`, `missing_information`;
- `stage` (`received`, `needs_clarification`, `qualified_enquiry`, `sales_opportunity`, `nurture`, `closed_won`, `closed_lost`, `excluded`), `stage_evidence`;
- `owner` (null finché assegnato), `owner_acceptance_evidence`, `next_action`, `next_action_status` (`proposed`, `accepted`, `done`, `blocked`), `follow_up_date`, `follow_up_date_status` (`proposed_internal`, `confirmed_internal`, `customer_confirmed`, `unknown`);
- `content_approval_evidence`, `execution_authorization_evidence`, `handoff_status` e `history_event_ids`, separati dall'accettazione commerciale.

Clienti potenziali e fornitori hanno viste e conteggi distinti; un soggetto con intenti misti conserva record/collegamenti distinti, evitando duplicati per progetto. Le candidature restano al flusso inbox, fuori dai conteggi lead. Non assegnare owner o scadenze clienti per inferenza. I segnali non diventano automaticamente record lead.

Ogni transizione aggiunge un evento idempotente a `events`, con record/revisione, vecchio/nuovo stato, motivo, fonte e autore. Rileggere il registro prima di una scrittura, non sovrascrivere revisioni altrui; scrivere atomicamente e verificare il risultato. Nessun ripristino distruttivo o pulizia di altri registri.

L'atomicità della copia locale non implica atomicità cloud. L'azione SharePoint exact-update esposta sostituisce l'intero file e non espone if-match; preferire una scrittura condizionale se disponibile. Prima di scrivere rileggere contenuto/eTag e riconciliare cambiamenti; se persiste un conflitto o un esito incerto, conservare la delta pendente. Dopo scrittura verificare contenuto, revisione e target prima di registrare l'aggiornamento condiviso come concluso.

## Passaggi fra i flussi

Inbox: preservare customer-first, formato e consegna mediante pacchetto Outputs/LinkedIn e Approvazioni native, frequenze e autorizzazione limitata per risposte candidature. Quando emerge una richiesta commerciale reale, aggiornare il registro condiviso secondo efs-lead-handoff e preparare l'handoff locale, senza secondo digest Teams. In caso di blocco conservare la modifica locale pending_sync. Un aggiornamento del registro non implica risposta al cliente.

Commenti nostri post: preservare contesto/thread, canale nativo Approvazioni da Outputs/LinkedIn, approvazione della revisione esatta e richiesta distinta di invio pubblico. Una domanda tecnica generica è engagement finché la conversazione non sostiene un intento commerciale. Non mescolare con commenti su post di altre aziende.

Prospecting: ricerca nuove aziende e follow rimangono nel flusso esistente. Monitor opportunità: riesame della shortlist e segnali datati, senza follow o outreach. Le nuove shortlist non devono essere riscritte dalla watchlist storica. Rapporti esistenti e disponibilità fornitori sono incognite fino a verifica.

## Report e proposte editoriali

Ogni numero conserva fonte, unità, base/periodo e data. Un post è classificato dal testo effettivo e ID pubblicato; una bozza non prova pubblicazione. Snapshot dei post e KPI giornalieri aggregati hanno semantiche diverse: non unirli se non verificati. Nel primo rilevamento del 01/10/2026 le finestre overview e tabella post differivano.

CTR ponderato = totale clic / totale impressioni × 100 per dati omogenei/completi; N.D. se denominatore zero o metrica mancante. Non mediare tassi semplici. Conservare il tasso engagement e la definizione LinkedIn, specificando formula/denominatore per metriche interne. Nuovi follower non misurano il saldo netto; l'attribuzione B2B/NE resta ignota senza fonte.

Proposte per il prossimo ciclo: osservazione → ipotesi → modifica concreta → misura → riesame. Campione iniziale di due post pubblicati il 30/09, osservati il 01/10, non determina un vincitore né causalità. Nessun target o quota nuova imposti sulla base della sola baseline. Le proposte passano alle skill editoriali e al flusso già approvato.

## Accesso e autorizzazioni

Accesso browser admin Contenuto/Follower verificato il 01/10/2026. People search e publisher non offrono analytics, inbox o ricerca/follow aziendali. Ogni esecuzione ricontrolla accesso e identità; sessione browser precedente non garantisce quella futura. Nessuna API/configurazione analytics creata con questa attività.

Ricerca, report, bozze e stato locale sono autorizzati. Richieste Teams dei flussi precedenti restano autorizzate nei loro ambiti. Nuovi report non vengono inviati automaticamente in quei gruppi. Pubblicazione, risposte commerciali/outreach e modifiche Pagina richiedono richiesta esplicita e approvazioni pertinenti; non ripetere autorizzazioni già valide nello stesso ambito. Non cambiare live publisher, permessi, impostazioni Page o CRM.

Il 01/10/2026 l'utente ha autorizzato il caricamento e indicato la destinazione del registro condiviso sopra. La gestione del registro in questa cartella è un'eccezione specifica al precedente vincolo SharePoint di sola lettura: non autorizza altri caricamenti, riorganizzazione delle fonti, modifiche di permessi, nuovi messaggi Teams o contatti commerciali. Nessuna nuova ricorrenza attivata con la sola scelta della destinazione.

Fonti di funzionamento verificate il 01/10/2026: [LinkedIn Page analytics](https://www.linkedin.com/help/linkedin/answer/a547077) e [LinkedIn Page messaging](https://business.linkedin.com/advertise/linkedin-pages/messaging-on-linkedin-pages). Descrivono capacità del prodotto, non i permessi dell'account. Fonti aziendali: contesto condiviso, framework/v12 e registri dei flussi esistenti.
