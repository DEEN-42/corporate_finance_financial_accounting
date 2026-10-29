"""Small python-docx helpers: Times New Roman 12 pt, 1.5 line spacing, captioned tables."""
import os
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, Cm, RGBColor

FONT = 'Times New Roman'


def new_document():
    doc = Document()
    sec = doc.sections[0]
    sec.page_height, sec.page_width = Cm(29.7), Cm(21.0)
    sec.left_margin = sec.right_margin = Cm(2.3)
    sec.top_margin = sec.bottom_margin = Cm(2.2)
    st = doc.styles['Normal']
    st.font.name = FONT; st.font.size = Pt(12)
    st.element.rPr.rFonts.set(qn('w:eastAsia'), FONT)
    pf = st.paragraph_format
    pf.line_spacing = 1.5; pf.space_after = Pt(4); pf.space_before = Pt(0)
    for name, size in [('Heading 1', 14), ('Heading 2', 12), ('Heading 3', 12)]:
        h = doc.styles[name]
        h.font.name = FONT; h.font.size = Pt(size); h.font.bold = True; h.font.italic = False
        h.font.color.rgb = RGBColor(0, 0, 0)
        rpr = h.element.get_or_add_rPr(); rf = rpr.find(qn('w:rFonts'))
        if rf is None:
            rf = OxmlElement('w:rFonts'); rpr.append(rf)
        for a in ('w:ascii', 'w:hAnsi', 'w:eastAsia', 'w:cs'):
            rf.set(qn(a), FONT)
        h.paragraph_format.space_before = Pt(10 if name == 'Heading 1' else 6)
        h.paragraph_format.space_after = Pt(4)
        h.paragraph_format.line_spacing = 1.5
        h.paragraph_format.keep_with_next = True
    add_page_number(sec)
    return doc


def add_page_number(section):
    p = section.footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    for kind, text in [('begin', None), (None, 'PAGE'), ('end', None)]:
        if kind:
            el = OxmlElement('w:fldChar'); el.set(qn('w:fldCharType'), kind)
        else:
            el = OxmlElement('w:instrText'); el.set(qn('xml:space'), 'preserve'); el.text = text
        run._r.append(el)
    run.font.size = Pt(10); run.font.name = FONT


def para(doc, text='', bold_lead=None, align='justify', size=None, italic=False, space_after=None, indent=False):
    p = doc.add_paragraph()
    if align == 'justify':
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    elif align == 'center':
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if bold_lead:
        r = p.add_run(bold_lead + ' '); r.bold = True
        if size: r.font.size = Pt(size)
    r = p.add_run(text); r.italic = italic
    if size:
        r.font.size = Pt(size)
    if space_after is not None:
        p.paragraph_format.space_after = Pt(space_after)
    if indent:
        p.paragraph_format.left_indent = Cm(0.8); p.paragraph_format.first_line_indent = Cm(-0.8)
    return p


def caption(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.keep_with_next = True
    p.paragraph_format.space_before = Pt(6); p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.15
    lead, _, rest = text.partition('. ')
    r = p.add_run(lead + '. '); r.bold = True; r.font.size = Pt(11)
    r = p.add_run(rest); r.font.size = Pt(11)
    return p


def note(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.0; p.paragraph_format.space_after = Pt(6)
    r = p.add_run(text); r.italic = True; r.font.size = Pt(9.5)
    return p


def _shade(cell, hexcolor):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd'); shd.set(qn('w:val'), 'clear'); shd.set(qn('w:color'), 'auto'); shd.set(qn('w:fill'), hexcolor)
    tcPr.append(shd)


def _borders(table):
    tbl = table._tbl
    tblPr = tbl.tblPr
    b = OxmlElement('w:tblBorders')
    for edge, val in [('top', 'single'), ('bottom', 'single'), ('insideH', 'nil'), ('insideV', 'nil'), ('left', 'nil'), ('right', 'nil')]:
        e = OxmlElement(f'w:{edge}'); e.set(qn('w:val'), val); e.set(qn('w:sz'), '8'); e.set(qn('w:color'), '000000')
        b.append(e)
    tblPr.append(b)


def table(doc, header, rows, widths=None, size=9.5, first_col_left=True, bold_rows=()):
    size = max(size, float(os.environ.get('MIN_TABLE_PT', 0)))
    t = doc.add_table(rows=1 + len(rows), cols=len(header))
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    _borders(t)
    for i, row in enumerate([header] + rows):
        for j, val in enumerate(row):
            c = t.cell(i, j)
            c.text = ''
            p = c.paragraphs[0]
            p.paragraph_format.line_spacing = 1.0
            p.paragraph_format.space_after = Pt(1); p.paragraph_format.space_before = Pt(1)
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if (j == 0 and first_col_left) else WD_ALIGN_PARAGRAPH.CENTER
            r = p.add_run(str(val)); r.font.size = Pt(size); r.font.name = FONT
            if i == 0 or i in bold_rows:
                r.bold = True
            if i == 0:
                _shade(c, 'E7E6E6')
                # bottom border under header
                tcPr = c._tc.get_or_add_tcPr(); tb = OxmlElement('w:tcBorders')
                e = OxmlElement('w:bottom'); e.set(qn('w:val'), 'single'); e.set(qn('w:sz'), '6'); e.set(qn('w:color'), '000000')
                tb.append(e); tcPr.append(tb)
    if widths:
        for j, w in enumerate(widths):
            for i in range(len(rows) + 1):
                t.cell(i, j).width = Cm(w)
    return t


def figure(doc, path, width_cm=15.5):
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.keep_with_next = True; p.paragraph_format.line_spacing = 1.0
    p.add_run().add_picture(path, width=Cm(width_cm))
    return p


def page_break(doc):
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
