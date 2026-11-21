// TX Game Club — standalone site. Accounts and data live in Firebase (Auth + Firestore).
import { firebaseConfig } from './firebase-config.js';

const FB_VERSION = '10.12.2';
const EMAIL_DOMAIN = 'txgc.example.com'; // never receives mail; usernames are mapped to these addresses for Firebase Auth

const $ = id => document.getElementById(id);
const el = (tag, cls, text) => { const e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; };
const STATUS = { yes: '参加', maybe: '可能来', no: '来不了' };
const WEEK = ['日', '一', '二', '三', '四', '五', '六'];
const PH_LABEL = { open: '报名中', closed: '报名已截止', live: '进行中', ended: '已结束' };
const NEEDS_LOGIN = new Set(['list', 'mine', 'event', 'edit', 'me', 'members']);

/* ---------- state ---------- */
let api = null, authKnown = false, setupNeeded = false, regPromise = null;
let me = null, profile = null, profileLoaded = false, isAdmin = false;
let events = new Map(), eventsLoaded = false, eventsError = false;
const rsvps = new Map(), rsvpSubs = new Map();
let unsubEvents = null, unsubUsers = null;
const pub = {}, pubPending = new Set();
let members = new Map(), membersLoaded = false;
let route = { view: 'home', id: null }, pendingRoute = null;
let tab = 'yes', myDraft = null, busy = false, confirmDel = null, confirmEvDel = false, formFor = null;

/* ---------- helpers ---------- */
function toast(msg) { const t = $('toast'); t.textContent = msg; t.hidden = false; clearTimeout(toast.t); toast.t = setTimeout(() => t.hidden = true, 2800); }
const pad = n => String(n).padStart(2, '0');
function fmtDate(iso) { const d = new Date(iso); if (isNaN(d)) return ''; return `${d.getFullYear()}年${d.getMonth() + 1}月${d.getDate()}日（周${WEEK[d.getDay()]}）${pad(d.getHours())}:${pad(d.getMinutes())}`; }
function tzLabel() { try { return Intl.DateTimeFormat().resolvedOptions().timeZone || ''; } catch (e) { return ''; } }
function toLocalInput(iso) { if (!iso) return ''; const d = new Date(iso); if (isNaN(d)) return ''; return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`; }
const clampNum = (v, a, b, d) => { const n = Math.round(Number(v)); return isFinite(n) ? Math.max(a, Math.min(b, n)) : d; };
const endOf = ev => Date.parse(ev.startAt) + (Number(ev.durationMin) || 120) * 60000;
function phaseOf(ev, now = Date.now()) {
  if (!ev || !ev.startAt) return 'none';
  if (now >= endOf(ev)) return 'ended';
  if (now >= Date.parse(ev.startAt)) return 'live';
  if (ev.deadline && now > Date.parse(ev.deadline)) return 'closed';
  return 'open';
}
function pillFor(ph) { const p = el('span', 'pill', PH_LABEL[ph] || ''); if (ph === 'closed' || ph === 'ended') p.classList.add('closed'); if (ph === 'live') p.classList.add('live'); return p; }
const sorted = () => [...events.entries()].filter(([, e]) => e && e.startAt && !isNaN(Date.parse(e.startAt))).sort((a, b) => Date.parse(a[1].startAt) - Date.parse(b[1].startAt));
const upcoming = () => sorted().filter(([, e]) => phaseOf(e) !== 'ended');
const past = () => sorted().filter(([, e]) => phaseOf(e) === 'ended').reverse();
function responses(evId) { const m = rsvps.get(evId); return m ? [...m.entries()].filter(([, r]) => r && STATUS[r.status]) : []; }
function counts(evId) { const c = { yes: 0, maybe: 0, no: 0 }; for (const [, r] of responses(evId)) c[r.status]++; return c; }
function myResp(evId) { const m = rsvps.get(evId); return (me && m && m.get(me.uid)) || null; }
function full(evId) { const ev = events.get(evId); const cap = Number(ev && ev.capacity) || 0; return cap > 0 && counts(evId).yes >= cap; }
const newId = () => 'e' + Date.now().toString(36) + Math.random().toString(36).slice(2, 6);
const emptyBox = text => el('div', 'empty', text);
function nameOf(uid) { return (pub[uid] && pub[uid].username) || (members.get(uid) || {}).username || '会员'; }
function copy(text, msg) {
  if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(text).then(() => toast(msg), () => fallbackCopy(text, msg));
  else fallbackCopy(text, msg);
}
function fallbackCopy(text, msg) {
  const ta = el('textarea'); ta.value = text; ta.style.cssText = 'position:fixed;left:-9999px'; document.body.append(ta); ta.select();
  let ok = false; try { ok = document.execCommand('copy'); } catch (e) { }
  ta.remove(); toast(ok ? msg : '复制失败，请手动选择文字复制');
}
function errText(e) {
  const c = (e && e.code) || '';
  if (c.includes('email-already-in-use')) return '这个用户名已经被注册了，换一个试试。';
  if (c.includes('invalid-credential') || c.includes('wrong-password') || c.includes('user-not-found') || c.includes('invalid-email')) return '用户名或密码不对。';
  if (c.includes('weak-password')) return '密码至少要 6 位。';
  if (c.includes('too-many-requests')) return '尝试次数太多，请过几分钟再试。';
  if (c.includes('network-request-failed') || c.includes('unavailable')) return '网络连接失败，请检查网络后再试。';
  if (c.includes('operation-not-allowed')) return '网站还没开启账号登录，请联系管理员。';
  if (c.includes('permission-denied')) return '你没有这个操作的权限。';
  return '出了点问题，请稍后再试。';
}
async function write(fn, okMsg) {
  if (busy) return false; busy = true;
  try { await fn(); if (okMsg) toast(okMsg); return true; }
  catch (e) { console.error(e); toast(errText(e)); return false; }
  finally { busy = false; }
}

/* ---------- username <-> login address ---------- */
const enc = new TextEncoder(), dec = new TextDecoder();
function usernameToEmail(u) { return 'u' + [...enc.encode(u.trim().toLowerCase())].map(b => b.toString(16).padStart(2, '0')).join('') + '@' + EMAIL_DOMAIN; }
function emailToUsername(email) {
  const m = /^u([0-9a-f]+)@/.exec(email || ''); if (!m) return '';
  try { return dec.decode(new Uint8Array(m[1].match(/../g).map(h => parseInt(h, 16)))); } catch (e) { return ''; }
}
const USERNAME_RE = /^[A-Za-z0-9_\u4e00-\u9fa5]{2,16}$/;
const PHONE_RE = /^\+?[0-9][0-9 -]{6,19}$/;

/* ---------- Firebase data layer ---------- */
async function firebaseApi(cfg) {
  const base = `https://www.gstatic.com/firebasejs/${FB_VERSION}/`;
  const [A, U, F] = await Promise.all([import(base + 'firebase-app.js'), import(base + 'firebase-auth.js'), import(base + 'firebase-firestore.js')]);
  const app = A.initializeApp(cfg), auth = U.getAuth(app), db = F.getFirestore(app);
  // Local testing only: open the site with ?emulator on localhost to use the Firebase emulators.
  if (/^(localhost|127\.0\.0\.1)$/.test(location.hostname) && new URLSearchParams(location.search).has('emulator')) {
    U.connectAuthEmulator(auth, 'http://127.0.0.1:9099', { disableWarnings: true });
    F.connectFirestoreEmulator(db, '127.0.0.1', 8080);
  }
  const list = snap => snap.docs.map(d => [d.id, d.data()]);
  return {
    onAuth: cb => U.onAuthStateChanged(auth, u => cb(u ? { uid: u.uid, email: u.email } : null)),
    async register({ username, phone, gameId, password }) {
      await U.setPersistence(auth, U.browserLocalPersistence);
      const cred = await U.createUserWithEmailAndPassword(auth, usernameToEmail(username), password);
      const now = new Date().toISOString(), b = F.writeBatch(db);
      b.set(F.doc(db, 'users', cred.user.uid), { username, phone, gameId, createdAt: now, updatedAt: now });
      b.set(F.doc(db, 'publicProfiles', cred.user.uid), { username, updatedAt: now });
      await b.commit();
    },
    async login(username, password, remember) {
      await U.setPersistence(auth, remember ? U.browserLocalPersistence : U.browserSessionPersistence);
      await U.signInWithEmailAndPassword(auth, usernameToEmail(username), password);
    },
    logout: () => U.signOut(auth),
    isAdmin: async uid => (await F.getDoc(F.doc(db, 'admins', uid))).exists(),
    getUser: async uid => { const s = await F.getDoc(F.doc(db, 'users', uid)); return s.exists() ? s.data() : null; },
    async saveProfile(uid, data, isNew) {
      const now = new Date().toISOString(), b = F.writeBatch(db);
      b.set(F.doc(db, 'users', uid), Object.assign({}, data, { updatedAt: now }, isNew ? { createdAt: now } : {}), { merge: !isNew });
      b.set(F.doc(db, 'publicProfiles', uid), { username: data.username, updatedAt: now });
      await b.commit();
    },
    getPublic: async uid => { const s = await F.getDoc(F.doc(db, 'publicProfiles', uid)); return s.exists() ? s.data() : null; },
    onEvents: (cb, err) => F.onSnapshot(F.collection(db, 'events'), s => cb(list(s)), err),
    saveEvent: (id, data) => F.setDoc(F.doc(db, 'events', id), data),
    deleteEvent: id => F.deleteDoc(F.doc(db, 'events', id)),
    onRsvps: (evId, cb, err) => F.onSnapshot(F.collection(db, 'events', evId, 'rsvps'), s => cb(list(s)), err),
    setRsvp: (evId, uid, data) => F.setDoc(F.doc(db, 'events', evId, 'rsvps', uid), data),
    deleteRsvp: (evId, uid) => F.deleteDoc(F.doc(db, 'events', evId, 'rsvps', uid)),
    onUsers: (cb, err) => F.onSnapshot(F.collection(db, 'users'), s => cb(list(s)), err)
  };
}

/* ---------- auth session ---------- */
function stopSubs() {
  if (unsubEvents) { unsubEvents(); unsubEvents = null; }
  if (unsubUsers) { unsubUsers(); unsubUsers = null; }
  for (const u of rsvpSubs.values()) u(); rsvpSubs.clear(); rsvps.clear();
}
async function onAuthChange(u) {
  stopSubs();
  const wasIn = !!me;
  me = u; profile = null; profileLoaded = false; isAdmin = false;
  events = new Map(); eventsLoaded = false; eventsError = false; members = new Map(); membersLoaded = false;
  authKnown = true;
  if (!me) {
    pendingRoute = !wasIn && NEEDS_LOGIN.has(route.view) ? location.hash.slice(1) : null;
    if (wasIn && NEEDS_LOGIN.has(route.view)) { location.hash = 'home'; return; }
    return render();
  }
  render();
  if (regPromise) { try { await regPromise; } catch (e) { } }
  try { isAdmin = await api.isAdmin(me.uid); } catch (e) { isAdmin = false; }
  try { profile = await api.getUser(me.uid); } catch (e) { profile = null; }
  profileLoaded = true;
  if (profile) pub[me.uid] = { username: profile.username };
  unsubEvents = api.onEvents(lst => { events = new Map(lst); eventsLoaded = true; syncRsvpSubs(); render(); }, e => { console.error(e); eventsLoaded = true; eventsError = true; render(); });
  if (isAdmin) unsubUsers = api.onUsers(lst => { members = new Map(lst); membersLoaded = true; render(); }, e => { console.error(e); membersLoaded = true; render(); });
  if (pendingRoute) { const r = pendingRoute; pendingRoute = null; go(r); }
  else if (route.view === 'login' || route.view === 'register') go('events');
  render();
}
function syncRsvpSubs() {
  const keep = new Set([...upcoming(), ...past().slice(0, 20)].map(([id]) => id));
  for (const [id, un] of rsvpSubs) if (!keep.has(id)) { un(); rsvpSubs.delete(id); rsvps.delete(id); }
  for (const id of keep) if (!rsvpSubs.has(id)) {
    rsvpSubs.set(id, api.onRsvps(id, lst => { rsvps.set(id, new Map(lst)); loadNames(lst.map(([uid]) => uid)); render(); }, e => console.error(e)));
  }
}
function loadNames(uids) {
  const missing = uids.filter(u => !pub[u] && !pubPending.has(u));
  if (!missing.length) return;
  missing.forEach(u => pubPending.add(u));
  Promise.all(missing.map(u => api.getPublic(u).then(p => { pub[u] = p || { username: '' }; }).catch(() => { pub[u] = { username: '' }; })))
    .then(() => { missing.forEach(u => pubPending.delete(u)); render(); });
}

/* ---------- routing ---------- */
function parseRoute() {
  const h = location.hash.slice(1);
  const simple = { events: 'list', signup: 'list', mine: 'mine', login: 'login', register: 'register', me: 'me', members: 'members', new: 'edit' };
  if (simple[h]) return { view: simple[h], id: null };
  let m = h.match(/^event-([a-z0-9]+)$/); if (m) return { view: 'event', id: m[1] };
  m = h.match(/^edit-([a-z0-9]+)$/); if (m) return { view: 'edit', id: m[1] };
  return { view: 'home', id: null };
}
function go(h) { if (location.hash === '#' + h) onRoute(); else location.hash = h; }
function onRoute() {
  const r = parseRoute(), changed = r.view !== route.view || r.id !== route.id;
  route = r;
  if (changed) { myDraft = null; confirmDel = null; confirmEvDel = false; tab = 'yes'; formFor = null; syncTabs(); setMenu(false); }
  if (NEEDS_LOGIN.has(route.view) && authKnown && !me) pendingRoute = location.hash.slice(1);
  $('viewHome').hidden = route.view !== 'home'; $('viewApp').hidden = route.view === 'home';
  if (changed) window.scrollTo(0, 0);
  render();
}

/* ---------- render ---------- */
const SECTIONS = ['secGate', 'secSetup', 'secList', 'secMine', 'secEvent', 'secEdit', 'secMissing', 'secLogin', 'secRegister', 'secMe', 'secMembers'];
function show(id) { SECTIONS.forEach(s => $(s).hidden = s !== id); }
function render() {
  renderAuthBoxes(); renderDrawer(); renderHome();
  if (route.view === 'home') return;
  renderTop();
  if (setupNeeded) return show('secSetup');
  if (!authKnown) return show(null);
  if (route.view === 'login') { show('secLogin'); return renderLogin(); }
  if (route.view === 'register') { show('secRegister'); return renderRegister(); }
  if (NEEDS_LOGIN.has(route.view) && !me) return show('secGate');
  if (route.view === 'me') { show('secMe'); return renderMe(); }
  if (route.view === 'members') { if (!isAdmin) return missing('只有管理员可以查看会员名单', '会员的电话和游戏 ID 只对管理员开放。'); show('secMembers'); return renderMembers(); }
  if (route.view === 'list') { show('secList'); return renderList(); }
  if (route.view === 'mine') { show('secMine'); return renderMine(); }
  const cur = route.id ? events.get(route.id) : null;
  if (route.id && eventsLoaded && !cur) return missing('找不到这个活动', '它可能已经被管理员删除了。');
  if (route.view === 'event') { show('secEvent'); return renderEvent(); }
  if (route.view === 'edit') { if (!isAdmin) return missing('只有管理员可以编辑活动', '如果你想办活动，请联系 TX Game Club 的管理员。'); show('secEdit'); return renderEdit(); }
}
function missing(title, text) { show('secMissing'); $('missTitle').textContent = title; $('missText').textContent = text; }

function renderAuthBoxes() {
  document.querySelectorAll('[data-auth]').forEach(box => {
    box.replaceChildren();
    if (!authKnown || setupNeeded) return;
    if (me) {
      const a = el('a', 'userchip'); a.href = '#me';
      const n = profile ? profile.username : emailToUsername(me.email) || '我';
      const av = el('span', 'av sm', n.slice(0, 1).toUpperCase());
      a.append(av, el('span', 'uname', n)); box.append(a);
    } else {
      const lg = el('a', 'btn-login', '登入'); lg.href = '#login';
      const rg = el('a', 'lnk-reg', '注册'); rg.href = '#register';
      box.append(lg, rg);
    }
  });
}
function renderTop() {
  const back = $('backLink'), hb = $('topHost');
  hb.hidden = true;
  if (route.view === 'list') { back.href = '#home'; back.textContent = '← 返回首页'; if (isAdmin) { hb.textContent = '+ 添加活动'; hb.hidden = false; } }
  else if (route.view === 'event') { back.href = '#events'; back.textContent = '← 全部活动'; if (isAdmin && events.get(route.id)) { hb.textContent = '编辑活动'; hb.hidden = false; } }
  else if (route.view === 'edit') { back.href = route.id ? '#event-' + route.id : '#events'; back.textContent = '← 返回'; }
  else { back.href = '#home'; back.textContent = '← 返回首页'; }
}

/* ---------- home ---------- */
function renderHome() {
  const pill = $('nPill'), name = $('nName'), when = $('nWhen'), nums = $('nNums'), link = $('nLink'), acts = $('nAuth');
  pill.className = 'pill'; link.hidden = true; nums.hidden = true; acts.hidden = true;
  $('homeAdd').hidden = !isAdmin;
  const up = upcoming();
  $('allLink').hidden = !(me && eventsLoaded && events.size);
  $('allLink').textContent = up.length ? `全部活动（${up.length} 场即将开始）→` : '查看往期活动 →';
  if (setupNeeded) { pill.textContent = '未连接'; pill.classList.add('closed'); name.textContent = '网站还没连接数据库'; when.textContent = '管理员按设置说明填好 Firebase 配置后，这里就会显示活动。'; return; }
  if (!authKnown) { pill.textContent = '读取中'; name.textContent = '正在读取…'; when.textContent = ''; return; }
  if (!me) { pill.textContent = '会员专享'; name.textContent = '登入后查看活动'; when.textContent = '活动信息只对会员开放。注册只要一分钟。'; acts.hidden = false; return; }
  if (!eventsLoaded) { pill.textContent = '读取中'; name.textContent = '正在读取活动信息…'; when.textContent = ''; return; }
  if (!up.length) { pill.textContent = '筹备中'; pill.classList.add('closed'); name.textContent = '下一场活动即将公布'; when.textContent = isAdmin ? '点下面的「添加活动」发布一场吧。' : '管理员还在准备，过几天再来看看。'; return; }
  const [id, ev] = up[0], ph = phaseOf(ev);
  pill.textContent = PH_LABEL[ph]; if (ph === 'closed') pill.classList.add('closed'); if (ph === 'live') pill.classList.add('live');
  name.textContent = ev.title || '未命名活动';
  when.textContent = [fmtDate(ev.startAt), ev.game, ev.place].filter(Boolean).join(' · ');
  link.hidden = false; link.href = '#event-' + id;
  nums.hidden = false;
  const days = Math.ceil((Date.parse(ev.startAt) - Date.now()) / 864e5);
  $('nDays').textContent = ph === 'live' ? '0' : String(Math.max(0, days));
  $('nDays').nextElementSibling.textContent = ph === 'live' ? '正在进行' : days <= 0 ? '今天开始' : '天后开始';
  const cap = Number(ev.capacity) || 0, c = counts(id);
  $('nSeats').textContent = cap > 0 ? `${c.yes}/${cap}` : String(c.yes);
  $('nSeatsLabel').textContent = cap > 0 ? '名额已报' : '人确认参加';
}

/* ---------- lists ---------- */
function listOf(arr) {
  const ul = el('ul', 'evlist');
  for (const [id, ev] of arr) {
    const d = new Date(ev.startAt), ph = phaseOf(ev), c = counts(id), cap = Number(ev.capacity) || 0, mine = myResp(id);
    const a = el('a', 'evcard'); a.href = '#event-' + id;
    const date = el('div', 'evdate'); date.append(el('b', null, String(d.getDate())), el('span', null, `${d.getMonth() + 1}月 周${WEEK[d.getDay()]}`));
    const info = el('div', 'evinfo');
    info.append(pillFor(ph), el('h3', null, ev.title || '未命名活动'), el('p', null, [`${pad(d.getHours())}:${pad(d.getMinutes())} 开始`, ev.game, ev.place].filter(Boolean).join(' · ')));
    const side = el('div', 'evside');
    const seats = el('span'); seats.append(document.createTextNode('参加 '), el('b', null, cap > 0 ? `${c.yes}/${cap}` : String(c.yes)));
    side.append(seats);
    if (mine) side.append(el('span', 'status ' + mine.status, '我：' + STATUS[mine.status]));
    side.append(el('span', 'go', ph === 'ended' || mine ? '查看 →' : '报名 →'));
    a.append(date, info, side);
    const li = el('li'); li.append(a); ul.append(li);
  }
  return ul;
}
function renderList() {
  const box = $('listBody'); box.replaceChildren();
  if (!eventsLoaded) return box.append(emptyBox('正在读取活动…'));
  if (eventsError) return box.append(emptyBox('读取活动失败，请刷新页面再试。'));
  const up = upcoming(), ps = past();
  if (!up.length) box.append(emptyBox(isAdmin ? '还没有即将开始的活动。点右上角「添加活动」发布一场吧。' : '暂时没有即将开始的活动，过几天再来看看。'));
  else box.append(listOf(up));
  if (ps.length) { const sec = el('section', 'list-sec past'); sec.append(el('h2', null, '往期活动'), listOf(ps)); box.append(sec); }
}
const myEvents = () => sorted().filter(([id]) => myResp(id));
function renderMine() {
  const box = $('mineBody'); box.replaceChildren();
  if (!eventsLoaded) return box.append(emptyBox('正在读取你的报名…'));
  const all = myEvents(), up = all.filter(([, e]) => phaseOf(e) !== 'ended'), ps = all.filter(([, e]) => phaseOf(e) === 'ended').reverse();
  if (!all.length) { const e = emptyBox('你还没有报名任何活动。'); const a = el('a', 'cardlink', '去看看有哪些活动 →'); a.href = '#events'; e.append(el('br'), a); return box.append(e); }
  box.append(up.length ? listOf(up) : emptyBox('你报名的活动都已经结束了。'));
  if (ps.length) { const sec = el('section', 'list-sec past'); sec.append(el('h2', null, '已结束'), listOf(ps)); box.append(sec); }
}

/* ---------- event page ---------- */
function renderEvent() {
  const id = route.id, ev = events.get(id);
  renderTicket(id, ev);
  const sd = !!(ev && ev.description); $('descPanel').hidden = !sd; if (sd) $('desc').textContent = ev.description;
  document.title = ev && ev.title ? ev.title + ' · TX Game Club' : 'TX Game Club';
  const typing = document.activeElement && $('rsvpBody').contains(document.activeElement);
  if (!typing) renderRsvp(id, ev);
  renderRoster(id);
  $('ownerBar').hidden = !isAdmin || !ev;
}
function renderTicket(id, ev) {
  const main = $('tMain'), stub = $('tStub');
  main.replaceChildren(); stub.replaceChildren();
  if (!ev) {
    main.append(el('span', 'pill', '读取中'));
    const s1 = el('div', 'skel'); s1.style.cssText = 'width:70%;height:40px'; const s2 = el('div', 'skel'); s2.style.width = '85%'; main.append(s1, s2);
    stub.append(el('div', 'stub-label', '距离开始'), el('div', 'stub-big', '…'));
    return;
  }
  const ph = phaseOf(ev);
  main.append(pillFor(ph), el('h1', null, ev.title || '未命名活动'));
  const dl = el('dl', 'meta');
  const add = (k, v, small) => { const dd = el('dd', null, v); if (small) dd.append(el('small', null, small)); dl.append(el('dt', null, k), dd); return dd; };
  const end = new Date(endOf(ev));
  add('时间', fmtDate(ev.startAt), `约 ${Number(ev.durationMin) || 120} 分钟，到 ${pad(end.getHours())}:${pad(end.getMinutes())} 结束 · 按你的时区 ${tzLabel()} 显示`);
  if (ev.game) add('游戏', ev.game);
  if (ev.place) add('方式', ev.place);
  if (ev.link) {
    const dd = add('链接', ''), row = el('div', 'linkrow');
    const a = el('a', null, ev.link); a.href = /^https?:\/\//i.test(ev.link) ? ev.link : 'https://' + ev.link; a.target = '_blank'; a.rel = 'noopener';
    const cp = el('button', 'mini', '复制'); cp.type = 'button'; cp.onclick = () => copy(ev.link, '链接已复制');
    row.append(a, cp); dd.append(row);
  }
  if (ev.deadline) add('报名截止', fmtDate(ev.deadline));
  const cap = Number(ev.capacity) || 0;
  add('名额', cap > 0 ? `${cap} 人` : '不限');
  main.append(dl);
  const c = counts(id);
  if (ph === 'open' || ph === 'closed') {
    stub.append(el('div', 'stub-label', '距离开始'));
    const cd = el('div', 'count'); cd.id = 'cd'; cd.setAttribute('aria-label', '倒计时');
    ['天', '时', '分', '秒'].forEach(u => { const d = el('div'); d.append(el('b', null, '--'), el('span', null, u)); cd.append(d); });
    stub.append(cd);
  } else stub.append(el('div', 'stub-big', ph === 'live' ? '正在进行！' : '活动已结束'));
  const seats = el('div', 'seats');
  seats.append(el('span', 'stub-label', '已确认参加'), el('br'), el('b', null, String(c.yes)), document.createTextNode(cap > 0 ? ` / ${cap} 人` : ' 人'));
  if (cap > 0) { const bar = el('div', 'bar'), i = el('i'); i.style.width = Math.min(100, c.yes / cap * 100) + '%'; bar.append(i); seats.append(bar); }
  stub.append(seats);
  if (ph === 'open' || ph === 'closed') { const ics = el('button', 'ics', '加入我的日历'); ics.type = 'button'; ics.onclick = () => saveIcs(id, ev); stub.append(ics); }
  tick();
}
function tick() {
  const cd = $('cd'); if (!cd || route.view !== 'event') return;
  const ev = events.get(route.id); if (!ev) return;
  let ms = Math.max(0, Date.parse(ev.startAt) - Date.now());
  const d = Math.floor(ms / 864e5); ms -= d * 864e5;
  const h = Math.floor(ms / 36e5); ms -= h * 36e5;
  const m = Math.floor(ms / 6e4); ms -= m * 6e4;
  const s = Math.floor(ms / 1e3), b = cd.querySelectorAll('b');
  [d, h, m, s].forEach((v, i) => { const t = pad(v); if (b[i].textContent !== t) b[i].textContent = t; });
}
let sig = '';
setInterval(() => { tick(); const s = sorted().map(([id, e]) => id + phaseOf(e)).join('|'); if (s !== sig) { sig = s; if (eventsLoaded) render(); } }, 1000);

function renderRsvp(id, ev) {
  const body = $('rsvpBody'); body.replaceChildren(); $('rsvpSub').textContent = '';
  if (!ev) { const s = el('div', 'skel'); s.style.width = '80%'; return body.append(s); }
  const ph = phaseOf(ev), mine = myResp(id);
  if (ph === 'ended') return body.append(el('p', 'note', mine ? `活动已结束。你当时的回复是「${STATUS[mine.status]}」。` : '活动已结束，报名已关闭。'));
  if (profileLoaded && !profile) {
    body.append(el('p', 'note', '报名前请先补全你的会员资料（电话号码和游戏 ID）。'));
    const a = el('a', 'btn', '去补全资料'); a.href = '#me'; a.style.textDecoration = 'none'; a.style.alignSelf = 'flex-start'; return body.append(a);
  }
  const locked = (ph === 'closed' || ph === 'live') && !isAdmin;
  if (mine && !myDraft) {
    const box = el('div', 'mine'), t = el('div', 'who'); t.style.flex = '1';
    t.append(el('b', null, mine.status === 'yes' ? '你已报名，到时见！' : mine.status === 'maybe' ? '你标记了可能来' : '你说这次来不了'));
    if (mine.note) t.append(el('span', null, '留言：' + mine.note));
    box.append(el('span', 'status ' + mine.status, STATUS[mine.status]), t); body.append(box);
    if (locked) return body.append(el('p', 'note', ph === 'live' ? '活动进行中，回复已锁定。' : '报名已截止，回复已锁定。'));
    const act = el('div', 'actions');
    const ch = el('button', 'ghost', '修改回复'); ch.type = 'button'; ch.onclick = () => { myDraft = { status: mine.status, note: mine.note || '' }; renderRsvp(id, ev); };
    const del = el('button', 'ghost danger', confirmDel === 'me' ? '确定撤回？' : '撤回报名'); del.type = 'button';
    del.onclick = async () => { if (confirmDel !== 'me') { confirmDel = 'me'; return renderRsvp(id, ev); } confirmDel = null; await write(() => api.deleteRsvp(id, me.uid), '已撤回报名'); };
    act.append(ch, del); return body.append(act);
  }
  if (locked) return body.append(el('p', 'note', ph === 'live' ? '活动已经开始，报名已关闭。' : '报名已截止。'));
  const d = myDraft || (myDraft = { status: '', note: '' });
  const isFull = full(id) && !(mine && mine.status === 'yes');
  if (isFull) $('rsvpSub').textContent = '「参加」名额已满';
  const submit = el('button', 'btn', mine ? '更新回复' : '提交报名'); submit.type = 'button'; submit.disabled = !d.status;
  const seg = el('div', 'seg'); seg.setAttribute('role', 'group'); seg.setAttribute('aria-label', '你会来吗');
  [['yes', '参加', '我会来'], ['maybe', '可能来', '还不确定'], ['no', '来不了', '这次算了']].forEach(([v, a, b]) => {
    const btn = el('button'); btn.type = 'button'; btn.dataset.v = v; btn.setAttribute('aria-pressed', d.status === v ? 'true' : 'false');
    btn.append(document.createTextNode(a), el('small', null, v === 'yes' && isFull ? '名额已满' : b));
    btn.disabled = v === 'yes' && isFull;
    btn.onclick = () => { d.status = v; seg.querySelectorAll('button').forEach(x => x.setAttribute('aria-pressed', x === btn ? 'true' : 'false')); submit.disabled = false; };
    seg.append(btn);
  });
  const note = el('label', 'f', '想说的话（可不填，大家都看得到）'); const nt = el('input'); nt.maxLength = 120; nt.value = d.note; nt.placeholder = '例如：可能晚到十分钟'; nt.oninput = () => d.note = nt.value; note.append(nt);
  submit.onclick = async () => {
    if (!d.status) return;
    const ok = await write(() => api.setRsvp(id, me.uid, { status: d.status, note: d.note.trim().slice(0, 120), updatedAt: new Date().toISOString() }), d.status === 'yes' ? '报名成功，到时见！' : '已记下你的回复');
    if (ok) myDraft = null;
    renderRsvp(id, events.get(id));
  };
  const act = el('div', 'actions'); act.append(submit);
  if (mine) { const cancel = el('button', 'ghost', '取消'); cancel.type = 'button'; cancel.onclick = () => { myDraft = null; renderRsvp(id, ev); }; act.append(cancel); }
  body.append(el('p', 'note', `将以「${profile ? profile.username : '你的用户名'}」报名，其他会员只看得到你的用户名。`), seg, note, act);
}

function syncTabs() { document.querySelectorAll('#tabs button').forEach(x => x.setAttribute('aria-selected', x.dataset.t === tab ? 'true' : 'false')); }
document.querySelectorAll('#tabs button').forEach(b => b.onclick = () => { tab = b.dataset.t; syncTabs(); renderRoster(route.id); });
const COLORS = ['#e3182a', '#8e0d18', '#ff3344', '#4a4446', '#b3121f', '#6b6466'];
function colorFor(id) { let h = 0; for (const ch of id) h = (h * 31 + ch.charCodeAt(0)) >>> 0; return COLORS[h % COLORS.length]; }
function renderRoster(id) {
  const c = counts(id);
  $('nYes').textContent = c.yes; $('nMaybe').textContent = c.maybe; $('nNo').textContent = c.no;
  const list = $('roster'), empty = $('rosterEmpty');
  list.replaceChildren();
  if (!rsvps.has(id)) { empty.hidden = false; empty.textContent = '正在读取报名名单…'; return; }
  const rows = responses(id).filter(([, r]) => r.status === tab).sort((a, b) => String(a[1].updatedAt).localeCompare(String(b[1].updatedAt)));
  empty.hidden = rows.length > 0;
  empty.textContent = tab === 'yes' ? '还没有人报名参加，来当第一个吧。' : tab === 'maybe' ? '还没有人标记「可能来」。' : '还没有人说来不了。';
  for (const [uid, r] of rows) {
    const name = nameOf(uid), li = el('li');
    const av = el('div', 'av', name.slice(0, 1).toUpperCase()); av.style.background = colorFor(uid);
    const who = el('div', 'who'); who.append(el('b', null, uid === me.uid ? name + '（你）' : name));
    if (isAdmin) { const m = members.get(uid); if (m) who.append(el('span', null, `游戏 ID：${m.gameId || '—'} · 电话：${m.phone || '—'}`)); }
    if (r.note) who.append(el('p', null, r.note));
    const side = el('div', 'side');
    const d = new Date(r.updatedAt); if (!isNaN(d)) side.append(el('span', 'note', `${d.getMonth() + 1}/${d.getDate()} ${pad(d.getHours())}:${pad(d.getMinutes())}`));
    if (isAdmin && uid !== me.uid) {
      const rm = el('button', 'mini danger', confirmDel === uid ? '确认移除' : '移除'); rm.type = 'button';
      rm.onclick = async () => { if (confirmDel !== uid) { confirmDel = uid; return renderRoster(id); } confirmDel = null; await write(() => api.deleteRsvp(id, uid), '已移除'); };
      side.append(rm);
    }
    li.append(av, who, side); list.append(li);
  }
}
$('copyList').onclick = () => {
  const id = route.id, ev = events.get(id); if (!ev) return;
  const rs = responses(id), lines = [`${ev.title || '活动'} 报名名单`, fmtDate(ev.startAt), ''];
  for (const st of ['yes', 'maybe', 'no']) {
    const g = rs.filter(([, r]) => r.status === st);
    lines.push(`【${STATUS[st]}】${g.length} 人`);
    g.forEach(([uid, r], i) => { const m = members.get(uid) || {}; lines.push(`${i + 1}. ${nameOf(uid)}${m.gameId ? '（游戏 ID：' + m.gameId + '）' : ''}${m.phone ? ' 电话：' + m.phone : ''}${r.note ? ' — ' + r.note : ''}`); });
    lines.push('');
  }
  copy(lines.join('\n').trim(), '名单已复制');
};
function saveIcs(id, ev) {
  const f = iso => new Date(iso).toISOString().replace(/[-:]/g, '').replace(/\.\d{3}/, '');
  const esc = s => String(s || '').replace(/\\/g, '\\\\').replace(/\n/g, '\\n').replace(/([,;])/g, '\\$1');
  const ics = ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//tx-game-club//CN', 'BEGIN:VEVENT',
    'UID:' + id + '@tx-game-club', 'DTSTAMP:' + f(new Date().toISOString()), 'DTSTART:' + f(ev.startAt), 'DTEND:' + f(new Date(endOf(ev)).toISOString()),
    'SUMMARY:' + esc(ev.title), 'DESCRIPTION:' + esc([ev.game && '游戏：' + ev.game, ev.place && '方式：' + ev.place, ev.link, ev.description].filter(Boolean).join('\n')),
    'LOCATION:' + esc(ev.place || ''), 'BEGIN:VALARM', 'TRIGGER:-PT30M', 'ACTION:DISPLAY', 'DESCRIPTION:' + esc(ev.title), 'END:VALARM', 'END:VEVENT', 'END:VCALENDAR'].join('\r\n');
  const url = URL.createObjectURL(new Blob([ics], { type: 'text/calendar' }));
  const a = el('a'); a.href = url; a.download = 'tx-game-club-event.ics'; document.body.append(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 2000);
}

/* ---------- event editor (admin) ---------- */
function renderEdit() {
  const id = route.id, key = id || 'new';
  if (id && !events.get(id)) return;
  $('editTitle').textContent = id ? '编辑活动' : '添加新活动';
  $('fDelete').hidden = !id; $('fDelete').textContent = confirmEvDel ? '确定删除？' : '删除这个活动';
  $('fCancel').href = id ? '#event-' + id : '#events';
  if (formFor === key) return;
  formFor = key;
  const e = (id && events.get(id)) || {};
  $('fTitle').value = e.title || ''; $('fGame').value = e.game || ''; $('fPlace').value = e.place || '';
  $('fStart').value = toLocalInput(e.startAt); $('fDur').value = e.durationMin || 120;
  $('fDeadline').value = toLocalInput(e.deadline); $('fCap').value = e.capacity || 0;
  $('fLink').value = e.link || ''; $('fDesc').value = e.description || ''; $('fMsg').textContent = '';
}
$('editForm').addEventListener('submit', async ev => {
  ev.preventDefault();
  if (busy) return;
  const start = new Date($('fStart').value), dl = $('fDeadline').value ? new Date($('fDeadline').value) : null;
  if (isNaN(start)) { $('fMsg').textContent = '请填写开始时间。'; return; }
  if (dl && dl > start) { $('fMsg').textContent = '报名截止时间要早于开始时间。'; return; }
  const id = route.id || newId(), old = events.get(id) || {};
  const body = {
    title: $('fTitle').value.trim(), game: $('fGame').value.trim(), place: $('fPlace').value.trim(),
    startAt: start.toISOString(), durationMin: clampNum($('fDur').value, 10, 1440, 120),
    deadline: dl ? dl.toISOString() : '', capacity: clampNum($('fCap').value, 0, 999, 0),
    link: $('fLink').value.trim(), description: $('fDesc').value.trim(), hostTimeZone: tzLabel(),
    createdAt: old.createdAt || new Date().toISOString(), updatedAt: new Date().toISOString()
  };
  $('fSave').disabled = true; $('fMsg').textContent = '保存中…';
  const ok = await write(() => api.saveEvent(id, body), route.id ? '活动已更新' : '新活动已发布');
  $('fSave').disabled = false; $('fMsg').textContent = '';
  if (ok) go('event-' + id);
});
$('fDelete').onclick = async () => {
  if (!route.id) return;
  if (!confirmEvDel) { confirmEvDel = true; return renderEdit(); }
  confirmEvDel = false;
  if (await write(() => api.deleteEvent(route.id), '活动已删除')) go('events');
};

/* ---------- login / register ---------- */
function renderLogin() {
  const done = !!me; $('loginForm').hidden = done; $('loginDone').hidden = !done;
  if (done) $('loginDoneName').textContent = profile ? profile.username : emailToUsername(me.email);
}
function renderRegister() {
  const done = !!me; $('regForm').hidden = done; $('regDone').hidden = !done;
}
$('loginForm').addEventListener('submit', async e => {
  e.preventDefault(); if (busy) return;
  const u = $('lUser').value.trim(), p = $('lPass').value;
  if (!u || !p) { $('lMsg').textContent = '请填写用户名和密码。'; return; }
  busy = true; $('lBtn').disabled = true; $('lMsg').textContent = '登入中…';
  try { await api.login(u, p, $('lRemember').checked); $('lMsg').textContent = ''; $('lPass').value = ''; toast('欢迎回来！'); }
  catch (er) { $('lMsg').textContent = errText(er); }
  finally { busy = false; $('lBtn').disabled = false; }
});
$('regForm').addEventListener('submit', async e => {
  e.preventDefault(); if (busy) return;
  const username = $('rUser').value.trim(), phone = $('rPhone').value.trim(), gameId = $('rGame').value.trim(), p1 = $('rPass').value, p2 = $('rPass2').value;
  const msg = t => { $('rMsg').textContent = t; };
  if (!USERNAME_RE.test(username) || enc.encode(username).length > 30) return msg('用户名要 2–16 个字，只能用中文、英文字母、数字和下划线。');
  if (!PHONE_RE.test(phone)) return msg('请填写正确的电话号码，可以带国家代码，例如 +60 12-345 6789。');
  if (!gameId || gameId.length > 40) return msg('请填写游戏 ID（最多 40 个字）。');
  if (p1.length < 6) return msg('密码至少要 6 位。');
  if (p1 !== p2) return msg('两次输入的密码不一样。');
  busy = true; $('rBtn').disabled = true; msg('注册中…');
  try { regPromise = api.register({ username, phone, gameId, password: p1 }); await regPromise; profile = { username, phone, gameId }; pub[me ? me.uid : ''] = { username }; msg(''); $('rPass').value = $('rPass2').value = ''; toast('注册成功，欢迎加入 TX Game Club！'); }
  catch (er) { msg(errText(er)); }
  finally { busy = false; regPromise = null; $('rBtn').disabled = false; }
});

/* ---------- my profile ---------- */
let meFormFor = null;
function renderMe() {
  const isNew = profileLoaded && !profile;
  $('meIntro').textContent = isNew ? '你的账号还缺少会员资料，请补全后才能报名。' : '电话号码和游戏 ID 只有管理员看得到；其他会员只看得到你的用户名。';
  $('meUid').textContent = me.uid;
  $('meRole').textContent = isAdmin ? '管理员' : '会员';
  const key = me.uid + (profile ? '1' : '0');
  if (meFormFor !== key && profileLoaded) {
    meFormFor = key;
    $('mUser').value = profile ? profile.username : emailToUsername(me.email);
    $('mPhone').value = profile ? profile.phone || '' : '';
    $('mGame').value = profile ? profile.gameId || '' : '';
  }
}
$('meForm').addEventListener('submit', async e => {
  e.preventDefault(); if (busy) return;
  const phone = $('mPhone').value.trim(), gameId = $('mGame').value.trim(), username = $('mUser').value.trim();
  if (!PHONE_RE.test(phone)) { $('mMsg').textContent = '请填写正确的电话号码。'; return; }
  if (!gameId || gameId.length > 40) { $('mMsg').textContent = '请填写游戏 ID（最多 40 个字）。'; return; }
  const isNew = !profile;
  const ok = await write(() => api.saveProfile(me.uid, { username, phone, gameId }, isNew), '资料已保存');
  if (ok) { profile = Object.assign({}, profile || {}, { username, phone, gameId }); pub[me.uid] = { username }; $('mMsg').textContent = ''; render(); }
});
$('meCopyUid').onclick = () => copy(me.uid, '编号已复制');
$('logout').onclick = () => write(() => api.logout(), '已退出登入');

/* ---------- members (admin) ---------- */
function renderMembers() {
  const body = $('membersBody'); body.replaceChildren();
  if (!membersLoaded) return body.append(emptyBox('正在读取会员名单…'));
  const rows = [...members.entries()].sort((a, b) => String(a[1].createdAt).localeCompare(String(b[1].createdAt)));
  $('membersCount').textContent = `共 ${rows.length} 位会员`;
  if (!rows.length) return body.append(emptyBox('还没有会员注册。'));
  const wrap = el('div', 'tablewrap'), t = el('table', 'mtable'), thead = el('thead'), tr = el('tr');
  ['用户名', '电话号码', '游戏 ID', '注册时间'].forEach(h => tr.append(el('th', null, h))); thead.append(tr); t.append(thead);
  const tb = el('tbody');
  for (const [uid, m] of rows) {
    const r = el('tr'), d = new Date(m.createdAt);
    r.append(el('td', null, m.username || '—'), el('td', null, m.phone || '—'), el('td', null, m.gameId || '—'), el('td', null, isNaN(d) ? '—' : `${d.getFullYear()}/${d.getMonth() + 1}/${d.getDate()}`));
    if (uid === me.uid) r.classList.add('self');
    tb.append(r);
  }
  t.append(tb); wrap.append(t); body.append(wrap);
}
$('copyMembers').onclick = () => {
  const rows = [...members.values()].sort((a, b) => String(a.createdAt).localeCompare(String(b.createdAt)));
  copy(['TX Game Club 会员名单', '用户名\t电话号码\t游戏 ID', ...rows.map(m => `${m.username}\t${m.phone}\t${m.gameId}`)].join('\n'), '会员名单已复制');
};

/* ---------- menu drawer ---------- */
const drawer = $('drawer'), scrim = $('scrim');
let menuOpener = null;
function setMenu(open) {
  if (open === drawer.classList.contains('open')) return;
  drawer.classList.toggle('open', open); drawer.setAttribute('aria-hidden', open ? 'false' : 'true');
  if (open) { scrim.hidden = false; requestAnimationFrame(() => scrim.classList.add('open')); }
  else { scrim.classList.remove('open'); setTimeout(() => { if (!drawer.classList.contains('open')) scrim.hidden = true; }, 260); }
  document.querySelectorAll('[data-menu]').forEach(b => b.setAttribute('aria-expanded', open ? 'true' : 'false'));
  document.body.style.overflow = open ? 'hidden' : '';
  if (open) setTimeout(() => { const cur = drawer.querySelector('[aria-current="page"]') || drawer.querySelector('.dnav a'); try { cur.focus({ preventScroll: true }); } catch (e) { } }, 60);
  else if (menuOpener) { try { menuOpener.focus({ preventScroll: true }); } catch (e) { } menuOpener = null; }
}
document.querySelectorAll('[data-menu]').forEach(b => b.onclick = () => { menuOpener = b; setMenu(true); });
$('dClose').onclick = () => setMenu(false);
scrim.onclick = () => setMenu(false);
drawer.querySelectorAll('a').forEach(a => a.addEventListener('click', () => setMenu(false)));
addEventListener('keydown', e => { if (e.key === 'Escape' && drawer.classList.contains('open')) setMenu(false); });
function renderDrawer() {
  const sec = { home: 'home', mine: 'mine', me: 'me', members: 'members', login: 'me', register: 'me' }[route.view] || 'list';
  drawer.querySelectorAll('[data-nav]').forEach(a => { if (a.dataset.nav === sec) a.setAttribute('aria-current', 'page'); else a.removeAttribute('aria-current'); });
  $('dMembersItem').hidden = !isAdmin;
  const nUp = me && eventsLoaded ? upcoming().length : 0, nMine = me && eventsLoaded ? myEvents().filter(([, e]) => phaseOf(e) !== 'ended').length : 0;
  $('dEvents').hidden = !nUp; $('dEvents').textContent = nUp;
  $('dMine').hidden = !nMine; $('dMine').textContent = nMine;
  $('dMeLabel').textContent = me ? '我的资料' : '登入 / 注册';
  $('dMeSub').textContent = me ? '电话、游戏 ID 和退出登入' : '会员才能查看活动和报名';
  $('dMeLink').href = me ? '#me' : '#login';
}

/* ---------- wiring + boot ---------- */
addEventListener('hashchange', onRoute);
$('toJoin').onclick = () => $('join').scrollIntoView({ behavior: 'smooth', block: 'start' });
$('homeAdd').onclick = () => go('new');
$('editBtn').onclick = () => go('edit-' + route.id);
$('topHost').onclick = () => go(route.view === 'event' ? 'edit-' + route.id : 'new');

onRoute();
(async () => {
  try {
    if (window.__TX_MOCK_API__) api = window.__TX_MOCK_API__;
    else if (!firebaseConfig || !firebaseConfig.apiKey) { setupNeeded = true; authKnown = true; render(); return; }
    else api = await firebaseApi(firebaseConfig);
    api.onAuth(u => { onAuthChange(u); });
  } catch (e) {
    console.error(e); setupNeeded = true; authKnown = true; render();
  }
})();
