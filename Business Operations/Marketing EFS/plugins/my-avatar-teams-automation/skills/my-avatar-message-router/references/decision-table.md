# Tabella decisionale

| Esito | Condizioni | Azione |
|---|---|---|
| `IGNORE` | messaggio del proprietario, bot, sistema, eliminato o duplicato | nessuna azione |
| `AUTO_REPLY` | chat verificata; richiesta semplice, certa e a basso rischio | una risposta breve |
| `ESCALATE` | ambiguità, dati sensibili, impegni, partecipanti non consentiti, strumenti mancanti | avviso al proprietario |
| `COORDINATE` | richiesta valida ma richiede un'automazione più ampia e il coordinatore è configurato | passa un riferimento minimo al coordinatore |

L'instradamento non sostituisce la policy dell'installazione.
