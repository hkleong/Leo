import json,struct,io,sys,glob,os
from PIL import Image
def rd(f):
  b=open(f,'rb').read();L=struct.unpack('<I',b[12:16])[0];j=json.loads(b[20:20+L]);o=20+L;BL=struct.unpack('<I',b[o:o+4])[0];return j,b[o+8:o+8+BL]
tot0=tot1=0
for f in sorted(glob.glob('charzip/models/*.glb')):
  j,B=rd(f);imgv={im['bufferView']:k for k,im in enumerate(j.get('images',[])) if 'bufferView' in im}
  out=bytearray();
  for vi,v in enumerate(j['bufferViews']):
    data=B[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']]
    if vi in imgv:
      im=Image.open(io.BytesIO(data));im.load()
      lim=512 if 'lead' in f and 'patrol' not in f else 256
      if max(im.size)>lim:im.thumbnail((lim,lim),Image.LANCZOS)
      bio=io.BytesIO();im.save(bio,'WEBP',quality=82,method=6);data=bio.getvalue();j['images'][imgv[vi]]['mimeType']='image/webp'
    while len(out)%4:out.append(0)
    v['byteOffset']=len(out);v['byteLength']=len(data);out+=data
  while len(out)%4:out.append(0)
  j['buffers'][0]['byteLength']=len(out)
  js=json.dumps(j,separators=(',',':')).encode();js+=b' '*((4-len(js)%4)%4)
  glb=struct.pack('<III',0x46546C67,2,12+8+len(js)+8+len(out))+struct.pack('<II',len(js),0x4E4F534A)+js+struct.pack('<II',len(out),0x004E4942)+bytes(out)
  o='glb2/'+os.path.basename(f);open(o,'wb').write(glb);tot0+=os.path.getsize(f);tot1+=len(glb);print(os.path.basename(f),os.path.getsize(f),len(glb))
print('total',tot0,tot1)
