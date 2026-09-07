#!/usr/bin/env python3
"""Bespoke Decem Fata production pass. Original articulated cuboid sculpture.
Runs after build_assets.py. No generic monster recipe is used for these forms.
"""
import hashlib, json, math, random, zipfile
from PIL import Image, ImageDraw
from build_assets import ROOT, RP, BP, Rig, dump, geometry, bbmodel

# Semantic materials; face islands get direction-sensitive painting and edge wear.
M={
 'obsidian':('#303338','scale'),'lava':('#f39b42','glow'),
 'bone':('#c4b28c','bone'),'membrane':('#5a302c','leather'),
 'steel':('#606f7b','metal'),'darksteel':('#303a48','metal'),
 'gold':('#b49657','metal'),'silver':('#a7b3bc','metal'),
 'skin':('#c9a58e','skin'),'hair':('#d3c6a1','hair'),
 'blackhair':('#302a30','hair'),'white':('#d9ddd7','cloth'),
 'navy':('#25334b','cloth'),'black':('#202731','cloth'),
 'red':('#713641','cloth'),'leather':('#645140','leather'),
 'eye':('#ddecd5','glow'),'pupil':('#181b25','flat'),
 'ivory':('#d6cdae','scale'),'violet':('#907db4','glow'),
 'sandstone':('#9b896c','stone'),'ancientmetal':('#536263','metal'),
 'aqua':('#66cfc5','glow'),'ocean':('#244651','scale'),
 'belly':('#829a91','skin'),'coral':('#b5797c','stone'),
 'bark':('#584e3d','bark'),'wood':('#c5c7a8','bark'),
 'leaf':('#536b3e','leaf'),'green':('#a6cf7b','glow'),
 'ghost':('#95c0bc','cloth'),'feather':('#cccbbd','feather'),
 'darkfeather':('#414552','feather'),'void':('#504267','stone'),
}
def rgb(s): return tuple(bytes.fromhex(s.lstrip('#')))

class Sculpt(Rig):
    def __init__(self):
        super().__init__(); self.bone('root',parent=None); self.bone('body',(0,0,0),'root')
    def add(self,n,o,s,mat='obsidian',rotation=None,pivot=None):
        self.parts.append(dict(bone=n,origin=list(o),size=list(s),material=mat))
        p=self.parts[-1]
        if rotation: p.update(rotation=list(rotation),pivot=list(pivot or o))
    def joint(self,n,p,parent='body',rot=None): self.bone(n,p,parent,rot); return n
    def bar(self,n,a,b,width,depth,mat):
        # A tapered horn/root/rib is built from joined oriented box sections.
        dx,dy,dz=[b[i]-a[i] for i in range(3)]; length=math.sqrt(dx*dx+dy*dy+dz*dz)
        rz=-math.degrees(math.atan2(dx,dy))
        rx=math.degrees(math.asin(max(-1,min(1,dz/length))))
        self.add(n,(a[0]-width/2,a[1],a[2]-depth/2),(width,length,depth),mat,(rx,0,rz),a)
    def horn(self,n,points,width,mat='bone'):
        for i,(a,b) in enumerate(zip(points,points[1:])): self.bar(n,a,b,max(.12,width*(1-i/len(points))),max(.12,width*(1-i/len(points))),mat)
    def ring(self,n,center,radius,thickness,mat='gold',count=20,gaps=()):
        x,y,z=center
        for i in range(count):
            if i in gaps: continue
            a=math.tau*i/count; xx=x+math.cos(a)*radius; yy=y+math.sin(a)*radius
            self.add(n,(xx-radius*math.pi/count,yy-thickness/2,z-thickness/2),(radius*math.tau/count*.91,thickness,thickness),mat,(0,0,math.degrees(a)+90),(xx,yy,z))
    def scaled(self,factor):
        for b in self.bones: b['pivot']=[v*factor for v in b['pivot']]
        for p in self.parts:
            for k in ['origin','size','pivot']:
                if k in p: p[k]=[round(v*factor,5) for v in p[k]]
        return self


def dragon(kind):
    r=Sculpt(); little=kind=='little_morrow'; true=kind=='true_morrow'
    scale='ivory' if little or true else 'obsidian'; accent='violet' if little or true else 'lava'
    # Horizontal ribcage, powerful forward shoulders, pelvis and plated belly.
    for o,s in [((-13,22,-15),(26,23,41)),((-16,26,-12),(32,15,29)),((-10,20,19),(20,19,23)),((-11,42,-8),(22,5,26))]: r.add('body',o,s,scale)
    for i in range(7): r.add('body',(-10+i%2,21,-14+i*6),(20-i%2*2,2,5),'bone' if not true else 'silver')
    r.joint('chest',(0,35,-12)); r.add('chest',(-11,27,-23),(22,17,13),scale)
    # Neck progressively rises into a long low crocodilian cranium.
    neckpoints=[(0,35,-19),(0,39,-31),(0,43,-41),(0,45,-51)]
    for i,p in enumerate(neckpoints):
        n='neck_'+str(i); r.joint(n,p,'chest' if i==0 else 'neck_'+str(i-1))
        r.add(n,(-9+i, p[1]-7, p[2]-12),(18-i*2,14-i,14),scale)
        for side in [-1,1]: r.add(n,(side*(8-i)-1,p[1]-2,p[2]-5),(2,4,8),accent,(-15,side*12,0))
    r.joint('head',(0,45,-54),'neck_3')
    for o,s in [((-9,41,-68),(18,13,18)),((-7,40,-82),(14,8,19)),((-5,42,-91),(10,5,11)),((-10,43,-65),(20,7,8))]: r.add('head',o,s,scale)
    r.add('head',(-5,41,-90),(10,1,20),'pupil')
    r.joint('jaw',(0,42,-58),'head'); r.add('jaw',(-6,37,-87),(12,3,28),scale)
    r.add('jaw',(-5,40,-85),(10,.55,24),'red')
    for side in [-1,1]:
        for j in range(8):
            z=-84+j*3.3; r.horn('head',[(side*5,42,z),(side*5.1,39.1,z-.4)],.8,'bone')
            if j%2==0: r.horn('jaw',[(side*5,40,z),(side*5,42,z-.5)],.65,'bone')
        # Eyes sit on the front corners below separate heavy brows.
        r.add('head',(side*7-.8,47,-70),(1.6,2.5,4),accent)
        r.add('head',(side*7-1,48,-70.2),(1.9,.7,3),'pupil')
        r.add('head',(side*7-2,50,-70),(4,2,7),scale,(0,side*-9,side*9))
        r.add('head',(side*3-1,44.8,-90),(2,.8,2),'pupil')
        length=6 if side==1 and kind=='vharos' else 20
        r.horn('head',[(side*7,52,-57),(side*12,60,-49),(side*14,60+length*.3,-49+length)],3.3)
        r.horn('head',[(side*9,44,-57),(side*15,43,-48),(side*18,46,-44)],2.2)
        # Forelimb: shoulder / upper arm / elbow / wrist / toes.
        for pos,z in [('front',-8),('back',30)]:
            x=side*(13 if pos=='front' else 10)
            upper=f'leg_{pos}_{"l" if side<0 else "r"}'; elbow=upper+'_elbow'; paw=upper+'_paw'
            r.joint(upper,(x,33,z)); r.add(upper,(x-4,17,z-5),(8,18,10),scale,(12 if pos=='back' else -10,0,side*8),(x,33,z))
            r.joint(elbow,(x+side*3,18,z+3),upper); r.add(elbow,(x+side*3-2.8,5,z),(5.6,14,7),scale)
            r.joint(paw,(x+side*3,5,z),elbow); r.add(paw,(x+side*3-4,2,z-6),(8,4,12),scale)
            for j in [-1,0,1]:
                tx=x+side*3+j*2.5
                r.horn(paw,[(tx,3,z-4),(tx,2,z-11),(tx,1,z-13)],1.8)
            r.add(upper,(x-4.4,26,z-5.4),(8.8,6,2),'bone')
    # Tail chain narrows all the way to an articulated blade tip.
    parent='body'
    for i in range(12):
        z=36+i*9; y=29-i*1.6; w=max(1,17-i*1.3); n='tail_'+str(i)
        r.joint(n,(0,y,z),parent); gap=1.8 if true else 0
        r.add(n,(-w/2,y-w*.35,z+gap),(w,w*.7,10-gap),scale)
        if i%2==0: r.horn(n,[(0,y+w*.35,z+3),(0,y+w*.35+5-i*.2,z+7)],max(.5,2-i*.1),accent if true else 'bone')
        parent=n
    # Broad, torn membranes supported by long fingers, independently folding tips.
    for side,label in [(-1,'l'),(1,'r')]:
        upper='wing_'+label; tip=upper+'_tip'
        r.joint(upper,(side*12,41,0)); r.joint(tip,(side*57,47,-10),upper)
        r.horn(upper,[(side*12,41,0),(side*33,49,-10),(side*57,47,-10)],4,scale)
        r.horn(tip,[(side*57,47,-10),(side*87,44,-20),(side*112,42,-13)],2.8,scale)
        for j in range(5):
            xx=side*(37+j*18); zz=42-j*5
            bone=upper if j<2 else tip
            r.horn(bone,[(side*30,46,-7),(xx,43,zz),(xx+side*4,41,zz+5)],1.4,'bone' if not true else 'silver')
        for i in range(24):
            x=16+i*4; start=-8-max(0,x-48)*.12; depth=51-(x-16)*.37
            # Visible tears are holes, not just a differently colored membrane.
            if not little and i in {6,13,19,22}: depth*=.54
            bone=upper if x<57 else tip; xx=-x-4 if side<0 else x
            r.add(bone,(xx,43,start),(4.1,.45,depth),'violet' if true else 'membrane')
            if i%3==0: r.add(bone,(xx,43.5,start+4),(3.8,.2,1),accent)
    # Dorsal armor, cracks and silhouettes of ancient embedded weapons.
    for i in range(11):
        z=-26+i*6
        r.horn('chest' if i<2 else 'body',[(0,44,z),(0,51+(i%3)*2,z+4),(0,49,z+7)],2.5,accent if true else 'bone')
        if not little:
            for side in [-1,1]: r.add('body',(side*12-1,33,z+8),(2,2,5),accent,(0,0,side*15))
    if kind=='vharos':
        for i,(x,y,z) in enumerate([(-10,40,6),(8,42,18),(-8,39,26)]):
            r.joint('ancient_spear_'+str(i),(x,y,z))
            r.bar('ancient_spear_'+str(i),(x,y,z),(x+5-i*3,y+20,z+7),.65,.65,'leather')
            r.add('ancient_spear_'+str(i),(x-1,y+16,z+4),(2,6,.5),'steel',(15,0,20),(x,y,z))
    if true:
        r.joint('spatial_ring',(0,52,5)); r.ring('spatial_ring',(0,52,5),30,1.4,'violet',24,(2,6,10,14,18,22))
    if little:
        # Entirely re-proportioned companion, not a scaled adult.
        for p in r.parts:
            if p['bone'].startswith('wing'): p['size'][2]*=.75
        # Big ears and readable forward-facing eyes.
        for side in [-1,1]:
            r.horn('head',[(side*8,50,-57),(side*20,58,-57),(side*22,66,-54)],4,'ivory')
            r.add('head',(side*4-2,47,-83),(4,4,.7),'violet')
            r.add('head',(side*4-1,48,-83.8),(2,2,.4),'pupil')
            r.add('head',(side*4-1,49,-84.3),(.7,.7,.3),'white')
        # Compress long adult tail and snout along z; boost cranium vertically.
        for p in r.parts:
            p['origin'][2]*=.52; p['size'][2]*=.52
            if 'pivot' in p: p['pivot'][2]*=.52
        for b in r.bones: b['pivot'][2]*=.52
    return r


def blade(r,parent='hand_r',kind='knight'):
    p=next(b['pivot'] for b in r.bones if b['name']==parent); x,y,z=p
    n='sword'; r.joint(n,(x,y,z),parent,(-13,0,0)); mat='darksteel' if kind in {'dullahan','kael_demon_king'} else 'steel'
    r.add(n,(x-.45,y-2,z-.45),(.9,4,.9),'leather')
    for j in range(5): r.add(n,(x-.49,y-1.6+j*.55,z-.49),(.98,.18,.98),'gold')
    r.add(n,(x-2.8,y+2,z-.4),(5.6,.65,.8),'gold' if kind=='caelum' else mat)
    r.add(n,(x-.6,y+2.6,z-.3),(1.2,13,.6),mat)
    r.add(n,(x-.18,y+3,z-.39),(.36,12,.2),'silver')
    r.add(n,(x-.36,y+15.6,z-.3),(.72,2,.6),mat)
    for side in [-1,1]: r.add(n,(x+side*.61-.1,y+3,z-.18),(.2,12,.36),'silver')
    r.add(n,(x-.65,y-2.8,z-.65),(1.3,.8,1.3),'gold')
    if kind=='kael_demon_king':
        for i in range(5): r.add(n,(x-.8,y+4+i*2,z-.4),(1.6,.35,.8),'lava')


def person(kind):
    r=Sculpt(); armored=kind in {'dullahan','caelum','sir_seraphiel','fallen_seraphiel','the_nameless_knight','kael_demon_king'}
    sealed=kind in {'dullahan','the_nameless_knight'}; king=kind=='kael_demon_king'; father=kind=='verdant_the_last_father'
    aion=kind.startswith('aion'); architect=kind=='aion_the_architect'; fallen=kind=='fallen_seraphiel'; spirit=kind=='elara_spirit'
    skin='wood' if father else 'ghost' if spirit else 'skin'
    armor='darksteel' if kind in {'dullahan','the_nameless_knight'} or king or fallen else 'gold' if kind=='caelum' else 'silver'
    cloth='white' if aion or kind=='sir_seraphiel' or spirit else 'red' if king else 'navy' if kind=='caelum' else 'black'
    # Base anatomy: bevels are actual geometry, not a flat skin.
    r.bones[1]['pivot']=[0,15,0]
    r.add('body',(-3.3,15,-1.9),(6.6,8.5,3.8),skin if father else cloth)
    r.add('body',(-4,20,-1.6),(8,3.5,3.2),skin if father else cloth)
    r.add('body',(-2.8,13,-1.8),(5.6,3,3.6),skin if father else cloth)
    r.joint('neck',(0,24,0)); r.add('neck',(-1.15,23.5,-1.2),(2.3,2.5,2.4),skin)
    r.joint('head',(0,25,0),'neck')
    if kind!='dullahan':
        r.add('head',(-2.8,25,-2.5),(5.6,5.9,5),armor if sealed else skin)
        r.add('head',(-2.3,24.6,-2.1),(4.6,.7,4.2),armor if sealed else skin)
        r.add('head',(-2.4,30.9,-2.1),(4.8,.5,4.2),armor if sealed else skin)
        if sealed:
            r.add('head',(-2.6,28,-2.7),(5.2,.48,.35),'pupil')
            r.add('head',(-.3,25.6,-2.8),(.6,2.4,.4),'silver')
            for side in [-1,1]: r.add('head',(side*2.1-.45,25.6,-2.65),(.9,1.9,.45),'darksteel',(0,0,side*15))
        elif not (kind=='aion_prologue'):
            for side in [-1,1]:
                r.add('head',(side*1.25-.6,28.2,-2.57),(1.2,.6,.18),'eye' if not king else 'lava')
                r.add('head',(side*1.25-.18,28.25,-2.78),(.36,.45,.2),'pupil')
                r.add('head',(side*1.25-.65,29,-2.65),(1.3,.2,.2),'blackhair')
                r.add('head',(side*2.65-.3,26.9,-.8),(.6,1.5,1.3),skin)
            r.add('head',(-.28,27.1,-2.85),(.56,1,.45),skin)
            r.add('head',(-.65,26.15,-2.58),(1.3,.15,.15),'leather')
            hair='blackhair' if kind.startswith('kael') else 'hair'
            r.add('head',(-2.9,30,-2.6),(5.8,1.5,5.2),hair)
            for i in range(9):
                x=-2.7+i*.62
                r.add('head',(x,29-(i%3)*.35,-2.7),(.65,2,.55),hair,(0,0,(i%3-1)*12))
            for side in [-1,1]: r.add('head',(side*2.65-.3,26.6,-.2),(.6,3.6,2.7),hair)
            if kind in {'caelum','kael_hunter','kael_demon_king'}:
                r.add('head',(-1.85,27.65,-2.65),(1.1,.16,.2),'leather')
        if architect:
            # Geometric void consumes one side of the face.
            r.add('head',(.15,25.2,-2.9),(2.55,5.4,.5),'pupil')
            for j in range(3): r.add('head',(.5+j*.6,26+j,-3.2),(.25,2,.3),'gold',(0,0,-25))
    else:
        r.add('neck',(-1.7,24,-1.7),(3.4,.7,3.4),'aqua')
    # Fully split limb chains with boots, greaves, couters, articulated fingers.
    for side,label in [(-1,'l'),(1,'r')]:
        x=side*4.6; n='arm_'+label
        r.joint(n,(x,22.6,0)); r.add(n,(x-1.05,17,-1.15),(2.1,5.6,2.3),skin if father else cloth)
        fn='forearm_'+label; r.joint(fn,(x,17,0),n); r.add(fn,(x-.85,12.6,-1),(1.7,4.6,2),skin if father else cloth)
        hand='hand_'+label; r.joint(hand,(x,12.7,-.2),fn); r.add(hand,(x-.8,11.3,-1),(1.6,1.6,1.6),armor if armored else skin)
        for j in range(3):
            r.joint(hand+'_finger_'+str(j),(x-.5+j*.5,11.5,-.5),hand)
            r.add(hand+'_finger_'+str(j),(x-.7+j*.5,10.6,-.6),(.4,1.1,.7),armor if armored else skin)
        r.add(hand,(x+side*.85-.2,11.4,-.8),(.4,1,.6),armor if armored else skin)
        leg='leg_'+label; lx=side*1.8
        r.joint(leg,(lx,14,0)); r.add(leg,(lx-1.25,8,-1.4),(2.5,6.2,2.8),skin if father else cloth)
        shin='shin_'+label; r.joint(shin,(lx,8,0),leg); r.add(shin,(lx-1.05,2,-1.1),(2.1,6,2.2),skin if father else 'leather')
        r.joint('foot_'+label,(lx,2,0),shin); r.add('foot_'+label,(lx-1.25,0,-2.5),(2.5,2.1,3.6),skin if father else armor if armored else 'leather')
        if armored:
            # Layered plates overlap along joints without replacing the whole limb.
            r.add(n,(x-1.5,21.2,-1.7),(3,2.5,3.4),armor,(0,0,side*12),(x,22.6,0))
            for j in range(3): r.add(n,(x-1.25,19.2+j*.7,-1.45),(2.5,.8,2.9),armor)
            r.add(fn,(x-1.2,16,-1.55),(2.4,1.4,3.1),armor)
            r.add(fn,(x-1,13.1,-1.3),(2,2.7,.7),armor)
            r.add(leg,(lx-1.4,7.3,-1.8),(2.8,1.6,1.2),armor)
            r.add(shin,(lx-1.15,2.4,-1.35),(2.3,4.8,.6),armor)
            r.add(shin,(lx-.15,2.6,-1.8),(.3,4.3,.2),'gold' if kind!='the_nameless_knight' else 'steel')
            for j in range(3): r.add('foot_'+label,(lx-1.2,.8+j*.3,-2.6),(2.4,.25,1.8),armor)
    if armored:
        r.add('body',(-3.5,18,-2.25),(7,5.8,.8),armor)
        for side in [-1,1]:
            r.add('body',(side*1.8-1.55,20,-2.65),(3.1,3,.6),armor,(0,side*8,side*-5),(side*1.8,22,-2.3))
            for j in range(3): r.add('body',(side*1.8-1.5,13+j*1.4,-2.1),(3,1.2,.6),armor,(0,0,side*5))
        r.add('body',(-2.8,17,-2.4),(5.6,.5,.4),'gold' if kind=='caelum' else 'steel')
        if kind=='caelum':
            for j in range(4): r.add('body',(-1+j*.4,19+j*.7,-2.8),(.2,1,.15),'pupil',(0,0,-25))
    # Belts, buckle, straps and separate hanging cloth strips.
    if not father:
        r.add('body',(-3.45,15.1,-2.15),(6.9,.8,4.3),'leather')
        r.add('body',(-.65,15,-2.55),(1.3,1,.35),'gold')
    cape=kind in {'dullahan','caelum','sir_seraphiel','kael_hunter','kael_demon_king','elara_spirit'} or aion
    if cape:
        for i in range(5):
            x=-3+i*1.5; n='cloak_'+str(i); r.joint(n,(x,23,2.2))
            r.add(n,(x-.7,8+(i%2),2.3),(1.4,15-(i%2),.35),cloth)
            r.joint(n+'_hem',(x,10,2.3),n); r.add(n+'_hem',(x-.7,5+(i%3),2.3),(1.4,5-(i%3),.35),cloth)
    if kind=='the_nameless_knight':
        for i in range(3):
            n='sash_'+str(i); r.joint(n,(2,15-i*3,2),'body' if i==0 else 'sash_'+str(i-1))
            r.add(n,(1.3,12-i*3,2),(1.4,3.5,.3),'white')
    if aion or spirit:
        for i in range(7):
            x=-3.2+i*.92; n='robe_'+str(i); r.joint(n,(x,15,0))
            r.add(n,(x-.4,1.5,-2.3),(.8,13.5,.4),cloth)
            if i%3==0: r.add(n,(x-.12,2,-2.6),(.24,12,.15),'gold')
    if king:
        for side in [-1,1]: r.horn('head',[(side*2.5,30,0),(side*5,34,2),(side*5.5,37,1),(side*3.5,38,-1)],.95,'darksteel')
        for i in range(6):
            a=math.tau*i/6; x=math.cos(a)*7; y=25+math.sin(a)*6
            n='shard_'+str(i); r.joint(n,(x,y,4)); r.add(n,(x-.45,y-2,4),(.9,4,.7),'obsidian',(0,0,i*60))
            r.add(n,(x-.15,y-1,3.8),(.3,2,.2),'lava')
    if aion:
        r.joint('halo',(0,23,5)); r.ring('halo',(0,23,5),10 if architect else 7,.22,'gold',28,(2,9,17) if architect else ())
        if architect:
            r.parts=[p for p in r.parts if p['bone']!='body']
            for i in range(3): r.add('body',(-3,15+i*3.4,-1.8),(6,2.3,3.6),'white')
            for i in range(2):
                for side,label in [(-1,'l'),(1,'r')]:
                    n=f'extra_arm_{label}_{i}'; x=side*(7+i*1.4); y=21-i*4
                    r.joint(n,(x,y,2)); r.add(n,(x-.7,y-4,1.4),(1.4,4,1.2),'white',(0,0,side*(30+i*20)),(x,y,2))
                    r.add(n,(x-.8,y-5,1.2),(1.6,1.2,1.6),'gold')
    if fallen or kind=='sir_seraphiel':
        if fallen:
            feather_wings(r,pairs=3,dark=True)
            r.joint('halo',(0,34,2)); r.ring('halo',(0,34,2),4,.3,'gold',16,(1,4,9,12))
        else: r.add('body',(-.3,19,-2.9),(.6,3,.2),'gold')
    if father:
        for side in [-1,1]:
            r.horn('head',[(side*2,30,0),(side*3,34,1),(side*4,35,0)],.6,'bark')
            for i in range(4): r.bar('body',(side*2.5,16+i*1.6,-2),(side*1.1,18+i*1.6,-2.4),.35,.3,'bark')
        r.add('body',(-.7,20,-2.3),(1.4,2,.5),'green')
        r.horn('hand_r',[(4.6,12,-1),(5,15,-4),(5,21,-7)],.8,'leaf')
    if kind=='dullahan':
        r.joint('held_head',(-4.6,12,-3.5),'hand_l')
        r.add('held_head',(-7,8,-6),(4.8,5,4.5),'skin')
        for x in [-5.7,-3.9]: r.add('held_head',(x-.4,10.6,-6.2),(.8,.5,.3),'aqua')
        r.add('held_head',(-7.1,12,-6.1),(5,1.3,4.7),'blackhair')
        for side in [-1,1]:
            for i in range(8):
                y=22-i*1.2; x=side*(3.5+math.sin(i*.5)*.4)
                r.add('body',(x-.25,y,2.8),(.5,.8,.25),'steel',(0,0,i%2*90),(x,y,2.8))
    if not aion and not spirit and not father and kind!='kael_hunter': blade(r,kind=kind)
    if kind=='kael_hunter':
        r.add('body',(3,14,1),(2,3.5,2),'leather')
        r.joint('bow',(4.6,12,-1),'hand_r')
        r.horn('bow',[(4.6,6,-1),(4.6,9,-3),(4.6,15,-3),(4.6,18,-1)],.4,'wood')
        r.bar('bow',(4.6,6,-1),(4.6,18,-1),.08,.08,'white')
    if father:
        r.parts=[p for p in r.parts if p['material'] not in {'hair','blackhair'}]
        for p in r.parts:
            if p['material']=='eye':p['material']='green'
    if kind=='dullahan':
        r.parts=[p for p in r.parts if p['bone']!='neck' or p['material']=='aqua']
    return r


def feather_wings(r,pairs=3,dark=False):
    for pair in range(pairs):
        for side,label in [(-1,'l'),(1,'r')]:
            n=f'wing_{label}_{pair}'; y=25-pair*3
            r.joint(n,(side*2.5,y,2),'body',(0,0,side*(25-pair*25)))
            r.horn(n,[(side*2.5,y,2),(side*8,y+3,3),(side*16,y+2,4)],.8,'bone')
            tip=n+'_tip'; r.joint(tip,(side*12,y+2,3),n)
            for i in range(16):
                x=side*(4+i*.8); length=4+math.sin(i/16*math.pi)*7
                if dark and i in {4,11,14}: length*=.55
                bone=n if i<9 else tip
                r.add(bone,(x-.4,y-length+2,3+i*.04),(.85,length,.28),'darkfeather' if dark else 'feather',(0,0,-side*18),(x,y+2,3))
                r.add(bone,(x-.08,y-length+2.3,2.85+i*.04),(.16,length-.5,.12),'silver' if dark else 'white',(0,0,-side*18),(x,y+2,3))


def thalassia():
    r=Sculpt(); r.bones[1]['pivot']=[0,22,0]
    # Whale barrel blends into a long leviathan tail, not dragon legs or wings.
    for i in range(10):
        z=-38+i*9; w=16+math.sin((i+1)/12*math.pi)*13; h=22+math.sin(i/10*math.pi)*9
        r.add('body',(-w/2,23-h/2,z),(w,h,10),'ocean')
        r.add('body',(-w*.35,23-h/2-.3,z),(w*.7,2,9.6),'belly')
    r.joint('head',(0,26,-38)); r.add('head',(-15,14,-66),(30,24,30),'ocean')
    r.add('head',(-12,17,-77),(24,16,14),'ocean'); r.add('head',(-10,21,-82),(20,10,7),'ocean')
    r.joint('jaw',(0,17,-47),'head'); r.add('jaw',(-12,11,-76),(24,6,31),'belly')
    for side in [-1,1]:
        r.add('head',(side*14.7-.6,28,-64),(1.2,2.3,6),'aqua')
        r.horn('head',[(side*11,35,-58),(side*18,42,-51),(side*21,44,-39)],2,'bone')
        for i in range(9): r.horn('jaw',[(side*10,16,-72+i*2.5),(side*10,20,-72+i*2.5)],.8,'bone')
        for pair in range(3):
            n=f'fin_{"l" if side<0 else "r"}_{pair}'; z=-24+pair*26
            r.joint(n,(side*12,18,z)); r.horn(n,[(side*12,18,z),(side*30,13,z+3),(side*43,10,z+14)],2,'ocean')
            for i in range(9):
                x=side*(13+i*3.3); depth=18-i*1.5
                r.add(n,(x-1.7,14-i*.4,z),(3.5,.8,depth),'ocean')
                r.add(n,(x-1.6,15-i*.4,z+depth-2),(3.3,.25,1.5),'aqua')
    parent='body'
    for i in range(10):
        z=48+i*8; w=max(2,20-i*1.8); n='tail_'+str(i)
        r.joint(n,(0,21,z),parent); r.add(n,(-w/2,21-w*.4,z),(w,w*.8,9),'ocean'); parent=n
    r.joint('fluke',(0,21,125),'tail_9')
    for side in [-1,1]:
        for i in range(9): r.add('fluke',(side*(i*3)-1.6,20,125+i*.65),(3.4,1.2,15-i*1.2),'ocean')
    for i in range(14):
        z=-27+i*5
        for side in [-1,1]: r.add('body',(side*12-.4,27+math.sin(i)*2,z),(.8,1.5,2.5),'aqua')
    for i in range(12):
        x=(i%3-1)*7; z=-15+i*4; y=39
        r.horn('body',[(x,y,z),(x+2,y+6+i%4,z),(x-1,y+8+i%4,z+2)],1,'coral')
        if i%2==0: r.horn('body',[(x,y+4,z),(x-3,y+6,z-1)],.7,'coral')
    for i in range(3):
        x=(i-1)*9; z=i*14
        r.horn('body',[(x,35,z),(x+3,56,z+5)],.7,'steel')
    return r


def tree_titan():
    r=Sculpt(); r.bones[1]['pivot']=[0,32,0]
    for i in range(9):
        a=math.tau*i/9; x=math.cos(a)*7; z=math.sin(a)*5
        r.horn('body',[(x,25,z),(x*1.2,42,z),(x*.6,57,z*.7)],3,'bark')
    r.add('body',(-5,29,-4),(10,21,8),'bark'); r.joint('core',(0,43,-5)); r.add('core',(-2,40,-5.5),(4,6,1),'green')
    r.joint('head',(0,55,0)); r.add('head',(-5,53,-4),(10,10,8),'bark')
    for x in [-2,2]: r.add('head',(x-.8,58,-4.5),(1.6,.8,.6),'green')
    for side,label in [(-1,'l'),(1,'r')]:
        r.joint('arm_'+label,(side*8,50,0)); r.horn('arm_'+label,[(side*8,50,0),(side*16,40,2),(side*20,28,0)],4,'bark')
        r.joint('hand_'+label,(side*20,28,0),'arm_'+label)
        for j in range(4): r.horn('hand_'+label,[(side*20+(j-1.5)*1.4,28,0),(side*22+(j-1.5)*1.6,18,-2),(side*24+(j-1.5)*1.8,17,-4)],1,'bark')
        r.joint('leg_'+label,(side*5,30,0)); r.horn('leg_'+label,[(side*5,30,0),(side*8,15,0),(side*9,3,-3)],4.6,'bark')
        for i in range(5): r.horn('leg_'+label,[(side*9,7,0),(side*9+(i-2)*2,1,-6),(side*9+(i-2)*3,0,-13)],1.3,'bark')
    for i in range(13):
        a=math.tau*i/13; x=math.cos(a)*6; z=math.sin(a)*5; n='branch_'+str(i)
        r.joint(n,(x,53,z)); end=(x*3,67+i%4*2,z*3)
        r.horn(n,[(x,53,z),(x*2,61,z*2),end],1.7,'bark')
        for j in range(3): r.add(n,(end[0]-4+j, end[1]+j,end[2]-4),(9-j*2,2,8-j),'leaf',(0,i*19,0),end)
    return r


def orun():
    r=Sculpt(); r.bones[1]['pivot']=[0,52,0]
    # Architecture sits inside chamfered armor. Body is deliberately vertical.
    r.add('body',(-14,42,-8),(28,32,16),'sandstone')
    r.add('body',(-11,39,-10),(22,29,20),'sandstone')
    for side in [-1,1]:
        r.add('body',(side*10-2,46,-11),(4,26,3),'ancientmetal')
        for j in range(7): r.add('body',(side*10-2.3,48+j*3,-11.3),(4.6,.5,.4),'gold')
    r.joint('core',(0,59,-11)); r.ring('core',(0,59,-11),7,1.2,'ancientmetal',16)
    r.add('core',(-3,56,-12),(6,6,1.4),'aqua')
    for i in range(14): r.add('body',(-13,42+i*1.1,-13+i*.25),(6,.6,2),'sandstone')
    r.joint('head',(0,77,0)); r.add('head',(-8,76,-6),(16,17,12),'sandstone')
    r.add('head',(-10,88,-7),(20,5,14),'ancientmetal')
    for side in [-1,1]:
        r.add('head',(side*4-2,83,-6.5),(4,1,1),'aqua')
        r.add('head',(side*8-1.5,77,-5),(3,13,10),'gold')
    r.add('head',(-1.3,78,-8),(2.6,6,2),'ancientmetal')
    for side,label in [(-1,'l'),(1,'r')]:
        x=side*20
        r.joint('arm_'+label,(x,70,0)); r.add('arm_'+label,(x-6,49,-6),(12,24,12),'sandstone')
        r.add('arm_'+label,(x-7,66,-7),(14,8,14),'ancientmetal')
        r.joint('forearm_'+label,(x,48,0),'arm_'+label); r.add('forearm_'+label,(x-5,29,-5),(10,19,10),'sandstone')
        r.joint('hand_'+label,(x,30,0),'forearm_'+label)
        for j in range(4): r.add('hand_'+label,(x-5+j*2.7,20,-4),(2.2,10,7),'ancientmetal')
        lx=side*8
        r.joint('leg_'+label,(lx,42,0)); r.add('leg_'+label,(lx-5,20,-5),(10,22,10),'sandstone')
        r.add('leg_'+label,(lx-6,18,-7),(12,5,14),'ancientmetal')
        r.joint('shin_'+label,(lx,20,0),'leg_'+label); r.add('shin_'+label,(lx-4.5,4,-5),(9,15,10),'sandstone')
        r.add('shin_'+label,(lx-6,0,-12),(12,5,18),'ancientmetal')
        r.add('shin_'+label,(lx-1,7,-5.8),(2,5,.8),'aqua')
        for j in range(6): r.add('arm_'+label,(x-5,51+j*2.2,-6.6),(10,.6,.6),'gold')
    # Roof terraces and pillars silhouette, not decorative random bumps.
    for side in [-1,1]:
        for j in range(3):
            x=side*(7+j*3); r.add('body',(x-1,73,-5),(2,8+j,2),'sandstone')
        r.add('body',(side*10-5,80,-6),(10,1.5,4),'ancientmetal')
    return r


def anomaly():
    r=Sculpt(); r.bones[1]['pivot']=[0,16,0]
    for i in range(7):
        n='fragment_'+str(i); r.joint(n,((i%2-.5)*3,9+i*3,0))
        r.add(n,(-3+(i%2),9+i*3,-2),(6-i*.2,2.1,4),'void',(i*7,i*11,i*5))
    r.joint('head',(0,31,0)); r.add('head',(-3,32,-3),(6,6,6),'ivory',(12,35,15),(0,34,0))
    for side,label in [(-1,'l'),(1,'r')]:
        r.joint('arm_'+label,(side*7,24,1)); r.horn('arm_'+label,[(side*7,24,1),(side*12,17,-2),(side*9,9,-3)],1,'void')
        r.joint('leg_'+label,(side*3,10,0)); r.horn('leg_'+label,[(side*3,10,0),(side*6,5,2),(side*4,0,-3)],1.2,'void')
    for i in range(5):
        n='shard_'+str(i); a=i*math.tau/5; x=math.cos(a)*11; y=23+math.sin(a)*13
        r.joint(n,(x,y,3)); r.add(n,(x-.5,y-2,3),(1,4,1),'violet',(0,i*30,i*40),(x,y,3))
    r.add('head',(-1,34,-4),(.8,.8,.8),'pupil')
    return r


def horse():
    r=Sculpt();r.bones[1]['pivot']=[0,17,0]
    r.add('body',(-4,14,-8),(8,8,20),'darksteel')
    for i in range(8):
        for side in [-1,1]: r.bar('body',(side*2,21,-6+i*2),(side*5,15,-6+i*2),.5,.6,'bone')
    r.joint('neck',(0,21,-7)); r.add('neck',(-2.5,20,-12),(5,12,6),'darksteel',(-18,0,0),(0,21,-7))
    r.joint('head',(0,30,-12),'neck'); r.add('head',(-2.8,28,-20),(5.6,7,10),'bone'); r.add('head',(-2,25,-24),(4,6,8),'darksteel')
    for side in [-1,1]:
        r.add('head',(side*2.8-.3,31,-18),(.6,1,2),'aqua')
        r.horn('head',[(side*1.8,34,-12),(side*2.2,38,-10)],.8,'bone')
        for pos,z in [('front',-6),('back',9)]:
            n=f'leg_{pos}_{"l" if side<0 else "r"}'; x=side*3
            r.joint(n,(x,16,z)); r.add(n,(x-.6,7,z-.6),(1.2,9,1.2),'bone')
            r.joint(n+'_shin',(x,8,z),n);r.add(n+'_shin',(x-.55,1,z-.55),(1.1,7,1.1),'bone')
            r.add(n+'_shin',(x-1.2,0,z-1.5),(2.4,1.5,3),'darksteel')
            for j in range(3):r.horn(n+'_shin',[(x+j*.6-1,1,z),(x+j*.6-1,4+j%2,z+1)],.3,'aqua')
    r.joint('tail_0',(0,20,12));r.horn('tail_0',[(0,20,12),(0,13,16),(0,8,17)],1,'black')
    r.add('body',(-4.5,22,-1),(9,1.5,7),'leather');r.add('body',(-4,23,5),(8,2,1),'darksteel')
    return r


def aion_orb():
    r=Sculpt(); r.bones[1]['pivot']=[0,14,0]
    # Rounded silhouette from thin circular voxel slices, deliberately no face.
    radius=8
    for j in range(20):
        yy=-radius+(j+.5)*radius/10; rr=math.sqrt(max(.1,radius*radius-yy*yy))
        for k in range(12):
            xx=-rr+(k+.5)*rr/6; zz=math.sqrt(max(.1,rr*rr-xx*xx))
            r.add('body',(xx-rr/12,14+yy-.4,-zz),(rr/6+.02,.82,zz*2),'pupil')
    for i in range(13):
        a=i*math.tau/13; x=math.cos(a)*(10+i%3*.4); y=14+math.sin(a)*(10+i%3*.6)
        n='fragment_'+str(i); r.joint(n,(x,y,math.sin(i)*3))
        r.add(n,(x-.35,y-1.2,math.sin(i)*3),(.7,2.4,.5),'obsidian',(i*13,i*7,i*24),(x,y,0))
    return r


def little_dragon():
    r=Sculpt(); r.bones[1]['pivot']=[0,8,0]
    for o,s in [((-4,5,-4),(8,7,13)),((-3,11,-2),(6,2,8)),((-3,4,3),(6,4,7))]:r.add('body',o,s,'ocean')
    for i in range(5):r.add('body',(-2.8,4.8,-3+i*2.2),(5.6,.8,2),'ivory')
    r.joint('chest',(0,10,-3));r.add('chest',(-3.3,7,-7),(6.6,7,5),'ocean')
    r.joint('neck_0',(0,12,-5),'chest');r.add('neck_0',(-2.8,11,-8),(5.6,5,5),'ocean')
    r.joint('head',(0,15,-8),'neck_0')
    r.add('head',(-4.5,13,-13),(9,7,8),'ocean');r.add('head',(-3.2,12.5,-17),(6.4,3.8,6),'ocean')
    r.add('head',(-2.5,14,-18),(5,1.8,2),'ocean')
    r.joint('jaw',(0,13,-10),'head');r.add('jaw',(-2.8,11.8,-17),(5.6,1.2,7),'ivory')
    for side,label in [(-1,'l'),(1,'r')]:
        r.add('head',(side*2.8-1.2,16,-13.25),(2.4,1.9,.4),'violet')
        r.add('head',(side*2.8-.35,16.2,-13.72),(.7,1.45,.25),'pupil')
        r.add('head',(side*2.8-.65,17.05,-14),(.45,.5,.22),'white')
        r.add('head',(side*2.8-1.4,18,-13.4),(2.8,.65,.6),'ocean',(0,0,-side*8),(side*2.8,18,-13))
        r.horn('head',[(side*3.3,19,-7),(side*5.1,22,-4),(side*6,23,-.5)],1.5,'bone')
        r.horn('head',[(side*4,15,-7),(side*7,16,-4),(side*7.8,18,-3)],.8,'ocean')
        r.add('head',(side*1.8-.4,15.2,-18.2),(.8,.5,.3),'pupil')
        for pos,z in [('front',-3),('back',6)]:
            n=f'leg_{pos}_{label}'; x=side*3.4
            r.joint(n,(x,8,z));r.add(n,(x-1.4,3,z-1.5),(2.8,5,3),'ocean')
            r.joint(n+'_paw',(x,3,z),n);r.add(n+'_paw',(x-1.5,1,z-2.5),(3,2.4,4),'ocean')
            for i in range(3):r.horn(n+'_paw',[(x-1+i,1.8,z-2),(x-1+i,1.2,z-4)],.45,'bone')
        n='wing_'+label;r.joint(n,(side*3,12,1));r.joint(n+'_tip',(side*13,16,-2),n)
        r.horn(n,[(side*3,12,1),(side*8,17,-2),(side*13,16,-2)],1.1,'ocean')
        r.horn(n+'_tip',[(side*13,16,-2),(side*22,13,-3),(side*26,11,0)],.7,'ocean')
        for i in range(10):
            x=6+i*2; d=12-i*.7; bone=n if x<13 else n+'_tip'
            r.add(bone,(-x-2 if side<0 else x,12.5,-1),(2.05,.25,d),'void')
        for i in range(4):
            x=side*(8+i*5);bone=n if i==0 else n+'_tip'
            r.horn(bone,[(side*8,14,-1),(x,12,11-i)],.35,'aqua')
    parent='body'
    for i in range(9):
        n='tail_'+str(i);z=8+i*3;w=max(.65,4-i*.42);y=7-i*.45
        r.joint(n,(0,y,z),parent);r.add(n,(-w/2,y-w*.35,z),(w,w*.7,3.5),'ocean');parent=n
        if i%2==0:r.horn(n,[(0,y+w*.35,z),(0,y+w*.35+1.5,z+1)],.5,'ivory')
    for i in range(5):r.horn('body',[(0,12,-1+i*2),(0,14.3-i*.2,i*2)],.55,'ivory')
    return r


def aion_dark(kind):
    r=person(kind)
    replacement={'white':'black','skin':'darksteel','hair':'blackhair','gold':'ancientmetal','eye':'violet','leather':'black'}
    for p in r.parts:
        p['material']=replacement.get(p['material'],p['material'])
    # High split collar and asymmetric mantle frame a barely readable dark face.
    for side in [-1,1]:
        r.add('body',(side*2.8-1,22.5,-1.8),(2,4.5,3.6),'obsidian',(0,0,-side*15),(side*2.8,23,0))
        r.add('body',(side*3.7-1.1,21.3,0),(2.2,2.2,3.7),'darksteel',(0,0,side*18),(side*3.7,22,0))
    r.add('body',(-.18,17,-2.35),(.36,6,.3),'violet')
    r.add('head',(-3,30,-2.8),(6,1.5,5.6),'black')
    if kind=='aion_the_architect':
        for i in range(8):
            a=i*math.tau/8;x=math.cos(a)*11;y=23+math.sin(a)*11;n='authority_fragment_'+str(i)
            r.joint(n,(x,y,5));r.add(n,(x-.45,y-2.2,5),(.9,4.4,.65),'obsidian',(0,0,i*45),(x,y,5))
            r.add(n,(x-.14,y-1.8,4.8),(.28,3.6,.2),'violet',(0,0,i*45),(x,y,5))
    return r


def paint_atlas(e,r):
    """Unique padded island per cube face; directional edge paint, no shared swatch UV."""
    width=1024 if len(r.parts)>260 else 512; padding=2; rows=[]; x=y=padding; rowh=0
    factor=e['recipe_scale']
    for pi,p in enumerate(r.parts):
        w,h,d=[v/factor for v in p['size']]; p['uv']={}
        for face,(fw,fh) in {'north':(w,h),'south':(w,h),'east':(d,h),'west':(d,h),'up':(w,d),'down':(w,d)}.items():
            iw=max(2,min(48,math.ceil(fw*2))); ih=max(2,min(48,math.ceil(fh*2)))
            if x+iw+padding>width: x=padding;y+=rowh+padding*2;rowh=0
            p['uv'][face]={'uv':[x,y],'uv_size':[iw,ih]}
            rows.append((pi,face,x,y,iw,ih,p['material'])); x+=iw+padding*2; rowh=max(rowh,ih)
    height=2**math.ceil(math.log2(y+rowh+padding)); im=Image.new('RGBA',(width,height),(0,0,0,0))
    for pi,face,x,y,w,h,material in rows:
        col,kind=M[material]; col=rgb(col)
        seed=int(hashlib.sha256(f'{e["id"]}:{pi}:{face}'.encode()).hexdigest()[:8],16); rng=random.Random(seed)
        tile=Image.new('RGBA',(w,h)); pix=tile.load()
        for yy in range(h):
            for xx in range(w):
                n=rng.choice([-3,-2,0,0,1,2,3]); grad=5*(1-yy/max(h,1))
                if kind=='metal': grad+=10*math.sin(xx/max(1,w)*math.pi)-5
                if kind=='scale':
                    # Staggered overlapping scales with directional lower rims.
                    sx=(xx+(yy//5%2)*3)%6; sy=yy%5
                    n+=7 if sy==0 and 1<=sx<=4 else -8 if sy==4 else 0
                if kind=='bark': n+=-10 if (xx+int(math.sin(yy*.18)*2))%7==0 else 0
                if kind in {'cloth','hair','feather'}: n+=3 if xx%3==0 else -2
                if kind=='stone': n+=-7 if xx%13==0 or yy%11==0 else 0
                if kind=='glow': grad=20*(1-abs(xx-w/2)/max(1,w/2));n=0
                edge=7 if yy==0 or xx==0 else -9 if yy==h-1 or xx==w-1 else 0
                if kind in {'skin','flat'}:edge=0;grad=0
                pix[xx,yy]=tuple(max(0,min(255,int(c+n+grad+edge))) for c in col)+(255,)
        dr=ImageDraw.Draw(tile)
        if kind=='metal' and w>5 and h>5:
            for a,b in [(2,2),(w-3,h-3)]: dr.point((a,b),fill=(211,202,178,255))
            if rng.random()<.4: dr.line([(w//2,2),(min(w-2,w//2+2),min(h-2,6))],fill=(*[min(255,c+23) for c in col],255))
        if material=='obsidian' and e['id']=='vharos' and w>7 and h>7 and pi%6==0:
            points=[(w//2,1),(w//2-2,h//3),(w//2+1,h//2),(w//2-1,h-2)]
            dr.line(points,fill=(115,54,28,255),width=3);dr.line(points,fill=(236,138,48,255),width=1)
        if material=='ocean' and w>7 and h>7 and pi%7==0:
            dr.line([(2,h//2),(w//3,h//2-2),(w-3,h//2)],fill=(94,191,180,255),width=1)
        # Bleed the island border into the padding, preserving nearest-neighbor mip edges.
        im.paste(tile.resize((w+4,h+4),Image.Resampling.NEAREST),(x-2,y-2));im.paste(tile,(x,y))
    for p in r.parts:p['material']=list(M).index(p['material'])%8
    e['texture_width']=width;e['texture_height']=height
    return im


def animate(e,r):
    out={}; scale=e['recipe_scale']; id=e['id']; isdragon=id in {'vharos','true_morrow','little_morrow'}
    def k(seq): return {str(t):v for t,v in seq}
    def R(seq): return {'rotation':k(seq)}
    def P(seq): return {'position':k([(t,[q*scale for q in v]) for t,v in seq])}
    def clip(name,duration,tracks,loop=False):
        out['animation.unwritten.'+id+'.'+name]={'loop':loop,'animation_length':duration,'bones':{n:v for n,v in tracks.items() if r.has(n)}}
    z=[0,0,0]
    if id=='aion_prologue':
        tracks={'body':P([(0,z),(2,[0,.65,0]),(4,z)])}
        for i in range(13):
            tracks['fragment_'+str(i)]=R([(0,z),(2,[i*.6,i*2,12]),(4,z)])
        clip('idle',4,tracks,True)
        clip('walk',4,tracks,True)
        clip('presence_pulse',2,{'body':{'scale':k([(0,[1,1,1]),(.7,[1.025,.98,1.025]),(1,[.99,1.025,.99]),(2,[1,1,1])])}})
        clip('reveal_cue',3,{'body':{'scale':k([(0,[1,1,1]),(1.8,[1.1,.9,1.1]),(2.5,[.45,1.3,.45]),(3,[.02,.02,.02])])},**{'fragment_'+str(i):P([(0,z),(2,[math.cos(i)*4,math.sin(i)*4,2]),(3,[math.cos(i)*9,math.sin(i)*9,5])]) for i in range(13)}})
        return out
    wings=[b['name'] for b in r.bones if b['name'].startswith('wing_') and not b['name'].endswith('_tip')]
    tails=[b['name'] for b in r.bones if b['name'].startswith('tail_')]
    cloak=[b['name'] for b in r.bones if b['name'].startswith(('cloak_','sash_','robe_'))]
    idle={'body':P([(0,z),(1.7,[0,.22,0]),(3.4,z)])}
    if r.has('head'):idle['head']=R([(0,z),(1.7,[1.5,-1,0]),(3.4,z)])
    for i,n in enumerate(cloak):idle[n]=R([(0,[2+i%3,0,0]),(1.7,[4+i%3,0,0]),(3.4,[2+i%3,0,0])])
    clip('idle',3.4,idle,True)
    for name,duration,amp in [('walk',1.6 if isdragon else 1.1,18),('run',.85 if isdragon else .62,34)]:
        tracks={'body':P([(0,z),(duration*.25,[0,-.4,0]),(duration*.5,z),(duration*.75,[0,-.4,0]),(duration,z)])}
        for side,label in [(-1,'l'),(1,'r')]:
            for pos,phase in [('front',1),('back',-1)]:
                n=f'leg_{pos}_{label}'; a=amp*side*phase
                tracks[n]=R([(0,[a,0,0]),(duration*.5,[-a,0,0]),(duration,[a,0,0])])
                for child in [n+'_elbow',n+'_paw',n+'_shin']:
                    tracks[child]=R([(0,[0,0,0]),(duration*.25,[12,0,0]),(duration*.5,z),(duration,z)])
            a=amp*side
            tracks['leg_'+label]=R([(0,[a,0,0]),(duration*.5,[-a,0,0]),(duration,[a,0,0])])
            tracks['shin_'+label]=R([(0,z),(duration*.25,[18,0,0]),(duration*.5,z),(duration,z)])
            tracks['arm_'+label]=R([(0,[-a*.7,0,0]),(duration*.5,[a*.7,0,0]),(duration,[-a*.7,0,0])])
        clip(name,duration,tracks,True)
    clip('hurt',.55,{'body':R([(0,z),(.1,[-5,-3,2]),(.22,[-8,2,-1]),(.55,z)]),'head':R([(0,z),(.12,[-8,5,0]),(.55,z)])})
    clip('stunned',2,{'body':R([(0,[8,0,0]),(1,[10,0,1]),(2,[8,0,0])]),'head':R([(0,[12,-2,0]),(1,[15,3,0]),(2,[12,-2,0])])},True)
    clip('death',3.8,{'body':P([(0,z),(.9,[0,-2,0]),(1.7,[0,-7,0]),(3.8,[0,-8,0])]),'root':R([(0,z),(.9,[0,0,8]),(1.7,[0,0,68]),(3.8,[0,0,72])])})
    if isdragon:
        necks=['neck_'+str(i) for i in range(4)]
        clip('sleeping_breathing',4,{'body':P([(0,[0,-11,0]),(2,[0,-10.4,0]),(4,[0,-11,0])]),**{n:R([(0,[14,0,0]),(2,[13,0,0]),(4,[14,0,0])]) for n in necks}},True)
        clip('wake_up_roar',5,{'body':P([(0,[0,-11,0]),(1.5,[0,-10,0]),(3,z),(5,z)]),'head':R([(0,[24,0,0]),(2,[10,-8,0]),(3.2,[-18,0,0]),(5,z)]),'jaw':R([(0,z),(2,z),(3.2,[30,0,0]),(4.3,[24,0,0]),(5,z)])})
        clip('bite',1.25,{'chest':R([(0,z),(.38,[-9,0,0]),(.6,[12,0,0]),(1.25,z)]),'head':R([(0,z),(.38,[-12,0,0]),(.6,[18,0,0]),(1.25,z)]),'jaw':R([(0,z),(.38,[32,0,0]),(.62,z),(1.25,z)])})
        clip('fire_breath' if id=='vharos' else 'authority_tear',4.4,{'chest':R([(0,z),(1,[-8,0,0]),(1.4,z),(3.5,z),(4.4,z)]),'head':R([(0,z),(1,[-10,0,0]),(1.4,[5,-13,0]),(3.5,[5,15,0]),(4.4,z)]),'jaw':R([(0,z),(1,[8,0,0]),(1.4,[27,0,0]),(3.5,[25,0,0]),(4.4,z)])})
        for side,label in [(-1,'l'),(1,'r')]:
            clip('claw_swipe_'+label,1.6,{'body':R([(0,z),(.6,[0,-side*8,0]),(.85,[0,side*10,0]),(1.6,z)]),'leg_front_'+label:R([(0,z),(.6,[-65,0,side*30]),(.85,[5,side*20,-side*25]),(1.6,z)])})
        clip('tail_sweep',2.2,{n:R([(0,z),(.8,[0,-18,0]),(1.15,[0,22,0]),(1.6,[0,8,0]),(2.2,z)]) for n in tails})
        clip('wing_unfold',2.5,{n:R([(0,[0,0,60 if '_l' in n else -60]),(1.2,[0,0,15 if '_l' in n else -15]),(2.5,z)]) for n in wings})
        clip('fly',1.5,{n:R([(0,[0,0,-18 if '_l' in n else 18]),(.6,[0,0,27 if '_l' in n else -27]),(1.5,[0,0,-18 if '_l' in n else 18])]) for n in wings},True)
        for name,seq in [('takeoff',[(0,z),(.65,[0,-4,0]),(1.2,[0,8,0]),(2.8,[0,30,0])]),('crash_landing',[(0,[0,30,0]),(.9,[0,2,0]),(1.2,[0,-5,0]),(2.8,z)])]:
            clip(name,2.8,{'body':P(seq),**{n:R([(0,z),(.6,[0,0,35 if '_l' in n else -35]),(1.2,[0,0,-20 if '_l' in n else 20]),(2.8,z)]) for n in wings}})
        clip('aerial_turn',2,{'root':R([(0,z),(.8,[0,20,12]),(1.4,[0,35,8]),(2,z)]),'head':R([(0,z),(.5,[0,15,0]),(2,z)])})
        clip('hundredth_awakening',7,{'body':P([(0,[0,-10,0]),(2,[0,-8,0]),(3.4,[0,2,0]),(4.8,[0,5,0]),(7,z)]),'head':R([(0,[20,0,0]),(2,[0,-15,0]),(3.4,[-25,0,0]),(5,[-18,0,0]),(7,z)]),'jaw':R([(0,z),(2,z),(3.4,[35,0,0]),(5,[30,0,0]),(7,z)]),**{n:R([(0,z),(2,[0,0,45 if '_l' in n else -45]),(3.4,[0,0,-12 if '_l' in n else 12]),(7,z)]) for n in wings}})
    elif id=='thalassia':
        fins=[b['name'] for b in r.bones if b['name'].startswith('fin_')]
        tracks={n:R([(0,[0,math.sin(i*.6)*5,0]),(2,[0,-math.sin(i*.6)*5,0]),(4,[0,math.sin(i*.6)*5,0])]) for i,n in enumerate(tails)}
        tracks.update({n:R([(0,[0,0,-7]),(2,[0,0,7]),(4,[0,0,-7])]) for n in fins})
        clip('swim',4,tracks,True);out['animation.unwritten.'+id+'.idle']=out['animation.unwritten.'+id+'.swim']
        for name,angle in [('breach',-32),('dive',30),('body_ram',-8)]:
            clip(name,3.5,{'body':R([(0,z),(1,[angle,0,0]),(2.5,[angle*.7,0,0]),(3.5,z)]),'jaw':R([(0,z),(1,[20,0,0]),(3.5,z)])})
        clip('death_sinking',6,{'root':P([(0,z),(2,[0,-8,0]),(6,[0,-35,0])]),'body':R([(0,z),(3,[12,0,10]),(6,[20,0,18])])})
    else:
        # Humanoid attack trajectories: staged wind-up, contact, follow-through, recovery.
        for i in range(5):
            d=1.05 if id=='dullahan' else .72; sign=-1 if i%2 else 1
            clip('slash_'+str(i+1),d,{'body':R([(0,z),(d*.38,[0,-sign*14,0]),(d*.55,[0,sign*20,0]),(d*.8,[0,sign*9,0]),(d,z)]),'arm_r':R([(0,z),(d*.38,[-105+i*7,-20,-sign*35]),(d*.55,[-35,35,sign*32]),(d*.8,[8,12,10]),(d,z)]),'forearm_r':R([(0,z),(d*.38,[-40,0,0]),(d*.55,[-5,0,0]),(d,z)]),'head':R([(0,z),(d*.38,[0,sign*8,0]),(d,z)])})
        for i in range(3):clip('thrust_'+str(i+1),.75,{'body':P([(0,z),(.28,[0,0,1]),(.42,[0,0,-2]),(.75,z)]),'arm_r':R([(0,z),(.28,[-45,-12,0]),(.42,[-92,i*6,0]),(.75,z)]),'forearm_r':R([(0,z),(.28,[-45,0,0]),(.42,z),(.75,z)])})
        for name,a in [('parry_high',-100),('parry_low',-42),('counter',-125)]:clip(name,.8,{'arm_r':R([(0,z),(.2,[a,0,40]),(.4,[a+12,0,36]),(.8,z)]),'forearm_r':R([(0,z),(.2,[-30,0,0]),(.4,[-15,0,0]),(.8,z)])})
        for name,dx,dz in [('dodge_left',-4,0),('dodge_right',4,0),('backstep',0,4)]:clip(name,.65,{'root':P([(0,z),(.1,[dx*.2,-.5,dz*.2]),(.3,[dx,-1,dz]),(.65,[dx,0,dz])]),'body':R([(0,z),(.1,[10,0,-dx*3]),(.3,[4,0,-dx*2]),(.65,z)])})
        clip('kneel',2.8,{'body':P([(0,z),(1.2,[0,-4,0]),(2.8,[0,-4,0])]),'leg_l':R([(0,z),(1.2,[-65,0,0]),(2.8,[-65,0,0])]),'shin_r':R([(0,z),(1.2,[65,0,0]),(2.8,[65,0,0])]),'head':R([(0,z),(1.8,[18,0,0]),(2.8,[22,0,0])])})
        clip('reach',2.6,{'arm_r':R([(0,z),(1.3,[-72,0,-8]),(2.6,[-80,0,-6])]),'forearm_r':R([(0,z),(1.3,[-20,0,0]),(2.6,[-8,0,0])]),'head':R([(0,z),(1.3,[0,-8,0]),(2.6,[0,-10,0])])})
        clip('guard_break',1.2,{'body':R([(0,z),(.22,[-20,0,4]),(.65,[-14,0,2]),(1.2,z)]),'arm_r':R([(0,z),(.22,[-30,0,50]),(1.2,z)])})
        clip('sitting',3,{'body':P([(0,[0,-6,0]),(1.5,[0,-5.8,0]),(3,[0,-6,0])]),**{'leg_'+l:R([(0,[-85,0,0]),(3,[-85,0,0])]) for l in ['l','r']},**{'shin_'+l:R([(0,[85,0,0]),(3,[85,0,0])]) for l in ['l','r']}},True)
        if id=='dullahan':
            clip('head_throw',1.7,{'arm_l':R([(0,z),(.45,[-60,0,-25]),(.8,[-100,0,15]),(1.7,z)]),'held_head':P([(0,z),(.45,z),(.8,[0,4,-8]),(1.2,[0,4,-12]),(1.7,z)])})
            clip('mounted_idle',2,{'body':P([(0,[0,-4,0]),(1,[0,-3.8,0]),(2,[0,-4,0])]),'leg_l':R([(0,[-70,0,-25]),(2,[-70,0,-25])]),'leg_r':R([(0,[-70,0,25]),(2,[-70,0,25])])},True)
        if id in {'caelum','elara_spirit'}:clip('reunion',4,{'head':R([(0,[12,0,0]),(1.5,[0,-12,0]),(4,[-3,-12,0])]),'arm_r':R([(0,z),(2,[-60,0,-12]),(4,[-75,0,-8])]),'forearm_r':R([(0,z),(2,[-18,0,0]),(4,[-10,0,0])])})
        if id=='the_nameless_knight':
            clip('wall_kick',1.2,{'body':R([(0,z),(.3,[0,0,-20]),(.6,[0,40,10]),(1.2,z)]),'leg_r':R([(0,z),(.3,[-85,0,0]),(.6,[30,0,0]),(1.2,z)]),'root':P([(0,z),(.3,[0,3,0]),(.6,[-3,5,0]),(1.2,[-5,0,0])])})
            clip('rooftop_landing',1.8,{'root':P([(0,[0,8,0]),(.55,z),(.8,[0,-3,0]),(1.8,z)]),'head':R([(0,z),(.8,[15,0,0]),(1.8,z)])})
            clip('final_look_up',3,{'head':R([(0,[24,0,0]),(1.5,[8,0,0]),(3,[-8,0,0])])})
        if id in {'verdant_giant','orun'}:
            clip('stomp',2.8,{'leg_r':R([(0,z),(1,[-30,0,0]),(1.3,[5,0,0]),(2.8,z)]),'body':P([(0,z),(1,[0,1,0]),(1.3,[0,-2,0]),(2.8,z)])})
            clip('arm_slam',3,{'arm_r':R([(0,z),(1.2,[-100,0,-10]),(1.65,[25,0,0]),(3,z)]),'body':R([(0,z),(1.2,[-8,0,0]),(1.65,[12,0,0]),(3,z)])})
        if id=='verdant_the_last_father':clip('seed_planting',4,{'body':R([(0,z),(1.6,[40,0,0]),(2.8,[40,0,0]),(4,z)]),'arm_r':R([(0,z),(1.6,[-25,0,0]),(2.8,[-10,0,0]),(4,z)]),'head':R([(0,z),(1.6,[20,0,0]),(4,z)])})
    if wings and not isdragon:
        clip('hover',2,{n:R([(0,[0,0,-6 if '_l' in n else 6]),(1,[0,0,12 if '_l' in n else -12]),(2,[0,0,-6 if '_l' in n else 6])]) for n in wings},True)
        clip('wings_erupt',3,{'body':P([(0,z),(1.3,[0,-1,0]),(1.7,[0,2,0]),(3,[0,4,0])]),'head':R([(0,z),(1.3,[25,0,0]),(1.7,[-20,0,0]),(3,z)]),**{n:R([(0,[0,0,70 if '_l' in n else -70]),(1.3,[0,0,60 if '_l' in n else -60]),(1.7,[0,0,-15 if '_l' in n else 15]),(3,z)]) for n in wings}})
    if id.startswith('aion'):
        for i,name in enumerate(['finger_snap','delete','copy','paste','rewind','gravity_change','arena_rewrite','authority_beam']):
            d=1.2+i*.1
            clip(name,d,{'arm_r':R([(0,z),(d*.4,[-65-i*4,8,0]),(d*.58,[-60-i*4,2,0]),(d,z)]),'forearm_r':R([(0,z),(d*.4,[-25,0,0]),(d*.58,[-15,0,0]),(d,z)]),'hand_r_finger_1':R([(0,z),(d*.4,[-60,0,0]),(d*.58,z),(d,z)]),'halo':R([(0,z),(d*.4,[0,0,10+i*8]),(d,[0,0,15+i*10])])})
    if id=='morrow_anomaly':
        clip('impossible_twitch',2,{b['name']:R([(0,z),(.6,z),(.61,[20+i*3,40,15]),(.9,[20+i*3,40,15]),(.91,z),(2,z)]) for i,b in enumerate(r.bones) if b['name'].startswith(('fragment','head'))},True)
    if id=='little_morrow':
        clip('curious_head_tilt',2.5,{'head':R([(0,z),(.5,[0,12,18]),(1.5,[0,-10,-12]),(2.5,z)])})
        clip('eat_cheese',1.4,{'head':R([(0,[10,0,0]),(.35,[14,0,0]),(.7,[10,0,0]),(1.05,[14,0,0]),(1.4,[10,0,0])]),'jaw':R([(0,z),(.2,[14,0,0]),(.4,z),(.6,[14,0,0]),(.8,z),(1.1,[14,0,0]),(1.4,z)])},True)
        clip('happy_bounce',1.1,{'body':P([(0,z),(.2,[0,-2,0]),(.5,[0,5,0]),(.8,[0,-1,0]),(1.1,z)]),'head':R([(0,z),(.5,[-12,0,0]),(1.1,z)])})
        clip('yawn',3.2,{'head':R([(0,z),(.8,[-12,0,0]),(2.3,[-10,0,0]),(3.2,z)]),'jaw':R([(0,z),(.8,[30,0,0]),(2.3,[26,0,0]),(3.2,z)])})
        clip('sit',2,{'body':P([(0,[0,-4,0]),(1,[0,-3.8,0]),(2,[0,-4,0])]),'leg_back_l':R([(0,[-55,0,0]),(2,[-55,0,0])]),'leg_back_r':R([(0,[-55,0,0]),(2,[-55,0,0])])},True)
    # Preview locomotion aliases remain intact; no runtime combat action is implied.
    first=next((k for k in out if k.endswith('.bite') or k.endswith('.slash_1')),None)
    if first:out['animation.unwritten.'+id+'.attack']=out[first]
    return {k:v for k,v in out.items() if v['bones']}


BUILDERS={
 'vharos':lambda:dragon('vharos'),'true_morrow':lambda:dragon('true_morrow'),
 'little_morrow':little_dragon,'thalassia':thalassia,'orun':orun,
 'verdant_giant':tree_titan,'morrow_anomaly':anomaly,'dullahan_horse':horse,
 **{k:(lambda k=k:person(k)) for k in ['dullahan','caelum','elara_spirit','kael_hunter','kael_demon_king','sir_seraphiel','fallen_seraphiel','the_nameless_knight','verdant_the_last_father']},
 'aion_prologue':aion_orb,'aion':lambda:aion_dark('aion'),'aion_the_architect':lambda:aion_dark('aion_the_architect'),
}

def build():
    catalog=json.loads((ROOT/'catalog/assets.json').read_text()); report=[]
    for e in catalog['entries']:
        if e['id'] not in BUILDERS:continue
        if any((ROOT/'source_overrides'/e[key]).exists() for key in ['source','geometry','texture']):
            print('Preserving saved override for '+e['id']);continue
        r=BUILDERS[e['id']](); axis=2 if e['id'] in {'vharos','true_morrow','thalassia'} else 1
        lo=min(p['origin'][axis] for p in r.parts); hi=max(p['origin'][axis]+p['size'][axis] for p in r.parts)
        factor=e['size']*16/(hi-lo);e['recipe_scale']=factor;r.scaled(factor)
        im=paint_atlas(e,r);tex=ROOT/e['texture'];im.save(tex)
        anim=animate(e,r);g=geometry(e,r)
        dump(ROOT/e['geometry'],g);dump(ROOT/e['source'],bbmodel(e,r,tex,anim))
        dump(RP/f'animations/unwritten/{e["id"]}.animation.json',{'format_version':'1.8.0','animations':anim})
        path=RP/f'entity/{e["id"]}.entity.json'; client=json.loads(path.read_text());desc=client['minecraft:client_entity']['description']
        desc['animations']={k.rsplit('.',1)[-1]:k for k in anim};desc['animations']['locomotion']='controller.animation.unwritten.'+e['id'];dump(path,client)
        e.update(status='bespoke_art_pass_2',rig_bones=len(r.bones),cubes=len(r.parts),animations=[k.rsplit('.',1)[-1] for k in anim],
          texture_layout='Unique padded face islands, directional material painting',
          limitations=['Bespoke art pass; actual Blockbench and Bedrock client review still required.','VFX, phase transitions, collision and gameplay are separate server work.'])
        report.append({k:e[k] for k in ['id','cubes','rig_bones','texture_width','texture_height','animations']})
    catalog['version']='0.2.0';dump(ROOT/'catalog/assets.json',catalog);dump(ROOT/'docs/colossi-art-report.json',report)
    for folder,filename in [(RP,'UNWRITTEN_Assets.mcpack'),(BP,'UNWRITTEN_Preview.mcpack')]:
        manifest=json.loads((folder/'manifest.json').read_text());manifest['header']['version']=[0,2,0]
        for m in manifest['modules']:m['version']=[0,2,0]
        for dep in manifest.get('dependencies',[]):dep['version']=[0,2,0]
        dump(folder/'manifest.json',manifest)
        with zipfile.ZipFile(ROOT/'dist'/filename,'w',zipfile.ZIP_DEFLATED) as z:
            for p in sorted(folder.rglob('*')):
                if p.is_file():
                    info=zipfile.ZipInfo(str(p.relative_to(folder)),date_time=(2026,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,p.read_bytes())
    print(json.dumps({'bespoke_forms':len(report),'cubes':sum(x['cubes'] for x in report),'clips':sum(len(x['animations']) for x in report)}))

if __name__=='__main__':build()
