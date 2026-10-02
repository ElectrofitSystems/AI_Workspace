# AI workspace

Repository con documentazione, strumenti marketing EFS e prototipi Teams.
I percorsi sono relativi a questa cartella: non dipendono dal nome dell'utente Windows.

| Percorso | Funzione e stato |
| --- | --- |
| [Business Operations/Marketing EFS](Business%20Operations/Marketing%20EFS/README.md) | Documenti canonici, procedure, strumenti LinkedIn/brochure e servizio Operations Teams |
| [My Avatar](My%20Avatar/README.md) | Prototipi separati: listener Windows e bridge MCP Events; non è il trasporto del servizio Operations |
| [Plugin My Avatar](Business%20Operations/Marketing%20EFS/plugins/my-avatar-teams-automation/README.md) | Sorgente del pacchetto originale v0.1.0, conservato per installazione e confronto |
| `MyAvatar-Plugin-v0.1.zip` | Archivio originale del plugin; stessi 32 file del pacchetto estratto, inclusi manifest e checksum |

## Copia Git e dati locali

`input/`, `output/` e `.local/` di Marketing EFS sono esclusi da Git e possono
mancare in una nuova copia. Fonti, asset, approvazioni, database e configurazioni
operative vanno recuperati dalle destinazioni documentate, non ricreati con dati
dimostrativi. Lo stato dei servizi descritto nei documenti riguarda il PC e la
data delle prove: un clone non installa plugin, non abilita servizi e non dimostra
che le connessioni siano ancora attive.

Il plugin confezionato e il prototipo `My Avatar/src/mcp_events/` sono versioni
diverse: non sostituire l'uno con l'altro. L'archivio ZIP conserva l'originale.
I due eseguibili in `My Avatar/tools/tunnel-client/v0.0.15/` (circa 59,4 MiB)
appartengono al tunnel sperimentale e si conservano insieme a licenze e manifest.

## Verifiche locali

Dalla radice, con Python 3.11 o successivo già disponibile:

```powershell
python -B -m unittest discover -s "Business Operations/Marketing EFS/scripts/operations" -p "test_*.py"
python -B -m unittest discover -s "Business Operations/Marketing EFS/scripts/linkedin/publisher" -p "test_*.py"
python -B -m unittest discover -s "Business Operations/Marketing EFS/plugins/my-avatar-teams-automation/runtime/tests" -p "test_*.py"
python -B -m unittest discover -s "My Avatar/src/mcp_events" -p "test_*.py"
```

Queste suite usano dati temporanei e non avviano il servizio Teams. I test di
protezione delle credenziali richiedono Windows; il bridge prova anche HTTP locale.
Per build e prerequisiti specifici consultare i README dei componenti.
