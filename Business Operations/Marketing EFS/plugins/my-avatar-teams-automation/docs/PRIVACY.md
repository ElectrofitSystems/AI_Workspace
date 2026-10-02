# Privacy e gestione dei segreti

## Dati che il pacchetto non contiene

- nomi o indirizzi personali;
- tenant ID, user ID, conversation ID, message ID o flow ID reali;
- URL di Power Automate, SharePoint, OneDrive o tunnel;
- API key, token, password, cookie o callback secret;
- corpi di messaggi Teams;
- screenshot, log o database della fase di sviluppo.

## Credenziali

Le credenziali Microsoft e OpenAI vengono gestite dalle schermate ufficiali dei rispettivi servizi. Il runtime non chiede di copiarle nei file del progetto.

I due token locali del bridge vengono acquisiti interattivamente e cifrati con DPAPI per l'utente Windows. Non sono portabili su un altro utente o PC: è intenzionale.

## Log

Il runtime registra solo stato tecnico e non deve scrivere testo dei messaggi. Prima di condividere diagnostica, controllare comunque che non contenga percorsi utente o identificativi dell'organizzazione.

## Disinstallazione

Mettere in pausa il task, disattivare il flusso Power Automate, arrestare i processi e revocare le connessioni nei portali Microsoft/OpenAI. La cancellazione della cartella `.sources/My Avatar` e dei dati cloud è un'operazione separata e deve essere esplicitamente autorizzata dall'utente.
