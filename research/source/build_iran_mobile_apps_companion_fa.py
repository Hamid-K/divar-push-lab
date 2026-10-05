#!/usr/bin/env python3
"""Translate English companion text in place over identical vector graphics."""

from __future__ import annotations

import html
import json
import re
import tempfile
from collections import defaultdict
from pathlib import Path

from pypdf import PdfReader, PdfWriter

from companion_layout_capture import capture_layout
from pango_fa_overlay import PangoFaOverlay, TextDoesNotFit, add_uri


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUTPUT = ROOT / "Iran_mobile_apps_companion_fa.pdf"
LABELS = HERE / "companion_fa_short_labels.json"
PAGES = [
    HERE / "companion_fa_pages_01_07.json",
    HERE / "companion_fa_pages_08_14.json",
    HERE / "companion_fa_pages_15_20.json",
]
LINK = re.compile(r"\[[^\]]+\]\((https?://[^)\s]+)\)")
HASH = re.compile(r"^[a-f0-9]{64}$")
NUMBER = re.compile(r"^(?:\*\*)?\d+(?:[.\-/]\d+)*(?:-[bw])?(?:\*\*)?$")


def translations_for(slots: list[dict]) -> dict[str, str]:
    by_text = json.loads(LABELS.read_text(encoding="utf-8"))
    by_id: dict[str, str] = {}
    for path in PAGES:
        entries = json.loads(path.read_text(encoding="utf-8"))
        duplicates = set(by_id) & set(entries)
        if duplicates:
            raise ValueError(f"Duplicate translated slots: {sorted(duplicates)[:5]}")
        by_id.update(entries)
    valid = {slot["id"] for slot in slots}
    unknown = set(by_id) - valid
    if unknown:
        raise ValueError(f"Unknown translated slots: {sorted(unknown)[:5]}")
    result = {
        slot["id"]: by_id.get(slot["id"], by_text.get(slot["text"], slot["text"]))
        for slot in slots
    }
    # New English prose must not silently slip into a Persian report.
    missing = []
    for slot in slots:
        original = slot["text"]
        if result[slot["id"]] != original:
            continue
        if slot["font"] == "Courier" or HASH.fullmatch(original) or NUMBER.fullmatch(original):
            continue
        if original in {"Divar", "Rubika", "Eitaa", "Snapp", "Neshan", "Telewebion",
                        "Balad", "Digikala", "Aparat", "Baam", "Behrooz", "2026",
                        "PUSH_LOGGER", "GEOSUBMIT", "COLLECT", "GEOLOCATE",
                        "metadata.cmd == PUSH_LOGGER?"}:
            continue
        if re.search(r"[A-Za-z]{3}", original):
            missing.append((slot["id"], original[:85]))
    if missing:
        raise ValueError("Untranslated natural-language slots:\n" +
                         "\n".join(map(str, missing)))
    return result


def baseline_box(slot: dict, same_page: list[dict], page_width: float) -> tuple[float, float, float, float]:
    """Expand a text line within its original graph/table lane."""
    x, y, size = slot["x"], slot["y"], slot["font_size"]
    if slot["align"] == "right":
        width = 190 if slot["page"] == 19 and x > 500 else max(slot["width"] * 1.45, 38)
        return x - width, y - size * .36, width, size * 1.78
    if size >= 20:
        width = 370 if slot["page"] == 1 else page_width - 86
    elif slot["page"] == 3 and 230 < y < 640 and x < 100:
        width = 140
    elif slot["page"] == 5 and 320 < y < 650 and x < 100:
        width = 105
    elif slot["page"] == 19 and x < 100 and 180 < y < 670:
        width = 260
    elif slot["page"] == 18 and y in (631, 648):
        width = 145
    elif y > 740 and x < 100:
        width = page_width - 86 if size >= 16 else 325
    elif y == 27 and x < 100:
        width = 300
    else:
        width = max(slot["width"] * 1.45, 65)
    peers = [other["x"] for other in same_page
             if other is not slot and other["kind"] == "baseline"
             and other["x"] > x + 15 and abs(other["y"] - y) < .7]
    if peers:
        width = min(width, min(peers) - x - 6)
    width = min(width, page_width - 42 - x)
    return x, y - size * .36, max(width, 14), size * 1.78


def paragraph_box(slot: dict, same_page: list[dict]) -> tuple[float, float, float, float]:
    x, y, width, height = slot["x"], slot["y"], slot["width"], slot["height"]
    top = y + height
    peers = [other["height"] for other in same_page if other["kind"] == "paragraph"
             and abs(other["y"] + other["height"] - top) < .7
             and abs(other["x"] - x) > 5]
    if peers and width < 300:
        height = max(height, *peers)
        y = top - height
    return x, y, width, height


def build() -> Path:
    with tempfile.TemporaryDirectory(prefix="companion-fa-", dir="/private/tmp") as tmp:
        graphics = Path(tmp) / "graphics.pdf"
        manifest = capture_layout(graphics, Path(tmp) / "manifest.json")
        slots = manifest["slots"]
        translated = translations_for(slots)
        by_page = defaultdict(list)
        for slot in slots:
            by_page[slot["page"]].append(slot)
        reader = PdfReader(str(graphics))
        writer = PdfWriter()
        links = []
        with PangoFaOverlay() as overlay:
            for page_number, page in enumerate(reader.pages, start=1):
                for slot in by_page[page_number]:
                    value = translated[slot["id"]]
                    direction = "rtl" if re.search("[\u0600-\u06ff]", value) else "ltr"
                    if slot["kind"] == "paragraph":
                        x, y, width, height = paragraph_box(slot, by_page[page_number])
                        try:
                            placed = overlay.draw_markdown(
                                page, value, x=x, y=y, width=width, height=height,
                                font_size=slot["font_size"],
                                min_font_size=max(5.7, slot["font_size"] * .65),
                                color=slot["color"], align="left", valign="top",
                                bold=slot["font"] == "ArialB", direction=direction,
                            )
                        except TextDoesNotFit as exc:
                            raise TextDoesNotFit(f"{slot['id']}: {exc}; {value[:110]}") from exc
                    else:
                        x, y, width, height = baseline_box(slot, by_page[page_number],
                                                           float(page.mediabox.width))
                        mono = slot["font"] == "Courier" or HASH.fullmatch(value) is not None
                        keep_left_anchor = (
                            (slot["page"] == 3 and slot["x"] < 100 and 145 <= slot["y"] <= 640)
                            or (slot["page"] == 5 and slot["x"] < 100 and 320 < slot["y"] < 650)
                        )
                        text_align = "right" if keep_left_anchor and direction == "rtl" else "left"
                        try:
                            if mono:
                                placed = overlay.draw(
                                    page, f'<span font_family="Courier">{html.escape(value)}</span>',
                                    x=x, y=y, width=width, height=height,
                                    font_size=slot["font_size"],
                                    min_font_size=max(5.3, slot["font_size"] * .65),
                                    color=slot["color"], align=text_align, valign="middle",
                                    markup=True, direction="ltr",
                                )
                            else:
                                placed = overlay.draw_markdown(
                                    page, value, x=x, y=y, width=width, height=height,
                                    font_size=slot["font_size"],
                                    min_font_size=max(5.3, slot["font_size"] * .65),
                                    color=slot["color"], align=text_align, valign="middle",
                                    bold=slot["font"].endswith("B"), direction=direction,
                                )
                        except TextDoesNotFit as exc:
                            raise TextDoesNotFit(f"{slot['id']}: {exc}; {value[:110]}") from exc
                    urls = LINK.findall(slot["text"])
                    if len(urls) == 1:
                        links.append((page_number - 1, placed, urls[0]))
                writer.add_page(page)
        for page_number, placed, url in links:
            add_uri(writer, page_number, placed, url)
        writer.add_metadata({
            "/Title": "از پوش تا موقعیت مکانی | گزارش همراه برنامه‌های موبایل ایران | نسخهٔ ۲٫۱",
            "/Author": "Hamid Kashfi",
            "/Subject": "Persian translation of the 20-page companion report with identical vector graphics",
        })
        with OUTPUT.open("wb") as handle:
            writer.write(handle)
    if len(PdfReader(str(OUTPUT)).pages) != 20:
        raise RuntimeError("The Persian PDF did not retain all 20 master pages")
    return OUTPUT


if __name__ == "__main__":
    print(build())
