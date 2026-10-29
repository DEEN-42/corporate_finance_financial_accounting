"""Assemble the Word report from results.json, the figures and report_text.py.
Run after zscore_analysis.py:  python build_report.py"""
import json, os
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH

import docx_helpers as H
import report_text as T
import report_results as RR
import report_sections as RS

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FIG = os.path.join(ROOT, 'figures')
R = json.load(open(os.path.join(HERE, 'results.json')))


def cover(doc):
    for _ in range(3):
        doc.add_paragraph()
    H.para(doc, T.COURSE, align='center', size=13)
    p = H.para(doc, '', align='center')
    r = p.add_run(T.TITLE); r.bold = True; r.font.size = Pt(18)
    p.paragraph_format.space_before = Pt(18); p.paragraph_format.space_after = Pt(18)
    H.para(doc, T.AREA, align='center', italic=True)
    doc.add_paragraph()
    H.para(doc, 'Submitted by', align='center', size=12).runs[0].bold = True
    t = H.table(doc, ['Team member', 'Roll number'], [[n, r_] for n, r_ in T.TEAM], widths=[7, 4], size=12)
    doc.add_paragraph()
    H.para(doc, 'Base paper', align='center').runs[0].bold = True
    H.para(doc, T.BASE_PAPER, align='center', size=11)
    doc.add_paragraph()
    H.para(doc, 'October 2026', align='center')
    H.page_break(doc)


def main():
    doc = H.new_document()
    cover(doc)

    doc.add_heading('Abstract', level=1)
    H.para(doc, RS.abstract(R))
    H.para(doc, 'Keywords: Altman Z-score; financial distress; Insolvency and Bankruptcy Code; discriminant '
                'analysis; logistic regression; India; investment screening.', italic=True)

    doc.add_heading('1. Introduction', level=1)
    for ptxt in T.INTRO:
        H.para(doc, ptxt)

    doc.add_heading('2. Literature Review', level=1)
    for lead, ptxt in T.LIT:
        H.para(doc, ptxt, bold_lead=lead)
    RR.lit_table(doc)

    doc.add_heading('3. Research Questions and Focus of the Work', level=1)
    H.para(doc, 'The work focuses on one practical question: is Altman\'s Z-score, built in 1968 on US '
                'manufacturers, a reliable screening tool for an investor evaluating Indian listed companies today? '
                'This question is split into four research questions.')
    for k, q in T.RQ:
        H.para(doc, q, bold_lead=k + '.', indent=True)
    H.para(doc, T.HYP)

    doc.add_heading('4. Dataset and Methodology', level=1)
    RR.data_section(doc, R)
    RR.method_section(doc, R)

    doc.add_heading('5. Results', level=1)
    RS.descriptive(doc, R, FIG)
    RS.tests(doc, R)
    RS.classification(doc, R, FIG)
    RS.mda(doc, R)
    RS.logit(doc, R)
    RS.comparison(doc, R, FIG)
    RS.investment(doc, R)

    doc.add_heading('6. Conclusion', level=1)
    RS.conclusion(doc, R)

    doc.add_heading('References', level=1)
    for ref in T.REFS:
        p = H.para(doc, ref, align='left', size=11, indent=True)
        p.paragraph_format.line_spacing = 1.15; p.paragraph_format.space_after = Pt(3)
    H.para(doc, 'Data sources: Screener.in standalone financial statements and NSE price history '
                '(https://www.screener.in); LSEG standalone annual-report data as published on Sharpely.in '
                '(https://sharpely.in); company annual reports from the BSE archive (https://www.bseindia.com) and '
                'company websites; '
                'NCLT admission orders as reported in company stock-exchange filings, the Insolvency and Bankruptcy '
                'Board of India order listings (https://ibbi.gov.in) and the financial press cited in the '
                'Appendix. Accessed October 2026.', align='left', size=11)

    doc.add_heading('Appendix: Sample Firms and Event Dates', level=1)
    RS.appendix(doc, R)

    out = os.path.join(ROOT, 'CFFM_Altman_Z_Score_Report.docx')
    doc.save(out)
    print('saved', out)


if __name__ == '__main__':
    main()
