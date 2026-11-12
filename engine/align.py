import json,re,subprocess,sys
BD=sys.argv[1] if len(sys.argv)>1 else 'build_data.py'
src=open(BD).read()
L=eval(src[src.index('L=[')+2:src.index('lines=[]')].strip())
GAP=0.35
tr=[l[0] for l in L]
parts=[(tr.index(k),len(tr)-tr[::-1].index(k)) for k in sorted(set(tr))]
def dur(f):return float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f]))
def sil(f):
    o=subprocess.run(['ffmpeg','-i',f,'-af','silencedetect=n=-38dB:d=0.18','-f','null','-'],capture_output=True,text=True).stderr
    s=[float(x) for x in re.findall(r'silence_start: ([0-9.]+)',o)];e=[float(x) for x in re.findall(r'silence_end: ([0-9.]+)',o)]
    return list(zip(s,e))
out=[None]*len(L);off=0
for p,(a,b) in enumerate(parts):
    f=f'f{p+1}.wav';D=dur(f);S=sil(f)
    # speech segments
    segs=[];t=0
    for s,e in S:
        if s>t: segs.append((t,s))
        t=e
    if t<D: segs.append((t,D))
    # leading/trailing trim
    tot=sum(e-s for s,e in segs)
    def at(frac):  # map fraction of speech to time
        x=frac*tot
        for s,e in segs:
            if x<=e-s: return s+x
            x-=e-s
        return segs[-1][1]
    lens=[len(L[i][1]) for i in range(a,b)];T=sum(lens);c=0
    starts=[]
    for k,i in enumerate(range(a,b)):
        est=at(c/T); c+=lens[k]
        if k==0: starts.append(segs[0][0]);continue
        cands=[e for s,e in S if e>starts[-1]+0.4 and abs(e-est)<0.9]
        starts.append(min(cands,key=lambda e:abs(e-est)) if cands else est)
    for k,i in enumerate(range(a,b)):
        st=starts[k]; nx=starts[k+1] if k+1<len(starts) else segs[-1][1]
        en=nx
        prev=[s for s,e in S if st<s<nx and nx-e<0.05]
        if prev: en=prev[-1]
        words=L[i][1].split(' ');wl=[len(w)+1 for w in words];W=sum(wl);x=st;ws=[]
        for w in wl:
            d=(en-st)*w/W; ws.append([round(off+x,3),round(off+x+d,3)]); x+=d
        out[i]=ws
    off+=D+GAP
json.dump(out,open('timings.json','w'))
for i,w in enumerate(out): print(i,w[0][0],w[-1][1],L[i][1][:34])
