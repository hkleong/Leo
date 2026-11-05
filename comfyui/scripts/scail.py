#!/usr/bin/env python3
"""SCAIL-2 character replacement (single segment, <=153 frames) built from the user's saved workflow.
scail.py --video V --ref IMG --frames N --drive-text woman --ref-text man --prompt "..." [--w 544 --h 960] [--seed S] [--no-distill]"""
import argparse, json, os, random, sys, time, uuid, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen as g

HERE = os.path.dirname(os.path.abspath(__file__))
p = argparse.ArgumentParser()
p.add_argument("--video", required=True); p.add_argument("--ref", required=True)
p.add_argument("--frames", type=int, required=True)
p.add_argument("--drive-text", default="woman"); p.add_argument("--ref-text", default="man")
p.add_argument("--prompt", required=True); p.add_argument("--w", type=int, default=544); p.add_argument("--h", type=int, default=960)
p.add_argument("--seed", type=int); p.add_argument("--objects", default=""); p.add_argument("--no-distill", action="store_true"); p.add_argument("--tag", default="scail")
a = p.parse_args()
n = a.frames - (a.frames - 1) % 4  # Wan wants 4k+1

src = json.load(open(os.path.join(HERE, "scail_57ecc63a.json")))
w = {k: v for k, v in src.items() if k.startswith("213:") or k in ("30", "155", "201", "202", "215")}
for v in w.values(): v.pop("_meta", None)
w["213:177"]["inputs"].update({"batch_index": 0, "length": n})
w["213:178"]["inputs"]["value"] = a.w; w["213:179"]["inputs"]["value"] = a.h
w["213:191"]["inputs"]["text"] = a.drive_text; w["213:212"]["inputs"]["text"] = a.ref_text
w["213:3"]["inputs"]["text"] = a.prompt
w["213:197"]["inputs"]["object_indices"] = a.objects
w["213:172"]["inputs"]["value"] = not a.no_distill
seed = a.seed if a.seed is not None else random.randint(0, 2**48)
w["213:19"]["inputs"]["noise_seed"] = seed
w["202"]["inputs"]["filename_prefix"] = f"video/{a.tag}"
w["30"]["inputs"]["image"] = g.upload(a.ref)
w["155"]["inputs"]["file"] = g.upload(a.video)
print("frames", n, "seed", seed, flush=True)
jid = g.req("POST", "/api/v2/jobs", {"workflow": w}, {"Idempotency-Key": str(uuid.uuid4())})["id"]
print("已提交任务", jid, flush=True)
last = None
while True:
    j = g.req("GET", f"/api/v2/jobs/{jid}"); pr = j.get("progress") or {}
    line = f"{j['status']} {pr.get('value', 0)*100:.0f}% {pr.get('message', '')}"
    if line != last: print(time.strftime("%H:%M:%S"), line, flush=True); last = line
    if j["status"] in ("succeeded", "failed", "canceled"): break
    time.sleep(15)
if j["status"] != "succeeded":
    sys.exit(f"任务结束: {j['status']} {json.dumps(j.get('error'), ensure_ascii=False)[:3000]}")
os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
for o in j.get("outputs") or []:
    dst = os.path.join(HERE, "out", f"{jid[:8]}_{a.tag}.mp4")
    urllib.request.urlretrieve(o["url"], dst); print("已下载", dst)
