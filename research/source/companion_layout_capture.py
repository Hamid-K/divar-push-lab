#!/usr/bin/env python3
"""Capture the English companion report's graphics and text layout separately.

This imports the published ReportLab builder unchanged. Its paragraph layout is
still measured by ReportLab, so page breaks, boxes, rules, arrows, and diagrams
stay at the same coordinates. Text drawing is replaced with manifest entries.

Usage:
    python3 research/source/companion_layout_capture.py
    python3 research/source/companion_layout_capture.py \
        --pdf /private/tmp/companion_graphics.pdf \
        --manifest /private/tmp/companion_text_manifest.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import build_iran_mobile_apps_companion_v2 as english
from pypdf import PdfReader
from reportlab.pdfbase import pdfmetrics


DEFAULT_PDF = Path("/private/tmp/companion_graphics.pdf")
DEFAULT_MANIFEST = Path("/private/tmp/companion_text_manifest.json")


class TextCapture:
    def __init__(self) -> None:
        self.slots: list[dict[str, Any]] = []
        self.page_counts: dict[int, int] = {}

    def add(self, canvas: Any, *, kind: str, text: str, x: float, y: float,
            width: float, height: float, align: str, font: str,
            font_size: float, tone: str, leading: float | None = None,
            formatted: bool | None = None) -> None:
        page = canvas.getPageNumber()
        self.page_counts[page] = self.page_counts.get(page, 0) + 1
        slot: dict[str, Any] = {
            "id": f"p{page:02d}-{self.page_counts[page]:04d}",
            "page": page,
            "kind": kind,
            "text": text,
            "x": round(x, 3),
            "y": round(y, 3),
            "width": round(width, 3),
            "height": round(height, 3),
            "align": align,
            "font": font,
            "font_size": round(font_size, 3),
            "tone": tone,
            "color": english.hx(tone),
        }
        if leading is not None:
            slot["leading"] = round(leading, 3)
        if formatted is not None:
            slot["formatted"] = formatted
        self.slots.append(slot)


class CapturedParagraph:
    """Keep the measured English height while suppressing paragraph painting."""

    def __init__(self, capture: TextCapture, text: str, width: float,
                 height: float, size: float, leading: float, color: str,
                 bold: bool, formatted: bool) -> None:
        self.capture = capture
        self.text = text
        self.width = width
        self.height = height
        self.size = size
        self.leading = leading
        self.color = color
        self.bold = bold
        self.formatted = formatted

    def drawOn(self, canvas: Any, x: float, y: float, *args: Any,
               **kwargs: Any) -> None:
        self.capture.add(
            canvas, kind="paragraph", text=self.text, x=x, y=y,
            width=self.width, height=self.height, align="left",
            font="ArialB" if self.bold else "ArialR", font_size=self.size,
            tone=self.color, leading=self.leading, formatted=self.formatted,
        )


def capture_layout(pdf: Path, manifest: Path) -> dict[str, Any]:
    pdf = pdf.resolve()
    manifest = manifest.resolve()
    pdf.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    captured = TextCapture()

    original_pdf = english.PDF
    original_txt = english.txt
    original_right = english.right
    original_para_obj = english.para_obj

    def capture_txt(canvas: Any, value: str, x: float, y: float,
                    size: float = 9, tone: str = "ink",
                    font: str = "ArialR") -> None:
        captured.add(
            canvas, kind="baseline", text=value, x=x, y=y,
            width=pdfmetrics.stringWidth(value, font, size), height=size,
            align="left", font=font, font_size=size, tone=tone,
        )

    def capture_right(canvas: Any, value: str, x: float, y: float,
                      size: float = 9, tone: str = "ink",
                      font: str = "ArialR") -> None:
        captured.add(
            canvas, kind="baseline", text=value, x=x, y=y,
            width=pdfmetrics.stringWidth(value, font, size), height=size,
            align="right", font=font, font_size=size, tone=tone,
        )

    def capture_para_obj(value: str, width: float, *, size: float = 9.1,
                         leading: float = 13.3, color: str = "ink",
                         bold: bool = False,
                         formatted: bool = True) -> tuple[CapturedParagraph, float]:
        _, height = original_para_obj(
            value, width, size=size, leading=leading, color=color,
            bold=bold, formatted=formatted,
        )
        return (
            CapturedParagraph(captured, value, width, height, size, leading,
                              color, bold, formatted),
            height,
        )

    try:
        english.PDF = pdf
        english.txt = capture_txt
        english.right = capture_right
        english.para_obj = capture_para_obj
        english.main()
    finally:
        english.PDF = original_pdf
        english.txt = original_txt
        english.right = original_right
        english.para_obj = original_para_obj

    reader = PdfReader(str(pdf))
    page_count = len(reader.pages)
    if page_count != 20:
        raise RuntimeError(f"Expected 20 pages of graphics, got {page_count}")
    if not captured.slots or {slot["page"] for slot in captured.slots} != set(range(1, 21)):
        raise RuntimeError("Text capture did not cover every page")
    if any(page.extract_text().strip() for page in reader.pages):
        raise RuntimeError("Graphics-only PDF unexpectedly contains drawn text")

    result = {
        "schema": "companion-layout-capture/v1",
        "source_builder": str(Path(english.__file__).resolve()),
        "graphics_pdf": str(pdf),
        "page_size_pt": [round(english.W, 3), round(english.H, 3)],
        "page_count": page_count,
        "slot_count": len(captured.slots),
        "slots": captured.slots,
    }
    manifest.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf", type=Path, default=DEFAULT_PDF)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    args = parser.parse_args()
    result = capture_layout(args.pdf, args.manifest)
    print(f"{result['graphics_pdf']} ({result['page_count']} pages)")
    print(f"{args.manifest.resolve()} ({result['slot_count']} text slots)")


if __name__ == "__main__":
    main()
