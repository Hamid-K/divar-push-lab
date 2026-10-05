#!/usr/bin/env python3
"""Place shaped Persian text over ReportLab vector pages without changing them.

ReportLab's Arabic shaping requires optional Python packages that are absent on
this host.  The installed Pango/Cairo renderer can instead make transparent,
vector PDF text fragments.  pypdf merges those fragments into a ReportLab page;
the original graphs remain vector artwork and the Persian text is selectable.

Coordinates passed to ``draw`` use PDF points and a lower-left origin.  Keep
this module independent of the companion report's content and geometry.
"""

from __future__ import annotations

import html
import os
import re
import subprocess
import tempfile
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Literal

from pypdf import PageObject, PdfReader, PdfWriter, Transformation
from pypdf.generic import ArrayObject, NumberObject


HERE = Path(__file__).resolve().parent
DEFAULT_FONT_DIR = HERE / "fonts"
_TOKEN = re.compile(
    r"\[([^\]]+)\]\((https?://[^)\s]+)\)|`([^`]+)`|\b[a-f0-9]{64}\b|\b\d+(?:\.\d+){2,4}(?:-[bw])?\b",
    re.I,
)
_BOLD = re.compile(r"\*\*(.+?)\*\*", re.S)
_HEX = re.compile(r"#?[0-9A-Fa-f]{6}\Z")


class TextDoesNotFit(ValueError):
    """The text remains taller than its box at the permitted minimum size."""


@dataclass(frozen=True)
class Placement:
    """Final location and typography of a text fragment in PDF coordinates."""

    x: float
    y: float
    width: float
    height: float
    font_size: float

    @property
    def rect(self) -> tuple[float, float, float, float]:
        return self.x, self.y, self.x + self.width, self.y + self.height


def _color(value: str) -> str:
    if not _HEX.fullmatch(value):
        raise ValueError(f"Expected a six-digit RGB hex color, got {value!r}")
    return value if value.startswith("#") else f"#{value}"


def markdown_to_pango_markup(
    value: str, *, teal: str = "#008F96", purple: str = "#6A5ABC"
) -> str:
    """Style report Markdown's links, code, hashes, versions, and bold spans.

    URLs are styled here; PDF annotations are added separately by the caller.
    Pango's ``allow_breaks=false`` keeps short LTR identifiers together while
    allowing long hashes to wrap rather than shrink an entire paragraph.
    """

    teal, purple = _color(teal), _color(purple)

    def tokens(part: str) -> str:
        out: list[str] = []
        pos = 0
        for match in _TOKEN.finditer(part):
            out.append(html.escape(part[pos : match.start()]))
            if match.group(1) is not None:  # Markdown link
                label = html.escape(match.group(1))
                out.append(
                    f'<span foreground="{teal}" underline="single">{label}</span>'
                )
            elif match.group(3) is not None:  # Code span
                token = match.group(3)
                attr = ' allow_breaks="false"' if len(token) <= 32 else ""
                out.append(
                    f'<span foreground="{purple}" font_family="Courier"{attr}>'
                    f'\u2066{html.escape(token)}\u2069</span>'
                )
            else:
                token = match.group()
                if len(token) == 64:
                    out.append(
                        f'<span foreground="{purple}" font_family="Courier">'
                        f'\u2066{token}\u2069</span>'
                    )
                else:
                    out.append(
                        f'<span foreground="{teal}" font_family="Arial" '
                        f'weight="bold" allow_breaks="false">'
                        f'\u2066{token}\u2069</span>'
                    )
            pos = match.end()
        out.append(html.escape(part[pos:]))
        return "".join(out)

    out: list[str] = []
    pos = 0
    for match in _BOLD.finditer(value):
        out.append(tokens(value[pos : match.start()]))
        out.append(f'<span weight="bold">{tokens(match.group(1))}</span>')
        pos = match.end()
    out.append(tokens(value[pos:]))
    return "".join(out)


class PangoFaOverlay:
    """Render and merge transparent RTL text fragments onto pypdf pages.

    This object caches identical fragments and owns a temporary Fontconfig
    setup.  Use it as a context manager or call ``close`` when done.
    """

    def __init__(self, font_dir: Path | str = DEFAULT_FONT_DIR) -> None:
        self.font_dir = Path(font_dir).resolve()
        for name in ("Vazirmatn-Regular.ttf", "Vazirmatn-Bold.ttf"):
            if not (self.font_dir / name).is_file():
                raise FileNotFoundError(self.font_dir / name)
        self._temporary = tempfile.TemporaryDirectory(prefix="pango-fa-", dir="/private/tmp")
        self._work = Path(self._temporary.name)
        self._config = self._work / "fonts.conf"
        system_config = next(
            (p for p in (Path("/opt/homebrew/etc/fonts/fonts.conf"),
                         Path("/usr/local/etc/fonts/fonts.conf")) if p.is_file()),
            None,
        )
        if system_config is None:
            raise FileNotFoundError("Fontconfig system fonts.conf was not found")
        self._config.write_text(
            '<?xml version="1.0"?>\n'
            '<!DOCTYPE fontconfig SYSTEM "fonts.dtd">\n'
            '<fontconfig>\n'
            f'  <include ignore_missing="yes">{html.escape(str(system_config))}</include>\n'
            f'  <dir>{html.escape(str(self.font_dir))}</dir>\n'
            f'  <cachedir>{html.escape(str(self._work / "font-cache"))}</cachedir>\n'
            '</fontconfig>\n',
            encoding="utf-8",
        )
        self._env = os.environ.copy()
        self._env.update(
            FONTCONFIG_FILE=str(self._config),
            XDG_CACHE_HOME=str(self._work),
            PANGOCAIRO_BACKEND="fc",
        )
        self._cache: dict[tuple, tuple[bytes, float, float]] = {}

    def close(self) -> None:
        self._temporary.cleanup()

    def __enter__(self) -> "PangoFaOverlay":
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()

    def _render(
        self,
        value: str,
        *,
        width: float | None,
        font_size: float,
        color: str,
        align: Literal["left", "center", "right"],
        bold: bool,
        markup: bool,
        direction: Literal["rtl", "ltr"],
        line_spacing: float,
    ) -> tuple[bytes, float, float]:
        key = (value, None if width is None else round(width, 2),
               round(font_size, 2), color, align, bold,
               markup, direction, round(line_spacing, 2))
        if key in self._cache:
            return self._cache[key]
        output = self._work / f"fragment-{len(self._cache):05d}.pdf"
        command = [
            "pango-view", "-q", "--no-auto-dir",
            f"--font=Vazirmatn {'Bold' if bold else 'Regular'} {font_size:.2f}",
            f"--foreground={color}", "--background=transparent", "--margin=0",
            f"--align={align}",
            f"--line-spacing={line_spacing:.2f}",
            f"--text={value}", "-o", str(output),
        ]
        if width is not None:
            command.insert(-4, f"--width={round(width)}")
            command.insert(-4, "--wrap=word-char")
        if direction == "rtl":
            command.insert(2, "--rtl")
        if markup:
            command.insert(2, "--markup")
        try:
            subprocess.run(
                command, check=True, env=self._env, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, timeout=30,
            )
        except subprocess.CalledProcessError as exc:
            raise RuntimeError(
                f"Pango could not render Persian text: {exc.stderr.decode('utf-8', 'replace')}"
            ) from exc
        pdf = output.read_bytes()
        output.unlink()
        box = PdfReader(BytesIO(pdf)).pages[0].mediabox
        rendered = pdf, float(box.width), float(box.height)
        self._cache[key] = rendered
        return rendered

    def draw(
        self,
        page: PageObject,
        value: str,
        *,
        x: float,
        y: float,
        width: float,
        height: float,
        font_size: float = 10,
        min_font_size: float | None = None,
        color: str = "#213449",
        align: Literal["left", "center", "right"] = "right",
        valign: Literal["bottom", "middle", "top"] = "middle",
        bold: bool = False,
        markup: bool = False,
        direction: Literal["rtl", "ltr"] = "rtl",
        line_spacing: float = 0.75,
        fit_bleed: float = 2.5,
    ) -> Placement:
        """Fit text to a box, draw it, and return its actual annotation rectangle.

        A wrapped block is reduced in 0.5-point steps until it fits.  Pango's
        single-line ascender/descender box exceeds ReportLab's baseline slot
        by about two points, so ``fit_bleed`` permits that small difference.
        If text still does not fit at ``min_font_size``, raise
        ``TextDoesNotFit`` so report code can enlarge or rewrite the box.
        """

        if width <= 0 or height <= 0 or font_size <= 0:
            raise ValueError("width, height, and font_size must be positive")
        if align not in ("left", "center", "right"):
            raise ValueError(f"Invalid alignment: {align}")
        if valign not in ("bottom", "middle", "top"):
            raise ValueError(f"Invalid vertical alignment: {valign}")
        if direction not in ("rtl", "ltr"):
            raise ValueError(f"Invalid text direction: {direction}")
        if line_spacing <= 0:
            raise ValueError("line_spacing must be positive")
        if fit_bleed < 0:
            raise ValueError("fit_bleed must be nonnegative")
        color = _color(color)
        if not value:
            return Placement(x, y, 0, 0, font_size)
        lower = min_font_size if min_font_size is not None else max(6.2, font_size * 0.72)
        if lower <= 0 or lower > font_size:
            raise ValueError("min_font_size must be positive and <= font_size")
        size = font_size
        while True:
            pdf, rendered_width, rendered_height = self._render(
                value, width=width, font_size=size, color=color, align=align,
                bold=bold, markup=markup, direction=direction,
                line_spacing=line_spacing,
            )
            if rendered_height <= height + fit_bleed:
                break
            if size <= lower + 0.01:
                raise TextDoesNotFit(
                    f"Text needs {rendered_height:.1f} pt in a {height:.1f} pt "
                    f"box at minimum font size {lower:.1f} pt"
                )
            size = max(lower, size - 0.5)
        placed_y = (
            y if valign == "bottom" else
            y + (height - rendered_height) / 2 if valign == "middle" else
            y + height - rendered_height
        )
        overlay = PdfReader(BytesIO(pdf)).pages[0]
        page.merge_transformed_page(
            overlay, Transformation().translate(x, placed_y)
        )
        return Placement(x, placed_y, rendered_width, rendered_height, size)

    def draw_markdown(self, page: PageObject, value: str, **kwargs: object) -> Placement:
        """Draw text using the English report's teal/purple inline token palette."""

        return self.draw(page, markdown_to_pango_markup(value), markup=True, **kwargs)

    def draw_baseline(
        self,
        page: PageObject,
        value: str,
        *,
        x: float,
        y: float,
        font_size: float = 10,
        max_width: float | None = None,
        min_font_size: float | None = None,
        color: str = "#213449",
        align: Literal["left", "center", "right"] = "left",
        bold: bool = False,
        markup: bool = False,
        direction: Literal["rtl", "ltr"] = "rtl",
        baseline_offset: float = 0.20,
    ) -> Placement:
        """Replace a ReportLab ``drawString`` baseline without forced wrapping.

        ``x`` is the original left/center/right anchor and ``y`` its baseline.
        Pango adds ascender/descender space around the glyphs, so placement is
        adjusted by ``baseline_offset`` times the measured fragment height.
        ``max_width`` optionally shrinks a longer translation to available
        horizontal space; no source-language text width should be used for it.
        """

        if not value:
            return Placement(x, y, 0, 0, font_size)
        if font_size <= 0 or (max_width is not None and max_width <= 0):
            raise ValueError("font_size and max_width must be positive")
        if not 0 <= baseline_offset <= 1:
            raise ValueError("baseline_offset must be between 0 and 1")
        color = _color(color)
        lower = min_font_size if min_font_size is not None else max(6.2, font_size * 0.72)
        if lower <= 0 or lower > font_size:
            raise ValueError("min_font_size must be positive and <= font_size")
        size = font_size
        while True:
            pdf, rendered_width, rendered_height = self._render(
                value, width=None, font_size=size, color=color, align=align,
                bold=bold, markup=markup, direction=direction,
                line_spacing=0.75,
            )
            if max_width is None or rendered_width <= max_width + 0.1:
                break
            if size <= lower + 0.01:
                raise TextDoesNotFit(
                    f"Text needs {rendered_width:.1f} pt in a {max_width:.1f} pt "
                    f"baseline slot at minimum font size {lower:.1f} pt"
                )
            size = max(lower, size - 0.5)
        placed_x = (
            x if align == "left" else
            x - rendered_width / 2 if align == "center" else
            x - rendered_width
        )
        placed_y = y - rendered_height * baseline_offset
        overlay = PdfReader(BytesIO(pdf)).pages[0]
        page.merge_transformed_page(
            overlay, Transformation().translate(placed_x, placed_y)
        )
        return Placement(placed_x, placed_y, rendered_width, rendered_height, size)

    def draw_baseline_markdown(
        self, page: PageObject, value: str, **kwargs: object
    ) -> Placement:
        """Place a baseline label with the report's inline token palette."""

        return self.draw_baseline(
            page, markdown_to_pango_markup(value), markup=True, **kwargs
        )


def add_uri(writer: PdfWriter, page_number: int, placement: Placement, url: str) -> None:
    """Make an entire placed text fragment a clickable link."""

    writer.add_uri(
        page_number, url, rect=placement.rect,
        border=ArrayObject([NumberObject(0), NumberObject(0), NumberObject(0)]),
    )


def _self_test() -> None:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas

    out = Path("/private/tmp/pango-fa-overlay-selftest.pdf")
    base = Path("/private/tmp/pango-fa-overlay-base.pdf")
    c = canvas.Canvas(str(base), pagesize=A4)
    c.setFillColorRGB(0.07, 0.15, 0.23)
    c.rect(0, 0, *A4, stroke=0, fill=1)
    c.setFillColorRGB(0.91, 0.42, 0.34)
    c.roundRect(60, 600, 475, 110, 12, stroke=0, fill=1)
    c.save()
    page = PdfReader(str(base)).pages[0]
    with PangoFaOverlay() as overlay:
        title = overlay.draw_markdown(
            page, "گزارش فنی **Divar** و `ReportDeserializer` در نسخه 11.8.1",
            x=80, y=635, width=430, height=55, font_size=17, bold=True,
            color="#FFFFFF", align="right", valign="middle",
        )
        body = overlay.draw_markdown(
            page, "مسیر دریافت فرمان در Neshan 12.5.3 به `/logger/uploadLogFile` "
                  "می‌رسد؛ اما اجرای کد در این نمونه ثابت نشده است.",
            x=80, y=510, width=430, height=75, font_size=12,
            color="#FFFFFF", align="right", valign="top",
        )
        overlay.draw_baseline_markdown(
            page, "مرز تغییر در نسخه 11.8.1",
            x=510, y=460, font_size=12, max_width=430,
            color="#47C5B5", align="right",
        )
    writer = PdfWriter()
    writer.add_page(page)
    add_uri(writer, 0, title, "https://example.com/report")
    with out.open("wb") as handle:
        writer.write(handle)
    check = PdfReader(str(out)).pages[0]
    assert check.get("/Annots")
    assert body.font_size > 0
    print(out)


if __name__ == "__main__":
    _self_test()
