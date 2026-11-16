import json, os, sys, subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFont
W,H,FPS=1080,1920,30
FB="/usr/share/fonts/opentype/inter/Inter-Black.otf"; FM="/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf"
YEL=(255,214,10); RED=(230,40,50); WHITE=(255,255,255); BLACK=(15,15,15); GREEN=(40,190,100); BLUE=(60,140,255)
AL=json.load(open("align.json")); TOTAL=AL["total"]; S=AL["start"]; E=S[1:]+[TOTAL]
# per scene: image, small header, top caption, sub caption, (bottom text, delay), (stamp, color, rot, delay)
SC=[("/mnt/user-data/uploads/GTA6-Clips/Video1/geld.png","100 € statt GTA VI?","Was du WIRKLICH für 100 € kriegst","(echte Preise, ehrlich)",None,None),
 ("sand.png","Idee 1 · ca. 80–95 €","1 Tonne Spielsand","Vice-City-Strand im Wohnzimmer",("Dein Vermieter wird es lieben.",3.94),("KAUTION WEG",RED,-8,4.1)),
 ("ducks.png","Idee 2 · ca. 15–30 € pro Ente","3 Laufenten","",("Jason, Lucia … und Kevin.",1.39),("KEVIN?!",YEL,10,3.08)),
 ("cardboard.png","Idee 3","Pappfigur von dir","in Lebensgröße",("Sitzt für dich im Meeting.",2.81),("MERKT KEINER",GREEN,-8,4.53)),
 ("eis.png","Idee 4 · ca. 2 € pro Kugel","50 Kugeln Eis","…im November",("Einfach, weil du's kannst.",2.57),("BRAINFREEZE",BLUE,-8,1.57)),
 ("couple.png","Plot Twist","…oder einfach GTA VI kaufen","",("Strand, Tiere & Chaos inklusive.",2.3),("PLOT TWIST",YEL,-8,0.1))]
_C={}
def photo(n):
    if n not in _C:
        im=Image.open(n).convert("RGB"); r=max(1080*1.12/im.width,760*1.12/im.height); _C[n]=im.resize((int(im.width*r)+1,int(im.height*r)+1),Image.LANCZOS)
    return _C[n]
def F(fn,s): return ImageFont.truetype(fn,s)
def fit(d,t,fn,size,maxw):
    f=F(fn,size)
    while d.textlength(t,font=f)>maxw: size-=3; f=F(fn,size)
    return f
def stamp(t,col,rot,size=100):
    f=F(FB,size)
    while f.getlength(t)>820: size-=4; f=F(FB,size)
    w=int(f.getlength(t))+80
    im=Image.new("RGBA",(w,int(size*1.55)),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.rounded_rectangle([6,6,w-6,im.height-6],24,outline=col+(255,),width=14); d.text((w//2,im.height//2),t,font=f,fill=col+(255,),anchor="mm")
    return im.rotate(rot,expand=True,resample=Image.BICUBIC)
STAMPS={k:stamp(s[5][0],s[5][1],s[5][2]) for k,s in enumerate(SC) if s[5]}
def pop(t): return 0 if t<=0 else (1 if t>=1 else 1+2.0*(t-1)**3+1.2*(t-1)**2)
def frame(i):
    t=i/FPS; si=max(k for k in range(len(S)) if S[k]<=t+1e-6); tl=t-S[si]; z=tl/max(E[si]-S[si],0.1)
    im=Image.new("RGBA",(W,H),BLACK+(255,)); d=ImageDraw.Draw(im)
    if si<len(SC):
        img,hd,a,b,bot,st=SC[si]
        d.rectangle([0,180,W,600],fill=WHITE)
        d.text((60,250),"@gtavi_germany · "+hd,font=F(FM,38),fill=(120,120,120),anchor="lm")
        d.text((W//2,420 if not b else 390),a,font=fit(d,a,FB,96,W-120),fill=BLACK,anchor="mm")
        if b: d.text((W//2,500),b,font=fit(d,b,FM,56,W-120),fill=(70,70,70),anchor="mm")
        p=photo(img); mw,mh=p.width-W,p.height-760; x=int(mw*(0.2+0.6*z)); im.paste(p.crop((x,mh//2,x+W,mh//2+760)),(0,600))
        if bot and tl>=bot[1]: d.text((W//2,1530),bot[0],font=fit(d,bot[0],FB,80,W-100),fill=YEL if si==6 else WHITE,anchor="mm")
        if st:
            s=pop((tl-st[3])/0.2)
            if s>0.02:
                sp=STAMPS[si]; sp=sp.resize((max(1,int(sp.width*s)),max(1,int(sp.height*s)))); im.alpha_composite(sp,(int(W/2-sp.width/2),int(980-sp.height/2)))
    else:
        p=Image.open("/home/claude/out/bilder5/skyline.png").convert("RGB"); p=p.resize((int(p.width*H/p.height),H)); im.paste(p.crop((300,0,300+W,H)),(0,0)); im.alpha_composite(Image.new("RGBA",(W,H),(0,0,0,110)))
        d=ImageDraw.Draw(im)
        for tx,y,c,s,dl in [("FOLGE DEM KANAL",820,WHITE,110,0),("FÜR MEHR INFOS!",980,YEL,120,0.3)]:
            if tl>=dl: d.text((W//2,y),tx,font=fit(d,tx,FB,s,W-80),fill=c,anchor="mm",stroke_width=7,stroke_fill=(0,0,0))
    a=np.asarray(im.convert("RGB")).astype(np.float32)
    if i<5: a*=i/5
    return a.astype(np.uint8)
if len(sys.argv)>1:
    n=len(S); s=Image.new("RGB",(310*n,533),(255,255,255))
    for j in range(n): s.paste(Image.fromarray(frame(int((E[j]-0.15)*FPS))).resize((300,533)),(j*310,0))
    s.save("pv.jpg"); sys.exit()
p=subprocess.Popen(["ffmpeg","-y","-v","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-c:v","libx264","-preset","veryfast","-crf","19","-pix_fmt","yuv420p","v_tmp.mp4"],stdin=subprocess.PIPE)
for i in range(int(TOTAL*FPS)): p.stdin.write(frame(i).tobytes())
p.stdin.close(); p.wait(); os.replace("v_tmp.mp4","v.mp4"); print("video ok")
