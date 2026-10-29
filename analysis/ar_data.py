"""Current assets / current liabilities / total assets (Rs crore) read directly from the
standalone balance sheets in company annual reports, for firms whose figures are not in the
LSEG data. Source PDFs are saved in ../raw/annual_reports/."""

AR = {
    # Bhushan Steel Ltd, Annual Report 2016-17, Standalone Balance Sheet p.36 (Rs lakh; Ind AS,
    # with 31.03.2016 and 01.04.2015 comparatives). BSE: bseplus/annualreport/500055/5000550317.pdf
    ('TATASTLBSL', 2017): dict(tca=5795.29, tcl=27539.10, ta=60463.40, src='Bhushan Steel AR 2016-17, standalone balance sheet, p.36'),
    ('TATASTLBSL', 2016): dict(tca=4106.46, tcl=21273.49, ta=60024.72, src='Bhushan Steel AR 2016-17, standalone balance sheet, p.36 (comparative)'),
    ('TATASTLBSL', 2015): dict(tca=4578.10, tcl=19086.51, ta=60649.69, src='Bhushan Steel AR 2016-17, standalone balance sheet, p.36 (Ind AS opening, 1 Apr 2015)'),
    # Bharat Forge Ltd, Annual Report 2016-17, Balance Sheet pp.114-115 (Rs million).
    ('BHARATFORG', 2017): dict(tca=3504.12, tcl=2294.74, ta=7677.03, src='Bharat Forge AR 2016-17, standalone balance sheet, pp.114-115'),
    ('BHARATFORG', 2016): dict(tca=3428.81, tcl=1884.65, ta=7179.16, src='Bharat Forge AR 2016-17, standalone balance sheet, pp.114-115 (comparative)'),
    ('BHARATFORG', 2015): dict(tca=3904.09, tcl=2039.57, ta=7393.75, src='Bharat Forge AR 2016-17, standalone balance sheet, pp.114-115 (Ind AS opening, 1 Apr 2015)'),
    # Sintex Industries Ltd, Annual Reports 2019-20 (p.68) and 2018-19 (p.62), Rs crore.
    ('SINTEX', 2020): dict(tca=1004.81, tcl=7422.97, ta=10557.93, src='Sintex Industries AR 2019-20, standalone balance sheet, p.68'),
    ('SINTEX', 2019): dict(tca=1719.03, tcl=2422.44, ta=11453.16, src='Sintex Industries AR 2019-20, standalone balance sheet, p.68 (comparative)'),
    ('SINTEX', 2018): dict(tca=1880.08, tcl=1698.44, ta=10419.54, src='Sintex Industries AR 2018-19, standalone balance sheet, p.62 (comparative)'),
    # JK Paper Ltd, Annual Report 2018-19, Standalone Balance Sheet p.100, Rs crore.
    ('JKPAPER', 2019): dict(tca=1266.78, tcl=817.64, ta=4235.64, src='JK Paper AR 2018-19, standalone balance sheet, p.100'),
    ('JKPAPER', 2018): dict(tca=857.64, tcl=793.16, ta=3607.86, src='JK Paper AR 2018-19, standalone balance sheet, p.100 (comparative)'),
}
