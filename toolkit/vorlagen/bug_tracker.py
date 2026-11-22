# Vorlage "Bug-Tracker/Fehlermeldung" (Anthrazit/Magenta/Signalgelb/Cyan): Tracker-Kopfzeile, Bildpanel mit RGB-Glitch + Scanlines,
# aufpoppende Fehler-Fenster, Bug-Tickets mit Schweregrad-Label, Stempel, Entweder-oder-Buttons
# Aufruf: python3 bug_tracker.py <vo.mp3> <out_video_noaudio.mp4> <bilder_dir> [preview.png]
import sys, subprocess, math, os, random
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageChops
W,H,FPS=1080,1920,30
FB="/usr/share/fonts/opentype/inter/Inter-Black.otf"; FM="/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf"
FA="/usr/share/fonts/truetype/google-fonts/ofl/anton/Anton-Regular.ttf"; FMO="/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
BG=(20,20,28); BG2=(32,32,44); MG=(255,46,136); YE=(255,214,0); CY=(0,229,255); WH=(245,245,250); GY=(140,140,160)
VO,OUT,BD=sys.argv[1],sys.argv[2],sys.argv[3]; PREV=sys.argv[4] if len(sys.argv)>4 else None
TOTAL=float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",VO]))
S=[0,4.5,8.4,10.0,14.4,17.4,21.0,24.2,28.3]
def seg(t):
    i=0
    for k,s in enumerate(S):
        if t>=s: i=k
    return i
_F={}
def F(fn,s):
    k=(fn,s)
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
PX,PY,PW,PH=50,330,980,640
def prep(n,col,ctr,tint=None):
    im=Image.open(os.path.join(BD,n)).convert("RGB")
    im=ImageEnhance.Contrast(ImageEnhance.Color(im).enhance(col)).enhance(ctr)
    if tint: im=Image.blend(im,Image.new("RGB",im.size,tint),0.18)
    r=PW*1.35/im.width; return im.resize((int(im.width*r),int(im.height*r)),Image.LANCZOS)
IM={"gl":prep("glitch.png",1.2,1.15,MG),"str":prep("strasse.png",1.1,1.15,(40,0,80)),"sky":prep("skyline.png",1.0,1.2,CY),"cou":prep("couch_gamer.png",1.05,1.1,MG)}
def crop(key,z,ox,oy,rot=0):
    im=IM[key]; cw=int(im.width*z); ch=int(cw*PH/PW)
    if ch>im.height: ch=im.height; cw=int(ch*PW/PH)
    x=int((im.width-cw)*ox); y=int((im.height-ch)*oy)
    p=im.crop((x,y,x+cw,y+ch)).resize((PW,PH),Image.BILINEAR)
    if rot: p=p.rotate(rot,resample=Image.BILINEAR,expand=False).resize((PW,PH))
    if rot: p=p.crop((60,40,PW-60,PH-40)).resize((PW,PH),Image.BILINEAR)
    return p
def glitch(p,t,amt):
    if amt<=0: return p
    r,g,b=p.split(); o=int(amt)
    r=ImageChops.offset(r,o,0); b=ImageChops.offset(b,-o,0)
    p=Image.merge("RGB",(r,g,b))
    rnd=random.Random(int(t*FPS))
    for _ in range(int(amt/3)):
        y=rnd.randint(0,PH-40); h=rnd.randint(8,40); dx=rnd.randint(-int(amt*3),int(amt*3))
        band=p.crop((0,y,PW,y+h)); p.paste(ImageChops.offset(band,dx,0),(0,y))
    return p
SCAN=Image.new("RGBA",(PW,PH),(0,0,0,0)); sd=ImageDraw.Draw(SCAN)
for y in range(0,PH,4): sd.line([(0,y),(PW,y)],fill=(0,0,0,55))
def panel(t,i):
    base=6+18*max(0,1-(t%2.3)/0.25)  # Glitch-Spitzen alle ~2,3 s
    if i<=2:
        k=t/8.4; return glitch(crop("gl",0.78-0.12*k,0.5,0.45),t,base+ (14 if i==0 and t<0.8 else 0))
    if i==3:
        k=(t-S[3])/4.4; p=crop("str",0.7-0.1*k,0.3,0.2+0.5*k)   # "Fallen": Ausschnitt wandert nach unten
        return glitch(p,t,base)
    if i==4:
        k=(t-S[4])/3; return glitch(crop("sky",0.75,0.5,0.6,rot=-7*ease(k*1.5)),t,base)
    if i==5:
        k=(t-S[5])/3.6; return glitch(crop("str",0.6+0.15*k,0.8,0.7-0.4*k),t,base)
    if i==6:
        return glitch(crop("gl",0.55,0.2+0.1*math.sin(t),0.5),t,base+10)
    k=(t-S[7])/6; return glitch(crop("cou",0.8-0.1*k,0.5,0.4),t,base*0.6)
MASK=Image.new("L",(PW,PH),0); ImageDraw.Draw(MASK).rounded_rectangle([0,0,PW-1,PH-1],26,fill=255)
def header(d,t):
    d.rectangle([0,0,W,300],fill=BG)
    on=int(t*2)%2==0
    d.ellipse([60,215,92,247],fill=MG if on else (90,20,50))
    d.text((112,231),"BUG-TRACKER",font=F(FB,46),fill=WH,anchor="lm")
    d.text((W-60,231),"GTA VI · LIVE",font=F(FMO,38),fill=YE,anchor="rm")
    d.line([(50,290),(W-50,290)],fill=MG,width=4)
def errwin(im,x,y,w,h,title,body,col,sc=1.0):
    if sc<=0: return
    win=Image.new("RGBA",(w,h),(0,0,0,0)); d=ImageDraw.Draw(win)
    d.rounded_rectangle([0,0,w-1,h-1],18,fill=(245,245,250,255),outline=col,width=6)
    d.rounded_rectangle([0,0,w-1,70],18,fill=col); d.rectangle([0,40,w-1,70],fill=col)
    d.text((26,36),title,font=F(FMO,34),fill=WH,anchor="lm")
    for k,c in enumerate([YE,WH,WH]):
        cx=w-40-k*48; d.ellipse([cx-14,22,cx+14,50],fill=c if k==0 else (255,255,255,140))
    yy=110
    for line in body:
        f=fit(d,line,FB,58,w-60); d.text((w//2,yy),line,font=f,fill=BG,anchor="mm"); yy+=78
    if sc!=1.0: win=win.resize((max(1,int(w*sc)),max(1,int(h*sc))),Image.BILINEAR)
    im.paste(win,(int(x+w/2-win.width/2),int(y+h/2-win.height/2)),win)
def ticket(d,y,nr,txt1,txt2,lab,col,pv):
    if pv<=0: return
    dx=int((1-min(1,pv))*500)
    d.rounded_rectangle([60+dx,y,1020+dx,y+222],24,fill=BG2,outline=col,width=5)
    d.text((100+dx,y+48),f"BUG #{nr}",font=F(FMO,40),fill=GY,anchor="lm")
    lw=d.textlength(lab,font=F(FB,36))+40
    d.rounded_rectangle([980+dx-lw,y+22,980+dx,y+76],27,fill=col)
    d.text((980+dx-lw/2,y+49),lab,font=F(FB,36),fill=BG,anchor="mm")
    d.text((100+dx,y+118),txt1,font=fit(d,txt1,FB,62,880),fill=WH,anchor="lm")
    d.text((100+dx,y+182),txt2,font=fit(d,txt2,FM,50,880),fill=col,anchor="lm")
def stamp(im,text,col,cx,cy,ang,sc):
    if sc<=0: return
    f=F(FA,150); tmp=Image.new("RGBA",(900,280),(0,0,0,0)); d=ImageDraw.Draw(tmp)
    d.rounded_rectangle([10,10,889,269],20,outline=col,width=14)
    d.text((450,140),text,font=fit(d,text,FA,150,820),fill=col,anchor="mm")
    tmp=tmp.rotate(ang,expand=True,resample=Image.BICUBIC)
    s=max(0.05,sc); tmp=tmp.resize((int(tmp.width*s),int(tmp.height*s)),Image.BILINEAR)
    im.paste(tmp,(int(cx-tmp.width/2),int(cy-tmp.height/2)),tmp)
def frame(t):
    i=seg(t); im=Image.new("RGB",(W,H),BG); d=ImageDraw.Draw(im)
    header(d,t)
    p=panel(t,i).convert("RGBA"); p.alpha_composite(SCAN); im.paste(p.convert("RGB"),(PX,PY),MASK)
    d.rounded_rectangle([PX,PY,PX+PW,PY+PH],26,outline=MG if i%2==0 else CY,width=6)
    y0=1010
    if i==0:
        d.text((70,y0),"99 PUNKTE",font=F(FA,170),fill=YE,anchor="lt")
        d.text((70,y0+215),"– UND DU FÄLLST",font=fit(d,"– UND DU FÄLLST",FB,92,940),fill=WH,anchor="lt")
        s=1+0.04*math.sin(t*6); txt="DURCH DEN BODEN?!"
        f=fit(d,txt,FB,int(92*s),900); bw=d.textlength(txt,font=f)+60
        d.rounded_rectangle([60,y0+335,60+bw,y0+470],22,fill=MG)
        d.text((60+bw/2,y0+402),txt,font=f,fill=WH,anchor="mm")
        errwin(im,560,PY+380,440,230,"FEHLER 0x99",["BODEN FEHLT"],MG)
    elif i==1:
        pv=pop((t-S[1])/0.4)
        d.text((W//2,y0+60),"STATUS-UPDATE",font=F(FMO,46),fill=GY,anchor="mm")
        d.text((W//2,y0+210),"GLITCHES",font=F(FA,int(170*max(0.3,min(1.1,pv)))),fill=WH,anchor="mm")
        if t>S[1]+1.9:
            pv2=pop((t-S[1]-1.9)/0.35)
            d.text((W//2,y0+390),"= GOLD WERT?",font=F(FA,int(140*max(0.3,min(1.1,pv2)))),fill=YE,anchor="mm")
        errwin(im,90,PY+60,420,230,"HINWEIS",["PHYSIK.EXE"],CY,sc=pop((t-S[1]-0.5)/0.3))
    elif i==2:
        pv=pop((t-S[2])/0.35)
        d.text((W//2,y0+80),"QUELLE",font=F(FMO,50),fill=GY,anchor="mm")
        d.text((W//2,y0+240),"FUTURISM",font=F(FA,int(180*max(0.3,min(1.1,pv)))),fill=CY,anchor="mm")
        d.text((W//2,y0+410),"gesammelte Bugs zum Release",font=F(FM,52),fill=WH,anchor="mm")
    elif i in (3,4,5):
        tk=[(1,"Durch den Gefängnisboden","→ landet mitten im Verkehr","KRITISCH",MG,S[3]),
            (2,"Schiff hängt schief","neben einer Brücke","SCHRÄG",CY,S[4]),
            (3,"Roller rammt Streifenwagen","→ und hebt einfach ab","ABGEHOBEN",YE,S[5])]
        for k,(nr,a,b,lab,col,ts) in enumerate(tk):
            ticket(d,y0-20+k*238,nr,a,b,lab,col,ease((t-ts)/0.45))
        if i==3 and t>12.2: errwin(im,520,PY+330,460,240,"POSITION",["Y = -∞"],MG,sc=pop((t-12.2)/0.3))
    elif i==6:
        d.text((W//2,y0+120),"PHYSIK?",font=F(FA,200),fill=WH,anchor="mm")
        if t>23.5: stamp(im,"OPTIONAL",MG,W//2,y0+380,-8,pop((t-23.5)/0.3)*1.0)
        for k in range(3):
            if t>S[6]+0.25*k: errwin(im,120+k*130,PY+80+k*110,460,230,"FEHLER",["LOL.EXE"],[MG,CY,YE][k])
    elif i==7:
        d.text((W//2,y0+60),"WAS MEINST DU?",font=F(FMO,48),fill=GY,anchor="mm")
        d.text((W//2,y0+170),"BUGS…",font=F(FA,120),fill=WH,anchor="mm")
        for k,(lab,col,ts) in enumerate([("RUINIEREN ES",MG,S[7]+0.3),("MACHEN ES LEGENDÄR",YE,26.2)]):
            pv=pop((t-ts)/0.35)
            if pv<=0: continue
            y=y0+270+k*185; sc=min(1.06,pv)
            d.rounded_rectangle([90,y,990,y+150],75,fill=col)
            d.text((W//2,y+75),lab,font=fit(d,lab,FB,int(66*sc),800),fill=BG,anchor="mm")
        d.text((W//2,y0+700),"Schreib's in die Kommentare 👇".replace(" 👇",""),font=F(FM,46),fill=WH,anchor="mm")
    else:
        pv=pop((t-S[8])/0.4)
        d.text((W//2,y0+150),"FOLGE DEM KANAL",font=fit(d,"FOLGE DEM KANAL",FA,int(150*max(0.3,min(1.08,pv))),960),fill=WH,anchor="mm")
        d.text((W//2,y0+310),"FÜR MEHR INFOS!",font=fit(d,"FÜR MEHR INFOS!",FA,int(130*max(0.3,min(1.08,pv))),900),fill=MG,anchor="mm")
        d.rounded_rectangle([260,y0+420,820,y0+520],50,fill=YE)
        d.text((W//2,y0+470),"GAMING FACTS & NEWS",font=F(FB,40),fill=BG,anchor="mm")
    # KI-Badge
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); od=ImageDraw.Draw(ov)
    od.rounded_rectangle([60,140,280,192],26,fill=(20,20,28,160)); od.text((170,166),"KI-generiert",font=F(FM,32),fill=(255,255,255,220),anchor="mm")
    im=im.convert("RGBA"); im.alpha_composite(ov); return im.convert("RGB")
N=int(TOTAL*FPS)+int(0.6*FPS)
if PREV:
    ts=[0.1,2.5,5,7.5,9,11,13,16,19.5,22,23.9,25,27.5,29.5]
    sheet=Image.new("RGB",(W//4*7,H//4*2),(0,0,0))
    for k,tt in enumerate(ts): sheet.paste(frame(tt).resize((W//4,H//4)),((k%7)*W//4,(k//7)*H//4))
    sheet.save(PREV); frame(0).save(PREV.replace(".png","_f0.png")); sys.exit()
p=subprocess.Popen(["ffmpeg","-y","-v","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-c:v","libx264","-preset","veryfast","-crf","21","-pix_fmt","yuv420p",OUT],stdin=subprocess.PIPE)
for n in range(N): p.stdin.write(frame(n/FPS).tobytes())
p.stdin.close(); p.wait()
