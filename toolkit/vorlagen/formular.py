import json, os, sys, subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W,H,FPS=1080,1920,30
FB="/usr/share/fonts/opentype/inter/Inter-Black.otf"; FM="/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf"; MONO="/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf"
SRC=["/home/claude/out/bilder5/","/mnt/user-data/uploads/GTA6-Clips/Video1/"]
def find(n):
    for s in SRC:
        if os.path.exists(s+n): return s+n
PINK=(255,90,170); CYAN=(60,220,255); WHITE=(255,255,255); RED=(230,40,50); GREEN=(40,190,100); INK=(30,30,40)
AL=json.load(open("align.json")); TOTAL=AL["total"]; starts=AL["start"]; D=AL["d"]; ends=starts[1:]+[TOTAL]
IMG=["kalender.png","buero.png","buero.png","street.png","buero.png","skyline.png"]
_C={}
def bg(n,dark,blur):
    k=(n,dark,blur)
    if k not in _C:
        im=Image.open(find(n)).convert("RGB"); r=max(W*1.1/im.width,H*1.05/im.height); im=im.resize((int(im.width*r)+1,int(im.height*r)+1),Image.LANCZOS)
        if blur: im=im.filter(ImageFilter.GaussianBlur(blur))
        _C[k]=np.asarray(im).astype(np.float32)*dark
    return _C[k]
def txt(t,font,size,col,stroke=7,maxw=W-80):
    f=ImageFont.truetype(font,size)
    while f.getlength(t)>maxw: size-=3; f=ImageFont.truetype(font,size)
    im=Image.new("RGBA",(W,int(size*1.5)),(0,0,0,0)); ImageDraw.Draw(im).text((W//2,im.height//2),t,font=f,fill=col,anchor="mm",stroke_width=stroke,stroke_fill=(0,0,0))
    return np.asarray(im).astype(np.float32)
def stamp(t,col,size=120,rot=-12):
    f=ImageFont.truetype(FB,size); w=int(f.getlength(t))+80
    im=Image.new("RGBA",(w,int(size*1.55)),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.rounded_rectangle([6,6,w-6,im.height-6],24,outline=col+(255,),width=14); d.text((w//2,im.height//2),t,font=f,fill=col+(255,),anchor="mm")
    return np.asarray(im.rotate(rot,expand=True,resample=Image.BICUBIC)).astype(np.float32)
def calendar():
    w,h=620,680; im=Image.new("RGBA",(w,h),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.rounded_rectangle([0,0,w-1,h-1],40,fill=(250,250,248,255)); d.rounded_rectangle([0,0,w-1,170],40,fill=RED+(255,)); d.rectangle([0,120,w-1,170],fill=RED+(255,))
    d.text((w//2,88),"NOVEMBER",font=ImageFont.truetype(FB,78),fill=WHITE,anchor="mm")
    d.text((w//2,410),"19",font=ImageFont.truetype(FB,330),fill=INK,anchor="mm")
    d.text((w//2,610),"DONNERSTAG",font=ImageFont.truetype(FM,60),fill=(110,110,120),anchor="mm")
    for x in (150,w-150): d.ellipse([x-22,-22,x+22,22],fill=(80,80,90,255))
    return np.asarray(im).astype(np.float32)
def stat(num,label,col):
    w,h=900,330; im=Image.new("RGBA",(w,h),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.rounded_rectangle([0,0,w-1,h-1],40,fill=(12,12,20,225),outline=col+(255,),width=8)
    d.text((40,h//2),num,font=ImageFont.truetype(FB,170),fill=col,anchor="lm")
    nx=40+ImageFont.truetype(FB,170).getlength(num)+40; lines=label.split("\n"); fs=58
    f=ImageFont.truetype(FM,fs)
    while max(f.getlength(l) for l in lines)>w-nx-30: fs-=2; f=ImageFont.truetype(FM,fs)
    for j,l in enumerate(lines): d.text((nx,h//2+(j-(len(lines)-1)/2)*70),l,font=f,fill=WHITE,anchor="lm")
    return np.asarray(im).astype(np.float32)
def sign():
    w,h=760,460; im=Image.new("RGBA",(w,h+120),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.line([(w//2,0),(150,120)],fill=(200,200,200,255),width=8); d.line([(w//2,0),(w-150,120)],fill=(200,200,200,255),width=8); d.ellipse([w//2-16,-16,w//2+16,16],fill=(200,200,200,255))
    d.rounded_rectangle([0,120,w-1,h+119],30,fill=(250,248,240,255),outline=RED+(255,),width=14)
    d.text((w//2,250),"GESCHLOSSEN",font=ImageFont.truetype(FB,90),fill=RED,anchor="mm")
    d.text((w//2,380),"Wir spielen GTA VI.",font=ImageFont.truetype(FM,58),fill=INK,anchor="mm")
    d.text((w//2,460),"Ab Freitag wieder da. Vielleicht.",font=ImageFont.truetype(FM,40),fill=(110,110,120),anchor="mm")
    return np.asarray(im).astype(np.float32)
def form(k):
    w,h=880,900; im=Image.new("RGBA",(w,h),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.rectangle([0,0,w-1,h-1],fill=(252,251,246,255)); d.rectangle([0,0,w-1,130],fill=(225,232,245,255))
    d.text((w//2,68),"URLAUBSANTRAG",font=ImageFont.truetype(FB,78),fill=INK,anchor="mm")
    fl=ImageFont.truetype(FM,42); fv=ImageFont.truetype(MONO,50)
    rows=[("Ab:","19.11.2026"),("Bis:","???"),("Grund:","Vice City"),("Rückkehr:","unklar")]
    for j,(a,b) in enumerate(rows):
        y=230+j*150; d.text((60,y),a,font=fl,fill=(110,110,120),anchor="lm"); d.line([(300,y+34),(w-60,y+34)],fill=(180,180,190),width=3)
        if j<k: d.text((310,y),b,font=fv,fill=(20,60,170),anchor="lm")
    return np.asarray(im.rotate(3,expand=True,resample=Image.BICUBIC)).astype(np.float32)
def over(fr,ov,cx,cy,a=1.0,scale=1.0):
    if a<=0.01 or scale<=0.02: return
    if abs(scale-1)>0.005:
        im=Image.fromarray(ov.astype(np.uint8),"RGBA").resize((max(1,int(ov.shape[1]*scale)),max(1,int(ov.shape[0]*scale))),Image.BILINEAR); ov=np.asarray(im).astype(np.float32)
    h,w=ov.shape[:2]; x=int(cx-w/2); y=int(cy-h/2); x0,y0=max(0,x),max(0,y); x1,y1=min(W,x+w),min(H,y+h)
    if x1<=x0 or y1<=y0: return
    o=ov[y0-y:y1-y,x0-x:x1-x]; al=o[:,:,3:4]/255*a; fr[y0:y1,x0:x1]=fr[y0:y1,x0:x1]*(1-al)+o[:,:,:3]*al
def pop(t): return 0 if t<=0 else (1 if t>=1 else 1+2.0*(t-1)**3+1.2*(t-1)**2)
FORMS=[form(k) for k in range(5)]
EL={0:[(calendar(),850,0),(txt("Halb Deutschland hat plötzlich…",FM,64,WHITE,5),300,D[0]),(stamp("OMAS GEBURTSTAG",PINK,96,-8),1420,D[1])],
    1:[(txt("UMFRAGE",FB,110,CYAN),300,0),(stat("1/3","nimmt sich\nfür GTA VI frei",CYAN),720,D[2]),(stat("12 %","nehmen gleich\neine ganze Woche",PINK),1140,D[3]),(txt("Quelle: GamePro-Community",FM,40,(220,220,220),3),1420,D[2])],
    2:[(stat("9 %","„Ich habe\ngekündigt“",RED),620,0.2),(stat("7 %","sind „leider\nkrank“",GREEN),1060,D[4]),(stamp("Rein zufällig",WHITE,80,6),1420,D[5])],
    3:[(txt("IN DEN USA:",FB,110,WHITE),300,0),(sign(),900,D[6]),(txt("…weil eh keiner gekommen wäre",FM,58,WHITE,5),1450,D[7])],
    4:[(txt("DER PERFEKTE ANTRAG",FB,96,CYAN),260,0)],
    5:[(txt("Hast du schon Urlaub",FB,88,WHITE),560,0),(txt("eingereicht?",FB,110,PINK),700,0.2),(txt("FOLGE DEM KANAL",FB,110,WHITE),1080,D[13]),(txt("FÜR MEHR INFOS!",FB,120,CYAN),1240,D[13]+0.3)]}
def frame(i):
    t=i/FPS; si=max(k for k in range(len(starts)) if starts[k]<=t+1e-6); tl=t-starts[si]; z=tl/max(ends[si]-starts[si],0.1)
    a=bg(IMG[si],0.5 if si in (1,2,4) else 0.62,14 if si in (1,2,4) else 0)
    mh,mw=a.shape[0]-H,a.shape[1]-W; x=int(mw*(0.2+0.6*z) if si%2==0 else mw*(0.8-0.6*z))
    fr=a[mh//2:mh//2+H,x:x+W].copy()
    for ov,cy,dl in EL[si]: over(fr,ov,W//2,cy,1,pop((tl-dl)/0.25))
    if si==4:
        k=sum(1 for th in D[8:12] if tl>=th); over(fr,FORMS[k],W//2,940,1,pop((tl-0.15)/0.3))
        over(fr,STP,W//2+40,1440,1,pop((tl-D[12])/0.2))
    if i<5: fr*=i/5
    return np.clip(fr,0,255).astype(np.uint8)
STP=stamp("RÜCKKEHR UNKLAR",RED,84,-14)
if len(sys.argv)>1 and sys.argv[1]=="preview":
    s=Image.new("RGB",(310*6,533),(255,255,255))
    for j in range(6): s.paste(Image.fromarray(frame(int((ends[j]-0.15)*FPS))).resize((300,533)),(j*310,0))
    s.save("pv.jpg"); sys.exit()
p=subprocess.Popen(["ffmpeg","-y","-v","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-c:v","libx264","-preset","veryfast","-crf","19","-pix_fmt","yuv420p","v_tmp.mp4"],stdin=subprocess.PIPE)
for i in range(int(TOTAL*FPS)): p.stdin.write(frame(i).tobytes())
p.stdin.close(); p.wait(); os.replace("v_tmp.mp4","v.mp4"); print("video ok")
