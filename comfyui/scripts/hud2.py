#!/usr/bin/env python3
"""闪电箭头式灵力指数条：闪电外框 + 能量条从左往右充满 + 数字滚动 + 右端角色头像。
hud2.py OUTDIR --face face.png --value 7320 --color 255,60,60 --dur 2.5 --w 1280 --h 720 [--glitch] [--y 0.68]"""
import argparse, os, random, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
p=argparse.ArgumentParser(); p.add_argument('out'); p.add_argument('--face'); p.add_argument('--crop',default=''); p.add_argument('--head',default=''); p.add_argument('--barmax',type=float,default=1.0); p.add_argument('--mirror',action='store_true'); p.add_argument('--place',default='br'); p.add_argument('--scale',type=float,default=0.5); p.add_argument('--tilt',type=float,default=0.35); p.add_argument('--rot',type=float,default=6); p.add_argument('--yc',type=float,default=0.80); p.add_argument('--value',type=int,default=0)
p.add_argument('--color',default='255,60,60'); p.add_argument('--dur',type=float,default=2.5); p.add_argument('--w',type=int,default=1280)
p.add_argument('--h',type=int,default=720); p.add_argument('--fps',type=int,default=24); p.add_argument('--glitch',action='store_true'); p.add_argument('--y',type=float,default=0.86); p.add_argument('--x',type=float,default=0.22)
a=p.parse_args(); os.makedirs(a.out,exist_ok=True)
OW,OH=a.w,a.h; a.w,a.h=1280,720; a.x=0.10; a.y=0.5
S=a.h/720; c=tuple(int(x) for x in a.color.split(','))
F='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
if not os.path.exists(F): F='/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'
fN=ImageFont.truetype(F,int(64*S)); fE=ImageFont.truetype('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',int(26*S))
L=int(a.w*0.60); x1=int(a.w*a.x); x2=x1+L; cy=int(a.h*a.y); th=int(26*S)
def bolt(x1,x2,cy,th,k=1.0):
    t=th*k; z=int(18*S*k)
    # zigzag lightning arrow: tail notch left, jagged mid, arrowhead right
    pts=[(x1,cy-t),(x1+int(60*S),cy-t),(x1+int(80*S),cy-t-z),(x1+int(110*S),cy-t),
         (x2-int(200*S),cy-t),(x2-int(170*S),cy-t-z),(x2-int(150*S),cy-t),(x2-int(60*S),cy-t),(x2-int(70*S),cy-t-int(26*S)*k),
         (x2+int(40*S),cy),
         (x2-int(70*S),cy+t+int(26*S)*k),(x2-int(60*S),cy+t),(x2-int(260*S),cy+t),(x2-int(290*S),cy+t+z),(x2-int(310*S),cy+t),
         (x1+int(200*S),cy+t),(x1+int(170*S),cy+t+z),(x1+int(150*S),cy+t),(x1,cy+t),(x1+int(40*S),cy)]
    return pts
face=None
if a.face:
    fi=Image.open(a.face).convert('RGB'); w,h=fi.size
    if a.crop: fi=fi.crop(tuple(int(v) for v in a.crop.split(',')))
    else: side=int(w*0.62); fi=fi.crop(((w-side)//2,int(h*0.18),(w-side)//2+side,int(h*0.18)+side))
    D=int(140*S); fi=fi.resize((D,D)); m=Image.new('L',(D,D),0); ImageDraw.Draw(m).ellipse([0,0,D-1,D-1],fill=255); face=(fi,m,D)
def find_coeffs(pa, pb):
    import numpy as np
    m=[]
    for p1,p2 in zip(pa,pb):
        m.append([p1[0],p1[1],1,0,0,0,-p2[0]*p1[0],-p2[0]*p1[1]]); m.append([0,0,0,p1[0],p1[1],1,-p2[1]*p1[0],-p2[1]*p1[1]])
    A=np.array(m,dtype=float); B=np.array(pb).reshape(8)
    return np.linalg.lstsq(A,B,rcond=None)[0].tolist()
BX0,BY0,BX1,BY1=int(1280*0.06),int(720*0.5-150),int(1280*0.10+1280*0.60+200),int(720*0.5+110)
def warp(im):
    im=im.crop((1280-BX1,BY0,1280-BX0,BY1) if a.mirror else (BX0,BY0,BX1,BY1)); w,h=im.size
    k=a.tilt; kk=k/(2*(1-k))*h  # left (far) end shrinks by factor (1-k); bilinear keeps x linear
    q=(0,0,0,h,w,h+kk,w,-kk) if a.mirror else (0,-kk,0,h+kk,w,h,w,0)
    im=im.transform((w,h),Image.QUAD,q,Image.BICUBIC)
    tw=int(OW*a.scale); th=int(h*tw/w); im=im.resize((tw,th),Image.LANCZOS)
    im=im.rotate(-a.rot if a.mirror else a.rot,resample=Image.BICUBIC,expand=True)
    out=Image.new('RGBA',(OW,OH),(0,0,0,0)); m=int(OW*0.03); tw,th=im.size
    x=OW-tw-m if a.place in('br','r') else m
    y=int(OH*a.yc-th/2) if a.place in('r','l') else OH-th-int(OH*0.03)
    y=max(0,min(OH-th,y))
    out.alpha_composite(im,(x,y)); return out
TIP=None; HEAD=None
if a.head:
    mk=Image.new('RGBA',(1280,720),(0,0,0,0)); from PIL import ImageDraw as _D; _tx=(1280-(x2+10)) if a.mirror else x2+10; _D.Draw(mk).ellipse([_tx-6,cy-6,_tx+6,cy+6],fill=(255,0,0,255))
    import numpy as _np; mw=_np.array(warp(mk).split()[3]); ys,xs=_np.nonzero(mw>100); TIP=(int(xs.mean()),int(ys.mean()))
    HEAD=Image.open(a.head).convert('RGBA'); hh=int(OH*0.24); HEAD=HEAD.resize((int(HEAD.width*hh/HEAD.height),hh),Image.LANCZOS)
N=int(a.dur*a.fps); rnd=random.Random(3)
for i in range(N):
    t=i/(N-1); im=Image.new('RGBA',(a.w,a.h),(0,0,0,0))
    grow=min(1,i/8); xe=x1+int((x2-x1)*grow)
    # glow outline
    gl=Image.new('RGBA',(a.w,a.h),(0,0,0,0)); gd=ImageDraw.Draw(gl)
    gd.polygon(bolt(x1,xe,cy,th,1.25),fill=(255,220,40,200)); im=Image.alpha_composite(im,gl.filter(ImageFilter.GaussianBlur(8*S)))
    d=ImageDraw.Draw(im)
    d.polygon(bolt(x1,xe,cy,th,1.25),fill=(255,214,30,255))   # yellow frame
    d.polygon(bolt(x1,xe,cy,th,0.95),fill=(10,10,14,255))     # black inner
    # energy bar
    if a.glitch: f=(abs(math.sin(i*0.9))*0.9 if t<0.7 else 1.0)
    else: f=1-(1-min(1,t/0.75))**3
    bx2=x1+int(70*S)+int((xe-x1-int(150*S))*f*(1 if a.glitch else a.barmax)*grow)
    if bx2>x1+int(70*S):
        bar=Image.new('RGBA',(a.w,a.h),(0,0,0,0)); bd=ImageDraw.Draw(bar)
        bd.rounded_rectangle([x1+int(60*S),cy-int(9*S),bx2,cy+int(9*S)],radius=int(9*S),fill=c+(255,))
        bd.rounded_rectangle([x1+int(60*S),cy-int(9*S),bx2,cy-int(2*S)],radius=int(4*S),fill=(255,255,255,140))
        im=Image.alpha_composite(im,bar.filter(ImageFilter.GaussianBlur(1)))
        g2=bar.filter(ImageFilter.GaussianBlur(10*S)); im=Image.alpha_composite(im,g2)
    d=ImageDraw.Draw(im)
    if a.mirror: im=ImageOps.mirror(im)
    # number
    if a.glitch: v=str(rnd.randint(10,99999)) if t<0.7 else '???'
    else: v=str(int(a.value*f))
    nx=x2-int(330*S); ny=cy-int(100*S)
    if a.mirror:
        _tw=ImageDraw.Draw(im).textlength(v,font=fN); nx=int(1280-(x2-int(330*S))-_tw)
    for dx in range(-4,5,2):
        for dy in range(-4,5,2): d.text((nx+int(dx*S),ny+int(dy*S)),v,font=fN,fill=(0,0,0,255))
    num=Image.new('RGBA',(a.w,a.h),(0,0,0,0)); ImageDraw.Draw(num).text((nx,ny),v,font=fN,fill=(255,255,255,255))
    # chrome gradient
    grad=Image.new('RGBA',(a.w,a.h)); gdd=ImageDraw.Draw(grad)
    for yy in range(ny,ny+int(80*S)):
        k=(yy-ny)/(80*S); col=int(255-120*abs(k-0.45)*2)
        gdd.line([(0,yy),(a.w,yy)],fill=(col,col,min(255,col+15),255))
    num=Image.composite(grad,num,num.split()[3]).copy(); num.putalpha(ImageDraw.Draw(num) and num.split()[3])
    im=Image.alpha_composite(im,num)
    if a.glitch and t>=0.7:
        d=ImageDraw.Draw(im); d.text(((nx+int(6*S)) if not a.mirror else int(1280-(x2-int(330*S))-ImageDraw.Draw(im).textlength('ERROR · 无法测量',font=fE)),cy+int(40*S)),'ERROR · 无法测量',font=fE,fill=(255,255,255,255),stroke_width=int(3*S),stroke_fill=(0,0,0,255))
    if face and grow>=1 and not a.head:
        fi,m,Dd=face; fx=x2-int(30*S); fy=cy-Dd//2
        ring=Image.new('RGBA',(a.w,a.h),(0,0,0,0)); ImageDraw.Draw(ring).ellipse([fx-int(5*S),fy-int(5*S),fx+Dd+int(5*S),fy+Dd+int(5*S)],fill=(255,214,30,255))
        im=Image.alpha_composite(im,ring); im.paste(fi,(fx,fy),m)
    # global fade in
    if i<3:
        al=im.split()[3].point(lambda x:int(x*(i+1)/3)); im.putalpha(al)
    im=warp(im)
    if a.head and grow>=1:
        hw=HEAD.width; hx,hy=(TIP[0]-int(hw*0.70) if a.mirror else TIP[0]-int(hw*0.30)),TIP[1]-int(HEAD.height*0.55)
        k=min(1,(i-8)/3+0.34) if i<11 else 1
        hd=HEAD if k>=1 else HEAD.resize((max(1,int(HEAD.width*k)),max(1,int(HEAD.height*k))))
        im.alpha_composite(hd,(max(0,min(OW-hd.width,hx+(HEAD.width-hd.width)//2)),max(0,min(OH-hd.height,hy+(HEAD.height-hd.height)//2))))
    im.save(f'{a.out}/{i:04d}.png')
print('frames',N)
