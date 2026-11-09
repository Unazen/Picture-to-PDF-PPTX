#!/usr/bin/env python3
"""
Превращает папку с картинками в PDF или PPTX (одна картинка = один слайд/страница на весь экран).

Использование:
    python photos_to_doc.py ./photos slides.pptx
    python photos_to_doc.py ./photos album.pdf

Зависимости:
    pip install pillow python-pptx
    (на Arch: sudo pacman -S python-pillow python-python-pptx  или через venv + pip)
"""
import re
import sys
from pathlib import Path

from PIL import Image

EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}


def natural_key(p: Path):
    # 2.jpg идёт перед 10.jpg
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", p.name)]


def list_images(folder: Path):
    imgs = [p for p in folder.iterdir() if p.suffix.lower() in EXTS]
    return sorted(imgs, key=natural_key)


def to_pdf(images, out: Path):
    pages = [Image.open(p).convert("RGB") for p in images]
    pages[0].save(out, "PDF", save_all=True, append_images=pages[1:], resolution=150.0)


def to_pptx(images, out: Path):
    from pptx import Presentation
    from pptx.util import Inches, Emu

    prs = Presentation()
    # размер слайда подгоняем под пропорции первой картинки
    with Image.open(images[0]) as im:
        w, h = im.size
    prs.slide_width = Inches(13.333)
    prs.slide_height = Emu(int(prs.slide_width * h / w))

    blank = prs.slide_layouts[6]  # пустой макет
    for path in images:
        slide = prs.slides.add_slide(blank)
        slide.shapes.add_picture(
            str(path), 0, 0, width=prs.slide_width, height=prs.slide_height
        )
    prs.save(out)


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    folder, out = Path(sys.argv[1]), Path(sys.argv[2])
    images = list_images(folder)
    if not images:
        sys.exit(f"В {folder} нет картинок")

    ext = out.suffix.lower()
    if ext == ".pdf":
        to_pdf(images, out)
    elif ext == ".pptx":
        to_pptx(images, out)
    else:
        sys.exit("Выходной файл должен быть .pdf или .pptx")
    print(f"Готово: {out} ({len(images)} шт.)")


if __name__ == "__main__":
    main()