"""Result-dependent sections of the report. All numbers are read from results.json."""
import os
import docx_helpers as H
from sample import PAIRS, EXCLUDED, t1_year

XS = ['X1', 'X2', 'X3', 'X4', 'X5']
LBL = {'X1': 'Working capital / Total assets', 'X2': 'Retained earnings / Total assets',
       'X3': 'EBIT / Total assets', 'X4': 'Market value of equity / Total liabilities',
       'X5': 'Sales / Total assets', 'Z': 'Altman Z-score', 'Zpp': "Z''-score (emerging market)"}
LAGS = {1: 't−1', 2: 't−2', 3: 't−3'}


def f(x, d=2):
    if x is None:
        return '–'
    return f'{x:.{d}f}'.replace('-', '−')


def pct(x, d=0):
    return '–' if x is None else f'{100 * x:.{d}f}%'


def pv(p):
    if p is None:
        return '–'
    return '<0.001' if p < 0.001 else f'{p:.3f}'


def stars(p):
    if p is None:
        return ''
    return '***' if p < 0.01 else '**' if p < 0.05 else '*' if p < 0.10 else ''


def get(lst, **kw):
    for r in lst:
        if all(r.get(k) == v for k, v in kw.items()):
            return r
    return None


# ------------------------------------------------------------------------------------------
def lit_table(doc):
    H.caption(doc, 'Table 1. Summary of key studies reviewed')
    rows = [
        ['Altman (1968)', 'US, 33+33 manufacturers', 'MDA, five ratios', '95% accuracy at t−1; 72% of bankrupt firms at t−2'],
        ['Ohlson (1980)', 'US industrial firms, 1970–76', 'Logit (O-score)', 'Probabilistic prediction; earlier studies may overstate accuracy'],
        ['Zmijewski (1984)', 'US, NYSE/AMEX firms', 'Probit; bias analysis', 'Matched samples overstate accuracy'],
        ['Grice & Ingram (2001)', 'US, recent samples', 'Original Z re-tested', 'Less accurate in recent data and outside manufacturing'],
        ['Altman (2005)', 'Emerging-market bonds', "EM / Z''-score", 'Four-ratio model without asset turnover'],
        ['Bandyopadhyay (2006)', 'India, bond defaults', 'MDA and logit', 'Re-estimated Z beats original model'],
        ['Singh & Mishra (2016)', 'India, 208 manufacturers', 'MDA, probit, logit', 'Re-estimation improves all three models'],
        ['Altman et al. (2017)', '34 countries', "Z''-score, logit", 'Original model still useful; local re-estimation helps'],
    ]
    H.table(doc, ['Study', 'Sample', 'Method', 'Main finding'], rows, widths=[3.4, 3.8, 3.4, 5.8], size=9)


# ------------------------------------------------------------------------------------------
def data_section(doc, R):
    doc.add_heading('4.1 Sample design', level=2)
    n = R['pairs_used']
    H.para(doc,
           f"Following Altman's paired-sample design, the study uses {n} distressed and {n} healthy companies "
           "listed on the NSE or BSE. A company is classed as distressed if the NCLT admitted it into CIRP under "
           "the IBC; the event date is the date of the admission order, confirmed from the company's stock-exchange "
           "filing, the IBBI order listing or contemporaneous press reports (Appendix). Banks, NBFCs and insurers "
           "are excluded because their balance sheets are not comparable with the Z-score ratios. Each "
           "distressed company is matched with a listed company from the same industry that never defaulted "
           "over the sample period, chosen as the closest in size among the industry's leading listed firms. "
           "Admissions span July 2017 to June 2024 and cover airlines, steel, textiles, real estate, power, "
           "auto components, EPC, telecom, edible oils, education, paper, retail and cement.")
    H.para(doc,
           "Timing is set so that the investor could actually have seen the statements. Year t−1 is the last "
           "fiscal year (ending 31 March) that closed at least 90 days before the admission order. SEBI's "
           "Listing Regulations require audited annual results within 60 days of the year end (Securities and "
           "Exchange Board of India, 2015, Reg. 33(3)(d)), and the extra 30 days allows for distressed firms "
           "that file late. Years t−2 and t−3 are the two preceding fiscal years. Each healthy peer is measured "
           "on exactly the same fiscal years as its distressed match, so macroeconomic conditions are held "
           "constant within each pair. One exception follows the same principle: Future Retail told the exchanges "
           "on 24 May 2022 that approval of its FY2022 results was delayed because its board and audit committee "
           "were not properly constituted, and no FY2022 statements appear in either data source, so its t−1 is "
           "FY2021, the latest year with audited statements available.")
    exc = '; '.join(f'{a} ({c})' for a, b, c in EXCLUDED)
    H.para(doc, f"Several other well-known IBC cases were examined and excluded: {exc}.")

    doc.add_heading('4.2 Data sources and validation', level=2)
    val, wct = R['validation'], R['validation_wc_ta']
    wc = R['wc_source_counts']; n_fy = R['n_firmyears']
    n_lseg = sum(c for k, c in wc.items() if k.startswith('LSEG'))
    n_ar = sum(c for k, c in wc.items() if ' AR ' in k)
    n_tab = sum(c for k, c in wc.items() if k.startswith('Sharpely'))
    sh = R['shares_source_counts']
    H.para(doc,
           "All accounting figures are standalone, because the IBC process applies to the legal entity, and are "
           "in Rs crore. The income statement and balance sheet (revenue from operations, profit before tax, "
           "interest, reserves and surplus, borrowings, other liabilities and total assets) were taken from "
           "Screener.in, which compiles the statements that listed companies file with the exchanges. A second, "
           "independent compilation, LSEG (Refinitiv) standalone annual-report data published on Sharpely.in, "
           "was used to check them and to supply reported totals of current assets and current liabilities. "
           "Where LSEG data were missing, these totals were read directly from the standalone balance sheets in "
           "the company annual reports (Bhushan Steel, Bharat Forge, Sintex Industries and JK Paper) obtained from "
           "the BSE archive or the company's website.")
    H.para(doc,
           f"The two compilations were reconciled before use. For the {val['Total assets']['n']} firm-years "
           f"covered by both, the median absolute difference is below 0.01% for total assets, revenue, profit "
           f"before tax and reserves. {pct(val['Total assets']['within5'])} of total-asset figures, "
           f"{pct(val['Revenue']['within5'])} of revenue figures and {pct(val['Profit before tax']['within5'])} of "
           f"profit figures agree within 5%; the remaining gaps come from later restatements, such as the Ind AS "
           f"transition. Current assets and liabilities come from LSEG for {n_lseg} of the {n_fy} firm-years, from "
           f"annual reports for {n_ar}, and from Sharpely's statement table for {n_tab}; the table is used only "
           f"when its total assets agree with the standalone figure within 5%. X1 is computed with the total "
           f"assets of the same source, which agree with Screener's at a median gap below 0.01% "
           f"({pct(wct['within5'])} within 5%). No working-capital figure is estimated. Retained earnings are measured "
           f"by 'reserves and surplus' (other equity under Ind AS), and both compilations agree on this figure. "
           f"It also includes securities premium, which is the usual limitation of Indian Z-score studies.")
    H.para(doc,
           f"The market value of equity is the last NSE closing price on or before 31 March of each fiscal year "
           f"multiplied by the number of shares. Because the price history is adjusted for later bonuses, splits "
           f"and rights issues, the share count must be adjusted on the same basis. LSEG's basic weighted share "
           f"count meets this requirement and is used for {sh.get('LSEG basic weighted shares', 0)} firm-years; net "
           f"profit divided by EPS is used for the other {sh.get('Net profit / EPS (Screener)', 0)}. As a check, "
           f"Bharti Airtel's computed market value at 31 March 2017 (Rs 1,39,926 crore) matches the Rs 1,398.89 "
           f"billion reported in its 2016-17 annual report to within 0.1%.")

    doc.add_heading('4.3 Variables', level=2)
    H.caption(doc, 'Table 2. Variable definitions')
    rows = [
        ['X1', 'Working capital / Total assets', '(Current assets − Current liabilities) / Total assets', 'Liquidity'],
        ['X2', 'Retained earnings / Total assets', 'Reserves and surplus / Total assets', 'Cumulative profitability, age'],
        ['X3', 'EBIT / Total assets', '(Profit before tax + Interest) / Total assets', 'Operating productivity'],
        ['X4', 'MVE / Total liabilities', 'Year-end market capitalisation / (Borrowings + Other liabilities)', 'Solvency (market)'],
        ["X4'", 'Book equity / Total liabilities', '(Share capital + Reserves) / Total liabilities', "Solvency (book), used in Z''"],
        ['X5', 'Sales / Total assets', 'Revenue from operations / Total assets', 'Asset turnover'],
    ]
    H.table(doc, ['Code', 'Ratio', 'Measurement', 'Dimension'], rows, widths=[1.3, 4.3, 7.0, 3.8], size=9)


def method_section(doc, R):
    doc.add_heading('4.4 Models and statistical methods', level=2)
    H.para(doc, "Original Z-score (Altman, 1968): Z = 1.2X1 + 1.4X2 + 3.3X3 + 0.6X4 + 1.0X5. Altman's zones "
                "are distress (Z < 1.81), grey (1.81 ≤ Z ≤ 2.99) and safe (Z > 2.99). A single cut-off of 2.675 "
                "minimised misclassification in his sample.", bold_lead='(a)')
    H.para(doc, "Emerging-market Z''-score (Altman, 2005; Altman et al., 2019): Z'' = 6.56X1 + 3.26X2 + 6.72X3 + "
                "1.05X4', with book equity in X4' and no asset-turnover term. Its zones are distress "
                "(Z'' < 1.10), grey (1.10–2.60) and safe (Z'' > 2.60). Adding the constant 3.25 gives the EM "
                "score used for bond-rating equivalents. The constant does not change any classification.",
           bold_lead='(b)')
    H.para(doc, "Ratio analysis and hypothesis tests. Each ratio is described by group and horizon. Because the "
                "design is matched, the main test of H0 is a paired t-test on the within-pair differences. "
                "A Welch two-sample t-test (unequal variances), the Wilcoxon signed-rank test and the "
                "Mann-Whitney U test are reported as robustness checks, since Shapiro-Wilk tests reject "
                "normality for several ratios. Effect sizes are Cohen's d. 95% confidence intervals for the mean "
                "within-pair difference are bootstrapped with 5,000 resamples.", bold_lead='(c)')
    w = R['winsor']
    H.para(doc, "Re-estimated discriminant analysis. Altman's MDA is re-estimated on the Indian t−1 sample with "
                "the same five ratios. To stop a few extreme values from dominating the estimation, ratios are "
                "winsorised at the pooled 5th and 95th percentiles before estimation. The output reported is "
                "the unstandardised coefficients, Wilks' lambda with Bartlett's χ² test, the univariate F-ratio "
                "for each variable (as in Altman, 1968), and the scaled coefficients (coefficient × pooled "
                "standard deviation) used to rank each variable's contribution. Accuracy is "
                "measured in-sample, by leave-one-out cross-validation (Lachenbruch & Mickey, 1968), and on the "
                "t−2 and t−3 hold-out years.", bold_lead='(d)')
    H.para(doc, "Logistic regression. Following Ohlson (1980), a logit of the distress dummy is estimated on Z "
                "alone (Model 1) and on X1–X5 (Model 2). When maximum likelihood fails because of complete "
                "separation, which is common when groups are well separated and samples are small, Firth's "
                "(1993) penalised likelihood is used. Coefficients, odds ratios, McFadden's pseudo-R², the "
                "likelihood-ratio test and AIC are reported.", bold_lead='(e)')
    H.para(doc, "Model comparison. Discriminating power is summarised by the area under the ROC curve (AUC), "
                "with bootstrapped 95% confidence intervals. Differences between correlated AUCs are tested "
                "with the DeLong, DeLong and Clarke-Pearson (1988) test. For the re-estimated models, "
                "leave-one-out scores are used so that the comparison is out of sample. The Youden index "
                "(sensitivity + specificity − 1) gives the cut-off that best fits the Indian sample. "
                "Sensitivity checks vary the X4 definition, the working-capital source and the industry "
                "composition.", bold_lead='(f)')
    H.para(doc, "Investment view. For each distressed firm, the share-price change from the end of fiscal year "
                "t−1 to the last trading day before the admission order is compared with the change for its peer "
                "over the same window. This shows what a Z-score warning was worth to a shareholder.",
           bold_lead='(g)')
    H.para(doc, "All calculations were done in Python (pandas, SciPy, statsmodels) with a script that is "
                "submitted with the report. The Excel workbook contains the raw figures, every ratio and every "
                "test statistic, so each number in this report can be traced back to its source.")
