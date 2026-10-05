# Teams e agente ERP

Account Teams verificato: Operations, operations@efitsys.com,
Entra ID `74ea6b2b-69f5-48dd-95bd-5edb7a4aad38`.
Tenant configurato nel servizio esistente: `3b97374b-4a43-4588-a04f-4c94edc33cf3`.

Il trasporto già attivo si trova nel workspace Marketing EFS:
`scripts/operations/teams_service.py`; registro `scripts/operations/agents.json`;
runbook `docs/maintenance/operations-teams-runbook.md`.
Non installare un secondo listener My Avatar o una seconda coda Teams.

Operations verifica chat oneOnOne, due membri, identità interne, mittente,
messaggio corrente e destinazione. Ogni collega mantiene un contesto separato.
Il servizio esistente deduplica gli invii e gestisce esiti incerti e arresto.

Il controllo ERP confronta user ID e email verificati con config/access.json
prima di acquisire il dataset e nuovamente prima di inviare dati finanziari.
Il testo del messaggio o il solo nome non possono concedere accesso.

I worker usano il profilo operations_teams: sola lettura, rete dei comandi
disabilitata, Apps/MCP/plugin/browser non disponibili. Il sandbox Windows
consente la lettura di base del filesystem; regole deny esplicite impediscono
di leggere input/, output/ e .local/ ERP, lo stato del trasporto e gli archivi
locali delle conversazioni Codex. Le istruzioni pubbliche restano leggibili.
Il trasporto Python separato legge il dataset solo dopo il controllo nominativo.
Le richieste ERP usano sessioni nuove; gli importi precedenti delle risposte
Operations non vengono reinseriti nel contesto. Prima dell'invio si verificano
nuovamente destinatario, permesso e validità/versione dello snapshot.

Uno snapshot è consultabile soltanto nello stesso giorno della situazione
Europe/Rome e fino a 24 ore dall'acquisizione. Quando è scaduto, la risposta
richiede una nuova esportazione e non riporta vecchi importi come attuali.
L'importazione richiede conteggio e netto osservati nella griglia eSolver;
scripts/payables.py valida lo schema e blocca importi mancanti o dati incoerenti.

Lo specialista ERP eredita il perimetro dell'esecutore Teams: consultazione dei
dati forniti dal trasporto, nessun accesso UI autonomo concorrente a RDP, nessun
connettore di scrittura. L'accesso RDP verificato nella chat desktop serve alla
raccolta iniziale e alle verifiche manuali; non prova un aggiornamento automatico.

Definizione personalizzata secondo la documentazione ufficiale OpenAI:
https://learn.chatgpt.com/docs/agent-configuration/subagents
Trasporto app-server: https://learn.chatgpt.com/docs/app-server
Profili permessi: https://learn.chatgpt.com/docs/permissions

Stato dell'estensione e collaudi effettivi in status.md.

Verifica collegamento ERP del 05/10/2026 in
[connectivity-verification.md](connectivity-verification.md): API REST e
Reporter via web services documentati dal produttore; componenti REST/Reporter
installati e schedulatore attivo. Accesso API alle scadenze fornitori ed export
automatico non ancora collaudati. Nessun nuovo servizio o lavoro configurato.
