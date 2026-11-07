#!/usr/bin/env python3
"""Standard character reference sheet (林逍 v3 standard).
refsheet.py spec.json  -> out/<id>/ refsheet + front/half/face singles
spec: {id, base, keep, details:[[key,label,prompt],...], title, line1, line2}"""
import json, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageDraw, ImageFont
HERE=os.path.dirname(os.path.abspath(__file__)); P6=os.path.dirname(HERE); Q=os.path.join(P6,'..','p2','qwen21.py')
s=json.load(open(sys.argv[1])); od=os.path.join(P6,'out','sheets',s['id']); os.makedirs(od,exist_ok=True)
EMB=os.path.join(P6,'out/emblem/STANDARD_emblem.png')
EM=" The small school emblem embroidered in white thread on the left chest of the navy blazer must be exactly the emblem shown in image 2 (a slim upward-pointing jian sword with a stylized cloud swirl around the lower blade), same shape, small size." if s.get('emblem') else ""
K=f"Keep exactly the same person from image 1: identical face, hairstyle and hair color, body build, {s['keep']}, no added decorations, same photorealistic live-action style, same plain medium-grey studio background, natural skin texture, no text."+EM
D="Keep exactly the same items from image 1 with identical design, colors, materials and wear, same plain medium-grey studio background, photorealistic product-detail photography, 100mm macro lens, razor-sharp focus, high detail, no text, no faces."
views={'front':"Change the view: full-body front view, standing straight facing the camera, relaxed natural pose, neutral calm expression.",
 'side':"Change the view: full-body standing in exact side profile, relaxed posture.",
 'back':"Change the view: full-body standing seen from directly behind, back view, head slightly turned.",
 'half':"Change the view: a front-facing waist-up half-body portrait framed from the top of the head to the waist, looking at the camera, natural expression in character.",
 'face':"Change the view: an extreme high-definition close-up headshot, the face fills most of the frame from the top of the hair to the collarbone, front facing, looking straight into the camera. Razor-sharp focus on the eyes, eyelashes, iris detail, individual hair strands and fine natural skin pores, soft studio key light, 100mm portrait lens."}
jobs={k:K+' '+v for k,v in views.items()}
for k,_,p in s['details']: jobs['d_'+k]=D+(EM if 'emblem' in k or 'collar' in k or 'jade' in k else '')+' '+p
def run(k):
    if os.path.exists(os.path.join(od,k+'_0.png')): return True
    pf=os.path.join(od,k+'.txt'); open(pf,'w').write(jobs[k])
    r=subprocess.run([sys.executable,Q,'--prompt-file',pf,'--out',os.path.join(od,k),'--images',s['base'],*([EMB] if s.get('emblem') and (not k.startswith('d_') or any(w in k for w in ('emblem','collar','jade'))) else []),'--full','--res','1328'],capture_output=True,text=True)
    ok=os.path.exists(os.path.join(od,k+'_0.png')); print(k,'ok' if ok else 'FAIL '+r.stdout[-300:]+r.stderr[-300:],flush=True); return ok
with ThreadPoolExecutor(9) as ex: res=list(ex.map(run,jobs))
if not all(res): sys.exit('some failed')
F='/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'
top=[('front','正面'),('side','侧面'),('back','背面'),('half','半身'),('face','特写')]
bot=[('d_'+k,'细节 · '+l) for k,l,_ in s['details']]
def row(items,H):
    ims=[(Image.open(os.path.join(od,p+'_0.png')).convert('RGB'),t) for p,t in items]
    return [(im.resize((int(im.width*H/im.height),H),Image.LANCZOS),t) for im,t in ims]
T=row(top,1200); Wt=sum(i.width for i,_ in T)
B0=[Image.open(os.path.join(od,p+'_0.png')) for p,_ in bot]; hb=int(Wt/sum(i.width/i.height for i in B0)); B=row(bot,hb)
HDR=220; out=Image.new('RGB',(Wt,HDR+1200+hb),(28,30,36)); d=ImageDraw.Draw(out)
fT=ImageFont.truetype(F,64); fL=ImageFont.truetype(F,40); fS=ImageFont.truetype(F,32)
d.text((30,20),s['title'],font=fT,fill=(255,255,255)); d.text((30,104),s['line1'],font=fS,fill=(180,190,210)); d.text((30,150),s['line2'],font=fS,fill=(150,220,255))
x=0
for im,t in T: out.paste(im,(x,HDR)); d.text((x+16,HDR+12),t,font=fL,fill=(255,220,90)); x+=im.width
x=0
for im,t in B: out.paste(im,(x,HDR+1200)); d.text((x+16,HDR+1212),t,font=fL,fill=(255,220,90)); x+=im.width
out.save(os.path.join(od,s['id']+'_refsheet.png')); out.resize((out.width//4,out.height//4)).save(os.path.join(od,'chk.png'))
print('done',os.path.join(od,s['id']+'_refsheet.png'))
