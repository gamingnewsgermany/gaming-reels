# Vorlage "Transfer-Ticker" (Rasengrün-Nacht/Gold/Magenta/Weiß): Sport-Breaking-News-Look mit Laufband, Bildpanel,
# Vertrags-Dokument mit Klauseln + animierter Unterschrift, NICHT-EXKLUSIV-Stempel, Bühnen-Spotlight, Release-Anzeigetafel,
# Entweder-oder-Buttons. Aufruf: python3 transfer_ticker.py <vo.mp3> <out_noaudio.mp4> <bilder_dir> [preview.png]
import sys, subprocess, math, os
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
W,H,FPS=1080,1920,30
FB="/usr/share/fonts/opentype/inter/Inter-Black.otf"; FM="/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf"
FA="/usr/share/fonts/truetype/google-fonts/ofl/anton/Anton-Regular.ttf"; FMO="/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
BG=(8,34,24); PAN=(16,56,40); GO=(246,192,46); MG=(232,38,112); WH=(255,255,255); GY=(160,190,175); PA=(248,244,232); INK=(22,30,60)
VO,OUT,BD=sys.argv[1],sys.argv[2],sys.argv[3]; PREV=sys.argv[4] if len(sys.argv)>4 else None
TOTAL=float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",VO]))
S=[0,5.55,12.95,15.15,17.35,20.35,23.65]
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
PX,PY,PW,PH=50,300,980,560
def prep(n,col,ctr,tint=None,a=0.2):
    im=Image.open(os.path.join(BD,n)).convert("RGB")
    im=ImageEnhance.Contrast(ImageEnhance.Color(im).enhance(col)).enhance(ctr)
    if tint: im=Image.blend(im,Image.new("RGB",im.size,tint),a)
    r=PW*1.5/im.width; return im.resize((int(im.width*r),int(im.height*r)),Image.LANCZOS)
IM={"couch":prep("couch_gamer.png",0.9,1.15,(20,90,60),0.22),"messe":prep("messe.png",0.8,1.2,MG,0.16),
    "count":prep("countdown.png",0.85,1.1,GO,0.12)}
def crop(key,z,ox,oy):
    im=IM[key]; cw=int(im.width*z); ch=int(cw*PH/PW)
    if ch>im.height: ch=im.height; cw=int(ch*PW/PH)
    x=int((im.width-cw)*ox); y=int((im.height-ch)*oy)
    return im.crop((x,y,x+cw,y+ch)).resize((PW,PH),Image.BILINEAR)
def panel(t,i):
    if i==0: k=t/5.55; return crop("couch",0.62-0.1*k,0.75,0.25)
    if i==1: k=(t-S[1])/7.4; return crop("couch",0.8-0.1*k,0.2+0.3*k,0.6)
    if i==2: return crop("couch",0.5,0.9,0.2)
    if i==3: k=(t-S[3])/2.2; return crop("messe",0.7-0.12*k,0.5,0.15)
    if i==4: k=(t-S[4])/3; return crop("count",0.6-0.08*k,0.25+0.1*k,0.4)
    if i==5: k=(t-S[5])/3.3; return crop("messe",0.9-0.1*k,0.3+0.3*k,0.5)
    return crop("couch",0.85,0.5,0.4)
MASK=Image.new("L",(PW,PH),0); ImageDraw.Draw(MASK).rounded_rectangle([0,0,PW-1,PH-1],24,fill=255)
TICK="+++ CD PROJEKT × SONY +++ DEAL VOM 24.11.2026 +++ MARKETING FÜR THE WITCHER 4 +++ RELEASE 2028 GEPLANT +++ "
def header(d,t):
    d.rectangle([0,0,W,262],fill=PAN)
    d.rounded_rectangle([50,150,300,206],10,fill=MG)
    d.text((175,178),"BREAKING",font=F(FB,36),fill=WH,anchor="mm")
    d.text((325,178),"TRANSFER-TICKER",font=F(FB,46),fill=WH,anchor="lm")
    d.rectangle([0,218,W,262],fill=GO)
    f=F(FMO,28); tw=d.textlength(TICK,font=f); x=-(t*170)%tw
    for k in range(3): d.text((x-tw+k*tw,240),TICK,font=f,fill=BG,anchor="lm")
def stamp(im,text,col,cx,cy,ang,sc,w=820,h=230,size=140):
    if sc<=0: return
    tmp=Image.new("RGBA",(w+40,h+40),(0,0,0,0)); d=ImageDraw.Draw(tmp)
    d.rounded_rectangle([10,10,w+29,h+29],20,outline=col,width=13)
    d.text(((w+40)//2,(h+40)//2),text,font=fit(d,text,FA,size,w-60),fill=col,anchor="mm")
    tmp=tmp.rotate(ang,expand=True,resample=Image.BICUBIC)
    s=max(0.05,sc); tmp=tmp.resize((int(tmp.width*s),int(tmp.height*s)),Image.BILINEAR)
    im.paste(tmp,(int(cx-tmp.width/2),int(cy-tmp.height/2)),tmp)
def contract(im,t):
    # Vertragsblatt über Panel + Textbereich
    k=ease((t-S[1])/0.35); y0=int(930+(1-k)*700)
    d=ImageDraw.Draw(im)
    d.rounded_rectangle([70,y0,1010,y0+760],18,fill=PA,outline=GO,width=6)
    d.text((W//2,y0+70),"VERTRAG",font=F(FA,84),fill=INK,anchor="mm")
    d.text((W//2,y0+140),"CD PROJEKT  ×  SONY · 24.11.2026",font=fit(d,"CD PROJEKT  ×  SONY · 24.11.2026",FMO,36,860),fill=(90,90,110),anchor="mm")
    d.line([(120,y0+185),(960,y0+185)],fill=(200,195,180),width=3)
    cl_=[("§1","Marketing für The Witcher 4",8.0),("§2","CD-Projekt-Spiele auf PS Plus",10.1)]
    for n,(p,txt,ts) in enumerate(cl_):
        if t<ts: continue
        pv=ease((t-ts)/0.3); yy=y0+250+n*130
        d.text((120,yy),p,font=F(FB,52),fill=MG,anchor="lm")
        d.text((210,yy),txt,font=fit(d,txt,FB,int(50*pv)+1,660),fill=INK,anchor="lm")
        if t>ts+0.35:
            d.rounded_rectangle([890,yy-34,958,yy+34],10,fill=(30,150,90))
            d.line([(905,yy),(920,yy+16),(945,yy-18)],fill=WH,width=9)
    # Unterschrift (animiert)
    d.line([(120,y0+640),(620,y0+640)],fill=(120,120,130),width=3)
    d.text((120,y0+680),"Unterschrift",font=F(FM,30),fill=(120,120,130),anchor="lm")
    p=ease((t-6.2)/1.4)
    if p>0:
        pts=[]; n=int(60*p)
        for j in range(n+1):
            x=140+j*7.5; y=y0+600+28*math.sin(j*0.55)*math.exp(-j/80)-14*math.sin(j*0.21)
            pts.append((x,y))
        if len(pts)>1: d.line(pts,fill=INK,width=7,joint="curve")
    if t>12.0: d.text((790,y0+620),"✓ DEAL",font=F(FB,56),fill=(30,150,90),anchor="mm")
def frame(t):
    i=seg(t); im=Image.new("RGB",(W,H),BG); d=ImageDraw.Draw(im)
    header(d,t)
    im.paste(panel(t,i),(PX,PY),MASK)
    d.rounded_rectangle([PX,PY,PX+PW,PY+PH],24,outline=GO,width=5)
    y0=920
    if i==0:
        d.text((70,y0),"ERST GTA VI,",font=fit(d,"ERST GTA VI,",FA,150,940),fill=WH,anchor="lt")
        d.text((70,y0+175),"JETZT WITCHER 4",font=fit(d,"JETZT WITCHER 4",FA,150,940),fill=GO,anchor="lt")
        s=1+0.03*math.sin(t*6); txt="KAUFT SONY JEDES MEGA-GAME?"
        f=fit(d,txt,FA,int(92*s),880); bw=d.textlength(txt,font=f)+60
        d.rounded_rectangle([60,y0+380,60+bw,y0+530],24,fill=MG)
        d.text((60+bw/2,y0+455),txt,font=f,fill=WH,anchor="mm")
        d.text((70,y0+590),"Neuer Deal – unterschrieben am 24.11.",font=fit(d,"Neuer Deal – unterschrieben am 24.11.",FM,48,940),fill=GY,anchor="lt")
    elif i==1:
        contract(im,t)
    elif i==2:
        pv=pop((t-S[2])/0.3)
        d.text((W//2,y0+120),"EXKLUSIV?",font=F(FA,int(230*cl(pv))),fill=WH,anchor="mm")
        stamp(im,"NEIN",MG,W//2,y0+400,-9,pop((t-14.1)/0.3)*0.85,w=600,h=220,size=170)
        if t>14.35: d.text((W//2,y0+620),"laut Berichten zum CD-Projekt-Quartalsbericht",font=fit(d,"laut Berichten zum CD-Projekt-Quartalsbericht",FM,40,960),fill=GY,anchor="mm")
    elif i==3:
        # Spotlight auf Panel
        ov=Image.new("RGBA",(PW,PH),(0,0,0,0)); od=ImageDraw.Draw(ov)
        od.polygon([(PW//2-60,0),(PW//2+60,0),(PW//2+330,PH),(PW//2-330,PH)],fill=(255,240,180,70))
        ov=ov.filter(ImageFilter.GaussianBlur(18)); im.paste(ov,(PX,PY),ov); d=ImageDraw.Draw(im)
        pv=pop((t-S[3])/0.35)
        d.text((W//2,y0+80),"WER ZAHLT,",font=F(FA,int(150*cl(pv))),fill=WH,anchor="mm")
        if t>16.0:
            pv2=pop((t-16.0)/0.3); txt="BEKOMMT DIE BÜHNE"
            f=fit(d,txt,FA,int(110*cl(pv2)),900); bw=d.textlength(txt,font=f)+60
            d.rounded_rectangle([W//2-bw/2,y0+200,W//2+bw/2,y0+350],24,fill=GO)
            d.text((W//2,y0+275),txt,font=f,fill=BG,anchor="mm")
        if t>16.4: d.text((W//2,y0+450),"Meinung · keine Exklusivität bestätigt",font=F(FM,42),fill=GY,anchor="mm")
    elif i==4:
        d.text((W//2,y0+30),"RELEASE GEPLANT",font=F(FB,62),fill=GY,anchor="mm")
        # Anzeigetafel mit Flip-Ziffern
        digits="2028"; p=(t-S[4])
        for k,c in enumerate(digits):
            x=150+k*200; ts=0.15+k*0.18
            show=c if p>ts+0.5 else str(int((p*23+k*3))%10) if p>ts else " "
            d.rounded_rectangle([x,y0+110,x+180,y0+390],18,fill=(5,18,12),outline=GO,width=5)
            d.line([(x+6,y0+250),(x+174,y0+250)],fill=(0,0,0),width=4)
            d.text((x+90,y0+250),show,font=F(FA,210),fill=GO,anchor="mm")
        if t>18.6:
            pv=pop((t-18.6)/0.3)
            d.text((W//2,y0+500),"Noch über ein Jahr Hype-Marketing.",font=fit(d,"Noch über ein Jahr Hype-Marketing.",FB,int(56*cl(pv)),960),fill=WH,anchor="mm")
        if t>19.2: d.text((W//2,y0+590),"Release-Fenster laut CD Projekt",font=F(FM,40),fill=GY,anchor="mm")
    elif i==5:
        pv=pop((t-S[5])/0.35)
        d.text((W//2,y0+60),"UND JETZT DU:",font=F(FA,int(120*cl(pv))),fill=WH,anchor="mm")
        for k,(lab,col,ts) in enumerate([("CLEVERER MOVE",GO,21.0),("UNFAIR GEGEN XBOX",MG,22.0)]):
            pv2=pop((t-ts)/0.35)
            if pv2<=0: continue
            y=y0+190+k*200; sc=min(1.06,pv2)
            d.rounded_rectangle([110,y,970,y+160],80,fill=col)
            d.text((W//2,y+80),lab,font=fit(d,lab,FB,int(68*sc),760),fill=BG if col==GO else WH,anchor="mm")
        if t>22.6: d.text((W//2,y0+620),"Schreib's in die Kommentare!",font=F(FB,48),fill=WH,anchor="mm")
    else:
        pv=pop((t-S[6])/0.4)
        d.text((W//2,y0+150),"FOLGE DEM KANAL",font=fit(d,"FOLGE DEM KANAL",FA,int(150*cl(pv)),960),fill=WH,anchor="mm")
        d.text((W//2,y0+310),"FÜR MEHR INFOS!",font=fit(d,"FÜR MEHR INFOS!",FA,int(130*cl(pv)),900),fill=GO,anchor="mm")
        d.rounded_rectangle([260,y0+420,820,y0+520],50,fill=MG)
        d.text((W//2,y0+470),"GAMING FACTS & NEWS",font=F(FB,40),fill=WH,anchor="mm")
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); od=ImageDraw.Draw(ov)
    od.rounded_rectangle([PX+24,PY+24,PX+244,PY+76],26,fill=(0,0,0,130)); od.text((PX+134,PY+50),"KI-generiert",font=F(FM,32),fill=(255,255,255,215),anchor="mm")
    im=im.convert("RGBA"); im.alpha_composite(ov); return im.convert("RGB")
N=int(TOTAL*FPS)+int(0.6*FPS)
if PREV:
    ts=[0.0,3.0,6.0,7.5,9.0,11.0,12.5,13.4,14.6,15.6,16.8,17.8,19.5,21.5,22.8,24.5]
    sheet=Image.new("RGB",(W//4*8,H//4*2),(0,0,0))
    for k,tt in enumerate(ts): sheet.paste(frame(tt).resize((W//4,H//4)),((k%8)*W//4,(k//8)*H//4))
    sheet.save(PREV); frame(0).save(PREV.replace(".png","_f0.png")); sys.exit()
p=subprocess.Popen(["ffmpeg","-y","-v","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-c:v","libx264","-preset","veryfast","-crf","21","-pix_fmt","yuv420p",OUT],stdin=subprocess.PIPE)
for n in range(N): p.stdin.write(frame(n/FPS).tobytes())
p.stdin.close(); p.wait()
