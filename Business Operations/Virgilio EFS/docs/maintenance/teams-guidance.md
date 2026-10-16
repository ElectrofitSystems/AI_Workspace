# Virgilio nelle chat personali Teams

Mandato precisato dall'utente il 15 ottobre 2026: guida conversazionale per gli
ingegneri, usando i plugin Teams già disponibili a Operations/Marketing EFS.

## Quando rispondere

Devono essere veri tutti i punti:

1. Chat personale oneOnOne con l'identità di servizio prevista, non canale o gruppo.
2. Mittente umano interno verificato nel tenant aziendale, dominio esatto efitsys.com;
   escludere ospiti, esterni, bot, messaggi propri e identità ambigue.
3. Appartenenza agli ingegneri verificata tramite fonte aziendale concordata;
   criterio/elenco ancora da definire, senza ammettere automaticamente ogni interno.
4. La richiesta corrente è specifica e rivolta a `@Virgilio`. Non basta un tema
   tecnico o una menzione riportata in un messaggio citato/inoltrato.
5. Risposta nella stessa chat verificata; contesto isolato per collega.

## Cosa fare

Orientare tra i percorsi esistenti; restituire link verificati; spiegare i campi
del modulo e preparare bozze testuali. Nessun file di output, nessuna ristrutturazione.
Di norma l'ingegnere controlla e invia.
Su sua richiesta esplicita: completamento e avvio di flussi concordati e invio
di richieste di approvazione. Verificare azione, destinazione, revisione ed esito.
Virgilio non può approvare, neppure su richiesta. Non selezionare approvatori
inventati o trasferiti da Marketing: utilizzare il processo concordato.

## Integrazione esistente consultata, senza modifiche

Riferimenti nel workspace fratello Marketing EFS:

- `docs/maintenance/operations-teams-runbook.md`: servizio Operations con connettore
  Teams esistente e Codex app-server; controlli di identità e chat, deduplicazione,
  gestione degli esiti incerti e readback.
- `scripts/operations/agents.json`: lettura del 15/10/2026; contiene Marketing ed ERP,
  nessuna voce Virgilio.
- `scripts/operations/teams_service.py` e `coordinator.md`: componenti del trasporto
  e del routing; non modificati durante questa consultazione.

L'integrazione Marketing risponde a un ambito più ampio e non soddisfa da sola il
filtro di Virgilio. La disponibilità dei connettori in questa chat non attesta
l'attivazione della menzione o di un nuovo agente. Il presente documento conserva
i requisiti; nessun servizio è stato avviato, riavviato o riconfigurato.

La documentazione ufficiale [Codex app-server](https://learn.chatgpt.com/docs/app-server)
è stata consultata come riferimento tecnico; lo stato della vostra installazione
è ricavato dai file locali, non dalla documentazione pubblica.
