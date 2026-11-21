// Preview-only data layer: same interface as the Firebase layer in app.js, but everything
// lives in this browser (localStorage). Used to try the site without a Firebase project.
(() => {
  const KEY = 'imperial-preview-v1', SKEY = 'txgc-preview-session';
  const day = 864e5;
  const at = (d, h, m = 0) => { const t = new Date(Date.now() + d * day); t.setHours(h, m, 0, 0); return t.toISOString(); };
  function seed() {
    const now = new Date().toISOString();
    return {
      accounts: { admin: { uid: 'u_admin', pw: '123456' }, '小明': { uid: 'u_xm', pw: '123456' }, '阿杰': { uid: 'u_aj', pw: '123456' } },
      admins: ['u_admin'],
      users: {
        u_admin: { username: 'admin', phone: '+60 12-000 0000', gameId: 'IMP-ADMIN', createdAt: now, updatedAt: now },
        u_xm: { username: '小明', phone: '+60 12-345 6789', gameId: 'XM-88', createdAt: now, updatedAt: now },
        u_aj: { username: '阿杰', phone: '+60 19-876 5432', gameId: 'AJ-21', createdAt: now, updatedAt: now }
      },
      events: {
        edemo1: { title: '周六晚 锦标赛（示例）', game: '无限注德州 · 盲注 1/2', place: '俱乐部牌室', startAt: at(8, 20), durationMin: 120, deadline: '', capacity: 8, link: '', description: '这是预览用的示例活动。买入 100，起始筹码 10,000，每 20 分钟升盲。', createdAt: now, updatedAt: now },
        edemo2: { title: '新手教学夜（示例）', game: '无限注德州 · 低盲注', place: '俱乐部牌室', startAt: at(15, 21), durationMin: 90, deadline: '', capacity: 0, link: '', description: '这是预览用的示例活动。', createdAt: now, updatedAt: now },
        edemo3: { title: '上周友谊局（示例）', game: '无限注德州 · 盲注 2/5', place: '俱乐部牌室', startAt: at(-7, 19), durationMin: 120, deadline: '', capacity: 0, link: '', description: '', createdAt: now, updatedAt: now }
      },
      rsvps: {
        edemo1: { u_xm: { status: 'yes', note: '可能晚到十分钟', updatedAt: now }, u_aj: { status: 'maybe', note: '', updatedAt: now } },
        edemo3: { u_xm: { status: 'yes', note: '', updatedAt: now } }
      }
    };
  }
  let mem = null;
  function load() { if (mem) return mem; try { const s = localStorage.getItem(KEY); mem = s ? JSON.parse(s) : seed(); } catch (e) { mem = seed(); } return mem; }
  function save() { try { localStorage.setItem(KEY, JSON.stringify(mem)); } catch (e) { } }
  const err = code => Object.assign(new Error(code), { code });
  const delay = v => new Promise(r => setTimeout(() => r(v), 180));
  let session = null;
  try { session = JSON.parse(localStorage.getItem(SKEY) || sessionStorage.getItem(SKEY) || 'null'); } catch (e) { }
  const authCbs = [], subs = new Set();
  const fire = () => { save(); subs.forEach(f => f()); };
  const sub = f => { subs.add(f); setTimeout(f, 60); return () => subs.delete(f); };
  const setSession = (s, remember) => {
    session = s;
    try { localStorage.removeItem(SKEY); sessionStorage.removeItem(SKEY); if (s) (remember ? localStorage : sessionStorage).setItem(SKEY, JSON.stringify(s)); } catch (e) { }
    authCbs.forEach(cb => cb(s));
  };
  const admin = () => session && load().admins.includes(session.uid);
  const clone = o => JSON.parse(JSON.stringify(o));
  const mailOf = u => 'u' + [...new TextEncoder().encode(u)].map(b => b.toString(16).padStart(2, '0')).join('') + '@txgc.example.com';

  window.__TX_PREVIEW__ = true;
  window.__TX_PREVIEW_RESET__ = () => { try { localStorage.removeItem(KEY); localStorage.removeItem(SKEY); sessionStorage.removeItem(SKEY); } catch (e) { } mem = null; location.hash = 'home'; location.reload(); };
  window.__TX_MOCK_API__ = {
    onAuth(cb) { authCbs.push(cb); setTimeout(() => cb(session), 80); return () => { }; },
    async register({ username, phone, gameId, password }) {
      const d = load(), k = username.toLowerCase();
      await delay();
      if (d.accounts[k]) throw err('auth/email-already-in-use');
      const uid = 'u_' + Math.random().toString(36).slice(2, 10), now = new Date().toISOString();
      d.accounts[k] = { uid, pw: password };
      d.users[uid] = { username, phone, gameId, createdAt: now, updatedAt: now };
      save(); setSession({ uid, email: mailOf(k) }, true); fire();
    },
    async login(username, password, remember) {
      const a = load().accounts[username.trim().toLowerCase()];
      await delay();
      if (!a || a.pw !== password) throw err('auth/invalid-credential');
      setSession({ uid: a.uid, email: mailOf(username.trim().toLowerCase()) }, remember);
    },
    async logout() { setSession(null, false); },
    async changePassword(current, next) {
      const d = load(); await delay();
      const acc = session && Object.values(d.accounts).find(x => x.uid === session.uid);
      if (!acc) throw err('auth/no-current-user');
      if (acc.pw !== current) throw err('auth/invalid-credential');
      acc.pw = next; save();
    },
    isAdmin: async uid => load().admins.includes(uid),
    getUser: async uid => { if (!session || (uid !== session.uid && !admin())) throw err('permission-denied'); const u = load().users[uid]; return u ? clone(u) : null; },
    async saveProfile(uid, data, isNew) {
      if (!session || uid !== session.uid) throw err('permission-denied');
      const d = load(), now = new Date().toISOString();
      d.users[uid] = Object.assign({}, isNew ? { createdAt: now } : d.users[uid], data, { updatedAt: now }); fire();
    },
    getPublic: async uid => { const u = load().users[uid]; return u ? { username: u.username } : null; },
    onEvents: cb => sub(() => cb(Object.entries(clone(load().events)))),
    async saveEvent(id, data) { if (!admin()) throw err('permission-denied'); load().events[id] = clone(data); fire(); },
    async deleteEvent(id) { if (!admin()) throw err('permission-denied'); delete load().events[id]; fire(); },
    onRsvps: (evId, cb) => sub(() => cb(Object.entries(clone(load().rsvps[evId] || {})))),
    async setRsvp(evId, uid, data) { if (!session || uid !== session.uid) throw err('permission-denied'); const r = load().rsvps; (r[evId] = r[evId] || {})[uid] = clone(data); fire(); },
    async deleteRsvp(evId, uid) { if (!session || (uid !== session.uid && !admin())) throw err('permission-denied'); const r = load().rsvps[evId]; if (r) delete r[uid]; fire(); },
    onUsers: (cb, e) => { if (!admin()) { setTimeout(() => e && e(err('permission-denied')), 0); return () => { }; } return sub(() => cb(Object.entries(clone(load().users)))); }
  };
})();
