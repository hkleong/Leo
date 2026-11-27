"""Build the home-screen web app into a folder ready for static hosting (e.g. GitHub Pages).

    python3 casino/build_app.py <output-dir>      # default: casino/dist

index.html is authored without <!doctype>/<html> (the Claude artifact viewer adds those),
so this wraps it into a standards-mode document and copies the manifest, service worker and icons.
"""
import os, shutil, sys, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
out = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "dist"))
os.makedirs(os.path.join(out, "icons"), exist_ok=True)

src = open(os.path.join(HERE, "index.html"), encoding="utf-8").read()
open(os.path.join(out, "index.html"), "w", encoding="utf-8").write('<!doctype html>\n<html lang="zh-CN">\n' + src.rstrip() + "\n</html>\n")

# version the service-worker cache by content so every rebuild updates installed apps
ver = hashlib.sha1(src.encode("utf-8")).hexdigest()[:10]
sw = open(os.path.join(HERE, "sw.js"), encoding="utf-8").read().replace('const VERSION = "gbc-v1";', 'const VERSION = "gbc-' + ver + '";')
open(os.path.join(out, "sw.js"), "w", encoding="utf-8").write(sw)

shutil.copy(os.path.join(HERE, "manifest.webmanifest"), out)
for f in os.listdir(os.path.join(HERE, "icons")):
    shutil.copy(os.path.join(HERE, "icons", f), os.path.join(out, "icons", f))
# illustrations (machine art); copied as a whole folder
if os.path.isdir(os.path.join(HERE, "art")):
    shutil.copytree(os.path.join(HERE, "art"), os.path.join(out, "art"), dirs_exist_ok=True)
os.makedirs(os.path.join(out, "music"), exist_ok=True)
for f in os.listdir(os.path.join(HERE, "music")):
    shutil.copy(os.path.join(HERE, "music", f), os.path.join(out, "music", f))
print("built", out, "cache", ver)
