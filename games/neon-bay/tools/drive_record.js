// 全路网试驾录像：1 辆 NPC 车按规划路线把每条路双向跑一遍，跟车视角每 STEP 米存一帧，同时记录驾驶问题
const {chromium}=require('playwright');const fs=require('fs');
(async()=>{const OUT=process.argv[3]||'frames',STEP=+(process.env.STEP||40),MAXSHOT=+(process.env.MAXSHOT||1e9);fs.mkdirSync(OUT,{recursive:true});
const b=await chromium.launch({args:['--use-gl=swiftshader','--ignore-gpu-blocklist']});const p=await b.newPage({viewport:{width:640,height:360}});
await p.addInitScript(()=>{try{localStorage.setItem('nby-quality','low')}catch(e){}});
p.on('pageerror',e=>console.log('ERR',e.message,(e.stack||'').split('\n').slice(1,3).join(' | ')));
await p.goto('file://'+process.argv[2]);await p.waitForFunction(()=>{try{return cityReady}catch(e){return false}},null,{timeout:300000});
console.log(await p.evaluate(()=>{PERF.on=false;ren.shadowMap.enabled=false;document.getElementById('start').click();DAY_SPEED=0;gameHour=14;try{setWeather('clear',true)}catch(e){}
 window.T=n=>{for(let i=0;i<n;i++){last=performance.now()-33;frame();if(dlg)nextDlg()}};T(5);while(cut)T(10);T(3);
 window.__RM=window.renderMain;window.renderMain=()=>{};player.hp=1e9;
 window.SIMT=0;window.updLights=eval('('+updLights.toString().replace('performance.now()/1000','window.SIMT')+')');
 const nk=(i,j)=>i+','+j,ekD=(a,b)=>nk(...a)+'>'+nk(...b);
 const E=[];for(let i=0;i<=NX;i++)for(let j=0;j<=NZ;j++){if(!nodeOK(i,j))continue;for(const[a,b]of DIRS8)if(linkOK(i,j,a,b))E.push([[i,j],[i+a,j+b]])}
 const pool=new Set(E.map(e=>ekD(...e))),planned=new Set();const nbr=u=>DIRS8.filter(([a,b])=>linkOK(u[0],u[1],a,b)).map(([a,b])=>[u[0]+a,u[1]+b]);
 function toNearest(cur,prev,strict){const Q=[[cur,prev,null]],seen=new Set([nk(...cur)+'|'+(prev?nk(...prev):'')]);let h=0;
   while(h<Q.length){const[u,pv,par]=Q[h++];for(const v of nbr(u)){if(pv&&v[0]===pv[0]&&v[1]===pv[1]&&nbr(u).length>1)continue;if(strict&&pv&&turnAng(pv[0],pv[1],u[0],u[1],v[0],v[1])>=2)continue;const e=ekD(u,v);
     if(pool.has(e)&&!planned.has(e)){const path=[v];let n=[u,pv,par];while(n&&n[2]!==null){path.unshift(n[0]);n=n[2]}return path}
     const sk=nk(...v)+'|'+nk(...u);if(seen.has(sk))continue;seen.add(sk);Q.push([v,u,[u,pv,par]])}}return null}
 // 从主角出生点附近开始
 let start=E[0];{let bd=1e9;for(const e of E){const d=Math.hypot(rx(e[0][0])-player.x,rz(e[0][1])-player.z);if(d<bd){bd=d;start=e}}}
 const tour=[start[0],start[1]];planned.add(ekD(...start));let g=0;while(g++<9000){const cur=tour[tour.length-1],prev=tour[tour.length-2];const path=toNearest(cur,prev,true)||toNearest(cur,prev,false);if(!path)break;for(const v of path){planned.add(ekD(tour[tour.length-1],v));tour.push(v)}}
 const oC=aiChoose,oP=aiPickNext;window.aiChoose=c=>{if(c.tour){const n=c.tour[c.tk+1];if(!n)return[-c.dx,-c.dz];return[n[0]-c.ni,n[1]-c.nj]}return oC(c)};
 window.ISS=[];window.COV=new Set();const add=(c,type,extra='')=>ISS.push({type,x:Math.round(c.x),z:Math.round(c.z),e:c.tk>0&&c.tour[c.tk]?ekD(c.tour[c.tk-1],c.tour[c.tk]):'',extra,t:+(SIMT).toFixed(1),shot:window.SHOTN||0});window.addIss=add;
 window.aiPickNext=c=>{oP(c);if(c.tour&&!c.done){c.tk++;const w=c.tour[c.tk];if(!w||w[0]!==c.ni||w[1]!==c.nj){add(c,'偏离路线');c.done=1}else{COV.add(ekD(c.tour[c.tk-1],w));if(c.tk>=c.tour.length-1)c.done=1}}};
 const a=tour[0],bb=tour[1],ln=laneOf(a[0],a[1],bb[0],bb[1]);const c=makeCar(ln.ax+ln.ux*(RD/2+3),ln.az+ln.uz*(RD/2+3),Math.atan2(ln.ux,ln.uz),{kind:'taxi'});
 c.driver='ai';c.target=1;c.ni=bb[0];c.nj=bb[1];c.dx=bb[0]-a[0];c.dz=bb[1]-a[1];c.nd=null;c.tour=tour;c.tk=1;c.mesh.position.set(c.x,0,c.z);c.mesh.rotation.y=c.h;COV.add(ekD(a,bb));
 window.TC=c;player.ride=c;player.mesh.visible=false;c.m={still:0,off:0,lx:c.x,lz:c.z,sp:0,hist:[],dist:0,sinceShot:1e9};
 return JSON.stringify({edges:E.length,tourLen:tour.length,planned:planned.size})}));
let n=0;const t0=Date.now();
while(true){const r=await p.evaluate(([STEP])=>{const c=TC,m=c.m;let f=0;
  while(!c.done&&m.sinceShot<STEP&&f<4000){f++;last=performance.now()-50;SIMT+=.05;frame();if(dlg)nextDlg();
   if(!cars.includes(c)||c.dead){addIss(c,'车毁/被删');c.done=1;break}
   const jump=Math.hypot(c.x-m.lx,c.z-m.lz);m.dist+=jump;m.sinceShot+=jump;if(jump>4)addIss(c,'瞬移',jump.toFixed(1));
   if(m.sp>3&&c.speed<-.5)addIss(c,'撞墙/反弹','v='+m.sp.toFixed(1));
   if(!onRoad(c.x,c.z,.8)&&!onBridge(c.x,c.z)){m.off+=.05;if(m.off>1&&!m.offR){m.offR=1;addIss(c,'开出路面')}}else{m.off=0;m.offR=0}
   if(Math.abs(c.speed)<.4){m.still+=.05;if(m.still>12&&!m.stR){m.stR=1;addIss(c,'长时间不动')}}else{m.still=0;m.stR=0}
   if((c.orbT||0)>3.9&&!m.orR){m.orR=1;addIss(c,'绕圈')}if((c.orbT||0)<1)m.orR=0;
   m.hist.push(c.h);if(m.hist.length>30)m.hist.shift();const d0=Math.abs(Math.atan2(Math.sin(c.h-m.hist[0]),Math.cos(c.h-m.hist[0])));if(d0>2.5&&Math.abs(c.speed)>3&&!m.flip){m.flip=1;addIss(c,'突然掉头')}if(d0<1)m.flip=0;
   m.sp=c.speed;m.lx=c.x;m.lz=c.z}
  if(c.done&&m.sinceShot<STEP)return{done:true};
  m.sinceShot=0;window.SHOTN=(window.SHOTN||0)+1;window.renderMain=window.__RM;last=performance.now()-50;SIMT+=.05;frame();const url=ren.domElement.toDataURL('image/jpeg',.75);window.renderMain=()=>{};
  return{img:url,x:c.x|0,z:c.z|0,e:c.tk>0?c.tour[c.tk-1]+'>'+c.tour[c.tk]:'',tk:c.tk,tl:c.tour.length,km:+(m.dist/1000).toFixed(2),t:+SIMT.toFixed(0),done:!!c.done}},[STEP]);
  if(r.img){n++;fs.writeFileSync(`${OUT}/f${String(n).padStart(5,'0')}.jpg`,Buffer.from(r.img.split(',')[1],'base64'));fs.appendFileSync(`${OUT}/meta.jsonl`,JSON.stringify({n,x:r.x,z:r.z,e:r.e,tk:r.tk,tl:r.tl,km:r.km,t:r.t})+'\n');
   if(n%25===0)console.log('frame',n,'tk',r.tk+'/'+r.tl,'km',r.km,'sim',r.t,'s real',((Date.now()-t0)/1000)|0,'s')}
  if(r.done||n>=MAXSHOT)break}
const fin=await p.evaluate(()=>JSON.stringify({covered:COV.size,issues:ISS,km:+(TC.m.dist/1000).toFixed(1),simMin:+(SIMT/60).toFixed(1)}));fs.writeFileSync(`${OUT}/result.json`,fin);
const R=JSON.parse(fin);const cnt={};for(const i of R.issues)cnt[i.type]=(cnt[i.type]||0)+1;console.log('DONE frames',n,'covered',R.covered,'km',R.km,'simMin',R.simMin,'issues',JSON.stringify(cnt));await b.close()})();
