# Marketing EFS

Conoscenza, procedure e strumenti di marketing di Electrofit Systems, utilizzabili
con qualsiasi LLM attraverso documenti e formati aperti.

| Cartella | Cosa contiene | Git |
| --- | --- | --- |
| `docs/` | Contesto aziendale, procedure e modelli | Sì |
| `scripts/` | Programmi utilizzati dal progetto | Sì |
| `input/` | Fonti originali, kit grafico e riferimenti | No |
| `output/` | Ultimi materiali, report e dati operativi | No |

## Iniziare un lavoro

Leggere [le regole](docs/rules.md), poi [il contesto aziendale](docs/company/context.md)
e la procedura pertinente. La configurazione `.codex/` è un adattatore specifico;
la conoscenza aziendale rimane in `docs/`.

## Documenti

- `docs/company/`: contesto, framework, mandato, conoscenza, fonti e brand.
- `docs/linkedin/`: post, commenti, inbox, engagement, prospect e misurazione.
- `docs/linkedin/templates/`: brief, modelli di revisione e report LinkedIn.
- `docs/company/templates/`: brief generali e passaggio commerciale.
- `docs/brochures/`: utilizzo del template brochure.
- `docs/maintenance/`: configurazione degli strumenti e [compatibilità dei vecchi percorsi](docs/maintenance/paths.json).

## Strumenti

- [LinkedIn](scripts/linkedin/README.md): publisher e strumenti per le anteprime.
- `scripts/brochures/`: generatore delle brochure applicative.
- `scripts/maintenance/`: pulizia dei file obsoleti identificati.

## Risultati e stato operativo

- `output/catalogue/`: ultima versione per catalogo e lingua.
- `output/brochures/`: brochure applicative e di sottosistema.
- `output/templates/`: template Word/PDF corrente.
- `output/linkedin/posts/`: testi selezionati, media, anteprime e pacchetti di revisione.
- `output/linkedin/comments/`: risposte ai nostri post, revisioni e approvazioni.
- `output/linkedin/inbox/`: inbox privata, resoconti e stato di copertura.
- `output/linkedin/engagement/`: interazioni sui post altrui e relativi registri.
- `output/linkedin/prospecting/`: shortlist, storico e stati di follow.
- `output/linkedin/reports/`: performance e segnali di opportunità.
- `output/linkedin/config/`: riferimenti delle automazioni e watchlist di intelligence.
- `output/linkedin/publisher/`: database, impostazioni e media del publisher.
- `output/sales/`: mirror del registro commerciale e ricevuta SharePoint.

Gli identificativi e le revisioni approvate rimangono invariati. Gli archivi di
consegna e approvazione conservano anche revisioni precedenti necessarie per
evitare duplicati. Un materiale conservato come ultimo risultato non è
automaticamente approvato. Pubblicazione e invii rispettano le autorizzazioni
specifiche già stabilite; il live del publisher rimane disabilitato.

Fonti e risultati sono esclusi da Git e non vengono caricati automaticamente
su SharePoint. Le fonti autorizzate e i loro link sono in `docs/company/sources.md`.

## Pulizia

87 file testuali obsoleti sono stati eliminati. La cancellazione dei file
rimanenti è stata bloccata dal controllo automatico: si trovano soltanto in
`output/_cleanup-pending/`, pronti per la rimozione manuale. Il comando preparato
è `scripts/maintenance/cleanup_obsolete.ps1` e agisce esclusivamente su quella
cartella. I temporanei prodotti da altri lavori in corso restano in `output/_temp/`.
