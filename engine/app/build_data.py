# Builds data.json. With no timings file, estimates timings from text length (preview mode).
import json,sys,re
T=[dict(n="★",title="Le Top 3 du jour",img="a13",credit="Photo d'illustration : Florian Pepellin / Domaine public",pos="50% 55%",intro=1,headline="Il joue au flic"),
   dict(n=3,title="Tom et Jerry",place="Toulouse · France",img="toulouse",credit="Photo : Archaeodontosaurus / CC BY-SA 4.0",pos="50% 55%"),
   dict(n=2,title="Papi bourré",place="Chypre",img="peyia",credit="Photo d'illustration : Dmitry Panov / CC BY 3.0",pos="50% 55%"),
   dict(n=1,title="Faux gyrophare",place="A13 · France",img="a13",credit="Photo d'illustration : Florian Pepellin / Domaine public",pos="50% 55%")]
# (track, text, flags) — les insultes sont du texte normal, pas de stamp ni d'effet
L=[(0,"Salut bande de connards.",{}),
(0,"Aujourd'hui, un mec roule sur l'autoroute",dict(hook=1)),
(0,"avec un faux gyrophare de police",dict(hook=1,stamp="FAUX GYROPHARE")),
(0,"juste pour éviter les bouchons.",dict(hook=1)),
(0,"Restez jusqu'au numéro un, sales connasses.",{}),
(1,"Numéro trois, petites merdes.",dict(switch=1)),
(1,"Près de Toulouse, un transporteur s'embrouille",{}),
(1,"avec deux policiers municipaux.",{}),
(1,"Le lendemain, il leur envoie par mail",{}),
(1,"un dessin de Tom et Jerry,",dict(stamp="TOM & JERRY")),
(1,"avec le chat en casquette de flic.",{}),
(1,"Résultat : il passe aujourd'hui au tribunal pour outrage.",dict(stamp="OUTRAGE")),
(1,"Il conteste, évidemment.",{}),
(1,"Quel artiste, ducons.",{}),
(2,"Numéro deux, sacs à merde.",dict(switch=1)),
(2,"À Chypre, la police convoque un papi de 69 ans",dict(stamp="69 ANS")),
(2,"pour une plainte.",{}),
(2,"Il arrive au commissariat en voiture…",{}),
(2,"complètement bourré.",dict(stamp="BOURRÉ")),
(2,"Il se gare tranquille sur le parking des flics.",{}),
(2,"Alcootest : explosé.",{}),
(2,"Il est arrêté sur place.",dict(stamp="ARRÊTÉ")),
(2,"Non mais quel génie, bande d'enfoirés.",{}),
(3,"Numéro un, tas de merde.",dict(switch=1)),
(3,"Jeudi soir, sur l'A13 près de Rouen,",dict(stamp="A13")),
(3,"un mec de 23 ans en treillis",dict(stamp="23 ANS")),
(3,"roule avec un gyrophare bleu.",{}),
(3,"Et la sirène ?",{}),
(3,"C'est son téléphone, branché sur l'autoradio, à fond.",dict(stamp="SON TÉLÉPHONE")),
(3,"Les vrais policiers l'interceptent.",{}),
(3,"Son excuse : il voulait éviter les bouchons.",{}),
(3,"Gyrophare saisi, et il passera devant la justice.",dict(stamp="GYROPHARE SAISI")),
(3,"Lequel est le pire ?",dict(outro=1)),
(3,"Dites-le en commentaire, gros débiles de merde. Bisous !",dict(outro=1))]
lines=[]
timings=json.load(open(sys.argv[1])) if len(sys.argv)>1 else None
t=0.15
for i,(tr,txt,fl) in enumerate(L):
    words=txt.split(" ")
    if timings:
        ws=timings[i]  # list of [start,end] per word
    else:
        cps=17.0 if not fl.get("shout") else 13.0
        dur=max(0.7,len(txt)/cps)
        tot=sum(len(w)+1 for w in words); ws=[];c=t
        for w in words:
            d=dur*(len(w)+1)/tot; ws.append([round(c,3),round(c+d,3)]); c+=d
        t+=dur+(0.45 if txt.rstrip()[-1] in ".!?…" else 0.12)
    lines.append(dict(track=tr,text=txt,words=[dict(w=w,s=a,e=b) for w,(a,b) in zip(words,ws)],start=ws[0][0],end=ws[-1][1],**fl))
for k,tk in enumerate(T):
    ls=[l for l in lines if l["track"]==k]; tk["start"]=0 if k==0 else ls[0]["start"]-0.15
total=lines[-1]["end"]+1.6
json.dump(dict(tracks=T,lines=lines,total=round(total,3),env=None),open("data.json","w"),ensure_ascii=False,indent=1)
print("total",total)
