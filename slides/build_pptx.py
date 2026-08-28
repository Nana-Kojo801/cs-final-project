"""Build slides/CS112_Team3_Presentation.pptx from slides/presentation.md.

Run:  python slides/build_pptx.py
Requires: python-pptx  (pip install python-pptx)
"""

import os
import re

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

HERE = os.path.dirname(os.path.abspath(__file__))
MD = os.path.join(HERE, "presentation.md")
OUT = os.path.join(HERE, "CS112_Team3_Presentation.pptx")

# palette
INK = RGBColor(0x1C, 0x27, 0x33)
ACCENT = RGBColor(0x25, 0x63, 0xEB)
ACCENT2 = RGBColor(0x0D, 0x94, 0x88)
MUTED = RGBColor(0x5B, 0x6B, 0x7D)
BG = RGBColor(0xFF, 0xFF, 0xFF)
BAND = RGBColor(0xF1, 0xF5, 0xFB)

SW, SH = Inches(13.333), Inches(7.5)


def strip_md(text):
    """Very small inline-markdown cleaner: **b** *i* `code` -> plain, keep text."""
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"\*(.+?)\*", r"\1", text)
    text = re.sub(r"`(.+?)`", r"\1", text)
    text = text.replace("→", "->").replace("∝", "~").replace("≈", "~").replace("≥", ">=")
    return text.strip()


def parse(md_text):
    # drop YAML frontmatter
    if md_text.startswith("---"):
        md_text = md_text.split("---", 2)[2]
    raw_slides = re.split(r"(?m)^---\s*$", md_text)
    slides = []
    for chunk in raw_slides:
        chunk = re.sub(r"<!--.*?-->", "", chunk, flags=re.S).strip()
        if not chunk:
            continue
        lines = chunk.split("\n")
        title, level = None, 2
        body = []  # list of ('bullet', text, indent) / ('para', text) / ('table', rows) / ('image', path) / ('num', text)
        i = 0
        tbl = []
        while i < len(lines):
            ln = lines[i].rstrip()
            m = re.match(r"^(#{1,6})\s+(.*)", ln)
            if m and title is None:
                level = len(m.group(1))
                title = strip_md(m.group(2))
                i += 1
                continue
            img = re.match(r"^!\[[^\]]*\]\(([^)]+)\)", ln)
            if img:
                body.append(("image", img.group(1)))
                i += 1
                continue
            if ln.startswith("|"):
                tbl.append(ln)
                if i + 1 >= len(lines) or not lines[i + 1].rstrip().startswith("|"):
                    rows = []
                    for r in tbl:
                        cells = [c.strip() for c in r.strip().strip("|").split("|")]
                        if set("".join(cells)) <= set("-: "):
                            continue
                        rows.append([strip_md(c) for c in cells])
                    if rows:
                        body.append(("table", rows))
                    tbl = []
                i += 1
                continue
            bm = re.match(r"^(\s*)[-*]\s+(.*)", ln)
            if bm:
                indent = len(bm.group(1)) // 2
                body.append(("bullet", strip_md(bm.group(2)), indent))
                i += 1
                continue
            nm = re.match(r"^\s*\d+\.\s+(.*)", ln)
            if nm:
                body.append(("num", strip_md(nm.group(1))))
                i += 1
                continue
            if ln.strip():
                body.append(("para", strip_md(ln.strip())))
            i += 1
        slides.append((title, level, body))
    return slides


def add_bg(slide):
    r = slide.shapes.add_shape(1, 0, 0, SW, SH)
    r.fill.solid()
    r.fill.fore_color.rgb = BG
    r.line.fill.background()
    r.shadow.inherit = False
    slide.shapes._spTree.remove(r._element)
    slide.shapes._spTree.insert(2, r._element)


def title_slide(prs, title, body):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(s)
    band = s.shapes.add_shape(1, 0, Inches(2.4), SW, Inches(0.12))
    band.fill.solid(); band.fill.fore_color.rgb = ACCENT; band.line.fill.background()
    band.shadow.inherit = False

    tb = s.shapes.add_textbox(Inches(0.9), Inches(2.7), Inches(11.5), Inches(1.6))
    tf = tb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.text = title
    p.font.size = Pt(38); p.font.bold = True; p.font.color.rgb = INK

    sub = s.shapes.add_textbox(Inches(0.9), Inches(4.4), Inches(11.5), Inches(2.3))
    stf = sub.text_frame; stf.word_wrap = True
    first = True
    for kind, *rest in body:
        txt = rest[0]
        para = stf.paragraphs[0] if first else stf.add_paragraph()
        first = False
        para.text = txt
        para.font.size = Pt(18)
        para.font.color.rgb = MUTED if txt.startswith("github") else INK
        para.space_after = Pt(6)


def content_slide(prs, title, body):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(s)
    # header band
    band = s.shapes.add_shape(1, 0, 0, SW, Inches(1.05))
    band.fill.solid(); band.fill.fore_color.rgb = BAND; band.line.fill.background()
    band.shadow.inherit = False
    bar = s.shapes.add_shape(1, 0, Inches(1.05), SW, Inches(0.05))
    bar.fill.solid(); bar.fill.fore_color.rgb = ACCENT; bar.line.fill.background()
    bar.shadow.inherit = False

    ht = s.shapes.add_textbox(Inches(0.7), Inches(0.18), Inches(12), Inches(0.75))
    hp = ht.text_frame.paragraphs[0]; hp.text = title
    hp.font.size = Pt(26); hp.font.bold = True; hp.font.color.rgb = INK

    images = [r[0] for k, *r in body if k == "image"]
    tables = [r[0] for k, *r in body if k == "table"]
    text_items = [(k, r) for k, *r in body if k in ("bullet", "para", "num")]

    text_w = Inches(7.4) if images else Inches(12.0)
    body_top = Inches(1.4)
    tb = s.shapes.add_textbox(Inches(0.7), body_top, text_w, Inches(5.6))
    tf = tb.text_frame; tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.TOP
    first = True
    for kind, rest in text_items:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        if kind == "bullet":
            text, indent = rest[0], rest[1]
            p.text = ("- " if indent == 0 else "  - ") + text
            p.font.size = Pt(17 if indent == 0 else 14)
            p.level = indent
        elif kind == "num":
            p.text = rest[0]
            p.font.size = Pt(16)
        else:  # para
            p.text = rest[0]
            p.font.size = Pt(15)
            p.font.italic = rest[0].startswith("(") or rest[0].endswith(")")
            p.font.color.rgb = ACCENT2 if rest[0].startswith(("Solution", "Recommendation",
                                                              "This grid", "Administrative",
                                                              "Cohort")) else INK
        p.space_after = Pt(7)

    # table
    for rows in tables:
        nr, nc = len(rows), max(len(r) for r in rows)
        gt = s.shapes.add_table(nr, nc, Inches(0.7), Inches(1.5) if not text_items else Inches(4.4),
                                text_w, Inches(0.4 * nr)).table
        for ci in range(nc):
            gt.columns[ci].width = int(text_w / nc)
        for ri, row in enumerate(rows):
            for ci in range(nc):
                cell = gt.cell(ri, ci)
                cell.text = row[ci] if ci < len(row) else ""
                para = cell.text_frame.paragraphs[0]
                para.font.size = Pt(12)
                para.font.bold = (ri == 0)
                if ri == 0:
                    cell.fill.solid(); cell.fill.fore_color.rgb = ACCENT
                    para.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
                else:
                    cell.fill.solid()
                    cell.fill.fore_color.rgb = RGBColor(0xFF, 0xFF, 0xFF) if ri % 2 else BAND

    # image on the right
    if images:
        path = os.path.normpath(os.path.join(HERE, images[0]))
        if os.path.exists(path):
            s.shapes.add_picture(path, Inches(8.4), Inches(1.5), width=Inches(4.4))
        else:
            note = s.shapes.add_textbox(Inches(8.4), Inches(3.0), Inches(4.4), Inches(1))
            note.text_frame.paragraphs[0].text = "[chart: %s]" % os.path.basename(images[0])
            note.text_frame.paragraphs[0].font.size = Pt(11)
            note.text_frame.paragraphs[0].font.color.rgb = MUTED


def main():
    with open(MD, encoding="utf-8") as f:
        slides = parse(f.read())
    prs = Presentation()
    prs.slide_width = SW
    prs.slide_height = SH
    for idx, (title, level, body) in enumerate(slides):
        if idx == 0 or level == 1:
            title_slide(prs, title, body)
        else:
            content_slide(prs, title, body)
    prs.save(OUT)
    print("wrote %s  (%d slides)" % (OUT, len(slides)))


if __name__ == "__main__":
    main()
