# Altman Z-Score Presentation: Study Guide and Script (Debanshu, slides 3 and 4)

Your slot: **Slide 3 (objective and hypotheses) and Slide 4 (dataset and filtration)**, about 2 minutes.
You follow Ayush (background) and hand over to Arghadeep (method).

---

## Part 1: The whole deck in one minute

| # | Slide | Who | What it says |
|---|---|---|---|
| 1 | Title | Ayush | Would Altman's Z-score have warned us about Indian listed firms that later went insolvent under the IBC? 15 distressed firms, each matched with a healthy peer. |
| 2 | Why it matters | Ayush | Insolvency wipes out shareholders. IBC 2016 gives a dated distress event (NCLT admission). Z = 1.2X1 + 1.4X2 + 3.3X3 + 0.6X4 + 1.0X5. Zones: <1.81 distress, 1.81–2.99 grey, >2.99 safe. |
| **3** | **Objective and hypotheses** | **You** | **One objective, four research questions, one null/alternative hypothesis.** |
| **4** | **Dataset and filtration** | **You** | **15+15 firms, 85 firm-years, how the sample was filtered, no look-ahead bias, two data sources cross-checked.** |
| 5 | Methodology | Arghadeep | 5 steps: ratios, tests, classify, re-estimate, investor view. |
| 6 | Results 1 | Arghadeep | Median Z: healthy ~2.8 throughout. Distressed 0.99, then 0.31, then −0.05. All 5 ratios are significantly lower at t−1. Retained earnings (X2) matter most on Indian data. |
| 7 | Results 2 | Swayam | 0% Type I error (no missed failures). 4 of 15 healthy peers were falsely flagged. Distressed shares fell 25% while peers rose 10%. |
| 8 | Conclusion and limitations | Swayam | Z is a good first screen. Use Z'' or a cut-off of about 1.2 for India. Small sample. |
| 9 | Lessons | All four | One lesson each. |
| 10 | Thank you | Swayam | Questions. |

**Story in one sentence:** the Z-score almost never misses a firm heading for insolvency in India, but it raises false alarms for capital-heavy industries, so use Z'' or a lower cut-off.

---

## Part 2: Script (about 2 minutes)

Pace: about 130 words per minute. The script is about 285 words, so roughly 2 minutes 10 seconds with pauses. Words in **bold** are the ones to stress.

### Slide 3: Research objective and hypotheses (about 55 seconds)

> Thanks, Ayush. Our main objective is in the dark box: **is Altman's 1968 Z-score a reliable screening tool for an investor looking at Indian listed companies today?**
>
> We split this into **four research questions**. One: do the ratios and scores actually **differ** between firms that later went insolvent and healthy firms, one to three years before? Two: how **accurately** do Altman's cut-offs classify them? Three: if we re-estimate the model on Indian data, which ratios carry the **most weight**? And four, the practical one: **how early** is the warning, and what happens to the **share price**?
>
> For every ratio, our **null hypothesis** is that the distressed and healthy **means are equal**, against the alternative that they **differ**. Following Altman, we expect the distressed firms to score **lower**.

*(Point at the dark box, then the four RQ cards left to right, then the hypothesis line at the bottom.)*

### Slide 4: Dataset and filtration (about 75 seconds)

> For the data, we follow Altman's **paired design**: **15 distressed and 15 healthy** listed companies. That gives **85 firm-years** across **13 industries**, with insolvency admissions between **2017 and 2024**.
>
> On the left is how we **filtered** the sample. We started with all NSE and BSE companies admitted to insolvency under the IBC. We removed **banks, NBFCs and insurers**, because their balance sheets don't fit these ratios. Then we dropped **nine cases**, such as Monnet Ispat and Videocon, because of missing share prices, irregular reporting periods or no listed peer. That left **15 distressed firms**, each matched to a **same-industry healthy peer**. For example, Jet Airways with IndiGo.
>
> Two design choices matter. First, **timing**: year t−1 is the last fiscal year that closed **at least 90 days before admission**, so an investor could really have seen those numbers. There is **no look-ahead bias**. Second, **data quality**: we cross-checked Screener against LSEG data, and the median gap was **under 0.01%**.
>
> Arghadeep will now explain the method.

*(Point at the four numbers across the top, then the funnel on the left, then the two boxes on the right.)*

### If you are running long, cut these
- Slide 3: the details of RQ1 ("one to three years before") can shrink to "do the ratios differ?".
- Slide 4: the "for example, Jet Airways with IndiGo" sentence and the names Monnet Ispat and Videocon.

### If you have extra time, add this line on slide 4
> Peers are measured on exactly the same fiscal years, so the comparison is like for like.

---

## Part 3: Study guide: concepts you must be able to explain

### Slide 3

**Objective:** test whether a 50-year-old US model (Altman 1968) still works as a quick, cheap first screen for Indian listed companies.

**The four research questions (RQ)**

| RQ | Plain English | Where answered |
|---|---|---|
| RQ1 | Are the ratios (X1–X5) and scores (Z, Z'') lower for firms that later fail, at t−1, t−2, t−3? | Slide 6 |
| RQ2 | How many firms do Altman's cut-offs classify correctly? (1.81, 2.675, 2.99 for Z; 1.10 and 2.60 for Z'') | Slide 7 |
| RQ3 | If we rebuild the model on Indian data, which ratios matter most? | Slide 6 (retained earnings X2 is first) |
| RQ4 | How early is the warning, how often is it wrong, and what happened to share prices? | Slide 7 |

**Hypotheses**
- H0 (null): mean of distressed firms = mean of healthy firms (no difference).
- H1 (alternative): the means differ. This is a two-sided test.
- We *expect* distressed firms to be lower on X1–X4 and Z, from Altman's findings. Two-sided is the safer choice because we don't assume the direction in the test itself.
- It is tested separately for each ratio and score, at each of t−1, t−2 and t−3.
- Result preview: H0 is rejected for all 5 ratios at t−1 (slide 6).

**Time notation**
- t−1 = the last fiscal year before the insolvency admission that investors could have seen.
- t−2 and t−3 = the two years before that.

### Slide 4

**Key terms**
- **IBC:** Insolvency and Bankruptcy Code, 2016. A single, time-bound insolvency law.
- **NCLT:** National Company Law Tribunal. The date it *admits* a case into CIRP is our "event date".
- **CIRP:** Corporate Insolvency Resolution Process.
- **Matched-pair design:** each distressed firm is paired with a healthy peer from the same industry, similar in size, measured over the same years. This controls for industry effects. Altman used the same idea (33 + 33 firms).
- **Look-ahead bias:** using information that was not public yet at the time. That is why t−1 must have closed at least 90 days before admission.
- **Why 90 days:** SEBI listing rules give 60 days to publish audited results, plus a 30-day buffer for late filers.
- **Why exclude banks, NBFCs and insurers:** their balance sheets are mostly financial assets and liabilities, so "working capital" and "sales / total assets" are not comparable with those of industrial firms.

**The numbers on the slide**

| Number | Meaning |
|---|---|
| 15 + 15 | 15 distressed firms and 15 matched healthy peers = 30 firms |
| 85 firm-years | 3 years per firm would be 90. The data are 15, 15, 13 (distressed at t−1, t−2, t−3) and 15, 14, 13 (healthy) = 85. Some t−2 and t−3 years are missing for a few firms (the exact reason per firm is in the report's data tables). |
| 13 industries | See the note below. |
| 2017–24 | Range of CIRP admission dates, from Educomp (May 2017) to Jaiprakash Associates (June 2024). |
| 9 dropped | Cases with no traded price (Monnet Ispat, Era Infra), irregular 12/15/18-month reporting periods (Videocon), no listed peer (ABG Shipyard), statements unavailable (Reliance Naval, Electrosteel Steels, Uttam Galva), or not listed in the pre-event years (Essar Steel, Bhushan Power & Steel). |
| < 0.01% | Median gap between Screener.in and LSEG (via Sharpely) figures. |

**The 15 pairs (distressed with healthy peer)**
Jet Airways – IndiGo · Bhushan Steel – JSW Steel · Alok Industries – Vardhman Textiles · Jaypee Infratech – Sobha · Lanco Infratech – Torrent Power · Amtek Auto – Bharat Forge · Jyoti Structures – KEC · Reliance Communications – Bharti Airtel · Punj Lloyd – Kalpataru Power (KPIL) · Ruchi Soya – Gokul Agro · Educomp – Aptech · Sintex – KPR Mill · Ballarpur – JK Paper · Future Retail – DMart · Jaiprakash Associates – Ramco Cements.

**Data sources:** standalone (not consolidated) financials from Screener.in, cross-checked against LSEG data via Sharpely, plus NSE share prices and annual reports for gaps.

---

## Part 4: Likely questions and short answers

1. **Why only 15 firms?** Few listed non-financial firms passed the filter (listed, has a price, regular reporting periods, has a listed peer). Altman himself used 33 + 33. We list the small sample as a limitation (slide 8).
2. **Why matched pairs?** It controls for industry and size, so differences are due to distress, not sector.
3. **Why two-sided H1 if you expect lower?** The test is a standard two-sided one. Direction is our expectation from Altman, not an assumption built into the test.
4. **What is a Type I error here?** Missing a firm that does fail (calling it safe). It is the costly error for an investor. We got 0%.
5. **What is look-ahead bias and how did you avoid it?** Using numbers an investor could not have seen. We use only fiscal years that closed at least 90 days before admission.
6. **Why standalone, not consolidated?** Insolvency is admitted against the legal entity, so standalone figures match the event. Check the report's methodology section before the Q&A in case you want its exact wording.
7. **Why exclude banks and NBFCs?** The ratios are not comparable (see above).
8. **How do you know the data are right?** Two independent sources agree to within 0.01% at the median.
9. **Why 2017–24?** The IBC started in 2016 and the first big cases came after the RBI referral in June 2017. We included admissions up to June 2024.
10. **Why those peers?** Same industry, closest in size among listed firms. Some, such as JSW Steel, Airtel and Torrent, are capital-heavy and were later falsely flagged (slide 7).

---

## Part 5: Things to double-check before you present

- **"13 industries":** the pair list in `analysis/sample.py` has 14 distinct industry labels (Textiles appears twice, and the two EPC labels are separate). The slide's 13 probably comes from grouping similar labels. Check the report if you want to be sure, or say "about a dozen industries" if asked.
- **"Nine cases":** the exclusion list has 7 rows but 9 company names (two rows hold two companies each: Electrosteel and Uttam Galva, and Essar Steel and Bhushan Power & Steel). So nine is correct. The slide notes name Essar Steel as an example for missing prices, but the reason actually recorded for it is "not listed on an Indian exchange in the pre-event years". Use Monnet Ispat and Videocon as your examples (as in the script above).
- **Future Retail exception:** its t−1 is FY2021, not FY2022, because the company never published FY2022 results. Mention only if asked.
- **Slide 4 title says "dataset and filtration":** the funnel on the left is the "filtration" part. Spend most of your time there.

## Part 6: Delivery tips

- Slide 3 is about 55 seconds, slide 4 about 75 seconds. Practise once aloud with a timer.
- Say the four numbers (15 + 15, 85, 13, 2017–24) clearly. They are the facts people remember.
- Use the hand-off line at the end, "Arghadeep will now explain the method", so the transition is smooth.
- Don't read the slide. The script follows the order of the slide, so you can glance at the boxes as you go.
