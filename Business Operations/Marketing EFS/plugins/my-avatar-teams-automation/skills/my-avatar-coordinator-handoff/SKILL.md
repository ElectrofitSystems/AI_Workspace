---
name: my-avatar-coordinator-handoff
description: Passa un messaggio Teams interno già verificato all'agente coordinatore configurato nel progetto, mantenendo riferimenti minimi e confini di autorizzazione. Usala solo quando My Avatar ha classificato l'evento come COORDINATE.
---

# My Avatar Coordinator Handoff

1. Leggi `coordinator` in `.sources/My Avatar/config/settings.json`.
2. Se `enabled` non è `true`, manca `threadId` o il thread non è accessibile, restituisci `ESCALATE` senza tentare invii alternativi.
3. Non inoltrare automaticamente l'intera cronologia Teams. Passa al coordinatore: riferimento opaco dell'evento, mittente verificato, sintesi minima, classificazione e limiti applicabili.
4. Il coordinatore può decidere di eseguire un'automazione, preparare o inviare una risposta se autorizzato, chiedere intervento umano oppure non fare nulla.
5. Non ampliare i permessi: l'accesso del coordinatore a strumenti, siti e account deve essere già autorizzato nel progetto.
6. Evita loop: includi `source=my-avatar`, l'identificativo persistente dell'evento e `handoffDepth=1`; rifiuta eventi con profondità maggiore di 1.
7. Non dichiarare completata l'azione finché il coordinatore non restituisce un esito verificabile.
8. Se l'esito è ambiguo, avvisa il proprietario e non ripetere automaticamente il passaggio.
