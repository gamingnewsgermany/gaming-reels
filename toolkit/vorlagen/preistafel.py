# Vorlage "Tankstellen-Preistafel" (Anthrazit/LED-Rot/Türkis/Weiß): Preismast-Kopfzeile mit Live-Punkt, Bildpanel mit
# LED-Preisanzeige, hochtickende LED-Ziffern (alt durchgestrichen -> neu), Prozent-Knall, Warnschild, Chip-Karten,
# Kalenderblatt, JA/NEIN-Zapfsäulen-Buttons. Aufruf: python3 preistafel.py <vo.mp3> <out_noaudio.mp4> <bilder_dir> [preview.png]
import sys, subprocess, math, os
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
W,H,FPS=1080,1920,30
FB="/usr/share/fonts/opentype/inter/Inter-Black.otf"; FM="/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf"
FA="/usr/share/fonts/truetype/google-fonts/ofl/anton/Anton-Regular.ttf"; FMO="/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
BG=(26,28,32); PAN=(40,43,49); LED=(255,52,46); LEDD=(70,18,16); TQ=(0,206,178); WH=(255,255,255); GY=(150,155,165); YE=(255,206,40)
VO,OUT,BD=sys.argv[1],sys.argv[2],sys.argv[3]; PREV=sys.argv[4] if len(sys.argv)>4 else None
TOTAL=float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",VO]))
S=[0,4.3,12.1,13.9,18.1,22.1,24.5,29.55]
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
IM={"geld":prep("neon_geld.png",1.0,1.15,LED,0.18),"pc":prep("gaming_pc.png",0.75,1.15,TQ,0.2),
    "rz":prep("rechenzentrum.png",0.6,1.2,(10,60,70),0.3)}
def crop(key,z,ox,oy):
    im=IM[key]; cw=int(im.width*z); ch=int(cw*PH/PW)
    if ch>im.height: ch=im.height; cw=int(ch*PW/PH)
    x=int((im.width-cw)*ox); y=int((im.height-ch)*oy)
    return im.crop((x,y,x+cw,y+ch)).resize((PW,PH),Image.BILINEAR)
def panel(t,i):
    if i==0: k=t/4.3; return crop("geld",0.6-0.08*k,0.5,0.5)
    if i in (1,2): k=(t-S[1])/9.6; return crop("pc",0.72-0.12*k,0.3+0.4*k,0.5)
    if i==3: k=(t-S[3])/4.2; return crop("pc",0.55,0.85-0.25*k,0.35)
    if i in (4,5): k=(t-S[4])/6.4; return crop("rz",0.75-0.15*k,0.2+0.5*k,0.5)
    if i==6: k=(t-S[6])/5; return crop("geld",0.75-0.1*k,0.2,0.6)
    return crop("pc",0.8,0.5,0.5)
MASK=Image.new("L",(PW,PH),0); ImageDraw.Draw(MASK).rounded_rectangle([0,0,PW-1,PH-1],26,fill=255)
def header(d,t):
    d.rectangle([0,0,W,250],fill=PAN); d.rectangle([0,244,W,250],fill=TQ)
    on=int(t*2)%2==0
    d.ellipse([60,170,92,202],fill=LED if on else LEDD)
    d.text((112,186),"PREISTAFEL",font=F(FB,48),fill=WH,anchor="lm")
    d.text((W-60,186),"HARDWARE · HEUTE",font=F(FMO,34),fill=TQ,anchor="rm")
def led(im,cx,cy,txt,size,col=LED,glow=True):
    lay=Image.new("RGBA",(W,500),(0,0,0,0)); d=ImageDraw.Draw(lay)
    d.text((W//2,250),txt,font=F(FA,size),fill=col+(255,),anchor="mm")
    if glow:
        g=lay.filter(ImageFilter.GaussianBlur(14)); im.paste(g,(int(cx-W//2),int(cy-250)),g)
    im.paste(lay,(int(cx-W//2),int(cy-250)),lay)
def signbox(im,cx,cy,w,h,label,txt,sc=1.0,col=LED,strike=False):
    if sc<=0: return
    box=Image.new("RGBA",(w,h),(0,0,0,0)); d=ImageDraw.Draw(box)
    d.rounded_rectangle([0,0,w-1,h-1],22,fill=(12,12,14,240),outline=(90,95,105,255),width=5)
    d.text((w//2,48),label,font=fit(d,label,FB,36,w-50),fill=GY,anchor="mm")
    lay=Image.new("RGBA",(w,h),(0,0,0,0)); dl=ImageDraw.Draw(lay)
    dl.text((w//2,h//2+30),txt,font=fit(dl,txt,FA,int(h*0.62),w-60),fill=col+(255,),anchor="mm")
    g=lay.filter(ImageFilter.GaussianBlur(10)); box.alpha_composite(g); box.alpha_composite(lay)
    if strike: d=ImageDraw.Draw(box); d.line([(40,h-40),(w-40,70)],fill=WH,width=12)
    box=box.resize((max(1,int(w*sc)),max(1,int(h*sc))),Image.BILINEAR)
    im.paste(box,(int(cx-box.width/2),int(cy-box.height/2)),box)
def stamp(im,text,col,cx,cy,ang,sc,w=820,h=230,size=140):
    if sc<=0: return
    tmp=Image.new("RGBA",(w+40,h+40),(0,0,0,0)); d=ImageDraw.Draw(tmp)
    d.rounded_rectangle([10,10,w+29,h+29],20,outline=col,width=13)
    d.text(((w+40)//2,(h+40)//2),text,font=fit(d,text,FA,size,w-60),fill=col,anchor="mm")
    tmp=tmp.rotate(ang,expand=True,resample=Image.BICUBIC)
    s=max(0.05,sc); tmp=tmp.resize((int(tmp.width*s),int(tmp.height*s)),Image.BILINEAR)
    im.paste(tmp,(int(cx-tmp.width/2),int(cy-tmp.height/2)),tmp)
def warn(im,cx,cy,sc):
    if sc<=0: return
    s=int(300*sc); tmp=Image.new("RGBA",(s,s),(0,0,0,0)); d=ImageDraw.Draw(tmp)
    d.polygon([(s//2,8),(s-8,s-12),(8,s-12)],fill=YE,outline=(20,20,20),width=max(2,int(10*sc)))
    d.text((s//2,int(s*0.62)),"!",font=F(FA,int(s*0.5)),fill=(20,20,20),anchor="mm")
    im.paste(tmp,(int(cx-s/2),int(cy-s/2)),tmp)
def frame(t):
    i=seg(t); im=Image.new("RGB",(W,H),BG); d=ImageDraw.Draw(im)
    header(d,t)
    im.paste(panel(t,i),(PX,PY),MASK)
    d.rounded_rectangle([PX,PY,PX+PW,PY+PH],26,outline=(90,95,105),width=6)
    y0=950
    if i==0:
        signbox(im,780,PY+430,380,260,"GAMING","LUXUS",1.0)
        d.text((70,y0),"GAMING WIRD",font=fit(d,"GAMING WIRD",FA,160,940),fill=WH,anchor="lt")
        s=1+0.03*math.sin(t*6); txt="ZUM LUXUS-HOBBY!"
        f=fit(d,txt,FA,int(128*s),900); bw=d.textlength(txt,font=f)+60
        d.rounded_rectangle([60,y0+215,60+bw,y0+380],24,fill=LED)
        d.text((60+bw/2,y0+297),txt,font=f,fill=WH,anchor="mm")
        d.text((70,y0+440),"…und Valve gibt's quasi zu.",font=F(FM,50),fill=TQ,anchor="lt")
    elif i==1:
        d.text((70,y0-10),"STEAM DECK 512 GB · SEIT MAI",font=fit(d,"STEAM DECK 512 GB · SEIT MAI",FMO,42,940),fill=GY,anchor="lt")
        pv=pop((t-S[1]-0.3)/0.35)
        signbox(im,300,y0+260,440,300,"VORHER","549 $",min(1.05,pv),col=GY,strike=t>7.7)
        if t>9.9:
            k=ease((t-9.9)/0.9); v=int(549+240*k)
            signbox(im,790,y0+260,440,300,"JETZT",f"{v} $",min(1.05,pop((t-9.9)/0.3)))
        if t>8.3: d.text((W//2,y0+500),"→",font=F(FB,90),fill=TQ,anchor="mm") if t<9.9 else None
        if t>11.0: d.text((W//2,y0+520),"+240 Dollar Aufpreis",font=F(FB,54),fill=WH,anchor="mm")
    elif i==2:
        pv=pop((t-S[2])/0.3)
        led(im,W//2,y0+220,"+44 %",int(330*cl(pv)))
        d.text((W//2,y0+470),"Steam Deck 549 → 789 $",font=F(FB,56),fill=WH,anchor="mm")
        stamp(im,"AUTSCH",LED,W//2,PY+PH//2,-8,pop((t-S[2]-0.4)/0.3)*0.8)
    elif i==3:
        warn(im,W//2,PY+PH//2,pop((t-S[3])/0.35)*1.2)
        pv=pop((t-S[3]-0.2)/0.35)
        d.text((W//2,y0+60),"VALVE WARNT:",font=F(FA,int(140*cl(pv))),fill=YE,anchor="mm")
        if t>15.4:
            d.rounded_rectangle([70,y0+170,1010,y0+430],26,fill=PAN,outline=TQ,width=5)
            d.text((W//2,y0+240),"STEAM MACHINE",font=F(FB,int(70*cl(pop((t-15.4)/0.3)))),fill=WH,anchor="mm")
            d.text((W//2,y0+350),"2027 ähnlich teurer?",font=F(FB,58),fill=TQ,anchor="mm")
        if t>16.4: d.text((W//2,y0+510),"„probably similar“ – Valve-Ingenieure zu IGN",font=fit(d,"„probably similar“ – Valve-Ingenieure zu IGN",FM,42,960),fill=GY,anchor="mm")
    elif i==4:
        d.text((70,y0-10),"DER GRUND",font=F(FMO,44),fill=GY,anchor="lt")
        cards=[("SPEICHER","knapp & teuer",LED,S[4]+0.2),("PRODUKTION","weniger als geplant",YE,20.1)]
        for k,(a,b,col,ts) in enumerate(cards):
            pv=ease((t-ts)/0.4)
            if pv<=0: continue
            y=y0+70+k*230; dx=int((1-pv)*420)
            d.rounded_rectangle([60+dx,y,1020+dx,y+190],22,fill=PAN,outline=col,width=6)
            for p in range(6): d.rectangle([90+dx+p*22,y+20,100+dx+p*22,y+40],fill=col); d.rectangle([90+dx+p*22,y+150,100+dx+p*22,y+170],fill=col)
            d.text((260+dx,y+70),a,font=F(FB,62),fill=WH,anchor="lm")
            d.text((260+dx,y+135),b,font=F(FM,48),fill=col,anchor="lm")
            d.rounded_rectangle([90+dx,y+55,230+dx,y+135],10,fill=(15,15,18))
        if t>21.0: d.text((W//2,y0+590),"laut Valve-Update, Nov. 2026",font=F(FM,42),fill=GY,anchor="mm")
    elif i==5:
        pv=pop((t-S[5])/0.35); sc=min(1.05,pv)
        cw,ch=int(520*sc),int(420*sc)
        if sc>0:
            cx,cy=W//2,y0+250
            d.rounded_rectangle([cx-cw//2,cy-ch//2,cx+cw//2,cy+ch//2],26,fill=WH)
            d.rounded_rectangle([cx-cw//2,cy-ch//2,cx+cw//2,cy-ch//2+int(110*sc)],26,fill=LED)
            d.rectangle([cx-cw//2,cy-ch//2+int(80*sc),cx+cw//2,cy-ch//2+int(110*sc)],fill=LED)
            d.text((cx,cy-ch//2+int(58*sc)),"JANUAR 2027",font=F(FB,max(10,int(54*sc))),fill=WH,anchor="mm")
            d.text((cx,cy+int(50*sc)),"PREIS-",font=F(FA,max(10,int(110*sc))),fill=BG,anchor="mm")
            d.text((cx,cy+int(150*sc)),"UPDATE",font=F(FA,max(10,int(80*sc))),fill=LED,anchor="mm")
        if t>23.0: d.text((W//2,y0+540),"Nächstes Valve-Update",font=F(FB,54),fill=TQ,anchor="mm")
    elif i==6:
        pv=pop((t-S[6])/0.35)
        d.text((W//2,y0+40),"1.000 €",font=F(FA,int(170*cl(pv))),fill=LED,anchor="mm")
        d.text((W//2,y0+180),"FÜR EINE KONSOLE?",font=fit(d,"FÜR EINE KONSOLE?",FA,int(100*cl(pv)),940),fill=WH,anchor="mm")
        for k,(lab,col,ts) in enumerate([("JA, ZAHL ICH",TQ,28.2),("NEIN, NIEMALS",LED,28.6)]):
            pv2=pop((t-ts)/0.35)
            if pv2<=0: continue
            y=y0+290+k*190; sc=min(1.06,pv2)
            d.rounded_rectangle([110,y,970,y+150],75,fill=col)
            d.text((W//2,y+75),lab,font=fit(d,lab,FB,int(66*sc),760),fill=WH if col==LED else BG,anchor="mm")
        if t>28.9: d.text((W//2,y0+690),"Schreib's in die Kommentare!",font=F(FB,48),fill=WH,anchor="mm")
    else:
        pv=pop((t-S[7])/0.4)
        d.text((W//2,y0+150),"FOLGE DEM KANAL",font=fit(d,"FOLGE DEM KANAL",FA,int(150*cl(pv)),960),fill=WH,anchor="mm")
        d.text((W//2,y0+310),"FÜR MEHR INFOS!",font=fit(d,"FÜR MEHR INFOS!",FA,int(130*cl(pv)),900),fill=LED,anchor="mm")
        d.rounded_rectangle([260,y0+420,820,y0+520],50,fill=TQ)
        d.text((W//2,y0+470),"GAMING FACTS & NEWS",font=F(FB,40),fill=BG,anchor="mm")
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); od=ImageDraw.Draw(ov)
    od.rounded_rectangle([PX+24,PY+24,PX+244,PY+76],26,fill=(0,0,0,130)); od.text((PX+134,PY+50),"KI-generiert",font=F(FM,32),fill=(255,255,255,215),anchor="mm")
    im=im.convert("RGBA"); im.alpha_composite(ov); return im.convert("RGB")
N=int(TOTAL*FPS)+int(0.6*FPS)
if PREV:
    ts=[0.0,2.5,5,8.5,10.5,11.6,13,15.0,17.0,19.5,21.5,23.5,25,28.4,29.0,30.5]
    sheet=Image.new("RGB",(W//4*8,H//4*2),(0,0,0))
    for k,tt in enumerate(ts): sheet.paste(frame(tt).resize((W//4,H//4)),((k%8)*W//4,(k//8)*H//4))
    sheet.save(PREV); frame(0).save(PREV.replace(".png","_f0.png")); sys.exit()
p=subprocess.Popen(["ffmpeg","-y","-v","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-c:v","libx264","-preset","veryfast","-crf","21","-pix_fmt","yuv420p",OUT],stdin=subprocess.PIPE)
for n in range(N): p.stdin.write(frame(n/FPS).tobytes())
p.stdin.close(); p.wait()
