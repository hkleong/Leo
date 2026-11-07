#!/usr/bin/env python3
"""SeedVR2 video upscale on the deployment.
upscale.py --video IN.mp4 --out OUT.mp4 [--res 1080] [--batch 21] [--overlap 4] [--fps 24]"""
import argparse, json, os, sys, time, uuid, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
_a = sys.argv; sys.argv = ["x"]
import gen as g
sys.argv = _a
p = argparse.ArgumentParser()
p.add_argument("--video", required=True); p.add_argument("--out", required=True)
p.add_argument("--res", type=int, default=1080); p.add_argument("--batch", type=int, default=21)
p.add_argument("--overlap", type=int, default=4); p.add_argument("--fps", type=float, default=24)
p.add_argument("--swap", type=int, default=0); p.add_argument("--in-noise", type=float, default=0.0); p.add_argument("--lat-noise", type=float, default=0.0); p.add_argument("--seed", type=int, default=42)
a = p.parse_args()
w = {
 "1": {"class_type": "LoadVideo", "inputs": {"file": g.upload(a.video), "video-preview": ""}},
 "2": {"class_type": "GetVideoComponents", "inputs": {"video": ["1", 0]}},
 "3": {"class_type": "SeedVR2LoadDiTModel", "inputs": {"model": "seedvr2_ema_7b_fp8_e4m3fn_mixed_block35_fp16.safetensors", "device": "cuda:0",
       "blocks_to_swap": a.swap, "swap_io_components": False, "offload_device": "cpu" if a.swap else "none", "cache_model": False, "attention_mode": "sdpa"}},
 "4": {"class_type": "SeedVR2LoadVAEModel", "inputs": {"model": "ema_vae_fp16.safetensors", "device": "cuda:0", "encode_tiled": True, "encode_tile_size": 1024,
       "encode_tile_overlap": 128, "decode_tiled": True, "decode_tile_size": 1024, "decode_tile_overlap": 128, "tile_debug": "false", "offload_device": "cpu", "cache_model": False}},
 "5": {"class_type": "SeedVR2VideoUpscaler", "inputs": {"image": ["2", 0], "dit": ["3", 0], "vae": ["4", 0], "seed": a.seed, "resolution": a.res, "max_resolution": 0,
       "batch_size": a.batch, "uniform_batch_size": False, "temporal_overlap": a.overlap, "prepend_frames": 0, "color_correction": "lab",
       "input_noise_scale": a.in_noise, "latent_noise_scale": a.lat_noise, "offload_device": "cpu", "enable_debug": False}},
 "6": {"class_type": "CreateVideo", "inputs": {"images": ["5", 0], "fps": a.fps, "audio": ["2", 1], "bit_depth": 8, "codec": "none", "color_space": "sRGB"}},
 "7": {"class_type": "SaveVideo", "inputs": {"video": ["6", 0], "filename_prefix": "video/seedvr2", "format": "auto", "codec": "auto", "format.codec": "auto"}},
}
jid = g.req("POST", "/api/v2/jobs", {"workflow": w}, {"Idempotency-Key": str(uuid.uuid4())})["id"]
print("已提交任务", jid, flush=True)
last = None
while True:
    j = g.req("GET", f"/api/v2/jobs/{jid}"); pr = j.get("progress") or {}
    line = f"{j['status']} {pr.get('value', 0)*100:.0f}% {pr.get('message', '')}"
    if line != last: print(time.strftime("%H:%M:%S"), line, flush=True); last = line
    if j["status"] in ("succeeded", "failed", "canceled"): break
    time.sleep(15)
if j["status"] != "succeeded": sys.exit(f"任务结束: {j['status']} {json.dumps(j.get('error'), ensure_ascii=False)[:3000]}")
o = (j.get("outputs") or [])[-1]; urllib.request.urlretrieve(o["url"], a.out); print("已下载", a.out)
