# Architettura v0.1

```text
Teams
  │ nuovo messaggio
  ▼
Power Automate
  ├─ deduplica persistente
  ├─ verifica tenant/dominio/ospiti/numero partecipanti
  ├─ ignora proprietario, bot, sistema, eliminati
  └─ scrive solo conversationId + messageId
         │
         ▼
OneDrive / My Avatar / MCP Events / Incoming
         │ sincronizzazione locale
         ▼
watch_onedrive_events.py
         │ riferimento pseudonimizzato
         ▼
bridge.py ── HTTPS tunnel ── MCP Events
         │                       │
         │                       ▼
         │                  task ChatGPT
         │                       │
         └── risoluzione ────────┤
                                 ├─ IGNORE
                                 ├─ AUTO_REPLY → Teams
                                 ├─ ESCALATE → proprietario
                                 └─ COORDINATE → agente coordinatore
```

## Confini di responsabilità

- Power Automate applica i filtri meccanici prima che l'evento raggiunga l'AI.
- OneDrive trasporta soltanto identificativi, non il testo.
- Il bridge gestisce sottoscrizione, firma webhook, pseudonimizzazione, deduplica, claim e kill switch.
- Teams fornisce il contenuto solo dopo il risveglio e solo per il riferimento verificato.
- Le skill applicano la policy e decidono il percorso.
- Il coordinatore è opzionale e non riceve permessi impliciti.

## Persistenza

`data/state.sqlite3` conserva sottoscrizioni cifrate con DPAPI, consegne, riferimenti e claim. `queue/Processed` e `queue/Rejected` contengono i file OneDrive già trattati. Nessun corpo Teams deve essere scritto dal runtime.

## Sicurezza

- endpoint locale vincolato a `127.0.0.1`;
- token MCP e ingress separati;
- segreti del callback cifrati con DPAPI;
- callback HTTPS con allowlist e rifiuto di indirizzi privati;
- kill switch a file;
- un solo claim per evento;
- niente retry ciechi dopo un invio ambiguo.

## Limiti

Power Automate e Teams possono consegnare eventi in ritardo. Il sistema non è una piattaforma real-time e non deve essere usato per emergenze, sicurezza, processi finanziari o comunicazioni che richiedono garanzie di consegna.
