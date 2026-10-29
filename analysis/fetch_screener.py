"""Download standalone annual financials, balance-sheet schedules and price history
from Screener.in for every firm in the sample. Raw responses are cached in ../raw/."""
import json, os, sys, time, urllib.request, urllib.parse, re

RAW = os.path.join(os.path.dirname(__file__), '..', 'raw')
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
SYMBOLS = sys.argv[1:]


def get(url, path, tries=6):
    if os.path.exists(path) and os.path.getsize(path) > 200:
        return open(path, encoding='utf8').read()
    for k in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            body = urllib.request.urlopen(req, timeout=60).read().decode('utf8')
            open(path, 'w', encoding='utf8').write(body)
            time.sleep(4)
            return body
        except urllib.error.HTTPError as e:
            wait = 30 * (k + 1) if e.code == 429 else 5
            print('  HTTP', e.code, url, 'retry in', wait, flush=True)
            time.sleep(wait)
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            print('  network error', e, url, flush=True)
            time.sleep(20)
    raise RuntimeError('failed ' + url)


for sym in SYMBOLS:
    print(sym, flush=True)
    try:
        html = get(f'https://www.screener.in/company/{sym}/', os.path.join(RAW, f'{sym}.html'))
    except RuntimeError as e:
        print('  SKIP', sym, e, flush=True)
        continue
    cid = re.search(r'data-company-id="(\d+)"', html).group(1)
    for parent in ['Other Assets', 'Other Liabilities', 'Borrowings']:
        q = urllib.parse.quote(parent)
        get(f'https://www.screener.in/api/company/{cid}/schedules/?parent={q}&section=balance-sheet&consolidated=',
            os.path.join(RAW, f'{sym}_sched_{parent.replace(" ", "_")}.json'))
    get(f'https://www.screener.in/api/company/{cid}/chart/?q=Price&days=10000&consolidated=false',
        os.path.join(RAW, f'{sym}_price.json'))
