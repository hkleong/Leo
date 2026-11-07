import subprocess, sys, os, json, time, re
from concurrent.futures import ThreadPoolExecutor
os.chdir(os.path.dirname(os.path.abspath(__file__))); os.makedirs('logs2', exist_ok=True); os.makedirs('raw2', exist_ok=True)
J = json.load(open('jobs2.json'))
only = sys.argv[1:]
if only: J = [j for j in J if j['id'] in only]
import urllib.request
BASE = "https://dep-f307503a-180f-462c-b702-a0138fdaa503.run.comfy.app"
KEY = open('../../../.comfy_key').read().strip()
def api(p):
    r = urllib.request.Request(BASE + p, headers={"Authorization": f"Bearer {KEY}"})
    with urllib.request.urlopen(r, timeout=120) as x: return json.loads(x.read())
def adopt(k, log):
    # 上一个 runner 被杀时留下的远端任务：继续等它，不重复提交
    if not os.path.exists(log): return False
    txt = open(log).read()
    m = re.search(r'已提交任务 (\S+)', txt)
    if not m or '已下载' in txt or '任务结束' in txt: return False
    jid = m.group(1)
    while True:
        try: j = api(f'/api/v2/jobs/{jid}')
        except Exception as e: time.sleep(30); continue
        if j['status'] in ('succeeded', 'failed', 'canceled'): break
        time.sleep(20)
    if j['status'] != 'succeeded': return False
    for o in j.get('outputs') or []:
        if o['name'].endswith('.mp4'):
            urllib.request.urlretrieve(o['url'], f'raw2/{k}.mp4')
            open(log, 'a').write(f'\n已下载(接管) {jid}\n'); return True
    return False
def run(j):
    k = j['id']; log = f'logs2/{k}.log'
    if os.path.exists(f'raw2/{k}.mp4'): return
    if adopt(k, log): print(k, 'adopted', time.strftime('%H:%M'), flush=True); return
    for t in range(40):
        with open(log, 'w') as f:
            subprocess.run([sys.executable, '-u', '../../../p2/gen.py', '--no-ref-video', '--steps40', '--prompt-file', f'prompts2/{k}.txt',
                            '--video', '../../../p7/seg1.mp4', '--pics', *j['pics'], '--duration', str(j['dur']), '--aspect', '16:9 (Widescreen)'],
                           stdout=f, stderr=subprocess.STDOUT)
        txt = open(log).read()
        m = re.search(r'已下载 (\S+\.mp4)', txt)
        if m:
            src = m.group(1); src = src if os.path.isabs(src) else os.path.join('../../../p2', src)
            os.replace(src, f'raw2/{k}.mp4'); break
        if re.search(r'HTTP (402|403|429|5\d\d)|quota|credit|limit|insufficient|balance|timed out|Connection', txt, re.I):
            print(k, '额度/网络问题，10分钟后重试', time.strftime('%H:%M'), flush=True); time.sleep(600); continue
        break
    print(k, 'done' if os.path.exists(f'raw2/{k}.mp4') else 'FAILED', time.strftime('%H:%M'), flush=True)
with ThreadPoolExecutor(3) as ex: list(ex.map(run, J))
