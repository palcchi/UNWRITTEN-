#!/usr/bin/env python3
"""Validated finalizer for AION motion v3.

Runs the bespoke motion pass, normalizes inherited clip lengths, writes
AION-specific locomotion controllers, then repacks the Bedrock bundles so the
committed Blockbench/RP sources and .mcpack output are exactly the same build.
"""

import zipfile
import build_aion_motion as motion
from build_assets import BP

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


def repack(folder, filename):
    target = ah.ROOT / 'dist' / filename
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(folder.rglob('*')):
            if not path.is_file():
                continue
            info = zipfile.ZipInfo(str(path.relative_to(folder)), date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, path.read_bytes())


ah.animate_aion = final_motion

if __name__ == '__main__':
    ah.build()
    write_controller('aion')
    write_controller('aion_the_architect')
    repack(ah.RP, 'UNWRITTEN_Assets.mcpack')
    repack(BP, 'UNWRITTEN_Preview.mcpack')
