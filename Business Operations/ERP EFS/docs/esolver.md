# Acquisizione scadenzario eSolver

Sessione RDP esistente verificata su 192.168.20.16. Ditta osservata: EL,
ELECTROFIT SYSTEMS S.R.L. Operatore visualizzato: FL01.

Percorso verificato: Preferiti → Interrogazione scadenzario, funzione EC742.
La voce si apre sulla consultazione fornitori.

Filtri della prima consultazione del 05/10/2026:

- Situazione al 05/10/2026; data riferimento scaduto 05/10/2026.
- Data scadenza iniziale vuota; finale 31/12/2099.
- Fornitore vuoto, Tutti.
- Aperte selezionato, Tutte; Chiuse escluso.
- Tipo pagamento, classe pagamento, nostro codice banca vuoti.
- Distinte da contabilizzare: No; registrazioni provvisorie: No;
  avvisi di parcella: No; bloccate: Tutte.
- Importi in valuta originale escluso; netto ritenute/contributi escluso.

Risultato acquisito e quadrato con la griglia; importi e dettagli sono
conservati esclusivamente nelle cartelle finanziarie protette. La valuta di conto non
è ancora stata verificata con le impostazioni della ditta. Le righe includono
FT e NC e importi negativi. Non pubblicare il residuo netto come totale dei
pagamenti da disporre. Stati/blocchi vanno acquisiti insieme agli importi.

L'icona Excel nella griglia apre un'esportazione con intestazioni e righe.
Salvare una copia datata in input/esolver/ senza modificare il gestionale.
Confrontare conteggio e somma dei residui con la griglia e conservare filtri,
data acquisizione e hash. Non importare silenziosamente viste parziali.

File originale acquisito in input/esolver/erp20261005.xlsx e normalizzato
con scripts/payables.py; conteggio e somma corrispondono alla griglia.

Da completare: verifica valuta, significato dei
codici di stato, inclusione delle distinte non contabilizzate e controllo con
l'amministrazione delle partite più vecchie.

Verifica del 05/10/2026: Sistemi documenta API REST e Reporter via web services.
Nella nostra installazione sono presenti Ambiente REST 2.0, Reporter e
schedulatore attivo. Non ancora collaudati un endpoint dello scadenzario
fornitori o un export senza operatore. Riscontri e limiti in
[connectivity-verification.md](connectivity-verification.md).
