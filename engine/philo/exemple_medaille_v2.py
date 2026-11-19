"""EXEMPLE STYLE V2+V3 — vidéo du 19/11 « Mieux vaut finir 3e » (médaille d'argent, 69,5 s). Personnages : person(..., pose="sad|joy|look_up|look_down|walk|think|point", look=-1..1, k=0..1).
Titre court via HOOK (en bas du fichier), animations qui démarrent au drop (1,5 s), aucun mot dans les scènes."""
from hp_engine_v2 import *

DURV = 69.54
BASE = 1400
POD = {1: (540, 250), 2: (330, 175), 3: (750, 115)}
PW = 210


def series_tags(ctx, t):
    # libellé de série en haut pendant l'accroche, mot-clé déjà dans l'accroche
    return


def podium(ctx, prog=1.0, a=1.0, nums=1.0, cx_shift=0, scale=1.0, base=BASE):
    for k in (2, 1, 3):
        x, h = POD[k]
        x = 540 + (x - 540) * scale + cx_shift
        w = PW * scale
        h = h * scale
        p = A(prog, 0.05 * k, 0.6 + 0.12 * k)
        polyline(ctx, [(x - w / 2, base), (x - w / 2, base - h), (x + w / 2, base - h), (x + w / 2, base)], p, 3.5, a)
        label(ctx, str(k), x, base - h / 2 + 14 * scale, 34 * scale, 0.8 * a * nums, spacing=0)
    polyline(ctx, [(540 - 1.7 * PW * scale + cx_shift, base), (540 + 1.7 * PW * scale + cx_shift, base)], prog, 3, 0.8 * a)


def top_of(k, scale=1.0, cx_shift=0, base=BASE):
    x, h = POD[k]
    return 540 + (x - 540) * scale + cx_shift, base - h * scale


def medal(ctx, x, y, r, a=1.0, fill=0.0, ribbon=True):
    if a <= 0:
        return
    white(ctx, a)
    if ribbon:
        polyline(ctx, [(x - r * 0.7, y - r * 2.2), (x, y - r * 0.9), (x + r * 0.7, y - r * 2.2)], 1, 2.2, 0.8 * a)
    ctx.new_path(); ctx.arc(x, y, r, 0, 2 * math.pi)
    ctx.set_line_width(3); ctx.stroke()
    if fill > 0:
        white(ctx, a * fill)
        ctx.new_path(); ctx.arc(x, y, r * 0.72, 0, 2 * math.pi); ctx.fill()


def athlete(ctx, x, y, s=1.0, a=1.0, mood=0.0, medal_a=0.0, glow=0.0, look=0.0, pose=None):
    """mood > 0 : joie (bras levés, petits sauts) ; mood < 0 : tristesse (tête basse, épaules tombantes)."""
    if a <= 0:
        return
    if pose is None:
        pose, k = ("joy", mood) if mood > 0 else (("sad", -mood) if mood < 0 else ("stand", 0))
    else:
        k = 1.0
    person(ctx, x, y, s, a, pose=pose, look=look, k=k)
    if medal_a > 0:
        medal(ctx, x, y - 22 * s, 7 * s, medal_a, 1.0, ribbon=False)
    if glow > 0:
        glowdot(ctx, x, y - 40 * s, 120 * s, 0.35 * glow)


def bubble(ctx, x, y, w, h, a, tail=(0, 0)):
    if a <= 0:
        return
    white(ctx, a); ctx.set_line_width(2.5)
    r = 22
    ctx.new_path()
    ctx.move_to(x - w / 2 + r, y - h / 2)
    ctx.arc(x + w / 2 - r, y - h / 2 + r, r, -math.pi / 2, 0)
    ctx.arc(x + w / 2 - r, y + h / 2 - r, r, 0, math.pi / 2)
    ctx.arc(x - w / 2 + r, y + h / 2 - r, r, math.pi / 2, math.pi)
    ctx.arc(x - w / 2 + r, y - h / 2 + r, r, math.pi, 1.5 * math.pi)
    ctx.close_path(); ctx.stroke()
    tx, ty = tail
    for k, rr in enumerate([7, 4.5]):
        white(ctx, a)
        ctx.new_path(); ctx.arc(lerp(x, tx, 0.55 + 0.25 * k), lerp(y + h / 2, ty, 0.55 + 0.25 * k), rr, 0, 2 * math.pi); ctx.fill()


def arrow(ctx, p0, p1, prog, w=3, a=1.0, dash=None, head=18):
    polyline(ctx, [p0, p1], prog, w, a, dash)
    if prog >= 0.98:
        ang = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
        hx, hy = p1
        polyline(ctx, [(hx - head * math.cos(ang - 0.45), hy - head * math.sin(ang - 0.45)), (hx, hy),
                       (hx - head * math.cos(ang + 0.45), hy - head * math.sin(ang + 0.45))], 1, w, a)


def face(ctx, x, y, r, mood, a=1.0):
    if a <= 0:
        return
    white(ctx, a); ctx.set_line_width(3)
    ctx.new_path(); ctx.arc(x, y, r, 0, 2 * math.pi); ctx.stroke()
    for side in (-1, 1):
        ctx.new_path(); ctx.arc(x + side * r * 0.35, y - r * 0.2, r * 0.08, 0, 2 * math.pi); ctx.fill()
    my = y + r * 0.35
    c = curve_pts(lambda u: my - mood * r * 0.3 * (1 - (2 * u - 1) ** 2) * -1, x - r * 0.4, x + r * 0.4, 20)
    polyline(ctx, c, 1, 3, a)


# ------------------------------------------------------------------ scènes
def s1(ctx, t, d):  # accroche : le podium, l'argent triste, le bronze heureux
    series_tags(ctx, t)
    t = (t - 1.5) * 1.6
    podium(ctx, A(t, 0, 0.7), 1, A(t, 0.3, 0.7))
    x1, y1 = top_of(1); x2, y2 = top_of(2); x3, y3 = top_of(3)
    athlete(ctx, x1, y1 - 3, 1.2, A(t, 0.2, 0.6), 0.6 * A(t, 0.5, 1.0), A(t, 0.4, 0.8))
    athlete(ctx, x2, y2 - 3, 1.2, A(t, 0.25, 0.65), -A(t, 0.9, 1.6), A(t, 0.4, 0.8))
    athlete(ctx, x3, y3 - 3, 1.2, A(t, 0.3, 0.7), A(t, 1.6, 2.3), A(t, 0.4, 0.8), A(t, 2.0, 2.8))
    label(ctx, "ARGENT", x2, BASE + 50, 16, 0.75 * A(t, 1.0, 1.4))
    label(ctx, "BRONZE", x3, BASE + 50, 16, 0.75 * A(t, 1.9, 2.3))


def s2(ctx, t, d):  # deuxième > troisième
    ctx.select_font_face(SANS, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    for i, (txt, x) in enumerate([("2", 330), (">", 540), ("3", 750)]):
        a = A(t, 0.2 + 0.35 * i, 0.6 + 0.35 * i)
        ctx.set_font_size(200 if txt != ">" else 150)
        e = ctx.text_extents(txt)
        white(ctx, a * (0.55 if txt == ">" else 1))
        ctx.move_to(x - e.x_advance / 2, 1200 - (0 if txt != ">" else 15))
        ctx.show_text(txt)
    label(ctx, "ARGENT", 330, 1270, 16, 0.75 * A(t, 0.6, 1.0))
    label(ctx, "BRONZE", 750, 1270, 16, 0.75 * A(t, 1.2, 1.6))
    # case cochée : « logique »
    checkbox(ctx, 540, 1380, 40, A(t, 3.0, 3.6), A(t, 2.6, 3.0), lw=3.5)
    label(ctx, "LOGIQUE", 540, 1450, 15, 0.6 * A(t, 3.2, 3.6))


def screen(ctx, x, y, w, h, a, prog=1.0):
    polyline(ctx, [(x - w / 2, y - h / 2), (x + w / 2, y - h / 2), (x + w / 2, y + h / 2), (x - w / 2, y + h / 2), (x - w / 2, y - h / 2)], prog, 3.5, a)


def s3(ctx, t, d):  # 1995 : trois psychologues revoient les images de Barcelone
    year = int(lerp(1960, 1995, eout(A(t, 0.1, 1.2))))
    label(ctx, str(year), 540, 860, 44, A(t, 0.0, 0.4) * (1 - 0.6 * A(t, 2.2, 2.8)), spacing=8)
    sx, sy, sw, sh = 540, 1080, 520, 300
    screen(ctx, sx, sy, sw, sh, 1, A(t, 1.8, 2.6))
    # mini podium dans l'écran
    sa = A(t, 2.6, 3.2)
    if sa > 0:
        ctx.save(); ctx.translate(sx, sy + 120); ctx.scale(0.42, 0.42); ctx.translate(-540, -BASE)
        podium(ctx, 1, sa, 0)
        for k in (1, 2, 3):
            x, y = top_of(k)
            athlete(ctx, x, y - 3, 1.2, sa, (0.6, -1, 1)[k - 1])
        ctx.restore()
        # tête de lecture qui défile
        px = lerp(sx - sw / 2 + 20, sx + sw / 2 - 20, clamp((t - 2.6) / 3))
        polyline(ctx, [(sx - sw / 2 + 20, sy + sh / 2 - 18), (px, sy + sh / 2 - 18)], 1, 3, 0.8 * sa)
    label(ctx, "BARCELONE 1992", sx, sy - sh / 2 - 22, 16, 0.75 * A(t, 4.0, 4.5))
    for i, x in enumerate([400, 540, 680]):
        person(ctx, x, 1420, 1.15, A(t, 0.9 + 0.2 * i, 1.3 + 0.2 * i), pose="look_up")


def s4(ctx, t, d):  # noter les visages, de l'agonie à l'extase
    y = 1250
    x0, x1 = 140, 940
    polyline(ctx, [(x0, y), (x1, y)], A(t, 0.1, 0.9), 3.5)
    for i in range(10):
        x = lerp(x0, x1, (i + 0.5) / 10)
        a = A(t, 0.5 + i * 0.06, 0.8 + i * 0.06)
        polyline(ctx, [(x, y - 14), (x, y + 14)], 1, 2.5, a)
        label(ctx, str(i + 1), x, y + 50, 16, 0.6 * a, spacing=0)
    label(ctx, "AGONIE", x0 + 40, y + 100, 16, 0.75 * A(t, 2.4, 2.8))
    label(ctx, "EXTASE", x1 - 40, y + 100, 16, 0.75 * A(t, 3.0, 3.4))
    # un visage qui glisse de l'agonie à l'extase
    k = A(t, 1.6, 4.2)
    fx = lerp(x0 + 40, x1 - 40, k)
    face(ctx, fx, y - 160, 70, lerp(-1, 1, k), A(t, 1.0, 1.5))
    polyline(ctx, [(fx, y - 85), (fx, y - 20)], 1, 2, 0.5 * A(t, 1.0, 1.5), dash=[4, 6])


def s5(ctx, t, d):  # résultat : bronze plus heureux que l'argent
    y = 1380
    x0, x1 = 140, 940
    polyline(ctx, [(x0, y), (x1, y)], 1, 3, 0.6)
    for i in range(10):
        x = lerp(x0, x1, (i + 0.5) / 10)
        polyline(ctx, [(x, y - 10), (x, y + 10)], 1, 2, 0.5)
    for k, (lab, score, mood, t0) in enumerate([("ARGENT", 4.8, -0.3, 0.2), ("BRONZE", 7.1, 0.9, 1.0)]):
        p = eout(A(t, t0, t0 + 1.2))
        x = lerp(x0, x1, (lerp(1, score, p) - 0.5) / 10)
        yy = 1080 + 170 * k
        face(ctx, x, yy - 10 - 70 * k, 52, lerp(0, mood, p), A(t, t0, t0 + 0.3))
        polyline(ctx, [(x, yy + 45 - 70 * k), (x, y - 14)], 1, 2, 0.5 * A(t, t0, t0 + 0.3), dash=[4, 6])
        label(ctx, lab, x, y + 50, 16, 0.8 * A(t, t0 + 0.4, t0 + 0.8))
        if k == 1:
            glowdot(ctx, x, yy - 80, 120, 0.3 * A(t, 2.0, 2.6))


def s6(ctx, t, d):  # relance : là que ça devient intéressant
    x, y = 540, 1330
    athlete(ctx, x, y, 1.6, A(t, 0, 0.4), -1, 1, pose="think")
    q = A(t, 0.4, 0.9)
    pulse = 1 + 0.12 * math.sin(t * 4)
    ctx.select_font_face(SERIF, cairo.FONT_SLANT_ITALIC, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(170 * pulse)
    e = ctx.text_extents("?")
    white(ctx, q)
    ctx.move_to(x - e.x_advance / 2, y - 200)
    ctx.show_text("?")
    glowdot(ctx, x, y - 250, 160, 0.15 * q)
    label(ctx, "ARGENT", x, y + 55, 16, 0.75 * A(t, 0.3, 0.7))


def s7(ctx, t, d):  # le deuxième regarde le premier : j'y étais presque
    podium(ctx, 1, 1, 0.6)
    x1, y1 = top_of(1); x2, y2 = top_of(2); x3, y3 = top_of(3)
    athlete(ctx, x1, y1 - 3, 1.2, 1, 0.6, 1, A(t, 1.6, 2.4))
    athlete(ctx, x2, y2 - 3, 1.2, 1, 0, 1, pose="look_up" if t < 3.6 else "sad", look=1)
    athlete(ctx, x3, y3 - 3, 1.2, 0.35 * (1 - A(t, 0.2, 1.2)) + 0.25, 0, 0.3)
    # regard vers le premier : flèche pointillée
    arrow(ctx, (x2 + 30, y2 - 110), (x1 - 50, y1 - 110), A(t, 1.0, 2.0), 2.5, 0.8, dash=[6, 8])
    # bulle « presque »
    ba = A(t, 3.8, 4.4)
    bubble(ctx, 300, 880, 300, 110, ba, tail=(x2 - 10, y2 - 90))
    medal(ctx, 300, 905, 26, ba, ba)  # il pense à l'or
    # petit écart mesuré entre 1 et 2
    ga = A(t, 4.8, 5.4)
    polyline(ctx, [(x1 - 120, y1), (x1 - 120, y2)], 1, 2, 0.7 * ga)
    label(ctx, "SI PEU", x1 - 200, (y1 + y2) / 2 + 6, 13, 0.7 * ga, spacing=3)


def s8(ctx, t, d):  # le troisième regarde vers le bas : sans rien
    podium(ctx, 1, 1, 0.6)
    x1, y1 = top_of(1); x2, y2 = top_of(2); x3, y3 = top_of(3)
    athlete(ctx, x1, y1 - 3, 1.2, 0.3, 0.6, 0.3)
    athlete(ctx, x2, y2 - 3, 1.2, 0.3, -1, 0.3)
    athlete(ctx, x3, y3 - 3, 1.2, 1, 0.9 * A(t, 2.6, 3.2), 1, A(t, 3.0, 4.0), look=1, pose="look_down" if t < 2.6 else None)
    # au pied du podium : la 4e place, les mains vides
    fx = 905
    person(ctx, fx, BASE - 3, 1.0, 0.7 * A(t, 0.4, 0.9), pose="sad", look=-1)
    label(ctx, "4", fx, BASE + 50, 20, 0.6 * A(t, 0.6, 1.0), spacing=0)
    arrow(ctx, (x3 + 40, y3 - 80), (fx - 20, BASE - 120), A(t, 0.6, 1.6), 2.5, 0.8, dash=[6, 8])
    ba = A(t, 2.0, 2.6)
    bubble(ctx, 800, 1000, 280, 110, ba, tail=(x3 + 10, y3 - 90))
    white(ctx, ba); ctx.set_dash([5, 6]); ctx.set_line_width(2.5)
    ctx.new_path(); ctx.arc(800, 1012, 26, 0, 2 * math.pi); ctx.stroke(); ctx.set_dash([])  # médaille absente


def s9(ctx, t, d):  # même podium, deux histoires dans la tête
    podium(ctx, 1, 1, 0.6)
    x1, y1 = top_of(1); x2, y2 = top_of(2); x3, y3 = top_of(3)
    athlete(ctx, x1, y1 - 3, 1.2, 0.35, 0.6, 0.35)
    athlete(ctx, x2, y2 - 3, 1.2, 1, -1, 1)
    athlete(ctx, x3, y3 - 3, 1.2, 1, 0.9, 1, 0.6)
    a2 = A(t, 0.6, 1.1)
    bubble(ctx, 280, 960, 170, 150, a2, tail=(x2, y2 - 95))
    arrow(ctx, (280, 1010), (280, 915), a2, 4, a2, head=22)
    a3 = A(t, 1.0, 1.5)
    bubble(ctx, 800, 1040, 170, 150, a3, tail=(x3, y3 - 95))
    arrow(ctx, (800, 990), (800, 1085), a3, 4, a3, head=22)
    label(ctx, "MÊME PODIUM", 540, BASE + 60, 18, 0.8 * A(t, 0.1, 0.5), spacing=6)


def s10(ctx, t, d):  # ce qu'on a / ce qu'on imagine à côté
    y = 1150
    medal(ctx, 340, y, 85, A(t, 0.1, 0.6), A(t, 0.4, 1.0))
    label(ctx, "CE QU'ON A", 340, y + 150, 16, 0.75 * A(t, 1.6, 2.0))
    ia = A(t, 2.4, 3.0)
    white(ctx, ia)
    ctx.set_dash([8, 9]); ctx.set_line_width(3)
    ctx.new_path(); ctx.arc(740, y, 85, 0, 2 * math.pi); ctx.stroke(); ctx.set_dash([])
    polyline(ctx, [(740 - 60, y - 187), (740, y - 77), (740 + 60, y - 187)], 1, 2.2, 0.6 * ia, dash=[6, 8])
    glowdot(ctx, 740, y, 150, 0.25 * ia * (0.7 + 0.3 * math.sin(t * 3)))
    label(ctx, "CE QU'ON IMAGINE", 740, y + 150, 16, 0.75 * A(t, 2.8, 3.2))
    # cerveau qui compare : petit balancier
    tilt = 0.18 * A(t, 2.6, 3.4)
    ctx.save(); ctx.translate(540, 1420); ctx.rotate(tilt)
    polyline(ctx, [(-240, 0), (240, 0)], A(t, 0.8, 1.4), 3, 0.8)
    ctx.restore()
    polyline(ctx, [(520, 1460), (540, 1420), (560, 1460), (520, 1460)], A(t, 0.8, 1.2), 3, 0.8)


def stairs_pts(n, x0=110, y0=1440, dx=95, dy=78):
    pts = [(x0, y0)]
    for i in range(n):
        x, y = pts[-1]
        pts += [(x + dx, y), (x + dx, y - dy)]
    return pts


def s11(ctx, t, d):  # viser plus haut... la marche au-dessus ne suffit jamais
    n = 7
    pts = stairs_pts(n)
    prog = A(t, 0.1, 2.0)
    polyline(ctx, pts, prog, 3.5, 1)
    # le grimpeur avance de marche en marche
    k = clamp((t - 1.0) / (d - 2.0))
    step = min(n - 1, int(k * n))
    sx, sy = pts[1 + 2 * step]
    person(ctx, sx - 48, sy - 3, 0.95, A(t, 0.3, 0.7), pose="walk", look=1)
    # la marche au-dessus brille toujours
    nx, ny = pts[min(len(pts) - 1, 1 + 2 * (step + 1))]
    glowdot(ctx, nx - 48, ny - 30, 70, 0.45 * A(t, 0.8, 1.2))
    # des marches en pointillé continuent au-delà du cadre
    ex, ey = pts[-1]
    ghost = [(ex, ey), (ex + 95, ey), (ex + 95, ey - 78), (ex + 190, ey - 78)]
    polyline(ctx, ghost, A(t, 2.0, 3.0), 2.5, 0.5, dash=[6, 8])
    label(ctx, "JAMAIS ASSEZ", 300, 900, 18, 0.7 * A(t, 5.5, 6.2), spacing=6)


def s12(ctx, t, d):  # à qui je me compare ?
    x, y = 540, 1240
    person(ctx, x, y, 1.4, A(t, 0, 0.4), pose="look_up" if t < 3.0 else "look_down")
    # au-dessus : une rangée de gens ; en dessous : une autre
    for i in range(7):
        xi = 180 + i * 120
        a = A(t, 0.3 + 0.08 * i, 0.6 + 0.08 * i)
        person(ctx, xi, 900, 0.8, 0.7 * a)
        person(ctx, xi, 1440, 0.8, 0.7 * A(t, 3.0 + 0.08 * i, 3.3 + 0.08 * i))
    arrow(ctx, (x, y - 110), (x, 930), A(t, 1.0, 1.8), 3, 0.8)
    arrow(ctx, (x, y + 20), (x, 1340), A(t, 3.2, 3.9), 3, 0.8)
    q = A(t, 3.6, 4.2)
    ctx.select_font_face(SERIF, cairo.FONT_SLANT_ITALIC, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(110)
    e = ctx.text_extents("?")
    white(ctx, q)
    ctx.move_to(x + 120 - e.x_advance / 2, y - 40)
    ctx.show_text("?")


def s13(ctx, t, d):  # défi : regarde une fois vers le bas, d'où tu es parti
    n = 6
    pts = stairs_pts(n, x0=130, y0=1400, dx=130, dy=82)
    polyline(ctx, pts, 1, 3.5, 1)
    tx, ty = pts[-1]
    person(ctx, tx - 50, ty - 3, 1.0, A(t, 0, 0.4), pose="look_down", look=-1, k=A(t, 0.6, 1.2))
    # regard vers le bas : chemin pointillé qui redescend jusqu'au départ
    path = [(pts[i][0] - 30, pts[i][1] - 30) for i in range(len(pts) - 1, -1, -2)]
    polyline(ctx, path, A(t, 0.8, 3.0), 2.5, 0.75, dash=[6, 8])
    da = A(t, 2.8, 3.4)
    glowdot(ctx, 140, 1385, 100, 0.6 * da)
    label(ctx, "DÉPART", 170, 1450, 16, 0.85 * da)
    label(ctx, "TOI", tx - 50, ty - 120, 16, 0.75 * A(t, 0.3, 0.7))


def s14(ctx, t, d):  # boucle : le podium, l'argent relève la tête, la médaille s'illumine
    podium(ctx, A(t, 0, 0.6), 1, A(t, 0.2, 0.6))
    x1, y1 = top_of(1); x2, y2 = top_of(2); x3, y3 = top_of(3)
    athlete(ctx, x1, y1 - 3, 1.2, A(t, 0.1, 0.5), 0.6, 1)
    athlete(ctx, x3, y3 - 3, 1.2, A(t, 0.1, 0.5), 0.9, 1)
    lift = A(t, 1.4, 2.6)
    athlete(ctx, x2, y2 - 3, 1.2, A(t, 0.1, 0.5), lerp(-1, 0.8, lift), 1)
    b = A(t, 2.2, 3.8)
    medal(ctx, x2, y2 - 3 - 22 * 1.2, 7 * 1.2, 1, 1, ribbon=False)
    glowdot(ctx, x2, y2 - 60, 320 * b + 1, 0.45 * b)
    glowdot(ctx, x2, y2 - 60, 140 * b + 1, 0.9 * b)
    label(ctx, "ARGENT", x2, BASE + 50, 16, 0.8 * A(t, 0.3, 0.7))


SCENES = [
    (0.0, 3.98, s1), (3.98, 9.75, s2), (9.75, 15.46, s3), (15.46, 20.12, s4),
    (20.12, 23.28, s5), (23.28, 25.6, s6), (25.6, 32.26, s7), (32.26, 37.38, s8),
    (37.38, 40.16, s9), (40.16, 44.64, s10), (44.64, 52.52, s11), (52.52, 58.88, s12),
    (58.88, 64.1, s13), (64.1, 69.54, s14),
]

HOOK = dict(title=["Mieux vaut", "finir *3e"], t_in=0.2, t_full=1.0, end=4.0, y=640, captions=False)
