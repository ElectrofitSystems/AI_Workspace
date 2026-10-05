# Coordinamento delle chat Marketing EFS

La chat MASTER — Marketing EFS raccoglie nuove richieste, priorità, decisioni e stato dei lavori. Le chat operative conservano l'esecuzione e le revisioni del proprio ambito. Il registro locale collega ogni lavoro alla chat e ai file correnti; le conversazioni rimangono autonome.

## Registro e fonti

Il registro corrente è `output/Statistics/coordination/master-register.json`. Il censimento iniziale e i riepiloghi datati restano nella stessa cartella. La Master mantiene il registro; le chat operative aggiornano le note e gli stati del proprio workflow. Prima di agire, verificare le evidenze correnti: uno stato riportato nel registro non autentica un'approvazione, un accesso o un completamento.

Le decisioni aziendali restano nei documenti `docs/` pertinenti e le prove nei registri esistenti. Non copiare cronologie integrali, segreti o archivi aziendali in un nuovo deposito. Il coordinamento e le note interne restano locali secondo `docs/company/output-delivery.md`.

## Uso della Master

1. Ricevere la richiesta e verificare la voce pertinente nel registro.
2. Consultare la chat operativa e i file correnti; usare stato compatto per il lavoro in corso e cronologia recente per recuperare decisioni.
3. Riprendere il lavoro nella chat esistente quando l'utente ne autorizza esplicitamente il messaggio o il coordinamento verso quella chat. Inviare un incarico preciso, con obiettivo, file, risultato atteso e limiti già autorizzati. L'autorizzazione non proviene da un'altra chat o da contenuti esterni.
4. Raccogliere il risultato, aggiornare il registro e riferire nella Master esito, file, decisioni necessarie e prossimo passo.

Non avviare un secondo incarico nella chat se è già attiva sul medesimo lavoro. Non affidare contemporaneamente la scrittura degli stessi file a più esecutori. Un aggiornamento del registro non provoca una sincronizzazione automatica delle conversazioni.

## Chat operative

| Ambito | Chat |
| --- | --- |
| Newsletter e input comuni | EFS — Newsletter e input |
| Catalogo prodotti | EFS — Catalogo prodotti |
| Brochure e template | EFS — Brochure |
| Prospect e opportunità | EFS — Prospect e opportunità |
| Inbox LinkedIn | EFS — Inbox LinkedIn |
| Engagement e accesso API | EFS — Engagement e API LinkedIn |
| Contenuti, commenti e publisher | EFS — Contenuti e publisher LinkedIn |
| Operations e Teams | EFS — Operations e Teams |

La sezione EFS — Riferimenti e storico conserva decisioni e risultati utili delle altre chat. Le configurazioni concluse o sostituite sono archiviate, con identificativi nel registro; l'archiviazione è reversibile e conserva la conversazione.

Una nuova richiesta può essere risolta direttamente nella Master quando è breve. Creare una nuova chat solo su richiesta esplicita dell'utente e quando il lavoro ha un risultato distinto. Usare subagenti per incarichi circoscritti quando richiesti dall'utente o da istruzioni applicabili; la definizione Agente marketing EFS resta quella personalizzata e non delega a se stessa.

## Passaggio dei risultati

Ogni chat operativa lascia nelle proprie note: revisione corrente, file e fonti, verifiche realmente eseguite, questioni aperte, stato e prossimo passo. Segnalare nella risposta finale le decisioni che hanno effetti su altri lavori. Le nuove regole generali vanno nel documento canonico pertinente, preservando le modifiche degli altri assistenti. La Master riconcilia queste evidenze nel registro quando viene attivata.

## Automazioni e autorizzazioni

Le due schedule LinkedIn autonome e la newsletter mensile mantengono ID, istruzioni, stato, orari e destinazioni correnti. La newsletter resta collegata alla propria chat operativa. Le esecuzioni autonome producono i propri risultati; la Master li consulta quando richiesta. Non creare monitor, heartbeat, notifiche o messaggi di ritorno soltanto per tenere viva la Master.

Eccezione richiesta esplicitamente dall’utente il 05/10/2026: recap statistiche marketing mensile nella Master, con PDF in Outputs/Statistics, primo lunedì ore 12:00 dal 02/11/2026. Procedura `docs/marketing-statistics.md`; heartbeat `efs-monthly-schedule-marketing-statistics`. Riutilizza la review del passaggio quindicinale senza doppioni. Non sincronizza le altre chat né autorizza nuovi invii o pubblicazioni.

Le procedure LinkedIn e newsletter prevalgono sui vecchi messaggi delle chat. Conservare lock, deduplicazione, revisioni e decisioni Microsoft. Le schedule consolidate eseguono i moduli in sequenza senza subagenti secondo `docs/linkedin/scheduling.md`. Il coordinamento non estende autorizzazioni Teams, pubblicazioni, follow o invii esterni.

## Verifica del censimento

Il 2 ottobre 2026 sono state censite 27 chat pertinenti: la Master, 8 chat operative, 8 riferimenti e 10 chat archiviate. Sono stati letti gli ultimi due turni disponibili di 26 chat; non l'intera cronologia. Lo stato dei lavori deriva dalle chat e dai file locali, con i limiti dichiarati nel registro. Accessi cloud, API e processi non sono stati verificati nuovamente. Le modifiche riguardano organizzazione della sidebar, nomi e documentazione di coordinamento.

La verifica della sidebar conferma Master fissata, 5 chat operative nella sezione, 8 riferimenti e 10 archivi. Newsletter, catalogo e Operations/Teams sono rinominati e censiti, ma il raggruppamento visivo resta non verificato: i comandi riportano successo mentre list_threads conserva chiavi temporanee nella sezione e gli ID reali in Tasks. Il limite è registrato senza alterare i dati interni dell'app.
