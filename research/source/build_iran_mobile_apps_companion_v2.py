#!/usr/bin/env python3
"""Build the independent Iranian mobile-app companion report, edition 2.0.

The narrative is deliberately bounded by the acquired APKs. The adjacent CSV is
the normalized, exact-file inventory used for the coverage graphic. No server
telemetry, historical payload, or company authorization is inferred from it.
"""

from __future__ import annotations

import csv
import html
import math
import re
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph


ROOT = Path(__file__).resolve().parent.parent
PDF = ROOT / "Iran_mobile_apps_companion_v2.0_2026-10-05.pdf"
INVENTORY = list(csv.DictReader((ROOT / "Iran_mobile_apps_sample_inventory_v2.0.csv").open(newline="")))
assert len(INVENTORY) == 103 and len({r["sha256"] for r in INVENTORY}) == 103
W, H = A4
M = 43
BW = W - 2 * M

FONT_DIR = Path("/System/Library/Fonts/Supplemental")
pdfmetrics.registerFont(TTFont("ArialR", str(FONT_DIR / "Arial.ttf")))
pdfmetrics.registerFont(TTFont("ArialB", str(FONT_DIR / "Arial Bold.ttf")))
pdfmetrics.registerFont(TTFont("ArialI", str(FONT_DIR / "Arial Italic.ttf")))
pdfmetrics.registerFontFamily("ArialR", normal="ArialR", bold="ArialB", italic="ArialI", boldItalic="ArialB")
pdfmetrics.registerFont(TTFont("AvenirR", "/System/Library/Fonts/Avenir Next.ttc", subfontIndex=7))
pdfmetrics.registerFont(TTFont("AvenirB", "/System/Library/Fonts/Avenir Next.ttc", subfontIndex=0))

C = {
    "navy": colors.HexColor("#13263B"),
    "navy2": colors.HexColor("#1C3B55"),
    "teal": colors.HexColor("#008F96"),
    "mint": colors.HexColor("#47C5B5"),
    "coral": colors.HexColor("#E66B57"),
    "amber": colors.HexColor("#C88A1E"),
    "purple": colors.HexColor("#6A5ABC"),
    "ink": colors.HexColor("#213449"),
    "muted": colors.HexColor("#617487"),
    "pale": colors.HexColor("#F3F7F8"),
    "pale2": colors.HexColor("#EAF2F3"),
    "line": colors.HexColor("#D5E2E7"),
    "green": colors.HexColor("#288365"),
    "white": colors.white,
    "charcoal": colors.HexColor("#161719"),
    "wine": colors.HexColor("#411E24"),
    "rose": colors.HexColor("#AF4760"),
}


def hx(name: str) -> str:
    return C[name].hexval().replace("0x", "#")


TOKEN = re.compile(
    r"\[([^\]]+)\]\((https?://[^)\s]+)\)|`([^`]+)`|\b[a-f0-9]{64}\b|\b\d+(?:\.\d+){2,4}(?:-[bw])?\b",
    re.I,
)


def rich(value: str) -> str:
    """Link sources and color versions/hashes in prose, not ordinary numbers."""
    parts: list[str] = []
    pos = 0
    for match in TOKEN.finditer(value):
        parts.append(html.escape(value[pos:match.start()]))
        if match.group(1) is not None:
            label = html.escape(match.group(1))
            url = html.escape(match.group(2), quote=True)
            parts.append(f'<link href="{url}" color="{hx("teal")}"><u>{label}</u></link>')
        elif match.group(3) is not None:
            parts.append(f'<font face="Courier" color="{hx("purple")}">{html.escape(match.group(3))}</font>')
        else:
            token = match.group()
            tone = "purple" if len(token) == 64 else "teal"
            font = "Courier" if tone == "purple" else "ArialB"
            parts.append(f'<font face="{font}" color="{hx(tone)}">{html.escape(token)}</font>')
        pos = match.end()
    parts.append(html.escape(value[pos:]))
    return re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", "".join(parts))


def para_obj(value: str, width: float, *, size: float = 9.1, leading: float = 13.3,
             color: str = "ink", bold: bool = False, formatted: bool = True) -> tuple[Paragraph, float]:
    style = ParagraphStyle(
        "body", fontName="ArialB" if bold else "ArialR", fontSize=size,
        leading=leading, textColor=C[color], allowWidows=0, allowOrphans=0,
        splitLongWords=1,
    )
    p = Paragraph(rich(value) if formatted else html.escape(value), style)
    _, height = p.wrap(width, H)
    return p, height


def txt(c: canvas.Canvas, value: str, x: float, y: float, size: float = 9,
        tone: str = "ink", font: str = "ArialR") -> None:
    c.setFillColor(C[tone]); c.setFont(font, size); c.drawString(x, y, value)


def right(c: canvas.Canvas, value: str, x: float, y: float, size: float = 9,
          tone: str = "ink", font: str = "ArialR") -> None:
    c.setFillColor(C[tone]); c.setFont(font, size); c.drawRightString(x, y, value)


def line(c: canvas.Canvas, x1: float, y1: float, x2: float, y2: float,
         tone: str = "line", width: float = 1, dash: tuple[int, ...] | None = None) -> None:
    c.setStrokeColor(C[tone]); c.setLineWidth(width); c.setDash(dash or [])
    c.line(x1, y1, x2, y2); c.setDash([])


def box(c: canvas.Canvas, x: float, y: float, w: float, h: float, tone: str = "pale",
        radius: float = 10, stroke: str | None = None) -> None:
    c.setFillColor(C[tone]); c.setStrokeColor(C[stroke or tone])
    c.roundRect(x, y, w, h, radius, fill=1, stroke=int(stroke is not None))


def arrow(c: canvas.Canvas, x1: float, y1: float, x2: float, y2: float,
          tone: str = "teal", dashed: bool = False, dotted: bool = False,
          width: float = 1.8) -> None:
    dash = (2, 4) if dotted else (7, 4) if dashed else None
    line(c, x1, y1, x2, y2, tone, width, dash)
    a = math.atan2(y2-y1, x2-x1)
    d = 6
    p = c.beginPath(); p.moveTo(x2, y2)
    p.lineTo(x2-d*math.cos(a-0.5), y2-d*math.sin(a-0.5))
    p.lineTo(x2-d*math.cos(a+0.5), y2-d*math.sin(a+0.5)); p.close()
    c.setFillColor(C[tone]); c.drawPath(p, fill=1, stroke=0)


class Report:
    def __init__(self):
        self.c = canvas.Canvas(str(PDF), pagesize=A4, pageCompression=1)
        self.c.setTitle("From push to position | Iranian mobile-app command and location paths | v2.0")
        self.c.setAuthor("Hamid Kashfi")
        self.c.setSubject("Bounded signed-APK analysis of Balad, Neshan, Snapp and Tapsi")
        self.n = 0
        self.label = ""
        self.y = H

    def cover(self) -> None:
        c = self.c
        self.n = 1
        c.setFillColor(C["charcoal"]); c.rect(0, 0, W, H, fill=1, stroke=0)
        # Stacked translucent city blocks and the network path echo the Divar
        # case-file cover without reusing its handset illustration.
        c.setFillColor(C["wine"])
        c.circle(478, 440, 275, fill=1, stroke=0)
        for i in range(7):
            for j in range(6):
                x = 285 + i*46 + (j % 2)*10
                y = 196 + j*52
                c.setStrokeColor(colors.HexColor("#5D3037")); c.setLineWidth(0.7)
                c.roundRect(x, y, 31, 29, 3, fill=0, stroke=1)
        c.setStrokeColor(colors.HexColor("#8B4048")); c.setLineWidth(1.1)
        for r in (93, 145, 205, 270): c.circle(453, 473, r, fill=0, stroke=1)
        # Three observed routes, with an intentionally interrupted dotted join.
        paths = [((413, 597), (514, 526), "teal"), ((465, 450), (535, 389), "coral"),
                 ((363, 294), (480, 347), "purple")]
        for (x1,y1),(x2,y2),tone in paths:
            c.setFillColor(C[tone]); c.circle(x1,y1,5,fill=1,stroke=0)
            arrow(c,x1,y1,x2,y2,tone,width=2.2)
            c.circle(x2,y2,7,fill=1,stroke=0)
        line(c, 482, 342, 545, 278, "muted", 1.5, (2,5))
        c.setFillColor(C["coral"]); c.rect(0, 0, 5, H, fill=1, stroke=0)
        txt(c, "M O B I L E   T H R E A T   R E S E A R C H", 45, 789, 8.0, "white", "AvenirB")
        right(c, "CASE FILE / 2026", W-45, 789, 8.0, "muted", "AvenirR")
        line(c, 45, 778, 74, 778, "coral", 2.6)
        txt(c, "From push", 45, 674, 45, "white", "AvenirR")
        txt(c, "to position", 45, 621, 46, "white", "AvenirB")
        line(c, 45, 592, 234, 592, "coral", 1.8)
        p, h = para_obj(
            "Beyond Divar: command and location paths in Balad, Neshan, Snapp and Tapsi; "
            "what changed in sampled Android APKs, and what the files cannot tell us.",
            330, size=12.1, leading=17.4, color="white",
        ); p.drawOn(c, 45, 574-h)
        box(c, 45, 259, 500, 101, "navy", 13)
        for i,(head,detail,tone) in enumerate([
            ("19 FEB", "Neshan VT submission", "teal"),
            ("28 FEB", "Iran war begins", "coral"),
            ("10 JUN", "Balad uploader observed", "purple"),
        ]):
            x=60+i*163
            if i: line(c,x-12,275,x-12,342,"muted",0.7)
            txt(c,head,x,321,16,tone,"AvenirB")
            txt(c,detail,x,297,7.9,"white","AvenirR")
            txt(c,"2026",x,278,7.5,"muted","AvenirR")
        p,h=para_obj("The Neshan and Balad dates are exact-file VT first submissions; the Neshan archive "
                     "lists the same build on 18 February. Dates do not establish rollout, device use or a shared operator.",
                     500,size=8.1,leading=11.4,color="white")
        p.drawOn(c,45,231-h)
        line(c,45,63,W-45,63,"muted",0.6)
        txt(c,"HAMID KASHFI",45,43,9.2,"white","AvenirB")
        txt(c,"LLM-generated report",45,29,7.8,"muted","AvenirR")
        right(c,"5 OCTOBER 2026",W-45,43,8.2,"white","AvenirB")
        right(c,"VERSION 2.0",W-45,29,8.0,"coral","AvenirB")

    def page(self, label: str, *, title: str | None = None, deck: str = "",
             continued: bool = False) -> None:
        if self.n: self.c.showPage()
        self.n += 1; self.label=label
        c=self.c
        c.setFillColor(C["white"]); c.rect(0,0,W,H,fill=1,stroke=0)
        c.setFillColor(C["navy"]); c.rect(0,H-9,W,9,fill=1,stroke=0)
        if title:
            txt(c,label.upper(),M,H-53,8.1,"teal","ArialB")
            txt(c,title,M,H-90,22.5,"navy","ArialB")
            line(c,M,H-107,W-M,H-107)
            self.y=H-126
            if deck: self.p(deck,size=9.1,leading=12.9,tone="muted",after=10)
        else:
            txt(c,label.upper()+(" / CONTINUED" if continued else ""),M,H-53,8.1,"teal","ArialB")
            line(c,M,H-65,W-M,H-65)
            self.y=H-83
        line(c,M,45,W-M,45)
        txt(c,"IRANIAN MOBILE APPS / COMPANION REPORT",M,27,7.2,"muted","ArialB")
        right(c,f"{self.n:02d}",W-M,27,8.2,"navy","ArialB")

    def ensure(self, height: float) -> None:
        if self.y-height<67:
            self.page(self.label,continued=True)

    def p(self, value: str, *, size: float = 9.1, leading: float = 13.3,
          tone: str = "ink", after: float = 8, width: float = BW,
          indent: float = 0, bold: bool = False, formatted: bool = True) -> None:
        p,h=para_obj(value,width-indent,size=size,leading=leading,color=tone,bold=bold,formatted=formatted)
        self.ensure(h+after)
        p.drawOn(self.c,M+indent,self.y-h)
        self.y-=h+after

    def h2(self, value: str, *, tone: str = "teal") -> None:
        self.ensure(31)
        txt(self.c,value,M,self.y-10,11,tone,"ArialB")
        self.y-=24

    def bullet(self, value: str, *, tone: str = "teal", after: float = 6,
               size: float = 8.8, leading: float = 12.5) -> None:
        p,h=para_obj(value,BW-19,size=size,leading=leading)
        self.ensure(h+after)
        self.c.setFillColor(C[tone]); self.c.circle(M+5,self.y-6,2.2,fill=1,stroke=0)
        p.drawOn(self.c,M+18,self.y-h)
        self.y-=h+after

    def callout(self, title: str, body: str, *, tone: str = "teal", fill: str = "pale2",
                size: float = 8.4) -> None:
        p,h=para_obj(body,BW-28,size=size,leading=12.1)
        height=h+42
        self.ensure(height+10)
        y=self.y-height
        box(self.c,M,y,BW,height,fill,9)
        self.c.setFillColor(C[tone]); self.c.rect(M,y,4,height,fill=1,stroke=0)
        txt(self.c,title.upper(),M+14,y+height-20,7.4,tone,"ArialB")
        p.drawOn(self.c,M+14,y+13)
        self.y=y-11

    def table(self, headers: list[str], rows: list[list[str]], widths: list[float],
              *, font: float = 7.6, leading: float = 10.3,
              pad: float = 6, min_row: float = 22) -> None:
        assert abs(sum(widths)-BW)<0.01
        self.ensure(28)
        self._table_head(headers,widths,pad)
        for i,row in enumerate(rows):
            cells=[]; height=min_row
            for value,w in zip(row,widths):
                p,h=para_obj(value,w-2*pad,size=font,leading=leading)
                cells.append((p,h))
                height=max(height,h+2*pad)
            if self.y-height<67:
                self.page(self.label,continued=True)
                self._table_head(headers,widths,pad)
            y=self.y-height
            self.c.setFillColor(C["pale"] if i%2==0 else C["white"])
            self.c.rect(M,y,BW,height,fill=1,stroke=0)
            x=M
            for (p,h),w in zip(cells,widths):
                p.drawOn(self.c,x+pad,self.y-pad-h); x+=w
            line(self.c,M,y,W-M,y,"line",0.45)
            self.y=y
        self.y-=11

    def _table_head(self, headers: list[str], widths: list[float], pad: float) -> None:
        box(self.c,M,self.y-25,BW,25,"navy",4)
        x=M
        for value,w in zip(headers,widths):
            txt(self.c,value.upper(),x+pad,self.y-16,6.9,"white","ArialB")
            x+=w
        self.y-=25

    def code(self, title: str, lines: list[str], note: str = "", *, tone: str = "teal",
             size: float = 7.35) -> None:
        line_h=10.0
        p,h=para_obj(note,BW-26,size=7.2,leading=9.8,color="muted") if note else (None,0)
        height=37+len(lines)*line_h+(h+8 if p else 0)
        self.ensure(height+10)
        y=self.y-height
        box(self.c,M,y,BW,height,"pale",8)
        self.c.setFillColor(C[tone]); self.c.rect(M,y+height-4,BW,4,fill=1,stroke=0)
        txt(self.c,title.upper(),M+13,y+height-21,7.3,tone,"ArialB")
        yy=y+height-37
        for item in lines:
            if pdfmetrics.stringWidth(item,"Courier",size)>BW-26:
                raise ValueError("Code line too long: "+item)
            txt(self.c,item,M+13,yy,size,"ink","Courier")
            yy-=line_h
        if p: p.drawOn(self.c,M+13,y+9)
        self.y=y-11

    def dual_code(self, left_title: str, left: list[str], right_title: str,
                  right: list[str], note: str = "") -> None:
        cw=(BW-12)/2; n=max(len(left),len(right)); height=36+n*10+10
        self.ensure(height+34)
        y=self.y-height
        for i,(title,items,tone) in enumerate([(left_title,left,"green"),(right_title,right,"coral")]):
            x=M+i*(cw+12)
            box(self.c,x,y,cw,height,"pale" if i==0 else "pale2",8)
            self.c.setFillColor(C[tone]);self.c.rect(x,y+height-4,cw,4,fill=1,stroke=0)
            txt(self.c,title.upper(),x+10,y+height-20,7.3,tone,"ArialB")
            yy=y+height-37
            for item in items:
                if pdfmetrics.stringWidth(item,"Courier",6.7)>cw-20:
                    raise ValueError("Side by side line too long: "+item)
                txt(self.c,item,x+10,yy,6.7,"ink","Courier")
                yy-=10
        self.y=y-11
        if note: self.p(note,size=7.6,leading=10.5,tone="muted",after=11)

    def save(self) -> None:
        self.c.save()


def node(c: canvas.Canvas, x: float, y: float, w: float, h: float,
         heading: str, detail: str, *, tone: str = "teal") -> None:
    box(c,x,y,w,h,"pale",8)
    c.setFillColor(C[tone]);c.rect(x,y+h-4,w,4,fill=1,stroke=0)
    txt(c,heading,x+9,y+h-20,7.0,tone,"ArialB")
    p,ph=para_obj(detail,w-18,size=7.15,leading=9.6)
    p.drawOn(c,x+9,y+h-28-ph)


def flow(c: canvas.Canvas, y: float, title: str, nodes: list[tuple[str,str]],
         *, tone: str = "teal", dashed: bool = False) -> None:
    txt(c,title.upper(),M,y+77,7.5,tone,"ArialB")
    n=len(nodes); gap=18; width=(BW-(n-1)*gap)/n
    for i,(heading,detail) in enumerate(nodes):
        x=M+i*(width+gap)
        node(c,x,y,width,66,heading,detail,tone=tone)
        if i+1<n: arrow(c,x+width+2,y+33,x+width+gap-2,y+33,tone,dashed=dashed,width=1.4)


def caption(r: Report, value: str) -> None:
    r.p(value,size=7.3,leading=10.1,tone="muted",after=8)


def source_hash(c: canvas.Canvas, x: float, y: float, label: str,
                sha: str, note: str) -> None:
    box(c,x,y,BW,44,"pale",7)
    txt(c,label,x+10,y+29,8.0,"navy","ArialB")
    right(c,note,x+BW-10,y+29,7.1,"muted","ArialR")
    txt(c,sha,x+10,y+10,6.9,"purple","Courier")
    c.linkURL("https://www.virustotal.com/gui/file/"+sha,(x,y,x+BW,y+44),relative=0)


def assessment(r: Report) -> None:
    r.page("assessment",title="What the four-app review found",
           deck="A companion to the Divar case file, based on acquired APKs rather than a claim about every release or device.")
    r.p("After Ramin Farajpour Cami's [Divar finding](https://gist.github.com/raminfp/a548a2af86108eb40b8bffc5c8f07aaa) "
        "and [my subsequent disclosure](https://x.com/hkashfi/status/2106147963332633025), I asked a narrower question: "
        "did contemporaneous Balad, Neshan, Snapp or Tapsi updates carry a comparable inserted delivery route, "
        "or add a sensitive location path that could matter in a targeting operation? The [Divar technical report]"
        "(https://github.com/Hamid-K/divar-push-lab/blob/main/research/Divar_backdoor_technical_analysis_v2.8_2026-10-05.pdf) "
        "now covers 282 exact signed files, including a push-to-stage route first observed in 2023 and a later HTTP-header entry. "
        "This companion examines **103 exact APKs across seven package tracks** for other app behavior. [01-03]")
    r.p("I found **no Divar-equivalent notification-to-loader chain** in the inspected Balad, Neshan, Snapp or Tapsi samples. "
        "The most important distinct finding is in Neshan: a new server-pull route can feed an older diagnostic/file-upload command "
        "without showing a notification. A separate native network path later accepts GPS-derived input; its plaintext destination "
        "and historical traffic remain unresolved. [07-09]")
    r.p("Balad, Snapp driver and Tapsi have location/radio request paths with plausible positioning or service uses. "
        "Their sampled code establishes what each client could send under its gates, not that any company enabled the path for "
        "particular users or that an attacker received the data. I recovered no cross-app device join, shared operator, hostile "
        "command, upload receipt or malicious patch. Signing continuity does not settle authorization. [07,10-11]")
    r.h2("What the APKs establish")
    r.table(["Track","Established in sampled code","Still unknown"],[
        ["Balad / 32", "In the 26-file Bazaar track, remote-gated radio/location upload appears by 4.81.1; 4.84.0 broadens source choice. Six Play APKs form a separate package/signing track.",
         "Historical AppMeta settings, wire fields, recipients and receipts."],
        ["Neshan / 21", "14.8.10 adds pull into PUSH_LOGGER dispatcher; later native code can POST observation-derived data.",
         "Pull commands, upload logs, native host/path, effective config and traffic."],
        ["Snapp / 17", "Driver 5.17.0 adds radio collection POST; passenger 8.39.0 adds notification polling classes.",
         "AB settings, dynamic destination, receipt logs and passenger activation."],
        ["Tapsi / 33", "Geolocation POST is callable; one driver 8.8.0 channel contains a patch updater.",
         "Jan-May APKs, feature settings, requests and patch delivery."],
    ],[93,220,BW-313],font=7.5,leading=10.2)
    r.callout("Interpretation", "These findings describe **capability and sampled version deltas**. "
              "They do not establish malicious collection, joint targeting, operator identity or use during the war. "
              "A negative Divar-pattern scan is a narrow result, not whole-app clearance.")


def sample_matrix(r: Report) -> None:
    r.page("sample coverage",title="The 103-file boundary",
           deck="Each tile below is one acquired exact APK. Color identifies a package track; it is not a benign or malicious verdict.")
    groups=defaultdict(list)
    for row in INVENTORY: groups[row["track"]].append(row)
    order=[("Balad Bazaar","teal"),("Balad Play","mint"),("Neshan","coral"),
           ("Snapp passenger","navy2"),("Snapp driver","amber"),
           ("Tapsi passenger","purple"),("Tapsi driver","green")]
    y=620
    for name,tone in order:
        rows=groups[name]
        txt(r.c,name.upper(),M,y+8,7.4,"navy","ArialB")
        x=M+142
        for row in rows:
            strong=bool(row["observation_date_utc"]) and row["date_basis"]=="VT first submission"
            r.c.setFillColor(C[tone] if strong else C["white"])
            r.c.setStrokeColor(C[tone]);r.c.setLineWidth(0.7)
            r.c.roundRect(x,y,9,15,2,fill=1,stroke=1)
            x+=11.4
        right(r.c,str(len(rows)),W-M,y+5,9,"navy","ArialB")
        line(r.c,M,y-14,W-M,y-14,"line",0.7)
        y-=63
    txt(r.c,"FILLED  /  VT FIRST-SUBMISSION DATE ON RECORD",M,166,7.2,"teal","ArialB")
    txt(r.c,"OUTLINE  /  ARCHIVE DATE OR NO EXACT-FILE VT DATE",M,149,7.2,"muted","ArialB")
    r.y=132
    r.p("The normalized [103-file inventory](https://github.com/Hamid-K/divar-push-lab/blob/main/research/Iran_mobile_apps_sample_inventory_v2.0.csv) "
        "retains SHA-256, package, versionCode, signer fingerprint and date basis for every tile, with archive "
        "listing/upload dates kept separately when available. "
        "One signer can group a lineage; it cannot tell who approved its code.",size=8.0,leading=11.3)
    # A second page uses the same chronology language as the Divar report but
    # makes the historical gaps explicit rather than giving a false cadence.
    r.page("sample coverage",title="Where the sample runs stop",
           deck="Version deltas are bounded by the acquired files on either side, never by presumed release cadence.")
    r.table(["Track","Acquired span","Critical gap or caveat"],[
        ["Balad / Bazaar", "26 APKs; 4.76.3-4.84.1", "4.78.0/4.78.1, 4.80.0 and 4.81.0 bytes missing; a transient path cannot be excluded."],
        ["Balad / Play", "6 APKs; 4.77.0-4.83.2", "Separate package/signer; 4.79.0 to 4.82.1 is a wider code gap."],
        ["Neshan", "21 APKs; 14.7.9-14.13.0.6", "Ten archived bases plus eleven VT same-version variants; March-May availability unproved."],
        ["Snapp / passenger", "12 APKs; 8.37.0-8.42.2", "8.39.0 version archives straddle 28 Feb; preserved hash is tied to the 2 Mar listing."],
        ["Snapp / driver", "5 APKs; 5.13.0-5.18.0", "5.14.0 and 5.16.0 missing; two distinct 5.17.0 install-permission variants."],
        ["Tapsi / passenger", "20 APKs; 7.3.0-8.4.0", "First submissions 12 Jun-30 Sep; January-May exact-package bytes absent."],
        ["Tapsi / driver", "13 APKs; 7.13.6-8.9.0", "First submissions 6 Jul-22 Sep; 8.8.0 has two distribution flavors."],
    ],[116,146,BW-262],font=7.55,leading=10.4)
    r.h2("How negative checks were used")
    r.p("The review scanned for the exact Divar class, the four-field trigger and calibrated relay/worker signatures, "
        "then followed the app-specific push, polling, location, updater and native call paths above. A renamed loader, "
        "server-only behavior, native-only implementation or unsampled release can escape those checks. "
        "The four apps therefore receive **bounded sampled-file conclusions**, not an all-version clean label.")
    r.callout("Date rule", "VirusTotal first submission dates the first known VT appearance of **one hash**. "
              "Archive dates usually describe a version listing or upload. Neither identifies the build date, rollout cohort, "
              "installation date, live configuration or historical use.",tone="amber",fill="pale")


def chronology(r: Report) -> None:
    r.page("evidence chronology",title="Code observations against the war",
           deck="Solid markers are exact-file VT first submissions. The hollow Snapp marker is an archive listing, not an exact-hash VT date.")
    c=r.c
    x0,x1=150,W-M
    start,end=date(2026,1,1),date(2026,9,30)
    def xx(d:date)->float:return x0+(d-start).days/(end-start).days*(x1-x0)
    # Phase bands are public chronology, not military-state claims per day.
    for a,b,tone in [(date(2026,2,28),date(2026,4,7),"pale2"),
                     (date(2026,4,7),date(2026,6,15),"pale"),
                     (date(2026,6,15),end,"pale2")]:
        c.setFillColor(C[tone]);c.rect(xx(a),280,xx(b)-xx(a),400,fill=1,stroke=0)
    for j,(d,label,tone) in enumerate([(date(2026,2,28),"28 FEB / STRIKES","coral"),
                         (date(2026,4,7),"7 APR / CEASEFIRE","amber"),
                         (date(2026,6,15),"15 JUN / UN REPORTS DEAL","teal")]):
        x=xx(d);line(c,x,283,x,671,tone,1,(4,3))
        txt(c,label,x+3,682-j*11,6.2,tone,"ArialB")
    for month in range(1,10):
        x=xx(date(2026,month,1));line(c,x,281,x,290,"muted",0.7)
        txt(c,date(2026,month,1).strftime("%b").upper(),x,264,6.7,"muted","ArialB")
    tracks=[
        ("DIVAR / reference",[(date(2026,2,24),"11.14.10 returns","coral",True)]),
        ("NESHAN / pull",[(date(2026,2,19),"14.8.10 pull","teal",True)]),
        ("SNAPP / passenger",[(date(2026,3,2),"8.39 archive*","amber",False)]),
        ("NESHAN / native",[(date(2026,6,6),"14.10.2.3 HTTPS","purple",True),
                             (date(2026,9,1),"GPS input / archive","purple",False)]),
        ("BALAD / Bazaar",[(date(2026,6,10),"4.81.1 geosubmit","teal",True)]),
        ("TAPSI / passenger",[(date(2026,6,12),"7.7 route literal","green",True)]),
        ("SNAPP / driver",[(date(2026,7,26),"5.17 collect","coral",True)]),
    ]
    for i,(name,events) in enumerate(tracks):
        y=635-i*49
        txt(c,name,M,y-2,7.2,"navy","ArialB")
        line(c,x0,y-5,x1,y-5,"line",0.8)
        for d,label,tone,solid in events:
            x=xx(d);c.setFillColor(C[tone] if solid else C["white"])
            c.setStrokeColor(C[tone]);c.circle(x,y-5,5,fill=1,stroke=1)
            label_y=y-18 if name=="NESHAN / native" and d.month==9 else y+9
            if x>W-175: right(c,label,x-8,label_y,6.4,tone,"ArialB")
            else: txt(c,label,x+7,label_y,6.4,tone,"ArialB")
    r.y=236
    r.p("* The preserved Snapp 8.39.0 APK is from an APKPure listing dated 2 March. Uptodown lists the "
        "**version** on 25 February, but that earlier listing is not tied to this exact hash. "
        "The colored bands mark public conflict milestones: opening strikes on 28 February, an announced two-week "
        "ceasefire announced on 7 April (UN statement published 8 April), and a June peace deal reported by the UN "
        "on 15 June. Intermittent fire continued after April. [04-06,10]",
        size=8.0,leading=11.4)
    r.callout("Timing inference", "Neshan's added pull path and Divar's returned route were in VT before 28 February. "
              "The acquired Balad, Snapp driver and Tapsi location-path checkpoints are from June or later. "
              "No acquired cross-app file or traffic proves pre-war location pre-positioning or coordinated deployment.",
              tone="coral",fill="pale")


def overview(r: Report) -> None:
    r.page("technical route map",title="Distinct paths, no demonstrated join",
           deck="Solid arrows summarize app-local code paths; dashed arrows rely on framework or server dispatch. Dotted lines below are an unverified cross-app hypothesis.")
    c=r.c
    flow(c,599,"Neshan / command input",[
        ("FCM OR PULL","Server content enters the same dispatcher."),
        ("PUSH_LOGGER","A recognized command selects diagnostics or files."),
        ("FIXED UPLOAD","POST to app.neshanmap.ir/logger/uploadLogFile."),
    ],tone="coral",dashed=True)
    flow(c,482,"Balad / radio observation",[
        ("LOCATION","Map or navigation location callback."),
        ("SERVER GATE","AppMeta isGeoSubmitEnabled must be true."),
        ("OBSERVATION","Location, nearby cell and Wi-Fi model."),
        ("GEOSUBMIT","POST to location.raah.ir/v2/geosubmit."),
    ],tone="teal")
    flow(c,365,"Snapp driver / radio observation",[
        ("AB FLAG","Enabled, interval and count must pass."),
        ("REQUEST DTO","Locations, radio, state and ride status."),
        ("COLLECT","Default locations.snapp.site route; base can vary."),
    ],tone="amber")
    flow(c,248,"Tapsi / positioning",[
        ("OBSERVATIONS","Cell or Wi-Fi data plus recent position."),
        ("GEOLOCATE","POST to Tapsi production API."),
        ("RESULT","App receives a location estimate."),
    ],tone="purple")
    line(c,M,225,W-M,225,"line",0.8)
    box(c,M,97,BW,110,"pale2",9)
    txt(c,"HYPOTHESIS / NO LINK OBSERVED",M+14,185,8.1,"rose","ArialB")
    p,h=para_obj("If an operator held device-level location records in one service and targeting access in another, "
                 "the first could inform a later payload send. No common device key, target list, operator, "
                 "push receipt or second stage connects these APKs to Divar. App-local UUID hashes are not "
                 "shown to be cross-app identifiers.",BW-30,size=8.3,leading=11.8)
    p.drawOn(c,M+14,170-h)
    line(c,W-105,227,W-105,207,"rose",1.3,(2,4))
    p,h=para_obj("Figure 1. App-local paths are drawn separately. Solid is inspected code flow, dashed is "
                 "framework/server delivery, and the dotted cross-app join remains a hypothesis. "
                 "No sampled APK or traffic proves that join.",BW,size=6.7,leading=8.8,color="muted")
    p.drawOn(c,M,88-h)
    r.y=72


def neshan_route_plate(r: Report) -> None:
    r.page("command reachability",title="Three entries to one Neshan dispatcher",
           deck="Reduced app-local graph from sampled 14.8.10 and 14.13.0.6 paths. The command branch predates both new pull entries.")
    c=r.c
    txt(c,"ENTRY ROUTES",M,679,7.6,"navy","ArialB")
    entries=[
        (M,"FCM SERVICE","Remote data -> source=1", "teal"),
        (M+174,"APP ATTACH","GET /notification/pull -> source=3", "amber"),
        (M+348,"SYNCWORKER","Scheduled pull -> source=4", "purple"),
    ]
    for x,head,detail,tone in entries:
        node(c,x,582,160,75,head,detail,tone=tone)
    node(c,154,449,287,82,"SHARED DISPATCHER",
         "do0.o.k(metadata, data, intentData, source); FCM and pulled responses reach the same handler.",tone="navy2")
    for x,_,_,tone in entries:
        arrow(c,x+80,582,297,531,tone,dashed=(tone!="teal"),width=1.6)
    txt(c,"COMMAND MATCH / AFTER METADATA AND APP-STATE CHECKS",M,417,7.1,"navy","ArialB")
    node(c,178,336,238,65,"metadata.cmd == PUSH_LOGGER?",
         "Recognized command takes the diagnostic/file path.",tone="coral")
    arrow(c,297,449,297,404,"navy2",width=1.7)
    node(c,M,218,214,79,"FALSE / OTHER COMMAND",
         "Continue ordinary dispatch or notification behavior, subject to command type.",tone="muted")
    node(c,338,218,214,79,"TRUE / FILE SELECTION",
         "sendInfo or fileList chooses diagnostics or app-readable paths; return before posting UI.",tone="coral")
    arrow(c,178,368,151,300,"muted",width=1.5)
    arrow(c,416,368,445,300,"coral",width=1.8)
    txt(c,"NO MATCH",99,309,6.6,"muted","ArialB")
    txt(c,"MATCH",458,309,6.6,"coral","ArialB")
    node(c,338,107,214,70,"FIXED UPLOAD",
         "POST /logger/uploadLogFile to app.neshanmap.ir; no historical body recovered.",tone="coral")
    arrow(c,445,218,445,180,"coral",width=1.8)
    c.setFillColor(C["pale2"]);c.roundRect(M,98,214,79,9,fill=1,stroke=0)
    txt(c,"NO OBSERVED OPERATION",M+10,153,7.2,"purple","ArialB")
    p,h=para_obj("No saved pull response, FCM command, selected file, upload receipt or target list was available.",194,size=7.4,leading=10.0)
    p.drawOn(c,M+10,141-h)
    line(c,445,107,445,93,"purple",1.2,(2,4))
    p,h=para_obj("Figure 2. Solid edges are inspected app branches; dashed entry edges depend on "
                 "Android/WorkManager or server scheduling. The dotted terminal marks missing operational "
                 "evidence, not a demonstrated upload. The file-selection concern does not establish a "
                 "historical attack.",BW,size=6.8,leading=9.0,color="muted")
    p.drawOn(c,M,84-h)
    r.y=75


def neshan_command(r: Report) -> None:
    r.page("neshan / command path",title="A new path to an older command",
           deck="The material change is ingress: a pulled server response reaches the same dispatcher as FCM.")
    r.p("In acquired 14.7.9 (archive upload 10 November 2025), Neshan already recognized "
        "`PUSH_LOGGER`. That command can package diagnostic data or selected app-readable files and upload them to "
        "`app.neshanmap.ir/logger/uploadLogFile`. It predates the 2026 war and is not itself a newly inserted "
        "Divar-style stage loader. [08]")
    r.p("Sampled 14.8.9 has no reviewed pull endpoint. In 14.8.10, app attachment calls "
        "`GET /notification/pull`; the response's `metadata`, `data` and `intentData` enter the existing dispatcher "
        "with source=3. FCM calls that dispatcher with source=1. A recognized `PUSH_LOGGER` branch returns before "
        "ordinary notification posting, so the pull route does not require a visible notification or tap. "
        "The app adds a bearer header when it holds a token; the APK cannot reveal server-side access rules.")
    r.dual_code("14.8.9 / sampled baseline",[
        "FCM -> dispatch(command, source=1)",
        "PUSH_LOGGER -> package / upload",
        "no /notification/pull endpoint",
    ],"14.8.10 / added entry",[
        "app attach -> GET /notification/pull",
        "response -> dispatch(..., source=3)",
        "PUSH_LOGGER -> same upload path",
    ],"Normalized from the acquired DEX/JADX path. The new edge is a silent server pull, not a new executable downloader.")
    r.h2("The later scheduled pull")
    r.p("By sampled 14.12.0.2, `SyncWorker` also polls the endpoint. In the inspected 14.13.0.6 app, "
        "attachment seeds the work; the worker dispatches each response with source=4 and schedules another run, "
        "including after a caught exception. The compiled `PullConfig` interval is eight hours, but server "
        "configuration and Android WorkManager can change effective timing. [08]")
    r.code("Inspected command contract / illustrative field names",[
        "pull response: { metadata, data, intentData }",
        "metadata.cmd == PUSH_LOGGER",
        "data.sendInfo or data.fileList selects diagnostics / files",
        "POST /logger/uploadLogFile  -> app.neshanmap.ir",
    ],"This is a normalized code contract, not a captured historical response or upload.",tone="coral")
    r.callout("What makes this an open lead", "The selected-file helper concatenates command-supplied path parts "
              "without canonical containment in the inspected Java path. `..` appears capable of selecting other "
              "files readable by the app. No historical traversal command, file contents or upload receipt was recovered.",
              tone="coral",fill="pale")
    r.p("**Exact transition:** 14.8.9 archive base `681b4f975d40b9d0f1dfa9d5d6b79d59cbd3ca46746a6f9f013ef1e1bf7bcfd4`; "
        "14.8.10 VT first submitted 19 February, `947c4a9412ef577b29c87d87764b4e9e0e3ddfd1966bff2cbab83adb3f2f8115`. "
        "No manifest permission was added at this boundary. The missing March-May APKs limit when later changes began.",
        size=8.0,leading=11.4)


def neshan_native(r: Report) -> None:
    r.page("neshan / native path",title="The opaque HTTPS branch evolved",
           deck="A separate JNI path later accepts an observation; it is not connected to the reviewed push/pull dispatcher.")
    r.p("The earliest sampled `Impulse` bridge is 14.10.2.3, first submitted to VT on 6 June. "
        "Its native `GetAll` path reaches HTTPS request code, but `nativeGetAll(long)` takes no Java observation "
        "String. The native object receives Android context and telephony state, so absence of that Java argument "
        "does not prove the request lacked location-related data. The exact body and runtime activity are unknown. [09]")
    r.p("By sampled 14.13.0.6, Java serializes an observation that can include the last GPS fix and passes it "
        "to `nativeGetAll(long,String)`. The JNI function consumes the String, incorporates input-derived data, "
        "transforms it, and passes a body to a native HTTPS `POST` builder. This is stronger than a string hit: "
        "the observation reaches the request body at the static call-graph level. It does **not** establish which "
        "individual fields survive the merge or what any device sent. [09]")
    r.dual_code("14.10.2.3 / June",[
        "nativeGetAll(handle)",
        "  -> native state -> HTTPS helper",
        "no Java observation String arg",
    ],"14.13.0.6 / later",[
        "nativeGetAll(handle, obsJson)",
        "  -> parse / merge / encrypt",
        "  -> JSON POST body -> HTTPS",
    ],"Semantic JNI comparison. No plaintext network capture was recovered, and the later GPS input must not be projected back into June.")
    r.h2("Destination and activation")
    r.table(["Question","What static analysis reached","What remains unresolved"],[
        ["Where?", "Native config reads `tth` host and `pat` path from XOR/base64/AES-GCM encoded material; TLS port 443.",
         "Plaintext recovery failed authentication; no exact host/path IOC is defensible."],
        ["When?", "Later Java config exposes `navigatorConfig.impulseConfig.enabled`; compiled default is false.",
         "Historical online-config responses, rollout cohort, device conditions and actual request rate."],
        ["What?", "Later observation-derived data reaches the native request body after transformation.",
         "Exact retained fields, wire bytes, receiver and any user targeting."],
    ],[72,222,BW-294],font=7.5,leading=10.4)
    r.callout("Evidence boundary", "This is an unresolved native data path, not a proven exfiltration incident. "
              "No caller from `PUSH_LOGGER` or the new pull dispatcher to `Impulse` was found. "
              "A controlled network trace and saved online-config response would decide what the code did in use.",
              tone="purple",fill="pale")
    r.p("**Anchors:** 14.10.2.3 APK `90499f420b9288d8574e9bf9ae01ee90b2dc1dabb3005877b8655468c204a698`; "
        "14.13.0.6 archived base `24e8c96780668a13d7d3fb9780a0c52ccd1012f4ba06515d2f523506a98e5a0a`. "
        "The inspected native libraries have distinct SHA-256 values retained in the case notes; the PDF records "
        "the APK anchors and the exact JNI signature change.",size=8.0,leading=11.3)


def balad(r: Report) -> None:
    r.page("balad / radio route",title="Location updates gain a radio POST",
           deck="The new path is controlled by app configuration and starts from map/navigation updates, not the reviewed FCM handler.")
    r.p("The Bazaar `ir.balad` 4.79.0 sample lacks the reviewed `RadioObservationUploader` path. "
        "In 4.81.1, `LocationLogger` calls that uploader from map and navigation location updates. "
        "The master `isGeoSubmitEnabled` flag comes from an AppMeta gRPC response; an absent config defaults "
        "it to false. The method accepts non-mock GPS/fused fixes with reported accuracy of 1-50 metres, "
        "rate-limits to about one upload per 30 seconds, then builds a `BaladRadioObservation` for "
        "`POST https://location.raah.ir/v2/geosubmit`. [07]")
    r.dual_code("4.79.0 / sampled",[
        "map/nav fix -> location log",
        "no RadioObservationUploader call",
        "no v2/geosubmit literal",
    ],"4.81.1 / sampled",[
        "map/nav fix -> uploader.p(...) ",
        "if !isGeoSubmitEnabled: return",
        "if trustedFix && throttle: POST",
    ],"Reduced from the decompiled `LocationLogger.kt` and `RadioObservationUploader.kt` paths. The earlier app may have other telemetry.")
    r.h2("What the observation model can hold")
    r.table(["Group","Model fields","Interpretation"],[
        ["Position", "Latitude, longitude, accuracy, provider, optional speed and timestamp.",
         "A precise fix if the gate and trust checks pass."],
        ["Radio", "Nearby cell identifiers/MCC/MNC/signal plus Wi-Fi MAC/BSSID/SSID, signal and frequency.",
         "Some Java fields are `transient`; exact serialized fields need a wire sample."],
        ["Link/context", "SHA-256 of a persisted generated app UUID; map or navigation context and spoofing state.",
         "Persistent app-local identifier; not shown to join identities across apps."],
    ],[87,240,BW-327],font=7.5,leading=10.3)
    r.p("Sampled 4.83.0 adds a GNSS integrity verdict that can suppress spoofed fixes. By 4.84.0, "
        "a second remote flag, `useBaladLocations`, permits Balad's network-location source and batching of up to ten "
        "observations. The master geosubmit flag still gates the route. Location and Wi-Fi permissions were already "
        "present before 4.81.1; the behavior changed without a new location grant. [07]")
    r.callout("What would settle historical use", "Recover AppMeta `baladNetworkProvider` values by time and cohort, "
              "the signed build inputs for missing 4.78.x/4.80.0/4.81.0 files, and geosubmit access/body logs. "
              "No actual request, recipient ownership proof or attacker-controlled config was recovered.",
              tone="teal",fill="pale2")
    r.p("**Exact transition:** 4.79.0 `4c015bc86454142d7d5e4318e02454d0e1c7c2c9c602f3227fbde5a631c31784`; "
        "4.81.1 `da7e348ba2fd161e0a0d05b7ad7a216f95389f9e69219144d5cc72bf7454370b` "
        "(VT first submission 10 June). Bazaar and Play packages/signers are analyzed as separate tracks.",
        size=7.9,leading=11.2)


def snapp_driver(r: Report) -> None:
    r.page("snapp / driver collection",title="A gated radio snapshot in the driver app",
           deck="The new request is distinct from Snapp's existing driver location publishing.")
    r.p("The acquired driver 5.13.0 and 5.15.0 DEX lack `RadioSignalCollectionRequest`, "
        "`isWifiCollectionEnabled` and the reviewed `publishRadioSignalData` path. Both acquired "
        "5.17.0 variants and 5.18.0 contain it. The first positive file reached VT on 26 July; "
        "unsampled 5.16.0 prevents an exact introduction claim. [10]")
    r.p("In 5.17.0, `JSDetectorInteractor` requires the AB flag, a positive collection interval and a positive "
        "Wi-Fi or cell sample count. The request builder combines fused/network/manually selected/suggested "
        "locations, Wi-Fi scans, connected cells, foreground state, ride status and device time. It POSTs to "
        "the default `https://locations.snapp.site/v1/driver/collect`, but a server-provided location base can "
        "replace that default. The code does not show the effective historical flags or destination. [10]")
    r.code("Selected decompiled request fields / 5.17.0",[
        '@SerializedName("device_timestamp") String timestamp;',
        '@SerializedName("location") LocationSources location;',
        '@SerializedName("wifi_scans") List<WifiScan> wifi;',
        '@SerializedName("connected_cells") List<ConnectedCell> cell;',
        '@SerializedName("app_state") int foregroundState;',
        '@SerializedName("ride_status") String rideStatus;',
    ],"Field names come from the preserved JADX request class; variable names above are shortened for legibility. This is not a captured POST body.",tone="amber")
    r.p("Wi-Fi BSSID/SSID values are hashed with unsalted SHA-256 in the request model, while coordinates "
        "and cell identifiers remain structurally available. Those hashes do not erase a radio-location "
        "fingerprint. The familiar `ACCESS_BACKGROUND_LOCATION`, fine/coarse location, Wi-Fi-state and "
        "foreground-location declarations were already present at the 5.15.0 checkpoint. [10]")
    r.table(["Sampled checkpoint","Known collector path","Date basis"],[
        ["5.15.0", "Reviewed route absent from raw DEX.", "VT 13 April 2026"],
        ["5.17.0 / two variants", "Gate, DTO and POST present in both; relevant DEX is identical.", "VT 26 July / 4 August"],
        ["5.18.0", "Collector retained; process-death location receiver added.", "VT 5 September"],
    ],[117,252,BW-369],font=7.5,leading=10.2)
    r.callout("Alternative explanation", "The path is compatible with positioning, signal quality or spoofing work. "
              "No attacker-controlled endpoint, enabled AB cohort, historical request or malicious use is verified. "
              "Recover the AB config, dynamic base URL and `/collect` receipts before treating it as an incident.",
              tone="amber",fill="pale")


def snapp_other(r: Report) -> None:
    r.page("snapp / other paths",title="Polling and updates are separate",
           deck="A notification inbox and an in-app updater deserve review, but neither is the Divar receiver shortcut in these samples.")
    r.h2("Passenger: Fanoos polling")
    r.p("Passenger 8.37.0 and sampled 8.38.0 lack `cab.snapp.fanoos`. Acquired 8.39.0 and later "
        "contain `GET v1/passenger/polling-notifications`, with `notifications[].{id,data,type}` and an "
        "`x-poll-interval` response header. The reviewed default renderer posts a visible Android notification; "
        "its link/action path follows a user tap. I found no `Fanoos.ignite()` callsite in decompiled passenger "
        "8.39.0, so fresh-install activation remains unverified. [10]")
    r.p("The archive dates are especially easy to overread: Uptodown lists the **version** 8.39.0 on "
        "25 February, while the preserved APK came from APKPure's 2 March listing. This record cannot put "
        "that exact binary on phones before the 28 February war boundary. Driver Fanoos polling is present "
        "by sampled 5.15.0, with authorization and feature checks around its `ignite()` call.")
    flow(r.c,442,"Reviewed Fanoos default behavior",[
        ("POLL","GET polling-notifications when active."),
        ("RENDER","Post a visible Android notification."),
        ("TAP","Open link or action after user interaction."),
    ],tone="teal",dashed=True)
    r.y=422
    r.h2("Behrooz: an update channel, not a recovered stage")
    r.p("The driver app also includes a Behrooz updater that can read `UpdateConfig.directUrl`, download an "
        "APK and ask Android `PackageInstaller` or an install intent to apply it. Install permissions vary "
        "within the same 5.17.0 version: one acquired variant declares `REQUEST_INSTALL_PACKAGES` and "
        "`UPDATE_PACKAGES_WITHOUT_USER_ACTION`, the other does not. Passenger variants also differ. "
        "A compromised update configuration could matter, but no hostile URL, APK or install outcome was "
        "recovered. The inspected FCM and polling handlers do not demonstrate a direct loader edge to Behrooz.")
    r.table(["Mechanism","Observed path","Important limit"],[
        ["Fanoos passenger", "Server poll -> visible notification -> tap action.", "Exact 8.39 timing and activation unresolved."],
        ["Fanoos driver", "Authorized/flagged polling inbox by 5.15.0.", "No silent command-loader branch shown."],
        ["Behrooz", "Configured APK URL -> download -> installer.", "No attacker patch or install trace; variant permissions differ."],
    ],[112,195,BW-307],font=7.5,leading=10.3)
    r.callout("Comparison rule", "The mere presence of polling, push SDKs, an updater or package-install permission "
              "is not a finding of the Divar backdoor. The decisive question is which received bytes reach a "
              "worker, under what gate, and whether a real server supplied them.")


def tapsi_geo(r: Report) -> None:
    r.page("tapsi / positioning",title="Tapsi production geolocation request",
           deck="The inspected callsites POST radio and prior-location observations to Tapsi production APIs and use the response as a location estimate.")
    r.p("The acquired Tapsi corpus begins in June for passengers and July for drivers; it does not cover "
        "January-May. Passenger 7.7.0 has the route string by its 12 June VT submission. Decompiled "
        "7.8.4 and 7.10.0 both call `POST v3/geolocation/geolocate` on the production "
        "`https://p1.tapsi.ir/api/` base with the same seven serialized fields. The later deobfuscation "
        "does not represent a new payload. The repository requires at least one cell or Wi-Fi observation "
        "before sending. [11]")
    r.code("Passenger request / seven stable JSON fields",[
        "cellTowers, wifiAccessPoints,",
        "cellTowersRepeatCount, wifiAccessPointsRepeatCount,",
        "isWifiEnabled, lastLocation, lastInHouseNetworkLocation",
        "POST https://p1.tapsi.ir/api/v3/geolocation/geolocate",
    ],"Both 7.8.4 and 7.10.0 expose this contract in decompiled DTO/API methods; this is not a captured request.",tone="purple")
    r.p("The inspected driver 8.8.0 landing app builds the analogous request from observation flows and recent "
        "driver locations, POSTs through `https://d1.tapsi.ir/api/`, and reads the location estimate. "
        "The inspected `EnabledFeatures` gate and SDK config default are disabled; live server settings are "
        "unknown. A route string in a lower version is a discovery lead, not proof of execution. [11]")
    flow(r.c,319,"Tapsi positioning path",[
        ("OBSERVE","Cell or Wi-Fi plus recent location."),
        ("FEATURE GATE","Driver SDK setting can disable call."),
        ("GEOLOCATE","POST to p1/d1 Tapsi production API."),
        ("RESPONSE","A location estimate returns to app."),
    ],tone="purple")
    r.y=294
    r.p("No non-Tapsi recipient, actual off-band exfiltration receipt, affected account or operator control "
        "was identified. This is sensitive location data in an apparent first-party positioning service. "
        "The first VT submission of a positive sample does not date the code's first public release.",
        size=8.5,leading=12.1)
    r.callout("Version-order trap", "The sampled driver 7.13.6 negative checkpoint was submitted to VT "
              "after a higher-version positive. For that pair, **version order** bounds the code change; VT order "
              "cannot be used as a developer rollout sequence. Missing January-May bytes preclude a pre-war verdict.",
              tone="amber",fill="pale")


def tapsi_updater(r: Report) -> None:
    r.page("tapsi / update channel",title="Two signed 8.8.0 flavors diverge",
           deck="The landing build has a binary-patch updater. The same-version Myket build lacks it; the difference is a distribution flavor.")
    r.p("Both driver 8.8.0 APKs use package `taxi.tap30.driver`, versionCode 1080080000 and the same "
        "signer certificate. The Myket file identifies itself as `myket_productionFinalRelease`; the "
        "landing file says `landing_productionFinalLanding`. The landing build adds Yadegar patch classes, "
        "`libapkpatch.so`, install-result handling and install/update manifest declarations. This is not "
        "an observed insertion followed by retraction. [11]")
    r.table(["Exact 8.8.0 file","Module state","VT first submission"],[
        ["Myket / `4f26428e71051bcf116cc97d33670adf76f24cafe8b1e1a550e19eb42a94ee47`",
         "No Yadegar patch module in reviewed variant.","5 September 2026"],
        ["Landing / `1647b9af56b3923ac8a32c3ee9aeb9513563d73a86181f1db05a10f3bbed95a4`",
         "Yadegar patch path and install declarations.","14 September 2026"],
    ],[247,176,BW-423],font=7.2,leading=9.9)
    r.h2("What the landing updater does")
    flow(r.c,427,"Yadegar landing path",[
        ("CHECK","GET patch metadata from d1.tapsi.ir."),
        ("FETCH","Response-selected patchUrl is downloaded."),
        ("REBUILD","Native patch reconstructs patched.apk."),
        ("INSTALL","PackageInstaller session is committed."),
    ],tone="coral",dashed=True)
    r.y=405
    r.p("The server response contains `hasNewUpdate`, `patchUrl`, `patchName`, `targetVersion` and `patchSize`. "
        "The inspected Java/Kotlin path does not compare an independent expected digest or detached signature "
        "before the installer commit; Android package-install and signer checks still apply. A server-selected "
        "update URL is a security-relevant delivery surface, but no malicious patch, attacker control or "
        "successful install was recovered. No edge from the inspected push handler to Yadegar was shown.")
    r.callout("What would verify this route", "Preserve Yadegar configuration and `get-patch` response logs, "
              "downloaded patch bytes, patch-host resolution, reconstructed APK hash and installer result. "
              "Compare each exact artifact with developer build approval and store-channel records.",
              tone="coral",fill="pale")
    r.p("The same signer is useful for grouping the pair but cannot establish who authorized it. "
        "A compromised signing key or release pipeline could produce a valid signature; neither is proven here.",
        size=8.5,leading=12)


def deltas(r: Report) -> None:
    r.page("semantic change ledger",title="What changed, and what did not",
           deck="These are the meaningful behavior boundaries in acquired files. Dates are observation dates unless explicitly marked as archives.")
    r.table(["Transition","New or persistent behavior","Consequence / limit"],[
        ["Neshan 14.8.9 -> 14.8.10", "App-open pull joins an existing FCM command dispatcher; `PUSH_LOGGER` remains the same command.",
         "A silent server response can reach file upload; no response or receipt recovered."],
        ["Neshan 14.10.2.3 -> 14.13.0.6", "Native HTTPS path evolves to accept Java observation JSON and send transformed, input-derived body.",
         "Later GPS input is proven at code level; June fields and plaintext host remain unknown."],
        ["Balad 4.79.0 -> 4.81.1", "Location callbacks gain config-gated radio observation POST.",
         "Sensitive collection capability; earlier gap and live flag values unresolved."],
        ["Balad 4.83.0 -> 4.84.0", "Second flag permits Balad network-location source and batches up to ten.",
         "Potentially changes source and volume; master geosubmit gate persists."],
        ["Snapp driver 5.15.0 -> 5.17.0", "AB-gated location/radio request and `collect` POST appear.",
         "No 5.16.0 bytes; default host can be replaced by dynamic base."],
        ["Snapp passenger 8.38.0 -> 8.39.0", "Fanoos poll classes appear; default renderer posts visible notification.",
         "Preserved hash is not placed before war by version-only archive listing."],
        ["Tapsi passenger 7.8.4 -> 7.10.0", "Same seven-field geolocation request survives deobfuscation.",
         "Class-name change alone is not a new upload."],
        ["Tapsi driver 8.8.0 Myket / landing", "Landing flavor alone carries Yadegar patch updater and install declarations.",
         "Same version/channel variant; no malicious patch or insertion/retraction shown."],
    ],[137,205,BW-342],font=7.25,leading=9.9)
    r.callout("Comparison to Divar", "Divar's confirmed sampled code has a special push/response entry "
              "that diverts to a fetch, file write and reflective invocation worker. None of the paths above "
              "demonstrated that same end-to-end worker chain in these four apps. Different malicious logic, "
              "native-only code or missing releases remain outside this narrow negative.",tone="purple",fill="pale2")


def permissions(r: Report) -> None:
    r.page("signing and permissions",title="The changes rarely needed a new grant",
           deck="Manifest comparisons explain app capability, not whether a user granted access or a company authorized an update.")
    r.table(["Track / boundary","Relevant manifest observation","Interpretation"],[
        ["Balad / 4.79.0 -> 4.81.1", "Coarse/fine location, Wi-Fi state and Internet were already declared. Bazaar referrer/attribution changes appear separately.",
         "Uploader can use existing grants; no new location prompt proves nothing about use."],
        ["Neshan / 14.8.9 -> 14.8.10", "No new permission. FCM service stays non-exported and registered for Firebase messaging.",
         "New pull reaches old file-upload command through app code and its existing access."],
        ["Snapp driver / 5.15.0 -> 5.17.0", "Background/fine/coarse location, Wi-Fi state and foreground-location permissions pre-exist.",
         "Radio collector is a code/config delta, not a manifest delta."],
        ["Tapsi driver / 8.8.0 same version", "Landing flavor adds install/update declarations and install-result receiver; Myket flavor lacks them.",
         "Distribution choice changes update capability; it is not proof of compromise."],
    ],[131,225,BW-356],font=7.35,leading=10.2)
    r.h2("What signing establishes")
    r.p("Every acquired Balad, Neshan, Snapp and Tapsi APK has an exact hash and an associated signer fingerprint "
        "in the companion inventory. "
        "Balad's Bazaar and Play packages are distinct signing tracks; Snapp passenger and driver are distinct "
        "products; Tapsi passenger and driver are separate packages. The Neshan variants share their compared "
        "lineage. These groupings make adjacent diffs more meaningful, but **a valid signature is not an "
        "authorization verdict**. A stolen key, unauthorized source edit or compromised build pipeline can "
        "still produce signed bytes. [07-11]")
    r.h2("Code, deployment and traffic are three different records")
    r.bullet("**Code:** a caller reaches a request or worker under stated conditions in the exact acquired file.")
    r.bullet("**Deployment:** a store, CDN or device installed that exact hash for a known cohort.")
    r.bullet("**Traffic:** a retained server/device record shows the condition passed and data or patch moved.")
    r.callout("Boundary", "This study establishes selected code capabilities and exact-file observations. "
              "It has no production backend configuration, OneSignal/FCM send record, device network trace, "
              "Tapsi patch payload, Neshan command response or location upload receipt. "
              "Consequently it does not estimate victims or attribute the paths to a threat actor.",
              tone="purple",fill="pale")


def investigation(r: Report) -> None:
    r.page("incident-response handoff",title="Records that could change the verdict",
           deck="Ask for exact-hash deployment and route-specific receipts before attempting a cross-app narrative.")
    r.table(["Priority","Preserve and correlate","Question answered"],[
        ["01 / build custody", "CI source commit and approval, signing event, exact output hash, store/CDN channel and device rollout cohort for each boundary and same-version variant.",
         "Was the changed code an authorized build, and where did that exact file go?"],
        ["02 / Neshan command", "FCM payloads, `/notification/pull` responses and access logs, `PUSH_LOGGER` dispatcher records, `/logger/uploadLogFile` bodies/receipts; especially `sendInfo` and `fileList`.",
         "Did a silent diagnostic request select unusual files or users?"],
        ["03 / Neshan native", "Saved `online-config/config/v5.2` responses, `impulseConfig` values, controlled app traffic, TLS destination and native request bytes for the two JNI generations.",
         "Which host and fields were used, and was it enabled?"],
        ["04 / Balad", "AppMeta `baladNetworkProvider` history by cohort; `isGeoSubmitEnabled` and `useBaladLocations`; `/v2/geosubmit` request and receipt logs.",
         "Which devices uploaded radio/location observations, if any?"],
        ["05 / Snapp", "Driver AB `isWifiCollectionEnabled`, counts/intervals, dynamic location base and `/collect` receipts; passenger Fanoos flags/poll records and device notification history.",
         "Was collection or polling active, and to what endpoint?"],
        ["06 / Tapsi", "Geolocate feature flags and request/response logs; Yadegar `get-patch` responses, downloaded patch, reconstructed APK hash and installer result.",
         "Was a patch or location request actually delivered?"],
    ],[93,272,BW-365],font=7.1,leading=9.9)
    r.h2("The cross-app join test")
    r.p("Only after proving individual events should investigators test whether the same device or person appears "
        "in a location record and a delivery target. Use lawful, independently verified device/account identifiers "
        "and exact timestamps. A hashed Balad app UUID is not shown to equal a Divar, Snapp, Neshan or Tapsi "
        "identifier. A common time window, country or valid signer does not establish common control.")
    r.callout("Preservation first", "Push bodies can be absent from ordinary notification history when a handler "
              "returns before posting UI. Preserve backend sends, pull responses and upload receipts while retention "
              "permits. For Divar's OneSignal/FCM route, consult the companion case file's separate handoff; "
              "the app providers here must be assessed on their own code and logs.",tone="teal",fill="pale2")


def anchors(r: Report) -> None:
    r.page("exact-file anchors",title="Files behind the pivotal comparisons",
           deck="Each SHA-256 is clickable to its VirusTotal file page. A file page or host name is an evidence pivot, not a malicious IOC.")
    items=[
        ("BALAD / 4.79.0 / Bazaar", "4c015bc86454142d7d5e4318e02454d0e1c7c2c9c602f3227fbde5a631c31784", "uploader absent"),
        ("BALAD / 4.81.1 / Bazaar", "da7e348ba2fd161e0a0d05b7ad7a216f95389f9e69219144d5cc72bf7454370b", "geosubmit present"),
        ("NESHAN / 14.8.9", "681b4f975d40b9d0f1dfa9d5d6b79d59cbd3ca46746a6f9f013ef1e1bf7bcfd4", "pull absent"),
        ("NESHAN / 14.8.10", "947c4a9412ef577b29c87d87764b4e9e0e3ddfd1966bff2cbab83adb3f2f8115", "pull added"),
        ("NESHAN / 14.10.2.3", "90499f420b9288d8574e9bf9ae01ee90b2dc1dabb3005877b8655468c204a698", "Impulse native path"),
        ("NESHAN / 14.13.0.6", "24e8c96780668a13d7d3fb9780a0c52ccd1012f4ba06515d2f523506a98e5a0a", "GPS input to native POST"),
        ("SNAPP DRIVER / 5.15.0", "74660538613dd5ccb077ed46a3124e9242258e1c139520642d5f1599613cbad4", "collector absent"),
        ("SNAPP DRIVER / 5.17.0", "2c7bee97b304134c58aafc15d9935a55a9091488e2a200080353218932bfe671", "collector present"),
        ("TAPSI PASSENGER / 7.8.4", "e7e7597fcc8e2dc93535bd8eebd862433da34c1c67a1c73120e3268a84ae2869", "geolocate call"),
        ("TAPSI DRIVER / 8.8.0 / Myket", "4f26428e71051bcf116cc97d33670adf76f24cafe8b1e1a550e19eb42a94ee47", "no Yadegar"),
        ("TAPSI DRIVER / 8.8.0 / landing", "1647b9af56b3923ac8a32c3ee9aeb9513563d73a86181f1db05a10f3bbed95a4", "Yadegar present"),
    ]
    y=632
    for label,sha,note in items:
        source_hash(r.c,M,y,label,sha,note)
        y-=46
    r.y=y-5
    r.p("The [full 103-APK inventory](https://github.com/Hamid-K/divar-push-lab/blob/main/research/Iran_mobile_apps_sample_inventory_v2.0.csv) "
        "preserves all inspected hashes, package tracks, versionCodes, signing-fingerprint algorithm, acquisition source "
        "and exact date basis. This page selects only files that make a substantive boundary or variant legible.",
        size=8.3,leading=11.7)


def sources(r: Report) -> None:
    r.page("sources and method",title="How to read and reproduce this case",
           deck="The primary evidence is the acquired APK bytes. Public pages below date or locate individual files; none supplies missing backend traffic.")
    entries=[
        ("01", "Divar case notes by Ramin Farajpour Cami", "https://gist.github.com/raminfp/a548a2af86108eb40b8bffc5c8f07aaa"),
        ("02", "My Divar disclosure on X", "https://x.com/hkashfi/status/2106147963332633025"),
        ("03", "Divar technical case file v2.8", "https://github.com/Hamid-K/divar-push-lab/blob/main/research/Divar_backdoor_technical_analysis_v2.8_2026-10-05.pdf"),
        ("04", "UN: opening strikes, 28 February 2026", "https://turkiye.un.org/en/310903-bombing-iran-and-retaliatory-strikes-%E2%80%98-grave-threat-international-peace-and-security%E2%80%99"),
        ("05", "UN: 7 April two-week ceasefire announcement", "https://india.un.org/en/313596-un-secretary-general-conflict-middle-east-7-april-2026"),
        ("06", "UN: June peace deal and intermittent fire", "https://india.un.org/en/317325-guterres-welcomes-us-iran-peace-deal-%E2%80%98critical-step%E2%80%99-toward-ending-conflict"),
        ("07", "Balad 4.81.1 exact-file checkpoint", "https://www.virustotal.com/gui/file/da7e348ba2fd161e0a0d05b7ad7a216f95389f9e69219144d5cc72bf7454370b"),
        ("08", "Neshan pull checkpoint", "https://www.virustotal.com/gui/file/947c4a9412ef577b29c87d87764b4e9e0e3ddfd1966bff2cbab83adb3f2f8115"),
        ("09", "Neshan native checkpoint", "https://www.virustotal.com/gui/file/90499f420b9288d8574e9bf9ae01ee90b2dc1dabb3005877b8655468c204a698"),
        ("10", "Snapp driver 5.17.0 exact-file checkpoint", "https://www.virustotal.com/gui/file/2c7bee97b304134c58aafc15d9935a55a9091488e2a200080353218932bfe671"),
        ("11", "Tapsi driver 8.8.0 landing exact file", "https://www.virustotal.com/gui/file/1647b9af56b3923ac8a32c3ee9aeb9513563d73a86181f1db05a10f3bbed95a4"),
        ("12", "Full normalized sample inventory", "https://github.com/Hamid-K/divar-push-lab/blob/main/research/Iran_mobile_apps_sample_inventory_v2.0.csv"),
        ("13", "Balad archive version listings", "https://balad-ir-balad.en.uptodown.com/android/versions"),
        ("14", "Snapp APKPure passenger archive", "https://apkpure.net/snapp-%D8%A7%D8%B3%D9%86%D9%BE/cab.snapp.passenger/versions"),
        ("15", "Snapp Uptodown version archive", "https://snapp.en.uptodown.com/android/versions"),
        ("16", "Tapsi passenger 7.8.4 exact file", "https://www.virustotal.com/gui/file/e7e7597fcc8e2dc93535bd8eebd862433da34c1c67a1c73120e3268a84ae2869"),
    ]
    for num,label,url in entries:
        r.p(f"**[{num}]** [{label}]({url})",size=8.0,leading=11.1,after=4)
    r.h2("Technical evidence notes")
    r.p("The public [evidence index](https://github.com/Hamid-K/divar-push-lab/blob/main/research/evidence/mobile_apps/README.md) "
        "links the inspected [Balad](https://github.com/Hamid-K/divar-push-lab/blob/main/research/evidence/mobile_apps/balad.md), "
        "[Neshan](https://github.com/Hamid-K/divar-push-lab/blob/main/research/evidence/mobile_apps/neshan.md), "
        "[Snapp](https://github.com/Hamid-K/divar-push-lab/blob/main/research/evidence/mobile_apps/snapp.md) and "
        "[Tapsi](https://github.com/Hamid-K/divar-push-lab/blob/main/research/evidence/mobile_apps/tapsi.md) "
        "method/line anchors and their exact APK hashes. The notes are decompiled/static evidence, not server telemetry.",
        size=7.8,leading=10.9,after=8)
    r.h2("Method and limits")
    r.p("For each acquired file I recorded the SHA-256, package, versionCode and signer fingerprint, then "
        "compared adjacent DEX, manifest and relevant decompiled methods. Distinctive Divar trigger/worker "
        "checks served as triage, followed by path-specific review of command dispatch, location callbacks, "
        "network interfaces, native call flow and updaters. Obfuscation and JADX errors were checked against "
        "raw DEX or repeated variants where material; the Impulse conclusion is bounded by disassembled "
        "request-path reachability. This was **static analysis**, not an observed victim-device run.",
        size=8.1,leading=11.5)
    r.callout("Report history", "Version 1.2 was a chronology-led preliminary cross-app review. "
              "Version 2.0 follows the Divar v2.7 case-file design, centers the four additional apps, "
              "adds 103-file coverage and semantic path diagrams, and sharpens date, native-host and "
              "server-use limits. Prepared 5 October 2026 by Hamid Kashfi with LLM assistance.",
              tone="teal",fill="pale2")


def main() -> None:
    r=Report()
    r.cover()
    assessment(r)
    sample_matrix(r)
    chronology(r)
    overview(r)
    neshan_route_plate(r)
    neshan_command(r)
    neshan_native(r)
    balad(r)
    snapp_driver(r)
    snapp_other(r)
    tapsi_geo(r)
    tapsi_updater(r)
    deltas(r)
    permissions(r)
    investigation(r)
    anchors(r)
    sources(r)
    r.save()
    print(PDF)


if __name__ == "__main__":
    main()
