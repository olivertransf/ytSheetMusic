# ytSheetMusic

Fork of [Wubaboo/ytSheetMusic](https://github.com/Wubaboo/ytSheetMusic) with a **local runner** that does not need AWS S3.

Get sheet music from YouTube videos: download → screenshot unique score frames → crop → combine into a PDF.

Test URL: https://www.youtube.com/watch?v=61Ln3Jy8WxU

![ytSheetMusic](https://github.com/Wubaboo/ytSheetMusic/assets/59407231/05467c91-6bbb-4f25-a669-2e169cfc87d7)

## Requirements

- Python 3.9+
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) on your `PATH`
- [ffmpeg](https://ffmpeg.org/) on your `PATH` (used by yt-dlp for merges)

## Quick start (local)

```bash
git clone https://github.com/olivertransf/ytSheetMusic.git
cd ytSheetMusic

python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python run_local.py "https://www.youtube.com/watch?v=VIDEO_ID" \
  -n "Piece Name" \
  --hands
```

PDF is written to `~/Downloads/<Piece Name>.pdf` by default.

### Options

| Flag | Meaning |
|------|---------|
| `-n` / `--name` | Output base name (video id if omitted) |
| `--hands` | Crop hands / non-score UI from frames |
| `--threshold` | Frame similarity cutoff (default `0.9`; lower keeps more frames) |
| `--out-dir` | Output directory for the final PDF (default `~/Downloads`) |

Example:

```bash
python run_local.py "https://www.youtube.com/watch?v=tyloC0e-Tqk" \
  -n "When You Wish Upon A Star" \
  --hands
```

## How it works

1. **download** — `yt-dlp` saves the video as MP4
2. **screenshot** — samples frames, keeps unique score regions (`screenshot.py`)
3. **combine** — stacks crops onto letter pages and writes a PDF (`combine.py`)

`run_local.py` orchestrates that pipeline and skips S3. Upstream `main.py` / `app.py` still expect the original AWS-backed flow.

## Modules

- **`run_local.py`** — CLI for local PDF generation (preferred)
- **`main.py`** — Original entry that uploaded to S3
- **`download.py`** — YouTube download helpers
- **`screenshot.py`** — Unique frame capture + optional hand crop
- **`combine.py`** — Page layout + PDF export
- **`awsServices.py`** — Local no-op stub (S3 disabled)

## Original upstream usage

```python
from main import main
main(url, "Clair de Lune", hands=True)
```

That path still imports the Flask app / bucket helpers and is not needed for local runs.
