#!/usr/bin/env python3
"""
Превращает картинки в PDF или PPTX (одна картинка = один слайд/страница на весь экран).

Примеры:
    python photos_to_doc.py                                  # картинки из текущей папки -> <папка>.pptx
    python photos_to_doc.py ~/Pictures/trip                  # папка -> trip.pptx в текущей папке
    python photos_to_doc.py ~/Pictures/trip -o ~/out/trip.pdf        # формат по расширению
    python photos_to_doc.py ~/Pictures/trip -t pdf                   # формат явно
    python photos_to_doc.py a.png b.png c.jpg -o slides.pptx         # список файлов
    python photos_to_doc.py ./shots -e png jpg -o deck.pptx          # только png и jpg
    python photos_to_doc.py ./shots -r                               # включая подпапки

Зависимости: pip install pillow python-pptx
"""
import argparse
import re
import sys
from pathlib import Path

from PIL import Image

ALL_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff", ".gif"}


def natural_key(p: Path):
    # 2.jpg идёт перед 10.jpg
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", p.name)]


def normalize_exts(exts):
    if not exts:
        return ALL_EXTS
    return {"." + e.lower().lstrip(".") for e in exts}


def collect_images(inputs, exts, recursive):
    found = []
    for raw in inputs:
        p = Path(raw).expanduser()
        if not p.exists():
            sys.exit(f"Не найдено: {p}  (текущая папка: {Path.cwd()})")
        if p.is_dir():
            it = p.rglob("*") if recursive else p.iterdir()
            found += sorted(
                (f for f in it if f.is_file() and f.suffix.lower() in exts),
                key=natural_key,
            )
        elif p.suffix.lower() in exts:
            found.append(p)  # отдельные файлы остаются в том порядке, как указаны
        else:
            print(f"Пропускаю (неподходящий формат): {p}", file=sys.stderr)
    return found


def to_pdf(images, out: Path):
    pages = [Image.open(p).convert("RGB") for p in images]
    pages[0].save(out, "PDF", save_all=True, append_images=pages[1:], resolution=150.0)


def to_pptx(images, out: Path, slide_width_in: float):
    from pptx import Presentation
    from pptx.util import Emu, Inches

    prs = Presentation()
    # размер слайда подгоняем под пропорции первой картинки
    with Image.open(images[0]) as im:
        w, h = im.size
    prs.slide_width = Inches(slide_width_in)
    prs.slide_height = Emu(int(prs.slide_width * h / w))

    blank = prs.slide_layouts[6]
    for path in images:
        slide = prs.slides.add_slide(blank)
        slide.shapes.add_picture(
            str(path), 0, 0, width=prs.slide_width, height=prs.slide_height
        )
    prs.save(out)


def main():
    ap = argparse.ArgumentParser(
        description="Картинки -> PDF/PPTX, одна картинка на весь слайд."
    )
    ap.add_argument("inputs", nargs="*", default=["."],
                    help="папка(и) и/или файлы (по умолчанию: текущая папка)")
    ap.add_argument("-o", "--output", help="выходной файл (по умолчанию: <имя папки>.pptx)")
    ap.add_argument("-t", "--type", choices=["pptx", "pdf"],
                    help="формат; если не указан — берётся из расширения -o, иначе pptx")
    ap.add_argument("-e", "--ext", nargs="+",
                    help="брать только эти расширения, напр. -e png jpg (по умолчанию все)")
    ap.add_argument("-r", "--recursive", action="store_true", help="искать и в подпапках")
    ap.add_argument("--width", type=float, default=13.333,
                    help="ширина слайда в дюймах для pptx (по умолчанию 13.333 = 16:9)")
    args = ap.parse_args()

    images = collect_images(args.inputs, normalize_exts(args.ext), args.recursive)
    if not images:
        sys.exit("Картинки не найдены")

    # формат: -t > расширение -o > pptx
    fmt = args.type
    if not fmt and args.output:
        suffix = Path(args.output).suffix.lower().lstrip(".")
        fmt = suffix if suffix in ("pptx", "pdf") else None
    fmt = fmt or "pptx"

    # выходной путь
    if args.output:
        out = Path(args.output).expanduser()
        if out.suffix.lower() != f".{fmt}":
            out = out.with_name(out.name + f".{fmt}") if not out.suffix else out.with_suffix(f".{fmt}")
    else:
        first = Path(args.inputs[0]).expanduser().resolve()
        name = first.name if first.is_dir() else "output"
        out = Path.cwd() / f"{name}.{fmt}"

    out.parent.mkdir(parents=True, exist_ok=True)

    if fmt == "pdf":
        to_pdf(images, out)
    else:
        to_pptx(images, out, args.width)
    print(f"Готово: {out} ({len(images)} шт.)")


if __name__ == "__main__":
    main()