# AI workspace

Repository con documentazione, strumenti marketing EFS e servizio Operations Teams.
I percorsi sono relativi a questa cartella: non dipendono dal nome dell'utente Windows.

| Percorso | Funzione e stato |
| --- | --- |
| [Business Operations/Marketing EFS](Business%20Operations/Marketing%20EFS/README.md) | Documenti canonici, procedure, strumenti LinkedIn/brochure e servizio Operations Teams |

## Copia Git e dati locali

`input/`, `output/` e `.local/` di Marketing EFS sono esclusi da Git e possono
mancare in una nuova copia. Fonti, asset, approvazioni, database e configurazioni
operative vanno recuperati dalle destinazioni documentate, non ricreati con dati
dimostrativi. Lo stato dei servizi descritto nei documenti riguarda il PC e la
data delle prove: un clone non installa plugin, non abilita servizi e non dimostra
che le connessioni siano ancora attive.

## Verifiche locali

Dalla radice, con Python 3.11 o successivo già disponibile:

```powershell
python -B -m unittest discover -s "Business Operations/Marketing EFS/scripts/operations" -p "test_*.py"
python -B -m unittest discover -s "Business Operations/Marketing EFS/scripts/linkedin/publisher" -p "test_*.py"
```

Queste suite usano dati temporanei e non avviano il servizio Teams. I test di
protezione delle credenziali richiedono Windows.
Per build e prerequisiti specifici consultare i README dei componenti.
