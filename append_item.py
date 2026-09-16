#!/usr/bin/env python3
"""Prepend a weekday TLDR item to feed.xml. Usage:
  append_item.py --date 2026-09-17 --do 'bullet1' 'bullet2' --watch 'w1' 'w2'
"""
import argparse
import html
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

FEED = Path(__file__).with_name("feed.xml")
TZ = ZoneInfo("Australia/Perth")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--date", required=True, help="YYYY-MM-DD")
    p.add_argument("--do", nargs="+", required=True)
    p.add_argument("--watch", nargs="*", default=[])
    args = p.parse_args()
    day = datetime.strptime(args.date, "%Y-%m-%d").replace(tzinfo=TZ)
    pub = day.replace(hour=7, minute=45, second=0)
    rfc = pub.strftime("%a, %d %b %Y %H:%M:%S %z")
    # RFC 822 wants +0800 style
    rfc = pub.strftime("%a, %d %b %Y %H:%M:%S ") + pub.strftime("%z")
    do_li = "\n".join(f"<li>{html.escape(b)}</li>" for b in args.do)
    watch_block = ""
    if args.watch:
        w_li = "\n".join(f"<li>{html.escape(b)}</li>" for b in args.watch)
        watch_block = f"<h2>Watch</h2>\n<ul>\n{w_li}\n</ul>\n"
    item = f"""    <item>
      <title>AI digest — {args.date}</title>
      <guid isPermaLink="false">ai-digest-{args.date}</guid>
      <pubDate>{rfc}</pubDate>
      <description><![CDATA[
<h2>Do this week</h2>
<ul>
{do_li}
</ul>
{watch_block}]]></description>
    </item>
"""
    text = FEED.read_text()
    marker = "    <item>"
    idx = text.find(marker)
    if idx == -1:
        raise SystemExit("no <item> found")
    # refresh lastBuildDate
    import re
    now = datetime.now(TZ)
    lbd = now.strftime("%a, %d %b %Y %H:%M:%S ") + now.strftime("%z")
    text = re.sub(r"<lastBuildDate>[^<]*</lastBuildDate>", f"<lastBuildDate>{lbd}</lastBuildDate>", text, count=1)
    text = text[:idx] + item + text[idx:]
    FEED.write_text(text)
    print(f"prepended {args.date}")


if __name__ == "__main__":
    main()
