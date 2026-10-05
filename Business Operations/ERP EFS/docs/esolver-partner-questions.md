# Bozza per il partner Sistemi — integrazione in sola lettura

Bozza tecnica del 05/10/2026, non inviata. Referente da identificare.

Vorremmo automatizzare la sola consultazione dello scadenzario fornitori di
Electrofit Systems, ditta EL, da eSolver 4.4.03E. Il primo risultato serve alla
chat individuale Operations di Francesco Lucherini. Non sono richieste
registrazioni di pagamenti o modifiche contabili.

Nell'installazione risultano AMBIENTE_REST 2026.06C, ES-EXT 4.4.03 e ES-RPT
4.4.03E. Reporter v.3 è apribile e il servizio di schedulazione risulta attivo.
La consultazione usata è EC742, Interrogazione scadenzario fornitori.

Potete verificare questi punti?

1. Quali API REST ufficiali o servizi Reporter sono licenziati e attivati
   sulla nostra installazione? Ci sono endpoint/report di sola lettura per
   lo scadenzario fornitori? Servono moduli o aggiornamenti aggiuntivi?
2. Potete fornire documentazione tecnica compatibile, URL del servizio,
   schema dei dati, filtri, paginazione, autenticazione e modalità per
   predisporre un account limitato alla sola lettura della ditta EL?
   Le credenziali andranno configurate tramite un canale protetto.
3. I dati includono identificativo stabile della rata, fornitore, fattura,
   date documento/scadenza, residuo, valuta, note di credito, blocchi,
   stato di pagamento/distinta e distinte non ancora contabilizzate?
   Qual è l'equivalenza esatta con i filtri di EC742?
4. In alternativa, quale report o programma supportato può esportare
   CSV/XLSX automaticamente tramite lo schedulatore, senza Excel o
   intervento dell'operatore? Come si imposta la data di situazione corrente
   e si conservano filtri/output? È richiesta una sessione interattiva?
5. Quale destinazione protetta e quale identità di servizio consigliate
   per l'output? Come si gestiscono esecuzioni fallite, file incompleti
   e aggiornamento atomico del file destinato all'importazione?
6. Possiamo collaudare una lettura e confrontare conteggio e residui con
   EC742 sugli stessi filtri, poi ripetere con una nuova data di situazione?

Per il pilota è già verificata una consultazione manuale con export Excel.
API di lettura specifica e export automatico restano da collaudare.
