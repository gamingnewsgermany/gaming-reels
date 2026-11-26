# Vorlage "Feed-Vergleich / Doppel-Handy" (Petrol-Schwarz/Amber/Eisblau/Weiß): zwei Handys nebeneinander
# ("DU" vs "DEIN KUMPEL") mit unterschiedlichen Deal-Karten, Countdown-Uhr, Stempel, sortierender Algorithmus-Feed,
# x10-Glow, Kalenderblatt, JA/NEIN-Buttons. Aufruf: python3 feed_vergleich.py <vo.mp3> <out_noaudio.mp4> <bilder_dir> [preview.png]
import sys, subprocess, math, os
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
W,H,FPS=1080,1920,30
FB="/usr/share/fonts/opentype/inter/Inter-Black.otf"; FM="/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf"
FA="/usr/share/fonts/truetype/google-fonts/ofl/anton/Anton-Regular.ttf"; FMO="/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
BG=(10,24,34); PAN=(22,44,60); AM=(255,172,40); IB=(120,212,255); WH=(255,255,255); GY=(150,178,196); DK=(6,14,20); RD=(255,84,84)
VO,OUT,BD=sys.argv[1],sys.argv[2],sys.argv[3]; PREV=sys.argv[4] if len(sys.argv)>4 else None
TOTAL=float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",VO]))
S=[0,2.95,5.5,9.94,12.4,15.0,19.4,22.3,25.6,28.2]
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
def prep(n,col,ctr,tint=None,a=0.2):
    im=Image.open(os.path.join(BD,n)).convert("RGB")
    im=ImageEnhance.Contrast(ImageEnhance.Color(im).enhance(col)).enhance(ctr)
    if tint: im=Image.blend(im,Image.new("RGB",im.size,tint),a)
    return im
IM={"pc":prep("gaming_pc.png",1.0,1.15,AM,0.22),"reg":prep("spieleregal.png",0.8,1.1,IB,0.25),
    "handy":prep("handy_news.png",0.9,1.15,(0,90,140),0.2),"rz":prep("rechenzentrum.png",0.7,1.2,(0,60,90),0.25)}
def crop(key,w,h,z,ox,oy):
    im=IM[key]; cw=int(im.width*z); ch=int(cw*h/w)
    if ch>im.height: ch=im.height; cw=int(ch*w/h)
    x=int((im.width-cw)*ox); y=int((im.height-ch)*oy)
    return im.crop((x,y,x+cw,y+ch)).resize((w,h),Image.BILINEAR)
def rmask(w,h,r):
    m=Image.new("L",(w,h),0); ImageDraw.Draw(m).rounded_rectangle([0,0,w-1,h-1],r,fill=255); return m
PX,PY,PW,PH=50,270,980,560
PMASK=rmask(PW,PH,30)
def header(d):
    d.rectangle([0,0,W,230],fill=DK); d.rectangle([0,224,W,230],fill=AM)
    # Feed-Symbol: drei Balken
    for k in range(3): d.rounded_rectangle([60,120+k*24,60+(70 if k!=1 else 48),134+k*24],7,fill=AM if k==0 else IB)
    d.text((160,165),"DEAL-FEED",font=F(FB,52),fill=WH,anchor="lm")
    d.text((W-60,165),"BLACK FRIDAY",font=F(FMO,34),fill=IB,anchor="rm")
DEALS_A=[("Rennspiel","-60 %"),("Shooter","-40 %"),("Rollenspiel","-50 %")]
DEALS_B=[("Strategie","-35 %"),("Simulator","-70 %"),("Indie-Hit","-25 %")]
def phone(im,x,y,w,h,label,col,key,deals,t,shift=0.0,order=None):
    d=ImageDraw.Draw(im)
    d.rounded_rectangle([x,y,x+w,y+h],46,fill=DK,outline=col,width=8)
    d.rounded_rectangle([x+w//2-60,y+16,x+w//2+60,y+34],9,fill=(40,60,74))
    sx,sy,sw=x+22,y+56,w-44
    img=crop(key,sw,300,0.55,0.3+0.2*math.sin(t*0.4+shift),0.5); im.paste(img,(sx,sy),rmask(sw,300,24))
    d.rounded_rectangle([sx+14,sy+14,sx+14+d.textlength(label,font=F(FB,34))+30,sy+66],24,fill=col)
    d.text((sx+29,sy+40),label,font=F(FB,34),fill=DK,anchor="lm")
    ords=order if order else [0,1,2]
    for slot,k in enumerate(ords):
        name,pc=deals[k]; cy=sy+330+slot*150
        d.rounded_rectangle([sx,cy,sx+sw,cy+130],20,fill=PAN)
        d.rounded_rectangle([sx+14,cy+35,sx+74,cy+95],12,fill=(48,78,98))
        d.text((sx+90,cy+48),name,font=fit(d,name,FB,38,sw-90-150),fill=WH,anchor="lm")
        d.text((sx+90,cy+92),"Beispiel",font=F(FM,26),fill=GY,anchor="lm")
        d.rounded_rectangle([sx+sw-140,cy+34,sx+sw-16,cy+96],14,fill=col)
        d.text((sx+sw-78,cy+65),pc,font=F(FB,34),fill=DK,anchor="mm")
def stamp(im,text,col,cx,cy,ang,sc,w=760,h=220,size=140):
    if sc<=0: return
    tmp=Image.new("RGBA",(w+40,h+40),(0,0,0,0)); d=ImageDraw.Draw(tmp)
    d.rounded_rectangle([10,10,w+29,h+29],20,outline=col,width=13)
    d.text(((w+40)//2,(h+40)//2),text,font=fit(d,text,FA,size,w-60),fill=col,anchor="mm")
    tmp=tmp.rotate(ang,expand=True,resample=Image.BICUBIC)
    s=max(0.05,sc); tmp=tmp.resize((int(tmp.width*s),int(tmp.height*s)),Image.BILINEAR)
    im.paste(tmp,(int(cx-tmp.width/2),int(cy-tmp.height/2)),tmp)
def glow(im,text,font,col,cx,cy,blur=14):
    lay=Image.new("RGBA",(W,420),(0,0,0,0)); dl=ImageDraw.Draw(lay)
    dl.text((W//2,210),text,font=font,fill=col+(255,),anchor="mm")
    g=lay.filter(ImageFilter.GaussianBlur(blur)); im.paste(g,(int(cx-W//2),int(cy-210)),g); im.paste(lay,(int(cx-W//2),int(cy-210)),lay)
def clock(d,cx,cy,r,hh,mm,col):
    d.ellipse([cx-r,cy-r,cx+r,cy+r],fill=PAN,outline=col,width=10)
    for k in range(12):
        a=k*math.pi/6; d.line([(cx+0.82*r*math.sin(a),cy-0.82*r*math.cos(a)),(cx+0.94*r*math.sin(a),cy-0.94*r*math.cos(a))],fill=GY,width=5)
    ah=(hh%12+mm/60)*math.pi/6; am=mm*math.pi/30
    d.line([(cx,cy),(cx+0.5*r*math.sin(ah),cy-0.5*r*math.cos(ah))],fill=WH,width=14)
    d.line([(cx,cy),(cx+0.78*r*math.sin(am),cy-0.78*r*math.cos(am))],fill=col,width=8)
    d.ellipse([cx-14,cy-14,cx+14,cy+14],fill=col)
def calsheet(d,x,y,w,h,mon,day,wd,col):
    d.rounded_rectangle([x,y,x+w,y+h],24,fill=WH)
    d.rounded_rectangle([x,y,x+w,y+110],24,fill=col); d.rectangle([x,y+80,x+w,y+110],fill=col)
    d.text((x+w//2,y+56),mon,font=F(FB,54),fill=DK,anchor="mm")
    d.text((x+w//2,y+110+(h-170)//2),day,font=F(FA,int(h*0.5)),fill=DK,anchor="mm")
    d.text((x+w//2,y+h-48),wd,font=F(FB,40),fill=(80,90,100),anchor="mm")
    for k in range(2): d.ellipse([x+w//3*(k+1)-14,y-14,x+w//3*(k+1)+14,y+14],fill=GY)
def panel(im,t,i):
    if i in (2,3): k=(t-S[2])/7; img=crop("pc",PW,PH,0.6-0.1*k,0.3+0.3*k,0.5)
    elif i==4: k=(t-S[4])/2.6; img=crop("reg",PW,PH,0.65-0.08*k,0.2+0.4*k,0.5)
    elif i==5: k=(t-S[5])/4.4; img=crop("handy",PW,PH,0.7-0.1*k,0.5,0.4+0.2*k)
    elif i==6: k=(t-S[6])/2.9; img=crop("rz",PW,PH,0.6-0.08*k,0.3+0.3*k,0.5)
    elif i==7: k=(t-S[7])/3.3; img=crop("reg",PW,PH,0.5,0.85-0.3*k,0.3)
    else: k=(t-S[min(i,8)])/4; img=crop("pc",PW,PH,0.75-0.1*k,0.6,0.5)
    im.paste(img,(PX,PY),PMASK)
    ImageDraw.Draw(im).rounded_rectangle([PX,PY,PX+PW,PY+PH],30,outline=AM if i not in (5,6) else IB,width=6)
def frame(t):
    i=seg(t); im=Image.new("RGB",(W,H),BG); d=ImageDraw.Draw(im)
    header(d)
    if i<=1:
        # Hook: zwei Handys mit verschiedenen Deals
        phone(im,40,520,480,820,"DU",AM,"pc",DEALS_A,t,0)
        phone(im,560,520,480,820,"DEIN KUMPEL",IB,"reg",DEALS_B,t,1.5)
        if i==0:
            s=1+0.02*math.sin(t*6)
            d.text((W//2,300),"ANDERE DEALS",font=F(FA,int(120*s)),fill=WH,anchor="mm")
            d.text((W//2,425),"ALS DEIN KUMPEL?!",font=fit(d,"ALS DEIN KUMPEL?!",FA,int(104*s),980),fill=AM,anchor="mm")
            d.rounded_rectangle([90,1380,990,1490],55,fill=AM)
            d.text((W//2,1435),"STEAM BLACK FRIDAY 2026",font=fit(d,"STEAM BLACK FRIDAY 2026",FB,52,820),fill=DK,anchor="mm")
        else:
            pv=pop((t-S[1])/0.35)
            d.text((W//2,300),"GENIAL",font=F(FA,int(130*cl(pv))),fill=AM,anchor="mm")
            d.text((W//2,430),"ODER GRUSELIG?",font=fit(d,"ODER GRUSELIG?",FA,int(110*cl(pv)),980),fill=IB,anchor="mm")
            for k,(lab,col,ts) in enumerate([("GENIAL",AM,3.3),("GRUSELIG",IB,3.8)]):
                p2=pop((t-ts)/0.3)
                if p2<=0: continue
                x=70+k*480; sc=min(1.06,p2)
                d.rounded_rectangle([x,1380,x+460,1500],60,fill=col)
                d.text((x+230,1440),lab,font=F(FB,int(58*sc)),fill=DK,anchor="mm")
    else:
        panel(im,t,i); y0=900
        if i==2:
            clock(d,250,y0+250,190,19,0,AM)
            pv=pop((t-S[2]-0.2)/0.35)
            d.text((500,y0+110),"HEUTE",font=F(FA,int(110*cl(pv))),fill=WH,anchor="lt")
            d.text((500,y0+235),"19:00",font=F(FA,int(150*cl(pv))),fill=AM,anchor="lt")
            if t>8.5:
                p2=pop((t-8.5)/0.3); sc=min(1.06,p2)
                d.rounded_rectangle([110,y0+520,970,y0+640],60,fill=IB)
                d.text((W//2,y0+580),"BIS MONTAG, 30.11.",font=F(FB,int(60*sc)),fill=DK,anchor="mm")
            d.text((W//2,y0+720),"Steam Black Friday · 26.–30.11.2026",font=F(FM,40),fill=GY,anchor="mm")
        elif i==3:
            d.text((W//2,y0+40),"OFFIZIELLER",font=F(FA,110),fill=WH,anchor="mt")
            d.text((W//2,y0+170),"VALVE-SALE?",font=F(FA,130),fill=AM,anchor="mt")
            if t>10.9: stamp(im,"KEINER",RD,W//2,y0+500,-8,pop((t-10.9)/0.3)*0.95)
            d.text((W//2,y0+720),"keine Featured-Deals von Valve",font=F(FM,42),fill=GY,anchor="mm")
        elif i==4:
            d.text((W//2,y0+20),"DIE PUBLISHER",font=F(FA,120),fill=WH,anchor="mt")
            d.text((W//2,y0+155),"ENTSCHEIDEN",font=F(FA,120),fill=IB,anchor="mt")
            for k,(lab,ts) in enumerate([("-20 %",12.9),("-50 %",13.4),("-75 %",13.9)]):
                p2=pop((t-ts)/0.3)
                if p2<=0: continue
                sc=min(1.06,p2); cx=220+k*320; cy=y0+470
                bw,bh=int(260*sc),int(130*sc)
                d.polygon([(cx-bw//2-40,cy),(cx-bw//2,cy-bh//2),(cx+bw//2,cy-bh//2),(cx+bw//2,cy+bh//2),(cx-bw//2,cy+bh//2)],fill=AM)
                d.ellipse([cx-bw//2-22,cy-10,cx-bw//2-2,cy+10],fill=BG)
                d.text((cx+10,cy),lab,font=F(FA,int(78*sc)),fill=DK,anchor="mm")
            d.text((W//2,y0+680),"…ob und wie viel billiger",font=F(FM,46),fill=GY,anchor="mm")
        elif i==5:
            d.text((W//2,y0+10),"ALGORITHMUS",font=F(FA,120),fill=IB,anchor="mt")
            d.text((W//2,y0+140),"SORTIERT NACH DEINEM GESCHMACK",font=fit(d,"SORTIERT NACH DEINEM GESCHMACK",FB,50,960),fill=WH,anchor="mt")
            # Feed-Karten, die sich umsortieren
            k=ease((t-16.5)/1.2)
            names=[("Rennspiel",AM),("Strategie",IB),("Shooter",WH)]
            start=[0,1,2]; end=[1,2,0]
            for j,(nm,col) in enumerate(names):
                yy=y0+260+(start[j]+(end[j]-start[j])*k)*140
                d.rounded_rectangle([150,yy,930,yy+120],22,fill=PAN,outline=col,width=5)
                d.text((190,yy+60),nm,font=F(FB,50),fill=WH,anchor="lm")
                mt=["97 %","88 %","41 %"][j] if t<16.5 else ["91 %","62 %","98 %"][j]
                d.text((890,yy+60),"Match "+mt,font=F(FMO,36),fill=col,anchor="rm")
            d.text((W//2,y0+720),"(Beispiel)",font=F(FM,40),fill=GY,anchor="mm")
        elif i==6:
            d.text((W//2,y0+20),"LAUT VALVE:",font=F(FA,100),fill=WH,anchor="mt")
            p2=pop((t-S[6]-0.4)/0.35)
            if p2>0: glow(im,"× 10",F(FA,int(280*cl(p2))),AM,W//2,y0+380)
            d.text((W//2,y0+620),"so viele Spiele pro Tag",font=F(FB,54),fill=WH,anchor="mm")
            d.text((W//2,y0+710),"in der Deal-Rubrik (Valve-Test)",font=F(FM,42),fill=GY,anchor="mm")
        elif i==7:
            calsheet(d,90,y0+40,400,460,"DEZEMBER","17","DONNERSTAG",IB)
            pv=pop((t-S[7]-0.3)/0.35)
            d.text((540,y0+90),"DER GROSSE",font=F(FA,int(80*cl(pv))),fill=WH,anchor="lt")
            d.text((540,y0+190),"WINTER",font=F(FA,int(120*cl(pv))),fill=IB,anchor="lt")
            d.text((540,y0+320),"SALE",font=F(FA,int(120*cl(pv))),fill=IB,anchor="lt")
            if t>23.8:
                p2=pop((t-23.8)/0.3); sc=min(1.06,p2)
                d.rounded_rectangle([110,y0+560,970,y0+670],55,fill=AM)
                d.text((W//2,y0+615),"KOMMT ERST IN 3 WOCHEN",font=fit(d,"KOMMT ERST IN 3 WOCHEN",FB,int(54*sc),820),fill=DK,anchor="mm")
            d.text((W//2,y0+740),"17.12.2026 – 4.1.2027",font=F(FM,40),fill=GY,anchor="mm")
        elif i==8:
            pv=pop((t-S[8])/0.35)
            d.text((W//2,y0+50),"ALGORITHMUS-",font=F(FA,int(130*cl(pv))),fill=WH,anchor="mm")
            d.text((W//2,y0+190),"DEALS?",font=F(FA,int(140*cl(pv))),fill=AM,anchor="mm")
            for k,(lab,col,ts) in enumerate([("JA, PASST ZU MIR",AM,26.9),("NEIN, ZEIG MIR ALLES",IB,27.4)]):
                p2=pop((t-ts)/0.35)
                if p2<=0: continue
                y=y0+300+k*180; sc=min(1.06,p2)
                d.rounded_rectangle([110,y,970,y+145],72,fill=col)
                d.text((W//2,y+72),lab,font=fit(d,lab,FB,int(62*sc),780),fill=DK,anchor="mm")
            d.text((W//2,y0+700),"Schreib's in die Kommentare!",font=F(FB,48),fill=WH,anchor="mm")
        else:
            pv=pop((t-S[9])/0.4)
            d.text((W//2,y0+150),"FOLGE DEM KANAL",font=fit(d,"FOLGE DEM KANAL",FA,int(150*cl(pv)),960),fill=WH,anchor="mm")
            d.text((W//2,y0+310),"FÜR MEHR INFOS!",font=fit(d,"FÜR MEHR INFOS!",FA,int(130*cl(pv)),900),fill=AM,anchor="mm")
            d.rounded_rectangle([260,y0+420,820,y0+520],50,fill=IB)
            d.text((W//2,y0+470),"GAMING FACTS & NEWS",font=F(FB,40),fill=DK,anchor="mm")
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); od=ImageDraw.Draw(ov)
    od.rounded_rectangle([W//2-115,1515,W//2+115,1567],26,fill=(0,0,0,140)) if i<=1 else od.rounded_rectangle([PX+24,PY+24,PX+254,PY+76],26,fill=(0,0,0,140))
    bx=(W//2,1541) if i<=1 else (PX+139,PY+50)
    od.text(bx,"KI-generiert",font=F(FM,32),fill=(255,255,255,215),anchor="mm")
    im=im.convert("RGBA"); im.alpha_composite(ov); return im.convert("RGB")
N=int(TOTAL*FPS)+int(0.6*FPS)
if PREV:
    ts=[0.0,2.0,4.2,7.0,9.2,11.5,14.0,15.5,18.0,20.5,24.5,27.6,29.5,1.0,10.5,22.8]
    sheet=Image.new("RGB",(W//4*8,H//4*2),(0,0,0))
    for k,tt in enumerate(ts): sheet.paste(frame(tt).resize((W//4,H//4)),((k%8)*W//4,(k//8)*H//4))
    sheet.save(PREV); frame(0).save(PREV.replace(".png","_f0.png")); sys.exit()
p=subprocess.Popen(["ffmpeg","-y","-v","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-c:v","libx264","-preset","veryfast","-crf","21","-pix_fmt","yuv420p",OUT],stdin=subprocess.PIPE)
for n in range(N): p.stdin.write(frame(n/FPS).tobytes())
p.stdin.close(); p.wait()
