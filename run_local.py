#!/usr/bin/env python3
"""Local runner for ytSheetMusic — skips AWS S3 uploads/downloads."""

import argparse
import os
import shutil
import sys
from typing import Optional

from screenshot import Screenie
from combine import Join


def download_video(url: str, file_name: str) -> str:
    out = f"{file_name}.mp4"
    if os.path.exists(out):
        print(f"Using existing {out}")
        return out
    # Prefer mp4; fall back to best video+audio merge
    cmd = (
        f'yt-dlp -f "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/b" '
        f'--merge-output-format mp4 -o "{out}" "{url}"'
    )
    print(cmd)
    code = os.system(cmd)
    if code != 0 or not os.path.exists(out):
        raise RuntimeError("yt-dlp failed to download the video")
    return out


def default_output_dir() -> str:
    return os.path.join(os.path.expanduser("~/Downloads"), "Sheet Music")


def run(
    url: str,
    file_name: str,
    hands: bool = False,
    threshold: float = 0.9,
    out_dir: Optional[str] = None,
):
    folder_name = "".join(file_name.split(" "))
    out_dir = out_dir or default_output_dir()
    os.makedirs(out_dir, exist_ok=True)
    pdf_path = os.path.join(out_dir, f"{file_name}.pdf")

    video_path = download_video(url, file_name)

    print("Taking screenshots…")
    s = Screenie(video_path, fname=folder_name, hands=hands, threshold=threshold)
    s.take_screenies()

    print("Combining into PDF…")
    # Avoid Join trying to pull from S3 when the folder is empty / missing
    if folder_name not in os.listdir("."):
        raise RuntimeError(f"No screenshot folder created: {folder_name}")
    frames = [f for f in os.listdir(folder_name) if f.endswith(".jpg")]
    if not frames:
        raise RuntimeError("No frames extracted — try hands=True/False or a lower threshold")

    # Monkey-patch AWS calls used during Join init / save
    j = Join(folder_name)
    j.save(f"{file_name}.pdf")
    src = os.path.join(folder_name, f"{file_name}.pdf")
    shutil.copy2(src, pdf_path)
    print(f"Saved: {pdf_path}")
    return pdf_path


def main():
    p = argparse.ArgumentParser(description="Extract sheet music PDF from a YouTube video")
    p.add_argument("url", help="YouTube URL")
    p.add_argument("-n", "--name", default=None, help="Output base name")
    p.add_argument("--hands", action="store_true", help="Crop out hands / non-score UI")
    p.add_argument("--threshold", type=float, default=0.9, help="Frame similarity threshold")
    p.add_argument(
        "--out-dir",
        default=None,
        help='Output directory for the final PDF (default: "~/Downloads/Sheet Music")',
    )
    args = p.parse_args()

    name = args.name
    if not name:
        _, _, name = args.url.rpartition("watch?v=")
        name = name.split("&")[0] or "sheetmusic"

    try:
        run(args.url, name, hands=args.hands, threshold=args.threshold, out_dir=args.out_dir)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
