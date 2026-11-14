# Builds data.json. With no timings file, estimates timings from text length (preview mode).
import json,sys,re
T=[dict(n="★",title="Le Top 3 du jour",img="coulounieix",credit="Photo d'illustration : Père Igor / CC BY-SA 3.0",pos="50% 55%",intro=1,headline="Trahi par son caca"),
   dict(n=3,title="Fossé douillet",place="Bergerac · France",img="bergerac",credit="Photo d'illustration : Père Igor / CC BY-SA",pos="50% 55%"),
   dict(n=2,title="Pneus policiers",place="Heidelberg · Allemagne",img="heidelberg",credit="Photo d'illustration : Eugene Alvin Villar (seav) / Creative Commons",pos="50% 50%"),
   dict(n=1,title="Caca fatal",place="Dordogne · France",img="coulounieix",credit="Photo d'illustration : Père Igor / CC BY-SA 3.0",pos="50% 55%")]
# (track, text, flags) — les insultes sont du texte normal, pas de stamp ni d'effet
L=[(0,"Salut bande de bâtards.",{}),
(0,"Aujourd'hui, un voleur se fait choper",dict(hook=1)),
(0,"parce qu'il avait envie de faire caca.",dict(hook=1,stamp="ENVIE DE CACA")),
(0,"Restez jusqu'au numéro un, trous du cul.",{}),
(1,"Numéro trois, branleurs.",dict(switch=1)),
(1,"À Bergerac, en pleine nuit,",dict(stamp="BERGERAC")),
(1,"la police trouve une voiture accidentée,",{}),
(1,"abandonnée au milieu de la route.",{}),
(1,"Personne dedans.",{}),
(1,"Mais 200 mètres plus loin, il y a un reflet jaune.",dict(stamp="200 MÈTRES")),
(1,"C'est le conducteur, endormi dans le fossé.",dict(stamp="DANS LE FOSSÉ")),
(1,"Il voulait rentrer chez lui à pied.",{}),
(1,"Bourré, évidemment, gros cons.",{}),
(1,"Il finit la nuit en garde à vue.",dict(stamp="GARDE À VUE")),
(1,"Quel sportif.",{}),
(2,"Numéro deux, sacs à merde.",dict(switch=1)),
(2,"En Allemagne, à Heidelberg, jeudi soir,",dict(stamp="HEIDELBERG")),
(2,"un mec de 37 ans essaie de dégonfler les pneus",dict(stamp="37 ANS")),
(2,"d'une voiture de police.",{}),
(2,"Petit problème : des policiers le regardent faire.",{}),
(2,"Ils contrôlent son identité…",{}),
(2,"et il avait déjà un mandat d'arrêt sur le dos.",dict(stamp="MANDAT D'ARRÊT")),
(2,"Direct en prison.",dict(stamp="PRISON")),
(2,"Non mais quel génie, bande d'enfoirés.",{}),
(3,"Numéro un, tas de merde.",dict(switch=1)),
(3,"Près de Périgueux, un samedi,",dict(stamp="PÉRIGUEUX")),
(3,"un homme s'arrête pour faire caca dehors.",{}),
(3,"Un chien le surprend.",{}),
(3,"Il panique, il s'enfuit, et il oublie sa sacoche.",{}),
(3,"Dedans : des bijoux qui ne sont pas à lui.",dict(stamp="BIJOUX")),
(3,"La police l'arrête.",dict(stamp="ARRÊTÉ")),
(3,"Le tribunal lui met 12 mois de prison.",dict(stamp="12 MOIS")),
(3,"Trahi par son propre caca. Respect.",{}),
(3,"Lequel est le pire ?",dict(outro=1)),
(3,"Dites-le en commentaire, petites merdes. Bisous !",dict(outro=1))]
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
