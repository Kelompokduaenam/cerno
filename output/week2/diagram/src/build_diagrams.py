from pathlib import Path
import xml.etree.ElementTree as ET
import math
from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parents[1]
OUT.mkdir(parents=True, exist_ok=True)
S = 1.5
INK = '#243746'
BLUE = '#EAF2F8'
TEAL = '#E9F4F1'
GRAY = '#F3F5F7'

def font(size, bold=False, mono=False):
    f = 'consola.ttf' if mono else ('arialbd.ttf' if bold else 'arial.ttf')
    return ImageFont.truetype('C:/Windows/Fonts/' + f, round(size*S))

class Page:
    def __init__(self, name, width, height, subtitle):
        self.name, self.w, self.h = name, width, height
        self.nodes, self.edges = {}, []
        self.label('title', 'CERNO  /  ' + name, 40, 25, width-80, 45, 28, True)
        self.label('subtitle', subtitle, 40, 76, width-80, 32, 17)

    def node(self, id, text, x, y, w, h, kind='rect', fill='white', size=18, bold=False, **kw):
        assert id not in self.nodes, id
        self.nodes[id] = dict(id=id, text=text, x=x, y=y, w=w, h=h,
                              kind=kind, fill=fill, size=size, bold=bold, **kw)
        return id

    def label(self,id,text,x,y,w,h,size=17,bold=False):
        return self.node(id,text,x,y,w,h,'text',size=size,bold=bold)

    def uc(self,id,text,x,y,w=280,h=100):
        return self.node(id,id.upper()+'\n'+text,x,y,w,h,'ellipse',BLUE,19)

    def actor(self,id,text,x,y):
        return self.node(id,text,x,y,64,100,'actor',size=18)

    def note(self,id,text,x,y,w,h):
        return self.node(id,text,x,y,w,h,'note',GRAY,17)

    def table(self,id,fields,x,y,w=350,ref=False):
        h = 48 + 29*len(fields)
        return self.node(id,id,x,y,w,h,'table',TEAL if not ref else GRAY,17,
                         fields=fields,ref=ref)

    def point(self,id,side,offset=.5):
        n=self.nodes[id]; x,y,w,h=n['x'],n['y'],n['w'],n['h']
        return {'L':(x,y+h*offset),'R':(x+w,y+h*offset),
                'T':(x+w*offset,y),'B':(x+w*offset,y+h)}[side]

    def edge(self,source,target,ss='R',ts='L',so=.5,to=.5,via=(),kind='assoc',label='',lp=None,cards=None):
        points=[self.point(source,ss,so),*via,self.point(target,ts,to)]
        self.edges.append(dict(source=source,target=target,ss=ss,ts=ts,so=so,to=to,
                               points=points,kind=kind,cards=cards))
        if label:
            x,y=lp
            width=max(font(16).getlength(t)/S for t in label.split('\n'))+10
            height=20*len(label.split('\n'))+8
            self.node('edge_label_'+str(len(self.edges)),label,x,y,width,height,'edge_label',size=16)

    def xml(self):
        model=ET.Element('mxGraphModel',dx=str(self.w),dy=str(self.h),grid='1',gridSize='10',
             guides='1',tooltips='1',connect='1',arrows='1',fold='1',page='1',pageScale='1',
             pageWidth=str(self.w),pageHeight=str(self.h),math='0',shadow='0')
        root=ET.SubElement(model,'root')
        ET.SubElement(root,'mxCell',id='0')
        ET.SubElement(root,'mxCell',id='1',parent='0')
        for n in self.nodes.values():
            k=n['kind']
            style=f'whiteSpace=wrap;html=0;fontFamily=Arial;fontSize={n["size"]};fontColor={INK};strokeColor={INK};strokeWidth=1.5;fillColor={n["fill"]};'
            if n['bold']: style+='fontStyle=1;'
            if k=='ellipse': style+='ellipse;'
            if k=='actor': style+='shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;align=center;'
            if k in ['text','edge_label']:
                style+='text;strokeColor=none;fillColor='+('white' if k=='edge_label' else 'none')+';align=left;verticalAlign=middle;'
            if k=='note': style+='align=left;verticalAlign=top;spacing=16;'
            if k=='boundary': style+='fillColor=none;align=left;verticalAlign=top;spacing=15;fontStyle=1;'
            if k=='table':
                # Native container + editable header/attribute rows.
                style='group;'
                value=''
            else: value=n['text']
            c=ET.SubElement(root,'mxCell',id=n['id'],value=value,style=style,vertex='1',parent='1')
            ET.SubElement(c,'mxGeometry',x=str(n['x']),y=str(n['y']),width=str(n['w']),height=str(n['h']),**{'as':'geometry'})
            if k=='table':
                c=ET.SubElement(root,'mxCell',id=n['id']+'_head',value=n['id']+('  [referensi]' if n['ref'] else ''),
                    style=f'rounded=0;whiteSpace=wrap;html=0;fillColor={n["fill"]};strokeColor={INK};fontFamily=Arial;fontSize=19;fontStyle=1;align=left;spacingLeft=14;',vertex='1',parent=n['id'])
                ET.SubElement(c,'mxGeometry',x='0',y='0',width=str(n['w']),height='48',**{'as':'geometry'})
                for i,field in enumerate(n['fields']):
                    c=ET.SubElement(root,'mxCell',id=n['id']+'_f'+str(i),value=field,
                        style=f'rounded=0;whiteSpace=wrap;html=0;fillColor=white;strokeColor=#D7DFE4;fontColor={INK};fontFamily=Consolas;fontSize=17;align=left;spacingLeft=14;',vertex='1',parent=n['id'])
                    ET.SubElement(c,'mxGeometry',x='0',y=str(48+29*i),width=str(n['w']),height='29',**{'as':'geometry'})
        def port(side,off):
            return {'L':(0,off),'R':(1,off),'T':(off,0),'B':(off,1)}[side]
        arrow={'1':'ERmandOne','0..1':'ERzeroToOne','0..*':'ERzeroToMany','1..*':'ERoneToMany'}
        for i,e in enumerate(self.edges):
            a,b=port(e['ss'],e['so']),port(e['ts'],e['to'])
            style=f'edgeStyle=none;rounded=0;html=0;strokeColor={INK};strokeWidth=1.5;startArrow=none;endArrow=none;exitX={a[0]};exitY={a[1]};exitPerimeter=0;entryX={b[0]};entryY={b[1]};entryPerimeter=0;'
            if e['kind'] in ['include','extend']:style+='dashed=1;endArrow=open;endFill=0;'
            if e['kind']=='general':style+='endArrow=block;endFill=0;endSize=18;'
            if e['cards']:
                style+=f'startArrow={arrow[e["cards"][0]]};endArrow={arrow[e["cards"][1]]};startFill=0;endFill=0;startSize=18;endSize=18;'
            c=ET.SubElement(root,'mxCell',id='rel_'+str(i),value='',style=style,edge='1',parent='1',source=e['source'],target=e['target'])
            g=ET.SubElement(c,'mxGeometry',relative='1',**{'as':'geometry'})
            if len(e['points'])>2:
                arr=ET.SubElement(g,'Array',**{'as':'points'})
                for x,y in e['points'][1:-1]: ET.SubElement(arr,'mxPoint',x=str(x),y=str(y))
        # Edge label boxes stay above connectors, without covering adjacent nodes.
        for c in list(root):
            if c.get('id','').startswith('edge_label_'):
                root.remove(c);root.append(c)
        return model

    def render(self, filename):
        im=Image.new('RGB',(round(self.w*S),round(self.h*S)),'white');d=ImageDraw.Draw(im)
        def box(n):return tuple(round(t*S) for t in (n['x'],n['y'],n['x']+n['w'],n['y']+n['h']))
        def line(p,fill=INK,width=2):d.line([(round(x*S),round(y*S)) for x,y in p],fill=fill,width=round(width*S))
        def text(t,x,y,w,h,size=18,bold=False,align='center',mono=False,fill=INK):
            f=font(size,bold,mono);lh=size*1.24
            lines=t.split('\n')
            assert lh*len(lines) <= h+2, (filename,t,'text height',lh*len(lines),h)
            yy=y if align=='lefttop' else y+(h-lh*len(lines))/2
            for s in lines:
                tw=d.textlength(s,font=f)/S
                assert tw <= w+1, (filename,s,tw,w)
                xx=x if align.startswith('left') else x+(w-tw)/2
                d.text((round(xx*S),round(yy*S)),s,font=f,fill=fill)
                yy+=lh
        # Background boundary first, relations second, normal nodes on top.
        for n in self.nodes.values():
            if n['kind']=='boundary':
                d.rectangle(box(n),outline=INK,width=2)
                text(n['text'],n['x']+16,n['y']+12,n['w']-32,35,20,True,'lefttop')
        def marker(p,q,card):
            dx,dy=q[0]-p[0],q[1]-p[1];length=math.hypot(dx,dy);u=(dx/length,dy/length);v=(-u[1],u[0])
            def at(a,b=0):return(p[0]+u[0]*a+v[0]*b,p[1]+u[1]*a+v[1]*b)
            if card.endswith('*'):
                for z in [-8,0,8]:line([at(0,z),at(15,0)])
                dist=24
            else:
                line([at(8,-8),at(8,8)]);dist=18
            if card.startswith('0'):
                cx,cy=at(dist)
                d.ellipse(((cx-5)*S,(cy-5)*S,(cx+5)*S,(cy+5)*S),fill='white',outline=INK,width=2)
            else:line([at(dist,-8),at(dist,8)])
        for e in self.edges:
            pts=e['points']
            if e['kind'] in ['include','extend']:
                for a,b in zip(pts,pts[1:]):
                    dist=math.dist(a,b)
                    for step in range(0,math.ceil(dist),12):
                        f0=step/dist; f1=min(step+7,dist)/dist
                        line([(a[0]+(b[0]-a[0])*f0,a[1]+(b[1]-a[1])*f0),
                              (a[0]+(b[0]-a[0])*f1,a[1]+(b[1]-a[1])*f1)])
            else:line(pts)
            if e['kind'] in ['include','extend','general']:
                p,q=pts[-1],pts[-2];dx,dy=q[0]-p[0],q[1]-p[1];dist=math.hypot(dx,dy);ux,uy=dx/dist,dy/dist
                a=(p[0]+ux*18-uy*8,p[1]+uy*18+ux*8);b=(p[0]+ux*18+uy*8,p[1]+uy*18-ux*8)
                if e['kind']=='general':d.polygon([(x*S,y*S) for x,y in [p,a,b]],fill='white',outline=INK,width=2)
                else:line([a,p,b])
            if e['cards']:
                marker(pts[0],pts[1],e['cards'][0]);marker(pts[-1],pts[-2],e['cards'][1])
        for n in self.nodes.values():
            k=n['kind'];x,y,w,h=n['x'],n['y'],n['w'],n['h']
            if k=='boundary':continue
            if k=='actor':
                d.ellipse(((x+20)*S,y*S,(x+44)*S,(y+24)*S),fill='white',outline=INK,width=3)
                line([(x+32,y+24),(x+32,y+65)])
                line([(x,y+42),(x+64,y+42)])
                line([(x+8,y+100),(x+32,y+65),(x+56,y+100)])
                text(n['text'],x-95,y+109,w+190,65,n['size'])
            elif k=='table':
                d.rectangle(box(n),fill='white',outline=INK,width=2)
                d.rectangle((x*S,y*S,(x+w)*S,(y+48)*S),fill=n['fill'],outline=INK,width=2)
                text(n['id']+('  [referensi]' if n['ref'] else ''),x+14,y+8,w-28,30,19,True,'left')
                for i,f in enumerate(n['fields']):
                    yy=y+48+29*i
                    if i:line([(x,yy),(x+w,yy)],'#D7DFE4',1)
                    text(f,x+14,yy+3,w-28,24,17,align='left',mono=True)
            elif k in ['text','edge_label']:
                if k=='edge_label':d.rectangle(box(n),fill='white')
                text(n['text'],x,y,w,h,n['size'],n['bold'],'left')
            else:
                if k=='ellipse':d.ellipse(box(n),fill=n['fill'],outline=INK,width=2)
                else:d.rectangle(box(n),fill=n['fill'],outline='#CAD5DE',width=2)
                if k=='note':text(n['text'],x+16,y+16,w-32,h-32,n['size'],align='lefttop')
                else:text(n['text'],x,y,w,h,n['size'],n['bold'])
        im.save(OUT/filename)

def save_drawio(filename,pages):
    root=ET.Element('mxfile',host='app.diagrams.net',type='device',version='24.7.17')
    for i,p in enumerate(pages):
        diagram=ET.SubElement(root,'diagram',id='page-'+str(i+1),name=p.name)
        diagram.append(p.xml())
    ET.indent(root)
    ET.ElementTree(root).write(OUT/filename,encoding='utf-8',xml_declaration=True)
    # Check actual saved native diagram references and geometry.
    loaded=ET.parse(OUT/filename)
    for diagram in loaded.getroot().findall('diagram'):
        cells=diagram.findall('.//mxCell');ids=[c.get('id') for c in cells]
        assert len(ids)==len(set(ids))
        for c in cells:
            for attr in ['parent','source','target']:
                if c.get(attr):assert c.get(attr) in ids,(filename,c.attrib)
    print(filename, len(pages),'pages; XML references valid')


u1=Page('Use Case 01 - Analisis',1600,1220,'Interaksi analisis teks, URL, screenshot, hasil, dan feedback | UML use case')
u1.node('system','Sistem CERNO',270,125,1060,925,'boundary',size=20)
u1.actor('public','Pengguna umum\n(tanpa / dengan akun)',90,500)
u1.actor('provider','Provider\nthreat intelligence',1440,335)
u1.uc('uc01','Menganalisis teks pesan',390,215)
u1.uc('uc02','Menganalisis URL',390,385)
u1.uc('uc03','Menganalisis screenshot',390,565)
u1.uc('uc04','Meninjau dan mengoreksi\nteks hasil OCR',950,565)
u1.uc('uc05','Melihat hasil dan\nrekomendasi tindakan',390,770)
u1.uc('uc06','Memberikan feedback',390,925)
u1.uc('uc07','Memeriksa reputasi URL',950,335)
for id in ['uc01','uc02','uc03','uc05','uc06']:
    u1.edge('public',id,so=.42)
u1.edge('uc03','uc04',kind='include',label='<<include>>',lp=(755,579))
u1.edge('uc02','uc07',via=[(810,427),(810,377)],kind='include',label='<<include>>',lp=(710,425))
u1.edge('uc07','uc01',ss='T',ts='R',via=[(1090,257)],kind='extend',label='<<extend>>\n[URL ditemukan]',lp=(760,199))
u1.edge('provider','uc07',ss='L',ts='R',so=.42)
u1.edge('uc06','uc05',ss='T',ts='B',kind='extend',label='<<extend>>\n[pengguna memilih feedback]',lp=(552,875))
u1.note('analysis_note','Analisis teks / screenshot mencakup:\n- redaksi data sensitif dan ekstraksi URL;\n- penilaian teks, URL, dan sinyal komunitas;\n- skor, indikator, dan rekomendasi.\n\nOCR ditinjau sebelum analisis final.\nPemeriksaan URL tidak membuka situs.',870,725,405,230)
u1.note('legend','Garis biasa: asosiasi aktor. Panah putus-putus: include (wajib) atau extend (bersyarat).\nPengguna berakun mewarisi akses umum pada halaman 02. Provider gagal: tampilkan pemeriksaan tidak lengkap.\nCERNO menilai risiko; tidak mengklasifikasikan jenis scam atau memberi jaminan aman.',270,1080,1060,108)

u2=Page('Use Case 02 - Akun dan Administrasi',1720,1430,'Lanjutan sistem yang sama | Riwayat pribadi, laporan anonim, moderasi, dan monitoring')
u2.node('system','Sistem CERNO',280,135,1150,1130,'boundary',size=20)
u2.actor('public','Pengguna umum',95,280)
u2.actor('member','Pengguna berakun',95,760)
u2.actor('moderator','Moderator',1550,860)
u2.actor('admin','Admin',1550,1140)
u2.uc('uc08','Mendaftar akun',420,235)
u2.uc('uc09','Login / logout',420,400)
u2.uc('uc10','Menyimpan hasil\nke riwayat pribadi',420,675)
u2.uc('uc11','Melihat riwayat\ndan detail analisis',420,865)
u2.uc('uc12','Menghapus riwayat pribadi',420,1055)
u2.uc('uc13','Mengirim laporan anonim',1010,235)
u2.uc('uc14','Memoderasi laporan\nkomunitas',1010,795)
u2.uc('uc16','Meninjau feedback\npengguna',1010,970)
u2.uc('uc15','Memantau dashboard\noperasional dan model',1010,1150)
u2.edge('public','uc08',so=.42)
u2.edge('public','uc09',so=.42)
u2.edge('public','uc13',ss='T',ts='T',via=[(127,180),(1150,180)])
u2.edge('member','public',ss='T',ts='L',to=.42,via=[(127,710),(40,710),(40,322)],kind='general')
for id in ['uc10','uc11','uc12']:u2.edge('member',id,so=.42)
u2.edge('moderator','uc14',ss='L',ts='R',so=.42)
u2.edge('moderator','uc16',ss='L',ts='R',so=.42)
u2.edge('admin','moderator',ss='T',ts='R',to=.42,via=[(1582,1090),(1670,1090),(1670,902)],kind='general')
u2.edge('admin','uc15',ss='L',ts='R',so=.42)
u2.note('report_note','Laporan anonim:\n- tanpa akun dan tanpa public feed;\n- redaksi, deduplikasi, dan rate limit;\n- konfirmasi pengiriman / status;\n- laporan valid menjadi sinyal tambahan.\n\nModerasi: accepted, rejected, duplicate,\natau needs_review; awalnya pending.',950,405,425,230)
u2.note('account_note','Riwayat: login, persetujuan simpan,\ndan akses hanya ke data milik sendiri.\nAdmin / moderator: wajib login\ndan lolos pemeriksaan role.',950,650,425,132)
u2.note('legend','Panah segitiga kosong: generalisasi, mengarah ke aktor yang diwarisi.\nAdmin mewarisi akses moderasi. Pengguna berakun mewarisi analisis umum (halaman 01).\nDashboard: statistik analisis, latency, kegagalan provider/OCR, versi model, dan metrik evaluasi.',280,1295,1150,105)

e1=Page('ERD 01 - Analisis dan Riwayat',1880,1540,'Model logis relasional | PK = primary key, FK = foreign key, UQ = unique, ? = nullable')
e1.table('users',['PK id : uuid','UQ email : varchar','password_hash : varchar','role : user|moderator|admin','created_at : timestamptz'],65,155,350)
e1.table('model_versions',['PK id : uuid','model_name : varchar','version : varchar','model_kind : text|url','dataset_version : varchar','metrics : jsonb','deployment_status : varchar'],1370,155,430)
e1.table('analysis_models',['PK,FK analysis_id : uuid','PK,FK model_version_id : uuid','component_score : numeric?'],720,180,410)
e1.table('analyses',['PK id : uuid','FK user_id : uuid?','input_type : text|url|screenshot','status : varchar','risk_score : numeric?','risk_level : low|suspicious|high?','recommended_actions : jsonb','consent_to_store : boolean','consent_to_train : boolean','created_at : timestamptz','expires_at : timestamptz','processing_time_ms : integer?'],720,490,410)
e1.table('analysis_inputs',['PK,FK analysis_id : uuid','redacted_text : text?','input_url_hash : varchar?','retained_at : timestamptz','expires_at : timestamptz'],65,555,350)
e1.table('evidences',['PK id : uuid','FK analysis_id : uuid','evidence_type : varchar','matched_span_redacted : text?','description : text','severity : varchar','confidence : numeric?'],1370,540,430)
e1.table('url_results',['PK id : uuid','FK analysis_id : uuid','normalized_url_hash : varchar','registered_domain : varchar','lexical_score : numeric?','threat_status : varchar','provider : varchar?','checked_at : timestamptz'],1370,990,430)
e1.table('feedback',['PK id : uuid','FK analysis_id : uuid','user_verdict : varchar','helpful : boolean?','comment_redacted : text?','created_at : timestamptz'],65,1060,350)
e1.table('ocr_jobs',['PK id : uuid','FK,UQ analysis_id : uuid?','object_key : varchar?','access_token_hash : varchar','status : varchar','redacted_extracted_text : text?','ocr_engine_version : varchar','created_at : timestamptz','completed_at : timestamptz?','expires_at : timestamptz'],720,1020,410)
e1.edge('users','analyses',so=.55,to=.14,via=[(555,267.15),(555,545.44)],cards=('0..1','0..*'),label='pemilik (opsional)',lp=(460,410))
e1.edge('analyses','analysis_inputs',ss='L',ts='R',so=.52,to=.5,cards=('1','0..1'))
e1.edge('analyses','evidences',so=.26,to=.45,cards=('1','0..*'))
e1.edge('analyses','url_results',so=.78,to=.25,via=[(1250,798.88),(1250,1060)],cards=('1','0..*'))
e1.edge('analyses','feedback',ss='L',ts='R',so=.84,to=.45,via=[(520,822.64),(520,1159.9)],cards=('1','0..*'))
e1.edge('analyses','ocr_jobs',ss='B',ts='T',cards=('0..1','0..1'))
e1.edge('analyses','analysis_models',ss='T',ts='B',cards=('1','0..*'))
e1.edge('model_versions','analysis_models',ss='L',ts='R',so=.45,cards=('1','0..*'))
e1.note('note','Aturan: skor 0..100; nilai hasil boleh kosong saat belum selesai. Model yang dipakai dicatat pada analysis_models.\nAnalisis anonim memiliki user_id NULL. Riwayat hanya untuk pemilik yang menyetujui penyimpanan.\nOCR job dapat belum terkait analisis; satu job menghasilkan paling banyak satu analisis. Screenshot disimpan sementara.\nNotasi crow\'s foot: dua garis = 1; lingkaran + garis = 0..1; lingkaran + kaki tiga = 0..*. Lanjutan komunitas: halaman 02.',65,1385,1735,125)

e2=Page('ERD 02 - Komunitas dan Moderasi',1880,1500,'Lanjutan ERD 01 | Tabel referensi adalah entitas yang sama, bukan tabel baru')
e2.table('users',['PK id : uuid','role : user|moderator|admin'],65,195,350,True)
e2.table('report_moderations',['PK id : uuid','FK report_id : uuid','FK moderator_id : uuid','previous_status : varchar','new_status : varchar','reason : text','created_at : timestamptz'],720,195,410)
e2.table('audit_logs',['PK id : uuid','FK actor_user_id : uuid?','actor_type : user|system','action : varchar','resource_type : varchar','resource_id : uuid?','metadata_redacted : jsonb','created_at : timestamptz'],1380,195,430)
e2.table('community_targets',['PK id : uuid','target_type : text|url|domain','target_fingerprint : varchar','normalized_domain : varchar?','unique_report_count : integer','accepted_report_count : integer','rejected_report_count : integer','community_score : numeric','first_reported_at : timestamptz','last_reported_at : timestamptz'],65,715,410)
e2.table('anonymous_reports',['PK id : uuid','FK community_target_id : uuid','reporter_token_hash : varchar','network_fingerprint_hash : varchar?','network_expires_at : timestamptz?','redacted_text : text?','reason_redacted : text','moderation_status : varchar','consent_redacted_use : boolean','dedupe_window_start : timestamptz','created_at : timestamptz'],720,720,440)
e2.table('analyses',['PK id : uuid','input_type : text|url|screenshot','created_at : timestamptz'],1380,655,430,True)
e2.table('analysis_community_matches',['PK,FK analysis_id : uuid','PK,FK community_target_id : uuid','match_method : varchar','score_snapshot : numeric','accepted_count_snapshot : integer','checked_at : timestamptz'],1380,970,430)
e2.edge('users','report_moderations',cards=('1','0..*'))
e2.edge('users','audit_logs',ss='T',ts='T',via=[(240,145),(1595,145)],cards=('0..1','0..*'))
e2.edge('anonymous_reports','report_moderations',ss='T',ts='B',so=.47,to=.5,cards=('1','0..*'),label='riwayat perubahan status',lp=(955,530))
e2.edge('community_targets','anonymous_reports',to=.45,cards=('1','0..*'))
e2.edge('analyses','analysis_community_matches',ss='B',ts='T',cards=('1','0..*'))
e2.edge('community_targets','analysis_community_matches',ss='B',ts='B',via=[(270,1240),(1595,1240)],cards=('1','0..*'))
e2.note('note','Constraint: UNIQUE(target_type, target_fingerprint). Satu laporan menunjuk tepat satu target.\nDeduplikasi: UNIQUE(community_target_id, reporter_token_hash, dedupe_window_start); pengiriman ulang tidak menambah hitungan.\nTidak ada FK akun pada laporan anonim. moderator_id wajib memiliki role moderator/admin. Perubahan status dan audit bersifat atomik.\nAgregat berasal dari laporan valid; snapshot menyimpan sinyal saat analisis dibuat. Tidak ada public accusation feed.\nresource_id pada audit_logs adalah referensi polimorfik, bukan FK ke semua tabel. Metadata tidak memuat pesan/screenshot mentah.',65,1330,1745,145)

save_drawio('CERNO-Use-Case.drawio',[u1,u2])
save_drawio('CERNO-ERD.drawio',[e1,e2])
for p,name in [(u1,'use-case-01-analisis.png'),(u2,'use-case-02-akun-administrasi.png'),
               (e1,'erd-01-analisis-riwayat.png'),(e2,'erd-02-komunitas-moderasi.png')]:
    p.render(name)
    print(name,'rendered')
