"""Abstract, results, conclusion and appendix of the report. Every number is read from results.json."""
import os
import pandas as pd

import docx_helpers as H
from report_results import XS, LBL, f, pct, pv, stars, get
from sample import PAIRS, T1_OVERRIDE, t1_year


def _t1(R):
    return pd.DataFrame(R['t1_table'])


def _cls(R, lag, rule_start):
    for c in R['classification']:
        if c['lag'] == lag and c['rule'].startswith(rule_start):
            return c


def abstract(R):
    c181 = _cls(R, 1, 'Z < 1.81'); c2675 = _cls(R, 1, 'Z < 2.675'); cpp = _cls(R, 1, "Z'' < 1.10")
    c3 = _cls(R, 3, 'Z < 1.81')
    auc = R['auc_by_lag']
    inv = R['invest_summary']
    return (f"This study tests whether Altman's (1968) Z-score would have warned investors about Indian listed "
            f"companies that were later admitted to insolvency under the Insolvency and Bankruptcy Code, 2016. "
            f"Fifteen non-financial companies admitted to the Corporate Insolvency Resolution Process between July "
            f"2017 and June 2024 are matched with fifteen healthy listed peers from the same industries, and "
            f"Altman's five ratios are computed for the three fiscal years before each admission (85 firm-years). "
            f"Standalone financial data from two independent compilations agree to within 0.01% at the median, and "
            f"current assets and liabilities are taken from reported statements. Paired t-tests and non-parametric "
            f"tests show that all five ratios are significantly lower for the distressed firms one year before the "
            f"event, with the largest effects for profitability (X3), retained earnings (X2) and working capital (X1). "
            f"Every distressed company was already in Altman's distress zone (Z < 1.81) one year before admission, "
            f"so the Type I error was zero, but {c181['fp']} of 15 healthy peers were also below 1.81, giving overall "
            f"accuracy of {pct(c181['acc'])} ({pct(c2675['acc'])} with the 2.675 cut-off). The emerging-market "
            f"Z''-score classified {pct(cpp['acc'])} correctly. Discriminating power stays high over time "
            f"(AUC {f(auc['1']['Z'])}, {f(auc['2']['Z'])} and {f(auc['3']['Z'])} at t−1, t−2 and t−3), and the score "
            f"flagged {c3['tp']} of {c3['n1']} distressed firms three years ahead. A discriminant function "
            f"re-estimated on Indian data ranks retained earnings and profitability as the most important ratios, "
            f"and a cut-off of about {f(R['roc']['youden_cut'])} fits Indian firms better than 1.81. Between the end "
            f"of year t−1 and the admission date, distressed shares lost a median {pct(-inv['median_d'])} while "
            f"their peers gained {pct(inv['median_h'])}. The Z-score is therefore a reliable, low-cost first screen "
            f"for Indian equity and credit investors, provided it is applied with industry-aware cut-offs.")


def descriptive(doc, R, FIG):
    t1 = _t1(R)
    doc.add_heading('5.1 Ratio analysis: descriptive statistics', level=2)
    H.caption(doc, 'Table 3. Mean (median) of the Altman ratios and scores by group and horizon')
    rows = []
    for v in XS + ['Z', 'Zpp']:
        row = [f"{v} – {LBL[v]}" if v in XS else LBL[v]]
        for lag in (1, 2, 3):
            for g in ('Distressed', 'Healthy'):
                r = get(R['desc'], lag=lag, group=g, var=v)
                row.append(f"{f(r['mean'])} ({f(r['median'])})")
        rows.append(row)
    H.table(doc, ['Variable', 't−1 D', 't−1 H', 't−2 D', 't−2 H', 't−3 D', 't−3 H'], rows,
            widths=[4.6, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0], size=8.5)
    H.note(doc, 'D = distressed (IBC) group; H = healthy peer group. n = 15 pairs at t−1, 15 distressed / 14 healthy '
                'at t−2, 13 / 13 at t−3. Raw (unwinsorised) values.')
    d = lambda lag, v: get(R['desc'], lag=lag, group='Distressed', var=v)
    h = lambda lag, v: get(R['desc'], lag=lag, group='Healthy', var=v)
    H.para(doc,
           f"Table 3 shows a clear pattern on every dimension of financial health. One year before admission, the "
           f"median distressed firm had negative working capital (X1 median {f(d(1, 'X1')['median'])}), so its "
           f"current liabilities exceeded current assets by about a third of total assets. This is partly because "
           f"defaulted long-term loans had been reclassified as current once lenders recalled them. Retained earnings "
           f"were close to zero (X2 median {f(d(1, 'X2')['median'])} against {f(h(1, 'X2')['median'])} for peers) after "
           f"several years of losses, and operating returns were negative (X3 median {f(d(1, 'X3')['median'])} against "
           f"{f(h(1, 'X3')['median'])}). The market had already priced in the distress: the median market value of "
           f"equity covered only {pct(d(1, 'X4')['median'])} of book liabilities, against "
           f"{f(h(1, 'X4')['median'], 1)} times for the peers. Asset turnover (X5) was also lower, because distressed "
           f"firms carried large unproductive assets such as stalled projects, idle plants and grounded aircraft. "
           f"Healthy-group means for X4 and Z are pulled up by two very lightly leveraged peers (Avenue Supermarts and "
           f"Aptech), so the medians are the better summary. The trend across the three years is also informative. "
           f"For the distressed firms, the median Z falls from {f(d(3, 'Z')['median'])} at t−3 to "
           f"{f(d(2, 'Z')['median'])} at t−2 and {f(d(1, 'Z')['median'])} at t−1, while the healthy median stays "
           f"close to {f(h(1, 'Z')['median'], 1)} (Figure 1). Among the distressed firms, the median X1 falls from "
           f"{f(d(3, 'X1')['median'])} to {f(d(1, 'X1')['median'])} and the median X3 from "
           f"{f(d(3, 'X3')['median'])} to {f(d(1, 'X3')['median'])}. Liquidity and operating profitability erode "
           f"first, and accumulated losses then eat into retained earnings.")
    H.figure(doc, os.path.join(FIG, 'fig2_z_trajectory.png'), 11.0)
    H.caption(doc, 'Figure 1. Median Z-score (shaded: inter-quartile range) from t−3 to t−1; dashed lines mark 1.81 and 2.99')
    vif, corr = R['vif'], R['corr']
    H.para(doc,
           f"Correlations among the winsorised t−1 ratios are positive and moderate to high (for example "
           f"r(X2, X3) = {f(corr['X2']['X3'])} and r(X1, X3) = {f(corr['X1']['X3'])}), as expected because all five "
           f"ratios reflect the same underlying condition. Variance inflation factors range from "
           f"{f(min(vif.values()), 1)} to {f(max(vif.values()), 1)}, below the usual threshold of 5 to 10, so "
           f"multicollinearity does not prevent multivariate estimation. It does, however, make individual "
           f"coefficients less stable (Section 5.4).")


def tests(doc, R):
    doc.add_heading('5.2 Hypothesis tests (RQ1)', level=2)
    H.caption(doc, 'Table 4. Tests of H0: μ(distressed) = μ(healthy)')
    rows = []
    for v in XS + ['Z', 'Zpp']:
        a = get(R['tests'], lag=1, var=v); b = get(R['tests'], lag=2, var=v); c = get(R['tests'], lag=3, var=v)
        rows.append([v if v in XS else ('Z' if v == 'Z' else "Z''"),
                     f"{f(a['mean_diff'])} [{f(a['ci_lo'])}, {f(a['ci_hi'])}]",
                     f"{f(a['paired_tw'])}{stars(a['paired_pw'])}", pv(a['paired_p']), pv(a['welch_p']),
                     pv(a['wilcoxon_p']), pv(a['mw_p']), f(a['cohen_d']), pv(b['paired_pw']), pv(c['paired_pw'])])
    H.table(doc, ['', 'Mean diff. t−1 [95% CI]', 'Paired t (wins.)', 'Paired p (raw)', 'Welch p', 'Wilcoxon p',
                  'Mann-Whitney p', "Cohen's d", 't−2 paired p', 't−3 paired p'], rows,
            widths=[0.9, 3.4, 1.6, 1.5, 1.3, 1.5, 1.6, 1.3, 1.5, 1.5], size=8)
    H.note(doc, 'Mean difference = distressed − healthy within each pair (bootstrap 95% CI, 5,000 resamples). Paired t '
                '(wins.) uses ratios winsorised at the pooled 5th/95th percentiles; *** p < 0.01, ** p < 0.05, '
                '* p < 0.10. The t−2 and t−3 columns report the winsorised paired-t p-value.')
    x4 = get(R['tests'], lag=1, var='X4'); z1 = get(R['tests'], lag=1, var='Z'); x13 = get(R['tests'], lag=3, var='X1')
    H.para(doc,
           f"H0 is rejected for every ratio at t−1. All within-pair differences are negative, as Altman's model "
           f"predicts, and their bootstrap confidence intervals exclude zero. The effects are very large: Cohen's d "
           f"is about −2 or larger for X1, X2, X3 and Z''. The only disagreement between tests concerns the raw "
           f"X4 and Z, whose paired t-tests are not significant (p = {pv(x4['paired_p'])} and {pv(z1['paired_p'])}). "
           f"The reason is not a weak effect. Two healthy peers have extreme market-to-liability ratios that inflate "
           f"the variance of the differences. Once these are winsorised, or rank-based tests are used, the "
           f"difference is highly significant (Wilcoxon p = {pv(x4['wilcoxon_p'])}). Shapiro-Wilk tests reject "
           f"normality for X4 and X5 in both groups, which is why the non-parametric tests are reported alongside "
           f"the t-tests. The differences remain significant at t−2 for all ratios and at t−3 for every ratio except "
           f"working capital (p = {pv(x13['paired_pw'])}). Profitability and retained earnings separate the groups "
           f"earliest, while liquidity deteriorates only in the last two years. The answer to RQ1 is therefore yes: "
           f"all five Altman ratios differ significantly between future IBC companies and matched healthy firms, and "
           f"four of the five already do so three years before the event.")


def classification(doc, R, FIG):
    t1 = _t1(R)
    doc.add_heading("5.3 Classification by the original Z and the Z''-score (RQ2)", level=2)
    H.figure(doc, os.path.join(FIG, 'fig1_z_by_pair.png'), 15.0)
    H.caption(doc, 'Figure 2. Z-score of each distressed firm and its matched peer at t−1 (values above 8 are truncated and labelled)')
    H.caption(doc, 'Table 5. Classification accuracy by horizon, compared with Altman (1968)')
    rows = []
    for rule, lab in [('Z < 2.675', 'Z, cut-off 2.675'), ('Z < 1.81', 'Z, cut-off 1.81'), ('Z < 2.99', 'Z, cut-off 2.99'),
                      ("Z'' < 1.10", "Z'', cut-off 1.10"), ("Z'' < 2.60", "Z'', cut-off 2.60")]:
        row = [lab]
        for lag in (1, 2, 3):
            c = _cls(R, lag, rule)
            row += [f"{c['tp']}/{c['n1']}", f"{c['tn']}/{c['n0']}", pct(c['acc'])]
        rows.append(row)
    rows.append(['Altman (1968), cut-off 2.675', '31/33', '32/33', '95%', '72%', '–', '–', '≈50%', '–', '–'])
    H.table(doc, ['Rule', 't−1 D hit', 't−1 H hit', 't−1 acc.', 't−2 D hit', 't−2 H hit', 't−2 acc.',
                  't−3 D hit', 't−3 H hit', 't−3 acc.'], rows,
            widths=[3.6, 1.35, 1.35, 1.35, 1.35, 1.35, 1.35, 1.35, 1.35, 1.35], size=8, bold_rows=(6,))
    H.note(doc, "D hit = distressed firms correctly flagged (1 − Type I error); H hit = healthy firms correctly passed "
                "(1 − Type II error). 'Cut-off 1.81' treats the grey zone as healthy and 'cut-off 2.99' treats it as "
                "distressed. Altman's figures are for his original sample of US manufacturers; for t−2 and t−3 only "
                "the share of bankrupt firms correctly classified is shown.")
    zd = get(R['zones'], lag=1, group='Distressed', model='Z'); zh = get(R['zones'], lag=1, group='Healthy', model='Z')
    zph = get(R['zones'], lag=1, group='Healthy', model='Zpp')
    low = t1[(t1.group == 'Healthy') & (t1.Z < 1.81)].sort_values('Z')
    low_names = ', '.join(f"{n.replace(' Ltd', '')} ({f(z)})" for n, z in zip(low.name, low.Z))
    dz = t1[t1.group == 'Distressed'].sort_values('Z')
    c181 = _cls(R, 1, 'Z < 1.81'); c3 = _cls(R, 3, 'Z < 1.81'); cpp1 = _cls(R, 1, "Z'' < 1.10")
    missed = t1[(t1.group == 'Distressed') & (t1.Zpp >= 1.10)].name.str.replace(' Ltd', '').tolist()
    H.para(doc,
           f"Figure 2 and Table 5 give the main answer to RQ2. All {zd['n']} distressed firms were in the distress "
           f"zone at t−1, so whichever cut-off is used, the Type I error, the costly error for an investor, is zero. "
           f"Their Z-scores range from {f(dz.Z.iloc[0])} ({dz.name.iloc[0].replace(' Ltd', '')}) to "
           f"{f(dz.Z.iloc[-1])} ({dz.name.iloc[-1].replace(' Ltd', '').replace(' Industries', '')}), far below 1.81. "
           f"The weakness lies on the other side. Of the healthy peers, only {zh['Safe']} scored above 2.99, "
           f"{zh['Grey']} fell in the grey zone and {zh['Distress']} were in the distress zone: {low_names}. All four "
           f"are capital-intensive, with low asset turnover and heavy fixed assets, a profile that Altman's 1968 "
           f"weights, estimated on manufacturers of 1946–1965, penalise. Grice and Ingram (2001) likewise found "
           f"that the model is less accurate in recent samples and outside manufacturing. Bharti Airtel's FY2017 score also reflects the Jio price war, which "
           f"pushed the telecom industry into losses that year. So with Altman's cut-offs, the overall accuracy of "
           f"{pct(c181['acc'])} at t−1 comes entirely from zero missed distressed firms combined with a Type II "
           f"error of {pct(c181['type2'])}.")
    H.para(doc,
           f"The Z''-score, which drops the asset-turnover term and uses book equity, corrects much of this industry "
           f"bias. No healthy peer falls in its distress zone ({zph['Grey']} are grey), and with the 1.10 cut-off it "
           f"classifies {pct(cpp1['acc'])} of firms correctly at t−1, missing only {', '.join(missed)}. At longer "
           f"horizons, however, the Z''-score loses more power than the original Z (AUC "
           f"{f(R['auc_by_lag']['3']['Zpp'])} against {f(R['auc_by_lag']['3']['Z'])} at t−3, Figure 3) because "
           f"book equity responds more slowly than market value. The original Z with the 1.81 cut-off flagged "
           f"{c3['tp']} of {c3['n1']} distressed firms three years ahead and misclassified only {c3['fp']} healthy "
           f"firm. That is far better than Altman's own long-range results (about half of bankrupt firms at t−3). The "
           f"likely reason is specific to India: most of these companies had been non-performing assets for years "
           f"before the IBC gave creditors an effective way to act. The 2017 RBI referral covered accounts that were "
           f"60% or more non-performing as of March 2016 (Reserve Bank of India, 2017). The admission date therefore "
           f"comes late in a long period of distress, and the Z-score picks up that distress early.")


def mda(doc, R):
    L = R['lda']
    doc.add_heading('5.4 Re-estimated discriminant function (RQ3)', level=2)
    H.caption(doc, 'Table 6. Multiple discriminant analysis re-estimated on the Indian t−1 sample (winsorised ratios)')
    rows = [[f"{v} – {LBL[v]}", f(L['coef'][v], 3), f(L['F'][v]['F'], 2) + stars(L['F'][v]['p']),
             f(L['scaled'][v], 2), str(L['rank'][v])] for v in XS]
    H.table(doc, ['Variable', 'Coefficient', 'Univariate F (1, 28)', 'Scaled coefficient', 'Rank by scaled coefficient'],
            rows, widths=[6.0, 2.2, 2.8, 2.4, 2.8], size=8.5)
    H.note(doc, f"Higher scores indicate financial health; cut-off (midpoint of the group centroids) = "
                f"{f(L['cutoff'], 3)}. Wilks' λ = {f(L['wilks'], 3)}, Bartlett χ²({L['chi2_df']}) = {f(L['chi2'], 2)}, "
                f"p < 0.001. Scaled coefficient = coefficient × pooled within-group standard deviation; ranks are by "
                f"absolute scaled coefficient.")
    H.para(doc,
           f"The re-estimated function is highly significant (Wilks' λ = {f(L['wilks'], 3)}, χ² = {f(L['chi2'], 1)}, "
           f"p < 0.001), and every ratio separates the groups on its own (Table 6). X3 has the largest univariate "
           f"F-ratio, which is consistent with Altman's (1968) finding that earning power (X3) contributes most to the "
           f"discriminant function. Asset turnover (X5) is the weakest, which mirrors Altman's 1968 sample, where X5 "
           f"was not significant on its own. The multivariate weights differ from Altman's, though. In the Indian "
           f"function, retained earnings (X2) carries the largest scaled weight, followed by profitability (X3) and "
           f"working capital (X1), while X4 "
           f"receives a small negative weight once the other ratios are controlled for. This sign reversal reflects "
           f"its overlap with X2 and X3 (Section 5.1), not a genuine negative effect of market value. The ranking "
           f"suggests that for Indian firms, the depletion of accumulated profits, which captures years of losses "
           f"and write-offs, is the most telling single symptom.")
    ho2, ho3 = L['holdout']['2'], L['holdout']['3']
    H.para(doc,
           f"The function classifies {pct(L['insample']['acc'])} of the estimation sample correctly and "
           f"{pct(L['loo']['acc'])} under leave-one-out cross-validation (one healthy firm misclassified). Applied "
           f"without change to earlier years, it classifies {pct(ho2['acc'])} correctly at t−2 and {pct(ho3['acc'])} "
           f"at t−3. Its Type I error rises to {pct(ho2['type1'])} and {pct(ho3['type1'])} because the function is tuned "
           f"to the deep distress of the final year. On hold-out years, therefore, re-estimation does not outperform "
           f"Altman's original weights with the 1.81 cut-off. This echoes Begley, Ming and Watts (1996), who found "
           f"that these models lose accuracy outside the period in which they were estimated.")


def logit(doc, R):
    doc.add_heading('5.5 Logistic regression (RQ3)', level=2)
    m1, m2 = R['logit']['m1'], R['logit']['m2']
    H.caption(doc, 'Table 7. Logit models of the probability of distress at t−1 (Firth penalised likelihood)')
    rows = []
    for name, m in [('Model 1', m1), ('Model 2', m2)]:
        for i, var in enumerate(m['names']):
            rows.append([name if i == 0 else '', 'Constant' if var == 'const' else var, f(m['params'][i], 3),
                         f(m['se'][i], 3), pv(m['p'][i]), '–' if var == 'const' else f(m['odds'][i], 3)])
        lrp = '< 0.001' if m['lr_p'] < 0.001 else '= ' + pv(m['lr_p'])
        rows.append(['', f"McFadden R² = {f(m['mcfadden'], 3)}; LR χ²({len(m['names']) - 1}) = {f(m['lr'], 2)}, "
                         f"p {lrp}; AIC = {f(m['aic'], 2)}", '', '', '', ''])
    H.table(doc, ['', 'Variable', 'Coefficient', 'Std. error', 'p-value', 'Odds ratio'], rows,
            widths=[1.7, 7.0, 2.0, 1.9, 1.7, 1.9], size=8.5)
    H.note(doc, 'Dependent variable = 1 if the firm was later admitted to CIRP. Maximum likelihood fails because of '
                'complete separation, so Firth (1993) bias-reduced estimates are reported. Model 2 uses winsorised ratios.')
    H.para(doc,
           f"Maximum-likelihood logit estimation breaks down because the Z-score separates the two groups perfectly "
           f"at t−1, so the Firth penalised estimator is used. In Model 1, the Z-score is a significant predictor of "
           f"distress (coefficient {f(m1['params'][1], 2)}, p = {pv(m1['p'][1])}). Each one-point increase in Z "
           f"multiplies the odds of later insolvency by {f(m1['odds'][1], 3)}, and the model's McFadden R² is "
           f"{f(m1['mcfadden'], 2)}. Model 2 is jointly highly significant (LR χ² = {f(m2['lr'], 1)}, p < 0.001), but "
           f"no single ratio is individually significant, and its AIC ({f(m2['aic'], 1)}) is worse than Model 1's "
           f"({f(m1['aic'], 1)}). With 30 observations and five correlated ratios, the data cannot separate the "
           f"individual effects, whereas the composite Z summarises them efficiently. Model 2's leave-one-out "
           f"accuracy is {pct(m2['loo_acc']['acc'])}, the same as the re-estimated MDA. In a small-sample screening "
           f"setting, Altman's composite score therefore does as well as a freshly estimated set of weights, and "
           f"Model 1 gives it the probability interpretation that Ohlson (1980) advocated.")


def comparison(doc, R, FIG):
    doc.add_heading('5.6 Model comparison, optimal cut-off and robustness', level=2)
    H.figure(doc, os.path.join(FIG, 'fig4_roc.png'), 14.0)
    H.caption(doc, "Figure 3. ROC curves of the original Z and the Z''-score at t−1, t−2 and t−3")
    roc = R['roc']
    H.caption(doc, 'Table 8. Area under the ROC curve at t−1 (re-estimated models scored out of sample)')
    H.table(doc, ['Model', 'AUC', 'Bootstrap 95% CI'],
            [[k, f(v['auc'], 3), f"[{f(v['lo'], 3)}, {f(v['hi'], 3)}]"] for k, v in roc['auc'].items()],
            widths=[7.5, 2.5, 4.0], size=9)
    worst = min(roc['delong'], key=lambda d: d['p'])
    oot2, oot3 = roc['youden_oot']['2'], roc['youden_oot']['3']
    H.para(doc,
           f"At t−1 all four models discriminate almost perfectly (AUC ≥ 0.99, Table 8), and DeLong tests find no "
           f"significant difference between any pair (smallest p = {pv(worst['p'])}). The re-estimated MDA and logit "
           f"therefore add nothing to the original Z-score in ranking firms by risk. What re-estimation does show is "
           f"that Altman's cut-offs are set too high for Indian firms. The Youden-optimal cut-off for the original Z "
           f"lies anywhere between {f(roc['youden_lo'])} and {f(roc['youden_hi'])}, so we take its midpoint, "
           f"{f(roc['youden_cut'])}. In sample it classifies every firm correctly. More importantly, when it is "
           f"applied out of time, it classifies {pct(oot2['acc'])} correctly at t−2 and {pct(oot3['acc'])} at t−3, "
           f"{'without flagging a single healthy firm at t−3' if oot3['fp'] == 0 else 'with ' + str(oot3['fp']) + ' healthy firm(s) misclassified at t−3'}. This is in line with the evidence of "
           f"Bandyopadhyay (2006) and Singh and Mishra (2016) that recalibrating the model to local data improves "
           f"accuracy for Indian firms. It is a cut-off for this sample, though, and needs validation on a larger "
           f"one before being used as a rule.")
    H.caption(doc, 'Table 9. Robustness of the t−1 results')
    H.table(doc, ['Specification', 'n', 'Accuracy', 'Type I', 'Type II', 'AUC'],
            [[s['label'], str(s['n']), pct(s['acc']), pct(s['type1']), pct(s['type2']), f(s['auc'], 3)]
             for s in R['sensitivity']], widths=[8.6, 1.0, 1.7, 1.5, 1.5, 1.4], size=8.5)
    sens = {s['label'][:20]: s for s in R['sensitivity']}
    H.para(doc,
           "Table 9 shows that the conclusions do not depend on how the variables are measured or which industries "
           "are included. Using book instead of market equity in X4 leaves the AUC unchanged but raises the Type II "
           "error, because the market had already marked distressed equity down. Excluding the airline and telecom "
           "pairs, whose 2017–2019 industry shocks could drive the result, leaves accuracy essentially unchanged, "
           "and restricting the sample to pairs whose working capital comes entirely from the LSEG data gives the "
           "same picture. Across every specification of the original Z, the Type I error at t−1 is zero, and the "
           "remaining errors are healthy firms flagged as distressed.")


def investment(doc, R):
    doc.add_heading('5.7 Investment implications (RQ4)', level=2)
    inv = pd.DataFrame(R['invest'])
    rows = []
    for _, r in inv.iterrows():
        rows.append([r['company'].replace(' Ltd', ''), '–' if pd.isna(r['Z3']) else f(r['Z3']), f(r['Z2']), f(r['Z1']),
                     pd.Timestamp(r['admission']).strftime('%d %b %Y'), pct(r['d_ret']), pct(r['h_ret'])])
    H.caption(doc, 'Table 10. Z-score path of the distressed firms and share-price change to the admission date')
    H.table(doc, ['Distressed company', 'Z t−3', 'Z t−2', 'Z t−1', 'CIRP admission', 'Share return', 'Peer return'],
            rows, widths=[5.0, 1.4, 1.4, 1.4, 2.4, 1.9, 1.9], size=8.5)
    H.note(doc, 'Share return = change in the NSE closing price (adjusted for corporate actions) from the last trading '
                'day of fiscal year t−1 to the last trading day before the admission order; the peer is measured over '
                'the same window.')
    s_, ff = R['invest_summary'], R['first_flag']
    big = inv[inv.d_ret < -0.8].company.str.replace(' Ltd', '').str.replace(' (India)', '', regex=False).tolist()
    up = inv[inv.d_ret > 0.5].company.str.replace(' Ltd', '').tolist()
    late = inv[inv.Z3.notna() & (inv.Z3 >= 1.81)].company.str.replace(' Ltd', '').str.replace(' Industries', '').tolist()
    H.para(doc,
           f"For an investor, the key question is how early the warning comes and what ignoring it would cost. "
           f"Table 10 shows that the warning came early. Of the {int(inv.Z3.notna().sum())} distressed firms with data "
           f"for t−3, {ff.get('3', 0)} were already in the distress zone three years before admission, and all 15 "
           f"were there by t−2. The exceptions, {' and '.join(late)}, are companies whose distress set in quickly: "
           f"commodity-margin losses at Ruchi, and Future Retail's collapse during the COVID-19 lockdowns. Between the "
           f"end of year t−1 and the admission order, the median distressed share fell {pct(-s_['median_d'])} while "
           f"the median peer gained {pct(s_['median_h'])}. {', '.join(big[:-1])} and {big[-1]} lost more than 80%. A "
           f"few low-priced shares ({', '.join(up)}) rose sharply on speculation about resolution bids. This is a "
           f"reminder that a distress signal measures the risk of default, not short-run price movements, which "
           f"agrees with Campbell, Hilscher and Szilagyi's (2008) finding that distressed stocks deliver poor and "
           f"highly volatile returns.")
    H.para(doc,
           f"For RQ4, the practical rule is simple: a Z below about {f(R['roc']['youden_cut'], 1)}, or a Z'' below "
           f"1.10, should exclude an Indian company from a long-only equity or unsecured-credit portfolio unless "
           f"deeper analysis shows otherwise. A score between that level and 3.0 should prompt an industry-adjusted "
           f"review rather than an automatic sale, especially in steel, power, real estate and telecom, where sound "
           f"firms naturally score low.")


def conclusion(doc, R):
    c181 = _cls(R, 1, 'Z < 1.81'); cpp = _cls(R, 1, "Z'' < 1.10"); c3 = _cls(R, 3, 'Z < 1.81')
    H.para(doc,
           "This project tested Altman's (1968) Z-score on fifteen Indian listed companies admitted to insolvency "
           "under the IBC between 2017 and 2024, each matched with a healthy listed peer, using standalone "
           "statements cross-checked across two independent data compilations and against annual reports. The "
           "main findings are:")
    pts = [
        "All five Altman ratios are significantly lower for distressed firms one and two years before admission, "
        "and all except working capital already differ three years before (RQ1). Retained earnings and operating "
        "profitability separate the groups earliest; liquidity collapses last.",
        f"Every distressed company was in Altman's distress zone a year before admission (Type I error 0%), and "
        f"{c3['tp']} of {c3['n1']} were already there three years before. The original model's weakness for Indian "
        f"firms is false alarms: {c181['fp']} of 15 healthy, capital-intensive peers scored below 1.81, giving overall "
        f"accuracy of {pct(c181['acc'])} at t−1. The emerging-market Z''-score reduces this industry bias and "
        f"reaches {pct(cpp['acc'])} accuracy at t−1, but it loses power faster at longer horizons (RQ2).",
        f"Re-estimating the model on Indian data does not improve the ranking of firms by risk (all AUCs ≥ 0.99; "
        f"DeLong tests not significant). It does show that retained earnings carry the most weight for Indian firms "
        f"and that a lower cut-off of about {f(R['roc']['youden_cut'], 1)} removes most false alarms while keeping "
        f"its early-warning power out of time (RQ3).",
        f"For investors, the Z-score gives a cheap and early warning. Distressed shares lost a median "
        f"{pct(-R['invest_summary']['median_d'])} between the end of year t−1 and admission, while their peers "
        f"gained {pct(R['invest_summary']['median_h'])} (RQ4).",
    ]
    for i, p_ in enumerate(pts, 1):
        H.para(doc, p_, bold_lead=f'({i})', indent=True)
    H.para(doc,
           "Limitations. The matched-pair sample is small (30 firms) and selected on the outcome, which Zmijewski "
           "(1984) shows overstates accuracy; the in-sample cut-off in particular needs validation on a larger, "
           "unmatched population before it is used as a rule. The distressed firms were also deeply distressed by "
           "the time of admission, so the near-perfect t−1 separation partly reflects how late the IBC event occurs "
           "rather than how sensitive the model is. Retained earnings are measured as reserves and surplus, and "
           "share prices for some distressed firms were thinly traded. Future work could use the full population "
           "of listed non-financial firms with a hazard model (Shumway, 2001), add market-based measures such as "
           "distance to default (Hillegeist et al., 2004), and estimate industry-specific cut-offs for India.",
           bold_lead=None)
    H.para(doc,
           "Overall, more than fifty years after it was proposed, Altman's Z-score remains a dependable first screen "
           "of financial health for Indian companies. It rarely misses a company heading for insolvency, but in "
           "capital-intensive industries its cut-offs should be lowered or the Z''-score used instead, so that "
           "sound firms are not flagged as distressed.")


def appendix(doc, R):
    rows = []
    for i, p in enumerate(PAIRS, 1):
        fy = T1_OVERRIDE.get(p[0], t1_year(p[5]))
        rows.append([str(i), p[1].replace(' Ltd', ''), p[3].replace(' Ltd', ''), p[4], p[5].strftime('%d %b %Y'),
                     f'FY{fy - 2}–FY{fy}', p[6]])
    H.caption(doc, 'Table A1. Matched sample, event dates and sources of the admission date')
    H.table(doc, ['#', 'Distressed company', 'Healthy peer', 'Industry', 'CIRP admitted', 'Years (t−3 to t−1)',
                  'Source of admission date'], rows, widths=[0.6, 2.9, 2.9, 2.3, 1.9, 1.9, 4.3], size=7.5)
    H.note(doc, "FY = fiscal year ending 31 March. Future Retail's t−1 is FY2021 because its FY2022 results were "
                "delayed (company filing of 24 May 2022) and no FY2022 statements are available in the data sources. Ratios, raw figures "
                "and the source of every working-capital figure are listed in Z_Score_Dataset.xlsx.")
