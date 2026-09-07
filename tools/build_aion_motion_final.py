#!/usr/bin/env python3
"""Validated finalizer for AION motion v3.

Runs the bespoke motion pass, normalizes inherited clip lengths, then writes
AION-specific locomotion controllers with distinct idle/walk/run states.
"""

import build_aion_motion as motion

ah = motion.ah
BASE_MOTION = motion.animate_motion


def normalize_animation_lengths(out):
    for anim in out.values():
        max_t = 0.0
        for bone_track in anim.get('bones', {}).values():
            for channel in ('rotation', 'position', 'scale'):
                keys = bone_track.get(channel)
                if isinstance(keys, dict):
                    for key in keys:
                        try:
                            max_t = max(max_t, float(key))
                        except (TypeError, ValueError):
                            pass
        anim['animation_length'] = max(float(anim.get('animation_length', 0)), max_t)
    return out


def final_motion(e, r):
    return normalize_animation_lengths(BASE_MOTION(e, r))


def write_controller(asset_id):
    # Tight blend times preserve the stepped pose language instead of smoothing it away.
    controller = {
        'format_version': '1.10.0',
        'animation_controllers': {
            f'controller.animation.unwritten.{asset_id}': {
                'initial_state': 'idle',
                'states': {
                    'idle': {
                        'animations': ['idle'],
                        'transitions': [
                            {'run': 'query.modified_move_speed > 0.42'},
                            {'walk': 'query.modified_move_speed > 0.01'},
                        ],
                        'blend_transition': 0.04,
                    },
                    'walk': {
                        'animations': ['walk'],
                        'transitions': [
                            {'run': 'query.modified_move_speed > 0.42'},
                            {'idle': 'query.modified_move_speed <= 0.01'},
                        ],
                        'blend_transition': 0.04,
                    },
                    'run': {
                        'animations': ['run'],
                        'transitions': [
                            {'walk': 'query.modified_move_speed <= 0.42 && query.modified_move_speed > 0.01'},
                            {'idle': 'query.modified_move_speed <= 0.01'},
                        ],
                        'blend_transition': 0.03,
                    },
                },
            }
        },
    }
    ah.dump(
        ah.RP / f'animation_controllers/unwritten/{asset_id}.controller.json',
        controller,
    )


ah.animate_aion = final_motion

if __name__ == '__main__':
    ah.build()
    write_controller('aion')
    write_controller('aion_the_architect')
