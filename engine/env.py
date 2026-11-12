"""Add the voice loudness envelope (equaliser bars) to data.json. usage: python3 env.py voice.wav data.json"""
import json,sys,subprocess,numpy as np
raw=subprocess.check_output(['ffmpeg','-loglevel','error','-i',sys.argv[1],'-f','s16le','-ac','1','-ar','48000','-'])
a=np.frombuffer(raw,np.int16).astype(np.float32)/32768;n=1600;fr=len(a)//n
rms=np.sqrt((a[:fr*n].reshape(fr,n)**2).mean(1));env=np.convolve(np.clip(rms/np.percentile(rms,97),0,1),[.25,.5,.25],'same')
d=json.load(open(sys.argv[2]));d['env']=[round(float(x),3) for x in env];json.dump(d,open(sys.argv[2],'w'),ensure_ascii=False);print('total',d['total'])
