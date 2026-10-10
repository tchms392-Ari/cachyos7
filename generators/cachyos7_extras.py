#!/usr/bin/env python3
"""CachyOS 7 extras: sound theme, shortcut cheat sheet, plymouth theme, login background, previews.
Used by build_cachyos7.py; can also be run alone:  python3 cachyos7_extras.py [sounds|sheet|plymouth|login|all]"""
import os, sys, re, shutil, subprocess, html
HOME=os.path.expanduser('~'); D=f'{HOME}/.local/share/cachyos7'; PKG=f'{HOME}/CachyOS7'
WALL=f'{HOME}/Pictures/Wallpapers/cachyos7.png'; LOGO=f'{D}/cachyos-logo.svg'
SLATE=(27,42,46); CHAR=(13,21,23); HI=(46,68,72); TEAL=(0,170,136); MINT=(0,255,204); CYAN=(0,204,255); TXT=(230,242,239)
FR='/usr/share/fonts/TTF/OpenSans-Regular.ttf'; FB='/usr/share/fonts/TTF/OpenSans-Bold.ttf'; FM='/usr/share/fonts/noto/NotoSansMono-Regular.ttf'
def sh(*a): return subprocess.run(a,capture_output=True,text=True)
def logo(size):
    from PIL import Image
    out=f'{D}/cachyos-logo-{size}.png'
    if not os.path.exists(out): sh('rsvg-convert','-w',str(size),'-h',str(size),'--keep-aspect-ratio',LOGO,'-o',out)
    return Image.open(out).convert('RGBA')

# ---------------- 1. sound theme ----------------
def make_sounds():
    """CachyOS-7 sound theme: the original Win7-Original chimes + new synthesized ones, as .oga. No Microsoft audio."""
    import numpy as np, wave
    src=f'{HOME}/.local/share/sounds/Win7-Original/stereo'; base=f'{HOME}/.local/share/sounds/CachyOS-7'; st=f'{base}/stereo'
    os.makedirs(st,exist_ok=True); SR=44100
    open(f'{base}/index.theme','w').write('[Sound Theme]\nName=CachyOS-7\nComment=CachyOS 7 original soft chimes (synthesized, no Microsoft audio)\nInherits=Win7-Original;freedesktop\nDirectories=stereo\n\n[stereo]\nOutputProfile=stereo\n')
    def chime(notes,dur=0.30,gap=0.09,vol=0.28,decay=5.0,bright=0.25):
        total=int(SR*(gap*(len(notes)-1)+dur+0.25)); out=np.zeros(total)
        for i,f in enumerate(notes):
            t=np.arange(int(SR*(dur+0.25)))/SR; env=np.exp(-decay*t)*np.minimum(1,t/0.006)
            w=(np.sin(2*np.pi*f*t)+bright*np.sin(2*np.pi*2*f*t)+0.08*np.sin(2*np.pi*3*f*t))*env
            s=int(SR*gap*i); out[s:s+len(w)]+=w[:total-s]
        out=out/max(1e-9,np.abs(out).max())*vol; return out
    new={  # event: (notes Hz, kwargs)
        'desktop-logout':([783.99,659.25,523.25,392.0],{}),
        'dialog-error':([392.0,311.13],dict(gap=0.12,decay=6)),
        'dialog-warning':([587.33,587.33],dict(gap=0.16,decay=7)),
        'dialog-information':([880.0,1174.66],dict(decay=6)),
        'message-new-instant':([1046.5,1318.5],dict(gap=0.07,decay=7)),
        'complete':([523.25,659.25,783.99,1046.5],dict(gap=0.07)),
        'device-added':([523.25,783.99],dict(gap=0.1)),
        'device-removed':([783.99,523.25],dict(gap=0.1)),
        'window-attention':([987.77,987.77],dict(gap=0.2,decay=8,vol=0.22)),
        'trash-empty':([698.46,587.33,466.16],dict(gap=0.05,decay=9,bright=0.6)),
        'audio-volume-change':([1318.5],dict(dur=0.12,decay=14,vol=0.22)),
        'bell':([1567.98],dict(dur=0.18,decay=10,vol=0.22)),
    }
    def to_oga(name,samples):
        wav=f'{st}/{name}.wav.tmp'
        st2=np.stack([samples,samples],1); pcm=(st2*32767).astype('<i2')
        with wave.open(wav,'wb') as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
        r=sh('ffmpeg','-y','-loglevel','error','-f','wav','-i',wav,'-c:a','libvorbis','-q:a','5',f'{st}/{name}.oga')
        if r.returncode: os.replace(wav,f'{st}/{name}.wav')
        else: os.remove(wav)
    # keep the existing original login chime (and others) by converting them
    if os.path.isfile(f'{src}/desktop-login.wav'):
        sh('ffmpeg','-y','-loglevel','error','-i',f'{src}/desktop-login.wav','-c:a','libvorbis','-q:a','5',f'{st}/desktop-login.oga')
    for name,(notes,kw) in new.items(): to_oga(name,chime(notes,**kw))
    for alias,target in (('message','message-new-instant'),('suspend-error','dialog-error'),('service-login','desktop-login'),('service-logout','desktop-logout')):
        p=f'{st}/{alias}.oga'
        if os.path.lexists(p): os.remove(p)
        os.symlink(f'{target}.oga',p)
    return base

# ---------------- 5. shortcut cheat sheet ----------------
FRIENDLY={'xfce4-popup-whiskermenu':'Open the Start menu','thunar':'Open Files (Thunar)','xflock4':'Lock the screen',
 'xfce4-taskmanager':'Task Manager','xfce4-appfinder -c':'Run…','xfce4-appfinder --collapsed':'Run…','xfce4-appfinder':'App finder',
 'xfce4-display-settings --minimal':'Display / projector settings','xfce4-screenshooter':'Screenshot (full screen)',
 'xfce4-screenshooter -w':'Screenshot (window)','xfce4-screenshooter -r':'Screenshot (region)',
 'exo-open --launch TerminalEmulator':'Open a terminal','xfce4-session-logout':'Log out / Shut down','xfdesktop --menu':'Desktop menu',
 'xkill':'Force-close a window (click it)','show_desktop_key':'Show desktop','cycle_windows_key':'Switch windows (with previews)',
 'cycle_reverse_windows_key':'Switch windows (backwards)','switch_window_key':'Cycle windows of the same app',
 'maximize_window_key':'Maximize','hide_window_key':'Minimize','close_window_key':'Close window','fullscreen_key':'Fullscreen',
 'above_key':'Keep window on top','popup_menu_key':'Window menu','move_window_key':'Move window (keyboard)',
 'resize_window_key':'Resize window (keyboard)','tile_left_key':'Snap left half','tile_right_key':'Snap right half',
 'tile_up_key':'Snap top half','tile_down_key':'Snap bottom half','tile_up_left_key':'Snap top-left quarter',
 'tile_up_right_key':'Snap top-right quarter','tile_down_left_key':'Snap bottom-left quarter','tile_down_right_key':'Snap bottom-right quarter'}
SKIP=re.compile(r'workspace|^(up|down|left|right|cancel)_key$|raise_window|lower_window|stick_window|orca|exo-open --launch (WebBrowser|MailReader)')
def pretty(k):
    k=k.replace('<Primary>','Ctrl+').replace('<Shift>','Shift+').replace('<Alt>','Alt+').replace('<Super>','Win+')
    k={'Super_L':'Win (tap)'}.get(k,k)
    for a,b in (('Page_Up','PgUp'),('Page_Down','PgDn'),('KP_','Keypad '),('Escape','Esc'),('Print','PrtSc'),('Next','PgDn')): k=k.replace(a,b)
    return re.sub(r'\+([a-z])$',lambda m:'+'+m.group(1).upper(),k)
def read_shortcuts():
    out=sh('xfconf-query','-c','xfce4-keyboard-shortcuts','-lv').stdout
    if not out.strip():   # no xfconfd (e.g. from GNOME): read the XML
        x=open(f'{HOME}/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-keyboard-shortcuts.xml').read()
        rows=[]
        for sec in ('commands','xfwm4'):
            m=re.search(r'<property name="%s".*?<property name="custom"[^>]*>(.*?)\n    </property>'%sec,x,re.S)
            if m: rows+= [(sec,html.unescape(a),html.unescape(b)) for a,b in re.findall(r'<property name="([^"]+)" type="string" value="([^"]*)"',m.group(1))]
    else:
        rows=[]
        for line in out.splitlines():
            m=re.match(r'/(commands|xfwm4)/custom/(\S+)\s+(.*)$',line)
            if m and '/' not in m.group(2) and m.group(2)!='override': rows.append((m.group(1),m.group(2),m.group(3).strip()))
    groups={'Start & apps':[],'Windows':[],'Snapping':[],'Screenshots & system':[]}
    seen=set()
    for sec,key,act in rows:
        if SKIP.search(act) or act not in FRIENDLY: continue
        label=FRIENDLY[act]; pk=pretty(key)
        if (pk,label) in seen or pk.startswith('XF86') or pk=='HomePage': continue
        seen.add((pk,label))
        g=('Snapping' if 'Snap' in label else 'Screenshots & system' if ('Screenshot' in label or label in ('Log out / Shut down','Force-close a window (click it)','Display / projector settings','Lock the screen','Task Manager','Desktop menu'))
           else 'Windows' if sec=='xfwm4' else 'Start & apps')
        groups[g].append((pk,label))
    # merge keys with the same action (e.g. Win+Home / Win+Keypad Home)
    for g,items in groups.items():
        m={}
        for k,l in items: m.setdefault(l,[]).append(k)
        groups[g]=[(' / '.join(sorted(ks,key=lambda s:('Keypad' in s,s))),l) for l,ks in m.items()]
    groups['Mouse']=[('Double-click title bar','Maximize / restore'),('Drag window to screen edge','Snap half / maximize (top edge)'),
                     ('Win + drag','Move window from anywhere'),('Middle-click taskbar icon','Open a new window of that app'),
                     ('Hover taskbar icon','Window previews'),('Far-right taskbar strip','Show desktop')]
    return groups
def make_shortcut_sheet():
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    groups=read_shortcuts(); os.makedirs(PKG,exist_ok=True)
    # HTML
    css=('body{background:#0d1517;color:#e6f2ef;font-family:"Open Sans",sans-serif;margin:40px}h1{color:#00ffcc;font-weight:600}'
         'h2{color:#00ccff;border-bottom:1px solid #00aa88;padding-bottom:4px}.g{display:inline-block;vertical-align:top;width:46%;margin:0 2% 24px 0;'
         'background:#1b2a2e;border:1px solid #2e4448;border-radius:8px;padding:12px 18px}td{padding:4px 10px}kbd{background:#2e4448;border:1px solid #00aa88;'
         'border-radius:4px;padding:2px 8px;font-family:"Noto Sans Mono",monospace;color:#fff;white-space:nowrap}')
    h=[f'<!doctype html><meta charset="utf-8"><title>CachyOS 7 Shortcuts</title><style>{css}</style><h1>CachyOS 7 Shortcuts</h1>']
    for g,items in groups.items():
        if items: h.append(f'<div class="g"><h2>{g}</h2><table>'+''.join(f'<tr><td><kbd>{html.escape(k)}</kbd></td><td>{html.escape(l)}</td></tr>' for k,l in items)+'</table></div>')
    html_path=f'{D}/CachyOS7-Shortcuts.html'; open(html_path,'w').write('\n'.join(h)+'\n<p style="color:#7f9a96">Generated from your live Xfce shortcut settings by build_cachyos7.py.</p>\n')
    # PNG (2400 wide = readable on the 4K TV at 2x)
    W=2400; fT=ImageFont.truetype(FB,64); fH=ImageFont.truetype(FB,38); fK=ImageFont.truetype(FM,28); fL=ImageFont.truetype(FR,30)
    cols=[[],[]]; hts=[0,0]
    for g,items in groups.items():
        if not items: continue
        hh=90+len(items)*54; i=0 if hts[0]<=hts[1] else 1; cols[i].append((g,items)); hts[i]+=hh+30
    H=220+max(hts)+60
    im=Image.new('RGB',(W,H),CHAR); d=ImageDraw.Draw(im)
    for y in range(H): d.line([(0,y),(W,y)],fill=tuple(int(CHAR[c]+(SLATE[c]-CHAR[c])*(1-y/H)) for c in range(3)))
    glow=Image.new('L',(W,H),0); ImageDraw.Draw(glow).ellipse([W-900,-500,W+300,500],fill=90); glow=glow.filter(ImageFilter.GaussianBlur(160))
    im=Image.composite(Image.new('RGB',(W,H),TEAL),im,glow); d=ImageDraw.Draw(im)
    lg=logo(120); im.paste(lg,(70,50),lg); d.text((220,62),'CachyOS 7 Shortcuts',font=fT,fill=MINT)
    d.text((222,140),'Windows 7 layout · CachyOS branding · generated from your live settings',font=fL,fill=(127,154,150))
    for ci,col in enumerate(cols):
        x=70+ci*(W//2); y=220
        for g,items in col:
            hh=90+len(items)*54; d.rounded_rectangle([x,y,x+W//2-140,y+hh],radius=18,fill=SLATE,outline=HI,width=2)
            d.text((x+28,y+18),g,font=fH,fill=CYAN); d.line([(x+28,y+72),(x+W//2-170,y+72)],fill=TEAL,width=2)
            yy=y+90
            for k,l in items:
                tw=d.textlength(k,font=fK); d.rounded_rectangle([x+28,yy,x+28+tw+28,yy+42],radius=8,fill=HI,outline=TEAL,width=2)
                d.text((x+42,yy+4),k,font=fK,fill=(255,255,255)); d.text((x+28+max(tw+50,480),yy+2),l,font=fL,fill=TXT); yy+=54
            y+=hh+30
    png=f'{HOME}/Pictures/cachyos7_shortcuts.png'; im.save(png); shutil.copy(png,f'{D}/CachyOS7-Shortcuts.png')
    # desktop launcher
    ic=f'{D}/shortcuts-icon.png'
    I=Image.new('RGBA',(256,256),(0,0,0,0)); di=ImageDraw.Draw(I); di.rounded_rectangle([16,40,240,216],radius=26,fill=SLATE+(255,),outline=TEAL+(255,),width=8)
    for r,row in enumerate((5,5,4)):
        for c in range(row): di.rounded_rectangle([40+c*36+r*10,66+r*44,68+c*36+r*10,96+r*44],radius=5,fill=HI+(255,),outline=MINT+(255,),width=2)
    I.save(ic)
    p=f'{HOME}/Desktop/cachyos7-shortcuts.desktop'
    open(p,'w').write(f'[Desktop Entry]\nType=Application\nName=CachyOS 7 Shortcuts\nComment=Keyboard and mouse shortcuts for CachyOS 7\nExec=xdg-open {html_path}\nIcon={ic}\nTerminal=false\nX-CachyOS7=true\n')
    os.chmod(p,0o755)
    sh('gio','set','-t','string',p,'metadata::xfce-exe-checksum',sh('sha256sum',p).stdout.split()[0]); sh('gio','set',p,'metadata::trusted','true')
    return png

# ---------------- 3. plymouth theme ----------------
PLY_SCRIPT='''# CachyOS 7 boot splash (original). Logo centred on dark slate with teal glow, 4 orbiting teal dots.
Window.SetBackgroundTopColor(0.106, 0.165, 0.180);
Window.SetBackgroundBottomColor(0.051, 0.082, 0.090);
sw = Window.GetWidth(); shh = Window.GetHeight();
scale = Math.Min(sw / 1920, shh / 1080); if (scale < 0.5) scale = 0.5;
glow_img = Image("glow.png"); glow_img = glow_img.Scale(glow_img.GetWidth() * scale, glow_img.GetHeight() * scale);
glow = Sprite(glow_img); glow.SetX(sw / 2 - glow_img.GetWidth() / 2); glow.SetY(shh * 0.42 - glow_img.GetHeight() / 2); glow.SetZ(1);
logo_img = Image("logo.png"); logo_img = logo_img.Scale(logo_img.GetWidth() * scale, logo_img.GetHeight() * scale);
logo = Sprite(logo_img); logo.SetX(sw / 2 - logo_img.GetWidth() / 2); logo.SetY(shh * 0.42 - logo_img.GetHeight() / 2); logo.SetZ(2);
title_img = Image("title.png"); title_img = title_img.Scale(title_img.GetWidth() * scale, title_img.GetHeight() * scale);
title = Sprite(title_img); title.SetX(sw / 2 - title_img.GetWidth() / 2); title.SetY(shh * 0.62); title.SetZ(2);
dot_img = Image("dot.png"); dot_img = dot_img.Scale(dot_img.GetWidth() * scale, dot_img.GetHeight() * scale);
for (i = 0; i < 4; i++) { dots[i] = Sprite(dot_img); dots[i].SetZ(3); }
cx = sw / 2; cy = shh * 0.78; r = 34 * scale; t = 0;
fun refresh_callback () {
  t++;
  for (i = 0; i < 4; i++) {
    a = t * 0.07 - i * 0.55;
    dots[i].SetX(cx + Math.Cos(a) * r - dot_img.GetWidth() / 2);
    dots[i].SetY(cy + Math.Sin(a) * r - dot_img.GetHeight() / 2);
    dots[i].SetOpacity(1 - i * 0.22);
  }
  glow.SetOpacity(0.75 + 0.25 * Math.Sin(t * 0.04));
}
Plymouth.SetRefreshFunction(refresh_callback);
# password prompt (disk encryption)
fun display_password_callback (prompt, bullets) {
  pr = Image.Text(prompt, 0.9, 0.95, 0.94); p_s = Sprite(pr); p_s.SetPosition(sw / 2 - pr.GetWidth() / 2, shh * 0.86, 10);
  b = ""; for (i = 0; i < bullets; i++) b += "•";
  bi = Image.Text(b, 0, 1, 0.8); global.b_s = Sprite(bi); global.b_s.SetPosition(sw / 2 - bi.GetWidth() / 2, shh * 0.86 + 40, 10);
  global.p_s = p_s;
}
fun display_normal_callback () { global.p_s = NULL; global.b_s = NULL; }
Plymouth.SetDisplayPasswordFunction(display_password_callback);
Plymouth.SetDisplayNormalFunction(display_normal_callback);
fun message_callback (text) { m = Image.Text(text, 0.6, 0.75, 0.72); global.m_s = Sprite(m); global.m_s.SetPosition(sw / 2 - m.GetWidth() / 2, shh * 0.93, 10); }
Plymouth.SetMessageFunction(message_callback);
'''
def make_plymouth():
    from PIL import Image, ImageDraw, ImageFilter, ImageFont
    t=f'{PKG}/plymouth/cachyos7'; os.makedirs(t,exist_ok=True)
    open(f'{t}/cachyos7.plymouth','w').write('[Plymouth Theme]\nName=CachyOS 7\nDescription=CachyOS 7: CachyOS logo on dark slate with a teal glow and orbiting dots (original)\nModuleName=script\n\n[script]\nImageDir=/usr/share/plymouth/themes/cachyos7\nScriptFile=/usr/share/plymouth/themes/cachyos7/cachyos7.script\n')
    open(f'{t}/cachyos7.script','w').write(PLY_SCRIPT)
    logo(300).save(f'{t}/logo.png')
    g=Image.new('RGBA',(700,700),(0,0,0,0)); ImageDraw.Draw(g).ellipse([150,150,550,550],fill=TEAL+(150,)); g=g.filter(ImageFilter.GaussianBlur(90)); g.save(f'{t}/glow.png')
    dot=Image.new('RGBA',(40,40),(0,0,0,0)); dd=ImageDraw.Draw(dot); dd.ellipse([4,4,36,36],fill=TEAL+(120,)); dd.ellipse([10,10,30,30],fill=MINT+(255,)); dot=dot.filter(ImageFilter.GaussianBlur(1)); dot.save(f'{t}/dot.png')
    f=ImageFont.truetype(FR,54); tw=int(ImageDraw.Draw(Image.new('RGB',(1,1))).textlength('Starting CachyOS 7',font=f))
    ti=Image.new('RGBA',(tw+20,80),(0,0,0,0)); ImageDraw.Draw(ti).text((10,4),'Starting CachyOS 7',font=f,fill=TXT+(255,)); ti.save(f'{t}/title.png')
    # preview mock at 1920x1080
    W,H=1920,1080; im=Image.new('RGBA',(W,H)); d=ImageDraw.Draw(im)
    for y in range(H): d.line([(0,y),(W,y)],fill=tuple(int(SLATE[c]+(CHAR[c]-SLATE[c])*y/H) for c in range(3))+(255,))
    im.alpha_composite(g,(W//2-350,int(H*0.42)-350)); lg=Image.open(f'{t}/logo.png'); im.alpha_composite(lg,(W//2-150,int(H*0.42)-150))
    im.alpha_composite(ti,(W//2-ti.width//2,int(H*0.62)))
    import math
    for i in range(4):
        a=1.2-i*0.55; dt=dot.copy(); dt.putalpha(dt.getchannel('A').point(lambda v:int(v*(1-i*0.22))))
        im.alpha_composite(dt,(int(W/2+math.cos(a)*34-20),int(H*0.78+math.sin(a)*34-20)))
    out=f'{HOME}/Pictures/cachyos7_plymouth_preview.png'; im.convert('RGB').save(out); return out

# ---------------- 2. login screen assets ----------------
def make_login():
    from PIL import Image, ImageFilter, ImageEnhance, ImageDraw, ImageFont
    g=f'{PKG}/gdm'; os.makedirs(g,exist_ok=True)
    bg=Image.open(WALL).convert('RGB').filter(ImageFilter.GaussianBlur(28)); bg=ImageEnhance.Brightness(bg).enhance(0.55); bg.save(f'{g}/cachyos7-login.png')
    L=logo(256); L.save(f'{g}/cachyos7-logo.png')
    # preview mock of the GDM greeter
    W,H=1920,1080; im=bg.resize((W,H)).convert('RGBA'); d=ImageDraw.Draw(im)
    d.rectangle([0,0,W,36],fill=(0,0,0,170)); fS=ImageFont.truetype(FB,20); d.text((W//2-40,6),'11:45 AM',font=fS,fill=(255,255,255))
    av=Image.open(f'{HOME}/.face').convert('RGBA').resize((128,128)); m=Image.new('L',(128,128),0); ImageDraw.Draw(m).ellipse([0,0,127,127],fill=255)
    im.paste(av,(W//2-64,H//2-170),m); fN=ImageFont.truetype(FB,30); d.text((W//2-d.textlength(__import__('pwd').getpwuid(os.getuid()).pw_gecos.split(',')[0] or os.environ.get('USER','User'),font=fN)/2,H//2-24),__import__('pwd').getpwuid(os.getuid()).pw_gecos.split(',')[0] or os.environ.get('USER','User'),font=fN,fill=(255,255,255))
    d.rounded_rectangle([W//2-180,H//2+30,W//2+180,H//2+80],radius=25,fill=(13,21,23,220),outline=TEAL+(255,),width=2)
    d.text((W//2-160,H//2+42),'Password',font=ImageFont.truetype(FR,22),fill=(127,154,150))
    d.ellipse([W-90,H-90,W-46,H-46],outline=TEAL+(255,),width=2); d.text((W-78,H-84),'⚙',font=ImageFont.truetype(FR,24),fill=(255,255,255))
    sm=L.resize((96,96)); im.alpha_composite(sm,(W//2-48,H-150))
    out=f'{HOME}/Pictures/cachyos7_login_preview.png'; im.convert('RGB').save(out); return out

if __name__=='__main__':
    what=sys.argv[1] if len(sys.argv)>1 else 'all'
    for n,f in (('sounds',make_sounds),('sheet',make_shortcut_sheet),('plymouth',make_plymouth),('login',make_login)):
        if what in (n,'all'): print(n,f())
