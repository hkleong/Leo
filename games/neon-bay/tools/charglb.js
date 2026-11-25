// ===== 外部人物模型（GLB）：解析内嵌的 glTF，按部位自动分配骨骼权重，套到原来的骨骼上，原有动作全部能用 =====
const GLBMAP={heroF:'female-lead',heroM:'male-lead',cop:'patrol-officer',copK9:'patrol-officer',copF:'female-patrol-officer',swat:'tactical-officer',detective:'detective',tourist:'tourist',skater:'skater',skater8:'skater',courier:'courier'};
const _glbC={};
function glbParse(name){if(name in _glbC)return _glbC[name];_glbC[name]=null;const b64=GLBDATA[name];if(!b64)return null;
  const raw=atob(b64),u8=new Uint8Array(raw.length);for(let i=0;i<raw.length;i++)u8[i]=raw.charCodeAt(i);const dv=new DataView(u8.buffer);
  const jl=dv.getUint32(12,true),J=JSON.parse(new TextDecoder().decode(u8.subarray(20,20+jl))),bo=20+jl+8,BIN=u8.subarray(bo,bo+dv.getUint32(20+jl,true));
  const CT={5126:Float32Array,5123:Uint16Array,5125:Uint32Array,5121:Uint8Array,5122:Int16Array,5120:Int8Array},NC={SCALAR:1,VEC2:2,VEC3:3,VEC4:4,MAT4:16};
  const acc=i=>{const a=J.accessors[i],v=J.bufferViews[a.bufferView],T=CT[a.componentType],n=NC[a.type],es=T.BYTES_PER_ELEMENT,off=(v.byteOffset||0)+(a.byteOffset||0),st=v.byteStride||n*es;
    const out=new T(a.count*n);if(st===n*es){out.set(new T(BIN.buffer.slice(BIN.byteOffset+off,BIN.byteOffset+off+a.count*n*es)))}
    else{const d=new DataView(BIN.buffer,BIN.byteOffset);const g=es===4?(T===Float32Array?'getFloat32':'getUint32'):es===2?(T===Int16Array?'getInt16':'getUint16'):(T===Int8Array?'getInt8':'getUint8');
      for(let k=0;k<a.count;k++)for(let c=0;c<n;c++)out[k*n+c]=d[g](off+k*st+c*es,true)}
    if(a.normalized&&T!==Float32Array){const f=new Float32Array(out.length),mx=T===Uint8Array?255:T===Uint16Array?65535:T===Int8Array?127:32767;for(let k=0;k<out.length;k++)f[k]=Math.max(-1,out[k]/mx);return{a:f,n}}return{a:out,n}};
  const texs=(J.textures||[]).map(t=>{const im=J.images[t.source],v=J.bufferViews[im.bufferView],blob=new Blob([BIN.subarray(v.byteOffset||0,(v.byteOffset||0)+v.byteLength)],{type:im.mimeType||'image/png'});
    const img=new Image(),tx=new THREE.Texture(img);tx.flipY=false;tx.wrapS=tx.wrapT=THREE.RepeatWrapping;img.onload=()=>{tx.needsUpdate=true};img.src=URL.createObjectURL(blob);return tx});
  const mats=(J.materials||[]).map(m=>{const p=m.pbrMetallicRoughness||{},f=p.baseColorFactor||[1,1,1,1];return{col:f,map:p.baseColorTexture?texs[p.baseColorTexture.index]:null,blend:m.alphaMode==='BLEND',mask:m.alphaMode==='MASK'?(m.alphaCutoff??.5):0,ds:!!m.doubleSided}});
  const parts=[],m4=new THREE.Matrix4();
  const walk=(ni,pm)=>{const n=J.nodes[ni],M=new THREE.Matrix4();if(n.matrix)M.fromArray(n.matrix);else M.compose(new THREE.Vector3(...(n.translation||[0,0,0])),new THREE.Quaternion(...(n.rotation||[0,0,0,1])),new THREE.Vector3(...(n.scale||[1,1,1])));
    const W=new THREE.Matrix4().multiplyMatrices(pm,M);if(n.mesh!==undefined)for(const pr of J.meshes[n.mesh].primitives){if(pr.mode!==undefined&&pr.mode!==4)continue;const A=pr.attributes;
      parts.push({pos:acc(A.POSITION).a,nor:A.NORMAL!==undefined?acc(A.NORMAL).a:null,uv:A.TEXCOORD_0!==undefined?acc(A.TEXCOORD_0).a:null,col:A.COLOR_0!==undefined?acc(A.COLOR_0):null,idx:pr.indices!==undefined?acc(pr.indices).a:null,mat:mats[pr.material??0]||{col:[1,1,1,1]},M:W})}
    for(const c of n.children||[])walk(c,W)};
  for(const r of J.scenes[J.scene||0].nodes)walk(r,m4);return _glbC[name]=parts}
const _glbMat={};
function glbMaterial(m,vc){const k=(m.map?m.map.uuid:'c')+(m.blend?'b':'')+(m.mask||'')+(m.ds?'d':'')+(vc?'v':'');if(_glbMat[k])return _glbMat[k];
  const mt=new THREE.MeshPhongMaterial({map:m.map||null,vertexColors:!!vc,shininess:8,specular:0x111111,transparent:m.blend,alphaTest:m.mask||(m.blend?0:0),side:m.ds?THREE.DoubleSide:THREE.FrontSide});
  if(!vc)mt.color.setRGB(m.col[0],m.col[1],m.col[2]);if(m.blend)mt.opacity=m.col[3];mt.skinning=true;return _glbMat[k]=mt}
// 换上模型：g 是 buildPerson 刚建好的人（骨骼已经在），成功返回 true
function glbPerson(g,look){const name=GLBMAP[look];if(!name||!self.GLBDATA)return false;const parts=glbParse(name);if(!parts||!parts.length)return false;
  g.updateMatrixWorld(true);const bones=BONE_NAMES.map(n=>g.getObjectByName(n));if(bones.some(b=>!b))return false;
  const inv=new THREE.Matrix4().copy(g.matrixWorld).invert(),P=n=>new THREE.Vector3().setFromMatrixPosition(g.getObjectByName(n).matrixWorld).applyMatrix4(inv);
  // 原模型的高度 → 缩放
  const ob=new THREE.Box3();g.traverse(o=>{if(o.isMesh&&o.geometry){o.geometry.computeBoundingBox();const b=o.geometry.boundingBox.clone().applyMatrix4(new THREE.Matrix4().multiplyMatrices(inv,o.matrixWorld));ob.union(b)}});
  const v=new THREE.Vector3();let top=-1e9,bot=1e9;for(const p of parts)for(let i=0;i<p.pos.length;i+=3){v.set(p.pos[i],p.pos[i+1],p.pos[i+2]).applyMatrix4(p.M);top=Math.max(top,v.y);bot=Math.min(bot,v.y)}
  const S=(ob.max.y-Math.max(0,ob.min.y))/(top-Math.min(0,bot)),SM=new THREE.Matrix4().makeScale(S,S,S);
  // 变换到人物坐标
  const L=parts.map(p=>{const M=new THREE.Matrix4().multiplyMatrices(SM,p.M),nm=new THREE.Matrix3().getNormalMatrix(M),n=p.pos.length/3,pos=new Float32Array(n*3),nor=new Float32Array(n*3);let cx=0,cy=0,cz=0;
    for(let i=0;i<n;i++){v.set(p.pos[i*3],p.pos[i*3+1],p.pos[i*3+2]).applyMatrix4(M);pos[i*3]=v.x;pos[i*3+1]=v.y;pos[i*3+2]=v.z;cx+=v.x;cy+=v.y;cz+=v.z;
      if(p.nor){v.set(p.nor[i*3],p.nor[i*3+1],p.nor[i*3+2]).applyMatrix3(nm).normalize();nor[i*3]=v.x;nor[i*3+1]=v.y;nor[i*3+2]=v.z}}
    const flip=M.determinant()<0;return{p,pos,nor,n,c:[cx/n,cy/n,cz/n],flip}});
  const hip=[P('rg_0_0'),P('rg_0_1')],knee=[P('rg_1_0'),P('rg_1_1')],sh=[P('rg_2_0'),P('rg_2_1')],hipY=hip[0].y,shX=Math.abs(sh[0].x);
  const sideOf=x=>Math.sign(x)===Math.sign(hip[0].x)?0:1;
  // 部件分类：手臂 / 腿 / 身体
  for(const q of L){const[cx,cy]=q.c;q.cat=Math.abs(cx)>shX*.62&&cy>hipY-.55&&cy<sh[0].y+.25?'arm':cy<hipY-.12&&Math.abs(cx)<shX*.62?'leg':'body';q.k=sideOf(cx)}
  // 按模型自己的手臂长度重新放肩、肘、腕关节
  for(const k of[0,1]){let ty=-1e9,my=1e9;const vs=[];for(const q of L)if(q.cat==='arm'&&q.k===k)for(let i=0;i<q.n;i++){const y=q.pos[i*3+1];ty=Math.max(ty,y);my=Math.min(my,y);vs.push(q.pos[i*3],y,q.pos[i*3+2])}
    if(!vs.length)continue;const R=ty-my,at=y=>{let sx=0,sz=0,c=0;for(let i=0;i<vs.length;i+=3)if(Math.abs(vs[i+1]-y)<R*.05){sx+=vs[i];sz+=vs[i+2];c++}return c?new THREE.Vector3(sx/c,y,sz/c):null};
    const sY=ty-R*.08,wY=my+R*.2,eY=(sY+wY)/2;const set=(bn,p)=>{if(!p)return;const b=g.getObjectByName(bn);b.parent.updateMatrixWorld(true);const w=p.clone().applyMatrix4(g.matrixWorld);b.position.copy(b.parent.worldToLocal(w));b.updateMatrixWorld(true)};
    set('rg_2_'+k,at(sY));set('rg_3_'+k,at(eY));set('rg_4_'+k,at(wY))}
  g.updateMatrixWorld(true);const J={};for(const n of BONE_NAMES)J[n]=P(n);const bi=n=>BONE_NAMES.indexOf(n);
  // 每个顶点的骨骼权重（最多两根骨头）
  const segT=(p,a,b)=>{const ab=b.clone().sub(a),t=clamp(p.clone().sub(a).dot(ab)/ab.lengthSq(),0,1);return{t,d:p.distanceTo(a.clone().addScaledVector(ab,t))}};
  const wOf=(q,x,y,z)=>{const p=new THREE.Vector3(x,y,z),k=q.cat==='body'?sideOf(x):q.k;
    if(q.cat==='arm'){const S0=J['rg_2_'+k],E=J['rg_3_'+k],W=J['rg_4_'+k],H=W.clone().addScaledVector(W.clone().sub(E).normalize(),.3);
      const s=[segT(p,S0,E),segT(p,E,W),segT(p,W,H)];let b=0;for(let i=1;i<3;i++)if(s[i].d<s[b].d-1e-4)b=i;
      const names=['rg_2_'+k,'rg_3_'+k,'rg_4_'+k];const r=.09;
      if(b===0&&p.distanceTo(S0)<.16)return[[bi(names[0]),.6+.4*p.distanceTo(S0)/.16],[0,.4-.4*p.distanceTo(S0)/.16]];
      const dE=p.distanceTo(E),dW=p.distanceTo(W);if(b<2&&dE<r){const t=.5*(1-dE/r);return b===0?[[bi(names[0]),1-t],[bi(names[1]),t]]:[[bi(names[1]),1-t],[bi(names[0]),t]]}
      if(b>0&&dW<r*.7){const t=.5*(1-dW/(r*.7));return b===1?[[bi(names[1]),1-t],[bi(names[2]),t]]:[[bi(names[2]),1-t],[bi(names[1]),t]]}
      return[[bi(names[b]),1]]}
    if(q.cat==='leg'||y<hipY-.08){const kn=J['rg_1_'+k],r=.12;if(y>hipY-.18&&q.cat!=='leg'){const t=clamp((hipY-y)/.3,0,.5);return[[0,1-t],[bi('rg_0_'+k),t]]}
      const dk=Math.abs(y-kn.y);if(dk<r){const t=.5*(1-dk/r);return y>kn.y?[[bi('rg_0_'+k),1-t],[bi('rg_1_'+k),t]]:[[bi('rg_1_'+k),1-t],[bi('rg_0_'+k),t]]}
      if(y>hipY-.12){const t=.35*(1-(hipY-y)/.12);return[[bi('rg_0_'+k),1-t],[0,t]]}
      return[[bi(y>kn.y?'rg_0_'+k:'rg_1_'+k),1]]}
    // 身体：肩头一带分一点给上臂
    const dS=Math.min(p.distanceTo(J.rg_2_0),p.distanceTo(J.rg_2_1));if(dS<.12){const kk=p.distanceTo(J.rg_2_0)<p.distanceTo(J.rg_2_1)?0:1,t=.35*(1-dS/.12);return[[0,1-t],[bi('rg_2_'+kk),t]]}
    return[[0,1]]};
  // 拆掉原来的身体部件
  const drop=[];g.traverse(o=>{if(o.isMesh)drop.push(o)});for(const o of drop)o.parent&&o.parent.remove(o);
  // 按材质合并：纯色材质并成一个顶点色网格，有贴图的各一个
  const groups=new Map();for(const q of L){const m=q.p.mat,vc=!m.map&&!m.blend&&!m.mask,key=vc?'VC':glbMaterial(m,false).uuid;if(!groups.has(key))groups.set(key,{mat:vc?glbMaterial({col:[1,1,1,1]},true):glbMaterial(m,false),vc,list:[]});groups.get(key).list.push(q)}
  const sk=new THREE.Skeleton(bones);
  for(const[,G0]of groups){const pos=[],nor=[],uv=[],col=[],si=[],sw=[];let hasUv=G0.list.some(q=>q.p.uv);
    for(const q of G0.list){const id=q.p.idx||Array.from({length:q.n},(_,i)=>i),c=q.p.mat.col;
      for(let t=0;t<id.length;t+=3){const tri=q.flip?[id[t],id[t+2],id[t+1]]:[id[t],id[t+1],id[t+2]];
        for(const i of tri){pos.push(q.pos[i*3],q.pos[i*3+1],q.pos[i*3+2]);nor.push(q.nor[i*3],q.nor[i*3+1],q.nor[i*3+2]);if(hasUv)uv.push(q.p.uv?q.p.uv[i*2]:0,q.p.uv?q.p.uv[i*2+1]:0);
          if(G0.vc){let r=c[0],gg=c[1],b=c[2];if(q.p.col){const C=q.p.col;r*=C.a[i*C.n];gg*=C.a[i*C.n+1];b*=C.a[i*C.n+2]}col.push(r,gg,b)}
          const w=wOf(q,q.pos[i*3],q.pos[i*3+1],q.pos[i*3+2]);si.push(w[0][0],w[1]?w[1][0]:0,0,0);sw.push(w[0][1],w[1]?w[1][1]:0,0,0)}}}
    const G=new THREE.BufferGeometry();G.setAttribute('position',new THREE.Float32BufferAttribute(pos,3));G.setAttribute('normal',new THREE.Float32BufferAttribute(nor,3));if(hasUv)G.setAttribute('uv',new THREE.Float32BufferAttribute(uv,2));
    if(G0.vc)G.setAttribute('color',new THREE.Float32BufferAttribute(col,3));G.setAttribute('skinIndex',new THREE.Uint16BufferAttribute(si,4));G.setAttribute('skinWeight',new THREE.Float32BufferAttribute(sw,4));G.userData.own=1;
    const sm=new THREE.SkinnedMesh(G,G0.mat);sm.castShadow=true;sm.receiveShadow=true;sm.frustumCulled=false;sm.name='skin';g.add(sm);sm.bind(sk,sm.matrixWorld)}
  g.userData.glb=name;return true}
// 开局先把所有模型解析好（贴图在城市生成期间解码完），避免第一次出现时是黑的
function glbPreload(){for(const n of new Set(Object.values(GLBMAP)))try{glbParse(n)}catch(e){console.warn('glb',n,e)}}glbPreload();
