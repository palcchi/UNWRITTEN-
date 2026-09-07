#!/usr/bin/env python3
"""Art-review sheets from exported meshes, not generated concept imagery."""
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from build_assets import ROOT, RP
from build_colossi import BUILDERS
from render_previews import render

def main():
    entries={e['id']:e for e in json.loads((ROOT/'catalog/assets.json').read_text())['entries']}
    out=ROOT/'docs/previews';out.mkdir(exist_ok=True)
    font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    small=ImageFont.truetype(font,15); title=ImageFont.truetype(font,25)
    groups={
      'aion_evolution':['aion_prologue','aion','aion_the_architect'],
      'colossi_bespoke':['vharos','dullahan','caelum','kael_demon_king','orun','fallen_seraphiel','the_nameless_knight','thalassia','verdant_giant','verdant_the_last_father','morrow_anomaly','true_morrow'],
      'colossi_support':['kael_hunter','sir_seraphiel','elara_spirit','dullahan_horse'],
    }
    for name,ids in groups.items():
        cols=3 if name!='colossi_support' else 4; tile=420;rows=(len(ids)+cols-1)//cols
        sheet=Image.new('RGB',(cols*tile,90+rows*(tile+56)),(18,22,28));d=ImageDraw.Draw(sheet)
        d.text((24,15),'UNWRITTEN / '+name.replace('_',' ').upper(),font=title,fill='#d7dcdb')
        d.text((24,54),'Bespoke art pass 02 | Actual textured geometry | Tiles use individual scale',font=small,fill='#99a8b5')
        for i,id in enumerate(ids):
            e=entries[id];im,_=render(e,tile);x=i%cols*tile;y=90+i//cols*(tile+56);sheet.paste(im,(x,y))
            d.text((x+15,y+tile+5),e['name'],font=small,fill='#e5dbbc')
            d.text((x+15,y+tile+28),f'{e["cubes"]} cubes / {e["rig_bones"]} bones / {e["texture_width"]}x{e["texture_height"]}',font=small,fill='#8d9eae')
        sheet.save(out/(name+'.png'))
    for id in ['little_morrow','vharos']:
        e=entries[id];sheet=Image.new('RGB',(1440,560),(18,22,28));d=ImageDraw.Draw(sheet)
        d.text((24,15),e['name'].upper()+' / MODEL STUDY',font=title,fill='#d7dcdb')
        for i,yaw in enumerate([-32,45,-90]):
            im,_=render(e,480,yaw=yaw,pitch=12);sheet.paste(im,(i*480,70))
        sheet.save(out/(id+'_study.png'))
    for id,clip in [('vharos','wake_up_roar'),('little_morrow','curious_head_tilt'),('aion_prologue','presence_pulse'),('the_nameless_knight','slash_3')]:
        e=entries[id];_,bounds=render(e,420)
        duration=json.loads((RP/f'animations/unwritten/{id}.animation.json').read_text())['animations']['animation.unwritten.'+id+'.'+clip]['animation_length']
        frames=[render(e,420,clip,float(t),bounds)[0] for t in np.linspace(0,duration,20)]
        frames[0].save(out/(id+'_bespoke.gif'),save_all=True,append_images=frames[1:],duration=max(40,int(duration/20*1000)),loop=0)
    print('Bespoke contact sheets, studies and four animated previews rendered.')

if __name__=='__main__':main()
