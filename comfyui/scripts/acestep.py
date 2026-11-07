#!/usr/bin/env python3
"""ACE-Step v1 music on the deployment. acestep.py --tags "..." --lyrics "[inst]" --sec 56 --out out.flac [--seed N] [--steps 50]"""
import argparse, json, os, random, sys, time, uuid, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
_a = sys.argv; sys.argv = ["x"]
import gen as g
sys.argv = _a
p = argparse.ArgumentParser(); p.add_argument("--tags", required=True); p.add_argument("--lyrics", default="[inst]")
p.add_argument("--sec", type=float, default=56); p.add_argument("--out", required=True); p.add_argument("--seed", type=int); p.add_argument("--steps", type=int, default=50)
a = p.parse_args(); seed = a.seed if a.seed is not None else random.randint(0, 2**48)
w = {
 "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "ace_step_v1_3.5b.safetensors"}},
 "2": {"class_type": "TextEncodeAceStepAudio", "inputs": {"clip": ["1", 1], "tags": a.tags, "lyrics": a.lyrics, "lyrics_strength": 0.99}},
 "3": {"class_type": "ConditioningZeroOut", "inputs": {"conditioning": ["2", 0]}},
 "4": {"class_type": "EmptyAceStepLatentAudio", "inputs": {"seconds": a.sec, "batch_size": 1}},
 "5": {"class_type": "ModelSamplingSD3", "inputs": {"model": ["1", 0], "shift": 5.0}},
 "6": {"class_type": "KSampler", "inputs": {"model": ["5", 0], "positive": ["2", 0], "negative": ["3", 0], "latent_image": ["4", 0], "seed": seed, "steps": a.steps, "cfg": 5, "sampler_name": "euler", "scheduler": "simple", "denoise": 1}},
 "7": {"class_type": "VAEDecodeAudio", "inputs": {"samples": ["6", 0], "vae": ["1", 2]}},
 "8": {"class_type": "SaveAudio", "inputs": {"audio": ["7", 0], "filename_prefix": "audio/acestep"}},
}
jid = g.req("POST", "/api/v2/jobs", {"workflow": w}, {"Idempotency-Key": str(uuid.uuid4())})["id"]
print("已提交", jid, "seed", seed, flush=True)
while True:
    j = g.req("GET", f"/api/v2/jobs/{jid}")
    if j["status"] in ("succeeded", "failed", "canceled"): break
    time.sleep(10)
if j["status"] != "succeeded": sys.exit(f"{j['status']} {json.dumps(j.get('error'), ensure_ascii=False)[:2500]}")
o = (j.get("outputs") or [])[-1]; urllib.request.urlretrieve(o["url"], a.out); print("已下载", a.out)
