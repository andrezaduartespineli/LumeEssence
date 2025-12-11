from appsite import app
import os
from pathlib import Path
client = app.test_client()
site_dir = Path(app.root_path) / 'templates' / 'site'
results = []
for p in site_dir.rglob('*.html'):
    rel = p.relative_to(site_dir)
    url1 = '/' + str(rel).replace('\\','/')
    url2 = '/site/' + str(rel).replace('\\','/')
    url3 = '/' + rel.name
    tried = set()
    for url in [url1, url2, url3]:
        if url in tried: continue
        tried.add(url)
        rv = client.get(url)
        results.append((url, rv.status_code))
# print summarized unique failures where status !=200
failures = [r for r in results if r[1] != 200]
print('Checked', len(results), 'requests; failures:', len(failures))
for f in failures:
    print(f[0], f[1])
