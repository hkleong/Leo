#!/usr/bin/env python3
"""把霓虹湾打包成可安装的网页 App（PWA），输出到仓库根目录的 docs/。

用法：在仓库根目录运行  python3 games/neon-bay/build_app.py
之后把 docs/ 用 GitHub Pages（或 Netlify / Cloudflare Pages）发布即可。
游戏源文件 games/neon-bay/index.html 改动后，重新运行一次本脚本。
"""
import hashlib, json, os, shutil
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.join(ROOT, 'docs')
os.makedirs(os.path.join(OUT, 'icons'), exist_ok=True)
os.makedirs(os.path.join(OUT, 'vendor'), exist_ok=True)

THREE_CDN = '<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>'
THREE_LOCAL = os.path.join(OUT, 'vendor', 'three.min.js')
if not os.path.exists(THREE_LOCAL):
    raise SystemExit('缺少 docs/vendor/three.min.js：先下载 three.js r128 的 three.min.js 放到这里')

# ---------- 图标：日落渐变 + 太阳 + 海面 + 椰子树 + “霓虹湾” ----------
FONT = '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'

ICON_SRC = os.path.join(HERE, 'art', 'icon.png')   # 有这张就用它（主角插画 + 霓虹湾字标）

def make_icon(size, maskable=False):
    if os.path.exists(ICON_SRC):
        img = Image.open(ICON_SRC).convert('RGB').resize((1024, 1024), Image.LANCZOS)
        if maskable:
            bg = Image.new('RGB', (1024, 1024), (26, 8, 40)); bg.paste(img.resize((820, 820), Image.LANCZOS), (102, 102)); img = bg
        return img.resize((size, size), Image.LANCZOS)
    W = 1024
    img = Image.new('RGB', (W, W))
    d = ImageDraw.Draw(img)
    top, mid, low = (43, 11, 61), (255, 61, 139), (255, 179, 71)
    for y in range(W):
        t = y / W
        c = [int(top[i] + (mid[i] - top[i]) * t / .55) for i in range(3)] if t < .55 else \
            [int(mid[i] + (low[i] - mid[i]) * (t - .55) / .45) for i in range(3)]
        d.line([(0, y), (W, y)], fill=tuple(c))
    # 太阳（横条纹）
    sun = Image.new('L', (W, W), 0); sd = ImageDraw.Draw(sun)
    sd.ellipse([262, 300, 762, 800], fill=255)
    for k in range(6):
        y = 560 + k * 38
        sd.rectangle([0, y, W, y + 8 + k * 3], fill=0)
    img.paste(Image.new('RGB', (W, W), (255, 225, 120)), (0, 0), sun)
    # 海面
    d.rectangle([0, 700, W, W], fill=(31, 181, 201))
    for k in range(5):
        y = 730 + k * 50
        d.line([(120 + k * 30, y), (900 - k * 30, y)], fill=(127, 214, 208), width=6)
    # 椰子树剪影
    pc = (26, 15, 42)
    d.line([(300, 700), (330, 520), (380, 360)], fill=pc, width=34, joint='curve')
    for ang in [(-260, -40), (-200, 60), (-60, 110), (40, 40), (60, -60), (-120, -120)]:
        d.line([(380, 360), (380 + ang[0] * .7, 360 + ang[1] * .7)], fill=pc, width=30)
    # 文字
    try:
        f = ImageFont.truetype(FONT, 168)
        txt = '霓虹湾'
        tw = d.textlength(txt, font=f)
        x, y = (W - tw) / 2, 800 if not maskable else 770
        d.text((x + 8, y + 8), txt, font=f, fill=(26, 15, 42))
        d.text((x, y), txt, font=f, fill=(255, 255, 255))
    except OSError:
        pass
    if maskable:   # 可裁剪图标：内容缩到安全区（中间 80%）
        bg = Image.new('RGB', (W, W), (43, 11, 61))
        small = img.resize((int(W * .8), int(W * .8)), Image.LANCZOS)
        bg.paste(small, (int(W * .1), int(W * .1)))
        img = bg
    return img.resize((size, size), Image.LANCZOS)

icons = {'icon-192.png': (192, False), 'icon-512.png': (512, False), 'icon-maskable-512.png': (512, True), 'apple-touch-icon.png': (180, False)}
for name, (sz, mask) in icons.items():
    make_icon(sz, mask).save(os.path.join(OUT, 'icons', name))

# ---------- 美术素材 ----------
shutil.copytree(os.path.join(HERE, 'art'), os.path.join(OUT, 'art'), dirs_exist_ok=True)

# ---------- 页面：补上完整的 HTML 头部 + App 标签 ----------
src = open(os.path.join(HERE, 'index.html'), encoding='utf-8').read()
assert THREE_CDN in src, '游戏页面里找不到 three.js 的 CDN 引用'
body = src.replace(THREE_CDN, '<script src="vendor/three.min.js"></script>')
head = '''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover,user-scalable=no">
<meta name="theme-color" content="#2a0b3d">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="NBY VI">
<link rel="manifest" href="manifest.webmanifest">
<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">
<link rel="icon" type="image/png" href="icons/icon-192.png">
<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}*{-webkit-tap-highlight-color:transparent}body{margin:0;overscroll-behavior:none}</style>
</head>
<body>
'''
tail = r'''
<div id="installTip" hidden style="position:fixed;left:50%;bottom:calc(14px + env(safe-area-inset-bottom,0px));transform:translateX(-50%);z-index:9;background:rgba(10,8,24,.88);color:#fff;font:600 13px/1.5 Rubik,system-ui,sans-serif;padding:8px 14px;border-radius:10px;border:1.5px solid #ff3d8b;max-width:88vw;text-align:center">
  安装到桌面：点 Safari 底部的「分享」→「添加到主屏幕」，之后从桌面图标打开就是全屏 App。<button id="installClose" style="margin-left:8px;background:none;border:0;color:#ffb347;font-weight:700">知道了</button>
</div>
<script>
// 离线缓存
if('serviceWorker'in navigator)addEventListener('load',()=>navigator.serviceWorker.register('sw.js').catch(()=>{}));
// iPhone 在 Safari 里（还没装到桌面）时，开始页面提示一次怎么安装
(function(){const ios=/iphone|ipad|ipod/i.test(navigator.userAgent),standalone=navigator.standalone||matchMedia('(display-mode: standalone)').matches;
  let seen=false;try{seen=localStorage.getItem('nb-install-tip')==='1'}catch(e){}
  if(ios&&!standalone&&!seen){const t=document.getElementById('installTip');t.hidden=false;document.getElementById('installClose').onclick=()=>{t.hidden=true;try{localStorage.setItem('nb-install-tip','1')}catch(e){}};
    document.getElementById('start').addEventListener('click',()=>t.hidden=true)}})();
// 全屏 App 里锁定横屏（安卓支持；iPhone 由系统决定）
try{screen.orientation&&screen.orientation.lock&&screen.orientation.lock('landscape').catch(()=>{})}catch(e){}
</script>
</body>
</html>
'''
html = head + body + tail
open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(html)

# ---------- manifest ----------
manifest = {
    'name': 'NBY VI · 霓虹湾', 'short_name': 'NBY VI', 'description': '日落海滨城市里的开放世界：开车、接活、躲警察。',
    'lang': 'zh-CN', 'start_url': './', 'scope': './', 'display': 'fullscreen', 'orientation': 'landscape',
    'background_color': '#2a0b3d', 'theme_color': '#2a0b3d',
    'icons': [
        {'src': 'icons/icon-192.png', 'sizes': '192x192', 'type': 'image/png'},
        {'src': 'icons/icon-512.png', 'sizes': '512x512', 'type': 'image/png'},
        {'src': 'icons/icon-maskable-512.png', 'sizes': '512x512', 'type': 'image/png', 'purpose': 'maskable'},
    ],
}
json.dump(manifest, open(os.path.join(OUT, 'manifest.webmanifest'), 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

# ---------- service worker：版本号取文件内容哈希，游戏更新后自动换新缓存 ----------
files = ['./', 'index.html', 'manifest.webmanifest', 'vendor/three.min.js'] + \
        ['icons/' + n for n in icons] + ['art/' + n for n in sorted(os.listdir(os.path.join(OUT, 'art')))]
h = hashlib.sha1()
for f in files[1:]:
    h.update(open(os.path.join(OUT, f), 'rb').read())
ver = h.hexdigest()[:10]
sw = f'''// 霓虹湾离线缓存（自动生成，版本 {ver}）
const CACHE='neonbay-{ver}';
const FILES={json.dumps(files)};
self.addEventListener('install',e=>{{e.waitUntil(caches.open(CACHE).then(c=>c.addAll(FILES)).then(()=>self.skipWaiting()))}});
self.addEventListener('activate',e=>{{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim()))}});
// 页面优先走网络（拿到最新版），断网时用缓存；其他文件优先用缓存
self.addEventListener('fetch',e=>{{const r=e.request;if(r.method!=='GET')return;
  if(r.mode==='navigate'){{e.respondWith(fetch(r).then(res=>{{const cp=res.clone();caches.open(CACHE).then(c=>c.put('index.html',cp));return res}}).catch(()=>caches.match('index.html')));return}}
  e.respondWith(caches.match(r).then(hit=>hit||fetch(r).then(res=>{{if(res.ok&&new URL(r.url).origin===location.origin){{const cp=res.clone();caches.open(CACHE).then(c=>c.put(r,cp))}}return res}})))}});
'''
open(os.path.join(OUT, 'sw.js'), 'w', encoding='utf-8').write(sw)
open(os.path.join(OUT, '.nojekyll'), 'w').write('')
print('已生成 docs/ ：', ', '.join(sorted(os.listdir(OUT))), ' 缓存版本', ver)
