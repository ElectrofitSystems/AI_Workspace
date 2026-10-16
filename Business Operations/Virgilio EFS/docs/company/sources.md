# Fonti e destinazioni — Virgilio EFS

Aggiornamento: **15 ottobre 2026**.

## Riferimenti verificati localmente

| Riferimento | Uso e perimetro |
| --- | --- |
| `../Marketing EFS/README.md` | Modello organizzativo del workspace |
| `../Marketing EFS/AGENTS.md` | Modello delle istruzioni persistenti |
| `../Marketing EFS/docs/rules.md` | Regole di struttura e conservazione |
| `../Marketing EFS/docs/company/context.md` | Modello del contesto persistente |
| `../Marketing EFS/docs/company/sources.md` | Modello del registro delle fonti |
| `../Marketing EFS/.gitignore` | Regole copiate senza modifiche |
| Repository `https://github.com/ElectrofitSystems/AI_Workspace.git` | Remote origin già configurato nella radice AI_Workspace |

I percorsi della tabella sono relativi alla radice del workspace Virgilio EFS.
La lettura è stata effettuata il 15/10/2026. Marketing EFS resta proprietario
dei suoi materiali e delle sue configurazioni.

## SharePoint e Teams

**Perimetro indicato dall'utente:** Engineering - Powertrain; processo Test Request
indicato in General. Consultazione in lettura effettuata il 15/10/2026 tramite
connettori Teams e SharePoint già disponibili. Nessuna destinazione output:
Virgilio risponde nella chat, senza produrre file di consegna.

### Identità verificate

- Tenant: `3b97374b-4a43-4588-a04f-4c94edc33cf3`.
- Team Engineering - Powertrain: `f11b679f-d834-4b98-9a1c-3e0dab6b5c7c`.
- Canale General: `19:iPew49Xkmu5o7a0wx0FjdhAEgPA73KBveY1Bo8ciaOk1@thread.tacv2`.
- [Sito Engineering - Powertrain](https://efitsys.sharepoint.com/sites/Engineering).
- Site ID: `efitsys.sharepoint.com,f8b69e5d-7509-4b63-81df-a1ed1ac1d149,7c187dbe-5318-4962-9011-1bbd0cf67b1d`.
- Libreria Documents: `b!XZ62-Al1Y0uB36HtGsHRSb59GHwYU2JJkBEbvQz2ex3pFKVDJpFYR5ODz_gNJptd`.
- [Lista Test Requests](https://efitsys.sharepoint.com/sites/Engineering/Lists/Test%20Requests):
  `024b96a8-b63b-41e9-8fb7-66e96aaee301`. Esistenza verificata; schema dei campi,
  Power App e comportamento del flusso non verificati.

### Struttura osservata

Canali Teams: General, Components, Testing, Suppliers, Customers, Products,
xCU Platforms e Management (privato). L'accesso ai contenuti del canale privato
non è stato verificato né richiesto.

Cartelle nella libreria Documents: Components, Customers, General, Products,
Suppliers, Testing e xCU Platforms. Presente anche `nvm.png` in radice.
Non dedurre da questo inventario la collocazione dei file di Management.

| Percorso verificato | Contenuto utile alla guida |
| --- | --- |
| [General](https://efitsys.sharepoint.com/sites/Engineering/Shared%20Documents/General) | Methodology, Planning Calendar, Workstations |
| [General/Methodology](https://efitsys.sharepoint.com/sites/Engineering/Shared%20Documents/General/Methodology) | Teams Organization; Git Tutorial.docx; xCU Development Process.docx |
| [Components](https://efitsys.sharepoint.com/sites/Engineering/Shared%20Documents/Components) | Auxiliary, Cable Harness, Energy System, General, Power System, Standard Parts, Vehicle Management System |
| [Testing](https://efitsys.sharepoint.com/sites/Engineering/Shared%20Documents/Testing) | Archive, Component Tests, General, Integration Tests, Product Tests, Production Tests |
| [Testing/General](https://efitsys.sharepoint.com/sites/Engineering/Shared%20Documents/Testing/General) | Documentation, Management, Test Framework |
| [Testing/General/Management](https://efitsys.sharepoint.com/sites/Engineering/Shared%20Documents/Testing/General/Management) | Test Activities.xlsx, Test Configurations.xlsx, Test Runs.xlsx e tre registri/proposte Testing_register |
| [Testing/General/Test Framework](https://efitsys.sharepoint.com/sites/Engineering/Shared%20Documents/Testing/General/Test%20Framework) | Manuals, Test Definitions, Test Procedures, Test Templates, Tools and Scripts; guida e registro di qualifica |

### Fonti effettivamente lette

- [Testing Traceability Guide.txt](https://efitsys.sharepoint.com/sites/Engineering/Shared%20Documents/Testing/General/Test%20Framework/Testing%20Traceability%20Guide.txt):
  versione documentale 1.0 del 14/10/2026, DriveItem `01TPBIPNH7TD5Y3VXZEVBLXYBJGJDU2TEM`.
  Distingue TACT (definizione), TCFG (configurazione prevista) e TRUN (esecuzione).
  Non richiede cartelle per questi ID. Descrive un'applicazione futura; non prova
  che l'attuale Test Request sia realizzata. I record storici citati restano da
  qualificare, senza identificativi ufficiali inventati o approvazioni dedotte.
- [Organizzazione Teams.pdf](https://efitsys.sharepoint.com/sites/Engineering/Shared%20Documents/General/Methodology/Teams%20Organization/Organizzazione%20Teams.pdf):
  documento del 28/11/2025, DriveItem `01TPBIPNB35LSQ33QYOBD3UBDB3GCD5RU2`.
  Riferimento storico di organizzazione/versionamento tecnico; non sostituisce
  la struttura corrente osservata o i requisiti della futura app.

Le liste di cartelle consultate hanno restituito `next_link: null` per il singolo
livello. Non è stato letto ogni documento o sottoalbero. Letti fino a 100 messaggi
di General per ricerca; nessuna cronologia copiata localmente. La definizione
specifica della Test Request indicata dall'utente non è stata individuata nella
copertura dei messaggi e documenti esaminati. Non ricostruirla da fonti generiche:
approfondirla più avanti come richiesto.

Quando disponibili, registrare per ciascuna fonte:

- Nome del team e canale oppure sito e libreria.
- URL esatto e, se restituiti dal connettore, ID stabili di sito/drive/cartella.
- Percorso nella libreria e relazione con la vista File di Teams.
- Uso previsto, responsabile, accesso verificato e data di verifica.
- Per i file: versione o eTag, data di modifica e ambito di utilizzo.
- Destinazione concordata e operazioni richieste per i risultati.

Usare il [modello di mappa](templates/source-map.md) solo come supporto interno;
la guida agli ingegneri viene resa nella chat, senza file di output.
Non trasferire qui le destinazioni Marketing/Inputs e Marketing/Outputs come
destinazioni di Virgilio senza una decisione dell'utente.
