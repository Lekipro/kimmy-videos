"""Musique de fond « dark ambient / loup » synthétisée de zéro (aucun échantillon, aucun modèle) -> music_wolf.wav
Ré mineur, 70 BPM, 80 s : drone grave, pulsation sub, nappes de chœur sombres, tambours lointains,
hurlement de loup synthétique très lointain, montée progressive puis retombée."""
import numpy as np, wave
from scipy import signal

SR = 44100
DUR = 80.0
N = int(SR * DUR)
t = np.arange(N) / SR
rng = np.random.default_rng(13)
BPM = 70
BEAT = 60 / BPM
BAR = 4 * BEAT


def hz(midi):
    return 440.0 * 2 ** ((midi - 69) / 12)


def env_adsr(n, a, r):
    e = np.ones(n)
    na, nr = int(a * SR), int(r * SR)
    e[:na] = np.linspace(0, 1, na) ** 2
    e[-nr:] *= np.linspace(1, 0, nr) ** 1.5
    return e


def lp(x, fc, order=4):
    b, a = signal.butter(order, fc / (SR / 2), "low")
    return signal.lfilter(b, a, x)


def bp(x, f0, q):
    b, a = signal.iirpeak(f0 / (SR / 2), q)
    return signal.lfilter(b, a, x)


def saw(f, ph=0.0):
    p = np.cumsum(np.broadcast_to(f, (N,)) / SR) + ph
    return 2 * (p % 1) - 1


def ramp(t0, t1):
    return np.clip((t - t0) / (t1 - t0), 0, 1)


# intensité globale : calme -> montée (20-55 s) -> retombée
inten = 0.35 + 0.65 * (ramp(18, 52) ** 1.3) * (1 - 0.6 * ramp(62, 76))

# ---------------------------------------------------------------- drone
lfo = 1 + 0.004 * np.sin(2 * np.pi * 0.07 * t)
drone = 0.55 * np.sin(2 * np.pi * np.cumsum(hz(26) * lfo) / SR)          # ré grave
drone += 0.25 * lp(saw(hz(38) * lfo) + saw(hz(38) * 1.003 * lfo, 0.3), 220)
drone += 0.12 * lp(saw(hz(45) * 0.998), 300)                              # quinte
drone *= 0.8 + 0.2 * np.sin(2 * np.pi * 0.05 * t)

# ---------------------------------------------------------------- nappes « chœur »
prog = [[50, 53, 57, 62], [46, 50, 53, 58], [43, 46, 50, 55], [45, 49, 52, 57]]  # Dm Bb Gm A
pad = np.zeros(N)
chord_len = 2 * BAR
k = 0
start = 0.0
while start < DUR:
    n0, n1 = int(start * SR), min(N, int((start + chord_len + 1.5) * SR))
    seg_t = np.arange(n1 - n0) / SR
    seg = np.zeros(n1 - n0)
    for m in prog[k % 4]:
        for det in (-0.006, 0.0, 0.007):
            f = hz(m) * (1 + det) * (1 + 0.003 * np.sin(2 * np.pi * 5.1 * seg_t + m))
            p = np.cumsum(np.full(len(seg_t), 1.0) * f / SR) + rng.random()
            seg += 2 * (p % 1) - 1
    seg = 0.55 * bp(seg, 700, 3) + 0.4 * bp(seg, 1150, 4) + 0.25 * lp(seg, 500)  # formants « ah »
    seg *= env_adsr(len(seg), 2.2, 2.0)
    pad[n0:n1] += seg
    start += chord_len
    k += 1
pad = lp(pad, 3000) * 0.05

# ---------------------------------------------------------------- pulsation sub (battement de cœur)
def hit_sub(at, amp):
    n = int(0.9 * SR)
    tt = np.arange(n) / SR
    f = 38 + 60 * np.exp(-tt * 28)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 4.5)
    i = int(at * SR)
    if i < N:
        j = min(N, i + n)
        sub[i:j] += amp * s[: j - i]

sub = np.zeros(N)
b = 8 * BEAT
while b < DUR - 3:
    a = 0.55 * inten[int(b * SR)]
    hit_sub(b, a)
    hit_sub(b + 0.32, 0.6 * a)
    b += 2 * BEAT

# ---------------------------------------------------------------- tambours de guerre lointains
def tom(at, amp, f0=72):
    n = int(1.2 * SR)
    tt = np.arange(n) / SR
    f = f0 * (1 + 0.6 * np.exp(-tt * 18))
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 5)
    s += 0.25 * lp(rng.standard_normal(n), 900) * np.exp(-tt * 20)
    i = int(at * SR)
    if i < N:
        j = min(N, i + n)
        drums[i:j] += amp * s[: j - i]

drums = np.zeros(N)
bar = int(np.ceil(20 / BAR))
while bar * BAR < 70:
    b0 = bar * BAR
    w = inten[int(b0 * SR)]
    tom(b0, 0.5 * w)
    tom(b0 + 1.5 * BEAT, 0.3 * w, 80)
    tom(b0 + 2 * BEAT, 0.42 * w, 66)
    if bar % 2:
        tom(b0 + 3.5 * BEAT, 0.28 * w, 88)
        tom(b0 + 3.75 * BEAT, 0.22 * w, 88)
    bar += 1
drums = lp(drums, 1400)

# ---------------------------------------------------------------- textures métalliques froides
noise = rng.standard_normal(N)
metal = bp(noise, 3200, 30) + 0.7 * bp(noise, 4700, 40)
metal *= 0.015 * (0.5 + 0.5 * np.sin(2 * np.pi * 0.11 * t)) ** 2 * inten

# ---------------------------------------------------------------- hurlement lointain (synthèse)
def howl(at, dur, amp):
    n = int(dur * SR)
    u = np.linspace(0, 1, n)
    contour = 380 + 330 * np.sin(np.pi * np.clip(u * 1.25, 0, 1)) ** 0.7 - 120 * u ** 3
    vib = 1 + 0.012 * np.sin(2 * np.pi * 5.5 * u * dur) * np.clip(u * 3, 0, 1)
    ph = np.cumsum(contour * vib) / SR
    s = np.sin(2 * np.pi * ph) + 0.35 * np.sin(4 * np.pi * ph) + 0.12 * np.sin(6 * np.pi * ph)
    s += 0.15 * bp(rng.standard_normal(n), 900, 2)
    s *= np.sin(np.pi * u) ** 1.5
    i = int(at * SR)
    j = min(N, i + n)
    wolf[i:j] += amp * s[: j - i]

wolf = np.zeros(N)
howl(11.5, 4.2, 0.10)
howl(44.0, 5.0, 0.13)
howl(47.2, 3.4, 0.07)
wolf = lp(wolf, 2500)

# ---------------------------------------------------------------- réverbération (IR synthétique)
def reverb(x, sec=3.2, wet=0.45, seed=0):
    n = int(sec * SR)
    r = np.random.default_rng(seed)
    ir = r.standard_normal(n) * np.exp(-np.arange(n) / SR * 6.9 / sec)
    ir = lp(ir, 5000)
    ir /= np.sqrt((ir ** 2).sum())
    y = signal.fftconvolve(x, ir)[: len(x)]
    return (1 - wet) * x + wet * y * 3


dry = drone * 0.5 + sub * 0.9
mid = pad + metal
L = dry + reverb(mid, 3.5, 0.55, 1) + reverb(drums, 2.4, 0.5, 2) * 0.9 + reverb(wolf, 4.5, 0.75, 3)
R = dry + reverb(mid, 3.5, 0.55, 4) + reverb(drums, 2.4, 0.5, 5) * 0.9 + reverb(wolf, 4.5, 0.75, 6)

fade = np.clip(t / 3.0, 0, 1) ** 2 * np.clip((DUR - t) / 4.0, 0, 1)
st = np.stack([L, R], 1) * fade[:, None]
st = np.stack([lp(st[:, 0], 11000, 6), lp(st[:, 1], 11000, 6)], 1)
st -= st.mean(0)
st *= 10 ** (-1.5 / 20) / np.abs(st).max()
pcm = (st * 32767).astype(np.int16)
with wave.open("music_wolf.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print("ok", DUR)
