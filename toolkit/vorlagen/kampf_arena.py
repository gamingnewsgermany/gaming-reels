# Vorlage "Kampf-Arena / Fighting-Game-HUD" (Kohlschwarz/Giftgrün/Kobaltblau/Gold): zwei Lebensbalken oben
# (Team A vs Team B), Runden-Banner, Vergleichskarten, FPS-Kurve mit Einbrüchen, Treffer-Stempel, WINNER-Banner,
# Entweder-oder-Buttons. Aufruf: python3 kampf_arena.py <vo.mp3> <out_noaudio.mp4> <bilder_dir> [preview.png]
import sys, subprocess, math, os, random
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
W,H,FPS=1080,1920,30
FB="/usr/share/fonts/opentype/inter/Inter-Black.otf"; FM="/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf"
FA="/usr/share/fonts/truetype/google-fonts/ofl/anton/Anton-Regular.ttf"; FMO="/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
BG=(14,12,18); GN=(110,230,70); BL=(70,130,255); GD=(255,206,60); WH=(255,255,255); GY=(170,170,185); DK=(8,8,12); RD=(255,70,70)
VO,OUT,BD=sys.argv[1],sys.argv[2],sys.argv[3]; PREV=sys.argv[4] if len(sys.argv)>4 else None
TOTAL=float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",VO]))
# Segmente (silencedetect): Hook, Peinlich, DF, Grafik, Performance, SeriesX, Zuhause, Pro, Frage, Outro
S=[0,4.55,5.95,7.75,10.95,16.75,18.95,22.15,24.25,26.85]
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
def prep(n,col,ctr,br,tint=None,a=0.2):
    im=Image.open(os.path.join(BD,n)).convert("RGB")
    im=ImageEnhance.Brightness(ImageEnhance.Contrast(ImageEnhance.Color(im).enhance(col)).enhance(ctr)).enhance(br)
    if tint: im=Image.blend(im,Image.new("RGB",im.size,tint),a)
    return im
IM={"str":prep("strasse.png",1.1,1.15,0.62,(20,40,10),0.12),
    "str2":prep("strasse.png",0.6,1.2,0.5,(10,30,90),0.3),
    "mes":prep("messe.png",0.8,1.15,0.55,(10,30,90),0.25),
    "pok":prep("pokal.png",1.0,1.1,0.6,None)}
def cover(key,z,ox,oy):
    im=IM[key]; ch=int(im.height*z); cw=int(ch*W/H)
    x=int((im.width-cw)*ox); y=int((im.height-ch)*oy)
    return im.crop((x,y,x+cw,y+ch)).resize((W,H),Image.BILINEAR)
def stroke_text(d,xy,t,font,fill,anchor="mm",sw=7):
    d.text(xy,t,font=font,fill=fill,anchor=anchor,stroke_width=sw,stroke_fill=DK)
def hud(im,t,hpA,hpB,timer="30"):
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); od=ImageDraw.Draw(ov)
    od.rectangle([0,110,W,330],fill=(0,0,0,150))
    d=ImageDraw.Draw(im); im.alpha_composite(ov)
    d=ImageDraw.Draw(im)
    # Lebensbalken
    bw=400
    for side,(lab,col,hp) in enumerate([("XBOX SERIES X",GN,hpA),("PS5",BL,hpB)]):
        if side==0: x0,x1=50,50+bw
        else: x0,x1=W-50-bw,W-50
        d.polygon([(x0-6,170),(x1+6,170),(x1+6,224),(x0-6,224)],fill=DK)
        d.rectangle([x0,176,x1,218],fill=(60,20,24))
        L=int(bw*max(0,hp))
        if side==0: d.rectangle([x1-L,176,x1,218],fill=col) if L>0 else None
        else: d.rectangle([x0,176,x0+L,218],fill=col) if L>0 else None
        d.rectangle([x0,176,x1,182],fill=(90,40,44))
        stroke_text(d,(x0 if side==0 else x1,262),lab,F(FB,40),col,anchor="lm" if side==0 else "rm",sw=5)
    # Timer
    d.ellipse([W//2-62,136,W//2+62,260],fill=DK,outline=GD,width=6)
    d.text((W//2,198),timer,font=F(FA,72),fill=GD,anchor="mm")
    # KI-Badge
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); od=ImageDraw.Draw(ov)
    od.rounded_rectangle([50,350,272,400],25,fill=(0,0,0,140))
    od.text((161,375),"KI-generiert",font=F(FM,32),fill=(255,255,255,215),anchor="mm")
    im.alpha_composite(ov)
def banner(im,text,col,y,p,size=110):
    if p<=0: return
    d=ImageDraw.Draw(im); k=ease(p)
    w=int(W*k)
    d.polygon([(W//2-w//2+40,y-80),(W//2+w//2,y-80),(W//2+w//2-40,y+80),(W//2-w//2,y+80)],fill=col)
    if k>0.6: d.text((W//2,y),text,font=fit(d,text,FA,size,W-200),fill=DK,anchor="mm")
def stamp(im,text,col,cx,cy,ang,sc,w=820,h=230,size=150):
    if sc<=0: return
    tmp=Image.new("RGBA",(w+40,h+40),(0,0,0,0)); d=ImageDraw.Draw(tmp)
    d.rounded_rectangle([10,10,w+29,h+29],22,outline=col,width=14,fill=(0,0,0,120))
    d.text(((w+40)//2,(h+40)//2),text,font=fit(d,text,FA,size,w-60),fill=col,anchor="mm")
    tmp=tmp.rotate(ang,expand=True,resample=Image.BICUBIC)
    s=max(0.05,sc); tmp=tmp.resize((int(tmp.width*s),int(tmp.height*s)),Image.BILINEAR)
    im.alpha_composite(tmp,(int(cx-tmp.width/2),int(cy-tmp.height/2)))
def glow(im,text,font,col,cx,cy,blur=16):
    lay=Image.new("RGBA",(W,460),(0,0,0,0)); dl=ImageDraw.Draw(lay)
    dl.text((W//2,230),text,font=font,fill=col+(255,),anchor="mm",stroke_width=6,stroke_fill=DK)
    g=lay.filter(ImageFilter.GaussianBlur(blur)); im.alpha_composite(g,(int(cx-W//2),int(cy-230))); im.alpha_composite(lay,(int(cx-W//2),int(cy-230)))
def fpscard(im,x,y,lab,col,val,sub,p):
    if p<=0: return
    sc=min(1.0,p); d=ImageDraw.Draw(im)
    w,h=440,420; yy=y+int((1-ease(p))*120)
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); od=ImageDraw.Draw(ov)
    od.rounded_rectangle([x,yy,x+w,yy+h],34,fill=(10,10,16,220),outline=col+(255,),width=8); im.alpha_composite(ov)
    d=ImageDraw.Draw(im)
    d.text((x+w//2,yy+60),lab,font=fit(d,lab,FB,46,w-50),fill=col,anchor="mm")
    d.text((x+w//2,yy+200),val,font=F(FA,170),fill=WH,anchor="mm")
    d.text((x+w//2,yy+320),"FPS",font=F(FB,50),fill=GY,anchor="mm")
    d.text((x+w//2,yy+380),sub,font=F(FM,34),fill=GY,anchor="mm")
random.seed(7)
NOISE=[random.random() for _ in range(400)]
def fpsval(k,dip):
    base=30-0.4*NOISE[k%400]
    for c,wd,dep in dip:
        if abs(k-c)<wd: base-=dep*(1-abs(k-c)/wd)
    return base
DIPA=[(60,6,3.5),(150,5,2.5)]
DIPB=[(30,8,6.5),(60,9,8),(95,6,5),(130,10,7.5),(160,7,6)]
def graph(im,x,y,w,h,prog):
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); od=ImageDraw.Draw(ov)
    od.rounded_rectangle([x,y,x+w,y+h],28,fill=(8,8,14,215),outline=(255,255,255,70),width=3); im.alpha_composite(ov)
    d=ImageDraw.Draw(im)
    def Y(v): return y+40+(32-v)/(32-18)*(h-90)
    for v in (30,25,20):
        d.line([(x+90,Y(v)),(x+w-30,Y(v))],fill=(70,70,90) if v!=30 else (130,130,150),width=3)
        d.text((x+75,Y(v)),str(v),font=F(FMO,32),fill=GY,anchor="rm")
    n=int(190*prog)
    for dips,col in ((DIPB,BL),(DIPA,GN)):
        pts=[(x+90+(k/190)*(w-120),Y(fpsval(k,dips))) for k in range(max(2,n))]
        d.line(pts,fill=col,width=8,joint="curve")
    d.text((x+w-40,y+h-28),"Beispielkurve",font=F(FM,28),fill=GY,anchor="rm")
def frame(t):
    i=seg(t); im=Image.new("RGBA",(W,H),BG+(255,))
    # Hintergrund
    if i<=1: bg=cover("str",0.98-0.05*t/5.9,0.08+0.06*t/5.9,0.5)
    elif i<=3: k=(t-S[2])/5; bg=cover("str2",0.9-0.06*k,0.55,0.5)
    elif i==4:
        k=(t-S[4])/5.8
        bg=cover("str",0.85-0.08*k,0.2+0.15*k,0.5) if t<13.6 else cover("mes",0.9-0.08*k,0.3+0.3*k,0.6)
    elif i==5: k=(t-S[5])/2.2; bg=cover("mes",0.75,0.7-0.1*k,0.5)
    elif i==6: k=(t-S[6])/3.2; bg=cover("str2",0.7-0.05*k,0.05+0.1*k,0.5)
    elif i==7: k=(t-S[7])/2.1; bg=cover("pok",0.95-0.08*k,0.5,0.5)
    else: k=(t-S[8])/5; bg=cover("pok",0.85,0.2+0.6*k,0.5); bg=ImageEnhance.Brightness(bg).enhance(0.75)
    # leichter Treffer-Shake
    sh=0
    for ts in (4.55,9.6,13.7,17.6,19.6):
        if 0<=t-ts<0.25: sh=int(14*math.sin((t-ts)*90)*(1-(t-ts)/0.25))
    im.paste(bg,(sh,0))
    # Lebensbalken
    hpA=1.0; hpB=1.0
    if t>=12.0: hpB=1-0.35*ease((t-12.0)/1.0)
    if t>=14.2: hpB-=0.2*ease((t-14.2)/1.0)
    if t>=17.6: hpB-=0.15*ease((t-17.6)/0.6)
    if t>=12.6: hpA=1-0.1*ease((t-12.6)/0.8)
    timer=str(max(0,30-int(t)))
    hud(im,t,hpA,hpB,timer)
    d=ImageDraw.Draw(im); y0=760
    if i==0:
        s=1+0.015*math.sin(t*6)
        stroke_text(d,(W//2,y0),"GTA VI LÄUFT",F(FA,int(140*s)),WH)
        stroke_text(d,(W//2,y0+170),"AUF XBOX",F(FA,int(170*s)),GN)
        stroke_text(d,(W//2,y0+340),"BESSER ALS",F(FA,int(140*s)),WH)
        stroke_text(d,(W//2,y0+500),"AUF PS5?!",F(FA,int(170*s)),BL)
    elif i==1:
        stroke_text(d,(W//2,y0-20),"GTA VI",F(FA,130),WH)
        stroke_text(d,(W//2,y0+130),"XBOX > PS5?",F(FA,150),GN)
        stamp(im,"PEINLICH, SONY?!",RD,W//2,y0+430,-7,pop((t-S[1])/0.3)*0.95)
    elif i==2:
        banner(im,"DER TEST",GD,y0+40,(t-S[2])/0.35)
        stroke_text(d,(W//2,y0+260),"DIGITAL FOUNDRY",F(FA,120),WH)
        stroke_text(d,(W//2,y0+400),"vergleicht alle Konsolen",F(FB,52),GY,sw=5)
    elif i==3:
        banner(im,"RUNDE 1: GRAFIK",GD,y0-120,(t-S[3])/0.3,size=100)
        fpscard(im,70,y0+20,"XBOX SERIES X",GN,"30","Ziel-Bildrate",pop((t-S[3]-0.2)/0.4))
        fpscard(im,570,y0+20,"PS5",BL,"30","Ziel-Bildrate",pop((t-S[3]-0.5)/0.4))
        stroke_text(d,(W//2,y0+530),"Grafik fast identisch",F(FB,56),WH,sw=5)
        if t>9.6: stamp(im,"UNENTSCHIEDEN",GD,W//2,y0+250,6,pop((t-9.6)/0.3)*0.85,size=140)
    elif i==4:
        banner(im,"RUNDE 2: PERFORMANCE",GD,y0-120,(t-S[4])/0.3,size=92)
        graph(im,60,y0+0,960,520,ease((t-S[4]-0.3)/4.6))
        lab="SCHNELLE AUTOFAHRTEN" if t<13.6 else "MENSCHENMASSEN"
        stroke_text(d,(W//2,y0+590),lab,fit(d,lab,FA,96,960),WH)
        stroke_text(d,(W//2,y0+700),"PS5 öfter in den 20ern",F(FB,58),BL,sw=5)
    elif i==5:
        stroke_text(d,(W//2,y0),"SERIES X",F(FA,170),GN)
        stroke_text(d,(W//2,y0+160),"FÄNGT RUCKLER",F(FA,120),WH)
        stroke_text(d,(W//2,y0+290),"BESSER AB",F(FA,120),WH)
        stamp(im,"TREFFER XBOX",GN,W//2,y0+540,-6,pop((t-17.6)/0.3)*0.85)
    elif i==6:
        stroke_text(d,(W//2,y0),"DABEI GALT",F(FA,120),WH)
        stroke_text(d,(W//2,y0+150),"DIE PS5 ALS",F(FA,120),WH)
        pv=pop((t-19.6)/0.35)
        if pv>0: glow(im,"„ZUHAUSE“",F(FA,int(190*cl(pv))),BL,W//2,y0+360)
        stroke_text(d,(W//2,y0+560),"von GTA VI",F(FB,64),WH,sw=5)
    elif i==7:
        banner(im,"WINNER",GD,y0-100,(t-S[7])/0.3,size=130)
        pv=pop((t-S[7]-0.3)/0.35)
        stroke_text(d,(W//2,y0+130),"BESTER PLATZ:",F(FA,int(110*cl(pv))),WH)
        glow(im,"PS5 PRO",F(FA,int(200*cl(pv))),GD,W//2,y0+340)
        stroke_text(d,(W//2,y0+540),"stabilste Bildrate lt. Test",F(FB,50),WH,sw=5)
    elif i==8:
        pv=pop((t-S[8])/0.35)
        stroke_text(d,(W//2,y0-60),"XBOX-SIEG",F(FA,int(170*cl(pv))),GN)
        stroke_text(d,(W//2,y0+110),"ODER EGAL?",F(FA,int(150*cl(pv))),WH)
        for k,(lab,col,ts) in enumerate([("XBOX-SIEG!",GN,24.9),("VÖLLIG EGAL",BL,25.4)]):
            p2=pop((t-ts)/0.35)
            if p2<=0: continue
            y=y0+260+k*175; sc=min(1.06,p2)
            d.rounded_rectangle([130,y,950,y+145],72,fill=col,outline=DK,width=6)
            d.text((W//2,y+72),lab,font=F(FB,int(70*sc)),fill=DK,anchor="mm")
        stroke_text(d,(W//2,y0+660),"Schreib's in die Kommentare!",F(FB,50),WH,sw=5)
    else:
        pv=pop((t-S[9])/0.4)
        stroke_text(d,(W//2,y0+80),"FOLGE DEM KANAL",fit(d,"FOLGE DEM KANAL",FA,int(150*cl(pv)),960),WH)
        stroke_text(d,(W//2,y0+250),"FÜR MEHR INFOS!",fit(d,"FÜR MEHR INFOS!",FA,int(130*cl(pv)),900),GD)
        d.rounded_rectangle([260,y0+380,820,y0+480],50,fill=GN)
        d.text((W//2,y0+430),"GAMING FACTS & NEWS",font=F(FB,40),fill=DK,anchor="mm")
    return im.convert("RGB")
N=int(TOTAL*FPS)+int(0.6*FPS)
if PREV:
    ts=[0.0,3.0,5.0,6.8,8.5,10.2,12.0,14.5,16.2,17.9,20.5,23.0,25.0,26.0,28.0,29.0]
    sheet=Image.new("RGB",(W//4*8,H//4*2),(0,0,0))
    for k,tt in enumerate(ts): sheet.paste(frame(tt).resize((W//4,H//4)),((k%8)*W//4,(k//8)*H//4))
    sheet.save(PREV); frame(0).save(PREV.replace(".png","_f0.png")); sys.exit()
p=subprocess.Popen(["ffmpeg","-y","-v","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-c:v","libx264","-preset","veryfast","-crf","21","-pix_fmt","yuv420p",OUT],stdin=subprocess.PIPE)
for n in range(N): p.stdin.write(frame(n/FPS).tobytes())
p.stdin.close(); p.wait()
