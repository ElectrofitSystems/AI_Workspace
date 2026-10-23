# Diagnostica runtime Marketing — 21 ottobre 2026

Esito del collaudo in questa sessione: `attention_required`.
Il dato ricevuto è `custom_agent_runtime_unverified`; nessuna riparazione
del ruolo è stata verificata. Non sono stati modificati sorgenti Operations
o definizioni Marketing: il confronto eseguito non dimostra un'incompatibilità.

## Verifiche ed evidenze

- CLI installata selezionata dal resolver esistente:
  `C:/Users/Operations/AppData/Local/OpenAI/Codex/bin/896a0166b774037a/codex.exe`,
  versione `0.163.0-alpha.10.2`, con helper Windows presente.
- Generato lo schema locale con
  `app-server generate-json-schema --experimental --out <temporanei>`.
  I campi usati dal client esistente sono ancora presenti:
  `collabAgentToolCall`, `spawnAgent`, `receiverThreadIds`,
  `subAgentActivity.agentThreadId`, `Thread.agentRole`,
  `ThreadReadParams.includeTurns` e `ThreadStartParams.ephemeral`.
  Il possibile problema nella lettura degli eventi non è confermato dal confronto.
- Entrambe le definizioni Marketing sono TOML validi, con nome esatto
  `Agente marketing EFS`, descrizione e istruzioni. Nessuna imposta il modello.
  Le due definizioni hanno contenuti distinti; non sono state sincronizzate.
- Suite esistente: **84 test superati**, uscita 0, in 1,281 secondi:
  `python -B -m unittest discover -s scripts/operations -p test_*.py`.
- Backup di **25 file**: file Operations e due definizioni Marketing.
  Verificati SHA-256 delle copie e identità dei sorgenti dopo la diagnostica.

Prove, schema e manifest:
`.local/maintenance/temporary/marketing-maintenance/runtime-20261021/`.
`backup-manifest.json` elenca copie e hash; `diagnosis.json` conserva l'esito;
`cli-initialize.txt` registra l'errore reale; `tests-baseline.txt` riporta
l'esito osservato della suite. Gli archivi precedenti restano conservati.

## Limite riprodotto

Un nuovo processo `app-server --stdio`, con la sola richiesta `initialize`,
termina con uscita 1, prima di avviare thread o turni del modello:

```text
WARNING: proceeding, even though we could not create PATH aliases: Could not find home directory
Error: Could not find home directory
```

Anche il client Operations rileva la disconnessione durante l'inizializzazione.
Questa sessione non espone inoltre strumenti per delegare al ruolo dedicato.
Non è stata quindi eseguita una nuova prova del ruolo con scrittura/rilettura
dell'artefatto e nonce fresco. L'errore osservato non dimostra la causa del
fallimento nel launcher originale e non giustifica modifiche speculative.

Il rapporto locale preesistente `check-20261021T060116.json` riportava una prova
riuscita alle 06:00 locali; è un'evidenza storica, non una verifica attuale.
Lo stato privato del servizio non è stato letto né aggiornato. Questo rapporto
non sostituisce lo stato di produzione.

Nessuna modifica a policy, controlli ERP, approvazioni, brand, autorizzazioni,
modello o schedule. Nessuna lettura diretta di credenziali o conversazioni,
installazione, pubblicazione, messaggio, upload, riavvio del servizio,
riparazione ACL o modifica a home e sandbox.

## Prossimo passo

Ripetere il collaudo esistente dal launcher autorizzato, in un ambiente in cui
`app-server` possa inizializzarsi. La verifica richiede il ruolo esatto e
l'artefatto con nonce nuovo. Conservare l'esito non verificato finché quella
prova non riesce; non modificare login o permessi per superare il limite.

Fonti ufficiali OpenAI:
[Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents)
documenta i campi delle definizioni;
[Codex App Server](https://learn.chatgpt.com/docs/app-server)
documenta la generazione dello schema specifico della CLI installata.
