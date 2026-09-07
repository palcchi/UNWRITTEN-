#!/usr/bin/env python3
"""CPU textured orthographic renderer of exported Bedrock cubes and bone pivots.
These are actual asset renders, never concept art. Does not emulate Bedrock lighting.
"""
import json
import math
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from build_assets import ROOT, RP

def rotate(v):
    x,y,z=np.radians(v); cx,sx=np.cos(x),np.sin(x); cy,sy=np.cos(y),np.sin(y); cz,sz=np.cos(z),np.sin(z)
    return np.array([[cz,-sz,0],[sz,cz,0],[0,0,1]]) @ np.array([[cy,0,sy],[0,1,0],[-sy,0,cy]]) @ np.array([[1,0,0],[0,cx,-sx],[0,sx,cx]])

def channel(keys,time,default):
    if keys is None: return np.array(default,dtype=float)
    items=sorted((float(k),np.array(v,dtype=float)) for k,v in keys.items())
    if time<=items[0][0]: return items[0][1]
    for (a,x),(b,y) in zip(items,items[1:]):
        if a<=time<=b: return x+(y-x)*(time-a)/(b-a)
    return items[-1][1]

def mesh(e,clip=None,time=0):
    g=json.loads((ROOT/e['geometry']).read_text())['minecraft:geometry'][0]
    bones={b['name']:b for b in g['bones']}; anim={}
    if clip:
        all_anim=json.loads((RP/f'animations/unwritten/{e["id"]}.animation.json').read_text())['animations']
        anim=all_anim['animation.unwritten.'+e['id']+'.'+clip]['bones']
    world={}
    def mat(name):
        if name in world: return world[name]
        b=bones[name]; a=anim.get(name,{}); p=np.array(b['pivot']); m=np.eye(4)
        rr=rotate(np.array(b.get('rotation',[0,0,0]))+channel(a.get('rotation'),time,[0,0,0])) @ np.diag(channel(a.get('scale'),time,[1,1,1]))
        m[:3,:3]=rr; m[:3,3]=p-rr@p+channel(a.get('position'),time,[0,0,0])
        if 'parent' in b: m=mat(b['parent'])@m
        world[name]=m; return m
    faces=[]
    idx={'north':[0,1,3,2],'south':[5,4,6,7],'west':[4,0,2,6],'east':[1,5,7,3],'up':[2,3,7,6],'down':[4,5,1,0]}
    for name,b in bones.items():
        m=mat(name)
        for c in b.get('cubes',[]):
            o=np.array(c['origin']); s=np.array(c['size'])
            vs=np.array([o+s*np.array(v) for v in [(0,0,0),(1,0,0),(0,1,0),(1,1,0),(0,0,1),(1,0,1),(0,1,1),(1,1,1)]])
            if 'rotation' in c:
                pivot=np.array(c['pivot']); vs=(rotate(c['rotation'])@(vs-pivot).T).T+pivot
            vs=(m[:3,:3]@vs.T).T+m[:3,3]
            for f,indices in idx.items():
                uv=c['uv'][f]; u,v=uv['uv']; w,h=uv['uv_size']
                faces.append((vs[indices],np.array([[u,v+h],[u+w,v+h],[u+w,v],[u,v]]),f))
    return faces

def render(e,size=320,clip=None,time=0,bounds=None,yaw=-32,pitch=18):
    faces=mesh(e,clip,time); camera=rotate([pitch,0,0])@rotate([0,yaw,0]); points=np.concatenate([f[0]@camera.T for f in faces])
    if bounds is None:
        mins=points.min(0); maxs=points.max(0); center=(mins+maxs)/2; zoom=(size-40)/max((maxs-mins)[:2])
    else: center,zoom=bounds
    texture=np.asarray(Image.open(ROOT/e['texture']).convert('RGBA'))/255
    canvas=np.zeros((size,size,3),float); canvas[:]=np.array([28,33,39])/255
    depth=np.full((size,size),np.inf)
    # Transparent faces composited far-to-near; opaque depth occlusion follows the same order.
    tris=[]
    for vs,uv,f in faces:
        q=(vs@camera.T-center)*zoom
        q[:,0]+=size/2; q[:,1]=size/2-q[:,1]
        for ids in [[0,1,2],[0,2,3]]: tris.append((q[ids],uv[ids],f))
    for p,uv,f in sorted(tris,key=lambda tri:tri[0][:,2].mean(),reverse=True):
        xmin=max(0,int(np.floor(p[:,0].min()))); xmax=min(size-1,int(np.ceil(p[:,0].max())))
        ymin=max(0,int(np.floor(p[:,1].min()))); ymax=min(size-1,int(np.ceil(p[:,1].max())))
        if xmin>xmax or ymin>ymax: continue
        xx,yy=np.meshgrid(np.arange(xmin,xmax+1)+.5,np.arange(ymin,ymax+1)+.5)
        a,b,c=p; den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
        if abs(den)<1e-8: continue
        u=((b[1]-c[1])*(xx-c[0])+(c[0]-b[0])*(yy-c[1]))/den
        v=((c[1]-a[1])*(xx-c[0])+(a[0]-c[0])*(yy-c[1]))/den; w=1-u-v
        zz=u*a[2]+v*b[2]+w*c[2]
        buffer=depth[ymin:ymax+1,xmin:xmax+1]
        mask=(u>=0)&(v>=0)&(w>=0)&(zz<buffer)
        tx=np.clip((u*uv[0,0]+v*uv[1,0]+w*uv[2,0]).astype(int),0,texture.shape[1]-1)
        ty=np.clip((u*uv[0,1]+v*uv[1,1]+w*uv[2,1]).astype(int),0,texture.shape[0]-1)
        tex=texture[ty,tx]; shade={'north':.95,'south':.75,'west':.74,'east':.82,'up':1.08,'down':.65}[f]
        alpha=tex[:,:,3:4]*mask[:,:,None]
        buffer[mask&(tex[:,:,3]>.99)]=zz[mask&(tex[:,:,3]>.99)]
        region=canvas[ymin:ymax+1,xmin:xmax+1]; region[:]=region*(1-alpha)+np.clip(tex[:,:,:3]*shade,0,1)*alpha
    return Image.fromarray((canvas*255).astype('uint8')), (center,zoom)

def main():
    entries=json.loads((ROOT/'catalog/assets.json').read_text())['entries']; index={e['id']:e for e in entries}
    out=ROOT/'docs/previews'; out.mkdir(parents=True,exist_ok=True)
    groups={
      'rank_e':['green_slime','horned_rabbit','forest_wolf','wild_boar','cave_bat','forest_spider','goblin','goblin_scout','lesser_skeleton','mud_crawler','giant_slime','alpha_forest_wolf','goblin_brute','broodmother_spider','golden_slime','white_horned_rabbit'],
      'colossi':['vharos','dullahan','caelum','kael_demon_king','orun','fallen_seraphiel','the_nameless_knight','thalassia','verdant_the_last_father','morrow_anomaly','little_morrow','aion_the_architect'],
      'world':['goblin_archer','kobold_miner','orc_warlord','stone_guardian','chimera','wyvern_king','three_headed_hydra','phoenix','cerberus','kraken','sandworm_queen','siren','original_bow','sacred_tome','wooden_doll','black_door']}
    fontpath='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    font=ImageFont.truetype(fontpath,14); title=ImageFont.truetype(fontpath,26)
    for group,ids in groups.items():
        sheet=Image.new('RGB',(1280,88+((len(ids)+3)//4)*365),(19,23,29)); d=ImageDraw.Draw(sheet)
        d.text((22,14),'UNWRITTEN / '+group.upper(),font=title,fill='#e9dfc7')
        d.text((22,52),'v0.1 first-pass assets | Actual geometry + texture | Individual scale per tile',font=font,fill='#9ca8ab')
        for i,id in enumerate(ids):
            e=index[id]; im,_=render(e); x=i%4*320; y=88+i//4*365; sheet.paste(im,(x,y))
            d.text((x+14,y+321),e['name'],font=font,fill='#e9dfc7')
            d.text((x+14,y+342),f'{e["size"]:g} blocks {e["size_axis"]} / {e["cubes"]} cubes',font=font,fill='#86949c')
        sheet.save(out/(group+'.png'))
    for id,clip in [('green_slime','hop'),('little_morrow','curious_head_tilt'),('the_nameless_knight','slash_3')]:
        e=index[id]; _,bounds=render(e,384); frames=[]
        anim=json.loads((RP/f'animations/unwritten/{id}.animation.json').read_text())['animations']['animation.unwritten.'+id+'.'+clip]
        for time in np.linspace(0,anim['animation_length'],18):
            im,_=render(e,384,clip,float(time),bounds); frames.append(im)
        frames[0].save(out/(id+'.gif'),save_all=True,append_images=frames[1:],duration=80,loop=0)
    print('Rendered three contact sheets and three animation GIFs.')

if __name__=='__main__': main()
