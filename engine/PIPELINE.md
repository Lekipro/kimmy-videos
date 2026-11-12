# Kimmy — fabrication et publication d'une vidéo

Chaîne complète utilisée par la tâche quotidienne. Les règles éditoriales et le personnage sont dans le doc du projet Grezil `claude/presentatrice-kimmy.md` : le lire avant d'écrire.

## 0. Préparation

```bash
git clone --depth 1 https://github.com/Lekipro/kimmy-videos /home/claude/kimmy-videos   # après add_repo(owner=Lekipro, repo=kimmy-videos, access=push)
pip install playwright --break-system-packages -q 2>/dev/null; python3 -c "import playwright"
W=/home/claude/kimmy-videos/engine; DAY=$(date +%F); WORK=/home/claude/run-$DAY; mkdir -p $WORK/out
```
Navigateur pour le rendu : `/usr/bin/google-chrome` (déjà présent dans le workspace).

## 1. Trois infos débiles (skill `gresil-infos-debiles`)

- Le niveau : un adulte fait un truc complètement con, ça se dit en une phrase, c'est vrai et sourcé (2 sources), moins de 7 jours.
- Pas de drame (mort, blessé grave, violence sexuelle), pas d'enfant ou de victime moqué, pas de nom de personne privée, « selon la police » pour un suspect.
- Ne jamais reprendre une info déjà traitée : voir `historique.md` dans ce dépôt.
- Classer de la moins folle (n° 3) à la pire (n° 1).

## 2. Images

Une vraie photo par info, Wikimedia Commons uniquement (API `commons.wikimedia.org/w/api.php`, User-Agent `GresilVideo/1.0 (personal video project)`, une requête toutes les ~6 s sinon 429). Le lieu réel (lycée, ville, magasin), « Photo d'illustration » si ce n'est pas le lieu exact. Noter auteur et licence pour le crédit.

Pour chaque image `X.jpg` dans `engine/app/` : version 1600 px de large `X.jpg`, et fond flouté `X_bg.jpg` (recadrage 9:16, 270×480, flou gaussien 22, saturation ×1.5, luminosité ×0.55, remis en 1080×1920). L'intro utilise `kimmy.jpg` (déjà présent).

## 3. Script et lignes

Éditer `engine/app/build_data.py` :
- `T` : 4 pistes. Piste 0 = intro Kimmy (inchangée). Pistes 1-3 = infos n° 3, 2, 1 avec `title` (2 mots), `place`, `img`, `credit`, `pos`.
- `L` : les lignes affichées `(piste, texte, flags)`. Flags : `shout` (rouge, tremblement), `stamp` (étiquette rouge), `instant` (étiquette dès le début de la ligne, pour les insultes), `hook`, `switch`, `outro` (les 2 dernières lignes).
- Le texte des lignes doit suivre exactement ce que dit la voix, chiffres écrits en chiffres.

Voix : un morceau par piste (donc 4 morceaux), chacun ≤ 500 octets UTF-8 sur le forfait gratuit. Les nombres sont écrits en lettres dans le texte envoyé à la voix.

## 4. Voix (Fish Audio)

- Vérifier d'abord `get_credit_balance`. Il faut environ 1 400 crédits. S'il en manque : ne rien publier, prévenir Duca.
- `text_to_speech` × 4, `voice_id = bdfbdcb27253419ba7e0746af7a154f8` (Clémence), `model = drama-3`, balises en anglais : `[screaming with excitement, very fast]` pour l'ouverture, `[hyper excited, fast]`, `[laughing]`, `[whispering]`, `[shouting]`.
- Ne jamais relancer une génération pour un même texte (ça recharge des crédits) : retélécharger `audio_url`.

```bash
cd $WORK; i=0; for URL in <4 audio_url>; do i=$((i+1)); curl -sS -o p$i.mp3 "$URL"; ffmpeg -y -loglevel error -i p$i.mp3 -af "atempo=1.15,aresample=48000" -ac 1 f$i.wav; done
ffmpeg -y -loglevel error -f lavfi -i anullsrc=r=48000:cl=mono -t 0.35 gap.wav
printf "file f1.wav\nfile gap.wav\nfile f2.wav\nfile gap.wav\nfile f3.wav\nfile gap.wav\nfile f4.wav\n" > l.txt
ffmpeg -y -loglevel error -f concat -i l.txt -c pcm_s16le voice.wav
python3 $W/align.py $W/app/build_data.py          # -> timings.json
```
Durée cible : 60 à 70 s (au-dessus de 60 s pour la rémunération TikTok).

## 5. Rendu

```bash
cd $W/app && python3 build_data.py $WORK/timings.json && python3 ../env.py $WORK/voice.wav data.json
export OUT_DIR=$WORK/out
python3 shoot.py stills 0.5 2.0 20 45        # regarder ces images avant le rendu complet
TOTAL=$(python3 -c "import json;print(json.load(open('data.json'))['total'])"); HALF=$(python3 -c "print(round($TOTAL/2,2))")
(python3 shoot.py range 0 $HALF A & python3 shoot.py range $HALF $TOTAL B & wait)
cd $WORK/out && printf "file A.mp4\nfile B.mp4\n" > p.txt && ffmpeg -y -loglevel error -f concat -i p.txt -c copy muet.mp4
ffmpeg -y -loglevel error -i $WORK/voice.wav -af "apad=pad_dur=2,loudnorm=I=-14:TP=-1.5:LRA=11" -ar 48000 voix.wav
python3 $W/sfx_mix.py $W/app/data.json voix.wav mix.wav
ffmpeg -y -loglevel error -i muet.mp4 -i mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart final.mp4
ffmpeg -y -loglevel error -ss 1.0 -i final.mp4 -frames:v 1 -q:v 2 cover.jpg
```
Commande de rendu longue : timeout 600 s, lancer les deux moitiés en parallèle.

## 6. Mise en ligne du fichier

```bash
cd /home/claude/kimmy-videos && cp $WORK/out/final.mp4 videos/$DAY-kimmy.mp4 && cp $WORK/out/cover.jpg videos/$DAY-kimmy.jpg
git add videos historique.md && git -c user.name=Claude -c user.email=noreply@anthropic.com commit -qm "Kimmy $DAY" && git -c push.negotiate=true push origin HEAD
```
Lien public : `https://raw.githubusercontent.com/Lekipro/kimmy-videos/main/videos/$DAY-kimmy.mp4` (vérifier avec `curl -sI`, code 200). Ne pas remettre en ligne `engine/app/data.json` ni les images du jour.

## 7. Publication (Metricool)

`createScheduledPost`, blogId `7712487`, fuseau `Europe/Rome`, 18:00 le jour même :
- `providers` : `tiktok` et `instagram`
- `media` : le lien raw de la vidéo ; `videoThumbnailUrl` : le lien raw de la couverture
- `text` : 1 phrase d'accroche sur l'info n° 1, « Lequel est le pire ? Dites-le en commentaire. », les sources (noms des médias), 5 hashtags (#insolite #infos #humour #faitsdivers #top3)
- `tiktokData` : `title` (obligatoire, ≤ 90 caractères), `privacyOption: PUBLIC_TO_EVERYONE`, `isAigc: true`
- `instagramData` : `type: REEL`, `showReelOnFeed: true`, `isAiGenerated: true`
- `autoPublish: true`

Après 18:00, vérifier avec `getScheduledPosts` que les deux réseaux sont `PUBLISHED`.
