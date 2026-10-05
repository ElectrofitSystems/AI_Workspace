# Marketing Statistics — recap mensile

Mandato dell’utente del 05/10/2026: raccogliere i dati marketing accessibili, mostrare follower nuovi, views e altri KPI in Outputs/Statistics e ripetere il recap circa una volta al mese.

## Consegna e ricorrenza

- Chat responsabile: MASTER — Marketing EFS, ID `01a0fd13-5047-7e01-8ddf-c5a98a2f58aa`.
- Heartbeat attivo `efs-monthly-schedule-marketing-statistics`, nome `EFS - Monthly schedule - Marketing statistics`.
- Primo lunedì del mese alle 12:00 Europe/Rome, dal 02/11/2026. Mese solare precedente confrontato con quello prima. Il recap iniziale del 05/10 copre settembre e un aggiornamento fino al 3 ottobre.
- PDF versionato nella cartella locale `output/Statistics/` e nella cartella SharePoint esistente `General/Marketing/Outputs/Statistics`, sito Documentation. Applicare `docs/company/output-delivery.md`; CSV, snapshot, note, configurazioni e ricevute restano locali.
- Stato mensile e consegna: `output/Statistics/config/monthly-state.json`. Non registrare completo prima di verifica del PDF e del caricamento. In caso di esito cloud incerto, riconciliare il file prima del retry. Non duplicare un month_key già consegnato; nuove evidenze possono richiedere una revisione versionata.

La review mensile eventualmente già prodotta dal passaggio LinkedIn quindicinale è una fonte del medesimo recap, non un secondo incarico. La raccolta mensile amplia e rende leggibili le evidenze disponibili. Le schedule LinkedIn e newsletter mantengono ID e frequenze; nessuna nuova pubblicazione o richiesta di approvazione è autorizzata dalla raccolta statistiche.

## Fonti e metodo

1. Rileggere README, AGENTS, regole, contesto, fonti, consegna output, coordinamento e `docs/linkedin/measurement-and-sales.md`.
2. Verificare accesso e identità amministratore della Pagina LinkedIn `103544667`. Preferire export originali Contenuto, Follower, Visitatori e integrare i dettagli admin dei post, ricerca e newsletter quando accessibili. L’accesso in una vecchia chat non garantisce quello corrente.
3. Conservare originali in `input/Technical documentation/Marketing analytics/YYYY-MM-DD/`; dati derivati in `output/Statistics/data/YYYY-MM-DD/`; temporanei in `.local/maintenance/temporary/`. Registrare hash, intervallo e fuso. Gli XLS LinkedIn del 05/10 hanno date UTC e segnalano un ritardo contenuto fino a due giorni.
4. Il lettore BIFF locale `scripts/maintenance/read_linkedin_biff.py` non installa pacchetti e rifiuta formule o strutture non gestite. Verificare intestazioni, 365 date uniche quando richieste e corrispondenza con riepiloghi admin prima di usare i numeri. Non presumere che export futuri abbiano lo stesso schema. Le estrazioni JSON sono file derivati, non originali.
5. Distinguere impressioni, reach, views video, views Pagina, visitatori unici, clic e visite sito. Non sommare unici giornalieri come audience mensile. Un valore del riepilogo LinkedIn conserva l’etichetta della piattaforma, senza affermare una deduplicazione indipendente.
6. Nuovi follower sono acquisizioni; la colonna “Follower totali” nel foglio “Nuovi follower” è il totale acquisito nel giorno, non il totale cumulativo della Pagina. Saldo netto solo da totali omogenei a inizio/fine periodo. Follower persi e saldo mensile mancanti restano N.D.
7. Totali mensili da eventi giornalieri confrontabili; anche medie giornaliere per mesi di durata diversa. CTR da somma clic / somma impressioni, non media semplice. Snapshot dei post separati dalle metriche per data di esposizione; non sommare snapshot successivi. Per lo stesso post non sommare righe organico/sponsorizzato e Totale.
8. Paid storico distinto da organico corrente. Nessuna spesa/ROI inventata. Lead, richieste e opportunità soltanto da registro commerciale canonico riconciliato; un registro vuoto non prova zero lead.
9. Newsletter, sito e altri analytics: usare solo fonti realmente accessibili. Dati mancanti N.D., mai zero. Nessuna nuova connessione, credenziale, installazione, campagna, invito o invio.
10. PDF: font Barlow e logo/palette del Corporate Design Kit 3.4, KPI chiari, periodi, confronto, andamento, post, audience e copertura. Render e verifica visiva, poi upload del solo PDF e readback di metadata/contenuto; archivi precedenti conservati.

## Primo rilevamento

Il tentativo quindicinale della mattina del 05/10 era bloccato dall’authwall. In questa raccolta l’accesso admin è riuscito; le prove del tentativo fallito sono conservate. Snapshot nuovo: `output/Statistics/data/2026-10-05/marketing-statistics-2026-10-05-v01.json`. Recap: `output/Statistics/efs-marketing-statistics-2026-10-05-v01.pdf`.

Tre XLS originali coprono 04/10/2025–03/10/2026. Copertura commerciale incompleta, sito non collegato nelle fonti recuperate, analytics newsletter non verificati. Il confronto competitor usa suggerimenti della piattaforma, non una shortlist strategica approvata.
