# Vorlage "Preis-Waage" (Tiefviolett/Neon-Lime/Pink/Weiß): Kopfzeile mit Waagen-Symbol, Bildpanel mit Alters-Sticker,
# Preisschild alt (durchgestrichen) -> neu hochzählend, Prozent-Knall, Chip-Karte, Balkenwaage mit zwei Preisschalen,
# Rabatt-0-Stempel, JA/NEIN-Buttons. Aufruf: python3 preiswaage.py <vo.mp3> <out_noaudio.mp4> <bilder_dir> [preview.png]
import sys, subprocess, math, os
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
W,H,FPS=1080,1920,30
FB="/usr/share/fonts/opentype/inter/Inter-Black.otf"; FM="/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf"
FA="/usr/share/fonts/truetype/google-fonts/ofl/anton/Anton-Regular.ttf"; FMO="/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
BG=(34,18,58); PAN=(56,32,92); LI=(190,255,60); PK=(255,62,140); WH=(255,255,255); GY=(185,170,210); DK=(20,10,34)
VO,OUT,BD=sys.argv[1],sys.argv[2],sys.argv[3]; PREV=sys.argv[4] if len(sys.argv)>4 else None
TOTAL=float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",VO]))
S=[0,4.3,12.75,16.25,19.8,22.28,26.1,29.5]
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
PX,PY,PW,PH=50,280,980,580
def prep(n,col,ctr,tint=None,a=0.2):
    im=Image.open(os.path.join(BD,n)).convert("RGB")
    im=ImageEnhance.Contrast(ImageEnhance.Color(im).enhance(col)).enhance(ctr)
    if tint: im=Image.blend(im,Image.new("RGB",im.size,tint),a)
    r=PW*1.45/im.width; return im.resize((int(im.width*r),int(im.height*r)),Image.LANCZOS)
IM={"ctl":prep("controller.png",1.05,1.15,(120,40,200),0.22),"reg":prep("spieleregal.png",0.8,1.1,PK,0.16),
    "rz":prep("rechenzentrum.png",0.6,1.2,(40,90,20),0.3),"sofa":prep("couch_gamer.png",0.8,1.1,(120,40,200),0.2)}
def crop(key,z,ox,oy):
    im=IM[key]; cw=int(im.width*z); ch=int(cw*PH/PW)
    if ch>im.height: ch=im.height; cw=int(ch*PW/PH)
    x=int((im.width-cw)*ox); y=int((im.height-ch)*oy)
    return im.crop((x,y,x+cw,y+ch)).resize((PW,PH),Image.BILINEAR)
def panel(t,i):
    if i==0: k=t/4.3; return crop("ctl",0.62-0.08*k,0.45,0.5)
    if i in (1,2): k=(t-S[1])/12.0; return crop("reg",0.7-0.12*k,0.2+0.5*k,0.5)
    if i==3: k=(t-S[3])/3.5; return crop("rz",0.7-0.1*k,0.3+0.3*k,0.5)
    if i==4: k=(t-S[4])/2.5; return crop("ctl",0.5,0.8-0.2*k,0.4)
    if i==5: k=(t-S[5])/3.8; return crop("reg",0.55,0.9-0.3*k,0.3)
    k=(t-S[6])/5; return crop("sofa",0.75-0.1*k,0.5,0.5)
MASK=Image.new("L",(PW,PH),0); ImageDraw.Draw(MASK).rounded_rectangle([0,0,PW-1,PH-1],30,fill=255)
def scale_icon(d,x,y,s,col):
    d.line([(x,y-s),(x,y+s)],fill=col,width=6); d.line([(x-s,y-s*0.6),(x+s,y-s*0.6)],fill=col,width=6)
    for sx in (x-s,x+s):
        d.line([(sx,y-s*0.6),(sx-s*0.35,y+s*0.1)],fill=col,width=3); d.line([(sx,y-s*0.6),(sx+s*0.35,y+s*0.1)],fill=col,width=3)
        d.pieslice([sx-s*0.4,y-s*0.2,sx+s*0.4,y+s*0.4],0,180,fill=col)
    d.rectangle([x-s*0.5,y+s-6,x+s*0.5,y+s],fill=col)
def header(d,t):
    d.rectangle([0,0,W,240],fill=DK); d.rectangle([0,234,W,240],fill=LI)
    scale_icon(d,100,170,34,LI)
    d.text((160,172),"PREIS-WAAGE",font=F(FB,50),fill=WH,anchor="lm")
    d.text((W-60,172),"KONSOLEN 2026",font=F(FMO,34),fill=PK,anchor="rm")
def tag(im,cx,cy,w,h,label,txt,sc=1.0,col=LI,strike=False,tc=DK):
    if sc<=0: return
    box=Image.new("RGBA",(w+60,h),(0,0,0,0)); d=ImageDraw.Draw(box)
    d.polygon([(0,h//2),(60,0),(w+59,0),(w+59,h-1),(60,h-1)],fill=col)
    d.ellipse([34,h//2-14,62,h//2+14],fill=BG)
    d.text((w//2+60,46),label,font=fit(d,label,FB,34,w-40),fill=tc,anchor="mm")
    d.text((w//2+60,h//2+28),txt,font=fit(d,txt,FA,int(h*0.5),w-50),fill=tc,anchor="mm")
    if strike: d.line([(80,h-40),(w+30,60)],fill=PK if col!=PK else WH,width=12)
    box=box.resize((max(1,int((w+60)*sc)),max(1,int(h*sc))),Image.BILINEAR)
    im.paste(box,(int(cx-box.width/2),int(cy-box.height/2)),box)
def stamp(im,text,col,cx,cy,ang,sc,w=760,h=220,size=140):
    if sc<=0: return
    tmp=Image.new("RGBA",(w+40,h+40),(0,0,0,0)); d=ImageDraw.Draw(tmp)
    d.rounded_rectangle([10,10,w+29,h+29],20,outline=col,width=13)
    d.text(((w+40)//2,(h+40)//2),text,font=fit(d,text,FA,size,w-60),fill=col,anchor="mm")
    tmp=tmp.rotate(ang,expand=True,resample=Image.BICUBIC)
    s=max(0.05,sc); tmp=tmp.resize((int(tmp.width*s),int(tmp.height*s)),Image.BILINEAR)
    im.paste(tmp,(int(cx-tmp.width/2),int(cy-tmp.height/2)),tmp)
def sticker(im,cx,cy,r,l1,l2,ang,sc):
    if sc<=0: return
    s=int(2*r); tmp=Image.new("RGBA",(s+20,s+20),(0,0,0,0)); d=ImageDraw.Draw(tmp)
    pts=[]
    for k in range(32):
        a=k*math.pi/16; rr=(r if k%2==0 else r*0.88); pts.append((s//2+10+rr*math.cos(a),s//2+10+rr*math.sin(a)))
    d.polygon(pts,fill=PK)
    d.text((s//2+10,s//2-12),l1,font=F(FA,int(r*0.62)),fill=WH,anchor="mm")
    d.text((s//2+10,s//2+int(r*0.42)),l2,font=F(FB,int(r*0.22)),fill=WH,anchor="mm")
    tmp=tmp.rotate(ang,expand=True,resample=Image.BICUBIC); tmp=tmp.resize((max(1,int(tmp.width*sc)),max(1,int(tmp.height*sc))),Image.BILINEAR)
    im.paste(tmp,(int(cx-tmp.width/2),int(cy-tmp.height/2)),tmp)
def chip(d,x,y,w,h,col):
    d.rounded_rectangle([x,y,x+w,y+h],14,fill=DK,outline=col,width=5)
    for p in range(7):
        px=x+20+p*(w-40)//6
        d.rectangle([px-5,y-22,px+5,y],fill=col); d.rectangle([px-5,y+h,px+5,y+h+22],fill=col)
    d.text((x+w//2,y+h//2),"RAM",font=F(FA,int(h*0.45)),fill=col,anchor="mm")
def balance(im,d,t,cy,ang):
    cx=W//2; L=380
    d.polygon([(cx-60,cy+330),(cx+60,cy+330),(cx+14,cy),(cx-14,cy)],fill=GY)
    d.rectangle([cx-150,cy+330,cx+150,cy+350],fill=GY)
    a=math.radians(ang); dx=L*math.cos(a); dy=L*math.sin(a)
    d.line([(cx-dx,cy-dy),(cx+dx,cy+dy)],fill=WH,width=14); d.ellipse([cx-22,cy-22,cx+22,cy+22],fill=LI)
    for sgn,lab,col,ts in ((-1,"SERIES S",LI,S[4]+0.2),(1,"SWITCH 2",PK,S[4]+1.0)):
        px,py=cx+sgn*dx,cy+sgn*dy
        d.line([(px,py),(px-120,py+120)],fill=GY,width=4); d.line([(px,py),(px+120,py+120)],fill=GY,width=4)
        d.chord([px-170,py+60,px+170,py+180],0,180,fill=PAN,outline=WH,width=4)
        pv=pop((t-ts)/0.35)
        if pv>0:
            sc=min(1.05,pv); bw,bh=int(300*sc),int(150*sc)
            d.rounded_rectangle([px-bw//2,py+120-bh,px+bw//2,py+120],18,fill=col)
            d.text((px,py+120-bh+int(40*sc)),lab,font=F(FB,max(8,int(36*sc))),fill=DK,anchor="mm")
            d.text((px,py+120-int(48*sc)),"499,99 €",font=F(FA,max(8,int(66*sc))),fill=DK,anchor="mm")
def frame(t):
    i=seg(t); im=Image.new("RGB",(W,H),BG); d=ImageDraw.Draw(im)
    header(d,t)
    im.paste(panel(t,i),(PX,PY),MASK)
    d.rounded_rectangle([PX,PY,PX+PW,PY+PH],30,outline=LI if i!=5 else PK,width=6)
    y0=920
    if i==0:
        sticker(im,PX+PW-150,PY+PH-140,125,"6","JAHRE ALT",-12+2*math.sin(t*3),1.0)
        s=1+0.025*math.sin(t*6)
        d.text((70,y0),"FAST",font=F(FA,120),fill=WH,anchor="lt")
        d.text((70,y0+125),"500 €",font=F(FA,int(260*s)),fill=LI,anchor="lt")
        txt="FÜR EINE 6 JAHRE ALTE XBOX?!"; f=fit(d,txt,FA,96,940); bw=d.textlength(txt,font=f)+50
        d.rounded_rectangle([60,y0+450,60+bw,y0+580],22,fill=PK)
        d.text((60+bw/2,y0+515),txt,font=f,fill=WH,anchor="mm")
        if t>3.2: d.text((70,y0+640),"Wer kauft das noch?",font=F(FB,int(62*cl(pop((t-3.2)/0.3)))),fill=WH,anchor="lt")
    elif i==1:
        d.text((70,y0-10),"XBOX SERIES S 512 GB · DEUTSCHLAND",font=fit(d,"XBOX SERIES S 512 GB · DEUTSCHLAND",FMO,40,940),fill=GY,anchor="lt")
        if t>4.4:
            k=ease((t-4.6)/1.6); v=349.99+150*k
            tag(im,W//2,y0+190,700,250,"JETZT",f"{v:.2f} €".replace(".",","),min(1.05,pop((t-4.4)/0.3)))
        if t>8.1:
            tag(im,280,y0+470,420,180,"VORHER","349,99 €",min(1.05,pop((t-8.1)/0.3)),col=GY,strike=t>9.6)
        if t>10.85:
            pv=pop((t-10.85)/0.3)
            lay=Image.new("RGBA",(520,260),(0,0,0,0)); dl=ImageDraw.Draw(lay)
            dl.text((260,130),"+43 %",font=F(FA,int(160*cl(pv))),fill=PK+(255,),anchor="mm")
            g=lay.filter(ImageFilter.GaussianBlur(12)); im.paste(g,(545,y0+340),g); im.paste(lay,(545,y0+340),lay)
        if t>11.6: d.text((W//2,y0+700),"seit August 2026",font=F(FM,46),fill=GY,anchor="mm")
    elif i==2:
        d.text((70,y0-10),"XBOX SERIES X 1 TB MIT LAUFWERK",font=fit(d,"XBOX SERIES X 1 TB MIT LAUFWERK",FMO,40,940),fill=GY,anchor="lt")
        tag(im,330,y0+190,460,190,"VORHER","599,99 €",min(1.05,pop((t-S[2])/0.3)),col=GY,strike=t>13.6)
        if t>14.2:
            k=ease((t-14.3)/1.0); v=599.99+200*k
            tag(im,W//2+40,y0+450,700,250,"JETZT",f"{v:.2f} €".replace(".",","),min(1.05,pop((t-14.2)/0.3)),col=PK,tc=WH)
        if t>15.3: d.text((W//2,y0+680),"+200 € Aufpreis",font=F(FB,int(60*cl(pop((t-15.3)/0.3)))),fill=LI,anchor="mm")
    elif i==3:
        d.text((70,y0-10),"BEGRÜNDUNG LAUT MICROSOFT",font=fit(d,"BEGRÜNDUNG LAUT MICROSOFT",FMO,40,940),fill=GY,anchor="lt")
        pv=pop((t-S[3]-0.1)/0.35)
        if pv>0:
            chip(d,110,y0+120,300,200,LI)
        if t>17.2:
            pv2=pop((t-17.2)/0.3)
            d.text((470,y0+150),"SPEICHER-",font=F(FA,int(96*cl(pv2))),fill=WH,anchor="lt")
            d.text((470,y0+255),"PREISE",font=F(FA,int(96*cl(pv2))),fill=WH,anchor="lt")
        if t>18.2:
            pv3=pop((t-18.2)/0.3)
            lay=Image.new("RGBA",(W,300),(0,0,0,0)); dl=ImageDraw.Draw(lay)
            dl.text((W//2,150),"× 2,5",font=F(FA,int(230*cl(pv3))),fill=LI+(255,),anchor="mm")
            g=lay.filter(ImageFilter.GaussianBlur(14)); im.paste(g,(0,y0+380),g); im.paste(lay,(0,y0+380),lay)
            d.text((W//2,y0+720),"„mehr als 2,5-mal so teuer“",font=F(FM,46),fill=GY,anchor="mm")
    elif i==4:
        ang=-8*(1-ease((t-S[4]-0.4)/0.9))*math.cos((t-S[4])*5) if t<S[4]+1.6 else 0
        balance(im,d,t,y0+260,ang)
        d.text((W//2,y0+10),"DER WITZ:",font=F(FA,110),fill=WH,anchor="mt")
        if t>21.0: stamp(im,"GLEICH TEUER",PK,W//2,PY+PH//2,-7,pop((t-21.0)/0.3)*0.95)
    elif i==5:
        d.text((W//2,y0+10),"BLACK FRIDAY",font=F(FA,140),fill=WH,anchor="mt")
        d.text((W//2,y0+190),"Offizieller PS5-Rabatt von Sony (USA):",font=fit(d,"Offizieller PS5-Rabatt von Sony (USA):",FB,48,960),fill=GY,anchor="mt")
        if t>24.6:
            pv=pop((t-24.6)/0.3)
            lay=Image.new("RGBA",(W,330),(0,0,0,0)); dl=ImageDraw.Draw(lay)
            dl.text((W//2,165),"0 $",font=F(FA,int(260*cl(pv))),fill=PK+(255,),anchor="mm")
            g=lay.filter(ImageFilter.GaussianBlur(14)); im.paste(g,(0,y0+260),g); im.paste(lay,(0,y0+260),lay)
            stamp(im,"KEINER",PK,W//2,PY+PH//2,8,pop((t-25.1)/0.3)*0.9)
        d.text((W//2,y0+720),"laut Gamerant, 25.11.2026",font=F(FM,42),fill=GY,anchor="mm")
    elif i==6:
        pv=pop((t-S[6])/0.35)
        d.text((W//2,y0+40),"SERIES S",font=F(FA,int(150*cl(pv))),fill=WH,anchor="mm")
        d.text((W//2,y0+190),"FÜR 500 €?",font=F(FA,int(150*cl(pv))),fill=LI,anchor="mm")
        for k,(lab,col,ts) in enumerate([("JA, KAUF ICH",LI,27.9),("NEIN, NIEMALS",PK,28.3)]):
            pv2=pop((t-ts)/0.35)
            if pv2<=0: continue
            y=y0+310+k*185; sc=min(1.06,pv2)
            d.rounded_rectangle([110,y,970,y+150],75,fill=col)
            d.text((W//2,y+75),lab,font=fit(d,lab,FB,int(66*sc),760),fill=DK if col==LI else WH,anchor="mm")
        if t>28.6: d.text((W//2,y0+700),"Schreib's in die Kommentare!",font=F(FB,48),fill=WH,anchor="mm")
    else:
        pv=pop((t-S[7])/0.4)
        d.text((W//2,y0+150),"FOLGE DEM KANAL",font=fit(d,"FOLGE DEM KANAL",FA,int(150*cl(pv)),960),fill=WH,anchor="mm")
        d.text((W//2,y0+310),"FÜR MEHR INFOS!",font=fit(d,"FÜR MEHR INFOS!",FA,int(130*cl(pv)),900),fill=LI,anchor="mm")
        d.rounded_rectangle([260,y0+420,820,y0+520],50,fill=PK)
        d.text((W//2,y0+470),"GAMING FACTS & NEWS",font=F(FB,40),fill=WH,anchor="mm")
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); od=ImageDraw.Draw(ov)
    od.rounded_rectangle([PX+24,PY+24,PX+244,PY+76],26,fill=(0,0,0,130)); od.text((PX+134,PY+50),"KI-generiert",font=F(FM,32),fill=(255,255,255,215),anchor="mm")
    im=im.convert("RGBA"); im.alpha_composite(ov); return im.convert("RGB")
N=int(TOTAL*FPS)+int(0.6*FPS)
if PREV:
    ts=[0.0,3.6,5.0,9.0,11.5,13.5,15.6,17.5,19.0,20.5,21.6,23.5,25.6,27.0,28.8,30.5]
    sheet=Image.new("RGB",(W//4*8,H//4*2),(0,0,0))
    for k,tt in enumerate(ts): sheet.paste(frame(tt).resize((W//4,H//4)),((k%8)*W//4,(k//8)*H//4))
    sheet.save(PREV); frame(0).save(PREV.replace(".png","_f0.png")); sys.exit()
p=subprocess.Popen(["ffmpeg","-y","-v","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-c:v","libx264","-preset","veryfast","-crf","21","-pix_fmt","yuv420p",OUT],stdin=subprocess.PIPE)
for n in range(N): p.stdin.write(frame(n/FPS).tobytes())
p.stdin.close(); p.wait()
