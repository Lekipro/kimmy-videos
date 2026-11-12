"""Free Fish Audio voice (model s2.1-pro-free) via the API.
usage: FISH_API_KEY=... python3 tts_free.py part1.txt part2.txt part3.txt part4.txt
Writes p1.mp3 ... pN.mp3 in the current folder. Voice: Clémence."""
import json,os,sys,time,urllib.request,urllib.error
KEY=os.environ['FISH_API_KEY']
VOICE='bdfbdcb27253419ba7e0746af7a154f8'
for i,f in enumerate(sys.argv[1:],1):
    text=open(f,encoding='utf-8').read().strip()
    body={"text":text,"reference_id":VOICE,"format":"mp3"}
    for attempt in range(3):
        r=urllib.request.Request("https://api.fish.audio/v1/tts",data=json.dumps(body).encode(),
            headers={"Authorization":"Bearer "+KEY,"Content-Type":"application/json","model":"s2.1-pro-free"})
        try:
            d=urllib.request.urlopen(r,timeout=180).read(); open(f'p{i}.mp3','wb').write(d); print('ok',f'p{i}.mp3',len(d)); break
        except urllib.error.HTTPError as e:
            msg=e.read()[:300]; print('erreur',e.code,msg)
            if e.code in (401,402,403): sys.exit(1)
            time.sleep(10)
    else: sys.exit(1)
