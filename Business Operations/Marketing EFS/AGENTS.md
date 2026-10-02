# Marketing EFS — istruzioni per gli assistenti

Leggi README.md, poi docs/rules.md e i documenti pertinenti al compito.
Il contesto aziendale condiviso è docs/company/context.md.
Le regole e le procedure in docs/ valgono per qualsiasi LLM; le skill disponibili sono strumenti facoltativi.
Salva i risultati in output/ e i temporanei in output/_temp/. Conserva gli originali in input/.
Per istruzioni o registri storici con vecchi percorsi, consulta docs/maintenance/paths.json; usa sempre le nuove destinazioni e non ricreare le vecchie cartelle.
Le autorizzazioni esistenti rimangono limitate ai rispettivi ambiti: la riorganizzazione non autorizza nuovi invii o pubblicazioni.

## Adattatore Codex

La definizione dedicata è .codex/agents/agente-marketing-EFS.toml, nome esatto “Agente marketing EFS”.
Quando l’utente chiede questo agente, delega alla definizione personalizzata se il runtime la espone; se manca, comunica il limite senza sostituirla silenziosamente. L’agente specializzato non deve delegare a se stesso.
