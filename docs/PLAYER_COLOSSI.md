# Colossi humanoid art pass 03

This pass supersedes the sculpted humanoids and dark AION palette in pass 02. Eleven humanoid forms use Steve proportions: an 8x8x8 head, 8x12x4 torso, 4x12x4 arms and legs. No sculpted fingers, visible neck, or subdivided elbows/knees. Dullahan is deliberately headless in entity form.

AION follows the supplied poster: ivory robes, restrained gold geometry, a featureless pale mask, a halo and floating fragments. His prologue remains an unidentified black orb. Architect retains the player silhouette with additional floating arms. Non-humanoid Colossi and Little Morrow are unchanged in this pass.

## Original texture construction

`tools/build_player_colossi.py` paints every pixel from color palettes and authored material rules. No poster pixels, projected concept art, downloaded texture, or image-generation output is used. Skin shading includes directional face ramps, hair layers, eye detail, cloth folds and stitches, plate occlusion, metal reflections, rivets, and character-specific scars or corruption. AION deliberately has no ordinary facial features.

Each accessory face receives its own padded UV island and separately painted material shading. The entity atlas includes the custom 64x64 base skin; copying this authored skin into its runtime atlas is not reference-image projection. This is procedural pixel-art authorship, not a claim that each pixel was manually brush-painted by an artist.

## Deliverables

- Editable models with embedded textures and numeric animation keys: `blockbench/colossi/` (consult catalog for exact paths).
- Standalone standard player skins: `skins/colossi/`.
- Runtime entity models, textures, animation clips and controllers: `packs/UNWRITTEN_RP/`.
- Import packs: `dist/UNWRITTEN_Assets.mcpack`, `UNWRITTEN_Preview.mcpack`, and `UNWRITTEN_Colossi_Skins.mcpack`.
- Actual exported-mesh preview: `docs/previews/player_colossi_review.png`.

The skin pack contains base skins only. Three-dimensional robes, halos, wings, horns, weapons and headless presentation belong to the entity resource pack, not ordinary player skins. Skin-pack geometry follows [Minecraft's official skin-pack documentation](https://learn.microsoft.com/en-us/minecraft/creator/documents/packagingaskinpack?view=minecraft-bedrock-stable).

## Rebuild and acceptance

Run `build_assets.py`, `build_colossi.py`, then `build_player_colossi.py` from `tools/`, followed by both validation scripts. The new pass must run last. Source overrides remain protected.

Structural and UV validation, archive parity, exact base dimensions and software-rendered inspection are available. Blockbench application import, Bedrock in-game animation timing, visual polish and multiplayer performance still require testing. This is an authored asset revision, not a claim that the entire roster is production-final. Existing animation curves are adapted to rigid player limbs; unique combat choreography needs in-game iteration.
