# My Avatar Teams Automation — v0.1

Prototipo Windows per ricevere eventi da Microsoft Teams, filtrarli in Power Automate, trasferire soltanto riferimenti minimi tramite OneDrive e risvegliare un task ChatGPT con MCP Events.

La versione `0.1.0` è sperimentale e non è adatta a processi critici. Il trigger Teams può arrivare in ritardo e le funzioni disponibili dipendono dal piano Microsoft/OpenAI, dalle policy dell'organizzazione e dai permessi concessi dall'utente.

## Contenuto verificato

- ricezione dei messaggi Teams tramite Power Automate;
- filtro preventivo di mittente, tenant, dominio, ospiti e dimensione della chat;
- coda OneDrive con soli `conversationId` e `messageId`;
- watcher locale e bridge MCP Events;
- deduplicazione persistente e kill switch;
- risveglio di un task ChatGPT senza refresh della pagina;
- lettura del messaggio con il connettore Teams e risposta automatica limitata;
- skill con policy modificabile;
- policy modulare, deduplicazione e kill switch.

L'instradamento a un agente coordinatore è incluso come integrazione opzionale, ma deve essere verificato nel progetto destinatario perché dipende dagli strumenti e dai permessi disponibili a quell'agente.

Non sono inclusi il listener delle notifiche Windows, i flussi diagnostici, screenshot, log di prova, identificativi personali, tenant, flow ID, URL di tunnel, token o credenziali.

## Installazione

Seguire [INSTALLAZIONE.md](INSTALLAZIONE.md). L'installazione crea nel progetto destinatario:

```text
<progetto>/.sources/My Avatar/
├── config/
├── data/
├── logs/
├── queue/
├── runtime/
└── scripts/
```

Il plugin non salva password. Le connessioni Microsoft e OpenAI vengono autorizzate direttamente nei rispettivi servizi; gli eventuali segreti locali vengono protetti per l'utente Windows corrente.

## Arresto rapido

1. rimuovere o rinominare `.sources/My Avatar/config/auto-reply.enabled`;
2. mettere in pausa il task ChatGPT;
3. per fermare anche la raccolta, disattivare il flusso Power Automate.

## Limiti noti v0.1

- Windows e PowerShell 7/Windows PowerShell;
- Python 3.11 o successivo;
- OneDrive sincronizzato localmente;
- Power Automate con connettore Teams disponibile;
- tunnel HTTPS e registrazione MCP configurati per ogni installazione;
- nessuna garanzia di consegna immediata del trigger Teams;
- la chat con sé stessi può non essere leggibile dal connettore Teams;
- un plugin locale non concede automaticamente accesso a Teams, SharePoint, OneDrive o account OpenAI.
- il passaggio a un agente coordinatore non è garantito finché il relativo thread e lo strumento di messaggistica non sono stati verificati.

## Documentazione OpenAI

Il pacchetto segue il formato portabile dei plugin e la separazione tra skill e server MCP descritta nella documentazione OpenAI:

- https://developers.openai.com/plugins/build/plugins
- https://developers.openai.com/plugins/concepts/skills
- https://developers.openai.com/plugins/build/mcp-server
