# Vorlage "Auktionshaus/Online-Gebot" (Creme/Schwarz/Signal-Orange/Dunkelgrün): Live-Auktions-Kopfzeile, Bildpanel mit
# Preisschild, Gebotszähler der hochtickt, Shop-Liste mit AUSVERKAUFT-Stempeln, UVP-vs-Gebot-Balken, Rabatt-0-%-Karte,
# Entweder-oder-Buttons. Aufruf: python3 auktion.py <vo.mp3> <out_noaudio.mp4> <bilder_dir> [preview.png]
import sys, subprocess, math, os
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
W,H,FPS=1080,1920,30
FB="/usr/share/fonts/opentype/inter/Inter-Black.otf"; FM="/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf"
FA="/usr/share/fonts/truetype/google-fonts/ofl/anton/Anton-Regular.ttf"; FMO="/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
BG=(244,237,224); INK=(22,20,18); OR=(255,92,22); GR=(18,104,70); GY=(120,112,100); WH=(255,255,255); CARD=(255,250,240)
VO,OUT,BD=sys.argv[1],sys.argv[2],sys.argv[3]; PREV=sys.argv[4] if len(sys.argv)>4 else None
TOTAL=float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",VO]))
S=[0,5.36,7.28,14.2,17.34,20.77,25.25,29.49]
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
PX,PY,PW,PH=50,300,980,620
def prep(n,col,ctr,tint=None,a=0.2):
    im=Image.open(os.path.join(BD,n)).convert("RGB")
    im=ImageEnhance.Contrast(ImageEnhance.Color(im).enhance(col)).enhance(ctr)
    if tint: im=Image.blend(im,Image.new("RGB",im.size,tint),a)
    r=PW*1.4/im.width; return im.resize((int(im.width*r),int(im.height*r)),Image.LANCZOS)
IM={"con":prep("controller.png",0.8,1.15,OR,0.22),"geld":prep("geldregen.png",0.9,1.1,(255,140,0),0.15),
    "reg":prep("spieleregal.png",0.7,1.1,(60,40,20),0.25),"cou":prep("couch_gamer.png",0.9,1.1,GR,0.2)}
def crop(key,z,ox,oy):
    im=IM[key]; cw=int(im.width*z); ch=int(cw*PH/PW)
    if ch>im.height: ch=im.height; cw=int(ch*PW/PH)
    x=int((im.width-cw)*ox); y=int((im.height-ch)*oy)
    return im.crop((x,y,x+cw,y+ch)).resize((PW,PH),Image.BILINEAR)
def panel(t,i):
    if i<=1: k=t/7.3; return crop("con",0.62-0.1*k,0.45+0.1*k,0.55)
    if i==2: k=(t-S[2])/7; return crop("reg",0.75-0.12*k,0.2+0.6*k,0.5)
    if i==3: k=(t-S[3])/3.2; return crop("geld",0.7-0.15*k,0.4,0.4)
    if i==4: k=(t-S[4])/3.4; return crop("con",0.8,0.2+0.2*k,0.4)
    if i==5: k=(t-S[5])/4.5; return crop("reg",0.6,0.9-0.3*k,0.3)
    k=(t-S[6])/6; return crop("cou",0.8-0.1*k,0.5,0.45)
MASK=Image.new("L",(PW,PH),0); ImageDraw.Draw(MASK).rounded_rectangle([0,0,PW-1,PH-1],28,fill=255)
def header(d,t):
    d.rectangle([0,0,W,280],fill=INK)
    on=int(t*2)%2==0
    d.ellipse([60,200,92,232],fill=OR if on else (110,40,10))
    d.text((112,216),"AUKTION LIVE",font=F(FB,46),fill=WH,anchor="lm")
    d.text((W-60,216),"LOS: PS5 PRO",font=F(FMO,38),fill=OR,anchor="rm")
def pricetag(im,x,y,txt,sub,col,sc=1.0,ang=-6):
    if sc<=0: return
    w,h=560,250; tg=Image.new("RGBA",(w,h),(0,0,0,0)); d=ImageDraw.Draw(tg)
    d.polygon([(0,h//2),(70,0),(w-1,0),(w-1,h-1),(70,h-1)],fill=col)
    d.ellipse([40,h//2-18,76,h//2+18],fill=BG)
    d.text((w//2+40,100),txt,font=fit(d,txt,FA,150,w-140),fill=WH,anchor="mm")
    d.text((w//2+40,200),sub,font=fit(d,sub,FB,40,w-140),fill=WH,anchor="mm")
    tg=tg.rotate(ang,expand=True,resample=Image.BICUBIC)
    tg=tg.resize((max(1,int(tg.width*sc)),max(1,int(tg.height*sc))),Image.BILINEAR)
    im.paste(tg,(int(x-tg.width/2),int(y-tg.height/2)),tg)
def stamp(im,text,col,cx,cy,ang,sc,w=820,h=240,size=140):
    if sc<=0: return
    tmp=Image.new("RGBA",(w+40,h+40),(0,0,0,0)); d=ImageDraw.Draw(tmp)
    d.rounded_rectangle([10,10,w+29,h+29],20,outline=col,width=13)
    d.text(((w+40)//2,(h+40)//2),text,font=fit(d,text,FA,size,w-60),fill=col,anchor="mm")
    tmp=tmp.rotate(ang,expand=True,resample=Image.BICUBIC)
    s=max(0.05,sc); tmp=tmp.resize((int(tmp.width*s),int(tmp.height*s)),Image.BILINEAR)
    im.paste(tmp,(int(cx-tmp.width/2),int(cy-tmp.height/2)),tmp)
def frame(t):
    i=seg(t); im=Image.new("RGB",(W,H),BG); d=ImageDraw.Draw(im)
    header(d,t)
    im.paste(panel(t,i),(PX,PY),MASK)
    d.rounded_rectangle([PX,PY,PX+PW,PY+PH],28,outline=INK,width=6)
    y0=980
    if i==0:
        pricetag(im,730,PY+460,"1.500 $","GEBOT FÜR EINE PS5 PRO",OR,1.0)
        d.text((70,y0),"WER DAS ZAHLT,",font=fit(d,"WER DAS ZAHLT,",FA,150,940),fill=INK,anchor="lt")
        s=1+0.03*math.sin(t*6); txt="IST SELBST SCHULD!"
        f=fit(d,txt,FA,int(130*s),900); bw=d.textlength(txt,font=f)+60
        d.rounded_rectangle([60,y0+215,60+bw,y0+380],24,fill=OR)
        d.text((60+bw/2,y0+297),txt,font=f,fill=WH,anchor="mm")
        d.text((70,y0+450),"Steile These? Lies weiter.",font=F(FM,46),fill=GY,anchor="lt")
    elif i==1:
        pricetag(im,730,PY+460,"1.500 $","GEBOT FÜR EINE PS5 PRO",OR,1.0)
        pv=pop((t-S[1])/0.35)
        d.text((W//2,y0+130),"JA.",font=F(FA,int(220*max(0.3,min(1.1,pv)))),fill=INK,anchor="mm")
        if t>S[1]+0.6:
            d.text((W//2,y0+330),"ICH HAB'S GESAGT.",font=fit(d,"ICH HAB'S GESAGT.",FA,int(120*min(1.05,pop((t-S[1]-0.6)/0.3)+0.01)),940),fill=OR,anchor="mm")
    elif i==2:
        d.text((70,y0-10),"GTA-WOCHE · LAUT IGN",font=F(FMO,40),fill=GY,anchor="lt")
        shops=[("BEST BUY",8.6),("TARGET",9.6),("GAMESTOP",10.5),("PLAYSTATION DIRECT",11.8)]
        for k,(n,ts) in enumerate(shops):
            pv=ease((t-S[2]-0.15*k)/0.4)
            if pv<=0: continue
            y=y0+60+k*150; dx=int((1-pv)*400)
            d.rounded_rectangle([60+dx,y,1020+dx,y+125],20,fill=CARD,outline=INK,width=4)
            d.text((100+dx,y+62),n,font=fit(d,n,FB,58,520),fill=INK,anchor="lm")
            if t>ts:
                stamp(im,"AUSVERKAUFT",OR,820,y+62,-7,pop((t-ts)/0.25)*0.42,size=150)
    elif i==3:
        k=ease((t-S[3]-0.3)/1.9); v=int(900+600*k)
        d.text((W//2,y0+40),"WIEDERVERKÄUFER-GEBOT",font=F(FMO,44),fill=GY,anchor="mm")
        txt=f"~{v:,}".replace(",",".")+" $"
        d.text((W//2,y0+230),txt,font=F(FA,230),fill=OR,anchor="mm")
        d.text((W//2,y0+420),"Stichprobe von IGN, 18.11.",font=F(FM,46),fill=INK,anchor="mm")
        if t>S[3]+2.4: stamp(im,"ZUSCHLAG?!",INK,W//2,PY+PH//2,-8,pop((t-S[3]-2.4)/0.3)*0.9)
    elif i==4:
        d.text((70,y0-10),"PREIS-CHECK",font=F(FMO,44),fill=GY,anchor="lt")
        bars=[("UVP",899.99,"899,99 $ / € (EU)",GR,S[4]+0.2),("SCALPER",1500,"~1.500 $",OR,S[4]+1.3)]
        for k,(lab,val,txt,col,ts) in enumerate(bars):
            pv=ease((t-ts)/0.7)
            if pv<=0: continue
            y=y0+70+k*220
            d.text((70,y),lab,font=F(FB,52),fill=INK,anchor="lt")
            bw=int(900*val/1500*pv); d.rounded_rectangle([70,y+70,70+max(40,bw),y+170],20,fill=col)
            d.text((100,y+120),txt,font=fit(d,txt,FB,54,max(300,bw-60)),fill=WH,anchor="lm")
        if t>S[4]+2.3:
            pv=pop((t-S[4]-2.3)/0.3)
            d.text((W//2,y0+580),"+67 % AUFPREIS",font=F(FA,int(120*max(0.3,min(1.05,pv)))),fill=OR,anchor="mm")
        pricetag(im,800,PY+150,"899,99","OFFIZIELLE UVP",GR,pop((t-S[4])/0.35)*0.8,ang=5)
    elif i==5:
        pv=pop((t-S[5])/0.35)
        d.text((W//2,y0+110),"BLACK FRIDAY?",font=F(FA,int(170*max(0.3,min(1.08,pv)))),fill=INK,anchor="mm")
        if t>21.9:
            pv2=ease((t-21.9)/0.4)
            d.rounded_rectangle([90,y0+250,990,y0+560],28,fill=CARD,outline=INK,width=5)
            d.text((W//2,y0+320),"RABATT AUF DIE PRO",font=F(FB,52),fill=GY,anchor="mm")
            d.text((W//2,y0+450),"0 %",font=F(FA,int(180*max(0.3,pv2))),fill=OR,anchor="mm")
            d.text((W//2,y0+620),"laut IGN · PS-Sale 16.–30.11.",font=F(FM,44),fill=INK,anchor="mm")
        if t>23.6: stamp(im,"KEIN RABATT",OR,W//2,PY+PH//2,7,pop((t-23.6)/0.3)*0.9)
    elif i==6:
        d.text((W//2,y0+50),"DEINE ENTSCHEIDUNG",font=F(FMO,46),fill=GY,anchor="mm")
        for k,(lab,col,ts) in enumerate([("SCALPER BEZAHLEN",OR,S[6]+0.6),("EINFACH WARTEN",GR,26.9)]):
            pv=pop((t-ts)/0.35)
            if pv<=0: continue
            y=y0+120+k*230; sc=min(1.06,pv)
            d.rounded_rectangle([90,y,990,y+160],80,fill=col)
            d.text((W//2,y+80),lab,font=fit(d,lab,FB,int(70*sc),800),fill=WH,anchor="mm")
        if t>27.3: d.text((W//2,y0+315),"ODER",font=F(FA,60),fill=INK,anchor="mm")
        if t>28.1: d.text((W//2,y0+600),"Schreib's in die Kommentare!",font=F(FB,52),fill=INK,anchor="mm")
    else:
        pv=pop((t-S[7])/0.4)
        d.text((W//2,y0+150),"FOLGE DEM KANAL",font=fit(d,"FOLGE DEM KANAL",FA,int(150*max(0.3,min(1.08,pv))),960),fill=INK,anchor="mm")
        d.text((W//2,y0+310),"FÜR MEHR INFOS!",font=fit(d,"FÜR MEHR INFOS!",FA,int(130*max(0.3,min(1.08,pv))),900),fill=OR,anchor="mm")
        d.rounded_rectangle([260,y0+420,820,y0+520],50,fill=INK)
        d.text((W//2,y0+470),"GAMING FACTS & NEWS",font=F(FB,40),fill=WH,anchor="mm")
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); od=ImageDraw.Draw(ov)
    od.rounded_rectangle([PX+24,PY+PH-76,PX+244,PY+PH-24],26,fill=(0,0,0,120)); od.text((PX+134,PY+PH-50),"KI-generiert",font=F(FM,32),fill=(255,255,255,215),anchor="mm")
    im=im.convert("RGBA"); im.alpha_composite(ov); return im.convert("RGB")
N=int(TOTAL*FPS)+int(0.6*FPS)
if PREV:
    ts=[0.0,3,6.5,8.2,10.8,12.6,15.5,17.0,19.6,21.2,24.2,26,28.6,30.5]
    sheet=Image.new("RGB",(W//4*7,H//4*2),(0,0,0))
    for k,tt in enumerate(ts): sheet.paste(frame(tt).resize((W//4,H//4)),((k%7)*W//4,(k//7)*H//4))
    sheet.save(PREV); frame(0).save(PREV.replace(".png","_f0.png")); sys.exit()
p=subprocess.Popen(["ffmpeg","-y","-v","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-c:v","libx264","-preset","veryfast","-crf","21","-pix_fmt","yuv420p",OUT],stdin=subprocess.PIPE)
for n in range(N): p.stdin.write(frame(n/FPS).tobytes())
p.stdin.close(); p.wait()
