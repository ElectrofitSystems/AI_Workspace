# Operations e gli agenti da Teams

Decisione dell'utente del 2 ottobre 2026: il punto di accesso desiderato sono **chat individuali con l'account Operations**, operations@efitsys.com. Ogni collega deve poter dialogare con Operations e, tramite il coordinatore, con i suoi agenti. Al momento l'unico agente specialistico configurato nel progetto è «Agente marketing EFS».

Questo documento conserva il progetto iniziale e le decisioni. L'implementazione locale e le prove effettive del 02/10/2026 sono nel [runbook Operations Teams](operations-teams-runbook.md), che prevale sulle sezioni storiche «implementazione ancora necessaria» sotto. Il plugin My Avatar è installato localmente; il suo bridge resta fermo, sostituito dal trasporto diretto tramite il connettore Teams esistente.

## Conversazione prevista

Teams → Operations → agente competente → Operations → risposta nella stessa chat Teams.

Operations conserva il filo della conversazione, risponde direttamente alle richieste generali e coinvolge l'agente Marketing per quelle pertinenti. Una richiesta esplicita come «Marketing, prepara una bozza» può indirizzare lo specialista; il risultato ritorna nella chat d'origine tramite Operations. I futuri agenti vengono aggiunti a un registro esplicito, con ruolo, workspace, strumenti e autorizzazioni propri. Non basta installare una skill per aggiungere un agente.

## Destinazione scelta

L'utente ha scelto chat individuali con Operations; la chat di gruppo «Noi & Operations», osservata con sei membri, non è la destinazione di questo servizio. Non è stata rinominata, non sono stati modificati membri e non sono stati inviati messaggi.

Ogni chat individuale ha due partecipanti, perciò il limite maxParticipants=3 della v0.1 non ostacola il modello. Per il servizio è proposto un filtro esplicito oneOnOne con Operations e un collega interno verificato: le chat di gruppo rimangono fuori dal perimetro. La presenza di un'email efitsys.com non sostituisce la verifica di tenant e guest status.

## Regole proposte

- Ascolto iniziale limitato alle chat individuali con Operations e colleghi interni verificati, escludendo gruppi, ospiti, esterni e messaggi del proprietario o di bot.
- Domande, analisi, aggiornamenti e bozze sono il primo perimetro del servizio; le azioni esterne rispettano autorizzazioni, ruoli e approvazioni già documentati. Una richiesta da un membro non diventa automaticamente un'approvazione editoriale valida.
- Ogni lavoro è associato alla chat, al mittente verificato e al messaggio d'origine. Il risultato viene restituito alla stessa conversazione. I contesti di diverse chat non devono mescolarsi.
- Nella chat individuale le richieste possono essere rivolte direttamente a Operations, senza menzioni obbligatorie. Marketing può essere nominato per indirizzare il lavoro. Conservare il contesto per ciascuna conversazione e verificare l'accesso del richiedente alle informazioni restituite.
- Operations gestisce la risposta finale e il rapporto con gli specialisti. Se uno specialista non è raggiungibile, segnala il limite senza sostituirlo silenziosamente o dichiarare un lavoro completato.
- Registro degli agenti iniziale: Marketing → definizione personalizzata «Agente marketing EFS», workspace canonico Marketing EFS, regole in AGENTS.md e docs/. Un thread ID non equivale a quella definizione.
- Restano necessarie verifiche di identità e permessi, deduplicazione, gestione degli esiti incerti e arresto. I messaggi Teams sono richieste e dati del canale previsto, ma non possono riscrivere policy o espandere autonomamente i privilegi.

## Implementazione ancora necessaria

Il modulo coordinator del pacchetto è soltanto una predisposizione e diventa il centro di questo progetto. Occorre implementare e testare invocazione dello specialista, attesa/esito, ritorno a Operations e invio Teams correlato. Non è stato creato un agente Operations o un nuovo thread: l'utente ha espresso l'obiettivo, senza chiedere di creare una nuova chat Codex.

La scelta dell'host è ancora aperta. Il percorso MCP Events ufficiale richiede ChatGPT Work Cloud; da quell'host non si può presumere accesso ai file o alla definizione personalizzata su questo PC. Serve un'integrazione esplicita con l'ambiente che esegue gli agenti, oppure un backend che renda disponibili le loro definizioni e fonti. Il semplice inoltro a coordinator.threadId non risolve questo confine.

Prima del pilota vanno corretti gli errori di formato evento, claim e recupero descritti in myavatar.md; configurati il filtro oneOnOne, trasporto, connessioni e percorso di esecuzione degli agenti; verificata una richiesta Marketing con risultato nella stessa chat e un successivo messaggio di revisione. La prova deve includere due colleghi in chat diverse, per verificare isolamento del contesto e del destinatario. La destinazione è decisa; non è stata ancora attivata.
