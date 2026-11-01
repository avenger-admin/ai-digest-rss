#!/usr/bin/env python3
"""Box-side hero still for the morning paper.

Why: GenerateImage writes to the agent host's asset store, which the box
Shell cannot see (box copy of /home/box/agent-data was frozen at the
17 Oct 21:31 migration). So we make the hero on the box itself.

Usage:
  python3 make_hero.py --date YYYY-MM-DD --prompt "..." [--repo /workspace/ai-digest-rss]
Order of attempts:
  1. --from PATH (e.g. the GenerateImage path) if Shell can see it
  2. OpenRouter image model (OPENROUTER_API_KEY, never printed)
  3. Local PIL typographic card (free, always works)
Writes media/YYYY-MM-DD.jpg (1280x640) and prints its repo-relative path.
"""
import argparse, base64, io, json, os, sys, time, urllib.request
from PIL import Image, ImageDraw, ImageFont, ImageFilter

MODELS = ["google/gemini-2.5-flash-image", "google/gemini-3.1-flash-lite-image"]

def fit(img):
    img = img.convert("RGB"); W, H = 1280, 640
    s = max(W / img.width, H / img.height)
    img = img.resize((int(img.width * s + .5), int(img.height * s + .5)), Image.LANCZOS)
    l, t = (img.width - W) // 2, (img.height - H) // 2
    return img.crop((l, t, l + W, t + H))

def from_path(p, wait):
    p = p.removeprefix("file://")
    for _ in range(max(1, wait)):
        if os.path.isfile(p) and os.path.getsize(p) > 0:
            return Image.open(p)
        time.sleep(1)
    return None

def openrouter(prompt):
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key: return None
    for model in MODELS:
        body = json.dumps({"model": model, "modalities": ["image", "text"],
            "messages": [{"role": "user", "content": "Generate one wide 2:1 editorial illustration, no text or logos. " + prompt}]}).encode()
        req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", body,
            {"Authorization": "Bearer " + key, "Content-Type": "application/json"})
        try:
            d = json.load(urllib.request.urlopen(req, timeout=120))
            for im in d["choices"][0]["message"].get("images", []):
                url = im["image_url"]["url"]
                if url.startswith("data:"):
                    return Image.open(io.BytesIO(base64.b64decode(url.split(",", 1)[1])))
                return Image.open(io.BytesIO(urllib.request.urlopen(url, timeout=60).read()))
        except Exception as e:
            print(f"openrouter {model} failed: {type(e).__name__}", file=sys.stderr)
    return None

def card(date, title):
    W, H = 1280, 640
    img = Image.new("RGB", (W, H)); px = img.load()
    for y in range(H):
        t = y / H
        for x in range(W):
            u = x / W
            px[x, y] = (int(250 - 120 * t + 20 * u), int(170 - 60 * t + 30 * u), int(110 + 60 * t + 40 * u))
    d = ImageDraw.Draw(img)
    d.ellipse((W*0.62, H*0.42, W*0.62+180, H*0.42+180), fill=(255, 236, 200))
    img = img.filter(ImageFilter.GaussianBlur(1.5)); d = ImageDraw.Draw(img)
    f = lambda s: ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", s)
    d.text((70, 380), "Morning paper", font=f(64), fill=(255, 255, 255))
    d.text((72, 470), (title or "AI brief")[:60] + "  ·  " + date, font=f(30), fill=(255, 245, 235))
    return img

def main():
    a = argparse.ArgumentParser()
    a.add_argument("--date", required=True); a.add_argument("--prompt", default="calm Perth sunrise, coffee, laptop, gentle tech motifs")
    a.add_argument("--from", dest="src"); a.add_argument("--wait", type=int, default=20)
    a.add_argument("--title", default=""); a.add_argument("--repo", default="/workspace/ai-digest-rss")
    a.add_argument("--no-api", action="store_true")
    o = a.parse_args()
    img, how = None, None
    if o.src: img, how = from_path(o.src, o.wait), "generateimage"
    if img is None and not o.no_api: img, how = openrouter(o.prompt), "openrouter"
    if img is None: img, how = card(o.date, o.title), "card"
    rel = f"media/{o.date}.jpg"; out = os.path.join(o.repo, rel)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    fit(img).save(out, "JPEG", quality=85, optimize=True)
    print(json.dumps({"hero": rel, "source": how, "bytes": os.path.getsize(out)}))

if __name__ == "__main__":
    main()
