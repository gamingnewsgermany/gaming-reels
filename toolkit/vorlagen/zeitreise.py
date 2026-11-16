import os, sys, subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W,H,FPS=1080,1920,30
FB="/usr/share/fonts/opentype/inter/Inter-Black.otf"; FM="/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf"; MONO="/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf"
ORANGE=(255,150,40); WHITE=(255,255,255); RED=(230,50,60); TEAL=(40,200,190); YEL=(255,214,10); INK=(30,30,40)
S=[0,7.64,10.67,14.51,18.27,21.80,26.80,31.71,36.24]; TOTAL=45.2; E=S[1:]+[TOTAL]
V1="/mnt/user-data/uploads/GTA6-Clips/Video1/"
BG=["zimmer2013.png","party.png",V1+"buero.png","flut.png","stadion.png","party.png","zimmer2013.png",V1+"geld.png","/home/claude/out/bilder5/skyline.png"]
_C={}
def bg(n,dark,blur):
    k=(n,dark,blur)
    if k not in _C:
        im=Image.open(n).convert("RGB"); r=max(W*1.12/im.width,H*1.05/im.height); im=im.resize((int(im.width*r)+1,int(im.height*r)+1),Image.LANCZOS)
        if blur: im=im.filter(ImageFilter.GaussianBlur(blur))
        _C[k]=np.asarray(im).astype(np.float32)*dark
    return _C[k]
def txt(t,font,size,col,stroke=7,maxw=W-90):
    f=ImageFont.truetype(font,size)
    while f.getlength(t)>maxw: size-=3; f=ImageFont.truetype(font,size)
    im=Image.new("RGBA",(W,int(size*1.5)),(0,0,0,0)); ImageDraw.Draw(im).text((W//2,im.height//2),t,font=f,fill=col,anchor="mm",stroke_width=stroke,stroke_fill=(0,0,0))
    return np.asarray(im).astype(np.float32)
def chip(t,col):
    f=ImageFont.truetype(FB,56); w=int(f.getlength(t))+70
    im=Image.new("RGBA",(w,96),(0,0,0,0)); d=ImageDraw.Draw(im); d.rounded_rectangle([0,0,w-1,95],48,fill=col+(255,)); d.text((w//2,48),t,font=f,fill=(0,0,0),anchor="mm")
    return np.asarray(im).astype(np.float32)
def polaroid(img,cap,rot):
    pw,ph=820,620; w,h=pw+60,ph+200
    im=Image.new("RGBA",(w,h),(0,0,0,0)); d=ImageDraw.Draw(im); d.rectangle([0,0,w-1,h-1],fill=(248,246,238,255))
    if img:
        p=Image.open(img).convert("RGB"); r=max(pw/p.width,ph/p.height); p=p.resize((int(p.width*r)+1,int(p.height*r)+1)); x=(p.width-pw)//2; p=p.crop((x,0,x+pw,ph)); im.paste(p,(30,30))
    f=ImageFont.truetype(FM,58); s=58
    while f.getlength(cap)>w-60: s-=2; f=ImageFont.truetype(FM,s)
    d.text((w//2,ph+115),cap,font=f,fill=INK,anchor="mm")
    return np.asarray(im.rotate(rot,expand=True,resample=Image.BICUBIC)).astype(np.float32)
def bigcard(lines,col,rot):
    w,h=860,700; im=Image.new("RGBA",(w,h),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.rectangle([0,0,w-1,h-1],fill=(248,246,238,255)); d.rectangle([24,24,w-25,h-25],outline=col+(255,),width=6)
    y=h/2-(len(lines)-1)*70
    for t,fn,sz,c in lines:
        f=ImageFont.truetype(fn,sz)
        while f.getlength(t)>w-90: sz-=3; f=ImageFont.truetype(fn,sz)
        d.text((w//2,y),t,font=f,fill=c,anchor="mm"); y+=140
    return np.asarray(im.rotate(rot,expand=True,resample=Image.BICUBIC)).astype(np.float32)
def over(fr,ov,cx,cy,a=1.0,scale=1.0):
    if a<=0.01 or scale<=0.02: return
    if abs(scale-1)>0.005:
        im=Image.fromarray(ov.astype(np.uint8),"RGBA").resize((max(1,int(ov.shape[1]*scale)),max(1,int(ov.shape[0]*scale))),Image.BILINEAR); ov=np.asarray(im).astype(np.float32)
    h,w=ov.shape[:2]; x=int(cx-w/2); y=int(cy-h/2); x0,y0=max(0,x),max(0,y); x1,y1=min(W,x+w),min(H,y+h)
    if x1<=x0 or y1<=y0: return
    o=ov[y0-y:y1-y,x0-x:x1-x]; al=o[:,:,3:4]/255*a; fr[y0:y1,x0:x1]=fr[y0:y1,x0:x1]*(1-al)+o[:,:,:3]*al
def pop(t): return 0 if t<=0 else (1 if t>=1 else 1+2.0*(t-1)**3+1.2*(t-1)**2)
WITZ=chip("WITZIG",YEL); ERN=chip("ERNST",RED); SPORT=chip("SPORT",TEAL); GAME=chip("GAMING",ORANGE)
EL={0:[(txt("17. SEPTEMBER 2013",FB,96,ORANGE),560,0),(txt("GTA V erscheint.",FB,110,WHITE),720,2.74),(txt("Aber was war",FM,80,WHITE,6),1180,5.01-0),(txt("sonst noch los?",FB,104,YEL),1300,5.4)],
 1:[(WITZ,430,0),(bigcard([("Merkel:",FM,70,(90,90,100)),("„Das Internet",FB,96,INK),("ist Neuland“",FB,96,INK)],YEL,-3),980,0.15)],
 2:[(ERN,430,0),(bigcard([("NSA-SKANDAL",FB,110,RED),("Snowden deckt",FM,72,INK),("weltweite Überwachung auf",FM,60,INK)],RED,2),980,0.15)],
 3:[(ERN,430,0),(polaroid("flut.png","Hochwasser an Elbe & Donau",-3),1000,0.15)],
 4:[(SPORT,430,0),(polaroid("stadion.png","CL-Finale: Bayern vs. Dortmund",3),1000,0.15)],
 5:[(WITZ,430,0),(polaroid("party.png","Harlem Shake überall",-2),980,0.15),(txt("What does the fox say?",FB,80,YEL),1560,3.8)],
 6:[(WITZ,430,0),(polaroid("zimmer2013.png","„Selfie“ = Wort des Jahres",2),960,0.15),(txt("November: PS4 kommt",FB,84,ORANGE),1560,2.74)],
 7:[(GAME,430,0),(txt("GTA V am 1. Tag:",FM,80,WHITE,6),800,0.2),(txt("800 MIO. $",FB,180,YEL),980,1.6),(txt("Umsatz",FB,100,WHITE),1160,1.9)],
 8:[(txt("13 JAHRE SPÄTER…",FB,100,WHITE),520,0),(txt("GTA VI",FB,230,YEL),720,1.4),(txt("Wo warst du 2013?",FM,76,WHITE,6),1050,4.17),(txt("FOLGE DEM KANAL",FB,104,WHITE),1360,6.48),(txt("FÜR MEHR INFOS!",FB,114,ORANGE),1510,6.8)]}
REC=Image.new("RGBA",(W,140),(0,0,0,0)); d=ImageDraw.Draw(REC); d.ellipse([60,50,100,90],fill=(230,30,30,255)); d.text((120,70),"REC",font=ImageFont.truetype(MONO,48),fill=WHITE,anchor="lm")
d.text((W-60,70),"SEP 17 2013",font=ImageFont.truetype(MONO,48),fill=ORANGE,anchor="rm"); REC=np.asarray(REC).astype(np.float32)
SCAN=np.ones((H,1,1),np.float32); SCAN[::4]=0.9
def frame(i):
    t=i/FPS; si=max(k for k in range(len(S)) if S[k]<=t+1e-6); tl=t-S[si]; z=tl/max(E[si]-S[si],0.1)
    sharp=si in (0,8); a=bg(BG[si],0.6 if sharp else 0.45,0 if sharp else 16)
    mh,mw=a.shape[0]-H,a.shape[1]-W; x=int(mw*(0.2+0.6*z) if si%2==0 else mw*(0.8-0.6*z))
    fr=a[mh//2:mh//2+H,x:x+W].copy()
    for ov,cy,dl in EL[si]: over(fr,ov,W//2,cy,1,pop((tl-dl)/0.25))
    if si<8 and int(t*2)%2==0: over(fr,REC,W//2,110)
    elif si<8: over(fr,REC[:,W//2:],W*3//4,110)
    fr*=SCAN
    if i<5: fr*=i/5
    return np.clip(fr,0,255).astype(np.uint8)
if len(sys.argv)>1:
    s=Image.new("RGB",(310*9,533),(255,255,255))
    for j in range(9): s.paste(Image.fromarray(frame(int((E[j]-0.15)*FPS))).resize((300,533)),(j*310,0))
    s.save("pv.jpg"); sys.exit()
p=subprocess.Popen(["ffmpeg","-y","-v","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-c:v","libx264","-preset","veryfast","-crf","19","-pix_fmt","yuv420p","v_tmp.mp4"],stdin=subprocess.PIPE)
for i in range(int(TOTAL*FPS)): p.stdin.write(frame(i).tobytes())
p.stdin.close(); p.wait(); os.replace("v_tmp.mp4","v.mp4"); print("video ok")
