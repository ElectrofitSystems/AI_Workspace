# Marketing EFS — istruzioni per gli assistenti

Leggi README.md, poi docs/rules.md e i documenti pertinenti al compito.
Il contesto aziendale condiviso è docs/company/context.md.
Coordinamento delle chat: applica docs/maintenance/master-coordination.md e consulta la voce pertinente in output/Statistics/coordination/master-register.json prima di nuovi incarichi. MASTER — Marketing EFS raccoglie richieste e decisioni; le chat operative conservano esecuzione e checkpoint nei propri file. Il registro è mantenuto dalla Master, senza sincronizzazione automatica o nuove schedule.
Regola permanente di consegna: applica docs/company/output-delivery.md. In SharePoint Outputs carica solo i file necessari e direttamente fruibili (catalogo: PDF); Markdown, note interne, sorgenti, configurazioni e verifiche restano locali. Conserva soltanto i file tecnici richiesti dal flusso di approvazione o da un'integrazione concordata. Non cancellare gli archivi esistenti.
Le regole e le procedure in docs/ valgono per qualsiasi LLM; le skill disponibili sono strumenti facoltativi.
Salva i risultati in output/ e i temporanei in .local/maintenance/temporary/. Conserva gli originali in input/.
Per istruzioni o registri storici con vecchi percorsi, consulta docs/maintenance/paths.json; usa sempre le nuove destinazioni e non ricreare le vecchie cartelle.
Le autorizzazioni esistenti rimangono limitate ai rispettivi ambiti: la riorganizzazione non autorizza nuovi invii o pubblicazioni.

Dal 2 ottobre 2026 i nuovi input provengono da SharePoint Documentation / Shared Documents / General / Marketing / Inputs; i risultati vanno caricati in Marketing / Outputs nelle sottocartelle già create. Link esatti, autorizzazione all'archiviazione e perimetro in docs/company/sources.md. Conserva gerarchie, originali e revisioni; non chiedere di ripetere questi link nelle nuove chat.

## Adattatore Codex

La definizione dedicata è .codex/agents/agente-marketing-EFS.toml, nome esatto “Agente marketing EFS”.
Una definizione personale in C:/Users/Operations/.codex/agents/agente-marketing-EFS.toml e le istruzioni C:/Users/Operations/.codex/AGENTS.md rimandano a questo workspace anche per chat esterne al progetto. Il contesto canonico resta nei documenti docs/, senza duplicarlo in skill o archivi di altre chat.
Quando l’utente chiede questo agente, delega alla definizione personalizzata se il runtime la espone; se manca, comunica il limite senza sostituirla silenziosamente. L’agente specializzato non deve delegare a se stesso.
