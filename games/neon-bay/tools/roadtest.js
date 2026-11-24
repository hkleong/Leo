// 道路全覆盖试驾：多辆 NPC 车按规划好的路线把每条路双向都跑一遍，记录沿途问题
const {chromium}=require('playwright');const fs=require('fs');(async()=>{const b=await chromium.launch({args:['--use-gl=swiftshader','--ignore-gpu-blocklist']});const p=await b.newPage({viewport:{width:320,height:200}});
p.on('pageerror',e=>console.log('ERR',e.message,(e.stack||'').split('\n').slice(1,3).join(' | ')));
await p.goto('file://'+process.argv[2]);await p.waitForFunction(()=>{try{return cityReady}catch(e){return false}},null,{timeout:300000});
const NCAR=+(process.env.NCAR||8),MAXF=+(process.env.MAXF||40000);
const res=await p.evaluate(([NCAR,MAXF])=>{PERF.on=false;document.getElementById('start').click();window.T=n=>{for(let i=0;i<n;i++){last=performance.now()-33;frame();if(dlg)nextDlg()}};T(5);while(cut)T(10);T(3);
 window.renderMain=()=>{};player.hp=1e9;player.x=0;player.z=0;
 // 全部街区都生成出来（碰撞体齐全），不再卸载
 for(const j of JOBS)if(!j.built)buildJob(j);window.updStream=()=>{};
 // 红绿灯一直绿（灯是按真实时间走的，加速模拟时会显得特别长）
 window.SIMT=0;window.updLights=eval('('+updLights.toString().replace('performance.now()/1000','window.SIMT')+')');
 const nk=(i,j)=>i+','+j,ekD=(a,b)=>nk(...a)+'>'+nk(...b);
 const E=[];for(let i=0;i<=NX;i++)for(let j=0;j<=NZ;j++){if(!nodeOK(i,j))continue;for(const[a,b]of DIRS8)if(linkOK(i,j,a,b))E.push([[i,j],[i+a,j+b]])}
 const cov=new Set(),planned=new Set();
 const nbr=u=>DIRS8.filter(([a,b])=>linkOK(u[0],u[1],a,b)).map(([a,b])=>[u[0]+a,u[1]+b]);
 // BFS：从 cur（来自 prev）出发，找最近的、还没规划的有向路段的起点；尽量不掉头
 function toNearest(cur,prev,pool,strict){const Q=[[cur,prev,null]],seen=new Map([[nk(...cur)+'|'+(prev?nk(...prev):''),null]]);let h=0;
   while(h<Q.length){const[u,pv,par]=Q[h++];for(const v of nbr(u)){if(pv&&v[0]===pv[0]&&v[1]===pv[1]&&nbr(u).length>1)continue;if(strict&&pv&&turnAng(pv[0],pv[1],u[0],u[1],v[0],v[1])>=2)continue;const e=ekD(u,v);if(pool.has(e)&&!planned.has(e)){const path=[v];let n=[u,pv,par];while(n&&n[2]!==null){path.unshift(n[0]);n=n[2]}return path}
     const sk=nk(...v)+'|'+nk(...u);if(seen.has(sk))continue;seen.set(sk,1);Q.push([v,u,[u,pv,par]])}}return null}
 // 按区域分给几辆车
 const reg=e=>{const x=(rx(e[0][0])+rx(e[1][0]))/2,z=(rz(e[0][1])+rz(e[1][1]))/2;const cx=Math.min(3,Math.max(0,Math.floor((x+HALFX)/(2*HALFX)*4)));return(cx*2+(z>0?1:0))%NCAR};
 const pools=[...Array(NCAR)].map(()=>new Set());for(const e of E)pools[reg(e)].add(ekD(e[0],e[1]));
 const tours=[];for(let k=0;k<NCAR;k++){const pool=pools[k];if(!pool.size){tours.push(null);continue}const first=[...pool][0].split('>').map(s=>s.split(',').map(Number));
   let tour=[first[0],first[1]];planned.add(ekD(first[0],first[1]));let guard=0;
   while(guard++<5000){const cur=tour[tour.length-1],prev=tour[tour.length-2];const path=toNearest(cur,prev,pool,true)||toNearest(cur,prev,pool,false);if(!path)break;for(const v of path){const u=tour[tour.length-1];planned.add(ekD(u,v));tour.push(v)}}
   tours.push(tour)}
 const unplanned=E.filter(e=>!planned.has(ekD(e[0],e[1]))).map(e=>ekD(e[0],e[1]));
 // 让 AI 按路线走
 const oC=aiChoose,oP=aiPickNext;
 window.aiChoose=c=>{if(c.tour){const n=c.tour[c.tk+1];if(!n)return[-c.dx,-c.dz];return[n[0]-c.ni,n[1]-c.nj]}return oC(c)};
 const ISS=[];const add=(c,type,extra='')=>ISS.push({car:c.tid,type,x:Math.round(c.x),z:Math.round(c.z),e:c.tour&&c.tk>0&&c.tour[c.tk]?ekD(c.tour[c.tk-1],c.tour[c.tk]):'',extra,t:+(F*.05).toFixed(1),near:c.tour?JSON.stringify(c.tour.slice(Math.max(0,c.tk-3),c.tk+3)):''});
 window.aiPickNext=c=>{if(c.tour&&!c.done&&c.nd){const a=turnAng(c.ni-c.dx,c.nj-c.dz,c.ni,c.nj,c.ni+c.nd[0],c.nj+c.nd[1]);if(a>=2)add(c,'走了急弯',(a*57|0)+'°')}oP(c);if(c.tour&&!c.done){c.tk++;const w=c.tour[c.tk];if(!w||w[0]!==c.ni||w[1]!==c.nj){add(c,'偏离路线',w?nk(...w)+' vs '+nk(c.ni,c.nj):'end');c.tour=null;c.lost=1}else{cov.add(ekD(c.tour[c.tk-1],w));if(c.tk>=c.tour.length-1){c.done=1;setTimeout(()=>{},0);c.rmMe=1}}}};
 const TC=[];let F=0;
 tours.forEach((tour,k)=>{if(!tour)return;const a=tour[0],bb=tour[1],ln=laneOf(a[0],a[1],bb[0],bb[1]);const c=makeCar(ln.ax+ln.ux*(RD/2+3),ln.az+ln.uz*(RD/2+3),Math.atan2(ln.ux,ln.uz),{kind:'sedan',color:0xff00ff});
   c.driver='ai';c.target=1;c.ni=bb[0];c.nj=bb[1];c.dx=bb[0]-a[0];c.dz=bb[1]-a[1];c.nd=null;c.tour=tour;c.tk=1;c.tid=k;c.mesh.position.set(c.x,0,c.z);c.mesh.rotation.y=c.h;cov.add(ekD(a,bb));
   c.m={still:0,off:0,lastx:c.x,lastz:c.z,sp:0,h:c.h,hist:[],air:0,dist:0};TC.push(c)});
 if(typeof BUS!=='undefined')for(const bc of BUS.buses){bc.tid='bus'+BUS.buses.indexOf(bc);bc.m={still:0,off:0,lastx:bc.x,lastz:bc.z,sp:0,h:bc.h,hist:[],air:0,dist:0};TC.push(bc)}
 window.JSTK=[];for(const c of TC){let _z=c.z;Object.defineProperty(c,'z',{get(){return _z},set(v){if(Math.abs(v-_z)>2.5&&JSTK.length<12)JSTK.push([c.tid,'z',(v-_z).toFixed(1),new Error().stack.split('\n').slice(2,6).map(s=>s.trim().replace(/file:.*?html:/,'L')).join(' < ')]);_z=v},configurable:true});let _x=c.x;Object.defineProperty(c,'x',{get(){return _x},set(v){if(Math.abs(v-_x)>2.5&&JSTK.length<12)JSTK.push([c.tid,(v-_x).toFixed(1),new Error().stack.split('\n').slice(2,6).map(s=>s.trim().replace(/file:.*?html:/,'L')).join(' < ')]);_x=v},configurable:true})}
 window.MVLOG=[];const wrapF=(name)=>{const o=window[name];window[name]=function(c,...a){const x0=c.x,z0=c.z,v0=c.speed;const res=o.call(this,c,...a);const d=Math.hypot(c.x-x0,c.z-z0);if(d>2&&MVLOG.length<20)MVLOG.push([name,c.tid||c.kind,d.toFixed(1),+v0.toFixed(1),+c.speed.toFixed(1),Math.round(c.x),Math.round(c.z),c.bus?c.bus.k:'',c.bus?+c.bus.wait.toFixed(1):'',c.ni+','+c.nj+' d'+c.dx+','+c.dz,F]);return res}};
 wrapF('driveAI');wrapF('carPhysics');if(window.busTick)wrapF('busTick');
 window.CHLOG=[];{const oc=capHit;window.capHit=function(c,o){const q=oc(c,o);if(q&&q.pen>.8&&(c.bus||o.bus||c.tid!==undefined||o.tid!==undefined)&&CHLOG.length<25){const fx=Math.sin(c.h),fz=Math.cos(c.h),dx=o.x-c.x,dz=o.z-c.z;CHLOG.push([c.tid||c.kind,c.bus?'BUS':'',+c.speed.toFixed(1),'vs',o.tid||o.kind,o.bus?'BUS':'',+o.speed.toFixed(1),o.driver||'',o.parked?'P':'',o.hold?'H':'',o.evt?'EVT':'',o.police?'COP':'','前'+(dx*fx+dz*fz).toFixed(1),'侧'+(dx*fz-dz*fx).toFixed(1),'角'+Math.round(((o.h-c.h)*57%360+360)%360),'pen'+q.pen.toFixed(1),Math.round(c.x),Math.round(c.z),F])}return q}}
 const t0=performance.now();
 for(F=0;F<MAXF;F++){last=performance.now()-50;window.SIMT+=.05;frame();
   for(const c of TC)if(c.rmMe&&cars.includes(c)){removeCar(c);c.rmMe=0}let alive=0;for(const c of TC){if(c.bus&&!c.tour){if(c.m.dist===undefined)continue}if(c.done||c.lost||c.dead||!cars.includes(c)){if((c.dead||!cars.includes(c))&&!c.repDead&&!c.done){c.repDead=1;add(c,'车毁/被删')}continue}alive++;const m=c.m;
     const jump=Math.hypot(c.x-m.lastx,c.z-m.lastz);m.dist+=jump;
     if((c.orbT||0)>3.9&&!m.orbRep){m.orbRep=1;const L=laneOf(c.ni-c.dx,c.nj-c.dz,c.ni,c.nj),P=laneProg(c,L);add(c,'绕圈',`h=${c.h*57|0} v=${c.speed.toFixed(1)} n=${c.ni},${c.nj} d=${c.dx},${c.dz} nd=${c.nd} prog=${P.p.toFixed(1)}/${P.L.toFixed(1)} 车道点=${JSON.stringify(lanePt(c.ni-c.dx,c.nj-c.dz,c.ni,c.nj,P.p+7))} pos=${c.x.toFixed(1)},${c.z.toFixed(1)}`)}if((c.orbT||0)<1)m.orbRep=0;if(jump>4)add(c,'瞬移(卡住被拉回)',jump.toFixed(1)+' v='+c.speed.toFixed(1)+' 上帧v='+m.sp.toFixed(1)+' 撞到:'+JSON.stringify(cars.filter(o=>o!==c&&Math.hypot(o.x-c.x,o.z-c.z)<9).map(o=>[o.kind,+o.speed.toFixed(1),Math.round(((o.h-c.h)*57%360+360)%360),o.driver||'',o.bus?'BUS':'',o.tid!==undefined?'T'+o.tid:'',o.parked?'P':'',o.hold?'H':'',o.police?'COP':'',o.gangCar?'GANG':'',o.evt?'EVT':'']))+' air='+(c.air||0)+' y='+(c.y||0).toFixed(1)+' 之前:'+(m.obs||''));if(Math.abs(c.speed)<.5&&F%5===0){m.obs=JSON.stringify([...cars.filter(o=>o!==c),player,...peds].filter(o=>Math.hypot(o.x-c.x,o.z-c.z)<9).map(o=>[o.kind||(o===player?'PLAYER':'ped'),Math.round(o.x-c.x),Math.round(o.z-c.z),o.speed!==undefined?+o.speed.toFixed(1):'',o.driver||'',o.parked?'P':'',o.hold?'H':'',o.bus?'BUS':'',o.tid!==undefined?'T'+o.tid:'',o.act||'']))+' h='+(c.h*57|0)+' blk='+(c.blockT||0).toFixed(1)+' ped='+(c.pedT||0).toFixed(1)+' hit='+!!hit(c.x+Math.sin(c.h)*2.5,c.z+Math.cos(c.h)*2.5,1)+' stuck='+(c.stuck||0).toFixed(1)+' orb='+(c.orbT||0).toFixed(1)}else if(Math.abs(c.speed)>2)m.obs='';
     if(m.sp>3&&c.speed<-.5)add(c,'撞墙/台阶反弹',`v=${m.sp.toFixed(1)} 高差=${(GH(c.x,c.z)-GH(m.lastx,m.lastz)).toFixed(2)} 碰撞=${!!hit(c.x+Math.sin(c.h)*2.5,c.z+Math.cos(c.h)*2.5,1)}`);
     if(!onRoad(c.x,c.z,.8)&&!onBridge(c.x,c.z)){m.off+=.05;if(m.off>1&&!m.offRep){m.offRep=1;add(c,'开出路面',`岸距=${sdfAt(c.x,c.z).toFixed(1)}`)}}else{m.off=0;m.offRep=0}
     if(sdfAt(c.x,c.z)<0&&!onBridge(c.x,c.z)&&!m.seaRep){m.seaRep=1;add(c,'掉进海里')}
     if(c.air&&!m.air){add(c,'腾空(高处掉下)',`高=${(c.y||0).toFixed(1)}`)}m.air=c.air?1:0;
     if(Math.abs(c.speed)<.4&&!(c.bus&&c.bus.wait>0)){m.still+=.05;if(m.still>8&&!m.stillRep){m.stillRep=1;add(c,'长时间不动',JSON.stringify([...cars.filter(o=>o!==c),player,...peds].filter(o=>{const dx=o.x-c.x,dz=o.z-c.z,f=dx*Math.sin(c.h)+dz*Math.cos(c.h),s=Math.abs(dx*Math.cos(c.h)-dz*Math.sin(c.h));return f>0&&f<25&&s<5}).map(o=>[o.kind||(o===player?'PLAYER':'ped'),o.x|0,o.z|0,o.act||'',o.speed!==undefined?o.speed.toFixed(1):'',o.driver||'',o.parked?'P':'',o.hold?'H':'',o.bus?'BUS':'',o.tid!==undefined?'T'+o.tid:'']))+' redStop='+c.redStop+' blockT='+(c.blockT||0).toFixed(1))}}else{m.still=0;m.stillRep=0}
     m.hist.push(c.h);if(m.hist.length>30)m.hist.shift();const d0=Math.abs(((c.h-m.hist[0]+Math.PI*3)%(Math.PI*2))-Math.PI);if(d0>2.5&&Math.abs(c.speed)>3&&!m.flip){m.flip=1;add(c,'突然掉头')}if(d0<1)m.flip=0;
     m.sp=c.speed;m.lastx=c.x;m.lastz=c.z}
   if(!TC.some(c=>c.tour&&!c.done&&!c.lost&&!c.dead))break}
 const missed=E.filter(e=>!cov.has(ekD(e[0],e[1]))).map(e=>ekD(e[0],e[1]));
 return{frames:F,simMin:+(F*.05/60).toFixed(1),realS:((performance.now()-t0)/1000)|0,edges:E.length,unplanned,covered:cov.size,missed:missed.length,missedList:missed.slice(0,80),
   jstk:JSTK,mv:MVLOG,ch:CHLOG,cars:TC.map(c=>({k:c.tid,tour:c.tour?c.tour.length:'lost',tk:c.tk,done:!!c.done,lost:!!c.lost,km:+(c.m.dist/1000).toFixed(1),near:c.tour?JSON.stringify(c.tour.slice(Math.max(0,c.tk-2),c.tk+3)):'',pos:[c.x|0,c.z|0],nd:c.nd,ni:[c.ni,c.nj,c.dx,c.dz]})),issues:ISS}},[NCAR,MAXF]);
fs.writeFileSync(process.argv[3]||'roadtest.json',JSON.stringify(res,null,1));
const cnt={};for(const i of res.issues)cnt[i.type]=(cnt[i.type]||0)+1;
console.log(JSON.stringify({frames:res.frames,simMin:res.simMin,realS:res.realS,edges:res.edges,covered:res.covered,missed:res.missed,unplanned:res.unplanned.length,cars:res.cars,issueCount:cnt}));
await b.close()})();
