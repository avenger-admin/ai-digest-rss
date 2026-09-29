# Spinal Frontier — AI morning paper

Friendly GitHub Pages “morning paper” for the **Daily AI News Summary** room.

## Live URLs

| What | URL |
|------|-----|
| **Today** (always current) | https://avenger-admin.github.io/ai-digest-rss/ |
| **Dated archive** | https://avenger-admin.github.io/ai-digest-rss/archive/YYYY-MM-DD.html |
| Archive index | https://avenger-admin.github.io/ai-digest-rss/archive/ |

Example for 29 Sep 2026:  
https://avenger-admin.github.io/ai-digest-rss/archive/2026-09-29.html

Pages serves from `/` on `main`. `.nojekyll` is present so assets are served as-is.

## Tone

Warm “good morning news” — short headlines, 2–3 sentences, optional source links. Not a standards memo.

## Publish (Number One / Researcher)

Helper: `publish_paper.py`

```bash
# Option A — you already drafted HTML
python3 publish_paper.py --date 2026-09-29 --from-html draft.html

# Option B — JSON content (renders the paper for you)
python3 publish_paper.py --date 2026-09-29 --from-json content.json
```

That writes `index.html` (today) and `archive/YYYY-MM-DD.html`, and refreshes `archive/index.html`.

Then commit & push `main`:

```bash
git add index.html style.css archive/ media/YYYY-MM-DD.jpg publish_paper.py
git commit -m "Morning paper YYYY-MM-DD"
git push origin main
```

Drop a hero image at `media/YYYY-MM-DD.jpg` when you have one; otherwise the JSON path can omit `hero` and a CSS placeholder appears.

See the docstring at the top of `publish_paper.py` for the JSON schema and the full daily checklist.

## Feeder / RSS — retired

The old Feeder-oriented landing page and daily RSS promotion are **retired**.

- `feed.xml` and `media/` are **kept in the repo** (do not delete) for history / any leftover subscribers.
- Do **not** promote `feed.xml` in the room or README going forward.
- Legacy helper `append_item.py` remains for reference only; new editions use `publish_paper.py` + HTML.

## Layout

```
index.html          ← always “today”
style.css
archive/
  index.html
  YYYY-MM-DD.html
media/              ← hero stills (kept)
feed.xml            ← legacy RSS (kept, not promoted)
.nojekyll
publish_paper.py
```
