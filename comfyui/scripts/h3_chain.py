#!/usr/bin/env python3
"""Seamless long H3 edit: convert source to 24fps, split into 124-frame pieces, generate them in order,
pinning the first 5 frames of each piece to the previous piece's output at the same moment (MiniMaxH3AddGuide),
then splice at native speed with the source audio.
h3_chain.py --video SRC --prompt-file P --pics a.png b.png --out OUT.mp4 [--charswap] [--aspect "16:9 (Widescreen)"] [--final]"""
import argparse, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
SEG, A = 124, 5
p = argparse.ArgumentParser()
p.add_argument("--video", required=True); p.add_argument("--prompt-file", required=True)
p.add_argument("--pics", nargs="+", required=True); p.add_argument("--out", required=True)
p.add_argument("--charswap", action="store_true"); p.add_argument("--aspect", default="16:9 (Widescreen)")
p.add_argument("--final", action="store_true"); p.add_argument("--deflicker", action="store_true"); p.add_argument("--done", nargs="*", default=[], help="already generated piece outputs (resume)"); p.add_argument("--prompt-last", help="prompt file for the last piece"); p.add_argument("--seed", type=int)
a = p.parse_args()
work = os.path.splitext(a.out)[0] + "_chain"; os.makedirs(work, exist_ok=True)
run = lambda *c: subprocess.run(list(c), check=True)
src = os.path.join(work, "src24.mp4")
run("ffmpeg", "-v", "error", "-y", "-i", a.video, "-vf", "fps=24", "-c:v", "libx264", "-crf", "14", "-c:a", "aac", src)
N = int(subprocess.check_output(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v", "-show_entries", "stream=nb_read_frames", "-of", "csv=p=0", src]).strip())
starts = [0]
while starts[-1] + SEG < N:
    starts.append(min(starts[-1] + SEG - A, N - SEG))
print(f"{N} frames @24fps -> pieces at {starts}", flush=True)
outs = []
for k, s in enumerate(starts):
    if k < len(a.done):
        outs.append(a.done[k]); print(f"piece {k+1} reused {a.done[k]}", flush=True); continue
    piece = os.path.join(work, f"src{k}.mp4")
    run("ffmpeg", "-v", "error", "-y", "-i", src, "-vf", f"select='between(n,{s},{s+SEG-1})',setpts=N/24/TB",
        "-af", f"atrim={s/24}:{(s+SEG)/24},asetpts=PTS-STARTPTS", "-c:v", "libx264", "-crf", "14", "-c:a", "aac", piece)
    cmd = [sys.executable, "-u", os.path.join(HERE, "gen.py"), "--prompt-file", (a.prompt_last if a.prompt_last and k == len(starts) - 1 else a.prompt_file), "--video", piece,
           "--pics", *a.pics, "--duration", str(SEG / 24), "--aspect", a.aspect]
    if a.charswap: cmd.append("--charswap")
    if a.final: cmd.append("--final")
    if a.seed is not None: cmd += ["--seed", str(a.seed)]
    if k:
        off = s - starts[k - 1]                     # where this piece's start sits inside the previous output
        anc = os.path.join(work, f"anchor{k}.mp4")
        run("ffmpeg", "-v", "error", "-y", "-i", outs[-1], "-vf", f"fps=24,select='between(n,{off},{off+A-1})',setpts=N/24/TB",
            "-an", "-c:v", "libx264", "-crf", "12", anc)
        cmd += ["--anchor", anc]
    print(f"piece {k+1}/{len(starts)} frames {s}-{s+SEG-1}", flush=True)
    res = subprocess.run(cmd, capture_output=True, text=True); print(res.stdout[-600:], res.stderr[-600:], flush=True)
    got = [l.split(" ", 1)[1] for l in res.stdout.splitlines() if l.startswith("已下载")]
    if not got: sys.exit(f"piece {k+1} failed")
    outs.append(got[-1])
# splice: cut each seam right after the pinned anchor frames of the next piece (continuity is guaranteed there)
cuts = [0] + [st + A for st in starts[1:]] + [N]
parts, fc = [], []
for k, (s, f) in enumerate(zip(starts, outs)):
    a0 = cuts[k] - s; b0 = min(cuts[k + 1] - s, SEG)
    parts += ["-i", f]
    fc.append(f"[{k}:v]fps=24,setsar=1,trim=start_frame={a0}:end_frame={b0},setpts=PTS-STARTPTS[v{k}]")
W, H = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "stream=width,height", "-of", "csv=p=0", outs[0]]).decode().strip().split(",")
fc = [f.replace("setsar=1", f"scale={W}:{H},setsar=1") for f in fc]
fc.append("".join(f"[v{k}]" for k in range(len(outs))) + f"concat=n={len(outs)}:v=1:a=0" + (",deflicker=mode=pm:size=5" if a.deflicker else "") + "[v]")
run("ffmpeg", "-v", "error", "-y", *parts, "-i", src, "-filter_complex", ";".join(fc), "-map", "[v]", "-map", f"{len(outs)}:a?",
    "-shortest", "-c:v", "libx264", "-crf", "17", "-c:a", "aac", a.out)
print("完成", a.out, flush=True)
