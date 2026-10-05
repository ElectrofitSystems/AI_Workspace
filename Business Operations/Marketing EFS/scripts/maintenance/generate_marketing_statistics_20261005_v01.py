import pathlib,json,csv,datetime,hashlib,sys,calendar
from read_linkedin_biff import workbook
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak,Flowable
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT,TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from xml.sax.saxutils import escape

ROOT=pathlib.Path.cwd(); SOURCE=ROOT/'input/Technical documentation/Marketing analytics/2026-10-05'
OUT=ROOT/'output/Statistics'; DATA=OUT/'data/2026-10-05'; DATA.mkdir(parents=True,exist_ok=True)
FILES={k:next(SOURCE.glob('*'+k+'*-original.xls')) for k in ['content','followers','visitors']}
ds={k:workbook(p) for k,p in FILES.items()}
date=lambda s:datetime.datetime.strptime(s,'%m/%d/%Y').date().isoformat()
content={date(r[0]):r for r in ds['content']['Metriche'][2:]}
followers={date(r[0]):r for r in ds['followers']['Nuovi follower'][1:]}
visitors={date(r[0]):r for r in ds['visitors']['Statistiche sui visitatori'][1:]}
assert len(content)==len(followers)==len(visitors)==365
assert set(content)==set(followers)==set(visitors)
assert min(content)=='2025-10-04' and max(content)=='2026-10-03'
def agg(start,end):
    keys=[d for d in content if start<=d<=end]
    total=lambda dic,k:int(sum(dic[d][k] for d in keys))
    a={name:total(dic,k) for name,dic,k in [('impressions',content,3),('organic_impressions',content,1),('paid_impressions',content,2),('clicks',content,7),('organic_clicks',content,5),('paid_clicks',content,6),('reactions',content,10),('comments',content,13),('reposts',content,16),('new_followers',followers,4),('page_views',visitors,21),('desktop_views',visitors,19),('mobile_views',visitors,20)]}
    a.update(start=start,end=end,days=len(keys),ctr=100*a['clicks']/a['impressions'] if a['impressions'] else None,interactions=a['clicks']+a['reactions']+a['comments']+a['reposts'])
    a['interaction_rate_internal']=100*a['interactions']/a['impressions'] if a['impressions'] else None
    return a
months=[]
for m in sorted({d[:7] for d in content}):
    keys=[d for d in content if d.startswith(m)];a=agg(min(keys),max(keys));a['month_key']=m;a['complete']=len(keys)==calendar.monthrange(int(m[:4]),int(m[5:]))[1];months.append(a)
aug=next(m for m in months if m['month_key']=='2026-08');sep=next(m for m in months if m['month_key']=='2026-09')
recent=agg('2026-09-04','2026-10-03');annual=agg(min(content),max(content))
assert [recent[k] for k in ['impressions','reactions','comments','reposts','page_views','new_followers']]==[658,16,2,2,130,2]
assert recent['clicks']==32 and sep['impressions']==409 and aug['impressions']==512
postrows=ds['content']['Tutti i post'][2:]
postgroups={}
for r in postrows:postgroups.setdefault(r[1],[]).append(r)
posts=[]
for link,rows in postgroups.items():
    totalrows=[r for r in rows if r[2]=='Totale']; chosen=totalrows[0] if totalrows else next(r for r in rows if r[2]=='Organico')
    organic=next(r for r in rows if r[2]=='Organico');paid=[r for r in rows if r[2]=='Sponsorizzato']
    if totalrows:
        for k in [9,12,14,15,16]:assert chosen[k]==organic[k]+sum(r[k] for r in paid)
    p={'url':link,'published_date':date(chosen[5]),'title':chosen[0].split('\n')[0], 'impressions_snapshot':int(chosen[9]),'organic_impressions_snapshot':int(organic[9]),'paid_impressions_snapshot':int(sum(r[9] for r in paid)),'clicks_snapshot':int(chosen[12]),'reactions_snapshot':int(chosen[14]),'comments_snapshot':int(chosen[15]),'reposts_snapshot':int(chosen[16]),'ctr_snapshot':chosen[13]*100,'linkedin_engagement_rate_snapshot':chosen[18]*100,'video_views':None,'outbound_clicks':None}
    posts.append(p)
posts[0].update(label='Nova Energia · Panda retrofit',reach_snapshot=218,page_visitors_attributed_snapshot=5,new_followers_attributed_snapshot=0)
posts[1].update(label='B2B · Tre sottosistemi',reach_snapshot=78,page_visitors_attributed_snapshot=2,new_followers_attributed_snapshot=0)
posts[2]['label']='Nova Energia · Ordinare la Panda elettrica'
posts[3]['label']='Nova Energia · L’auto che esiste già'
ui={'observed_at_utc':'2026-10-05T10:00:00Z','precision':'approximately; observations collected 09:45–10:05 UTC','total_followers':299,'total_followers_baseline_2026_10_01':299,'net_change_2026_10_01_to_05':0,'monthly_net_change':None,'lost_followers':None,'monthly_ui':{'2026-08':{'page_views':412,'unique_visitors_reported_linkedin':176,'custom_button_clicks':0},'2026-09':{'page_views':93,'unique_visitors_reported_linkedin':35,'custom_button_clicks':0}},'recent_30_days_ui':{'start':'2026-09-04','end':'2026-10-03','unique_visitors_reported_linkedin':46,'custom_button_clicks':0},'search_appearances':{'start':'2026-09-27','end':'2026-10-03','count':51,'change_percent_reported':121.7,'top_keyword':'Electrofit'},'lead_gen_ui':'Ancora nessun lead; limited to LinkedIn lead-generation surface, not company enquiries','competitor_suggestions_30days':[{'name':'Ideas & Motion','followers':657,'new_followers':8,'posts':4,'comments':0,'reactions':37},{'name':'Electrofit (other Page)','followers':279,'new_followers':6,'posts':3,'comments':0,'reactions':17},{'name':'CustoM 2.0 srl','followers':668,'new_followers':3,'posts':0,'comments':0,'reactions':0}],'visitor_job_functions_september_ui':[('Operazioni',15),('Business Development',12),('Ingegneria',10),('Controllo qualità',9),('Ricerca',8)],'commercial_register':{'revision':2,'records_imported':0,'coverage':'inbox and own comments not reconciled; CRM not connected','qualified_leads':None,'sales_opportunities':None},'newsletter':'Local October edition revision_requested; publication and subscribers analytics not verified','website_analytics':'No connected source retrieved; plugin discovery found available but uninstalled providers; no connection created'}
snapshot={'schema_version':1,'organization_id':'103544667','generated_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'observations':ui,'export_period':{'start':'2025-10-04','end':'2026-10-03','timezone':'UTC','content_lag_up_to_days':2},'sources':[{'path':str(p.relative_to(ROOT)).replace('\\','/'),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'byte_size':p.stat().st_size} for p in FILES.values()], 'monthly':months,'recent_30_days':recent,'annual_export_window':annual,'posts_snapshot':posts,'follower_demographics_current':{k:v for k,v in ds['followers'].items() if k!='Nuovi follower'},'visitor_demographics_export_window':{k:v for k,v in ds['visitors'].items() if k!='Statistiche sui visitatori'},'notes':['Daily unique impressions and daily unique visitors are not summed as period reach. Monthly unique values are copied from LinkedIn overview, not claimed independently deduplicated.','Post export totals are snapshots; acquisition-date totals and snapshots are not interchangeable.','New follower daily Follower totali is acquisitions in that day, not cumulative Page total.','Older sponsored campaigns appear in historical data; current authorized content work is organic.','Morning access-blocked report retained; authenticated browser evidence supersedes access status only for this observation.']}
(DATA/'marketing-statistics-2026-10-05-v01.json').write_text(json.dumps(snapshot,ensure_ascii=False,indent=2),encoding='utf-8')
with (DATA/'daily-marketing-20251004-20261003.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.writer(f);w.writerow(['date_utc','organic_impressions','paid_impressions','total_impressions','daily_unique_organic_impressions','organic_clicks','paid_clicks','total_clicks','reactions','comments','reposts','new_followers','page_views_desktop','page_views_mobile','page_views_total','daily_unique_visitors_reported'])
    for d in sorted(content):
        c=content[d];v=visitors[d];w.writerow([d,c[1],c[2],c[3],c[4],c[5],c[6],c[7],c[10],c[13],c[16],followers[d][4],v[19],v[20],v[21],v[24]])
for kind in ['followers','visitors']:
    for idx,(name,rows) in enumerate(list(ds[kind].items())[1:]):
        with (DATA/f'{kind}-demographics-{idx+1:02d}.csv').open('w',encoding='utf-8-sig',newline='') as f:csv.writer(f).writerows(rows)
with (DATA/'posts-snapshot-2026-10-05.csv').open('w',encoding='utf-8-sig',newline='') as f:
    keys=sorted({k for p in posts for k in p});w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(posts)

KIT=ROOT/'input/Brand identity/EFITSYS_Corporate_Design_Kit_3.4_EN/EFITSYS_Corporate_Design_Kit_3.4_EN'
for name,file in [('Barlow','Barlow-Regular.ttf'),('BarlowBold','Barlow-Bold.ttf'),('BarlowCondensed','BarlowCondensed-Bold.ttf')]:pdfmetrics.registerFont(TTFont(name,str(KIT/'08_Reference/Fonts'/file)))
NAVY=colors.HexColor('#0B2348');TEAL=colors.HexColor('#007A8F');CYAN=colors.HexColor('#00A8C6');ICE=colors.HexColor('#F2F6F8');SLATE=colors.HexColor('#60717E');LINE=colors.HexColor('#CED7DE');GRAPH=colors.HexColor('#27343D')
styles={'body':ParagraphStyle('body',fontName='Barlow',fontSize=11,leading=14,textColor=GRAPH,spaceAfter=9),'small':ParagraphStyle('small',fontName='Barlow',fontSize=9.5,leading=12,textColor=SLATE,spaceAfter=7),'title':ParagraphStyle('title',fontName='BarlowCondensed',fontSize=28,leading=30,textColor=NAVY,spaceAfter=10),'h2':ParagraphStyle('h2',fontName='BarlowBold',fontSize=14,leading=17,textColor=NAVY,spaceBefore=12,spaceAfter=8),'cell':ParagraphStyle('cell',fontName='Barlow',fontSize=10.5,leading=13,textColor=GRAPH),'th':ParagraphStyle('th',fontName='BarlowBold',fontSize=10,leading=12,textColor=colors.white),'link':ParagraphStyle('link',fontName='Barlow',fontSize=9.5,leading=13,textColor=TEAL,spaceAfter=5)}
pdfmetrics.registerFontFamily('Barlow',normal='Barlow',bold='BarlowBold',italic='Barlow',boldItalic='BarlowBold')
story=[]
def p(s,sty='body'):return Paragraph(s,styles[sty])
def add(s,sty='body'):story.append(p(s,sty))
def table(rows,widths,compact=False):
    data=[[p(str(c),'th' if i==0 else 'cell') for c in row] for i,row in enumerate(rows)]
    t=Table(data,colWidths=widths,hAlign='LEFT',repeatRows=1)
    pad=3 if compact else 4
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),NAVY),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,ICE]),('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),pad),('BOTTOMPADDING',(0,0),(-1,-1),pad),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),('LINEBELOW',(0,-1),(-1,-1),0.5,LINE)]));story.append(t);story.append(Spacer(1,8))
fmt=lambda n:f'{n:,.0f}'.replace(',','.')
pct=lambda n:f'{n:.2f}%'.replace('.',',')
delta=lambda a,b:'N.D.' if not b else f'{(a/b-1)*100:+.1f}%'.replace('.',',')
W=A4[0]-96
class DailyChart(Flowable):
    def __init__(self):Flowable.__init__(self);self.width=W;self.height=116
    def draw(self):
        c=self.canv;left=28;bottom=21;hh=82;bw=(W-left-4)/30
        c.setStrokeColor(LINE);c.line(left,bottom,W,bottom)
        c.setFont('Barlow',8);c.setFillColor(SLATE)
        for tick in [0,100,200,300]:
            y=bottom+tick/350*hh;c.drawRightString(left-5,y-3,str(tick));c.setStrokeColor(LINE);c.line(left,y,W,y)
        for i in range(30):
            d=f'2026-09-{i+1:02d}';v=content[d][3];c.setFillColor(TEAL if i<29 else CYAN);c.rect(left+i*bw+2,bottom,bw-4,max(v/350*hh,0.5),fill=1,stroke=0)
        c.setFillColor(SLATE);c.drawString(left,5,'1 settembre');c.drawCentredString(left+14*bw,5,'15');c.drawRightString(W,5,'30 settembre')

add('Marketing Statistics','title');add('Settembre 2026 · confronto con agosto · rilevazione 5 ottobre 2026','small')
add('La ripresa dei post a fine settembre genera un picco visibile. Il mese completo resta sotto agosto per impressioni, clic, visite e nuovi follower. Il seguito di ottobre è riportato separatamente.')
table([['KPI del mese completo','Agosto<br/>31 giorni','Settembre<br/>30 giorni','Variazione'],['Impressioni dei contenuti',fmt(aug['impressions']),fmt(sep['impressions']),delta(sep['impressions'],aug['impressions'])],['Clic sui contenuti',27,18,delta(18,27)],['CTR calcolato · clic / impressioni',pct(aug['ctr']),pct(sep['ctr']),'−0,87 punti'],['Reazioni / commenti / repost','1 / 0 / 0','8 / 0 / 2','Campione ridotto'],['Nuovi follower acquisiti',57,1,delta(1,57)],['Visualizzazioni della Pagina',412,93,delta(93,412)],['Visitatori unici riportati da LinkedIn¹',176,35,delta(35,176)],['Clic sul pulsante personalizzato²',0,0,'Nessun clic rilevato']],[240,78,88,W-406])
add('Andamento delle impressioni giornaliere','h2');story.append(DailyChart())
add('Il 30 settembre concentra <b>342 delle 409 impressioni del mese (83,6%)</b>. Due nuovi post pubblicati quel giorno; nessun nuovo post nell’export per agosto. Il campione non consente di attribuire causalità o stabilire un formato vincente.','small')
add('Normalizzazione: impressioni/giorno 16,52 → 13,63 (−17,5%); clic/giorno 0,87 → 0,60 (−31,1%); views Pagina/giorno 13,29 → 3,10 (−76,7%). Export UTC; dati contenuto aggiornati con ritardo fino a 2 giorni.','small')
add('¹ Valori letti direttamente nel riepilogo mensile LinkedIn; non ricostruiti sommando unici giornalieri. ² Il pulsante della Pagina è distinto dai clic dei post.','small')
story.append(PageBreak())

add('Il quadro aggiornato e lo storico','title');add('Finestre distinte per leggere correttamente la crescita','small')
table([['Ultimi 30 giorni · 4 settembre–3 ottobre','Valore'],['Impressioni / clic / CTR','658 / 32 / 4,86%'],['Reazioni / commenti / repost','16 / 2 / 2'],['Visualizzazioni Pagina / visitatori unici LinkedIn','130 / 46'],['Nuovi follower acquisiti / follower totali attuali','2 / 299'],['Visualizzazioni Pagina desktop / mobile','46 / 84 (64,6% mobile)']],[W-130,130])
add('Il totale follower è 299 anche nella baseline del 1° ottobre: saldo osservato 1–5 ottobre <b>0</b>. Questo non determina il saldo netto mensile: follower persi e totali a inizio/fine mese non sono disponibili.','small')
add('Storico disponibile · 4 ottobre 2025–3 ottobre 2026','h2')
table([['Mese UTC','Impressioni<br/>organiche','Impressioni<br/>sponsorizzate','Totale','Nuovi<br/>follower']]+[[m['month_key']+(' *' if not m['complete'] else ''),fmt(m['organic_impressions']),fmt(m['paid_impressions']),fmt(m['impressions']),fmt(m['new_followers'])] for m in months],[85,105,115,100,W-405],compact=True)
add(f"Totale finestra: <b>{fmt(annual['impressions'])} impressioni</b>, {fmt(annual['clicks'])} clic (CTR {pct(annual['ctr'])}), {fmt(annual['reactions'])} reazioni, {annual['comments']} commenti, {annual['reposts']} repost, {annual['new_followers']} nuovi follower e {fmt(annual['page_views'])} views Pagina. Non è crescita netta dei follower.",'small')
add('Le sponsorizzazioni storiche rappresentano il 92,8% delle impressioni, concentrate in febbraio–marzo. Agosto e settembre sono interamente organici. La distinzione evita di confrontare direttamente campagne a pagamento con attività organica. Costi e conversioni pubblicitarie N.D.','small')
add('* Ottobre 2025 copre solo 4–31 ottobre; ottobre 2026 solo 1–3 ottobre. I mesi parziali non sono confrontabili con mesi completi.','small')
story.append(PageBreak())

add('Risultati dei contenuti','title');add('Snapshot osservati il 5 ottobre · distinti dagli aggregati mensili','small')
add('I due post del 30 settembre','h2')
table([['Metrica','Nova Energia<br/>Panda retrofit','B2B<br/>Tre sottosistemi'],['Impressioni',393,163],['Utenti raggiunti · dettaglio post',218,78],['Clic / CTR','16 / 4,07%','13 / 7,98%'],['Reazioni / commenti / repost','13 / 2 / 3','3 / 0 / 1'],['Interazioni / engagement LinkedIn','34 / 8,65%','17 / 10,43%'],['Visite Pagina attribuite al post',5,2],['Follower acquisiti attribuiti al post',0,0]],[W-248,124,124])
add('Nova Energia produce più esposizione e conversazione; B2B ha un CTR maggiore. Sono due osservazioni iniziali, senza prova di conversione commerciale. Gli utenti raggiunti dei due post possono sovrapporsi: non sommarli come audience unica.','small')
add('Dalla baseline del 1° ottobre: Nova Energia passa da 292 a 393 impressioni (+101), da 13 a 16 clic; B2B da 134 a 163 impressioni (+29), da 9 a 13 clic. Sono differenze tra snapshot, non dati del mese di settembre.','small')
add('Contenuti storici nell’export','h2')
table([['Post / data','Organiche','Sponsor.','Totale','Clic / CTR'],['Panda elettrica: ordinazione<br/>17 febbraio 2026','1.872','35.558','37.430','1.954 / 5,22%'],['L’auto che esiste già<br/>8 febbraio 2026','1.723','19.133','20.856','437 / 2,10%']],[180,65,75,75,W-395])
add('L’export contiene righe per campagna, organico e Totale dello stesso post: qui si usa una sola riga Totale. Le righe non vengono sommate due volte. I repost dei due post recenti sono 4 nello snapshot; il riepilogo giornaliero degli ultimi 30 giorni ne riporta 2. Le basi differiscono e non sono forzate a coincidere.','small')
add('Le colonne “Visualizzazioni” video e “Visualizzazioni offsite” dei quattro post sono vuote: N.D., non zero. Le cifre 393 e 163 sono impressioni, non views video. I clic sono clic sul contenuto, non visite certificate al sito.','small')
add('Prossimo riesame: verificare se il CTR B2B resta più alto con altri post comparabili e se le visite Pagina portano richieste tecniche. Nessuna nuova quota editoriale o campagna è attivata da questo report.','body')
story.append(PageBreak())

add('Chi raggiungiamo','title');add('Follower attuali · distribuzioni aggregate dell’export','small')
def topfollowers(key,n=4):
    rows=ds['followers'][key][1:];return sorted(rows,key=lambda r:r[1],reverse=True)[:n]
table([['Località','Follower','% dei 299'],*[ [escape(r[0]),fmt(r[1]),pct(r[1]/299*100)] for r in topfollowers('Località',3)]],[W-140,65,75])
table([['Funzione lavorativa','Follower','% dei 299'],*[ [escape(r[0]),fmt(r[1]),pct(r[1]/299*100)] for r in topfollowers('Funzione lavorativa',3)]],[W-140,65,75])
add('Settori principali: fabbricazione di autoveicoli 32 (10,7%); servizi IT e consulenza IT 31 (10,4%); fabbricazione di apparecchi elettrici, materiali elettrici e componenti elettronici 18 (6,0%).','small')
add('Anzianità: livello base 111 (37,1%), senior 84 (28,1%), amministratore 21 (7,0%). Dimensioni azienda: 11–50 addetti 46 (15,4%); oltre 10.000 addetti 44 (14,7%); 2–10 addetti 36 (12,0%). Le categorie mostrate non coprono necessariamente tutti i follower.','small')
add('Visite e ricerca','h2')
add('A settembre: 35 views desktop e 58 mobile (62,4% mobile). Le principali funzioni nelle views Pagina sono Operazioni 15, Business Development 12 e Ingegneria 10. Sono visualizzazioni segmentate, non persone uniche né lead.','small')
add('Nella settimana 27 settembre–3 ottobre: <b>51 comparse nelle ricerche</b> (+121,7% nel confronto LinkedIn). Principale parola chiave mostrata: “Electrofit”. Il dato settimanale non rappresenta settembre intero.','small')
add('Confronto proposto dalla piattaforma · ultimi 30 giorni','h2')
table([['Pagina suggerita','Nuovi follower','Post','Reazioni'],['Ideas &amp; Motion',8,4,37],['Electrofit · altra Pagina, 279 follower',6,3,17],['CustoM 2.0 srl',3,0,0],['ElectroFit Systems · nostra Pagina',2,2,16]],[W-215,85,55,75])
add('Suggerimenti LinkedIn, non una selezione di concorrenti validata. La Pagina “Electrofit” con 279 follower è diversa dalla nostra. Nessun elenco competitor o impostazione è stato modificato.','small')
story.append(PageBreak())

add('Copertura e aggiornamento mensile','title');add('Cosa è misurato e cosa richiede ancora una fonte','small')
table([['Ambito','Copertura verificata'],['LinkedIn contenuti, follower e visitatori','Tre export originali, 365 date UTC; mesi agosto e settembre completi. KPI UI e dettaglio dei due post recenti.'],['Audience','Località, funzioni, anzianità, settore e dimensioni azienda aggregati. Distribuzioni complete conservate nei CSV locali.'],['Lead LinkedIn','La sezione Lead mostra “Ancora nessun lead”. Si riferisce alla raccolta tramite la relativa superficie LinkedIn, non a tutte le richieste commerciali.'],['Richieste, lead qualificati, opportunità','N.D. Registro commerciale condiviso revisione 2 letto: nessun record importato; inbox e commenti non riconciliati, CRM non collegato. Registro vuoto non prova zero richieste.'],['Sito e conversioni','N.D. Nessuna fonte GA4/Search Console collegata recuperata. Provider disponibili individuati; nessuna installazione o nuova connessione effettuata.'],['Newsletter LinkedIn','Iscritti, views e letture N.D. L’edizione locale di ottobre è in revisione; pubblicazione e analytics non verificati.'],['Pubblicità','Impressioni e clic storici disponibili. Spesa, CPC, CPL e ROAS N.D.']],[145,W-145])
add('Ricorrenza attiva','h2')
add('<b>Primo lunedì del mese, ore 12:00 Europe/Rome.</b> Prossima esecuzione: <b>2 novembre 2026</b>, per il mese di ottobre confrontato con settembre. Il PDF sarà versionato in Outputs/Statistics e il recap tornerà nella chat Master. La review già presente nel passaggio quindicinale viene riutilizzata per evitare doppioni.','body')
add('Metodologia','h2')
add('Ogni KPI conserva fonte, unità e periodo. CTR = somma clic / somma impressioni. L’engagement dei post è quello riportato da LinkedIn; i tassi giornalieri non sono sommati o mediati. Nuovi follower acquisiti e saldo netto restano separati. I totali mensili sono confrontati anche per giorno. Le visualizzazioni Pagina non misurano il traffico del sito.','small')
add('Fonti e tracciabilità','h2')
for name,url in [('Analytics Contenuto','https://www.linkedin.com/company/103544667/admin/analytics/updates/'),('Analytics Follower e Visitatori','https://www.linkedin.com/company/103544667/admin/analytics/followers/'),('Registro commerciale condiviso','https://efitsys.sharepoint.com/sites/Administration/Shared%20Documents/Operations/Marketing/Commercial%20Register/ElectroFit-Commercial-Register.json')]:add(f'<link href="{url}" color="#007A8F">{escape(name)}</link>','link')
add('Originali XLS conservati in input/Technical documentation/Marketing analytics/2026-10-05. Snapshot con hash, serie giornaliere, dati post e distribuzioni complete in output/Statistics/data/2026-10-05. Rilevazione admin del 5 ottobre; il precedente tentativo mattutino bloccato resta archiviato.','small')

def header(c,doc):
    c.saveState();logo=KIT/'02_Logos/EFITSYS_Logo.png';c.drawImage(str(logo),48,A4[1]-52,width=113,height=28,preserveAspectRatio=True,anchor='c',mask='auto')
    c.setFont('Barlow',9);c.setFillColor(SLATE);c.drawRightString(A4[0]-48,A4[1]-40,'STATISTICS  /  05.10.2026')
    c.setStrokeColor(LINE);c.line(48,A4[1]-65,A4[0]-48,A4[1]-65)
    c.setFont('Barlow',9);c.setFillColor(SLATE);c.drawString(48,29,'ElectroFit Systems · Marketing · Uso interno');c.drawRightString(A4[0]-48,29,f'{doc.page}');c.restoreState()
PDF=OUT/'efs-marketing-statistics-2026-10-05-v01.pdf'
assert not (OUT/'efs-marketing-statistics-2026-10-05-v01-delivery.json').exists(),'Delivered revision cannot be overwritten'
doc=SimpleDocTemplate(str(PDF),pagesize=A4,rightMargin=48,leftMargin=48,topMargin=83,bottomMargin=48,title='EFS Marketing Statistics | Settembre 2026',author='ElectroFit Systems',pageCompression=1)
doc.build(story,onFirstPage=header,onLaterPages=header)
print(json.dumps({'pdf':str(PDF),'september':sep,'august':aug,'recent':recent,'annual':annual},ensure_ascii=False))
