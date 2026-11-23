# Vorlage "Werbeprospekt/Preis-Achterbahn" (Royalblau/Signalgelb/Rot/Weiß): Prospekt-Kopfzeile mit Laufband,
# Bildpanel, Angebots-Sterne (Starburst), durchgestrichene Preise, Preisschilder alt->neu, Preis-Achterbahn-Chart
# mit Stationen, Stempel, Entweder-oder-Buttons. Aufruf: python3 prospekt.py <vo.mp3> <out_noaudio.mp4> <bilder_dir> [preview.png]
import sys, subprocess, math, os
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
W,H,FPS=1080,1920,30
FB="/usr/share/fonts/opentype/inter/Inter-Black.otf"; FM="/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf"
FA="/usr/share/fonts/truetype/google-fonts/ofl/archivoblack/ArchivoBlack-Regular.ttf"
BL=(24,52,196); BLD=(12,28,120); YE=(255,214,0); RD=(232,28,44); WH=(255,255,255); INK=(14,16,40); PALE=(214,224,255)
VO,OUT,BD=sys.argv[1],sys.argv[2],sys.argv[3]; PREV=sys.argv[4] if len(sys.argv)>4 else None
TOTAL=float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",VO]))
S=[0,3.9,6.55,12.85,19.75,22.75,26.15]
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
    while d.textlength(t,font=F(fn,size))>maxw and size>10: size-=3
    return F(fn,size)
def ease(x): x=max(0,min(1,x)); return 1-(1-x)**3
def pop(x):
    if x<=0: return 0
    if x>=1: return 1
    return 1+2.2*(x-1)**3+1.2*(x-1)**2
PX,PY,PW,PH=60,340,960,640
def prep(n,col,ctr,tint=None,a=0.2):
    im=Image.open(os.path.join(BD,n)).convert("RGB")
    im=ImageEnhance.Contrast(ImageEnhance.Color(im).enhance(col)).enhance(ctr)
    if tint: im=Image.blend(im,Image.new("RGB",im.size,tint),a)
    r=PW*1.5/im.width; return im.resize((int(im.width*r),int(im.height*r)),Image.LANCZOS)
IM={"con":prep("controller.png",1.0,1.2,BL,0.25),"geld":prep("neon_geld.png",0.9,1.1,YE,0.12),
    "reg":prep("spieleregal.png",0.8,1.1,BLD,0.3)}
def crop(key,z,ox,oy):
    im=IM[key]; cw=int(im.width*z); ch=int(cw*PH/PW)
    if ch>im.height: ch=im.height; cw=int(ch*PW/PH)
    x=int((im.width-cw)*ox); y=int((im.height-ch)*oy)
    return im.crop((x,y,x+cw,y+ch)).resize((PW,PH),Image.BILINEAR)
def panel(t,i):
    if i<=1: k=t/6.5; return crop("con",0.58-0.08*k,0.5,0.5)
    if i==2: k=(t-S[2])/6.3; return crop("geld",0.75-0.12*k,0.3+0.4*k,0.5)
    if i==3: k=(t-S[3])/6.9; return crop("reg",0.7-0.1*k,0.7-0.4*k,0.5)
    if i==4: k=(t-S[4])/3; return crop("con",0.8,0.2+0.3*k,0.35)
    k=(t-S[5])/5; return crop("geld",0.6,0.8-0.3*k,0.4)
MASK=Image.new("L",(PW,PH),0); ImageDraw.Draw(MASK).rounded_rectangle([0,0,PW-1,PH-1],30,fill=255)
def star(cx,cy,r1,r2,n=16,rot=0):
    return [(cx+(r1 if j%2==0 else r2)*math.cos(rot+math.pi*j/n),cy+(r1 if j%2==0 else r2)*math.sin(rot+math.pi*j/n)) for j in range(2*n)]
def burst(im,cx,cy,r,l1,l2,sc,col=YE,tc=RD,rot=0.0):
    if sc<=0: return
    s=int(r*2.3); tmp=Image.new("RGBA",(s,s),(0,0,0,0)); d=ImageDraw.Draw(tmp)
    d.polygon(star(s/2,s/2,r,r*0.82,18,rot),fill=col,outline=INK)
    d.text((s/2,s/2-r*0.22),l1,font=fit(d,l1,FA,int(r*0.5),r*1.4),fill=tc,anchor="mm")
    if l2: d.text((s/2,s/2+r*0.3),l2,font=fit(d,l2,FB,int(r*0.25),r*1.3),fill=INK,anchor="mm")
    sc=max(0.05,sc); tmp=tmp.resize((int(s*sc),int(s*sc)),Image.BILINEAR)
    im.paste(tmp,(int(cx-tmp.width/2),int(cy-tmp.height/2)),tmp)
def stamp(im,text,col,cx,cy,ang,sc,w=820,h=230,size=130):
    if sc<=0: return
    tmp=Image.new("RGBA",(w+40,h+40),(0,0,0,0)); d=ImageDraw.Draw(tmp)
    d.rounded_rectangle([10,10,w+29,h+29],20,outline=col,width=13)
    d.text(((w+40)//2,(h+40)//2),text,font=fit(d,text,FA,size,w-60),fill=col,anchor="mm")
    tmp=tmp.rotate(ang,expand=True,resample=Image.BICUBIC)
    s=max(0.05,sc); tmp=tmp.resize((int(tmp.width*s),int(tmp.height*s)),Image.BILINEAR)
    im.paste(tmp,(int(cx-tmp.width/2),int(cy-tmp.height/2)),tmp)
def header(im,d,t):
    d.rectangle([0,0,W,300],fill=YE)
    d.rectangle([0,300,W,312],fill=RD)
    d.text((60,150),"BLACK-FRIDAY-",font=F(FA,74),fill=BL,anchor="lm")
    d.text((60,235),"CHECK",font=F(FA,74),fill=RD,anchor="lm")
    burst(im,880,180,105,"%?","DEAL-TEST",1.0+0.04*math.sin(t*5),col=RD,tc=WH,rot=t*0.4)
def strike(d,x0,y,x1,col=RD,w=12): d.line([(x0,y+8),(x1,y-8)],fill=col,width=w)
def tag(d,x,y,w,h,label,old,new,diff,pv,t0,t):
    if pv<=0: return
    dx=int((1-pv)*600); x+=dx
    d.rounded_rectangle([x,y,x+w,y+h],26,fill=WH,outline=INK,width=5)
    d.rounded_rectangle([x,y,x+200,y+h],26,fill=BLD); d.rectangle([x+170,y,x+200,y+h],fill=BLD)
    d.text((x+100,y+h/2),label,font=fit(d,label,FA,60,170),fill=WH,anchor="mm")
    d.text((x+230,y+48),old,font=F(FB,52),fill=(120,124,150),anchor="lm")
    ow=d.textlength(old,font=F(FB,52))
    if t>t0+0.5: strike(d,x+225,y+48,x+235+ow)
    if t>t0+0.8:
        d.text((x+230,y+130),new,font=F(FA,70),fill=INK,anchor="lm")
        d.rounded_rectangle([x+w-210,y+20,x+w-20,y+90],35,fill=RD)
        d.text((x+w-115,y+55),diff,font=fit(d,diff,FB,46,170),fill=WH,anchor="mm")
def frame(t):
    i=seg(t); im=Image.new("RGB",(W,H),BL); d=ImageDraw.Draw(im)
    for yy in range(312,H,60): d.line([(0,yy),(W,yy)],fill=(30,60,206),width=2)
    header(im,d,t)
    im.paste(panel(t,i),(PX,PY),MASK)
    d.rounded_rectangle([PX,PY,PX+PW,PY+PH],30,outline=WH,width=6)
    y0=PY+PH+50
    if i==0:
        burst(im,770,PY+PH-60,170,"FAKE?","RABATT-CHECK",1.0+0.05*math.sin(t*6),rot=0.2)
        d.text((70,y0),"NINTENDOS",font=F(FA,92),fill=WH,anchor="lt")
        d.text((70,y0+115),"BLACK-FRIDAY-RABATT",font=fit(d,"BLACK-FRIDAY-RABATT",FA,92,920),fill=YE,anchor="lt")
        txt="IN WAHRHEIT FAKE?"; f=fit(d,txt,FA,int(104*(1+0.03*math.sin(t*6))),880); bw=d.textlength(txt,font=f)+60
        d.rounded_rectangle([60,y0+250,60+bw,y0+400],24,fill=RD)
        d.text((60+bw/2,y0+325),txt,font=f,fill=WH,anchor="mm")
    elif i==1:
        pv=pop((t-S[1])/0.35)
        d.rounded_rectangle([70,y0,520,y0+330],26,fill=WH,outline=INK,width=5)
        d.rectangle([70,y0,520,y0+90],fill=RD); d.rounded_rectangle([70,y0,520,y0+60],26,fill=RD)
        d.text((295,y0+48),"SEPTEMBER",font=F(FA,54),fill=WH,anchor="mm")
        d.text((295,y0+215),"2026",font=F(FA,int(130*max(0.3,min(1.05,pv)))),fill=INK,anchor="mm")
        if t>S[1]+0.7:
            k=ease((t-S[1]-0.7)/0.6)
            d.text((780,y0+90),"SWITCH 2",font=F(FA,64),fill=WH,anchor="mm")
            d.polygon([(780,y0+150-60*k),(700,y0+250-60*k),(750,y0+250-60*k),(750,y0+330-30*k),(810,y0+330-30*k),(810,y0+250-60*k),(860,y0+250-60*k)],fill=YE)
            d.text((780,y0+400),"TEURER!",font=F(FA,int(80*max(0.3,min(1.05,pop((t-S[1]-1.0)/0.3))))),fill=YE,anchor="mm")
    elif i==2:
        d.text((70,y0-10),"PREISERHÖHUNG AB 1.9.2026",font=F(FB,44),fill=PALE,anchor="lt")
        tag(d,60,y0+60,900,190,"USA","449,99 $","499,99 $","+50 $",ease((t-S[2]-0.2)/0.4),S[2]+0.2,t)
        tag(d,60,y0+290,900,190,"EU","469,99 €","499,99 €","+30 €",ease((t-S[2]-2.8)/0.4),S[2]+2.8,t)
        if t>S[2]+4.6: stamp(im,"+50 $ / +30 €",YE,W//2,PY+PH//2,-6,pop((t-S[2]-4.6)/0.3)*0.85)
    elif i==3:
        d.rounded_rectangle([60,y0,1020,y0+440],30,fill=WH,outline=INK,width=6)
        d.text((100,y0+40),"USA-ANGEBOT · 22.11.–5.12.",font=F(FB,40),fill=BL,anchor="lt")
        d.text((100,y0+100),"SWITCH 2 +",font=F(FA,70),fill=INK,anchor="lt")
        d.text((100,y0+185),"MARIO-KART-BUNDLE",font=fit(d,"MARIO-KART-BUNDLE",FA,70,600),fill=INK,anchor="lt")
        if t>S[3]+1.0:
            d.text((100,y0+320),"549,99 $",font=F(FA,84),fill=(120,124,150),anchor="lm")
            ow=d.textlength("549,99 $",font=F(FA,84))
            if t>S[3]+2.6: strike(d,95,y0+320,110+ow,w=16)
        burst(im,850,y0+330,150,"499,99 $","−50 $",pop((t-S[3]-3.4)/0.4)*(1+0.03*math.sin(t*6)),rot=0.1)
    elif i==4:
        d.text((70,y0-15),"BUNDLE-PREIS (USA)",font=F(FB,44),fill=PALE,anchor="lt")
        pts=[(190,y0+330,"LAUNCH 2025","499,99 $"),(540,y0+190,"AB SEPT. 2026","549,99 $"),(870,y0+330,"BLACK FRIDAY","499,99 $")]
        k=ease((t-S[4]-0.1)/1.6); segs=k*2
        for j in range(2):
            f=max(0,min(1,segs-j))
            if f<=0: continue
            (x0,yy0,_,_),(x1,yy1,_,_)=pts[j],pts[j+1]
            d.line([(x0,yy0),(x0+(x1-x0)*f,yy0+(yy1-yy0)*f)],fill=YE,width=16)
        for j,(x,y,l,p) in enumerate(pts):
            if segs<j-0.02: continue
            d.ellipse([x-26,y-26,x+26,y+26],fill=RD if j==1 else WH,outline=INK,width=5)
            if j==1:
                d.text((x,y-120),l,font=F(FB,40),fill=PALE,anchor="mm"); d.text((x,y-65),p,font=F(FA,54),fill=WH,anchor="mm")
            else:
                d.text((x,y+65),p,font=F(FA,54),fill=YE,anchor="mm"); d.text((x,y+120),l,font=F(FB,40),fill=PALE,anchor="mm")
        if t>S[4]+1.9: stamp(im,"ALTER PREIS!",RD,W//2,PY+PH//2,-7,pop((t-S[4]-1.9)/0.3)*0.9)
    elif i==5:
        d.text((W//2,y0+40),"DEINE MEINUNG?",font=F(FB,50),fill=PALE,anchor="mm")
        for k,(lab,col,tc,ts) in enumerate([("ECHTER DEAL",YE,BL,S[5]+0.1),("NINTENDO-TRICK",RD,WH,S[5]+0.9)]):
            pv=pop((t-ts)/0.35)
            if pv<=0: continue
            y=y0+110+k*230; sc=min(1.06,pv)
            d.rounded_rectangle([90,y,990,y+160],80,fill=col,outline=INK,width=5)
            d.text((W//2,y+80),lab,font=fit(d,lab,FA,int(76*sc),800),fill=tc,anchor="mm")
        if t>S[5]+0.6: d.text((W//2,y0+305),"ODER",font=F(FA,54),fill=WH,anchor="mm")
        if t>24.7: d.text((W//2,y0+575),"Schreib's in die Kommentare!",font=F(FB,52),fill=WH,anchor="mm")
    else:
        pv=pop((t-S[6])/0.4)
        d.text((W//2,y0+120),"FOLGE DEM KANAL",font=fit(d,"FOLGE DEM KANAL",FA,int(120*max(0.3,min(1.08,pv))),940),fill=WH,anchor="mm")
        d.text((W//2,y0+270),"FÜR MEHR INFOS!",font=fit(d,"FÜR MEHR INFOS!",FA,int(110*max(0.3,min(1.08,pv))),900),fill=YE,anchor="mm")
        d.rounded_rectangle([260,y0+380,820,y0+480],50,fill=YE)
        d.text((W//2,y0+430),"GAMING FACTS & NEWS",font=F(FB,40),fill=BL,anchor="mm")
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); od=ImageDraw.Draw(ov)
    od.rounded_rectangle([PX+24,PY+24,PX+244,PY+76],26,fill=(0,0,0,120)); od.text((PX+134,PY+50),"KI-generiert",font=F(FM,32),fill=(255,255,255,215),anchor="mm")
    im=im.convert("RGBA"); im.alpha_composite(ov); return im.convert("RGB")
N=int(TOTAL*FPS)+int(0.8*FPS)
if PREV:
    ts=[0.0,2,4.5,6,8,11,13.5,15.5,18.5,20,21.5,23.5,25.5,27.5]
    sheet=Image.new("RGB",(W//4*7,H//4*2),(0,0,0))
    for k,tt in enumerate(ts): sheet.paste(frame(tt).resize((W//4,H//4)),((k%7)*W//4,(k//7)*H//4))
    sheet.save(PREV); frame(0).save(PREV.replace(".png","_f0.png")); sys.exit()
p=subprocess.Popen(["ffmpeg","-y","-v","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-c:v","libx264","-preset","veryfast","-crf","21","-pix_fmt","yuv420p",OUT],stdin=subprocess.PIPE)
for n in range(N): p.stdin.write(frame(n/FPS).tobytes())
p.stdin.close(); p.wait()
