# Adattatore Codex

Il progetto funziona attraverso README.md e docs/rules.md. Le skill installate sono supporti facoltativi, non il deposito del contesto aziendale.

L’agente dedicato è `.codex/agents/agente-marketing-EFS.toml`, nome esatto **Agente marketing EFS**. Mantenerne il mandato e usare la definizione personalizzata quando richiesta e disponibile.

Il plugin locale `efs-linkedin-publisher` usa il server in `scripts/linkedin/publisher/mcp_server.py`. Lo stato e il database sono in `output/linkedin/publisher/`, esclusi da Git. Il live rimane disabilitato. La configurazione del plugin installato viene aggiornata dal suo source locale e ricaricata con il flusso supportato.
