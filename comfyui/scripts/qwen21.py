#!/usr/bin/env python3
"""Local Qwen-Image 2.1 on the deployment (no per-image API fee).
t2i:  qwen21.py --prompt-file P --out PREFIX [--w 1024 --h 1536] [--n 2] [--seed S] [--full]
edit: qwen21.py --prompt-file P --out PREFIX --images a.png [b.png ...]
Default uses the 8-step LoRA (fast); --full = 25 steps without LoRA."""
import argparse, json, os, random, sys, time, uuid, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
_argv = sys.argv; sys.argv = ["x"]
import gen as g
sys.argv = _argv

p = argparse.ArgumentParser()
p.add_argument("--prompt-file", required=True); p.add_argument("--out", required=True)
p.add_argument("--negative", default="")
p.add_argument("--images", nargs="*", default=[])
p.add_argument("--w", type=int, default=1024); p.add_argument("--h", type=int, default=1536)
p.add_argument("--n", type=int, default=1); p.add_argument("--seed", type=int)
p.add_argument("--full", action="store_true")
a = p.parse_args()
seed = a.seed if a.seed is not None else random.randint(0, 2**48)
w = {
    "1": {"class_type": "UNETLoader", "inputs": {"unet_name": "qwen_image_2.1_int8_convrot.safetensors", "weight_dtype": "default"}},
    "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen3vl_8b_int8_convrot.safetensors", "type": "qwen_image", "device": "default"}},
    "3": {"class_type": "VAELoader", "inputs": {"vae_name": "qwen_image_2.1_vae_bf16.safetensors"}},
    "4": {"class_type": "QwenImage21Cache", "inputs": {"model": ["1", 0], "device": "auto", "dtype": "default"}},
    "6": {"class_type": "TextEncodeQwenImage21", "inputs": {"clip": ["2", 0], "vae": ["3", 0], "prompt": open(a.prompt_file).read(),
                                                          "negative_prompt": a.negative, "resolution": 1024}},
    "9": {"class_type": "VAEDecode", "inputs": {"samples": ["8", 0], "vae": ["3", 0]}},
    "10": {"class_type": "SaveImage", "inputs": {"images": ["9", 0], "filename_prefix": "qwen21"}},
}
model = ["4", 0]
if not a.full:
    w["5"] = {"class_type": "LoraLoaderModelOnly", "inputs": {"model": ["4", 0], "lora_name": "p_q_image_2.1_8_steps_v0.1_comfyui_bf16.safetensors", "strength_model": 1}}
    model = ["5", 0]
for i, f in enumerate(a.images):
    w[str(20 + i)] = {"class_type": "LoadImage", "inputs": {"image": g.upload(f)}}
    w["6"]["inputs"][f"images.image_{i+1}"] = [str(20 + i), 0]
if a.images:
    latent = ["6", 2]
else:
    w["7"] = {"class_type": "EmptyLatentImage", "inputs": {"width": a.w, "height": a.h, "batch_size": a.n}}
    latent = ["7", 0]
w["8"] = {"class_type": "KSampler", "inputs": {"model": model, "positive": ["6", 0], "negative": ["6", 1], "latent_image": latent,
                                              "seed": seed, "steps": 25 if a.full else 8, "cfg": 1, "sampler_name": "euler",
                                              "scheduler": "simple", "denoise": 1}}
jid = g.req("POST", "/api/v2/jobs", {"workflow": w}, {"Idempotency-Key": str(uuid.uuid4())})["id"]
print("已提交", jid, "seed", seed, flush=True)
t0 = time.time()
while True:
    j = g.req("GET", f"/api/v2/jobs/{jid}")
    if j["status"] in ("succeeded", "failed", "canceled"): break
    time.sleep(5)
if j["status"] != "succeeded":
    sys.exit(f"{j['status']} {json.dumps(j.get('error'), ensure_ascii=False)[:2500]}")
for i, o in enumerate(j.get("outputs") or []):
    dst = f"{a.out}_{i}.png"; urllib.request.urlretrieve(o["url"], dst); print("已下载", dst)
print(f"用时 {time.time()-t0:.0f}s")
