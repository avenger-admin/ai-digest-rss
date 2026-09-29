#!/usr/bin/env python3
"""Publish the Spinal Frontier HTML morning paper to GitHub Pages.

Writes:
  index.html                  — always “today”
  archive/YYYY-MM-DD.html     — dated archive copy
  archive/index.html          — simple listing (regenerated from archive/*.html)

Does NOT touch feed.xml or media/ (Feeder RSS is retired; keep files in place).

────────────────────────────────────────────────────────────────────────────
Daily workflow (Number One / Researcher)
────────────────────────────────────────────────────────────────────────────
1. Research & draft 3–5 friendly items (headline + 2–3 sentences + optional URL).
2. Optionally drop a hero still at media/YYYY-MM-DD.jpg (or .png).
3. Either:
   A) Draft a full HTML page, then:
        python3 publish_paper.py --date YYYY-MM-DD --from-html draft.html
   B) Or hand a JSON content file, then:
        python3 publish_paper.py --date YYYY-MM-DD --from-json content.json
4. Review the generated index.html locally (open in a browser).
5. Commit & push main:
        git add index.html archive/ style.css media/YYYY-MM-DD.jpg
        git commit -m "Morning paper YYYY-MM-DD"
        git push origin main
6. Live in ~1 min at:
        https://avenger-admin.github.io/ai-digest-rss/
        https://avenger-admin.github.io/ai-digest-rss/archive/YYYY-MM-DD.html

JSON shape (--from-json):
{
  "title": "Good morning — AI brief",          # optional
  "lede": "A short, friendly skim…",           # optional
  "hero": "media/2026-09-29.jpg",              # optional; relative to repo root
  "hero_alt": "…",                             # optional
  "callout": { "title": "…", "body": "…" },    # optional; omit for none
  "items": [
    {
      "headline": "…",
      "body": ["paragraph 1", "paragraph 2"],  # 1–3 short paras
      "source_label": "Anthropic →",           # optional
      "source_url": "https://…"                # optional
    }
  ]
}
"""
from __future__ import annotations

import argparse
import html
import json
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent
TZ = ZoneInfo("Australia/Perth")
BASE = "https://avenger-admin.github.io/ai-digest-rss"


def _parse_date(s: str) -> datetime:
    return datetime.strptime(s, "%Y-%m-%d").replace(tzinfo=TZ)


def _friendly_date(day: datetime) -> str:
    # e.g. Tuesday 29 Sep 2026
    return day.strftime("%A %-d %b %Y")


def _rewrite_paths_for_archive(index_html: str) -> str:
    """Turn root-relative asset hrefs/srcs into ../ for archive/YYYY-MM-DD.html."""
    out = index_html
    out = out.replace('href="style.css"', 'href="../style.css"')
    out = out.replace('src="media/', 'src="../media/')
    out = out.replace('href="media/', 'href="../media/')
    # Footer: archive link → back to today
    out = re.sub(
        r'<span><a href="archive/[^"]+\.html">Today’s archive page</a>\s*·\s*<a href="archive/">Archives</a></span>',
        '<span><a href="../">Back to today</a> · <a href="./">Archives</a></span>',
        out,
        count=1,
    )
    # Kicker tweak
    out = out.replace(">Morning paper</p>", ">Morning paper · archive</p>", 1)
    out = out.replace(
        f"<title>Good morning — AI brief · ",
        f"<title>Good morning — AI brief · ",
    )
    # Title suffix
    out = re.sub(
        r"(<title>Good morning — AI brief · [^<]+)</title>",
        r"\1 (archive)</title>",
        out,
        count=1,
    )
    return out


def _render_from_json(day: datetime, data: dict) -> str:
    title = html.escape(data.get("title") or "Good morning — AI brief")
    lede = html.escape(
        data.get("lede")
        or "A short, friendly skim of what’s new in AI — so you can start the day curious, not buried."
    )
    friendly = _friendly_date(day)
    date_iso = day.strftime("%Y-%m-%d")
    short = day.strftime("%-d %b %Y")

    hero = data.get("hero") or ""
    hero_alt = html.escape(data.get("hero_alt") or "Lead still for today’s brief")
    if hero:
        hero_block = f"""    <figure class="hero">
      <img src="{html.escape(hero)}" width="1280" height="640" alt="{hero_alt}"/>
    </figure>"""
    else:
        hero_block = """    <figure class="hero">
      <div class="hero-fallback" role="img" aria-label="Morning paper">
        <div><strong>Good morning</strong>Your AI brief is ready</div>
      </div>
    </figure>"""

    stories = []
    for item in data.get("items") or []:
        headline = html.escape(item.get("headline") or "Untitled")
        paras = item.get("body") or []
        if isinstance(paras, str):
            paras = [paras]
        body_html = "\n".join(f"        <p>{html.escape(p)}</p>" for p in paras if p)
        src_url = item.get("source_url")
        src_label = item.get("source_label") or "Source →"
        source = ""
        if src_url:
            source = (
                f'\n        <p class="source"><a href="{html.escape(src_url)}" '
                f'rel="noopener">{html.escape(src_label)}</a></p>'
            )
        stories.append(
            f"""      <article class="story">
        <h2>{headline}</h2>
{body_html}{source}
      </article>"""
        )
    stories_html = "\n\n".join(stories) if stories else "      <!-- no items -->"

    callout = data.get("callout")
    callout_html = ""
    if callout and (callout.get("title") or callout.get("body")):
        ct = html.escape(callout.get("title") or "Quick tip")
        cb = html.escape(callout.get("body") or "")
        callout_html = f"""
    <aside class="callout" aria-label="Quick tip">
      <strong>{ct}</strong>
      <p>{cb}</p>
    </aside>"""

    return f"""<!DOCTYPE html>
<html lang="en-AU">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>{title} · {html.escape(short)}</title>
  <meta name="description" content="Spinal Frontier morning AI brief for {html.escape(friendly)}."/>
  <link rel="stylesheet" href="style.css"/>
</head>
<body>
  <main class="wrap">
    <header class="masthead">
      <div>
        <p class="kicker">Morning paper</p>
        <h1>{title}</h1>
      </div>
      <div class="date-chip">{html.escape(friendly)} · Perth</div>
    </header>

    <p class="lede">{lede}</p>

{hero_block}

    <section class="stories" aria-label="Today’s stories">
{stories_html}
    </section>
{callout_html}

    <footer class="footer">
      <span>Published for Spinal Frontier</span>
      <span><a href="archive/{date_iso}.html">Today’s archive page</a> · <a href="archive/">Archives</a></span>
    </footer>
  </main>
</body>
</html>
"""


def _list_archive_dates() -> list[str]:
    archive = ROOT / "archive"
    dates = sorted(
        {p.stem for p in archive.glob("????-??-??.html")},
        reverse=True,
    )
    return dates


def _write_archive_index(dates: list[str]) -> None:
    items = []
    for d in dates:
        try:
            day = _parse_date(d)
            label = _friendly_date(day)
        except ValueError:
            label = d
        items.append(
            f"""      <article class="story">
        <h2><a href="{d}.html">{html.escape(label)}</a></h2>
        <p>Archived morning paper for {html.escape(d)}.</p>
      </article>"""
        )
    body = "\n".join(items) if items else "      <p>No editions yet.</p>"
    html_out = f"""<!DOCTYPE html>
<html lang="en-AU">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>AI brief archives · Spinal Frontier</title>
  <link rel="stylesheet" href="../style.css"/>
</head>
<body>
  <main class="wrap">
    <header class="masthead">
      <div>
        <p class="kicker">Morning paper</p>
        <h1>Archives</h1>
      </div>
      <div class="date-chip"><a href="../">← Today’s brief</a></div>
    </header>
    <p class="lede">Dated editions of the Spinal Frontier AI morning paper.</p>
    <section class="stories">
{body}
    </section>
    <footer class="footer">
      <span>Published for Spinal Frontier</span>
      <span><a href="../">Today</a></span>
    </footer>
  </main>
</body>
</html>
"""
    (ROOT / "archive" / "index.html").write_text(html_out, encoding="utf-8")


def publish(day: datetime, index_html: str) -> None:
    date_iso = day.strftime("%Y-%m-%d")
    archive_dir = ROOT / "archive"
    archive_dir.mkdir(exist_ok=True)

    index_path = ROOT / "index.html"
    archive_path = archive_dir / f"{date_iso}.html"

    index_path.write_text(index_html, encoding="utf-8")
    archive_path.write_text(_rewrite_paths_for_archive(index_html), encoding="utf-8")
    _write_archive_index(_list_archive_dates())

    print(f"Wrote {index_path.relative_to(ROOT)}")
    print(f"Wrote {archive_path.relative_to(ROOT)}")
    print(f"Wrote archive/index.html")
    print(f"Today URL:   {BASE}/")
    print(f"Archive URL: {BASE}/archive/{date_iso}.html")


def main() -> None:
    p = argparse.ArgumentParser(
        description="Publish Spinal Frontier HTML morning paper (index + archive)."
    )
    p.add_argument("--date", required=True, help="YYYY-MM-DD (Australia/Perth edition date)")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--from-html", type=Path, help="Draft HTML to copy into index + archive")
    g.add_argument("--from-json", type=Path, help="JSON content file (see module docstring)")
    args = p.parse_args()

    day = _parse_date(args.date)
    if args.from_html:
        raw = args.from_html.read_text(encoding="utf-8")
        # Ensure footer archive link points at this date if missing
        if f"archive/{args.date}.html" not in raw and 'href="archive/' not in raw:
            pass  # leave draft as-is; author owns links
        publish(day, raw)
    else:
        data = json.loads(args.from_json.read_text(encoding="utf-8"))
        publish(day, _render_from_json(day, data))


if __name__ == "__main__":
    main()
