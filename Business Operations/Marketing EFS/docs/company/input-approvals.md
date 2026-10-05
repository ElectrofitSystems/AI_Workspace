# Approvazione degli input — LinkedIn e newsletter

**Canale newsletter — 5 ottobre 2026:** la newsletter è per ora solo quella nativa della Pagina LinkedIn EFS. Ambiti, limiti e revisioni delle approvazioni input comuni restano invariati. La review finale del derivato è distinta; il suo stato dopo approvazione è approved_pending_linkedin_publication. I riferimenti storici sotto a mailing e approved_pending_send sono superati da docs/newsletter/workflow.md.

## Procedura corrente — 5 ottobre 2026

Le nuove aggiunte in Marketing/Inputs ora avviano automaticamente la richiesta mediante il flusso cloud dedicato documentato in `docs/company/marketing-input-folder.md`, su ulteriore richiesta esplicita dell'utente. Questo automatizza soltanto la creazione della review: non costituisce approvazione, non reinvia il pregresso e non autorizza il riuso senza controllo della versione originale.

La correzione più recente sostituisce la lista con collegamenti nativi .url agli originali in SharePoint Marketing/Inputs. Applicare [Marketing Inputs - collegamenti e approvazioni](marketing-input-folder.md) per nuove selezioni e review native del collegamento, vincolate anche alla revisione del file originale. Conservare le decisioni originali Lists e riconciliare le richieste pregresse, senza duplicarle. Ambito comune LinkedIn/newsletter, cache con lock e separazione dal derivato restano validi. Lo stato del collegamento non approva automaticamente successive modifiche del documento originale. I paragrafi sotto conservano il flusso storico.

Versione 1.1 — 2 ottobre 2026. Richiesta esplicita dell'utente: approvare i nuovi input prima di usarli per entrambi i canali, usando un elenco Teams con allegati o link. Percorso corrente: approvazioni native delle voci di Marketing Inputs, secondo docs/company/marketing-input-list.md. Questo aggiornamento supera il precedente invio di manifest per nuove richieste input; conservare i pacchetti e le richieste pregresse.

## Fonte comune e perimetro

La selezione dei nuovi input proviene dall'elenco Microsoft Lists Marketing Inputs nel canale Teams Documentation / General. Ogni voce contiene un file allegato oppure un link verso l'originale. La cartella SharePoint Marketing/Inputs resta l'archivio file secondo docs/company/sources.md. Lettura consentita per inventario, valutazione e richiesta; presenza nell'elenco o nella cartella non autorizza il riuso. La regola riguarda documenti tecnici, foto, video e asset di brand. Non modificare gli originali né spostarli in Outputs.

Le approvazioni esplicite delle fonti già concesse restano valide nel loro ambito documentato. Non inventare un'approvazione pregressa per ogni file della cartella. Nuovi file, nuove revisioni e ampliamenti del perimetro richiedono approvazione. Un input non ancora approvato può essere esaminato per la review, ma non alimenta claim o media dei pacchetti editoriali.

Registro condiviso locale: output/Linkedin/config/input-approvals.json, cache usata anche dalla newsletter. La decisione originale Microsoft resta autoritativa. Identificare voce/list URL e item ID, URL o allegato originale, drive/item ID quando disponibili, nome, versione/eTag e SHA256 dei byte acquisiti. Registrare data, ambito, limiti, stato, dettaglio decisione e fonti effettivamente usate. Se non è possibile identificare la revisione esatta, lo stato è unknown e il file è escluso dal riuso.

## Richiesta unica per entrambi i canali

1. Leggere le voci nuove/modificate dell'elenco con la copertura effettivamente disponibile; individuare allegato o link e revisione. Non importare automaticamente tutti i file della cartella e non dichiarare una scansione completa se parziale.
2. Verificare completezza, claim/media proposti, diritti, limiti e scope «uso come fonte per LinkedIn e newsletter». Conservare note/snapshot in output/Linkedin/input-approvals/ quando necessari. Non chiedere approvazione finale di un derivato in questo passaggio.
3. Creare la richiesta nativa dalla voce dell'elenco, usando approvatori e regola configurati nel servizio Microsoft. La richiesta identifica revisione della voce e del file, ambito e limiti. La cache resta pending alla sola richiesta. Se mancano revisori o evidenze, segnalare l'input necessario e non scegliere destinatari dalla cronologia.
4. Deduplicare per voce, revisione, file e scope; riconciliare eventuali review del percorso manifest preesistente senza duplicarle nell'elenco. Non mandare richieste alternative in chat/DM/email. Unknown richiede riconciliazione prima del retry.
5. Verificare dettagli originali della decisione Microsoft, identità autorizzata e regola, voce/revisione/file/ambito. Una scelta manuale di stato o la cache non autenticano l'approvazione. Solo dopo verifica registrare approved/rejected/revoked, approval ID o URL dettagli e data/evidenza. Se il servizio non è leggibile, mantenere pending/unknown.
6. Prima del riuso verificare anche il file collegato: aggiornare il file senza cambiare la voce non è una nuova approvazione. Nuova revisione del file o della voce richiede nuova review; preservare storia e prove. Annotare i riusi nella cache e nei derivati, senza modificare la voce approvata.

## Inserimento nelle ricorrenze

LinkedIn fortnightly e newsletter mensile leggono lo stesso elenco e consultano la cache prima della selezione. Se una fonte è pending/rejected/revoked/unknown, lavorano sulle fonti già autorizzate oppure registrano awaiting_input_approval. Non produrre contenuti riempitivi e non bloccare le fasi indipendenti. Ogni pacchetto registra voce, input effettivamente usati e prove di approvazione. Accesso browser verificato, API Lists non esposta: applicare i limiti di docs/company/marketing-input-list.md.

Daily operations riconcilia le approvazioni degli input e della newsletter insieme alle review già previste, senza una nuova schedule di monitoraggio. Acquisire il lock comune `output/Linkedin/config/input-approvals.lock` quando si aggiorna il registro; usare scritture atomiche, conservare le altre voci e rilasciare solo il proprio lock. Non resettare registri esistenti.

L'approvazione degli input non approva il derivato. Post e newsletter finali hanno pacchetti di approvazione distinti. La newsletter resta approved_pending_send dopo la review finale: invio ai destinatari e configurazione di mailing richiedono il relativo mandato esplicito.

## Stato iniziale

Elenco, scheda Teams, approvazioni moderne e ricorrenze configurati il 02/10/2026. Nessun input è dichiarato approvato dall'agente e nessuna nuova decisione umana è stata simulata. La prima richiesta pertinente userà la voce reale; il test storico del flusso Outputs non costituisce un collaudo delle approvazioni di Lists.

Il primo popolamento dello stesso giorno comprende 68 materiali selezionati dagli archivi aziendali, con link, tema, contesto e versione verificati nella scheda Teams. Stato nativo Non inviata / Not submitted; cache unreviewed. Non sono state inviate richieste massive durante il popolamento. Gli ID delle voci e le revisioni native non ancora acquisite vanno risolti e verificati prima delle richieste e del riuso; metadata e stato locale non costituiscono approvazione.
