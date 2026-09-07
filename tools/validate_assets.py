#!/usr/bin/env python3
"""Structural integration checks, not a substitute for the Bedrock content log."""
import base64
import io
import json
import math
import zipfile
from PIL import Image
from build_assets import ROOT, RP, BP

def main():
    entries=json.loads((ROOT/'catalog/assets.json').read_text())['entries']; ids=set(); clips=0; cubes=0
    for e in entries:
        id=e['id']; assert id not in ids; ids.add(id)
        g=json.loads((ROOT/e['geometry']).read_text())['minecraft:geometry'][0]
        assert g['description']['identifier']=='geometry.unwritten.'+id
        bones={b['name']:b for b in g['bones']}; assert len(bones)==len(g['bones'])
        tex=Image.open(ROOT/e['texture']); assert tex.size==(g['description']['texture_width'],g['description']['texture_height'])
        for name,b in bones.items():
            visited={name}; parent=b.get('parent')
            while parent:
                assert parent in bones and parent not in visited,(id,parent)
                visited.add(parent); parent=bones[parent].get('parent')
            for c in b.get('cubes',[]):
                cubes+=1; assert all(v>0 and math.isfinite(v) for v in c['size'])
                assert len(c['uv'])==6
                for uv in c['uv'].values():
                    a,b=uv['uv']; w,h=uv['uv_size']; assert 0<=a<a+w<=tex.width and 0<=b<b+h<=tex.height,(id,uv)
        a=json.loads((RP/f'animations/unwritten/{id}.animation.json').read_text())['animations']
        for name,anim in a.items():
            clips+=1; assert name.startswith('animation.unwritten.'+id+'.')
            assert anim['bones']
            for bone,channels in anim['bones'].items():
                assert bone in bones,(id,bone)
                for keys in channels.values():
                    assert min(map(float,keys))==0
                    assert max(map(float,keys))<=anim['animation_length']+.0001
                    assert all(len(v)==3 and all(math.isfinite(x) for x in v) for v in keys.values())
        bb=json.loads((ROOT/e['source']).read_text()); assert len(bb['animations'])==len(a)
        embedded=Image.open(io.BytesIO(base64.b64decode(bb['textures'][0]['source'].split(',')[1])))
        assert embedded.tobytes()==tex.tobytes()
        elements={x['uuid'] for x in bb['elements']}; assert len(elements)==len(bb['elements'])
        groupids=set(); used=[]
        def walk(groups):
            for group in groups:
                if isinstance(group,str): used.append(group); continue
                assert group['uuid'] not in groupids; groupids.add(group['uuid']); walk(group['children'])
        walk(bb['outliner']); assert set(used)==elements and len(used)==len(elements)
        for anim in bb['animations']: assert set(anim['animators'])<=groupids
        client=json.loads((RP/f'entity/{id}.entity.json').read_text())['minecraft:client_entity']['description']
        assert client['identifier']=='unwritten:'+id
        assert client['geometry']['default']==g['description']['identifier']
        assert (RP/(client['textures']['default']+'.png')).exists()
        assert set(client['animations'].values())-{f'controller.animation.unwritten.{id}'}==set(a)
        behavior=json.loads((BP/f'entities/{id}.json').read_text())['minecraft:entity']
        assert behavior['description']['identifier']==client['identifier']
    for filename,folder in [('UNWRITTEN_Assets.mcpack',RP),('UNWRITTEN_Preview.mcpack',BP)]:
        with zipfile.ZipFile(ROOT/'dist'/filename) as z:
            assert z.testzip() is None and 'manifest.json' in z.namelist()
            for name in z.namelist(): assert z.read(name)==(folder/name).read_bytes()
    assert not (BP/'spawn_rules').exists()
    report={'assets':len(entries),'cubes':cubes,'animation_clips':clips,'checks':'passed','blockbench_app_test':False,'bedrock_in_game_test':False}
    from build_assets import dump
    dump(ROOT/'docs/validation.json',report); print(json.dumps(report))

if __name__=='__main__': main()
