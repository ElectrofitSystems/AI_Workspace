# Compilazione delle automazioni

## Dalla richiesta al risultato

1. Identificare l'automazione reale: nome, modulo o flusso, proprietario, obiettivo
   e risultato atteso. Non assumere che sia Power Automate dal solo termine
   «automazione».
2. Consultare modulo e istruzioni correnti. Il modello interno
   `docs/company/templates/automation-brief.md` aiuta a distinguere campi e fonti;
   non produrre una scheda da consegnare all'ingegnere.
3. Mappare ogni campo alla fonte e alla revisione corretta. Riutilizzare i dati
   già disponibili e chiedere soltanto quelli mancanti.
4. Preparare compilazione, bozza testuale o guida direttamente nella chat personale
   che contiene la richiesta specifica a @Virgilio.
5. Verificare campi obbligatori, formato, coerenza, destinazione e azione finale.
   L'ingegnere verifica e preme Invia nella modalità normale.
6. Se l'ingegnere richiede esplicitamente l'esecuzione, completare e avviare il
   flusso concordato e inviare le richieste di approvazione previste, solo attraverso
   strumenti effettivamente disponibili. Non assumere decisioni di approvazione.
7. Verificare ricevuta e stato; restituire il riscontro nella chat senza generare
   file di output. Non dichiarare eseguita un'azione non provata.

## Stati descrittivi

`da chiarire` → `bozza` → `verificata` → eventuale `in revisione` →
`pronta per l'azione richiesta` → `consegnata/eseguita`.

Usare lo stato effettivamente dimostrato. Un salvataggio locale non prova che il
flusso cloud sia stato avviato. Dopo un esito incerto, verificare se l'operazione
è già avvenuta prima di ripeterla, per evitare invii o record duplicati.

Procedure riutilizzabili senza dati operativi possono essere mantenute in docs/.
Le conversazioni restano in Teams; non trasformarle in file di consegna.
Non sviluppare, riconfigurare o ristrutturare l'automazione durante la guida.

## Primo processo

Test Request, ancora in sviluppo secondo l'utente: Power Apps con Teams.
Esiste una lista Test Requests nel sito Engineering. Non considerare questa
esistenza una verifica dell'app o dell'intero flusso. Approfondire i dettagli
funzionali più avanti, come richiesto, senza inventare campi o approvatori.
