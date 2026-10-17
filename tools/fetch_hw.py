"""Download the electrical 3D models (STEP) + BOMs from Roboparty/RP1_hardware into hw/."""
import json, os, sys, urllib.request, urllib.parse
from concurrent.futures import ThreadPoolExecutor
tree = json.load(open('tree.json', encoding='utf-8'))['tree']
want = [e['path'] for e in tree if e['type'] == 'blob' and (
    (e['path'].startswith('02_PCB/') and ('/03_3D' in e['path'] or '/01_BOM' in e['path']))
    or e['path'].startswith('04_BOM/RP1_BOM_7DOF') or e['path'].startswith('03_Harness/RP1_Harness_BOM'))]
os.makedirs('hw/pcb', exist_ok=True)
def get(p):
    dst = os.path.join('hw', 'pcb', p.replace('/', '__').encode('ascii', 'replace').decode().replace('?', '_'))
    if os.path.exists(dst): return dst
    url = 'https://raw.githubusercontent.com/Roboparty/RP1_hardware/main/' + urllib.parse.quote(p)
    urllib.request.urlretrieve(url, dst); return dst
with ThreadPoolExecutor(6) as ex:
    for d in ex.map(get, want): print(d, os.path.getsize(d)//1024, 'KB')
