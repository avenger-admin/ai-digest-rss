#!/usr/bin/env python3
"""Prepend a weekday TLDR item to feed.xml.

Usage:
  append_item.py --date 2026-09-17 --image media/2026-09-17.jpg \\
    --do 'bullet1' 'bullet2' --watch 'w1' 'w2'

--image is Pages-relative (e.g. media/YYYY-MM-DD.jpg), already in the repo.
One still/day: media:thumbnail + media:content and <img> atop description. No video.
"""
import argparse
import html
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

FEED = Path(__file__).with_name("feed.xml")
TZ = ZoneInfo("Australia/Perth")
BASE = "https://avenger-admin.github.io/ai-digest-rss"


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--date", required=True)
    p.add_argument("--do", nargs="+", required=True)
    p.add_argument("--watch", nargs="*", default=[])
    p.add_argument("--image", required=True, help="e.g. media/2026-09-17.jpg")
    p.add_argument("--image-width", type=int, default=1280)
    p.add_argument("--image-height", type=int, default=640)
    p.add_argument("--image-alt", default="Lead still for today’s digest")
    args = p.parse_args()
    day = datetime.strptime(args.date, "%Y-%m-%d").replace(tzinfo=TZ)
    pub = day.replace(hour=7, minute=45, second=0)
    rfc = pub.strftime("%a, %d %b %Y %H:%M:%S ") + pub.strftime("%z")
    do_li = "\n".join(f"<li>{html.escape(b)}</li>" for b in args.do)
    watch_block = ""
    if args.watch:
        w_li = "\n".join(f"<li>{html.escape(b)}</li>" for b in args.watch)
        watch_block = f"<h2>Watch</h2>\n<ul>\n{w_li}\n</ul>\n"
    link = f"{BASE}/#{args.date}"
    img = args.image if args.image.startswith("http") else f"{BASE}/{args.image.lstrip('/')}"
    alt = html.escape(args.image_alt)
    text = FEED.read_text()
    if "xmlns:media=" not in text:
        text = text.replace(
            '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">',
            '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:media="http://search.yahoo.com/mrss/">',
            1,
        )
    item = f"""    <item>
      <title>AI digest — {args.date}</title>
      <link>{link}</link>
      <guid isPermaLink="false">ai-digest-{args.date}</guid>
      <pubDate>{rfc}</pubDate>
      <media:thumbnail url="{img}" width="{args.image_width}" height="{args.image_height}"/>
      <media:content url="{img}" type="image/jpeg" medium="image" width="{args.image_width}" height="{args.image_height}"/>
      <description><![CDATA[
<img src="{img}" alt="{alt}"/>
<h2>Do this week</h2>
<ul>
{do_li}
</ul>
{watch_block}]]></description>
    </item>
"""
    idx = text.find("    <item>")
    if idx == -1:
        raise SystemExit("no <item> found")
    now = datetime.now(TZ)
    lbd = now.strftime("%a, %d %b %Y %H:%M:%S ") + now.strftime("%z")
    text = re.sub(r"<lastBuildDate>[^<]*</lastBuildDate>", f"<lastBuildDate>{lbd}</lastBuildDate>", text, count=1)
    FEED.write_text(text[:idx] + item + text[idx:])
    print(f"prepended {args.date} with {img}")


if __name__ == "__main__":
    main()
