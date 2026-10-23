# Diagnostica runtime Marketing — 17 ottobre 2026

Esito: `attention_required`. Il dato diagnostico ricevuto è
`custom_agent_runtime_unverified`; la riparazione del ruolo non è verificata.

## Verifiche eseguite

- CLI locale individuata: `codex-cli 0.163.0-alpha.10.2`, distribuzione
  `e78bad9887fa50cf` già installata.
- Generato lo schema sperimentale con
  `codex app-server generate-json-schema --experimental --out <temporanei>`.
  Lo schema conferma `collabAgentToolCall`, `spawnAgent`,
  `receiverThreadIds`, `subAgentActivity.agentThreadId`, `Thread.agentRole`,
  `ThreadReadParams.includeTurns` e `ThreadStartParams.ephemeral`, usati dal
  client esistente. Non emerge una rinomina incompatibile di questi campi.
- Entrambe le definizioni Marketing sono TOML validi con nome esatto
  `Agente marketing EFS`, descrizione e istruzioni. Nessuna imposta il modello.
- Suite esistente: **81 test superati**, uscita 0, con
  `python -B -m unittest discover -s scripts/operations -p test_*.py`.
  I test non dimostrano la disponibilità del ruolo nel servizio effettivo.
- Salvati e verificati tramite SHA-256 i backup di 25 file: gli script
  Operations e le due definizioni Marketing. Nessun sorgente modificato.

## Limite riprodotto

Un nuovo processo locale `app-server --stdio`, con la sola richiesta
`initialize` e senza avviare turni del modello, termina con uscita 1:

```text
WARNING: proceeding, even though we could not create PATH aliases: Could not find home directory
Error: Could not find home directory
```

Questa sessione di manutenzione inoltre non espone uno strumento di delega.
Non è quindi possibile collaudare qui il ruolo esatto e la scrittura/rilettura
di un artefatto con nonce nuovo. L'errore di inizializzazione è un limite
osservato nell'ambiente corrente; non prova la causa del controllo fallito
nel launcher originale. Nessuna modifica a home, sandbox o login è stata
tentata per superarlo.

Nessuna modifica a policy, controlli ERP, approvazioni, brand, autorizzazioni,
modelli o schedule. Nessuna installazione, pubblicazione, messaggio,
riavvio del servizio o riparazione ACL. Lo stato privato del servizio non è
stato letto né aggiornato. Questo rapporto non sostituisce il suo stato reale.

## Evidenze e prossimo passo

Prove, schema e manifest dei backup:
`.local/maintenance/temporary/marketing-maintenance/diagnostic-20261017/`.
Il file `diagnosis.json` contiene esiti, percorso esatto del backup e limiti.
`cli-initialize.txt` registra l'errore; `tests-baseline.txt` riporta il risultato
osservato della suite.

Ripetere il collaudo esistente dal launcher autorizzato in un ambiente dove
`app-server` riesce a inizializzarsi. Conservare `attention_required` fino alla
prova reale del ruolo e dell'artefatto con nonce nuovo. Non applicare una
correzione al TOML o al rilevamento degli eventi senza un'incompatibilità
dimostrata.

Fonti ufficiali consultate:
[Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents),
[Codex App Server](https://learn.chatgpt.com/docs/app-server).
La prima documenta i campi obbligatori delle definizioni; la seconda documenta
la generazione dello schema specifico della versione installata.
