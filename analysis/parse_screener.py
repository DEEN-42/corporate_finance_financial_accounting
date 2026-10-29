"""Parse the cached Screener.in responses into one tidy firm-year table (Rs crore)."""
import html as htmllib, json, os, re
import pandas as pd

RAW = os.path.join(os.path.dirname(__file__), '..', 'raw')


def num(x):
    x = (x or '').replace(',', '').replace('%', '').strip()
    try:
        return float(x)
    except ValueError:
        return None


def section_table(page, sec):
    i = page.find(f'id="{sec}"')
    j = page.find('</section>', i)
    out, header = {}, None
    for r in re.findall(r'<tr[^>]*>(.*?)</tr>', page[i:j], re.S):
        cells = [re.sub(r'\s+', ' ', htmllib.unescape(re.sub(r'<[^>]+>', '', c))).strip()
                 for c in re.findall(r'<t[hd][^>]*>(.*?)</t[hd]>', r, re.S)]
        if header is None:
            header = cells
            continue
        if len(cells) == len(header):
            out[cells[0].replace(' +', '').strip()] = dict(zip(header[1:], cells[1:]))
    return out


def load(sym):
    page = open(os.path.join(RAW, f'{sym}.html'), encoding='utf8').read()
    pl, bs = section_table(page, 'profit-loss'), section_table(page, 'balance-sheet')
    sched = {}
    for p in ['Other_Assets', 'Other_Liabilities', 'Borrowings']:
        f = os.path.join(RAW, f'{sym}_sched_{p}.json')
        if os.path.exists(f):
            sched.update(json.load(open(f, encoding='utf8')))
    prices = {}
    f = os.path.join(RAW, f'{sym}_price.json')
    if os.path.exists(f):
        for ds in json.load(open(f, encoding='utf8')).get('datasets', []):
            if ds['metric'] == 'Price':
                prices = {d: float(v) for d, v in ds['values']}
    fv = re.search(r'Face Value</span>.*?<span class="number">([\d.]+)</span>', page, re.S)
    name = re.search(r'<h1[^>]*>(.*?)</h1>', page, re.S)
    return dict(pl=pl, bs=bs, sched=sched, prices=prices,
                face_value=float(fv.group(1)) if fv else None,
                name=htmllib.unescape(re.sub(r'<[^>]+>', '', name.group(1))).strip() if name else sym)


def year_end_price(prices, fy):
    """Last available closing price on or before 31 March of fiscal year `fy`."""
    cut = f'{fy}-03-31'
    dates = [d for d in prices if d <= cut and d >= f'{fy}-02-15']
    return (prices[max(dates)], max(dates)) if dates else (None, None)


def firm_year(sym, fy, data=None):
    d = data or load(sym)
    col = f'Mar {fy}'
    g = lambda tab, k: num(tab.get(k, {}).get(col))
    s = lambda k: num(d['sched'].get(k, {}).get(col))
    pl, bs = d['pl'], d['bs']
    pbt, interest = g(pl, 'Profit before tax'), g(pl, 'Interest')
    np_, eps = g(pl, 'Net Profit'), g(pl, 'EPS in Rs')
    price, pdate = year_end_price(d['prices'], fy)
    shares_eps = np_ / eps if (np_ and eps) else None          # crore shares
    shares_fv = g(bs, 'Equity Capital') / d['face_value'] if d['face_value'] and g(bs, 'Equity Capital') else None
    return dict(
        symbol=sym, company=d['name'], fy=fy,
        sales=g(pl, 'Sales'), pbt=pbt, interest=interest, ebit=(pbt + interest) if pbt is not None and interest is not None else None,
        net_profit=np_, eps=eps,
        equity_capital=g(bs, 'Equity Capital'), reserves=g(bs, 'Reserves'),
        borrowings=g(bs, 'Borrowings'), other_liabilities=g(bs, 'Other Liabilities'),
        total_assets=g(bs, 'Total Assets'), fixed_assets=g(bs, 'Fixed Assets'), cwip=g(bs, 'CWIP'),
        investments=g(bs, 'Investments'), other_assets=g(bs, 'Other Assets'),
        inventories=s('Inventories'), receivables=s('Trade receivables'), cash=s('Cash Equivalents'),
        loans_advances=s('Loans n Advances'), other_asset_items=s('Other asset items'),
        trade_payables=s('Trade Payables'), advance_customers=s('Advance from Customers'),
        other_liability_items=s('Other liability items'),
        st_borrowings=s('Short term Borrowings'), lt_borrowings=s('Long term Borrowings'), oth_borrowings=s('Other Borrowings'),
        price=price, price_date=pdate, shares_eps_cr=shares_eps, shares_fv_cr=shares_fv, face_value_now=d['face_value'],
    )


def sharpely(sym):
    """Reported Total Current Assets / Liabilities / Total Assets from Sharpely (Rs crore).
    Returns {fy: {'tca':..,'tcl':..,'ta_sh':..,'basis':..}}; basis 'C' = consolidated, 'R' = restated."""
    f = os.path.join(RAW, 'sharpely', f'{sym}.html')
    if not os.path.exists(f):
        return {}
    s = re.sub(r'<svg.*?</svg>', '', open(f, encoding='utf8').read(), flags=re.S)
    header, out = None, {}
    want = {'Total Current Assets': 'tca', 'Total Current Liabilities': 'tcl', 'Total Assets': 'ta_sh'}
    for r in re.findall(r'<tr[^>]*>(.*?)</tr>', s, re.S):
        cells = [re.sub(r'\s+', ' ', htmllib.unescape(re.sub(r'<[^>]+>', '', c))).strip()
                 for c in re.findall(r'<t[hd][^>]*>(.*?)</t[hd]>', r, re.S)]
        if cells and cells[0] == '' and len(cells) > 1 and 'Mar 31' in cells[1]:
            header = cells
            continue
        if header and cells and cells[0] in want and len(cells) == len(header):
            for h, v in zip(header[1:], cells[1:]):
                m = re.match(r'([A-Z]?)(\d{4})Mar 31', h)
                if m:
                    rec = out.setdefault(int(m.group(2)), {})
                    rec[want[cells[0]]] = num(v)
                    rec.setdefault('basis_' + want[cells[0]], m.group(1))
    return out
