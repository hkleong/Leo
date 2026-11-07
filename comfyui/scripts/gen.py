#!/usr/bin/env python3
"""MiniMax H3 Ref2VA on the Comfy deployment.
gen.py --prompt-file P --video V --pics a.png b.png [--duration 15] [--aspect "..."] [--seed N] [--dry-run]"""
import argparse, json, mimetypes, os, random, sys, time, uuid, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = "https://dep-f307503a-180f-462c-b702-a0138fdaa503.run.comfy.app"
KEY = os.environ.get("COMFY_API_KEY") or open(os.path.join(HERE, "..", ".comfy_key")).read().strip()


def req(method, path, body=None, headers=None):
    h = {"Authorization": f"Bearer {KEY}"}; h.update(headers or {})
    if isinstance(body, dict):
        body = json.dumps(body).encode(); h["Content-Type"] = "application/json"
    r = urllib.request.Request(BASE + path, data=body, headers=h, method=method)
    try:
        with urllib.request.urlopen(r, timeout=300) as resp: return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        sys.exit(f"HTTP {e.code} {method} {path}: {e.read().decode(errors='replace')[:3000]}")


def upload(path):
    ct = mimetypes.guess_type(path)[0] or "application/octet-stream"; name = os.path.basename(path); b = uuid.uuid4().hex
    parts = [f'--{b}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode() for k, v in (("content_type", ct), ("file_path", name))]
    parts.append(f'--{b}\r\nContent-Disposition: form-data; name="file"; filename="{name}"\r\nContent-Type: {ct}\r\n\r\n'.encode() + open(path, "rb").read() + b"\r\n")
    parts.append(f"--{b}--\r\n".encode())
    a = req("POST", "/api/v2/assets", b"".join(parts), {"Content-Type": f"multipart/form-data; boundary={b}"})
    return {"__type": "core/ASSET", "info": {"id": a["id"], "hash": a.get("hash"), "file_path": name}}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--prompt-file", required=True); p.add_argument("--video", required=True)
    p.add_argument("--pics", nargs="+", required=True)
    p.add_argument("--duration", type=float, default=15); p.add_argument("--aspect")
    p.add_argument("--seed", type=int); p.add_argument("--mp", type=float, default=0.4); p.add_argument("--final", action="store_true"); p.add_argument("--dry-run", action="store_true"); p.add_argument("--no-ref-video", action="store_true"); p.add_argument("--charswap", action="store_true"); p.add_argument("--steps40", action="store_true", help="480p-size but 40 full steps, no turbo LoRA"); p.add_argument("--anchor", help="short clip whose frames are pinned at frame 0 (continuity)")
    a = p.parse_args()
    w = json.load(open(os.path.join(HERE, "template.json")))
    w["138"]["inputs"]["value"] = open(a.prompt_file).read()
    w["132"]["inputs"]["value"] = a.duration
    if a.aspect: w["115"]["inputs"]["aspect_ratio"] = a.aspect
    w["129"]["inputs"]["noise_seed"] = a.seed if a.seed is not None else random.randint(0, 2**48)
    w["115"]["inputs"]["megapixels"] = 0.9 if a.final else a.mp
    w["146"]["inputs"]["value"] = not a.final
    if a.steps40:
        w["146"]["inputs"]["value"] = False; w["143"]["inputs"]["value"] = 40
    if a.charswap:
        w["145"]["inputs"]["lora_name"] = "minimax_h3_fl2v_turbo_8step_v1.0_768p_comfyui_bf16.safetensors"
        w["800"] = {"class_type": "LoraLoaderModelOnly", "inputs": {"model": ["145", 0], "lora_name": "h3_character_swap_v1.5.safetensors", "strength_model": 1.0}}
        w["141"]["inputs"]["on_true"] = ["800", 0]
        w["146"]["inputs"]["value"] = True
        if a.final:   # 720p/40 steps: drop the 8-step turbo, swap LoRA directly on the base model
            w["800"]["inputs"]["model"] = ["127", 0]; w.pop("145"); w["144"]["inputs"]["value"] = 40
        w["123"]["inputs"]["sampler_name"] = "er_sde"
        w["124"]["inputs"]["scheduler"] = "normal"
    n = w["136"]["inputs"]
    if a.no_ref_video:
        n.pop("ref_videos.ref_video_0", None); n.pop("ref_video_audios.ref_video_audio_0", None)
    for k in [k for k in n if k.startswith("ref_images.")]: n.pop(k)
    for nid in ("137", "139", "149"): w.pop(nid, None)
    for i, f in enumerate(a.pics):
        nid = str(700 + i); w[nid] = {"class_type": "LoadImage", "inputs": {"image": "x"}}
        n[f"ref_images.ref_image_{i}"] = [nid, 0]
    print("dur", a.duration, "aspect", w["115"]["inputs"]["aspect_ratio"], "seed", w["129"]["inputs"]["noise_seed"], flush=True)
    if a.dry_run: return
    for i, f in enumerate(a.pics): w[str(700 + i)]["inputs"]["image"] = upload(f)
    import subprocess, tempfile
    v24 = os.path.join(tempfile.mkdtemp(), "ref24.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a.video, "-vf", "fps=24", "-c:v", "libx264", "-crf", "14", "-c:a", "aac", v24], check=True)
    w["147"]["inputs"]["file"] = upload(v24)
    if a.anchor:
        w["810"] = {"class_type": "LoadVideo", "inputs": {"file": upload(a.anchor), "video-preview": ""}}
        w["811"] = {"class_type": "GetVideoComponents", "inputs": {"video": ["810", 0]}}
        w["812"] = {"class_type": "MiniMaxH3AddGuide", "inputs": {"positive": ["136", 0], "latent": ["136", 1], "vae": ["119", 0], "image": ["811", 0], "frame_idx": 0}}
        w["126"]["inputs"]["conditioning"] = ["812", 0]
    jid = req("POST", "/api/v2/jobs", {"workflow": w}, {"Idempotency-Key": str(uuid.uuid4())})["id"]
    print("已提交任务", jid, flush=True)
    last = None
    while True:
        j = req("GET", f"/api/v2/jobs/{jid}"); pr = j.get("progress") or {}
        line = f"{j['status']} {pr.get('value', 0)*100:.0f}% {pr.get('message', '')}"
        if line != last: print(time.strftime("%H:%M:%S"), line, flush=True); last = line
        if j["status"] in ("succeeded", "failed", "canceled"): break
        time.sleep(15)
    if j["status"] != "succeeded": sys.exit(f"任务结束: {j['status']} {json.dumps(j.get('error'), ensure_ascii=False)[:3000]}")
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    for o in j.get("outputs") or []:
        dst = os.path.join(HERE, "out", f"{jid[:8]}_{o['name'].split('/')[-1]}")
        urllib.request.urlretrieve(o["url"], dst); print("已下载", dst)


if __name__ == "__main__":
    main()
