# Collegamento del plugin al server MCP

La v0.1 non incorpora un ID di connessione MCP: quell'ID appartiene all'account e al workspace dell'installatore e non è portabile tra aziende.

## ChatGPT Work

1. Avviare il bridge e il tunnel HTTPS.
2. In ChatGPT sul web abilitare Developer Mode, se disponibile e consentito dall'amministratore.
3. Registrare l'endpoint `https://<host>/mcp` con il token MCP dell'installazione.
4. Copiare l'identificativo tecnico `plugin_asdk_app...` creato da ChatGPT.
5. Collegare quell'app al plugin usando Plugin Creator oppure aggiungere una `.app.json` locale conforme alle funzioni disponibili nel workspace.
6. Installare il plugin e collegare separatamente Teams e SharePoint/OneDrive.

## Codex locale

Il plugin può essere aggiunto a un marketplace di repository collocandolo in `plugins/my-avatar-teams-automation` e registrandolo in `.agents/plugins/marketplace.json`. Il server MCP può essere abilitato separatamente nella configurazione Codex o tramite la connessione registrata.

Non copiare `.app.json` da un'altra azienda: potrebbe puntare a un account, server o autorizzazione non appartenente al destinatario.
