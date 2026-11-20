# Vorlage "Sehtest/Optiker" (Creme/Navy/Rot/Senf): Sehtafel-Header, verpixeltes Bildpanel mit Lupe, Befund-Karten, JA/NEIN
# Aufruf: python3 sehtest.py <vo.mp3> <out_video_noaudio.mp4> <bilder_dir> [preview.png]
import sys, subprocess, math, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
W,H,FPS=1080,1920,30
FB="/usr/share/fonts/opentype/inter/Inter-Black.otf"; FM="/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf"
FA="/usr/share/fonts/truetype/google-fonts/ofl/anton/Anton-Regular.ttf"; FMO="/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
BG=(244,239,228); NV=(18,32,64); RD=(226,48,58); MU=(232,170,30); GY=(120,118,110); CARD=(255,252,245); GN=(30,150,95)
VO,OUT,BD=sys.argv[1],sys.argv[2],sys.argv[3]; PREV=sys.argv[4] if len(sys.argv)>4 else None
TOTAL=float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",VO]))
S=[0,6.28,8.10,11.85,15.06,17.83,21.22,24.55,26.08,29.03]
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
PX,PY,PW,PH=60,400,960,610
def prep(n,col,ctr):
    im=Image.open(os.path.join(BD,n)).convert("RGB")
    im=ImageEnhance.Contrast(ImageEnhance.Color(im).enhance(col)).enhance(ctr)
    r=PW*1.3/im.width; return im.resize((int(im.width*r),int(im.height*r)),Image.LANCZOS)
IM={"str":prep("strasse.png",1.15,1.1),"rz":prep("rechenzentrum.png",0.7,1.2),"ctl":prep("controller.png",0.9,1.15)}
def crop(key,z,ox,oy):
    im=IM[key]; cw=int(im.width*z); ch=int(cw*PH/PW)
    if ch>im.height: ch=im.height; cw=int(ch*PW/PH)
    x=int((im.width-cw)*ox); y=int((im.height-ch)*oy)
    return im.crop((x,y,x+cw,y+ch)).resize((PW,PH),Image.BILINEAR)
def pixelate(p,blk):
    if blk<=1: return p
    return p.resize((max(1,PW//blk),max(1,PH//blk)),Image.BILINEAR).resize((PW,PH),Image.NEAREST)
def panel(t,i):
    if i<=3:
        k=t/12; p=crop("str",0.82-0.1*k,0.45,0.55)
        blk=14 if i in (0,2,3) else 8
        if i==1: blk=int(4+10*ease((t-S[1])/1.5))
        return pixelate(p,blk),"str"
    if i<=5:
        k=(t-S[4])/6; p=crop("rz",0.7+0.15*k,0.5,0.45)
        return p,"rz"
    k=(t-S[6])/9; p=crop("ctl",0.9-0.15*k,0.5,0.5)
    return (pixelate(p,3) if i<8 else p),"ctl"
MASK=Image.new("L",(PW,PH),0); ImageDraw.Draw(MASK).rounded_rectangle([0,0,PW-1,PH-1],30,fill=255)
def header(d,t):
    # Sehtafel-Zeilen
    d.text((60,250),"E",font=F(FB,92),fill=NV,anchor="lm")
    d.text((140,262),"F P",font=F(FB,54),fill=NV,anchor="lm")
    d.text((262,270),"T O Z",font=F(FB,32),fill=NV,anchor="lm")
    d.text((395,276),"L P E D",font=F(FB,20),fill=GY,anchor="lm")
    d.rounded_rectangle([W-430,215,W-60,300],20,fill=NV)
    d.text((W-245,258),"SEHTEST · GTA VI",font=fit(d,"SEHTEST · GTA VI",FB,40,340),fill=BG,anchor="mm")
    d.line([(60,335),(W-60,335)],fill=NV,width=4)
def lens(im,d,t):
    # Lupe über dem Panel mit "720p"-Label
    cx=PX+PW-170+int(18*math.sin(t*1.3)); cy=PY+PH-150+int(12*math.cos(t*1.1)); r=110
    d.ellipse([cx-r,cy-r,cx+r,cy+r],outline=NV,width=14)
    d.line([(cx+78,cy+78),(cx+150,cy+150)],fill=NV,width=26)
    d.ellipse([cx-r+7,cy-r+7,cx+r-7,cy+r-7],fill=(255,255,255))
    d.text((cx,cy),"720p",font=F(FA,84),fill=RD,anchor="mm")
def frame(t):
    i=seg(t); im=Image.new("RGB",(W,H),BG); d=ImageDraw.Draw(im)
    header(d,t)
    p,key=panel(t,i); im.paste(p,(PX,PY),MASK)
    d.rounded_rectangle([PX,PY,PX+PW,PY+PH],30,outline=NV,width=6)
    if i<=3: lens(im,d,t)
    y0=1060
    if i==0:
        d.text((70,y0+20),"GTA VI IN",font=F(FA,150),fill=NV,anchor="lt")
        d.text((W-70,y0+20),"720p",font=F(FA,150),fill=RD,anchor="rt")
        s=1+0.04*math.sin(t*5)
        f=fit(d,"ELEKTROSCHROTT?",FB,int(118*s),W-160); bw=d.textlength("ELEKTROSCHROTT?",font=f)+70
        d.rounded_rectangle([W/2-bw/2,y0+230,W/2+bw/2,y0+390],26,fill=RD)
        d.text((W//2,y0+310),"ELEKTROSCHROTT?",font=f,fill=(255,255,255),anchor="mm")
        d.text((W//2,y0+460),"Xbox Series S im Härtetest",font=F(FM,52),fill=NV,anchor="mm")
    elif i==1:
        pv=pop((t-S[1])/0.4)
        d.text((W//2,y0+60),"BEFUND VON",font=F(FMO,48),fill=GY,anchor="mm")
        f=F(FA,int(150*max(0.3,min(1.1,pv))))
        d.text((W//2,y0+210),"DIGITAL FOUNDRY",font=fit(d,"DIGITAL FOUNDRY",FA,f.size,W-120),fill=NV,anchor="mm")
        d.text((W//2,y0+360),"Patientin: Xbox Series S",font=F(FM,54),fill=RD,anchor="mm")
    elif i in (2,3):
        rows=[("AUFLÖSUNG (intern)","720p",RD,S[2]),("ZIEL-FPS","30",NV,S[2]+1.6),("SCHIESSEREIEN","~20 FPS",RD,S[3])]
        for k,(lab,val,col,ts) in enumerate(rows):
            pv=pop((t-ts)/0.35)
            if pv<=0: continue
            y=y0+k*165
            d.rounded_rectangle([60,y,1020,y+140],26,fill=CARD,outline=col,width=5)
            d.text((100,y+70),lab,font=F(FM,46),fill=NV,anchor="lm")
            d.text((980,y+70),val,font=F(FA,int(96*min(1.12,pv))),fill=col,anchor="rm")
        if i==3 and t>S[3]+1.5: d.text((W//2,y0+540),"▼ Einbrüche unter die 30",font=F(FB,50),fill=RD,anchor="mm")
    elif i==4:
        a=ease((t-S[4])/1.6)
        d.text((W//2,y0+50),"VERDACHT: ARBEITSSPEICHER",font=fit(d,"VERDACHT: ARBEITSSPEICHER",FMO,46,W-120),fill=GY,anchor="mm")
        for k,(lab,v,col) in enumerate([("Series S",10,RD),("PS5 / Series X",16,NV)]):
            y=y0+130+k*170
            d.text((70,y),lab,font=F(FM,50),fill=NV,anchor="lm")
            d.rounded_rectangle([70,y+40,1010,y+130],22,fill=(225,219,205))
            d.rounded_rectangle([70,y+40,70+max(40,int(940*a*v/16)),y+130],22,fill=col)
            d.text((990,y+85),f"{v} GB",font=F(FB,54),fill=(255,255,255) if (v==16 and a>0.9) else NV,anchor="rm")
        d.text((W//2,y0+520),"… und langsamer angebunden",font=F(FB,52),fill=RD,anchor="mm")
    elif i==5:
        pv=pop((t-S[5])/0.4)
        d.text((W//2,y0+50),"EMPFEHLUNG DES TESTERS",font=F(FMO,46),fill=GY,anchor="mm")
        if pv>0:
            sc=min(1.08,pv)
            d.rounded_rectangle([70,y0+120,1010,y0+430],30,fill=CARD,outline=NV,width=6)
            d.text((W//2,y0+210),"„Lieber auf einer",font=F(FB,int(70*sc)),fill=NV,anchor="mm")
            d.text((W//2,y0+310),"anderen Konsole spielen“",font=fit(d,"anderen Konsole spielen“",FB,int(70*sc),880),fill=NV,anchor="mm")
            d.text((W//2,y0+390),"– Digital Foundry (sinngemäß)",font=F(FM,36),fill=GY,anchor="mm")
        if t>S[5]+1.6:
            ang=-12; st=Image.new("RGBA",(560,150),(0,0,0,0)); sd=ImageDraw.Draw(st)
            sd.rounded_rectangle([5,5,555,145],20,outline=RD+(230,),width=10); sd.text((280,75),"AUTSCH!",font=F(FB,90),fill=RD+(230,),anchor="mm")
            st=st.rotate(ang,expand=True,resample=Image.BICUBIC); im.paste(st,(W-st.width-40,y0+345),st)
    elif i in (6,7):
        d.text((W//2,y0+60),"UND DIE SERIES X?",font=fit(d,"UND DIE SERIES X?",FA,130,W-120),fill=NV,anchor="mm")
        if t>S[6]+1.3:
            pv=pop((t-S[6]-1.3)/0.35)
            for k,(lab,val) in enumerate([("intern","1440p"),("Ziel","30 FPS")]):
                if k==1 and i<7: continue
                cx=290+k*500; s=min(1.1,pv if k==0 else pop((t-S[7])/0.35))
                d.rounded_rectangle([cx-220,y0+190,cx+220,y0+420],30,fill=CARD,outline=NV if k==0 else RD,width=6)
                d.text((cx,y0+250),lab,font=F(FM,44),fill=GY,anchor="mm")
                d.text((cx,y0+345),val,font=F(FA,int(110*s)),fill=NV if k==0 else RD,anchor="mm")
        if i==7: d.text((W//2,y0+500),"Auch nur 30. Für alle.",font=F(FB,54),fill=NV,anchor="mm")
    elif i>=8:
        d.text((W//2,y0+50),"SERIES S VERKAUFEN?",font=fit(d,"SERIES S VERKAUFEN?",FA,140,W-120),fill=NV,anchor="mm")
        pv=pop((t-S[8]-0.4)/0.4)
        if pv>0:
            for k,(txt,col) in enumerate([("JA",RD),("NEIN",GN)]):
                cx=300+k*480; s=pv; w2,h2=200*s,85*s
                d.rounded_rectangle([cx-w2,y0+215-h2,cx+w2,y0+215+h2],30,fill=col)
                d.text((cx,y0+215),txt,font=F(FB,int(92*s)),fill=(255,255,255),anchor="mm")
        if i==9:
            pf=pop((t-S[9])/0.4)
            if pf>0:
                d.rounded_rectangle([60,y0+360,1020,y0+480],30,fill=NV)
                d.text((W//2,y0+420),"Folge dem Kanal für mehr Infos!",font=fit(d,"Folge dem Kanal für mehr Infos!",FB,int(58*min(1,pf)),900),fill=BG,anchor="mm")
        else:
            d.text((W//2,y0+420),"Schreib's in die Kommentare 👇".replace(" 👇",""),font=F(FM,46),fill=GY,anchor="mm")
    d.text((60,1680),"Quelle: Digital Foundry (via TweakTown, Notebookcheck)",font=F(FM,28),fill=GY,anchor="lm")
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); od=ImageDraw.Draw(ov)
    od.rounded_rectangle([60,140,280,192],26,fill=(18,32,64,150)); od.text((170,166),"KI-generiert",font=F(FM,32),fill=(255,255,255,220),anchor="mm")
    im.paste(ov,(0,0),ov)
    return im
if PREV:
    ts=[0.0,7,9.5,13.5,16.5,20,22,25,27.5,29.8]
    sheet=Image.new("RGB",(5*270,2*480))
    for k,tt in enumerate(ts): sheet.paste(frame(tt).resize((270,480)),((k%5)*270,(k//5)*480))
    sheet.save(PREV); frame(0).save(PREV.replace(".png","_f0.png")); sys.exit()
N=int(TOTAL*FPS)+1
p=subprocess.Popen(["ffmpeg","-y","-v","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-c:v","libx264","-preset","veryfast","-crf","21","-pix_fmt","yuv420p",OUT],stdin=subprocess.PIPE)
for n in range(N): p.stdin.write(frame(n/FPS).tobytes())
p.stdin.close(); p.wait()
