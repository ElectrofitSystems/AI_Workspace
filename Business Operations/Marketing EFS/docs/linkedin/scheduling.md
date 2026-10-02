# LinkedIn — controlli quotidiani e contenuti quindicinali

Aggiornamento dell'utente del 02/10/2026: startup di sei persone, poco tempo disponibile. La correzione successiva mantiene la riduzione dei contenuti e dell'analisi ogni due settimane e ripristina i controlli operativi alla cadenza precedente.

**Due schedule autonome attive:** LinkedIn daily operations, lunedì–venerdì 11:00 Europe/Rome, per inbox, commenti, approvazioni e il modulo engagement esterno; LinkedIn fortnightly, lunedì 09:00 ogni 14 giorni dal 05/10/2026, per il singolo post bilingue, prospecting, performance e review mensile quando dovuta. Tutti gli altri trigger e il test restano sospesi. Manifest corrente: `output/Linkedin/config/schedule-consolidation-20261002-v05.json`.

## Carico per il team

Un solo nuovo post bilingue ogni due settimane; se una revisione è ancora pendente, riprenderla senza aggiungere un secondo pacchetto. Le bozze già prodotte si conservano: passare al successivo elemento soltanto nel periodo successivo, senza duplicare né recuperare pubblicazioni saltate. L'ordine finale resta EN/IT per B2B e IT/EN per Nova Energia. Conservare la sequenza a dieci post B2B, NE, B2B, NE, B2B, B2B, NE, B2B, B2B, NE e il punto corrente: il rapporto 6/4 si distribuisce ora su venti settimane.

Preparazione il lunedì, **martedì successivo alle 16:00 come proposta editoriale** per il singolo post. Le precedenti fonti sui benchmark restano nel manifest storico; non è un picco EFS dimostrato. Non creare invii programmati, non pubblicare e non attivare live publisher. Approvazioni native, kit corrente, fonti SharePoint e limiti delle azioni restano quelli documentati.

Per contenuti e analisi, un'unica sintesi breve ogni due settimane in Scheduled quando ci sono novità utili: post proposto, decisioni necessarie e opportunità rilevanti. I controlli operativi giornalieri segnalano separatamente solo nuove conversazioni, cambiamenti azionabili o nuovi blocchi, mantenendo deduplicati gli avvisi invariati. Nessun reminder ripetuto o quota di proposte da riempire. Prospecting ed engagement soltanto per casi pertinenti con nuove evidenze, alle rispettive cadenze; se un batch è pendente, riprenderlo. Conservare i limiti massimi già autorizzati e preferire poche proposte documentate. Applicare `docs/maintenance/teams-approvals.md` per tutte le nuove revisioni: pacchetto completo nella cartella cloud Outputs/LinkedIn, manifest versionato caricato per ultimo, Approvazione nativa e ricevuta accanto ai file. Gli approvatori sono gestiti dal flusso Microsoft; nessuna chat, gruppo, DM, email o menzione personale come destinazione. Le skill facoltative aiutano con fonti e accessi: le loro vecchie istruzioni di routing sono superate. Conservare prove storiche e richieste pendenti senza reinvii automatici. Approvazione e autorizzazione di esecuzione rimangono distinte secondo il proprio workflow.

## Controlli operativi — lun–ven 11:00

Aggiornamento successivo del 02/10/2026: riconciliare nel passaggio esistente anche le approvazioni comuni degli input e quelle delle newsletter, secondo docs/company/input-approvals.md e docs/newsletter/workflow.md. Non crea un ulteriore monitor. La preparazione newsletter ha la propria ricorrenza mensile nella chat; i due gruppi LinkedIn e il manifest v05 restano invariati.

1. Inbox e commenti propri: recuperare gli eventi dall'ultimo checkpoint completo, compresi weekend e interruzioni, rispettando baseline e policy delle risposte.
2. Riconciliare approvazioni pendenti, aggiornare lo stato dei post originali nei loro canali e riprendere follow prospect soltanto quando già autorizzati e approvati.
3. Engagement esterno nel medesimo passaggio operativo, con approvazioni e limiti propri. Recuperare gli eventi del weekend al successivo passaggio, senza resettare baseline o duplicare digest/proposte.

## Preparazione e analisi — ogni due settimane

Prima della selezione di fonti e media leggere l'elenco Teams Marketing Inputs in Documentation / General e i dettagli delle approvazioni native; consultare il registro input comune come cache e applicare docs/company/marketing-input-list.md e docs/company/input-approvals.md, anche quando i moduli operativi v02 contengono indicazioni precedenti. Non usare nuove revisioni senza approvazione né duplicare richieste pendenti create dalla newsletter. Marketing/Inputs conserva gli originali. Le fasi indipendenti continuano sulle fonti già autorizzate.

1. Performance degli ultimi 14 giorni completi confrontabili con i 14 precedenti e segnali delle aziende in watchlist. Periodi parziali e dati mancanti espliciti.
2. Preparare/riprendere il singolo pacchetto bilingue del periodo.
3. Prospecting mirato, senza richieste di riempire una coda o attività senza evidenze utili. Il monitor approvazioni/follow resta nel passaggio operativo: non duplicarne gli invii.

La prima esecuzione quindicinale disponibile del mese include una breve review del mese solare precedente, se non già completata. Integrarla nella stessa sintesi e nelle note locali; nessun ulteriore report da revisionare per il team o trigger mensile. Conservare fonti e report locali necessari alla tracciabilità.

## Ripresa e confini

Leggere i moduli operativi v02 immutabili indicati nel manifest e verificarne gli hash SHA-256. Questo documento, il manifest v05 e le regole correnti hanno precedenza sui vecchi orari e quantità contenuti nei moduli; autorizzazioni e deduplicazione conservano il proprio ambito; nuovi destinatari e decisioni sono gestiti nel flusso Microsoft.

Eseguire le fasi in sequenza nella stessa esecuzione, senza sottoagenti o nuove schedule. Lock esclusivo del proprio gruppo `output/Linkedin/config/schedule-runs/fortnightly.lock` oppure `output/Linkedin/config/schedule-runs/daily_operations.lock` con owner, timestamp e scopo, più i lock specifici dei workflow. Non eliminare alla cieca lock vivi/orfani; rilasciare solo quelli posseduti. Conservare `output/Linkedin/config/schedule-runs/state.json` e i registri canonici esistenti, senza azzerare gruppi precedenti, baseline, code o approvazioni.

Per daily_operations la slot key è data locale più 11:00; per fortnightly period_key è il periodo di 14 giorni ancorato al 05/10/2026; month_key è il mese solare analizzato. Non eseguire i moduli dell'altro gruppo, conservando i checkpoint già esistenti per riprendere le precedenti scansioni. Usare stato e prove già presenti per evitare duplicati anche quando manca il checkpoint dell'orchestratore. Non generare un nuovo pacchetto se il periodo è già preparato o una review è pendente. Nessun recupero automatico dei periodi saltati.

Unknown/sending richiede riconciliazione sul servizio originale prima di ritentare. Un modulo bloccato non impedisce quelli indipendenti; salvare copertura e stato parziale, senza avanzare un checkpoint completo falso. Le autorizzazioni di inbox, commenti propri, engagement esterno, prospecting e original-post restano distinte. Input, output e temporanei restano nelle categorie canoniche del workspace.
