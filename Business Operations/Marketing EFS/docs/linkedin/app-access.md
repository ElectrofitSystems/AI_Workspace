# Accesso LinkedIn e preflight delle ricorrenze

Aggiornamento tecnico del 16 ottobre 2026. Per la riparazione usare l'app Windows
LinkedIn già autenticata, distinta dalla sessione Edge. La Community Management
API in revisione non è un percorso operativo verificato. Non cambiare il live
publisher, token, policy di sicurezza o autorizzazioni persistenti.

## Percorso comune

Leggere la skill Computer Use installata corrente e guidance/API/confirmations
prima delle azioni. Usare esclusivamente `node_repl` con `@oai/sky` per questa
app; non creare client del protocollo helper o usare HTTP, cookie, profili browser,
DevTools o librerie di automazione alternative per superare un rifiuto.

1. Importare `@oai/sky` come nella skill e inventariare le app. L'app osservata è
   LinkedIn, AUMID `7EE7776C.LinkedInforWindows_w1wdnht996qgy!App`; lo stato può
   riportare anche `LinkedIn.exe`. Usare gli oggetti restituiti dal runtime,
   senza fissare un window ID. Non confondere la presenza nell'inventario con
   l'autorizzazione a leggere o controllare l'app.
2. Selezionare un'unica finestra LinkedIn e acquisirne lo stato. Per le schermate
   che richiedono input, attivare soltanto quella finestra e rileggere lo stato:
   una schermata di un'altra app o un albero AX in contrasto con lo screenshot
   non è una prova valida. Nell'app LinkedIn l'albero AX può restare sulla pagina
   precedente mentre il contenuto visibile è già cambiato. In tal caso usare
   screenshot aggiornati e le coordinate di quello screenshot, secondo la skill.
3. Verificare l'account Francesco Lucherini e la Pagina amministrata
   ElectroFit Systems S.r.l., organizzazione `103544667`. Se non corrispondono,
   fermare il modulo LinkedIn. Non usare la messaggistica personale per l'inbox
   della Pagina e non leggere conversazioni personali aperte in overlay.
4. Verificare soltanto le sezioni necessarie al modulo: inbox della Pagina,
   post/commenti della Pagina, feed, analisi contenuti/follower/visitatori.
   La sola presenza di un pulsante non collauda esportazione, pubblicazione,
   follow, commento, invio, né l'idoneità della newsletter.
5. Registrare data/ora Europe/Rome, launcher reale, ruolo effettivo, app,
   identità, Pagina e copertura. Un test nella chat interattiva, nel subagente
   della chat o nel servizio Operations non certifica il launcher cron Codex.

Non sostituire automaticamente questo percorso con Edge o con il browser in-app:
le relative sessioni e autorizzazioni possono essere differenti. Un login wall
osservato in Edge descrive solo quella sessione. Un diniego della app non si
aggira passando a un altro account, app, protocollo o policy.

## Classificare l'interruzione

- `computer_use_app_approval_required`: messaggio esatto «Computer Use was not
  approved to use LinkedIn». È un diniego del consenso applicativo. Login non
  verificato in quel tentativo, non logout dimostrato. Fermarsi al primo diniego.
- `login_required`: schermata login effettivamente osservata nell'app scelta.
  L'accesso va completato dall'utente; non automatizzare dialoghi autenticazione.
- `wrong_identity_or_page`: account o Pagina non corrispondenti.
- `app_unavailable` / `helper_error`: finestra mancante o guasto tecnico distinto
  dal consenso. Applicare soltanto il recupero limitato previsto dalla skill.
- `section_unavailable`: account/Pagina verificati ma sezione non disponibile.

Il servizio Operations usa un launcher stdio distinto dalle cron. Rifiuta le
richieste interattive: conservarlo fail-closed. La classificazione tipizzata in
`scripts/operations/appserver.py` non concede accesso né approva richieste.

## Consenso supportato e collaudo delle schedule

Quando il runtime presenta «Allow ChatGPT/Codex to use LinkedIn?», l'utente deve
agire direttamente nel dialogo. «Allow» può essere limitato alla sessione;
«Always allow» è una decisione persistente del proprietario. Per controllare lo
stato: Settings > Computer use > Always-allowed apps > LinkedIn. L'assistente
non modifica questa lista o il relativo `config.toml` e non automatizza Codex.

La UI Scheduled della schedule originale è il percorso di avvio da collaudare.
Se manca un'azione supportata per avviare con un override diagnostico in sola
lettura, non premere Run sul prompt di produzione: i moduli possono scrivere
in servizi esterni. Non equiparare un nuovo processo `app-server` al launcher
della schedule. Riportare il test cron come non eseguito e indicare il passaggio
manuale necessario; non dichiarare riparata l'esecuzione senza supervisione.

Durante la diagnosi: nessuna pubblicazione, messaggio, reazione, follow, upload,
richiesta di approvazione, iscrizione o creazione di bozza cloud. Si possono
salvare esclusivamente prove locali. Non avanzare checkpoint di produzione,
azzerare baseline/code/storico, prendere lock di produzione o recuperare arretrati.

Nell'esecuzione ordinaria il preflight è solo lettura; ogni successiva azione
mantiene l'autorizzazione specifica e l'approvazione della revisione richieste
dal proprio workflow. Moduli indipendenti possono proseguire; un accesso parziale
non giustifica un checkpoint completo. Team/SharePoint, brand 4.1 e autorizzazioni
ERP mantengono le regole esistenti.
