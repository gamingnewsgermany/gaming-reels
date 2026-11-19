# Vorlage "Börsen-Ticker" (Schwarz/Grün/Rot): Kurs-Header, Laufband, Chart-Linie, Bildpanel, Kurs-Karten
# Aufruf: python3 boerse.py <vo.mp3> <out_video_noaudio.mp4> <bilder_dir> [preview.png]
import sys, subprocess, math, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
W,H,FPS=1080,1920,30
FB="/usr/share/fonts/opentype/inter/Inter-Black.otf"; FM="/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf"
FA="/usr/share/fonts/truetype/google-fonts/ofl/anton/Anton-Regular.ttf"; FMO="/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
BGC=(8,12,10); GR=(0,230,118); RD=(255,59,92); WH=(255,255,255); GY=(120,135,128); PAN=(18,26,22)
VO,OUT,BD=sys.argv[1],sys.argv[2],sys.argv[3]; PREV=sys.argv[4] if len(sys.argv)>4 else None
TOTAL=float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",VO]))
S=[0,4.66,6.42,12.37,16.32,20.70,25.09,27.53]
def seg(t):
    i=0
    for k,s in enumerate(S):
        if t>=s: i=k
    return i
_F={}
def F(fn,s):
    k=(fn,s)
    if k not in _F: _F[k]=ImageFont.truetype(fn,s)
    return _F[k]
def fit(d,t,fn,size,maxw):
    while d.textlength(t,font=F(fn,size))>maxw: size-=3
    return F(fn,size)
def ease(x): x=max(0,min(1,x)); return 1-(1-x)**3
def pop(x):
    if x<=0: return 0
    if x>=1: return 1
    return 1+2.2*(x-1)**3+1.2*(x-1)**2
# Bilder vorbereiten: getönt, groß für Ken-Burns
def prep(n,tint,boost):
    im=Image.open(os.path.join(BD,n)).convert("RGB")
    im=ImageEnhance.Contrast(ImageEnhance.Color(im).enhance(0.55)).enhance(1.25)
    g=im.convert("L").convert("RGB"); im=Image.blend(im,Image.composite(Image.new("RGB",im.size,tint),g,g.convert("L")),boost)
    r=1180/im.width; return im.resize((int(im.width*r*1.25),int(im.height*r*1.25)),Image.LANCZOS)
IM={"geld":prep("geldregen.png",(0,255,140),0.38),"pc":prep("gaming_pc.png",(255,60,90),0.32),"couch":prep("couch_gamer.png",(0,220,120),0.25)}
PX,PY,PW,PH=60,430,960,500
def panel(t,i):
    key="geld" if i<=3 else ("pc" if i<=5 else "couch")
    im=IM[key]; k=(t-(0 if key=="geld" else S[4] if key=="pc" else S[6]))/10
    z=1.0-0.12*min(1,k) if key!="pc" else 0.88+0.12*min(1,k)
    cw,ch=int(im.width*z*0.8),int(im.width*z*0.8*PH/PW)
    ox={"geld":0.15,"pc":0.6,"couch":0.4}[key]; oy={"geld":0.2,"pc":0.35,"couch":0.5}[key]
    x=int((im.width-cw)*ox); y=int((im.height-ch)*oy)
    return im.crop((x,y,x+cw,y+ch)).resize((PW,PH),Image.BILINEAR)
MASK=Image.new("L",(PW,PH),0); ImageDraw.Draw(MASK).rounded_rectangle([0,0,PW-1,PH-1],34,fill=255)
TICK="  GTA6 ▲ 17,1 MIO. KOPIEN (SCHÄTZUNG)   ●   UMSATZ ▲ 1,65 MRD $   ●   GTA5 DAY ONE 11,2 MIO.   ●   XBOX: 212 GB FREI MACHEN ▼   ●   HYPE-INDEX ▲▲▲  "
def _strip():
    f=F(FMO,36); big=Image.new("L",(6000,70),0); ImageDraw.Draw(big).text((0,35),TICK,font=f,fill=255,anchor="lm")
    tw=big.getbbox()[2]+60
    one=Image.new("RGB",(tw,70),(0,40,22)); ImageDraw.Draw(one).text((0,35),TICK,font=f,fill=GR,anchor="lm")
    st=Image.new("RGB",(tw*3,70)); [st.paste(one,(k*tw,0)) for k in range(3)]; return st,tw
STRIP,TW=_strip()
CH=[0.05,0.12,0.09,0.2,0.18,0.3,0.27,0.42,0.38,0.55,0.5,0.66,0.61,0.78,0.72,0.9,0.86,1.0]
def frame(t):
    i=seg(t); im=Image.new("RGB",(W,H),BGC); d=ImageDraw.Draw(im)
    for y in range(200,1500,100): d.line([(0,y),(W,y)],fill=(16,24,20),width=2)
    # Header
    d.text((60,250),"GTA VI",font=F(FA,64),fill=WH,anchor="lm")
    d.text((265,252),"LAUNCH-BÖRSE",font=F(FMO,40),fill=GR,anchor="lm")
    blink=int(t*2)%2==0
    d.ellipse([W-260,236,W-236,260],fill=RD if blink else (110,20,40)); d.text((W-225,250),"LIVE",font=F(FB,40),fill=WH,anchor="lm")
    # Laufband
    d.rectangle([0,310,W,380],fill=(0,40,22)); off=int(t*170)%TW
    im.paste(STRIP.crop((off,0,off+W,70)),(0,310))
    # Bild-Panel
    p=panel(t,i); im.paste(p,(PX,PY),MASK)
    d.rounded_rectangle([PX,PY,PX+PW,PY+PH],34,outline=GR if i not in (4,5) else RD,width=5)
    # Chart-Linie über Panel
    if i<=3:
        prog=1 if i==0 else 1  # Hook-Frame: Chart schon voll
        pts=[(PX+40+k*(PW-80)/(len(CH)-1),PY+PH-50-v*(PH-120)) for k,v in enumerate(CH)]
        d.line(pts,fill=GR,width=9,joint="curve"); x,y=pts[-1]; r=14+4*math.sin(t*6)
        d.ellipse([x-r,y-r,x+r,y+r],fill=GR)
    y0=990
    if i<=1:
        d.text((W//2,y0+60),"UMSATZ AN TAG 1*",font=F(FMO,44),fill=GY,anchor="mm")
        d.text((W//2,y0+200),"1,65 MRD $",font=fit(d,"1,65 MRD $",FA,230,W-120),fill=GR,anchor="mm")
        s=1+0.06*math.sin(t*5) if i==1 else 1
        st=F(FB,int(112*s)); txt="HYPE-OPFER?"
        bw=d.textlength(txt,font=st)+80
        d.rounded_rectangle([W/2-bw/2,y0+330,W/2+bw/2,y0+330+150],28,fill=RD)
        d.text((W//2,y0+405),txt,font=st,fill=WH,anchor="mm")
    elif i==2:
        a=ease((t-S[2])/1.6); n=17.1*a
        d.text((W//2,y0+60),"VERKAUFTE KOPIEN ZUM START",font=fit(d,"VERKAUFTE KOPIEN ZUM START",FMO,44,W-120),fill=GY,anchor="mm")
        s=f"{n:4.1f} MIO.".replace(".",",",1).strip()
        d.text((W//2,y0+210),s,font=F(FA,220),fill=GR,anchor="mm")
        d.text((W//2,y0+370),"▲ laut Schätzung von Sensor Tower",font=F(FM,46),fill=WH,anchor="mm")
    elif i==3:
        a=ease((t-S[3])/1.2); b=ease((t-S[3]-0.8)/1.2)
        for k,(lab,v,col,p) in enumerate([("GTA V · Day One 2013",11.21,GY,a),("GTA VI · Start (Schätzung)",17.1,GR,b)]):
            y=y0+40+k*200
            d.text((70,y),lab,font=F(FM,50),fill=WH,anchor="lm")
            d.rounded_rectangle([70,y+45,1010,y+145],22,fill=PAN)
            if p>0: d.rounded_rectangle([70,y+45,70+max(40,int(940*p*v/17.1)),y+145],22,fill=col)
            d.text((990,y+95),f"{v:.1f}".replace(".",",")+" MIO.",font=F(FB,54),fill=WH,anchor="rm")
        if t>S[3]+2.2: d.text((W//2,y0+450),"+ ca. 6 Mio. mehr",font=F(FB,64),fill=GR,anchor="mm")
    elif i==4:
        a=ease((t-S[4])/2.5)
        d.text((W//2,y0+50),"XBOX WILL VORHER FREI:",font=F(FMO,46),fill=GY,anchor="mm")
        d.text((W//2,y0+200),"212 GB",font=F(FA,240),fill=RD,anchor="mm")
        d.rounded_rectangle([70,y0+350,1010,y0+430],20,fill=PAN)
        d.rounded_rectangle([70,y0+350,70+max(40,int(940*a)),y0+430],20,fill=RD)
        d.text((W//2,y0+390),f"SPEICHER {int(100*a)} %",font=F(FB,44),fill=WH,anchor="mm")
    elif i==5:
        items=[("SPIELE LÖSCHEN",S[5]),("KONTO LEEREN",S[5]+1.3),("NACHT DURCHZOCKEN",S[5]+2.6)]
        for k,(txt,ts) in enumerate(items):
            pv=pop((t-ts)/0.35)
            if pv<=0: continue
            y=y0+30+k*150; x=70
            d.rounded_rectangle([x,y,1010,y+120],26,fill=PAN,outline=RD if k<2 else GR,width=4)
            d.text((x+70,y+60),"✔" if False else "▼" if k<2 else "▲",font=F(FMO,60),fill=RD if k<2 else GR,anchor="mm")
            f=F(FB,int(64*min(1.15,pv))); d.text((x+140,y+60),txt,font=f,fill=WH,anchor="lm")
    elif i>=6:
        d.text((W//2,y0+60),"DAY ONE GEKAUFT?",font=fit(d,"DAY ONE GEKAUFT?",FA,130,W-120),fill=WH,anchor="mm")
        pv=pop((t-S[6]-0.3)/0.4)
        if pv>0:
            for k,(txt,col) in enumerate([("JA",GR),("NEIN",RD)]):
                cx=300+k*480; s=pv; w2,h2=200*s,80*s
                d.rounded_rectangle([cx-w2,y0+190-h2,cx+w2,y0+190+h2],30,fill=col)
                d.text((cx,y0+190),txt,font=F(FB,int(90*s)),fill=BGC if k==0 else WH,anchor="mm")
        if i==7:
            pf=pop((t-S[7])/0.4)
            if pf>0:
                d.rounded_rectangle([60,y0+320,1020,y0+440],30,fill=WH)
                d.text((W//2,y0+380),"Folge dem Kanal für mehr Infos!",font=fit(d,"Folge dem Kanal für mehr Infos!",FB,int(58*min(1,pf)),900),fill=BGC,anchor="mm")
    # Quelle + KI-Badge
    d.text((60,1500),"*Schätzungen: Sensor Tower · GTA V: Guinness · Xbox-Hinweis",font=F(FM,28),fill=GY,anchor="lm")
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); od=ImageDraw.Draw(ov)
    od.rounded_rectangle([60,150,280,202],26,fill=(0,0,0,150)); od.text((170,176),"KI-generiert",font=F(FM,32),fill=(255,255,255,210),anchor="mm")
    im.paste(ov,(0,0),ov)
    return im
if PREV:
    ts=[0.0,3,5.2,9,14.5,18,23.8,26.3,29]
    sheet=Image.new("RGB",(5*270,2*480))
    for k,tt in enumerate(ts): sheet.paste(frame(tt).resize((270,480)),((k%5)*270,(k//5)*480))
    sheet.save(PREV); frame(0).save(PREV.replace(".png","_f0.png")); sys.exit()
N=int(TOTAL*FPS)+1
p=subprocess.Popen(["ffmpeg","-y","-v","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-c:v","libx264","-preset","veryfast","-crf","21","-pix_fmt","yuv420p",OUT],stdin=subprocess.PIPE)
for n in range(N): p.stdin.write(frame(n/FPS).tobytes())
p.stdin.close(); p.wait()
