# v0.27.3：地形真正的高低差（平面 + 竖直崖壁）、人物和车辆整体抬起、桥栏杆和桥身用精确桥面高度
import sys,re
src,dst=sys.argv[1],sys.argv[2];s=open(src,encoding='utf-8').read()
def R(a,b,n=1):
  global s
  c=s.count(a);assert c==n,(a[:80],c);s=s.replace(a,b)
# ---------- 1) 桥：整座桥都有栏杆（只在路口方块里断开），栏杆/桥身/立柱/路灯按精确桥面高度摆，不再逐顶点贴地 ----------
R("const need=(x,z)=>(sdfAt(x,z)<6||GH(x,z)-LP(x,z)>1.2)&&!(landA&&Math.hypot(x-A[0],z-A[1])<BAND+1)&&!(landB&&Math.hypot(x-B[0],z-B[1])<BAND+1);",
  "const need=(x,z)=>!(landA&&Math.abs(x-A[0])<RD/2+2&&Math.abs(z-A[1])<RD/2+2)&&!(landB&&Math.abs(x-B[0])<RD/2+2&&Math.abs(z-B[1])<RD/2+2);const _bArr=CAP||scene.children,_bS0=_bArr.length;")
R("  for(let t=12;t<L-6;t+=34){const q=ptAt(P,t);if(sdfAt(q.x,q.z)>-3)continue;const py=",
  "  for(let k=_bS0;k<_bArr.length;k++){const m=_bArr[k];if(!m||!m.isMesh)continue;if(!m.geometry.boundingBox)m.geometry.computeBoundingBox();{const b=m.geometry.boundingBox;if(b.max.z-b.min.z>RD||b.max.x-b.min.x>RD)continue} // 路面底下的桥身照旧逐顶点贴地，只有栏杆、立柱、路灯用精确高度\n    m.position.y+=Gexact(m.position.x,m.position.z);m.material=nwMat(m.material);m.castShadow=false}\n  for(let t=12;t<L-6;t+=34){const q=ptAt(P,t);if(sdfAt(q.x,q.z)>-3)continue;const py=")
# ---------- 2) 车辆、人物：整体按脚下地面高度抬起（不做逐顶点贴地），阴影用同样不贴地的深度材质 ----------
R("for(const c of cars){const m=c.mesh;if(!m||m.parent!==scene||c.air||c.dead)continue;const fx=Math.sin(c.h)*2.2,fz=Math.cos(c.h)*2.2,p=-Math.atan2(GH(c.x+fx,c.z+fz)-GH(c.x-fx,c.z-fz),4.4);if(!p)continue;m.rotation.x+=p;_lift.push([m,0,p,0,0])}",
  "for(const c of cars){const m=c.mesh;if(!m||m.parent!==scene)continue;meshNW(m);const dy=GH(c.x,c.z);let p=0;if(!c.air&&!c.dead){const fx=Math.sin(c.h)*2.2,fz=Math.cos(c.h)*2.2;p=-Math.atan2(GH(c.x+fx,c.z+fz)-GH(c.x-fx,c.z-fz),4.4)}m.rotation.x+=p;m.position.y+=dy;_lift.push([m,dy,p,0,0])}\n"
  "    {const ppl=peds.map(p=>[p.mesh,p.x,p.z]);if(player.mesh)ppl.push([player.mesh,player.x,player.z]);for(const[m,x,z]of ppl){if(!m||m.parent!==scene)continue;meshNW(m);const dy=GH(x,z);m.position.y+=dy;_lift.push([m,dy,0,0,0])}}")
R("const _lift=[];let _camLift=0;","""const _lift=[];let _camLift=0;
// 不做逐顶点贴地的材质（按原材质缓存），以及对应的阴影深度材质
const _nw=new Map();var _nwD=null,_nwDS=null;
function nwMat(mt){if(!mt||mt.defines&&'NOWARPH' in mt.defines)return mt;let c=_nw.get(mt);if(!c){c=mt.clone();c.defines=Object.assign({},mt.defines||{},{NOWARPH:''});
  if(Object.prototype.hasOwnProperty.call(mt,'onBeforeCompile'))c.onBeforeCompile=mt.onBeforeCompile;if(Object.prototype.hasOwnProperty.call(mt,'customProgramCacheKey'))c.customProgramCacheKey=mt.customProgramCacheKey;c.userData=Object.assign({},mt.userData);_nw.set(mt,c)}return c}
function meshNW(m){if(m.userData.nw)return;m.userData.nw=1;if(!_nwD){_nwD=new THREE.MeshDepthMaterial({depthPacking:THREE.RGBADepthPacking});_nwD.defines={NOWARPH:''};_nwDS=new THREE.MeshDepthMaterial({depthPacking:THREE.RGBADepthPacking,skinning:true});_nwDS.defines={NOWARPH:''}}
  m.traverse(o=>{if(!o.material)return;o.material=Array.isArray(o.material)?o.material.map(nwMat):nwMat(o.material);if(o.isMesh)o.customDepthMaterial=o.isSkinnedMesh?_nwDS:_nwD})}""")
# ---------- 3) 地形：高差处不再拉成斜坡。网格里有高差的格子挖掉，按 1 米细格重建：高处平面 + 低处平面 + 竖直崖壁 ----------
R("     const hr=lowRoadNear(x,z);\n     if(hr!==null)y=hr-.4-GH(x,z);\n     else if(REAL&&sd>3)","     if(REAL&&sd>3)")
R(" g.computeVertexNormals();\n const TER=new THREE.Mesh(g,REAL?pixelTerrainMaterial()"," g.computeVertexNormals();terraceCut(g,nx,nz,st,x0,z0,SAND,GRASS,HIGH,ROCK,SHAL,DEEP);\n const TER=new THREE.Mesh(g,REAL?pixelTerrainMaterial()")
R("// —— 地形网格：沙滩、草地、台地、悬崖岩壁、近岸浅水（顶点色）","""// —— 台地高差：找出地形网格里跨高差的格子，从网格里挖掉，单独用平面 + 竖直崖壁重建（绝对高度，不做逐顶点贴地）
function terraceCut(g,nx,nz,st,x0,z0,SAND,GRASS,HIGH,ROCK,SHAL,DEEP){const S=HG,A=S.a,cut=new Uint8Array((nx-1)*(nz-1));let nc=0;
  for(let j=0;j<nz-1;j++)for(let i=0;i<nx-1;i++){const X=x0+i*st,Z=z0+j*st,ia=Math.max(0,Math.floor((X-2.5-S.x0)/S.st)),ib=Math.min(S.nx-1,Math.ceil((X+st+2.5-S.x0)/S.st)),ja=Math.max(0,Math.floor((Z-2.5-S.z0)/S.st)),jb=Math.min(S.nz-1,Math.ceil((Z+st+2.5-S.z0)/S.st));
    let hit=false;for(let b=ja;b<=jb&&!hit;b++)for(let a=ia;a<=ib;a++){const v=A[b*S.nx+a];if(a<ib&&Math.abs(A[b*S.nx+a+1]-v)>.8||b<jb&&Math.abs(A[(b+1)*S.nx+a]-v)>.8){hit=true;break}}
    if(hit){cut[j*(nx-1)+i]=1;nc++}}
  if(!nc)return;const I=g.index.array,ni=[];for(let c=0;c<(nx-1)*(nz-1);c++)if(!cut[c])for(let q=0;q<6;q++)ni.push(I[c*6+q]);g.setIndex(ni);
  // 精确地面高度（和地形网格顶点用同一套偏移）
  const TH=(x,z)=>{const sd=sdfAt(x,z);_gRoad=0;let ge=Gexact(x,z),road=_gRoad===1;if(sd<=0){ge=0;road=false}let y; // 水下（桥底下）按海底算，不跟着桥面抬
    if(sd>0)y=road&&!inZone(x,z,-14)&&onRoad(x,z,-.3)?(ge>.05?-.75:-.4):-.18;else y=sd>-14?-.95:-.95-Math.min(8,(-sd-14)*.25); // 只在沥青路面底下往下压；路边没铺面的地方和地面一样高（否则会低于海面，海水透上来）
    if(sd>0&&sd<3&&LP(x,z)===0)y=Math.min(y,-.1+sd*.03);if(sd>3&&!road&&REAL)y+=Math.round(Math.sin(x*.30)*Math.cos(z*.27)*3)*.035;return{h:ge+y,r:road}}; // 和地形网格顶点完全一样的公式（含起伏），接缝才对得上
  const pos=[],col=[],mix=[],c=new THREE.Color();
  const paint=(x,z,wall)=>{const sd=sdfAt(x,z),lp=sd>0?LP(x,z):0,beach=x>WU(.94)?48:14,land=clamp(sd/4,0,1);let m=[0,0,0];
    if(wall){c.copy(ROCK);m=[0,0,land>0?1:0]}else if(sd<=0)c.copy(sd>-14?SHAL:DEEP);else if(sd<beach&&lp===0){c.copy(SAND);m=[0,land,0]}else{c.copy(lp>0?HIGH:GRASS);m=[land,0,0]}
    const sh=.92+.08*Math.sin(x*.13+z*.07)*Math.cos(z*.11);col.push(c.r*sh,c.g*sh,c.b*sh);mix.push(...m)};
  const wpos=[],wuv=[];const tri=(a,b,d,wall)=>{if(wall){for(const v of[a,b,d]){wpos.push(v[0],v[1],v[2]);wuv.push((v[0]+v[2])/8,v[1]/5)}return}for(const v of[a,b,d]){pos.push(v[0],v[1],v[2]);paint(v[0],v[2],wall)}};
  const poly=(L,wall)=>{for(let k=1;k<L.length-1;k++)tri(L[0],L[k],L[k+1],wall)};
  const sub=st/3;
  for(let j=0;j<nz-1;j++)for(let i=0;i<nx-1;i++){if(!cut[j*(nx-1)+i])continue;const X=x0+i*st,Z=z0+j*st,n=Math.round(st/sub),H=[];
    for(let b=0;b<=n;b++)for(let a=0;a<=n;a++)H.push(TH(X+a*sub,Z+b*sub));
    { // 角点挨着没重建的格子：直接用地形网格那个顶点的实际高度
      const GP=g.attributes.position;for(const[a2,b2]of[[0,0],[n,0],[0,n],[n,n]]){const I0=i+(a2?1:0),J0=j+(b2?1:0);let flat=false;
        for(const[di,dj]of[[-1,-1],[0,-1],[-1,0],[0,0]]){const ci=I0+di,cj=J0+dj;if(ci>=0&&cj>=0&&ci<nx-1&&cj<nz-1&&!cut[cj*(nx-1)+ci])flat=true}
        if(flat){const vi=J0*nx+I0,xx=GP.getX(vi),zz=GP.getZ(vi),hv=GH(xx,zz)+GP.getY(vi);if(hv>GH(xx,zz)-.55||onRoad(xx,zz,-.3))H[b2*(n+1)+a2]={h:hv,r:H[b2*(n+1)+a2].r}}}}
    { // 和没重建的相邻格子接边：边上的中间点按两端角点线性插值，和地形网格那条直边完全重合（不留裂缝）
      const cutAt=(ii,jj)=>ii<0||jj<0||ii>=nx-1||jj>=nz-1||cut[jj*(nx-1)+ii],at=(p,q)=>H[q*(n+1)+p],lin=(p0,q0,p1,q1,t)=>at(p0,q0).h+(at(p1,q1).h-at(p0,q0).h)*t;
      for(let k=1;k<n;k++){const t=k/n;
        if(!cutAt(i-1,j))H[k*(n+1)+0]={h:lin(0,0,0,n,t),r:at(0,k).r};if(!cutAt(i+1,j))H[k*(n+1)+n]={h:lin(n,0,n,n,t),r:at(n,k).r};
        if(!cutAt(i,j-1))H[k]={h:lin(0,0,n,0,t),r:at(k,0).r};if(!cutAt(i,j+1))H[n*(n+1)+k]={h:lin(0,n,n,n,t),r:at(k,n).r}}}
    for(let b=0;b<n;b++)for(let a=0;a<n;a++){const C=[[a,b],[a+1,b],[a+1,b+1],[a,b+1]].map(([p,q])=>({x:X+p*sub,z:Z+q*sub,...H[q*(n+1)+p]}));
      let lo=1e9,hi=-1e9;for(const v of C){lo=Math.min(lo,v.h);hi=Math.max(hi,v.h)}
      if(hi-lo<.6){poly(C.map(v=>[v.x,v.h,v.z]),false);continue}
      const t=(lo+hi)/2,up=C.map(v=>v.h>t),X2=[];
      for(let e=0;e<4;e++){const f=(e+1)%4;if(up[e]===up[f])continue;let ax=C[e].x,az=C[e].z,bx=C[f].x,bz=C[f].z;const ua=up[e];
        for(let k=0;k<12;k++){const mx=(ax+bx)/2,mz=(az+bz)/2;if((TH(mx,mz).h>t)===ua){ax=mx;az=mz}else{bx=mx;bz=mz}}
        const cx=(ax+bx)/2,cz=(az+bz)/2,dx=C[f].x-C[e].x,dz=C[f].z-C[e].z,l=Math.hypot(dx,dz)||1,ox=dx/l*.04,oz=dz/l*.04;
        const hA=TH(cx-ox,cz-oz),hB2=TH(cx+ox,cz+oz),hiH=ua?hA:hB2,loH=ua?hB2:hA;X2.push({e,x:cx,z:cz,hh:hiH.h,lh:loH.h,road:hiH.r||loH.r})}
      const build=want=>{const L=[];for(let e=0;e<4;e++){if(up[e]===want)L.push([C[e].x,C[e].h,C[e].z]);const x=X2.find(q=>q.e===e);if(x)L.push([x.x,want?x.hh:x.lh,x.z])}return L};
      {const cutAt=(ii,jj)=>ii<0||jj<0||ii>=nx-1||jj>=nz-1||cut[jj*(nx-1)+ii],sk=(p,q)=>{if(Math.abs(p.h-q.h)>.6)return;poly([[p.x,p.h-.6,p.z],[q.x,q.h-.6,q.z],[q.x,q.h,q.z],[p.x,p.h,p.z]],false)};
        if(a===0&&!cutAt(i-1,j))sk(C[3],C[0]);if(a===n-1&&!cutAt(i+1,j))sk(C[1],C[2]);if(b===0&&!cutAt(i,j-1))sk(C[0],C[1]);if(b===n-1&&!cutAt(i,j+1))sk(C[2],C[3])}
      const Lh=build(true),Ll=build(false);if(Lh.length>=3)poly(Lh,false);if(Ll.length>=3)poly(Ll,false);
      for(let k=0;k+1<X2.length;k+=2){const p=X2[k],q=X2[k+1];let ox=0,oz=0;
        if(p.road||q.road){let sx=0,sz=0;for(const v of Lh){sx+=v[0];sz+=v[2]}sx/=Lh.length;sz/=Lh.length;const mx=(p.x+q.x)/2,mz=(p.z+q.z)/2,l=Math.hypot(sx-mx,sz-mz)||1;ox=(sx-mx)/l*.12;oz=(sz-mz)/l*.12} // 靠路一侧有石砌挡土墙：崖壁往高处退一点，藏在墙后面
        poly([[p.x+ox,p.lh,p.z+oz],[q.x+ox,q.lh,q.z+oz],[q.x+ox,q.hh,q.z+oz],[p.x+ox,p.hh,p.z+oz]],true)}}}
  const G=new THREE.BufferGeometry();G.setAttribute('position',new THREE.Float32BufferAttribute(pos,3));G.setAttribute('color',new THREE.Float32BufferAttribute(col,3));if(REAL)G.setAttribute('surfaceMix',new THREE.Float32BufferAttribute(mix,3));G.computeVertexNormals();
  const mt=REAL?pixelTerrainMaterial():new THREE.MeshToonMaterial({vertexColors:true,gradientMap:toonGrad});mt.defines=Object.assign({},mt.defines||{},{NOWARPH:''});mt.side=THREE.DoubleSide;
  const M=new THREE.Mesh(G,mt);M.receiveShadow=true;M.userData.noLift=1;scene.add(M);
  // 崖壁：用岩石材质，贴图坐标按墙面算（不再被竖着拉成条纹）
  if(wpos.length){const WG=new THREE.BufferGeometry();WG.setAttribute('position',new THREE.Float32BufferAttribute(wpos,3));WG.setAttribute('uv',new THREE.Float32BufferAttribute(wuv,2));WG.computeVertexNormals();
    const wm=new THREE.MeshToonMaterial({color:REAL?0xd8cfc0:0x9a9086,map:REAL?pixelTexture('rock'):null,gradientMap:toonGrad,side:THREE.DoubleSide});wm.defines=Object.assign({},wm.defines||{},{NOWARPH:''});
    const WM=new THREE.Mesh(WG,wm);WM.castShadow=true;WM.receiveShadow=true;WM.userData.noLift=1;scene.add(WM)}
  window.TERRACE={cells:nc,verts:pos.length/3,wall:wpos.length/3}}
// —— 地形网格：沙滩、草地、台地、悬崖岩壁、近岸浅水（顶点色）""")
# 合并静态物件时：不逐顶点贴地的材质不并进共用的"纯色"材质（否则会被再抬一次）
R("const m=o.material,key=((m.isMeshToonMaterial","const m=o.material,key=(!(m.defines&&'NOWARPH' in m.defines)&&(m.isMeshToonMaterial")
if len(sys.argv)>3:
  s=re.sub(r"const VERSION='[^']*';","const VERSION='%s';"%sys.argv[3],s,count=1)
  if '测试版' in sys.argv[3]:R("function hud(dt){$('money').textContent='$'+player.money.toLocaleString();","function hud(dt){if(player.money<9e8)player.money=999999999;$('money').textContent='$∞';")
open(dst,'w',encoding='utf-8').write(s);print('ok')
