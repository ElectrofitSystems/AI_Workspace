"""Build the eight Efitsys A4 brochures and their combined collection.

Source: content.json. Run with Python with reportlab, Pillow and pypdf installed.
Fonts and original logo are external assets, configurable with command arguments.
No source assets are modified. All coordinates are points measured from page top.
"""
from pathlib import Path
from xml.sax.saxutils import escape
import argparse
import json
import re
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image
from pypdf import PdfReader, PdfWriter

PROJECT = Path(__file__).resolve().parents[2]
BASE = PROJECT / 'output/brochures/applications'
parser = argparse.ArgumentParser()
parser.add_argument('--logo', type=Path, default=PROJECT / 'input/brand/Efitsys_Corporate_Design_Kit/02_Logos/PNG/efitsys-logo-primary-1280w.png')
parser.add_argument('--arial', type=Path, default=Path('C:/Windows/Fonts/arial.ttf'))
parser.add_argument('--arial-bold', type=Path, default=Path('C:/Windows/Fonts/arialbd.ttf'))
args = parser.parse_args()
pdfmetrics.registerFont(TTFont('Arial', str(args.arial)))
pdfmetrics.registerFont(TTFont('Arial-Bold', str(args.arial_bold)))
W, H = A4
M = 56.693
CW = W - 2 * M
C = {k: HexColor(v) for k, v in dict(navy='#0B2348', cyan='#00A8C6', teal='#007A8F', lime='#BDD63A', ice='#F2F6F8', graphite='#27343D', slate='#60717E', white='#FFFFFF').items()}
geometry = []

def rect(c, x, top, w, h, color):
    c.setFillColor(C[color]); c.rect(x, H-top-h, w, h, fill=1, stroke=0)

def para(c, text, x, top, width, size=11, leading=14, font='Arial', color='graphite', limit=None):
    style = ParagraphStyle('p', fontName=font, fontSize=size, leading=leading, textColor=C[color], spaceAfter=0, allowWidows=0, allowOrphans=0)
    p = Paragraph(escape(text).replace('\n', '<br/>'), style)
    pw, ph = p.wrap(width, 1000)
    if limit is not None and ph > limit + .1:
        raise ValueError(f'Overflow: {text[:55]} ({ph} > {limit})')
    p.drawOn(c, x, H-top-ph)
    geometry.append({'text':text[:60], 'x':round(x,2), 'top':round(top,2), 'height':round(ph,2), 'width':round(width,2)})
    return ph

def label(c, text, x, top, color='teal', size=8.7):
    return para(c, text.upper(), x, top, CW, size, size+2, 'Arial-Bold', color)

def page(c, b, index):
    c.setTitle(b['title']); c.setAuthor('Electrofit Systems'); c.setSubject(b['sector'])
    c.setFillColor(C['white']); c.rect(0,0,W,H,fill=1,stroke=0)
    # Use the complete transparent canvas: never crop the logo or its clear space.
    logo_w=166; iw,ih=Image.open(args.logo).size
    c.drawImage(str(args.logo), M-6, H-31-logo_w*ih/iw, logo_w, logo_w*ih/iw, mask='auto')
    para(c, 'Your vision. Our drive.', W-M-207, 46, 207, 11.4, 14, 'Arial-Bold', 'navy')
    c.setStrokeColor(C['ice']); c.setLineWidth(1); c.line(M,H-94,W-M,H-94)
    label(c, 'POWERTRAIN APPLICATIONS / '+b['sector'], M, 111)
    title=b['title'].replace(' for ', '\nfor ', 1)
    para(c,title,M,135,CW,28.5,31.5,'Arial-Bold','navy',65)
    para(c,b['lead'],M,213,CW,11.2,14.7,limit=59)
    rect(c,M,283,CW,43,'ice')
    rect(c,M,283,3,43,'cyan')
    label(c,'Application areas',M+12,291,size=7.8)
    para(c,b['application_line'],M+12,305,CW-24,9.6,12,'Arial','navy',13)
    left_w=278
    for j,v in enumerate(b['benefits']):
        top=344+j*86
        para(c,v['heading'],M,top,left_w,12.7,15.5,'Arial-Bold','navy',17)
        para(c,v['text'],M,top+20,left_w,11,14.1,limit=56.5)
    sx=M+301; sw=CW-301
    rect(c,sx,345,sw,250,'ice')
    rect(c,sx,345,sw,3,'teal')
    para(c,'Your project brief',sx+13,361,sw-26,12.1,15,'Arial-Bold','navy',16)
    para(c,'Requirements to discuss',sx+13,381,sw-26,8.7,11,'Arial','slate',12)
    top=406
    for req in b['requirements']:
        rect(c,sx+13,top+4,3,3,'teal')
        ph=para(c,req,sx+23,top,sw-36,10.2,13.1,limit=40)
        top+=ph+9
    if top>588: raise ValueError('Requirements overflow: '+b['id'])
    label(c,'System architecture',M,611)
    ah=para(c,b['architecture'],M,629,CW,10.6,13.5,limit=67.6)
    if b.get('reference'):
        rt=629+ah+9
        rect(c,M,rt,3,32,'teal')
        para(c,'PANDA / NOVA ENERGIA',M+12,rt,120,7.8,10,'Arial-Bold','teal',10)
        para(c,b['reference'],M+140,rt-1,CW-140,9.2,11.3,limit=34)
    rect(c,M,733,CW,78,'navy')
    rect(c,M,733,3,78,'lime')
    cta=re.sub(r' Start at www\.efitsys\.com\.$','',b['cta'])
    cta=re.sub(r' at www\.efitsys\.com\.$','.',cta)
    para(c,cta,M+14,744,CW-28,10.4,13.4,'Arial','white',27)
    para(c,'www.efitsys.com',M+14,784,142,10.7,13,'Arial-Bold','white',14)
    para(c,'info@efitsys.com',M+178,784,180,10.7,13,'Arial-Bold','white',14)
    c.linkURL('https://www.efitsys.com',(M+14,H-800,M+150,H-782),relative=0)
    c.linkURL('mailto:info@efitsys.com',(M+178,H-800,M+340,H-782),relative=0)
    para(c,'Electrofit Systems',M,823,250,7.3,9,'Arial','slate',10)
    para(c,f'{index:02d} / {b["sector"]}',W-M-210,823,210,7.3,9,'Arial','slate',10)
    c.showPage()

data=json.loads((BASE/'content.json').read_text(encoding='utf-8-sig'))
outputs=[]
for i,b in enumerate(data['brochures'],1):
    dest=BASE/f'efitsys-{b["id"]}-en-v01.pdf'
    c=canvas.Canvas(str(dest),pagesize=A4,pageCompression=1,invariant=1)
    page(c,b,i);c.save();outputs.append(dest)
    assert len(PdfReader(dest).pages)==1
writer=PdfWriter()
for p in output: writer.append(str(p))
writer.add_metadata({'/Title':'Electrofit Systems - Electric Powertrain Applications','/Author':'Electrofit Systems','/Subject':'Eight application brochures'})
collection=BASE/'efitsys-powertrain-applications-en-v01.pdf'
with collection.open('wb') as f: writer.write(f)
assert len(PdfReader(collection).pages)==8
(BASE/'layout-checks.json').write_text(json.dumps({'page_size':'A4','font':'Arial embedded','pages':8,'layout_blocks':geometry},indent=2),encoding='utf-8')
print('Created 8 single-page A4 PDFs and one 8-page collection.')
