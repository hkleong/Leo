#!/usr/bin/env python3
"""SCAIL-2 + MaskVidExperiments: SAM3 track the subject -> MVEx Subject Crop (tracked, upscaled)
-> SCAIL-2 replace on the crop -> MVEx Subject Uncrop back into the full frame.
One job per segment (<=153 frames @30fps). Test preset = distill LoRA 6 steps, crop ~0.4 MP; --final = 40 steps, ~0.9 MP.
scail_crop.py --video SEG.mp4 --ref IMG --prompt P --out OUT.mp4 [--subject man] [--crop-scale 1.6] [--final]"""
import argparse, json, os, random, subprocess, sys, time, uuid, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
_a = sys.argv; sys.argv = ["x"]
import gen as g
sys.argv = _a
HERE = os.path.dirname(os.path.abspath(__file__))

p = argparse.ArgumentParser()
p.add_argument("--video", required=True); p.add_argument("--ref", required=True)
p.add_argument("--prompt", required=True); p.add_argument("--out", required=True)
p.add_argument("--subject", default="man"); p.add_argument("--ref-text", default="man")
p.add_argument("--crop-scale", type=float, default=1.6); p.add_argument("--final", action="store_true")
p.add_argument("--seed", type=int); p.add_argument("--debug", action="store_true"); p.add_argument("--max-frames", type=int, default=153); p.add_argument("--objects", default="")
a = p.parse_args()

src = a.out + ".src30.mp4"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a.video, "-vf", "fps=30", "-c:v", "libx264", "-crf", "14", "-c:a", "aac", src], check=True)
N = int(subprocess.check_output(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v", "-show_entries", "stream=nb_read_frames", "-of", "csv=p=0", src]).strip())
n = min(N, a.max_frames); n -= (n - 1) % 4
seed = a.seed if a.seed is not None else random.randint(0, 2**48)
mp = 0.9 if a.final else 0.4

base = json.load(open(os.path.join(HERE, "scail_57ecc63a.json")))
w = {k: json.loads(json.dumps(v)) for k, v in base.items() if k.startswith("213:") or k in ("30", "155", "215")}
for v in w.values(): v.pop("_meta", None)
# full source frames
w["213:177"]["inputs"].update({"batch_index": 0, "length": n})          # ImageFromBatch on source
# SAM3 track of the subject on the full frames -> mask
w["600"] = {"class_type": "CLIPTextEncode", "inputs": {"clip": ["213:193", 1], "text": a.subject}}
w["601"] = {"class_type": "SAM3_VideoTrack", "inputs": {"images": ["213:177", 0], "model": ["213:193", 0], "conditioning": ["600", 0],
                                                       "detection_threshold": 0.5, "max_objects": 1, "detect_interval": 1}}
w["602"] = {"class_type": "SAM3_TrackToMask", "inputs": {"track_data": ["601", 0], "object_indices": ""}}
w["603"] = {"class_type": "MVEx_MaskCleanup", "inputs": {"masks": ["602", 0], "threshold": 0.5, "method": "components",
                                                        "method.min_pixels": 32, "method.min_frames": 2, "edge_grow": 0}}
w["604"] = {"class_type": "MVEx_SubjectCrop", "inputs": {"original_images": ["213:177", 0], "masks": ["603", 0], "mode": "tracked",
                                                        "mode.crop_scale": a.crop_scale, "mode.padding": "firm", "mode.prefer": "stillness",
                                                        "mode.aspect_ratio": 0.0, "mode.seamless_loop": False,
                                                        "divisible_by": 32, "upscale_megapixels": mp, "resize_method": "auto"}}
# SCAIL now runs on the crop: crop becomes the pose video; size from the crop itself
w["213:163"]["inputs"]["image"] = ["604", 0]                              # GetImageSize -> crop dims
w["213:196"]["inputs"]["images"] = ["604", 0]                             # driving track on the crop
w["213:114"]["inputs"]["pose_video"] = ["604", 0]
w["213:197"]["inputs"]["object_indices"] = a.objects
w["213:191"]["inputs"]["text"] = a.subject; w["213:212"]["inputs"]["text"] = a.ref_text
w["213:3"]["inputs"]["text"] = a.prompt
w["213:172"]["inputs"]["value"] = not a.final
w["213:19"]["inputs"]["noise_seed"] = seed
for k in ("213:156", "213:178", "213:179", "213:180", "213:182"): w.pop(k, None)
# paste back
w["605"] = {"class_type": "MVEx_SubjectUncrop", "inputs": {"cropped_images": ["213:6", 0], "original_images": ["213:177", 0],
                                                          "bboxes": ["604", 2], "cropped_masks": ["604", 1], "feather": 16, "resize_method": "auto"}}
w["606"] = {"class_type": "CreateVideo", "inputs": {"images": ["605", 0], "fps": 30, "audio": ["215", 1],
                                                   "bit_depth": 8, "codec": "none", "color_space": "sRGB"}}
w["607"] = {"class_type": "SaveVideo", "inputs": {"video": ["606", 0], "filename_prefix": "video/scail_crop", "format": "auto",
                                                 "codec": "auto", "format.codec": "auto"}}
w["608"] = {"class_type": "PreviewAny", "inputs": {"source": ["604", 3]}}
if a.debug:
    w["700"] = {"class_type": "CreateVideo", "inputs": {"images": ["604", 0], "fps": 30, "bit_depth": 8, "codec": "none", "color_space": "sRGB"}}
    w["701"] = {"class_type": "SaveVideo", "inputs": {"video": ["700", 0], "filename_prefix": "video/dbg_crop", "format": "auto", "codec": "auto", "format.codec": "auto"}}
    w["702"] = {"class_type": "CreateVideo", "inputs": {"images": ["213:6", 0], "fps": 30, "bit_depth": 8, "codec": "none", "color_space": "sRGB"}}
    w["703"] = {"class_type": "SaveVideo", "inputs": {"video": ["702", 0], "filename_prefix": "video/dbg_scail", "format": "auto", "codec": "auto", "format.codec": "auto"}}
    w["704"] = {"class_type": "MaskToImage", "inputs": {"mask": ["213:197", 0]}} if False else None
    w.pop("704")
w["30"]["inputs"]["image"] = g.upload(a.ref)
w["155"]["inputs"]["file"] = g.upload(src)
print(f"frames {n}/{N} seed {seed} crop_mp {mp}", flush=True)
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
outs = j.get("outputs") or []
for o in outs: print("output", o["name"], o.get("node_id"))
main = [o for o in outs if "scail_crop" in o["name"]] or outs
urllib.request.urlretrieve(main[-1]["url"], a.out); print("已下载", a.out)
for o in outs:
    if "dbg_" in o["name"]:
        dst = a.out.replace(".mp4", "_" + o["name"].split("/")[-1]); urllib.request.urlretrieve(o["url"], dst); print("debug", dst)
try:
    lg = g.req("GET", f"/api/v2/jobs/{jid}/logs")
    print(json.dumps(lg, ensure_ascii=False)[:200])
except SystemExit: pass
