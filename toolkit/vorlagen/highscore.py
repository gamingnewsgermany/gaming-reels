# Vorlage "Arcade-Highscore" (Schwarzviolett/Neon-Gelb/Magenta/Cyan, Scanlines, Mono-Ziffern): INSERT-COIN-Kopfzeile,
# Bildpanel, Hook-Duell (Tage vs Jahre), hochzählende Score-Zähler, Highscore-Tabelle mit NEW-ENTRY, der sich einreiht,
# Stempel, Fortschrittsbalken zur Nr. 1, JA/NEIN-Buttons. Aufruf: python3 highscore.py <vo.mp3> <out_noaudio.mp4> <bilder_dir> [preview.png]
import sys, subprocess, math, os
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
W,H,FPS=1080,1920,30
FB="/usr/share/fonts/opentype/inter/Inter-Black.otf"; FM="/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf"
FA="/usr/share/fonts/truetype/google-fonts/ofl/archivoblack/ArchivoBlack-Regular.ttf"
FO="/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
BG=(16,6,28); BG2=(34,14,58); YE=(255,228,0); PK=(255,46,147); CY=(60,235,255); WH=(255,255,255); INK=(10,4,18); GR=(140,120,170)
VO,OUT,BD=sys.argv[1],sys.argv[2],sys.argv[3]; PREV=sys.argv[4] if len(sys.argv)>4 else None
TOTAL=float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",VO]))
S=[0,5.13,11.17,17.87,20.11,24.13,26.65]
def seg(t):
    i=0
    for k,s in enumerate(S):
        if t>=s: i=k
    return i
_F={}
def F(fn,s):
    k=(fn,int(s))
    if k not in _F: _F[k]=ImageFont.truetype(fn,max(8,int(s)))
    return _F[k]
def fit(d,t,fn,size,maxw):
    while d.textlength(t,font=F(fn,size))>maxw and size>10: size-=3
    return F(fn,size)
def ease(x): x=max(0,min(1,x)); return 1-(1-x)**3
def pop(x):
    if x<=0: return 0
    if x>=1: return 1
    return 1+2.2*(x-1)**3+1.2*(x-1)**2
def cl(v): return max(0.3,min(1.06,v))
PX,PY,PW=60,290,960
def prep(n,col,ctr,tint=None,a=0.2):
    im=Image.open(os.path.join(BD,n)).convert("RGB")
    im=ImageEnhance.Contrast(ImageEnhance.Color(im).enhance(col)).enhance(ctr)
    if tint: im=Image.blend(im,Image.new("RGB",im.size,tint),a)
    r=PW*1.6/im.width; return im.resize((int(im.width*r),int(im.height*r)),Image.LANCZOS)
IM={"arc":prep("arcade.png",1.2,1.2,PK,0.14),"cou":prep("couch_gamer.png",0.9,1.15,CY,0.2),"pok":prep("pokal.png",1.0,1.2,YE,0.12)}
def crop(key,z,ox,oy,pw,ph):
    im=IM[key]; cw=int(im.width*z); ch=int(cw*ph/pw)
    if ch>im.height: ch=im.height; cw=int(ch*pw/ph)
    x=int((im.width-cw)*ox); y=int((im.height-ch)*oy)
    return im.crop((x,y,x+cw,y+ch)).resize((pw,ph),Image.BILINEAR)
def panel_h(i): return {2:0,0:640,4:420}.get(i,560)
def panel(t,i):
    ph=panel_h(i)
    if i==0: k=t/5; return crop("arc",0.55-0.07*k,0.45,0.4,PW,ph)
    if i==1: k=(t-S[1])/6; return crop("cou",0.7-0.1*k,0.2+0.4*k,0.5,PW,ph)
    if i==3: k=(t-S[3])/2.3; return crop("cou",0.5,0.8,0.5-0.2*k,PW,ph)
    if i==4: k=(t-S[4])/4; return crop("pok",0.55-0.08*k,0.5,0.4,PW,ph)
    k=(t-S[i])/3; return crop("arc",0.62,0.8-0.3*k,0.5,PW,ph)
_M={}
def mask(ph):
    if ph not in _M:
        m=Image.new("L",(PW,ph),0); ImageDraw.Draw(m).rounded_rectangle([0,0,PW-1,ph-1],26,fill=255); _M[ph]=m
    return _M[ph]
def stamp(im,text,col,cx,cy,ang,sc,w=820,h=220,size=120):
    if sc<=0: return
    tmp=Image.new("RGBA",(w+40,h+40),(0,0,0,0)); d=ImageDraw.Draw(tmp)
    d.rectangle([10,10,w+29,h+29],outline=col,width=14)
    d.text(((w+40)//2,(h+40)//2),text,font=fit(d,text,FA,size,w-60),fill=col,anchor="mm")
    tmp=tmp.rotate(ang,expand=True,resample=Image.BICUBIC)
    s=max(0.05,sc); tmp=tmp.resize((int(tmp.width*s),int(tmp.height*s)),Image.BILINEAR)
    im.paste(tmp,(int(cx-tmp.width/2),int(cy-tmp.height/2)),tmp)
def header(d,t):
    d.rectangle([0,0,W,240],fill=BG2)
    for x in range(0,W,40): d.rectangle([x,234,x+20,246],fill=PK if (x//40+int(t*6))%2 else YE)
    d.text((60,60),"HIGHSCORE",font=F(FA,84),fill=YE,anchor="lt")
    d.text((62,165),"MEISTVERKAUFTE SPIELE",font=F(FO,36),fill=CY,anchor="lt")
    if int(t*2)%2==0: d.text((W-60,90),"INSERT COIN",font=F(FO,34),fill=PK,anchor="rm")
    d.text((W-60,170),"1UP  2026",font=F(FO,34),fill=WH,anchor="rm")
TABLE0=[("GTA V","235"),("RED DEAD 2","89"),("MARIO KART 8","80"),("SKYRIM","65"),("WITCHER 3","65"),("ANIMAL CROSS.","50,6")]
def table(im,d,t):
    y0=340
    d.text((60,y0),"RANG  SPIEL",font=F(FO,40),fill=GR,anchor="lt"); d.text((W-60,y0),"MIO.",font=F(FO,40),fill=GR,anchor="rt")
    tin=13.0  # GTA VI rutscht auf Platz 6
    rh=168; ytop=y0+70
    rows=list(TABLE0)
    for n,(name,sc) in enumerate(rows):
        appear=S[2]+0.12*n; pv=ease((t-appear)/0.3)
        if pv<=0: continue
        slot=n if n<5 else 5+ease((t-tin)/0.5)
        y=ytop+slot*rh; x=60+int((1-pv)*-400)
        ac=name.startswith("ANIMAL")
        col=(PK if (ac and t>15.4) else WH)
        d.rectangle([x,y,x+960,y+rh-18],fill=BG2,outline=(70,40,110),width=3)
        d.text((x+30,y+(rh-18)/2),f"{slot+1:.0f}." if n<5 or t>tin+0.5 else f"{n+1}.",font=F(FO,62),fill=YE if n==0 else CY,anchor="lm")
        d.text((x+150,y+(rh-18)/2),name,font=fit(d,name,FA,60,560),fill=col,anchor="lm")
        d.text((x+930,y+(rh-18)/2),sc,font=F(FO,62),fill=col,anchor="rm")
    if t>=tin:
        pv=pop((t-tin)/0.4); y=ytop+5*rh; x=60+int((1-min(1,max(0,(t-tin)/0.35)))*600)
        blink=int(t*5)%2==0
        d.rectangle([x,y,x+960,y+rh-18],fill=YE,outline=PK,width=6)
        d.text((x+30,y+(rh-18)/2),"6.",font=F(FO,58),fill=INK,anchor="lm")
        d.text((x+150,y+(rh-18)/2),"GTA VI",font=F(FA,int(60*cl(pv))),fill=INK,anchor="lm")
        d.text((x+930,y+(rh-18)/2),"53",font=F(FO,66),fill=INK,anchor="rm")
        if blink: d.text((x+620,y+(rh-18)/2),"NEW!",font=F(FO,44),fill=PK,anchor="mm")
    d.text((W//2,ytop+7*rh+150),"Vollpreisspiele, Mio. Exemplare (lt. Forbes)",font=F(FM,34),fill=GR,anchor="mt")
    d.text((W//2,ytop+7*rh+200),"GTA VI = Schätzung von Alinea",font=F(FM,34),fill=GR,anchor="mt")
    if t>15.6: stamp(im,"ÜBERHOLT!",PK,W//2+150,ytop+7*rh+40,-6,pop((t-15.6)/0.3)*0.62)
def counter(d,x,y,lab,val,unit,col,prog):
    d.text((x,y),lab,font=F(FO,40),fill=GR,anchor="lt")
    d.text((x,y+55),val(prog),font=F(FO,130),fill=col,anchor="lt")
    d.text((x+20+d.textlength(val(1),font=F(FO,130)),y+125),unit,font=F(FA,58),fill=WH,anchor="ls")
def frame(t):
    i=seg(t); im=Image.new("RGB",(W,H),BG); d=ImageDraw.Draw(im)
    header(d,t)
    if i==2:
        table(im,d,t)
    else:
        ph=panel_h(i); im.paste(panel(t,i),(PX,PY),mask(ph))
        d.rounded_rectangle([PX,PY,PX+PW,PY+ph],26,outline=PK,width=5)
        y0=PY+ph+50
        if i==0:
            # Duell im Panel
            for k,(top,big,col,tc,x) in enumerate([("GTA VI","8 TAGE",YE,INK,80),("ANIMAL C.","6 JAHRE",CY,INK,590)]):
                d.rectangle([x,PY+ph-230,x+410,PY+ph-40],fill=col,outline=INK,width=6)
                d.text((x+205,PY+ph-185),top,font=F(FO,40),fill=tc,anchor="mm")
                d.text((x+205,PY+ph-110),big,font=fit(d,big,FA,84,380),fill=tc,anchor="mm")
            r=62*(1+0.07*math.sin(t*8)); d.ellipse([540-r,PY+ph-135-r,540+r,PY+ph-135+r],fill=PK,outline=INK,width=5)
            d.text((540,PY+ph-135),"VS",font=F(FA,int(r*0.85)),fill=WH,anchor="mm")
            d.text((60,y0+10),"8 TAGE SCHLAGEN",font=fit(d,"8 TAGE SCHLAGEN",FA,100,960),fill=WH,anchor="lt")
            d.text((60,y0+140),"6 JAHRE?!",font=F(FA,120),fill=YE,anchor="lt")
            txt="GTA VI vs. ANIMAL CROSSING"; f=fit(d,txt,FA,int(60*(1+0.03*math.sin(t*6))),880); bw=d.textlength(txt,font=f)+60
            d.rectangle([60,y0+320,60+bw,y0+440],fill=PK); d.text((60+bw/2,y0+380),txt,font=f,fill=WH,anchor="mm")
        elif i==1:
            d.rectangle([60,y0-10,620,y0+60],fill=PK); d.text((80,y0+25),"SCHÄTZUNG: ALINEA",font=F(FO,40),fill=WH,anchor="lm")
            if t>7.33: counter(d,60,y0+110,"KOPIEN",lambda p:f"{int(53*p)}",  "MIO.",YE,ease((t-7.33)/1.2))
            if t>9.0: counter(d,60,y0+380,"UMSATZ",lambda p:f"{4.7*p:.1f}".replace(".",","),"MRD. $",CY,ease((t-9.0)/1.2))
            if t>7.33: d.text((W-60,y0+25),"IN 8 TAGEN",font=F(FO,40),fill=YE,anchor="rm")
        elif i==3:
            d.text((W//2,y0+20),"NUR PS5 + XBOX",font=F(FA,84),fill=WH,anchor="mt")
            for k,(lab,ok) in enumerate([("PS5",True),("XBOX SERIES",True),("PC",False)]):
                y=y0+150+k*130; pv=pop((t-S[3]-0.15*k)/0.3)
                if pv<=0: continue
                d.rectangle([120,y,960,y+105],fill=BG2,outline=CY if ok else PK,width=4)
                d.text((160,y+52),lab,font=F(FA,int(58*cl(pv))),fill=WH,anchor="lm")
                d.text((920,y+52),"✓" if ok else "✗",font=F("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",70),fill=CY if ok else PK,anchor="rm")
            if t>18.6: stamp(im,"OHNE PC!",PK,W//2,PY+280,-7,pop((t-18.6)/0.3)*0.85)
        elif i==4:
            d.text((60,y0),"PLATZ 1 – DER BOSS:",font=F(FO,44),fill=GR,anchor="lt")
            pv=pop((t-S[4]-0.2)/0.4)
            d.text((60,y0+70),"GTA V",font=F(FA,int(150*cl(pv))),fill=YE,anchor="lt")
            if t>22.0:
                pv2=pop((t-22.0)/0.4)
                d.text((W-60,y0+90),"235",font=F(FO,int(150*cl(pv2))),fill=WH,anchor="rt")
                d.text((W-60,y0+260),"MIO.",font=F(FA,54),fill=WH,anchor="rt")
            # Fortschrittsbalken
            by=y0+400; d.text((60,by),"GTA VI: 53 / 235",font=F(FO,44),fill=CY,anchor="lt")
            d.rectangle([60,by+70,1020,by+150],outline=WH,width=5)
            p=ease((t-S[4]-0.5)/1.5)*53/235
            for s in range(int(p*24)): d.rectangle([72+s*39.5,by+82,72+s*39.5+30,by+138],fill=YE)
            if t>21.0: d.text((W-60,by+180),f"{int(round(p*100))} %",font=F(FO,60),fill=YE,anchor="rt")
        elif i==5:
            d.text((W//2,y0+10),"PACKT GTA VI",font=F(FA,96),fill=WH,anchor="mt")
            d.text((W//2,y0+130),"DIE 235 MIO.?",font=F(FA,96),fill=YE,anchor="mt")
            for k,(lab,col,tc,ts) in enumerate([("JA",YE,INK,25.2),("NEIN",PK,WH,25.5)]):
                pv=pop((t-ts)/0.3)
                if pv<=0: continue
                x=80+k*480; sc=min(1.06,pv)
                d.rectangle([x,y0+300,x+440,y0+460],fill=col,outline=WH,width=5)
                d.text((x+220,y0+380),lab,font=F(FA,int(90*sc)),fill=tc,anchor="mm")
            if t>25.8: d.text((W//2,y0+540),"Ab in die Kommentare!",font=F(FB,54),fill=CY,anchor="mm")
        else:
            pv=pop((t-S[6])/0.4)
            d.text((W//2,y0+100),"FOLGE DEM KANAL",font=fit(d,"FOLGE DEM KANAL",FA,int(120*cl(pv)),940),fill=WH,anchor="mm")
            d.text((W//2,y0+250),"FÜR MEHR INFOS!",font=fit(d,"FÜR MEHR INFOS!",FA,int(110*cl(pv)),900),fill=YE,anchor="mm")
            d.rectangle([260,y0+370,820,y0+470],fill=PK)
            d.text((W//2,y0+420),"GAMING FACTS & NEWS",font=F(FB,40),fill=WH,anchor="mm")
            if int(t*2)%2==0: d.text((W//2,y0+560),"CONTINUE? ▶",font=F(FO,48),fill=CY,anchor="mm")
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); od=ImageDraw.Draw(ov)
    for yy in range(0,H,4): od.line([(0,yy),(W,yy)],fill=(0,0,0,28))
    bx,by=(PX+24,PY+24) if i!=2 else (W-280,250+20)
    if i==2: bx,by=W-280,262
    od.rounded_rectangle([bx,by,bx+220,by+52],26,fill=(0,0,0,130)); od.text((bx+110,by+26),"KI-generiert",font=F(FM,32),fill=(255,255,255,215),anchor="mm")
    im=im.convert("RGBA"); im.alpha_composite(ov); return im.convert("RGB")
N=int(TOTAL*FPS)+int(0.8*FPS)
if PREV:
    ts=[0.0,2,6,8.5,10.5,12.5,14,16.5,19,21,23.5,25.9,27.5,28.8]
    sheet=Image.new("RGB",(W//4*7,H//4*2),(0,0,0))
    for k,tt in enumerate(ts): sheet.paste(frame(tt).resize((W//4,H//4)),((k%7)*W//4,(k//7)*H//4))
    sheet.save(PREV); frame(0).save(PREV.replace(".png","_f0.png")); sys.exit()
p=subprocess.Popen(["ffmpeg","-y","-v","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-c:v","libx264","-preset","veryfast","-crf","21","-pix_fmt","yuv420p",OUT],stdin=subprocess.PIPE)
for n in range(N): p.stdin.write(frame(n/FPS).tobytes())
p.stdin.close(); p.wait()
