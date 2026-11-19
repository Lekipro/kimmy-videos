"""Audio de la chaîne « animation minimaliste ».
  python3 hp_audio.py voice OUT.wav p1.mp3 p2.mp3 ...       assemble la voix (float, pause 0,45 s) -> affiche la durée
  python3 hp_audio.py align script.txt voice.wav phrases.json   timings mot à mot (faster-whisper) calés sur le script
  python3 hp_audio.py mix voice.wav music.wav DUREE mix.wav     musique sous la voix (ducking) + niveau final
  python3 hp_audio.py check fichier.wav                          contrôle grésillement / niveau

IMPORTANT (bug du 14/11) : ne JAMAIS assembler la voix avec un filtre concat ffmpeg + anullsrc :
anullsrc sort en 8 bits (u8) et tout le son est converti en 8 bits -> grésillement. Tout se fait ici en float.
"""
import sys, json, re, subprocess, unicodedata, difflib, wave
import numpy as np

SR = 44100

def loadf(p, sr=SR):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-f", "f32le", "-ac", "1", "-ar", str(sr), "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).copy()

def save16(path, x, sr=SR, ch=1):
    pcm = (np.clip(x, -1, 1) * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(ch); w.setsampwidth(2); w.setframerate(sr); w.writeframes(pcm.tobytes())

def voice(out, parts):
    gap = np.zeros(int(0.45 * SR), np.float32)
    segs = []
    for i, p in enumerate(parts):
        if i: segs.append(gap)
        segs.append(loadf(p))
    v = np.concatenate(segs)
    v *= 10 ** (-1.5 / 20) / (np.abs(v).max() + 1e-9)   # simple gain, crête à -1,5 dBFS
    save16(out, v)
    print(f"{len(v) / SR:.2f}")

def norm(w):
    w = w.lower().replace("*", "")
    w = "".join(c for c in unicodedata.normalize("NFD", w) if unicodedata.category(c) != "Mn")
    w = re.sub(r"[^a-z0-9'-]", "", w)
    if w.isdigit():
        try:
            from num2words import num2words
            w = norm(num2words(int(w), lang="fr"))
        except Exception:
            pass
    return w

def align(script, wav, out):
    from faster_whisper import WhisperModel
    lines = [l.strip() for l in open(script, encoding="utf-8") if l.strip()]
    a = loadf(wav, 16000)
    m = WhisperModel("small", device="cpu", compute_type="int8")
    segs, _ = m.transcribe(a, language="fr", word_timestamps=True)
    W = [[w.word.strip(), w.start, w.end] for s in segs for w in s.words]
    print("TRANSCRIPTION :", " ".join(w[0] for w in W))
    mine = []
    for pi, p in enumerate(lines):
        for tok in p.split():
            if norm(tok) == "":
                if mine: mine[-1]["txt"] += " " + tok
                continue
            mine.append(dict(p=pi, txt=tok, n=norm(tok)))
    wn = [norm(w[0]) for w in W]
    sm = difflib.SequenceMatcher(None, [m_["n"] for m_ in mine], wn, autojunk=False)
    for a_, b_, size in sm.get_matching_blocks():
        for k in range(size):
            mine[a_ + k]["s"] = W[b_ + k][1]; mine[a_ + k]["e"] = W[b_ + k][2]
    miss = 0
    for i, m_ in enumerate(mine):
        if "s" not in m_:
            miss += 1
            prev = next((mine[j]["e"] for j in range(i - 1, -1, -1) if "s" in mine[j]), 0)
            nxt = next((mine[j]["s"] for j in range(i + 1, len(mine)) if "s" in mine[j]), prev + 0.3)
            m_["s"], m_["e"] = prev, nxt
    phr = []
    for pi in range(len(lines)):
        ws = [dict(t=m_["txt"], s=round(m_["s"], 2), e=round(m_["e"], 2)) for m_ in mine if m_["p"] == pi]
        phr.append(dict(words=ws, s=ws[0]["s"], e=ws[-1]["e"]))
    json.dump(phr, open(out, "w"), ensure_ascii=False, indent=0)
    for p in phr:
        print(f"{p['s']:6.2f}-{p['e']:6.2f}", " ".join(w["t"] for w in p["words"]))
    print(f"mots non retrouvés : {miss}/{len(mine)}")

def mix(vwav, mwav, dur, out):
    dur = float(dur)
    flt = (f"[0]aformat=sample_fmts=fltp:sample_rates=44100:channel_layouts=stereo,apad=whole_dur={dur},asplit=2[v][sc];"
           f"[1]aformat=sample_fmts=fltp:sample_rates=44100:channel_layouts=stereo,atrim=0:{dur},volume=-12dB,"
           f"afade=t=in:d=0.6,afade=t=out:st={dur - 1.7}:d=1.7[m];"
           "[m][sc]sidechaincompress=threshold=0.03:ratio=3:attack=30:release=450:makeup=1[md];"
           "[v][md]amix=inputs=2:normalize=0:duration=first,volume=5.5dB,"
           "alimiter=limit=0.84:attack=5:release=60:level=disabled,aformat=sample_fmts=fltp")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vwav, "-i", mwav, "-filter_complex", flt, "-t", str(dur), "-c:a", "pcm_f32le", out], check=True)
    check(out)

def check(p):
    v = loadf(p)
    hop = 1024; n = len(v) // hop
    fr = v[: n * hop].reshape(n, hop)
    sp = np.abs(np.fft.rfft(fr * np.hanning(hop), axis=1)) + 1e-9
    f = np.fft.rfftfreq(hop, 1 / SR)
    rms = 20 * np.log10(np.sqrt((fr ** 2).mean(1)) + 1e-9)
    loud = rms > np.percentile(rms, 60)
    top = 20 * np.log10(sp[loud][:, f > 16000].mean()) - 20 * np.log10(sp[loud][:, (f > 200) & (f < 3000)].mean())
    lufs = subprocess.run(["ffmpeg", "-nostats", "-i", p, "-af", "loudnorm=print_format=summary", "-f", "null", "-"], capture_output=True, text=True).stderr
    li = re.search(r"Input Integrated:\s+(-?[\d.]+)", lufs); tp = re.search(r"Input True Peak:\s+(-?[\d.+]+)", lufs)
    ok = top < -55
    print(f"aigus >16 kHz : {top:.1f} dB ({'OK' if ok else 'GRÉSILLEMENT PROBABLE (attendu < -55 dB)'}) | "
          f"loudness {li.group(1) if li else '?'} LUFS | crête {tp.group(1) if tp else '?'} dBTP")
    return ok

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "voice": voice(sys.argv[2], sys.argv[3:])
    elif cmd == "align": align(*sys.argv[2:5])
    elif cmd == "mix": mix(*sys.argv[2:6])
    elif cmd == "check": sys.exit(0 if check(sys.argv[2]) else 1)
