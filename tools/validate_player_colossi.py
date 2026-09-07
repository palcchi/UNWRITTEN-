"""Check Steve dimensions, custom skin UVs and packaged skin bytes."""
import json, zipfile
from PIL import Image
from build_assets import ROOT
from build_player_colossi import IDS, PARTS, player_rig, skin_uv

entries={e['id']:e for e in json.loads((ROOT/'catalog/assets.json').read_text())['entries']}
for id in IDS:
    e=entries[id]
    if e['status']!='player_skin_art_pass_3':continue
    r=player_rig(id)
    base={p['base_part']:p for p in r.parts if p.get('base_part')}
    assert len(base)==(5 if id=='dullahan' else 6),id
    for name,p in base.items():
        assert tuple(p['size'])==PARTS[name][1],(id,name)
    skin=Image.open(ROOT/e['skin']).convert('RGBA')
    assert skin.size==(64,64),id
    atlas=Image.open(ROOT/e['texture']).convert('RGBA')
    assert atlas.crop((0,0,64,64)).tobytes()==skin.tobytes(),id
folder=ROOT/'packs/UNWRITTEN_Colossi_Skins'
with zipfile.ZipFile(ROOT/'dist/UNWRITTEN_Colossi_Skins.mcpack') as z:
    files={str(p.relative_to(folder)):p for p in folder.rglob('*') if p.is_file()}
    assert set(z.namelist())==set(files)
    for name,p in files.items():assert z.read(name)==p.read_bytes(),name
print('Steve dimensions, 64x64 custom skins, atlas copies and skin pack parity passed.')
