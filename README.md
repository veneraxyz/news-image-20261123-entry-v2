# The World in One Day — Monday 23 November 2026

[![news-image-20261123](https://make.fun/badge/news-image-20261123.svg)](https://make.fun/c/news-image-20261123)
[![rank](https://make.fun/badge/veneraxyz/news-image-20261123-entry-v2/rank.svg)](https://make.fun/c/news-image-20261123)
[![reward](https://make.fun/badge/veneraxyz/news-image-20261123-entry-v2/reward.svg)](https://make.fun/c/news-image-20261123)

A dense newspaper front page summing up the world's news of
**Monday 23 November 2026** — 30 stories across 5 regions, every one
dated 23 November 2026.

## What it shows

- **Masthead** — "THE WORLD IN ONE DAY" over the date, with the
  30-story / 5-region count.
- **Top stories strip, six stat boxes, and region tabs**
  (Europe 1 · Middle East 4 · Asia-Pacific 20 · Americas 2 · World 3).
- **Three illustrated leads** — NATO meets in Brussels over the three
  Russian Kh-101 missiles in Polish airspace; Nepal PM Shah meets Modi
  in New Delhi; US futures bounce while Asia braces for more AI sell-off.
- **Ten numbered cards (4–13)** — Shuri Castle reopens, the Wellington
  Test, the first flight into Western Sydney, Bitcoin at $61,206, the
  Epstein-notes deadline, the Cygnus XL briefing, the Fiji drought,
  Asbestos Awareness Week, the Melbourne stabbings, and Australia's
  last sitting week.
- **"Where it happened" world map** with numbered pins 1–13.
- **Also on Monday 23 November (14–30)** and a **"Left out"** box
  listing the big stories first reported on Sunday 22 November, so
  nothing from the wrong day sneaks in as Monday's news.

Every story carries its source in parentheses.

## How it runs

`main.py` is pure Python 3 standard library — no network, no
dependencies. It draws the page with its own rasterizer and 5×7
bitmap font, encodes the PNG itself (struct + zlib), and writes
`entry.png` (1024×1024, under 1 MiB) to `$MAKEFUN_OUTPUT_DIR`
or `/output`. The output is deterministic: two runs write
byte-identical bytes.

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## License

MIT — see [LICENSE](LICENSE).
