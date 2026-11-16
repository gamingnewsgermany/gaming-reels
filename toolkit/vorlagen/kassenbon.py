import json, os, sys, subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
W,H,FPS=1080,1920,30
FB="/usr/share/fonts/opentype/inter/Inter-Black.otf"; FM="/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf"; MONO="/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf"
SRC=["/home/claude/out/bilder5/","/mnt/user-data/uploads/GTA6-Clips/Video1/"]
def find(n):
    for s in SRC:
        if os.path.exists(s+n): return s+n
GREEN=(40,200,120); YEL=(255,214,10); RED=(230,40,50); WHITE=(255,255,255)
AL=json.load(open("align.json")) if os.path.exists("align.json") else None
TOTAL=AL["total"] if AL else 40.0
starts=AL["start"] if AL else [TOTAL*x for x in [0,0.12,0.42,0.58,0.75,0.95]]
ends=starts[1:]+[TOTAL]
IMG=["geld.png","room.png","wohnzimmer.png","geld.png","room.png","strand.png"]
_C={}
def bg(n,blur=0,dark=0.75):
    k=(n,blur,dark)
    if k not in _C:
        im=Image.open(find(n)).convert("RGB"); r=max(W*1.1/im.width,H*1.05/im.height); im=im.resize((int(im.width*r)+1,int(im.height*r)+1),Image.LANCZOS)
        if blur: im=im.filter(ImageFilter.GaussianBlur(blur))
        _C[k]=np.asarray(ImageEnhance.Color(im).enhance(1.15)).astype(np.float32)*dark
    return _C[k]
def txt(text,font,size,col,stroke=6,maxw=W-80):
    f=ImageFont.truetype(font,size)
    while f.getlength(text)>maxw: size-=3; f=ImageFont.truetype(font,size)
    im=Image.new("RGBA",(W,int(size*1.5)),(0,0,0,0)); ImageDraw.Draw(im).text((W//2,im.height//2),text,font=f,fill=col,anchor="mm",stroke_width=stroke,stroke_fill=(0,0,0))
    return np.asarray(im).astype(np.float32)
def receipt(lines,total=None,title="KASSENBON"):
    w=820; lh=78; h=200+lh*len(lines)+(150 if total else 40)
    im=Image.new("RGBA",(w,h+40),(0,0,0,0)); d=ImageDraw.Draw(im)
    pts=[(0,0),(w,0),(w,h)]+[(w-i*40-(20 if i%2 else 0),h+(20 if i%2==0 else 0)) for i in range(int(w/40)+1)]+[(0,h)]
    d.polygon([(0,0),(w,0),(w,h)]+[(w-i*41,h+(22 if i%2 else 0)) for i in range(21)]+[(0,h)],fill=(250,248,240,255))
    fm=ImageFont.truetype(MONO,44); ft=ImageFont.truetype(MONO,56)
    d.text((w//2,70),title,font=ft,fill=(30,30,30),anchor="mm"); d.text((w//2,125),"- "*16,font=fm,fill=(120,120,120),anchor="mm")
    y=180
    for a,b,c in lines:
        d.text((50,y),a,font=fm,fill=(30,30,30)); d.text((w-50,y),b,font=fm,fill=c or (30,30,30),anchor="ra"); y+=lh
    if total:
        d.text((w//2,y+10),"= "*16,font=fm,fill=(120,120,120),anchor="mm")
        d.text((50,y+50),total[0],font=ft,fill=(30,30,30)); d.text((w-50,y+50),total[1],font=ft,fill=(200,40,50),anchor="ra")
    return np.asarray(im).astype(np.float32)
def stamp(text,col=RED,size=150,rot=-12):
    f=ImageFont.truetype(FB,size); w=int(f.getlength(text))+80
    im=Image.new("RGBA",(w,int(size*1.55)),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.rounded_rectangle([6,6,w-6,im.height-6],24,outline=col+(255,),width=14); d.text((w//2,im.height//2),text,font=f,fill=col+(255,),anchor="mm")
    return np.asarray(im.rotate(rot,expand=True,resample=Image.BICUBIC)).astype(np.float32)
def over(fr,ov,cx,cy,a=1.0,scale=1.0):
    if a<=0.01 or scale<=0.02: return
    if abs(scale-1)>0.005:
        im=Image.fromarray(ov.astype(np.uint8),"RGBA"); im=im.resize((max(1,int(im.width*scale)),max(1,int(im.height*scale))),Image.BILINEAR); ov=np.asarray(im).astype(np.float32)
    h,w=ov.shape[:2]; x=int(cx-w/2); y=int(cy-h/2); x0,y0=max(0,x),max(0,y); x1,y1=min(W,x+w),min(H,y+h)
    if x1<=x0 or y1<=y0: return
    o=ov[y0-y:y1-y,x0-x:x1-x]; al=o[:,:,3:4]/255*a; fr[y0:y1,x0:x1]=fr[y0:y1,x0:x1]*(1-al)+o[:,:,:3]*al
def pop(t): return 0 if t<=0 else (1 if t>=1 else 1+2.0*(t-1)**3+1.2*(t-1)**2)
R1_LINES=[("PS5 Digital","599,99 €",None),("PS5 Laufwerk","649,99 €",None),("PS5 Pro","899,99 €",RED)]
R1=[receipt(R1_LINES[:k],title="PS5-PREISE 2026") for k in range(4)]
R2=receipt([("PS5 Digital","599,99 €",None),("GTA VI","79,99 €",None)],("SUMME","679,98 €"),title="GÜNSTIGSTE KOMBI")
EL={0:[(txt("WAS KOSTET DICH",FB,100,WHITE),520,0),(txt("GTA VI WIRKLICH?",FB,120,YEL),660,0.3),(txt("Spoiler: nicht 79,99 €",FM,64,WHITE,4),1400,2.9)],
    1:[(txt("PREISERHÖHUNG SEIT APRIL",FB,90,YEL),330,0)],
    2:[(txt("PS5 PRO WEGEN GTA VI",FB,90,WHITE),360,0),(stamp("AUSVERKAUFT",RED,130),880,2.5),(txt("Drittanbieter: oft über",FM,62,WHITE,4),1330,3.7),(txt("1.300 €",FB,140,YEL),1470,5.3)],
    3:[(txt("PRO + GTA VI BUNDLE",FB,92,WHITE),400,0),(txt("1.599,99 €",FB,190,YEL),640,0.5),(txt("Offizielles Sony-Bundle?",FM,64,WHITE,4),1250,4.6),(stamp("GIBT'S NICHT",RED,110,8),1460,6.35)],
    4:[(txt("MEIN TIPP",FB,110,GREEN),300,0),(txt("Auch auf der Pro: 30 FPS",FM,62,WHITE,4),1560,4.5)],
    5:[(txt("FOLGE DEM KANAL",FB,110,WHITE),760,0),(txt("FÜR MEHR INFOS!",FB,120,YEL),920,0.35)]}
def frame(i):
    t=i/FPS; si=max(k for k in range(len(starts)) if starts[k]<=t+1e-6); tl=t-starts[si]; dur=ends[si]-starts[si]; z=tl/max(dur,0.1)
    a=bg(IMG[si],blur=18 if si in (1,4) else 0,dark=0.55 if si in (1,4) else 0.75)
    mh,mw=a.shape[0]-H,a.shape[1]-W; x=int(mw*(0.2+0.6*z) if si%2==0 else mw*(0.8-0.6*z))
    fr=a[mh//2:mh//2+H,x:x+W].copy()
    for ov,cy,dl in EL[si]: over(fr,ov,W//2,cy,1,pop((tl-dl)/0.25))
    if si==1:
        k=sum(1 for th in (3.03,6.32,9.14) if tl>=th)
        over(fr,R1[k],W//2,1050,1,1.25*pop((tl-0.2)/0.3))
    if si==4: over(fr,R2,W//2,1000,1,1.25*pop((tl-0.8)/0.3))
    if i<5: fr*=i/5
    return np.clip(fr,0,255).astype(np.uint8)
if len(sys.argv)>1 and sys.argv[1]=="preview":
    for k in [1,2,3,4]:
        Image.fromarray(frame(int((starts[k]+(ends[k]-starts[k])*0.95)*FPS))).resize((300,533)).save(f"pv{k}.jpg")
    s=Image.new("RGB",(1240,533),(255,255,255))
    for j,k in enumerate([1,2,3,4]): s.paste(Image.open(f"pv{k}.jpg"),(j*310,0))
    s.save("pv.jpg"); sys.exit()
n=int(TOTAL*FPS)
p=subprocess.Popen(["ffmpeg","-y","-v","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-c:v","libx264","-preset","veryfast","-crf","19","-pix_fmt","yuv420p","v.mp4"],stdin=subprocess.PIPE)
for i in range(n): p.stdin.write(frame(i).tobytes())
p.stdin.close(); p.wait(); print("video ok")
