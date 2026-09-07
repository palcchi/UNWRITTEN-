# Decem Fata: bespoke art pass 02

Latest visual direction from the owner takes precedence over the earlier white-robed
AION concept. Prologue AION is an indistinct black spherical object, without face,
hair, limbs or visible human identity. AION's revealed humanoid is dark and mysterious.
The Architect is an evolution of that dark appearance, not a switch to white robes.
Little Morrow is a cool miniature dragon with an original compact body, not a
scaled adult dragon and not a generic round mascot.

## Delivered forms

20 rebuilt forms: Vharos, Dullahan and his horse, Caelum, Elara, both Kael forms,
Orun, both Seraphiel forms, Nameless Knight, Thalassia, both Verdant forms,
Morrow Anomaly, Little Morrow, True Morrow, AION orb, humanoid AION and Architect.
Detached weapons, old Orun component props and armor-display props are still v0.1;
they must be re-fitted to the new body/socket dimensions before use as attachments.

| Character | Distinct visual work |
| :--- | :--- |
| Vharos | Long plated neck, broad ribcage, heavy limbs, separate jaw and teeth, claws, dorsal spines, asymmetric horns, torn membrane sections and ancient spears |
| Dullahan | Layered dark armor, open spectral neck, a held head parented to the left hand, cloth strips and chain links; skeletal horse has separate lower-leg joints |
| Caelum | Worn gold armor, cracked breastplate, cloth layers, pale hair and a restrained human face |
| Kael | Same face and dark hair in both forms; hunter bow/satchel versus horned king with six suspended shards, red coat and dark sword |
| Orun | Architectural armor, core ring, small stairs, shoulder terraces, pillars, fingers and ankle cores |
| Seraphiel | Layered knight armor and contrasting fallen form with six independently rooted wings, feather strips, tips and fragmented halo |
| Nameless Knight | Sealed narrow helmet, visor slit, restrained segmented armor, sword and articulated sash |
| Thalassia | Whale barrel, long tapering tail, jaw, teeth, six fins, broad fluke, coral, markings and embedded harpoons |
| Verdant | Giant branch/root anatomy and canopy; separate pale-wood humanoid with visible vine ribs, branch crown and hand-grown blade |
| Morrow | Unstable disconnected anomaly; independently sculpted compact companion; segmented dimensional adult with broken spatial ring |
| AION | Faceless black orb with hovering fragments; dark humanoid with split collar; Architect with separated torso sections, multiple arms and orbiting pieces |

## Modeling and texture method

Geometry is editable Bedrock cuboid sculpture, including rotated cube segments.
No mesh is a rendered concept image. Horn/root/bone segments are oriented to join
their intended endpoints. Material groups distinguish scale, membrane, cloth,
metal, skin, bark, stone, feather and bright accent. Every cube face has a separate
padded UV island. Larger atlases are packed according to the geometry, not merely
upscaled from the old shared swatch texture. Resolution and counts are listed in
`colossi-art-report.json`.

Large texture dimensions do not alone imply final art quality. These textures are
procedural pixel painting with direction-sensitive shading, edge wear, overlapping
scale motifs and selected cracks/runes. No movie screenshots, ripped game assets,
third-party meshes or protected textures are included. The silhouettes are original.

## Animation scope

Keyframes include anticipation, contact, follow-through and recovery. Vharos has
sleep, wake-up, roar, bite, breath, both claw swipes, tail sweep, wing unfolding,
flight, turn, takeoff, landing and the hundredth-awakening pose sequence.
Humanoid variants have sword, parry, counter, dodge, kneel and reach vocabulary,
with character-specific reunion, head throw, wall kick, seed planting and authority
gestures. Some humanoid attack curves are intentionally shared. Catalog entries
enumerate exact clips rather than promising every original cinematic is complete.

AION orb clips are limited to hovering, pulse and a reveal cue. Actual orb-to-person
model replacement is a runtime transition, not geometry morphing. Little Morrow
has head tilt, Cheese chewing, bounce, yawn, sit and dragon movement clips.

Camera, particles, emissive materials, physics, damage, arena editing, model-state
switching, audio, hitboxes, mounting and multiplayer synchronization are not supplied
by the keyframes. Glowing-colored pixels are not true emissive rendering. Roots in
some action clips are pose/motion studies and need server movement reconciliation.

## Review and performance

Actual UV-mapped model renders, alternate-angle studies and four animation GIFs
are in `docs/previews/`. The renderer supports cube rotations and depth testing.
Structural validation covers the entire 297-asset roster with dynamic atlas sizes.
The actual Blockbench app and Bedrock client were not run here. Final quality needs
in-app inspection, motion review, readability at game camera distance and iPad
frame-time testing. LOD meshes and texture downsample variants are not yet provided.

Keep custom edits in `source_overrides/` and export matching geometry, texture and
animation files. The Colossus builder skips assets with saved source/export
overrides. Never regenerate directly over unprotected hand edits.
