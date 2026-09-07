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
    r=Sculpt()
    # Shape progression: deep shoulders, tucked abdomen, compact hip.
    for z,w,h,y in [(-23,24,28,27),(-13,32,30,25),(0,31,28,24),(13,25,23,26),(25,21,22,27),(35,22,22,26)]:
        r.add('body',(-w/2,y,z),(w,h,14),0)
        r.add('body',(-w*.36,y-1,z+1),(w*.72,3,12),2)
        for side in [-1,1]:
            for row in range(3):
                r.add('body',(side*w*.44-2,y+4+row*7,z+2),(4,6,12),1,(0,side*9,side*(12-row*8)),(side*w*.44,y+4+row*7,z+2))
    # Rising articulated neck, armor follows the neck rather than floating beside it.
    points=[(0,45,-22),(0,55,-34),(0,65,-45),(0,73,-57),(0,78,-69)]
    parent='body'
    for i,p in enumerate(points):
        n=f'neck_{i}';r.joint(n,p,parent);w=20-i*2
        r.add(n,(-w/2,p[1]-9,p[2]-13),(w,18-i,17),0,(-22,0,0),p)
        r.add(n,(-w*.32,p[1]-10,p[2]-12),(w*.64,3,13),2,(-22,0,0),p)
        for side in [-1,1]:
            r.add(n,(side*w*.4-2,p[1]-2,p[2]-10),(4,7,12),1,(-25,side*12,side*12),p)
            r.horn(n,[(side*w*.4,p[1]+5,p[2]-3),(side*(w*.5+3),p[1]+12,p[2]+5),(side*(w*.5+4),p[1]+13,p[2]+10)],2.7,0)
        parent=n
    r.joint('head',(0,80,-72),parent)
    for o,s in [((-10,75,-88),(20,14,20)),((-8,74,-102),(16,9,18)),((-6,74,-112),(12,6,13)),((-9,79,-95),(18,6,12))]:r.add('head',o,s,0)
    r.joint('jaw',(0,75,-78),'head')
    r.add('jaw',(-7,68,-107),(14,5,30),0)
    r.add('jaw',(-5.5,72,-106),(11,1,27),4)
    r.add('head',(-6,73,-108),(12,1,27),4)
    for side in [-1,1]:
        # Deep eye recess, slit and overhanging brow are geometry.
        r.add('head',(side*8.9-.6,80,-92),(1.2,3,6),4)
        r.add('head',(side*9.4-.3,80.5,-90.8),(.6,2,3),5)
        r.add('head',(side*9.75-.15,80.4,-89.6),(.3,2.2,.6),4)
        r.add('head',(side*8-2,83,-94),(4,3,10),1,(0,side*14,side*14),(side*8,83,-94))
        r.add('head',(side*4.5-.6,78,-109),(1.2,1,2),4)
        for i in range(7):
            z=-105+i*3.5
            r.horn('head',[(side*6,74,z),(side*6,70.7,z-.5)],.9,3)
            if i%2==0:r.horn('jaw',[(side*5.6,72,z),(side*5.6,74.7,z-.2)],.7,3)
        # One clearly truncated primary horn, independently named for editing.
        n='horn_left_broken' if side<0 else 'horn_right';r.joint(n,(side*8,87,-80),'head')
        pts=[(side*8,87,-80),(side*13,94,-70),(side*16,96,-58)]
        if side>0:pts.extend([(side*18,97,-45),(side*17,98,-39)])
        r.horn(n,pts,4.5,3)
        if side<0:r.add(n,(-17.8,94.5,-59),(3.6,3,.8),2)
        r.horn('head',[(side*9,76,-78),(side*16,74,-70),(side*20,78,-61)],3,0)
        r.horn('jaw',[(side*6,69,-82),(side*11,65,-72),(side*13,66,-66)],2,3)
        # Layered cheek plates make a serrated jaw silhouette.
        for i in range(4):r.add('head',(side*9-2,76+i*2,-85+i*3),(4,5,7),1,(-15,side*20,side*15),(side*9,76+i*2,-85+i*3))
        for pos,z in [('front',-12),('back',34)]:
            x=side*(15 if pos=='front' else 12);n=f'{pos}_leg_{"left" if side<0 else "right"}'
            r.joint(n,(x,39,z))
            r.bar(n,(x,39,z),(x+side*5,22,z+6),9,12,0)
            r.add(n,(x-5,30,z-6),(10,10,13),1,(0,0,side*12),(x,39,z))
            r.joint(n+'_shin',(x+side*5,22,z+6),n)
            r.bar(n+'_shin',(x+side*5,22,z+6),(x+side*5,7,z-1),6,7,0)
            r.joint(n+'_foot',(x+side*5,7,z-1),n+'_shin')
            r.add(n+'_foot',(x+side*5-5,2,z-9),(10,5,14),0)
            for toe in range(4):
                tx=x+side*5-3.8+toe*2.5
                r.add(n+'_foot',(tx-.9,1.5,z-12),(1.8,3,8),1)
                r.horn(n+'_foot',[(tx,2.8,z-10),(tx,1.5,z-17),(tx,1,z-19)],1.5,3)
            for k in range(3):r.add(n+'_shin',(x+side*5-3.3,8+k*4,z-3),(6.6,3,3),1)
    # Overlapping dorsal plates and long asymmetric rock-like spines.
    for i in range(12):
        z=-22+i*6;y=57 if i<5 else 51
        r.add('body',(-5,y-4,z),(10,3,8),1,(-10,0,0),(0,y,z))
        r.horn('body',[(0,y-2,z+1),((-1 if i%2 else 1)*2,y+8+(i%3)*2,z+5),(0,y+10+(i%3)*2,z+11)],3.3,0)
    parent='body'
    for i in range(13):
        n=f'tail_{i}';z=45+i*8;y=35-i*1.5;w=max(1.1,20-i*1.5)
        r.joint(n,(0,y,z),parent);r.add(n,(-w/2,y-w*.4,z),(w,w*.8,10),0)
        r.add(n,(-w*.43,y+w*.24,z+1),(w*.86,2,8),1)
        if i<11:r.horn(n,[(0,y+w*.4,z+2),(0,y+w*.4+7-i*.4,z+7),(0,y+w*.4+5-i*.3,z+11)],max(.8,2.5-i*.15),0)
        if i%2==0 and i<9:
            for side in [-1,1]:r.horn(n,[(side*w*.4,y,z+1),(side*(w*.6+3),y+2,z+8)],max(.7,2-i*.12),0)
        parent=n
    # Arched wing spars and scalloped torn membranes. Every strip is solid geometry.
    for side,label in [(-1,'left'),(1,'right')]:
        n='wing_'+label;r.joint(n,(side*14,49,-5))
        anchors=[(14,49,-5),(40,86,-24),(75,112,-24),(105,105,-10),(133,85,8)]
        pts=[(side*x,y,z) for x,y,z in anchors]
        r.horn(n,pts,5,0)
        r.horn(n,[(side*75,112,-24),(side*78,123,-26),(side*82,128,-22)],3,3)
        # Four elongated digits leave strong, readable web lobes.
        for k,(ex,ey,ez) in enumerate([(40,57,55),(68,66,66),(96,69,52),(126,78,27)]):
            r.horn(n,[(side*40,86,-24),(side*(ex+5),ey+12,ez*.5),(side*ex,ey,ez)],2.1,1)
        for i in range(58):
            x=16+i*2
            a,b=next((a,b) for a,b in zip(anchors,anchors[1:]) if a[0]<=x<=b[0])
            t=(x-a[0])/(b[0]-a[0]);y=a[1]+t*(b[1]-a[1]);z=a[2]+t*(b[2]-a[2])
            # Lower edge scallops and missing notches are real negative silhouette.
            end=62-abs(x-68)*.45-8*abs(math.sin((x-16)*math.pi/29))
            if i in ({12,13,33,48} if side<0 else {19,38,39,51}):end-=14
            d=max(3,end-z);drop=max(3,y-(52+x*.16))
            # Overlap adjacent slabs along the arch so the web remains connected.
            # Positive X pitch makes the trailing edge descend toward the digits.
            thickness=1.1+abs((b[1]-a[1])/(b[0]-a[0]))*2.3
            r.add(n,(-x-2.25 if side<0 else x,y-thickness/2,z),(2.35,thickness,math.hypot(d,drop)),6,(math.degrees(math.atan2(drop,d)),0,0),(side*x,y,z))
        for j in range(5):
            x=20+j*4;r.add(n,(side*x-2,53+j*4,-12-j*2),(4,5,9),1,(0,0,-side*28),(side*x,53+j*4,-12-j*2))
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
    assert not any('spear' in b['name'] or 'weapon' in b['name'] for b in r.bones)
    data=json.loads((OUT/'vharos.bbmodel').read_text());assert not data['animations']
    names={b['name'] for b in r.bones};assert len(names)==len(r.bones)
    assert all(b.get('parent') in names for b in r.bones if 'parent' in b)
    dump(OUT/'review.json',{'id':'vharos','stage':'geometry only','cubes':len(r.parts),'bones':len(r.bones),
         'dimensions_blocks':dict(zip(['width','height','length'],map(float,sizes))),
         'weapons':False,'animation_clips':0,'final_textures':False,'blockbench_application_test':False})
    font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',23)
    sheet=Image.new('RGB',(1800,1320),(28,33,39));draw=ImageDraw.Draw(sheet)
    draw.text((35,22),'UNWRITTEN / VHAROS / GEOMETRY REVIEW',font=font,fill='#e6e3da')
    draw.text((35,60),'Actual exported model | Clay materials | No texture, animation or weapon pass',font=font,fill='#a8b4bd')
    for i,(yaw,pitch,label) in enumerate([(-38,12,'Three-quarter'),(-90,0,'Side'),(0,5,'Front')]):
        pic,_=render(e,600,yaw=yaw,pitch=pitch);sheet.paste(pic,(i*600,105));draw.text((i*600+30,710),label,font=font,fill='#d8d7cd')
    # Head-only mesh preview retains the real exported head geometry.
    g=json.loads((ROOT/e['geometry']).read_text())
    for b in g['minecraft:geometry'][0]['bones']:
        if b['name'] not in {'head','jaw','horn_left_broken','horn_right'}:b.pop('cubes',None)
    dump(OUT/'head_review.geo.json',g);he=dict(e,geometry='model_studio/vharos/head_review.geo.json')
    pic,_=render(he,550,yaw=-35,pitch=12);sheet.paste(pic,(35,760))
    draw.text((650,805),'Sculpt details',font=font,fill='#e6e3da')
    for i,s in enumerate(['Long armored neck and predator jaw','Asymmetric horns, left horn broken','Four articulated legs and individual claws','Arched spars, scalloped and torn wing membranes','Layered dorsal plates and segmented tail',f'Length: {sizes[2]:.1f} blocks | Height: {sizes[1]:.1f} blocks',f'{len(r.parts)} editable cubes | {len(r.bones)} named groups']):
        draw.text((650,865+i*48),s,font=font,fill='#aebcc4')
    sheet.save(OUT/'preview.png')
    print(json.dumps(json.loads((OUT/'review.json').read_text())))

if __name__=='__main__':build()
