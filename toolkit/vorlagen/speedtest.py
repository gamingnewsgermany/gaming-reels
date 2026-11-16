import json, os, sys, subprocess, math, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W,H,FPS=1080,1920,30
FB="/usr/share/fonts/opentype/inter/Inter-Black.otf"; FM="/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf"
CY=(0,220,255); MG=(255,60,170); YEL=(255,214,10); RED=(255,70,70); WHITE=(255,255,255); GREEN=(60,230,130); BLUE=(70,120,255)
AL=json.load(open("align.json")); TOTAL=AL["total"]; S=AL["start"]; D=AL["d"]; E=S[1:]+[TOTAL]
BG=["router.png","dc.png","dc.png","router.png","router.png","dc.png","router.png","/home/claude/out/bilder5/skyline.png"]
_C={}
def bgimg(n,blur):
    k=(n,blur)
    if k not in _C:
        im=Image.open(n).convert("RGB"); r=max(W*1.12/im.width,H*1.05/im.height); im=im.resize((int(im.width*r)+1,int(im.height*r)+1),Image.LANCZOS)
        if blur: im=im.filter(ImageFilter.GaussianBlur(blur))
        _C[k]=im
    return _C[k]
def F(fn,s): return ImageFont.truetype(fn,s)
def fit(d,t,fn,size,maxw):
    f=F(fn,size)
    while d.textlength(t,font=f)>maxw: size-=3; f=F(fn,size)
    return f
def T(d,xy,t,fn,size,col,stroke=7,maxw=W-90):
    d.text(xy,t,font=fit(d,t,fn,size,maxw),fill=col,anchor="mm",stroke_width=stroke,stroke_fill=(0,0,0))
def pop(t): return 0 if t<=0 else (1 if t>=1 else 1+2.0*(t-1)**3+1.2*(t-1)**2)
def gauge(d,cx,cy,r,v,col):
    d.arc([cx-r,cy-r,cx+r,cy+r],180,360,fill=(40,50,70),width=40)
    d.arc([cx-r,cy-r,cx+r,cy+r],180,180+int(180*v),fill=col,width=40)
    a=math.pi*(1+v); d.line([(cx,cy),(cx+math.cos(a)*(r-50),cy+math.sin(a)*(r-50))],fill=WHITE,width=14); d.ellipse([cx-26,cy-26,cx+26,cy+26],fill=WHITE)
def bar(d,y,label,val,p,col,txt):
    d.text((90,y),label,font=F(FM,56),fill=WHITE,anchor="lm",stroke_width=4,stroke_fill=(0,0,0))
    d.rounded_rectangle([90,y+50,990,y+140],26,fill=(20,25,40))
    if p>0: d.rounded_rectangle([90,y+50,90+max(50,int(900*p)),y+140],26,fill=col)
    d.text((970,y+95),txt,font=F(FB,50),fill=WHITE,anchor="rm",stroke_width=4,stroke_fill=(0,0,0))
def stamp(t,col,rot=-10,size=110):
    f=F(FB,size)
    while f.getlength(t)>860: size-=4; f=F(FB,size)
    w=int(f.getlength(t))+80; im=Image.new("RGBA",(w,int(size*1.55)),(0,0,0,0)); dd=ImageDraw.Draw(im)
    dd.rounded_rectangle([6,6,w-6,im.height-6],24,outline=col+(255,),width=14); dd.text((w//2,im.height//2),t,font=f,fill=col+(255,),anchor="mm")
    return im.rotate(rot,expand=True,resample=Image.BICUBIC)
STD=stamp("KEINE DISC",RED); STB=stamp("UND BETEN",YEL,8)
def pp(im,sp,cx,cy,s):
    if s>0.02: sp=sp.resize((max(1,int(sp.width*s)),max(1,int(sp.height*s)))); im.alpha_composite(sp,(int(cx-sp.width/2),int(cy-sp.height/2)))
def bubble(d,x,y,t,col):
    f=F(FB,54); w=int(d.textlength(t,font=f))+70
    d.rounded_rectangle([x,y,x+w,y+100],40,fill=(255,255,255)); d.polygon([(x+40,y+95),(x+80,y+95),(x+30,y+140)],fill=(255,255,255)); d.text((x+35,y+50),t,font=f,fill=col,anchor="lm")
def frame(i):
    t=i/FPS; si=max(k for k in range(len(S)) if S[k]<=t+1e-6); tl=t-S[si]; z=tl/max(E[si]-S[si],0.1)
    src=bgimg(BG[si],0 if si in (0,7) else 12); dark=0.6 if si in (0,7) else 0.4
    mw,mh=src.width-W,src.height-H; x=int(mw*(0.2+0.6*z) if si%2==0 else mw*(0.8-0.6*z))
    base=Image.eval(src.crop((x,mh//2,x+W,mh//2+H)),lambda v:int(v*dark)).convert("RGBA"); d=ImageDraw.Draw(base)
    if si==0:
        T(d,(W//2,330),"GTA VI",FB,150,YEL); T(d,(W//2,480),"vs. DEUTSCHES INTERNET",FB,90,WHITE)
        v=0.85+0.12*math.sin(tl*25) if tl>D[0] else min(0.85,tl/D[0]*0.85); gauge(d,W//2,1250,330,max(0,min(1,v)),RED if v>0.8 else CY)
        if tl>D[0]: T(d,(W//2,1380),"ÜBERLASTET",FB,90,RED)
    elif si==1:
        T(d,(W//2,330),"DE-CIX FRANKFURT",FB,96,CY); T(d,(W//2,450),"neuer Rekord beim Preload",FM,60,WHITE,5)
        p=min(1,max(0,(tl-D[1])/1.8)); T(d,(W//2,820),f"{22.30*p:0.2f}".replace(".",",")+" Tbit/s",FB,150,YEL)
        if tl>D[1]+1.9: T(d,(W//2,1020),"+19 % über altem Rekord",FB,70,GREEN)
    elif si==2:
        T(d,(W//2,330),"VODAFONE",FB,120,RED)
        bar(d,600,"Vortag",1,min(1,tl/0.6)*0.62,(110,120,140),"100 %")
        if tl>D[2]: bar(d,860,"Preload-Tag",1,min(1,(tl-D[2])/0.8),MG,"160 %")
        if tl>D[2]+0.9: T(d,(W//2,1230),"+60 % · > 4 Tbit/s",FB,110,YEL)
    elif si==3:
        p=min(1,tl/1.0); T(d,(W//2,640),f"{int(212*p)} GB",FB,230,YEL); T(d,(W//2,850),"Download-Größe",FM,64,WHITE,5)
        if tl>D[3]: T(d,(W//2,1150),"Box-Version = nur Download-Code",FB,64,WHITE)
        pp(base,STD,W//2,1390,pop((tl-D[3]-0.4)/0.2))
    elif si==4:
        T(d,(W//2,330),"TELEKOM RECHNET VOR",FB,90,MG)
        bar(d,560,"10 Mbit/s",1,min(0.03,tl*0.01)+0.02,RED,"47+ Std.")
        bar(d,790,"50 Mbit/s",1,min(0.12,tl*0.03),YEL,"9 Std. 25")
        bar(d,1020,"1000 Mbit/s",1,min(1,tl/1.2),GREEN,"~28 Min.")
        if tl>D[4]:
            bubble(d,110,1280,"47 STUNDEN?!",RED)
            if tl>D[4]+0.4: bubble(d,420,1440,"Danke Telekom…",(30,30,40))
    elif si==5:
        T(d,(W//2,330),"IM SCHNITT",FB,110,WHITE); T(d,(W//2,450),"(212 GB, Medianleitung)",FM,52,(200,200,210),4)
        bar(d,650,"Deutschland",1,min(0.35,max(0,tl-1.6)*0.08),RED,"~4,5 Std.")
        if tl>D[5]-0.2: bar(d,900,"Frankreich",1,min(1,(tl-D[5]+0.2)/0.9),BLUE,"~1,5 Std.")
        if tl>D[5]+1.3: T(d,(W//2,1250),"AUA.",FB,170,YEL)
    elif si==6:
        T(d,(W//2,700),"PRELOAD",FB,170,CY); T(d,(W//2,880),"STARTEN",FB,170,WHITE)
        pp(base,STB,W//2,1120,pop((tl-D[6])/0.2))
    else:
        for tx,y,c,s,dl in [("FOLGE DEM KANAL",820,WHITE,110,0),("FÜR MEHR INFOS!",980,CY,120,0.3)]:
            if tl>=dl: T(d,(W//2,y),tx,FB,s,c)
    a=np.asarray(base.convert("RGB")).astype(np.float32)
    if i<5: a*=i/5
    return a.astype(np.uint8)
if len(sys.argv)>1:
    n=len(S); s=Image.new("RGB",(310*n,533),(255,255,255))
    for j in range(n): s.paste(Image.fromarray(frame(int((E[j]-0.15)*FPS))).resize((300,533)),(j*310,0))
    s.save("pv.jpg"); sys.exit()
p=subprocess.Popen(["ffmpeg","-y","-v","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-c:v","libx264","-preset","veryfast","-crf","19","-pix_fmt","yuv420p","v_tmp.mp4"],stdin=subprocess.PIPE)
for i in range(int(TOTAL*FPS)): p.stdin.write(frame(i).tobytes())
p.stdin.close(); p.wait(); os.replace("v_tmp.mp4","v.mp4"); print("video ok")
