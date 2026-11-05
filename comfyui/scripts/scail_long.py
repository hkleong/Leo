#!/usr/bin/env python3
"""SCAIL-2 long video: splits a 30fps driving clip into 153-frame segments with 5-frame overlap,
runs them sequentially (each conditioned on the previous output), then concatenates.
Preset test = 480p + distill LoRA (6 steps); final = 720p, 40 steps (--final).
scail_long.py --video V --ref IMG --prompt P --out OUT.mp4 [--drive-text man --ref-text man] [--final] [--seed S]"""
import argparse, json, os, random, subprocess, sys, time, uuid, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen as g

HERE = os.path.dirname(os.path.abspath(__file__))
SEG, OV = 153, 5
p = argparse.ArgumentParser()
p.add_argument("--video", required=True); p.add_argument("--ref", required=True)
p.add_argument("--prompt", required=True); p.add_argument("--out", required=True)
p.add_argument("--drive-text", default="man"); p.add_argument("--ref-text", default="man")
p.add_argument("--objects", default=""); p.add_argument("--final", action="store_true")
p.add_argument("--w", type=int); p.add_argument("--h", type=int); p.add_argument("--seed", type=int)
a = p.parse_args()
portrait = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "stream=width,height", "-of", "json", a.video]))["streams"][0]
land = portrait["width"] >= portrait["height"]
if a.final: W, H = (1280, 720) if land else (720, 1280)
else: W, H = (832, 480) if land else (480, 832)
W, H = a.w or W, a.h or H
seed = a.seed if a.seed is not None else random.randint(0, 2**48)
work = os.path.splitext(a.out)[0] + "_segs"; os.makedirs(work, exist_ok=True)

src = os.path.join(work, "src30.mp4")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a.video, "-vf", "fps=30", "-c:v", "libx264", "-crf", "14", "-c:a", "aac", src], check=True)
N = int(subprocess.check_output(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v", "-show_entries", "stream=nb_read_frames", "-of", "csv=p=0", src]).strip())
starts = []; s = 0
while True:
    starts.append(s)
    if s + SEG >= N: break
    s += SEG - OV
print(f"{N} frames -> {len(starts)} segments, {W}x{H}, {'final 40 steps' if a.final else 'test LoRA 6 steps'}, seed {seed}", flush=True)

base = json.load(open(os.path.join(HERE, "scail_57ecc63a.json")))
ref_asset = g.upload(a.ref)
prev = None; outs = []
for k, st in enumerate(starts):
    n = min(SEG, N - st); n -= (n - 1) % 4
    chunk = os.path.join(work, f"chunk{k}.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-vf", f"select='between(n,{st},{st+n-1})',setpts=N/30/TB",
                    "-af", f"atrim={st/30}:{(st+n)/30},asetpts=PTS-STARTPTS", "-c:v", "libx264", "-crf", "14", "-c:a", "aac", chunk], check=True)
    w = {kk: json.loads(json.dumps(v)) for kk, v in base.items() if kk.startswith("213:") or kk in ("30", "155", "201", "202", "215")}
    for v in w.values(): v.pop("_meta", None)
    w["213:177"]["inputs"].update({"batch_index": 0, "length": n})
    w["213:178"]["inputs"]["value"] = W; w["213:179"]["inputs"]["value"] = H
    w["213:191"]["inputs"]["text"] = a.drive_text; w["213:212"]["inputs"]["text"] = a.ref_text
    w["213:197"]["inputs"]["object_indices"] = a.objects
    w["213:3"]["inputs"]["text"] = a.prompt
    w["213:172"]["inputs"]["value"] = not a.final
    w["213:19"]["inputs"]["noise_seed"] = seed
    w["30"]["inputs"]["image"] = ref_asset
    w["155"]["inputs"]["file"] = g.upload(chunk)
    if prev:
        w["500"] = {"class_type": "LoadVideo", "inputs": {"file": g.upload(prev), "video-preview": ""}}
        w["501"] = {"class_type": "GetVideoComponents", "inputs": {"video": ["500", 0]}}
        w["213:114"]["inputs"]["previous_frames"] = ["501", 0]
    jid = g.req("POST", "/api/v2/jobs", {"workflow": w}, {"Idempotency-Key": str(uuid.uuid4())})["id"]
    print(f"seg {k+1}/{len(starts)} frames {st}-{st+n-1} 已提交 {jid}", flush=True)
    last = None
    while True:
        j = g.req("GET", f"/api/v2/jobs/{jid}"); pr = j.get("progress") or {}
        line = f"seg {k+1} {j['status']} {pr.get('value', 0)*100:.0f}% {pr.get('message', '')}"
        if line != last: print(time.strftime("%H:%M:%S"), line, flush=True); last = line
        if j["status"] in ("succeeded", "failed", "canceled"): break
        time.sleep(15)
    if j["status"] != "succeeded":
        sys.exit(f"seg {k+1} 失败: {json.dumps(j.get('error'), ensure_ascii=False)[:3000]}")
    seg_out = os.path.join(work, f"seg{k}.mp4")
    urllib.request.urlretrieve(j["outputs"][0]["url"], seg_out); outs.append(seg_out); prev = seg_out

# concat: drop first OV frames of every segment after the first; audio from source
parts = []; fc = []
for i, f in enumerate(outs):
    parts += ["-i", f]
    fc.append(f"[{i}:v]fps=30,scale={W}:{H},setsar=1{',trim=start_frame=%d,setpts=PTS-STARTPTS' % OV if i else ''}[v{i}]")
fc.append("".join(f"[v{i}]" for i in range(len(outs))) + f"concat=n={len(outs)}:v=1:a=0[v]")
subprocess.run(["ffmpeg", "-v", "error", "-y", *parts, "-i", src, "-filter_complex", ";".join(fc), "-map", "[v]", "-map", f"{len(outs)}:a?",
                "-shortest", "-c:v", "libx264", "-crf", "17", "-c:a", "aac", a.out], check=True)
print("完成", a.out, flush=True)
