import json, os, sys, subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W,H,FPS=1080,1920,30
FB="/usr/share/fonts/opentype/inter/Inter-Black.otf"; FM="/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf"; MONO="/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf"
G=(60,255,140); RED=(255,70,80); YEL=(255,214,10); WHITE=(255,255,255); CY=(70,210,255); GREY=(150,160,170)
AL=json.load(open("align.json")); TOTAL=AL["total"]; S=AL["start"]; D=AL["d"]; E=S[1:]+[TOTAL]
BG=["pc.png","pc.png","pc.png","glitch.png","glitch.png","pc.png","/home/claude/out/bilder5/skyline.png"]
_C={}
def bg(n,blur,dark):
    k=(n,blur,dark)
    if k not in _C:
        im=Image.open(n).convert("RGB"); r=max(W*1.12/im.width,H*1.05/im.height); im=im.resize((int(im.width*r)+1,int(im.height*r)+1),Image.LANCZOS)
        if blur: im=im.filter(ImageFilter.GaussianBlur(blur))
        _C[k]=(im,dark)
    return _C[k]
def F(fn,s): return ImageFont.truetype(fn,s)
def fit(d,t,fn,size,maxw):
    f=F(fn,size)
    while d.textlength(t,font=f)>maxw: size-=3; f=F(fn,size)
    return f
def pop(t): return 0 if t<=0 else (1 if t>=1 else 1+2.0*(t-1)**3+1.2*(t-1)**2)
def mark(d,x,y,ok,s=34):
    col=G if ok else RED; d.ellipse([x-s,y-s,x+s,y+s],fill=col)
    if ok: d.line([(x-16,y+2),(x-4,y+14),(x+18,y-14)],fill=(0,0,0),width=9)
    else: d.line([(x-13,y-13),(x+13,y+13)],fill=(0,0,0),width=9); d.line([(x+13,y-13),(x-13,y+13)],fill=(0,0,0),width=9)
def panel(d,box,title):
    x0,y0,x1,y1=box; d.rounded_rectangle(box,28,fill=(8,12,16,225),outline=G+(255,),width=4)
    d.rectangle([x0+4,y0+4,x1-4,y0+70],fill=(20,40,30,255)); d.text((x0+30,y0+38),title,font=F(MONO,36),fill=G,anchor="lm")
    for k,c in enumerate([(255,90,90),(255,200,60),(80,220,120)]): d.ellipse([x1-150+k*42,y0+24,x1-122+k*42,y0+52],fill=c)
def typed(d,xy,text,font,col,tl,start,cps=28):
    n=int(max(0,tl-start)*cps)
    if n<=0: return
    s=text[:n]; d.text(xy,s,font=font,fill=col,anchor="lm")
    if n<len(text) and int(tl*4)%2==0: d.text((xy[0]+d.textlength(s,font=font)+4,xy[1]),"_",font=font,fill=col,anchor="lm")
def stamp(t,col,rot=-10,size=96):
    f=F(FB,size)
    while f.getlength(t)>860: size-=4; f=F(FB,size)
    w=int(f.getlength(t))+80; im=Image.new("RGBA",(w,int(size*1.55)),(0,0,0,0)); dd=ImageDraw.Draw(im)
    dd.rounded_rectangle([6,6,w-6,im.height-6],24,outline=col+(255,),width=14); dd.text((w//2,im.height//2),t,font=f,fill=col+(255,),anchor="mm")
    return im.rotate(rot,expand=True,resample=Image.BICUBIC)
ST1=stamp("UNWAHRSCHEINLICH",RED,-10,110)
def paste_pop(im,sp,cx,cy,s):
    if s>0.02: sp=sp.resize((max(1,int(sp.width*s)),max(1,int(sp.height*s)))); im.alpha_composite(sp,(int(cx-sp.width/2),int(cy-sp.height/2)))
def frame(i):
    t=i/FPS; si=max(k for k in range(len(S)) if S[k]<=t+1e-6); tl=t-S[si]; z=tl/max(E[si]-S[si],0.1)
    src,dark=bg(BG[si],0 if si in (0,6) else 10,0.62 if si in (0,6) else 0.42)
    mw,mh=src.width-W,src.height-H; x=int(mw*(0.2+0.6*z) if si%2==0 else mw*(0.8-0.6*z))
    base=Image.eval(src.crop((x,mh//2,x+W,mh//2+H)),lambda v:int(v*dark)).convert("RGBA"); d=ImageDraw.Draw(base)
    mf=F(MONO,46)
    if si==0:
        d.text((W//2,330),"GTA VI AM PC?",font=F(FB,120),fill=WHITE,anchor="mm",stroke_width=8,stroke_fill=(0,0,0))
        if tl>=D[0]:
            panel(d,(110,620,970,1180),"release_19-11.cfg")
            for k,(n,ok) in enumerate([("PlayStation 5",True),("Xbox Series X|S",True),("PC",False)]):
                if tl>=D[0]+0.3+k*0.5: mark(d,200,780+k*140,ok); d.text((270,780+k*140),n,font=F(FM,62),fill=WHITE,anchor="lm")
    elif si==1:
        panel(d,(70,420,1010,1250),"terminal ~ pc-status")
        typed(d,(110,560),"> rockstar --pc-version",mf,GREY,tl,0.1)
        typed(d,(110,650),"STATUS: NICHT ANGEKÜNDIGT",F(MONO,52),RED,tl,0.9)
        typed(d,(110,800),"> gamesbeat --report",mf,GREY,tl,D[1])
        typed(d,(110,890),"PC-Release: Q1 2027 ?",F(MONO,52),YEL,tl,D[1]+0.7)
        typed(d,(110,1040),"BESTÄTIGT: NEIN",F(MONO,56),RED,tl,D[2])
    elif si==2:
        d.text((W//2,360),"PC-PORT DAUER",font=F(FB,100),fill=WHITE,anchor="mm",stroke_width=7,stroke_fill=(0,0,0))
        rows=[("GTA V",19,"19 Monate",CY,0.2),("Red Dead 2",12,"12 Monate",CY,D[3]),("GTA VI",None,"???",YEL,D[4])]
        for k,(n,m,lab,c,dl) in enumerate(rows):
            if tl<dl: continue
            y=640+k*280; d.text((100,y),n,font=F(FM,58),fill=WHITE,anchor="lm")
            p=min(1,(tl-dl)/0.8); full=(m or 3)/19*600; d.rounded_rectangle([100,y+50,100+max(10,int(full*p)),y+130],20,fill=c)
            d.text((100+int(full*p)+24,y+90),lab,font=F(FB,54),fill=c if not m else WHITE,anchor="lm")
    elif si==3:
        panel(d,(70,420,1010,1300),"KytyPS5 · PS5-Emulator")
        typed(d,(110,560),"> load GTA_V_PS5",mf,GREY,tl,0.2)
        typed(d,(110,650),"Status: läuft teilweise",F(MONO,50),YEL,tl,1.0)
        if tl>=D[5]:
            d.text((110,800),"FPS",font=mf,fill=GREY,anchor="lm"); p=min(1,(tl-D[5])/1.0)
            d.rounded_rectangle([110,850,970,930],18,outline=G,width=4); d.rounded_rectangle([118,858,118+int(844*p),922],14,fill=G)
            d.text((W//2,1030),f"bis {int(60*p)} FPS",font=F(FB,100),fill=G,anchor="mm")
            d.text((W//2,1180),"(High-End-PC)",font=F(FM,48),fill=GREY,anchor="mm")
    elif si==4:
        d.text((W//2,330),"ABER:",font=F(FB,120),fill=WHITE,anchor="mm",stroke_width=8,stroke_fill=(0,0,0))
        for k,n in enumerate(["Abstürze","Grafikfehler","Nicht durchspielbar"]):
            if tl>=D[6+k]: 
                d.rounded_rectangle([140,520+k*150,940,640+k*150],28,fill=(10,10,14,220)); mark(d,210,580+k*150,False); d.text((280,580+k*150),n,font=F(FM,60),fill=WHITE,anchor="lm")
        if tl>=D[9]: d.text((W//2,1080),"GTA VI zum Release im Emulator?",font=fit(d,"GTA VI zum Release im Emulator?",FB,70,W-100),fill=WHITE,anchor="mm",stroke_width=6,stroke_fill=(0,0,0))
        paste_pop(base,ST1,W//2,1320,pop((tl-D[10])/0.2))
    elif si==5:
        d.text((W//2,560),"HEISST FÜR DICH:",font=F(FB,90),fill=WHITE,anchor="mm",stroke_width=7,stroke_fill=(0,0,0))
        if tl>=0.6: d.text((W//2,820),"KONSOLE",font=F(FB,170),fill=CY,anchor="mm",stroke_width=8,stroke_fill=(0,0,0))
        if tl>=1.2: d.text((W//2,990),"oder",font=F(FM,80),fill=WHITE,anchor="mm",stroke_width=6,stroke_fill=(0,0,0))
        if tl>=1.5: d.text((W//2,1160),"GEDULD",font=F(FB,170),fill=YEL,anchor="mm",stroke_width=8,stroke_fill=(0,0,0))
    else:
        for tx,y,c,s,dl in [("FOLGE DEM KANAL",820,WHITE,110,0),("FÜR MEHR INFOS!",980,G,120,0.3)]:
            if tl>=dl: d.text((W//2,y),tx,font=fit(d,tx,FB,s,W-80),fill=c,anchor="mm",stroke_width=7,stroke_fill=(0,0,0))
    a=np.asarray(base.convert("RGB")).astype(np.float32); a[::4]*=0.93
    if i<5: a*=i/5
    return a.astype(np.uint8)
if len(sys.argv)>1:
    n=len(S); s=Image.new("RGB",(310*n,533),(255,255,255))
    for j in range(n): s.paste(Image.fromarray(frame(int((E[j]-0.15)*FPS))).resize((300,533)),(j*310,0))
    s.save("pv.jpg"); sys.exit()
p=subprocess.Popen(["ffmpeg","-y","-v","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-c:v","libx264","-preset","veryfast","-crf","19","-pix_fmt","yuv420p","v_tmp.mp4"],stdin=subprocess.PIPE)
for i in range(int(TOTAL*FPS)): p.stdin.write(frame(i).tobytes())
p.stdin.close(); p.wait(); os.replace("v_tmp.mp4","v.mp4"); print("video ok")
