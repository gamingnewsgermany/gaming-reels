# Vorlage "Festival-Ticket / Line-up-Poster" (Miami-Sunset: Tiefpetrol/Pink/Türkis/Gold): Bildpanel oben,
# Konzert-Ticket mit Perforation, Line-up-Namen poppen nacheinander, Lotterie-Kugeln, Charity-Stempel, Entweder-oder
# Aufruf: python3 festival_ticket.py <vo.mp3> <out_video_noaudio.mp4> <bilder_dir> [preview.png]
import sys, subprocess, math, os, random
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
W,H,FPS=1080,1920,30
FB="/usr/share/fonts/opentype/inter/Inter-Black.otf"; FM="/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf"
FA="/usr/share/fonts/truetype/google-fonts/ofl/anton/Anton-Regular.ttf"; FMO="/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
TOP=(6,34,44); BOT=(40,14,52); PK=(255,64,150); TQ=(40,225,210); GD=(255,196,60); WH=(255,255,255); GY=(175,200,205)
CARD=(14,54,66); PAPER=(255,244,226); INK=(30,20,40)
VO,OUT,BD=sys.argv[1],sys.argv[2],sys.argv[3]; PREV=sys.argv[4] if len(sys.argv)>4 else None
TOTAL=float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",VO]))+0.6
S=[0,5.77,10.68,15.35,17.89,22.31,25.66]
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
BG=Image.new("RGB",(W,H)); _d=ImageDraw.Draw(BG)
for y in range(H):
    a=y/H; _d.line([(0,y),(W,y)],fill=tuple(int(TOP[c]*(1-a)+BOT[c]*a) for c in range(3)))
random.seed(28)
for _ in range(60):  # Konfetti
    x,y=random.randint(0,W),random.randint(0,H); c=random.choice([PK,TQ,GD]); r=random.randint(3,7)
    _d.rectangle([x,y,x+r*2,y+r],fill=tuple(int(v*0.45+TOP[k]*0.55) for k,v in enumerate(c)))
L,R=60,W-60
PX,PY,PW,PH=L,300,R-L,680
def prep(n,col,ctr,tint=None,a=0.2):
    im=Image.open(os.path.join(BD,n)).convert("RGB")
    im=ImageEnhance.Contrast(ImageEnhance.Color(im).enhance(col)).enhance(ctr)
    if tint: im=Image.blend(im,Image.new("RGB",im.size,tint),a)
    r=PH*1.4/im.height; return im.resize((int(im.width*r),int(im.height*r)),Image.LANCZOS)
IM={"sky":prep("skyline.png",1.25,1.08,(255,60,140),0.12),"crowd":prep("messe.png",1.1,1.15,(255,40,160),0.22),
    "crowd2":prep("messe.png",1.0,1.2,(20,200,200),0.25),"geld":prep("neon_geld.png",1.1,1.1,(255,190,60),0.15)}
def crop(key,z,ox,oy):
    im=IM[key]; ch=int(im.height*z); cw=int(ch*PW/PH)
    if cw>im.width: cw=im.width; ch=int(cw*PH/PW)
    x=int((im.width-cw)*ox); y=int((im.height-ch)*oy)
    return im.crop((x,y,x+cw,y+ch)).resize((PW,PH),Image.BILINEAR)
MASK=Image.new("L",(PW,PH),0); ImageDraw.Draw(MASK).rounded_rectangle([0,0,PW-1,PH-1],30,fill=255)
def panel(t,i):
    if i==0: k=t/5.8; return crop("sky",0.78-0.14*k,0.5+0.08*k,0.15)
    if i==1: k=(t-S[1])/4.9; return crop("crowd",0.8-0.15*k,0.25+0.2*k,0.3)
    if i==2: k=(t-S[2])/4.7; return crop("crowd2",0.6-0.1*k,0.72,0.2)
    if i==3: k=(t-S[3])/2.5; return crop("sky",0.55,0.1+0.15*k,0.7)
    if i==4: k=(t-S[4])/4.4; return crop("geld",0.85-0.15*k,0.5,0.5)
    k=(t-S[5])/5.7; return crop("sky",0.95-0.1*k,0.45,0.3)
def ticket(im,box,col=PAPER,stub=True):
    x1,y1,x2,y2=box; d=ImageDraw.Draw(im)
    d.rounded_rectangle(box,26,fill=col)
    for y in (y1,y2):  # Kerben links/rechts der Perforation
        pass
    if stub:
        sx=x2-200
        for yy in range(y1+20,y2-10,26): d.line([(sx,yy),(sx,yy+12)],fill=(150,130,120),width=4)
        d.ellipse([sx-22,y1-22,sx+22,y1+22],fill=BGc(y1)); d.ellipse([sx-22,y2-22,sx+22,y2+22],fill=BGc(y2))
    return d
def BGc(y): return BG.getpixel((W//2,max(0,min(H-1,int(y)))))
def header(d,t):
    d.text((L,245),"GTA VI: THE FESTIVAL",font=F(FA,58),fill=WH,anchor="lm")
    d.rounded_rectangle([R-210,215,R,275],30,fill=PK); d.text((R-105,245),"MIAMI",font=F(FB,38),fill=WH,anchor="mm")
def sticker(im,txt,col,cx,cy,ang,s,size=90,w=420):
    st=Image.new("RGBA",(w,160),(0,0,0,0)); sd=ImageDraw.Draw(st)
    sd.rounded_rectangle([6,6,w-6,154],24,outline=col+(240,),width=10)
    sd.text((w//2,80),txt,font=fit(sd,txt,FB,int(size*max(.3,min(1.1,s))),w-50),fill=col+(240,),anchor="mm")
    st=st.rotate(ang,expand=True,resample=Image.BICUBIC); im.paste(st,(int(cx-st.width/2),int(cy-st.height/2)),st)
def frame(t):
    i=seg(t); im=BG.copy(); d=ImageDraw.Draw(im)
    header(d,t)
    im.paste(panel(t,i),(PX,PY),MASK); d.rounded_rectangle([PX,PY,PX+PW,PY+PH],30,outline=TQ,width=5)
    y0=1030
    if i==0:
        f=fit(d,"EIGENES FESTIVAL",FA,150,R-L); d.text((L,y0+10),"EIGENES FESTIVAL",font=f,fill=WH,anchor="lt")
        f2=fit(d,"FÜR EIN GAME?!",FB,int(112*(1+0.03*math.sin(t*5))),R-L-90); bw=d.textlength("FÜR EIN GAME?!",font=f2)+80
        d.rounded_rectangle([L,y0+200,L+bw,y0+350],28,fill=PK); d.text((L+bw/2,y0+275),"FÜR EIN GAME?!",font=f2,fill=WH,anchor="mm")
        pv=pop((t-2.9)/0.4)
        if pv>0:
            for k,(txt,col) in enumerate([("GAMING",TQ),("GRÖSSENWAHN",GD)]):
                x=L+k*((R-L)//2+10); ww=(R-L)//2-10; s=min(1.06,pv)
                d.rounded_rectangle([x,y0+400,x+ww,y0+510],26,fill=col)
                d.text((x+ww/2,y0+455),txt,font=fit(d,txt,FB,int(60*s),ww-40),fill=INK,anchor="mm")
    elif i==1:
        pv=pop((t-S[1])/0.45); dy=int((1-min(1,pv))*120)
        bx=[L,y0+40+dy,R,y0+520+dy]; td=ticket(im,bx)
        td.text((L+40,bx[1]+60),"ROCKSTAR × PLAYSTATION",font=fit(td,"ROCKSTAR × PLAYSTATION",FMO,40,R-L-300),fill=PK,anchor="lm")
        td.text((L+40,bx[1]+105),"PRESENT",font=F(FMO,34),fill=(120,100,100),anchor="lm")
        td.text((L+40,bx[1]+200),"GTA VI:",font=F(FA,96),fill=INK,anchor="lm")
        td.text((L+40,bx[1]+310),"THE FESTIVAL",font=fit(td,"THE FESTIVAL",FA,100,R-L-300),fill=INK,anchor="lm")
        rows=[("SA 21.11.",S[1]+1.2),("MIAMI · MANA WYNWOOD",S[1]+2.4)]
        for k,(txt,ts) in enumerate(rows):
            if t>=ts: td.text((L+40,bx[1]+395+k*50),txt,font=fit(td,txt,FB,40,R-L-300),fill=(200,40,110) if k==0 else INK,anchor="lm")
        sx=R-100; td.text((sx,bx[1]+120),"ADMIT",font=F(FB,34),fill=INK,anchor="mm"); td.text((sx,bx[1]+165),"ONE",font=F(FB,34),fill=INK,anchor="mm")
        for k in range(9): td.rectangle([sx-60+k*14,bx[1]+260,sx-60+k*14+(8 if k%3 else 4),bx[1]+400],fill=INK)
        td.text((sx,bx[1]+440),"2 BÜHNEN",font=F(FM,26),fill=(120,100,100),anchor="mm")
    elif i==2:
        d.text((L,y0+40),"LINE-UP (u. a.)",font=F(FMO,44),fill=TQ,anchor="lm")
        names=[("TRAVIS SCOTT",S[2]+0.05,WH),("CARDI B",S[2]+1.25,PK),("METRO BOOMIN",S[2]+2.05,GD),("JUSTICE",S[2]+3.05,TQ)]
        for k,(n,ts,col) in enumerate(names):
            pv=pop((t-ts)/0.35)
            if pv>0:
                y=y0+90+k*118; f=fit(d,n,FA,int(108*min(1.1,pv)),R-L)
                d.text((L,y),n,font=f,fill=col,anchor="lt")
        if t>=S[2]+3.5:
            pv=pop((t-S[2]-3.5)/0.35)
            d.rounded_rectangle([L+430,y0+455,R,y0+545],22,fill=CARD,outline=TQ,width=4)
            d.text(((L+430+R)//2,y0+500),"komponierte den Score",font=fit(d,"komponierte den Score",FM,int(38*max(.3,min(1,pv))),R-L-480),fill=WH,anchor="mm")
    elif i==3:
        d.text((L,y0+60),"TICKETS?",font=F(FA,130),fill=WH,anchor="lm")
        pv=pop((t-15.8)/0.4)
        # Lotterie-Kugeln
        cx,cy=R-180,y0+110
        for k in range(6):
            a=t*3+k*1.05; x=cx+70*math.cos(a); y=cy+40*math.sin(a)
            col=[PK,TQ,GD][k%3]; d.ellipse([x-30,y-30,x+30,y+30],fill=col,outline=WH,width=3)
            d.text((x,y),str([7,19,11,21,6,4][k]),font=F(FB,26),fill=INK,anchor="mm")
        if pv>0:
            s=min(1.08,pv); d.rounded_rectangle([L,y0+200,R,y0+380],30,fill=PK)
            d.text(((L+R)//2,y0+290),"NUR PER LOTTERIE",font=fit(d,"NUR PER LOTTERIE",FB,int(92*s),R-L-60),fill=WH,anchor="mm")
            if t>16.4: d.text((L,y0+450),"Geld allein reicht nicht.",font=F(FM,52),fill=TQ,anchor="lm")
    elif i==4:
        d.text((L,y0+50),"DER CLOU:",font=F(FMO,50),fill=GD,anchor="lm")
        pv=pop((t-18.85)/0.4)
        if pv>0:
            s=min(1.08,pv)
            d.text((L,y0+110),"100 %",font=F(FA,int(170*s)),fill=WH,anchor="lt")
            tx=L+int(d.textlength("100 %",font=F(FA,170)))+40
            d.text((tx,y0+150),"der Ticket-",font=F(FB,58),fill=WH,anchor="lt"); d.text((tx,y0+225),"Einnahmen",font=F(FB,58),fill=WH,anchor="lt")
        if t>=19.9:
            pv2=pop((t-19.9)/0.4); s=min(1.06,pv2)
            d.rounded_rectangle([L,y0+340,R,y0+470],28,fill=TQ)
            d.text(((L+R)//2,y0+405),"→ CHARITYS IN MIAMI",font=fit(d,"→ CHARITYS IN MIAMI",FB,int(72*s),R-L-60),fill=INK,anchor="mm")
            d.text((L,y0+520),"laut Rockstar",font=F(FM,38),fill=GY,anchor="lm")
        if t>=20.6: sticker(im,"CHARITY",GD,PX+PW-230,PY+PH-110,-9,pop((t-20.6)/0.3))
    elif i>=5:
        d.text((L,y0+40),"Festival für ein Game –",font=fit(d,"Festival für ein Game –",FB,62,R-L),fill=WH,anchor="lm")
        pv=pop((t-S[5])/0.4)
        for k,(txt,col,tc) in enumerate([("GENIALER MOVE",TQ,INK),("PR-STUNT",PK,WH)]):
            if pv<=0: continue
            y=y0+110+k*145; s=min(1.06,pv)
            d.rounded_rectangle([L,y,R,y+122],30,fill=col)
            d.text(((L+R)//2,y+61),txt,font=fit(d,txt,FB,int(80*s),R-L-80),fill=tc,anchor="mm")
        if i==6:
            pf=pop((t-S[6])/0.4)
            if pf>0:
                d.rounded_rectangle([L,y0+420,R,y0+530],30,fill=GD)
                d.text(((L+R)//2,y0+475),"Folge dem Kanal für mehr Infos!",font=fit(d,"Folge dem Kanal für mehr Infos!",FB,int(56*min(1,pf)),R-L-80),fill=INK,anchor="mm")
        elif t>=24.3:
            d.text((L,y0+470),"Schreib's in die Kommentare!",font=F(FM,46),fill=TQ,anchor="lm")
    src="Quellen: Rockstar Games, Gematsu (9.11.), Dancehall Mag (20.11.)"
    d.text((L,1640),src,font=fit(d,src,FM,26,R-L),fill=GY,anchor="lm")
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); od=ImageDraw.Draw(ov)
    od.rounded_rectangle([L,150,L+220,202],26,fill=(0,0,0,140)); od.text((L+110,176),"KI-generiert",font=F(FM,32),fill=(255,255,255,225),anchor="mm")
    im.paste(ov,(0,0),ov)
    return im
if PREV:
    ts=[0.0,4.0,8.5,10.9,14.6,17.0,21.5,23.5,25.0,27.5]
    sheet=Image.new("RGB",(5*270,2*480))
    for k,tt in enumerate(ts): sheet.paste(frame(tt).resize((270,480)),((k%5)*270,(k//5)*480))
    sheet.save(PREV); frame(0).save(PREV.replace(".png","_f0.png")); sys.exit()
N=int(TOTAL*FPS)+1
p=subprocess.Popen(["ffmpeg","-y","-v","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-c:v","libx264","-preset","veryfast","-crf","21","-pix_fmt","yuv420p",OUT],stdin=subprocess.PIPE)
for n in range(N): p.stdin.write(frame(n/FPS).tobytes())
p.stdin.close(); p.wait()
