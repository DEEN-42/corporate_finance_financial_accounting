"""Altman Z-score study of Indian IBC companies vs matched healthy peers.

Builds the firm-year dataset from cached Screener.in / Sharpely.in data, computes
Altman's ratios and scores, runs every statistical test reported in the paper, and
writes the Excel workbook, figures and a results.json that build_report.py reads.
Run:  python zscore_analysis.py
"""
import json, os, warnings
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import parse_screener as ps
import sharpely_json as sj
from ar_data import AR
from sample import PAIRS, t1_year, T1_OVERRIDE

warnings.filterwarnings('ignore')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FIG = os.path.join(ROOT, 'figures')
os.makedirs(FIG, exist_ok=True)
RNG = np.random.default_rng(20261029)
XS = ['X1', 'X2', 'X3', 'X4', 'X5']
LABEL = {'X1': 'Working capital / Total assets', 'X2': 'Retained earnings / Total assets',
         'X3': 'EBIT / Total assets', 'X4': 'Market value of equity / Total liabilities',
         'X5': 'Sales / Total assets'}
DIST_C, HEALTH_C = '#B5403A', '#2F6C8F'
LAGS_TXT = {1: 't−1', 2: 't−2', 3: 't−3'}

# ----------------------------------------------------------------------------------
# 1. Dataset
# ----------------------------------------------------------------------------------

def build_dataset():
    rows = []
    for k, (dsym, dname, hsym, hname, ind, adm, src) in enumerate(PAIRS, 1):
        fy1 = T1_OVERRIDE.get(dsym, t1_year(adm))
        for sym, name, grp in [(dsym, dname, 1), (hsym, hname, 0)]:
            try:
                data = ps.load(sym)
            except FileNotFoundError:
                print('missing data for', sym)
                continue
            sh = ps.sharpely(sym)
            lseg = sj.annual(sym)
            for lag in (1, 2, 3):
                fy = fy1 - lag + 1
                r = ps.firm_year(sym, fy, data)
                r.update(pair=k, industry=ind, distressed=grp, name=name, lag=lag,
                         admission=adm.isoformat(), admission_source=src, t1_fy=fy1)
                rec, ls, ar = sh.get(fy, {}), lseg.get(fy, {}), AR.get((sym, fy))
                r['ta_sharpely'] = rec.get('ta_sh')
                for key in ('ta', 'tca', 'tcl', 'tl', 're', 'revenue', 'pbt', 'interest', 'shares_basic'):
                    r['lseg_' + key] = ls.get(key)
                # reported current assets / liabilities, in order of preference
                if ls.get('tca') is not None and ls.get('tcl') is not None and ls.get('ta'):
                    r.update(tca=ls['tca'], tcl=ls['tcl'], ta_wc=ls['ta'],
                             wc_source='LSEG standalone statements (annual report data, via Sharpely)')
                elif ar:
                    r.update(tca=ar['tca'], tcl=ar['tcl'], ta_wc=ar['ta'], wc_source=ar['src'])
                elif rec.get('tca') is not None and rec.get('tcl') is not None and rec.get('ta_sh')                         and r['total_assets'] and abs(rec['ta_sh'] / r['total_assets'] - 1) <= 0.05:
                    r.update(tca=rec['tca'], tcl=rec['tcl'], ta_wc=rec['ta_sh'],
                             wc_source='Sharpely statements table (total assets within 5% of standalone)')
                else:
                    r.update(tca=None, tcl=None, ta_wc=None, wc_source='missing')
                rows.append(r)
    df = pd.DataFrame(rows)

    # X1 uses the current assets, current liabilities and total assets of the same source.
    df['X1'] = (df['tca'] - df['tcl']) / df['ta_wc']
    df['wc_ta_gap'] = (df['ta_wc'] - df['total_assets']).abs() / df['total_assets']

    # Shares on the same corporate-action-adjusted basis as the Screener price series:
    # LSEG basic weighted shares; fall back to net profit / EPS when LSEG is missing or
    # differs from it by more than 50% (capital-reduction adjustments).
    alt = df['shares_eps_cr']
    ls_sh = df['lseg_shares_basic']
    use_ls = ls_sh.notna() & (alt.isna() | ((ls_sh / alt - 1).abs() <= 0.5))
    df['shares_cr'] = np.where(use_ls, ls_sh, alt)
    df['shares_source'] = np.where(use_ls, 'LSEG basic weighted shares', 'Net profit / EPS (Screener)')
    df['total_liabilities'] = df['borrowings'] + df['other_liabilities']
    df['book_equity'] = df['equity_capital'] + df['reserves']
    df['mve'] = df['price'] * df['shares_cr']
    df['X2'] = df['reserves'] / df['total_assets']
    df['X3'] = df['ebit'] / df['total_assets']
    df['X4'] = df['mve'] / df['total_liabilities']
    df['X4_book'] = df['book_equity'] / df['total_liabilities']
    df['X5'] = df['sales'] / df['total_assets']
    df['Z'] = 1.2 * df.X1 + 1.4 * df.X2 + 3.3 * df.X3 + 0.6 * df.X4 + 1.0 * df.X5
    df['Z_book'] = 1.2 * df.X1 + 1.4 * df.X2 + 3.3 * df.X3 + 0.6 * df.X4_book + 1.0 * df.X5
    df['Zpp'] = 6.56 * df.X1 + 3.26 * df.X2 + 6.72 * df.X3 + 1.05 * df.X4_book
    df['EM'] = df['Zpp'] + 3.25
    df['Z_zone'] = pd.cut(df.Z, [-np.inf, 1.81, 2.99, np.inf], labels=['Distress', 'Grey', 'Safe'], right=False)
    df['Zpp_zone'] = pd.cut(df.Zpp, [-np.inf, 1.10, 2.60, np.inf], labels=['Distress', 'Grey', 'Safe'], right=False)
    df['group'] = np.where(df.distressed == 1, 'Distressed', 'Healthy')
    return df


# ----------------------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------------------

def winsor(s, lo, hi):
    return s.clip(lo, hi)


def cohen_d(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    sp = np.sqrt(((len(a) - 1) * a.var(ddof=1) + (len(b) - 1) * b.var(ddof=1)) / (len(a) + len(b) - 2))
    return (a.mean() - b.mean()) / sp


def boot_ci_paired(diff, n=5000):
    diff = np.asarray(diff, float)
    means = [RNG.choice(diff, len(diff), replace=True).mean() for _ in range(n)]
    return np.percentile(means, [2.5, 97.5])


def confusion(y, pred_distress):
    y, p = np.asarray(y), np.asarray(pred_distress)
    tp = int(((y == 1) & (p == 1)).sum()); fn = int(((y == 1) & (p == 0)).sum())
    tn = int(((y == 0) & (p == 0)).sum()); fp = int(((y == 0) & (p == 1)).sum())
    n1, n0 = tp + fn, tn + fp
    return dict(tp=tp, fn=fn, tn=tn, fp=fp, n1=n1, n0=n0,
                type1=fn / n1 if n1 else np.nan, type2=fp / n0 if n0 else np.nan,
                acc=(tp + tn) / (n1 + n0) if n1 + n0 else np.nan)


def auc_score(y, s):
    """AUC where higher s = more likely distressed (Mann-Whitney form)."""
    y, s = np.asarray(y), np.asarray(s, float)
    pos, neg = s[y == 1], s[y == 0]
    return (np.greater.outer(pos, neg).sum() + 0.5 * np.equal.outer(pos, neg).sum()) / (len(pos) * len(neg))


def delong(y, s1, s2):
    """DeLong, DeLong & Clarke-Pearson (1988) test for two correlated AUCs."""
    y = np.asarray(y)
    def comps(s):
        s = np.asarray(s, float); pos, neg = s[y == 1], s[y == 0]
        psi = np.greater.outer(pos, neg) + 0.5 * np.equal.outer(pos, neg)
        return psi.mean(axis=1), psi.mean(axis=0), psi.mean()
    v10a, v01a, a1 = comps(s1); v10b, v01b, a2 = comps(s2)
    m, n = len(v10a), len(v01a)
    s10 = np.cov(np.vstack([v10a, v10b])); s01 = np.cov(np.vstack([v01a, v01b]))
    var = (s10[0, 0] + s10[1, 1] - 2 * s10[0, 1]) / m + (s01[0, 0] + s01[1, 1] - 2 * s01[0, 1]) / n
    z = (a1 - a2) / np.sqrt(var) if var > 0 else np.nan
    return a1, a2, z, 2 * (1 - stats.norm.cdf(abs(z))) if var > 0 else np.nan


def boot_auc_ci(y, s, n=3000):
    y, s = np.asarray(y), np.asarray(s, float); out = []
    for _ in range(n):
        i = RNG.integers(0, len(y), len(y))
        if y[i].min() == y[i].max():
            continue
        out.append(auc_score(y[i], s[i]))
    return np.percentile(out, [2.5, 97.5])


def roc_points(y, s):
    y, s = np.asarray(y), np.asarray(s, float)
    thr = np.r_[np.inf, np.sort(np.unique(s))[::-1]]
    tpr = [((s >= t) & (y == 1)).sum() / (y == 1).sum() for t in thr]
    fpr = [((s >= t) & (y == 0)).sum() / (y == 0).sum() for t in thr]
    return np.array(fpr), np.array(tpr), thr


def firth_logit(X, y, iters=100):
    """Firth (1993) bias-reduced logistic regression. X includes the constant column."""
    X, y = np.asarray(X, float), np.asarray(y, float)
    b = np.zeros(X.shape[1])
    for _ in range(iters):
        p = 1 / (1 + np.exp(-X @ b)); W = p * (1 - p)
        info = X.T @ (X * W[:, None]); inv = np.linalg.inv(info)
        h = np.einsum('ij,jk,ik->i', X * np.sqrt(W)[:, None], inv, X * np.sqrt(W)[:, None])
        step = inv @ (X.T @ (y - p + h * (0.5 - p)))
        b = b + step
        if np.max(np.abs(step)) < 1e-8:
            break
    p = 1 / (1 + np.exp(-X @ b)); W = p * (1 - p)
    cov = np.linalg.inv(X.T @ (X * W[:, None]))
    se = np.sqrt(np.diag(cov))
    ll = np.sum(y * np.log(p) + (1 - y) * np.log(1 - p))
    return b, se, ll, p


def lda_fit(X, y):
    """Two-group Fisher discriminant: coefficients, cutoff, Wilks' lambda."""
    X, y = np.asarray(X, float), np.asarray(y)
    X1, X0 = X[y == 1], X[y == 0]
    m1, m0 = X1.mean(0), X0.mean(0)
    n1, n0 = len(X1), len(X0)
    Sw = ((n1 - 1) * np.cov(X1, rowvar=False) + (n0 - 1) * np.cov(X0, rowvar=False))
    Sp = Sw / (n1 + n0 - 2)
    w = np.linalg.solve(Sp, m0 - m1)          # higher score = healthier, as in Altman
    cut = w @ (m1 + m0) / 2
    T = (len(X) - 1) * np.cov(X, rowvar=False)
    wilks = np.linalg.det(Sw) / np.linalg.det(T)
    return w, cut, wilks, Sp


# ----------------------------------------------------------------------------------
# 2. Analysis
# ----------------------------------------------------------------------------------

def main():
    df = build_dataset()
    R = {}
    need = XS + ['X4_book']
    df['complete'] = df[need].notna().all(axis=1)

    # pairs usable at t-1 (both firms complete)
    t1 = df[df.lag == 1]
    ok_pairs = sorted(set(t1[t1.complete].groupby('pair').filter(lambda g: len(g) == 2).pair))
    R['pairs_total'] = len(PAIRS); R['pairs_used'] = len(ok_pairs)
    R['dropped_pairs'] = [PAIRS[p - 1][1] for p in range(1, len(PAIRS) + 1) if p not in ok_pairs]
    df['in_sample'] = df.pair.isin(ok_pairs) & df.complete
    S = df[df.in_sample].copy()

    # winsorised copies (pooled 5th/95th percentile across all in-sample firm-years)
    bounds = {x: S[x].quantile([0.05, 0.95]).values for x in XS + ['X4_book']}
    n_wins = {}
    for x in XS + ['X4_book']:
        lo, hi = bounds[x]
        n_wins[x] = int(((S[x] < lo) | (S[x] > hi)).sum())
        S[x + 'w'] = winsor(S[x], lo, hi)
    for x in ['Z', 'Zpp']:
        lo, hi = S[x].quantile([0.05, 0.95]).values
        S[x + 'w'] = S[x].clip(lo, hi)
    R['winsor'] = {x: dict(lo=float(bounds[x][0]), hi=float(bounds[x][1]), n=n_wins[x]) for x in bounds}
    R['n_firmyears'] = int(len(S)); R['n_by_lag'] = S.groupby(['lag', 'group']).size().unstack().to_dict()
    R['wc_source_counts'] = S.wc_source.value_counts().to_dict()

    # ---------------- data validation: Screener.in vs LSEG (two independent compilations) -------
    val = {}
    for lab, sc, ls in [('Total assets', 'total_assets', 'lseg_ta'), ('Revenue', 'sales', 'lseg_revenue'),
                        ('Profit before tax', 'pbt', 'lseg_pbt'), ('Reserves / retained earnings', 'reserves', 'lseg_re')]:
        v = S.dropna(subset=[sc, ls])
        v = v[v[sc].abs() > 1]
        gap = (v[ls] - v[sc]).abs() / v[sc].abs()
        val[lab] = dict(n=int(len(v)), median=float(gap.median()), within2=float((gap <= 0.02).mean()),
                        within5=float((gap <= 0.05).mean()))
    R['validation'] = val
    g = S.wc_ta_gap.dropna()
    R['validation_wc_ta'] = dict(n=int(len(g)), median=float(g.median()), within5=float((g <= 0.05).mean()))
    R['shares_source_counts'] = S.shares_source.value_counts().to_dict()

    # ---------------- A. descriptive statistics ----------------
    desc = []
    for lag in (1, 2, 3):
        for g in ('Distressed', 'Healthy'):
            sub = S[(S.lag == lag) & (S.group == g)]
            for x in XS + ['Z', 'Zpp']:
                desc.append(dict(lag=lag, group=g, var=x, n=int(sub[x].notna().sum()), mean=sub[x].mean(),
                                 median=sub[x].median(), sd=sub[x].std(), min=sub[x].min(), max=sub[x].max()))
    desc = pd.DataFrame(desc)
    R['desc'] = desc.to_dict('records')

    t1s = S[S.lag == 1]
    corr = t1s[[x + 'w' for x in XS]].corr()
    corr.index = corr.columns = XS
    R['corr'] = corr.round(3).to_dict()
    Xv = sm.add_constant(t1s[[x + 'w' for x in XS]])
    R['vif'] = {XS[i]: float(variance_inflation_factor(Xv.values, i + 1)) for i in range(5)}

    # ---------------- B. Z-score classification ----------------
    cls = []
    for lag in (1, 2, 3):
        sub = S[S.lag == lag]
        y = sub.distressed.values
        rules = [('Z', 'Z < 2.675 (Altman optimal cut-off)', sub.Z < 2.675),
                 ('Z', 'Z < 1.81 (grey zone counted healthy)', sub.Z < 1.81),
                 ('Z', 'Z < 2.99 (grey zone counted distressed)', sub.Z < 2.99),
                 ('Zpp', "Z'' < 1.10 (grey zone counted healthy)", sub.Zpp < 1.10),
                 ('Zpp', "Z'' < 2.60 (grey zone counted distressed)", sub.Zpp < 2.60)]
        for model, rule, pred in rules:
            c = confusion(y, pred.astype(int).values); c.update(lag=lag, model=model, rule=rule); cls.append(c)
    R['classification'] = cls
    zones = []
    for lag in (1, 2, 3):
        for g in ('Distressed', 'Healthy'):
            sub = S[(S.lag == lag) & (S.group == g)]
            for m, col in [('Z', 'Z_zone'), ('Zpp', 'Zpp_zone')]:
                vc = sub[col].value_counts()
                zones.append(dict(lag=lag, group=g, model=m, n=int(len(sub)),
                                  **{z: int(vc.get(z, 0)) for z in ['Distress', 'Grey', 'Safe']}))
    R['zones'] = zones

    # ---------------- C. hypothesis tests ----------------
    tests = []
    for lag in (1, 2, 3):
        sub = S[S.lag == lag]
        wide = sub.pivot_table(index='pair', columns='distressed', values=XS + ['Z', 'Zpp'])
        widew = sub.pivot_table(index='pair', columns='distressed', values=[x + 'w' for x in XS + ['Z', 'Zpp']])
        for x in XS + ['Z', 'Zpp']:
            d_ = sub[sub.distressed == 1][x].dropna(); h_ = sub[sub.distressed == 0][x].dropna()
            pr = wide[x].dropna()
            diff = pr[1] - pr[0]
            sw_d = stats.shapiro(d_).pvalue if len(d_) >= 3 else np.nan
            sw_h = stats.shapiro(h_).pvalue if len(h_) >= 3 else np.nan
            pt = stats.ttest_rel(pr[1], pr[0]) if len(pr) > 2 else None
            wt = stats.ttest_ind(d_, h_, equal_var=False)
            prw = widew[x + 'w'].dropna()
            ptw = stats.ttest_rel(prw[1], prw[0])
            wil = stats.wilcoxon(diff) if len(diff) > 2 else None
            mw = stats.mannwhitneyu(d_, h_, alternative='two-sided')
            ci = boot_ci_paired(diff)
            tests.append(dict(lag=lag, var=x, n_pairs=int(len(pr)), mean_d=d_.mean(), mean_h=h_.mean(),
                              mean_diff=diff.mean(), ci_lo=ci[0], ci_hi=ci[1],
                              shapiro_d=sw_d, shapiro_h=sw_h,
                              paired_t=pt.statistic, paired_p=pt.pvalue, paired_tw=ptw.statistic, paired_pw=ptw.pvalue, welch_t=wt.statistic, welch_p=wt.pvalue,
                              welch_df=None, wilcoxon_p=wil.pvalue if wil else np.nan, mw_p=mw.pvalue,
                              cohen_d=cohen_d(d_, h_)))
    R['tests'] = tests

    # ---------------- D. re-estimated discriminant analysis ----------------
    Xw = [x + 'w' for x in XS]
    T1 = S[S.lag == 1].dropna(subset=Xw)
    X, y = T1[Xw].values, T1.distressed.values
    w, cut, wilks, Sp = lda_fit(X, y)
    n, p = X.shape
    chi = -(n - 1 - (p + 2) / 2) * np.log(wilks)
    chi_p = 1 - stats.chi2.cdf(chi, p)
    sd_pooled = np.sqrt(np.diag(Sp))
    uniF = []
    for j in range(p):
        a, b = X[y == 1, j], X[y == 0, j]
        t, pv = stats.ttest_ind(a, b, equal_var=True)
        uniF.append((t ** 2, pv))
    scaled = w * sd_pooled
    order = np.argsort(-np.abs(scaled))
    score = X @ w
    pred_in = (score < cut).astype(int)
    loo_pred, loo_score = [], []
    for i in range(n):
        m = np.arange(n) != i
        wi, ci_, _, _ = lda_fit(X[m], y[m])
        s_i = X[i] @ wi
        loo_score.append(ci_ - s_i)                    # >0 means distressed side
        loo_pred.append(int(s_i < ci_))
    hold = {}
    for lag in (2, 3):
        H = S[S.lag == lag].dropna(subset=Xw)
        hs = H[Xw].values @ w
        hold[lag] = confusion(H.distressed.values, (hs < cut).astype(int))
    R['lda'] = dict(coef={XS[j]: float(w[j]) for j in range(p)}, cutoff=float(cut),
                    wilks=float(wilks), chi2=float(chi), chi2_df=p, chi2_p=float(chi_p),
                    F={XS[j]: dict(F=float(uniF[j][0]), p=float(uniF[j][1])) for j in range(p)},
                    scaled={XS[j]: float(scaled[j]) for j in range(p)},
                    rank={XS[j]: int(np.where(order == j)[0][0] + 1) for j in range(p)},
                    insample=confusion(y, pred_in), loo=confusion(y, np.array(loo_pred)),
                    holdout={str(k): v for k, v in hold.items()},
                    centroid_d=float(score[y == 1].mean()), centroid_h=float(score[y == 0].mean()))

    # ---------------- E. logistic regression ----------------
    yv = T1.distressed.values.astype(float)
    def fit_logit(cols, data):
        Xl = sm.add_constant(data[cols].values.astype(float))
        try:
            res = sm.Logit(data.distressed.values.astype(float), Xl).fit(disp=0, maxiter=200)
            sep = bool(np.any(np.abs(res.params) > 25) or res.mle_retvals.get('warnflag', 0)
                       or np.any(np.isin(res.predict(Xl).round(6), [0.0, 1.0])))
        except Exception:
            res, sep = None, True
        if res is not None and not sep:
            ll0 = res.llnull
            return dict(method='Maximum likelihood', params=res.params.tolist(), se=res.bse.tolist(),
                        p=res.pvalues.tolist(), ll=float(res.llf), ll0=float(ll0),
                        mcfadden=float(res.prsquared), lr=float(res.llr), lr_p=float(res.llr_pvalue),
                        aic=float(res.aic), prob=res.predict(Xl).tolist())
        b, se, ll, pr = firth_logit(Xl, data.distressed.values)
        ybar = yv.mean(); ll0 = len(yv) * (ybar * np.log(ybar) + (1 - ybar) * np.log(1 - ybar))
        z = b / se
        lr = 2 * (ll - ll0)
        return dict(method='Firth penalised likelihood (complete separation under ML)', params=b.tolist(),
                    se=se.tolist(), p=(2 * (1 - stats.norm.cdf(np.abs(z)))).tolist(), ll=float(ll), ll0=float(ll0),
                    mcfadden=float(1 - ll / ll0), lr=float(lr), lr_p=float(1 - stats.chi2.cdf(lr, len(cols))),
                    aic=float(2 * (len(cols) + 1) - 2 * ll), prob=pr.tolist())
    m1 = fit_logit(['Z'], T1.assign(Z=T1.Z.clip(*T1.Z.quantile([0.05, 0.95]).values)))
    m2 = fit_logit(Xw, T1)
    for m, cols in [(m1, ['Z']), (m2, XS)]:
        m['names'] = ['const'] + cols
        m['odds'] = np.exp(m['params']).tolist()
        m['acc'] = confusion(yv, (np.array(m['prob']) > 0.5).astype(int))
    # LOO probabilities for the 5-ratio logit (Firth always, for stability)
    loo_prob = []
    Xl_all = sm.add_constant(T1[Xw].values.astype(float))
    for i in range(len(T1)):
        msk = np.arange(len(T1)) != i
        b, *_ = firth_logit(Xl_all[msk], T1.distressed.values[msk])
        loo_prob.append(float(1 / (1 + np.exp(-Xl_all[i] @ b))))
    m2['loo_acc'] = confusion(yv, (np.array(loo_prob) > 0.5).astype(int))
    R['logit'] = dict(m1=m1, m2=m2)
    T1 = T1.assign(p_logit=m2['prob'], p_logit_loo=loo_prob, lda_score=score, lda_loo=loo_score)

    # ---------------- F. ROC / AUC ----------------
    scores = {'Altman Z (1968)': -T1.Z.values, "Altman Z'' (emerging market)": -T1.Zpp.values,
              'Re-estimated MDA (LOO)': np.array(loo_score), 'Logit X1-X5 (LOO)': np.array(loo_prob)}
    aucs = {}
    for k, s in scores.items():
        ci = boot_auc_ci(yv, s)
        aucs[k] = dict(auc=float(auc_score(yv, s)), lo=float(ci[0]), hi=float(ci[1]))
    keys = list(scores)
    comps = []
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            a1, a2, z, pv = delong(yv, scores[keys[i]], scores[keys[j]])
            comps.append(dict(a=keys[i], b=keys[j], z=float(z), p=float(pv)))
    fpr, tpr, thr = roc_points(yv, -T1.Z.values)
    j = np.argmax(tpr - fpr)
    zcut = -thr[j]
    above = np.sort(T1.Z.values[T1.Z.values > zcut])
    zmid = float((zcut + above[0]) / 2) if len(above) else float(zcut)   # midpoint to the next score
    R['roc'] = dict(auc=aucs, delong=comps, youden_cut=zmid, youden_lo=float(zcut),
                    youden_hi=float(above[0]) if len(above) else None,
                    youden_tpr=float(tpr[j]), youden_fpr=float(fpr[j]))
    yc = confusion(yv, (T1.Z.values < zmid).astype(int))
    R['roc']['youden_conf'] = yc
    # the India-fitted cut-off is chosen at t-1, then tested out of time at t-2 and t-3
    R['roc']['youden_oot'] = {str(lag): confusion(S[S.lag == lag].distressed.values,
                                                  (S[S.lag == lag].Z.values < zmid).astype(int)) for lag in (2, 3)}
    # AUC by horizon for Z and Z''
    R['auc_by_lag'] = {}
    for lag in (1, 2, 3):
        sub = S[S.lag == lag]
        R['auc_by_lag'][lag] = dict(Z=float(auc_score(sub.distressed, -sub.Z)), Zpp=float(auc_score(sub.distressed, -sub.Zpp)))

    # ---------------- sensitivity ----------------
    sens = []
    def add(label, sub, col, cut):
        c = confusion(sub.distressed.values, (sub[col] < cut).astype(int).values)
        sens.append(dict(label=label, n=int(len(sub)), acc=c['acc'], type1=c['type1'], type2=c['type2'],
                         auc=float(auc_score(sub.distressed, -sub[col]))))
    base = S[S.lag == 1]
    add('Baseline: original Z, market equity (cut-off 2.675)', base, 'Z', 2.675)
    add('Book equity in X4 (cut-off 2.675)', base, 'Z_book', 2.675)
    exc = base[~base.industry.isin(['Airlines', 'Telecommunications'])]
    add('Excluding airline and telecom pairs (cut-off 2.675)', exc, 'Z', 2.675)
    ls_only = base.groupby('pair').filter(lambda g: g.wc_source.str.startswith('LSEG').all())
    add('Pairs with LSEG-sourced working capital only (cut-off 2.675)', ls_only, 'Z', 2.675)
    add('Original Z with the single cut-off 1.81', base, 'Z', 1.81)
    add('Original Z with the single cut-off 2.99', base, 'Z', 2.99)
    add("Z'' (book equity), cut-off 1.10", base, 'Zpp', 1.10)
    R['sensitivity'] = sens

    # ---------------- G. investment view: price path ----------------
    inv = []
    for k in ok_pairs:
        dsym, dname, hsym, hname, ind, adm, src = PAIRS[k - 1]
        row = dict(pair=k, company=dname, peer=hname, admission=adm.isoformat())
        for sym, tag in [(dsym, 'd'), (hsym, 'h')]:
            pr = ps.load(sym)['prices']
            fy1 = T1_OVERRIDE.get(dsym, t1_year(adm))
            p0, d0 = ps.year_end_price(pr, fy1)
            before = [d for d in pr if d < adm.isoformat()]
            p1 = pr[max(before)] if before else None
            row[f'{tag}_p_t1'] = p0; row[f'{tag}_p_adm'] = p1
            row[f'{tag}_ret'] = (p1 / p0 - 1) if p0 and p1 else None
        zz = S[(S.pair == k) & (S.distressed == 1)].set_index('lag').Z
        row.update(Z3=zz.get(3), Z2=zz.get(2), Z1=zz.get(1))
        inv.append(row)
    inv = pd.DataFrame(inv)
    R['invest'] = inv.to_dict('records')
    R['invest_summary'] = dict(median_d=float(inv.d_ret.median()), median_h=float(inv.h_ret.median()),
                               n=int(inv.d_ret.notna().sum()))
    first_flag = []
    for k in ok_pairs:
        zz = S[(S.pair == k) & (S.distressed == 1)].set_index('lag')
        flagged = [lag for lag in (3, 2, 1) if lag in zz.index and zz.loc[lag, 'Z'] < 1.81]
        first_flag.append(max(flagged) if flagged else 0)
    R['first_flag'] = pd.Series(first_flag).value_counts().to_dict()

    # ---------------- figures ----------------
    plt.rcParams.update({'font.family': 'Times New Roman', 'font.size': 10})
    # Fig 1: Z by pair at t-1
    t1p = S[S.lag == 1].sort_values(['pair', 'distressed'], ascending=[True, False])
    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    pairs_ = sorted(t1p.pair.unique()); xpos = np.arange(len(pairs_))
    zd = [t1p[(t1p.pair == k) & (t1p.distressed == 1)].Z.iloc[0] for k in pairs_]
    zh = [t1p[(t1p.pair == k) & (t1p.distressed == 0)].Z.iloc[0] for k in pairs_]
    ax.axhspan(-10, 1.81, color='#F3D9D7', zorder=0); ax.axhspan(1.81, 2.99, color='#EFEFEF', zorder=0)
    ax.bar(xpos - 0.2, np.clip(zd, -3, 8), 0.4, color=DIST_C, label='Distressed (IBC)')
    ax.bar(xpos + 0.2, np.clip(zh, -3, 8), 0.4, color=HEALTH_C, label='Healthy peer')
    ax.axhline(1.81, color='k', lw=0.6, ls='--'); ax.axhline(2.99, color='k', lw=0.6, ls='--')
    for x_, z_ in zip(xpos, zh):
        if z_ > 8:
            ax.text(x_ + 0.2, 8.1, f'{z_:.1f}', ha='center', va='bottom', fontsize=7)
    ax.set_xticks(xpos); ax.set_xticklabels([PAIRS[k - 1][1].replace(' Ltd', '').replace(' (India)', '').replace(' Industries', ' Ind.')
                                              for k in pairs_], rotation=55, ha='right', fontsize=8)
    ax.set_xlim(-1.6, len(pairs_) - 0.4); ax.set_ylim(-3, 9.2)
    ax.set_ylabel('Altman Z-score (t−1)'); ax.legend(frameon=False, fontsize=8, loc='upper center', ncol=2)
    ax.text(-1.5, 0.9, 'Distress zone'.replace(' ', chr(10)), fontsize=7.5, va='center')
    ax.text(-1.5, 2.4, 'Grey zone'.replace(' ', chr(10)), fontsize=7.5, va='center')
    ax.text(-1.5, 4.0, 'Safe zone'.replace(' ', chr(10)), fontsize=7.5, va='center')
    fig.tight_layout(); fig.savefig(os.path.join(FIG, 'fig1_z_by_pair.png'), dpi=220); plt.close(fig)

    # Fig 2: median Z trajectory
    fig, ax = plt.subplots(figsize=(5.6, 3.2))
    for g, c in [('Distressed', DIST_C), ('Healthy', HEALTH_C)]:
        med = [S[(S.lag == l) & (S.group == g)].Z.median() for l in (3, 2, 1)]
        q1 = [S[(S.lag == l) & (S.group == g)].Z.quantile(0.25) for l in (3, 2, 1)]
        q3 = [S[(S.lag == l) & (S.group == g)].Z.quantile(0.75) for l in (3, 2, 1)]
        ax.plot(['t−3', 't−2', 't−1'], med, marker='o', color=c, label=f'{g} (median)')
        ax.fill_between(['t−3', 't−2', 't−1'], q1, q3, color=c, alpha=0.15)
    ax.axhline(1.81, color='k', lw=0.6, ls='--'); ax.axhline(2.99, color='k', lw=0.6, ls='--')
    ax.set_ylabel('Altman Z-score'); ax.legend(frameon=False, fontsize=8)
    fig.tight_layout(); fig.savefig(os.path.join(FIG, 'fig2_z_trajectory.png'), dpi=220); plt.close(fig)

    # Fig 3: box plots of ratios at t-1
    fig, axes = plt.subplots(1, 5, figsize=(7.4, 2.8))
    for ax, x in zip(axes, XS):
        data = [t1s[t1s.distressed == 1][x + 'w'].dropna(), t1s[t1s.distressed == 0][x + 'w'].dropna()]
        bp = ax.boxplot(data, widths=0.6, patch_artist=True, medianprops=dict(color='k'))
        for patch, c in zip(bp['boxes'], [DIST_C, HEALTH_C]):
            patch.set_facecolor(c); patch.set_alpha(0.75)
        ax.set_xticks([1, 2]); ax.set_xticklabels(['D', 'H']); ax.set_title(x, fontsize=10)
        ax.axhline(0, color='grey', lw=0.5)
    fig.tight_layout(); fig.savefig(os.path.join(FIG, 'fig3_boxplots.png'), dpi=220); plt.close(fig)

    # Fig 4: ROC of the original Z and Z'' (fixed Altman coefficients) at each horizon
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.4), sharey=True)
    for ax, col, title in [(axes[0], 'Z', 'Original Z-score'), (axes[1], 'Zpp', "Z''-score")]:
        for lag, c, ls in [(1, '#222222', '-'), (2, '#2F6C8F', '--'), (3, '#B5403A', ':')]:
            sub = S[S.lag == lag]
            f_, t_, _ = roc_points(sub.distressed.values, -sub[col].values)
            ax.plot(f_, t_, color=c, ls=ls, lw=1.6,
                    label=f"{LAGS_TXT[lag]} (AUC {auc_score(sub.distressed, -sub[col]):.2f})")
        ax.plot([0, 1], [0, 1], color='grey', lw=0.6)
        ax.set_title(title, fontsize=10); ax.set_xlabel('False positive rate')
        ax.legend(frameon=False, fontsize=8, loc='lower right')
    axes[0].set_ylabel('True positive rate')
    fig.tight_layout(); fig.savefig(os.path.join(FIG, 'fig4_roc.png'), dpi=220); plt.close(fig)

    # ---------------- workbook ----------------
    cols_raw = ['pair', 'industry', 'name', 'symbol', 'group', 'lag', 'fy', 'admission', 'admission_source',
                'sales', 'pbt', 'interest', 'ebit', 'net_profit', 'eps', 'equity_capital', 'reserves', 'borrowings',
                'other_liabilities', 'total_liabilities', 'total_assets', 'tca', 'tcl', 'ta_wc', 'wc_source',
                'lseg_ta', 'lseg_revenue', 'lseg_pbt', 'lseg_re', 'price', 'price_date', 'shares_cr', 'shares_source', 'mve', 'book_equity']
    cols_ratio = ['pair', 'name', 'group', 'lag', 'fy', 'X1', 'X2', 'X3', 'X4', 'X4_book',
                  'X5', 'Z', 'Z_zone', 'Z_book', 'Zpp', 'Zpp_zone', 'EM', 'in_sample']
    out = os.path.join(ROOT, 'Z_Score_Dataset.xlsx')
    with pd.ExcelWriter(out, engine='openpyxl') as xw:
        pd.DataFrame([dict(pair=i + 1, distressed=p[1], screener_symbol_d=p[0], healthy_peer=p[3], screener_symbol_h=p[2],
                           industry=p[4], cirp_admission=p[5].isoformat(), t1_fiscal_year=f'FY{T1_OVERRIDE.get(p[0], t1_year(p[5]))}',
                           admission_source=p[6], in_sample=(i + 1) in ok_pairs) for i, p in enumerate(PAIRS)]
                     ).to_excel(xw, sheet_name='Sample', index=False)
        df[cols_raw].to_excel(xw, sheet_name='Raw financials (Rs crore)', index=False)
        df[cols_ratio].to_excel(xw, sheet_name='Ratios and scores', index=False)
        desc.to_excel(xw, sheet_name='Descriptive stats', index=False)
        pd.DataFrame(tests).to_excel(xw, sheet_name='Hypothesis tests', index=False)
        pd.DataFrame(cls).to_excel(xw, sheet_name='Classification', index=False)
        T1[['pair', 'name', 'group', 'Z', 'Zpp', 'lda_score', 'lda_loo', 'p_logit', 'p_logit_loo']].to_excel(xw, sheet_name='Model scores t-1', index=False)
        inv.to_excel(xw, sheet_name='Price path', index=False)
        pd.DataFrame([dict(item='Financial statements', source='Screener.in standalone annual P&L and balance sheet, https://www.screener.in/company/<symbol>/'),
                                            dict(item='Share price', source='Screener.in NSE price history (adjusted for corporate actions); last close on or before 31 March'),
                      dict(item='Shares outstanding', source='LSEG basic weighted shares (same adjustment basis as price); net profit / EPS where unavailable'),
                      dict(item='Current assets / liabilities', source='LSEG standalone annual statements embedded in https://sharpely.in/stocks/<symbol>/statements; company annual reports (BSE archive / company website) where LSEG data are absent'),
                      dict(item='CIRP admission dates', source='NCLT orders as reported in company exchange filings, IBBI and financial press (see Sample sheet)')]
                     ).to_excel(xw, sheet_name='Sources', index=False)

    def clean(o):
        if isinstance(o, dict):
            return {str(k): clean(v) for k, v in o.items()}
        if isinstance(o, (list, tuple)):
            return [clean(v) for v in o]
        if isinstance(o, (np.floating, float)):
            return None if np.isnan(o) else float(o)
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, (pd.Timestamp,)):
            return o.isoformat()
        return o
    R['t1_table'] = clean(T1[['pair', 'name', 'group', 'fy', 'X1', 'X2', 'X3', 'X4', 'X4_book', 'X5', 'Z', 'Zpp',
                              'wc_source']].to_dict('records'))
    json.dump(clean(R), open(os.path.join(HERE, 'results.json'), 'w'), indent=1, default=str)
    import finalize_workbook
    finalize_workbook.run()
    print('pairs used', R['pairs_used'], 'dropped', R['dropped_pairs'])
    print('firm-years', R['n_firmyears'], R['n_by_lag'])
    return df, R


if __name__ == '__main__':
    main()
