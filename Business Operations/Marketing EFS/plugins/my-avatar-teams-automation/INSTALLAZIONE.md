# Installazione guidata — v0.1

## 1. Prerequisiti

- Windows 10/11;
- Python 3.11+ disponibile come `python` o percorso esplicito;
- OneDrive aziendale sincronizzato;
- accesso a Power Automate nello stesso ambiente Microsoft 365 di Teams;
- connettori Microsoft Teams, OneDrive for Business e, se usato, SharePoint;
- ChatGPT Work/Codex con plugin, Teams e MCP Events disponibili;
- un endpoint HTTPS raggiungibile da ChatGPT per il bridge locale.

Non inserire password, token o chiavi nei file JSON/Markdown del progetto.

## 2. Installare i file nel progetto

Aprire PowerShell nella cartella del plugin ed eseguire:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\Install-MyAvatar.ps1 -TargetProject "C:\percorso\del\progetto"
```

La modifica della execution policy vale soltanto per la finestra corrente. Lo script crea `<progetto>/.sources/My Avatar` senza sovrascrivere una configurazione esistente, salvo uso esplicito di `-Force`.

## 3. Configurare identità e policy

Aprire:

```text
<progetto>/.sources/My Avatar/config/settings.json
<progetto>/.sources/My Avatar/config/FILTER-POLICY.md
```

Compilare almeno:

- `owner.email` e `owner.userId`;
- `organization.tenantId`, `organization.allowedDomains`;
- `organization.maxParticipants` (predefinito: 3, proprietario compreso);
- `oneDrive.queueRoot` oppure lasciare `auto`;
- `coordinator.enabled` e `coordinator.threadId` solo se esiste un agente coordinatore.

Gli ID non sono password. Non inserire comunque dati non necessari.

## 4. Creare le cartelle OneDrive

Lo script di installazione prova a individuare OneDrive e crea:

```text
OneDrive - <Azienda>/My Avatar/MCP Events/Incoming
OneDrive - <Azienda>/My Avatar/MCP Events/Processed
OneDrive - <Azienda>/My Avatar/MCP Events/Rejected
```

Se OneDrive non è rilevato, creare manualmente le cartelle e impostare `oneDrive.queueRoot` in `settings.json`.

## 5. Creare il flusso Power Automate

Seguire [docs/POWER-AUTOMATE.md](docs/POWER-AUTOMATE.md). Il flusso deve scrivere nella cartella `Incoming` un JSON con esattamente:

```json
{"conversationId":"<id-chat>","messageId":"<id-messaggio>"}
```

Non inserire il testo del messaggio nel file OneDrive.

## 6. Salvare i segreti locali

Generare due token casuali distinti di almeno 32 caratteri e salvarli protetti per l'utente Windows:

```powershell
.\scripts\Save-MyAvatarSecrets.ps1 -InstallRoot "C:\percorso\del\progetto\.sources\My Avatar"
```

Lo script chiede i valori in modo interattivo e usa DPAPI. Non crea file di testo con le chiavi.

## 7. Avviare bridge e watcher

```powershell
& "C:\percorso\del\progetto\.sources\My Avatar\scripts\Start-MyAvatar.ps1"
```

Controllare:

```powershell
& "C:\percorso\del\progetto\.sources\My Avatar\scripts\Status-MyAvatar.ps1"
```

## 8. Pubblicare il bridge tramite HTTPS

Configurare il proprio tunnel HTTPS verso `http://127.0.0.1:8766`. Non condividere la chiave del tunnel e non commetterla nel repository.

Registrare in ChatGPT Developer Mode il server MCP usando:

- URL: `https://<endpoint>/mcp`;
- autenticazione bearer: il token MCP salvato al punto 6;
- callback host consentito: `connectors.api.openai.com`, salvo indicazione diversa mostrata dall'interfaccia ufficiale.

Ogni organizzazione deve creare la propria connessione. Il pacchetto non contiene un `plugin_asdk_app` preconfigurato.

## 9. Collegare plugin e account

Installare/importare il plugin dalla cartella o dal relativo ZIP. Collegare i plugin/app Microsoft Teams e SharePoint/OneDrive usando l'account scelto. L'installazione non concede automaticamente permessi.

## 10. Creare il task ChatGPT

Creare una nuova chat operativa nel progetto e un task basato sull'evento `myavatar.message.ready`. Copiare le istruzioni da [docs/TASK-PROMPT.md](docs/TASK-PROMPT.md), sostituendo i segnaposto.

Il task deve rimanere in pausa fino al completamento dei test.

## 11. Test in tre fasi

1. `python runtime/tests/test_bridge.py`: tutti i test devono passare.
2. Inviare un evento sintetico con `scripts/Test-MyAvatar.ps1`; verificare il risveglio senza risposta Teams.
3. Attivare il task e provare un messaggio reale semplice da un collega interno autorizzato.

Verificare che:

- venga prodotta una sola risposta;
- esterni, ospiti e chat sopra il limite siano bloccati;
- un messaggio ambiguo venga segnalato al proprietario;
- disabilitando il kill switch non partano risposte.

## 12. Attivazione e arresto

Attivare le risposte creando il file vuoto:

```text
<progetto>/.sources/My Avatar/config/auto-reply.enabled
```

Per sospendere immediatamente le risposte, eliminare o rinominare quel file e mettere in pausa il task ChatGPT. Per fermare anche la ricezione, disattivare il flusso Power Automate.
