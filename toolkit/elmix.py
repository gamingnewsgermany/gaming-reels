import numpy as np, subprocess, sys, os
SR=48000
def dec(p): return np.frombuffer(subprocess.check_output(["ffmpeg","-v","error","-i",p,"-f","f32le","-ac","1","-ar",str(SR),"-"]),np.float32).copy()
SFX={n:(lambda a:a/(np.abs(a).max()+1e-9))(dec(os.path.join(os.path.dirname(os.path.abspath(__file__)),"sfx",f"{n}.mp3"))) for n in ["kaching","whoosh","scratch","coins","trombone","ding","stamp"]}
VOICE_FX="highpass=f=90,equalizer=f=250:t=q:w=1.2:g=-3,equalizer=f=3500:t=q:w=1.0:g=4,highshelf=f=8000:g=3,acompressor=threshold=-20dB:ratio=3:attack=5:release=80:makeup=2"
def dec_voice(p):
    return np.frombuffer(subprocess.check_output(["ffmpeg","-v","error","-i",p,"-af",VOICE_FX,"-f","f32le","-ac","1","-ar",str(SR),"-"]),np.float32).copy()
def mix(vo_path,music_path,music_off,T,events,out,mgain=0.07,sgain=0.22,stereo=True):
    vo=dec_voice(vo_path); mu=dec(music_path); N=int(T*SR)
    o=np.zeros(N,np.float32); o[:len(vo)]+=vo[:N]
    m=mu[int(music_off*SR):int(music_off*SR)+N]; m=np.pad(m,(0,max(0,N-len(m))))
    env=np.ones(N)*mgain; env[len(vo):]=mgain*2.4
    fx=np.zeros(N,np.float32)
    for t,n,g in events:
        x=SFX[n]*g*sgain; j=int(t*SR); fx[j:j+len(x)]+=x[:max(0,N-j)]
    y=o+m*env+fx; f=int(0.6*SR); y[-f:]*=np.linspace(1,0,f); y/=np.abs(y).max()/0.9
    subprocess.run(["ffmpeg","-y","-v","error","-f","f32le","-ar",str(SR),"-ac","1","-i","-","-af","loudnorm=I=-14:TP=-1.5","-ar","48000","-ac","2" if stereo else "1",out],input=y.astype(np.float32).tobytes(),check=True)
