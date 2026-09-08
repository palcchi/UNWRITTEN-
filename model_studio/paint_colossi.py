"""Original pixel-art material and character painting on unique face UV islands.

No reference-image pixels, downloaded textures or shared color swatches.
Broad authored clusters carry shading; no random pixel noise is applied.
"""
import math
from PIL import Image, ImageDraw

HUMANS={'dullahan','caelum','elara_spirit','kael_hunter','kael_demon_king','sir_seraphiel','fallen_seraphiel','the_nameless_knight','verdant_the_last_father','aion','aion_the_architect'}
ARMOR={'dullahan','caelum','kael_demon_king','sir_seraphiel','fallen_seraphiel'}
DRAGONS={'vharos','little_morrow','true_morrow','morrow_anomaly'}

def rgb(c):return tuple(bytes.fromhex(c.lstrip('#')))

def tone(c,level):
    """Six-value hue-shifted ramps, deliberately quantized."""
    shifts={-3:(-39,-35,-25),-2:(-26,-24,-16),-1:(-13,-12,-7),0:(0,0,0),1:(17,18,18),2:(35,36,31),3:(55,52,42)}
    return tuple(max(0,min(255,v+d)) for v,d in zip(c,shifts[max(-3,min(3,level))]))+(255,)

class Tile:
    def __init__(self,w,h,c):
        self.w=w;self.h=h;self.im=Image.new('RGBA',(w,h),c);self.d=ImageDraw.Draw(self.im)
    def pt(self,p):return (round(p[0]*(self.w-1)),round(p[1]*(self.h-1)))
    def poly(self,pts,c):self.d.polygon([self.pt(p) for p in pts],fill=c)
    def rect(self,a,b,c):
        x,y=self.pt(a);xx,yy=self.pt(b);self.d.rectangle((min(x,xx),min(y,yy),max(x,xx),max(y,yy)),fill=c)
    def line(self,pts,c,width=1):self.d.line([self.pt(p) for p in pts],fill=c,width=width)

def material_kind(id,p):
    mat=p['material'];bone=p['bone']
    if mat=='skin':return 'skin'
    if mat=='hair':return 'hair'
    if mat in {'eye','core','light'}:return 'glow'
    if mat=='void':return 'void'
    if id in {'sir_seraphiel','fallen_seraphiel'} and bone.startswith('wing_'):return 'feather'
    if id=='orun':return 'stone' if mat in {'base','edge','stone'} else 'leaf' if mat=='moss' else 'metal'
    if id=='verdant_giant':return 'leaf' if mat in {'leaf','moss'} else 'bark'
    if id=='verdant_the_last_father':return 'leaf' if mat in {'trim','accent'} else 'cloth' if mat=='cloth' else 'bark'
    if id in DRAGONS:
        return 'membrane' if mat=='wing' else 'horn' if mat in {'bone','horn'} else 'belly' if mat=='belly' else 'scale'
    if id=='thalassia':return 'stone' if mat=='barnacle' else 'horn' if mat=='coral' else 'whale'
    if id=='dullahan_horse':return 'cloth' if mat=='cloth' else 'hair' if mat=='hair' else 'metal' if mat in {'edge','trim','accent'} else 'skin'
    if mat=='trim':return 'metal'
    if mat in {'cloth','accent'} or 'cloak' in bone or 'robe' in bone:return 'cloth'
    if id in ARMOR:return 'metal'
    return 'cloth'

def paint_face(id,p,face,w,h,palette,index):
    c=rgb(palette[p['material']]);kind=material_kind(id,p);bone=p['bone'];mat=p['material']
    bias={'north':0,'south':-1,'east':-1,'west':0,'up':1,'down':-2}[face]
    t=Tile(w,h,tone(c,bias));shade=lambda n:tone(c,n+bias)
    # One coherent volume pass: light upper-left, dark underside and far edge.
    t.poly([(0,0),(.78,0),(.6,.17),(.18,.25),(0,.5)],shade(1))
    t.poly([(.78,0),(1,0),(1,1),(.67,1),(.8,.7),(.9,.3)],shade(-1))
    t.poly([(0,.85),(.22,.77),(.61,.86),(1,.8),(1,1),(0,1)],shade(-1))
    if kind=='cloth':
        t.poly([(.07,.15),(.25,.07),(.2,.62),(.34,1),(.12,.9)],shade(-2))
        t.poly([(.25,.07),(.32,.05),(.26,.61),(.4,1),(.31,.9),(.19,.62)],shade(1))
        t.poly([(.78,.05),(.86,.17),(.7,.72),(.83,1),(.66,.85)],shade(-1))
        if 'cloak' in bone:
            t.line([(.05,.1),(.05,.87),(.3,.91),(.37,.98)],shade(2))
            t.poly([(0,1),(.18,.86),(.23,1),(.47,.95),(.6,1)],shade(-3))
    elif kind=='metal':
        t.poly([(.07,.08),(.4,.05),(.25,.61),(.15,.79)],shade(2))
        t.poly([(.45,.06),(.57,.1),(.44,.7),(.29,.85)],shade(1))
        t.poly([(.64,.06),(.8,.1),(.59,.68),(.52,.94),(.45,.76)],shade(-2))
        t.line([(.05,.72),(.18,.9),(.79,.9),(.95,.76)],shade(1))
        t.line([(.06,.77),(.19,.97),(.82,.97),(.96,.8)],shade(-2))
        if w>=9 and h>=8:
            for x,y in [(.12,.14),(.85,.82)]:
                xx,yy=t.pt((x,y));t.d.rectangle((xx,yy,xx+1,yy+1),fill=shade(-2));t.d.point((xx,yy),fill=shade(3))
            if index%3==0:t.line([(.7,.26),(.62,.37),(.66,.4)],shade(-2))
    elif kind=='feather':
        t.poly([(.12,0),(.42,0),(.46,.82),(.3,1),(.13,.67)],shade(1))
        t.poly([(.63,0),(.9,.1),(.83,.73),(.53,1),(.59,.64)],shade(-1))
        t.line([(.48,.04),(.52,.58),(.44,.94)],shade(2))
        for y in [.25,.49,.72]:
            t.line([(.13,y-.1),(.43,y+.06)],shade(-1))
            t.line([(.61,y+.06),(.86,y-.08)],shade(-1))
    elif kind=='hair':
        for i,(x,y) in enumerate([(.2,.06),(.66,.1)]):
            t.poly([(x,y),(x+.2,y),(x+.12,.55),(x+.18,.85),(x+.04,1),(x,.57)],shade(1 if i else -1))
            if h>8:t.line([(x+.08,y+.08),(x+.04,.5),(x+.08,.67)],shade(1))
        t.poly([(0,.92),(.2,.86),(.35,.98),(.68,.94),(1,.88),(1,1),(0,1)],shade(-1))
    elif kind=='bark':
        for i,x in enumerate([.14,.43,.77]):
            t.poly([(x,0),(x+.08,0),(x+.02,.35),(x+.1,.66),(x+.03,1),(x-.04,1),(x+.02,.63),(x-.05,.3)],shade(-2))
            t.line([(x+.1,.08),(x+.05,.31),(x+.13,.65),(x+.07,.9)],shade(2))
        if w>10 and h>12:
            t.poly([(.37,.44),(.48,.35),(.63,.42),(.65,.59),(.55,.7),(.41,.61)],shade(-2))
            t.poly([(.46,.46),(.54,.43),(.58,.52),(.53,.6),(.48,.56)],shade(1))
    elif kind=='leaf':
        for x,y in [(.08,.08),(.45,.04),(.25,.4),(.65,.47),(.03,.74)]:
            t.poly([(x,y+.13),(x+.14,y),(x+.3,y+.11),(x+.25,y+.28),(x+.1,y+.3)],shade(1))
            t.line([(x+.05,y+.19),(x+.15,y+.12),(x+.25,y+.14)],shade(2))
    elif kind=='stone':
        t.poly([(.08,.1),(.75,.08),(.62,.4),(.11,.55)],shade(1))
        t.line([(0,.57),(.38,.56),(.42,.7),(1,.65)],shade(-2))
        t.line([(.71,0),(.64,.15),(.69,.32),(.6,.54)],shade(-2))
        t.line([(.72,.02),(.67,.16),(.72,.29)],shade(1))
        t.poly([(0,0),(.2,0),(.1,.13),(0,.12)],shade(-2))
        if 'leg' in bone or 'forearm' in bone:
            t.line([(.38,.24),(.59,.24),(.59,.4),(.41,.4),(.41,.32)],shade(-2))
            t.line([(.4,.22),(.61,.22),(.61,.4)],shade(2))
    elif kind=='scale':
        # Broad staggered pixel clusters rather than tiny checkerboard noise.
        for row in range(0,h,8):
            for col in range(-4 if (row//8)%2 else 0,w,8):
                t.d.polygon([(col+1,row+1),(col+6,row),(col+8,row+3),(col+5,row+7),(col+2,row+6)],fill=shade(0 if (row//8+col//8)%3 else 1))
                t.d.line([(col+1,row+2),(col+5,row+1),(col+7,row+3)],fill=shade(1))
                t.d.line([(col+2,row+6),(col+5,row+7),(col+7,row+5)],fill=shade(-1))
        t.poly([(.84,0),(1,0),(1,1),(.7,1),(.85,.72)],shade(-1))
    elif kind=='membrane':
        for x in [.14,.5,.85]:
            t.poly([(x-.05,0),(x+.01,0),(x+.13,.6),(x+.05,1),(x-.02,.62)],shade(-2))
            t.line([(x+.03,.03),(x+.15,.6),(x+.07,.95)],shade(1))
        t.line([(0,.9),(.15,.83),(.45,.92),(.73,.85),(1,.9)],shade(-2))
    elif kind=='belly':
        for row in range(3,h,6):
            t.d.line([(0,row),(w//2,row+1),(w-1,row)],fill=shade(-2))
            t.d.line([(1,row+2),(w//2,row+3),(w-2,row+2)],fill=shade(1))
    elif kind=='horn':
        t.poly([(.1,0),(.35,0),(.45,1),(.25,1)],shade(2))
        t.poly([(.62,0),(.85,0),(.74,1),(.52,1)],shade(-1))
        for y in [.28,.55,.82]:t.line([(0,y),(.3,y+.03),(.85,y)],shade(-1))
    elif kind=='whale':
        t.poly([(0,.16),(.2,.07),(.7,.13),(1,.04),(1,.35),(.67,.4),(.22,.28),(0,.4)],shade(1))
        t.poly([(0,.65),(.22,.5),(.61,.67),(1,.58),(1,1),(0,1)],shade(-1))
        if mat=='belly':
            for x in [.15,.35,.55,.75]:t.line([(x,.13),(x-.04,.46),(x+.03,.89)],shade(-1))
        elif bone=='body' and face in {'east','west'} and index%2==0:
            t.line([(.2,.36),(.32,.4),(.45,.36),(.63,.41)],tone(rgb(palette['scar']),1))
    elif kind=='skin':
        t.poly([(0,.55),(.17,.32),(.38,.43),(.29,.75),(.44,1),(0,1)],shade(-1))
        t.poly([(.32,.15),(.62,.15),(.69,.36),(.58,.56),(.43,.42)],shade(1))
    elif kind=='glow':
        t.rect((.12,.12),(.85,.85),shade(1));t.rect((.3,.3),(.68,.67),shade(3))
    elif kind=='void':
        t.im.paste(tone(c,0),(0,0,w,h))
        t.line([(0,.2),(.13,0),(.8,0)],shade(1))

    # Painted face replaces tiny floating facial geometry on Steve humanoids.
    if id in HUMANS and mat=='skin' and bone in {'head','held_head'}:
        if face=='north':
            t.rect((0,0),(1,1),shade(0))
            t.poly([(0,0),(.15,0),(.1,.68),(.24,.88),(.84,.88),(1,.65),(1,1),(0,1)],shade(-1))
            t.rect((0,0),(1,.14),shade(-1))
            t.rect((.18,.45),(.38,.56),tone(rgb(palette['edge']),2))
            t.rect((.62,.45),(.82,.56),tone(rgb(palette['edge']),2))
            for x in [.29,.65]:t.rect((x,.44),(x+.1,.57),tone(rgb(palette['eye']),0))
            brow=rgb(palette['hair'])
            t.line([(.15,.4),(.27,.37),(.4,.4)],tone(brow,-1))
            t.line([(.6,.4),(.74,.37),(.85,.4)],tone(brow,-1))
            t.rect((.46,.6),(.51,.64),shade(-1))
            t.line([(.39,.79),(.58,.79)],shade(-1))
            if id=='caelum':t.line([(.79,.58),(.77,.68)],tone((154,116,97),0))
            if id=='fallen_seraphiel':t.line([(.74,.61),(.65,.68),(.74,.76),(.68,.84)],tone(rgb(palette['accent']),-2))
            if id=='kael_demon_king':
                for x in [.24,.73]:t.line([(x,.62),(x,.7)],tone(rgb(palette['accent']),-1))
        elif face in {'east','west'}:
            t.rect((.38,.44),(.6,.68),shade(-1));t.rect((.44,.47),(.6,.61),shade(1))
    # Base player limbs contain painted cuffs, boots, and seams; scale never changes.
    part=p.get('steve_base')
    if id in HUMANS and part and part.startswith('arm') and face in {'north','south','east','west'}:
        t.rect((0,.85),(1,1),tone(rgb(palette['skin']),bias))
        t.rect((0,.8),(1,.84),tone(rgb(palette['trim']),-1))
        t.line([(.15,.88),(.15,.97)],tone(rgb(palette['skin']),bias+1))
    if id in HUMANS and part and part.startswith('leg'):
        t.rect((0,.81),(1,1),tone(rgb(palette['cloth']),-2))
        t.line([(.1,.81),(.85,.81)],tone(rgb(palette['trim']),-1))
        t.line([(.16,.88),(.16,.96),(.72,.96)],tone(rgb(palette['cloth']),1))
    if id in HUMANS and bone=='body' and face=='north' and (p.get('steve_base')=='body' or (mat=='base' and p['size'][2]<1)):
        trim=rgb(palette['trim'])
        t.poly([(.04,0),(.18,0),(.5,.23),(.81,0),(.94,0),(.5,.35)],tone(trim,0))
        t.line([(.06,.02),(.49,.29),(.92,.03)],tone(trim,2))
        if id in ARMOR:
            t.line([(.18,.42),(.44,.52),(.44,.76)],shade(-2))
            t.line([(.82,.42),(.56,.52),(.56,.76)],shade(-2))
            t.line([(.14,.44),(.4,.55)],shade(2))
        else:
            t.line([(.46,.34),(.39,.69),(.5,.88)],shade(-2))
            t.line([(.52,.35),(.45,.69),(.57,.88)],shade(1))
    if id=='vharos' and mat=='base' and bone in {'neck_1','jaw'} and face in {'north','east','west'}:
        crack=[(.25,0),(.36,.23),(.29,.41),(.49,.6),(.43,.82),(.55,1)]
        t.line(crack,(113,44,32,255),3);t.line(crack,(245,112,34,255),1)
    if id=='true_morrow' and mat in {'wing','accent'}:
        t.line([(.1,.12),(.3,.28),(.26,.47),(.5,.7),(.4,.93)],(143,119,185,255),1)
    # Bevels remain one pixel wide; they are not thick uniform outlines.
    if kind not in {'skin','glow','void','hair'}:
        t.d.line([(0,0),(w-1,0)],fill=shade(2))
        t.d.line([(0,h-1),(w-1,h-1)],fill=shade(-2))
        if w>4:t.d.line([(w-1,1),(w-1,h-2)],fill=shade(-1))
    return t.im

def prepare_model(id,r):
    """Use pixels for face detail rather than numerous tiny face cubes."""
    if id in HUMANS:
        def facial(p):
            if p['bone'] not in {'head','held_head'}:return False
            if p['material']=='eye':return True
            if p['bone']=='head' and p['material']=='edge' and p['size'][1]<1:return True
            return p['bone']=='head' and p['material']=='accent' and p['size'][1]<.4
        r.parts=[p for p in r.parts if not facial(p)]
    return r

def paint_atlas(id,r,palette):
    width=512;x=y=2;row=0;islands=[]
    for index,p in enumerate(r.parts):
        w,h,d=p['size'];p['uv']={}
        for face,(fw,fh) in {'north':(w,h),'south':(w,h),'east':(d,h),'west':(d,h),'up':(w,d),'down':(w,d)}.items():
            iw=max(2,min(64,math.ceil(fw*2)));ih=max(2,min(64,math.ceil(fh*2)))
            if x+iw+2>width:x=2;y+=row+4;row=0
            p['uv'][face]={'uv':[x,y],'uv_size':[iw,ih]}
            islands.append((index,p,face,x,y,iw,ih));x+=iw+4;row=max(row,ih)
    height=2**math.ceil(math.log2(y+row+2));atlas=Image.new('RGBA',(width,height))
    for index,p,face,x,y,w,h in islands:
        tile=paint_face(id,p,face,w,h,palette,index);atlas.paste(tile,(x,y))
        # Actual edge extrusion, not image resizing that distorts border texels.
        atlas.paste(tile.crop((0,0,1,h)).resize((2,h)),(x-2,y));atlas.paste(tile.crop((w-1,0,w,h)).resize((2,h)),(x+w,y))
        atlas.paste(tile.crop((0,0,w,1)).resize((w,2)),(x,y-2));atlas.paste(tile.crop((0,h-1,w,h)).resize((w,2)),(x,y+h))
    for p in r.parts:
        p['material_name']=p['material'];p['material']=list(palette).index(p['material'])
    return atlas
