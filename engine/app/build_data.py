# Builds data.json. With no timings file, estimates timings from text length (preview mode).
import json,sys,re
T=[dict(n="★",title="Le Top 3 du jour",place="Kimmy · Infos débiles",img="kimmy",credit="",pos="50% 22%",intro=1),
   dict(n=3,title="Pilleur en live",place="Nantes · France",img="nantes",credit="Photo : Chabe01 / CC BY-SA 4.0",pos="50% 55%"),
   dict(n=2,title="Papa Pokémon",place="Charleston · États-Unis",img="target",credit="Photo d'illustration : Winnebaggo / CC0",pos="72% 50%"),
   dict(n=1,title="Mauvais perdant",place="Michigan · États-Unis",img="lycee",credit="Photo : 'lectric eye / CC BY-SA 4.0",pos="52% 50%")]
# (track, text, flags)
L=[(0,"Coucou mes micropénis !",dict(shout=1,stamp="MICROPÉNIS",instant=1)),
(0,"Fermez vos gueules, bande de branleurs !",dict(shout=1,stamp="BRANLEURS",instant=1)),
(0,"Aujourd'hui, un daron a chié dans le couloir d'un lycée",dict(hook=1)),
(0,"parce que l'équipe de son fils a perdu 42 à 0 !",dict(hook=1,stamp="42 – 0")),
(0,"Restez jusqu'au numéro un, sales trous du cul !",dict(shout=1,stamp="TROUS DU CUL",instant=1)),
(1,"Numéro trois, mes petites couilles molles !",dict(switch=1,shout=1,stamp="COUILLES MOLLES",instant=1)),
(1,"À Nantes, selon la police, un jeune de 23 ans pille des magasins…",{}),
(1,"en live sur TikTok !",dict(hook=1,stamp="● EN LIVE")),
(1,"Il montre même son butin à ses abonnés !",{}),
(1,"La police a juste eu à s'abonner.",dict(stamp="+1 ABONNÉ")),
(1,"Non mais quel génie,",{}),
(1,"bande de tocards !",dict(shout=1,stamp="TOCARDS",instant=1)),
(2,"Numéro deux, les culs plats !",dict(switch=1,shout=1,stamp="CULS PLATS",instant=1)),
(2,"En Caroline du Sud, un papa veut des cartes Pokémon.",dict(stamp="POKÉMON")),
(2,"Une heure du matin, il laisse sa fille de 6 ans dormir dans la file devant le magasin,",dict(stamp="01:00")),
(2,"et il rentre chez lui !",{}),
(2,"Six ans, bande de bouffons.",dict(shout=1,stamp="BOUFFONS",instant=1)),
(2,"La petite va bien, et lui s'est fait arrêter.",dict(stamp="ARRÊTÉ")),
(2,"Pas de cartes pour papa !",{}),
(3,"Numéro un, mes gros nazes !",dict(switch=1,shout=1,stamp="GROS NAZES",instant=1)),
(3,"Michigan. L'équipe de son fils perd 42 à 0.",dict(stamp="42 – 0")),
(3,"Le daron entre dans le lycée adverse,",{}),
(3,"passe devant plusieurs toilettes…",{}),
(3,"et chie en plein couloir !",dict(hook=1)),
(3,"Devant les caméras !",dict(stamp="● REC")),
(3,"Il parle d'urgence médicale, la police n'y croit pas.",dict(stamp="« urgence médicale »")),
(3,"Quel papa supporter !",{}),
(3,"Lequel est le pire ?",dict(outro=1)),
(3,"Dites-le en commentaire, bande de gros cons ! Bisous !",dict(outro=1,shout=1))]
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
