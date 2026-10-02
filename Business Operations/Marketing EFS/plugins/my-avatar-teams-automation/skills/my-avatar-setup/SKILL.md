---
name: my-avatar-setup
description: Installa, configura, verifica o aggiorna My Avatar Teams Automation in un progetto Windows usando Power Automate, OneDrive e MCP Events. Usala quando l'utente chiede di predisporre o diagnosticare questa automazione; non usarla per elaborare un singolo messaggio Teams.
---

# My Avatar Setup

Guida l'utente senza assumere accessi o permessi. Prima di modificare servizi cloud, identifica il progetto destinatario e usa `<progetto>/.sources/My Avatar` come directory locale.

## Procedura

1. Leggi `../../../INSTALLAZIONE.md` e `../../../docs/ARCHITETTURA.md`.
2. Verifica i prerequisiti senza chiedere password o token in chat.
3. Esegui `scripts/Install-MyAvatar.ps1` con il progetto scelto.
4. Fai compilare `config/settings.json` e `config/FILTER-POLICY.md` con dominio, tenant, proprietario e limite partecipanti dell'organizzazione.
5. Guida la creazione del flusso usando `docs/POWER-AUTOMATE.md`. Non importare ID, connessioni o URL appartenenti a un'altra installazione.
6. Fai salvare i segreti tramite `Save-MyAvatarSecrets.ps1`; non accettare file di testo contenenti credenziali.
7. Collega il server MCP e le app Microsoft solo dopo l'autorizzazione esplicita dell'utente nei rispettivi servizi.
8. Crea una chat operativa nuova e un task inizialmente in pausa usando `docs/TASK-PROMPT.md`.
9. Esegui prima test locali, poi evento sintetico, infine un messaggio reale semplice. Interrompi l'attivazione se un filtro non è verificato.
10. Registra soltanto configurazione non segreta e stato dei test; non salvare corpi dei messaggi, password, token o cookie.

Non promettere affidabilità in tempo reale: nella v0.1 il trigger Teams può essere ritardato.
