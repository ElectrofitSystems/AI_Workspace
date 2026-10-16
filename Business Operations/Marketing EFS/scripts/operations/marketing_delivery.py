"""File-scoped Marketing delivery checks and safe Teams HTML.

Only connector observations authorize delivery; model claims are not ACL evidence.
The worker journals uploads; this transport journals grants and Teams send state.
"""
from __future__ import annotations
import html
import json
import re
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit
from teams_state import GuardError, internal_email

SIGNATURE = '- by Agente Marketing EFS'
OUTPUTS = '/sites/Documentation/Shared Documents/General/Marketing/Outputs/'
BROCHURES = OUTPUTS + 'Documentation/Brochures/'
FALLBACK = '/personal/operations_efitsys_com/Documents/'


def safe_url(value):
    if not isinstance(value, str) or any(c.isspace() or ord(c)<32 for c in value):
        raise GuardError('invalid_delivery_url')
    url=urlsplit(value)
    if (url.scheme!='https' or url.username or url.password or url.port not in (None,443)
            or url.hostname not in ('efitsys.sharepoint.com','efitsys-my.sharepoint.com')
            or url.query or url.fragment):
        raise GuardError('not_canonical_tenant_file_url')
    path=unquote(url.path)
    if any(p in ('.','..') for p in path.split('/')) or '\\' in path or '%' in path:
        raise GuardError('invalid_delivery_path')
    return url.hostname,path


def destination(url,kind):
    host,path=safe_url(url)
    if host=='efitsys.sharepoint.com' and path.startswith(OUTPUTS):
        if kind=='datasheet' and not path.startswith(BROCHURES):
            raise GuardError('datasheet_wrong_destination')
        return None
    if host=='efitsys-my.sharepoint.com' and any(path.startswith(FALLBACK+folder+'/')
            for folder in ('Chat con efitsys','Microsoft Teams Chat Files')):
        # Datasheets already have an exact destination; fallback is for unknown types.
        if kind=='datasheet':raise GuardError('datasheet_wrong_destination')
        return 'File in OneDrive di Operations / '+path[len(FALLBACK):].rsplit('/',1)[0]
    raise GuardError('delivery_outside_authorized_destinations')


def direct_write(permissions,peer):
    if permissions.get('next_link') or permissions.get('@odata.nextLink'):
        raise GuardError('incomplete_permission_coverage')
    rows=permissions.get('value')
    if not isinstance(rows,list):raise GuardError('missing_permission_observation')
    if any((row.get('link') or {}).get('scope') in ('anonymous','organization') for row in rows):
        raise GuardError('broad_sharing_requires_review')
    for row in rows:
        link=row.get('link') or {}
        if link.get('scope') in ('anonymous','organization'):
            # Never send a general sharing link or silently alter preexisting ACLs.
            raise GuardError('broad_sharing_requires_review')
        if not {'write','owner'}.intersection(row.get('roles',[])):continue
        if row.get('expiration_date_time') or row.get('expirationDateTime'):continue
        identities=[]
        for key in ('granted_to','grantedTo','granted_to_v2','grantedToV2'):
            if isinstance(row.get(key),dict):identities.append(row[key])
        for key in ('granted_to_identities','grantedToIdentities','granted_to_identities_v2','grantedToIdentitiesV2'):
            identities.extend(row.get(key) or [])
        for identity in identities:
            user=identity.get('user') or {}
            if user.get('id')==peer['peer_id']:
                email=user.get('email') or user.get('userPrincipalName')
                if email and email.lower()!=peer['peer_email']:continue
                return True
    return False


def verify_files(call,db,request,deliveries):
    """Read back uploaded revision, grant only that file, verify named write ACL."""
    if not internal_email(request.get('peer_email')) or not request.get('peer_id'):
        raise GuardError('unverified_file_recipient')
    if not isinstance(deliveries,list) or len(deliveries)>20:
        raise GuardError('invalid_delivery_manifest')
    db.execute('CREATE TABLE IF NOT EXISTS marketing_file_grants '
        '(chat TEXT,message TEXT,drive TEXT,item TEXT,peer TEXT,revision TEXT,state TEXT,'
        'PRIMARY KEY(chat,message,drive,item,peer,revision))')
    verified=[];seen=set()
    for entry in deliveries:
        required=('drive_id','item_id','web_url','e_tag','label','kind')
        if not isinstance(entry,dict) or any(not isinstance(entry.get(k),str) or not entry[k] for k in required):
            raise GuardError('incomplete_delivery_manifest')
        if entry['kind'] not in ('datasheet','document','presentation','visual','statistics','other'):
            raise GuardError('unknown_delivery_kind')
        key=(entry['drive_id'],entry['item_id'])
        if key in seen:raise GuardError('duplicate_delivery_file')
        seen.add(key)
        item=call('get_drive_item',dict(zip(('drive_id','item_id'),key)))
        if (item.get('id')!=entry['item_id'] or not item.get('file') or item.get('folder')
                or item.get('parent_reference',{}).get('drive_id')!=entry['drive_id']
                or item.get('web_url')!=entry['web_url'] or item.get('e_tag')!=entry['e_tag']
                or not isinstance(item.get('size'),int) or item['size']<=0):
            raise GuardError('uploaded_file_or_revision_mismatch')
        tenant=(item.get('sharepoint_ids') or {}).get('tenant_id')
        if tenant and tenant!='3b97374b-4a43-4588-a04f-4c94edc33cf3':
            raise GuardError('wrong_file_tenant')
        kind='datasheet' if re.search(r'datasheet|scheda[-_ ]tecnica',item.get('name',''),re.I) else entry['kind']
        note=destination(item['web_url'],kind)
        if note:
            drives=call('list_drives',{})
            if not any(d.get('id')==entry['drive_id'] and d.get('web_url')==
                    'https://efitsys-my.sharepoint.com'+FALLBACK.rstrip('/') for d in drives.get('value',[])):
                raise GuardError('unverified_operations_onedrive')
        target={'type':'drive_item','drive_id':entry['drive_id'],'item_id':entry['item_id']}
        permissions=call('list_item_permissions',{'target':target})
        journal=(request['chat_id'],request['message_id'],*key,request['peer_id'],entry['e_tag'])
        if not direct_write(permissions,request):
            # Persist before the mutation. Any exception leaves a durable uncertain grant.
            if db.execute('SELECT state FROM marketing_file_grants WHERE '
                    'chat=? AND message=? AND drive=? AND item=? AND peer=? AND revision=?',journal).fetchone():
                raise GuardError('file_grant_uncertain_do_not_repeat')
            db.execute('INSERT INTO marketing_file_grants VALUES (?,?,?,?,?,?,?)',(*journal,'granting'))
            db.commit()
            call('invite_item_recipients',{'target':target,'recipients':[request['peer_email']],
                'role':'write','require_sign_in':True,'send_invitation':False,'retain_inherited_permissions':True})
            if not direct_write(call('list_item_permissions',{'target':target}),request):
                raise GuardError('named_file_write_not_verified')
        db.execute('INSERT OR REPLACE INTO marketing_file_grants VALUES (?,?,?,?,?,?,?)',(*journal,'verified'))
        db.commit()
        verified.append({**entry,'fallback_note':note})
    return verified


def teams_html(response,files):
    """Construct safe HTML ourselves; never forward model-generated tags."""
    if not isinstance(response,str) or not response.strip():raise GuardError('invalid_response')
    allowed={f['web_url'] for f in files}
    pattern=re.compile(r'\[([^\]\n]+)\]\((https://[^\s)]+)\)|(https?://[^\s<>]+)')
    pieces=[];offset=0;linked=set()
    for match in pattern.finditer(response):
        pieces.append(html.escape(response[offset:match.start()]))
        url=match[2] or match[3]
        if url not in allowed:
            # Public evidence URLs are not file deliveries. Preserve research use;
            # tenant documents always require the verified delivery manifest.
            source=urlsplit(url)
            if (source.scheme!='https' or not source.hostname or source.username or source.password
                    or source.hostname.endswith(('sharepoint.com','onedrive.com','1drv.ms'))):
                raise GuardError('unverified_response_link')
        pieces.append('<a href="'+html.escape(url,quote=True)+'">'+html.escape(match[1] or url)+'</a>')
        linked.add(url);offset=match.end()
    pieces.append(html.escape(response[offset:]))
    body=''.join(pieces).replace('\n','<br>')
    for f in files:
        if f['web_url'] not in linked:
            body+='<br><a href="'+html.escape(f['web_url'],quote=True)+'">'+html.escape(f['label'])+'</a>'
    for note in dict.fromkeys(f['fallback_note'] for f in files if f.get('fallback_note')):
        body+='<br>'+html.escape(note)
    # Exactly one signature, including if a worker already appended it.
    body=re.sub(r'(?:<br>|\s)+$','',body.replace(SIGNATURE,''))
    return '<p>'+body+'</p><p>'+SIGNATURE+'</p>'


class _Fingerprint(HTMLParser):
    def __init__(self):super().__init__(convert_charrefs=True);self.parts=[]
    def handle_starttag(self,tag,attrs):
        if tag=='a':self.parts.append(('href',dict(attrs).get('href','')))
    def handle_data(self,data):
        self.parts.extend(('text',word) for word in data.split())


def html_fingerprint(value):
    # Include anchor targets: same visible label with a different URL is not a receipt.
    value=value or ''
    if not re.search(r'<(?:p|div|a|br)\b',value,re.I):
        # Teams read actions return Markdown, including wrapped long URL targets.
        value=re.sub(r'\\([\-_*])',r'\1',value)
        parts=[];offset=0
        for match in re.finditer(r'\[([^\]]+)\]\((https?://[^)]+)\)',value):
            parts.append(html.escape(value[offset:match.start()]))
            url=re.sub(r'[ \t]*\r?\n[ \t]*','',match[2])
            parts.append('<a href="'+html.escape(url,quote=True)+'">'+html.escape(match[1])+'</a>')
            offset=match.end()
        parts.append(html.escape(value[offset:]))
        value=''.join(parts)
    parser=_Fingerprint();parser.feed(value)
    return json.dumps(parser.parts,ensure_ascii=False,separators=(',',':'))
