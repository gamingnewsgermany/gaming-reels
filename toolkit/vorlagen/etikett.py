# Vorlage "Bio-Etikett/Zutatenliste" (Kraftpapier/Dunkelbraun/Blattgrün/Tomatenrot): Etikett-Kopfzeile mit Barcode,
# Bildpanel mit eigenem rundem Siegel, Nährwert-/Zutatentabelle mit 0-%-Zeilen, Prüf-Checkliste, KI-Stempel-Twist,
# JA/NEIN-Buttons. Aufruf: python3 etikett.py <vo.mp3> <out_noaudio.mp4> <bilder_dir> [preview.png]
import sys, subprocess, math, os
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
W,H,FPS=1080,1920,30
FB="/usr/share/fonts/opentype/inter/Inter-Black.otf"; FM="/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf"
FA="/usr/share/fonts/truetype/google-fonts/ofl/archivoblack/ArchivoBlack-Regular.ttf"; FMO="/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
KR=(214,184,140); KRD=(190,158,112); BR=(58,38,24); GR=(52,128,58); RD=(214,58,38); CR=(250,243,228); WH=(255,255,255)
VO,OUT,BD=sys.argv[1],sys.argv[2],sys.argv[3]; PREV=sys.argv[4] if len(sys.argv)>4 else None
TOTAL=float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",VO]))
S=[0,4.6,8.1,11.5,15.3,20.6,23.6,28.1]
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
PX,PY,PW,PH=60,300,960,580
def prep(n,col,ctr,tint=None,a=0.2):
    im=Image.open(os.path.join(BD,n)).convert("RGB")
    im=ImageEnhance.Contrast(ImageEnhance.Color(im).enhance(col)).enhance(ctr)
    if tint: im=Image.blend(im,Image.new("RGB",im.size,tint),a)
    r=PW*1.45/im.width; return im.resize((int(im.width*r),int(im.height*r)),Image.LANCZOS)
IM={"ctl":prep("controller.png",0.9,1.1,(200,150,80),0.22),"regal":prep("spieleregal.png",0.8,1.1,GR,0.18),
    "pc":prep("gaming_pc.png",0.5,1.15,RD,0.22)}
def crop(key,z,ox,oy):
    im=IM[key]; cw=int(im.width*z); ch=int(cw*PH/PW)
    if ch>im.height: ch=im.height; cw=int(ch*PW/PH)
    x=int((im.width-cw)*ox); y=int((im.height-ch)*oy)
    return im.crop((x,y,x+cw,y+ch)).resize((PW,PH),Image.BILINEAR)
def panel(t,i):
    if i==0: k=t/4.6; return crop("ctl",0.6-0.08*k,0.45,0.5)
    if i in (1,2): k=(t-S[1])/6.9; return crop("regal",0.75-0.12*k,0.2+0.5*k,0.5)
    if i in (3,4): k=(t-S[3])/9.1; return crop("regal",0.55,0.8-0.4*k,0.3)
    if i==5: k=(t-S[5])/3; return crop("pc",0.7-0.1*k,0.5,0.5)
    if i==6: k=(t-S[6])/4.5; return crop("ctl",0.8-0.1*k,0.3+0.3*k,0.5)
    return crop("ctl",0.85,0.5,0.5)
MASK=Image.new("L",(PW,PH),0); ImageDraw.Draw(MASK).rounded_rectangle([0,0,PW-1,PH-1],30,fill=255)
# Kraftpapier-Textur (statisch)
import random
random.seed(7); BASE=Image.new("RGB",(W,H),KR); bd=ImageDraw.Draw(BASE)
for _ in range(2600):
    x,y=random.randint(0,W),random.randint(0,H); c=random.choice([KRD,(222,194,152),(200,170,126)])
    bd.line([(x,y),(x+random.randint(4,30),y+random.randint(-2,2))],fill=c,width=1)
def header(d,t):
    d.rectangle([0,0,W,250],fill=BR); d.rectangle([0,250,W,262],fill=GR)
    d.text((60,170),"ZUTATENLISTE",font=F(FA,54),fill=CR,anchor="lm")
    d.text((60,222),"GAMING · FRISCH VON HEUTE",font=F(FMO,28),fill=(200,180,150),anchor="lm")
    random.seed(3); x=760
    while x<1020:
        w=random.choice([3,5,8]); d.rectangle([x,140,x+w,215],fill=CR); x+=w+random.choice([3,5,7])
def seal(im,cx,cy,sc,top="100 %",bot="OHNE KI",col=GR,ang=-12):
    if sc<=0: return
    s=360; tmp=Image.new("RGBA",(s,s),(0,0,0,0)); d=ImageDraw.Draw(tmp)
    d.ellipse([6,6,s-6,s-6],fill=col+(255,),outline=CR+(255,),width=10)
    d.ellipse([34,34,s-34,s-34],outline=CR+(255,),width=4)
    for a in range(0,360,30):
        r=a*math.pi/180; x,y=s/2+math.cos(r)*150,s/2+math.sin(r)*150; d.ellipse([x-5,y-5,x+5,y+5],fill=CR)
    d.text((s//2,s//2-50),top,font=F(FA,62),fill=CR,anchor="mm")
    d.text((s//2,s//2+40),bot,font=fit(d,bot,FA,58,250),fill=CR,anchor="mm")
    tmp=tmp.rotate(ang,expand=True,resample=Image.BICUBIC); z=max(0.05,sc)
    tmp=tmp.resize((int(tmp.width*z),int(tmp.height*z)),Image.BILINEAR)
    im.paste(tmp,(int(cx-tmp.width/2),int(cy-tmp.height/2)),tmp)
def stamp(im,text,col,cx,cy,ang,sc,w=860,h=230,size=130):
    if sc<=0: return
    tmp=Image.new("RGBA",(w+40,h+40),(0,0,0,0)); d=ImageDraw.Draw(tmp)
    d.rounded_rectangle([10,10,w+29,h+29],18,outline=col,width=14)
    d.text(((w+40)//2,(h+40)//2),text,font=fit(d,text,FA,size,w-70),fill=col,anchor="mm")
    tmp=tmp.rotate(ang,expand=True,resample=Image.BICUBIC)
    s=max(0.05,sc); tmp=tmp.resize((int(tmp.width*s),int(tmp.height*s)),Image.BILINEAR)
    im.paste(tmp,(int(cx-tmp.width/2),int(cy-tmp.height/2)),tmp)
def card(d,x0,y,x1,h,dx,col):
    d.rounded_rectangle([x0+dx+8,y+8,x1+dx+8,y+h+8],20,fill=KRD)
    d.rounded_rectangle([x0+dx,y,x1+dx,y+h],20,fill=CR,outline=BR,width=5)
    d.rectangle([x0+dx,y+18,x0+dx+18,y+h-18],fill=col)
def frame(t):
    i=seg(t); im=BASE.copy(); d=ImageDraw.Draw(im)
    header(d,t)
    d.rounded_rectangle([PX+10,PY+10,PX+PW+10,PY+PH+10],30,fill=KRD)
    im.paste(panel(t,i),(PX,PY),MASK)
    d.rounded_rectangle([PX,PY,PX+PW,PY+PH],30,outline=BR,width=7)
    y0=950
    if i==0:
        seal(im,PX+PW-170,PY+PH-150,1.0+0.03*math.sin(t*5))
        d.text((70,y0),"SPIELE OHNE KI",font=fit(d,"SPIELE OHNE KI",FA,150,940),fill=BR,anchor="lt")
        txt="BIO-SIEGEL ODER MARKETING?"
        f=fit(d,txt,FA,74,880); bw=d.textlength(txt,font=f)+60
        d.rounded_rectangle([60,y0+200,60+bw,y0+330],22,fill=RD)
        d.text((60+bw/2,y0+265),txt,font=f,fill=WH,anchor="mm")
        d.text((70,y0+390),"Ab heute auf Steam – im Ernst.",font=F(FM,50),fill=GR,anchor="lt")
    elif i==1:
        pv=pop((t-S[1])/0.35)
        d.text((W//2,y0+30),"STEAM-FESTIVAL",font=F(FMO,44),fill=BR,anchor="mm")
        lab="„GAMES WITHOUT AI“"
        card(d,60,y0+90,1020,200,0,GR)
        d.text((W//2+10,y0+190),lab,font=fit(d,lab,FA,int(84*cl(pv)),880),fill=BR,anchor="mm")
        if t>5.9:
            pv2=pop((t-5.9)/0.35)
            d.rounded_rectangle([200,y0+340,880,y0+480],70,fill=BR)
            d.text((W//2,y0+410),"25.11. – 6.12.",font=F(FA,int(72*cl(pv2))),fill=CR,anchor="mm")
        if t>6.8: d.text((W//2,y0+560),"Showcase heute 18 Uhr · Partner: IGN",font=fit(d,"Showcase heute 18 Uhr · Partner: IGN",FM,44,940),fill=BR,anchor="mm")
    elif i==2:
        pv=pop((t-S[2])/0.35); k=ease((t-S[2])/1.2); n=int(95*k)
        d.text((W//2,y0+170),f"{n}",font=F(FA,int(330*cl(pv))),fill=GR,anchor="mm")
        d.text((W//2,y0+380),"INDIE-SPIELE",font=F(FA,90),fill=BR,anchor="mm")
        if t>9.6:
            txt="ohne generative KI"
            d.rounded_rectangle([210,y0+460,870,y0+560],50,fill=RD)
            d.text((W//2,y0+510),txt,font=F(FB,int(52*cl(pop((t-9.6)/0.3)))),fill=WH,anchor="mm")
        seal(im,PX+170,PY+PH-150,pop((t-S[2]-0.3)/0.4)*0.85,ang=10)
    elif i==3:
        d.rectangle([60,y0-20,1020,y0+600],fill=CR,outline=BR,width=6)
        d.text((90,y0+40),"Nährwerte pro Spiel",font=F(FA,58),fill=BR,anchor="lm")
        d.rectangle([80,y0+90,1000,y0+104],fill=BR)
        rows=[("KI-Grafik",11.6),("KI-Musik",12.8),("KI-Stimmen",14.0)]
        for k,(a,ts) in enumerate(rows):
            if t<ts: continue
            pv=pop((t-ts)/0.3); y=y0+150+k*130
            d.text((100,y+50),a,font=F(FB,int(62*cl(pv))),fill=BR,anchor="lm")
            d.text((980,y+50),"0 %",font=F(FA,int(80*cl(pv))),fill=GR,anchor="rm")
            d.line([(90,y+115),(990,y+115)],fill=KRD,width=4)
        if t>14.6: d.text((W//2,y0+560),"Handgemacht: Grafik, Musik, Stimmen",font=fit(d,"Handgemacht: Grafik, Musik, Stimmen",FM,40,900),fill=BR,anchor="mm")
    elif i==4:
        pv=pop((t-S[4])/0.35)
        d.text((W//2,y0+40),"DER BEWEIS?",font=F(FA,int(120*cl(pv))),fill=RD,anchor="mm")
        cards=[("Skizzen & Entwürfe","✓",GR,16.1),("von Menschen geprüft","✓",GR,17.4),("technischer Test","✗",RD,18.9)]
        for k,(a,sym,col,ts) in enumerate(cards):
            p=ease((t-ts)/0.4)
            if p<=0: continue
            y=y0+150+k*165; dx=int((1-p)*450)
            card(d,60,y,1020,135,dx,col)
            d.text((120+dx,y+68),a,font=F(FB,54),fill=BR,anchor="lm")
            d.ellipse([890+dx,y+22,980+dx,y+112],fill=col)
            d.text((935+dx,y+66),sym,font=F("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",62),fill=WH,anchor="mm")
        if t>19.3: stamp(im,"GIBT'S NICHT",RD,W//2,PY+PH//2,-7,pop((t-19.3)/0.3)*0.75)
    elif i==5:
        pv=pop((t-S[5])/0.35)
        d.text((W//2,y0+60),"UND DIESES VIDEO?",font=fit(d,"UND DIESES VIDEO?",FA,int(110*cl(pv)),960),fill=BR,anchor="mm")
        if t>21.4:
            stamp(im,"KI-GENERIERT",RD,W//2,y0+320,-9,pop((t-21.4)/0.3)*1.0,w=900,h=250,size=150)
        if t>22.3: d.text((W//2,y0+560),"Ja. Komplett. Wir stehen dazu. 😅".replace(" 😅",""),font=F(FM,48),fill=GR,anchor="mm")
        seal(im,PX+PW-170,PY+150,pop((t-S[5])/0.3)*0.8,top="0 %",bot="OHNE KI",col=RD,ang=14)
    elif i==6:
        pv=pop((t-S[6])/0.35)
        d.text((W//2,y0+20),"KAUFST DU EIN SPIEL,",font=fit(d,"KAUFST DU EIN SPIEL,",FA,int(84*cl(pv)),960),fill=BR,anchor="mm")
        d.text((W//2,y0+130),"NUR WEIL'S OHNE KI IST?",font=fit(d,"NUR WEIL'S OHNE KI IST?",FA,int(84*cl(pv)),960),fill=RD,anchor="mm")
        for k,(lab,col,ts) in enumerate([("JA, NUR HANDMADE",GR,26.9),("NEIN, EGAL",RD,27.3)]):
            pv2=pop((t-ts)/0.35)
            if pv2<=0: continue
            y=y0+240+k*180; sc=min(1.06,pv2)
            d.rounded_rectangle([110,y,970,y+145],72,fill=col,outline=BR,width=5)
            d.text((W//2,y+72),lab,font=fit(d,lab,FB,int(64*sc),760),fill=WH,anchor="mm")
        if t>27.6: d.text((W//2,y0+640),"Schreib's in die Kommentare!",font=F(FB,48),fill=BR,anchor="mm")
    else:
        pv=pop((t-S[7])/0.4)
        d.text((W//2,y0+150),"FOLGE DEM KANAL",font=fit(d,"FOLGE DEM KANAL",FA,int(130*cl(pv)),960),fill=BR,anchor="mm")
        d.text((W//2,y0+300),"FÜR MEHR INFOS!",font=fit(d,"FÜR MEHR INFOS!",FA,int(120*cl(pv)),900),fill=GR,anchor="mm")
        d.rounded_rectangle([250,y0+410,830,y0+510],50,fill=BR)
        d.text((W//2,y0+460),"GAMING FACTS & NEWS",font=F(FB,40),fill=CR,anchor="mm")
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); od=ImageDraw.Draw(ov)
    od.rounded_rectangle([PX+24,PY+24,PX+244,PY+76],26,fill=(0,0,0,130)); od.text((PX+134,PY+50),"KI-generiert",font=F(FM,32),fill=(255,255,255,215),anchor="mm")
    im=im.convert("RGBA"); im.alpha_composite(ov); return im.convert("RGB")
N=int(TOTAL*FPS)+int(0.6*FPS)
if PREV:
    ts=[0.0,2.5,5.5,7.5,9.0,10.5,12.5,14.8,15.8,17.8,19.8,21.0,22.8,25.5,27.8,29.5]
    sheet=Image.new("RGB",(W//4*8,H//4*2),(0,0,0))
    for k,tt in enumerate(ts): sheet.paste(frame(tt).resize((W//4,H//4)),((k%8)*W//4,(k//8)*H//4))
    sheet.save(PREV); frame(0).save(PREV.replace(".png","_f0.png")); sys.exit()
p=subprocess.Popen(["ffmpeg","-y","-v","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-c:v","libx264","-preset","veryfast","-crf","21","-pix_fmt","yuv420p",OUT],stdin=subprocess.PIPE)
for n in range(N): p.stdin.write(frame(n/FPS).tobytes())
p.stdin.close(); p.wait()
