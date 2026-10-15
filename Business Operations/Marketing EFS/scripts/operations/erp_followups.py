"""Recognize bounded ERP continuations; Operations messages never set intent."""
import re

FOLLOW_UP=re.compile(
    r"^(?:e\s+)?(?:puoi\s+|potresti\s+)?"
    r"(?:(?:mostra(?:mi)?|dammi|fammi vedere|vorrei)\s+)?"
    r"(?:il\s+|un\s+|le\s+)?"
    r"(?:dettaglio(?:\s+completo)?|riepilogo|totale|scadenze|fornitori|"
    r"quante sono|quali scadono(?:\s+(?:oggi|domani|questa settimana|questo mese))?|"
    r"(?:solo|anche)\s+(?:quelle|queste)(?:\s+(?:di\s+\w+|scadute|aperte|in scadenza))?|"
    r"(?:ordina(?:r)?l[ei]|raggruppa(?:r)?l[ei])(?:\s+per\s+(?:data|fornitore|importo))?|"
    r"continua|tutte|domani|oggi)"
    r"[?.!]*$", re.IGNORECASE)

EXPLICIT_ERP=re.compile(r"\b(erp|esolver|scadenzari\w*|fattur\w*|pagament\w*|pagare|bonific\w*|debiti|crediti)\b",re.I)

def explicit_erp_request(text):
    # A session deadline or a plugin supplier is not a payables request.
    return bool(EXPLICIT_ERP.search(text or ''))

def erp_follow_up(text, history, explicit_intent=explicit_erp_request):
    """Only a bounded continuation of the peer's actual ERP discussion is ERP."""
    if explicit_intent(text) or not FOLLOW_UP.fullmatch((text or '').strip()):
        return False
    active=False
    for message in history:
        if message.get('speaker')!='collega':
            continue
        previous=(message.get('text') or '').strip()
        active=bool(explicit_intent(previous) or (active and FOLLOW_UP.fullmatch(previous)))
    return active
