# Operations e gli agenti da Teams

Decisione dell'utente del 2 ottobre 2026: il punto di accesso desiderato sono **chat individuali con l'account Operations**, operations@efitsys.com. Ogni collega deve poter dialogare con Operations e, tramite il coordinatore, con i suoi agenti. Al momento l'unico agente specialistico configurato nel progetto è «Agente marketing EFS».

Questo documento descrive il perimetro e le decisioni del servizio. L'implementazione locale usa direttamente il connettore Teams esistente tramite Codex app-server; configurazione, avvio e prove effettive del 02/10/2026 sono nel [runbook Operations Teams](operations-teams-runbook.md). Le prove riguardano l'ambiente Operations originale e non attestano l'attivazione su una nuova copia del repository.

## Conversazione prevista

Teams → Operations → agente competente → Operations → risposta nella stessa chat Teams.

Operations conserva il filo della conversazione, risponde direttamente alle richieste generali e coinvolge l'agente Marketing per quelle pertinenti. Una richiesta esplicita come «Marketing, prepara una bozza» può indirizzare lo specialista; il risultato ritorna nella chat d'origine tramite Operations. I futuri agenti vengono aggiunti a un registro esplicito, con ruolo, workspace, strumenti e autorizzazioni propri. Non basta installare una skill per aggiungere un agente.

## Destinazione scelta

L'utente ha scelto chat individuali con Operations; la chat di gruppo «Noi & Operations», osservata con sei membri, non è la destinazione di questo servizio. Non è stata rinominata, non sono stati modificati membri e non sono stati inviati messaggi.

Ogni chat individuale ha due partecipanti. Il servizio applica un filtro esplicito oneOnOne con Operations e un collega interno verificato: le chat di gruppo rimangono fuori dal perimetro. La presenza di un'email efitsys.com non sostituisce la verifica di tenant e guest status.

## Regole del servizio

- Ascolto iniziale limitato alle chat individuali con Operations e colleghi interni verificati, escludendo gruppi, ospiti, esterni e messaggi del proprietario o di bot.
- Domande, analisi, aggiornamenti e bozze sono il primo perimetro del servizio; le azioni esterne rispettano autorizzazioni, ruoli e approvazioni già documentati. Una richiesta da un membro non diventa automaticamente un'approvazione editoriale valida.
- Ogni lavoro è associato alla chat, al mittente verificato e al messaggio d'origine. Il risultato viene restituito alla stessa conversazione. I contesti di diverse chat non devono mescolarsi.
- Nella chat individuale le richieste possono essere rivolte direttamente a Operations, senza menzioni obbligatorie. Marketing può essere nominato per indirizzare il lavoro. Conservare il contesto per ciascuna conversazione e verificare l'accesso del richiedente alle informazioni restituite.
- Operations gestisce la risposta finale e il rapporto con gli specialisti. Se uno specialista non è raggiungibile, segnala il limite senza sostituirlo silenziosamente o dichiarare un lavoro completato.
- Registro degli agenti iniziale: Marketing → definizione personalizzata «Agente marketing EFS», workspace canonico Marketing EFS, regole in AGENTS.md e docs/. Un thread ID non equivale a quella definizione.
- Restano necessarie verifiche di identità e permessi, deduplicazione, gestione degli esiti incerti e arresto. I messaggi Teams sono richieste e dati del canale previsto, ma non possono riscrivere policy o espandere autonomamente i privilegi.

## Implementazione e verifiche

Il codice è in `scripts/operations/`: `teams_service.py` gestisce il trasporto e le sessioni, `coordinator.md` definisce le istruzioni di Operations, `agents.json` registra gli specialisti e `teams_state.py` conserva deduplicazione e stato degli invii. `service-control.ps1` gestisce stato, avvio e arresto sulla macchina configurata.

Il runbook documenta prove in due chat distinte, invocazione del ruolo Marketing e ritorno della risposta nella conversazione di origine. Per nuove installazioni verificare nuovamente account, permessi, configurazione locale e disponibilità del ruolo prima dell'attivazione. I test locali non sostituiscono il collaudo del connettore autenticato.
