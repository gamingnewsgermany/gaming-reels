# Vorlage "Kletter-Tracker/Höhenmesser" (Nachtblau-Indigo/Orange/Cyan/Eigelb): Leiter links mit Kletterpunkt,
# Höhen- & Stoppuhr-Anzeige, Bildpanel, Info-Karten, fallendes Ei + SPLAT-Stempel, Entweder-oder-Buttons
# Aufruf: python3 kletter_tracker.py <vo.mp3> <out_video_noaudio.mp4> <bilder_dir> [preview.png]
import sys, subprocess, math, os
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
W,H,FPS=1080,1920,30
FB="/usr/share/fonts/opentype/inter/Inter-Black.otf"; FM="/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf"
FA="/usr/share/fonts/truetype/google-fonts/ofl/anton/Anton-Regular.ttf"; FMO="/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
TOP=(20,16,58); BOT=(58,22,88); OR=(255,138,31); CY=(63,211,255); YE=(255,214,70); WH=(255,255,255); GY=(170,165,200)
CARD=(34,28,84); PK=(255,70,170); GN=(40,200,120)
VO,OUT,BD=sys.argv[1],sys.argv[2],sys.argv[3]; PREV=sys.argv[4] if len(sys.argv)>4 else None
TOTAL=float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",VO]))+0.6
S=[0,4.19,7.98,10.35,14.29,16.27,21.65,22.52,24.93]
def seg(t):
    i=0
    for k,s in enumerate(S):
        if t>=s: i=k
    return i
_F={}
def F(fn,s):
    s=max(8,int(s)); k=(fn,s)
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
BG=Image.new("RGB",(W,H))
_d=ImageDraw.Draw(BG)
for y in range(H):
    a=y/H; _d.line([(0,y),(W,y)],fill=tuple(int(TOP[c]*(1-a)+BOT[c]*a) for c in range(3)))
import random; random.seed(7)
for _ in range(90):
    x,y=random.randint(0,W),random.randint(0,H); r=random.choice([1,1,2]); _d.ellipse([x-r,y-r,x+r,y+r],fill=(200,200,255))
PX,PY,PW,PH=250,330,780,640
def prep(n,col,ctr,tint=None):
    im=Image.open(os.path.join(BD,n)).convert("RGB")
    im=ImageEnhance.Contrast(ImageEnhance.Color(im).enhance(col)).enhance(ctr)
    if tint: im=Image.blend(im,Image.new("RGB",im.size,tint),0.18)
    r=PH*1.35/im.height; return im.resize((int(im.width*r),int(im.height*r)),Image.LANCZOS)
IM={"sky":prep("skyline.png",1.2,1.1,(60,20,120)),"str":prep("strasse.png",1.1,1.1),"cg":prep("couch_gamer.png",0.9,1.2,(20,60,140))}
def crop(key,z,ox,oy):
    im=IM[key]; ch=int(im.height*z); cw=int(ch*PW/PH)
    if cw>im.width: cw=im.width; ch=int(cw*PH/PW)
    x=int((im.width-cw)*ox); y=int((im.height-ch)*oy)
    return im.crop((x,y,x+cw,y+ch)).resize((PW,PH),Image.BILINEAR)
MASK=Image.new("L",(PW,PH),0); ImageDraw.Draw(MASK).rounded_rectangle([0,0,PW-1,PH-1],28,fill=255)
def panel(t,i):
    if i<=1: k=t/8; return crop("sky",0.62-0.12*k,0.35+0.1*k,0.05)
    if i<=3: k=(t-S[2])/6.3; return crop("cg",0.85-0.15*k,0.5,0.4)
    if i==4: k=(t-S[4])/2; return crop("sky",0.5,0.3,0.2+0.6*ease(k))
    if i==5: k=(t-S[5])/5.4; return crop("str",0.75-0.12*k,0.38,0.6)
    k=(t-S[6])/5; return crop("str",0.9-0.1*k,0.75,0.4)
def egg(d,cx,cy,s,col=(250,246,235)):
    pts=[]
    for a in range(0,360,6):
        r=math.radians(a); x=math.cos(r); y=math.sin(r)
        k=0.78 if y<0 else 1.0
        pts.append((cx+34*s*x*(k if y<0 else 1)*(1-0.12*max(0,-y)),cy+(46 if y<0 else 36)*s*y))
    d.polygon(pts,fill=col,outline=(40,30,20),width=max(2,int(4*s)))
    d.ellipse([cx-16*s,cy-30*s,cx-4*s,cy-12*s],fill=(255,255,255))
def ladder(d,t):
    x1,x2,y1,y2=80,190,330,1560
    d.line([(x1,y1),(x1,y2)],fill=GY,width=8); d.line([(x2,y1),(x2,y2)],fill=GY,width=8)
    for y in range(y1+30,y2,70): d.line([(x1,y),(x2,y)],fill=GY,width=6)
    # Fortschritt: 0..1 über das ganze Video, bis Segment 4 oben
    p=ease(min(1,t/S[4])) if t<S[4] else 1
    cy=y2-(y2-y1-40)*p
    d.line([(x1-14,y2),(x1-14,cy)],fill=OR,width=10)
    d.ellipse([135-30,cy-30,135+30,cy+30],fill=OR,outline=WH,width=5)
    d.text((135,y1-40),"TOP",font=F(FB,34),fill=OR if p>=1 else GY,anchor="mm")
    return p
def header(d):
    d.text((PX,250),"KLETTER-TRACKER",font=F(FA,64),fill=WH,anchor="lm")
    d.rounded_rectangle([W-250,220,W-50,282],30,fill=OR)
    d.text((W-150,251),"GTA VI",font=F(FB,40),fill=TOP,anchor="mm")
def stopwatch(d,t,cx,cy,r):
    p=max(0,min(1,(t-S[2])/2.0)) if t>=S[2] else 0
    secs=int(420*ease(p)) if t<S[3] else 420
    d.ellipse([cx-r,cy-r,cx+r,cy+r],fill=CARD,outline=CY,width=10)
    d.rectangle([cx-22,cy-r-40,cx+22,cy-r-6],fill=CY)
    a=-math.pi/2+2*math.pi*(secs%60)/60
    d.line([(cx,cy),(cx+(r-40)*math.cos(a),cy+(r-40)*math.sin(a))],fill=OR,width=8)
    d.text((cx,cy+r*0.35),f"{secs//60}:{secs%60:02d}",font=F(FA,int(r*0.55)),fill=WH,anchor="mm")
def frame(t):
    i=seg(t); im=BG.copy(); d=ImageDraw.Draw(im)
    header(d); ladder(d,t)
    im.paste(panel(t,i),(PX,PY),MASK); d.rounded_rectangle([PX,PY,PX+PW,PY+PH],28,outline=CY,width=5)
    y0=1020
    if i==0:
        # Nest + Ei im Panel
        s=1+0.05*math.sin(t*6); nx,ny=PX+PW//2,PY+PH//2+70
        d.ellipse([nx-150,ny-20,nx+150,ny+80],fill=(110,70,35),outline=(60,35,15),width=7)
        egg(d,nx,ny-60,2.2*s,(252,246,232))
        d.text((PX,y0+20),"7 MINUTEN LEITER",font=fit(d,"7 MINUTEN LEITER",FA,140,W-PX-50),fill=WH,anchor="lt")
        f=fit(d,"FÜR EIN EI?!",FB,int(110*(1+0.03*math.sin(t*5))),W-PX-120); bw=d.textlength("FÜR EIN EI?!",font=f)+70
        d.rounded_rectangle([PX,y0+200,PX+bw,y0+350],28,fill=OR)
        d.text((PX+bw/2,y0+275),"FÜR EIN EI?!",font=f,fill=TOP,anchor="mm")
        d.text((PX,y0+420),"Genial oder Zeitverschwendung?",font=fit(d,"Genial oder Zeitverschwendung?",FM,48,W-PX-50),fill=CY,anchor="lm")
    elif i==1:
        pv=pop((t-S[1])/0.4)
        d.text((PX,y0+40),"SPIELER ENTDECKEN:",font=F(FMO,44),fill=CY,anchor="lm")
        if pv>0:
            d.rounded_rectangle([PX,y0+100,W-50,y0+400],30,fill=CARD,outline=OR,width=5)
            d.text((PX+40,y0+190),"VOGELNEST",font=F(FA,int(110*min(1.1,pv))),fill=WH,anchor="lm")
            d.text((PX+40,y0+320),"auf einem Funkturm",font=F(FB,int(60*min(1.1,pv))),fill=OR,anchor="lm")
        # Nest im Panel
        nx,ny=PX+PW-180,PY+170
        d.ellipse([nx-120,ny-10,nx+120,ny+70],fill=(110,70,35),outline=(60,35,15),width=6)
        for k,c in enumerate([(255,214,70),(120,220,255),(255,140,190)]): egg(d,nx-70+k*70,ny-5,0.85,c)
    elif i in (2,3):
        stopwatch(d,t,PX+170,y0+205,150)
        if i==2:
            d.text((PX+400,y0+150),"AUFSTIEG",font=F(FMO,44),fill=CY,anchor="lm")
            d.text((PX+400,y0+250),"≈ 7 MIN",font=F(FA,120),fill=WH,anchor="lm")
            d.text((PX+400,y0+340),"laut Spielern",font=F(FM,40),fill=GY,anchor="lm")
        else:
            a=ease((t-S[3])/1.2)
            d.text((PX,y0+400),"VS. LEGENDÄRE LEITER",font=F(FMO,40),fill=CY,anchor="lm")
            for k,(lab,v,col,txt) in enumerate([("MGS3",2,GY,"knapp 2 Min"),("GTA VI",7,OR,"~7 Min")]):
                y=y0+440+k*90
                d.text((PX,y+35),lab,font=F(FB,40),fill=WH,anchor="lm")
                bx=PX+170; d.rounded_rectangle([bx,y,W-50,y+70],20,fill=CARD)
                d.rounded_rectangle([bx,y,bx+max(40,int((W-50-bx)*a*v/7)),y+70],20,fill=col)
                d.text((W-70,y+35),txt,font=F(FB,40),fill=WH,anchor="rm")
            if t>S[3]+1.6:
                pv=pop((t-S[3]-1.6)/0.35)
                st=Image.new("RGBA",(380,150),(0,0,0,0)); sd=ImageDraw.Draw(st)
                sd.rounded_rectangle([5,5,375,145],22,outline=YE+(240,),width=10); sd.text((190,75),"3,5×",font=F(FB,int(90*max(.3,min(1.1,pv)))),fill=YE+(240,),anchor="mm")
                st=st.rotate(10,expand=True,resample=Image.BICUBIC); im.paste(st,(W-st.width-30,y0+20),st)
    elif i==4:
        k=(t-S[4])/(S[5]-S[4])
        ey=PY+60+(PH-120)*k*k; egg(d,PX+PW//2+int(20*math.sin(t*9)),int(ey),1.4,YE)
        d.text((PX,y0+60),"OBEN ANGEKOMMEN:",font=F(FMO,44),fill=CY,anchor="lm")
        d.text((PX,y0+200),"EI WERFEN",font=F(FA,170),fill=WH,anchor="lm")
        d.text((PX,y0+340),"↓ ↓ ↓",font=F(FB,70),fill=OR,anchor="lm")
    elif i==5:
        sp=pop((t-S[5])/0.3)
        if sp>0:
            cx,cy=PX+int(PW*0.42),PY+int(PH*0.48); r=int(110*min(1.15,sp))
            for a in range(0,360,40):
                rr=r*(1.25 if a%80==0 else 0.95); x=cx+rr*math.cos(math.radians(a)); y=cy+rr*0.6*math.sin(math.radians(a))
                d.ellipse([x-30,y-22,x+30,y+22],fill=(252,248,236))
            d.ellipse([cx-r,cy-r*0.6,cx+r,cy+r*0.6],fill=(252,248,236)); d.ellipse([cx-45,cy-30,cx+45,cy+30],fill=YE)
        if t>S[5]+0.3:
            st=Image.new("RGBA",(420,150),(0,0,0,0)); sd=ImageDraw.Draw(st)
            sd.rounded_rectangle([5,5,415,145],22,outline=OR+(240,),width=10); sd.text((210,75),"SPLAT!",font=F(FB,92),fill=OR+(240,),anchor="mm")
            st=st.rotate(-10,expand=True,resample=Image.BICUBIC); im.paste(st,(PX+PW-st.width+10,PY+PH-st.height-10),st)
        d.text((PX,y0+60),"VOLLTREFFER AUF",font=F(FMO,44),fill=CY,anchor="lm")
        rows=[("das Auto eines",S[5]+0.6),("telefonierenden",S[5]+1.6),("Typen im 80er-Look",S[5]+2.8)]
        for k,(txt,ts) in enumerate(rows):
            pv=pop((t-ts)/0.35)
            if pv>0: d.text((PX,y0+150+k*100),txt,font=fit(d,txt,FB,int(72*min(1.08,pv)),W-PX-50),fill=WH if k<2 else OR,anchor="lm")
    elif i==6:
        pv=pop((t-S[6])/0.3)
        d.rounded_rectangle([PX,y0+60,W-50,y0+420],30,fill=CARD,outline=PK,width=6)
        d.text((PX+(W-50-PX)//2,y0+170),"GRUSS AN",font=F(FMO,48),fill=CY,anchor="mm")
        d.text((PX+(W-50-PX)//2,y0+290),"VICE CITY",font=F(FA,int(140*max(.3,min(1.1,pv)))),fill=PK,anchor="mm")
        d.text((PX+(W-50-PX)//2,y0+390),"Anspielung auf GTA: Vice City (2002)",font=fit(d,"Anspielung auf GTA: Vice City (2002)",FM,34,W-PX-110),fill=GY,anchor="mm")
    elif i>=7:
        d.text((PX,y0+40),"7 MINUTEN FÜR EIN EI –",font=fit(d,"7 MINUTEN FÜR EIN EI –",FB,60,W-PX-50),fill=WH,anchor="lm")
        pv=pop((t-S[7])/0.4)
        for k,(txt,col) in enumerate([("GENIAL",GN),("ZEITVERSCHWENDUNG",PK)]):
            if pv<=0: continue
            y=y0+110+k*150; s=min(1.06,pv)
            d.rounded_rectangle([PX,y,W-50,y+125],30,fill=col)
            d.text((PX+(W-50-PX)//2,y+62),txt,font=fit(d,txt,FB,int(80*s),W-PX-110),fill=WH,anchor="mm")
        d.text((PX+(W-50-PX)//2,y0+262),"oder",font=F(FM,0.1+30),fill=WH,anchor="mm") if False else None
        if i==8:
            pf=pop((t-S[8])/0.4)
            if pf>0:
                d.rounded_rectangle([PX,y0+430,W-50,y0+540],30,fill=OR)
                d.text((PX+(W-50-PX)//2,y0+485),"Folge dem Kanal für mehr Infos!",font=fit(d,"Folge dem Kanal für mehr Infos!",FB,int(54*min(1,pf)),W-PX-100),fill=TOP,anchor="mm")
        else:
            d.text((PX,y0+470),"Schreib's in die Kommentare!",font=F(FM,42),fill=CY,anchor="lm")
    d.text((PX,1640),"Quelle: GamingBible (20.11.), Clip von X-Nutzer xGarbett",font=fit(d,"Quelle: GamingBible (20.11.), Clip von X-Nutzer xGarbett",FM,26,W-PX-50),fill=GY,anchor="lm")
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); od=ImageDraw.Draw(ov)
    od.rounded_rectangle([PX,150,PX+220,202],26,fill=(0,0,0,140)); od.text((PX+110,176),"KI-generiert",font=F(FM,32),fill=(255,255,255,225),anchor="mm")
    im.paste(ov,(0,0),ov)
    return im
if PREV:
    ts=[0.0,5.5,9.5,13.2,15.2,19.5,22.0,23.8,26.0,27.2]
    sheet=Image.new("RGB",(5*270,2*480))
    for k,tt in enumerate(ts): sheet.paste(frame(tt).resize((270,480)),((k%5)*270,(k//5)*480))
    sheet.save(PREV); frame(0).save(PREV.replace(".png","_f0.png")); sys.exit()
N=int(TOTAL*FPS)+1
p=subprocess.Popen(["ffmpeg","-y","-v","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-c:v","libx264","-preset","veryfast","-crf","21","-pix_fmt","yuv420p",OUT],stdin=subprocess.PIPE)
for n in range(N): p.stdin.write(frame(n/FPS).tobytes())
p.stdin.close(); p.wait()
