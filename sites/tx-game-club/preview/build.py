# Builds preview/index.html (a single-file Claude Artifact) from the standalone site + the local mock data layer.
import re, pathlib
root = pathlib.Path(__file__).resolve().parent.parent
html = (root / 'index.html').read_text(encoding='utf8')
app = (root / 'app.js').read_text(encoding='utf8')
mock = (root / 'preview' / 'mock-api.js').read_text(encoding='utf8')
css = html[html.index('<style>') + 7: html.index('</style>')]
body = html[html.index('<body>') + 6: html.index('</body>')]
body = body.replace('<script type="module" src="app.js"></script>', '')
app = app.replace("import { firebaseConfig } from './firebase-config.js';", "const firebaseConfig = {};")
assert "import " not in app.split('\n')[1]
extra_css = '''
/* preview badge */
.pv{position:fixed;z-index:30;left:max(12px,env(safe-area-inset-left,0px));bottom:calc(env(safe-area-inset-bottom,0px) + 12px);max-width:calc(100% - 24px);
  display:flex;align-items:center;flex-wrap:wrap;gap:6px 10px;padding:8px 10px 8px 12px;border-radius:12px;background:#1c1c1f;border:1px solid var(--accent);font-size:12px;color:var(--muted);box-shadow:0 8px 24px rgba(0,0,0,.5)}
.pv b{color:var(--accent-hot);letter-spacing:.1em}
.pv button{border:1px solid var(--line);background:transparent;border-radius:8px;padding:2px 8px;font-size:12px;color:var(--ink)}
.pv.min span,.pv.min #pvReset{display:none}
.toast{bottom:calc(env(safe-area-inset-bottom,0px) + 78px)}
'''
badge = '''<div class="pv" id="pv" role="note"><b>预览模式</b><span>数据只存在你的浏览器里，别人看不到 · 测试账号：admin / 123456（管理员）、小明 / 123456</span><button type="button" id="pvReset">重置预览数据</button><button type="button" id="pvMin" aria-label="收起提示">–</button></div>
<script>
document.getElementById('pvReset').onclick = () => window.__TX_PREVIEW_RESET__ && window.__TX_PREVIEW_RESET__();
document.getElementById('pvMin').onclick = e => { const p = document.getElementById('pv'); p.classList.toggle('min'); e.currentTarget.textContent = p.classList.contains('min') ? '+' : '–'; };
</script>'''
out = ('<title>TX Game Club 预览</title>\n<meta name="claude:viewport-fit-sides" content="cover">\n'
       '<link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
       '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Anton&family=Saira+Condensed:wght@500;700;800&family=ZCOOL+QingKe+HuangYou&display=swap">\n'
       '<style>' + css + extra_css + '</style>\n' + body + badge +
       '\n<script>\n' + mock + '\n</script>\n<script type="module">\n' + app + '\n</script>\n')
(root / 'preview' / 'index.html').write_text(out, encoding='utf8')
print('built', len(out))
