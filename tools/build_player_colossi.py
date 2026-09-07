#!/usr/bin/env python3
"""Steve-proportion Colossi: standard 64x64 skins plus removable entity extras.

Six rigid base cubes. No sculpted fingers, neck, elbows, knees or changed anatomy.
The supplied Decem Fata poster guides palette/costume, not realistic proportions.
"""
import json
import math
import zipfile
from PIL import Image, ImageDraw
from build_assets import ROOT, RP, BP, dump, geometry, bbmodel, uid
from build_colossi import Sculpt, animate

IDS=['dullahan','caelum','elara_spirit','kael_hunter','kael_demon_king',
     'sir_seraphiel','fallen_seraphiel','the_nameless_knight',
     'verdant_the_last_father','aion','aion_the_architect']

# Standard Java/Bedrock Steve texture locations, including modern left limbs.
PARTS={
 'head':((-4,24,-4),(8,8,8),(0,24,0),(0,0)),
 'body':((-4,12,-2),(8,12,4),(0,12,0),(16,16)),
 'arm_r':((-8,12,-2),(4,12,4),(-5,22,0),(40,16)),
 'arm_l':((4,12,-2),(4,12,4),(5,22,0),(32,48)),
 'leg_r':((-4,0,-2),(4,12,4),(-2,12,0),(0,16)),
 'leg_l':((0,0,-2),(4,12,4),(2,12,0),(16,48)),
}
THEMES={
 'dullahan':('#bca58f','#272534','#263040','#8492a0','#282638','#79c5c4'),
 'caelum':('#d1b7a3','#d9dbe0','#697887','#b8c2c9','#384652','#69818f'),
 'elara_spirit':('#d2e3e0','#e5ecea','#d0dedc','#f1ece0','#9baeb1','#738f99'),
 'kael_hunter':('#d3ad97','#3b2a2b','#60493c','#aa8964','#333139','#8e5148'),
 'kael_demon_king':('#d3ad97','#3b2a2b','#302d38','#a0875c','#6d2b35','#d26750'),
 'sir_seraphiel':('#dbc1a9','#e1ded4','#d6d7cd','#b79a56','#e7e6d9','#7b9696'),
 'fallen_seraphiel':('#cbb8ac','#dedbd3','#9e9e99','#a98c57','#4b4650','#97636c'),
 'the_nameless_knight':('#3a434d','#242b34','#303944','#9aa8ae','#222b35','#10161c'),
 'verdant_the_last_father':('#d4d6bd','#71664b','#c7c9ab','#6d7652','#868e65','#74b66d'),
 'aion':('#d5d2c8','#8f9196','#dcd8cb','#ae9051','#bbb9b3','#5b5b65'),
 'aion_the_architect':('#d5d2c8','#8f9196','#d2cfc5','#b49a60','#aaaab1','#4d4b58'),
}

def rgb(h):return tuple(bytes.fromhex(h[1:]))
def tint(c,d):return tuple(max(0,min(255,q+d)) for q in c)
def skin_uv(offset,size):
    u,v=offset;w,h,d=size
    return {
      'east':{'uv':[u,v+d],'uv_size':[d,h]},
      'north':{'uv':[u+d,v+d],'uv_size':[w,h]},
      'west':{'uv':[u+d+w,v+d],'uv_size':[d,h]},
      'south':{'uv':[u+2*d+w,v+d],'uv_size':[w,h]},
      'up':{'uv':[u+d,v],'uv_size':[w,d]},
      'down':{'uv':[u+d+w,v],'uv_size':[w,d]},
    }

def draw_skin(id):
    skin,hair,armor,trim,cloth,eye=map(rgb,THEMES[id]);im=Image.new('RGBA',(64,64),(0,0,0,0))
    sealed=id in {'dullahan','the_nameless_knight'}
    aion=id.startswith('aion');wood=id=='verdant_the_last_father';ghost=id=='elara_spirit'
    for part,(_,size,_,offset) in PARTS.items():
        for face,uv in skin_uv(offset,size).items():
            w,h=uv['uv_size'];tile=Image.new('RGBA',(w,h));px=tile.load();d=ImageDraw.Draw(tile)
            base=skin if part=='head' else armor
            for y in range(h):
                for x in range(w):
                    # Deliberate stepped light ramps, not noise or projected imagery.
                    light=5*(1-x/max(1,w-1))+4*(1-y/max(1,h-1))
                    face_bias={'north':1,'south':-3,'east':-2,'west':2,'up':4,'down':-5}[face]
                    shade=int((light+face_bias-5)/2)*2
                    px[x,y]=tint(base,shade)+(255,)
            if part=='head':
                if sealed:
                    d.rectangle((0,0,w-1,h-1),fill=armor)
                    d.line((0,1,w-1,1),fill=tint(armor,13))
                    if face=='north':
                        d.rectangle((1,3,6,3),fill=(12,17,23))
                        d.line((3,4,3,6),fill=trim)
                        d.point((1,6),fill=trim);d.point((6,6),fill=trim)
                    if face in {'east','west'}:d.line((w-2,2,w-2,h-2),fill=tint(armor,15))
                elif aion:
                    # Featureless mask: no ordinary Steve eyes or smile.
                    for yy in range(h):
                        for xx in range(w):
                            d.point((xx,yy),fill=tint(skin,int(8-xx*1.4-yy*1.2)))
                    if face=='north':
                        for y in range(8):
                            for x in range(8):
                                dist=(x-3.5)**2+(y-3.5)**2
                                d.point((x,y),fill=tint(skin,int(-dist*1.8+4)))
                        # A subtle central void, no human eyes/nose/mouth.
                        d.point((3,3),fill=(127,124,127));d.point((4,4),fill=(146,142,141))
                elif wood:
                    for x in [1,5]:d.line((x,1,x,h-1),fill=tint(skin,-20))
                    if face=='north':
                        d.point((2,4),fill=eye);d.point((5,4),fill=eye)
                        d.line((3,6,4,6),fill=trim)
                else:
                    if face in {'up','south'}:d.rectangle((0,0,w-1,h-1),fill=hair)
                    elif face!='down':
                        d.rectangle((0,0,w-1,1),fill=hair)
                        for x in range(w):
                            if x%3!=1:d.point((x,2),fill=tint(hair,-12))
                        if face in {'east','west'}:
                            d.rectangle((0,2,2,h-1),fill=hair)
                            d.rectangle((4,4,5,5),fill=tint(skin,-13))
                    if face=='north':
                        for x in [1,5]:
                            d.point((x,4),fill=(219,222,217));d.point((x+1,4),fill=eye)
                        d.point((3,5),fill=tint(skin,-15));d.point((4,5),fill=tint(skin,-9))
                        d.line((3,6,4,6),fill=tint(skin,-26))
                        if id=='caelum':d.point((6,5),fill=(155,126,119))
            elif part=='body':
                if face in {'north','south'}:
                    if wood:
                        for x in [1,3,6]:d.line((x,1,(x+1)%w,h-2),fill=trim)
                        if face=='north':d.rectangle((3,3,4,5),fill=eye)
                    elif ghost or aion:
                        for yy in range(h):
                            for xx in range(w):
                                folds=[0,5,-10,-4,8,2,-8,-2]
                                d.point((xx,yy),fill=tint(armor,folds[xx%8]-(yy//4)*2))
                        for x in [0,7]:d.line((x,0,x,h-1),fill=trim if aion else tint(armor,12))
                        d.line((1,0,3,3),fill=trim);d.line((6,0,4,3),fill=trim)
                        d.point((3,4),fill=tint(trim,18));d.point((4,4),fill=tint(trim,-9))
                        if aion:
                            d.line((2,5,3,7),fill=trim);d.line((5,5,4,7),fill=trim)
                            for x in [1,6]:
                                for yy in [5,8]:d.point((x,yy),fill=tint(trim,6))
                        d.line((0,10,7,10),fill=cloth)
                    else:
                        # Pixel-painted chestplate, collar, fauld and belt.
                        if id!='kael_hunter':
                            for yy in range(2,7):
                                for xx in range(w):
                                    ramp=[-10,3,17,-13,-8,11,20,-7]
                                    d.point((xx,yy),fill=tint(armor,ramp[xx]+(2 if yy==2 else -2)))
                        d.line((0,0,2,2),fill=trim);d.line((7,0,5,2),fill=trim)
                        d.line((3,3,3,6),fill=tint(armor,-18))
                        d.line((1,3,1,5),fill=tint(armor,23));d.line((6,3,6,5),fill=tint(armor,23))
                        for y in [7,9]:d.line((0,y,7,y),fill=tint(armor,-19))
                        d.line((0,10,7,10),fill=cloth);d.rectangle((3,10,4,11),fill=trim)
                        if id=='caelum':d.line((5,2,4,5),fill=(43,48,53))
                        if id.startswith('kael'):d.line((0,6,7,6),fill=cloth)
                        if id=='fallen_seraphiel':d.line((1,1,4,6),fill=(48,45,55))
                        # Plate rivets, reflected edges, under-plate contact shadows.
                        if id!='kael_hunter':
                            for x in [1,6]:d.point((x,2),fill=tint(trim,15))
                            d.line((0,8,7,8),fill=tint(armor,7))
                        else:
                            d.line((1,1,5,8),fill=cloth)
                            for yy in [2,4,6]:d.point((6,yy),fill=trim)
                else:d.line((0,8,w-1,8),fill=cloth)
            elif part.startswith('arm'):
                if wood:
                    d.line((1,0,1,11),fill=trim)
                else:
                    if face in {'north','south','east','west'}:
                        for yy in range(h):
                            d.point((0,yy),fill=tint(armor,-14));d.point((2,yy),fill=tint(armor,9))
                    d.line((0,2,w-1,2),fill=trim)
                    d.rectangle((0,5,w-1,6),fill=cloth)
                    d.line((0,9,w-1,9),fill=trim)
                    if id in {'kael_hunter','elara_spirit','aion','aion_the_architect'}:
                        d.rectangle((0,10,w-1,11),fill=skin)
            elif part.startswith('leg'):
                if wood:d.line((1,0,2,11),fill=trim)
                elif ghost or aion:
                    d.rectangle((0,0,w-1,h-1),fill=cloth)
                    d.line((0,0,0,h-1),fill=trim)
                    d.line((1,0,1,h-1),fill=tint(cloth,13));d.line((3,0,3,h-1),fill=tint(cloth,-14))
                    d.line((0,h-2,w-1,h-2),fill=trim)
                else:
                    d.rectangle((0,0,w-1,2),fill=cloth)
                    d.line((0,5,w-1,5),fill=trim)
                    d.line((1,7,1,9),fill=tint(armor,17))
                    d.rectangle((0,10,w-1,11),fill=tint(cloth,-6))
            im.paste(tile,tuple(uv['uv']))
    # Standard transparent head overlay: layered hair or narrow helm edging.
    for face,uv in skin_uv((32,0),(8,8,8)).items():
        w,h=uv['uv_size'];tile=Image.new('RGBA',(w,h));d=ImageDraw.Draw(tile)
        if sealed:
            if face=='north':d.line((0,0,7,0),fill=trim+(255,));d.line((0,1,0,6),fill=armor+(255,))
        elif not aion and not wood:
            if face=='up':d.rectangle((0,0,7,7),fill=tint(hair,5)+(255,))
            elif face in {'north','east','west','south'}:
                d.rectangle((0,0,7,1),fill=tint(hair,3)+(255,))
                for x,y in [(0,2),(1,2),(4,2),(6,2),(7,3)]:d.point((x,y),fill=tint(hair,-5)+(255,))
        im.paste(tile,tuple(uv['uv']))
    return im


def player_rig(id):
    r=Sculpt();r.bones[1]['pivot']=[0,12,0]
    for name,(o,s,p,offset) in PARTS.items():
        if name!='body':r.joint(name,p)
        if id=='dullahan' and name=='head':continue
        r.add(name,o,s,0);r.parts[-1].update(uv=skin_uv(offset,s),base_part=name)
    if id!='dullahan':
        r.add('head',(-4.25,23.75,-4.25),(8.5,8.5,8.5),0)
        r.parts[-1].update(uv=skin_uv((32,0),(8,8,8)),skin_overlay=True)
    for side,x in [('r',-6),('l',6)]:r.joint('hand_'+side,(x,12,0),'arm_'+side)
    # Simple extras, all under explicit attachment groups. Can be hidden in editor.
    def extra(n,o,s,slot=0,rot=None,pivot=None):
        r.add(n,o,s,slot,rot,pivot);r.parts[-1]['attachment']=True
    def joint(n,p,parent='body',rot=None):return r.joint(n,p,parent,rot)
    def horns(n,points,w,slot=2):
        before=len(r.parts);r.horn(n,points,w,slot)
        for p in r.parts[before:]:p['attachment']=True
    def ring(n,c,rad,slot=2,gaps=()):
        before=len(r.parts);r.ring(n,c,rad,.25,slot,20,gaps)
        for p in r.parts[before:]:p['attachment']=True
    armored=id in {'dullahan','caelum','sir_seraphiel','fallen_seraphiel','the_nameless_knight','kael_demon_king'}
    if armored:
        for side,x in [('r',-6),('l',6)]:
            joint('pauldron_'+side,(x,23,0),'arm_'+side)
            extra('pauldron_'+side,(x-2.3,21.9,-2.35),(4.6,2.4,4.7),0)
            extra('pauldron_'+side,(x-2.45,21.7,-2.5),(4.9,.45,5),2)
    cape=id!='verdant_the_last_father'
    if cape:
        for i in range(3):
            x=-3+i*3;n='cloak_'+str(i);joint(n,(x,23,2.2))
            hem=4+(i%2)*1.5 if id in {'dullahan','the_nameless_knight'} else 6
            extra(n,(x-1.45,hem,2.35),(2.9,23-hem,.35),1)
            extra(n,(x-1.45,hem,2.25),(.2,23-hem,.15),2)
    if id in {'elara_spirit','aion','aion_the_architect'}:
        for side,x in [('r',-2),('l',2)]:
            n='robe_'+side;joint(n,(x,12,0),'leg_'+side)
            extra(n,(x-2.12,.4,-2.12),(4.24,11.6,.2),1)
    if id=='dullahan':
        joint('neck_mist',(0,24,0));extra('neck_mist',(-1.5,24,-1.5),(3,.5,3),3)
        joint('held_head',(6,12,-3),'hand_l')
        extra('held_head',(3,6,-6),(6,6,6),0)
        r.parts[-1]['uv']=skin_uv((0,0),(8,8,8))
        r.parts[-1]['held_head_skin']=True
    if id=='kael_demon_king':
        for sign in [-1,1]:horns('head',[(sign*3,31,0),(sign*5,35,1),(sign*5,37,-1),(sign*3,37.5,-2)],.8,0)
        joint('crown',(0,31,0),'head')
        for i in range(5):extra('crown',(-3+i*1.5,31.2,-3.8),(.6,1.5+i%2,.45),2)
        for i in range(6):
            a=i*math.tau/6;x=math.cos(a)*8;y=24+math.sin(a)*6;n='shard_'+str(i)
            joint(n,(x,y,5));extra(n,(x-.35,y-1.8,5),(.7,3.6,.7),0,(0,0,i*60),(x,y,5))
    if id in {'sir_seraphiel','fallen_seraphiel'}:
        if id=='fallen_seraphiel':
            for pair in range(3):
                for sign,label in [(-1,'l'),(1,'r')]:
                    y=23-pair*3;n=f'wing_{label}_{pair}';joint(n,(sign*3,y,2.5),'body',(0,0,sign*(25-pair*24)))
                    horns(n,[(sign*3,y,3),(sign*9,y+3,3),(sign*15,y+2,4)],.6,2)
                    for i in range(10):
                        x=sign*(5+i);ln=4+math.sin(i/10*math.pi)*5
                        if i in {3,8}:ln*=.6
                        extra(n,(x-.5,y+2-ln,3),(.95,ln,.25),4,(0,0,-sign*18),(x,y+2,3))
            joint('halo',(0,35,1));ring('halo',(0,35,1),3.6,2,(1,5,11,15))
    if id=='verdant_the_last_father':
        for sign in [-1,1]:horns('head',[(sign*2.5,31,0),(sign*3.2,34,1),(sign*4.5,35,0)],.5,2)
        horns('hand_r',[(-6,12,-1),(-6,18,-3),(-6,22,-5)],.65,5)
    if id.startswith('aion'):
        joint('halo',(0,25,5));ring('halo',(0,25,5),9,2,(3,10,16) if id.endswith('architect') else ())
        for sign in [-1,1]:
            extra('body',(sign*3-1,22.5,-1),(2,3.5,3),0,(0,0,-sign*18),(sign*3,23,0))
            for i in range(3):
                x=sign*(3.8+i*.45)
                extra('body',(x-.25,22-i*.7,2),(.5,3,2.6),2,(0,0,sign*18),(x,22,2))
        for i in range(8):
            a=i*math.tau/8;x=math.cos(a)*9;y=25+math.sin(a)*9
            extra('halo',(x-.16,y-.8,4.8),(.32,1.6,.5),2,(0,0,i*45),(x,y,5))
        if id=='aion_the_architect':
            # Extra arms are accessories. Six original Steve body cubes stay intact.
            for pair in range(2):
                for sign,label in [(-1,'l'),(1,'r')]:
                    x=sign*(8+pair*1.8);y=22-pair*3;n=f'extra_arm_{label}_{pair}';joint(n,(x,y,3))
                    extra(n,(x-1,y-7,2),(2,7,2),0,(0,0,sign*(25+pair*15)),(x,y,3))
            for i in range(8):
                a=i*math.tau/8;x=math.cos(a)*11;y=25+math.sin(a)*11;n='authority_fragment_'+str(i)
                joint(n,(x,y,5));extra(n,(x-.3,y-1.6,5),(.6,3.2,.6),2,(0,0,i*45),(x,y,5))
    if armored:
        joint('sword',(-6,12,-1),'hand_r',(-15,0,0))
        extra('sword',(-6.4,10,-1.4),(.8,3,.8),1)
        extra('sword',(-8,13,-1.4),(4,.6,.8),2)
        extra('sword',(-6.55,13.6,-1.25),(1.1,11,.5),0)
        extra('sword',(-6.16,14,-1.45),(.32,10,.2),2)
    if id=='kael_hunter':
        joint('satchel',(4,15,2));extra('satchel',(3.7,12,1.5),(2.2,3.5,2),1)
        joint('bow',(-6,12,-1),'hand_r');horns('bow',[(-6,6,-1),(-6,9,-3),(-6,15,-3),(-6,18,-1)],.35,2)
    return r


def entity_atlas(id,r,skin):
    sk,ha,ar,tr,cl,ey=map(rgb,THEMES[id]);palette=[ar,cl,tr,ey,cl if id=='fallen_seraphiel' else (206,210,204),(88,124,76)]
    width=512;x=2;y=82;rowh=0;islands=[]
    for pi,p in enumerate(r.parts):
        if not p.get('attachment') or 'uv' in p:continue
        p['uv']={};w,h,d=p['size']
        for face,(fw,fh) in {'north':(w,h),'south':(w,h),'east':(d,h),'west':(d,h),'up':(w,d),'down':(w,d)}.items():
            iw=max(2,min(32,math.ceil(fw*2)));ih=max(2,min(48,math.ceil(fh*2)))
            if x+iw+2>width:x=2;y+=rowh+4;rowh=0
            p['uv'][face]={'uv':[x,y],'uv_size':[iw,ih]}
            islands.append((p['bone'],pi,p['material'],face,x,y,iw,ih));x+=iw+4;rowh=max(rowh,ih)
    height=2**math.ceil(math.log2(y+rowh+2));atlas=Image.new('RGBA',(width,height));atlas.paste(skin,(0,0))
    for bone,pi,slot,face,x,y,w,h in islands:
        col=palette[slot];tile=Image.new('RGBA',(w,h));d=ImageDraw.Draw(tile)
        cloth=slot==1;metal=slot in {0,2};feather=slot==4
        for yy in range(h):
            for xx in range(w):
                t=xx/max(1,w-1);v=yy/max(1,h-1)
                if cloth:
                    # Longitudinal fabric folds with dark trough and thin ridge.
                    shade=int(6*math.cos((t*2.5+pi*.09)*math.pi)-v*5)
                elif metal:
                    # Broad reflected highlight and occlusion at plate boundaries.
                    shade=int(18*math.exp(-((t-.28)/.2)**2)-8*t-4*v)
                elif feather:shade=9 if abs(t-.5)<.08 else int(-8*abs(t-.5))
                else:shade=int(9*(1-t)-v*4)
                edge=7 if xx==0 or yy==0 else -11 if xx==w-1 or yy==h-1 else 0
                d.point((xx,yy),fill=tint(col,shade+edge)+(255,))
        if cloth and w>3 and h>5:
            for yy in range(2,h-2,3):d.point((1,yy),fill=tint(col,15))
        if metal and w>5 and h>5:
            d.point((2,2),fill=tint(col,30));d.point((w-3,h-3),fill=tint(col,-15))
        if id.startswith('aion') and cloth and w>6 and h>8:
            d.line((2,1,2,h-2),fill=tr);d.line((w-3,1,w-3,h-2),fill=tint(tr,-8))
            cy=h//2;cx=w//2
            d.line([(cx,cy-3),(cx+2,cy),(cx,cy+3),(cx-2,cy),(cx,cy-3)],fill=tr)
        atlas.paste(tile.resize((w+4,h+4),Image.Resampling.NEAREST),(x-2,y-2));atlas.paste(tile,(x,y))
    return atlas


def write_skinpack(skins):
    folder=ROOT/'packs/UNWRITTEN_Colossi_Skins';folder.mkdir(exist_ok=True)
    dump(folder/'manifest.json',{'format_version':1,'header':{'name':'pack.name','version':[0,3,0],'uuid':uid('colossi_skins/header')},'modules':[{'type':'skin_pack','version':[0,3,0],'uuid':uid('colossi_skins/module')}]})
    dump(folder/'skins.json',{'serialize_name':'unwritten_colossi','localization_name':'unwritten_colossi','skins':[{'localization_name':id,'geometry':'geometry.humanoid.custom','texture':id+'.png','type':'free'} for id in skins]})
    for id,im in skins.items():im.save(folder/(id+'.png'))
    names=['skinpack.unwritten_colossi=UNWRITTEN Colossi Base Skins','skinpack.unwritten_colossi.by=AION','pack.name=UNWRITTEN Colossi Base Skins']
    names += [f'skin.unwritten_colossi.{id}={id.replace("_"," ").title()}' for id in skins]
    (folder/'texts').mkdir(exist_ok=True);(folder/'texts/en_US.lang').write_text('\n'.join(names)+'\n')
    dump(folder/'texts/languages.json',['en_US'])
    return folder


def build():
    cat=json.loads((ROOT/'catalog/assets.json').read_text());skins={};reports=[]
    for e in cat['entries']:
        id=e['id']
        if id not in IDS:continue
        if any((ROOT/'source_overrides'/e[key]).exists() for key in ['source','geometry','texture']):continue
        r=player_rig(id);skin=draw_skin(id);skins[id]=skin
        target=ROOT/'skins/colossi'/f'{id}.png';target.parent.mkdir(parents=True,exist_ok=True);skin.save(target)
        atlas=entity_atlas(id,r,skin);atlas.save(ROOT/e['texture'])
        e.update(recipe_scale=1,texture_width=atlas.width,texture_height=atlas.height,size=2,size_axis='height')
        animations=animate(e,r)
        dump(ROOT/e['geometry'],geometry(e,r));dump(ROOT/e['source'],bbmodel(e,r,ROOT/e['texture'],animations))
        dump(RP/f'animations/unwritten/{id}.animation.json',{'format_version':'1.8.0','animations':animations})
        path=RP/f'entity/{id}.entity.json';j=json.loads(path.read_text());desc=j['minecraft:client_entity']['description']
        desc['animations']={n.rsplit('.',1)[-1]:n for n in animations};desc['animations']['locomotion']='controller.animation.unwritten.'+id
        dump(path,j)
        e.update(status='player_skin_art_pass_3',base_rig='Steve / 4px arms / six rigid body parts',
          skin=str(target.relative_to(ROOT)),texture_layout='64x64 standard skin with individually painted padded accessory face islands',
          cubes=len(r.parts),rig_bones=len(r.bones),animations=[n.rsplit('.',1)[-1] for n in animations],
          limitations=['Player base skin does not include 3D attachments.','Dullahan headless presentation is entity-only.','Actual Blockbench/Bedrock import and performance review remain untested.'])
        base=[p for p in r.parts if p.get('base_part')]
        reports.append({'id':id,'base_cubes':len(base),'attachment_cubes':sum(bool(p.get('attachment')) for p in r.parts),
                        'base_dimensions':{p['base_part']:p['size'] for p in base},'skin':e['skin'],'cubes':len(r.parts),'bones':len(r.bones)})
    cat['version']='0.3.0';dump(ROOT/'catalog/assets.json',cat);dump(ROOT/'docs/player-colossi-report.json',reports)
    skinfolder=write_skinpack(skins)
    for folder,name in [(RP,'UNWRITTEN_Assets.mcpack'),(BP,'UNWRITTEN_Preview.mcpack'),(skinfolder,'UNWRITTEN_Colossi_Skins.mcpack')]:
        if folder!=skinfolder:
            j=json.loads((folder/'manifest.json').read_text());j['header']['version']=[0,3,0]
            for m in j['modules']:m['version']=[0,3,0]
            for dep in j.get('dependencies',[]):dep['version']=[0,3,0]
            dump(folder/'manifest.json',j)
        with zipfile.ZipFile(ROOT/'dist'/name,'w',zipfile.ZIP_DEFLATED) as z:
            for p in sorted(folder.rglob('*')):
                if p.is_file():
                    zi=zipfile.ZipInfo(str(p.relative_to(folder)),date_time=(2026,1,1,0,0,0));zi.compress_type=zipfile.ZIP_DEFLATED;z.writestr(zi,p.read_bytes())
    print(f'Built {len(reports)} Steve-proportion humanoids with standalone 64x64 skins.')

if __name__=='__main__':build()
