# Efitsys — Base di conoscenza iniziale dell’agente marketing

Versione 0.3 — 29 settembre 2026 (nome file mantenuto per continuità)  
Stato: base iniziale integrata con la presentazione inglese v12 e le decisioni di configurazione. Informazioni del sito osservate in questa data, senza verifica dei documenti tecnici sottostanti.

## Fonti disponibili

| Fonte | Stato | Uso |
| --- | --- | --- |
| `docs/company/framework.md` | Letto integralmente; versione 0.1 del 29/09/2026 | Decisioni, proposte e punti aperti del marketing |
| [Home Efitsys](https://www.efitsys.com/) | Letta nel browser il 29/09/2026 | Posizionamento e descrizione pubblica |
| [Prodotti](https://www.efitsys.com/#/products) | Letto elenco prodotti il 29/09/2026 | Mappa iniziale dell’offerta; dettagli tecnici da approfondire |
| [Applicazioni](https://www.efitsys.com/#/applications) | Letti introduzione, elenco delle categorie e pannello retrofit il 29/09/2026 | Ambiti pubblicamente presentati; non è un audit di ogni applicazione |
| [Servizi](https://www.efitsys.com/#/services) | Letta pagina il 29/09/2026 | Sviluppo, validazione, software e supporto alla certificazione |
| Presentazione aziendale inglese v12, PowerPoint su SharePoint | Testo di 35 slide acquisito il 29/09/2026; ultima modifica del file 23/09/2026 | Fonte selezionata dall’utente per offerta, competenze, differenzianti e mercati; note e testo in `input/` |
| Corporate Design Kit e handbook 1.0, indicati dall’utente | ZIP acquisito ed estratto; lette le 28 pagine dell’handbook e controllati visivamente logo, tipografia e applicazioni | Riferimento grafico operativo, con eccezione confermata sui motti; `docs/company/brand.md` |

## Contesto aziendale confermato dal framework

Mission: aiutare i clienti, attraverso le competenze nei sistemi di propulsione elettrica, ad accelerare lo sviluppo dei loro prodotti e ad avere successo sul mercato.

Valori confermati: attenzione al cliente, affidabilità, visione di lungo periodo, onestà e trasparenza. Personalità: competente e rigorosa, affidabile, innovativa ma concreta, collaborativa e vicina al cliente.

La vision richiama sistemi certificati, modulari e definiti dal software come direzione aziendale; non costituisce da sola prova tecnica sul catalogo. Il purpose nel framework è indicato come ultima formulazione discussa, senza promuoverlo qui a definitiva approvazione.

Il framework mantiene tutti i differenzianti selezionati nella presentazione. La v12 è ora acquisita: la mappa di strategia, competenze, cinque proposte di valore e otto mercati è in `docs/company/presentation-notes.md`, con riferimenti alle slide e punti da verificare. L’estrazione completa è in `input/Technical documentation/efitsys-company-presentation-v12-en-extracted.md`. Diagrammi e immagini non sono stati esaminati.

## Decisioni di configurazione confermate

- Fonti approvate e accesso: il materiale del canale ElectroFit Systems nel team Documentation è approved content per il marketing per conferma esplicita dell'utente. Il collegamento indicato anche da Engineering - Powertrain non è visibile nell'elenco del connettore. Nova Energia è il riferimento prodotto per retrofit Panda 141. Usa `docs/company/sources.md` per link, perimetro e limiti. Tutti gli originali Teams/SharePoint rimangono in sola lettura e nelle loro posizioni.
- Piattaforma: questo progetto Codex, tramite `AGENTS.md` e istruzioni operative locali.
- Dopo il chiarimento dell'utente, è stata aggiunta la definizione di agente personalizzato `.codex/agents/agente-marketing-EFS.toml`, con nome esatto **Agente marketing EFS**. È distinta dalle sole istruzioni del progetto; lo stato della verifica di avvio è registrato in `docs/maintenance/codex.md`.
- Priorità iniziale: produzione di contenuti e materiali commerciali.
- Fonte aziendale: presentazione inglese v12 nella cartella SharePoint indicata dall’utente. Il PowerPoint è più recente dei PDF v12 elencati nella cartella; non assumere identità di contenuto tra i file.
- Riferimento grafico: Corporate Design Kit fornito dall’utente, con logo originale e Arial. Eccezione confermata esplicitamente: usare i motti italiano e inglese del framework al posto di “Your success is our success!”.
- Lettura SharePoint verificata; estrazione locale datata, senza sincronizzazione automatica.
- Traccia operativa: `docs/company/templates/content-brief.md`; nuove bozze richieste in `output/`.

La presentazione aggiunge alla ricognizione iniziale, tra gli altri elementi, robotica mobile e settore forestale. Tutti gli otto mercati rimangono nel perimetro. I prezzi divergono tra la slide 17 e le slide 32–33: chiarire il listino prima di produrre materiali con importi. Le sezioni su costi e investitori rimangono conoscenza interna, senza riuso automatico in materiali pubblici o per clienti.

## Offerta osservata sul sito

La comunicazione presenta Efitsys come partner per l’integrazione di sistemi di propulsione elettrica, con sistemi completi, sottosistemi e supporto ingegneristico. Il sito presenta eFit Kit come piattaforma di powertrain per veicoli leggeri, adatta a nuove piattaforme e conversioni.

| Famiglia | Descrizione pubblica sintetica | Fonte |
| --- | --- | --- |
| Integrated Electrical Drive (IED) | Motore e inverter integrati; la pagina menziona il controllo Flux Polar Control (FPC) e una licenza esclusiva di tecnologia brevettata | Prodotti |
| Modular Battery Pack | Sistema batteria modulare a celle prismatiche con flessibilità meccanica ed elettrica | Prodotti |
| Power Distribution Unit (PDU) | Nodo di distribuzione e conversione che collega batteria, azionamento, caricatore e ausiliari | Prodotti |
| Powertrain Control Unit (PCU) | Unità che coordina coppia, flussi energetici e reazioni di sicurezza del powertrain | Prodotti |

La pagina Applicazioni elenca retrofit, veicoli di categoria L, mezzi municipali e di servizio, macchine agricole, costruzioni e movimentazione al chiuso, applicazioni marine. Non dedurre da questo elenco priorità commerciali, quote di mercato o casi realizzati in ciascun settore.

I servizi pubblicati comprendono sviluppo e validazione, supporto a certificazioni e omologazioni e sviluppo software ECU. La pagina menziona le metodologie eV-Cycle e Digital Triplets. I riferimenti a normative e processi richiedono documentazione specifica prima di essere trasformati in nuove dichiarazioni di conformità.

## Affermazioni da documentare per nuovi materiali

| Tema | Indicazione pubblica osservata | Evidenza necessaria per formulazioni specifiche |
| --- | --- | --- |
| eFit Kit | La home riporta omologazione NAD | Documento, identificativo, configurazioni e campo di applicazione |
| Componenti certificati | La home usa un messaggio generale sui moduli certificati | Elenco di componenti/versioni e relativi documenti |
| FPC | La pagina Prodotti menziona brevetto e licenza esclusiva | Riferimenti, titolarità, licenza e formulazione divulgabile |
| Sicurezza funzionale | Il sito descrive processi orientati agli standard automotive | Documenti che distinguano metodo, valutazione e certificazione |
| Vantaggi economici e ambientali | Il pannello retrofit elenca benefici qualitativi | Condizioni d’uso, confronto, dati e limiti per eventuali claim quantitativi |
| Progetti e clienti | Il sito cita il progetto Panda di Nova Energia | Materiali aggiornati e perimetro divulgabile del caso |

Queste lacune non impediscono di sviluppare strategia o bozze basate sui fatti disponibili. Impediscono di presentare come provati dettagli non ancora verificati.

## Identità visiva: stato effettivo

La palette del kit coincide con quella del framework: navy #0B2348, cyan #00A8C6, teal #007A8F, lime #BDD63A, bianco #FFFFFF, ice #F2F6F8, graphite #27343D e slate #60717E. Il kit ora indicato dall’utente prescrive Arial, che sostituisce operativamente Korataki e Inter delle precedenti esplorazioni. Usare i loghi originali del pacchetto e i template disponibili, conservando i master.

Il wordmark fornito è minuscolo e convertito in tracciati: non ridisegnarlo né ridigitarlo. I motti del framework restano confermati e devono sostituire il vecchio motto nelle copie di lavoro. Le regole, i formati e i percorsi esatti sono in `docs/company/brand.md`.

## Questioni aperte e dipendenze

**Configurazione locale completata:** progetto Codex, priorità contenuti/materiali commerciali, presentazione v12 acquisita come testo, handbook e kit grafico scaricati e indicizzati. Motti del framework riconfermati dall’utente. Sono disponibili loghi, template Office e asset per stampa e digitale; fotografie di prodotto e ulteriori schede tecniche andranno reperite secondo il materiale richiesto.

**Per produrre materiali specifici:** prodotto/applicazione; obiettivo; fonti tecniche e prove divulgabili; eventuali mercati geografici e lingua. Non imporre una definizione delle personas che l’azienda ha già rinviato.

**Per il flusso editoriale:** referenti tecnici e comunicazione; capacità reale di revisione; calendario; struttura e permessi SharePoint. Approvatore finale già confermato: il referente configurato nel flusso Microsoft. Le notifiche di revisione sono gestite dal flusso Microsoft, senza indirizzi personali nel progetto.

**Per la misurazione:** fonti e accesso ai dati, definizione di contatto qualificato, baseline, obiettivi e responsabilità. Controllo mensile e revisione trimestrale già confermati; non equivalgono ad automazioni attivate.

## Osservazione tecnica sul sito

L’HTML della home restituito il 29/09/2026 contiene `<meta name="robots" content="noindex, nofollow" />`. Registrare questo punto per un eventuale audit del sito e verificare con il responsabile se sia intenzionale. Il rilievo riguarda il codice ricevuto: non prova da solo lo stato effettivo di indicizzazione e non autorizza modifiche al sito.

## Utilizzo dei documenti

Le istruzioni operative sono in `docs/company/mandate.md` e sono richiamate dal nuovo `AGENTS.md` del progetto, secondo la [guida ufficiale OpenAI](https://learn.chatgpt.com/docs/agent-configuration/agents-md). Il framework originale rimane il riferimento per lo stato delle decisioni. Le nuove decisioni esplicite dell’utente sulla piattaforma, la priorità e la fonte sono registrate sopra. Non sono state attivate automazioni o funzioni di pubblicazione.
