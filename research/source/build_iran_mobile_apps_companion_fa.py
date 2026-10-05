#!/usr/bin/env python3
"""Build the Persian cross-app companion report from its reviewable Markdown.

Requirements: pandoc, XeLaTeX, and the bundled OFL-licensed Vazirmatn fonts.
The stable PDF path deliberately has no date or version in its filename.
"""

from __future__ import annotations

import re
import subprocess
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
MARKDOWN = HERE / "iran_mobile_apps_companion_fa.md"
OUTPUT = ROOT / "Iran_mobile_apps_companion_fa.pdf"
FONT_DIR = HERE / "fonts"


def run(*command: str, cwd: Path | None = None) -> None:
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(f"{' '.join(command)} failed:\n" + "\n".join(result.stdout.splitlines()[-55:]) + "\n" + result.stderr)


def convert_body(tmp: Path) -> str:
    body = tmp / "body.tex"
    run(
        "pandoc", "-f", "gfm", "-t", "latex", "--wrap=none",
        "--syntax-highlighting=none", str(MARKDOWN), "-o", str(body),
    )
    tex = body.read_text()
    # The cover carries the report title and subtitle. Promote content headings.
    tex = re.sub(r"^\\section\{از پوش تا موقعیت مکانی\}[^\n]*\n\n", "", tex, count=1)
    tex = tex.replace("گزارش همراهِ بررسی برنامه‌های موبایل ایران، نسخهٔ ۲٫۱ (فارسی)\n\n", "", 1)
    tex = tex.replace(r"\subsubsection{", "TEMP_SUBSECTION{")
    tex = tex.replace(r"\subsection{", r"\section{")
    tex = tex.replace("TEMP_SUBSECTION{", r"\subsection{")
    tex = re.sub(r"\\label\{[^}]+\}", "", tex)

    # Long Persian cells need fixed widths; default Pandoc l/r columns overrun A4.
    widths = {
        "lll": r"p{0.21\linewidth}p{0.40\linewidth}p{0.34\linewidth}",
        "lr": r"p{0.77\linewidth}p{0.17\linewidth}",
        "lrrrr": r"p{0.19\linewidth}p{0.19\linewidth}p{0.18\linewidth}p{0.18\linewidth}p{0.18\linewidth}",
    }
    for spec, replacement in widths.items():
        tex = tex.replace(f"@{{}}{spec}@{{}}", replacement)
    tex = tex.replace(r"\begin{longtable}[]", r"\begin{longtable}")
    tex = tex.replace(r"{\def\LTcaptype{none} % do not increment counter", "{")

    # Long hash labels are selectable and clickable, split only for the page layout.
    def split_hash(match: re.Match[str]) -> str:
        url, digest = match.groups()
        return (
            r"\href{" + url + r"}{\hashtext{" + digest[:32] + "}{"
            + digest[32:] + "}}"
        )

    tex = re.sub(
        r"\\href\{(https://www\.virustotal\.com/gui/file/[0-9a-f]{64})\}\{([0-9a-f]{64})\}",
        split_hash,
        tex,
    )
    # Full hashes are printed in the anchor table; compact linked references
    # elsewhere keep dense Persian paragraphs and narrow comparison rows intact.
    def compact_hash(match: re.Match[str]) -> str:
        digest = match.group(1)
        return (
            r"\href{https://www.virustotal.com/gui/file/" + digest
            + r"}{\texttt{" + digest[:10] + r"\ldots " + digest[-6:] + "}}"
        )

    tex = re.sub(r"\\texttt\{([0-9a-f]{64})\}", compact_hash, tex)
    # Pandoc uses a few LaTeX forms that otherwise read left-to-right in RTL copy.
    tex = tex.replace(r"\tightlist", "")
    tex = tex.replace(r"\begin{verbatim}", "\\begin{latin}\n\\begin{verbatim}")
    tex = tex.replace(r"\end{verbatim}", "\\end{verbatim}\n\\end{latin}")
    tex = tex.replace("←", r"\ensuremath{\leftarrow}")
    tex = tex.replace("→", r"\ensuremath{\rightarrow}")
    tex = tex.replace(r"{[}۰۱--۰۳{]}", r"[۰۱–۰۳]")

    tex = inject_after_section(tex, "پوشش نمونه‌ها", SAMPLE_FIGURE)
    tex = inject_after_section(tex, "گاه‌شمار شواهد در کنار جنگ", TIMELINE_FIGURE)
    tex = inject_after_section(tex, "نقشهٔ مسیرها: چهار زنجیرهٔ جدا، بدون پیوندِ ثابت‌شده", ROUTE_FIGURE)
    tex = inject_after_section(tex, "کارهای بعدی", BACKLOG_FIGURE)
    return tex


def inject_after_section(tex: str, title: str, figure: str) -> str:
    needle = r"\section{" + title + "}"
    if needle not in tex:
        raise ValueError(f"Missing target section: {title}")
    return tex.replace(needle, needle + "\n\n" + figure, 1)


SAMPLE_FIGURE = r"""
\begin{figure}[htbp]\centering
\begin{tikzpicture}[x=1cm,y=0.58cm]
\fill[inklight] (-0.15,-0.55) rectangle (14.8,7.25);
\node[anchor=east,text=ink,font=\bfseries] at (14.2,6.65) {۱۰۳ فایل مشخص، هفت تبار بسته};
\foreach \yy/\lab/\cnt/\col in {5.7/بلد بازار/26/teal,4.9/بلد گوگل‌پلی/6/teal,4.1/نشان/21/purple,3.3/اسنپ مسافران/12/coral,2.5/اسنپ رانندگان/5/coral,1.7/تپسی مسافران/20/red,0.9/تپسی رانندگان/13/red}{
  \node[anchor=east,text=ink,font=\small] at (14.1,\yy) {\lab};
  \fill[white] (2.0,\yy-0.18) rectangle (10.6,\yy+0.18);
  \pgfmathsetmacro{\barwidth}{8.6*\cnt/26}
  \fill[\col] (2.0,\yy-0.18) rectangle (2.0+\barwidth,\yy+0.18);
  \node[anchor=east,text=\col,font=\bfseries\small] at (1.6,\yy) {\cnt};
}
\end{tikzpicture}
\caption*{تعداد فایل‌های دقیق در مجموعهٔ بررسی‌شده؛ رنگ، نتیجهٔ امنیتی را نشان نمی‌دهد.}
\end{figure}
"""


TIMELINE_FIGURE = r"""
\begin{figure}[htbp]\centering
\begin{tikzpicture}[x=1cm,y=1cm]
\fill[inklight] (-0.2,-0.55) rectangle (14.8,4.4);
\node[anchor=east,text=ink,font=\bfseries] at (14.2,3.85) {نقطه‌های زمانیِ فایل‌های بررسی‌شده در کنار جنگ};
\draw[thick,grayline] (1.0,1.68) -- (13.7,1.68);
\draw[line width=2.7pt,red] (2.7,1.68) -- (5.8,1.68);
\draw[line width=2.7pt,red!60] (5.8,1.68) -- (9.6,1.68);
\foreach \xx/\date/\event/\col in {1.5/۱۹ فوریه/نشان: واکشی فرمان/purple,2.7/۲۸ فوریه/آغاز جنگ/red,5.8/۷ آوریل/آتش‌بس اعلامی/red,9.6/۱۵ ژوئن/توافق صلح/red,12.7/۲۶ ژوئیه/اسنپ: گردآورنده/coral}{
  \fill[\col] (\xx,1.68) circle (0.11);
  \node[anchor=south,text=\col,font=\bfseries\scriptsize,align=center] at (\xx,1.9) {\date};
  \node[anchor=north,text=ink,font=\scriptsize,align=center,text width=2.25cm] at (\xx,1.42) {\event};
}
\node[anchor=south,text=teal,font=\bfseries\scriptsize] at (2.0,2.78) {۲۴ فوریه: دیوار 11.14.10};
\draw[teal,densely dotted] (2.0,2.65)--(2.0,1.76);
\node[anchor=south,text=teal,font=\bfseries\scriptsize] at (9.3,2.78) {۱۰ ژوئن: بلد 4.81.1};
\draw[teal,densely dotted] (9.3,2.65)--(9.3,1.76);
\end{tikzpicture}
\caption*{تاریخ‌ها مبنای مشاهدهٔ فایل یا خبر عمومی‌اند؛ زمانِ نصب یا فعال‌شدن مسیر را ثابت نمی‌کنند.}
\end{figure}
"""


ROUTE_FIGURE = r"""
\begin{figure}[htbp]\centering
\begin{tikzpicture}[x=1cm,y=1cm,>=latex]
\fill[inklight] (-0.15,-0.7) rectangle (14.8,5.1);
\node[anchor=east,text=ink,font=\bfseries] at (14.2,4.55) {مسیرهای کد در چهار برنامه};
\foreach \yy/\app/\start/\target/\col in {3.75/نشان/FCM یا pull/PUSH\_LOGGER و آپلود فایل/purple,2.85/بلد/callback مکان/geosubmit رادیو و مکان/teal,1.95/اسنپ راننده/تنظیم AB/collect رادیو و GPS/coral,1.05/تپسی/مشاهدهٔ سلول یا Wi-Fi/API موقعیت‌یابی/red}{
  \node[draw=\col,fill=white,rounded corners=3pt,minimum width=2.1cm,minimum height=0.55cm,text=\col,font=\bfseries\small] at (12.45,\yy) {\app};
  \node[draw=grayline,fill=white,rounded corners=3pt,minimum width=3.0cm,minimum height=0.55cm,text=ink,font=\scriptsize] at (8.45,\yy) {\start};
  \node[draw=grayline,fill=white,rounded corners=3pt,minimum width=4.7cm,minimum height=0.55cm,text=ink,font=\scriptsize] at (3.25,\yy) {\target};
  \draw[->,thick,\col] (11.3,\yy)--(10.0,\yy);
  \draw[->,thick,\col] (6.9,\yy)--(5.62,\yy);
}
\draw[densely dotted,red,thick] (2.35,0.66) -- (2.35,-0.15) -- (11.3,-0.15);
\node[anchor=west,text=red,font=\scriptsize] at (2.55,0.27) {پیوند فرضی با هدف‌گیریِ برنامه‌ای دیگر: شاهدی به دست نیامد};
\end{tikzpicture}
\caption*{فلش‌های پیوسته از مسیرهای کدِ بررسی‌شده می‌آیند؛ خط نقطه‌چین فقط فرضیهٔ پیوند میان برنامه‌هاست.}
\end{figure}
"""


BACKLOG_FIGURE = r"""
\begin{figure}[htbp]\centering
\begin{tikzpicture}[x=1cm,y=1cm]
\fill[inklight] (-0.1,-0.15) rectangle (14.8,2.75);
\node[anchor=east,text=ink,font=\bfseries] at (14.2,2.2) {صف آینده: هدف‌های ۲۰۲۳ تا ۲۰۲۶ در ده برنامه};
\fill[teal] (1.1,1.1) rectangle (6.15,1.55);
\fill[coral] (6.15,1.1) rectangle (13.8,1.55);
\node[text=teal,font=\bfseries] at (3.6,0.65) {۱۴۵ هدف دارای APK};
\node[text=coral,font=\bfseries] at (9.9,0.65) {۲۱۷ هدف نیازمند APK};
\end{tikzpicture}
\caption*{هدف نسخه/ساخت با فایل APK یکی نیست؛ این اعداد طبقه‌بندیِ فهرست است، نه نتیجهٔ ممیزی کد.}
\end{figure}
"""


def document(body: str) -> str:
    font_path = FONT_DIR.as_posix() + "/"
    return r"""\documentclass[10pt,a4paper]{article}
\usepackage[a4paper,top=21mm,bottom=21mm,left=18mm,right=18mm,headheight=20pt]{geometry}
\usepackage{fontspec}
\usepackage{xcolor}
\usepackage{tikz}
\usepackage{longtable,booktabs,array,colortbl}
\usepackage{fancyhdr}
\usepackage{enumitem}
\usepackage{caption}
\usepackage[most]{tcolorbox}
\usepackage{titlesec}
\usepackage{fancyvrb}
\usepackage{needspace}
\usepackage{hyperref}
\usepackage{xepersian}
\settextfont[Path=""" + font_path + r""",Extension=.ttf,BoldFont=Vazirmatn-Bold]{Vazirmatn-Regular}
\setlatintextfont{Arial}
\setmonofont{Menlo}
\let\originaltexttt\texttt
\renewcommand{\texttt}[1]{\textcolor{linkblue}{\lr{\originaltexttt{#1}}}}
\definecolor{ink}{HTML}{17202A}
\definecolor{inklight}{HTML}{F1F4F6}
\definecolor{grayline}{HTML}{BAC8CE}
\definecolor{red}{HTML}{D84347}
\definecolor{teal}{HTML}{0B9D99}
\definecolor{coral}{HTML}{E66D59}
\definecolor{purple}{HTML}{7651B2}
\definecolor{linkblue}{HTML}{087884}
\hypersetup{colorlinks=true,urlcolor=linkblue,linkcolor=teal,pdftitle={از پوش تا موقعیت مکانی},pdfauthor={Hamid Kashfi},pdfsubject={Iranian mobile app companion research, Persian edition v2.1}}
\renewcommand{\arraystretch}{1.37}
\setlength{\tabcolsep}{4pt}
\arrayrulecolor{grayline}
\setlength{\parindent}{0pt}
\setlength{\parskip}{5pt}
\linespread{1.20}
\sloppy
\setlist[itemize]{rightmargin=1.2em,topsep=3pt,itemsep=1pt}
\setlist[enumerate]{rightmargin=1.4em,topsep=3pt,itemsep=1pt}
\captionsetup{font=small,labelformat=empty,textfont=it}
\titleformat{\section}{\Large\bfseries\color{ink}}{}{0pt}{}
\titlespacing*{\section}{0pt}{17pt}{6pt}
\titleformat{\subsection}{\large\bfseries\color{teal}}{}{0pt}{}
\titlespacing*{\subsection}{0pt}{12pt}{4pt}
\let\originalsection\section
\renewcommand{\section}[1]{\Needspace{6\baselineskip}\originalsection{#1}}
\let\originalsubsection\subsection
\renewcommand{\subsection}[1]{\Needspace{4\baselineskip}\originalsubsection{#1}}
\newcommand{\hashtext}[2]{{\footnotesize\ttfamily\lr{#1}}\newline{\footnotesize\ttfamily\lr{#2}}}
\pagestyle{fancy}
\fancyhf{}
\fancyhead[R]{\footnotesize\color{grayline} پژوهش تهدیدات موبایل / گزارش همراه}
\fancyhead[L]{\footnotesize\color{grayline} \lr{HAMID KASHFI · 2026}}
\fancyfoot[R]{\footnotesize\color{grayline} از پوش تا موقعیت مکانی}
\fancyfoot[L]{\footnotesize\color{grayline}\thepage}
\renewcommand{\headrulewidth}{0.25pt}
\renewcommand{\footrulewidth}{0pt}
\begin{document}
\begin{titlepage}
\thispagestyle{empty}\color{white}
\begin{tikzpicture}[remember picture,overlay]
\fill[ink] (current page.south west) rectangle (current page.north east);
\fill[red] (current page.north west) rectangle ([xshift=3pt]current page.south west);
\draw[red,line width=0.6pt] ([xshift=-11.0cm,yshift=-10.0cm]current page.north east) circle (5.5cm);
\draw[red!65,line width=0.6pt] ([xshift=-11.0cm,yshift=-10.0cm]current page.north east) circle (4.15cm);
\draw[red!50,line width=0.6pt] ([xshift=-11.0cm,yshift=-10.0cm]current page.north east) circle (2.75cm);
\draw[red!35,line width=0.6pt] ([xshift=-11.0cm,yshift=-10.0cm]current page.north east) circle (1.45cm);
\fill[teal] ([xshift=-13.0cm,yshift=-8.2cm]current page.north east) circle (5pt);
\fill[coral] ([xshift=-6.6cm,yshift=-11.8cm]current page.north east) circle (6pt);
\fill[purple] ([xshift=-9.0cm,yshift=-7.2cm]current page.north east) circle (4pt);
\draw[teal,thick] ([xshift=-13.0cm,yshift=-8.2cm]current page.north east) -- ([xshift=-11.1cm,yshift=-9.6cm]current page.north east);
\draw[coral,thick] ([xshift=-6.6cm,yshift=-11.8cm]current page.north east) -- ([xshift=-8.1cm,yshift=-10.6cm]current page.north east);
\end{tikzpicture}
\vspace*{12mm}
{\color{white}\footnotesize\bfseries پژوهش تهدیدات موبایل \hfill \lr{CASE FILE / 2026}}\par
\vspace{14mm}
{\color{white}\fontsize{32}{46}\selectfont\bfseries از پوش تا\par موقعیت مکانی}\par
\vspace{8mm}
{\color{white}\large مسیرهای فرمان و مکان در بلد، نشان، اسنپ و تپسی}\par
\vspace{4mm}
{\color{grayline}\normalsize خوانشِ محدودِ ۱۰۳ فایل APK مشخص و مرزهای آنچه این فایل‌ها نشان نمی‌دهند}\par
\vfill
\begin{tcolorbox}[enhanced,colback=ink!75!black,colframe=grayline!45,boxrule=.3pt,arc=2mm,left=5mm,right=5mm,top=5mm,bottom=5mm]
\textcolor{teal}{\bfseries ۱۹ فوریه}\hspace{5mm}\textcolor{white}{نشان: ورودیِ فرمان} \hfill
\textcolor{red}{\bfseries ۲۸ فوریه}\hspace{5mm}\textcolor{white}{آغاز جنگ} \hfill
\textcolor{coral}{\bfseries ۱۰ ژوئن}\hspace{5mm}\textcolor{white}{بلد: مسیر ارسال}
\end{tcolorbox}
\vspace{14mm}
{\color{grayline}\small این گزارش همراه، زنجیره‌های کد و فاصله‌های نمونه‌برداری را از ادعای استفادهٔ عملیاتی یا هماهنگی میان برنامه‌ها جدا می‌کند.}\par
\vspace{9mm}
{\color{white}\bfseries حمید کشفی} \hfill {\color{white}\bfseries ۵ اکتبر ۲۰۲۶}\par
{\color{grayline}\small گزارش تولیدشده با یاری مدل زبانی؛ شواهد و محدودیت‌ها در متن آمده‌اند.}\hfill{\color{coral}\small\bfseries \lr{VERSION 2.1 · FA}}\par
\end{titlepage}
\color{ink}
\fontsize{9.4}{15.5}\selectfont
""" + body + "\n\\end{document}\n"


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="iran-mobile-fa-") as folder:
        tmp = Path(folder)
        source = tmp / "companion_fa.tex"
        source.write_text(document(convert_body(tmp)))
        for _ in range(2):
            run("xelatex", "-interaction=nonstopmode", "-halt-on-error", f"-output-directory={tmp}", str(source), cwd=tmp)
        OUTPUT.write_bytes((tmp / "companion_fa.pdf").read_bytes())
    print(OUTPUT)


if __name__ == "__main__":
    main()
