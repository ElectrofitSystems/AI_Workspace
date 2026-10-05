# Verifica integrazione eSolver — 5 ottobre 2026

Verifica in sola consultazione della documentazione pubblica Sistemi e
dell'installazione aperta via RDP su 192.168.20.16. Nessun endpoint, servizio,
lavoro schedulato, accesso o dato contabile modificato. Nessun messaggio esterno
inviato. Il pilota Teams continua a usare l'esportazione manuale datata.

## Esito

La disponibilità di tecnologie API REST nel prodotto eSolver è confermata
da Sistemi. La scheda ufficiale elenca anche «Reporter via web services».
Non è ancora verificata un'interfaccia di sola lettura dello scadenzario
fornitori utilizzabile dalla nostra installazione. L'installazione dei
componenti non dimostra licenza, attivazione HTTP, permessi o copertura dei dati.

La schedulazione nativa è presente e il relativo servizio risulta attivo.
La voce dello scadenzario offre «Aggiungi a schedulazione». Questo non prova
che EC742 possa produrre automaticamente CSV/XLSX senza aprire finestre o Excel.
Un'esportazione automatica funzionante non è ancora stata collaudata.

## Riscontri sull'installazione

| Osservazione | Riscontro | Limite |
| --- | --- | --- |
| Versione eSolver | 4.4.03E, ditta EL | Versione osservata, non verifica delle licenze |
| Prodotti installati | AMBIENTE_REST, Ambiente REST 2.0, versione 2026.06C | Nessun URL/API autenticato verificato |
| Integrazioni esterne | ES-EXT, versione 4.4.03 | Nessuna interfaccia fornitori identificata |
| Report e query | ES-RPT, versione 4.4.03E; Reporter v.3, BCRPTA apribile | Reporter via web services non collaudato |
| Schedulatore | Stato lavori schedulati Attivo; Servizio Schedulazioni Attivo | Nessuna nuova schedulazione creata |
| Scadenzario | EC742 già verificato; menu contestuale con Aggiungi a schedulazione | Output senza operatore e data dinamica non verificati |
| Report personalizzati | Elenco vuoto nella cartella personalizzata selezionata | Non dimostra assenza di report standard o in altre cartelle |

Nella lista di lavori visualizzata non è stato osservato un export scadenzario.
Non è una verifica esaustiva di tutte le configurazioni o di eventuali
schedulazioni esterne.

Percorsi osservati nell'applicazione: installazione
`\\server2015\SISTEMI\ESOLVER\`, runtime `D:\SISTEMI\ESOLVER\`, report
`\\server2015\SISTEMI\ESOLVER\REPORT\`. Un controllo Test-Path della cartella
di installazione dal computer Operations ha restituito false con l'identità
corrente; la causa non è stata identificata. La sessione RDP resta utilizzabile.
Non sono stati tentati accessi con altre credenziali.

Il collegamento Manuale apre una guida locale con intestazione eSolver 4.2.
Questa intestazione differisce dalla versione installata 4.4.03E e non costituisce
documentazione attuale degli endpoint REST. Identificativi di installazione,
chiavi di accreditamento e credenziali non sono trascritti in questi appunti.

## Fonti ufficiali

- [Scheda eSolver Sistemi](https://www.sistemi.com/downloads/eSOLVER-scheda.pdf):
  pagina 2, API REST; pagina 3, Reporter via web services. Consultata il
  05/10/2026. Descrive il prodotto, senza specifica tecnica degli endpoint.
- [Le integrazioni di eSolver](https://www.sistemi.com/software-gestionali/esolver/le-integrazioni-di-esolver/):
  Sistemi dichiara API REST e tracciati di importazione/esportazione. Non
  identifica un endpoint pubblico dello scadenzario fornitori.

## Verifica tecnica ancora necessaria

Richiedere al partner Sistemi documentazione e abilitazioni della nostra
installazione. Preparata una [bozza tecnica](esolver-partner-questions.md),
senza inviarla. Referente dell'assistenza ancora da identificare.

Per la via API/Reporter occorrono URL verificato, documentazione compatibile
con 4.4.03E, modalità di autenticazione e un account limitato alla lettura
delle scadenze fornitori della ditta EL. Verificare che siano disponibili
residui, rate, valuta, note di credito, stati/blocchi e dati delle distinte,
con filtri e data di situazione equivalenti alla consultazione EC742.
Reporter via web services è una possibilità da verificare, non un endpoint
REST dello scadenzario già identificato.

Per la via export occorrono programma/report supportato, configurazione
riutilizzabile, data di situazione aggiornata automaticamente, formato
CSV/XLSX, destinazione protetta raggiungibile e funzionamento senza operatore.
Il percorso manuale che apre Excel non soddisfa ancora questi requisiti.

Il collaudo dovrà confrontare conteggio e residui con EC742 a parità di filtri,
verificare completezza/paginazione e ripetere l'acquisizione con una nuova
data di situazione. Pubblicare uno snapshot soltanto dopo validazione completa;
in caso di errore mantenere i controlli di scadenza del pilota. Frequenza e
configurazione della ricorrenza sono ancora da definire.
