# ERP EFS

Progetto ERP Electrofit Systems, avviato il 5 ottobre 2026.
Workspace canonico: `C:/Users/Operations/Documents/AI_Workspace/Business Operations/ERP EFS`.

Il primo servizio consulta lo scadenzario fornitori di eSolver e risponde alle
domande sulle fatture da pagare nella chat individuale con Operations.
Utente finanziario autorizzato dall'utente: Francesco Lucherini.

- [Mandato e regole](docs/rules.md)
- [Accessi e integrazione Teams](docs/integration.md)
- [Acquisizione dello scadenzario](docs/esolver.md)
- [Verifica API, Reporter e schedulatore](docs/connectivity-verification.md)
- [Stato e prossima verifica](docs/status.md)
- `config/access.json`: identità autorizzate, verificate in Entra tramite Teams.
- `.codex/agents/agente-ERP-EFS.toml`: definizione dell'Agente ERP EFS.
- `input/esolver/`: esportazioni originali datate, da conservare.
- `output/payables/`: risultati locali della consultazione.
- `.local/`: dati del pilota e temporanei di manutenzione.

Gli archivi Marketing e le autorizzazioni SharePoint Marketing non si applicano
alle fatture. Nessuna destinazione cloud ERP è stata ancora scelta.

Pilota: sessione RDP e consultazione eSolver verificate, prima esportazione
acquisita e quadrata, Agente ERP EFS configurato e controllo nominativo Teams.
Per usarlo, Francesco può scrivere nella chat individuale con Operations:
"ERP, quali fatture risultano da pagare?" oppure "Dettaglio delle scadenze CBM".
Il pilota usa un'esportazione datata; l'aggiornamento automatico ERP deve
ancora essere configurato. Collaudi effettivi e limiti in docs/status.md.
