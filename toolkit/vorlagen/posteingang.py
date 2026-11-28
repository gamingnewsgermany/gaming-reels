# Vorlage "Posteingang / Plattform-Checkliste" (Mitternachtsblau/Siegelrot/Papier/Mint/Gold):
# Mail-App-Kopfzeile, Bildpanel, Mail-Karte, Kalenderblatt, Plattform-Checkliste mit Haken/Kreuz,
# Zitat-Karte, Balkendiagramm, Stempel, JA/NEIN-Buttons.
# Aufruf: python3 posteingang.py <vo.mp3> <out_noaudio.mp4> <bilder_dir> [preview.png]
import sys, subprocess, math, os
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
W,H,FPS=1080,1920,30
FB="/usr/share/fonts/opentype/inter/Inter-Black.otf"; FM="/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf"
FA="/usr/share/fonts/truetype/google-fonts/ofl/anton/Anton-Regular.ttf"; FMO="/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
BG=(12,20,38); PAN=(26,38,66); RD=(232,57,70); PA=(246,240,228); MI=(80,220,130); GO=(255,196,70); WH=(255,255,255); GY=(150,165,195)
VO,OUT,BD=sys.argv[1],sys.argv[2],sys.argv[3]; PREV=sys.argv[4] if len(sys.argv)>4 else None
TOTAL=float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",VO]))
S=[0,1.75,4.45,9.85,12.3,13.25,14.25,19.4,24.6,27.3]
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
IM={"co":prep("controller.png",0.8,1.2,(30,60,140),0.28),"sr":prep("spieleregal.png",1.0,1.1,RD,0.18),
    "cg":prep("couch_gamer.png",0.6,1.15,(20,30,70),0.3)}
def crop(key,z,ox,oy):
    im=IM[key]; cw=int(im.width*z); ch=int(cw*PH/PW)
    if ch>im.height: ch=im.height; cw=int(ch*PW/PH)
    x=int((im.width-cw)*ox); y=int((im.height-ch)*oy)
    return im.crop((x,y,x+cw,y+ch)).resize((PW,PH),Image.BILINEAR)
def panel(t,i):
    if i in (0,1): k=t/4.45; return crop("co",0.6-0.1*k,0.3+0.2*k,0.45)
    if i in (2,3): k=(t-S[2])/7.85; return crop("sr",0.7-0.12*k,0.15+0.6*k,0.5)
    if i in (4,5,6): k=(t-S[4])/7.1; return crop("cg",0.62-0.1*k,0.6-0.3*k,0.4)
    if i==7: k=(t-S[7])/5.2; return crop("co",0.5-0.06*k,0.85,0.6)
    if i==8: k=(t-S[8])/2.7; return crop("sr",0.55,0.9-0.2*k,0.4)
    return crop("cg",0.75,0.5,0.4)
MASK=Image.new("L",(PW,PH),0); ImageDraw.Draw(MASK).rounded_rectangle([0,0,PW-1,PH-1],30,fill=255)
def header(d,t):
    d.rectangle([0,0,W,240],fill=PAN)
    d.text((60,140),"POSTEINGANG",font=F(FMO,34),fill=GO,anchor="lm")
    d.text((60,192),"1 neue Nachricht: Playtonic",font=F(FB,44),fill=WH,anchor="lm")
    cx,cy=W-110,168
    d.rounded_rectangle([cx-56,cy-40,cx+56,cy+40],10,fill=RD)
    d.line([(cx-56,cy-40),(cx,cy+6),(cx+56,cy-40)],fill=WH,width=7)
    d.ellipse([cx+36,cy-62,cx+72,cy-26],fill=GO); d.text((cx+54,cy-44),"1",font=F(FB,26),fill=BG,anchor="mm")
    p=min(1,t/TOTAL); d.rectangle([0,232,W,240],fill=(40,55,90)); d.rectangle([0,232,int(W*p),240],fill=GO)
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
        yy=y+k*175; sc=min(1.06,pv)
        d.rounded_rectangle([110,yy,970,yy+140],70,fill=col)
        d.text((W//2,yy+70),lab,font=fit(d,lab,FB,int(62*sc),760),fill=fg,anchor="mm")
def check(d,cx,cy,s,col):
    d.ellipse([cx-40*s,cy-40*s,cx+40*s,cy+40*s],fill=col)
    d.line([(cx-20*s,cy),(cx-5*s,cy+16*s),(cx+22*s,cy-16*s)],fill=BG,width=int(10*s)+1)
def cross(d,cx,cy,s,col):
    d.ellipse([cx-40*s,cy-40*s,cx+40*s,cy+40*s],fill=col)
    d.line([(cx-17*s,cy-17*s),(cx+17*s,cy+17*s)],fill=WH,width=int(10*s)+1)
    d.line([(cx-17*s,cy+17*s),(cx+17*s,cy-17*s)],fill=WH,width=int(10*s)+1)
def checklist(im,d,t,y0):
    rows=[("PS5",S[3]+0.1),("SWITCH 2",S[3]+0.7),("PC",S[3]+1.3)]
    d.text((70,y0-20),"DEFINITIVE EDITION · PLATTFORMEN",font=fit(d,"DEFINITIVE EDITION · PLATTFORMEN",FMO,36,940),fill=GY,anchor="lt")
    for k,(lab,ts) in enumerate(rows):
        yy=y0+40+k*150
        d.rounded_rectangle([60,yy,1020,yy+125],24,fill=PAN)
        d.text((110,yy+62),lab,font=F(FA,80),fill=WH,anchor="lm")
        pv=pop((t-ts)/0.3)
        if pv>0: check(d,940,yy+62,min(1.1,pv),MI)
    yy=y0+40+3*150
    hl=t>=S[4]
    d.rounded_rectangle([60,yy,1020,yy+125],24,fill=(60,20,30) if t>=S[5] else PAN,outline=RD if hl else (50,65,100),width=6)
    d.text((110,yy+62),"XBOX",font=F(FA,80),fill=WH if hl else GY,anchor="lm")
    if hl and t<S[5]:
        d.text((940,yy+62),"?",font=F(FA,int(100*(1+0.08*math.sin(t*10)))),fill=GO,anchor="mm")
    if t>=S[5]: cross(d,940,yy+62,min(1.1,pop((t-S[5])/0.3)),RD)
def chart(d,t,y0):
    k=ease((t-S[7]-0.9)/1.6)
    d.text((70,y0-10),"US-KONSOLEN-VERKÄUFE",font=F(FA,70),fill=WH,anchor="lt")
    d.text((70,y0+80),"Jan.–Aug. 2026 vs. Vorjahr · Stückzahl",font=fit(d,"Jan.–Aug. 2026 vs. Vorjahr · Stückzahl",FM,40,940),fill=GY,anchor="lt")
    for j,(lab,v,col) in enumerate([("XBOX",-33,RD),("PS5",-25,GO)]):
        yy=y0+170+j*190
        d.text((70,yy+50),lab,font=F(FA,70),fill=WH,anchor="lm")
        full=640; L=int(full*abs(v)/33*k)
        d.rounded_rectangle([300,yy,300+full,yy+100],20,fill=PAN)
        if L>10: d.rounded_rectangle([300,yy,300+L,yy+100],20,fill=col)
        val=int(round(v*k))
        if k<0.05: continue
        d.text((300+max(L,0)+20 if L<full-200 else 300+L-20,yy+50),f"{val} %",font=F(FA,72),fill=WH if L>=full-200 else col,anchor="lm" if L<full-200 else "rm")
    d.text((W//2,y0+590),"Quelle: Circana (via Tom's Hardware)",font=F(FM,36),fill=GY,anchor="mm")
def frame(t):
    i=seg(t); im=Image.new("RGB",(W,H),BG); d=ImageDraw.Draw(im)
    header(d,t)
    im.paste(panel(t,i),(PX,PY),MASK)
    d.rounded_rectangle([PX,PY,PX+PW,PY+PH],30,outline=GO,width=6)
    y0=930
    if i==0:
        d.text((W//2,y0+80),"XBOX LOHNT SICH",font=fit(d,"XBOX LOHNT SICH",FA,150,960),fill=WH,anchor="mm")
        boxtext(d,"NICHT MEHR?",y0+190,RD,WH,150,s=1+0.03*math.sin(t*6))
        d.text((W//2,y0+470),"Ein Studio zieht die Reißleine …",font=F(FM,50),fill=PA,anchor="mm")
    elif i==1:
        pv=ease((t-S[1])/0.35); dx=int((1-pv)*600)
        d.rounded_rectangle([60+dx,y0-10,1020+dx,y0+330],28,fill=PA)
        d.text((100+dx,y0+30),"VON: Playtonic (Studio)",font=fit(d,"VON: Playtonic (Studio)",FMO,38,860),fill=(90,90,110),anchor="lt")
        d.text((100+dx,y0+85),"AN: Xbox-Spieler",font=F(FMO,38),fill=(90,90,110),anchor="lt")
        d.line([(100+dx,y0+145),(980+dx,y0+145)],fill=(200,190,175),width=3)
        d.text((100+dx,y0+170),"Betreff:",font=F(FM,40),fill=(90,90,110),anchor="lt")
        d.text((100+dx,y0+225),"Definitive Edition – ohne Xbox",font=fit(d,"Definitive Edition – ohne Xbox",FB,64,860),fill=BG,anchor="lt")
        stamp(im,"OHNE XBOX",RD,W//2,PY+PH//2,-8,pop((t-S[1]-0.9)/0.3)*0.9)
    elif i==2:
        pv=ease((t-S[2])/0.4)
        d.rounded_rectangle([60,y0-10,1020,y0+300],28,fill=PAN,outline=GO,width=6)
        d.text((100,y0+30),"YOOKA-LAYLEE AND THE",font=fit(d,"YOOKA-LAYLEE AND THE",FMO,40,880),fill=GO,anchor="lt")
        d.text((100,y0+80),"IMPOSSIBLE LAIR",font=fit(d,"IMPOSSIBLE LAIR",FA,int(120*cl(pv)),880),fill=WH,anchor="lt")
        d.text((100,y0+235),"Definitive Edition",font=F(FM,48),fill=PA,anchor="lt")
        if t>S[2]+2.2:
            pc=pop((t-S[2]-2.2)/0.35); s=cl(pc)
            cx=300; d.rounded_rectangle([cx-170,y0+350,cx+170,y0+650],24,fill=PA)
            d.rounded_rectangle([cx-170,y0+350,cx+170,y0+430],24,fill=RD); d.rectangle([cx-170,y0+405,cx+170,y0+430],fill=RD)
            d.text((cx,y0+392),"DEZEMBER",font=F(FB,int(44*s)),fill=WH,anchor="mm")
            d.text((cx,y0+545),"15",font=F(FA,int(170*s)),fill=BG,anchor="mm")
        if t>S[2]+3.6:
            pg=pop((t-S[2]-3.6)/0.35)
            d.rounded_rectangle([540,y0+420,1000,y0+580],80,fill=MI)
            d.text((770,y0+500),"GRATIS",font=F(FA,int(100*cl(pg))),fill=BG,anchor="mm")
            d.text((770,y0+630),"Update",font=F(FM,44),fill=PA,anchor="mm")
    elif i in (3,4,5):
        checklist(im,d,t,y0)
        if i==5: stamp(im,"GEHT LEER AUS",RD,W//2,PY+PH//2,7,pop((t-S[5])/0.3)*0.9)
    elif i==6:
        pv=ease((t-S[6])/0.4)
        d.rounded_rectangle([60,y0-10,1020,y0+470],30,fill=PA)
        d.text((110,y0+10),"„",font=F(FA,200),fill=RD,anchor="lt")
        d.text((W//2+20,y0+150),"Zu teuer.",font=F(FA,int(130*cl(pv))),fill=BG,anchor="mm")
        if t>S[6]+1.4:
            d.text((W//2,y0+290),"Technisch zu aufwendig.",font=fit(d,"Technisch zu aufwendig.",FA,int(100*cl(pop((t-S[6]-1.4)/0.3))),880),fill=RD,anchor="mm")
        d.text((W//2,y0+410),"Playtonic, kleines Team (sinngemäß)",font=fit(d,"Playtonic, kleines Team (sinngemäß)",FM,42,880),fill=(80,80,100),anchor="mm")
    elif i==7:
        chart(d,t,y0)
    elif i==8:
        pv=pop((t-S[8])/0.35)
        d.text((W//2,y0+40),"IST XBOX NOCH",font=fit(d,"IST XBOX NOCH",FA,int(140*cl(pv)),960),fill=WH,anchor="mm")
        d.text((W//2,y0+180),"EINE PLATTFORM?",font=fit(d,"EINE PLATTFORM?",FA,int(130*cl(pv)),960),fill=GO,anchor="mm")
        buttons(d,t,[("JA, KLAR!",MI,BG),("NEIN, DURCH",RD,WH)],y0+290,S[8]+0.8)
        if t>26.4: d.text((W//2,y0+680),"Schreib's in die Kommentare!",font=F(FB,48),fill=PA,anchor="mm")
    else:
        pv=pop((t-S[9])/0.4)
        d.text((W//2,y0+150),"FOLGE DEM KANAL",font=fit(d,"FOLGE DEM KANAL",FA,int(150*cl(pv)),960),fill=WH,anchor="mm")
        d.text((W//2,y0+310),"FÜR MEHR INFOS!",font=fit(d,"FÜR MEHR INFOS!",FA,int(130*cl(pv)),900),fill=GO,anchor="mm")
        d.rounded_rectangle([260,y0+420,820,y0+520],50,fill=RD)
        d.text((W//2,y0+470),"GAMING FACTS & NEWS",font=F(FB,40),fill=WH,anchor="mm")
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); od=ImageDraw.Draw(ov)
    od.rounded_rectangle([PX+24,PY+24,PX+244,PY+76],26,fill=(0,0,0,130)); od.text((PX+134,PY+50),"KI-generiert",font=F(FM,32),fill=(255,255,255,215),anchor="mm")
    im=im.convert("RGBA"); im.alpha_composite(ov); return im.convert("RGB")
N=int(TOTAL*FPS)+int(0.6*FPS)
if PREV:
    ts=[0.0,1.2,2.8,4.0,6.0,8.5,11.5,12.8,13.8,16.5,18.8,20.0,23.5,25.5,27.0,29.0]
    sheet=Image.new("RGB",(W//4*8,H//4*2),(0,0,0))
    for k,tt in enumerate(ts): sheet.paste(frame(tt).resize((W//4,H//4)),((k%8)*W//4,(k//8)*H//4))
    sheet.save(PREV); frame(0).save(PREV.replace(".png","_f0.png")); sys.exit()
p=subprocess.Popen(["ffmpeg","-y","-v","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-c:v","libx264","-preset","veryfast","-crf","21","-pix_fmt","yuv420p",OUT],stdin=subprocess.PIPE)
for n in range(N): p.stdin.write(frame(n/FPS).tobytes())
p.stdin.close(); p.wait()
