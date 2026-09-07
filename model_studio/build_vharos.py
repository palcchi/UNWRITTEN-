"""Focused geometry review. No combat animations, weapons or finished textures."""
import sys, json, math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from PIL import Image, ImageDraw, ImageFont
from build_assets import ROOT, dump, geometry, bbmodel
from build_colossi import Sculpt
from render_previews import render, mesh
import numpy as np

OUT=ROOT/'model_studio/vharos'

def sculpt():
    """Lean mod-style anatomy; coherent masses instead of repeated armor tiles."""
    r=Sculpt()
    # Three interlocking masses, elongated along the spine.
    r.add('body',(-13,21,-18),(26,23,36),0)
    r.add('body',(-11,23,9),(22,19,28),0,(5,0,0),(0,30,12))
    r.add('body',(-10,23,29),(20,18,17),0,(-8,0,0),(0,30,30))
    r.add('body',(-9,20.5,-12),(18,3,39),2)
    # Low, forward-reaching neck. Rotated links overlap without external plates.
    neck=[((0,35,-14),(0,40,-32),16,17),
          ((0,40,-30),(0,48,-48),13,14),
          ((0,48,-46),(0,52,-63),10,12)]
    parent='body'
    for i,(a,b,w,d) in enumerate(neck):
        n=f'neck_{i}';r.joint(n,a,parent)
        r.bar(n,a,b,w,d,0);parent=n
    r.joint('head',(0,53,-62),parent)
    r.add('head',(-8,48,-78),(16,12,18),0)
    r.add('head',(-6,47,-91),(12,7,18),0,(-4,0,0),(0,49,-77))
    r.add('head',(-4.5,47,-99),(9,5,10),0)
    r.joint('jaw',(0,48,-66),'head')
    r.add('jaw',(-5.5,43.5,-82),(11,3.5,15),0)
    r.add('jaw',(-4.5,44,-96),(9,3,16),0)
    r.add('jaw',(-4.5,46.5,-94),(9,.5,26),4)
    for side in [-1,1]:
        # Eye sockets are narrow. No decorative eye frame cubes.
        r.add('head',(side*7.7-.25,53,-77),(.5,2.2,4),4)
        r.add('head',(side*8-.15,53.3,-76.5),(.3,1.4,2.4),5)
        r.add('head',(side*7-1.5,55,-79),(3,2.1,9),0,(0,side*9,side*16),(side*7,55,-79))
        r.add('head',(side*7-1.7,47,-71),(3.4,5,8),0,(0,side*22,0),(side*7,48,-71))
        n='horn_left_broken' if side<0 else 'horn_right'
        r.joint(n,(side*6,59,-66),'head')
        pts=[(side*6,59,-66),(side*10,65,-57),(side*12,65,-48)]
        if side>0:pts.append((side*13,64,-36))
        r.horn(n,pts,3,3)
        r.horn('head',[(side*7,49,-67),(side*13,46,-56)],2.2,0)
        for z in [-91,-83]:
            r.horn('head',[(side*4.9,47,z),(side*4.9,44.2,z-.5)],.9,3)
        # Digitigrade rear legs and slimmer front legs carry the torso naturally.
        for pos,z in [('front',-8),('back',32)]:
            x=side*(12 if pos=='front' else 10)
            n=f'{pos}_leg_{"left" if side<0 else "right"}'
            r.joint(n,(x,32,z))
            knee=(x+side*4,16,z+(7 if pos=='back' else -3))
            ankle=(x+side*4,5,z+(-2 if pos=='back' else 2))
            r.bar(n,(x,32,z),knee,8 if pos=='back' else 6,10 if pos=='back' else 7,0)
            r.joint(n+'_shin',knee,n);r.bar(n+'_shin',knee,ankle,4,5,0)
            r.joint(n+'_foot',ankle,n+'_shin')
            r.add(n+'_foot',(ankle[0]-3.8,1,z-8),(7.6,4,11),0)
            for toe in [-1,0,1]:
                tx=ankle[0]+toe*2.4
                r.horn(n+'_foot',[(tx,2.4,z-6),(tx,1.2,z-12)],1.3,3)
    # Eight clean tail links, only four silhouette spines.
    parent='body'
    for i in range(8):
        n=f'tail_{i}';z=41+i*12;y=32-i*2.2;w=max(1.2,17-i*2.15)
        r.joint(n,(0,y,z),parent)
        r.bar(n,(0,y,z),(0,y-2.4,z+14),w,w*.85,0)
        if i%2==0:r.horn(n,[(0,y+w*.43,z+3),(0,y+w*.43+5-i*.4,z+9)],max(.6,2-i*.15),0)
        parent=n
    for i,(y,z) in enumerate([(46,-17),(45,0),(43,18),(42,34)]):
        r.horn('body',[(0,y-3,z),(0,y+6,z+5),(0,y+3,z+9)],2.5,0)
    # Wings share a planar local surface, then the whole shoulder group is lifted.
    # Few broad strips form each web; no disconnected angled slats.
    for side,label in [(-1,'left'),(1,'right')]:
        n='wing_'+label;r.joint(n,(side*11,40,-4),rot=(0,0,side*22))
        wrist=(side*40,40,-29);tip=(side*105,40,-8)
        r.horn(n,[(side*11,40,-4),wrist,tip],3.2,0)
        r.horn(n,[wrist,(side*42,40,-38),(side*45,40,-39)],1.6,3)
        for ex,ez in [(36,46),(62,47),(84,31)]:
            r.horn(n,[wrist,(side*ex,40,ez)],1.2,0)
        # Constant plane avoids gaps; sparse notches retain an old wing silhouette.
        for i in range(12):
            x=12+i*7.7
            front=-4-(x-12)*25/28 if x<40 else -29+(x-40)*21/65
            back=12+(x-12)*1.35 if x<36 else 45-(x-36)*.65
            if i in ({5,10} if side<0 else {8}):back-=8
            r.add(n,(-x-8 if side<0 else x,39.7,front),(8,.6,max(2,back-front)),6)
    return r

def build():
    OUT.mkdir(parents=True,exist_ok=True);r=sculpt()
    # Clay swatches only, not a finished UV layout or custom texture deliverable.
    colors=['#8b9296','#a5abae','#727c82','#c7c3b8','#303a41','#d2d0c6','#67747e']
    im=Image.new('RGBA',(len(colors)*4,4))
    d=ImageDraw.Draw(im)
    for i,c in enumerate(colors):d.rectangle((i*4,0,i*4+3,3),fill=c)
    for p in r.parts:p['uv']={f:{'uv':[p['material']*4,0],'uv_size':[3,3]} for f in ['north','south','east','west','up','down']}
    e={'id':'vharos_sculpt','name':'Vharos | Geometry review','size':38,'texture_width':im.width,'texture_height':im.height,
       'geometry':'model_studio/vharos/vharos.geo.json','texture':'model_studio/vharos/clay_preview.png'}
    im.save(ROOT/e['texture'])
    dump(ROOT/e['geometry'],geometry(e,r))
    actual=np.concatenate([v for v,uv,f in mesh(e)])
    factor=38*16/(actual[:,2].max()-actual[:,2].min());r.scaled(factor)
    dump(ROOT/e['geometry'],geometry(e,r))
    dump(OUT/'vharos.bbmodel',bbmodel(e,r,ROOT/e['texture'],{}))
    actual=np.concatenate([v for v,uv,f in mesh(e)])
    sizes=(actual.max(0)-actual.min(0))/16
    assert all(all(v>0 for v in p['size']) for p in r.parts)
    assert len(r.parts)<=140,'Geometry budget exceeded'
    assert not any('spear' in b['name'] or 'weapon' in b['name'] for b in r.bones)
    data=json.loads((OUT/'vharos.bbmodel').read_text());assert not data['animations']
    names={b['name'] for b in r.bones};assert len(names)==len(r.bones)
    assert all(b.get('parent') in names for b in r.bones if 'parent' in b)
    dump(OUT/'review.json',{'id':'vharos','stage':'geometry only / simplified anatomy revision','cubes':len(r.parts),'previous_cubes':474,'cube_reduction_percent':round((1-len(r.parts)/474)*100,1),'bones':len(r.bones),
         'dimensions_blocks':dict(zip(['width','height','length'],map(float,sizes))),
         'weapons':False,'animation_clips':0,'final_textures':False,'blockbench_application_test':False})
    font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',23)
    sheet=Image.new('RGB',(1800,1320),(28,33,39));draw=ImageDraw.Draw(sheet)
    draw.text((35,22),'UNWRITTEN / VHAROS / GEOMETRY REVIEW',font=font,fill='#e6e3da')
    draw.text((35,60),'Actual exported model | Clay materials | No texture, animation or weapon pass',font=font,fill='#a8b4bd')
    for i,(yaw,pitch,label) in enumerate([(-48,25,'Three-quarter'),(-90,0,'Side'),(0,5,'Front')]):
        pic,_=render(e,600,yaw=yaw,pitch=pitch);sheet.paste(pic,(i*600,105));draw.text((i*600+30,710),label,font=font,fill='#d8d7cd')
    # Head-only mesh preview retains the real exported head geometry.
    g=json.loads((ROOT/e['geometry']).read_text())
    for b in g['minecraft:geometry'][0]['bones']:
        if b['name'] not in {'head','jaw','horn_left_broken','horn_right'}:b.pop('cubes',None)
    dump(OUT/'head_review.geo.json',g);he=dict(e,geometry='model_studio/vharos/head_review.geo.json')
    pic,_=render(he,550,yaw=-35,pitch=12);sheet.paste(pic,(35,760))
    draw.text((650,805),'Sculpt details',font=font,fill='#e6e3da')
    for i,s in enumerate(['Lower neck, lean torso, tapered jaw','Asymmetric horns, left horn broken','Four bent legs and individual claws','Thin connected wing webs, fewer cutouts','Sparse spines and eight tail links',f'Length: {sizes[2]:.1f} blocks | Height: {sizes[1]:.1f} blocks',f'{len(r.parts)} cubes / previously 474 | {len(r.bones)} groups']):
        draw.text((650,865+i*48),s,font=font,fill='#aebcc4')
    sheet.save(OUT/'preview.png')
    print(json.dumps(json.loads((OUT/'review.json').read_text())))

if __name__=='__main__':build()
