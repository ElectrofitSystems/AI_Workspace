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

Gli [strumenti LinkedIn](scripts/linkedin/README.md) sono in `scripts/linkedin/`;
il generatore delle brochure è in `scripts/brochures/`.

Fonti e output sono esclusi da Git e non vengono caricati automaticamente su
SharePoint. Le fonti autorizzate sono documentate in `docs/company/sources.md`.

## Manutenzione locale

Temporanei e verifiche sono in `.local/maintenance/`. I residui della precedente
pulizia bloccata sono conservati in `.local/maintenance/cleanup-pending/`.
Lo script `scripts/maintenance/cleanup_obsolete.ps1` agisce soltanto su quella
cartella quando eseguito manualmente. La riorganizzazione non esegue cancellazioni.
