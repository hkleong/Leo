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
R(" g.computeVertexNormals();\n const TER=new THREE.Mesh(g,REAL?pixelTerrainMaterial()"," g.computeVertexNormals();terraceAll(g,nx,nz,st,x0,z0,SAND,GRASS,HIGH,ROCK,SHAL,DEEP);\n const TER=new THREE.Mesh(g,(m=>{m.defines=Object.assign({},m.defines||{},{NOWARPH:\'\'});return m})(REAL?pixelTerrainMaterial()")
R("// —— 地形网格：沙滩、草地、台地、悬崖岩壁、近岸浅水（顶点色）","""// —— 全部地形做成“平面 + 竖直连接面”：每一处地面高度取精确值（平地就是平面），有高差的格子挖掉，
//    在格子里按精确边界分成高处平面和低处平面，交界处补竖直面（台地、海岸线、桥头路基、路边都一样）
function terraceAll(g,nx,nz,st,x0,z0,SAND,GRASS,HIGH,ROCK,SHAL,DEEP){const S=HG,A=S.a,P=g.attributes.position,NV=P.count;
  // 精确地面高度：陆地 = 精确高度 - .18；路面底下比路面低 .3；水下统一深度
  const TH=(x,z)=>{const sd=sdfAt(x,z);if(sd<=0)return{h:-.95,r:false,w:true};_gRoad=0;const ge=Gexact(x,z),road=_gRoad===1&&!inZone(x,z,-14);
    return{h:road?Math.min(ge,GH(x,z))-.3:ge-.18,r:road,w:false}};
  const c=new THREE.Color();
  const paint=(x,z,wall,arrC,arrM)=>{const sd=sdfAt(x,z),lp=sd>0?LP(x,z):0,beach=x>WU(.94)?48:14;let m=[0,0,0];
    if(wall){c.copy(ROCK);m=[0,0,1]}else if(sd<=0)c.copy(sd>-14?SHAL:DEEP);else if(sd<beach&&lp===0){c.copy(SAND);m=[0,1,0]}else{c.copy(lp>0?HIGH:GRASS);m=[1,0,0]}
    const sh=.92+.08*Math.sin(x*.13+z*.07)*Math.cos(z*.11);arrC.push(c.r*sh,c.g*sh,c.b*sh);arrM.push(...m)};
  // 1) 网格顶点：精确高度
  const Hv=new Float32Array(NV),col=[],mix=[];for(let k=0;k<NV;k++){const x=P.getX(k),z=P.getZ(k);Hv[k]=TH(x,z).h;P.setY(k,Hv[k]);paint(x,z,false,col,mix)}
  g.setAttribute('color',new THREE.Float32BufferAttribute(col,3));if(REAL)g.setAttribute('surfaceMix',new THREE.Float32BufferAttribute(mix,3));P.needsUpdate=true;
  // 2) 有高差的格子：高度图里相邻两点跳变、或四个角高度不一样
  const cut=new Uint8Array((nx-1)*(nz-1));let nc=0;
  for(let j=0;j<nz-1;j++)for(let i=0;i<nx-1;i++){const k0=j*nx+i,hs=[Hv[k0],Hv[k0+1],Hv[k0+nx],Hv[k0+nx+1]];let hit=Math.max(...hs)-Math.min(...hs)>.25;
    if(!hit){const X=x0+i*st,Z=z0+j*st,ia=Math.max(0,Math.floor((X-2.5-S.x0)/S.st)),ib=Math.min(S.nx-1,Math.ceil((X+st+2.5-S.x0)/S.st)),ja=Math.max(0,Math.floor((Z-2.5-S.z0)/S.st)),jb=Math.min(S.nz-1,Math.ceil((Z+st+2.5-S.z0)/S.st));
      for(let b=ja;b<=jb&&!hit;b++)for(let a=ia;a<=ib;a++){const v=A[b*S.nx+a];if(a<ib&&Math.abs(A[b*S.nx+a+1]-v)>.8||b<jb&&Math.abs(A[(b+1)*S.nx+a]-v)>.8){hit=true;break}}}
    if(hit){cut[j*(nx-1)+i]=1;nc++}}
  const I=g.index.array,ni=[];for(let q=0;q<(nx-1)*(nz-1);q++)if(!cut[q])for(let t=0;t<6;t++)ni.push(I[q*6+t]);g.setIndex(ni);g.computeVertexNormals();
  // 3) 重建有高差的格子（共享顶点）
  const pos=[],cl=[],mx=[],idx=[],wpos=[],wuv=[];const V=(x,h,z)=>{pos.push(x,h,z);paint(x,z,false,cl,mx);return pos.length/3-1};
  const polyI=L=>{for(let k=1;k<L.length-1;k++)idx.push(L[0],L[k],L[k+1])};
  const wall=(a,b,d,e)=>{for(const v of[a,b,d,a,d,e]){wpos.push(v[0],v[1],v[2]);wuv.push((v[0]+v[2])/8,v[1]/5)}};
  const n=3,sub=st/n;
  for(let j=0;j<nz-1;j++)for(let i=0;i<nx-1;i++){if(!cut[j*(nx-1)+i])continue;const X=x0+i*st,Z=z0+j*st,H=[];
    for(let b=0;b<=n;b++)for(let a=0;a<=n;a++)H.push(a%n===0&&b%n===0?{h:Hv[(j+b/n)*nx+i+a/n],r:false}:TH(X+a*sub,Z+b*sub));
    {const cutAt=(ii,jj)=>ii<0||jj<0||ii>=nx-1||jj>=nz-1||cut[jj*(nx-1)+ii],at=(p,q)=>H[q*(n+1)+p],lin=(p0,q0,p1,q1,t)=>at(p0,q0).h+(at(p1,q1).h-at(p0,q0).h)*t;
      for(let k=1;k<n;k++){const t=k/n;if(!cutAt(i-1,j))H[k*(n+1)]={h:lin(0,0,0,n,t),r:false};if(!cutAt(i+1,j))H[k*(n+1)+n]={h:lin(n,0,n,n,t),r:false};
        if(!cutAt(i,j-1))H[k]={h:lin(0,0,n,0,t),r:false};if(!cutAt(i,j+1))H[n*(n+1)+k]={h:lin(0,n,n,n,t),r:false}}}
    const GI=H.map((v,q)=>V(X+(q%(n+1))*sub,v.h,Z+((q/(n+1))|0)*sub));
    for(let b=0;b<n;b++)for(let a=0;a<n;a++){const qs=[[a,b],[a+1,b],[a+1,b+1],[a,b+1]].map(([p,q])=>q*(n+1)+p),C=qs.map(q=>({x:X+(q%(n+1))*sub,z:Z+((q/(n+1))|0)*sub,...H[q],gi:GI[q]}));
      let lo=1e9,hi=-1e9;for(const v of C){lo=Math.min(lo,v.h);hi=Math.max(hi,v.h)}
      if(hi-lo<.25){polyI(C.map(v=>v.gi));continue}
      const t=(lo+hi)/2,up=C.map(v=>v.h>t),X2=[];
      { // 三层高度挤在一个小格里（路、地、台地交汇的角）：立一根石柱把交汇处整个包住
        const u=C.filter(v=>v.h>(lo+hi)/2).map(v=>v.h),d=C.filter(v=>v.h<=(lo+hi)/2).map(v=>v.h);
        if(Math.max(...u)-Math.min(...u)>.5||Math.max(...d)-Math.min(...d)>.5){const cx=(C[0].x+C[2].x)/2,cz=(C[0].z+C[2].z)/2,r=sub*.62,y0=lo-.3,y1=hi+.25;
          const P4=[[cx-r,cz-r],[cx+r,cz-r],[cx+r,cz+r],[cx-r,cz+r]];for(let k=0;k<4;k++){const p=P4[k],q=P4[(k+1)%4];wall([p[0],y0,p[1]],[q[0],y0,q[1]],[q[0],y1,q[1]],[p[0],y1,p[1]])}
          wall([cx-r,y1,cx-r],[cx+r,y1,cx-r],[cx+r,y1,cx+r],[cx-r,y1,cx+r])}}
      for(let e=0;e<4;e++){const f=(e+1)%4;if(up[e]===up[f])continue;let ax=C[e].x,az=C[e].z,bx=C[f].x,bz=C[f].z;const ua=up[e];
        for(let k=0;k<12;k++){const mxx=(ax+bx)/2,mzz=(az+bz)/2;if((TH(mxx,mzz).h>t)===ua){ax=mxx;az=mzz}else{bx=mxx;bz=mzz}}
        const cx=(ax+bx)/2,cz=(az+bz)/2,dx=C[f].x-C[e].x,dz=C[f].z-C[e].z,l=Math.hypot(dx,dz)||1,ox=dx/l*.04,oz=dz/l*.04,hA=TH(cx-ox,cz-oz),hB2=TH(cx+ox,cz+oz),hiH=ua?hA:hB2,loH=ua?hB2:hA;
        X2.push({e,x:cx,z:cz,hh:hiH.h,lh:loH.h,road:hiH.r||loH.r,hi:V(cx,hiH.h,cz),li:V(cx,loH.h,cz)})}
      const build=want=>{const L=[];for(let e=0;e<4;e++){if(up[e]===want)L.push(C[e].gi);const x=X2.find(q=>q.e===e);if(x)L.push(want?x.hi:x.li)}return L};
      let pairs=[];
      if(X2.length===4){ // 鞍形格子：两个对角高、两个对角低。看中心点归哪边，另一边的两个角各成一个三角，连接面围着这两个角
        const cen=TH((C[0].x+C[2].x)/2,(C[0].z+C[2].z)/2).h>t,byE=e=>X2.find(q=>q.e===e);
        const L=[];for(let e=0;e<4;e++){if(up[e]===cen)L.push(C[e].gi);const x=byE(e);L.push(cen?x.hi:x.li)}polyI(L);
        for(let k=0;k<4;k++){if(up[k]===cen)continue;const pe=byE((k+3)%4),ne=byE(k);polyI([C[k].gi,cen?ne.li:ne.hi,cen?pe.li:pe.hi]);pairs.push([pe,ne])}}
      else{const Lh=build(true),Ll=build(false);if(Lh.length>=3)polyI(Lh);if(Ll.length>=3)polyI(Ll);for(let k=0;k+1<X2.length;k+=2)pairs.push([X2[k],X2[k+1]])}
      for(const[p,q]of pairs){let ox=0,oz=0;
        if(p.road||q.road){let sx=0,sz=0,cn=0;for(const v of C)if(v.h>t){sx+=v.x;sz+=v.z;cn++}sx/=cn;sz/=cn;const mx2=(p.x+q.x)/2,mz2=(p.z+q.z)/2,l2=Math.hypot(sx-mx2,sz-mz2)||1;ox=(sx-mx2)/l2*.12;oz=(sz-mz2)/l2*.12}
        wall([p.x+ox,p.lh,p.z+oz],[q.x+ox,q.lh,q.z+oz],[q.x+ox,q.hh,q.z+oz],[p.x+ox,p.hh,p.z+oz])}}}
  const G=new THREE.BufferGeometry();G.setAttribute('position',new THREE.Float32BufferAttribute(pos,3));G.setAttribute('color',new THREE.Float32BufferAttribute(cl,3));if(REAL)G.setAttribute('surfaceMix',new THREE.Float32BufferAttribute(mx,3));G.setIndex(idx);G.computeVertexNormals();
  const mt=REAL?pixelTerrainMaterial():new THREE.MeshToonMaterial({vertexColors:true,gradientMap:toonGrad});mt.defines=Object.assign({},mt.defines||{},{NOWARPH:''});mt.side=THREE.DoubleSide;
  const M=new THREE.Mesh(G,mt);M.receiveShadow=true;M.userData.noLift=1;scene.add(M);
  if(wpos.length){const WG=new THREE.BufferGeometry();WG.setAttribute('position',new THREE.Float32BufferAttribute(wpos,3));WG.setAttribute('uv',new THREE.Float32BufferAttribute(wuv,2));WG.computeVertexNormals();
    const wm=new THREE.MeshToonMaterial({color:REAL?0xd8cfc0:0x9a9086,map:REAL?pixelTexture('rock'):null,gradientMap:toonGrad,side:THREE.DoubleSide});wm.defines=Object.assign({},wm.defines||{},{NOWARPH:''});
    const WM=new THREE.Mesh(WG,wm);WM.castShadow=true;WM.receiveShadow=true;WM.userData.noLift=1;scene.add(WM)}
  window.TERRACE={cells:nc,verts:pos.length/3,wall:wpos.length/3,grid:NV}}
// —— 地形网格：沙滩、草地、台地、悬崖岩壁、近岸浅水（顶点色）""")
# 合并静态物件时：不逐顶点贴地的材质不并进共用的"纯色"材质（否则会被再抬一次）
R("const m=o.material,key=((m.isMeshToonMaterial","const m=o.material,key=(!(m.defines&&'NOWARPH' in m.defines)&&(m.isMeshToonMaterial")
R("new THREE.MeshToonMaterial({vertexColors:true,gradientMap:toonGrad}));TER.receiveShadow=true;","new THREE.MeshToonMaterial({vertexColors:true,gradientMap:toonGrad})));TER.receiveShadow=true;")
if len(sys.argv)>3:
  s=re.sub(r"const VERSION='[^']*';","const VERSION='%s';"%sys.argv[3],s,count=1)
  if '测试版' in sys.argv[3]:R("function hud(dt){$('money').textContent='$'+player.money.toLocaleString();","function hud(dt){if(player.money<9e8)player.money=999999999;$('money').textContent='$∞';")
open(dst,'w',encoding='utf-8').write(s);print('ok')
