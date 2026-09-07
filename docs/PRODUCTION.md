# Production status and integration

All 297 entries have editable cuboid models, mapped 128×64 textures, keyframe
clips, Bedrock exports and optional stationary preview entities. They are first
passes. Seventy named recipe variants share anatomical construction branches;
these are not seventy fully independent bespoke skeletons. Recolors, ordinary
creatures, props and cinematic forms all count separately. Not 297 unique monsters.

The Golden Slime shares Golden Slime. World Boss Demon General shares Rank S Boss
Demon General. VIII is the Thalassia/Verdant pair. Orun includes assembled and
separate visual pieces; parts are not automatically aligned gameplay modules.
Core Chamber is an open visual frame, not a climbable world structure. Caelum
Armor Display is not equipable armor item definitions.

## Coordinates and textures

One block is 16 units. Size is height except length for dragons, wyverns, drakes,
serpents, worms, fish and whales; bird/bat/harpy use wingspan width. Size normalization
uses unrotated cube extents. Posed wings/weapons can extend beyond that dimension.
Final posed dimensions need art review. Preview collision boxes are intentionally
small with collision/gravity disabled and do not represent giant encounter hitboxes.

Eight 32×32 atlas tiles: base, accent, metal/bone, cloth, bright, dark, secondary,
translucent body. Per-face UVs use a one-pixel guard. Pixel patterns are procedural.
Bright eye/rune/lava pixels are not emissive. Only slime shell alpha is enabled;
spirits currently have opaque spectral colors. VFX remain separate work.

## Reuse and overrides

Humanoids share root/body/head/arms/forearms/legs/shins. Quadrupeds add neck, jaw,
front/back legs, paws and tail segments. Wings have individual tips. Hydra heads,
seraph wings, halo fragments and tentacles have independent bones.

Matching names alone does not guarantee transferable animation: pivots and scaled
position tracks matter. Human variants currently share a neutral base body. They
do not replace player skins; AION player mimic requires server appearance data.

Keep hand-edited files under source_overrides/ with repository-relative paths.
Also save matching Bedrock geometry, PNG and animation exports there. Build copies
these last. It does not automatically export arbitrary edited Blockbench files.

## Remaining bespoke production

A clip name denotes a pose sample, not its gameplay effect. Breath does not create
flame, transform does not switch forms, delete does not delete an entity. Curves
are reused, and props receive preview-only idle/hurt/death clips. Consult assets.json
for the exact existing clips; do not infer complete animation coverage from names.

| Asset | Still required for final production |
| :--- | :--- |
| Vharos | Ancient silhouette, full wing anatomy, eye opening, unique awakening 100, mountain breach, kingdom flight, crash and final fall |
| Dullahan | Mounted sockets, skeletal horse detail, reins/chains, held-head attachment, gallop/charge/dismount, head throw/return, execution |
| Caelum / Elara | Grave sitting/standing, shared gaze, sword draw, readable counter/perfect dodge, weapon drop, smile, joined hands and fade |
| Kael | Recognizable shared face, tavern/throne acting, reveal, black flame, crying laugh and final smile |
| Orun | Climbable structures, assembly sockets, weakpoint modules, shoulder shake, grab, collapse, portal gesture |
| Seraphiel | Authored transition, armor-fracture pieces, damaged wings, wing choreography, airborne combo and fall |
| Nameless Knight | High/low parry, three dodge directions, distinctive counter, exact arcs, wall kick, rooftop landing, final look |
| Thalassia | Whale–leviathan–dragon silhouette, fin choreography, breach/dive, currents, sinking death |
| Verdant | Giant decay, humanoid emergence, martial arts, vines, teleport, regeneration, seed planting and growth |
| Morrow | Impossible anatomy, expressive face, all Cheese comedy beats, shoulder socket, spatial transformation and AION attack |
| AION | Anonymous prologue, calm face/hand acting, snap, editing choreography, extra-arm movement, player-history mimic and ending |
| Common creatures | Individually refined anatomy and costume, fear/retreat, attack variety, bow string/arrow, summons, slime split, web and poison VFX |
| NPCs / pets | Repair/social acting, travel, recognition, affection and carrying sockets |

Feature tags preserve design intent, not proof every visual detail is implemented.
Audit against the owner's complete roster before marking any asset final. Colossi
in particular must not be presented as completed bespoke models.

## Server responsibilities

This is an asset repository. The production engine must own registration, spawning,
ecological population, damage, hitboxes, phases, quests, persistence and Chronicle.
No Dragonfly plugin, loot, raid, AI combat or natural spawning is implemented.
Verify chosen engine behavior-pack support separately. The preview BP is optional.

Persistent facts include Vharos's awakening count/permanent death, kingdom damage,
refugees, reconstruction, faction standings, titles, single active Morrow,
Thalassia/Verdant dependency, Colossus resolution and AION finale. WORLD RESET is
narrative, never a command that wipes Era I. Model IDs remain stable as presentation
states change. Giant encounters need server positioning and real world structures.

## Verification boundary

Validator checks skeleton graph, references, positive sizes, finite keyframes,
timing, UV bounds, texture parity, Blockbench groups, client links and ZIP parity.
CPU renderer evaluates numeric animation and maps actual textures to cube faces;
it does not emulate all Bedrock lighting or transparency.

Actual Blockbench import, Bedrock content logs, in-game animation timing, client
visibility, multiplayer synchronization and iPad performance still need testing.
The package is versioned 0.1.0 to make this boundary explicit.
