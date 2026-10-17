"""usage: assemble.py template.html data.json elec.json out.html"""
import sys
t = open(sys.argv[1], encoding='utf-8').read()
d = open(sys.argv[2], encoding='utf-8').read()
e = open(sys.argv[3], encoding='utf-8').read()
assert '/*__DATA__*/null' in t and '/*__ELEC__*/null' in t
open(sys.argv[4], 'w', encoding='utf-8').write(t.replace('/*__DATA__*/null', d).replace('/*__ELEC__*/null', e))
