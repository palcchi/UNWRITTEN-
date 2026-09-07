#!/usr/bin/env python3
"""Final AION motion pass.

This script deliberately runs AFTER build_player_colossi.py so AION is never left
with generic Steve locomotion. It rebuilds AION from the bespoke high-end rig,
fixes left/right bone naming, then replaces/extends its animation set with a
stepped pose-to-pose motion language inspired by Minecraft cinematic readability.
"""

import math
import build_aion_highend as ah

ORIG_ANIMATE = ah.animate_aion
ORIG_HUMANOID = ah.aion_humanoid


def _swap_lr_name(name):
    return name.replace('_l', '__TMP_L').replace('_r', '_l').replace('__TMP_L', '_r')


def fix_lr(rig):
    """The old bespoke rig labelled negative-X limbs as left.

    Minecraft/Steve convention uses negative X for the right side. Swapping the
    labels fixes mirrored animation targeting without moving any geometry.
    """
    for bone in rig.bones:
        bone['name'] = _swap_lr_name(bone['name'])
        if 'parent' in bone:
            bone['parent'] = _swap_lr_name(bone['parent'])
    for part in rig.parts:
        part['bone'] = _swap_lr_name(part['bone'])
    return rig


def humanoid_fixed(architect=False):
    return fix_lr(ORIG_HUMANOID(architect))


def animate_motion(e, r):
    out = ORIG_ANIMATE(e, r)
    aid = e['id']
    if aid == 'aion_prologue':
        return out

    scale = e['recipe_scale']
    z = [0, 0, 0]

    def stepped(seq, snap=1/12):
        return ah.stepped(seq, snap=snap)

    def K(seq):
        return {str(t): v for t, v in stepped(seq)}

    def R(seq):
        return {'rotation': K(seq)}

    def P(seq):
        return {'position': K([(t, [q * scale for q in v]) for t, v in seq])}

    def S(seq):
        return {'scale': K(seq)}

    def clip(name, duration, tracks, loop=False):
        bones = {n: v for n, v in tracks.items() if r.has(n)}
        if bones:
            out[f'animation.unwritten.{aid}.{name}'] = {
                'loop': loop,
                'animation_length': duration,
                'bones': bones,
            }

    robe = [b['name'] for b in r.bones if b['name'].startswith(('robe_', 'mantle_', 'waist_side_'))]
    frags = [b['name'] for b in r.bones if b['name'].startswith('authority_fragment_')]
    aux = [b['name'] for b in r.bones if b['name'].startswith(('aux_arm_', 'aux_forearm_', 'aux_hand_'))]

    # WALK: controlled ceremonial stride. Head stays nearly level, upper body leads,
    # arms barely swing, robe follows one pose late. This is intentionally not Steve walk.
    walk = {
        'root': P([(0,z),(.32,[0,-.18,0]),(.66,z),(.98,[0,-.18,0]),(1.32,z)]),
        'body': R([(0,[1.5,-3,0]),(.32,[1.5,4,0]),(.66,[1.5,3,0]),(.98,[1.5,-4,0]),(1.32,[1.5,-3,0])]),
        'head': R([(0,[-1,2,0]),(.32,[-1,-2,0]),(.66,[-1,-1,0]),(.98,[-1,2,0]),(1.32,[-1,2,0])]),
        'leg_r': R([(0,[25,0,0]),(.32,[7,0,0]),(.66,[-20,0,0]),(.98,[-6,0,0]),(1.32,[25,0,0])]),
        'shin_r': R([(0,[-8,0,0]),(.32,[24,0,0]),(.66,[10,0,0]),(.98,[-2,0,0]),(1.32,[-8,0,0])]),
        'foot_r': R([(0,[3,0,0]),(.32,[-10,0,0]),(.66,[4,0,0]),(.98,[8,0,0]),(1.32,[3,0,0])]),
        'leg_l': R([(0,[-20,0,0]),(.32,[-6,0,0]),(.66,[25,0,0]),(.98,[7,0,0]),(1.32,[-20,0,0])]),
        'shin_l': R([(0,[10,0,0]),(.32,[-2,0,0]),(.66,[-8,0,0]),(.98,[24,0,0]),(1.32,[10,0,0])]),
        'foot_l': R([(0,[4,0,0]),(.32,[8,0,0]),(.66,[3,0,0]),(.98,[-10,0,0]),(1.32,[4,0,0])]),
        'arm_r': R([(0,[-8,0,-5]),(.66,[7,0,-3]),(1.32,[-8,0,-5])]),
        'forearm_r': R([(0,[-12,0,0]),(.66,[-6,0,0]),(1.32,[-12,0,0])]),
        'arm_l': R([(0,[6,0,4]),(.66,[-7,0,3]),(1.32,[6,0,4])]),
        'forearm_l': R([(0,[-6,0,0]),(.66,[-12,0,0]),(1.32,[-6,0,0])]),
        'halo_inner': R([(0,z),(.66,[0,0,5]),(1.32,[0,0,10])]),
        'halo_outer': R([(0,z),(.66,[0,0,-3]),(1.32,[0,0,-6])]),
    }
    for i,n in enumerate(robe):
        lag = 4 + (i % 3) * 2
        walk[n] = R([(0,[lag,0,0]),(.32,[lag+5,0,0]),(.66,[lag-2,0,0]),(.98,[lag+5,0,0]),(1.32,[lag,0,0])])
    clip('walk', 1.32, walk, True)

    # WALK START / STOP make locomotion transitions feel authored instead of instantly switching loops.
    clip('walk_start', .72, {
        'body': R([(0,z),(.28,z),(.38,[3,-4,0]),(.72,[1.5,-3,0])]),
        'leg_r': R([(0,z),(.28,z),(.38,[21,0,0]),(.72,[25,0,0])]),
        'arm_r': R([(0,z),(.38,[-7,0,-4]),(.72,[-8,0,-5])]),
        'head': R([(0,z),(.38,[-1,2,0]),(.72,[-1,2,0])]),
    })
    clip('walk_stop', .88, {
        'body': R([(0,[1.5,-3,0]),(.34,[1.5,-3,0]),(.46,[-2,4,0]),(.66,[-2,4,0]),(.78,z),(.88,z)]),
        'leg_r': R([(0,[25,0,0]),(.34,[25,0,0]),(.46,[8,0,0]),(.78,z),(.88,z)]),
        'leg_l': R([(0,[-20,0,0]),(.34,[-20,0,0]),(.46,[-6,0,0]),(.78,z),(.88,z)]),
        'halo_inner': R([(0,z),(.46,[0,0,8]),(.88,[0,0,10])]),
    })

    # RUN: AION does not pump his arms like Steve. He leans forward and takes long,
    # clipped strides while robe/halo trail behind. The motion reads as controlled pursuit.
    run = {
        'root': P([(0,z),(.22,[0,-.35,0]),(.44,z),(.66,[0,-.35,0]),(.88,z)]),
        'body': R([(0,[10,-5,0]),(.22,[12,7,0]),(.44,[10,5,0]),(.66,[12,-7,0]),(.88,[10,-5,0])]),
        'head': R([(0,[-7,3,0]),(.22,[-8,-3,0]),(.44,[-7,-2,0]),(.66,[-8,3,0]),(.88,[-7,3,0])]),
        'leg_r': R([(0,[42,0,0]),(.22,[10,0,0]),(.44,[-34,0,0]),(.66,[-9,0,0]),(.88,[42,0,0])]),
        'shin_r': R([(0,[-14,0,0]),(.22,[38,0,0]),(.44,[18,0,0]),(.66,[-4,0,0]),(.88,[-14,0,0])]),
        'leg_l': R([(0,[-34,0,0]),(.22,[-9,0,0]),(.44,[42,0,0]),(.66,[10,0,0]),(.88,[-34,0,0])]),
        'shin_l': R([(0,[18,0,0]),(.22,[-4,0,0]),(.44,[-14,0,0]),(.66,[38,0,0]),(.88,[18,0,0])]),
        'arm_r': R([(0,[-28,0,-13]),(.44,[-18,0,-8]),(.88,[-28,0,-13])]),
        'forearm_r': R([(0,[-36,0,0]),(.44,[-28,0,0]),(.88,[-36,0,0])]),
        'arm_l': R([(0,[-15,0,12]),(.44,[-25,0,8]),(.88,[-15,0,12])]),
        'forearm_l': R([(0,[-24,0,0]),(.44,[-34,0,0]),(.88,[-24,0,0])]),
        'halo_inner': R([(0,[6,0,0]),(.44,[10,0,8]),(.88,[6,0,16])]),
        'halo_outer': R([(0,[-4,0,0]),(.44,[-8,0,-6]),(.88,[-4,0,-12])]),
    }
    for i,n in enumerate(robe):
        run[n] = R([(0,[16+i%3*3,0,0]),(.22,[24+i%3*4,0,0]),(.44,[10+i%3*2,0,0]),(.66,[26+i%3*4,0,0]),(.88,[16+i%3*3,0,0])])
    clip('run', .88, run, True)

    clip('run_start', .62, {
        'body': R([(0,z),(.18,z),(.28,[12,-5,0]),(.62,[10,-5,0])]),
        'head': R([(0,z),(.28,[-8,3,0]),(.62,[-7,3,0])]),
        'leg_r': R([(0,z),(.28,[36,0,0]),(.62,[42,0,0])]),
        'arm_r': R([(0,z),(.28,[-26,0,-12]),(.62,[-28,0,-13])]),
    })
    clip('run_stop', 1.05, {
        'body': R([(0,[10,-5,0]),(.32,[10,-5,0]),(.44,[-8,8,0]),(.70,[-8,8,0]),(.82,[3,0,0]),(1.05,z)]),
        'leg_r': R([(0,[42,0,0]),(.32,[42,0,0]),(.44,[14,0,0]),(.82,z),(1.05,z)]),
        'leg_l': R([(0,[-34,0,0]),(.32,[-34,0,0]),(.44,[-10,0,0]),(.82,z),(1.05,z)]),
        'arm_r': R([(0,[-28,0,-13]),(.44,[-46,0,-16]),(.82,[-12,0,-4]),(1.05,z)]),
        'halo_inner': R([(0,z),(.44,[0,0,16]),(1.05,[0,0,20])]),
    })

    # Pivot / directional read. AION turns from pelvis/chest first, head snaps last.
    for name,sgn in [('pivot_left',1),('pivot_right',-1)]:
        clip(name, 1.12, {
            'body': R([(0,z),(.34,z),(.46,[0,25*sgn,0]),(.82,[0,25*sgn,0]),(.94,[0,48*sgn,0]),(1.12,[0,48*sgn,0])]),
            'head': R([(0,z),(.70,z),(.82,[0,18*sgn,0]),(.94,[0,34*sgn,0]),(1.12,[0,34*sgn,0])]),
            'leg_r': R([(0,z),(.46,[8,0,3*sgn]),(1.12,[8,0,3*sgn])]),
            'leg_l': R([(0,z),(.46,[-6,0,-3*sgn]),(1.12,[-6,0,-3*sgn])]),
        })

    # Combat stance and movement. No sword-slash set: AION attacks with authority gestures.
    clip('combat_ready', 1.35, {
        'body': R([(0,z),(.46,z),(.58,[5,-8,0]),(1.35,[5,-8,0])]),
        'head': R([(0,z),(.58,[0,9,0]),(1.35,[0,9,0])]),
        'arm_r': R([(0,z),(.58,[-46,0,-18]),(1.35,[-46,0,-18])]),
        'forearm_r': R([(0,z),(.58,[-34,0,0]),(1.35,[-34,0,0])]),
        'arm_l': R([(0,z),(.58,[-18,0,14]),(1.35,[-18,0,14])]),
        'halo_inner': R([(0,z),(.58,[0,0,18]),(1.35,[0,0,18])]),
    })

    clip('palm_strike', 1.28, {
        'body': R([(0,[5,-8,0]),(.36,[5,-8,0]),(.46,[8,-18,0]),(.66,[8,-18,0]),(.75,[-2,14,0]),(.96,[-2,14,0]),(1.08,[4,-4,0]),(1.28,[5,-8,0])]),
        'arm_r': R([(0,[-46,0,-18]),(.36,[-46,0,-18]),(.46,[-70,-10,-24]),(.66,[-70,-10,-24]),(.75,[-92,8,-2]),(.96,[-92,8,-2]),(1.08,[-52,0,-12]),(1.28,[-46,0,-18])]),
        'forearm_r': R([(0,[-34,0,0]),(.66,[-34,0,0]),(.75,[-12,0,0]),(.96,[-12,0,0]),(1.28,[-34,0,0])]),
        'head': R([(0,[0,9,0]),(.66,[0,9,0]),(.75,[0,-8,0]),(.96,[0,-8,0]),(1.28,[0,9,0])]),
        'authority_core': S([(0,[1,1,1]),(.66,[1,1,1]),(.75,[1.25,1.05,1.25]),(.96,[1.25,1.05,1.25]),(1.28,[1,1,1])]),
    })

    clip('authority_sweep', 1.72, {
        'body': R([(0,[5,-8,0]),(.46,[5,-8,0]),(.58,[4,-28,0]),(.92,[4,-28,0]),(1.02,[2,34,0]),(1.32,[2,34,0]),(1.44,[5,-8,0]),(1.72,[5,-8,0])]),
        'arm_r': R([(0,[-46,0,-18]),(.46,[-46,0,-18]),(.58,[-82,-15,-38]),(.92,[-82,-15,-38]),(1.02,[-32,34,36]),(1.32,[-32,34,36]),(1.44,[-46,0,-18]),(1.72,[-46,0,-18])]),
        'halo_inner': R([(0,z),(.92,z),(1.02,[0,0,42]),(1.72,[0,0,42])]),
        'halo_outer': R([(0,z),(.92,z),(1.02,[0,0,-30]),(1.72,[0,0,-30])]),
    })

    clip('blink_step', .78, {
        'body': R([(0,[5,-8,0]),(.20,[5,-8,0]),(.30,[12,-12,-4]),(.44,[12,-12,-4]),(.52,[3,-4,2]),(.78,[5,-8,0])]),
        'root': P([(0,z),(.20,z),(.30,[0,0,1.2]),(.44,[0,0,1.2]),(.52,[0,0,4.8]),(.78,[0,0,4.8])]),
        'halo_inner': R([(0,z),(.30,[0,0,22]),(.52,[0,0,48]),(.78,[0,0,48])]),
    })

    clip('dodge_side', .86, {
        'body': R([(0,[5,-8,0]),(.22,[5,-8,0]),(.32,[12,-12,-10]),(.58,[12,-12,-10]),(.68,[4,-5,2]),(.86,[5,-8,0])]),
        'root': P([(0,z),(.22,z),(.32,[2.8,0,0]),(.58,[2.8,0,0]),(.68,[4.8,0,0]),(.86,[4.8,0,0])]),
        'head': R([(0,[0,9,0]),(.32,[-4,4,6]),(.68,[0,9,0]),(.86,[0,9,0])]),
    })

    # Bespoke hit/death aliases used by generic entity state controllers.
    clip('hurt', 1.08, {
        'body': R([(0,z),(.18,z),(.28,[-7,5,3]),(.52,[-7,5,3]),(.62,[3,-3,-1]),(.88,[3,-3,-1]),(1.08,z)]),
        'head': R([(0,z),(.28,[-10,-6,0]),(.52,[-10,-6,0]),(.62,[4,2,0]),(1.08,z)]),
        'halo_inner': R([(0,z),(.28,[0,0,-12]),(.62,[0,0,8]),(1.08,[0,0,8])]),
    })

    if aid == 'aion':
        clip('death', 4.8, {
            'body': R([(0,z),(1.2,z),(1.34,[6,0,0]),(2.4,[6,0,0]),(2.54,[15,0,0]),(3.6,[15,0,0]),(3.76,[28,0,0]),(4.8,[28,0,0])]),
            'root': P([(0,z),(2.4,z),(2.54,[0,-1.2,0]),(3.6,[0,-1.2,0]),(3.76,[0,-4.8,0]),(4.8,[0,-4.8,0])]),
            'halo_inner': S([(0,[1,1,1]),(3.6,[1,1,1]),(3.76,[.35,.35,.35]),(4.8,[.35,.35,.35])]),
            'halo_outer': S([(0,[1,1,1]),(3.6,[1,1,1]),(3.76,[.12,.12,.12]),(4.8,[.12,.12,.12])]),
        })

    # Remove names accidentally inherited from older generic player animation passes
    # if this script is ever changed to merge outputs instead of rebuilding them.
    for bad in ['slash_1','slash_2','slash_3','slash_4','slash_5','thrust_1','thrust_2','thrust_3','attack']:
        out.pop(f'animation.unwritten.{aid}.{bad}', None)

    return out


# Override the high-end module only for this final motion build.
ah.aion_humanoid = humanoid_fixed
ah.animate_aion = animate_motion

if __name__ == '__main__':
    ah.build()
