// 路面扫描：找出路面上的障碍物、被覆盖的路面、被盖住的标线、两层太近会闪烁的地方、太长不能跟着画面弯曲的面
// 用法：node tools/roadscan.js games/neon-bay/index.html [输出.json]
// 原理：把全图所有模型的三角面投到 1 米一格的网格上（只看离路边 2.5 米以内的路面格子），
//       看每一格最上面是什么、有没有东西挡在 0.3~4.5 米高度。扫描前清掉所有车和行人。
const {chromium}=require('playwright');const fs=require('fs');const path=require('path');
(async()=>{const src=path.resolve(process.argv[2]||'games/neon-bay/index.html');
 // 做一份扫描用的副本：让游戏不在上传显卡后清掉顶点数据（否则读不到合并后的静态网格）
 let html=fs.readFileSync(src,'utf8');const m=html.match(/<script src="[^"]*three[^"]*"><\/script>/);
 html=html.slice(0,m.index+m[0].length)+'<script>THREE.BufferAttribute.prototype.onUpload=function(){return this};</script>'+html.slice(m.index+m[0].length);
 const tmp=path.join(path.dirname(src),'_roadscan_tmp.html');fs.writeFileSync(tmp,html);
 const b=await chromium.launch({args:['--use-gl=swiftshader','--ignore-gpu-blocklist']});const p=await b.newPage();
 p.on('pageerror',e=>console.log('ERR',e.message));
 try{await p.goto('file://'+tmp);await p.waitForFunction(()=>{try{return cityReady}catch(e){return false}},null,{timeout:300000});
  const r=JSON.parse(await p.evaluate(SCAN));if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(r,null,1));
  console.log('路面格',r.roadCells,'三角面',r.tris,'用时',(r.ms/1000|0)+'s');
  const sec=(lab,v,list)=>{console.log('== '+lab+'：'+v+' 格');for(const c of (list||[]).slice(0,10))console.log('   ',JSON.stringify(c))};
  sec('障碍物',r.obstacle.cells,r.obstacle.clusters);sec('路面被覆盖',r.covered.cells,r.covered.top);sec('标线被盖',r.hiddenMarks.cells,r.hiddenMarks.top);sec('闪烁（两层不到1.5cm）',r.flicker.cells,r.flicker.top);
  const L=r.longTri.top.filter(c=>c.len>30);console.log('== 路上超过30米的长面（画面弯曲时会错位）：'+L.length);for(const c of L.slice(0,10))console.log('   ',JSON.stringify(c));
 }finally{await b.close();fs.unlinkSync(tmp)}})();
const SCAN=`// 路面扫描 v2：每个路面格子（1m）记录最上面的几层水平面 + 穿过路面的竖直物体
(()=>{const T0=performance.now();for(const j of JOBS)if(!j.built)buildJob(j);
 for(const c of [...cars])removeCar(c);for(const p of [...peds])dropPed(p);scene.updateMatrixWorld(true);
 const st=1,x0=WU(-.12),z0=WV(-.12),nx=Math.ceil((WU(1.12)-x0)/st),nz=Math.ceil((WV(1.12)-z0)/st);
 const RM=new Uint8Array(nx*nz);for(let j=0;j<nz;j++)for(let i=0;i<nx;i++){const x=x0+(i+.5)*st,z=z0+(j+.5)*st;if(sdfAt(x,z)>-30&&onRoad(x,z,-2.5))RM[j*nx+i]=1}
 const MATS=[],MI=new Map();const mid=nm=>{if(!MI.has(nm)){MI.set(nm,MATS.length);MATS.push(nm)}return MI.get(nm)};
 const name=o=>{const m=o.material;if(Array.isArray(m))return 'multi';const g=Object.entries(GM).find(([k,v])=>v===m);if(g)return 'gm:'+g[0];
   for(const k of['whiteMat','lineMat','zebraMat','glassMat','lampMat','wallMat'])try{if(eval(k)===m)return k}catch(e){}
   return m.type.replace('Material','')+'#'+(m.color?m.color.getHexString():'')+(m.map?'+map':'')};
 // 每格保存最多 6 层水平面 (y, 材质)
 const L=6,HY=new Float32Array(nx*nz*L).fill(-99),HM=new Int16Array(nx*nz*L).fill(-1),OBS=new Map(),LONG=new Map();
 const A=new THREE.Vector3(),B=new THREE.Vector3(),C=new THREE.Vector3(),mtx=new THREE.Matrix4(),tmp=new THREE.Matrix4();let nTri=0;
 const visit=(o,matW,nm,mi)=>{const g=o.geometry,P=g.attributes.position;if(!P||!P.array)return;const idx=g.index,nt=idx?idx.count/3:P.count/3;
  for(let t=0;t<nt;t++){const a=idx?idx.getX(t*3):t*3,b=idx?idx.getX(t*3+1):t*3+1,c=idx?idx.getX(t*3+2):t*3+2;
   A.fromBufferAttribute(P,a).applyMatrix4(matW);B.fromBufferAttribute(P,b).applyMatrix4(matW);C.fromBufferAttribute(P,c).applyMatrix4(matW);nTri++;
   const ymin=Math.min(A.y,B.y,C.y),ymax=Math.max(A.y,B.y,C.y);if(ymin>4.5||ymax<-.3)continue;
   const bx0=Math.min(A.x,B.x,C.x),bx1=Math.max(A.x,B.x,C.x),bz0=Math.min(A.z,B.z,C.z),bz1=Math.max(A.z,B.z,C.z);if(bx1-bx0>400||bz1-bz0>400)continue;
   const i0=Math.max(0,Math.floor((bx0-x0)/st)),i1=Math.min(nx-1,Math.floor((bx1-x0)/st)),j0=Math.max(0,Math.floor((bz0-z0)/st)),j1=Math.min(nz-1,Math.floor((bz1-z0)/st));
   let any=false;for(let j=j0;j<=j1&&!any;j++)for(let i=i0;i<=i1;i++)if(RM[j*nx+i]){any=true;break}if(!any)continue;
   const e=Math.max(Math.hypot(A.x-B.x,A.z-B.z),Math.hypot(B.x-C.x,B.z-C.z),Math.hypot(C.x-A.x,C.z-A.z));
   const area=Math.abs((B.x-A.x)*(C.z-A.z)-(C.x-A.x)*(B.z-A.z))/2,vert=area<.02*e*e+.01;
   if(e>14&&ymax>-.1){const k=Math.round((A.x+B.x+C.x)/60)+','+Math.round((A.z+B.z+C.z)/60);const v=LONG.get(k);if(!v||e>v.len)LONG.set(k,{nm,len:e|0,x:(A.x+B.x+C.x)/3|0,z:(A.z+B.z+C.z)/3|0})}
   for(let j=j0;j<=j1;j++)for(let i=i0;i<=i1;i++){const ci=j*nx+i;if(!RM[ci])continue;const px=x0+(i+.5)*st,pz=z0+(j+.5)*st;
     if(vert){let d=1e9;for(const[p,q]of[[A,B],[B,C],[C,A]]){const dx=q.x-p.x,dz=q.z-p.z,l2=dx*dx+dz*dz||1,tt=Math.max(0,Math.min(1,((px-p.x)*dx+(pz-p.z)*dz)/l2));d=Math.min(d,Math.hypot(px-p.x-dx*tt,pz-p.z-dz*tt))}
       if(d<=.7&&ymax>.2){const v=OBS.get(ci);if(!v||ymax>v.y1)OBS.set(ci,{nm,x:px|0,z:pz|0,y0:+ymin.toFixed(2),y1:+ymax.toFixed(2),kind:'竖'})}continue}
     const d0=(B.z-C.z)*(A.x-C.x)+(C.x-B.x)*(A.z-C.z);if(Math.abs(d0)<1e-9)continue;const l1=((B.z-C.z)*(px-C.x)+(C.x-B.x)*(pz-C.z))/d0,l2=((C.z-A.z)*(px-C.x)+(A.x-C.x)*(pz-C.z))/d0,l3=1-l1-l2;if(l1<-1e-4||l2<-1e-4||l3<-1e-4)continue;
     const y=l1*A.y+l2*B.y+l3*C.y;
     if(y>.3){if(y<4.5){const v=OBS.get(ci);if(!v||y>v.y1)OBS.set(ci,{nm,x:px|0,z:pz|0,y0:+y.toFixed(2),y1:+y.toFixed(2),kind:'面'})}continue}
     // 插入水平层（按 y 从高到低，保留 L 层；同材质同高度去重）
     const base=ci*L;let dup=false;for(let q=0;q<L;q++)if(HM[base+q]===mi&&Math.abs(HY[base+q]-y)<.001){dup=true;break}if(dup)continue;
     let pos=L;for(let q=0;q<L;q++)if(y>HY[base+q]){pos=q;break}if(pos<L){for(let q=L-1;q>pos;q--){HY[base+q]=HY[base+q-1];HM[base+q]=HM[base+q-1]}HY[base+pos]=y;HM[base+pos]=mi}}}};
 scene.traverse(o=>{if(!o.isMesh||!o.visible||o===sky)return;if(!o.geometry.boundingSphere)o.geometry.computeBoundingSphere();if(o.geometry.boundingSphere.radius*Math.max(o.scale.x,o.scale.y,o.scale.z)>3500)return;
  if(o.material&&o.material.transparent)return;if(o.material&&o.material.vertexColors&&o.geometry.type==='PlaneGeometry')return;
  let nm=name(o);const jb=JOBS.find(J=>J.group&&(J.group===o.parent||J.group===o));nm+=(jb?' @'+jb.kind+(jb.kind==='block'?'('+BTYPE[jb.i+','+jb.j]+')':''):'');const mi=mid(nm);
  if(o.isInstancedMesh){for(let k=0;k<o.count;k++){o.getMatrixAt(k,tmp);mtx.multiplyMatrices(o.matrixWorld,tmp);visit(o,mtx,nm,mi)}}else visit(o,o.matrixWorld,nm,mi)});
 const isRoad=nm=>/^gm:(asphalt|stone)/.test(nm),isDecal=nm=>/^(whiteMat|lineMat|zebraMat)/.test(nm);
 const COV=new Map(),HID=new Map(),ZF=new Map();const put=(M,key,v)=>{const e=M.get(key);if(e)e.n++;else M.set(key,Object.assign({n:1},v))};
 for(let ci=0;ci<nx*nz;ci++){if(!RM[ci])continue;const base=ci*L;if(HM[base]<0)continue;const x=x0+(ci%nx+.5)*st|0,z=z0+((ci/nx|0)+.5)*st|0;
   // 最上面一层（忽略标线）
   let q=0;while(q<L&&HM[base+q]>=0&&isDecal(MATS[HM[base+q]]))q++;
   const topNm=MATS[HM[base+q]];if(q<L&&HM[base+q]>=0&&!isRoad(topNm))put(COV,topNm+'@'+Math.round(x/40)+','+Math.round(z/40),{nm:topNm,x,z,y:+HY[base+q].toFixed(3)});
   // 标线被路面盖住
   for(let r=q+1;r<L&&HM[base+r]>=0;r++){const nm=MATS[HM[base+r]];if(isDecal(nm)&&HY[base+q]>HY[base+r]+.003)put(HID,nm+'@'+Math.round(x/40)+','+Math.round(z/40),{nm,by:topNm,x,z})}
   // 闪烁：最上面两层非标线面，材质不同、高度差 < 1.5cm
   let r=q+1;while(r<L&&HM[base+r]>=0&&isDecal(MATS[HM[base+r]]))r++;
   if(r<L&&HM[base+r]>=0&&HM[base+r]!==HM[base+q]&&HY[base+q]-HY[base+r]<.015)put(ZF,topNm+'|'+MATS[HM[base+r]]+'@'+Math.round(x/40)+','+Math.round(z/40),{a:topNm,b:MATS[HM[base+r]],dy:+(HY[base+q]-HY[base+r]).toFixed(3),x,z})}
 const clus=M=>{const g=new Map();for(const v of M.values()){const k=v.nm+'@'+Math.round(v.x/25)+','+Math.round(v.z/25);const e=g.get(k)||{nm:v.nm,x:v.x,z:v.z,n:0,y0:v.y0,y1:v.y1,kind:v.kind};e.n++;e.y1=Math.max(e.y1,v.y1);g.set(k,e)}return[...g.values()].sort((a,b)=>b.n-a.n)};
 const top=(M,n)=>[...M.values()].sort((a,b)=>b.n-a.n).slice(0,n);const tot=M=>[...M.values()].reduce((a,v)=>a+v.n,0);
 const byNm=M=>{const c={};for(const v of M.values())c[v.nm||v.a+'|'+v.b]=(c[v.nm||v.a+'|'+v.b]||0)+v.n;return c};
 return JSON.stringify({ms:(performance.now()-T0)|0,roadCells:RM.reduce((a,b)=>a+b,0),tris:nTri,
   obstacle:{cells:OBS.size,clusters:clus(OBS).slice(0,30)},covered:{cells:tot(COV),by:byNm(COV),top:top(COV,15)},hiddenMarks:{cells:tot(HID),by:byNm(HID),top:top(HID,15)},
   flicker:{cells:tot(ZF),by:byNm(ZF),top:top(ZF,15)},longTri:{n:LONG.size,top:[...LONG.values()].sort((a,b)=>b.len-a.len).slice(0,15)}})})()
`;
