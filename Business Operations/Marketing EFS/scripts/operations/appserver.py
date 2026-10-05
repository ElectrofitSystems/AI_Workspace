"""Local stdio client for the documented Codex app-server JSON-RPC protocol."""
from __future__ import annotations
import json
import queue
import re
import subprocess
import threading
import time
from pathlib import Path

class RpcError(RuntimeError):
    pass

class RateLimited(RpcError):
    def __init__(self, seconds):
        self.retry_after=max(1,int(seconds))
        super().__init__('connector_rate_limited; retry_after='+str(self.retry_after))

def config_value(value):
    if isinstance(value,dict):
        return '{'+', '.join(json.dumps(k)+' = '+config_value(v) for k,v in value.items())+'}'
    return json.dumps(value,ensure_ascii=False)

class AppServer:
    def __init__(self, executable, cwd, process_config=None):
        self.cwd = str(Path(cwd).resolve())
        self.cooldown=Path(self.cwd)/'.local/operations-teams/cooldown.json'
        command=[str(executable)]
        for key,value in (process_config or {}).items():
            command.extend(['-c',key+'='+config_value(value)])
        command.extend(['app-server','--stdio'])
        self.permission_profile=bool((process_config or {}).get('default_permissions'))
        self.process = subprocess.Popen(command,
            cwd=self.cwd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL, text=True, encoding='utf-8', bufsize=1,
            creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        self.lock = threading.Lock()
        self.pending = {}
        self.events = queue.Queue()
        self.counter = 0
        self.verified_roles={}
        self.specialists={}
        threading.Thread(target=self._reader, daemon=True).start()
        self.request('initialize', {'clientInfo':{'name':'efs_operations_local',
            'title':'Operations Teams local','version':'0.2.0'},
            'capabilities':{'experimentalApi':True}})
        self._write({'method':'initialized','params':{}})

    def _write(self, payload):
        with self.lock:
            self.process.stdin.write(json.dumps(payload,ensure_ascii=False)+'\n')
            self.process.stdin.flush()

    def _reader(self):
        try:
            for line in self.process.stdout:
                try: message=json.loads(line)
                except ValueError: continue
                if 'id' in message and 'method' not in message:
                    future=self.pending.get(message['id'])
                    if future: future.put(message)
                elif 'id' in message:
                    # No automatic acceptance of approvals, elicitation, or new permissions.
                    self._write({'id':message['id'],'error':{'code':-32000,
                        'message':'Interactive approval required; unattended service declines.'}})
                    self.events.put({'method':'operations/approvalRequired','params':{
                        'requestMethod':message.get('method')}})
                else:self.events.put(message)
        finally:
            for future in list(self.pending.values()):
                future.put({'error':{'message':'app-server disconnected'}})

    def request(self, method, params, timeout=60):
        with self.lock:
            self.counter+=1
            identifier=self.counter
            future=queue.Queue()
            self.pending[identifier]=future
        try:
            self._write({'id':identifier,'method':method,'params':params})
            try: response=future.get(timeout=timeout)
            except queue.Empty:raise RpcError('timeout:'+method)
            if 'error' in response:raise RpcError(str(response['error']))
            return response['result']
        finally:self.pending.pop(identifier,None)

    def start_thread(self, developer=None, config=None):
        params={'cwd':self.cwd,'ephemeral':True,'approvalPolicy':'never',
            'serviceName':'efs_operations_local'}
        if not self.permission_profile:params['sandbox']='read-only'
        if developer:params['developerInstructions']=developer
        if config:params['config']=config
        return self.request('thread/start',params)['thread']['id']

    def tool(self, thread, name, arguments):
        if self.cooldown.exists():
            try:deadline=json.loads(self.cooldown.read_text(encoding='utf-8'))['until']
            except (ValueError,KeyError):deadline=0
            if deadline>time.time():raise RateLimited(deadline-time.time()+1)
        result=self.request('mcpServer/tool/call',{'threadId':thread,
            'server':'codex_apps','tool':'microsoft_teams.'+name,'arguments':arguments})
        if result.get('isError'):
            data=result.get('structuredContent') or {}
            detail=' '.join(c.get('text','') for c in result.get('content',[]) if isinstance(c,dict) and c.get('type')=='text')
            if data.get('error_code')=='RATE_LIMITED' or '429' in detail or 'HTTPRateLimitError' in detail:
                match=re.search(r'at least (\d+) seconds',detail)
                seconds=int(data.get('retry_after_seconds') or (match.group(1) if match else 120))
                self.cooldown.parent.mkdir(parents=True,exist_ok=True)
                self.cooldown.write_text(json.dumps({'until':time.time()+seconds+2}),encoding='utf-8')
                raise RateLimited(seconds+2)
            raise RpcError('connector_error:'+name+':'+detail[:500])
        data=result.get('structuredContent')
        if not isinstance(data,dict):raise RpcError('missing_structured_content:'+name)
        return data

    def answer(self, thread, text, timeout=600):
        start=time.monotonic()
        result=self.request('turn/start',{'threadId':thread,'input':[{'type':'text','text':text}],
            'outputSchema':{'type':'object','properties':{'response':{'type':'string'},
                'agent':{'type':'string'}},'required':['response','agent'],
                'additionalProperties':False}})
        turn_id=result['turn']['id']
        final=[]
        delegated=[]
        children=set()
        while time.monotonic()-start < timeout:
            try:event=self.events.get(timeout=1)
            except queue.Empty:continue
            method,params=event.get('method'),event.get('params',{})
            if params.get('threadId')!=thread:continue
            if method=='item/completed':
                item=params.get('item',{})
                if item.get('type')=='agentMessage' and item.get('phase') in ('final_answer',None):
                    final.append(item.get('text',''))
                if item.get('type')=='collabAgentToolCall':delegated.append(item)
                if item.get('type')=='subAgentActivity' and item.get('agentThreadId'):
                    children.add(item['agentThreadId'])
            if method=='turn/completed' and params.get('turn',{}).get('id')==turn_id:
                if params['turn'].get('status')!='completed':raise RpcError('agent_turn_failed')
                if not final:raise RpcError('missing_final_answer')
                answer=json.loads(final[-1])
                roles=[]
                for delegation in delegated:
                    if delegation.get('tool')=='spawnAgent':
                        children.update(delegation.get('receiverThreadIds',[]))
                for child in children:
                    info=self.request('thread/read',{'threadId':child,'includeTurns':False})
                    role=info.get('thread',{}).get('agentRole')
                    roles.append(role)
                    if role:
                        self.specialists.setdefault(thread,{})[role]=child
                        self.verified_roles.setdefault(child,set()).add(role)
                known=self.verified_roles.setdefault(thread,set())
                known.update(role for role in roles if role)
                return {**answer,'elapsed_seconds':round(time.monotonic()-start,3),
                    'delegated_roles':list(known),
                    'specialist_threads':self.specialists.get(thread,{})}
        self.request('turn/interrupt',{'threadId':thread,'turnId':turn_id})
        raise RpcError('agent_timeout')

    def close(self):
        if self.process.poll() is None:
            self.process.terminate()
            try:self.process.wait(timeout=10)
            except subprocess.TimeoutExpired:self.process.kill()
