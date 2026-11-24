# Vorlage "Ruhmeshalle/Hall of Fame" (Nachtblau/Signal-Orange/Eisblau/Weiß): Kopfzeile mit Lorbeer-Sternen,
# Bildpanel, VS-Karte, 10 Jahres-Plaketten (2 Spalten) mit Highlight auf gesprochene Namen, Kalenderblatt,
# Krone + Stempel, Entweder-oder-Buttons. Aufruf: python3 ruhmeshalle.py <vo.mp3> <out_noaudio.mp4> <bilder_dir> [preview.png]
import sys, subprocess, math, os
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
W,H,FPS=1080,1920,30
FB="/usr/share/fonts/opentype/inter/Inter-Black.otf"; FM="/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf"
FA="/usr/share/fonts/truetype/google-fonts/ofl/archivoblack/ArchivoBlack-Regular.ttf"
BG=(12,18,34); BG2=(22,32,58); OR=(255,106,19); IC=(143,211,255); WH=(255,255,255); INK=(8,12,24); RD=(240,40,60); GR=(120,135,165)
VO,OUT,BD=sys.argv[1],sys.argv[2],sys.argv[3]; PREV=sys.argv[4] if len(sys.argv)>4 else None
TOTAL=float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",VO]))
S=[0,3.34,7.1,18.82,21.43,24.98,28.71]
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
PX,PY,PW=60,300,960
def prep(n,col,ctr,tint=None,a=0.2,pw=PW):
    im=Image.open(os.path.join(BD,n)).convert("RGB")
    im=ImageEnhance.Contrast(ImageEnhance.Color(im).enhance(col)).enhance(ctr)
    if tint: im=Image.blend(im,Image.new("RGB",im.size,tint),a)
    r=pw*1.5/im.width; return im.resize((int(im.width*r),int(im.height*r)),Image.LANCZOS)
IM={"pok":prep("pokal.png",1.1,1.15,OR,0.12),"pc":prep("gaming_pc.png",0.85,1.15,IC,0.22),"arc":prep("arcade.png",0.8,1.1,BG2,0.3)}
def crop(key,z,ox,oy,pw,ph):
    im=IM[key]; cw=int(im.width*z); ch=int(cw*ph/pw)
    if ch>im.height: ch=im.height; cw=int(ch*pw/ph)
    x=int((im.width-cw)*ox); y=int((im.height-ch)*oy)
    return im.crop((x,y,x+cw,y+ch)).resize((pw,ph),Image.BILINEAR)
def panel_h(i): return 300 if i==2 else 620
def panel(t,i):
    ph=panel_h(i)
    if i==0: k=t/3.3; return crop("pok",0.62-0.06*k,0.5,0.45,PW,ph)
    if i==1: k=(t-S[1])/3.8; return crop("pc",0.7-0.1*k,0.3+0.3*k,0.5,PW,ph)
    if i==2: k=(t-S[2])/11.7; return crop("arc",0.75,0.1+0.8*k,0.5,PW,ph)
    if i==3: k=(t-S[3])/2.6; return crop("pc",0.55,0.8-0.2*k,0.4,PW,ph)
    if i==4: k=(t-S[4])/3.5; return crop("pok",0.5-0.08*k,0.5,0.35,PW,ph)
    k=(t-S[5])/5; return crop("arc",0.6,0.7-0.3*k,0.5,PW,ph)
_M={}
def mask(ph):
    if ph not in _M:
        m=Image.new("L",(PW,ph),0); ImageDraw.Draw(m).rounded_rectangle([0,0,PW-1,ph-1],30,fill=255); _M[ph]=m
    return _M[ph]
def stamp(im,text,col,cx,cy,ang,sc,w=820,h=220,size=120):
    if sc<=0: return
    tmp=Image.new("RGBA",(w+40,h+40),(0,0,0,0)); d=ImageDraw.Draw(tmp)
    d.rounded_rectangle([10,10,w+29,h+29],20,outline=col,width=13)
    d.text(((w+40)//2,(h+40)//2),text,font=fit(d,text,FA,size,w-60),fill=col,anchor="mm")
    tmp=tmp.rotate(ang,expand=True,resample=Image.BICUBIC)
    s=max(0.05,sc); tmp=tmp.resize((int(tmp.width*s),int(tmp.height*s)),Image.BILINEAR)
    im.paste(tmp,(int(cx-tmp.width/2),int(cy-tmp.height/2)),tmp)
def starpoly(cx,cy,r,rot=0):
    return [(cx+(r if j%2==0 else r*0.45)*math.cos(rot-math.pi/2+math.pi*j/5),cy+(r if j%2==0 else r*0.45)*math.sin(rot-math.pi/2+math.pi*j/5)) for j in range(10)]
def header(d,t):
    d.rectangle([0,0,W,250],fill=BG2); d.rectangle([0,250,W,262],fill=OR)
    for k,x in enumerate([70,130,190]): d.polygon(starpoly(x,80,24+3*math.sin(t*4+k)),fill=OR)
    d.text((60,135),"STEAM AWARDS",font=F(FA,66),fill=WH,anchor="lt")
    d.text((W-60,80),"HALL OF FAME",font=F(FB,40),fill=IC,anchor="rm")
    d.text((W-60,200),"2016 – 2025",font=F(FB,40),fill=GR,anchor="rm")
def crown(d,cx,cy,s):
    if s<=0: return
    pts=[(-1,0.5),(-1,-0.4),(-0.5,0.05),(0,-0.7),(0.5,0.05),(1,-0.4),(1,0.5)]
    d.polygon([(cx+x*90*s,cy+y*90*s) for x,y in pts],fill=OR,outline=INK)
    for x,y in [(-1,-0.4),(0,-0.7),(1,-0.4)]: d.ellipse([cx+x*90*s-14*s,cy+y*90*s-14*s,cx+x*90*s+14*s,cy+y*90*s+14*s],fill=IC)
GAMES=[("2016","GTA V",11.19),("2017","THE|WITCHER 3",12.28),("2018","PUBG",17.03),("2019","SEKIRO",None),
       ("2020","RED DEAD 2",13.2),("2021","RE VILLAGE",None),("2022","ELDEN RING",14.25),("2023","BALDUR'S|GATE 3",15.0),
       ("2024","BLACK MYTH:|WUKONG",None),("2025","SILKSONG",15.9)]
def frame(t):
    i=seg(t); im=Image.new("RGB",(W,H),BG); d=ImageDraw.Draw(im)
    for xx in range(0,W,72): d.line([(xx,262),(xx,H)],fill=(17,25,45),width=2)
    header(d,t)
    ph=panel_h(i); im.paste(panel(t,i),(PX,PY),mask(ph))
    d.rounded_rectangle([PX,PY,PX+PW,PY+ph],30,outline=IC,width=5)
    y0=PY+ph+50
    if i==0:
        # VS-Karte im Panel
        for k,(lab,col,tc,x) in enumerate([("PUBG",RD,WH,90),("ELDEN RING",IC,INK,600)]):
            d.rounded_rectangle([x,PY+ph-190,x+(390 if k==0 else 390),PY+ph-50],26,fill=col,outline=INK,width=5)
            d.text((x+195,PY+ph-120),lab,font=fit(d,lab,FA,72,350),fill=tc,anchor="mm")
        r=70*(1+0.06*math.sin(t*7)); d.ellipse([540-r,PY+ph-120-r,540+r,PY+ph-120+r],fill=OR,outline=INK,width=5)
        d.text((540,PY+ph-120),"VS",font=F(FA,int(r*0.9)),fill=WH,anchor="mm")
        d.text((70,y0+10),"PUBG GEGEN",font=F(FA,104),fill=WH,anchor="lt")
        d.text((70,y0+140),"ELDEN RING?",font=F(FA,104),fill=IC,anchor="lt")
        txt="ECHT JETZT, VALVE?!"; f=fit(d,txt,FA,int(86*(1+0.03*math.sin(t*6))),860); bw=d.textlength(txt,font=f)+60
        d.rounded_rectangle([60,y0+300,60+bw,y0+440],24,fill=OR); d.text((60+bw/2,y0+370),txt,font=f,fill=WH,anchor="mm")
    elif i==1:
        pv=pop((t-S[1])/0.4)
        r=150*max(0.2,min(1.05,pv)); cx,cy=260,y0+200
        d.polygon(starpoly(cx,cy,r*1.25,t*0.3),fill=OR)
        d.ellipse([cx-r*0.7,cy-r*0.7,cx+r*0.7,cy+r*0.7],fill=BG2,outline=WH,width=6)
        d.text((cx,cy-8),"10",font=F(FA,int(r*0.8)),fill=WH,anchor="mm")
        d.text((cx,cy+r*0.42),"JAHRE",font=F(FB,int(r*0.2)),fill=IC,anchor="mm")
        if t>S[1]+0.6:
            d.text((470,y0+90),"STEAM AWARDS",font=F(FA,58),fill=WH,anchor="lt")
            d.text((470,y0+165),"GEBURTSTAG",font=F(FA,58),fill=IC,anchor="lt")
        if t>S[1]+2.0:
            k=pop((t-S[1]-2.0)/0.35)
            d.rounded_rectangle([60,y0+430,1020,y0+570],70,fill=OR)
            d.text((540,y0+500),"NEU: HALL OF FAME",font=F(FA,int(78*max(0.3,min(1.05,k)))),fill=WH,anchor="mm")
    elif i==2:
        d.text((70,y0-15),"ALLE STEAM-SPIELE DES JAHRES – 1 SIEGER",font=fit(d,"ALLE STEAM-SPIELE DES JAHRES – 1 SIEGER",FB,40,940),fill=IC,anchor="lt")
        bw,bh,gap=465,150,18; yy=y0+50
        for n,(yr,name,ts) in enumerate(GAMES):
            col=n//5; row=n%5; x=60+col*(bw+30); y=yy+row*(bh+gap)
            appear=S[2]+0.25*n; pv=ease((t-appear)/0.35)
            if pv<=0: continue
            x+=int((1-pv)*(300 if col else -300))
            hi=ts is not None and t>=ts
            pubg=name=="PUBG" and t>=17.03
            fill=RD if pubg else (OR if hi else BG2); tc=WH
            sc=1.0
            if hi: sc=1+0.06*max(0,1-(t-ts)/0.3)
            d.rounded_rectangle([x,y,x+bw,y+bh],22,fill=fill,outline=IC if not hi else WH,width=4)
            d.rounded_rectangle([x+12,y+14,x+130,y+bh-14],16,fill=INK)
            d.text((x+71,y+bh/2),yr,font=F(FB,40),fill=OR if not hi else WH,anchor="mm")
            if "|" in name:
                l1,l2=name.split("|"); f=F(FA,int(min(fit(d,l1,FA,46,bw-170).size,fit(d,l2,FA,46,bw-170).size)*sc))
                d.text((x+150,y+bh/2-27),l1,font=f,fill=tc,anchor="lm"); d.text((x+150,y+bh/2+27),l2,font=f,fill=tc,anchor="lm")
            else: d.text((x+150,y+bh/2),name,font=fit(d,name,FA,int(50*sc),bw-170),fill=tc,anchor="lm")
        if t>=17.03: stamp(im,"WIRKLICH?!",RD,W//2,PY+150,-6,pop((t-17.03)/0.3)*0.95)
    elif i==3:
        pv=pop((t-S[3])/0.35)
        d.rounded_rectangle([90,y0,500,y0+400],30,fill=WH,outline=INK,width=6)
        d.rounded_rectangle([90,y0,500,y0+100],30,fill=OR); d.rectangle([90,y0+60,500,y0+100],fill=OR)
        d.text((295,y0+52),"NOVEMBER",font=F(FA,54),fill=WH,anchor="mm")
        d.text((295,y0+250),"30",font=F(FA,int(200*max(0.3,min(1.05,pv)))),fill=INK,anchor="mm")
        if t>S[3]+0.5:
            d.text((560,y0+60),"NOMINIEREN",font=F(FA,62),fill=WH,anchor="lt")
            d.text((560,y0+150),"LÄUFT",font=F(FA,62),fill=IC,anchor="lt")
            d.text((560,y0+240),"BIS 30.11.",font=F(FA,62),fill=OR,anchor="lt")
    elif i==4:
        d.text((W//2,y0+10),"MEINE STEILE THESE:",font=F(FB,54),fill=IC,anchor="mt")
        crown(d,W//2,y0+170,pop((t-S[4]-0.2)/0.4))
        if t>22.84:
            k=pop((t-22.84)/0.35)
            d.text((W//2,y0+320),"BALDUR'S GATE 3",font=fit(d,"BALDUR'S GATE 3",FA,int(104*max(0.3,min(1.05,k))),950),fill=WH,anchor="mm")
            d.text((W//2,y0+450),"SCHLÄGT SIE ALLE",font=fit(d,"SCHLÄGT SIE ALLE",FA,int(90*max(0.3,min(1.05,k))),950),fill=OR,anchor="mm")
        if t>23.6: stamp(im,"STEILE THESE",WH,W//2,PY+310,-7,pop((t-23.6)/0.3)*0.85)
    elif i==5:
        d.text((W//2,y0+30),"UND DU?",font=F(FA,70),fill=WH,anchor="mm")
        for k,(lab,col,tc,ts) in enumerate([("ELDEN RING",IC,INK,25.74),("BALDUR'S GATE 3",OR,WH,26.4)]):
            pv=pop((t-ts)/0.35)
            if pv<=0: continue
            y=y0+110+k*220; sc=min(1.06,pv)
            d.rounded_rectangle([90,y,990,y+150],75,fill=col,outline=INK,width=5)
            d.text((W//2,y+75),lab,font=fit(d,lab,FA,int(76*sc),800),fill=tc,anchor="mm")
        if t>26.1: d.text((W//2,y0+295),"ODER",font=F(FA,50),fill=WH,anchor="mm")
        if t>27.3: d.text((W//2,y0+540),"Ab in die Kommentare!",font=F(FB,54),fill=WH,anchor="mm")
    else:
        pv=pop((t-S[6])/0.4)
        d.text((W//2,y0+110),"FOLGE DEM KANAL",font=fit(d,"FOLGE DEM KANAL",FA,int(120*max(0.3,min(1.08,pv))),940),fill=WH,anchor="mm")
        d.text((W//2,y0+260),"FÜR MEHR INFOS!",font=fit(d,"FÜR MEHR INFOS!",FA,int(110*max(0.3,min(1.08,pv))),900),fill=OR,anchor="mm")
        d.rounded_rectangle([260,y0+370,820,y0+470],50,fill=IC)
        d.text((W//2,y0+420),"GAMING FACTS & NEWS",font=F(FB,40),fill=INK,anchor="mm")
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); od=ImageDraw.Draw(ov)
    od.rounded_rectangle([PX+24,PY+24,PX+244,PY+76],26,fill=(0,0,0,120)); od.text((PX+134,PY+50),"KI-generiert",font=F(FM,32),fill=(255,255,255,215),anchor="mm")
    im=im.convert("RGBA"); im.alpha_composite(ov); return im.convert("RGB")
N=int(TOTAL*FPS)+int(0.8*FPS)
if PREV:
    ts=[0.0,2,4.5,6.5,8.5,11.5,14,16,17.6,20,22,24,26.5,29.5]
    sheet=Image.new("RGB",(W//4*7,H//4*2),(0,0,0))
    for k,tt in enumerate(ts): sheet.paste(frame(tt).resize((W//4,H//4)),((k%7)*W//4,(k//7)*H//4))
    sheet.save(PREV); frame(0).save(PREV.replace(".png","_f0.png")); sys.exit()
p=subprocess.Popen(["ffmpeg","-y","-v","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-c:v","libx264","-preset","veryfast","-crf","21","-pix_fmt","yuv420p",OUT],stdin=subprocess.PIPE)
for n in range(N): p.stdin.write(frame(n/FPS).tobytes())
p.stdin.close(); p.wait()
