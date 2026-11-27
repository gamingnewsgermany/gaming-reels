# Vorlage "Musik-Player / Review-Meter" (Pflaume/Koralle/Creme/Mint): Player-Kopfzeile mit Fortschrittsbalken,
# Bildpanel mit animierter Waveform, Track-Karte, Steam-Review-Meter (sinkt auf Prozentwert), Zitat-Karte,
# Stempel, JA/NEIN-Buttons. Aufruf: python3 musikplayer.py <vo.mp3> <out_noaudio.mp4> <bilder_dir> [preview.png]
import sys, subprocess, math, os
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
W,H,FPS=1080,1920,30
FB="/usr/share/fonts/opentype/inter/Inter-Black.otf"; FM="/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf"
FA="/usr/share/fonts/truetype/google-fonts/ofl/anton/Anton-Regular.ttf"; FMO="/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
BG=(34,14,40); PAN=(56,26,64); CO=(255,94,98); CR=(250,236,210); MI=(60,220,170); AM=(255,186,60); WH=(255,255,255); GY=(185,160,190)
VO,OUT,BD=sys.argv[1],sys.argv[2],sys.argv[3]; PREV=sys.argv[4] if len(sys.argv)>4 else None
TOTAL=float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",VO]))
S=[0,4.4,6.42,10.8,14.5,15.5,18.2,21.06,22.5,25.4,28.15]
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
    while d.textlength(t,font=F(fn,size))>maxw: size-=3
    return F(fn,size)
def ease(x): x=max(0,min(1,x)); return 1-(1-x)**3
def pop(x):
    if x<=0: return 0
    if x>=1: return 1
    return 1+2.2*(x-1)**3+1.2*(x-1)**2
def cl(v): return max(0.3,min(1.08,v))
PX,PY,PW,PH=50,290,980,600
def prep(n,col,ctr,tint=None,a=0.2):
    im=Image.open(os.path.join(BD,n)).convert("RGB")
    im=ImageEnhance.Contrast(ImageEnhance.Color(im).enhance(col)).enhance(ctr)
    if tint: im=Image.blend(im,Image.new("RGB",im.size,tint),a)
    r=PW*1.45/im.width; return im.resize((int(im.width*r),int(im.height*r)),Image.LANCZOS)
IM={"hs":prep("headset.png",1.1,1.15,CO,0.22),"ar":prep("arcade.png",0.9,1.1,(120,40,140),0.25),
    "ph":prep("handy_news.png",0.6,1.2,(90,20,60),0.3)}
def crop(key,z,ox,oy):
    im=IM[key]; cw=int(im.width*z); ch=int(cw*PH/PW)
    if ch>im.height: ch=im.height; cw=int(ch*PW/PH)
    x=int((im.width-cw)*ox); y=int((im.height-ch)*oy)
    return im.crop((x,y,x+cw,y+ch)).resize((PW,PH),Image.BILINEAR)
def panel(t,i):
    if i in (0,1): k=t/6.4; return crop("hs",0.62-0.1*k,0.1+0.15*k,0.4)
    if i in (2,3,4): k=(t-S[2])/9.1; return crop("ar",0.75-0.15*k,0.2+0.5*k,0.5)
    if i in (5,6): k=(t-S[5])/5.6; return crop("ph",0.6-0.1*k,0.55,0.35)
    if i in (7,8): k=(t-S[7])/4.4; return crop("hs",0.5-0.06*k,0.05,0.3)
    if i==9: k=(t-S[9])/2.8; return crop("ar",0.55,0.9-0.2*k,0.6)
    return crop("ph",0.75,0.5,0.4)
MASK=Image.new("L",(PW,PH),0); ImageDraw.Draw(MASK).rounded_rectangle([0,0,PW-1,PH-1],30,fill=255)
def header(d,t):
    d.rectangle([0,0,W,250],fill=PAN)
    d.text((60,150),"NOW PLAYING",font=F(FMO,34),fill=MI,anchor="lm")
    d.text((60,200),"Crime Mode – Track 01",font=F(FB,44),fill=WH,anchor="lm")
    # Play/Pause-Icon
    cx,cy=W-110,175
    d.ellipse([cx-50,cy-50,cx+50,cy+50],fill=CO)
    d.rectangle([cx-18,cy-22,cx-6,cy+22],fill=WH); d.rectangle([cx+6,cy-22,cx+18,cy+22],fill=WH)
    p=min(1,t/TOTAL); d.rectangle([0,242,W,250],fill=(80,45,90)); d.rectangle([0,242,int(W*p),250],fill=CO)
def wave(im,t,y,h,col,amp=1.0,dead=False):
    d=ImageDraw.Draw(im); n=46; bw=PW//n
    for k in range(n):
        v=0.15 if dead else (0.35+0.65*abs(math.sin(k*0.7+t*5.3)*math.sin(k*0.23+t*2.1)))*amp
        hh=int(h*v); x=PX+k*bw+4
        d.rounded_rectangle([x,y-hh,x+bw-8,y+hh],4,fill=col)
def stamp(im,text,col,cx,cy,ang,sc,w=820,h=230,size=140):
    if sc<=0: return
    tmp=Image.new("RGBA",(w+40,h+40),(0,0,0,0)); d=ImageDraw.Draw(tmp)
    d.rounded_rectangle([10,10,w+29,h+29],20,outline=col,width=13)
    d.text(((w+40)//2,(h+40)//2),text,font=fit(d,text,FA,size,w-60),fill=col,anchor="mm")
    tmp=tmp.rotate(ang,expand=True,resample=Image.BICUBIC)
    s=max(0.05,sc); tmp=tmp.resize((int(tmp.width*s),int(tmp.height*s)),Image.BILINEAR)
    im.paste(tmp,(int(cx-tmp.width/2),int(cy-tmp.height/2)),tmp)
def boxtext(d,txt,y,col,fg,size,maxw=900,s=1.0):
    f=fit(d,txt,FA,int(size*s),maxw); bw=d.textlength(txt,font=f)+60
    d.rounded_rectangle([W/2-bw/2,y,W/2+bw/2,y+int(size*1.3)],24,fill=col)
    d.text((W/2,y+int(size*0.65)),txt,font=f,fill=fg,anchor="mm")
def buttons(d,t,labels,y,ts):
    for k,(lab,col,fg) in enumerate(labels):
        pv=pop((t-ts-0.3*k)/0.35)
        if pv<=0: continue
        yy=y+k*180; sc=min(1.06,pv)
        d.rounded_rectangle([110,yy,970,yy+145],72,fill=col)
        d.text((W//2,yy+72),lab,font=fit(d,lab,FB,int(64*sc),760),fill=fg,anchor="mm")
def meter(im,d,t,ts,y):
    k=ease((t-ts)/1.6); v=80-72*k
    d.text((70,y),"STEAM · KÜRZLICHE REVIEWS",font=fit(d,"STEAM · KÜRZLICHE REVIEWS",FMO,40,940),fill=GY,anchor="lt")
    d.rounded_rectangle([70,y+70,1010,y+170],50,fill=PAN)
    col=MI if v>60 else (AM if v>30 else CO)
    d.rounded_rectangle([70,y+70,70+max(100,int(940*v/100)),y+170],50,fill=col)
    d.text((W//2,y+290),f"{int(round(v))} %",font=F(FA,190),fill=col,anchor="mm")
    d.text((W//2,y+430),"positiv",font=F(FB,54),fill=WH,anchor="mm")
def frame(t):
    i=seg(t); im=Image.new("RGB",(W,H),BG); d=ImageDraw.Draw(im)
    header(d,t)
    im.paste(panel(t,i),(PX,PY),MASK)
    d.rounded_rectangle([PX,PY,PX+PW,PY+PH],30,outline=CO,width=6)
    y0=950
    if i in (0,1):
        d.text((W//2,y0+70),"EIN KI-SONG –",font=fit(d,"EIN KI-SONG –",FA,150,940),fill=WH,anchor="mm")
        s=1+0.03*math.sin(t*6)
        boxtext(d,"NUR NOCH 8 % POSITIV!",y0+180,CO,WH,125,s=s)
        if i==0: d.text((W//2,y0+450),"…bei Steam. Wegen EINEM Track.",font=F(FM,50),fill=CR,anchor="mm")
        else: buttons(d,t,[("ÜBERTRIEBEN",CR,BG),("VERDIENT",MI,BG)],y0+380,S[1]+0.1)
        wave(im,t,PY+PH-90,60,(255,255,255),0.9)
    elif i in (2,3,4):
        pv=ease((t-S[2])/0.4); dx=int((1-pv)*500)
        d.rounded_rectangle([60+dx,y0-20,1020+dx,y0+300],28,fill=PAN,outline=AM,width=6)
        d.text((100+dx,y0+30),"FREIES UPDATE · REPENTANCE+",font=fit(d,"FREIES UPDATE · REPENTANCE+",FMO,38,880),fill=AM,anchor="lt")
        d.text((100+dx,y0+90),"CRIME MODE",font=F(FA,130),fill=WH,anchor="lt")
        d.text((100+dx,y0+245),"Daily Challenge mit GTA-VI-Anspielungen",font=fit(d,"Daily Challenge mit GTA-VI-Anspielungen",FM,44,880),fill=CR,anchor="lt")
        if i>=3:
            wave(im,t,PY+PH-110,80,CO,1.0)
            pv2=pop((t-S[3]-0.2)/0.35)
            if pv2>0:
                d.rounded_rectangle([60,y0+340,1020,y0+560],28,fill=(20,8,24),outline=CO,width=5)
                d.text((100,y0+375),"TRACK 01 · DATEI-INFO",font=F(FMO,36),fill=GY,anchor="lt")
                d.text((100,y0+430),"Erstellt mit: SUNO-KI?",font=fit(d,"Erstellt mit: SUNO-KI?",FB,int(66*cl(pv2)),880),fill=CO,anchor="lt")
                d.text((100,y0+510),"laut Spielern (Metadaten) – via PC Gamer",font=fit(d,"laut Spielern (Metadaten) – via PC Gamer",FM,38,880),fill=CR,anchor="lt")
        if i==4:
            stamp(im,"OHNE HINWEIS",CO,W//2,PY+PH//2-40,-9,pop((t-S[4])/0.3)*0.9)
    elif i==5:
        meter(im,d,t,S[5]+0.1,y0-10)
        if t>16.9: boxtext(d,"ÄUSSERST NEGATIV",y0+500,CO,WH,90,s=cl(pop((t-16.9)/0.3)))
    elif i==6:
        pv=ease((t-S[6])/0.4)
        d.rounded_rectangle([60,y0-10,1020,y0+420],30,fill=CR)
        d.text((110,y0+20),"„",font=F(FA,200),fill=CO,anchor="lt")
        d.text((W//2+30,y0+150),"Ich wusste",font=F(FA,int(120*cl(pv))),fill=BG,anchor="mm")
        d.text((W//2+30,y0+280),"nichts davon.",font=F(FA,int(120*cl(pv))),fill=CO,anchor="mm")
        d.text((W//2,y0+380),"Edmund McMillen, Schöpfer (sinngemäß)",font=fit(d,"Edmund McMillen, Schöpfer (sinngemäß)",FM,40,900),fill=BG,anchor="mm")
        d.text((W//2,y0+500),"Publisher: Nicalis",font=F(FMO,40),fill=GY,anchor="mm")
    elif i==7:
        wave(im,t,PY+PH-110,80,(150,130,150),dead=True)
        stamp(im,"ENTFERNT",CO,W//2,PY+PH//2-30,7,pop((t-S[7])/0.3)*0.85)
        d.text((W//2,y0+120),"TRACK 01",font=F(FA,150),fill=GY,anchor="mm")
        d.line([(200,y0+125),(880,y0+125)],fill=CO,width=16)
        d.text((W//2,y0+300),"Song schon wieder raus",font=F(FB,60),fill=WH,anchor="mm")
    elif i==8:
        pv=pop((t-S[8])/0.35)
        d.text((W//2,y0+60),"UND JA …",font=F(FA,int(130*cl(pv))),fill=CR,anchor="mm")
        if t>23.5:
            boxtext(d,"DIESE STIMME",y0+170,MI,BG,110,s=cl(pop((t-23.5)/0.3)))
            d.text((W//2,y0+420),"IST AUCH KI.",font=F(FA,int(130*cl(pop((t-23.9)/0.3)))),fill=WH,anchor="mm")
        stamp(im,"KI-GENERIERT",MI,W//2,PY+PH//2,-6,pop((t-24.2)/0.3)*0.8)
    elif i==9:
        pv=pop((t-S[9])/0.35)
        d.text((W//2,y0+40),"REVIEW-BOMBING",font=fit(d,"REVIEW-BOMBING",FA,int(150*cl(pv)),960),fill=WH,anchor="mm")
        d.text((W//2,y0+185),"BERECHTIGT?",font=F(FA,int(120*cl(pv))),fill=CO,anchor="mm")
        buttons(d,t,[("JA, VÖLLIG",MI,BG),("NEIN, ÜBERTRIEBEN",CO,WH)],y0+290,S[9]+0.9)
        if t>27.2: d.text((W//2,y0+680),"Schreib's in die Kommentare!",font=F(FB,48),fill=CR,anchor="mm")
    else:
        pv=pop((t-S[10])/0.4)
        d.text((W//2,y0+150),"FOLGE DEM KANAL",font=fit(d,"FOLGE DEM KANAL",FA,int(150*cl(pv)),960),fill=WH,anchor="mm")
        d.text((W//2,y0+310),"FÜR MEHR INFOS!",font=fit(d,"FÜR MEHR INFOS!",FA,int(130*cl(pv)),900),fill=CO,anchor="mm")
        d.rounded_rectangle([260,y0+420,820,y0+520],50,fill=MI)
        d.text((W//2,y0+470),"GAMING FACTS & NEWS",font=F(FB,40),fill=BG,anchor="mm")
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); od=ImageDraw.Draw(ov)
    od.rounded_rectangle([PX+24,PY+24,PX+244,PY+76],26,fill=(0,0,0,130)); od.text((PX+134,PY+50),"KI-generiert",font=F(FM,32),fill=(255,255,255,215),anchor="mm")
    im=im.convert("RGBA"); im.alpha_composite(ov); return im.convert("RGB")
N=int(TOTAL*FPS)+int(0.6*FPS)
if PREV:
    ts=[0.0,2.5,5.3,8.0,12.5,15.0,16.0,17.6,19.5,22.0,23.0,24.8,26.0,27.6,29.0,30.5]
    sheet=Image.new("RGB",(W//4*8,H//4*2),(0,0,0))
    for k,tt in enumerate(ts): sheet.paste(frame(tt).resize((W//4,H//4)),((k%8)*W//4,(k//8)*H//4))
    sheet.save(PREV); frame(0).save(PREV.replace(".png","_f0.png")); sys.exit()
p=subprocess.Popen(["ffmpeg","-y","-v","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-c:v","libx264","-preset","veryfast","-crf","21","-pix_fmt","yuv420p",OUT],stdin=subprocess.PIPE)
for n in range(N): p.stdin.write(frame(n/FPS).tobytes())
p.stdin.close(); p.wait()
