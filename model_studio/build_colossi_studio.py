"""Ten Colossi model and pixel-art texture review. No animation clips.

Only the model_studio output tree is written. No runtime pack, existing skin,
animation or weapon asset is replaced by this geometry review.
"""
import sys, json, math, zipfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from build_assets import ROOT, dump, geometry, bbmodel
from build_colossi import Sculpt
from build_player_colossi import PARTS
from build_vharos import sculpt as vharos_base
from paint_colossi import prepare_model, paint_atlas
from render_previews import render as render_geometry, mesh

OUT=ROOT/'model_studio'
BACKGROUND=(46,53,64)

def render(*args,**kwargs):
    image,bounds=render_geometry(*args,**kwargs)
    # Neutral viewport background gives dark material silhouettes room to read.
    pixels=np.array(image);pixels[np.all(pixels==[28,33,39],axis=2)]=BACKGROUND
    return Image.fromarray(pixels),bounds

FACE_NAMES=['north','south','east','west','up','down']
# Solid viewport materials. These are not painted textures or final UV assets.
PALETTES={
 'dullahan':dict(base='#34313e',edge='#6c6576',cloth='#28222f',trim='#877e87',skin='#bcafab',hair='#302934',eye='#9c73be',accent='#655077'),
 'caelum':dict(base='#55575b',edge='#96948b',cloth='#303440',trim='#88764e',skin='#c6aa92',hair='#b8b2a4',eye='#565e64',accent='#6b6155'),
 'elara_spirit':dict(base='#a0aeb3',edge='#c9cdd0',cloth='#7b8a98',trim='#b8b7b3',skin='#c1c6c7',hair='#d0d4d5',eye='#668da1',accent='#7c829f'),
 'kael_hunter':dict(base='#35323b',edge='#514850',cloth='#28252d',trim='#6b5747',skin='#c4a28c',hair='#23232b',eye='#893b46',accent='#593540'),
 'kael_demon_king':dict(base='#302a33',edge='#65434c',cloth='#25222b',trim='#947246',skin='#c4a28c',hair='#23232b',eye='#b85561',accent='#773848'),
 'sir_seraphiel':dict(base='#bcb9aa',edge='#ded8c9',cloth='#898e98',trim='#a9905d',skin='#ccb7a5',hair='#d3cdbf',eye='#a89262',accent='#71828a'),
 'fallen_seraphiel':dict(base='#35313d',edge='#645864',cloth='#292633',trim='#74614b',skin='#b4a5a2',hair='#a5a0a4',eye='#9f5a77',accent='#6e4058'),
 'the_nameless_knight':dict(base='#424044',edge='#686361',cloth='#2c2e34',trim='#655347',skin='#ad8b75',hair='#2b272b',eye='#50565e',accent='#4a3940'),
 'verdant_the_last_father':dict(base='#5b5144',edge='#897758',cloth='#454638',trim='#65765a',skin='#c4af97',hair='#c9c6bf',eye='#6e9167',accent='#526b48'),
 'aion':dict(base='#b9b6ad',edge='#d8d1c1',cloth='#3c3b44',trim='#a68d5c',skin='#d3c9b9',hair='#dad5cb',eye='#b2a07d',accent='#625f74'),
 'aion_the_architect':dict(base='#afaba5',edge='#cec8bc',cloth='#2c2c36',trim='#a18c61',skin='#c8c1b7',hair='#d3d0c7',eye='#958cac',accent='#59556d'),
 'vharos':dict(base='#35363d',edge='#55535a',belly='#565153',bone='#807568',void='#24212a',eye='#ac6544',wing='#4e3540'),
 'dullahan_horse':dict(base='#35313c',edge='#57515f',cloth='#2c2634',trim='#8a7b8a',skin='#847d87',hair='#292632',eye='#9c73be',accent='#655077'),
 'orun':dict(base='#7c715e',edge='#a7997f',stone='#5c594f',metal='#484951',bronze='#8f805e',core='#bacfd1',moss='#5b6651',void='#33343a'),
 'thalassia':dict(base='#304754',edge='#486470',belly='#8b9b9f',fin='#354d5c',scar='#819ea5',barnacle='#707a7d',eye='#99b8bf',coral='#7f7177'),
 'verdant_giant':dict(base='#514a3d',edge='#746b50',leaf='#435847',moss='#667350',core='#98ac79',void='#343a37'),
 'little_morrow':dict(base='#b7b0ca',edge='#d8d0e0',belly='#d3cbdc',horn='#81748f',wing='#857695',eye='#685681',void='#3c334c',accent='#a297bb'),
 'true_morrow':dict(base='#34303f',edge='#645671',belly='#52465e',horn='#827190',wing='#494052',eye='#a493be',void='#23212c',accent='#7c6994'),
 'morrow_anomaly':dict(base='#34303f',edge='#645671',belly='#52465e',horn='#827190',wing='#494052',eye='#b7a8c9',void='#23212c',accent='#7c6994'),
 'aion_prologue':dict(void='#24232c',edge='#53505e',trim='#948268',light='#bbb5ac'),
}

def joint(r,n,p,parent='body',rot=None):
    if not r.has(n):r.joint(n,p,parent,rot)
    return n

def box(r,n,o,s,mat='base',rot=None,pivot=None):r.add(n,o,s,mat,rot,pivot)
def bar(r,n,a,b,w,d,mat='base'):r.bar(n,a,b,w,d,mat)
def horn(r,n,pts,w,mat='trim'):r.horn(n,pts,w,mat)

def band(r,n,c,radius,thick=.3,mat='trim',count=12,gaps=()):
    r.ring(n,c,radius,thick,mat,count,gaps)

def hair(r,n='head',long=False,short=False):
    box(r,n,(-4.15,30.35,-4.1),(8.3,1.85,8.25),'hair')
    box(r,n,(-4.1,25.7,3.35),(8.2,4.8,1),'hair')
    for side in [-1,1]:
        box(r,n,(side*3.65-.6,26.3,-1.8),(1.2,4.7,5.4),'hair',(0,0,side*7),(side*3.6,31,0))
    for x,y,w in [(-3.8,28.4,2.1),(-1.7,29.0,2.5),(.8,28.0,2.9)]:
        box(r,n,(x,y,-4.45),(w,31-y,.6),'hair',(0,0,5 if x<0 else -6),(x,31,-4))
    if long and not short:
        joint(r,'long_hair',(0,27,3.7),'head')
        box(r,'long_hair',(-3.7,18.5,3.5),(7.4,9,.75),'hair',(-8,0,0),(0,27,3.7))
        box(r,'long_hair',(-2.5,16.5,4.0),(5,4,.6),'hair',(-8,0,0),(0,27,3.7))

def face(r,n='head',y=24,z=-4):
    for side in [-1,1]:
        box(r,n,(side*2-.8,y+3.4,z-.15),(1.6,.8,.18),'edge')
        box(r,n,(side*2-.32,y+3.35,z-.28),(.64,.85,.15),'eye')
    box(r,n,(-.7,y+1.3,z-.12),(1.4,.25,.15),'accent')

def cloak(r,kind='long',mat='cloth'):
    # Two slightly swept panels, avoiding a wall of thin strips.
    hem=4 if kind=='long' else 10
    for side in [-1,1]:
        n=f'cloak_{side}';joint(r,n,(side*2,23,2.4))
        box(r,n,(side*2-2.1,hem+(side>0),2.6),(4.2,23-hem-(side>0),.48),mat,(-9,side*4,side*2),(side*2,23,2.4))
        box(r,n,(side*2-1.9,hem+(side>0),2.4),(.22,23-hem-(side>0),.25),'edge',(-9,side*4,side*2),(side*2,23,2.4))

def armor(r,heavy=False,wood=False):
    # Torso and limb bases keep exact Steve dimensions under removable panels.
    box(r,'body',(-3.9,15,-2.5),(7.8,7.5,.65),'base')
    box(r,'body',(-.25,15.5,-2.95),(.5,6.5,.3),'trim')
    box(r,'body',(-4.2,12.7,-2.5),(8.4,1,5),'cloth')
    box(r,'body',(-.75,12.6,-2.85),(1.5,1.3,.6),'trim')
    for side,label in [(-1,'r'),(1,'l')]:
        x=side*6;n='arm_'+label
        joint(r,'pauldron_'+label,(x,23,0),n)
        w=5.3 if heavy and side<0 else 4.7
        box(r,'pauldron_'+label,(x-w/2,21.4,-2.5),(w,2.9,5),'base',(0,0,-side*9),(x,23,0))
        box(r,'pauldron_'+label,(x-w/2,21.25,-2.65),(w,.4,5.3),'trim',(0,0,-side*9),(x,23,0))
        box(r,n,(x-2.05,12.2,-2.15),(4.1,3.8,.5),'edge')
        leg='leg_'+label;lx=side*2
        box(r,leg,(lx-1.95,.1,-2.3),(3.9,3.3,4.65),'cloth')
        box(r,leg,(lx-1.55,5.4,-2.2),(3.1,2.1,.4),'base')
    if wood:
        for i in range(3):box(r,'pauldron_l',(4.2+i*.65,23.1,-2),(1.8,.45,3.5),'accent',(0,i*18,-20),(6,23,0))

def robe(r):
    box(r,'body',(-3.8,13.6,-2.5),(7.6,9.8,.65),'base')
    for side,label in [(-1,'r'),(1,'l')]:
        x=side*2;n='robe_'+label;joint(r,n,(x,12,0),'leg_'+label)
        box(r,n,(x-2.2,.4,-2.4),(4.4,11.6,.45),'base',(0,0,-side*3),(x,12,0))
        box(r,n,(x+side*1.6-.16,.6,-2.7),(.32,11.1,.2),'trim',(0,0,-side*3),(x,12,0))
        box(r,'arm_'+label,(side*6-2.15,12.5,-2.2),(4.3,1,4.4),'trim')
        box(r,'body',(side*2.8-.7,20.5,-2.8),(1.4,3.3,.4),'edge',(0,0,-side*23),(side*2.8,23,-2.8))
    for x in [-3.6,3.3]:box(r,'body',(x,14.4,-2.65),(.3,9,.3),'trim')

def humanoid(id):
    r=Sculpt();r.bones[1]['pivot']=[0,12,0]
    for name,(o,s,p,uv) in PARTS.items():
        if name!='body':joint(r,name,p)
        if id=='dullahan' and name=='head':continue
        mat='skin' if name=='head' else ('base' if id in {'aion','aion_the_architect','elara_spirit'} and name.startswith('arm') else 'cloth')
        box(r,name,o,s,mat)
        r.parts[-1]['steve_base']=name
    if id!='dullahan':
        hair(r,long=id in {'caelum','elara_spirit','sir_seraphiel','verdant_the_last_father','aion'})
        face(r)
    armored=id in {'dullahan','caelum','kael_demon_king','sir_seraphiel','fallen_seraphiel','verdant_the_last_father'}
    if armored:armor(r,heavy=id=='kael_demon_king',wood=id=='verdant_the_last_father')
    if id!='verdant_the_last_father':cloak(r,'short' if id=='kael_hunter' else 'long')
    # Upright collars frame the Steve head without oversized shoulders.
    for side in [-1,1]:box(r,'body',(side*3-.75,22.2,-1.5),(1.5,2.3,4.2),'cloth',(0,0,-side*12),(side*3,23,0))
    if id in {'kael_hunter','the_nameless_knight'}:
        box(r,'body',(-4.1,12.3,-2.2),(8.2,.8,4.4),'trim')
        box(r,'body',(-3.2,14.2,-2.45),(.9,8.2,.4),'accent',(0,0,32),(-2,19,-2))
        box(r,'body',(-3.8,22.2,-2.8),(7.6,1.4,5.4),'accent')
        if id=='kael_hunter':
            joint(r,'satchel',(4,14,1.5));box(r,'satchel',(3.7,10.8,.5),(2.4,4,3),'trim')
            box(r,'satchel',(3.6,13.4,.3),(2.6,.7,3.3),'edge')
        else:
            box(r,'body',(-5,19.6,-2.7),(6,3.3,.45),'cloth',(0,0,-13),(-3,22,-2.7))
            joint(r,'cloak_side',(-4,22,1.6));box(r,'cloak_side',(-7,5,1.8),(3,17,.5),'cloth',(-10,0,-8),(-4,22,1.6))
        for s,l in [(-1,'r'),(1,'l')]:box(r,'leg_'+l,(s*2-1.95,.1,-2.1),(3.9,3.5,4.4),'base')
    if id=='dullahan':
        joint(r,'empty_collar',(0,24,0));box(r,'empty_collar',(-2,24,-1.7),(4,.8,3.4),'cloth')
        # The head is a detachable object, not a weapon. Left arm holds it low.
        joint(r,'held_head',(6,12,-3),'arm_l')
        box(r,'held_head',(3,5.5,-6),(6,6,6),'skin')
        box(r,'held_head',(2.85,10,-6.1),(6.3,1.7,6.2),'hair')
        for x in [4.4,7.0]:box(r,'held_head',(x,8.1,-6.15),(1,.45,.2),'eye')
        for side in [-1,1]:
            box(r,'body',(side*2.5-.25,18,-2.9),(.5,3,.25),'trim',(0,0,side*24),(side*2.5,21,-2.9))
    if id=='kael_demon_king':
        for side in [-1,1]:horn(r,'head',[(side*3,31,1),(side*5,35,2),(side*5.5,36.5,5)],1.1,'base')
        box(r,'body',(-.7,18.5,-3.2),(1.4,1.8,.45),'accent',(0,0,45),(0,19.4,-3))
        for i in range(6):
            a=math.tau*i/6;x=math.cos(a)*8.4;y=23+math.sin(a)*6.2;n='shard_'+str(i)
            joint(r,n,(x,y,5.5));box(r,n,(x-.55,y-1.8,5.5),(1.1,3.6,.7),'base',(0,0,i*60),(x,y,5.5))
            box(r,n,(x-.15,y-1.3,5.35),(.3,2.6,.2),'accent',(0,0,i*60),(x,y,5.5))
    if id in {'sir_seraphiel','fallen_seraphiel'}:
        fallen=id=='fallen_seraphiel'
        for pair in range(3):
            for sign,label in [(-1,'l'),(1,'r')]:
                y=22-pair*2.1;n=f'wing_{label}_{pair}'
                joint(r,n,(sign*3.4,y,3.2),'body',(0,sign*8,sign*(40-pair*35)))
                bar(r,n,(sign*3.4,y,3.4),(sign*15,y+2.5,4.8),.45,.65,'base' if fallen else 'edge')
                for j in range(5):
                    if fallen and (pair,j,sign) in {(0,4,-1),(2,2,1)}:continue
                    x=sign*(5+j*2.1);length=9-j*.8-pair*.9
                    box(r,n,(x-1,y-length+1,3.5),(2.15,length,.42),'base' if fallen else 'edge',(0,0,sign*(18+j*6)),(x,y+1,3.7))
        for side in [-1,1]:box(r,'body',(side*2.6-1.3,8,-2.8),(2.6,5.5,.5),'base',(0,0,-side*5),(side*2.6,13,-2.8))
        joint(r,'halo',(0,34,1),'head',(0,0,13 if fallen else 0))
        band(r,'halo',(0,34,1),5.7,.22,'trim',12,(1,5,8) if fallen else ())
    if id=='verdant_the_last_father':
        for side in [-1,1]:
            box(r,'head',(side*4-(1.5 if side<0 else .2),27,-.4),(1.7,.7,1),'skin',(0,0,side*20),(side*4,27,0))
            horn(r,'head',[(side*2.5,31,3),(side*4,34,3),(side*3.5,35,4)],.45,'trim')
        for i in range(3):box(r,'arm_r',(-8.15,13+i*2.5,-2.2),(4.3,.55,4.4),'accent',(0,0,12),(-6,16,0))
    if id in {'aion','aion_the_architect','elara_spirit'}:robe(r)
    if id.startswith('aion'):
        joint(r,'authority_ring',(0,26,6));band(r,'authority_ring',(0,26,6),11 if id=='aion' else 14,.28,'trim',16,(3,11) if id.endswith('architect') else ())
        # The prologue core is visibly retained behind the human head.
        joint(r,'original_core',(0,28,6.8));box(r,'original_core',(-2.4,25.6,6.4),(4.8,4.8,2.4),'cloth',(0,0,45),(0,28,7))
        for side in [-1,1]:
            joint(r,'pendant_'+str(side),(side*10,24,6))
            box(r,'pendant_'+str(side),(side*10-.8,22.8,5.7),(1.6,2.4,.5),'trim',(0,0,45),(side*10,24,6))
        if id=='aion_the_architect':
            # Separate whole Steve torso/arms while retaining exact base sizes.
            for p in r.parts:
                if p.get('steve_base')=='body':p['origin'][1]+=.65
                if p.get('steve_base') in {'arm_r','arm_l'}:p['origin'][0]+=(-.65 if p['steve_base']=='arm_r' else .65)
            for side in [-1,1]:
                for row in range(2):
                    x=side*(10+row*2);y=20-row*6;n=f'floating_arm_{side}_{row}'
                    joint(r,n,(x,y,5));box(r,n,(x-1.3,y-5,4),(2.6,8,2.6),'base',(0,0,-side*(35+row*20)),(x,y,5))
                    box(r,n,(x-1.35,y-4.5,3.9),(2.7,.6,2.8),'trim',(0,0,-side*(35+row*20)),(x,y,5))
            box(r,'head',(-.3,25,-4.32),(3.1,5,.3),'cloth')
            for i in range(4):
                x=(-1 if i%2 else 1)*(6+i);y=8+i*4;n='robe_fragment_'+str(i)
                joint(r,n,(x,y,5));box(r,n,(x-.5,y-1.6,4.8),(1,3.2,.5),'base',(0,0,i*35),(x,y,5))
    if id in {'caelum','kael_demon_king','dullahan'}:
        # Narrow waist plates and chest clasps carry detail without bulk.
        for side in [-1,1]:box(r,'body',(side*2.5-1.4,10,-2.7),(2.8,2.8,.4),'base',(0,0,-side*8),(side*2.5,13,-2.7))
        for side in [-1,1]:box(r,'body',(side*2.5-.35,21.4,-2.8),(.7,.65,.35),'trim')
    return r

def horse():
    r=Sculpt()
    box(r,'body',(-4,13,-8),(8,9,20));box(r,'body',(-3,20,-3),(6,2,8),'cloth')
    joint(r,'neck',(0,21,-6));box(r,'neck',(-2.5,20,-11),(5,11,6),'base',(-22,0,0),(0,21,-6))
    joint(r,'head',(0,29,-11),'neck');box(r,'head',(-2.8,27,-20),(5.6,6,10));box(r,'head',(-2.2,24,-23),(4.4,5,6))
    box(r,'head',(-2.4,29,-20.4),(4.8,2,.6),'edge')
    box(r,'neck',(-.6,23,-5),(1.2,9,1.5),'hair',(-22,0,0),(0,21,-6))
    for side in [-1,1]:
        horn(r,'head',[(side*1.8,32,-12),(side*2.3,36,-11)],.8,'base')
        box(r,'head',(side*2.8-.15,29,-18),(.3,.8,1.3),'eye')
        box(r,'body',(side*4-.3,15,-5),(.6,5,9),'edge')
        for pos,z in [('front',-5),('back',8)]:
            n=f'leg_{pos}_{side}';x=side*3
            joint(r,n,(x,15,z));bar(r,n,(x,15,z),(x,3,z+1),2.1,2.5)
            box(r,n,(x-1.3,1,z-.5),(2.6,2.5,3.4),'accent')
    joint(r,'tail',(0,19,11));bar(r,'tail',(0,19,11),(0,10,16),1.5,1.6,'hair')
    for x in [-3.2,3.2]:box(r,'body',(x-.3,13,-2),(.6,8,1),'trim')
    return r

def construct():
    r=Sculpt()
    box(r,'body',(-12,36,-7),(24,28,14));box(r,'body',(-10,34,-9),(20,23,18),'stone')
    for side in [-1,1]:
        x=side*9
        box(r,'body',(x-1.3,40,-9.9),(2.6,20,2),'bronze')
        for i in range(4):box(r,'body',(side*7-2,62+i*2,-4),(4,2,8-i),'edge')
        n='arm_'+str(side);joint(r,n,(side*17,58,0))
        box(r,n,(side*17-4.7,36,-5),(9.4,24,10))
        box(r,n,(side*17-5.5,53,-6),(11,9,12),'stone')
        joint(r,n+'_forearm',(side*17,37,0),n);box(r,n+'_forearm',(side*17-4,21,-4),(8,17,8))
        for j in range(3):box(r,n+'_forearm',(side*17-4+j*2.8,15,-4),(2.3,7,6),'metal')
        n='leg_'+str(side);joint(r,n,(side*6.5,35,0))
        box(r,n,(side*6.5-4,4,-4),(8,32,8));box(r,n,(side*6.5-4.7,0,-8),(9.4,5,13),'stone')
        box(r,n,(side*6.5-2.7,8,-4.8),(5.4,17,1),'metal')
        box(r,n,(side*6.5-.65,14,-5.4),(1.3,5,.4),'bronze')
    joint(r,'head',(0,65,0));box(r,'head',(-6,64,-4),(12,13,8),'stone');box(r,'head',(-7,73,-5),(14,4,10))
    for x in [-3,3]:box(r,'head',(x-1.5,69,-4.6),(3,.8,.5),'core')
    box(r,'head',(-1,65,-5.2),(2,4,1),'metal')
    joint(r,'core',(0,50,-10));band(r,'core',(0,50,-10),5.2,.9,'bronze',12)
    box(r,'core',(-2.3,47.7,-10.5),(4.6,4.6,.8),'core',(0,0,45),(0,50,-10))
    joint(r,'architecture_ring',(0,65,9));band(r,'architecture_ring',(0,65,9),17,1,'edge',16,(3,12))
    for i in range(7):box(r,'body',(-11,38+i*1.8,-10-i*.1),(4,1,2.5),'edge')
    # Small towers and recessed openings make the silhouette architectural.
    for side in [-1,1]:
        for j in range(3):box(r,'body',(side*9-3+j*2.4,68,-3),(1.6,5+j%2*2,3),'stone')
        for j in [-1,1]:box(r,'arm_'+str(side),(side*17+j*3-.6,62,-3),(1.2,7,2),'edge')
        box(r,'arm_'+str(side),(side*17-4,68,-3),(8,1.2,2.5),'stone')
        box(r,'leg_'+str(side),(side*6.5-1.1,26,-5.2),(2.2,6,.45),'void')
    for i,(x,y,z) in enumerate([(-10,60,-7),(11,55,6),(-17,50,-6),(7,27,-5)]):
        parent='arm_-1' if x==-17 else 'body';box(r,parent,(x,y-7,z),(.7,8,.7),'moss')
        box(r,parent,(x-.5,y-6,z-.1),(1.8,1.6,.6),'moss')
    return r

def whale():
    r=Sculpt()
    # Blue whale silhouette. Two pectoral fins, horizontal flukes, no dragon traits.
    for o,s in [((-12,12,-34),(24,20,37)),((-14,13,-8),(28,23,38)),((-11,15,25),(22,19,25))]:box(r,'body',o,s)
    box(r,'body',(-11,9,-33),(22,5,53),'belly')
    box(r,'body',(-12,15,-40),(24,13,13));box(r,'body',(-10,11,-39),(20,4,12),'belly')
    parent='body'
    for i,(w,z) in enumerate([(18,46),(12,59),(7,72),(4,85)]):
        n='tail_'+str(i);joint(r,n,(0,23,z),parent);box(r,n,(-w/2,23-w*.35,z),(w,w*.7,15));parent=n
    joint(r,'flukes',(0,23,98),parent)
    for side in [-1,1]:
        box(r,'body',(side*11.5-2,24,-27),(4,6,40),'edge',(0,0,side*25),(side*11.5,25,0))
        box(r,'body',(side*10-1.5,11,-27),(3,4,38),'belly',(0,0,-side*25),(side*10,12,0))
        box(r,'flukes',(side*8-9,22,96),(18,2,10),'fin',(0,-side*18,0),(0,23,98))
        n='fin_'+str(side);joint(r,n,(side*12,19,-6))
        box(r,n,(side*21-10,17,-8),(20,2.5,9),'fin',(0,side*18,-side*14),(side*12,19,-6))
        box(r,'body',(side*12-.2,20,-30),(.4,1.1,1.8),'eye')
        for i in range(3):box(r,'body',(side*11.1-.25,12,-27+i*8),(.5,.7,6),'scar')
    for i,(x,z) in enumerate([(-8,-4),(6,13),(-5,29)]):
        box(r,'body',(x,35,z),(3,1,3),'barnacle')
        horn(r,'body',[(x+1,36,z+1),(x,40,z+1),(x+2,42,z+2)],.8,'coral')
    box(r,'body',(-1,36,33),(2,3,6),'fin',(-20,0,0),(0,36,33))
    return r

def tree():
    r=Sculpt()
    box(r,'body',(-7,22,-5),(14,28,10))
    for side in [-1,1]:
        bar(r,'body',(side*6,24,0),(side*5,53,0),5,7)
        n='root_leg_'+str(side);joint(r,n,(side*4,25,0))
        bar(r,n,(side*4,25,0),(side*7,4,-2),5.5,7)
        for j in [-1,0,1]:bar(r,n,(side*7,7,-2),(side*7+j*4,1,-10),1.4,2,'edge')
        n='branch_arm_'+str(side);joint(r,n,(side*7,45,0))
        horn(r,n,[(side*7,45,0),(side*15,34,1),(side*17,20,-2)],4,'base')
        for j in [-1,0,1]:bar(r,n,(side*17+j*1.4,22,-2),(side*19+j*2,14,-4),1.1,1.5)
    joint(r,'face',(0,45,-5));box(r,'face',(-2.5,40.5,-5.4),(5,5,.6),'void')
    for x in [-2,2]:box(r,'face',(x-.8,45,-5.7),(1.6,.8,.3),'core')
    box(r,'face',(-1.2,41.5,-5.8),(2.4,2,.4),'core')
    for i in range(7):
        a=math.tau*i/7;x=math.cos(a)*16;z=math.sin(a)*12;y=53+(i%3)*3
        n='canopy_'+str(i);joint(r,n,(0,47,0))
        horn(r,n,[(0,47,0),(x*.6,y-2,z*.6),(x,y,z)],2.2,'base')
        box(r,n,(x-7,y,z-5),(14,4,10),'leaf',(0,i*27,0),(x,y,z))
        box(r,n,(x-5,y+3,z-4),(10,3,8),'moss',(0,i*27,0),(x,y,z))
        if i%2==0:box(r,n,(x,y-12,z),(.65,13,.65),'moss')
    return r

def small_dragon():
    r=Sculpt()
    box(r,'body',(-3.5,4,-3),(7,6,11));box(r,'body',(-2.8,3.6,-2),(5.6,1,9),'belly')
    joint(r,'neck',(0,8,-3));box(r,'neck',(-2.6,7,-6),(5.2,5,5))
    joint(r,'head',(0,12,-6),'neck');box(r,'head',(-4,10,-12),(8,6.5,7));box(r,'head',(-2.8,9.7,-15),(5.6,3.5,5))
    joint(r,'jaw',(0,10,-9),'head');box(r,'jaw',(-2.6,9.1,-14),(5.2,.9,5),'belly')
    for side in [-1,1]:
        box(r,'head',(side*2.8-.95,12.5,-12.25),(1.9,1.8,.3),'eye')
        box(r,'head',(side*2.8-.25,12.7,-12.55),(.5,1.35,.15),'void')
        box(r,'head',(side*2.8-.5,13.65,-12.72),(.4,.4,.15),'edge')
        box(r,'head',(side*4-.14,12.5,-10.8),(.28,1.7,2),'eye')
        box(r,'head',(side*4.16-.1,12.65,-10.2),(.2,1.25,.4),'void')
        horn(r,'head',[(side*3,16,-6),(side*4.6,19,-3),(side*5,19.5,-.5)],1.2,'horn')
        horn(r,'head',[(side*3.8,13,-6),(side*6.5,15,-3)],1,'edge')
        for pos,z in [('front',-2),('back',5)]:
            n=f'leg_{pos}_{side}';joint(r,n,(side*3,6,z));box(r,n,(side*3-1.2,1.2,z-1.5),(2.4,5,3))
            box(r,n,(side*3-1.3,.7,z-2.6),(2.6,1.4,4),'belly')
        n='wing_'+str(side);joint(r,n,(side*3,9,0),'body',(0,0,side*25))
        horn(r,n,[(side*3,9,0),(side*8,9,-4),(side*17,9,-1)],.8,'horn')
        for j in range(5):
            x=5+j*2.5;box(r,n,(-x-2.6 if side<0 else x,8.8,-2),(2.6,.35,8-j*.8),'wing')
    parent='body'
    for i in range(6):
        n='tail_'+str(i);w=3.3-i*.47;z=7+i*3.3;y=6-i*.5
        joint(r,n,(0,y,z),parent);box(r,n,(-w/2,y-w*.35,z),(w,w*.7,4));parent=n
    for z in [-1,3,7]:horn(r,'body',[(0,10,z),(0,11.8,z+1)],.6,'edge')
    return r

def impossible_dragon(anomaly=False):
    r=vharos_base()
    mapping={0:'base',1:'edge',2:'belly',3:'horn',4:'void',5:'eye',6:'wing'}
    for p in r.parts:p['material']=mapping[p['material']]
    # Replace the physical membranes with sparse hovering plates.
    r.parts=[p for p in r.parts if not (p['bone'].startswith('wing') and p['material']=='wing')]
    for side,label in [(-1,'left'),(1,'right')]:
        n='wing_'+label
        for i in range(4):
            x=25+i*20;box(r,n,(-x-12 if side<0 else x,40,-8+i*7),(12,.55,35-i*5),'wing',(0,side*12,0),(side*x,40,0))
    for p in r.parts:
        if p['bone'].startswith('neck_'):
            p['size']=[v*.83 for v in p['size']]
        if p['bone'].startswith('tail_'):
            p['origin'][1]+=3 if int(p['bone'].split('_')[1])%2 else -2
    if anomaly:
        # Same alien family, interrupted limb locations; no gore.
        for b in r.bones:
            if b['name']=='head':b['rotation']=[8,13,-14]
            if b['name']=='wing_left':b['rotation']=[0,0,38]
        for p in r.parts:
            if p['bone']=='head':p['origin'][1]+=4
    for i in range(5):
        x=(-1 if i%2 else 1)*(20+i*5);y=34+i*3;n='spatial_fragment_'+str(i)
        joint(r,n,(x,y,15+i*7));box(r,n,(x-1.3,y-4,15+i*7),(2.6,8,2),'accent',(0,i*15,i*30),(x,y,15+i*7))
    return r

def prologue():
    r=Sculpt();joint(r,'unknown_core',(0,8,0))
    box(r,'unknown_core',(-4,4,-4),(8,8,8),'void')
    box(r,'unknown_core',(-3,3,-3),(6,10,6),'void')
    box(r,'unknown_core',(-3,5,-5),(6,6,10),'void')
    joint(r,'thin_ring',(0,8,0));band(r,'thin_ring',(0,8,0),6.5,.18,'trim',12,(2,6,10))
    return r

def anomaly_form():
    """A compact, dislocated dragon silhouette distinct from the true form."""
    r=Sculpt()
    for i,(x,y,z) in enumerate([(0,12,0),(1.5,19,-2),(-1,26,-3)]):
        n='torso_fragment_'+str(i);joint(r,n,(x,y,z))
        box(r,n,(x-3.5,y-3,z-2.5),(7,5,5),'base',(i*11,0,-12+i*13),(x,y,z))
    joint(r,'unknown_core',(0,21,-5));box(r,'unknown_core',(-1.3,19.7,-5.5),(2.6,2.6,1.4),'void',(0,0,45),(0,21,-5))
    joint(r,'head',(0,31,-5));box(r,'head',(-3.5,30,-10),(7,6,6),'base',(8,-12,-9),(0,32,-7))
    joint(r,'jaw',(0,30,-6),'head');box(r,'jaw',(-2.5,27.8,-12),(5,1.4,7),'belly')
    for side in [-1,1]:
        box(r,'head',(side*2.5-.5,32,-10.8),(1,1,.5),'eye')
        horn(r,'head',[(side*3,35,-5),(side*5,38,-2),(side*5,38,2)],1,'horn')
        n='detached_forelimb_'+str(side);joint(r,n,(side*6,23,-2))
        bar(r,n,(side*6,23,-2),(side*11,18,-4),1.6,2)
        bar(r,n,(side*11,16.5,-4),(side*9,10,-6),1.2,1.6)
        n='detached_hindlimb_'+str(side);joint(r,n,(side*4,11,0))
        bar(r,n,(side*4,11,0),(side*7,6,2),2.1,2.5)
        box(r,n,(side*7-1,1,-2),(2,4,4),'belly')
        for i in range(3):
            x=side*(9+i*3.5);y=27-i*3;n=f'wing_fragment_{side}_{i}'
            joint(r,n,(x,y,4));box(r,n,(x-1.4,y-4,4),(2.8,8,.5),'wing',(0,side*20,side*(40-i*18)),(x,y,4))
    parent='body'
    for i in range(5):
        x=math.sin(i*.65)*5;y=12-i*1.3;z=4+i*4.4;w=3-i*.45;n='tail_fragment_'+str(i)
        joint(r,n,(x,y,z),parent);box(r,n,(x-w/2,y-w*.4,z),(w,w*.8,3.5),'base');parent=n
    for i,(x,y) in enumerate([(-9,35),(8,39),(-13,17),(11,8)]):
        n='orbit_fragment_'+str(i);joint(r,n,(x,y,0));box(r,n,(x-.5,y-1.8,0),(1,3.6,.8),'accent',(0,i*17,i*29),(x,y,0))
    return r

SPECS=[
 ('vharos','I','Vharos','Ancient dragon',38,'length',140,lambda:vharos_base()),
 ('dullahan','II','The Dullahan','Headless rider',1.8,'player',65,lambda:humanoid('dullahan')),
 ('dullahan_horse','II','Dullahan Horse','Spectral horse',2.4,'height',50,horse),
 ('caelum','III','Caelum','Fallen hero',1.8,'player',70,lambda:humanoid('caelum')),
 ('elara_spirit','III','Elara','Supporting spirit',1.8,'player',55,lambda:humanoid('elara_spirit')),
 ('kael_hunter','IV','Kael','Hunter',1.8,'player',60,lambda:humanoid('kael_hunter')),
 ('kael_demon_king','IV','Kael','Demon king',1.8,'player',90,lambda:humanoid('kael_demon_king')),
 ('orun','V','Orun','Walking architecture',96,'height',130,construct),
 ('sir_seraphiel','VI','Seraphiel','Angel',1.8,'player',120,lambda:humanoid('sir_seraphiel')),
 ('fallen_seraphiel','VI','Seraphiel','Fallen',1.8,'player',120,lambda:humanoid('fallen_seraphiel')),
 ('the_nameless_knight','VII','The Nameless Knight','Cloaked swordsman',1.8,'player',60,lambda:humanoid('the_nameless_knight')),
 ('thalassia','VIII','Thalassia','Primordial whale',50,'length',65,whale),
 ('verdant_giant','VIII','Verdant','Ancient tree',30,'height',95,tree),
 ('verdant_the_last_father','VIII','Verdant','The Last Father',1.8,'player',90,lambda:humanoid('verdant_the_last_father')),
 ('morrow_anomaly','IX','Morrow','Anomaly',3.5,'height',80,anomaly_form),
 ('little_morrow','IX','Little Morrow','Companion',.75,'height',85,small_dragon),
 ('true_morrow','IX','True Morrow','The Unwritten Dragon',28,'length',140,impossible_dragon),
 ('aion_prologue','X','???','Prologue presence',1,'height',25,prologue),
 ('aion','X','AION','The Architect',1.8,'player',105,lambda:humanoid('aion')),
 ('aion_the_architect','X','AION','Authority unbound',1.8,'player',110,lambda:humanoid('aion_the_architect')),
]

def export(spec):
    id,roman,name,form,size,axis,budget,builder=spec;r=builder();folder=OUT/id;folder.mkdir(parents=True,exist_ok=True)
    palette=PALETTES[id]
    if id=='vharos':
        mapping={0:'base',1:'edge',2:'belly',3:'bone',4:'void',5:'eye',6:'wing'}
        for p in r.parts:p['material']=mapping[p['material']]
    r=prepare_model(id,r)
    tex=paint_atlas(id,r,palette);tex.save(folder/'texture.png')
    e={'id':id+'_studio','name':name+' | '+form,'size':size,'texture_width':tex.width,'texture_height':tex.height,
       'geometry':str((folder/(id+'.geo.json')).relative_to(ROOT)),'texture':str((folder/'texture.png').relative_to(ROOT))}
    dump(ROOT/e['geometry'],geometry(e,r))
    vs=np.concatenate([v for v,uv,f in mesh(e)])
    # Steve base is uniformly scaled, never stretched; accessories do not set body height.
    factor=size*16/32 if axis=='player' else size*16/np.ptp(vs[:,2 if axis=='length' else 1])
    r.scaled(factor);dump(ROOT/e['geometry'],geometry(e,r))
    model=bbmodel(e,r,ROOT/e['texture'],{})
    for el,p in zip(model['elements'],r.parts):el['name']=p['bone']+' / '+p['material_name']
    dump(folder/(id+'.bbmodel'),model)
    vs=np.concatenate([v for v,uv,f in mesh(e)]);dims=np.ptp(vs,axis=0)/16
    # Gates check actual exported file, not only the author's intended counts.
    parsed=json.loads((ROOT/e['geometry']).read_text())['minecraft:geometry'][0];bn={b['name'] for b in parsed['bones']}
    assert len(bn)==len(parsed['bones']),id
    assert all(b.get('parent') in bn for b in parsed['bones'] if 'parent' in b),id
    parents={b['name']:b.get('parent') for b in parsed['bones']}
    for bone_name in bn:
        chain=set();n=bone_name
        while n is not None:
            assert n not in chain,(id,'cyclic group',n)
            chain.add(n);n=parents[n]
    assert len(r.parts)<=budget,(id,len(r.parts),budget)
    assert not model['animations'],id
    import base64
    assert base64.b64decode(model['textures'][0]['source'].split(',')[1])==(folder/'texture.png').read_bytes(),id
    for b in parsed['bones']:
        for cube in b.get('cubes',[]):
            for uv in cube['uv'].values():
                x,y=uv['uv'];w,h=uv['uv_size']
                assert 0<=x<x+w<=tex.width and 0<=y<y+h<=tex.height,(id,'UV outside texture')
    assert all(all(s>0 for s in c['size']) for b in parsed['bones'] for c in b.get('cubes',[])),id
    assert all(word not in b.lower() for b in bn for word in ['sword','blade','spear','weapon','bow']),id
    base={p['steve_base']:p for p in r.parts if p.get('steve_base')}
    if axis=='player':
        assert len(base)==(5 if id=='dullahan' else 6),id
        for n,p in base.items():assert np.allclose(p['size'],np.array(PARTS[n][1])*factor),(id,n)
    if id in {'sir_seraphiel','fallen_seraphiel'}:assert len([n for n in bn if n.startswith('wing_')])==6,id
    record={'id':id,'colossus':roman,'name':name,'form':form,'cubes':len(r.parts),'budget':budget,'groups':len(r.bones),
        'dimensions_blocks':dict(zip(['width','height','length'],map(lambda x:round(float(x),3),dims))),
        'body_height_blocks':size if axis=='player' else None,'source':str((folder/(id+'.bbmodel')).relative_to(ROOT)),
        'steve_base_parts':len(base),'stage':'original pixel-art texture and model revision','final_texture':False,'painted_texture':True,
        'texture':str((folder/'texture.png').relative_to(ROOT)),'texture_size':[tex.width,tex.height],'animations':0,'weapons':False,
        'blockbench_application_test':False,'bedrock_in_game_test':False}
    dump(folder/'review.json',record)
    return e,record

def reviews(all_entries):
    fontpath='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';font=ImageFont.truetype(fontpath,18);big=ImageFont.truetype(fontpath,28)
    previews=OUT/'previews';previews.mkdir(exist_ok=True)
    contact=Image.new('RGB',(1600,90+5*450),BACKGROUND);cd=ImageDraw.Draw(contact)
    cd.text((24,18),'UNWRITTEN / TEN COLOSSI / ALL FORMS',font=big,fill='#d8d0c4')
    cd.text((24,56),'Actual textured models. Original pixel painting. Individual tile scale.',font=font,fill='#9cabb6')
    entries={r['id']:(e,r) for e,r in all_entries}
    for i,(e,r) in enumerate(all_entries):
        id=r['id'];player=r['body_height_blocks'] is not None
        angles=[(-32,10),(0,0),(135,10)] if player else [(-48,22),(-90,0),(0,12)]
        sheet=Image.new('RGB',(1440,575),BACKGROUND);d=ImageDraw.Draw(sheet)
        d.text((24,12),r['colossus']+' / '+r['name'].upper()+' / '+r['form'],font=big,fill='#d8d0c4')
        d.text((24,52),f'{r["cubes"]} cubes | {r["texture_size"][0]}x{r["texture_size"][1]} original pixel atlas | Model + texture review',font=font,fill='#9cabb6')
        for a,(yaw,pitch) in enumerate(angles):
            pic,_=render(e,480,yaw=yaw,pitch=pitch);sheet.paste(pic,(a*480,80))
        sheet.save(OUT/id/'preview.png')
        tile,_=render(e,400,yaw=angles[0][0],pitch=angles[0][1]);x=(i%4)*400;y=90+(i//4)*450
        contact.paste(tile,(x,y));cd.text((x+16,y+399),r['colossus']+' / '+r['name'],font=font,fill='#d8d0c4')
        cd.text((x+16,y+424),r['form']+f' / {r["cubes"]} cubes',font=font,fill='#9cabb6')
    contact.save(previews/'all_forms.png')
    selected=['vharos','dullahan','caelum','kael_demon_king','orun','fallen_seraphiel','the_nameless_knight','thalassia','verdant_giant','verdant_the_last_father','little_morrow','aion']
    main=Image.new('RGB',(1600,90+3*465),BACKGROUND);d=ImageDraw.Draw(main)
    d.text((24,18),'DECEM FATA / MODEL GALLERY',font=big,fill='#d8d0c4')
    d.text((24,56),'Ten existences. VIII has two beings. All renders use their own scale.',font=font,fill='#9cabb6')
    for i,id in enumerate(selected):
        e,r=entries[id];pic,_=render(e,400,yaw=-32 if r['body_height_blocks'] else -48,pitch=12 if r['body_height_blocks'] else 22)
        x=i%4*400;y=90+i//4*465;main.paste(pic,(x,y));d.text((x+16,y+402),r['colossus']+' / '+r['name'],font=font,fill='#d8d0c4');d.text((x+16,y+428),r['form'],font=font,fill='#9cabb6')
    main.save(previews/'ten_colossi.png')
    closeups=Image.new('RGB',(1500,555),BACKGROUND);draw=ImageDraw.Draw(closeups)
    for i,id in enumerate(['caelum','kael_demon_king','aion']):
        e,r=entries[id];pic,_=render(e,500,yaw=-30,pitch=10);closeups.paste(pic,(i*500,0))
        draw.text((i*500+24,520),r['name']+' / textured model',font=font,fill='#d8d0c4')
    closeups.save(previews/'texture_closeups.png')
    return previews

def build():
    all_entries=[]
    for spec in SPECS:
        e,r=export(spec);all_entries.append((e,r));print(f'{r["id"]}: {r["cubes"]}/{r["budget"]} cubes',flush=True)
    records=[r for e,r in all_entries]
    assert set(r['colossus'] for r in records)=={'I','II','III','IV','V','VI','VII','VIII','IX','X'}
    report={'forms':len(records),'colossi':10,'total_cubes':sum(r['cubes'] for r in records),'entries':records,'checks':'passed',
        'scope':'Models, accessories and authored pixel-art textures. Animation, weapons and runtime integration remain deferred.'}
    dump(OUT/'catalog.json',report);reviews(all_entries)
    lines=['# Ten Colossi: model review','','All ten Colossi and their forms now follow the simplified Vharos approach. Twenty editable models include Dullahan\'s horse and Elara. Original pixel-art textures now replace flat material swatches: stepped shading, readable faces, cloth folds, metal bevels, scales and material-specific detail.','','![Ten Colossi](previews/ten_colossi.png)','','[All 20 forms](previews/all_forms.png) | [Download model bundle](Ten_Colossi_Models.zip) | [Validation and dimensions](catalog.json)','','Humanoids retain the six Steve body parts, uniformly sized to a 1.8-block body. Hair, clothing, armor, wings and rings are separate geometry. Dullahan omits the attached head; Architect separates parts while retaining their proportions. Accessories can extend beyond body height.','','| Colossus | Form | Cubes | Model | Preview |','|---|---|---:|---|---|']
    for r in records:
        id=r['id'];lines.append(f'| {r["colossus"]}: {r["name"]} | {r["form"]} | {r["cubes"]} / {r["budget"]} | [Blockbench]({id}/{id}.bbmodel) | [Three views]({id}/preview.png) |')
    lines+=['','## Scope and validation','','The current model revision lives in `model_studio/`. Previous runtime packs and animation sources are unchanged and are not this revision. No weapons are present. Each texture.png is an original painted atlas with unique padded face islands, embedded in its Blockbench model. Painting is generated from authored pixel-art rules and character palettes, with no reference-image pixels or downloaded assets. This is an art revision, not a claim of final quality approval. Animation authoring remains deferred.','','Export parsing, cube budgets, positive dimensions, bone parent references, Steve proportions, six Seraphiel wings, no weapon groups and zero animation clips are checked during build. Renders come from actual exported geometry. Blockbench application import and Bedrock runtime testing remain pending.','','Orun remains a visual model, not a climbable structure or a completed modular encounter. Different preview tiles use different scale. Read `catalog.json` for dimensions.','','The painted palette preserves each identity: pearl/black Seraphiel, pale Little Morrow, an ocean-blue whale and ivory/gold AION. No horror effects or body gore are added.']
    (OUT/'README.md').write_text('\n'.join(lines)+'\n')
    with zipfile.ZipFile(OUT/'Ten_Colossi_Models.zip','w',zipfile.ZIP_DEFLATED) as z:
        for r in records:
            for filename in [r['id']+'.bbmodel',r['id']+'.geo.json','preview.png','texture.png','review.json']:
                p=OUT/r['id']/filename;zi=zipfile.ZipInfo(str(p.relative_to(OUT)),date_time=(2026,1,1,0,0,0));zi.compress_type=zipfile.ZIP_DEFLATED;z.writestr(zi,p.read_bytes())
        for name in ['catalog.json','README.md','previews/ten_colossi.png','previews/all_forms.png','previews/texture_closeups.png']:
            zi=zipfile.ZipInfo(name,date_time=(2026,1,1,0,0,0));zi.compress_type=zipfile.ZIP_DEFLATED;z.writestr(zi,(OUT/name).read_bytes())
    with zipfile.ZipFile(OUT/'Ten_Colossi_Models.zip') as z:
        assert len([n for n in z.namelist() if n.endswith('.bbmodel')])==20
        for r in records:assert z.read(r['id']+'/'+r['id']+'.bbmodel')==(OUT/r['id']/(r['id']+'.bbmodel')).read_bytes()
    print('All 20 model forms exported, reviewed and packaged.',flush=True)

if __name__=='__main__':build()
