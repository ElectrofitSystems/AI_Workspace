# Stato di validazione v0.1

Data: 2 ottobre 2026.

## Verificato sul prototipo di origine

- trigger Power Automate su messaggi Teams reali;
- filtro tra conversazioni interne ed esterne/miste;
- deduplicazione persistente tramite registro univoco;
- trasferimento OneDrive di soli identificativi;
- watcher locale e bridge MCP Events;
- risveglio del task ChatGPT senza refresh;
- lettura del messaggio con Teams e due risposte automatiche semplici;
- pausa e ripresa del task;
- kill switch e claim persistente.

## Verificato sul pacchetto distribuibile

- manifest JSON validi;
- sintassi di tutti gli script PowerShell;
- compilazione dei moduli Python;
- quattro test unitari del bridge: stato/skill, consegna pseudonimizzata, kill switch/claim singolo e rifiuto del corpo messaggio;
- installazione in un progetto temporaneo con creazione di `.sources/My Avatar` e della coda OneDrive simulata;
- scansione negativa per nomi personali, identificativi reali e percorsi utente incorporati.

## Da verificare per ogni nuova installazione

- disponibilità e autorizzazione dei connettori Microsoft/OpenAI;
- endpoint tunnel e callback MCP;
- ritardo effettivo del trigger Teams;
- regole specifiche di tenant e dominio;
- invio Teams consentito dalle policy del workspace;
- accessibilità dell'eventuale agente coordinatore;
- comportamento su chat di gruppo e account esterni reali.

## Escluso

Il listener delle notifiche Windows sperimentale non è incluso perché non ha dimostrato una ricezione Teams affidabile.
