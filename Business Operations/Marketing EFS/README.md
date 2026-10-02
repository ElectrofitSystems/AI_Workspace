# Marketing EFS

Conoscenza, procedure e strumenti di marketing di Electrofit Systems, utilizzabili
con qualsiasi LLM attraverso documenti e formati aperti.

| Cartella | Cosa contiene | Git |
| --- | --- | --- |
| `docs/` | Conoscenza aziendale, procedure e manutenzione | Sì |
| `scripts/` | Programmi utilizzati dal progetto | Sì |
| `input/` | Fonti originali e media di riferimento | No |
| `output/` | Materiali prodotti, report e registri operativi | No |
| `.local/` | Temporanei e registri di manutenzione locali | No |

## Input

```text
input/
├── Brand identity/
├── Technical documentation/
└── Media/
    ├── Pictures/
    └── Videos/
```

`Brand identity` conserva il kit originale: loghi, handbook e master.
`Technical documentation` contiene presentazioni, estrazioni e riferimenti tecnici.
`Media` raccoglie le immagini e i video da riutilizzare nei materiali.

## Output

```text
output/
├── Documentation/
│   ├── Brochures/
│   ├── Catalogues/
│   └── Whitepapers/
├── Linkedin/
├── Newsletter/
└── Statistics/
```

- `Documentation/Brochures/`: brochure applicative, di sottosistema e template corrente.
- `Documentation/Catalogues/`: cataloghi per lingua e formato.
- `Documentation/Whitepapers/`: documenti tecnici prodotti per i clienti.
- `Linkedin/`: post, revisioni, commenti, inbox, engagement, prospect e stato del publisher.
- `Newsletter/`: contenuti e pacchetti di revisione delle newsletter.
- `Statistics/Linkedin/`: report di performance e segnali di opportunità.

Whitepapers, Newsletter e Videos sono pronti per i primi materiali; non sono stati
creati contenuti dimostrativi per riempirli. I registri di consegna e approvazione
conservano le revisioni storiche necessarie per evitare duplicati.

## Documenti e strumenti

Leggere [il contesto aziendale](docs/company/context.md) e la procedura pertinente.
`docs/company/` contiene la conoscenza aziendale; `docs/linkedin/` le procedure e
modelli LinkedIn; `docs/brochures/` le istruzioni dei template; `docs/maintenance/`
la configurazione e la [mappa dei vecchi percorsi](docs/maintenance/paths.json).
La configurazione `.codex/` rimane un adattatore specifico dell'ambiente.

Il collegamento sperimentale My Avatar tra Teams e l'agente Marketing è
documentato in [docs/maintenance/myavatar.md](docs/maintenance/myavatar.md).
Il plugin locale è installato; il bridge originale resta disabilitato.
Il servizio locale Operations usa direttamente il connettore Teams esistente;
configurazione, prove e limiti sono nel
[runbook Operations Teams](docs/maintenance/operations-teams-runbook.md).

Il flusso [Teams Approvazioni per Marketing](docs/maintenance/teams-approvals.md)
è attivo e testato: pacchetto completo in SharePoint Outputs → richiesta nativa
→ ricevuta nella stessa cartella. La pubblicazione automatica LinkedIn resta da
collegare e richiede accesso API operativo.

Gli [strumenti LinkedIn](scripts/linkedin/README.md) sono in `scripts/linkedin/`;
il generatore delle brochure è in `scripts/brochures/`.

Fonti e output sono esclusi da Git. Dal 2 ottobre 2026 usare come origine dei nuovi
input la cartella SharePoint [Marketing/Inputs](https://efitsys.sharepoint.com/sites/Documentation/Shared%20Documents/General/Marketing/Inputs)
e caricare i risultati in [Marketing/Outputs](https://efitsys.sharepoint.com/sites/Documentation/Shared%20Documents/General/Marketing/Outputs),
nelle sottocartelle già create. Conservare la stessa organizzazione delle copie
locali; cataloghi in `output/Documentation/Catalogues/`. Non spostare gli originali
né riorganizzare le cartelle condivise. Destinazioni, perimetro e verifiche di
accesso sono documentati in `docs/company/sources.md`. Non è una sincronizzazione
automatica di tutto il workspace.

## Manutenzione locale

Temporanei e verifiche sono in `.local/maintenance/`. I residui della precedente
pulizia bloccata sono conservati in `.local/maintenance/cleanup-pending/`.
Lo script `scripts/maintenance/cleanup_obsolete.ps1` agisce soltanto su quella
cartella quando eseguito manualmente. La riorganizzazione non esegue cancellazioni.
