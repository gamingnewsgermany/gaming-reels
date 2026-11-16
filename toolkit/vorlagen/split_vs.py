import json, os, sys, subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
W,H,FPS=1080,1920,30
FB="/usr/share/fonts/opentype/inter/Inter-Black.otf"; FM="/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf"
SRC=["/home/claude/out/bilder5/","/mnt/user-data/uploads/GTA6-Clips/Video1/"]
def find(n):
    for s in SRC:
        if os.path.exists(s+n): return s+n
GOLD=(255,196,40); STEEL=(120,170,230); WHITE=(255,255,255); RED=(230,40,50); GREEN=(60,210,120)
AL=json.load(open("align.json")); TOTAL=AL["total"]; starts=AL["start"]; D=AL["d"]
ends=starts[1:]+[TOTAL]
IMG=["skyline.png","street.png","strand.png","room.png","skyline.png","street.png"]
_C={}
def bg(n,dark=0.6,blur=0):
    k=(n,dark,blur)
    if k not in _C:
        im=Image.open(find(n)).convert("RGB"); r=max(W*1.1/im.width,H*1.05/im.height); im=im.resize((int(im.width*r)+1,int(im.height*r)+1),Image.LANCZOS)
        if blur: im=im.filter(ImageFilter.GaussianBlur(blur))
        _C[k]=np.asarray(im).astype(np.float32)*dark
    return _C[k]
def txt(t,font,size,col,stroke=6,maxw=W-80,w=W):
    f=ImageFont.truetype(font,size)
    while f.getlength(t)>maxw: size-=3; f=ImageFont.truetype(font,size)
    im=Image.new("RGBA",(w,int(size*1.5)),(0,0,0,0)); ImageDraw.Draw(im).text((w//2,im.height//2),t,font=f,fill=col,anchor="mm",stroke_width=stroke,stroke_fill=(0,0,0))
    return np.asarray(im).astype(np.float32)
def card(title,price,col,w=480,h=560):
    im=Image.new("RGBA",(w,h),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.rounded_rectangle([0,0,w-1,h-1],36,fill=(12,12,18,225),outline=col+(255,),width=10)
    f1=ImageFont.truetype(FB,64); f2=ImageFont.truetype(FB,80); f3=ImageFont.truetype(FM,40)
    d.text((w//2,120),title,font=f1,fill=col,anchor="mm"); d.text((w//2,150+40),"EDITION",font=f3,fill=(200,200,200),anchor="mm")
    d.text((w//2,360),price,font=f2,fill=WHITE,anchor="mm")
    return np.asarray(im).astype(np.float32)
def row(label,ok,col,w=920):
    im=Image.new("RGBA",(w,120),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.rounded_rectangle([0,6,w-1,114],28,fill=(10,10,16,215))
    c=(60,60); 
    d.ellipse([28,22,104,98],fill=col+(255,))
    if ok: d.line([(46,62),(62,80),(88,42)],fill=(0,0,0),width=11,joint="curve")
    else: d.line([(48,42),(84,78)],fill=(0,0,0),width=11); d.line([(84,42),(48,78)],fill=(0,0,0),width=11)
    f=ImageFont.truetype(FM,52); s=52
    while f.getlength(label)>w-170: s-=2; f=ImageFont.truetype(FM,s)
    d.text((135,60),label,font=f,fill=WHITE,anchor="lm")
    return np.asarray(im).astype(np.float32)
def badge(t,col,size=110,rot=-10):
    f=ImageFont.truetype(FB,size); w=int(f.getlength(t))+80
    im=Image.new("RGBA",(w,int(size*1.55)),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.rounded_rectangle([6,6,w-6,im.height-6],24,outline=col+(255,),width=14); d.text((w//2,im.height//2),t,font=f,fill=col+(255,),anchor="mm")
    return np.asarray(im.rotate(rot,expand=True,resample=Image.BICUBIC)).astype(np.float32)
def vs():
    im=Image.new("RGBA",(220,220),(0,0,0,0)); d=ImageDraw.Draw(im); d.ellipse([5,5,215,215],fill=(230,40,50,255),outline=(255,255,255,255),width=8)
    d.text((110,112),"VS",font=ImageFont.truetype(FB,96),fill=WHITE,anchor="mm"); return np.asarray(im).astype(np.float32)
def over(fr,ov,cx,cy,a=1.0,scale=1.0):
    if a<=0.01 or scale<=0.02: return
    if abs(scale-1)>0.005:
        im=Image.fromarray(ov.astype(np.uint8),"RGBA").resize((max(1,int(ov.shape[1]*scale)),max(1,int(ov.shape[0]*scale))),Image.BILINEAR); ov=np.asarray(im).astype(np.float32)
    h,w=ov.shape[:2]; x=int(cx-w/2); y=int(cy-h/2); x0,y0=max(0,x),max(0,y); x1,y1=min(W,x+w),min(H,y+h)
    if x1<=x0 or y1<=y0: return
    o=ov[y0-y:y1-y,x0-x:x1-x]; al=o[:,:,3:4]/255*a; fr[y0:y1,x0:x1]=fr[y0:y1,x0:x1]*(1-al)+o[:,:,:3]*al
def pop(t): return 0 if t<=0 else (1 if t>=1 else 1+2.0*(t-1)**3+1.2*(t-1)**2)
CS=card("STANDARD","79,99 €",STEEL); CU=card("ULTIMATE","99,99 €",GOLD); VS=vs()
# element: (overlay, cx, cy, delay)
EL={0:[(txt("WELCHE EDITION",FB,104,WHITE),W//2,330,0),(txt("LOHNT SICH?",FB,120,GOLD),W//2,470,0.25),(CS,265,1000,D[0]),(CU,815,1000,D[1]),(VS,W//2,1000,D[1]+0.3)],
    1:[(txt("IN BEIDEN DRIN",FB,100,WHITE),W//2,330,0)]+[(row(l,True,GREEN),W//2,620+i*150,D[2+i]) for i,l in enumerate(["Komplette Story","Ganz Vice City","Ganz Leonida"])]+[(txt("Unterschied:",FM,64,WHITE,4),W//2,1240,D[5]),(txt("+20 €",FB,200,GOLD),W//2,1420,D[5]+0.2)],
    2:[(txt("NUR IN ULTIMATE",FB,100,GOLD),W//2,300,0)]+[(row(l,True,GOLD),W//2,560+i*150,D[6+i]) for i,l in enumerate(["Exklusive Klassiker-Autos","Garage mit Waffenschrank","Tuning-Werkstätten","Gravierte Pistolen","Extra-Missionen"])],
    3:[(txt("ABER ACHTUNG",FB,110,WHITE),W//2,330,0),(badge("NUR DIGITAL",RED),W//2,760,D[11]),(row("Upgrade jederzeit später möglich",True,GREEN),W//2,1250,D[12])],
    4:[(txt("MEIN TIPP",FB,120,GREEN),W//2,330,0),(CS,W//2,980,0.3),(badge("ERST DIE",GREEN,90,8),W//2,560,0.1),(txt("später upgraden",FB,90,GOLD),W//2,1400,D[13])],
    5:[(txt("FOLGE DEM KANAL",FB,110,WHITE),W//2,760,0),(txt("FÜR MEHR INFOS!",FB,120,GOLD),W//2,920,0.35)]}
def frame(i):
    t=i/FPS; si=max(k for k in range(len(starts)) if starts[k]<=t+1e-6); tl=t-starts[si]; z=tl/max(ends[si]-starts[si],0.1)
    a=bg(IMG[si],0.5 if si in (1,2,3) else 0.62,14 if si in (1,2,3) else 0)
    mh,mw=a.shape[0]-H,a.shape[1]-W; x=int(mw*(0.2+0.6*z) if si%2==0 else mw*(0.8-0.6*z))
    fr=a[mh//2:mh//2+H,x:x+W].copy()
    if si==0 and tl>D[0]:
        fr[:,:W//2]=fr[:,:W//2]*0.75+np.array(STEEL)*0.08; fr[:,W//2:]=fr[:,W//2:]*0.75+np.array(GOLD)*0.08
    for ov,cx,cy,dl in EL[si]: over(fr,ov,cx,cy,1,pop((tl-dl)/0.25))
    if i<5: fr*=i/5
    return np.clip(fr,0,255).astype(np.uint8)
if len(sys.argv)>1 and sys.argv[1]=="preview":
    s=Image.new("RGB",(310*5,533),(255,255,255))
    for j,k in enumerate([0,1,2,3,4]):
        s.paste(Image.fromarray(frame(int((ends[k]-0.2)*FPS))).resize((300,533)),(j*310,0))
    s.save("pv.jpg"); sys.exit()
p=subprocess.Popen(["ffmpeg","-y","-v","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-c:v","libx264","-preset","veryfast","-crf","19","-pix_fmt","yuv420p","v_tmp.mp4"],stdin=subprocess.PIPE)
for i in range(int(TOTAL*FPS)): p.stdin.write(frame(i).tobytes())
p.stdin.close(); p.wait(); os.replace("v_tmp.mp4","v.mp4"); print("video ok")
