"""Moteur de rendu v2 (19/11/2026) : titre court seul au début, pas de sous-titres, pas de mots dans les scènes.\nMoteur de rendu « animation minimaliste » (fond noir, traits blancs lumineux, sous-titres mot à mot).
Usage :
  python3 hp_engine.py still  scenes.py phrases.json DUREE t1 t2 ...   -> still_XX.jpg
  python3 hp_engine.py video  scenes.py phrases.json DUREE part nparts out.mp4
scenes.py fait `from hp_engine import *` et définit SCENES = [(debut, fin, fonction), ...] ; fonction(ctx, t_local, duree).
"""
import cairo, math, json, random, sys, subprocess, importlib.util, os
import numpy as np, cv2

W, H = 1080, 1920
FPS = 30
DUR = 60.0  # set by load()
CX, CY = 540, 1100
XF = 0.35  # crossfade
SANS = "Montserrat ExtraBold"
SERIF = "Playfair Display"

PHR = []   # set by load()
SCENES = []  # set by load()

# ---------------------------------------------------------------- helpers
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))

def ease(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)

def eout(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3

def A(t, a, b):
    return ease((t - a) / (b - a)) if b > a else float(t >= a)

def lerp(a, b, k):
    return a + (b - a) * k

def white(ctx, a=1.0):
    ctx.set_source_rgba(1, 1, 1, a)

def polyline(ctx, pts, prog=1.0, width=3.0, a=1.0, dash=None):
    if prog <= 0 or a <= 0:
        return
    segs = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    total = sum(segs)
    left = total * clamp(prog)
    ctx.new_path()
    ctx.move_to(*pts[0])
    for i, L in enumerate(segs):
        if left >= L:
            ctx.line_to(*pts[i + 1]); left -= L
        else:
            k = left / L if L else 0
            ctx.line_to(lerp(pts[i][0], pts[i + 1][0], k), lerp(pts[i][1], pts[i + 1][1], k))
            break
    ctx.set_line_width(width)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    if dash:
        ctx.set_dash(dash)
    white(ctx, a)
    ctx.stroke()
    ctx.set_dash([])

def curve_pts(f, x0, x1, n=80):
    return [(lerp(x0, x1, i / n), f(i / n)) for i in range(n + 1)]

def person(ctx, x, y, s=1.0, a=1.0, dy=0.0):
    if a <= 0:
        return
    y = y + dy
    white(ctx, a)
    ctx.new_path()
    ctx.arc(x, y - 58 * s, 12 * s, 0, 2 * math.pi)
    ctx.fill()
    r = 15 * s
    l, rr, top, bot = x - 20 * s, x + 20 * s, y - 40 * s, y
    ctx.new_path()
    ctx.move_to(l, bot)
    ctx.line_to(l, top + r)
    ctx.arc(l + r, top + r, r, math.pi, 1.5 * math.pi)
    ctx.arc(rr - r, top + r, r, 1.5 * math.pi, 2 * math.pi)
    ctx.line_to(rr, bot)
    ctx.close_path()
    ctx.fill()

def pot_path(ctx):
    ctx.new_path()
    ctx.move_to(-12, 0); ctx.line_to(12, 0)
    ctx.curve_to(20, -4, 24, -16, 22, -26)
    ctx.curve_to(20, -38, 10, -42, 9, -50)
    ctx.line_to(13, -58); ctx.line_to(-13, -58); ctx.line_to(-9, -50)
    ctx.curve_to(-10, -42, -20, -38, -22, -26)
    ctx.curve_to(-24, -16, -20, -4, -12, 0)
    ctx.close_path()

def pot(ctx, x, y, s=1.0, a=1.0, fill=True, broken=0.0, lw=2.5, rot=0.0):
    if a <= 0 or s <= 0:
        return
    zig = [(2, -66), (-4, -46), (5, -31), (-3, -16), (3, 4)]
    def body(part):
        ctx.save()
        if part:
            side = -1 if part == "L" else 1
            ctx.translate(side * 5 * broken, 2 * broken)
            ctx.rotate(side * 0.16 * broken)
            ctx.new_path()
            ctx.move_to(side * 40, -70)
            for p in zig:
                ctx.line_to(*p)
            ctx.line_to(side * 40, 10)
            ctx.close_path()
            ctx.clip()
        pot_path(ctx)
        white(ctx, a)
        if fill:
            ctx.fill()
        else:
            ctx.set_line_width(lw / s)
            ctx.stroke()
        ctx.restore()
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    ctx.scale(s, s)
    if broken > 0:
        body("L"); body("R")
    else:
        body(None)
    ctx.restore()

def checkbox(ctx, x, y, size=26, check=0.0, a=1.0, lw=3):
    white(ctx, a)
    ctx.set_line_width(lw)
    ctx.new_path()
    r = 5
    h = size / 2
    ctx.move_to(x - h + r, y - h)
    ctx.arc(x + h - r, y - h + r, r, -math.pi / 2, 0)
    ctx.arc(x + h - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x - h + r, y + h - r, r, math.pi / 2, math.pi)
    ctx.arc(x - h + r, y - h + r, r, math.pi, 1.5 * math.pi)
    ctx.close_path()
    if check > 0:
        ctx.fill()
        ctx.set_source_rgba(0, 0, 0, a)
        polyline_dark(ctx, [(x - h * 0.5, y), (x - h * 0.1, y + h * 0.42), (x + h * 0.55, y - h * 0.45)], check, lw)
    else:
        ctx.stroke()

def polyline_dark(ctx, pts, prog, w):
    segs = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    left = sum(segs) * clamp(prog)
    ctx.new_path(); ctx.move_to(*pts[0])
    for i, L in enumerate(segs):
        if left >= L:
            ctx.line_to(*pts[i + 1]); left -= L
        else:
            k = left / L
            ctx.line_to(lerp(pts[i][0], pts[i + 1][0], k), lerp(pts[i][1], pts[i + 1][1], k)); break
    ctx.set_line_width(w); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke()

SCENE_TEXT = [False]  # style v2 : aucun mot dans les scènes, seulement des chiffres

def label(ctx, txt, x, y, size=17, a=0.85, spacing=4, font=SANS, slant=cairo.FONT_SLANT_NORMAL, center=True):
    if a <= 0:
        return
    if not SCENE_TEXT[0] and not txt.replace(" ", "").isdigit():
        return
    ctx.select_font_face(font, slant, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(size)
    widths = [ctx.text_extents(c).x_advance for c in txt]
    total = sum(widths) + spacing * (len(txt) - 1)
    cx = x - total / 2 if center else x
    white(ctx, a)
    for c, w in zip(txt, widths):
        ctx.move_to(cx, y)
        ctx.show_text(c)
        cx += w + spacing

def spinner(ctx, x, y, t, r=15, a=1.0):
    ang = t * 5
    ctx.new_path()
    ctx.arc(x, y, r, ang, ang + 4.4)
    ctx.set_line_width(3.5)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    white(ctx, a)
    ctx.stroke()

def bin_box(ctx, x, y, w, h, a=1.0, prog=1.0):
    polyline(ctx, [(x - w / 2, y - h), (x - w / 2, y), (x + w / 2, y), (x + w / 2, y - h)], prog, 4, a)

def glowdot(ctx, x, y, r, a):
    g = cairo.RadialGradient(x, y, 0, x, y, r)
    g.add_color_stop_rgba(0, 1, 1, 1, a)
    g.add_color_stop_rgba(1, 1, 1, 1, 0)
    ctx.set_source(g)
    ctx.arc(x, y, r, 0, 2 * math.pi)
    ctx.fill()

def sparkle(ctx, x, y, r, a):
    white(ctx, a)
    ctx.set_line_width(2.5)
    ctx.new_path()
    ctx.move_to(x - r, y); ctx.line_to(x + r, y)
    ctx.move_to(x, y - r); ctx.line_to(x, y + r)
    ctx.stroke()

rng = random.Random(7)

# ---------------------------------------------------------------- captions
def caption_layout(ctx, phrase):
    items = []
    for w in phrase["words"]:
        it = w["t"].startswith("*")
        txt = w["t"].lstrip("*")
        if it:
            ctx.select_font_face(SERIF, cairo.FONT_SLANT_ITALIC, cairo.FONT_WEIGHT_NORMAL); ctx.set_font_size(66)
        else:
            txt = txt.upper()
            ctx.select_font_face(SANS, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL); ctx.set_font_size(54)
        items.append(dict(txt=txt, it=it, w=ctx.text_extents(txt).x_advance, s=w["s"]))
    space, maxw = 18, 880
    lines, cur, cw = [], [], 0
    for it in items:
        need = it["w"] + (space if cur else 0)
        if cur and cw + need > maxw:
            lines.append((cur, cw)); cur, cw = [], 0; need = it["w"]
        cur.append(it); cw += need
    if cur:
        lines.append((cur, cw))
    out = []
    y0 = 560 - (len(lines) - 1) * 36
    for li, (ln, lw) in enumerate(lines):
        x = W / 2 - lw / 2
        for it in ln:
            out.append(dict(it, x=x, y=y0 + li * 74)); x += it["w"] + space
    return out

HOOK = dict(end=0.0, lines=[])

def draw_hook(ctx, T):
    """Titre court, seul, qui apparaît calmement puis reste en haut quelques secondes."""
    if not HOOK.get("title"):
        return
    a0, a1, end = HOOK.get("t_in", 0.15), HOOK.get("t_full", 0.9), HOOK.get("end", 3.5)
    a = A(T, a0, a1) * (1 - A(T, end - 0.4, end))
    if a <= 0:
        return
    rows = HOOK["title"]
    k = 1.0 + 0.03 * clamp(T / end)
    y0 = HOOK.get("y", 640)
    for li, words in enumerate(rows):
        items = []
        for w in words.split():
            it = w.startswith("*"); txt = w.lstrip("*")
            if it:
                ctx.select_font_face(SERIF, cairo.FONT_SLANT_ITALIC, cairo.FONT_WEIGHT_NORMAL); ctx.set_font_size(112 * k)
            else:
                txt = txt.upper(); ctx.select_font_face(SANS, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL); ctx.set_font_size(92 * k)
            items.append((txt, it, ctx.text_extents(txt).x_advance))
        sp = 26 * k
        tw = sum(i[2] for i in items) + sp * (len(items) - 1)
        x = W / 2 - tw / 2
        y = y0 + li * 120 * k + (1 - a) * 18
        for txt, it, wd in items:
            if it:
                ctx.select_font_face(SERIF, cairo.FONT_SLANT_ITALIC, cairo.FONT_WEIGHT_NORMAL); ctx.set_font_size(112 * k)
            else:
                ctx.select_font_face(SANS, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL); ctx.set_font_size(92 * k)
            white(ctx, a)
            ctx.move_to(x, y); ctx.show_text(txt)
            x += wd + sp

def draw_captions(ctx, T):
    draw_hook(ctx, T)
    if not HOOK.get("captions", True):
        return
    for i, p in enumerate(PHR):
        nxt = PHR[i + 1]["s"] if i + 1 < len(PHR) else DUR - 0.8
        start, end = p["s"] - 0.06, min(nxt - 0.04, p["e"] + 1.0) if i + 1 < len(PHR) else DUR - 0.8
        if not (start <= T <= end):
            continue
        fo = 1 - A(T, end - 0.12, end)
        for it in caption_layout(ctx, p):
            a = eout((T - it["s"] + 0.04) / 0.16) * fo
            if a <= 0:
                continue
            dy = (1 - a) * 10
            if it["it"]:
                ctx.select_font_face(SERIF, cairo.FONT_SLANT_ITALIC, cairo.FONT_WEIGHT_NORMAL); ctx.set_font_size(66)
            else:
                ctx.select_font_face(SANS, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL); ctx.set_font_size(54)
            white(ctx, a)
            ctx.move_to(it["x"], it["y"] + dy)
            ctx.show_text(it["txt"])

# ---------------------------------------------------------------- frame
STARS = [(rng.uniform(0, W), rng.uniform(250, 1650), rng.uniform(0.8, 2.0), rng.uniform(0.08, 0.35), rng.uniform(0, 6)) for _ in range(140)]
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
VIG = np.clip(1.15 - 0.75 * (((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - CY) / (H * 0.55)) ** 2), 0.25, 1.0)[..., None]
BG = np.array([7, 8, 9], np.float32) + (10 * np.exp(-(((xx - W / 2) / 520) ** 2 + ((yy - CY) / 520) ** 2)))[..., None]

def to_np(surf):
    W, H = surf.get_width(), surf.get_height()
    buf = np.ndarray((H, W, 4), np.uint8, surf.get_data())
    return buf[..., :3].astype(np.float32)

def glow(img, k1=0.9, k2=0.55):
    H, W = img.shape[:2]
    small = cv2.resize(img, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
    g1 = cv2.GaussianBlur(small, (0, 0), 3)
    g2 = cv2.GaussianBlur(small, (0, 0), 12)
    g = cv2.resize(g1 * k1 + g2 * k2, (W, H), interpolation=cv2.INTER_LINEAR)
    return img + g

def render(T, grain_rng):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf)
    ctx.set_antialias(cairo.ANTIALIAS_BEST)
    for (x, y, r, a, ph) in STARS:
        white(ctx, a * (0.6 + 0.4 * math.sin(T * 0.8 + ph)))
        ctx.arc(x, y - T * 2.0, r, 0, 2 * math.pi); ctx.fill()
    for (s, e, fn) in SCENES:
        if s - XF / 2 <= T <= e + XF / 2:
            a = A(T, s - XF / 2, s + XF / 2) if s > 0 else 1.0
            if e < DUR:
                a *= 1 - A(T, e - XF / 2, e + XF / 2)
            if a <= 0:
                continue
            lt = T - s
            z = 1.1 + 0.035 * (lt / (e - s))
            ctx.save()
            ctx.translate(CX, CY); ctx.scale(z, z); ctx.translate(-CX, -CY)
            ctx.push_group()
            fn(ctx, lt, e - s)
            ctx.pop_group_to_source()
            ctx.paint_with_alpha(a)
            ctx.restore()
    scene = glow(to_np(surf))
    cs = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    cc = cairo.Context(cs)
    draw_captions(cc, T)
    cap = to_np(cs)
    cap = cap + 0.35 * cv2.resize(cv2.GaussianBlur(cv2.resize(cap, (W // 4, H // 4)), (0, 0), 4), (W, H))
    img = BG + scene + cap
    img *= VIG
    fade = A(T, 0, 0.25) * (1 - A(T, DUR - 0.7, DUR))
    img *= fade
    img += grain_rng.normal(0, 3.0, (H // 2, W // 2, 1)).repeat(2, 0).repeat(2, 1)
    # BGR(A) from cairo -> RGB for ffmpeg
    return np.clip(img[..., ::-1], 0, 255).astype(np.uint8)


def load(scenes_path, phrases_path, dur):
    global PHR, SCENES, DUR
    DUR = float(dur)
    PHR[:] = json.load(open(phrases_path))
    spec = importlib.util.spec_from_file_location("scenes_mod", scenes_path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["scenes_mod"] = mod
    spec.loader.exec_module(mod)
    SCENES[:] = mod.SCENES
    if hasattr(mod, "HOOK"):
        HOOK.update(mod.HOOK)
    SCENE_TEXT[0] = bool(HOOK.get("scene_text", False))

if __name__ == "__main__":
    mode, scenes_path, phrases_path, dur = sys.argv[1:5]
    load(scenes_path, phrases_path, dur)
    if mode == "still":
        for T in map(float, sys.argv[5:]):
            cv2.imwrite(f"still_{T:05.2f}.jpg", render(T, np.random.default_rng(0))[..., ::-1], [cv2.IMWRITE_JPEG_QUALITY, 85])
    else:
        part, nparts, out = int(sys.argv[5]), int(sys.argv[6]), sys.argv[7]
        N = int(DUR * FPS)
        a, b = part * N // nparts, (part + 1) * N // nparts
        p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                              "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
        g = np.random.default_rng(part)
        for f in range(a, b):
            p.stdin.write(render(f / FPS, g).tobytes())
        p.stdin.close(); p.wait()
