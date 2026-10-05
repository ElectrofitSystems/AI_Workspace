"""Read-only BIFF8 extraction for archived LinkedIn XLS exports.
SST continuation supported. No formulas evaluated; unsupported formulas fail.
"""
import struct, json, pathlib, collections
U=lambda b,o=0:struct.unpack_from('<I',b,o)[0]
H=lambda b,o=0:struct.unpack_from('<H',b,o)[0]
def workbook(path):
    data=pathlib.Path(path).read_bytes()
    assert data[:8]==bytes.fromhex('D0CF11E0A1B11AE1')
    size=1<<H(data,30)
    sector=lambda n:data[(n+1)*size:(n+2)*size]
    difat=list(struct.unpack_from('<109I',data,76)); nxt=U(data,68)
    for _ in range(U(data,72)):
        nums=struct.unpack('<'+'I'*(size//4),sector(nxt)); difat+=list(nums[:-1]); nxt=nums[-1]
    fat=[]
    for n in [n for n in difat if n<0xFFFFFFFA][:U(data,44)]: fat+=list(struct.unpack('<'+'I'*(size//4),sector(n)))
    def chain(start, table=fat, getter=sector):
        parts=[];seen=set();n=start
        while n<0xFFFFFFFA:
            assert n not in seen; seen.add(n);parts.append(getter(n));n=table[n]
        return b''.join(parts)
    dirs=chain(U(data,48)); entries=[]
    for off in range(0,len(dirs),128):
        e=dirs[off:off+128]; ln=H(e,64)
        if ln: entries.append((e[:ln-2].decode('utf-16le'),e[66],U(e,116),struct.unpack_from('<Q',e,120)[0]))
    root=next(e for e in entries if e[1]==5)
    e=next(e for e in entries if e[0] in ('Workbook','Book'))
    if e[3]<U(data,56):
        mini=chain(root[2])[:root[3]]; mf=chain(U(data,60)); mt=struct.unpack('<'+'I'*(len(mf)//4),mf)
        wb=chain(e[2],mt,lambda n:mini[n*64:(n+1)*64])[:e[3]]
    else: wb=chain(e[2])[:e[3]]
    rec=[];o=0
    while o+4<=len(wb):
        typ,ln=struct.unpack_from('<HH',wb,o); rec.append((o,typ,wb[o+4:o+4+ln]));o+=4+ln
    strings=[];bounds=[]
    for idx,(pos,typ,b) in enumerate(rec):
        if typ==0x85:
            ln=b[6];enc='utf-16le' if b[7]&1 else 'latin1';bounds.append((U(b),b[8:8+ln*(2 if b[7]&1 else 1)].decode(enc)))
        if typ==0xFC:
            chunks=[b];j=idx+1
            while j<len(rec) and rec[j][1]==0x3C:chunks.append(rec[j][2]);j+=1
            ci=0;p=8
            def take(n):
                nonlocal ci,p
                out=b''
                while n:
                    if p==len(chunks[ci]):ci+=1;p=0
                    count=min(n,len(chunks[ci])-p);out+=chunks[ci][p:p+count];p+=count;n-=count
                return out
            for _ in range(U(b,4)):
                ln=H(take(2));flags=take(1)[0];rich=H(take(2)) if flags&8 else 0
                ext=U(take(4)) if flags&4 else 0
                value='';wide=bool(flags&1)
                while ln:
                    if p==len(chunks[ci]):ci+=1;p=0;wide=bool(take(1)[0]&1)
                    count=min(ln,(len(chunks[ci])-p)//(2 if wide else 1));assert count>0
                    value+=take(count*(2 if wide else 1)).decode('utf-16le' if wide else 'latin1');ln-=count
                strings.append(value);take(rich*4+ext)
    def rk(n):
        v=(n>>2)-(1<<30 if n&0x80000000 else 0) if n&2 else struct.unpack('<d',struct.pack('<II',0,n&0xFFFFFFFC))[0]
        return v/100 if n&1 else v
    sheets={name:{} for _,name in bounds};current=None
    for pos,typ,b in rec:
        for at,name in bounds:
            if pos==at: current=name
        if current is None:continue
        c=sheets[current]
        if typ in (0xFD,0x203,0x27E,0x205):
            row,col=H(b),H(b,2)
            val=strings[U(b,6)] if typ==0xFD else struct.unpack_from('<d',b,6)[0] if typ==0x203 else rk(U(b,6)) if typ==0x27E else bool(b[6])
            c[row,col]=val
        elif typ==0xBD:
            row=H(b);col=H(b,2)
            for off in range(4,len(b)-2,6):c[row,col]=rk(U(b,off+2));col+=1
        elif typ==6: raise ValueError('Formula found; extraction requires cached value handling')
    out={}
    for name,c in sheets.items():
        out[name]=[[c.get((r,k)) for k in range(max(k for _,k in c)+1)] for r in range(max(r for r,_ in c)+1)] if c else []
    return out
if __name__=='__main__':
    import sys
    destdir=pathlib.Path('.local/maintenance/temporary/marketing_metrics')
    destdir.mkdir(parents=True,exist_ok=True)
    for path in sys.argv[1:]:
        out=workbook(path);dest=destdir/pathlib.Path(path).with_suffix('.extracted.json').name;dest.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
        print(pathlib.Path(path).name,[(k,len(v),v[:4]) for k,v in out.items()])
