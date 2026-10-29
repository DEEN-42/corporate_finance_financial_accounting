"""Fixed prose for the report (sections that do not depend on computed results)."""

TITLE = ("Predicting Financial Distress Using Altman's Z-Score Model: A Matched-Pair Study of "
         "Distressed and Healthy Indian Listed Non-Financial Companies")
COURSE = 'Corporate Finance and Financial Modelling: Term Project'
AREA = 'Area: Investment (financial-health and default-risk assessment before investment decisions)'
TEAM = [('Ayush Kumar Maurya', '23CH3FP43'), ('Debanshu Ghosh', '23CH3FP56'),
        ('Arghadeep Ghosh', '23CH3FP53'), ('Swayam', '23MF3FP26')]
BASE_PAPER = ('Altman, E. I. (1968). Financial ratios, discriminant analysis and the prediction of corporate '
              'bankruptcy. The Journal of Finance, 23(4), 589–609. https://doi.org/10.1111/j.1540-6261.1968.tb00843.x')

INTRO = [
    "An equity or debt investor who commits capital to a company is exposed to the possibility that the company "
    "will be unable to meet its obligations. When that happens, shareholders are usually wiped out and creditors "
    "recover only part of their claims, so an early and inexpensive signal of deteriorating financial health is "
    "valuable at the screening stage of any investment decision. Accounting-based distress models turn the "
    "information in published financial statements into such a signal. The best known of these is the Z-score of "
    "Altman (1968), which combines five financial ratios through multiple discriminant analysis (MDA) into a single "
    "score that separates firms likely to fail from firms likely to survive.",
    "India offers a natural test bed for the model. Before 2016 a creditor of a defaulting Indian company had to "
    "work through a fragmented set of laws (the Sick Industrial Companies Act, debt recovery tribunals, the "
    "SARFAESI Act and winding-up petitions in High Courts), and large defaults were often not resolved for years. "
    "The Insolvency and Bankruptcy Code, 2016 (IBC) replaced this with a single time-bound process: once the "
    "National Company Law Tribunal (NCLT) admits an application, a Corporate Insolvency Resolution Process (CIRP) "
    "starts, the board is suspended and an insolvency professional takes control. On 13 June 2017 the Reserve Bank "
    "of India (RBI) directed banks to refer twelve large accounts, which together made up about a quarter of "
    "banking-system non-performing assets, for insolvency under the Code (Reserve Bank of India, 2017). Many of "
    "them were listed companies whose financial statements had been public for years. The admission of these and "
    "later cases gives a clearly dated, legally defined distress event for a group of listed Indian firms, which "
    "is close in spirit to the bankruptcy-petition event that Altman used for US manufacturers.",
    "This project applies Altman's original Z-score and its emerging-market variant (the Z''-score) to fifteen "
    "Indian listed non-financial companies admitted to CIRP between 2017 and 2024, each matched with a healthy "
    "listed company from the same industry, and measures how well the scores would have warned an investor one, "
    "two and three years before the event. It also re-estimates the discriminant function and a logistic model on "
    "the Indian data, to show which ratios matter most for Indian firms and whether Altman's 1968 weights and "
    "cut-offs still hold.",
]

LIT = [
    ("Univariate and multivariate beginnings.",
     "Beaver (1966) showed that individual ratios, especially cash flow to total debt, differ between failed and "
     "non-failed US firms up to five years before failure. Altman (1968) argued that single ratios can give "
     "conflicting signals and used MDA on 33 bankrupt and 33 matched non-bankrupt manufacturers (1946–1965) to "
     "combine working capital/total assets, retained earnings/total assets, EBIT/total assets, market value of "
     "equity/book value of total liabilities and sales/total assets. The resulting function classified 95% of the "
     "original sample correctly one year before bankruptcy (Type I error 6%, Type II error 3%), but accuracy for "
     "bankrupt firms fell to 72% two years before and to about half three years before. Altman reported a cut-off of 2.675 "
     "that minimised misclassifications and a 'zone of ignorance' between 1.81 and 2.99. Deakin (1972) applied "
     "the fourteen ratios that Beaver had examined one at a time within a series of multivariate discriminant "
     "models."),
    ("Refinements and alternative estimators.",
     "Altman, Haldeman and Narayanan (1977) built the seven-variable ZETA model on a larger and more recent sample "
     "and improved accuracy at longer horizons. Taffler (1983) developed a UK Z-score for listed manufacturers. "
     "Ohlson (1980) replaced MDA with logistic regression, which does not need multivariate normality or equal "
     "covariance matrices and gives a probability of failure directly. Zmijewski (1984) showed that choice-based "
     "(matched) samples and the exclusion of firms with incomplete data bias estimated coefficients and overstate "
     "accuracy, a caution that applies to every matched-pair design, including this one. Shumway (2001) argued "
     "that single-period models ignore how risk changes over time and proposed a hazard model that also adds "
     "market variables."),
    ("Out-of-sample stability.",
     "Begley, Ming and Watts (1996) found that the original Altman and Ohlson models perform worse on 1980s data "
     "than in the periods in which they were estimated, even when their coefficients are re-estimated. Grice and Ingram (2001) found that the "
     "original Z-score predicts bankruptcy less accurately in recent samples than in Altman's original periods "
     "and is less accurate for non-manufacturing firms, although it remains useful for identifying financial "
     "stress short of bankruptcy. "
     "Altman, Iwanicz-Drozdowska, Laitinen and Suvas (2017) tested the Z''-score on firms from 34 countries and "
     "concluded that the model, even with its original coefficients, keeps useful classification power "
     "internationally, and that re-estimating it on local data and adding country- or industry-specific "
     "information improves accuracy. Altman (2018) reviews fifty years of applications of the Z-score family, including the Z'' version for "
     "non-manufacturers and emerging markets, which omits the asset-turnover ratio (X5)."),
    ("Accounting versus market information.",
     "Hillegeist, Keating, Cram and Lundstedt (2004) found that a Black-Scholes-Merton probability of bankruptcy "
     "carries more information than the Z-score or O-score, whereas Agarwal and Taffler (2008) found that for UK "
     "firms the accounting-based z-score performs as well as market-based models and gives larger economic "
     "benefits when used for credit pricing. Campbell, Hilscher and Szilagyi (2008) linked distress to equity "
     "returns, showing that stocks with high predicted failure risk earn anomalously low subsequent returns. That "
     "result gives the investor in our study a direct reason to screen for distress before buying. Wu, Gaunt and Gray (2010) "
     "compared five established models on up-to-date data and found that each contains unique "
     "information but that their performance varies over time. A combined model using key variables from all "
     "five, plus a diversification measure, outperformed them in-sample and out of sample."),
    ("Emerging-market and Indian evidence.",
     "Altman (2005) proposed the emerging-market (EM) score, the four-variable Z''-model with a constant of 3.25 "
     "added so that the score maps onto US bond-rating equivalents, as a starting point for assessing emerging-"
     "market corporate credit. In India, Bandyopadhyay (2006) estimated MDA and logit models for corporate-bond "
     "defaults and found that a re-estimated Z-score clearly beat the original Altman model in the Indian context. "
     "Singh and Mishra (2016) re-estimated the Altman, Ohlson and Zmijewski models on 208 Indian manufacturing "
     "firms and showed that local re-estimation improves accuracy in both estimation and hold-out samples. Singh "
     "and Singla (2023) re-estimated the Z-score coefficients on recent Indian data and found, using ROC analysis "
     "on a test sample, that a newly built logistic model predicted distress more accurately. "
     "Most Indian studies define distress through rating downgrades, defaults on bonds or BIFR registration. "
     "Fewer use the legally defined IBC admission event, and fewer still examine the score's value at the "
     "investor's screening horizon of two to three years. This project addresses that gap."),
]

RQ = [
    ("RQ1", "Do the five Altman ratios (X1–X5), and the composite Z and Z'' scores, differ significantly between "
            "Indian companies that were later admitted to insolvency and matched healthy companies one, two and "
            "three years before the event?"),
    ("RQ2", "How accurately do Altman's original Z-score (with the 1.81 / 2.675 / 2.99 cut-offs) and the "
            "emerging-market Z''-score (1.10 / 2.60) classify the two groups at each horizon, and how do these "
            "accuracies compare with Altman's 1968 benchmarks?"),
    ("RQ3", "When the discriminant function is re-estimated on Indian data, and when a logistic model is "
            "fitted, which ratios carry the most weight? Do the re-estimated models classify better than the "
            "original coefficients out of sample?"),
    ("RQ4", "What do the results imply for an investor who uses the Z-score as a screening tool, in terms of how "
            "early the warning comes, how wrong it can be, and what happens to the share price?"),
]
HYP = ("For each ratio and score, the null hypothesis is H0: μ(distressed) = μ(healthy); the alternative is "
       "H1: μ(distressed) ≠ μ(healthy). Based on Altman (1968), we expect the distressed group to have lower "
       "values of X1–X4 and of Z.")

REFS = [
    "Agarwal, V., & Taffler, R. (2008). Comparing the performance of market-based and accounting-based bankruptcy prediction models. Journal of Banking & Finance, 32(8), 1541–1551. https://doi.org/10.1016/j.jbankfin.2007.07.014",
    "Altman, E. I. (1968). Financial ratios, discriminant analysis and the prediction of corporate bankruptcy. The Journal of Finance, 23(4), 589–609. https://doi.org/10.1111/j.1540-6261.1968.tb00843.x",
    "Altman, E. I. (2005). An emerging market credit scoring system for corporate bonds. Emerging Markets Review, 6(4), 311–323. https://doi.org/10.1016/j.ememar.2005.09.007",
    "Altman, E. I. (2018). Applications of distress prediction models: What have we learned after 50 years from the Z-score models? International Journal of Financial Studies, 6(3), Article 70. https://doi.org/10.3390/ijfs6030070",
    "Altman, E. I., Haldeman, R. G., & Narayanan, P. (1977). ZETA analysis: A new model to identify bankruptcy risk of corporations. Journal of Banking & Finance, 1(1), 29–54. https://doi.org/10.1016/0378-4266(77)90017-6",
    "Altman, E. I., Hotchkiss, E., & Wang, W. (2019). Corporate financial distress, restructuring, and bankruptcy: Analyze leveraged finance, distressed debt, and bankruptcy (4th ed.). Wiley. https://doi.org/10.1002/9781119541929",
    "Altman, E. I., Iwanicz-Drozdowska, M., Laitinen, E. K., & Suvas, A. (2017). Financial distress prediction in an international context: A review and empirical analysis of Altman's Z-score model. Journal of International Financial Management & Accounting, 28(2), 131–171. https://doi.org/10.1111/jifm.12053",
    "Bandyopadhyay, A. (2006). Predicting probability of default of Indian corporate bonds: Logistic and Z-score model approaches. The Journal of Risk Finance, 7(3), 255–272. https://doi.org/10.1108/15265940610664942",
    "Beaver, W. H. (1966). Financial ratios as predictors of failure. Journal of Accounting Research, 4, 71–111. https://doi.org/10.2307/2490171",
    "Begley, J., Ming, J., & Watts, S. (1996). Bankruptcy classification errors in the 1980s: An empirical analysis of Altman's and Ohlson's models. Review of Accounting Studies, 1(4), 267–284. https://doi.org/10.1007/BF00570833",
    "Campbell, J. Y., Hilscher, J., & Szilagyi, J. (2008). In search of distress risk. The Journal of Finance, 63(6), 2899–2939. https://doi.org/10.1111/j.1540-6261.2008.01416.x",
    "Deakin, E. B. (1972). A discriminant analysis of predictors of business failure. Journal of Accounting Research, 10(1), 167–179. https://doi.org/10.2307/2490225",
    "DeLong, E. R., DeLong, D. M., & Clarke-Pearson, D. L. (1988). Comparing the areas under two or more correlated receiver operating characteristic curves: A nonparametric approach. Biometrics, 44(3), 837–845. https://doi.org/10.2307/2531595",
    "Firth, D. (1993). Bias reduction of maximum likelihood estimates. Biometrika, 80(1), 27–38. https://doi.org/10.1093/biomet/80.1.27",
    "Grice, J. S., & Ingram, R. W. (2001). Tests of the generalizability of Altman's bankruptcy prediction model. Journal of Business Research, 54(1), 53–61. https://doi.org/10.1016/S0148-2963(00)00126-0",
    "Hillegeist, S. A., Keating, E. K., Cram, D. P., & Lundstedt, K. G. (2004). Assessing the probability of bankruptcy. Review of Accounting Studies, 9(1), 5–34. https://doi.org/10.1023/B:RAST.0000013627.90884.b7",
    "Insolvency and Bankruptcy Code, 2016, No. 31, Acts of Parliament, 2016 (India).",
    "Lachenbruch, P. A., & Mickey, M. R. (1968). Estimation of error rates in discriminant analysis. Technometrics, 10(1), 1–11. https://doi.org/10.1080/00401706.1968.10490530",
    "Ohlson, J. A. (1980). Financial ratios and the probabilistic prediction of bankruptcy. Journal of Accounting Research, 18(1), 109–131. https://doi.org/10.2307/2490395",
    "Reserve Bank of India. (2017, June 13). RBI identifies accounts for reference by banks under the Insolvency and Bankruptcy Code (IBC) [Press release]. https://www.rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx?prid=40743",
    "Securities and Exchange Board of India. (2015). Securities and Exchange Board of India (Listing Obligations and Disclosure Requirements) Regulations, 2015.",
    "Shumway, T. (2001). Forecasting bankruptcy more accurately: A simple hazard model. The Journal of Business, 74(1), 101–124. https://doi.org/10.1086/209665",
    "Singh, B. P., & Mishra, A. K. (2016). Re-estimation and comparisons of alternative accounting based bankruptcy prediction models for Indian companies. Financial Innovation, 2, Article 6. https://doi.org/10.1186/s40854-016-0026-9",
    "Singh, G., & Singla, R. (2023). Prediction of financial distress in the Indian corporate sector: An improvement over Altman's Z-score model. International Journal of Business Continuity and Risk Management, 13(1). https://doi.org/10.1504/IJBCRM.2023.130287",
    "Taffler, R. J. (1983). The assessment of company solvency and performance using a statistical model. Accounting and Business Research, 13(52), 295–308. https://doi.org/10.1080/00014788.1983.9729767",
    "Wu, Y., Gaunt, C., & Gray, S. (2010). A comparison of alternative bankruptcy prediction models. Journal of Contemporary Accounting & Economics, 6(1), 34–45. https://doi.org/10.1016/j.jcae.2010.04.002",
]
