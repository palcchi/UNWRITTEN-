"""Render exported, textured models, never concept-art substitutes."""
import json
from PIL import Image, ImageDraw, ImageFont
from build_assets import ROOT
from render_previews import render

def main():
    entries={e['id']:e for e in json.loads((ROOT/'catalog/assets.json').read_text())['entries']}
    ids=['caelum','aion','aion_the_architect']
    sheet=Image.new('RGB',(1260,470),(28,33,39))
    d=ImageDraw.Draw(sheet)
    font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18)
    for i,id in enumerate(ids):
        im,_=render(entries[id],420)
        sheet.paste(im,(i*420,0))
        d.text((i*420+20,435),entries[id]['name'],font=font,fill='#e2d8c5')
    sheet.save(ROOT/'docs/previews/player_colossi_review.png')

if __name__=='__main__':main()
