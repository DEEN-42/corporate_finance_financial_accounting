"""Read the standalone statements that Sharpely.in embeds in its page as JSON
(LSEG data compiled from company annual reports, source code 'IND ARS')."""
import json, os

RAW = os.path.join(os.path.dirname(__file__), '..', 'raw', 'sharpely')
BS = '\\'


def _grab(s, key):
    tag = key + BS + '":'
    i = s.find(tag)
    if i < 0:
        return None
    i += len(tag)
    depth = 0
    for j in range(i, len(s)):
        if s[j] == '{':
            depth += 1
        elif s[j] == '}':
            depth -= 1
            if depth == 0:
                break
    raw = s[i:j + 1].replace(BS + '"', '"').replace(BS + BS, BS)
    return json.loads(raw)


def statements(sym, kind='bal', basis='standalone'):
    f = os.path.join(RAW, f'{sym}.html')
    if not os.path.exists(f):
        return None
    return _grab(open(f, encoding='utf8').read(), f'{kind}_{basis}_annual')


CODES = {'bal': {'ATOT': 'ta', 'STCA': 'tca', 'SCLT': 'tcl', 'STLB': 'tl', 'SRED': 're', 'QTEP': 'equity',
                 'SLSD': 'total_debt'},
         'inc': {'STLR': 'revenue', 'SIBT': 'pbt', 'SIEN': 'interest', 'SEBIT': 'ebit_lseg', 'SNIC': 'pat',
                 'SBASC': 'shares_basic', 'SBAIC': 'eps_basic'}}


def annual(sym, basis='standalone'):
    """{fy: {field: value}} from the embedded LSEG annual statements (Rs crore)."""
    out = {}
    for kind, codes in CODES.items():
        st = statements(sym, kind, basis)
        if not st:
            continue
        cols = st['statement']['columns']
        hdr = {h['period_end_date']: h for h in st.get('header', [])}
        for row in st['statement']['data']:
            if row[0] in codes:
                for c, v in zip(cols, row[1:]):
                    if c.endswith('-03-31'):
                        rec = out.setdefault(int(c[:4]), {})
                        rec[codes[row[0]]] = v
                        h = hdr.get(c, {})
                        rec.setdefault(kind + '_source', h.get('source'))
                        rec.setdefault(kind + '_months', h.get('period_length'))
    return out
