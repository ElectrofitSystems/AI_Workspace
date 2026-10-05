# Stato ERP EFS

Aggiornamento: 5 ottobre 2026, 13:05 CEST. Pilota configurato e servizio attivo.

Verifica integrazione ERP: 5 ottobre 2026, 13:18 CEST. Documentazione Sistemi
conferma API REST e Reporter via web services. Installazione osservata:
eSolver 4.4.03E, Ambiente REST 2.0 2026.06C, ES-EXT, ES-RPT e schedulatore
attivo; EC742 offre Aggiungi a schedulazione. Non ancora verificati endpoint
fornitori, licenze/abilitazioni del servizio o export automatico funzionante.
Nessuna configurazione modificata. Dettagli e prossima verifica tecnica in
[connectivity-verification.md](connectivity-verification.md); bozza per
assistenza in [esolver-partner-questions.md](esolver-partner-questions.md),
non inviata. Referente Sistemi richiesto all'utente e ancora da identificare.

Verificati:
- porta RDP 192.168.20.16:3389 raggiungibile;
- sessione RDP autenticata e eSolver aperto sulla ditta Electrofit Systems;
- consultazione fornitori EC742 ed esportazione verso Excel;
- account Operations e identità esatta Francesco Lucherini tramite Teams;
- servizio Teams generale già attivo.

Completati:
- originale eSolver acquisito in input/esolver/erp20261005.xlsx, schema
  validato e conteggio/netto confrontati con la griglia;
- snapshot datato in .local/erp/payables-latest.json e report leggibile in
  output/payables/scadenzario-fornitori-2026-10-05.txt;
- definizione Agente ERP EFS nel progetto e nella directory agenti personale;
- registro e coordinatore Operations estesi al ruolo ERP;
- accesso finanziario per Francesco Lucherini tramite ID + email + tenant;
- diniego deterministico agli altri account, senza leggere il dataset;
- controlli prima dell'acquisizione e prima dell'invio, validità giornaliera
  e nuova sessione per ogni richiesta ERP;
- profilo worker con dati ERP e stato Teams negati ai comandi, rete dei
  comandi, Apps, MCP, plugin e browser disabilitati;
- riavvio del servizio unico esistente con Codex 0.160.0. Health verificato
  running/live, ultima scansione 11:05:48 UTC, coda vuota, PID 10788.

Collaudi effettivi:
- 15 test ERP: importi, crediti, periodi, identità, revoca, dati scaduti,
  cambio destinatario e sessioni finanziarie separate;
- 13 test preesistenti del trasporto Teams: tutti superati;
- probe Windows: istruzioni leggibili; snapshot, originale, report e stato
  del trasporto non leggibili dal sandbox;
- due turni locali con vero ruolo Agente ERP EFS, identità verificata dal
  runtime e risposta confrontata con il dataset; ultimo turno 148,4 secondi.
  È il tempo di elaborazione locale, senza latenza Teams;
- get_profile sul nuovo runtime: identità Operations confermata.
Nessun messaggio di prova o annuncio è stato inviato in Teams.

Non ancora verificati: aggiornamento automatico ERP, riconciliazione
amministrativa, test reale Teams del nuovo flusso, valuta di conto e codici stati.
Nessuna nuova ricorrenza o invio proattivo ERP configurato.

Prossima verifica: Francesco scrive nella chat individuale con Operations
"ERP, quali fatture risultano da pagare?". Controllare identità del ruolo,
risposta, data dei dati e readback nel servizio, senza pubblicare i log privati.
Per dati dei giorni successivi serve una nuova acquisizione eSolver e
importazione con conteggio/netto della griglia. Il collegamento automatico
di acquisizione è un lavoro ancora aperto, distinto dal trasporto Teams.
Conservare il file originale e la fotografia del 05/10/2026.

File del servizio condiviso modificati: scripts/operations/appserver.py,
teams_service.py, coordinator.md, agents.json, watchdog.py e relativo runbook
in Marketing EFS. Copie precedenti conservate nei temporanei ERP per rollback;
nessuna modifica a permessi Microsoft, credenziali o master marketing.

## BOM eFit96-141 — preparazione del 05/10/2026

Richiesta desktop dell'utente: gestire la BOM eFit96-141 in eSolver. Scelto
esplicitamente il foglio generale `eFit96-Kit-V2 - Status` della V9.1; sistema
solare confermato come opzione separata. Preparazione locale eseguita con
Agente ERP EFS; nessun articolo o distinta modificato nella fase iniziale di
preparazione. Il successivo comando desktop «Ok applica e rimandaci nella
pagina principale dell'ERP» autorizza l'applicazione descritta sotto.

- Originale SharePoint e manifest in `input/esolver/bom/2026-10-05/`.
- Export tecnico EM001 con filtro codice `010*`: 327 righe, conteggio
  confrontato con la griglia, originale XLSX acquisito tramite clipboard RDP.
- EM031 Anagrafica distinta base disponibile. Articoli verificati: finito
  `010000000 — EFIT-96 KIT V2`, PDU `010100000` e cavo `010701200` in metri.
- Standard: 263 righe componente, 247 codici definitivi distinti, 246 trovati
  nel catalogo esportato. Solare: 12 righe, di cui 8 con codice non trovato.
- Unico codice definitivo standard non trovato: `0107020010`; candidato
  `010702010` con descrizione coincidente, P/N ERP vuoto. Correzione proposta,
  non applicata. Sette voci standard con codice TBD/MOD TBD o vuoto rimangono
  da definire; domanda all'utente sui codici/specifiche ancora aperta.
- U.M. assenti dall'export; 33 differenze di P/N quando entrambi valorizzati
  nell'intera sorgente sono segnalazioni da valutare, non errori automatici.
  Da risolvere anche la descrizione della rondella `010107019` e la gerarchia.

Report e mapping in
[fattibilita-mapping-esolver-2026-10-05.md](../output/bom/eFit96-141/fattibilita-mapping-esolver-2026-10-05.md),
staging `output/bom/eFit96-141/bom-staging-v9.1.json`, confronto
`output/bom/eFit96-141/confronto-articoli-esolver-v9.1-2026-10-05.json`.
Lo staging conserva le 275 righe sorgente e la separazione standard/solare;
non è un tracciato importabile eSolver. Import/API BOM ed editor righe non
ancora verificati. Prossimo passo: risolvere i dati tecnici aperti, completare
U.M. e legami padre/componente e identificare il caricamento supportato prima
di completare e verificare la revisione ERP. Il servizio Teams scadenzario
rimane un'attività separata.

## BOM eFit96-141 — applicazione autorizzata del 05/10/2026

Rilettura stabile EM031: otto distinte attive già presenti; il conteggio zero
iniziale era transitorio durante il caricamento. Il finito `010000000` ha otto
righe con riferimento 1 N.; il solare `010800000` è già separato e non incluso
nel finito. I campi Tipo/Alternativa/Decorrenza nei dialoghi Nuovo e Copia non
consentono una bozza alternativa separata nella configurazione osservata.

Completato l'allineamento quantitativo verificabile della PDU esistente
`010100000`, con backup nativo e riferimento invariato di 1 N.: 59 candidati
iniziali, 58 correzioni salvate e verificate, una quantità zero rifiutata da
eSolver (`010104001`, valore precedente 1 conservato). Ulteriori 15 differenze
escluse per identità/P/N/dimensioni da chiarire. Confronto degli export nativi:
80 righe conservate, 58 quantità conformi al piano, 22 righe invariate,
tutti gli altri campi esportati identici al backup. Risultato in
`output/bom/eFit96-141/verifica-export-PDU-prima-dopo-2026-10-05.json`.
Il piano con valori prima/dopo e verifiche è in
`output/bom/eFit96-141/piano-correzione-quantita-PDU-2026-10-05.json`.
L'esito finale e il ritorno alla home sono registrati in
`output/bom/eFit96-141/esecuzione-bom-esolver-2026-10-05.md`.

Solar `010800000`: due cavi `010701600` e `010701700` corretti da 0 a 4 M
ciascuno. Salvataggio, riapertura e confronto export nativi verificati:
quattro righe conservate, due quantità aggiornate, altre due righe e tutti i
campi non quantitativi invariati. Terminale `010803004` lasciato a 15 N.
per P/N source/catalogo discordanti. Piano e prova in
`output/bom/eFit96-141/piano-correzione-quantita-Solar-2026-10-05.json`.
Totale del passaggio: 60 correzioni quantitative salvate e verificate.
Pagina principale eSolver, ditta EL, verificata alle 16:38:16 CEST;
editor, liste ed Excel chiusi, sessione RDP connessa. Evidenza conservata:
`home-esolver-EL-2026-10-05-163816.jpg` nel materiale di esecuzione BOM.

La revisione completa V9.1 resta da validare: sette articoli provvisori,
mapping Schuko, identità ambigue e otto codici solari mancanti. Nessuna
creazione di anagrafiche non definite e nessuna inclusione del solare standard.
Gli altri cinque semiassiemi non sono stati allineati in questo passaggio.
