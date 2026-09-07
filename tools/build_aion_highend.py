#!/usr/bin/env python3
"""High-end bespoke AION art pass.

Runs after tools/build_colossi.py and only overwrites:
- aion_prologue
- aion
- aion_the_architect

The geometry stays Minecraft-readable and player-scaled for humanoid forms.
Textures are procedurally painted per-face. No pasted concept art or photo UVs.
"""

import json
import math

from PIL import ImageDraw

from build_assets import ROOT, RP, dump, geometry, bbmodel
from build_colossi import Sculpt, M, paint_atlas


# AION-only semantic materials. Kept deterministic so rebuilding never changes the look.
M.update({
    "aion_void": ("#05060a", "stone"),
    "aion_black": ("#11141b", "cloth"),
    "aion_graphite": ("#242a35", "metal"),
    "aion_ink": ("#090a0f", "flat"),
    "aion_ivory": ("#d8d4c9", "cloth"),
    "aion_skin": ("#c9c2b7", "skin"),
    "aion_hair": ("#d8d8d2", "hair"),
    "aion_gold": ("#b99a52", "metal"),
    "aion_gold_glow": ("#f0d486", "glow"),
    "aion_violet": ("#7665a8", "glow"),
    "aion_cold": ("#9aa9b5", "metal"),
})


def _uuidless_ring(r, bone, center, radius, thickness, mat, count=24, gaps=()):
    r.ring(bone, center, radius, thickness, mat, count=count, gaps=gaps)


def aion_orb_highend():
    """Prologue form: a black object, readable as a sphere but not as a creature."""
    r = Sculpt()
    r.bones[1]["pivot"] = [0, 14, 0]

    # Layered voxel latitude bands. Dense enough to read round from gameplay distance,
    # still unmistakably Minecraft geometry when approached.
    radius = 8.0
    slices = 22
    columns = 14
    for j in range(slices):
        yy = -radius + (j + 0.5) * (radius * 2 / slices)
        rr = math.sqrt(max(0.08, radius * radius - yy * yy))
        for k in range(columns):
            xx = -rr + (k + 0.5) * (rr * 2 / columns)
            zz = math.sqrt(max(0.08, rr * rr - xx * xx))
            w = max(0.22, rr * 2 / columns + 0.03)
            r.add(
                "body",
                (xx - w / 2, 14 + yy - 0.37, -zz),
                (w, 0.78, zz * 2),
                "aion_void",
            )

    # A second, slightly offset inner shell prevents flat black faces when the camera moves.
    for j in range(8):
        a = math.tau * j / 8
        x, y = math.cos(a) * 4.8, 14 + math.sin(a) * 4.8
        r.add("body", (x - 0.45, y - 0.45, -6.7), (0.9, 0.9, 13.4), "aion_ink", (0, 0, j * 11), (x, y, 0))

    # Orbiting fragments are intentionally almost black. The player notices movement,
    # not "magic particles". This keeps AION unreadable in the White Beginning.
    for i in range(12):
        a = math.tau * i / 12
        rad = 10.4 + (i % 3) * 0.45
        x = math.cos(a) * rad
        y = 14 + math.sin(a) * (9.5 + (i % 2) * 0.7)
        z = math.sin(i * 1.71) * 2.8
        n = f"fragment_{i}"
        r.joint(n, (x, y, z))
        r.add(n, (x - 0.28, y - 1.1, z - 0.22), (0.56, 2.2, 0.44), "aion_black", (i * 7, i * 13, i * 23), (x, y, z))

    # One tiny cold-violet seam only becomes visible at very close range.
    r.joint("seam", (0, 14, -8))
    r.add("seam", (-0.09, 11.5, -8.15), (0.18, 5.0, 0.16), "aion_violet", (0, 0, 7), (0, 14, -8))
    return r


def _steve_base(r, architect=False):
    """Player-sized Minecraft silhouette with split bones for cleaner animation."""
    # Minecraft player proportions: head 8x8, torso 8x12, arms/legs 4x12.
    r.bones[1]["pivot"] = [0, 12, 0]

    r.add("body", (-4, 12, -2), (8, 12, 4), "aion_black" if not architect else "aion_ivory")

    r.joint("neck", (0, 24, 0), "body")
    r.joint("head", (0, 24, 0), "neck")
    r.add("head", (-4, 24, -4), (8, 8, 8), "aion_graphite" if not architect else "aion_skin")

    for side, label in [(-1, "l"), (1, "r")]:
        x = side * 6
        r.joint(f"arm_{label}", (x, 24, 0), "body")
        r.add(f"arm_{label}", (x - 2, 12, -2), (4, 12, 4), "aion_black" if not architect else "aion_ivory")

        r.joint(f"hand_{label}", (x, 12, 0), f"arm_{label}")
        r.add(f"hand_{label}", (x - 1.65, 10.4, -1.65), (3.3, 1.8, 3.3), "aion_graphite" if not architect else "aion_skin")

        # Three visible finger blocks, enough for snap/gesture silhouettes without
        # turning Minecraft hands into tiny realism sculptures.
        for j in range(3):
            fn = f"finger_{label}_{j}"
            fx = x - 1.2 + j * 1.15
            r.joint(fn, (fx, 10.6, -1.3), f"hand_{label}")
            r.add(fn, (fx - 0.35, 9.25, -1.55), (0.7, 1.5, 0.8), "aion_graphite" if not architect else "aion_skin")

        lx = side * 2
        r.joint(f"leg_{label}", (lx, 12, 0), "body")
        r.add(f"leg_{label}", (lx - 2, 0, -2), (4, 12, 4), "aion_black" if not architect else "aion_ivory")
        r.joint(f"foot_{label}", (lx, 1.5, -1.4), f"leg_{label}")
        r.add(f"foot_{label}", (lx - 2, 0, -3.1), (4, 2, 5.1), "aion_graphite" if not architect else "aion_black")


def _aion_hair(r, architect=False):
    # Blocky white/silver hair with actual layered geometry instead of a flat head skin.
    base = "aion_hair" if architect else "aion_cold"
    r.add("head", (-4.18, 30.4, -4.05), (8.36, 1.65, 8.1), base)
    for i in range(9):
        x = -4.0 + i * 0.98
        drop = (i % 3) * 0.55
        r.add("head", (x, 27.8 - drop, -4.3), (1.05, 3.2 + drop, 0.65), base, (0, 0, (i % 3 - 1) * 8), (x + 0.5, 30.5, -4))
    for side in [-1, 1]:
        x = side * 3.9
        r.add("head", (x - 0.65, 25.2, -2.6), (1.3, 5.5, 4.3), base, (0, 0, -side * 5), (x, 30, 0))


def _aion_robe(r, architect=False):
    # Split robe panels animate individually. The body remains player-readable.
    cloth = "aion_ivory" if architect else "aion_black"
    trim = "aion_gold" if architect else "aion_graphite"
    glow = "aion_gold_glow" if architect else "aion_violet"

    # High collar and shoulder mantle.
    for side in [-1, 1]:
        r.add("body", (side * 3.0 - 1.15, 22.0, -2.8), (2.3, 4.6, 5.6), trim, (0, 0, -side * 14), (side * 3.0, 23.5, 0))
        r.add("body", (side * 4.25 - 1.1, 20.7, -0.2), (2.2, 2.5, 4.0), "aion_graphite", (0, 0, side * 20), (side * 4.2, 22, 0))

    # Chest authority line, tiny and surgical rather than neon armor.
    r.add("body", (-0.16, 15.0, -2.34), (0.32, 7.8, 0.26), glow)
    r.add("body", (-2.8, 21.5, -2.28), (5.6, 0.28, 0.24), trim)

    # Belt-like geometric lock.
    r.add("body", (-3.4, 11.5, -2.25), (6.8, 0.65, 4.5), "aion_graphite")
    r.add("body", (-0.8, 11.2, -2.6), (1.6, 1.2, 0.35), trim)

    # Front and back robe strips.
    for i in range(7):
        x = -3.25 + i * 1.08
        n = f"robe_front_{i}"
        r.joint(n, (x, 12, -2.1), "body")
        y0 = 1.2 + (i % 3) * 0.45
        r.add(n, (x - 0.48, y0, -2.55), (0.96, 10.8 - (i % 3) * 0.45, 0.5), cloth)
        if i in {0, 3, 6}:
            r.add(n, (x - 0.09, y0 + 0.4, -2.83), (0.18, 9.8, 0.18), trim)

        bn = f"robe_back_{i}"
        r.joint(bn, (x, 12, 2.1), "body")
        r.add(bn, (x - 0.48, y0 + 0.3, 2.15), (0.96, 10.4, 0.42), cloth)

    # Long broken mantle behind, asymmetrical to avoid angel/king silhouette.
    for i in range(5):
        x = -3.0 + i * 1.5
        n = f"mantle_{i}"
        r.joint(n, (x, 23.3, 2.25), "body")
        length = 14.0 - (i % 2) * 2.2
        r.add(n, (x - 0.72, 23.3 - length, 2.3), (1.44, length, 0.38), cloth, (3 + i, 0, 0), (x, 23.3, 2.3))


def _aion_face(r, architect=False):
    if architect:
        # Half the face is literally absent/void. The other half retains AION's identity.
        r.add("head", (0.1, 24.2, -4.45), (3.75, 7.2, 0.55), "aion_void")
        r.add("head", (-3.25, 27.4, -4.42), (2.1, 0.55, 0.22), "aion_gold_glow")
        r.add("head", (-2.0, 26.0, -4.5), (0.45, 2.0, 0.22), "aion_gold")
        for j in range(3):
            r.add("head", (0.55 + j * 0.75, 25.1 + j * 1.25, -4.75), (0.22, 2.1, 0.22), "aion_gold", (0, 0, -24), (1.0 + j * 0.75, 26, -4.5))
    else:
        # Face mostly unreadable. Two very thin authority eyes and a dark brow.
        r.add("head", (-3.35, 27.4, -4.26), (2.35, 0.42, 0.18), "aion_gold_glow")
        r.add("head", (1.0, 27.4, -4.26), (2.35, 0.42, 0.18), "aion_gold_glow")
        r.add("head", (-3.65, 28.35, -4.22), (7.3, 0.7, 0.22), "aion_ink")
        r.add("head", (-0.22, 25.5, -4.25), (0.44, 1.4, 0.18), "aion_graphite")


def _halo_and_orb(r, architect=False):
    # The black prologue sphere is now recognized as AION's core.
    r.joint("core_orb", (0, 27.5, 6.2), "body")
    r.add("core_orb", (-2.1, 25.4, 4.1), (4.2, 4.2, 4.2), "aion_void")

    r.joint("halo", (0, 27.5, 6.0), "body")
    radius = 11.0 if architect else 8.3
    gaps = (1, 4, 8, 12, 17, 21) if architect else (3, 12, 20)
    _uuidless_ring(r, "halo", (0, 27.5, 6.0), radius, 0.28 if architect else 0.22,
                   "aion_gold" if architect else "aion_graphite", 28, gaps)

    if not architect:
        # Only three cold-gold markers on the ring. Form stays dark.
        for a in (0.15, 2.25, 4.35):
            x = math.cos(a) * radius
            y = 27.5 + math.sin(a) * radius
            r.add("halo", (x - 0.25, y - 0.25, 5.72), (0.5, 0.5, 0.5), "aion_gold_glow")
    else:
        # Architect geometry is larger and intentionally incomplete.
        r.joint("outer_halo", (0, 27.5, 7.0), "body")
        _uuidless_ring(r, "outer_halo", (0, 27.5, 7.0), 15.0, 0.34, "aion_gold", 32, (0, 3, 7, 11, 16, 20, 26, 30))


def aion_humanoid_highend(architect=False):
    r = Sculpt()
    _steve_base(r, architect=architect)
    _aion_hair(r, architect=architect)
    _aion_face(r, architect=architect)
    _aion_robe(r, architect=architect)
    _halo_and_orb(r, architect=architect)

    if architect:
        # Separate torso slabs create the "world editor" body without changing player scale.
        # Remove only the main body cube, keep robe/collar details.
        r.parts = [p for p in r.parts if not (
            p["bone"] == "body" and p["origin"] == [-4, 12, -2] and p["size"] == [8, 12, 4]
        )]
        for i, y in enumerate((12.3, 16.2, 20.1)):
            n = f"torso_fragment_{i}"
            r.joint(n, (0, y + 1.4, 0), "body")
            r.add(n, (-3.8, y, -1.9), (7.6, 2.5, 3.8), "aion_ivory")
            r.add(n, (-0.12, y + 0.2, -2.2), (0.24, 2.0, 0.25), "aion_gold")

        # Two additional floating arm pairs. They are geometric extensions, not anatomy.
        for pair in range(2):
            for side, label in [(-1, "l"), (1, "r")]:
                x = side * (8.1 + pair * 1.9)
                y = 22.2 - pair * 4.2
                n = f"extra_arm_{label}_{pair}"
                r.joint(n, (x, y, 2.6), "body", (0, 0, side * (28 + pair * 16)))
                r.add(n, (x - 1.0, y - 5.0, 1.5), (2.0, 5.2, 2.2), "aion_ivory", (0, 0, side * (28 + pair * 16)), (x, y, 2.6))
                r.add(n, (x - 1.2, y - 6.0, 1.25), (2.4, 1.5, 2.6), "aion_black")

        # Authority fragments orbit like pieces of a UI/world rather than wings.
        for i in range(10):
            a = math.tau * i / 10
            x = math.cos(a) * 12.8
            y = 21.5 + math.sin(a) * 10.5
            z = 6.0 + math.sin(i * 1.37) * 2.0
            n = f"authority_fragment_{i}"
            r.joint(n, (x, y, z), "body")
            r.add(n, (x - 0.45, y - 2.4, z - 0.3), (0.9, 4.8, 0.6), "aion_black", (i * 5, i * 11, i * 31), (x, y, z))
            r.add(n, (x - 0.12, y - 1.9, z - 0.48), (0.24, 3.8, 0.18), "aion_gold_glow", (0, 0, i * 31), (x, y, z))

    return r


def animate_aion(e, r):
    aid = e["id"]
    scale = e["recipe_scale"]
    out = {}

    def k(seq):
        return {str(t): v for t, v in seq}

    def R(seq):
        return {"rotation": k(seq)}

    def P(seq):
        return {"position": k([(t, [q * scale for q in v]) for t, v in seq])}

    def S(seq):
        return {"scale": k(seq)}

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
        tracks = {"body": P([(0, z), (2.0, [0, 0.45, 0]), (4.0, z)])}
        for i in range(12):
            tracks[f"fragment_{i}"] = R([(0, z), (2, [i * 0.8, i * 2.2, 8 + i * 0.7]), (4, z)])
        clip("idle", 4.0, tracks, True)
        clip("presence_pulse", 2.4, {
            "body": S([(0, [1, 1, 1]), (0.8, [1.025, 0.98, 1.025]), (1.3, [0.992, 1.02, 0.992]), (2.4, [1, 1, 1])]),
            "seam": S([(0, [0.5, 0.5, 0.5]), (1.0, [1.4, 1.0, 1.0]), (2.4, [0.5, 0.5, 0.5])]),
        }, True)
        clip("reveal_cue", 3.4, {
            "body": S([(0, [1, 1, 1]), (1.5, [1.12, 0.92, 1.12]), (2.35, [0.55, 1.22, 0.55]), (3.4, [0.03, 0.03, 0.03])]),
            **{f"fragment_{i}": P([(0, z), (2.3, [math.cos(i) * 4.5, math.sin(i) * 4.0, 2]), (3.4, [math.cos(i) * 10.0, math.sin(i) * 9.0, 6])]) for i in range(12)}
        })
        return out

    robe_bones = [b["name"] for b in r.bones if b["name"].startswith(("robe_", "mantle_"))]
    fragment_bones = [b["name"] for b in r.bones if b["name"].startswith("authority_fragment_")]

    idle = {
        "body": P([(0, z), (1.8, [0, 0.22, 0]), (3.6, z)]),
        "head": R([(0, z), (1.8, [1.5, -1.5, 0]), (3.6, z)]),
        "halo": R([(0, z), (3.6, [0, 0, 360])]),
        "core_orb": R([(0, z), (3.6, [0, 180, 0])]),
    }
    if r.has("outer_halo"):
        idle["outer_halo"] = R([(0, z), (5.4, [0, 0, -360])])
    for i, n in enumerate(robe_bones):
        idle[n] = R([(0, [2 + i % 3, 0, 0]), (1.8, [4 + i % 4, 0, 0]), (3.6, [2 + i % 3, 0, 0])])
    for i, n in enumerate(fragment_bones):
        idle[n] = R([(0, z), (3.6, [0, (i + 1) * 16, 18 if i % 2 else -18])])
    clip("idle", 3.6, idle, True)

    clip("turn", 1.4, {
        "body": R([(0, z), (0.7, [0, 28, 0]), (1.4, z)]),
        "head": R([(0, z), (0.45, [0, 35, 0]), (1.4, z)]),
        "halo": R([(0, z), (1.4, [0, 0, 90])]),
    })

    clip("hand_raise", 1.6, {
        "arm_r": R([(0, z), (0.8, [-78, 0, -10]), (1.6, [-82, 0, -8])]),
        "hand_r": R([(0, z), (0.8, [12, 0, 0]), (1.6, [8, 0, 0])]),
        "head": R([(0, z), (1.0, [0, -8, 0]), (1.6, [0, -8, 0])]),
    })

    clip("finger_snap", 0.9, {
        "arm_r": R([(0, z), (0.35, [-82, 0, -8]), (0.9, [-78, 0, -6])]),
        "finger_r_0": R([(0, z), (0.32, [0, 0, 28]), (0.42, [0, 0, -20]), (0.9, z)]),
        "finger_r_1": R([(0, z), (0.32, [0, 0, -18]), (0.42, [0, 0, 22]), (0.9, z)]),
        "halo": R([(0, z), (0.42, [0, 0, 55]), (0.9, [0, 0, 80])]),
    })

    clip("authority_grant", 3.0, {
        "arm_r": R([(0, z), (1.1, [-66, 0, -12]), (2.2, [-72, 0, -8]), (3, z)]),
        "arm_l": R([(0, z), (1.1, [-48, 0, 12]), (2.2, [-52, 0, 8]), (3, z)]),
        "halo": R([(0, z), (3, [0, 0, 180])]),
        "core_orb": S([(0, [1, 1, 1]), (1.4, [1.2, 1.2, 1.2]), (2.2, [0.92, 0.92, 0.92]), (3, [1, 1, 1])]),
    })

    clip("freeze_player", 1.8, {
        "arm_r": R([(0, z), (0.55, [-70, 0, -3]), (1.8, [-70, 0, -3])]),
        "head": R([(0, z), (0.6, [0, -10, 0]), (1.8, [0, -10, 0])]),
        "halo": R([(0, z), (0.6, [0, 0, 35]), (1.8, [0, 0, 35])]),
    })

    clip("remove_authority", 2.8, {
        "arm_r": R([(0, z), (0.7, [-80, 0, -14]), (1.35, [-38, 0, 22]), (2.8, z)]),
        "core_orb": S([(0, [1, 1, 1]), (1.35, [0.78, 0.78, 0.78]), (2.0, [1.18, 1.18, 1.18]), (2.8, [1, 1, 1])]),
        "halo": R([(0, z), (1.35, [0, 0, -100]), (2.8, [0, 0, -180])]),
    })

    clip("teleport", 1.1, {
        "root": P([(0, z), (0.38, [0, 0.8, 0]), (0.52, [0, 4.0, 0]), (0.7, [0, -2.0, 0]), (1.1, z)]),
        "body": S([(0, [1, 1, 1]), (0.46, [0.35, 1.18, 0.35]), (0.6, [0.04, 1.5, 0.04]), (0.72, [0.35, 1.18, 0.35]), (1.1, [1, 1, 1])]),
    })

    clip("subtle_smile", 2.4, {
        "head": R([(0, z), (1.2, [0, -5, 0]), (2.4, z)]),
    })

    if aid == "aion_the_architect":
        clip("delete", 2.2, {
            "arm_r": R([(0, z), (0.7, [-72, 0, -16]), (1.2, [-80, 0, -8]), (2.2, z)]),
            "outer_halo": R([(0, z), (1.2, [0, 0, 140]), (2.2, [0, 0, 190])]),
            **{n: S([(0, [1, 1, 1]), (1.2, [0.7, 1.35, 0.7]), (2.2, [1, 1, 1])]) for n in fragment_bones[:5]},
        })

        clip("copy", 1.8, {
            "arm_l": R([(0, z), (0.6, [-60, 0, 12]), (1.8, z)]),
            "halo": R([(0, z), (0.9, [0, 0, 90]), (1.8, [0, 0, 180])]),
        })

        clip("paste", 1.8, {
            "arm_r": R([(0, z), (0.6, [-60, 0, -12]), (1.8, z)]),
            "outer_halo": R([(0, z), (0.9, [0, 0, -90]), (1.8, [0, 0, -180])]),
        })

        clip("rewind", 3.0, {
            "halo": R([(0, z), (3.0, [0, 0, -540])]),
            "outer_halo": R([(0, z), (3.0, [0, 0, 720])]),
            "body": R([(0, z), (1.5, [0, -15, 0]), (3, z)]),
        })

        clip("gravity_shift", 2.6, {
            "root": R([(0, z), (1.3, [0, 0, 180]), (2.6, [0, 0, 360])]),
            "halo": R([(0, z), (2.6, [0, 180, 180])]),
            "outer_halo": R([(0, z), (2.6, [180, 0, -180])]),
        })

        clip("arena_rewrite", 4.2, {
            "arm_l": R([(0, z), (1.0, [-68, 0, 20]), (3.0, [-40, 0, 35]), (4.2, z)]),
            "arm_r": R([(0, z), (1.0, [-68, 0, -20]), (3.0, [-40, 0, -35]), (4.2, z)]),
            "halo": R([(0, z), (4.2, [0, 0, 360])]),
            "outer_halo": R([(0, z), (4.2, [0, 0, -360])]),
            **{n: R([(0, z), (2.1, [0, 0, 90 if i % 2 else -90]), (4.2, z)]) for i, n in enumerate(fragment_bones)},
        })

        clip("authority_beam", 3.4, {
            "arm_r": R([(0, z), (0.9, [-88, 0, -4]), (2.6, [-88, 0, -4]), (3.4, z)]),
            "arm_l": R([(0, z), (0.9, [-88, 0, 4]), (2.6, [-88, 0, 4]), (3.4, z)]),
            "core_orb": S([(0, [1, 1, 1]), (1.4, [1.5, 1.5, 1.5]), (2.6, [1.65, 1.65, 1.65]), (3.4, [1, 1, 1])]),
        })

        clip("final_collapse", 5.2, {
            "body": P([(0, z), (2.0, [0, -1.0, 0]), (5.2, [0, -6.0, 0])]),
            "head": R([(0, z), (3.0, [10, 0, 0]), (5.2, [26, 0, 0])]),
            "halo": S([(0, [1, 1, 1]), (3.0, [1.15, 0.85, 1.15]), (5.2, [0.04, 0.04, 0.04])]),
            "outer_halo": S([(0, [1, 1, 1]), (3.0, [1.3, 0.7, 1.3]), (5.2, [0.02, 0.02, 0.02])]),
            **{n: P([(0, z), (3.0, [math.cos(i) * 3.0, math.sin(i) * 3.0, 2]), (5.2, [math.cos(i) * 9.0, math.sin(i) * 8.0, 7])]) for i, n in enumerate(fragment_bones)}
        })

    return out


def postpaint_aion(im, e):
    """Add tiny authored atlas-wide accents without using external images."""
    dr = ImageDraw.Draw(im)
    # Corner registration marks make the texture feel intentionally authored while
    # never touching UV islands generated by paint_atlas' two-pixel padding.
    w, h = im.size
    gold = (185, 154, 82, 255)
    violet = (118, 101, 168, 255)
    for x in range(8, min(w - 8, 80), 12):
        dr.point((x, h - 5), fill=gold if x % 24 else violet)
    return im


def build_one(e, r):
    # Same scaling rule as build_colossi.py. Humanoid AION stays catalog/player sized.
    axis = 1
    lo = min(p["origin"][axis] for p in r.parts)
    hi = max(p["origin"][axis] + p["size"][axis] for p in r.parts)
    factor = e["size"] * 16 / (hi - lo)
    e["recipe_scale"] = factor
    r.scaled(factor)

    im = paint_atlas(e, r)
    im = postpaint_aion(im, e)
    tex = ROOT / e["texture"]
    tex.parent.mkdir(parents=True, exist_ok=True)
    im.save(tex)

    anim = animate_aion(e, r)
    g = geometry(e, r)

    dump(ROOT / e["geometry"], g)
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
        status="aion_highend_pass_1",
        rig_bones=len(r.bones),
        cubes=len(r.parts),
        animations=[k.rsplit(".", 1)[-1] for k in anim],
        texture_layout="AION bespoke procedural face islands; no pasted UV artwork",
        limitations=[
            "High-end AION pass; final in-game lighting/VFX tuning still belongs in the resource pack.",
            "Gameplay authority effects and phase logic are separate from the Blockbench source."
        ],
    )
    return {
        "id": e["id"],
        "cubes": len(r.parts),
        "rig_bones": len(r.bones),
        "texture_width": e.get("texture_width"),
        "texture_height": e.get("texture_height"),
        "animations": e["animations"],
    }


def build():
    catalog_path = ROOT / "catalog/assets.json"
    catalog = json.loads(catalog_path.read_text())

    wanted = {
        "aion_prologue": aion_orb_highend,
        "aion": lambda: aion_humanoid_highend(False),
        "aion_the_architect": lambda: aion_humanoid_highend(True),
    }

    report = []
    for e in catalog["entries"]:
        builder = wanted.get(e["id"])
        if not builder:
            continue
        report.append(build_one(e, builder()))

    dump(catalog_path, catalog)
    dump(ROOT / "docs/aion-art-report.json", report)
    print(json.dumps({"aion_highend_forms": len(report), "report": report}, indent=2))


if __name__ == "__main__":
    build()
