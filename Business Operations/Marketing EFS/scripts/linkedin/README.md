# Strumenti LinkedIn

Tutti gli strumenti LinkedIn del progetto sono raccolti qui. Le procedure e i
modelli sono in `docs/linkedin/`; risultati e registri sono in `output/Linkedin/`.

| Funzione | Procedura | Strumento o registro |
| --- | --- | --- |
| Preparare post e pacchetti bilingui | `docs/linkedin/editorial.md` | `output/Linkedin/posts/` |
| Verificare/esportare anteprime | Procedura editoriale | `previews/check_preview.cjs`, `previews/export_review.cjs` |
| Leggere la coda e validare bozze | Procedura editoriale | `publisher/publisher.py`, `publisher/mcp_server.py` |
| Commenti sui nostri post | `docs/linkedin/comments.md` | `output/Linkedin/comments/` |
| Inbox privata | `docs/linkedin/inbox.md` | `output/Linkedin/inbox/` |
| Engagement sui post altrui | `docs/linkedin/engagement.md` | `output/Linkedin/engagement/` |
| Prospect e follow autorizzati | `docs/linkedin/prospecting.md` | `output/Linkedin/prospecting/` |
| Misurazione e segnali commerciali | `docs/linkedin/measurement-and-sales.md` | `output/Statistics/Linkedin/`, `output/Linkedin/sales/` |

Il publisher gestisce soltanto la coda dei post originali. Non offre strumenti
per inbox, commenti, follow o analytics: questi flussi usano gli accessi verificati
disponibili nell'ambiente e mantengono registri distinti.

Il database del publisher è `output/Linkedin/publisher/publisher.sqlite3`, con
impostazioni e media nello stesso dossier. Le credenziali non fanno parte di Git.
Pubblicazione live disabilitata; approvazione autenticata e richiesta di esecuzione
restano requisiti separati.

I media di riferimento sono in `input/Media/Pictures/`; il publisher conserva
le proprie copie gestite in `output/Linkedin/publisher/media/`.

I programmi Python usano un interprete già disponibile. Le anteprime JavaScript
usano Node.js e Playwright disponibili nel runtime dell'ambiente. Non installare
dipendenze automaticamente. Gli strumenti per anteprime non inviano messaggi.

Dalla radice del progetto:

```text
python scripts/linkedin/publisher/publisher.py status
python scripts/linkedin/publisher/publisher.py list
python scripts/linkedin/publisher/publisher.py dry-run EFS-001
python scripts/linkedin/publisher/mcp_server.py
node scripts/linkedin/previews/check_preview.cjs --verify-only
node scripts/linkedin/previews/export_review.cjs
```

La verifica con `--verify-only` conserva le anteprime. L'esportazione crea un
nuovo pacchetto locale sotto `output/Linkedin/posts/reviews/`.

Il plugin locale `efs-linkedin-publisher` versione 0.1.6 punta al server in questa
cartella. Le chat che avevano già caricato il vecchio processo devono ricaricare
il plugin prima di usare nuovamente i suoi strumenti.
