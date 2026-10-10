#!/usr/bin/env python3
"""CachyOS 7: original Aero-style xfwm4 theme in CachyOS slate/teal glass.
Usage: C7_SCALE=1|2 C7_OUT=<themes dir> python3 make_xfwm4_theme.py  -> CachyOS-7-Aero (1x) / CachyOS-7-Aero-xhdpi (2x)"""
import os, shutil
from PIL import Image, ImageDraw
import sys
S=int(os.environ.get("C7_SCALE","2"))  # 1 or 2
T=30*S                   # title bar height incl. top border
B=8*S                    # side/bottom border
R=6*S                    # top corner radius
NAME='CachyOS-7-Aero-xhdpi' if S==2 else 'CachyOS-7-Aero'
OUT=os.path.join(os.environ.get('C7_OUT',os.path.expanduser('~/.themes')),NAME,'xfwm4')
if os.path.isdir(OUT): shutil.rmtree(OUT)
os.makedirs(OUT)
def lerp(a,b,t): return tuple(int(a[i]+(b[i]-a[i])*t) for i in range(len(a)))
GL={'active':  dict(top=(58,92,96),bot=(26,44,48),line=(6,12,14),inner=(0,170,136),hi=(0,204,170)),
    'inactive':dict(top=(70,84,88),bot=(46,56,60),line=(14,20,22),inner=(70,90,92),hi=(110,128,130))}
def vgrad(w,h,top,bot,y0=0,H=None):
    H=H or h; im=Image.new('RGBA',(w,h))
    d=ImageDraw.Draw(im)
    for y in range(h):
        t=(y+y0)/max(1,H-1); c=lerp(top,bot,t)
        # glass sheen: brighter upper 40%
        if t<0.42: c=lerp(c,(170,255,235),0.16*(1-t/0.42))
        d.line([(0,y),(w,y)],fill=c+(255,))
    return im
def save(im,name): im.save(os.path.join(OUT,name+'.png'))
for st,g in GL.items():
    # title pieces
    for n in range(1,6):
        im=vgrad(16,T,g['top'],g['bot']); d=ImageDraw.Draw(im)
        d.rectangle([0,0,15,S-1],fill=g['line']+(255,)); d.rectangle([0,S,15,2*S-1],fill=g['hi']+(255,))
        save(im,f'title-{n}-{st}')
    # top corners (rounded, alpha mask -> xfwm4 shape)
    for side in ('left','right'):
        im=vgrad(B,T,g['top'],g['bot']); d=ImageDraw.Draw(im)
        mask=Image.new('L',(B*4,T*4),0); md=ImageDraw.Draw(mask)
        md.rounded_rectangle([0,0,B*8,T*4+R*8],radius=R*4,fill=255)
        mask=mask.resize((B,T),Image.LANCZOS).point(lambda v:255 if v>127 else 0)
        # outline
        o=Image.new('RGBA',(B,T),g['line']+(255,)); inner=mask.copy()
        er=Image.new('L',(B*4,T*4),0); ed=ImageDraw.Draw(er)
        ed.rounded_rectangle([S*4,S*4,B*8,T*4+R*8],radius=(R-S)*4,fill=255)
        er=er.resize((B,T),Image.LANCZOS).point(lambda v:255 if v>127 else 0)
        base=Image.composite(im,o,er); base.putalpha(mask)
        d=ImageDraw.Draw(base)
        d.line([(B-S,T-S),(B-1,T-S)],fill=g['inner']+(255,),width=S)   # client top edge hint
        if side=='right': base=base.transpose(Image.FLIP_LEFT_RIGHT)
        save(base,f'top-{side}-{st}')
    # side borders
    for side in ('left','right'):
        im=Image.new('RGBA',(B,8),g['bot']+(255,)); d=ImageDraw.Draw(im)
        d.rectangle([0,0,S-1,7],fill=g['line']+(255,)); d.rectangle([S,0,2*S-1,7],fill=lerp(g['bot'],g['hi'],0.5)+(255,))
        d.rectangle([B-S,0,B-1,7],fill=g['inner']+(255,))
        if side=='right': im=im.transpose(Image.FLIP_LEFT_RIGHT)
        save(im,side+'-'+st)
    # bottom
    im=Image.new('RGBA',(8,B),g['bot']+(255,)); d=ImageDraw.Draw(im)
    d.rectangle([0,B-S,7,B-1],fill=g['line']+(255,)); d.rectangle([0,0,7,S-1],fill=g['inner']+(255,))
    save(im,'bottom-'+st)
    for side in ('left','right'):
        im=Image.new('RGBA',(B,B),g['bot']+(255,)); d=ImageDraw.Draw(im)
        d.rectangle([0,0,S-1,B-1],fill=g['line']+(255,)); d.rectangle([0,B-S,B-1,B-1],fill=g['line']+(255,))
        d.rectangle([B-S,0,B-1,S-1],fill=g['inner']+(255,))
        if side=='right': im=im.transpose(Image.FLIP_LEFT_RIGHT)
        save(im,f'bottom-{side}-{st}')

# ---- caption buttons ----
BH=20*S   # visible button height
STY={  # name: (top, mid_hi, mid_lo, bottom, border)
 'norm':  ((112,140,144),(80,106,110),(44,64,68),(66,92,96),(6,14,16)),
 'hover': ((150,255,235),(40,214,190),(0,150,130),(0,204,255),(0,60,52)),
 'press': ((40,120,108),(0,100,84),(0,64,54),(0,110,96),(0,30,26)),
 'close': ((236,170,160),(220,120,105),(196,52,36),(218,96,72),(90,30,24)),
 'closeh':((255,190,175),(246,110,90),(224,30,16),(255,120,80),(110,24,16)),
 'closep':((200,110,100),(170,60,48),(130,20,10),(170,50,30),(70,14,8)),
 'inact': ((96,110,114),(80,94,98),(62,74,78),(72,86,90),(20,28,30)),
}
def button(w,style,glyph,glyph_col=(255,255,255),glyph_out=(38,48,66)):
    top,mh,ml,bot,bd=STY[style]
    im=Image.new('RGBA',(w,T),(0,0,0,0))
    btn=Image.new('RGBA',(w,BH)); d=ImageDraw.Draw(btn)
    for y in range(BH):
        t=y/(BH-1)
        c=lerp(top,mh,t/0.45) if t<0.45 else lerp(ml,bot,(t-0.45)/0.55)
        d.line([(0,y),(w,y)],fill=c+(255,))
    m=Image.new('L',(w*4,BH*4),0); ImageDraw.Draw(m).rounded_rectangle([0,-40,w*4-1,BH*4-1],radius=4*S*4,fill=255)
    m=m.resize((w,BH),Image.LANCZOS)
    ob=Image.new('RGBA',(w,BH),bd+(255,)); inner=Image.new('L',(w*4,BH*4),0)
    ImageDraw.Draw(inner).rounded_rectangle([S*4,-40,w*4-1-S*4,BH*4-1-S*4],radius=3*S*4,fill=255)
    inner=inner.resize((w,BH),Image.LANCZOS)
    full=Image.composite(btn,ob,inner); full.putalpha(m)
    # inner white highlight
    hd=ImageDraw.Draw(full); hd.line([(2*S,S),(w-2*S-1,S)],fill=(255,255,255,140),width=S)
    g=Image.new('RGBA',(w,BH),(0,0,0,0)); gd=ImageDraw.Draw(g)
    cx,cy=w//2,BH//2
    def shape(dd,col,grow):
        if glyph=='min': dd.rectangle([cx-5*S-grow,cy+2*S-grow,cx+4*S+grow,cy+4*S+grow],fill=col)
        elif glyph=='max':
            dd.rectangle([cx-5*S-grow,cy-4*S-grow,cx+5*S+grow,cy+4*S+grow],fill=col)
        elif glyph=='rest':
            dd.rectangle([cx-2*S-grow,cy-5*S-grow,cx+6*S+grow,cy+1*S+grow],fill=col)
            dd.rectangle([cx-6*S-grow,cy-1*S-grow,cx+2*S+grow,cy+5*S+grow],fill=col)
        elif glyph=='close':
            k=4*S
            for a,b in (((cx-k,cy-k),(cx+k,cy+k)),((cx-k,cy+k),(cx+k,cy-k))):
                dd.line([a,b],fill=col,width=int(2.5*S)+2*grow)
    shape(gd,glyph_out+(255,),S)
    shape(gd,glyph_col+(255,),0)
    if glyph=='max':   # hollow centre
        gd.rectangle([cx-3*S,cy-1*S,cx+3*S,cy+2*S],fill=glyph_out+(255,))
        gd.rectangle([cx-3*S+S//1,cy-1*S+S//1,cx+3*S-S//1,cy+2*S-S//1],fill=(0,0,0,0)) if False else None
        cut=Image.new('L',(w,BH),255); ImageDraw.Draw(cut).rectangle([cx-3*S+S,cy-1*S+S,cx+3*S-S,cy+2*S-S],fill=0)
        g.putalpha(Image.composite(g.getchannel('A'),Image.new('L',(w,BH),0),cut))
    if glyph=='rest':
        cut=Image.new('L',(w,BH),255); cd=ImageDraw.Draw(cut)
        cd.rectangle([cx-4*S,cy+1*S,cx,cy+3*S],fill=0)
        g.putalpha(Image.composite(g.getchannel('A'),Image.new('L',(w,BH),0),cut))
    full=Image.alpha_composite(full,g)
    im.paste(full,(0,S),full)   # hangs from just under the top edge, like Win7
    return im
W_MM=26*S; W_CL=45*S
for st in ('active','inactive'):
    for state in ('active','prelight','pressed','inactive'):
        if st=='inactive' and state!='inactive': continue
    pass
def emit(base,w,glyph,closebtn=False):
    if closebtn:
        save(button(w,'close',glyph),f'{base}-active'); save(button(w,'closeh',glyph),f'{base}-prelight')
        save(button(w,'closep',glyph),f'{base}-pressed')
    else:
        save(button(w,'norm',glyph),f'{base}-active'); save(button(w,'hover',glyph),f'{base}-prelight')
        save(button(w,'press',glyph),f'{base}-pressed')
    save(button(w,'inact',glyph,glyph_col=(150,160,162),glyph_out=(30,38,40)),f'{base}-inactive')
emit('hide',W_MM,'min'); emit('maximize',W_MM,'max'); emit('maximize-toggled',W_MM,'rest'); emit('close',W_CL,'close',True)
for state in ('active','inactive','prelight','pressed'):
    save(Image.new('RGBA',(22*S,T),(0,0,0,0)),f'menu-{state}')
open(os.path.join(OUT,'themerc'),'w').write(f"""# {NAME}: original Aero-style xfwm4 theme in CachyOS colours ({S}x).
active_text_color=#ffffff
inactive_text_color=#b8c4c4
title_shadow_active=frame
title_shadow_inactive=false
active_text_shadow_color=#06100f
inactive_text_shadow_color=#ffffff
button_offset={2*S}
button_spacing=0
show_app_icon=true
full_width_title=true
maximized_offset=0
title_horizontal_offset={4*S}
title_vertical_offset_active=0
title_vertical_offset_inactive=0
shadow_delta_height=0
shadow_delta_width=0
shadow_delta_x=0
shadow_delta_y={2*S}
shadow_opacity=45
""")
open(os.path.join(os.path.dirname(OUT),'index.theme'),'w').write("[Desktop Entry]\nType=X-GNOME-Metatheme\nName="+NAME+"\nComment=CachyOS 7 Aero-style xfwm4 theme ("+str(S)+"x)\n")
print('wrote',len(os.listdir(OUT)),'files to',OUT)
