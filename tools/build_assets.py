#!/usr/bin/env python3
"""Deterministic UNWRITTEN first-pass asset factory. Python 3.10+, Pillow.

The roster and these authored rig recipes are source. Outputs are editable copies.
Do not regenerate over hand edits without first moving them to source_overrides/.
"""
import base64
import hashlib
import json
import math
from pathlib import Path
import random
import re
import shutil
import uuid
import zipfile
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
RP = ROOT / 'packs/UNWRITTEN_RP'
BP = ROOT / 'packs/UNWRITTEN_Preview_BP'
NS = uuid.UUID('ddf3a597-5365-4180-9d46-4c5fa20c7911')

def uid(s): return str(uuid.uuid5(NS, s))
def dump(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False)+'\n')
def slug(s): return re.sub(r'[^a-z0-9]+', '_', s.lower()).strip('_')

PALETTES = {
 'green':('#638845','#afc877'), 'brown':('#715142','#baa17c'),
 'dark':('#272936','#858493'), 'bone':('#b8af91','#eee0b6'),
 'mud':('#574a36','#90825d'), 'gold':('#bb893a','#ffe4a0'),
 'white':('#d7dedb','#fff0c0'), 'blue':('#386d9a','#95e4ed'),
 'red':('#923d3d','#e99666'), 'poison':('#576f3d','#b8f077'),
 'copper':('#9c633f','#ddac70'), 'gray':('#636975','#bac8c8'),
 'stone':('#616d71','#8bd0cc'), 'spectral':('#83b8b4','#d1fff2'),
 'purple':('#705179','#d2a0ed'), 'abyss':('#1b4052','#54dccc'),
 'shadow':('#24233b','#ad8bdb'), 'fire':('#a33c28','#ffd077'),
 'ice':('#719ab5','#ddfcff'), 'sand':('#ac9367','#d7e7e0'),
 'crimson':('#852d46','#f595a4'), 'flesh':('#9d6264','#ddaca1'),
 'coral':('#a56f70','#83d3c9'), 'wood':('#665541','#91b969'),
 'orange':('#bd713c','#f4d8a3'), 'charcoal':('#303035','#ff8c37'),
 'steel':('#59636c','#b9c8c8'), 'ivory':('#d8cfb0','#a696da'),
}
def rgb(h): return tuple(bytes.fromhex(h.lstrip('#')))

def read_roster():
    entries=[]
    for line in (ROOT/'catalog/roster.txt').read_text().splitlines():
        if not line or line.startswith('#'): continue
        if line.startswith('['):
            group, biome=line[1:-1].split('|'); continue
        name, family, size, features=line.split('|')
        f=features.split(); palette=next((x for x in f if x in PALETTES),'brown')
        entries.append(dict(id=slug(name),name=name,family=family,size=float(size),
            features=f,palette=palette,category=group,biome=biome))
    assert len({e['id'] for e in entries})==len(entries)
    return entries

class Rig:
    def __init__(self): self.bones=[]; self.parts=[]
    def bone(self,name,pivot=(0,0,0),parent='root',rotation=None):
        b=dict(name=name,pivot=list(pivot))
        if parent is not None: b['parent']=parent
        if rotation: b['rotation']=list(rotation)
        self.bones.append(b); return name
    def cube(self,bone,origin,size,material=0):
        self.parts.append(dict(bone=bone,origin=list(origin),size=list(size),material=material))
    def box(self,name,pivot,origin,size,material=0,parent='body',rotation=None):
        self.bone(name,pivot,parent,rotation); self.cube(name,origin,size,material); return name
    def has(self,n): return any(b['name']==n for b in self.bones)

def rig_for(e):
    r=Rig(); r.bone('root',parent=None); f=e['family']; t=set(e['features'])
    def box(*a,**kw): return r.box(*a,**kw)
    def cube(*a,**kw): return r.cube(*a,**kw)
    def eyes(head='head',x=2,y=24,z=-4.1,one=False):
        for sx in ([0] if one else [-x,x]):
            cube(head,(sx-0.9,y,z),(1.8,1.7,0.5),4)
            cube(head,(sx-0.4,y+0.25,z-0.2),(0.8,1,0.4),5)
    def tail(parent='body',start=(0,10,8),count=4,width=3):
        x,y,z=start
        for i in range(count):
            n='tail' if i==0 else f'tail_{i}'
            box(n,(x,y,z),(x-width/2,y-width/2,z),(width,width,5),0,parent)
            parent=n; z+=4.7; width=max(0.8,width*0.76)
    def wings(parent='body',y=19,z=1,pairs=1,feather=False):
        for p in range(pairs):
            for sign,side in [(-1,'l'),(1,'r')]:
                n=f'wing_{side}'+(f'_{p}' if p else '')
                yy=y-p*4
                box(n,(sign*3,yy,z),(-15 if sign<0 else 3,yy-1,z),(12,2,2),2,parent,(0,0,sign*(12+p*15)))
                # Stepped membrane/feathers creates a scalloped wing outline.
                for j in range(4):
                    xx=sign*(5+j*2.5)
                    cube(n,(xx-1.2,yy-2-j*0.5,z+1),(2.4,1,7-j),6 if feather else 1)
                tip=n+'_tip'
                box(tip,(sign*14,yy,z),(-22 if sign<0 else 14,yy-0.5,z),(8,1,1.5),2,n,(0,sign*12,0))
                for j in range(3):
                    xx=sign*(15+j*2.3)
                    cube(tip,(xx-1,yy-1,z+1),(2,0.7,5-j),6 if feather else 1)
    human={'humanoid','goblin','orc','heavy','skeleton','reptile','demon','angel','architect','anomaly','fairy'}
    quad={'wolf','boar','cat','fox','horse','deer','behemoth','chimera','griffin','manticore','drake','dragon','wyvern','pet_dragon','hydra'}
    if f in human:
        small=f=='goblin'; heavy=f in {'orc','heavy'}; thin=f=='skeleton'
        hip=11 if small else 13; w=12 if heavy else (5 if thin else 8)
        box('body',(0,hip,0),(-w/2,hip,-2.5),(w,10,5),0,'root')
        box('head',(0,hip+10,0),(-4,hip+10,-4),(8,8,8),0)
        eyes(y=hip+14,one='one_eye' in t)
        for sign,side in [(-1,'l'),(1,'r')]:
            legw=2 if thin else 3.5
            xx=sign*(w/2+1.5)
            box('arm_'+side,(xx,hip+9,0),(xx-1.5,hip,-1.5),(3,9,3),0)
            box('forearm_'+side,(xx,hip+1,0),(xx-1.5,hip-5,-1.5),(3,6,3),0,'arm_'+side)
            lx=sign*(w/4)
            box('leg_'+side,(lx,hip,0),(lx-legw/2,5,-1.6),(legw,hip-5,3.2),0)
            box('shin_'+side,(lx,6,0),(lx-legw/2,0,-2),(legw,6,4),0,'leg_'+side)
        if small or 'ears' in t:
            for sign in [-1,1]: cube('head',(-7 if sign<0 else 4,hip+13,-1),(3,3,1.5),0)
        if f=='reptile' or 'wolf_head' in t or 'bull' in t:
            cube('head',(-2.8,hip+10,-7),(5.6,3.5,4),1); tail(start=(0,hip,2))
        if f=='skeleton':
            for y in [hip+3,hip+6,hip+9]: cube('body',(-3.5,y,-3),(7,1,1),1)
            cube('head',(-2,hip+10.2,-4.2),(4,1,0.5),5)
        if 'belly' in t: cube('body',(-6,hip,-5),(12,8,7),1)
        if f in {'humanoid','goblin','orc','demon','angel','heavy'}:
            # Tunic, belt and boots separate skin from costume without extra rigs.
            cube('body',(-w/2-.15,hip,-2.7),(w+.3,6,5.4),3)
            cube('body',(-w/2-.25,hip+1,-2.85),(w+.5,1.2,5.7),2)
            for side in ['l','r']:
                for p in list(r.parts):
                    if p['bone']=='shin_'+side:
                        x,y,z=p['origin']; ww,hh,dd=p['size']; cube('shin_'+side,(x-.1,y,z-.1),(ww+.2,2,dd+.2),3)
        if 'headless' in t:
            r.parts=[p for p in r.parts if p['bone']!='head']
            cube('head',(-2,hip+10,-2),(4,0.8,4),4)
        if f=='anomaly':
            for i,b in enumerate(r.bones):
                if b['name'].startswith(('head','arm','shin')): b['rotation']=[i*7,0,i*9]
        if f=='architect':
            # True disconnected torso silhouette, with three independently rigged pairs.
            r.parts=[p for p in r.parts if p['bone']!='body']
            for i in range(3): cube('body',(-4,hip+i*3.6,-2.5),(8,2.5,5),1)
            for i in [1,2]:
                for sign,side in [(-1,'l'),(1,'r')]:
                    box(f'extra_arm_{side}_{i}',(sign*8,hip+8-i*4,1),(sign*8-1,hip+1-i*4,-1),(2,7,2),1,rotation=(0,0,sign*30*i))
    elif f in quad or f=='rider':
        long=f in {'dragon','wyvern','drake'}; baby=f=='pet_dragon'
        leg=4 if baby or f in {'boar','cat','fox'} else 8
        length=18 if long else 13; w=12 if f=='behemoth' else 8
        box('body',(0,leg+3,0),(-w/2,leg,-length/2),(w,7,length),0,'root')
        box('neck',(0,leg+5,-length/2+2),(-3,leg+3,-length/2-3),(6,7,5),0)
        heady=leg+8; headz=-length/2-4
        box('head',(0,heady,headz),(-4,heady-1,headz-4),(8,6 if not baby else 8,7),0,'neck')
        cube('head',(-2.5,heady-1,headz-7),(5,3,4),1)
        eyes(y=heady+2,z=headz-4.2,x=2.5)
        box('jaw',(0,heady-0.7,headz),(-2.5,heady-2,headz-7),(5,1.5,6),1,'head')
        for side,sign in [('l',-1),('r',1)]:
            for pos,z in [('front',-length/2+3),('back',length/2-3)]:
                if f=='wyvern' and pos=='front': continue
                x=sign*(w/2-0.5); n=f'leg_{pos}_{side}'
                box(n,(x,leg+2,z),(x-1.5,2,z-1.5),(3,leg,3),0)
                box(n+'_paw',(x,2,z),(x-1.6,0,z-3),(3.2,2.5,4.5),2,n)
        tail(start=(0,leg+4,length/2-1),count=6 if long else 3,width=4 if long else 2.5)
        if f in {'cat','fox','wolf','pet_dragon'}:
            for sign in [-1,1]: cube('head',(sign*3-1,heady+5,headz-1),(2,4 if baby else 3,2),0)
        if f=='boar' or 'tusks' in t:
            for sign in [-1,1]: cube('head',(sign*3-0.5,heady-1,headz-6),(1,4,1),2)
        if f in {'horse','deer'}:
            cube('neck',(-2,leg+7,headz+1),(4,7,4),0)
        if f in {'griffin','manticore'} or 'wings' in t or f=='wyvern':
            wings(y=leg+7,feather=f=='griffin')
        if f=='griffin': cube('head',(-2,heady+0.5,headz-8),(4,2,3),2)
        if f=='manticore' or 'stinger' in t:
            box('stinger',(0,leg+4,length/2+12),(-1,leg+3,length/2+10),(2,5,2),2,'tail_2')
        headcount=7 if 'heads7' in t else 5 if 'heads5' in t else 3 if 'heads3' in t else 2 if 'heads2' in t else 1
        if f=='hydra': headcount=max(3,headcount)
        for i in range(1,headcount):
            sign=-1 if i%2 else 1; xx=sign*(6+((i-1)//2)*5); yy=heady+((i-1)//2)*3
            n=f'neck_{i}'; box(n,(xx,leg+5,-4),(xx-1.7,leg+4,-8),(3.4,yy-leg,4),0)
            h=f'head_{i}'; box(h,(xx,yy,-8),(xx-2.5,yy,-12),(5,4,6),0,n)
            for dx in [-1.3,1.3]: cube(h,(xx+dx-0.4,yy+2,-12.2),(0.8,0.8,0.4),4)
        if f=='chimera':
            box('goat_head',(0,leg+8,2),(-2.5,leg+8,1),(5,5,5),6)
            cube('goat_head',(-2,leg+12,2),(1,4,1),2); cube('goat_head',(1,leg+12,2),(1,4,1),2)
            cube('tail_2',(-1,leg+3,length/2+12),(2,3,4),3)
        if f=='rider':
            box('rider_body',(0,leg+7,1),(-3,leg+7,-2),(6,7,4),3)
            box('rider_head',(0,leg+14,0),(-3,leg+14,-3),(6,5,5),0,'rider_body')
            for sign in [-1,1]:
                box('rider_arm_'+str(sign),(sign*4,leg+13,0),(sign*4-1,leg+8,-1),(2,6,2),0,'rider_body')
    elif f in {'bird','bat','harpy'}:
        box('body',(0,9,0),(-3,5,-2),(6,9,5),0,'root')
        box('head',(0,14,-1),(-3,14,-4),(6,6,6),0)
        eyes(y=17,z=-4.3,x=1.6)
        cube('head',(-1,14,-6),(2,2,3),2)
        wings(y=12,feather=f!='bat')
        for sign,side in [(-1,'l'),(1,'r')]: box('leg_'+side,(sign*2,6,0),(sign*2-0.5,1,-1),(1,5,2),2)
        tail(start=(0,7,2),count=2,width=2)
    elif f in {'rabbit'}:
        box('body',(0,4,0),(-3,2,-3),(6,6,8),0,'root')
        box('head',(0,7,-3),(-3,6,-6),(6,5,5),0)
        eyes(y=8,z=-6.2,x=1.7)
        for sign,side in [(-1,'l'),(1,'r')]:
            box('ear_'+side,(sign*2,10,-2),(sign*2-0.7,10,-2),(1.4,7,1.5),0,'head',(0,0,sign*10))
            cube('ear_'+side,(sign*2-0.35,11,-2.1),(0.7,5,0.3),1)
            box('leg_'+side,(sign*2,4,1),(sign*2-1.5,0,0),(3,4,5),0)
        cube('body',(-1.5,4,5),(3,3,3),6)
    elif f=='slime':
        box('body',(0,0,0),(-6,0,-6),(12,9,12),7,'root')
        cube('body',(-5,9,-5),(10,2,10),7)
        box('core',(0,5,0),(-2.3,3,-2.3),(4.6,4.6,4.6),4)
        box('head',(0,6,-5.8),(-3.5,5.5,-6.15),(2,1.4,0.3),5)
        cube('head',(1.5,5.5,-6.15),(2,1.4,0.3),5)
    elif f in {'spider','scorpion','insect','beetle','crab'}:
        box('body',(0,6,2),(-4,3,-1),(8,6,10),0,'root')
        box('head',(0,6,-3),(-3,3,-6),(6,5,5),0)
        eyes(y=6,z=-6.2,x=1.6)
        count=4 if f=='spider' else 3
        for side,sign in [('l',-1),('r',1)]:
            for i in range(count):
                z=-3+i*3; n=f'leg_{side}_{i}'
                box(n,(sign*3,6,z),(-10 if sign<0 else 3,5,z),(7,1.5,1.5),0,rotation=(0,sign*(i-1)*14,0))
                box(n+'_tip',(sign*9,5,z),(sign*9-0.7,0,z),(1.4,6,1.4),2,n,(0,0,-sign*12))
            if f in {'scorpion','crab'}:
                n='claw_'+side; box(n,(sign*4,5,-3),(sign*6-2,3,-11),(4,4,7),0)
                box(n+'_pincer',(sign*6,4,-10),(sign*6-0.6,4,-14),(1.2,2,5),2,n)
        if f=='scorpion':
            for i in range(4):
                box('sting_'+str(i),(0,6+i*3,8-i),(-1,6+i*3,7-i),(2,4,2),0,'body' if i==0 else 'sting_'+str(i-1))
            cube('sting_3',(-0.7,17,2),(1.4,2,4),2)
        if f=='beetle':
            cube('body',(-4.2,7,0),(4,2.5,8),1); cube('body',(0.2,7,0),(4,2.5,8),1)
        if 'eggs' in t:
            for x,z in [(-2,3),(1,5),(-1,7)]: cube('body',(x,8,z),(2.5,3,2.5),6)
    elif f in {'golem','treant'}:
        wood=f=='treant'; box('body',(0,13,0),(-7,11,-4),(14,15,8),0,'root')
        box('head',(0,26,0),(-4,26,-3),(8,7,6),0); eyes(y=29,z=-3.2)
        for sign,side in [(-1,'l'),(1,'r')]:
            box('arm_'+side,(sign*8,24,0),(sign*10-2,10,-2.5),(4,14,5),0,rotation=(0,0,sign*8))
            box('forearm_'+side,(sign*10,11,0),(sign*10-2.5,5,-3),(5,7,6),0,'arm_'+side)
            box('leg_'+side,(sign*4,12,0),(sign*4-2.5,0,-3),(5,12,6),0)
            if wood:
                for j in range(3): cube('leg_'+side,(sign*4-3+j*2,0,-5-j),(1.5,2,9),0)
        if wood:
            for i in range(5):
                x=(i-2)*4; box(f'branch_{i}',(x,25,0),(x-1,24,-1),(2,11-abs(i-2),2),0,rotation=(0,0,(i-2)*-14))
    elif f in {'spirit','wisp'}:
        box('body',(0,12,0),(-3,10,-2),(6,10,4),0,'root')
        box('head',(0,20,0),(-3,20,-3),(6,6,6),0)
        if 'faceless' not in t: eyes(y=23,z=-3.2,x=1.6)
        for i in range(4): box('cloth_'+str(i),((i-1.5)*2,12,1),((i-1.5)*2-0.8,3+i%2,0),(1.6,9-i%2,2),1)
        for sign,side in [(-1,'l'),(1,'r')]: box('arm_'+side,(sign*4,18,0),(sign*4-1,10,-1),(2,9,2),0)
    elif f in {'serpent','worm','fish','whale','mermaid'}:
        wide=f in {'fish','whale'}; radius=6 if wide else 3
        box('body',(0,8,0),(-radius,8-radius,-6),(radius*2,radius*2,12),0,'root')
        box('head',(0,8,-6),(-radius,8-radius,-13),(radius*2,radius*2,8),0)
        eyes(y=10,z=-13.2,x=radius*0.6)
        box('jaw',(0,5,-7),(-radius,3,-13),(radius*2,2,8),1,'head')
        tail(start=(0,8,5),count=9 if f in {'serpent','worm'} else 4,width=radius*1.7)
        for sign,side in [(-1,'l'),(1,'r')]:
            for i in range(3 if 'fins6' in t else 1):
                box(f'fin_{side}_{i}',(sign*radius,8,i*4),(-radius-7 if sign<0 else radius,7,i*4),(7,1,4),1)
        box('fluke',(0,8,23),(-8,7,22),(16,1.5,4),1,'tail_3')
        if f=='fish': cube('body',(-0.5,13,0),(1,5,6),2)
        if f=='mermaid':
            box('upper_body',(0,12,-3),(-3,12,-5),(6,10,4),6)
            box('siren_head',(0,22,-3),(-3,22,-6),(6,6,6),6,'upper_body')
    elif f in {'kraken','jellyfish'}:
        box('body',(0,12,0),(-6,10,-6),(12,9,12),0,'root')
        cube('body',(-4.5,19,-4.5),(9,3,9),1)
        box('head',(0,13,-5.8),(-4,13,-6.2),(2,2,0.5),4); cube('head',(2,13,-6.2),(2,2,0.5),4)
        for i in range(8):
            angle=math.tau*i/8; x=math.cos(angle)*4; z=math.sin(angle)*4
            n=f'tentacle_{i}'
            box(n,(x,12,z),(x-1,4,z-1),(2,8,2),0,rotation=(math.sin(angle)*25,0,-math.cos(angle)*25))
            box(n+'_tip',(x,5,z),(x-0.7,-2,z-0.7),(1.4,7,1.4),1,n)
    elif f in {'plant','mushroom'}:
        box('body',(0,0,0),(-2,0,-2),(4,9,4),0,'root')
        box('head',(0,9,0),(-5,8,-5),(10,5,10),1)
        cube('head',(-3.5,13,-3.5),(7,2,7),0); eyes(y=10,z=-5.2)
        if 'mouth' in t: cube('head',(-4,8,-5.2),(8,2,0.4),5)
        for sign,side in [(-1,'l'),(1,'r')]: box('leaf_'+side,(sign*2,4,0),(sign*4-2,3,-1),(4,1,4),3)
    elif f=='crawler':
        box('body',(0,3,0),(-4,0,-3),(8,5,8),0,'root')
        box('head',(0,4,-3),(-3,3,-6),(6,4,4),0); eyes(y=5,z=-6.2)
        for side,sign in [('l',-1),('r',1)]:
            box('arm_'+side,(sign*4,4,-1),(sign*6-1,0,-8),(2,3,9),0)
            box('forearm_'+side,(sign*6,1,-7),(sign*6-1.5,0,-13),(3,2,6),0,'arm_'+side)
    elif f=='mimic':
        box('body',(0,0,0),(-7,0,-5),(14,8,10),0,'root')
        box('lid',(0,8,5),(-7,8,-5),(14,3,10),0)
        for x in [-5,-2,1,4]: cube('lid',(x,7,-5),(1,2,1),2)
        cube('body',(-6,7,-4),(12,0.5,8),5)
        box('tongue',(0,7,-2),(-1,6,-10),(2,1,8),6)
        for x in [-6,5]: cube('body',(x,0,-5.1),(1,8,0.5),2); cube('lid',(x,8,-5.1),(1,3,0.5),2)
        if 'legs' in t:
            for side,sign in [('l',-1),('r',1)]: box('leg_'+side,(sign*5,0,0),(sign*5-1,-5,-1),(2,5,3),0)
    elif f=='weapon':
        box('body',(0,0,0),(-0.7,0,-0.7),(1.4,5,1.4),3,'root')
        cube('body',(-3,5,-1),(6,1.3,2),2); box('blade',(0,6,0),(-1,6,-0.5),(2,17,1),1)
        cube('blade',(-0.5,23,-0.5),(1,2,1),4)
        if t & {'bow','staff','shield','tome','gauntlets','daggers'}:
            r.parts=[]
            if 'bow' in t:
                for j in range(5): cube('body',(-.6,2+j*4,abs(j-2)*1.5),(1.2,4,1.2),0)
                cube('body',(-.15,2,4),(.3,20,.3),6)
            elif 'staff' in t:
                cube('body',(-.7,0,-.7),(1.4,22,1.4),0); cube('blade',(-2,22,-2),(4,4,4),4)
            elif 'shield' in t:
                cube('body',(-5,1,-1),(10,14,2),2); cube('body',(-3,0,-1),(6,1,2),2)
                cube('body',(-1,6,-2),(2,4,1),4)
            elif 'tome' in t:
                cube('body',(-4,0,-1),(8,11,2),0); cube('body',(-3.5,.5,-1.2),(7,10,.4),6)
                cube('body',(-.5,3,-1.7),(1,5,.5),2)
            elif 'gauntlets' in t:
                for x in [-5,2]:
                    cube('body',(x,0,-2),(3,5,4),2)
                    for j in range(3): cube('blade',(x+j,5,-2),(0.8,2,2),1)
            else:
                for x in [-3,2]:
                    cube('body',(x,0,-.5),(1,4,1),3); cube('blade',(x,4,-.3),(1,7,.6),2)
    elif f=='head':
        box('body',(0,0,0),(-4,0,-4),(8,8,8),0,'root'); r.bone('head',(0,0,0),'body'); eyes(y=4)
    elif f in {'foot','legs','arm','torso','chamber'}:
        dims={'foot':(12,7,18),'legs':(10,32,10),'arm':(8,32,8),'torso':(28,30,16),'chamber':(24,24,24)}[f]
        w,h,d=dims; box('body',(0,0,0),(-w/2,0,-d/2),dims,0,'root')
        if f=='legs': cube('body',(w,0,-d/2),dims,0)
        if f=='chamber':
            r.parts=[]
            cube('body',(-12,0,-12),(24,2,24),0)
            for x in [-10,8]:
                for z in [-10,8]: cube('body',(x,0,z),(2,24,2),0)
            cube('body',(-12,22,-12),(24,2,24),0)
    elif f=='chain':
        box('body',(0,0,0),(-1,0,-0.5),(2,0.6,1),2,'root')
        for i in range(10):
            n=f'link_{i}'; r.bone(n,(0,i*2,0),'body' if i==0 else f'link_{i-1}')
            for x in [-1,0.5]: cube(n,(x,i*2,0),(0.5,2,0.5),2)
            for y in [i*2,i*2+1.5]: cube(n,(-1,y,0),(2,0.5,0.5),2)
    else:
        shapes={'cheese':(6,3,5),'grave':(10,16,3),'seed':(3,4,3),'scale':(5,1,7),'book':(7,2,10),'key':(2,8,1),'door':(16,32,2),'totem':(5,10,4),'doll':(4,9,2),'branch':(2,16,2)}
        w,h,d=shapes[f]; box('body',(0,0,0),(-w/2,0,-d/2),(w,h,d),0,'root')
        if f=='grave': cube('body',(-7,0,-4),(14,2,8),1)
        if f=='cheese':
            for x,y in [(-2,1),(1,2)]: cube('body',(x,y,-2.55),(1,0.7,0.2),3)
        if f=='door':
            cube('body',(-9,0,-2),(2,34,4),2); cube('body',(7,0,-2),(2,34,4),2); cube('body',(-9,32,-2),(18,2,4),2)
        if f=='doll':
            cube('body',(-3,9,-2),(6,5,4),1); cube('body',(-5,6,-1),(10,2,2),0)
        if f=='key': cube('body',(-3,6,-.5),(6,3,1),2); cube('body',(0,1,-.5),(3,1,1),2)
        if f=='branch': cube('body',(0,8,-1),(5,1.5,2),0)
    # Shared attachments are parented to anatomical sockets, not world space.
    head=next((b for b in r.bones if b['name']=='head'),None)
    hp=head['pivot'] if head else [0,20,0]; hx,hy,hz=hp
    body=next(b for b in r.bones if b['name']=='body'); bx,by,bz=body['pivot']
    if ('horns' in t or 'horn' in t or 'antlers' in t) and head:
        for side,sign in ([('c',0)] if 'horn' in t else [('l',-1),('r',1)]):
            n='horn_'+side; xx=hx+sign*3
            box(n,(xx,hy+5,hz),(xx-0.7,hy+5,hz),(1.4,5 if not ('broken_horn' in t and sign==1) else 2,1.4),2,'head',(20,0,-sign*18))
            if 'antlers' in t:
                for j in [1,2]: cube(n,(xx-2,hy+6+j,hz),(4,0.7,1),2)
    if 'armor' in t or 'scrap' in t:
        for p in list(r.parts):
            if p['bone']=='body':
                x,y,z=p['origin']; w,h,d=p['size']
                cube('body',(x-0.3,y+0.7,z-0.4),(w+0.6,max(1,h-1.4),0.8),2); break
    if 'helmet' in t and head:
        cube('head',(hx-4.4,hy+4,hz-4.4),(8.8,4.4,8.8),2)
        cube('head',(hx-4.4,hy+1,hz-4.4),(2,3,1),2); cube('head',(hx+2.4,hy+1,hz-4.4),(2,3,1),2)
    if 'hair' in t and head:
        cube('head',(hx-4.1,hy+6,hz-3.5),(8.2,2.2,7.6),6)
        cube('head',(hx-4.1,hy+2,hz+3),(8.2,5,1.2),6)
    if 'eyepatch' in t and head: cube('head',(hx-3.5,hy+3.5,hz-4.5),(3,2.5,0.5),3)
    if 'crown' in t and head:
        for i in range(5): cube('head',(hx-4+i*1.7,hy+7,hz-3),(1,2+i%2,1),2)
    if 'cloak' in t or 'robe' in t or 'coat' in t or 'hood' in t:
        box('cloak',(0,by+9,bz+3),(-4,by-5,bz+3),(8,14,0.7),3)
        if 'robe' in t: cube('body',(-4,by-6,-2.7),(8,7,5.4),1)
        if 'hood' in t and head:
            cube('head',(hx-4.4,hy+6,hz-4.3),(8.8,2.4,8.6),3)
            for xx in [-4.4,3.5]: cube('head',(hx+xx,hy,hz-4.3),(0.9,6,8.6),3)
    if 'sash' in t: box('sash',(2,by,1),(2,by-8,1),(1.8,8,0.4),6)
    if 'satchel' in t or 'quiver' in t:
        box('satchel',(4,by,2),(3,by-3,1),(3,5,3),3)
    if 'mane' in t and head: cube('neck' if r.has('neck') else 'head',(-5,hy-2,hz+2),(10,9,3),6)
    if 'leaves' in t:
        for i,(xx,yy,zz) in enumerate([(-7,by+17,0),(2,by+19,1),(-2,by+23,-1)]):
            box('canopy_'+str(i),(xx,yy,zz),(xx-4,yy,zz-4),(9,4,8),3)
    if 'coral' in t or 'crystal' in t or 'spikes' in t or 'thorns' in t:
        for i in range(5): cube('body',((i-2)*2,by+5+i%2,-1+i),(1.5,4+i%3,1.5),4 if 'crystal' in t else 6)
    if 'core' in t and f!='slime':
        box('core',(0,by+5,-4),(-2,by+3,-4.7),(4,4,1.5),4)
    if 'harpoons' in t:
        for i in range(3): box('harpoon_'+str(i),((i-1)*3,by+5,i*3),((i-1)*3-0.3,by+4,i*3),(0.6,7,0.6),2,rotation=(10,0,(i-1)*25))
    if 'architecture' in t:
        for i in range(6): cube('body',(-8,by-5+i*2,-5),(5,0.8,3),1)
    if 'shards' in t or 'shards6' in t or 'fragments' in t:
        for i in range(6):
            a=math.tau*i/6; xx=math.cos(a)*8; yy=by+8+math.sin(a)*8
            box('shard_'+str(i),(xx,yy,6),(xx-0.6,yy-2,5.5),(1.2,4,1),4,'body',(0,0,i*60))
    if 'rings' in t or 'broken_halo' in t or f=='angel':
        r.bone('halo',(0,by+12,5),'body')
        for i in range(12):
            if 'broken_halo' in t and i%4==0: continue
            a=math.tau*i/12; xx=math.cos(a)*9; yy=by+12+math.sin(a)*9
            box('halo_'+str(i),(xx,yy,5),(xx-1.7,yy-0.4,5),(3.4,0.8,0.6),2,'halo',(0,0,i*30+90))
    if f in human and ('wings' in t or 'wings6' in t): wings(y=by+8,pairs=3 if 'wings6' in t else 1,feather=f in {'angel','fairy'})
    # Visible tears: omit selected membrane strips, retaining wing spars.
    if 'torn' in t:
        r.parts=[p for i,p in enumerate(r.parts) if not (p['bone'].startswith('wing') and p['material']==1 and i%3==0)]
    if 'detached' in t and f=='dragon':
        for p in r.parts:
            if p['bone'].startswith('tail'): p['size'][2]*=0.68
    if f=='fox':
        n=9 if 'tails9' in t else 5 if 'tails5' in t else 3 if 'tails3' in t else 1
        for i in range(1,n):
            xx=(i-(n/2))*2
            box('fox_tail_'+str(i),(0,7,5),(xx-0.8,5,6),(1.6,3,10),6,rotation=(0,xx*6,15))
    weapons=t & {'sword','dual_swords','dagger','dual_daggers','axe','dual_axes','club','dual_clubs','kanabo','pillar','spear','staff','bow','pickaxe','vine_blade','chain'}
    if weapons and f!='weapon' and r.has('arm_r'):
        weapon=sorted(weapons)[0]; dual=weapon.startswith('dual_')
        for side in (['r','l'] if dual else ['r']):
            parent='forearm_'+side if r.has('forearm_'+side) else 'arm_'+side
            pp=next(b['pivot'] for b in r.bones if b['name']==parent); xx,yy,zz=pp; yy-=3
            zz-=2
            n='weapon_'+side; r.bone(n,(xx,yy,zz),parent,(-75,0,0) if weapon not in {'bow','staff','spear','pillar'} else (0,0,12))
            cube(n,(xx-0.5,yy-1,zz-0.5),(1,5,1),3)
            if weapon in {'bow'}:
                for j in range(3): cube(n,(xx-0.5,yy-6+j*4,zz-2+abs(j-1)*2),(1,4,1),0)
                cube(n,(xx-0.1,yy-6,zz+1.5),(0.2,12,0.2),6)
            elif weapon in {'staff','spear','pillar'}:
                cube(n,(xx-0.5,yy-6,zz-0.5),(1,18,1),2)
                cube(n,(xx-1.2,yy+12,zz-1.2),(2.4,3,2.4),4 if weapon=='staff' else 2)
            elif weapon in {'club','dual_clubs','kanabo'}:
                cube(n,(xx-1.5,yy+3,zz-1.5),(3,9,3),0)
            elif weapon in {'axe','dual_axes','pickaxe'}:
                cube(n,(xx-0.5,yy+3,zz-0.5),(1,7,1),3)
                cube(n,(xx-3,yy+7,zz-0.7),(6,3,1.4),2)
            else:
                cube(n,(xx-2,yy+3,zz-0.7),(4,1,1.4),2)
                cube(n,(xx-0.8,yy+4,zz-0.4),(1.6,5 if 'dagger' in weapon else 10,0.8),2)
    if 'shield' in t and r.has('forearm_l'):
        xx,yy,zz=next(b['pivot'] for b in r.bones if b['name']=='forearm_l')
        box('shield',(xx,yy,zz),(xx-2.5,yy-4,zz-3),(5,7,1),2,'forearm_l')
    # Normalize the chosen size axis; articulated extremities count in the rest pose.
    points=[(p['origin'],[a+b for a,b in zip(p['origin'],p['size'])]) for p in r.parts]
    mins=[min(a[i] for a,b in points) for i in range(3)]
    maxs=[max(b[i] for a,b in points) for i in range(3)]
    axis=2 if f in {'dragon','wyvern','drake','serpent','worm','fish','whale'} else 0 if f in {'bird','bat','harpy'} else 1
    scale=e['size']*16/(maxs[axis]-mins[axis])
    for b in r.bones: b['pivot']=[round(v*scale,4) for v in b['pivot']]
    for p in r.parts:
        p['origin']=[round(v*scale,4) for v in p['origin']]
        p['size']=[round(v*scale,4) for v in p['size']]
    # Scale the entity above ground even when the recipe has negative tentacle/leg coordinates.
    floor=min(p['origin'][1] for p in r.parts)
    for p in r.parts: p['origin'][1]-=floor
    for b in r.bones:
        if b['name']!='root': b['pivot'][1]-=floor
    e['size_axis']=['width','height','length'][axis]; e['recipe_scale']=scale
    return r

def texture_for(e):
    seed=int(hashlib.sha256(e['id'].encode()).hexdigest()[:8],16); rng=random.Random(seed)
    a,b=map(rgb,PALETTES[e['palette']]); t=set(e['features'])
    cols=[a,b,(157,151,133),(65,61,54),b,(25,26,34),(203,186,156),a]
    if 'leaves' in t or e['palette']=='wood': cols[3]=(75,106,55)
    im=Image.new('RGBA',(128,64)); px=im.load()
    for slot,col in enumerate(cols):
        ox=(slot%4)*32; oy=(slot//4)*32
        for y in range(32):
            for x in range(32):
                noise=rng.choice([-7,-4,0,0,3,6]); edge=8 if y%8==0 else -9 if y%8==7 else 0
                if slot==2: noise+=int((31-y)*0.45)
                if slot==3: edge=5 if x%8==0 else -4
                if slot==4: noise=8 if (x+y)%7<2 else -5
                alpha=135 if slot==7 and 'translucent' in t else 255
                px[ox+x,oy+y]=tuple(max(0,min(255,c+noise+edge)) for c in col)+(alpha,)
        d=ImageDraw.Draw(im)
        if slot==0:
            for j in range(6):
                x=ox+rng.randrange(3,27); y=oy+rng.randrange(3,27)
                d.line([(x,y),(x+2,y+2),(x+2,y+4)],fill=tuple(max(0,c-22) for c in col)+(255,),width=1)
        if slot==1 or ('runes' in t and slot==0) or ('lava' in t and slot==0):
            d.line([(ox+6,oy+23),(ox+6,oy+10),(ox+13,oy+10),(ox+13,oy+18),(ox+22,oy+18),(ox+22,oy+6)],fill=(*b,255),width=1)
        if 'scar' in t and slot==0: d.line([(ox+3,oy+4),(ox+13,oy+18)],fill=(201,160,131,255),width=2)
    return im,cols

def uv_for(p):
    slot=p['material']; x=(slot%4)*32+1; y=(slot//4)*32+1
    # Per-face UVs stay in one semantic tile. 30px usable with a 1px guard.
    w,h,d=p['size']; unit=max(1,max(w,h,d)/24)
    dims={'north':(w,h),'south':(w,h),'east':(d,h),'west':(d,h),'up':(w,d),'down':(w,d)}
    return {face:{'uv':[x,y],'uv_size':[max(1,round(a/unit,2)),max(1,round(b/unit,2))]} for face,(a,b) in dims.items()}

def geometry(e,r):
    bones=[]
    for b in r.bones:
        b=dict(b); parts=[p for p in r.parts if p['bone']==b['name']]
        if parts: b['cubes']=[dict(origin=p['origin'],size=p['size'],uv=uv_for(p)) for p in parts]
        bones.append(b)
    span=max(e['size']*3,6)
    return {'format_version':'1.12.0','minecraft:geometry':[{'description':{
        'identifier':'geometry.unwritten.'+e['id'],'texture_width':128,'texture_height':64,
        'visible_bounds_width':span,'visible_bounds_height':span,'visible_bounds_offset':[0,e['size']/2,0]},'bones':bones}]}

def animation_set(e,r):
    result={}; scale=e['recipe_scale']; f=e['family']
    def put(name,tracks,length=1,loop=False):
        result['animation.unwritten.'+e['id']+'.'+name]={'loop':loop,'animation_length':length,'bones':{b:v for b,v in tracks.items() if r.has(b)}}
    def keys(values,length=1): return {str(round(i*length/(len(values)-1),4)):v for i,v in enumerate(values)}
    def rot(vals,length=1): return {'rotation':keys(vals,length)}
    def pos(vals,length=1): return {'position':keys([[x*scale,y*scale,z*scale] for x,y,z in vals],length)}
    zero=[0,0,0]
    put('idle',{'body':pos([zero,[0,0.25,0],zero],2),'head':rot([zero,[2,0,0],zero],2)},2,True)
    legs=[b['name'] for b in r.bones if b['name'].startswith('leg') and not b['name'].endswith(('_tip','_paw'))]
    for name,duration,amp in [('walk',1,23),('run',0.55,40)]:
        tracks={}
        for i,b in enumerate(legs):
            # Front-left/back-right pair is opposite front-right/back-left.
            sign=(-1 if b.endswith('_l') else 1)*(-1 if 'back' in b else 1) if 'front' in b or 'back' in b else (-1 if i%2 else 1)
            tracks[b]=rot([[amp*sign,0,0],[-amp*sign,0,0],[amp*sign,0,0]],duration)
        for side,sign in [('l',1),('r',-1)]: tracks['arm_'+side]=rot([[amp*sign,0,0],[-amp*sign,0,0],[amp*sign,0,0]],duration)
        tracks['body']=pos([zero,[0,0.6 if name=='run' else 0.2,0],zero],duration)
        put(name,tracks,duration,True)
    put('hurt',{'body':rot([zero,[-12,0,5],zero],0.35)},0.35)
    put('death',{'root':rot([zero,[0,0,15],[0,0,85]],1.2),'body':pos([zero,[0,-1,0],[0,-3,0]],1.2)},1.2)
    put('bite',{'head':rot([zero,[-15,0,0],[20,0,0],zero],0.7),'jaw':rot([zero,[35,0,0],zero,zero],0.7)},0.7)
    put('attack',{'body':rot([zero,[0,-18,0],[15,20,0],zero],0.8),'arm_r':rot([zero,[-90,0,-20],[45,0,10],zero],0.8),'head':rot([zero,[-15,0,0],[18,0,0],zero],0.8)},0.8)
    put('stun',{'head':rot([zero,[0,0,12],[0,0,-12],zero],1.2)},1.2,True)
    wingnames=[b['name'] for b in r.bones if b['name'].startswith('wing_') and not b['name'].endswith('_tip')]
    if wingnames:
        tracks={'body':pos([zero,[0,0.6,0],zero],0.8)}
        for b in wingnames:
            sign=-1 if '_l' in b else 1
            tracks[b]=rot([[0,0,-sign*20],[0,0,sign*35],[0,0,-sign*20]],0.8)
        put('fly',tracks,0.8,True)
        put('wing_unfold',{b:rot([[0,0,-65 if '_l' in b else 65],zero],1.5) for b in wingnames},1.5)
        put('takeoff',{'root':pos([zero,[0,-1,0],[0,12,0]],1.3),**{b:rot([zero,[0,0,40 if '_l' in b else -40],zero],1.3) for b in wingnames}},1.3)
        put('land',{'root':pos([[0,12,0],[0,0,0],[0,-1,0],zero],1)},1)
    tails=[b['name'] for b in r.bones if b['name'].startswith(('tail','tentacle'))]
    if tails:
        tracks={b:rot([[0,math.sin(i*.8)*10,0],[0,-math.sin(i*.8)*10,0],[0,math.sin(i*.8)*10,0]],2) for i,b in enumerate(tails)}
        put('swim',tracks,2,True)
        put('tail_sweep',{b:rot([zero,[0,-35,0],[0,50,0],zero],1.3) for b in tails if b.startswith('tail')},1.3)
    if f=='slime':
        put('idle',{'body':{'scale':keys([[1,1,1],[1.06,.92,1.06],[1,1,1]],1.4)}},1.4,True)
        for n in ['hop','walk','run','slam']:
            put(n,{'body':{'scale':keys([[1,1,1],[1.2,.7,1.2],[.85,1.2,.85],[1.3,.6,1.3],[1,1,1]]),'position':keys([[0,0,0],[0,0,0],[0,8*scale,0],[0,0,0],[0,0,0]])}},1,n in ['walk','run'])
        put('death_melt',{'body':{'scale':keys([[1,1,1],[1.3,.3,1.3],[1.7,.03,1.7]],1.4)}},1.4)
        result['animation.unwritten.'+e['id']+'.death']=result['animation.unwritten.'+e['id']+'.death_melt']
    if f=='mimic':
        for n in ['open','attack']:
            put(n,{'lid':rot([zero,[-75,0,0],[-40,0,0],zero]),'tongue':pos([zero,[0,0,-3],[0,0,-5],zero])})
        put('disguise',{'lid':rot([zero,zero])},1,True)
    if f=='rabbit': put('hop',{'body':pos([zero,[0,4,0],zero],.6),'ear_l':rot([zero,[-18,0,0],zero],.6),'ear_r':rot([zero,[-18,0,0],zero],.6)},.6)
    # Reusable attack vocabulary with distinct anticipation, contact and recovery poses.
    vocab={
      'slash':('arm_r',[[0,0,0],[-70,-25,-35],[30,35,20],[0,0,0]],.75),
      'thrust':('arm_r',[[0,0,0],[-30,0,15],[-95,0,0],[0,0,0]],.65),
      'parry':('arm_r',[[0,0,0],[-65,0,50],[-65,0,50],[0,0,0]],.6),
      'cast':('arm_r',[[0,0,0],[-120,0,-20],[-100,0,0],[0,0,0]],1.4),
      'roar':('head',[[0,0,0],[-35,0,0],[-25,8,0],[0,0,0]],1.7),
      'bow_attack':('arm_r',[[0,0,0],[-90,30,0],[-90,10,0],[0,0,0]],1.2),
      'smash':('body',[[0,0,0],[-25,0,0],[40,0,0],[0,0,0]],1.4),
      'dodge':('root',[[0,0,0],[0,0,-20],[0,0,0],[0,0,0]],.45),
    }
    features=set(e['features'])
    if r.has('arm_r'):
        for n in ['slash','thrust','parry','cast','smash','dodge']:
            b,v,l=vocab[n]; put(n,{b:rot(v,l)},l)
    if 'bow' in features:
        b,v,l=vocab['bow_attack']; put('bow_attack',{b:rot(v,l),'arm_l':rot([zero,[-90,0,0],[-90,0,0],zero],l)},l)
    b,v,l=vocab['roar']; put('roar',{b:rot(v,l),'jaw':rot([zero,[28,0,0],[20,0,0],zero],l)},l)
    if e['category'].startswith('pet') or e['id']=='little_morrow':
        for n in ['sit','sleep','yawn','scratch_ear','curious_head_tilt','angry_puff','chase_tail','climb','eat_cheese','steal_cheese','happy_bounce','shoulder_sit']:
            if n in {'sleep','sit','shoulder_sit'}:
                put(n,{'body':pos([[0,-2,0],[0,-1.8,0],[0,-2,0]],2),'head':rot([[15,0,0],[17,0,0],[15,0,0]],2)},2,True)
            elif n=='chase_tail': put(n,{'root':rot([zero,[0,180,0],[0,360,0]],2)},2)
            elif n in {'eat_cheese','yawn','angry_puff'}: put(n,{'jaw':rot([zero,[35 if n=='yawn' else 15,0,0],zero],1.1),'head':rot([zero,[12,0,0],zero],1.1)},1.1)
            elif n=='curious_head_tilt': put(n,{'head':rot([zero,[0,15,20],[0,-10,-10],zero],2)},2)
            else: put(n,{'body':pos([zero,[0,2,0],zero]),'head':rot([zero,[0,15,0],zero])})
    if f=='spider':
        put('web_spit',{'head':rot([zero,[-15,0,0],[20,0,0],zero]),'body':rot([zero,[-10,0,0],zero,zero])})
    if f in {'dragon','wyvern','drake'}:
        put('breath',{'head':rot([zero,[-15,0,0],[0,-15,0],[0,15,0],zero],3),'jaw':rot([zero,[28,0,0],[28,0,0],[28,0,0],zero],3)},3)
        put('sleeping',{'body':pos([[0,-3,0],[0,-2.7,0],[0,-3,0]],3),'head':rot([[20,0,0],[21,0,0],[20,0,0]],3)},3,True)
    if e['category']=='colossi':
        # Cinematic pose clips only: camera, phase, VFX and damage remain server work.
        put('awaken',{'body':pos([[0,-4,0],[0,-3,0],zero],3),'head':rot([[30,0,0],[20,-10,0],zero],3)},3)
        put('kneel',{'body':pos([zero,[0,-4,0],[0,-4,0]],2),'leg_l':rot([zero,[-65,0,0],[-65,0,0]],2),'head':rot([zero,[20,0,0],[20,0,0]],2)},2)
        put('reach',{'arm_r':rot([zero,[-80,0,-15],[-80,0,-15]],2)},2)
        put('transform',{'body':pos([zero,[0,3,0],[0,5,0]],3),'head':rot([zero,[-25,0,0],zero],3),**{b:rot([zero,[0,0,50 if '_l' in b else -50],zero],3) for b in wingnames}},3)
        if r.has('arm_r'):
            for i in range(1,6):
                put('slash_'+str(i),{'arm_r':rot([zero,[-50-i*7,-i*8,-30],[30,i*12,30-i*5],zero],.6+i*.06),'body':rot([zero,[0,-i*5,0],[0,i*8,0],zero],.6+i*.06)},.6+i*.06)
            for i in range(1,4): put('thrust_'+str(i),{'arm_r':rot([zero,[-30,i*10,0],[-90,-i*7,0],zero],.65)},.65)
        if e['id'].startswith('aion'):
            for i,n in enumerate(['delete','copy','paste','rewind','gravity_change','dimensional_slash','arena_rewrite','authority_beam']):
                put(n,{'arm_r':rot([zero,[-60-i*8,i*5,0],zero],1.4),'halo':rot([zero,[0,0,60+i*15],[0,0,120+i*15]],1.4)},1.4)
    # A clip that only targeted missing bones must not be advertised.
    return {k:v for k,v in result.items() if v['bones']}

def bbmodel(e,r,im_path,animations):
    elements=[]; groups={}; tex_id=uid(e['id']+'/texture')
    for b in r.bones:
        p=b['pivot']; rot=b.get('rotation',[0,0,0])
        groups[b['name']]={'name':b['name'],'origin':[-p[0],p[1],p[2]],'rotation':[-rot[0],-rot[1],rot[2]],'uuid':uid(e['id']+'/bone/'+b['name']),'export':True,'isOpen':False,'children':[]}
    for i,p in enumerate(r.parts):
        x,y,z=p['origin']; w,h,d=p['size']; uv=uv_for(p); faces={}
        for face,data in uv.items():
            a,b=data['uv']; c,dd=data['uv_size']
            faces[{'east':'west','west':'east'}.get(face,face)]={'uv':[a,b,a+c,b+dd],'texture':0}
        el={'name':p['bone']+'_'+str(i),'from':[-x-w,y,z],'to':[-x,y+h,z+d],'autouv':0,'color':p['material'],'uuid':uid(e['id']+'/cube/'+str(i)),'faces':faces,'type':'cube','box_uv':False,'rescale':False,'rotation':[0,0,0],'origin':[0,0,0]}
        elements.append(el); groups[p['bone']]['children'].append(el['uuid'])
    for b in r.bones:
        if 'parent' in b: groups[b['parent']]['children'].append(groups[b['name']])
    bb_anims=[]
    for name,a in animations.items():
        animators={}
        for bone,channels in a['bones'].items():
            kfs=[]
            for channel,keys in channels.items():
                for time,vals in keys.items():
                    vals=list(vals)
                    if channel=='rotation': vals=[-vals[0],-vals[1],vals[2]]
                    if channel=='position': vals[0]=-vals[0]
                    kfs.append({'channel':channel,'data_points':[dict(zip(['x','y','z'],map(str,vals)))],'uuid':uid(name+'/'+bone+'/'+channel+'/'+time),'time':float(time),'color':-1,'interpolation':'linear'})
            animators[groups[bone]['uuid']]={'name':bone,'type':'bone','keyframes':kfs}
        bb_anims.append({'uuid':uid(name),'name':name,'loop':'loop' if a['loop'] else 'once','override':False,'length':a['animation_length'],'snapping':20,'animators':animators})
    return {'meta':{'format_version':'4.10','model_format':'bedrock','box_uv':False},'name':e['name'],'model_identifier':'unwritten.'+e['id'],
      'visible_box':[max(e['size']*3,6),max(e['size']*3,6),e['size']/2],
      'resolution':{'width':128,'height':64},'elements':elements,'outliner':[groups['root']],
      'textures':[{'path':'','name':e['id']+'.png','uuid':tex_id,'id':'0','mode':'bitmap','saved':False,'width':128,'height':64,'uv_width':128,'uv_height':64,'source':'data:image/png;base64,'+base64.b64encode(im_path.read_bytes()).decode()}],
      'animations':bb_anims}

def manifest(name,kind):
    return {'format_version':2,'header':{'name':name,'description':'UNWRITTEN asset production v0.1.0; visual first pass, no combat AI.','uuid':uid(kind+'/header'),'version':[0,1,0],'min_engine_version':[1,21,0]},'modules':[{'type':'resources' if kind=='rp' else 'data','uuid':uid(kind+'/module'),'version':[0,1,0]}]}

def build():
    entries=read_roster(); reports=[]; names=[]
    dump(RP/'manifest.json',manifest('UNWRITTEN Creature Assets','rp'))
    bp=manifest('UNWRITTEN Preview Only','bp'); bp['dependencies']=[{'uuid':uid('rp/header'),'version':[0,1,0]}]; dump(BP/'manifest.json',bp)
    dump(RP/'render_controllers/unwritten.render_controllers.json',{'format_version':'1.8.0','render_controllers':{'controller.render.unwritten':{'geometry':'Geometry.default','materials':[{'*':'Material.default'}],'textures':['Texture.default']}}})
    for e in entries:
        r=rig_for(e); im,colors=texture_for(e); id=e['id']; tex=RP/f'textures/entity/unwritten/{id}.png'; tex.parent.mkdir(parents=True,exist_ok=True); im.save(tex)
        geo=geometry(e,r); anim=animation_set(e,r)
        dump(RP/f'models/entity/unwritten/{id}.geo.json',geo)
        dump(RP/f'animations/unwritten/{id}.animation.json',{'format_version':'1.8.0','animations':anim})
        dump(ROOT/f'blockbench/{e["category"]}/{id}.bbmodel',bbmodel(e,r,tex,anim))
        aliases={n.rsplit('.',1)[-1]:n for n in anim}
        controller='controller.animation.unwritten.'+id
        aliases['locomotion']=controller
        dump(RP/f'animation_controllers/unwritten/{id}.controller.json',{'format_version':'1.10.0','animation_controllers':{controller:{'initial_state':'idle','states':{
            'idle':{'animations':['idle'],'transitions':[{'moving':'query.modified_move_speed > 0.01'}],'blend_transition':0.15},
            'moving':{'animations':['walk'],'transitions':[{'idle':'query.modified_move_speed <= 0.01'}],'blend_transition':0.15}}}}})
        dump(RP/f'entity/{id}.entity.json',{'format_version':'1.10.0','minecraft:client_entity':{'description':{
            'identifier':'unwritten:'+id,'materials':{'default':'entity_alphablend' if 'translucent' in e['features'] else 'entity_alphatest'},
            'textures':{'default':'textures/entity/unwritten/'+id},'geometry':{'default':'geometry.unwritten.'+id},
            'animations':aliases,'scripts':{'animate':['locomotion']},'render_controllers':['controller.render.unwritten'],
            'spawn_egg':{'base_color':PALETTES[e['palette']][0],'overlay_color':PALETTES[e['palette']][1]}}}})
        dump(BP/f'entities/{id}.json',{'format_version':'1.21.0','minecraft:entity':{'description':{'identifier':'unwritten:'+id,'is_spawnable':True,'is_summonable':True,'is_experimental':False},'components':{
            'minecraft:type_family':{'family':['unwritten_preview']},'minecraft:health':{'value':20,'max':20},
            'minecraft:collision_box':{'width':min(1.2,e['size']*.6),'height':min(2.0,e['size'])},
            'minecraft:physics':{'has_gravity':False,'has_collision':False},'minecraft:pushable':{'is_pushable':False,'is_pushable_by_piston':False},
            'minecraft:nameable':{}}}})
        names.append('entity.unwritten:'+id+'.name='+e['name'])
        e.update(status='first_pass',rig_bones=len(r.bones),cubes=len(r.parts),animations=list(n.rsplit('.',1)[-1] for n in anim),
          source=f'blockbench/{e["category"]}/{id}.bbmodel',texture=str(tex.relative_to(ROOT)),
          geometry=f'packs/UNWRITTEN_RP/models/entity/unwritten/{id}.geo.json',
          role=('companion' if e['category'].startswith('pet') else 'cinematic / raid visual' if e['category']=='colossi' else 'neutral quest candidate' if 'unique' in e['category'] else 'creature visual'),
          element={'fire':'fire','ice':'ice','poison':'poison','abyss':'dark / water','spectral':'spirit','wood':'earth','gold':'unspecified'}.get(e['palette'],'unspecified'),
          limitations=['Family-derived first-pass silhouette; needs individual art review.','No combat logic, loot, VFX, camera, navigation or phase transitions.'])
        reports.append(e)
    (RP/'texts').mkdir(exist_ok=True); (RP/'texts/en_US.lang').write_text('\n'.join(names)+'\n'); dump(RP/'texts/languages.json',['en_US'])
    # Override files are deliberately copied last. Never overwrite handcrafted source.
    overrides=ROOT/'source_overrides'
    if overrides.exists():
        for p in overrides.rglob('*'):
            if p.is_file() and p.name!='README.md':
                target=ROOT/p.relative_to(overrides); target.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(p,target)
    dump(ROOT/'catalog/assets.json',{'version':'0.1.0','entries':reports,'aliases':{'The Golden Slime':'golden_slime','world_boss/Demon General':'demon_general'},'colossus_viii':['thalassia','verdant_giant','verdant_the_last_father']})
    (ROOT/'dist').mkdir(exist_ok=True)
    for path,name in [(RP,'UNWRITTEN_Assets.mcpack'),(BP,'UNWRITTEN_Preview.mcpack')]:
        with zipfile.ZipFile(ROOT/'dist'/name,'w',zipfile.ZIP_DEFLATED) as z:
            for p in sorted(path.rglob('*')):
                if p.is_file():
                    info=zipfile.ZipInfo(str(p.relative_to(path)),date_time=(2026,1,1,0,0,0)); info.compress_type=zipfile.ZIP_DEFLATED; z.writestr(info,p.read_bytes())
    print(f'Built {len(entries)} assets, {len(set(e["family"] for e in entries))} rig recipes, {sum(len(e["animations"]) for e in reports)} clips.')
    return reports

if __name__=='__main__': build()
