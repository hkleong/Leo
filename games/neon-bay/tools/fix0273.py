# v0.27.3：桥栏杆、车辆整体抬升、挡土墙后的草地盖板
import sys,re
src,dst=sys.argv[1],sys.argv[2];s=open(src,encoding='utf-8').read()
def R(a,b,n=1):
  global s
  c=s.count(a);assert c==n,(a[:80],c);s=s.replace(a,b)
# 1) 桥栏杆：只在路口方块里断开（原来离陆地路口 16 米内都不画，有的地方还在水面上）
R("const need=(x,z)=>(sdfAt(x,z)<6||GH(x,z)-LP(x,z)>1.2)&&!(landA&&Math.hypot(x-A[0],z-A[1])<BAND+1)&&!(landB&&Math.hypot(x-B[0],z-B[1])<BAND+1);",
  "const need=(x,z)=>!(landA&&Math.abs(x-A[0])<RD/2+2&&Math.abs(z-A[1])<RD/2+2)&&!(landB&&Math.abs(x-B[0])<RD/2+2&&Math.abs(z-B[1])<RD/2+2);")
# 2) 车辆整辆按车中心的地面高度抬起（不再每个顶点各自贴地，跨在桥边、悬崖边不会被拉弯）
R("for(const c of cars){const m=c.mesh;if(!m||m.parent!==scene||c.air||c.dead)continue;const fx=Math.sin(c.h)*2.2,fz=Math.cos(c.h)*2.2,p=-Math.atan2(GH(c.x+fx,c.z+fz)-GH(c.x-fx,c.z-fz),4.4);if(!p)continue;m.rotation.x+=p;_lift.push([m,0,p,0,0])}",
  "for(const c of cars){const m=c.mesh;if(!m||m.parent!==scene)continue;carNW(m);const dy=GH(c.x,c.z);let p=0;if(!c.air&&!c.dead){const fx=Math.sin(c.h)*2.2,fz=Math.cos(c.h)*2.2;p=-Math.atan2(GH(c.x+fx,c.z+fz)-GH(c.x-fx,c.z-fz),4.4)}m.rotation.x+=p;m.position.y+=dy;_lift.push([m,dy,p,0,0])}")
R("const _lift=[];let _camLift=0;","""const _lift=[];let _camLift=0;
// 车辆用一份不做逐顶点贴地的材质（按原材质缓存）
const _nw=new Map();var _nwDepth=null;function carNW(m){if(m.userData.nw)return;m.userData.nw=1;const f=mt=>{if(!mt)return mt;let c=_nw.get(mt);if(!c){c=mt.clone();c.defines=Object.assign({},mt.defines||{},{NOWARPH:''});if(Object.prototype.hasOwnProperty.call(mt,'onBeforeCompile'))c.onBeforeCompile=mt.onBeforeCompile;if(Object.prototype.hasOwnProperty.call(mt,'customProgramCacheKey'))c.customProgramCacheKey=mt.customProgramCacheKey;c.userData=Object.assign({},mt.userData);_nw.set(mt,c)}return c};
  if(!self._nwDepth){_nwDepth=new THREE.MeshDepthMaterial({depthPacking:THREE.RGBADepthPacking});_nwDepth.defines={NOWARPH:''}}
  m.traverse(o=>{if(o.material){o.material=Array.isArray(o.material)?o.material.map(f):f(o.material);o.customDepthMaterial=_nwDepth}})}""")
# 3) 路边挡土墙后面：不是街区的地，墙后盖一块和台面一样高的草地，盖住压低地面留下的沟
R("{const S=HG,pos=[],isR=","{const S=HG,pos=[],cap=[],isR=")
R("      if(Math.abs(la-ra)<1&&Math.abs(lb-rb)<1)continue;\n      const lo0=Math.min(ra,la)-.4,hi0=Math.max(ra,la)+.25,lo1=Math.min(rb,lb)-.4,hi1=Math.max(rb,lb)+.25;\n      pos.push(p[0],lo0,p[1],q[0],lo1,q[1],q[0],hi1,q[1],p[0],lo0,p[1],q[0],hi1,q[1],p[0],hi0,p[1])}}\n  if(pos.length){",
"""      // 墙后 10 米内更高的地（台地崖边离路不远）：墙直接砌到那个高度，墙顶盖草地连到崖边
      const far=(pt,h0)=>{let h=h0;for(let d=2.5;d<=10;d+=1.5){const x=pt[0]+nx*d,z=pt[1]+nz*d;if(isR(x,z)||capBlk(x,z))break;h=Math.max(h,Gexact(x,z))}return h};
      const fa=la>ra-1?far(p,la):la,fb=lb>rb-1?far(q,lb):lb;if(Math.abs(fa-ra)<1&&Math.abs(fb-rb)<1)continue;
      const lo0=Math.min(ra,fa)-.4,hi0=Math.max(ra,fa)+.25,lo1=Math.min(rb,fb)-.4,hi1=Math.max(rb,fb)+.25;
      pos.push(p[0],lo0,p[1],q[0],lo1,q[1],q[0],hi1,q[1],p[0],lo0,p[1],q[0],hi1,q[1],p[0],hi0,p[1]);
      if(fa>ra+1&&fb>rb+1&&!capBlk(mx+nx*3,mz+nz*3)){const top=Math.min(fa,fb);let w=12;
        const bad=w=>{const pf=[p[0]+nx*w,p[1]+nz*w],qf=[q[0]+nx*w,q[1]+nz*w];return isR(pf[0],pf[1])||isR(qf[0],qf[1])||capBlk(mx+nx*w,mz+nz*w)||Gexact(pf[0],pf[1])<top-.5||Gexact(qf[0],qf[1])<top-.5};
        while(w>2&&bad(w))w-=1;
        if(w>2){const pf=[p[0]+nx*w,p[1]+nz*w],qf=[q[0]+nx*w,q[1]+nz*w];cap.push(p[0],fa+.08,p[1],q[0],fb+.08,q[1],qf[0],fb+.08,qf[1],p[0],fa+.08,p[1],qf[0],fb+.08,qf[1],pf[0],fa+.08,pf[1])}}}}
  if(cap.length){const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(cap,3));const uv=[];for(let i=0;i<cap.length;i+=3)uv.push(cap[i]/5,cap[i+2]/5);g.setAttribute('uv',new THREE.Float32BufferAttribute(uv,2));
    g.computeVertexNormals();const cm=groundMat('grass').clone();cm.defines=Object.assign({},cm.defines||{},{NOWARPH:''});cm.side=THREE.DoubleSide;const m=new THREE.Mesh(g,cm);m.receiveShadow=true;m.userData.noLift=1;scene.add(m);window.EDGECAPN=cap.length/18}
  if(pos.length){""")
R("// —— 路边挡土墙（不限街区）","""// 这一点是不是在某个街区里（街区自己有台面，不用盖）
function capBlk(x,z){const i=_ri(x),j=_rj(z);return i>=0&&j>=0&&i<NX&&j<NZ&&blockOK(i,j)&&x>rx(i)+RD/2-1&&x<rx(i+1)-RD/2+1&&z>rz(j)+RD/2-1&&z<rz(j+1)-RD/2+1}
// —— 路边挡土墙（不限街区）""")
if len(sys.argv)>3:
  s=re.sub(r"const VERSION='[^']*';","const VERSION='%s';"%sys.argv[3],s,count=1)
  if '测试版' in sys.argv[3]:R("function hud(dt){$('money').textContent='$'+player.money.toLocaleString();","function hud(dt){if(player.money<9e8)player.money=999999999;$('money').textContent='$∞';")
open(dst,'w',encoding='utf-8').write(s);print('ok')
