"""Matched-pair sample definition.

Event date = date on which the National Company Law Tribunal (NCLT) admitted the
company into the Corporate Insolvency Resolution Process (CIRP) under the
Insolvency and Bankruptcy Code, 2016. t-1 is the last fiscal year (ending 31 March)
that ended at least 90 days before the admission date, so that its audited results
were due to be public under SEBI LODR Regulation 33(3)(d) (60 days) with a 30-day
buffer for late filers. The healthy peer is measured on the same fiscal years.
"""
from datetime import date

PAIRS = [
    # distressed symbol, distressed name, peer symbol, peer name, industry, admission date, admission source
    ('JETAIRWAYS', 'Jet Airways (India) Ltd', 'INDIGO', 'InterGlobe Aviation Ltd', 'Airlines',
     date(2019, 6, 20), 'NCLT Mumbai order on SBI petition (Business Today, 20 Jun 2019)'),
    ('TATASTLBSL', 'Bhushan Steel Ltd', 'JSWSTEEL', 'JSW Steel Ltd', 'Integrated steel',
     date(2017, 7, 26), 'NCLT Principal Bench order on SBI petition (Business Today, 26 Jul 2017)'),
    ('ALOKINDS', 'Alok Industries Ltd', 'VTL', 'Vardhman Textiles Ltd', 'Textiles',
     date(2017, 7, 18), 'NCLT Ahmedabad order on SBI petition (Business Standard, 19 Jul 2017)'),
    ('JPINFRATEC', 'Jaypee Infratech Ltd', 'SOBHA', 'Sobha Ltd', 'Real estate & infrastructure',
     date(2017, 8, 9), 'NCLT Allahabad order on IDBI Bank petition (Business Standard, 10 Aug 2017)'),
    ('LITL', 'Lanco Infratech Ltd', 'TORNTPOWER', 'Torrent Power Ltd', 'Power generation & EPC',
     date(2017, 8, 7), 'NCLT Hyderabad order on IDBI Bank-led petition (BloombergQuint, 9 Aug 2017)'),
    ('AMTEKAUTO', 'Amtek Auto Ltd', 'BHARATFORG', 'Bharat Forge Ltd', 'Auto components (forgings)',
     date(2017, 7, 24), 'NCLT Chandigarh order on Corporation Bank petition (BSE filing, 24 Jul 2017)'),
    ('JYOTISTRUC', 'Jyoti Structures Ltd', 'KEC', 'KEC International Ltd', 'Power transmission EPC',
     date(2017, 7, 4), 'NCLT Mumbai order on SBI petition (Hindustan Times, 5 Jul 2017)'),
    ('RCOM', 'Reliance Communications Ltd', 'BHARTIARTL', 'Bharti Airtel Ltd', 'Telecommunications',
     date(2018, 5, 15), 'NCLT Mumbai order on Ericsson India petition (Business Standard, 16 May 2018)'),
    ('PUNJLLOYD', 'Punj Lloyd Ltd', 'KPIL', 'Kalpataru Power Transmission Ltd', 'Engineering, procurement & construction',
     date(2019, 3, 8), 'NCLT Principal Bench order on ICICI Bank petition (company filing; IBBI)'),
    ('PATANJALI', 'Ruchi Soya Industries Ltd', 'GOKULAGRO', 'Gokul Agro Resources Ltd', 'Edible oils',
     date(2017, 12, 15), 'NCLT Mumbai order on Standard Chartered/DBS petitions (Business Standard; IBBI)'),
    ('EDUCOMP', 'Educomp Solutions Ltd', 'APTECHT', 'Aptech Ltd', 'Education services',
     date(2017, 5, 30), 'NCLT Principal Bench order on Section 10 application (company filing; IBBI)'),
    ('SINTEX', 'Sintex Industries Ltd', 'KPRMILL', 'K.P.R. Mill Ltd', 'Textiles',
     date(2021, 4, 6), 'NCLT Ahmedabad order on Invesco AMC petition, CP(IB) 848/2019 (IBBI)'),
    ('BALLARPUR', 'Ballarpur Industries Ltd', 'JKPAPER', 'JK Paper Ltd', 'Paper',
     date(2020, 1, 17), 'NCLT Mumbai order on Finquest Financial Solutions petition, CP 2915/2019 (company annual report 2019-20; IBBI)'),
    ('FRETAIL', 'Future Retail Ltd', 'DMART', 'Avenue Supermarts Ltd', 'Organised retail',
     date(2022, 7, 20), 'NCLT Mumbai order on Bank of India petition (Business Standard, 20 Jul 2022)'),
    ('JPASSOCIAT', 'Jaiprakash Associates Ltd', 'RAMCOCEM', 'The Ramco Cements Ltd', 'Cement & construction',
     date(2024, 6, 3), 'NCLT Allahabad order on ICICI Bank and SBI petitions (LiveLaw, Jun 2024)'),
]

# Audited results for the year selected by the 90-day rule were not published before the
# admission date, so t-1 is the latest year that had been published. Future Retail told the
# exchanges on 24 May 2022 that it could not approve its FY2022 results (board vacancies).
T1_OVERRIDE = {'FRETAIL': 2021}

# Candidates examined but excluded, with the reason (reported in the methodology section)
EXCLUDED = [
    ('Monnet Ispat & Energy Ltd', 'CIRP admitted 18 Jul 2017', 'no traded share price for FY2015–FY2017 in the price history'),
    ('Videocon Industries Ltd', 'CIRP admitted 6 Jun 2018', 'irregular 18-, 12- and 15-month reporting periods before the event'),
    ('Era Infra Engineering Ltd', 'CIRP admitted 8 May 2018', 'no traded share price available for the pre-event years'),
    ('ABG Shipyard Ltd', 'CIRP admitted 1 Aug 2017', 'no listed shipbuilding peer with a share price for FY2015–FY2017'),
    ('Reliance Naval and Engineering Ltd', 'CIRP admitted 15 Jan 2020', 'historical statements not available in the data source'),
    ('Electrosteel Steels Ltd; Uttam Galva Steels Ltd', 'CIRP admitted 2017–2018', 'historical statements not available in the data source after delisting'),
    ('Essar Steel Ltd; Bhushan Power & Steel Ltd', 'CIRP admitted 2017', 'not listed on an Indian exchange in the pre-event years'),
]


def t1_year(adm):
    """Fiscal year (ending 31 March) of t-1 under the 90-day availability rule."""
    fy = adm.year if adm >= date(adm.year, 3, 31) else adm.year - 1
    if (adm - date(fy, 3, 31)).days < 90:
        fy -= 1
    return fy
