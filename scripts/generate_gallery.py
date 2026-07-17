"""assets/gallery/ の画像から README.md のギャラリーグリッドを自動生成する。

使い方:
    python scripts/generate_gallery.py

- assets/gallery/ 内の画像ファイルを走査
- mtime（更新日時）の新しい順で並べ替え
- 上位3枚は表示領域のグリッドに配置
- 残りは <details> 内に隠し、1行4枚で配置
- <!-- GALLERY:START --> と <!-- GALLERY:END --> の間を書き換え
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GALLERY_DIR = ROOT / "assets" / "gallery"
README = ROOT / "README.md"
IMG_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}

START_MARKER = "<!-- GALLERY:START -->"
END_MARKER = "<!-- GALLERY:END -->"

TOP_ROW_COUNT = 3
DETAILS_ROW_COUNT = 4


def list_images() -> list[Path]:
    """gallery/ 内の画像ファイルを mtime の新しい順で返す。"""
    files = [p for p in GALLERY_DIR.iterdir() if p.suffix.lower() in IMG_EXTS]
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return files


def chunk(items: list, size: int) -> list[list]:
    """items を `size` 件ごとの行に分割する。最終行は件数が少ない場合がある。"""
    return [items[i : i + size] for i in range(0, len(items), size)]


def render_row(paths: list[Path], per_row: int) -> str:
    width_pct = 100 // per_row - 3
    lines = ["<div>"]
    for i, p in enumerate(paths):
        is_last = i == len(paths) - 1
        style = "" if is_last else ' style="margin-right: 15px"'
        lines.append(
            f'<img align="left" width="{width_pct}%"{style} src="./assets/gallery/{p.name}">'
        )
    lines.append('<br clear="left">')
    lines.append("</div>")
    return "\n".join(lines)


def render_gallery(images: list[Path]) -> str:
    top = images[:TOP_ROW_COUNT]
    rest = images[TOP_ROW_COUNT:]

    parts: list[str] = []
    parts.append(render_row(top, TOP_ROW_COUNT))
    parts.append("")
    parts.append("<br>")
    parts.append("")

    if rest:
        parts.append("<details><summary>and more...</summary>")
        parts.append("<br>")
        for row in chunk(rest, DETAILS_ROW_COUNT):
            parts.append(render_row(row, DETAILS_ROW_COUNT))
            parts.append("")
        parts.append("</details>")

    return "\n".join(parts)


def update_readme(gallery_html: str) -> None:
    text = README.read_text(encoding="utf-8")
    pattern = re.compile(
        re.escape(START_MARKER) + r".*?" + re.escape(END_MARKER),
        re.DOTALL,
    )
    replacement = f"{START_MARKER}\n{gallery_html}\n{END_MARKER}"
    new_text, n = pattern.subn(replacement, text)
    if n == 0:
        sys.exit(f"markers not found in {README}")
    README.write_text(new_text, encoding="utf-8")
    print(f"updated {README} ({len(gallery_html)} chars in gallery block)")


def main() -> None:
    images = list_images()
    if not images:
        sys.exit(f"no images found in {GALLERY_DIR}")
    print(f"found {len(images)} image(s)")
    html = render_gallery(images)
    update_readme(html)


if __name__ == "__main__":
    main()
