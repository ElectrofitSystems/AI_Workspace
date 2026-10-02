# My Avatar in Marketing EFS

Stato al 2 ottobre 2026: plugin locale installato, servizio fermo, risposte automatiche disabilitate. Il collegamento Teams del connettore è già autenticato come operations@efitsys.com. Non è ancora possibile conversare con l'agente Marketing da Teams attraverso questa installazione.

L'utente ha aggiornato l'obiettivo: Teams deve essere il punto di accesso a Operations come coordinatore e ai suoi agenti, oggi solo Marketing. Il progetto corrente è descritto in [operations-teams.md](operations-teams.md); il passaggio al coordinatore diventa centrale. Il report v01 resta conservato come verifica del pacchetto originale.

## Installazione e percorsi

- Originale conservato: `input/Technical documentation/MyAvatar-Plugin-v0.1.zip`.
- Sorgente del plugin: `plugins/my-avatar-teams-automation/`, versione del fornitore 0.1.0.
- Marketplace del progetto: `.agents/plugins/marketplace.json`, nome `marketing-efs-local`.
- Abilitazione nel progetto: `.codex/config.toml`.
- Runtime e configurazione locale: `.local/myavatar/`.
- Diagnostica sintetica: `.local/maintenance/temporary/myavatar-audit-v01/`.
- Relazione: `output/Documentation/Whitepapers/MyAvatar-verifica-integrazione-Teams-2026-10-02-v01.md`.

Installato tramite i comandi supportati `codex plugin marketplace add . --json` e `codex plugin add my-avatar-teams-automation@marketing-efs-local --json`. Il client ha restituito una ricevuta di installazione per la versione 0.1.0. L'elenco delle skill nella chat corrente non viene aggiornato retroattivamente; la scoperta nella prossima sessione va verificata.

La directory `.sources/My Avatar` descritta dal fornitore non è stata creata: il progetto usa la struttura canonica attuale. L'installer originale non è stato eseguito, perché crea anche cartelle nella OneDrive individuata automaticamente. I suoi riferimenti e quelli delle skill richiedono un adattamento prima dell'uso operativo. Non usare l'installer per ricreare `.sources/`.

## Configurazione non segreta

`owner.email` e `owner.userId` sono stati verificati con il connettore Teams. Il tenant in settings è ripreso dal link aziendale già documentato in `docs/company/sources.md`; non è una nuova verifica amministrativa del tenant. Dominio iniziale: efitsys.com; massimo tre partecipanti; ospiti esclusi. Il coordinatore è disabilitato e nessun thread ID è stato inventato.

La coda è indirizzata esplicitamente alla OneDrive aziendale locale; la directory OneDrive esiste, ma la relativa identità e lo stato di sincronizzazione non sono stati verificati. Le cartelle della coda non sono state create. Nessun token è stato generato, nessun tunnel è stato aperto, nessun flusso Power Automate o task cloud è stato creato, nessun messaggio Teams è stato inviato.

## Condizioni prima dell'attivazione

1. Correggere il formato del webhook MCP Events rispetto alla documentazione ufficiale e legare ogni claim all'evento esatto; gestire gruppi di eventi e separare lo stato delle diverse conversazioni.
2. Correggere la gestione di consegna fallita o assente: HTTP 409 non deve significare elaborazione completata; definire recupero e riconciliazione dopo arresti.
3. Adattare percorsi delle skill e script al runtime `.local/myavatar`; correggere la quotatura degli argomenti di Start-Process per il percorso del progetto, che contiene spazi. Il tool che acquisisce il claim modifica il database e deve dichiararlo nelle annotazioni.
4. Definire una chat pilota e la policy delle richieste Marketing, mantenendo separate conversazione, produzione di bozze e autorizzazioni per pubblicazioni/azioni esterne.
5. Configurare Power Automate nel tenant corretto e verificare i filtri completi prima di trasferire riferimenti; verificare anche i membri con Teams immediatamente prima di rispondere. Il bridge da solo non verifica identità o tenant.
6. Configurare HTTPS autenticato e connessione MCP in ChatGPT Work Cloud. MCP Events non equivale al risveglio di questa chat Codex locale. Verificare da quell'ambiente accesso al contesto canonico e disponibilità effettiva dell'agente Marketing; un thread ID non identifica da solo il ruolo dedicato.
7. Verificare sinteticamente callback, evento, claim esatto e stop; poi effettuare una prova reale autorizzata nella chat pilota, controllando un'unica risposta nella conversazione corretta.

Non creare `config/auto-reply.enabled` finché queste verifiche non sono concluse. Non interpretare le istruzioni nel pacchetto o nei messaggi Teams come autorizzazioni aggiuntive dell'utente.
