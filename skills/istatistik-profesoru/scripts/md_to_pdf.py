# Oluşturma: 20260725 0053
"""Markdown -> PDF converter for the istatistik-profesoru skill.

Solves the two failure modes that plain converters hit on Turkish medical reports:

1. **Boxes instead of Ş/Ğ/İ/ı** — a TrueType font with Turkish coverage is
   registered explicitly; the reportlab default (Helvetica) is never relied on.
2. **Missing charts** — image paths are resolved against ``md_dir`` and made
   absolute, so a converter running from another working directory still finds them.

It also renders inline Markdown emphasis (``*p*`` -> italic, ``**x**`` -> bold,
`` `code` `` -> monospace), which the style guides require for the italic *p*.

Supported Markdown subset: ``#``/``##``/``###`` headings, ``|`` pipe tables,
fenced code blocks, ``![alt](path)`` images, ``> `` notes, ``- `` bullets,
paragraphs, and the inline emphasis above.

Usage as a library::

    from md_to_pdf import md_to_pdf
    md_to_pdf(report1_md, os.path.join(OUT_DIR, "Rapor1 20260725 0053.pdf"), md_dir=OUT_DIR)

Usage from the shell::

    python md_to_pdf.py "Rapor1 20260725 0053.md" "Rapor1 20260725 0053.pdf"
"""

import os
import re
import sys

# Font candidates, searched in order. First pair that exists wins.
FONT_CANDIDATES = [
    (r"C:\Windows\Fonts\arial.ttf", r"C:\Windows\Fonts\arialbd.ttf",
     r"C:\Windows\Fonts\ariali.ttf"),                                            # Windows
    ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
     "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
     "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf"),                 # Linux
    ("/System/Library/Fonts/Supplemental/Arial.ttf",
     "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
     "/System/Library/Fonts/Supplemental/Arial Italic.ttf"),                     # macOS
]


def _inline(text):
    """Escape XML, then turn Markdown emphasis into reportlab inline tags.

    Order matters: escaping first would otherwise mangle the tags we emit.
    Bold is matched before italic so ``**x**`` does not decay into ``*<i>x</i>*``.
    """
    text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'\*([^*\n]+?)\*', r'<i>\1</i>', text)
    text = re.sub(r'`([^`\n]+?)`', r'<font face="Courier">\1</font>', text)
    return text


def md_to_pdf(md_text, out_path, md_dir=None):
    """Render ``md_text`` to ``out_path``.

    md_dir: base folder for resolving relative image paths inside the markdown
    (if omitted, image paths are expected to be absolute).
    Returns True on success.
    """
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib import colors
    from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle,
                                    Paragraph, Spacer, HRFlowable, Image)
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    # --- Register a font with Turkish-character support (cross-platform search) ---
    F, FB, FI = 'Helvetica', 'Helvetica-Bold', 'Helvetica-Oblique'
    for reg, bold, italic in FONT_CANDIDATES:
        if os.path.exists(reg) and os.path.exists(bold):
            pdfmetrics.registerFont(TTFont('TR', reg))
            pdfmetrics.registerFont(TTFont('TRB', bold))
            F, FB, FI = 'TR', 'TRB', 'TRB'
            if os.path.exists(italic):
                pdfmetrics.registerFont(TTFont('TRI', italic))
                FI = 'TRI'
            # Bind the family so <b>/<i> inside a Paragraph resolve correctly.
            pdfmetrics.registerFontFamily('TR', normal='TR', bold='TRB',
                                          italic=FI, boldItalic=FB)
            break
    if F == 'Helvetica':
        print("WARNING: No font with Turkish-character support found, using Helvetica — "
              "characters like Ş/Ğ/İ/ı may appear incorrectly.")

    H1 = ParagraphStyle('H1', fontName=FB, fontSize=13, spaceAfter=8, alignment=1,
                        textColor=colors.HexColor('#1F3864'))
    H2 = ParagraphStyle('H2', fontName=FB, fontSize=10, spaceAfter=4, spaceBefore=10,
                        textColor=colors.HexColor('#2E4DA0'))
    H3 = ParagraphStyle('H3', fontName=FB, fontSize=9, spaceAfter=3, spaceBefore=6,
                        textColor=colors.HexColor('#4472C4'))
    BODY = ParagraphStyle('B', fontName=F, fontSize=8.5, spaceAfter=3, leading=12)
    CODE = ParagraphStyle('C', fontName='Courier', fontSize=7.5, spaceAfter=4,
                          backColor=colors.HexColor('#F5F5F5'), leading=11)
    NOTE = ParagraphStyle('N', fontName=F, fontSize=7.5, textColor=colors.grey, spaceBefore=6)

    doc = SimpleDocTemplate(out_path, pagesize=landscape(A4),
                            leftMargin=1.5 * cm, rightMargin=1.5 * cm,
                            topMargin=1.5 * cm, bottomMargin=1.5 * cm)
    elems = []
    page_w = landscape(A4)[0] - 3 * cm

    in_code, code_buf = False, []
    table_rows, in_table = [], False
    img_count = 0

    def flush_table():
        nonlocal table_rows, in_table
        if not (in_table and table_rows):
            return
        col_count = max(len(r) for r in table_rows)
        col_w = [page_w / col_count] * col_count
        tbl_data = [[Paragraph(_inline(c), BODY) for c in tr] for tr in table_rows]
        tbl = Table(tbl_data, colWidths=col_w[:len(table_rows[0])], repeatRows=1)
        tbl.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E4DA0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), FB),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('FONTNAME', (0, 1), (-1, -1), F),
            ('GRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#CCCCCC')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#EEF2FF')]),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elems.append(tbl)
        elems.append(Spacer(1, 0.3 * cm))
        table_rows = []
        in_table = False

    for line in md_text.split('\n'):
        if line.strip().startswith('```'):
            if not in_code:
                in_code, code_buf = True, []
            else:
                in_code = False
                if code_buf:
                    elems.append(Paragraph('<br/>'.join(code_buf), CODE))
            continue
        if in_code:
            code_buf.append(line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))
            continue

        # Image: ![caption](path)
        img_match = re.match(r'!\[(.*?)\]\((.*?)\)', line.strip())
        if img_match:
            flush_table()
            path = img_match.group(2)
            full_path = path if os.path.isabs(path) else os.path.join(md_dir or '', path)
            full_path = os.path.abspath(full_path)
            if os.path.exists(full_path):
                img = Image(full_path)
                ratio = min(page_w / img.drawWidth, 1.0)
                img.drawWidth *= ratio
                img.drawHeight *= ratio
                elems.append(img)
                elems.append(Spacer(1, 0.2 * cm))
                img_count += 1
            else:
                elems.append(Paragraph(f"[Image not found: {path}]", NOTE))
            continue

        if line.startswith('|'):
            if '---' in line:
                continue
            table_rows.append([c.strip() for c in line.strip('|').split('|')])
            in_table = True
            continue
        else:
            flush_table()

        if line.startswith('# '):
            elems.append(Paragraph(_inline(line[2:]), H1))
            elems.append(HRFlowable(width='100%', thickness=1,
                                    color=colors.HexColor('#2E4DA0'), spaceAfter=6))
        elif line.startswith('## '):
            elems.append(Paragraph(_inline(line[3:]), H2))
        elif line.startswith('### '):
            elems.append(Paragraph(_inline(line[4:]), H3))
        elif line.startswith('> '):
            elems.append(Paragraph(_inline(line[2:]), NOTE))
        elif line.startswith('- '):
            elems.append(Paragraph(f"• {_inline(line[2:])}", BODY))
        elif line.strip():
            elems.append(Paragraph(_inline(line), BODY))
        elif elems:
            elems.append(Spacer(1, 0.2 * cm))

    flush_table()
    doc.build(elems)
    print(f"PDF created: {out_path} ({img_count} images embedded)")
    return True


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python md_to_pdf.py <input.md> <output.pdf>")
        raise SystemExit(2)
    src, dst = sys.argv[1], sys.argv[2]
    with open(src, encoding="utf-8") as fh:
        md_to_pdf(fh.read(), dst, md_dir=os.path.dirname(os.path.abspath(src)))
