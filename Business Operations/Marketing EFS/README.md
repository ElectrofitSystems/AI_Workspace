# Marketing EFS

Agente dedicato al marketing B2B tecnico di ElectroFit Systems, in italiano e
inglese. Produce contenuti, materiali commerciali, ricerca e report sulla base
delle fonti e delle decisioni aziendali.

La chat **MASTER — Marketing EFS** raccoglie richieste, priorità e decisioni.
Le chat operative conservano i propri lavori; il
[registro Master](output/Statistics/coordination/master-register.json) collega
stato e risultati secondo il [coordinamento](docs/maintenance/master-coordination.md).

## Flusso di lavoro

1. Recuperare le fonti da SharePoint
   [Marketing/Inputs](https://efitsys.sharepoint.com/sites/Documentation/Shared%20Documents/General/Marketing/Inputs),
   seguendo i collegamenti ai documenti originali.
2. Verificare approvazione, revisione e ambito degli input prima del riuso.
3. Produrre e verificare i materiali, conservandone le versioni locali.
4. Consegnare in
   [Marketing/Outputs](https://efitsys.sharepoint.com/sites/Documentation/Shared%20Documents/General/Marketing/Outputs)
   soltanto i file leggibili e necessari, nella categoria esistente.
5. Per materiali editoriali e commerciali, avviare la review Microsoft del
   pacchetto completo. Pubblicare o inviare la revisione approvata quando
   l’esecuzione è autorizzata.

I nuovi file e collegamenti in Inputs avviano il flusso di revisione configurato.
I report informativi, come Statistics, vengono consegnati senza una richiesta
di approvazione automatica. Note interne, sorgenti e verifiche restano locali.
Procedure: [input](docs/company/marketing-input-folder.md),
[consegna](docs/company/output-delivery.md),
[approvazioni](docs/maintenance/teams-approvals.md).

## Attività e ricorrenze

| Attività | Cadenza, Europe/Rome |
| --- | --- |
| Inbox, commenti, engagement e approvazioni LinkedIn | Lun–ven, 11:00 |
| Un post bilingue, prospecting, performance e segnali di opportunità | Lunedì, 09:00 ogni 14 giorni dal 05/10/2026 |
| Preparazione newsletter della Pagina LinkedIn EFS | Primo lunedì del mese, 10:00 |
| Recap marketing in Statistics e nella Master | Primo lunedì del mese, 12:00 dal 02/11/2026 |

Le ricorrenze riprendono le revisioni pendenti e riutilizzano le analisi già
disponibili. Procedure: [LinkedIn](docs/linkedin/scheduling.md),
[newsletter](docs/newsletter/workflow.md),
[statistiche](docs/marketing-statistics.md).
La pubblicazione automatica LinkedIn tramite API resta da completare.

Cataloghi, brochure, presentazioni, white paper, audit della Pagina,
intelligence di settore e supporto commerciale sono disponibili su richiesta.

## Documenti e cartelle

Leggere [regole](docs/rules.md), [mandato](docs/company/mandate.md),
[contesto aziendale](docs/company/context.md) e
[fonti](docs/company/sources.md). Per grafica e template vale il
[kit corrente verificato](docs/company/brand.md).

| Cartella | Uso |
| --- | --- |
| `docs/` | Conoscenza aziendale e procedure |
| `scripts/` | Strumenti del progetto |
| `input/` | Originali, brand e media |
| `output/Documentation/` | Brochures, Catalogues e Whitepapers |
| `output/Linkedin/` | Contenuti e registri LinkedIn |
| `output/Newsletter/` | Newsletter e review |
| `output/Statistics/` | Report, dati e coordinamento |
| `.local/maintenance/temporary/` | Temporanei e verifiche |

Originali, master, revisioni e prove restano conservati. Non riorganizzare gli
archivi condivisi. `input/`, `output/` e `.local/` sono esclusi da Git e devono
essere recuperati dalla copia operativa su un nuovo host; accessi e installazioni
vanno verificati nell’ambiente effettivo. Per vecchi percorsi consultare la
[mappa di migrazione](docs/maintenance/paths.json).
