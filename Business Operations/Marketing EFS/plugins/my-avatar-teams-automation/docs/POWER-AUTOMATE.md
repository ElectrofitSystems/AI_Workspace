# Flusso Power Automate

Questa guida descrive la variante senza azioni Premium: il passaggio al PC avviene tramite OneDrive for Business.

## Trigger

Usare il trigger Microsoft Teams per un nuovo messaggio in chat. Se il tenant espone un trigger globale, verificare con messaggi reali che copra le chat desiderate. Non considerare affidabile un test basato solo sul designer.

## Sequenza minima

1. Estrarre `conversationId`, `messageId`, tipo evento e mittente.
2. Ignorare eventi diversi da messaggi ed eventi eliminati.
3. Ignorare messaggi del proprietario, bot e applicazioni.
4. Registrare una chiave univoca persistente, preferibilmente in una lista SharePoint privata:
   `tenantId|conversationId|messageId`.
5. Elencare tutti i membri della chat.
6. Bloccare se l'elenco è vuoto, incompleto o paginato senza gestione completa.
7. Bloccare se almeno un membro è guest, esterno, privo di tenant verificabile o fuori dai domini consentiti.
8. Bloccare se il numero dei partecipanti supera `organization.maxParticipants`.
9. Verificare che il mittente corrisponda esattamente a un membro interno.
10. Solo per `VERIFIED_INTERNAL`, creare in OneDrive un file JSON con due proprietà e nessun testo del messaggio.

## File OneDrive

Nome consigliato:

```text
<ticks>-<conversationId-sanitizzato>-<messageId-sanitizzato>.json
```

Contenuto:

```json
{
  "conversationId": "@{...}",
  "messageId": "@{...}"
}
```

Cartella: `My Avatar/MCP Events/Incoming` nell'OneDrive aziendale dell'utente.

## Rami

- `IGNORE_SELF`: nessuna azione.
- `IGNORE_SYSTEM_OR_BOT`: nessuna azione.
- `DUPLICATE`: nessuna azione.
- `EXTERNAL_OR_MIXED`: eventuale avviso al proprietario senza corpo del messaggio.
- `TOO_MANY_PARTICIPANTS`: avviso al proprietario, nessuna risposta automatica.
- `UNVERIFIED`: nessuna chiamata AI; avviso tecnico privo di contenuto.
- `VERIFIED_INTERNAL`: scrittura del riferimento OneDrive.

## Impostazioni consigliate

- Secure Inputs/Outputs sulle azioni che leggono dettagli del messaggio.
- Retry disattivato sulla registrazione univoca per evitare duplicati.
- Nessuna azione che invii il testo del messaggio a servizi esterni.
- Concorrenza controllata per preservare l'ordine quando necessario.

## Test obbligatori

- messaggio del proprietario;
- messaggio interno 1:1;
- chat interna entro il limite;
- chat interna oltre il limite;
- chat con ospite o esterno;
- replay dello stesso evento;
- messaggio eliminato o evento di sistema;
- arresto con flusso disabilitato.
