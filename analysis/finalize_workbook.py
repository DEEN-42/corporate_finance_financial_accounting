"""Turn the raw pandas output Z_Score_Dataset.xlsx into a submission-ready workbook:
README + data dictionary + expanded Sources sheets, formatted headers/widths/number formats,
and live formulas for every derived column (EBIT, total liabilities, book equity, market value,
X1-X5, Z, Z'', zones, EM score) so the calculations can be audited in Excel.
Run automatically at the end of zscore_analysis.py (or: python finalize_workbook.py)."""
import json, os
from openpyxl import load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter as L

from ar_data import AR
from sample import EXCLUDED

HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(os.path.dirname(HERE), 'Z_Score_Dataset.xlsx')
RAW, RAT = 'Raw financials (Rs crore)', 'Ratios and scores'
HDR_FILL = PatternFill('solid', fgColor='1F3864')
HDR_FONT = Font(name='Calibri', bold=True, color='FFFFFF', size=10)
BODY = Font(name='Calibri', size=10)
THIN = Side(style='thin', color='BFBFBF')
SHADE = PatternFill('solid', fgColor='F2F2F2')
EXCL = PatternFill('solid', fgColor='FCE4D6')

DICT = {
    # --- sample / raw
    'pair': 'Matched-pair number (1-15). A distressed firm and its healthy peer share a pair number.',
    'distressed': 'Name of the company admitted to CIRP.', 'healthy_peer': 'Matched healthy company, same industry.',
    'screener_symbol_d': 'Screener.in / NSE symbol of the distressed firm (some are the current symbol after a rename, e.g. TATASTLBSL = Bhushan Steel, PATANJALI = Ruchi Soya).',
    'screener_symbol_h': 'Screener.in / NSE symbol of the healthy peer.', 'industry': 'Industry used for matching.',
    'cirp_admission': 'Date the NCLT admitted the company into the Corporate Insolvency Resolution Process (event date).',
    't1_fiscal_year': 't-1 = last fiscal year (ending 31 March) closed at least 90 days before the admission; Future Retail uses FY2021 (FY2022 results delayed).',
    'admission_source': 'Source of the admission date (NCLT order as reported in filings / IBBI / press).',
    'in_sample': 'TRUE if the pair and firm-year have complete data and enter the statistical tests (85 of 90 firm-years).',
    'name': 'Company name.', 'symbol': 'Screener.in / NSE symbol.', 'group': 'Distressed (admitted to CIRP) or Healthy (peer).',
    'lag': 'Years before the event: 1 = t-1, 2 = t-2, 3 = t-3.', 'fy': 'Fiscal year ending 31 March of that year.',
    'admission': 'CIRP admission date of the distressed firm in the pair.',
    'sales': 'Revenue from operations, Rs crore (standalone).', 'pbt': 'Profit before tax, Rs crore.',
    'interest': 'Interest expense, Rs crore.', 'ebit': 'EBIT = profit before tax + interest (formula).',
    'net_profit': 'Net profit, Rs crore.', 'eps': 'Earnings per share, Rs.',
    'equity_capital': 'Equity share capital, Rs crore.', 'reserves': "Reserves and surplus (other equity) - proxy for retained earnings, Rs crore.",
    'borrowings': 'Total borrowings, Rs crore.', 'other_liabilities': 'Other liabilities (all non-borrowing liabilities), Rs crore.',
    'total_liabilities': 'Total liabilities = borrowings + other liabilities (formula).', 'total_assets': 'Total assets, Rs crore (Screener.in standalone).',
    'tca': 'Reported total current assets, Rs crore.', 'tcl': 'Reported total current liabilities, Rs crore.',
    'ta_wc': 'Total assets from the same source as tca/tcl (denominator of X1).',
    'wc_source': 'Where tca, tcl and ta_wc come from (LSEG standalone data, company annual report with page, or Sharpely table).',
    'lseg_ta': 'Total assets from LSEG (cross-check of Screener.in).', 'lseg_revenue': 'Revenue from LSEG (cross-check).',
    'lseg_pbt': 'Profit before tax from LSEG (cross-check).', 'lseg_re': 'Retained earnings from LSEG (cross-check).',
    'price': 'NSE closing price on or before 31 March of the fiscal year (adjusted for corporate actions), Rs.',
    'price_date': 'Date of that closing price.', 'shares_cr': 'Shares outstanding, crore, on the same adjustment basis as price.',
    'shares_source': 'Source of the share count (LSEG basic weighted shares, or net profit / EPS).',
    'mve': 'Market value of equity = price x shares, Rs crore (formula).', 'book_equity': 'Book equity = equity capital + reserves (formula).',
    # --- ratios
    'X1': 'Working capital / total assets = (tca - tcl) / ta_wc (formula).', 'X2': 'Retained earnings / total assets = reserves / total_assets (formula).',
    'X3': 'EBIT / total assets (formula).', 'X4': 'Market value of equity / total liabilities (formula).',
    'X4_book': 'Book equity / total liabilities (formula); used in Z-double-prime.', 'X5': 'Sales / total assets (formula).',
    'Z': 'Altman (1968) Z = 1.2 X1 + 1.4 X2 + 3.3 X3 + 0.6 X4 + 1.0 X5 (formula).',
    'Z_zone': 'Distress if Z < 1.81, Grey if 1.81 <= Z < 2.99, Safe if Z >= 2.99.',
    'Z_book': 'Z computed with book equity in X4 (robustness check).',
    'Zpp': "Altman Z'' = 6.56 X1 + 3.26 X2 + 6.72 X3 + 1.05 X4_book (emerging-market / non-manufacturer form, no constant).",
    'Zpp_zone': "Distress if Z'' < 1.10, Grey if 1.10 <= Z'' < 2.60, Safe if Z'' >= 2.60.",
    'EM': "Z'' + 3.25 (bond-rating-equivalent form of the emerging-market score; does not change classification).",
    # --- stats
    'var': 'Variable: X1-X5, Z or Zpp.', 'n': 'Number of observations.', 'mean': 'Mean.', 'median': 'Median.', 'sd': 'Standard deviation.',
    'min': 'Minimum.', 'max': 'Maximum.', 'n_pairs': 'Number of matched pairs with data.',
    'mean_d': 'Mean of distressed group.', 'mean_h': 'Mean of healthy group.', 'mean_diff': 'Mean within-pair difference (distressed - healthy).',
    'ci_lo': 'Bootstrap 95% CI of mean difference, lower.', 'ci_hi': 'Bootstrap 95% CI of mean difference, upper.',
    'shapiro_d': 'Shapiro-Wilk p-value, distressed group.', 'shapiro_h': 'Shapiro-Wilk p-value, healthy group.',
    'paired_t': 'Paired t statistic (raw ratios).', 'paired_p': 'Paired t-test p-value (raw ratios).',
    'paired_tw': 'Paired t statistic (ratios winsorised at pooled 5th/95th percentile).', 'paired_pw': 'Paired t-test p-value (winsorised).',
    'welch_t': 'Welch two-sample t statistic.', 'welch_p': 'Welch two-sample t-test p-value.',
    'wilcoxon_p': 'Wilcoxon signed-rank test p-value (paired).', 'mw_p': 'Mann-Whitney U test p-value.', 'cohen_d': "Cohen's d (distressed - healthy).",
    'tp': 'Distressed firms correctly flagged.', 'fn': 'Distressed firms missed (Type I errors).', 'tn': 'Healthy firms correctly passed.',
    'fp': 'Healthy firms wrongly flagged (Type II errors).', 'n1': 'Number of distressed firms.', 'n0': 'Number of healthy firms.',
    'type1': 'Type I error rate = fn / n1.', 'type2': 'Type II error rate = fp / n0.', 'acc': 'Overall accuracy.',
    'model': 'Model tested (Z or Zpp).', 'rule': 'Classification rule (cut-off and treatment of the grey zone).',
    'lda_score': 'Re-estimated discriminant score (in-sample, t-1).', 'lda_loo': 'Leave-one-out discriminant score (positive = distressed side).',
    'p_logit': 'Fitted probability of distress, logit on X1-X5 (Firth).', 'p_logit_loo': 'Leave-one-out probability of distress.',
    'company': 'Distressed company.', 'peer': 'Healthy peer.', 'd_p_t1': 'Distressed share price at end of t-1, Rs.',
    'd_p_adm': 'Distressed share price on last trading day before admission, Rs.', 'd_ret': 'Distressed share return, t-1 year-end to admission.',
    'h_p_t1': 'Peer share price at end of t-1, Rs.', 'h_p_adm': 'Peer price on same pre-admission date, Rs.', 'h_ret': 'Peer return over the same window.',
    'Z3': 'Z-score of the distressed firm at t-3.', 'Z2': 'Z-score at t-2.', 'Z1': 'Z-score at t-1.',
    'item': 'Item.', 'source': 'Source.',
}
NOTES = {'Sample': 'The 15 matched pairs and their CIRP admission dates.',
         RAW: 'Raw standalone figures (Rs crore). Grey-shaded derived columns are Excel formulas. Rows shaded orange are excluded from the tests because data are incomplete.',
         RAT: 'Ratios, scores and zones for every firm-year. All ratio columns are live formulas on the raw sheet.',
         'Descriptive stats': 'Mean, median, SD, min, max by group and horizon (in-sample firm-years, raw values). Report Table 3.',
         'Hypothesis tests': 'Paired t, Welch, Wilcoxon and Mann-Whitney tests by horizon. Report Table 4.',
         'Classification': 'Confusion counts and error rates for each cut-off rule. Report Table 5.',
         'Model scores t-1': 'Scores and probabilities of every firm at t-1 under each model. Report Tables 6-8.',
         'Price path': 'Z-score path and share-price change to admission. Report Table 10.',
         'Sources': 'Data sources, page references and cross-checks.', 'Data dictionary': 'Meaning of every column.'}


def style_sheet(ws, wide=None, numfmt=None, freeze_col=None):
    wide = wide or {}
    for c in ws[1]:
        c.fill, c.font = HDR_FILL, HDR_FONT
        c.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
    ws.row_dimensions[1].height = 30
    for row in ws.iter_rows(min_row=2):
        for c in row:
            c.font = BODY
            c.border = Border(bottom=THIN)
            if isinstance(c.value, float) or (isinstance(c.value, str) and c.value.startswith('=')):
                if numfmt:
                    c.number_format = numfmt
    for i, c in enumerate(ws[1], 1):
        name = str(c.value)
        width = max([len(name)] + [len(str(x.value)) if x.value is not None and not str(x.value).startswith('=') else 8
                                   for x in ws[L(i)][1:60]])
        ws.column_dimensions[L(i)].width = wide.get(name, min(max(width + 2, 9), 40))
    ws.freeze_panes = (freeze_col or 'A') + '2'
    ws.auto_filter.ref = ws.dimensions
    ws.sheet_view.zoomScale = 90


def run():
    wb = load_workbook(PATH)
    if 'README' in wb.sheetnames:
        print('workbook already finalised - run zscore_analysis.py to regenerate it first')
        return
    R = json.load(open(os.path.join(HERE, 'results.json'), encoding='utf8'))
    raw, rat = wb[RAW], wb[RAT]
    rc = {c.value: L(i) for i, c in enumerate(raw[1], 1)}
    qc = {c.value: L(i) for i, c in enumerate(rat[1], 1)}
    n = raw.max_row
    assert rat.max_row == n

    # ---- raw sheet: derived columns as formulas
    def rf(r, a, b, expr):
        return f'=IF(COUNT({a}{r},{b}{r})=2,{expr},"")'
    for r in range(2, n + 1):
        c = lambda k: f'{rc[k]}{r}'
        raw[c('ebit')] = f'=IF(COUNT({c("pbt")},{c("interest")})=2,{c("pbt")}+{c("interest")},"")'
        raw[c('total_liabilities')] = f'=IF(COUNT({c("borrowings")},{c("other_liabilities")})=2,{c("borrowings")}+{c("other_liabilities")},"")'
        raw[c('book_equity')] = f'=IF(COUNT({c("equity_capital")},{c("reserves")})=2,{c("equity_capital")}+{c("reserves")},"")'
        raw[c('mve')] = f'=IF(COUNT({c("price")},{c("shares_cr")})=2,{c("price")}*{c("shares_cr")},"")'

    # ---- ratio sheet: formulas on the raw sheet
    S = f"'{RAW}'!"
    for r in range(2, n + 1):
        g = lambda k: S + f'{rc[k]}{r}'
        q = lambda k: f'{qc[k]}{r}'
        rat[q('X1')] = f'=IF(COUNT({g("tca")},{g("tcl")},{g("ta_wc")})=3,({g("tca")}-{g("tcl")})/{g("ta_wc")},"")'
        rat[q('X2')] = f'=IF(COUNT({g("reserves")},{g("total_assets")})=2,{g("reserves")}/{g("total_assets")},"")'
        rat[q('X3')] = f'=IF(COUNT({g("ebit")},{g("total_assets")})=2,{g("ebit")}/{g("total_assets")},"")'
        rat[q('X4')] = f'=IF(COUNT({g("mve")},{g("total_liabilities")})=2,{g("mve")}/{g("total_liabilities")},"")'
        rat[q('X4_book')] = f'=IF(COUNT({g("book_equity")},{g("total_liabilities")})=2,{g("book_equity")}/{g("total_liabilities")},"")'
        rat[q('X5')] = f'=IF(COUNT({g("sales")},{g("total_assets")})=2,{g("sales")}/{g("total_assets")},"")'
        X1, X2, X3, X4, X4b, X5 = (q(k) for k in ('X1', 'X2', 'X3', 'X4', 'X4_book', 'X5'))
        rat[q('Z')] = f'=IF(COUNT({X1},{X2},{X3},{X4},{X5})=5,1.2*{X1}+1.4*{X2}+3.3*{X3}+0.6*{X4}+1*{X5},"")'
        rat[q('Z_book')] = f'=IF(COUNT({X1},{X2},{X3},{X4b},{X5})=5,1.2*{X1}+1.4*{X2}+3.3*{X3}+0.6*{X4b}+1*{X5},"")'
        rat[q('Zpp')] = f'=IF(COUNT({X1},{X2},{X3},{X4b})=4,6.56*{X1}+3.26*{X2}+6.72*{X3}+1.05*{X4b},"")'
        z, zp = q('Z'), q('Zpp')
        rat[q('Z_zone')] = f'=IF({z}="","",IF({z}<1.81,"Distress",IF({z}<2.99,"Grey","Safe")))'
        rat[q('Zpp_zone')] = f'=IF({zp}="","",IF({zp}<1.1,"Distress",IF({zp}<2.6,"Grey","Safe")))'
        rat[q('EM')] = f'=IF({zp}="","",{zp}+3.25)'

    # ---- hypothesis tests: drop the empty welch_df column
    ht = wb['Hypothesis tests']
    for i, c in enumerate(ht[1], 1):
        if c.value == 'welch_df':
            ht.delete_cols(i)
            break

    # ---- style
    style_sheet(wb['Sample'], {'admission_source': 70, 'distressed': 30, 'healthy_peer': 30, 'industry': 30})
    style_sheet(raw, {'name': 34, 'admission_source': 40, 'wc_source': 55, 'industry': 28, 'shares_source': 28}, '#,##0.00', 'D')
    style_sheet(rat, {'name': 34}, '0.000', 'D')
    for ws in ('Descriptive stats', 'Hypothesis tests', 'Classification', 'Model scores t-1', 'Price path'):
        style_sheet(wb[ws], {'rule': 42, 'name': 34, 'company': 32, 'peer': 32}, '0.0000')
    for ws in ('Descriptive stats',):
        pass
    for row in wb['Price path'].iter_rows(min_row=2):
        for c in row:
            if wb['Price path'].cell(1, c.column).value in ('d_ret', 'h_ret'):
                c.number_format = '0.0%'
    for k in ('type1', 'type2', 'acc'):
        for i, c in enumerate(wb['Classification'][1], 1):
            if c.value == k:
                for cell in wb['Classification'][L(i)][1:]:
                    cell.number_format = '0.0%'
    # derived-column shading and excluded-row shading
    derived_raw = [rc[k] for k in ('ebit', 'total_liabilities', 'book_equity', 'mve')]
    insample = {r: wb[RAT][f'{qc["in_sample"]}{r}'].value for r in range(2, n + 1)}
    for r in range(2, n + 1):
        for col in derived_raw:
            raw[f'{col}{r}'].fill = SHADE
        if insample[r] is False:
            for ws in (raw, rat):
                for c in ws[r]:
                    c.fill = EXCL

    # ---- Sources sheet (rewritten)
    if 'Sources' in wb.sheetnames:
        del wb['Sources']
    src = wb.create_sheet('Sources')
    src.append(['item', 'source'])
    val = R['validation']
    rows = [
        ('Financial statements', 'Screener.in standalone annual P&L and balance sheet: https://www.screener.in/company/<symbol>/ (accessed October 2026)'),
        ('Share prices', 'Screener.in NSE price history (adjusted for corporate actions); last close on or before 31 March of each fiscal year'),
        ('Shares outstanding', 'LSEG basic weighted shares (same adjustment basis as the price series); net profit / EPS where LSEG is unavailable'),
        ('Current assets / liabilities (main)', 'LSEG standalone annual-report data embedded in https://sharpely.in/stocks/<symbol>/statements'),
    ]
    for (sym, fy), a in sorted(AR.items()):
        rows.append((f'Current assets / liabilities - {sym} FY{fy}', a['src'] + f" (tca {a['tca']}, tcl {a['tcl']}, total assets {a['ta']})"))
    rows += [
        ('Event dates (CIRP admission)', 'NCLT admission orders as reported in company stock-exchange filings, the Insolvency and Bankruptcy Board of India order listing (https://ibbi.gov.in) and financial press; see Sample sheet'),
        ('Availability rule', 'SEBI LODR Regulation 33(3)(d): audited annual results within 60 days of year end; t-1 = last year closed at least 90 days before admission'),
        ('Cross-check: Screener.in vs LSEG', ' ; '.join(f"{k}: median abs. gap < 0.01%, {100 * v['within5']:.0f}% of firm-years within 5% (n={v['n']})" for k, v in val.items())),
        ('Cross-check: market value', "Bharti Airtel at 31 Mar 2017: computed Rs 1,39,926 crore vs Rs 1,398.89 bn in its 2016-17 annual report"),
    ]
    for a, b, c in EXCLUDED:
        rows.append((f'Excluded candidate - {a}', f'{b}: {c}'))
    for r_ in rows:
        src.append(list(r_))
    style_sheet(src, {'item': 52, 'source': 140})
    for row in src.iter_rows(min_row=2):
        for c in row:
            c.alignment = Alignment(wrap_text=True, vertical='top')

    # ---- Data dictionary
    dd = wb.create_sheet('Data dictionary')
    dd.append(['sheet', 'column', 'meaning'])
    for ws in wb.worksheets:
        if ws.title in ('Data dictionary', 'README', 'Sources'):
            continue
        for c in ws[1]:
            assert c.value in DICT, (ws.title, c.value)
            dd.append([ws.title, c.value, DICT[c.value]])
    style_sheet(dd, {'sheet': 28, 'column': 20, 'meaning': 120})

    # ---- README (first sheet)
    rd = wb.create_sheet('README', 0)
    k = R['n_firmyears']
    lines = [
        ('Predicting Financial Distress Using Altman\'s Z-Score Model: A Matched-Pair Study of Distressed and Healthy Indian Listed Non-Financial Companies', 'title'),
        ('Corporate Finance and Financial Modelling - term project dataset (supports CFFM_Altman_Z_Score_Report)', 'sub'),
        ('Team: Ayush Kumar Maurya (23CH3FP43), Debanshu Ghosh (23CH3FP56), Arghadeep Ghosh (23CH3FP53), Swayam (23MF3FP26)', 'sub'),
        ('', ''),
        ('How to read this workbook', 'h'),
        (f'15 distressed companies (admitted to CIRP under the IBC, 2017-2024) are matched with 15 healthy listed peers; {k} firm-years (t-1, t-2, t-3) are used in the tests.', ''),
        ('All amounts are standalone, Rs crore, for fiscal years ending 31 March. t-1 is the last year closed at least 90 days before the admission order.', ''),
        ("Grey-shaded cells in 'Raw financials' and every ratio/score cell in 'Ratios and scores' are live Excel formulas: change a raw figure and X1-X5, Z, Z'' and the zones update.", ''),
        ('Orange rows are firm-years excluded from the statistical tests because a required figure is not available (5 of 90). Blank cells mean the figure is not available, not zero.', ''),
        ('Statistical results (descriptive stats, tests, classification, model scores, price path) are static outputs of analysis/zscore_analysis.py (Python) and match the report tables.', ''),
        ('', ''),
        ('Sheets', 'h'),
    ] + [(f'{k_}: {v}', '') for k_, v in NOTES.items()] + [
        ('', ''),
        ('Key formulas', 'h'),
        ('X1 = (current assets - current liabilities) / total assets;  X2 = reserves / total assets;  X3 = EBIT / total assets;  X4 = market value of equity / total liabilities;  X5 = sales / total assets', ''),
        ("Z = 1.2 X1 + 1.4 X2 + 3.3 X3 + 0.6 X4 + 1.0 X5 (zones: <1.81 distress, 1.81-2.99 grey, >2.99 safe);  Z'' = 6.56 X1 + 3.26 X2 + 6.72 X3 + 1.05 X4(book) (zones: <1.10, 1.10-2.60, >2.60)", ''),
        ('', ''),
        ('Reproduce: run analysis/zscore_analysis.py then analysis/build_report.py. Raw downloads are in raw/ (not required to read this workbook).', ''),
    ]
    for i, (t, kind) in enumerate(lines, 1):
        c = rd.cell(i, 1, t)
        c.alignment = Alignment(wrap_text=True, vertical='top')
        c.font = {'title': Font(name='Calibri', bold=True, size=14, color='1F3864'), 'sub': Font(name='Calibri', size=11, italic=True),
                  'h': Font(name='Calibri', bold=True, size=11, color='1F3864')}.get(kind, Font(name='Calibri', size=10))
    rd.column_dimensions['A'].width = 150
    rd.sheet_view.showGridLines = False

    wb.active = 0
    for ws in wb.worksheets:
        ws.sheet_view.tabSelected = (ws.title == 'README')
    wb.save(PATH)
    print('workbook finalised:', PATH)


if __name__ == '__main__':
    run()
