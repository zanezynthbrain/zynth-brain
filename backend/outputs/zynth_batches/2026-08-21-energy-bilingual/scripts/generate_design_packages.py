from __future__ import annotations

import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path('/home/ubuntu/zynth-brain/backend/outputs/zynth_batches/2026-08-21-energy-bilingual')
CONCEPTS = json.loads((ROOT / 'data' / 'concepts.json').read_text(encoding='utf-8'))
OUT = ROOT / 'design_packages'
W, H = 1800, 1080
NAVY, INK, PAPER, PALE, GOLD, CYAN, GREEN, WHITE, MUTED = '#0E3150', '#17212B', '#F7FAFC', '#EAF2F7', '#E2A744', '#5EB6C5', '#2F7B61', '#FFFFFF', '#5D6A75'
FONT_MY = '/usr/share/fonts/truetype/noto/NotoSansMyanmar-Regular.ttf'
BOLD_MY = '/usr/share/fonts/truetype/noto/NotoSansMyanmar-Bold.ttf'
FONT_LAT = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD_LAT = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'


def font(size, bold=False, content=''):
    has_myanmar = any('\u1000' <= ch <= '\u109f' for ch in str(content))
    regular = FONT_MY if has_myanmar else FONT_LAT
    strong = BOLD_MY if has_myanmar else BOLD_LAT
    return ImageFont.truetype(strong if bold else regular, size)


def rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2],16) for i in (0,2,4))


def fit(draw, text, x, y, width, size=23, bold=False, fill=INK, line_gap=6):
    f = font(size, bold, text)
    words, lines, line = text.split(' '), [], ''
    for word in words:
        test = word if not line else line + ' ' + word
        if draw.textbbox((0,0), test, font=f)[2] <= width:
            line = test
        else:
            lines.append(line)
            line = word
    if line: lines.append(line)
    for i, ln in enumerate(lines):
        draw.text((x, y+i*(size+line_gap)), ln, font=f, fill=rgb(fill))
    return y + len(lines)*(size+line_gap)


def rect(draw, xy, fill, outline=None, width=2, radius=0):
    if radius: draw.rounded_rectangle(xy, radius=radius, fill=rgb(fill), outline=rgb(outline) if outline else None, width=width)
    else: draw.rectangle(xy, fill=rgb(fill), outline=rgb(outline) if outline else None, width=width)


def line(draw, pts, fill=NAVY, width=3):
    draw.line(pts, fill=rgb(fill), width=width)


def text(draw, pos, txt, size=22, bold=False, fill=INK, anchor=None):
    draw.text(pos, txt, font=font(size,bold,txt), fill=rgb(fill), anchor=anchor)


def header(draw, c, label):
    rect(draw, (0,0,W,126), NAVY)
    text(draw, (54,28), 'ZYNTH • ENERGY / SOLAR ADOPTION', 20, True, WHITE)
    text(draw, (54,60), f"{c['id']}  {c['title_en']}", 34, True, WHITE)
    text(draw, (54,97), c['title_my'], 20, False, GOLD)
    text(draw, (W-54,36), label, 18, True, GOLD, 'ra')
    text(draw, (W-54,70), 'CONCEPTUAL • NOT FOR CONSTRUCTION', 14, False, WHITE, 'ra')


def footer(draw, status='New ZYNTH concept • proposed/TBC • client approval and supplier engineering required'):
    rect(draw, (0,H-52,W,H), NAVY)
    text(draw, (54,H-38), status, 14, False, WHITE)
    text(draw, (W-54,H-38), 'A3 landscape source: SVG • client preview: PNG', 14, False, WHITE, 'ra')


def panel(draw, box, title, title_my):
    x1,y1,x2,y2 = box
    rect(draw, box, WHITE, '#C5D4DE', 2, 18)
    rect(draw, (x1,y1,x2,y1+48), PALE, None, radius=18)
    text(draw, (x1+20,y1+11), title, 17, True, NAVY)
    text(draw, (x2-20,y1+13), title_my, 15, False, MUTED, 'ra')


def zone_box(draw, xy, label, sub, accent=GOLD):
    x1,y1,x2,y2=xy
    rect(draw, xy, '#F9FCFD', NAVY, 2, 9)
    rect(draw, (x1,y1,x2,y1+8), accent, None, radius=9)
    text(draw, ((x1+x2)//2,y1+28), label, 14, True, NAVY, 'mm')
    text(draw, ((x1+x2)//2,y1+54), sub, 12, False, MUTED, 'mm')


def make_sketch(c, path):
    im = Image.new('RGB',(W,H),rgb(PAPER)); d=ImageDraw.Draw(im)
    header(d,c,'LABELLED SKETCH DESIGN PACKAGE')
    panels=[(54,160,870,565),(930,160,1746,565),(54,612,870,1018),(930,612,1746,1018)]
    for box, ti, tm in zip(panels,['HERO PERSPECTIVE','FRONT / STAGE ELEVATION','PLAN / TOP VIEW','DETAIL VIEW'],['Hero မြင်ကွင်း','ရှေ့မျက်နှာပြင်','အပေါ်မြင်ကွင်း','Detail']): panel(d,box,ti,tm)
    # Hero perspective
    x,y=105,250
    line(d,[(x,500),(750,500)],MUTED,3)
    # sightlines
    for dx in [0,150,300,450]: line(d,[(x+dx,500),(x+325,282)],'#B8CAD5',2)
    # raised demo space
    d.polygon([(300,470),(600,470),(680,405),(380,405)],fill=rgb('#DDECF2'),outline=rgb(NAVY))
    d.polygon([(380,405),(680,405),(680,335),(380,335)],fill=rgb('#FDF0D5'),outline=rgb(NAVY))
    text(d,(530,365),'PROOF / DEMO',16,True,NAVY,'mm')
    # zones foreground
    for bx,lab,sub in [(120,'WELCOME','QR + consent'),(185,'DISCOVER','question cards'),(660,'BOOK','next step')]:
        zone_box(d,(bx,390,bx+105,468),lab,sub,CYAN if lab=='DISCOVER' else GOLD)
    text(d,(120,520),'Open audience sightline • protected technical rear • accessible route',14,False,MUTED)
    # elevation
    x1,y1,x2,y2=panels[1]
    line(d,[(1000,480),(1670,480)],MUTED,3)
    rect(d,(1110,275,1515,475),'#EDF4F7',NAVY,2,10)
    rect(d,(1230,320,1395,475),'#FCE6B4',NAVY,2,6)
    text(d,(1312,370),'HERO\nMESSAGE',16,True,NAVY,'mm')
    for xx in [1060,1570]:
        rect(d,(xx,330,xx+28,475),'#DCEAF0',NAVY,2,3)
        text(d,(xx+14,495),'light',12,False,MUTED,'ma')
    line(d,[(980,515),(1680,515)],GOLD,2)
    text(d,(995,535),'Approx. clear face 6–10m; final dimensions by venue survey and engineer',13,False,MUTED)
    # plan
    x1,y1,x2,y2=panels[2]
    rect(d,(155,710,760,945),'#EDF4F7',NAVY,3,2)
    rect(d,(155,710,760,752),GOLD,None,0)
    text(d,(458,730),'OPEN FRONT / AUDIENCE SIGHTLINE',13,True,NAVY,'mm')
    zone_box(d,(180,775,315,865),'WELCOME','QR / queue',GOLD)
    zone_box(d,(340,775,570,910),'PROOF ZONE','safe demo',CYAN)
    zone_box(d,(600,775,735,865),'CONSULT','booking',GREEN)
    rect(d,(180,890,735,925),'#DCEAF0',NAVY,1,4)
    text(d,(458,908),'TECHNICAL REAR • supplier-engineered only',12,True,NAVY,'mm')
    # arrows
    for xx in [220,340,570,710]:
        line(d,[(xx,760),(xx+30,760)],GOLD,4)
        d.polygon([(xx+30,760),(xx+21,754),(xx+21,766)],fill=rgb(GOLD))
    # Detail
    x1,y1,x2,y2=panels[3]
    rect(d,(1020,720,1380,930),'#EFF6F8',NAVY,3,12)
    rect(d,(1060,765,1340,850),'#FCE6B4',NAVY,2,8)
    text(d,(1200,808),'DEMO\nPLINTH',18,True,NAVY,'mm')
    rect(d,(1450,735,1620,920),'#F9FCFD',NAVY,2,8)
    text(d,(1535,765),'MATERIAL\nKEY',15,True,NAVY,'mm')
    for i,(lab,col) in enumerate([('frame',NAVY),('surface',GOLD),('light',CYAN),('wayfinding',GREEN)]):
        rect(d,(1470,820+i*22,1490,838+i*22),col,None,0)
        text(d,(1500,820+i*22),lab,13,False,MUTED)
    text(d,(1020,955),'Indicative: powder-coated modular frame • recycled surface • low-glare LED • non-slip finish',13,False,MUTED)
    footer(d)
    im.save(path)


def iso_cube(draw, ox, oy, scale=1.0, accent=GOLD):
    # main central structure with simple perspective
    A=(ox,oy+120); B=(ox+300*scale,oy+120); C=(ox+420*scale,oy+55); D=(ox+120*scale,oy+55)
    E=(ox,oy+280*scale); F=(ox+300*scale,oy+280*scale); G=(ox+420*scale,oy+215*scale)
    draw.polygon([A,B,F,E],fill=rgb('#D8E8EF'),outline=rgb(NAVY))
    draw.polygon([B,C,G,F],fill=rgb('#B8D5E1'),outline=rgb(NAVY))
    draw.polygon([D,C,B,A],fill=rgb('#FCE4B1'),outline=rgb(NAVY))
    draw.polygon([(ox+120*scale,oy+150*scale),(ox+280*scale,oy+150*scale),(ox+350*scale,oy+112*scale),(ox+190*scale,oy+112*scale)],fill=rgb(accent),outline=rgb(NAVY))
    return (A,B,C,D,E,F,G)


def make_3d(c, path):
    im = Image.new('RGB',(W,H),rgb(PAPER)); d=ImageDraw.Draw(im)
    header(d,c,'CONCEPTUAL 3D-STYLE DESIGN PACKAGE')
    panels=[(54,160,1120,650),(1150,160,1746,650),(54,690,850,1018),(880,690,1746,1018)]
    for box,ti,tm in zip(panels,['HERO PERSPECTIVE','FRONT ELEVATION','PLAN / TOP VIEW','AUDIENCE + DETAIL'],['Hero မြင်ကွင်း','ရှေ့မျက်နှာပြင်','အပေါ်မြင်ကွင်း','Audience + Detail']): panel(d,box,ti,tm)
    # Hero 3D
    iso_cube(d,220,275,1.6,CYAN)
    text(d,(520,452),'PROOF\nMOMENT',24,True,NAVY,'mm')
    # people
    for px,py in [(175,515),(230,540),(740,525),(810,545)]:
        d.ellipse((px,py,px+20,py+20),fill=rgb(NAVY)); line(d,[(px+10,py+20),(px+10,py+60)],NAVY,6); line(d,[(px+10,py+60),(px,py+80)],NAVY,4); line(d,[(px+10,py+60),(px+20,py+80)],NAVY,4)
    line(d,[(135,600),(980,600)],GOLD,3)
    text(d,(165,615),'Audience sightline is open at the front; rear technical access is controlled.',14,False,MUTED)
    # elevation
    rect(d,(1240,300,1645,540),'#EDF4F7',NAVY,3,10)
    rect(d,(1370,370,1520,540),'#FCE4B1',NAVY,2,4)
    text(d,(1445,440),'MESSAGE',16,True,NAVY,'mm')
    for x in [1290,1595]:
        rect(d,(x,345,x+26,540),'#B8D5E1',NAVY,2,3)
    text(d,(1445,565),'Front elevation • low-glare light wash',13,False,MUTED,'ma')
    # Plan 3D
    rect(d,(145,775,760,950),'#EDF4F7',NAVY,3,2)
    for box, lab, color in [((180,805,315,910),'WELCOME',GOLD),((345,805,565,930),'PROOF',CYAN),((595,805,725,910),'BOOK',GREEN)]:
        zone_box(d,box,lab,'zone',color)
    text(d,(453,970),'Approx. audience flow: entry → proof → consultation → exit',13,False,MUTED,'ma')
    # detail
    rect(d,(970,770,1210,940),'#F9FCFD',NAVY,2,12)
    rect(d,(1005,815,1175,880),'#FCE4B1',NAVY,2,6)
    text(d,(1090,842),'MATERIAL',14,True,NAVY,'mm')
    line(d,[(1240,800),(1660,800)],GOLD,4)
    text(d,(1240,820),'Surface: low-reflective, cleanable, non-slip',14,False,INK)
    line(d,[(1240,865),(1660,865)],CYAN,4)
    text(d,(1240,885),'Light: directional / low-glare / engineer-reviewed',14,False,INK)
    line(d,[(1240,930),(1660,930)],GREEN,4)
    text(d,(1240,950),'Furniture: modular, accessible, reconfigurable',14,False,INK)
    footer(d)
    im.save(path)


def svg_for_physical(c, kind):
    title = 'Labelled Sketch Design Package' if kind == 'sketch' else 'Conceptual 3D-Style Design Package'
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="1080" viewBox="0 0 1800 1080">
<style>text{{font-family:'DejaVu Sans','Noto Sans Myanmar','Arial',sans-serif}}.h{{fill:#0E3150}}.p{{fill:#F7FAFC}}.l{{fill:#EAF2F7;stroke:#0E3150;stroke-width:3}}.g{{fill:#E2A744}}.c{{fill:#5EB6C5}}.m{{fill:#5D6A75}}</style>
<rect width="1800" height="1080" class="p"/><rect width="1800" height="126" class="h"/>
<text x="54" y="55" fill="white" font-size="20" font-weight="700">ZYNTH • ENERGY / SOLAR ADOPTION</text><text x="54" y="94" fill="white" font-size="34" font-weight="700">{c['id']} {c['title_en']}</text><text x="54" y="118" fill="#E2A744" font-size="20">{c['title_my']}</text><text x="1746" y="54" fill="#E2A744" font-size="18" text-anchor="end" font-weight="700">{title.upper()}</text>
<g transform="translate(54 160)"><rect width="816" height="405" rx="18" class="l"/><text x="22" y="31" font-size="18" font-weight="700" class="h">HERO PERSPECTIVE / Hero မြင်ကွင်း</text><polygon points="250,310 570,310 650,230 330,230" fill="#DDECF2" stroke="#0E3150" stroke-width="3"/><polygon points="330,230 650,230 650,160 330,160" fill="#FCE4B1" stroke="#0E3150" stroke-width="3"/><text x="490" y="200" class="h" font-size="18" font-weight="700" text-anchor="middle">PROOF / DEMO</text><text x="40" y="370" class="m" font-size="15">Open sightline • controlled technical rear • accessible route</text></g>
<g transform="translate(930 160)"><rect width="816" height="405" rx="18" class="l"/><text x="22" y="31" font-size="18" font-weight="700" class="h">FRONT / STAGE ELEVATION / ရှေ့မျက်နှာပြင်</text><rect x="180" y="115" width="405" height="210" rx="10" fill="#EDF4F7" stroke="#0E3150" stroke-width="3"/><rect x="300" y="160" width="165" height="165" rx="5" class="g"/><text x="383" y="245" class="h" font-size="17" font-weight="700" text-anchor="middle">HERO MESSAGE</text><text x="408" y="365" class="m" font-size="14" text-anchor="middle">Approx. dimensions • venue survey required</text></g>
<g transform="translate(54 612)"><rect width="816" height="406" rx="18" class="l"/><text x="22" y="31" font-size="18" font-weight="700" class="h">PLAN / TOP VIEW / အပေါ်မြင်ကွင်း</text><rect x="100" y="90" width="610" height="240" fill="#EDF4F7" stroke="#0E3150" stroke-width="3"/><rect x="125" y="145" width="135" height="95" fill="#FCE4B1" stroke="#0E3150" stroke-width="2"/><rect x="295" y="125" width="220" height="130" fill="#D8E8EF" stroke="#0E3150" stroke-width="2"/><rect x="550" y="145" width="125" height="95" fill="#DCEEDF" stroke="#0E3150" stroke-width="2"/><text x="192" y="196" class="h" font-size="15" text-anchor="middle">WELCOME</text><text x="405" y="196" class="h" font-size="15" text-anchor="middle">PROOF ZONE</text><text x="612" y="196" class="h" font-size="15" text-anchor="middle">BOOK</text><text x="405" y="370" class="m" font-size="14" text-anchor="middle">Audience flow: entry → proof → consultation → exit</text></g>
<g transform="translate(930 612)"><rect width="816" height="406" rx="18" class="l"/><text x="22" y="31" font-size="18" font-weight="700" class="h">DETAIL VIEW / Detail</text><rect x="115" y="110" width="350" height="205" rx="12" fill="#EFF6F8" stroke="#0E3150" stroke-width="3"/><rect x="155" y="155" width="270" height="90" rx="8" class="g"/><text x="290" y="205" class="h" font-size="19" font-weight="700" text-anchor="middle">DEMO PLINTH</text><text x="500" y="140" class="h" font-size="15" font-weight="700">MATERIAL / LIGHT / WAYFINDING</text><text x="500" y="180" class="m" font-size="14">Modular frame • recycled surface • low-glare LED</text><text x="500" y="215" class="m" font-size="14">Non-slip finish • supplier engineering and samples TBC</text></g>
<rect y="1028" width="1800" height="52" class="h"/><text x="54" y="1061" fill="white" font-size="14">New ZYNTH concept • proposed/TBC • client approval and supplier engineering required</text><text x="1746" y="1061" fill="white" font-size="14" text-anchor="end">A3 source: SVG • client preview: PNG</text></svg>'''


def make_ui(c, path):
    im=Image.new('RGB',(W,H),rgb(PAPER));d=ImageDraw.Draw(im);header(d,c,'CAMPAIGN UI / EXPERIENCE STORYBOARD')
    # Flow line
    steps=[('01','ENTRY','Promise'),('02','PRIORITY','What must run?'),('03','CONTEXT','Pattern'),('04','CONSENT','Permission'),('05','BOOK','Next step')]
    x=70
    for i,(n,lab,sub) in enumerate(steps):
        rect(d,(x,205,x+300,720),WHITE,NAVY,2,22)
        rect(d,(x,205,x+300,255),NAVY,None,0)
        text(d,(x+25,220),n+'  '+lab,17,True,WHITE)
        # phone screen
        rect(d,(x+55,285,x+245,615),'#EEF5F8',NAVY,3,22)
        rect(d,(x+75,325,x+225,365),GOLD,None,8)
        text(d,(x+150,345),lab,14,True,NAVY,'mm')
        if i==0:
            text(d,(x+150,420),'Tell us\nwhat must\nkeep running.',16,True,NAVY,'mm')
        elif i==1:
            for j,a in enumerate(['Payment','Light','Cold','Tools']):
                rect(d,(x+75,395+j*38,x+225,425+j*38),'#FFFFFF',CYAN,1,7);text(d,(x+150,410+j*38),a,12,False,INK,'mm')
        elif i==2:
            text(d,(x+150,420),'When does\nthe work\npause?',16,True,NAVY,'mm')
        elif i==3:
            text(d,(x+150,420),'Your data,\nyour choice.',16,True,NAVY,'mm')
        else:
            rect(d,(x+75,435,x+225,485),GREEN,None,10);text(d,(x+150,460),'BOOK',14,True,WHITE,'mm')
            text(d,(x+150,515),'Subject to\nreview.',13,False,MUTED,'mm')
        text(d,(x+150,650),sub,14,False,MUTED,'mm')
        if i<4:
            line(d,[(x+305,462),(x+345,462)],GOLD,5);d.polygon([(x+345,462),(x+332,454),(x+332,470)],fill=rgb(GOLD))
        x += 350
    # bottom spec
    panel(d,(70,770,1730,1000),'EXPERIENCE / DATA / ACCESSIBILITY','အတွေ့အကြုံ / Data / Accessibility')
    cols=[('UX','Mobile-first; 5-step decision path; no engineering promise.'),('COPY','Bilingual plain language; proof questions before product claims.'),('CONSENT','Clear opt-in, notice, opt-out and client-owned follow-up.'),('ACCESS','Contrast, tap targets, subtitles, readable Myanmar Unicode.'),('ANALYTICS','View, progress, submit, booking and opt-out only after approval.')]
    cx=105
    for h,b in cols:
        text(d,(cx,855),h,16,True,NAVY)
        fit(d,b,cx,885,285,14,False,MUTED)
        cx += 325
    footer(d,'New ZYNTH UI concept • not a working application • privacy, build and analytics specification TBC')
    im.save(path)


def svg_for_ui(c):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="1080" viewBox="0 0 1800 1080"><rect width="1800" height="1080" fill="#F7FAFC"/><rect width="1800" height="126" fill="#0E3150"/><text x="54" y="55" font-family="Noto Sans Myanmar" fill="white" font-size="20" font-weight="700">ZYNTH • ENERGY / SOLAR ADOPTION</text><text x="54" y="94" font-family="Noto Sans Myanmar" fill="white" font-size="34" font-weight="700">{c['id']} {c['title_en']}</text><text x="54" y="118" font-family="Noto Sans Myanmar" fill="#E2A744" font-size="20">{c['title_my']}</text><text x="1746" y="54" font-family="Noto Sans Myanmar" fill="#E2A744" font-size="18" text-anchor="end" font-weight="700">CAMPAIGN UI / EXPERIENCE STORYBOARD</text>{''.join(f'<g transform="translate({70+i*350} 205)"><rect width="300" height="515" rx="22" fill="white" stroke="#0E3150" stroke-width="2"/><rect width="300" height="50" fill="#0E3150"/><text x="25" y="32" font-family="Noto Sans Myanmar" fill="white" font-size="17" font-weight="700">0{i+1} {lab}</text><rect x="55" y="80" width="190" height="330" rx="22" fill="#EEF5F8" stroke="#0E3150" stroke-width="3"/><rect x="75" y="120" width="150" height="40" rx="8" fill="#E2A744"/><text x="150" y="146" font-family="Noto Sans Myanmar" fill="#0E3150" font-size="14" text-anchor="middle" font-weight="700">{lab}</text><text x="150" y="450" font-family="Noto Sans Myanmar" fill="#5D6A75" font-size="14" text-anchor="middle">{sub}</text></g>' for i,(lab,sub) in enumerate([('ENTRY','Promise'),('PRIORITY','What must run?'),('CONTEXT','Pattern'),('CONSENT','Permission'),('BOOK','Next step')]))}<rect y="1028" width="1800" height="52" fill="#0E3150"/><text x="54" y="1061" font-family="Noto Sans Myanmar" fill="white" font-size="14">New ZYNTH UI concept • not a working application • privacy, build and analytics specification TBC</text></svg>'''


def main():
    records=[]
    for c in CONCEPTS:
        folder=OUT/f"{c['id']}_{c['slug']}";folder.mkdir(parents=True,exist_ok=True)
        if c['mode']=='physical':
            for kind, maker in [('sketch',make_sketch),('3d',make_3d)]:
                png=folder/f"{c['id']}_{c['slug']}_{kind}.png";svg=folder/f"{c['id']}_{c['slug']}_{kind}.svg"
                maker(c,png);svg.write_text(svg_for_physical(c,kind),encoding='utf-8');records.append((c['id'],c['slug'],kind,png.name,svg.name))
        else:
            png=folder/f"{c['id']}_{c['slug']}_ui_experience_storyboard.png";svg=folder/f"{c['id']}_{c['slug']}_ui_experience_storyboard.svg"
            make_ui(c,png);svg.write_text(svg_for_ui(c),encoding='utf-8');records.append((c['id'],c['slug'],'ui_storyboard',png.name,svg.name))
    readme=['# Design Package Manifest','', 'All visuals are original ZYNTH planning concepts. They are **not** construction drawings, engineering schematics, electrical load plans, supplier quotations, venue approvals, permits or technical performance evidence. Client approval, venue survey, supplier engineering, safety review and rights clearance are required before any production.', '', '| Concept | Package | Client preview | Editable source |', '|---|---|---|---|']
    for row in records: readme.append('| ' + ' | '.join(row) + ' |')
    (OUT/'README.md').write_text('\n'.join(readme)+'\n',encoding='utf-8')
    print(f'Created {len(records)} design packages, with PNG and SVG assets.')

if __name__=='__main__': main()
