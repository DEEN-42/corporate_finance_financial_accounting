"""Download Sharpely.in statements pages (second, independent source for reported
total current assets / liabilities and total assets). Cached in ../raw/sharpely/."""
import os, sys, time, urllib.request

OUT = os.path.join(os.path.dirname(__file__), '..', 'raw', 'sharpely')
os.makedirs(OUT, exist_ok=True)
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

for sym in sys.argv[1:]:
    path = os.path.join(OUT, f'{sym}.html')
    if os.path.exists(path) and os.path.getsize(path) > 50000:
        continue
    for k in range(4):
        try:
            req = urllib.request.Request(f'https://sharpely.in/stocks/{sym.lower()}/statements', headers=UA)
            body = urllib.request.urlopen(req, timeout=90).read().decode('utf8')
            open(path, 'w', encoding='utf8').write(body)
            print(sym, len(body), flush=True)
            break
        except Exception as e:
            print(sym, 'error', e, flush=True)
            time.sleep(15)
    time.sleep(3)
