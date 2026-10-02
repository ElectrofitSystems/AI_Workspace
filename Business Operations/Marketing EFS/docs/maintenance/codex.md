# Adattatore Codex

Il progetto funziona attraverso README.md e docs/rules.md. Le skill installate sono supporti facoltativi, non il deposito del contesto aziendale.

L’agente dedicato è `.codex/agents/agente-marketing-EFS.toml`, nome esatto **Agente marketing EFS**. Mantenerne il mandato e usare la definizione personalizzata quando richiesta e disponibile.

Dal 02/10/2026 è salvata anche la definizione personale `C:/Users/Operations/.codex/agents/agente-marketing-EFS.toml`, con le istruzioni globali condizionali in `C:/Users/Operations/.codex/AGENTS.md`. Servono per richiamare l'agente da nuove chat anche esterne al progetto su questo computer. Entrambi rimandano al workspace canonico e ai documenti correnti, senza copiare l'intera conoscenza aziendale o bloccare una vecchia versione del kit. Le nuove sessioni devono caricare la configurazione aggiornata; l'accesso a questo workspace da altri computer/host non è implicito.

Fonti permanenti: SharePoint Marketing/Inputs; consegna risultati: Marketing/Outputs, categorie esistenti. Link e autorizzazioni in `docs/company/sources.md`. La richiesta breve «Rifai il catalogo prodotti col nuovo design kit che trovi nell'input al link che ti ho passato» usa quelle destinazioni senza richiedere nuovamente i link. Documentazione di configurazione: https://learn.chatgpt.com/docs/agent-configuration/subagents e https://learn.chatgpt.com/docs/agent-configuration/agents-md.

Il plugin locale `efs-linkedin-publisher` usa il server in `scripts/linkedin/publisher/mcp_server.py`. Lo stato e il database sono in `output/Linkedin/publisher/`, esclusi da Git. Il live rimane disabilitato. La configurazione del plugin installato viene aggiornata dal suo source locale e ricaricata con il flusso supportato.
