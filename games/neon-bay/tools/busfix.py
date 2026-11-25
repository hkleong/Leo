# 在线上版 index.html 上打补丁：巴士靠边停站、站前不停车、NPC 坐巴士
import sys
src,dst,ver=sys.argv[1],sys.argv[2],sys.argv[3]
s=open(src,encoding='utf-8').read()
def R(a,b,n=1):
  global s
  c=s.count(a);assert c==n,(a[:80],c);s=s.replace(a,b)
R("const VERSION='v0.27.0';","const VERSION='%s';"%ver)
# 1) 巴士靠站：进站前 30 米开始往路边靠到停车道，停稳上下客，出站再并回车道
R("""function busTick(c,dt){const B=c.bus;
  if(B.wait>0){""","""function busTick(c,dt){const B=c.bus;
  if(BUS.stopAt.has(B.k)){const ln=laneOf(c.ni-c.dx,c.nj-c.dz,c.ni,c.nj),prog=(c.x-ln.ax)*ln.ux+(c.z-ln.az)*ln.uz,d=ln.L*.5-prog;
    if(d<34&&d>-28&&ln.L>70)return busBay(c,dt,ln,prog,d)}
  if(B.wait>0){""")
R("// 每帧（车辆循环里）：快到站减速，到站停 WAIT 秒","""// 靠站段由这里直接控制位置：横向偏移按平滑曲线从车道中线移到停车道（PARK_O），停稳后再移回
const sstep=t=>{t=clamp(t,0,1);return t*t*(3-2*t)},BAYX=()=>PARK_O-LANE;
function busBay(c,dt,ln,prog,d){const B=c.bus,s=BUS.stops[BUS.stopAt.get(B.k)],nx=ln.uz,nz=-ln.ux;
  if(B.wait>0){B.wait-=dt;c.speed=0;if(B.wait>1.5)for(const p of s.q||[])if(peds.includes(p)&&p.busq&&p.busq.st==='wait'){p.busq.st='board';p.busq.bus=c;p.busq.delay=Math.random()*1.2}
    if(BUS.peds.some(p=>p.busq&&p.busq.bus===c&&p.busq.st==='board'))B.wait=Math.max(B.wait,.4);
    if(B.wait<=0){B.left=B.k;if(player.ride===c){const n=busNextStop(c);toast('巴士开动了 · 下一站：'+(n?n.name:''))}}return true}
  if(B.left!==B.k){if(d<.5){B.wait=BUS.WAIT;c.speed=0;busArrive(c,s);if(player.ride===c)toast('到站：'+s.name+'  （按 E 下车）');else if(Math.hypot(c.x-player.x,c.z-player.z)<60)beep(660,.12,'sine',.05);return true}
    c.speed=Math.min(Math.max(c.speed,3),Math.max(2,Math.sqrt(2*2.6*Math.max(0,d-.3))),c.speed+4*dt)}
  else{let blk=false;for(const o of cars)if(o!==c&&!o.dead){const rx2=o.x-c.x,rz2=o.z-c.z,f=rx2*ln.ux+rz2*ln.uz,sd=Math.abs(rx2*nx+rz2*nz);if(f>0&&f<14&&sd<2.6){blk=true;break}}
    c.speed=blk?Math.max(0,c.speed-12*dt):Math.min(13,c.speed+3*dt)}
  const off=p=>{const dd=ln.L*.5-p;return BAYX()*(dd>0?sstep(1-dd/30):sstep(1+dd/24))},np=prog+c.speed*dt,o=off(np),g=(off(np+1)-off(np-1))/2;
  c.x=ln.ax+ln.ux*np+nx*o;c.z=ln.az+ln.uz*np+nz*o;c.h=Math.atan2(ln.ux+nx*g,ln.uz+nz*g);c.mesh.position.x=c.x;c.mesh.position.z=c.z;c.mesh.rotation.y=c.h;return true}
// 车门（右侧前门）在世界里的位置
function busDoor(c){const fx=Math.sin(c.h),fz=Math.cos(c.h),rx2=Math.cos(c.h),rz2=-Math.sin(c.h);return{x:c.x+fx*3.2+rx2*2.6,z:c.z+fz*3.2+rz2*2.6}}
// 到站：车上的人下来几个，站台上等车的人走过去上车
function busArrive(c,s){const B=c.bus;B.pax=B.pax??((Math.random()*5)|0)+1;const n=Math.min(B.pax,((Math.random()*3)|0)+(Math.random()<.6?1:0));
  for(let k=0;k<n;k++){B.pax--;setTimeout(()=>{if(!cars.includes(c))return;const dr=busDoor(c),p=busPed(dr.x,dr.z);if(!p)return;const t=(Math.random()-.5)*8,ux=Math.sin(c.h),uz=Math.cos(c.h);
    p.busq={st:'off',tx:s.wx+ux*t,tz:s.wz+uz*t,bus:c}},k*700+300)}
  for(const p of s.q||[])if(peds.includes(p)&&p.busq&&p.busq.st==='wait'){p.busq.st='board';p.busq.bus=c;p.busq.delay=Math.random()*1.2}}
function busPed(x,z){_noPair=true;const look=NPC_KEYS[(Math.random()*NPC_KEYS.length)|0];const p=spawnPed(x,z,look);_noPair=false;if(!p)return null;
  if(p.bench){p.bench.used=null;p.bench=null}p.partner=null;p.act='walk';p.onPath=false;p.job=null;BUS.peds.push(p);return p}
// 等车 / 上车 / 下车 的行人：返回 true 表示这一帧由这里处理
function busPedTick(p,dt){const q=p.busq;if(p.flee>0){p.busq=null;return false}
  const walkTo=(tx,tz,sp)=>{const dx=tx-p.x,dz=tz-p.z,d=Math.hypot(dx,dz);if(d>.05){p.rot=Math.atan2(dx,dz);const m=Math.min(d,sp*dt);p.x+=dx/d*m;p.z+=dz/d*m}return d};
  let st='idle',k=0;
  if(q.st==='wait'){p.rot+=angDiff(q.face,p.rot)*Math.min(1,dt*4);st=p.t%9<3?'phone':'idle'}
  else if(q.st==='board'){if((q.delay-=dt)>0){st='idle'}else{const c=q.bus;if(!cars.includes(c)||c.dead||!(c.bus&&c.bus.wait>0)){q.st='wait';return true}
    const dr=busDoor(c);if(walkTo(dr.x,dr.z,3)<1.2){c.bus.pax=Math.min(24,(c.bus.pax||0)+1);dropPed(p);return true}st='walk';k=1}}
  else if(q.st==='off'){if(walkTo(q.tx,q.tz,2.4)<.4){p.busq=null;p.act='walk';p.dir=Math.random()<.5?1:-1;pedSnap(p);return false}st='walk';k=1}
  p.mesh.position.set(p.x,0,p.z);p.mesh.rotation.y=p.rot;pose(p.mesh,st,p.t,k);return true}
// 站台上补等车的人：玩家附近的站各 1~4 人；离远了收掉
let busPedT=0;function busPedsUpd(dt){if((busPedT-=dt)>0)return;busPedT=1.5;BUS.peds=BUS.peds.filter(p=>peds.includes(p)&&!p.dead);
  for(const s of BUS.stops){s.q=(s.q||[]).filter(p=>peds.includes(p)&&p.busq&&p.busq.st!=='off');const d=Math.hypot(s.sx-player.x,s.sz-player.z);
    if(d>260){for(const p of s.q)dropPed(p);s.q=[];s.want=null;continue}
    if(d>170)continue;if(s.want==null)s.want=1+((Math.random()*4)|0);if(BUS.buses.some(c=>c.bus&&c.bus.wait>0&&Math.hypot(c.x-s.bx,c.z-s.bz)<25)){s.cool=25;continue}if((s.cool=(s.cool||0)-1.5)>0)continue;
    const waiting=s.q.filter(p=>p.busq.st==='wait').length;if(waiting<s.want&&d>50){s.cool=6;const ux=s.ux,uz=s.uz,t=(Math.random()-.5)*6,o=Math.hypot(s.sx-s.cx,s.sz-s.cz)-1.6+Math.random()*.5,x=s.cx+s.nx*o+ux*t,z=s.cz+s.nz*o+uz*t,p=busPed(x,z);
      if(p){p.busq={st:'wait',face:Math.atan2(-s.nx,-s.nz)+(Math.random()-.5)*.8};s.q.push(p)}}
    if(Math.random()<.04)s.want=1+((Math.random()*4)|0)}}
// 每帧（车辆循环里）：快到站减速，到站停 WAIT 秒""")
# 站台数据：记下路段中点、方向，站前路面刷一块巴士专用区（盖掉停车格），并把那里已经停着的车挪走
R("""    s.sx=cx+nx*(RD/2+3.4);s.sz=cz+nz*(RD/2+3.4);""","""    s.cx=cx;s.cz=cz;s.nx=nx;s.nz=nz;s.ux=ln.ux;s.uz=ln.uz;s.bx=cx+nx*PARK_O;s.bz=cz+nz*PARK_O;busBayPaint(s);
    for(const sp of PARK)if(Math.hypot(sp.x-s.bx,sp.z-s.bz)<20&&sp.used&&!sp.used.driver&&sp.used!==player.car){removeCar(sp.used);sp.used=null}
    s.sx=cx+nx*(RD/2+1.3);s.sz=cz+nz*(RD/2+1.3);""")
R("function busNext(c){","""function busBayPaint(s){const ry=Math.atan2(s.ux,s.uz),L=30,W=4.2;const pl=(w,l,mat,y,o=0,f=0)=>{const g=new THREE.PlaneGeometry(w,l,1,Math.max(1,Math.ceil(l/6)));g.rotateX(-Math.PI/2);const m=new THREE.Mesh(g,mat);m.rotation.y=ry;
    m.position.set(s.bx+s.nx*o+s.ux*f,y,s.bz+s.nz*o+s.uz*f);m.userData.noLift=0;scene.add(m);return m};
  const AM=asphalt.clone();AM.polygonOffset=true;AM.polygonOffsetFactor=-1;AM.polygonOffsetUnits=-2;pl(W,L,AM,.049);const Y=new THREE.MeshBasicMaterial({color:0xf2c230,polygonOffset:true,polygonOffsetFactor:-2,polygonOffsetUnits:-4});for(const o of[-W/2,W/2])pl(.25,L,Y,.0499,o);for(const f of[-L/2,L/2])pl(W,.25,Y,.0499,0,f);
  const cv=document.createElement('canvas');cv.width=256;cv.height=96;const g=cv.getContext('2d');g.fillStyle='#f2c230';g.font='bold 80px sans-serif';g.textAlign='center';g.textBaseline='middle';g.fillText('BUS',128,52);
  const t=new THREE.CanvasTexture(cv);const m=pl(3.4,4.2,new THREE.MeshBasicMaterial({map:t,transparent:true,depthWrite:false,polygonOffset:true,polygonOffsetFactor:-2,polygonOffsetUnits:-4}),.0499,0,-L/2+5);m.geometry.rotateY(Math.PI)}
function busNext(c){""")
R("RT.pop();BUS.route=RT;","RT.pop();BUS.peds=[];BUS.route=RT;")
# 主循环：每帧更新等车的人
R("function busUpd(dt){if(!BUS.ready){","function busUpd(dt){if(BUS.ready)busPedsUpd(dt);if(!BUS.ready){")
# 行人更新：坐巴士的人走自己的逻辑（在被车撞的判定之后）
R("  if(p.gang&&gangPed(p,dt,pd))return;","  if(p.busq&&busPedTick(p,dt))return;\n  if(p.gang&&gangPed(p,dt,pd))return;")
# 2) 巴士站前不刷路边停车
R("    if(cars.some(c=>!c.dead&&Math.hypot(c.x-sp.x,c.z-sp.z)<7))continue;if(Math.random()<.35)continue;","    if(cars.some(c=>!c.dead&&Math.hypot(c.x-sp.x,c.z-sp.z)<7))continue;if(Math.random()<.35)continue;if(BUS.stops&&BUS.stops.some(s=>Math.hypot(s.bx-sp.x,s.bz-sp.z)<20))continue;")
R("function parkSpot(minD,maxD){const c=PARK.filter(sp=>{if(sp.used)return false;","function parkSpot(minD,maxD){const c=PARK.filter(sp=>{if(sp.used)return false;if(BUS.stops&&BUS.stops.some(s=>Math.hypot(s.bx-sp.x,s.bz-sp.z)<20))return false;")
# 3) 线路站台挪到人行道上（原来在人行道外侧，高台街区会埋进挡土墙、平地街区会被院子和楼盖住）
R("function busStop(x,z,ry){if(guard('bus',x,z,1.5))return;","function busStop(x,z,ry,gm=1.5){if(guard('bus',x,z,gm))return;")
R("busStop(s.sx,s.sz,Math.atan2(-nx,-nz));","busStop(s.sx,s.sz,Math.atan2(-nx,-nz),.6);")
# 4) 线路站点提前算（地形生成之前），站后面那段街区往后退 SB_D 米，留出和路面同高的站前空地
i=s.index("function busBuild(){");j=s.index("  // 站台：放在车道这一侧的人行道上，面朝马路",i);head=s[i:j]
old_end="RT.pop();BUS.peds=[];BUS.route=RT;BUS.stops=stops;stops.forEach((s,q)=>BUS.stopAt.set(s.k,q));"
assert head.count(old_end)==1
pre=head.replace("function busBuild(){","function busPre(){").replace("BUS.dbg","BP.dbg").replace(old_end,"RT.pop();BP.RT=RT;BP.stops=stops;busSB()}\n")
assert 'BUS.' not in pre,pre[pre.find('BUS.')-50:pre.find('BUS.')+50]
s=s[:i]+"function busBuild(){const RT=BP.RT,stops=BP.stops;BUS.dbg=BP.dbg;if(!RT)return;BUS.peds=[];BUS.route=RT;BUS.stops=stops;stops.forEach((s,q)=>BUS.stopAt.set(s.k,q));\n"+s[j:]
early=pre+r"""// 站前空地：沿路段 ±22 米、从人行道外沿往里 SB_D 米，地面和路面一样高
function busSB(){for(const s of BP.stops){const ax=rx(s.a[0]),az=rz(s.a[1]),L=Math.hypot(rx(s.b[0])-ax,rz(s.b[1])-az),ln={ux:(rx(s.b[0])-ax)/L,uz:(rz(s.b[1])-az)/L,L},nx=ln.uz,nz=-ln.ux,cx=(ax+rx(s.b[0]))/2,cz=(az+rz(s.b[1]))/2,hl=Math.min(22,ln.L/2-BAND-4);if(hl<8)continue;
  const P=[];for(const a of[-hl,hl])for(const b of[BAND-.6,BAND+SB_D])P.push([cx+ln.ux*a+nx*b,cz+ln.uz*a+nz*b]);
  SBR.push({x0:Math.min(...P.map(p=>p[0])),x1:Math.max(...P.map(p=>p[0])),z0:Math.min(...P.map(p=>p[1])),z1:Math.max(...P.map(p=>p[1])),h:hN(s.a[0],s.a[1]),nx,nz})}}
const inSB=(x,z,m=0)=>{for(const r of SBR)if(x>r.x0-m&&x<r.x1+m&&z>r.z0-m&&z<r.z1+m)return r;return null};
// 一个矩形减掉若干矩形，剩下的拆成小矩形 [x0,x1,z0,z1]
function rectMinus(r,holes){let out=[r];for(const h of holes){const nx=[];for(const q of out){const a=Math.max(q[0],h.x0),b=Math.min(q[1],h.x1),c=Math.max(q[2],h.z0),d=Math.min(q[3],h.z1);if(a>=b||c>=d){nx.push(q);continue}
  if(q[0]<a)nx.push([q[0],a,q[2],q[3]]);if(b<q[1])nx.push([b,q[1],q[2],q[3]]);if(q[2]<c)nx.push([a,b,q[2],c]);if(d<q[3])nx.push([a,b,d,q[3]])}out=nx}return out.filter(q=>q[1]-q[0]>.3&&q[3]-q[2]>.3)}
var SBR=[];const SB_D=6,BP={};try{busPre()}catch(e){window.__bpErr=String(e)+' '+(e.stack||'').split('\n')[1]}
"""
R("const HG=(()=>{",early+"const HG=(()=>{")
R("function Gexact(x,z){","function Gexact(x,z){for(const r of SBR)if(x>r.x0&&x<r.x1&&z>r.z0&&z<r.z1){_gRoad=1;return r.h}")
# 街区挡土墙：站前空地那段不砌（空地周围的墙由路边挡土墙自动砌）
R("if(Math.abs(ga-h)<.3&&Math.abs(gb-h)<.3)continue;","if(inSB((pa[0]+pb[0])/2,(pa[1]+pb[1])/2,.6))continue;if(Math.abs(ga-h)<.3&&Math.abs(gb-h)<.3)continue;")
# 街区挡土墙在空地两端：碰到空地的那段切细（每段 25 厘米），只去掉真正在空地里的部分，不留缺口
R("    for(let k=0;k<n;k++){const t0=k/n,t1=(k+1)/n,pa=[ax+(bx-ax)*t0,az+(bz-az)*t0],pb=[ax+(bx-ax)*t1,az+(bz-az)*t1];\n      const ga=Gexact(",
  "    const TT=[];for(let k=0;k<n;k++){const a0=k/n,a1=(k+1)/n,ma=[ax+(bx-ax)*a0,az+(bz-az)*a0],mb=[ax+(bx-ax)*a1,az+(bz-az)*a1];if(SBR.length&&(inSB(ma[0],ma[1],1)||inSB(mb[0],mb[1],1)||inSB((ma[0]+mb[0])/2,(ma[1]+mb[1])/2,1))){for(let q=0;q<16;q++)TT.push([a0+(a1-a0)*q/16,a0+(a1-a0)*(q+1)/16])}else TT.push([a0,a1])}\n    for(const[t0,t1]of TT){const pa=[ax+(bx-ax)*t0,az+(bz-az)*t0],pb=[ax+(bx-ax)*t1,az+(bz-az)*t1];\n      const ga=Gexact(")
R("if(inSB((pa[0]+pb[0])/2,(pa[1]+pb[1])/2,.6))continue;if(Math.abs(ga-h)<.3","if(inSB((pa[0]+pb[0])/2,(pa[1]+pb[1])/2,-.3))continue;if(Math.abs(ga-h)<.3")
# 站前空地在高台上：直接砌三面墙（背墙 + 两头端墙），贴图坐标和街区挡土墙一样
R("// —— 路边挡土墙（不限街区）","""// —— 站前空地的三面挡土墙
{const pos=[];const seg=(ax,az,bx,bz,ox,oz,rh)=>{const L=Math.hypot(bx-ax,bz-az),n=Math.max(1,Math.ceil(L/2));for(let k=0;k<n;k++){const pa=[ax+(bx-ax)*k/n,az+(bz-az)*k/n],pb=[ax+(bx-ax)*(k+1)/n,az+(bz-az)*(k+1)/n];
    const la=Gexact(pa[0]+ox,pa[1]+oz),lb=Gexact(pb[0]+ox,pb[1]+oz);if(la<rh+1&&lb<rh+1)continue;const lo=rh-.4;pos.push(pa[0],lo,pa[1],pb[0],lo,pb[1],pb[0],lb+.25,pb[1],pa[0],lo,pa[1],pb[0],lb+.25,pb[1],pa[0],la+.25,pa[1])}};
  for(const r of SBR){const e=1.2;if(r.nx){const bx=r.nx>0?r.x1:r.x0,xa=r.nx>0?r.x0+.6:r.x0,xb=r.nx>0?r.x1:r.x1-.6;seg(bx,r.z0,bx,r.z1,r.nx*e,0,r.h);seg(xa,r.z0,xb,r.z0,0,-e,r.h);seg(xa,r.z1,xb,r.z1,0,e,r.h)}
    else{const bz=r.nz>0?r.z1:r.z0,za=r.nz>0?r.z0+.6:r.z0,zb=r.nz>0?r.z1:r.z1-.6;seg(r.x0,bz,r.x1,bz,0,r.nz*e,r.h);seg(r.x0,za,r.x0,zb,-e,0,r.h);seg(r.x1,za,r.x1,zb,e,0,r.h)}}
  // 转角立一根方柱，盖住墙和墙之间的接缝
  for(const r of SBR){const C=r.nx?[[r.nx>0?r.x0+.6:r.x1-.6,r.z0],[r.nx>0?r.x0+.6:r.x1-.6,r.z1],[r.nx>0?r.x1:r.x0,r.z0],[r.nx>0?r.x1:r.x0,r.z1]]:[[r.x0,r.nz>0?r.z0+.6:r.z1-.6],[r.x1,r.nz>0?r.z0+.6:r.z1-.6],[r.x0,r.nz>0?r.z1:r.z0],[r.x1,r.nz>0?r.z1:r.z0]];
    for(const[x,z]of C){let top=-1e9;for(const[dx,dz]of[[1.3,1.3],[1.3,-1.3],[-1.3,1.3],[-1.3,-1.3]])top=Math.max(top,Gexact(x+dx,z+dz));if(top<r.h+1)continue;const H=top+.55-(r.h-.4);
      const p=new THREE.Mesh(new THREE.BoxGeometry(1.6,H,1.6),wallMat);p.position.set(x,r.h-.4+H/2,z);p.castShadow=p.receiveShadow=true;p.userData.noLift=1;scene.add(p)}}
  if(pos.length){const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(pos,3));const uv=[];for(let i=0;i<pos.length;i+=3)uv.push((pos[i]+pos[i+2])/8,pos[i+1]/5);
    g.setAttribute('uv',new THREE.Float32BufferAttribute(uv,2));g.computeVertexNormals();const m=new THREE.Mesh(g,wallMat);m.castShadow=m.receiveShadow=true;m.userData.noLift=1;scene.add(m)}}
// —— 路边挡土墙（不限街区）""")
# 高台街区台面挖掉空地，空地铺一块贴路面高度的人行道
R("pl(W-5,D-5,cx,cz,.052);","for(const q of rectMinus([cx-(W-5)/2,cx+(W-5)/2,cz-(D-5)/2,cz+(D-5)/2],SBR))pl(q[1]-q[0],q[3]-q[2],(q[0]+q[1])/2,(q[2]+q[3])/2,.052);for(const r of SBR){const a=Math.max(r.x0,cx-W/2-2),b=Math.min(r.x1,cx+W/2+2),c=Math.max(r.z0,cz-D/2-2),d=Math.min(r.z1,cz+D/2+2);if(b>a+.3&&d>c+.3)pl(b-a,d-c,(a+b)/2,(c+d)/2,.048)}")
# 楼、住宅：压到空地就不盖
R("function lotOnRoad(x,z,w,d){for(let u=-.5;u<=.5;u+=.125)for(let v=-.5;v<=.5;v+=.125){const px=x+u*(w-2),pz=z+v*(d-2);if(onRoad(px,pz,.5))return true}return false}",
  "function lotOnRoad(x,z,w,d){for(let u=-.5;u<=.5;u+=.125)for(let v=-.5;v<=.5;v+=.125){const px=x+u*(w-2),pz=z+v*(d-2);if(onRoad(px,pz,.5)||inSB(px,pz,1))return true}return false}")
# 小物件（长椅、消防栓、路灯等）不放在空地上
R("const guard=(name,x,z,m)=>{if(onRoad(x,z,m)||inZone(x,z,3)","const guard=(name,x,z,m)=>{if(name!=='bus'&&inSB(x,z,.5)||onRoad(x,z,m)||inZone(x,z,3)")
# 商业街店铺：挨着空地的那几间整栋往后挪 SB_D 米
a=s.index("function shopRow(i,j,side){");b=s.index("\nfunction ",a+10);body=s[a:b]
decl="bx=fx-s*dd/2,bz=z+w/2;";assert body.count(decl)==1
k=body.index(decl)+len(decl);import re
tail=re.sub(r'\bfx\b','FX',body[k:])
body=body[:k].replace(decl,"bz=z+w/2,FX=fx-s*(SBR.some(r=>fx>r.x0-3&&fx<r.x1+3&&z+w>r.z0&&z<r.z1)?SB_D:0),bx=FX-s*dd/2;")+tail
s=s[:a]+body+s[b:]
# 站台放进空地里，等车的人站在站台前
R("    s.sx=cx+nx*(RD/2+1.3);s.sz=cz+nz*(RD/2+1.3);","    s.sx=cx+nx*(RD/2+(inSB(cx+nx*(BAND+2),cz+nz*(BAND+2))?4.6:1.3));s.sz=cz+nz*(RD/2+(inSB(cx+nx*(BAND+2),cz+nz*(BAND+2))?4.6:1.3));")
# 测试版专用：金钱无限（每帧补满，界面显示 $∞）；发布线上版时不加
if '测试版' in ver:
  R("function hud(dt){$('money').textContent='$'+player.money.toLocaleString();","function hud(dt){if(player.money<9e8)player.money=999999999;$('money').textContent='$∞';")
open(dst,'w',encoding='utf-8').write(s);print('ok')
