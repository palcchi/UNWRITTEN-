#!/usr/bin/env python3
"""UNWRITTEN AION production pass 2.

This pass only owns:
- aion_prologue
- aion
- aion_the_architect

Art direction:
- Prologue is a sealed floating reliquary, never a plain sphere.
- Humanoid forms keep true Steve/player scale.
- Materials are custom procedural pixel shading, never pasted concept art.
- Animation language is stepped pose-to-pose: long holds, short snaps, recoil,
  delayed secondary motion, inspired by Minecraft cinematic / Dungeons readability.
"""

import json
import math
from PIL import ImageDraw

from build_assets import ROOT, RP, dump, geometry, bbmodel
from build_colossi import Sculpt, M, paint_atlas

# AION-only deterministic materials.
M.update({
    "aion_void": ("#060609", "stone"),
    "aion_ink": ("#0a0b10", "flat"),
    "aion_black": ("#141418", "cloth"),
    "aion_black_2": ("#1e1f24", "cloth"),
    "aion_graphite": ("#2f3138", "metal"),
    "aion_cold": ("#747b86", "metal"),
    "aion_ivory": ("#d9d4cb", "cloth"),
    "aion_broken_ivory": ("#c6c1ba", "cloth"),
    "aion_skin": ("#c9c3ba", "skin"),
    "aion_hair": ("#ddd9d2", "hair"),
    "aion_hair_shadow": ("#a6a19c", "hair"),
    "aion_gold": ("#b8964f", "metal"),
    "aion_gold_pale": ("#d5bf7c", "metal"),
    "aion_gold_glow": ("#f1dfaa", "glow"),
    "aion_violet": ("#7860b3", "glow"),
    "aion_violet_hot": ("#a989ef", "glow"),
})


def ring(r, bone, center, radius, thickness, mat, count=24, gaps=()):
    r.ring(bone, center, radius, thickness, mat, count=count, gaps=gaps)


def stepped(poses, snap=1/12):
    """Convert [(time, value), ...] into held poses with short transitions.

    Bedrock itself interpolates keyframes. Duplicating each pose shortly before the
    next key creates Minecraft-like held poses followed by a fast snap.
    """
    if len(poses) <= 1:
        return poses
    out = []
    for i, (t, value) in enumerate(poses):
        out.append((round(t, 4), value))
        if i + 1 < len(poses):
            nt = poses[i + 1][0]
            hold_t = max(t, nt - snap)
            if hold_t > t + 1e-4:
                out.append((round(hold_t, 4), value))
    return out


def reliquary():
    """Form 0: The Sealed Reliquary. Artifact, not creature, not orb."""
    r = Sculpt()
    r.bones[1]["pivot"] = [0, 16, 0]

    r.joint("reliquary_core", (0, 16, 0), "body")
    r.add("reliquary_core", (-3.6, 7.0, -2.5), (7.2, 18.0, 5.0), "aion_black")
    r.add("reliquary_core", (-2.9, 5.8, -2.1), (5.8, 2.2, 4.2), "aion_graphite")
    r.add("reliquary_core", (-2.9, 25.0, -2.1), (5.8, 2.2, 4.2), "aion_graphite")

    for side in (-1, 1):
        r.add("reliquary_core", (side * 3.3 - 1.0, 9.2, -2.2), (2.0, 13.5, 4.4),
              "aion_black_2", (0, 0, -side * 9), (side * 3.2, 16, 0))
        r.add("reliquary_core", (side * 2.4 - .55, 24.2, -1.8), (1.1, 4.4, 3.6),
              "aion_graphite", (0, 0, -side * 23), (side * 2.2, 24.5, 0))
        r.add("reliquary_core", (side * 2.1 - .45, 4.3, -1.6), (.9, 4.2, 3.2),
              "aion_graphite", (0, 0, side * 24), (side * 2.0, 7.0, 0))

    r.joint("center_seam", (0, 16, -2.8), "reliquary_core")
    r.add("center_seam", (-0.16, 8.4, -2.86), (0.32, 15.3, 0.25), "aion_violet")
    for y in (11.0, 15.6, 20.3):
        r.add("center_seam", (-.6, y, -3.02), (1.2, .18, .18), "aion_violet_hot")

    r.joint("pulse_core", (0, 16, 0), "reliquary_core")
    r.add("pulse_core", (-1.3, 12.1, -2.75), (2.6, 7.8, .35), "aion_ink")
    r.add("pulse_core", (-.45, 13.0, -2.98), (.9, 6.0, .18), "aion_violet_hot")

    plates = [
        (-5.3, 19.2, 0, -12), (5.3, 18.0, 0, 12),
        (-4.5, 10.2, .8, 16), (4.7, 9.4, -.8, -16),
        (-2.4, 28.2, .3, -8), (2.4, 3.2, -.3, 8),
    ]
    for i, (x, y, z, rz) in enumerate(plates):
        n = f"shell_plate_{i}"
        r.joint(n, (x, y, z), "body")
        r.add(n, (x - 1.15, y - 2.3, z - .45), (2.3, 4.6, .9),
              "aion_black_2", (0, 0, rz), (x, y, z))
        r.add(n, (x - .12, y - 1.7, z - .62), (.24, 3.4, .16),
              "aion_graphite", (0, 0, rz), (x, y, z))

    r.joint("ring_inner", (0, 16, 2.8), "body")
    ring(r, "ring_inner", (0, 16, 2.8), 8.2, .28, "aion_graphite", 24, (2, 3, 9, 14, 20))
    r.joint("ring_outer", (0, 16, 3.5), "body")
    ring(r, "ring_outer", (0, 16, 3.5), 11.4, .33, "aion_black_2", 28, (0, 5, 6, 12, 18, 23, 24))

    for i in range(8):
        a = math.tau * i / 8
        x = math.cos(a) * (12.2 + (i % 2) * 1.0)
        y = 16 + math.sin(a) * (10.0 + (i % 3) * .7)
        z = 4.4 + math.sin(i * 1.7) * 1.8
        n = f"fragment_{i}"
        r.joint(n, (x, y, z), "body")
        r.add(n, (x - .35, y - 1.4, z - .25), (.7, 2.8, .5),
              "aion_black", (i * 7, i * 11, i * 19), (x, y, z))
    return r


def steve_base(r, architect=False):
    """True Steve scale. Accessories never affect body scale."""
    r.bones[1]["pivot"] = [0, 12, 0]
    body_mat = "aion_broken_ivory" if architect else "aion_black"
    limb_mat = "aion_ivory" if architect else "aion_black_2"

    r.add("body", (-4, 12, -2), (8, 12, 4), body_mat)
    r.joint("neck", (0, 24, 0), "body")
    r.add("neck", (-1.3, 23.4, -1.35), (2.6, 2.2, 2.7),
          "aion_skin" if architect else "aion_graphite")
    r.joint("head", (0, 24, 0), "neck")
    r.add("head", (-4, 24, -4), (8, 8, 8),
          "aion_skin" if architect else "aion_graphite")

    for side, label in [(-1, "l"), (1, "r")]:
        x = side * 6
        r.joint(f"arm_{label}", (x, 24, 0), "body")
        r.add(f"arm_{label}", (x - 2, 12, -2), (4, 12, 4), limb_mat)
        r.joint(f"forearm_{label}", (x, 17, 0), f"arm_{label}")
        r.add(f"forearm_{label}", (x - 1.7, 11.4, -1.75), (3.4, 5.9, 3.5),
              "aion_graphite" if not architect else "aion_broken_ivory")
        r.joint(f"hand_{label}", (x, 11.6, 0), f"forearm_{label}")
        r.add(f"hand_{label}", (x - 1.65, 9.9, -1.65), (3.3, 1.9, 3.3),
              "aion_graphite" if not architect else "aion_skin")
        for j in range(4):
            fx = x - 1.35 + j * .9
            fn = f"finger_{label}_{j}"
            r.joint(fn, (fx, 10.2, -1.4), f"hand_{label}")
            r.add(fn, (fx - .28, 8.85, -1.7), (.56, 1.55, .75),
                  "aion_graphite" if not architect else "aion_skin")

        lx = side * 2
        r.joint(f"leg_{label}", (lx, 12, 0), "body")
        r.add(f"leg_{label}", (lx - 2, 0, -2), (4, 12, 4), limb_mat)
        r.joint(f"shin_{label}", (lx, 6, 0), f"leg_{label}")
        r.add(f"shin_{label}", (lx - 1.75, 0.6, -2.05), (3.5, 5.6, 4.1),
              "aion_graphite" if not architect else "aion_broken_ivory")
        r.joint(f"foot_{label}", (lx, 1.5, -1.4), f"shin_{label}")
        r.add(f"foot_{label}", (lx - 2, 0, -3.1), (4, 2.1, 5.1), "aion_black")


def hair(r, architect=False):
    base = "aion_hair" if architect else "aion_hair_shadow"
    hi = "aion_hair" if architect else "aion_cold"
    r.joint("hair_back", (0, 30, 1.4), "head")
    r.add("hair_back", (-3.9, 27.0, 2.0), (7.8, 5.2, 2.2), base)
    r.add("head", (-4.15, 30.2, -4.0), (8.3, 1.8, 8.0), hi)
    r.joint("hair_front", (0, 30, -4.2), "head")
    for i in range(11):
        x = -4.05 + i * .8
        drop = (i % 4) * .45
        r.add("hair_front", (x, 27.6 - drop, -4.4), (.9, 3.0 + drop, .65),
              hi, (0, 0, (i % 3 - 1) * 9), (x + .45, 30.2, -4.0))
    for side in (-1, 1):
        x = side * 3.95
        r.add("head", (x - .65, 25.0, -2.7), (1.3, 5.6, 4.4),
              base, (0, 0, -side * 5), (x, 30, 0))


def face(r, architect=False):
    if architect:
        r.add("head", (0.05, 24.25, -4.42), (3.9, 7.2, .52), "aion_void")
        r.add("head", (-3.3, 27.35, -4.45), (2.15, .48, .20), "aion_gold_glow")
        r.add("head", (-2.1, 26.0, -4.5), (.42, 2.1, .20), "aion_gold")
        for j in range(4):
            r.add("head", (.4 + j * .68, 24.8 + j * 1.15, -4.72),
                  (.20, 2.0, .20), "aion_violet", (0, 0, -22), (1 + j * .6, 26, -4.5))
    else:
        r.add("head", (-3.35, 27.25, -4.28), (2.3, .48, .20), "aion_gold_glow")
        r.add("head", (1.05, 27.25, -4.28), (2.3, .48, .20), "aion_gold_glow")
        r.add("head", (-3.55, 28.1, -4.24), (7.1, .52, .20), "aion_ink")
        r.add("head", (-.24, 25.6, -4.30), (.48, 1.4, .20), "aion_cold")
        for side in (-1, 1):
            r.add("head", (side * 3.3 - .32, 24.8, -4.38), (.64, 3.3, .23),
                  "aion_graphite", (0, 0, side * 5), (side * 3.2, 27, -4.1))
        r.add("head", (-1.2, 24.75, -4.36), (2.4, .24, .18), "aion_black")


def costume(r, architect=False):
    cloth = "aion_broken_ivory" if architect else "aion_black"
    cloth2 = "aion_ivory" if architect else "aion_black_2"
    metal = "aion_gold" if architect else "aion_graphite"
    trim = "aion_gold_pale" if architect else "aion_cold"
    glow = "aion_violet_hot" if architect else "aion_violet"

    r.joint("collar", (0, 23, 0), "body")
    for side in (-1, 1):
        r.add("collar", (side * 2.8 - 1.05, 22.0, -2.9), (2.1, 4.7, 5.8),
              metal, (0, 0, -side * 14), (side * 2.8, 23.5, 0))
        r.add("collar", (side * 3.8 - .85, 21.0, -.2), (1.7, 2.6, 4.2),
              cloth2, (0, 0, side * 20), (side * 3.8, 22, 0))

    for side, label in [(-1, "l"), (1, "r")]:
        n = f"shoulder_{label}"
        r.joint(n, (side * 5.0, 23.0, 0), "body")
        for j in range(3):
            r.add(n, (side * (4.2 + j * .55) - (1.25 if side > 0 else 0),
                      20.7 - j * .35, -2.4 + j * .2),
                  (1.25, 2.6, 4.8 - j * .25), metal,
                  (0, 0, side * (8 + j * 7)), (side * 4.8, 23, 0))

    r.add("body", (-3.45, 17.0, -2.45), (6.9, 5.8, .62), cloth2)
    for side in (-1, 1):
        r.add("body", (side * 1.75 - 1.5, 18.1, -2.72), (3.0, 3.4, .38),
              metal, (0, side * 8, side * -4), (side * 1.75, 20, -2.4))
    r.add("body", (-.15, 14.8, -2.78), (.30, 8.1, .24), glow)
    for y in (16.5, 19.2, 21.7):
        r.add("body", (-1.35, y, -2.70), (2.7, .18, .20), trim)

    for side, label in [(-1, "l"), (1, "r")]:
        x = side * 6
        r.add(f"forearm_{label}", (x - 2.0, 13.0, -2.2), (4.0, 3.4, .55), metal)
        r.add(f"forearm_{label}", (x - .14, 12.5, -2.47), (.28, 4.1, .18), glow)
        r.add(f"hand_{label}", (x - .7, 9.65, -1.98), (1.4, .24, .32), trim)

    r.add("body", (-3.6, 11.35, -2.22), (7.2, .8, 4.45), "aion_graphite")
    r.add("body", (-.8, 11.1, -2.62), (1.6, 1.25, .35), metal)

    for side, label in [(-1, "l"), (1, "r")]:
        n = f"waist_side_{label}"
        r.joint(n, (side * 3.2, 12.0, 0), "body")
        r.add(n, (side * 3.2 - .85, 3.3, -1.6), (1.7, 8.8, 3.2), cloth2,
              (0, 0, side * 4), (side * 3.2, 12, 0))
    for i in range(5):
        x = -2.5 + i * 1.25
        n = f"robe_front_{i}"
        r.joint(n, (x, 12, -2.0), "body")
        length = 9.8 - (i % 2) * 1.4
        r.add(n, (x - .54, 12 - length, -2.55), (1.08, length, .55), cloth)
        if i in (0, 2, 4):
            r.add(n, (x - .10, 12 - length + .4, -2.83), (.20, length - .8, .18), trim)
    for i in range(5):
        x = -3.0 + i * 1.5
        n = f"mantle_{i}"
        r.joint(n, (x, 23.2, 2.2), "body")
        length = 14.5 - (i % 3) * 1.7
        r.add(n, (x - .68, 23.2 - length, 2.3), (1.36, length, .40), cloth2,
              (2 + (i % 2) * 2, 0, 0), (x, 23.2, 2.3))


def authority_backpiece(r, architect=False):
    """Broken halo + sealed reliquary core callback. Never a simple orb."""
    r.joint("authority_core", (0, 26.5, 5.8), "body")
    r.add("authority_core", (-1.55, 22.9, 4.5), (3.1, 7.2, 2.6), "aion_void")
    r.add("authority_core", (-.12, 23.7, 4.1), (.24, 5.7, .20),
          "aion_violet_hot" if architect else "aion_violet")
    for side in (-1, 1):
        r.add("authority_core", (side * 1.5 - .55, 23.8, 4.7), (1.1, 5.0, 2.2),
              "aion_graphite", (0, 0, -side * 10), (side * 1.5, 26.4, 5.8))

    r.joint("halo_inner", (0, 26.5, 6.4), "body")
    ring(r, "halo_inner", (0, 26.5, 6.4), 8.5, .26,
         "aion_gold" if architect else "aion_graphite",
         28, (2, 9, 17, 22) if not architect else (1, 4, 8, 13, 18, 24))
    r.joint("halo_outer", (0, 26.5, 7.0), "body")
    ring(r, "halo_outer", (0, 26.5, 7.0), 11.5 if architect else 10.2, .28,
         "aion_gold_pale" if architect else "aion_black_2",
         32, (0, 5, 11, 16, 21, 27) if architect else (4, 12, 19, 26))

    for i, a in enumerate((.1, 1.65, 3.15, 4.7)):
        rad = 8.5 if i % 2 == 0 else (11.5 if architect else 10.2)
        x = math.cos(a) * rad
        y = 26.5 + math.sin(a) * rad
        r.add("halo_inner" if i % 2 == 0 else "halo_outer",
              (x - .27, y - .27, 6.0), (.54, .54, .54),
              "aion_gold_glow" if architect else "aion_cold")


def aion_humanoid(architect=False):
    r = Sculpt()
    steve_base(r, architect)
    hair(r, architect)
    face(r, architect)
    costume(r, architect)
    authority_backpiece(r, architect)

    if architect:
        r.parts = [p for p in r.parts if not (
            p["bone"] == "body" and p["origin"] == [-4, 12, -2] and p["size"] == [8, 12, 4]
        )]
        for i, y in enumerate((12.2, 14.8, 17.4, 20.0, 22.5)):
            n = f"torso_slab_{i}"
            r.joint(n, (0, y + 1.0, 0), "body")
            width = 7.8 - (i % 2) * .5
            r.add(n, (-width / 2, y, -1.9), (width, 2.0, 3.8), "aion_broken_ivory")
            r.add(n, (-.11, y + .2, -2.18), (.22, 1.55, .22), "aion_gold")

        for pair in range(2):
            for side, label in [(-1, "l"), (1, "r")]:
                x = side * (8.0 + pair * 1.8)
                y = 22.0 - pair * 4.1
                upper = f"aux_arm_{label}_{pair}"
                fore = f"aux_forearm_{label}_{pair}"
                hand = f"aux_hand_{label}_{pair}"
                r.joint(upper, (x, y, 2.7), "body", (0, 0, side * (28 + pair * 18)))
                r.add(upper, (x - .95, y - 4.6, 1.7), (1.9, 4.8, 2.0),
                      "aion_broken_ivory", (0, 0, side * (28 + pair * 18)), (x, y, 2.7))
                r.joint(fore, (x + side * 1.4, y - 4.0, 2.5), upper)
                r.add(fore, (x + side * 1.4 - .75, y - 7.8, 1.6), (1.5, 4.1, 1.8),
                      "aion_ivory", (0, 0, side * (12 + pair * 10)), (x, y - 4, 2.5))
                r.joint(hand, (x + side * 1.6, y - 7.6, 2.4), fore)
                r.add(hand, (x + side * 1.6 - .9, y - 9.0, 1.5), (1.8, 1.8, 1.9), "aion_void")

        for i in range(14):
            a = math.tau * i / 14
            x = math.cos(a) * (13.0 + (i % 3) * .9)
            y = 21.0 + math.sin(a) * (10.5 + (i % 2) * .8)
            z = 6.5 + math.sin(i * 1.37) * 2.3
            n = f"authority_fragment_{i}"
            r.joint(n, (x, y, z), "body")
            h = 3.6 + (i % 3) * .8
            r.add(n, (x - .42, y - h / 2, z - .3), (.84, h, .6),
                  "aion_black", (i * 5, i * 11, i * 27), (x, y, z))
            r.add(n, (x - .10, y - h / 2 + .4, z - .48), (.20, h - .8, .18),
                  "aion_violet_hot" if i % 2 else "aion_gold_glow",
                  (0, 0, i * 27), (x, y, z))
    return r


def animate_aion(e, r):
    aid = e["id"]
    scale = e["recipe_scale"]
    out = {}

    def K(seq):
        return {str(t): v for t, v in stepped(seq)}

    def R(seq):
        return {"rotation": K(seq)}

    def P(seq):
        return {"position": K([(t, [q * scale for q in v]) for t, v in seq])}

    def S(seq):
        return {"scale": K(seq)}

    def clip(name, duration, tracks, loop=False):
        bones = {n: v for n, v in tracks.items() if r.has(n)}
        if bones:
            out[f"animation.unwritten.{aid}.{name}"] = {
                "loop": loop,
                "animation_length": duration,
                "bones": bones,
            }

    z = [0, 0, 0]

    if aid == "aion_prologue":
        idle = {
            "body": P([(0, z), (2.4, [0, .18, 0]), (4.8, z)]),
            "ring_inner": R([(0, z), (4.8, [0, 0, 22])]),
            "ring_outer": R([(0, z), (4.8, [0, 0, -16])]),
            "pulse_core": S([(0, [1,1,1]), (2.4, [1,1.05,1]), (4.8, [1,1,1])]),
        }
        for i in range(8):
            idle[f"fragment_{i}"] = R([(0, z), (4.8, [0, 0, 8 if i % 2 else -8])])
        clip("idle", 4.8, idle, True)
        clip("sealed_idle", 4.8, idle, True)

        pulse = {
            "center_seam": S([(0, [.65,1,.65]), (1.2, [.65,1,.65]),
                              (1.32, [1.5,1,1.5]), (2.7, [1.5,1,1.5]), (3.0, [.65,1,.65])]),
            "pulse_core": S([(0, [1,1,1]), (1.2, [1,1,1]),
                             (1.32, [1.35,1.1,1.35]), (2.7, [1.2,1,1.2]), (3.0, [1,1,1])]),
            "ring_inner": R([(0,z),(1.2,z),(1.32,[0,0,28]),(2.7,[0,0,28]),(3.0,[0,0,34])]),
        }
        clip("pulse_awaken", 3.0, pulse)
        clip("presence_pulse", 3.0, pulse)

        reveal = {
            "reliquary_core": S([(0,[1,1,1]),(2.0,[1,1,1]),(2.17,[1.08,.98,1.08]),
                                  (4.2,[1.08,.98,1.08]),(4.42,[.86,1.06,.86]),(6.8,[.86,1.06,.86]),
                                  (7.1,[.03,.03,.03])]),
            "ring_inner": R([(0,z),(1.8,z),(2.0,[0,0,45]),(4.2,[0,0,45]),
                              (4.42,[0,0,120]),(7.1,[0,0,180])]),
            "ring_outer": R([(0,z),(1.8,z),(2.0,[0,0,-35]),(4.2,[0,0,-35]),
                              (4.42,[0,0,-110]),(7.1,[0,0,-170])]),
            "center_seam": S([(0,[.6,1,.6]),(1.8,[.6,1,.6]),(2.0,[2.0,1,2.0]),
                               (4.2,[2.0,1,2.0]),(4.42,[3.0,1,3.0]),(7.1,[.01,.01,.01])]),
        }
        for i in range(6):
            reveal[f"shell_plate_{i}"] = P([
                (0,z),(2.0,z),(2.17,[math.cos(i*1.2)*2.2, math.sin(i*1.2)*1.8, .6]),
                (4.2,[math.cos(i*1.2)*2.2, math.sin(i*1.2)*1.8, .6]),
                (4.42,[math.cos(i*1.2)*6.5, math.sin(i*1.2)*5.0, 3.2]),
                (7.1,[math.cos(i*1.2)*9.0, math.sin(i*1.2)*7.0, 6.0]),
            ])
        clip("unseal_reveal", 7.1, reveal)
        clip("reveal_cue", 7.1, reveal)
        return out

    robe = [b["name"] for b in r.bones if b["name"].startswith(("robe_", "mantle_", "waist_side_"))]
    frags = [b["name"] for b in r.bones if b["name"].startswith("authority_fragment_")]
    aux = [b["name"] for b in r.bones if b["name"].startswith(("aux_arm_", "aux_forearm_", "aux_hand_"))]
    slabs = [b["name"] for b in r.bones if b["name"].startswith("torso_slab_")]

    idle = {
        "body": P([(0,z),(2.0,z),(2.08,[0,.12,0]),(4.2,[0,.12,0]),(4.28,z)]),
        "head": R([(0,z),(1.6,z),(1.68,[1.5,-1.2,0]),(3.7,[1.5,-1.2,0]),(3.78,z),(4.4,z)]),
        "halo_inner": R([(0,z),(4.4,[0,0,18])]),
        "halo_outer": R([(0,z),(4.4,[0,0,-12])]),
        "authority_core": S([(0,[1,1,1]),(2.1,[1,1.03,1]),(4.4,[1,1,1])]),
    }
    for i, n in enumerate(robe):
        idle[n] = R([(0,[2+i%2,0,0]),(2.0,[2+i%2,0,0]),
                     (2.08,[4+i%3,0,0]),(4.2,[4+i%3,0,0]),(4.28,[2+i%2,0,0])])
    for i, n in enumerate(frags):
        idle[n] = R([(0,z),(2.0,z),(2.08,[0,0,6 if i%2 else -6]),(4.4,[0,0,6 if i%2 else -6])])
    clip("idle", 4.4, idle, True)
    clip("architect_idle" if aid == "aion_the_architect" else "idle_authority", 4.4, idle, True)

    slow_turn = {
        "head": R([(0,z),(.9,z),(1.0,[0,24,0]),(1.9,[0,24,0]),(2.0,[0,34,0]),(2.6,[0,34,0])]),
        "body": R([(0,z),(1.25,z),(1.34,[0,9,0]),(2.6,[0,9,0])]),
        "halo_inner": R([(0,z),(2.6,[0,0,14])]),
    }
    clip("slow_turn", 2.6, slow_turn)
    clip("turn", 2.6, slow_turn)

    clip("hand_raise", 2.2, {
        "arm_r": R([(0,z),(.7,z),(.82,[-28,0,-5]),(1.25,[-28,0,-5]),
                    (1.36,[-74,0,-11]),(2.2,[-74,0,-11])]),
        "forearm_r": R([(0,z),(1.25,z),(1.36,[-28,0,0]),(2.2,[-28,0,0])]),
        "hand_r": R([(0,z),(1.36,z),(1.48,[12,0,4]),(2.2,[12,0,4])]),
        "head": R([(0,z),(1.36,z),(1.48,[0,-7,0]),(2.2,[0,-7,0])]),
    })

    clip("finger_snap", 1.5, {
        "arm_r": R([(0,[-74,0,-11]),(.58,[-74,0,-11]),(.67,[-82,0,-7]),
                    (.84,[-82,0,-7]),(.92,[-76,0,-4]),(1.5,[-76,0,-4])]),
        "finger_r_1": R([(0,z),(.58,z),(.67,[0,0,-18]),(.84,[0,0,-18]),
                         (.92,[0,0,30]),(1.5,[0,0,30])]),
        "finger_r_2": R([(0,z),(.58,z),(.67,[0,0,22]),(.84,[0,0,22]),
                         (.92,[0,0,-24]),(1.5,[0,0,-24])]),
        "halo_inner": R([(0,z),(.84,z),(.92,[0,0,28]),(1.5,[0,0,28])]),
        "authority_core": S([(0,[1,1,1]),(.84,[1,1,1]),(.92,[1.18,1.05,1.18]),(1.5,[1,1,1])]),
    })

    clip("authority_grant", 4.6, {
        "arm_r": R([(0,z),(1.2,z),(1.32,[-48,0,-12]),(2.2,[-48,0,-12]),
                    (2.34,[-70,0,-8]),(3.9,[-70,0,-8]),(4.08,[-32,0,-4]),(4.6,z)]),
        "arm_l": R([(0,z),(1.2,z),(1.32,[-38,0,12]),(2.2,[-38,0,12]),
                    (2.34,[-58,0,8]),(3.9,[-58,0,8]),(4.08,[-25,0,4]),(4.6,z)]),
        "head": R([(0,z),(2.2,z),(2.34,[-3,-5,0]),(3.9,[-3,-5,0]),(4.6,z)]),
        "halo_inner": R([(0,z),(2.2,z),(2.34,[0,0,35]),(3.9,[0,0,35]),(4.6,[0,0,48])]),
        "halo_outer": R([(0,z),(2.2,z),(2.34,[0,0,-24]),(3.9,[0,0,-24]),(4.6,[0,0,-36])]),
        "authority_core": S([(0,[1,1,1]),(2.2,[1,1,1]),(2.34,[1.28,1.08,1.28]),
                              (3.9,[1.28,1.08,1.28]),(4.08,[.92,1,.92]),(4.6,[1,1,1])]),
    })

    clip("freeze_player", 3.0, {
        "head": R([(0,z),(.8,z),(.92,[0,-10,0]),(3.0,[0,-10,0])]),
        "arm_r": R([(0,z),(.8,z),(.92,[-76,0,-2]),(3.0,[-76,0,-2])]),
        "forearm_r": R([(0,z),(.8,z),(.92,[-8,0,0]),(3.0,[-8,0,0])]),
        "halo_inner": R([(0,z),(.8,z),(.92,[0,0,22]),(3.0,[0,0,22])]),
    })

    clip("remove_authority", 4.0, {
        "arm_r": R([(0,z),(.9,z),(1.02,[-82,0,-16]),(2.0,[-82,0,-16]),
                    (2.12,[-35,0,24]),(3.1,[-35,0,24]),(3.24,[-58,0,8]),(4,z)]),
        "forearm_r": R([(0,z),(2.0,z),(2.12,[-42,0,0]),(3.1,[-42,0,0]),(4,z)]),
        "body": R([(0,z),(2.0,z),(2.12,[0,-8,0]),(3.1,[0,-8,0]),(4,z)]),
        "authority_core": S([(0,[1,1,1]),(2.0,[1,1,1]),(2.12,[.72,.82,.72]),
                              (3.1,[1.34,1.12,1.34]),(4,[1,1,1])]),
    })

    teleport = {
        "body": S([(0,[1,1,1]),(.7,[1,1,1]),(.82,[.72,1.08,.72]),
                   (1.15,[.72,1.08,.72]),(1.27,[.05,1.32,.05]),(1.55,[.05,1.32,.05]),
                   (1.67,[.72,1.08,.72]),(2.2,[1,1,1])]),
        "halo_inner": S([(0,[1,1,1]),(1.15,[1,1,1]),(1.27,[1.3,.6,1.3]),
                         (1.55,[1.3,.6,1.3]),(2.2,[1,1,1])]),
    }
    clip("teleport_break", 2.2, teleport)
    clip("teleport", 2.2, teleport)

    clip("subtle_smile", 2.2, {
        "head": R([(0,z),(.9,z),(1.0,[0,-4,1]),(1.7,[0,-4,1]),(1.82,[0,-2,0]),(2.2,z)])
    })

    clip("hover_descend", 3.0, {
        "root": P([(0,[0,3,0]),(1.2,[0,3,0]),(1.34,[0,.8,0]),(2.4,[0,.8,0]),(2.54,z),(3.0,z)]),
        "body": R([(0,[2,0,0]),(2.4,[2,0,0]),(2.54,z),(3.0,z)]),
    })

    if aid == "aion_the_architect":
        for name, sign in [("delete", -1), ("copy", 1), ("paste", -1)]:
            tracks = {
                "arm_r" if name != "copy" else "arm_l": R([
                    (0,z),(.9,z),(1.02,[-64,0,sign*14]),(2.3,[-64,0,sign*14]),
                    (2.42,[-78,0,sign*5]),(3.2,[-78,0,sign*5])
                ]),
                "halo_outer": R([(0,z),(2.3,z),(2.42,[0,0,sign*48]),(3.2,[0,0,sign*48])]),
            }
            for i, n in enumerate(aux[:6]):
                tracks[n] = R([(0,z),(1.02,z),(1.16,[0,0,(18+i*4)*sign]),(2.5,[0,0,(18+i*4)*sign]),(3.2,z)])
            clip(name, 3.2 if name == "delete" else 2.8, tracks)

        clip("rewind", 4.2, {
            "head": R([(0,z),(1.1,z),(1.22,[8,-8,0]),(3.0,[8,-8,0]),(3.12,z),(4.2,z)]),
            "halo_inner": R([(0,z),(1.1,z),(1.22,[0,0,-90]),(3.0,[0,0,-90]),(3.12,[0,0,-180]),(4.2,[0,0,-180])]),
            "halo_outer": R([(0,z),(1.1,z),(1.22,[0,0,120]),(3.0,[0,0,120]),(3.12,[0,0,260]),(4.2,[0,0,260])]),
            **{n: R([(0,z),(1.22,z),(1.34,[0,0,(-25 if i%2 else 25)]),(3.0,[0,0,(-25 if i%2 else 25)]),(4.2,z)])
               for i,n in enumerate(frags)}
        })

        clip("gravity_shift", 3.6, {
            "root": R([(0,z),(1.0,z),(1.12,[0,0,28]),(2.4,[0,0,28]),(2.52,[0,0,86]),(3.6,[0,0,86])]),
            "arm_l": R([(0,z),(1.0,z),(1.12,[-52,0,20]),(3.6,[-52,0,20])]),
            "arm_r": R([(0,z),(1.0,z),(1.12,[-52,0,-20]),(3.6,[-52,0,-20])]),
            **{n: R([(0,z),(1.12,z),(1.24,[0,0,16 if i%2 else -16]),(3.6,[0,0,16 if i%2 else -16])])
               for i,n in enumerate(robe)}
        })

        arena = {
            "arm_l": R([(0,z),(1.1,z),(1.22,[-62,0,24]),(2.6,[-62,0,24]),
                        (2.74,[-35,0,48]),(4.8,[-35,0,48]),(5.4,z)]),
            "arm_r": R([(0,z),(1.1,z),(1.22,[-62,0,-24]),(2.6,[-62,0,-24]),
                        (2.74,[-35,0,-48]),(4.8,[-35,0,-48]),(5.4,z)]),
            "halo_inner": R([(0,z),(2.6,z),(2.74,[0,0,70]),(4.8,[0,0,70]),(5.4,[0,0,90])]),
            "halo_outer": R([(0,z),(2.6,z),(2.74,[0,0,-90]),(4.8,[0,0,-90]),(5.4,[0,0,-120])]),
            "authority_core": S([(0,[1,1,1]),(2.6,[1,1,1]),(2.74,[1.45,1.12,1.45]),
                                 (4.8,[1.45,1.12,1.45]),(5.4,[1,1,1])]),
        }
        for i,n in enumerate(aux):
            arena[n] = R([(0,z),(1.22,z),(1.34,[0,0,(24+i*3) * (-1 if "_l_" in n else 1)]),
                          (4.8,[0,0,(24+i*3) * (-1 if "_l_" in n else 1)]),(5.4,z)])
        clip("arena_rewrite", 5.4, arena)

        clip("authority_beam", 3.8, {
            "arm_l": R([(0,z),(.9,z),(1.02,[-86,0,5]),(3.0,[-86,0,5]),(3.14,[-40,0,3]),(3.8,z)]),
            "arm_r": R([(0,z),(.9,z),(1.02,[-86,0,-5]),(3.0,[-86,0,-5]),(3.14,[-40,0,-3]),(3.8,z)]),
            "authority_core": S([(0,[1,1,1]),(.9,[1,1,1]),(1.02,[1.55,1.18,1.55]),
                                 (3.0,[1.55,1.18,1.55]),(3.14,[.8,.9,.8]),(3.8,[1,1,1])]),
        })

        clip("false_mercy", 3.5, {
            "head": R([(0,z),(.8,z),(.92,[4,-6,0]),(2.0,[4,-6,0]),(2.12,[-2,3,0]),(3.5,[-2,3,0])]),
            "arm_r": R([(0,z),(.8,z),(.92,[-46,0,-10]),(2.0,[-46,0,-10]),(2.12,[-78,0,-4]),(3.5,[-78,0,-4])]),
            "halo_inner": R([(0,z),(2.0,z),(2.12,[0,0,35]),(3.5,[0,0,35])]),
        })

        collapse = {
            "body": P([(0,z),(1.8,z),(1.92,[0,-.8,0]),(3.6,[0,-.8,0]),
                       (3.75,[0,-2.4,0]),(5.5,[0,-2.4,0]),(5.67,[0,-5.8,0]),(7.0,[0,-5.8,0])]),
            "head": R([(0,z),(3.6,z),(3.75,[12,0,0]),(5.5,[12,0,0]),(5.67,[28,0,0]),(7.0,[28,0,0])]),
            "halo_inner": S([(0,[1,1,1]),(3.6,[1,1,1]),(3.75,[1.15,.85,1.15]),
                             (5.5,[1.15,.85,1.15]),(5.67,[.06,.06,.06]),(7,[.06,.06,.06])]),
            "halo_outer": S([(0,[1,1,1]),(3.6,[1,1,1]),(3.75,[1.3,.7,1.3]),
                             (5.5,[1.3,.7,1.3]),(5.67,[.03,.03,.03]),(7,[.03,.03,.03])]),
        }
        for i,n in enumerate(frags):
            collapse[n] = P([(0,z),(3.6,z),(3.75,[math.cos(i)*2.0, math.sin(i)*2.0, 1.0]),
                             (5.5,[math.cos(i)*2.0, math.sin(i)*2.0, 1.0]),
                             (5.67,[math.cos(i)*8.0, math.sin(i)*7.0, 6.0]),
                             (7.0,[math.cos(i)*10.0, math.sin(i)*9.0, 8.0])])
        for i,n in enumerate(slabs):
            collapse[n] = P([(0,z),(5.5,z),(5.67,[(-1)**i * (1+i*.4), -i*.8, i*.6]),
                              (7.0,[(-1)**i * (2+i*.6), -i*1.2, i])])
        clip("final_collapse", 7.0, collapse)

    return out


def postpaint(im, e):
    """Small authored pixel accents after procedural per-face material shading."""
    dr = ImageDraw.Draw(im)
    w, h = im.size
    gold = (184, 150, 79, 255)
    violet = (120, 96, 179, 255)
    for x in range(8, min(w - 8, 96), 12):
        dr.point((x, h - 5), fill=gold if x % 24 else violet)
    return im


def build_one(e, r):
    if e["id"] in {"aion", "aion_the_architect"}:
        factor = 1.0
        e["size"] = 2.0
    else:
        axis = 1
        lo = min(p["origin"][axis] for p in r.parts)
        hi = max(p["origin"][axis] + p["size"][axis] for p in r.parts)
        factor = e["size"] * 16 / (hi - lo)

    e["recipe_scale"] = factor
    r.scaled(factor)

    im = postpaint(paint_atlas(e, r), e)
    tex = ROOT / e["texture"]
    tex.parent.mkdir(parents=True, exist_ok=True)
    im.save(tex)

    anim = animate_aion(e, r)
    dump(ROOT / e["geometry"], geometry(e, r))
    dump(ROOT / e["source"], bbmodel(e, r, tex, anim))
    dump(RP / f'animations/unwritten/{e["id"]}.animation.json',
         {"format_version": "1.8.0", "animations": anim})

    client_path = RP / f'entity/{e["id"]}.entity.json'
    if client_path.exists():
        client = json.loads(client_path.read_text())
        desc = client["minecraft:client_entity"]["description"]
        desc["animations"] = {k.rsplit(".", 1)[-1]: k for k in anim}
        desc["animations"]["locomotion"] = f'controller.animation.unwritten.{e["id"]}'
        dump(client_path, client)

    e.update(
        status="aion_highend_pass_2",
        rig_bones=len(r.bones),
        cubes=len(r.parts),
        animations=[k.rsplit(".", 1)[-1] for k in anim],
        texture_layout="AION pass 2 procedural per-face authored shading; no pasted concept art",
        animation_language="12fps-style held poses with 1-frame snap transitions and delayed secondary motion",
        limitations=[
            "Blockbench structural validation is automated; final Bedrock lighting/VFX still needs in-game art review.",
            "Gameplay authority effects, camera cuts and hit timing remain separate from the model source.",
        ],
    )
    return {
        "id": e["id"],
        "cubes": len(r.parts),
        "rig_bones": len(r.bones),
        "texture_width": e.get("texture_width"),
        "texture_height": e.get("texture_height"),
        "animations": e["animations"],
        "animation_language": e["animation_language"],
    }


def build():
    catalog_path = ROOT / "catalog/assets.json"
    catalog = json.loads(catalog_path.read_text())
    wanted = {
        "aion_prologue": reliquary,
        "aion": lambda: aion_humanoid(False),
        "aion_the_architect": lambda: aion_humanoid(True),
    }
    report = []
    for e in catalog["entries"]:
        builder = wanted.get(e["id"])
        if builder:
            report.append(build_one(e, builder()))
    dump(catalog_path, catalog)
    dump(ROOT / "docs/aion-art-report.json", report)
    print(json.dumps({"aion_highend_pass": 2, "forms": len(report), "report": report}, indent=2))


if __name__ == "__main__":
    build()
