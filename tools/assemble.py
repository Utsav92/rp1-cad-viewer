import sys
t=open(sys.argv[1],encoding='utf-8').read(); d=open(sys.argv[2],encoding='utf-8').read()
assert '/*__DATA__*/null' in t
open(sys.argv[3],'w',encoding='utf-8').write(t.replace('/*__DATA__*/null', d))
