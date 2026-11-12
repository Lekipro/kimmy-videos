"""Mix voice + sound effects. usage: python3 sfx_mix.py data.json voix.wav out.wav
Bonk/boing after each insult line (flag instant), whoosh at each new track,
and keyword sounds (en live, abonn, arrêt, chie, caméra, urgence, last line = kiss)."""
import subprocess,re,json,sys,os
D=os.path.join(os.path.dirname(os.path.abspath(__file__)),'sfx')
d=json.load(open(sys.argv[1]));L=d['lines'];T=d['tracks']
ev=[];k=0
for t in T[1:]: ev.append((t['start']-0.25,'whoosh.wav',-17))
KW=[('live','ding.mp3',-16,'start',-0.1),('abonn','ding.mp3',-16,'end',-0.3),('arrêt','police.wav',-19,'end',-0.6),
    ('chie','fart.wav',-13,'end',-0.1),('caméra','shutter.mp3',-15,'end',-0.3),('urgence','ambulance.wav',-22,'start',0.4),
    ('police','police.wav',-19,'end',-0.6)]
used=set()
for kw,f,db,ref,off in KW:
    for l in L[:-1]:
        if kw in l['text'].lower() and kw not in used and not (kw=='police' and 'arrêt' in used):
            ev.append((l[ref]+off,f,db)); used.add(kw); break
ev.append((L[-1]['end']-0.4,'kiss.mp3',-14))
def peak(f):
    o=subprocess.run(['ffmpeg','-i',f,'-af','volumedetect','-f','null','-'],capture_output=True,text=True).stderr
    return float(re.search(r'max_volume: (-?[0-9.]+)',o).group(1))
ev=sorted(ev);pk={f:peak(os.path.join(D,f)) for f in set(e[1] for e in ev)}
ins=['-i',sys.argv[2]];fl=[];labs=[]
for j,(t,f,db) in enumerate(ev):
    ins+=['-i',os.path.join(D,f)];ms=int(max(0,t)*1000)
    fl.append(f"[{j+1}:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:1.3,afade=t=out:st=1.0:d=0.3,volume={db-pk[f]:.1f}dB,adelay={ms}|{ms}[s{j}]");labs.append(f"[s{j}]")
fl.append(f"[0:a]aformat=channel_layouts=stereo[v];[v]{''.join(labs)}amix=inputs={len(ev)+1}:duration=first:normalize=0,alimiter=limit=0.89[o]")
subprocess.run(['ffmpeg','-y','-loglevel','error',*ins,'-filter_complex',';'.join(fl),'-map','[o]','-ar','48000',sys.argv[3]],check=True)
print(len(ev),'bruitages')
