"""Minimal MCP stdio transport: newline-delimited JSON-RPC, no network listener."""
import json
import sys
from publisher import Publisher, GuardError

TOOLS = [
    ('connection_status','Read local LinkedIn connection state. Does not contact LinkedIn.',{},True),
    ('list_drafts','List local post revisions and publication states.',{},True),
    ('get_draft','Read a draft including exact bilingual copy, media and blockers.',{'post_id':{'type':'string'}},True),
    ('dry_run','Validate a draft without uploading or publishing. Returns blockers and review hash.',{'post_id':{'type':'string'}},True),
    ('save_draft','Save a new local draft revision. Invalidates prior approval. Image is copied into managed storage.',{
        'post_id':{'type':'string'},'commentary':{'type':'string'},'media_path':{'type':'string'},
        'alt_text':{'type':'string'},'blockers':{'type':'array','items':{'type':'string'}},'expected_revision':{'type':'integer','minimum':0}},False),
    ('publish_approved','Publish an authenticated, exact approved revision to the configured LinkedIn company page only for an explicit user execution request. Content approval alone is insufficient. External write. Disabled by default. Never call for draft-only requests.',{'post_id':{'type':'string'}},False),
]

def tool_list():
    return [{'name':name,'description':desc,'inputSchema':{'type':'object','properties':props,
        'required':(['post_id','commentary','expected_revision'] if name=='save_draft' else list(props)),
        'additionalProperties':False},'annotations':{'readOnlyHint':read,'destructiveHint':not read,
        'idempotentHint':read,'openWorldHint':name=='publish_approved'}} for name,desc,props,read in TOOLS]

def handle(request,p):
    method=request.get('method'); params=request.get('params',{})
    if method=='initialize':
        supported=('2024-11-05','2025-03-26','2025-06-18')
        version=params.get('protocolVersion')
        return {'protocolVersion':version if version in supported else supported[-1],
                'capabilities':{'tools':{}},'serverInfo':{'name':'efs-linkedin-publisher','version':'0.1.6'},
                'instructions':'Draft-only by default. Read the persistent company context and draft in Italian first. LinkedIn publication requires an explicit user execution request and authenticated approval of the exact content revision; approval alone does not trigger publication. Teams approval ingestion is not yet supported: never forge a terminal approval, supply a reviewer password or change live settings on behalf of the user. No automatic retries after an unknown publishing outcome.'}
    if method=='ping': return {}
    if method=='tools/list': return {'tools':tool_list()}
    if method=='tools/call':
        name=params.get('name'); args=params.get('arguments',{})
        schema=next((x for x in tool_list() if x['name']==name),None)
        if not schema: raise GuardError('Unknown tool.')
        if set(args)-set(schema['inputSchema']['properties']) or any(k not in args for k in schema['inputSchema']['required']):
            raise GuardError('Invalid tool arguments.')
        try:
            if name=='connection_status': result=p.status()
            elif name=='list_drafts': result=p.list()
            elif name=='get_draft': result=p.get(args['post_id'])
            elif name=='dry_run': result=p.dry_run(args['post_id'])
            elif name=='save_draft': result=p.save_draft(**args)
            else: result=p.publish(args['post_id'])
            return {'content':[{'type':'text','text':json.dumps(result,ensure_ascii=False)}]}
        except GuardError as exc:
            return {'isError':True,'content':[{'type':'text','text':str(exc)}]}
    raise GuardError('Method not found.')

def main():
    p=Publisher()
    for line in sys.stdin:
        req={}
        try:
            req=json.loads(line)
            if 'id' not in req: continue
            result=handle(req,p)
            response={'jsonrpc':'2.0','id':req['id'],'result':result}
        except Exception as exc:
            # Never emit stack traces, request arguments or credential-bearing exceptions.
            response={'jsonrpc':'2.0','id':req.get('id'),'error':{'code':-32603,'message':str(exc) if isinstance(exc,GuardError) else 'Request failed; check local configuration.'}}
        print(json.dumps(response,ensure_ascii=False),flush=True)
    p.db.close()

if __name__=='__main__': main()
