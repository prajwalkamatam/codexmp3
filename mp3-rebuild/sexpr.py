from pathlib import Path
import re, json, uuid, copy
BASE=Path('/workspace/codexmp3-dev/mp3/ESP32_WROVER_TFT_MP3_Player/hardware')
OUT=Path(__file__).parent/'hardware'
# Parse S-expressions without dropping any existing records.
class Atom(str): pass
def parse(s):
 tokens=re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+',s); stack=[]; root=None
 for t in tokens:
  if t=='(':
   n=[]
   if stack: stack[-1].append(n)
   else: root=n
   stack.append(n)
  elif t==')': stack.pop()
  else: stack[-1].append(json.loads(t) if t.startswith('"') else Atom(t))
 assert not stack
 return root
def dump(n):
 if isinstance(n,list): return '('+' '.join(dump(x) for x in n)+')'
 return str(n) if isinstance(n,Atom) else json.dumps(n,ensure_ascii=False)
def nodes(n,k): return [x for x in n if isinstance(x,list) and x and x[0]==k]
def first(n,k): return next(iter(nodes(n,k)),None)
libs={}
def sym(lib,name):
 if lib not in libs:
  libs[lib]={x[1]:x for x in nodes(parse((Path('/usr/share/kicad/symbols')/(lib+'.kicad_sym')).read_text()),'symbol')}
 s=copy.deepcopy(libs[lib][name]); base=first(s,'extends')
 if base:
  parent=sym(lib,base[1]); inherited=[x for x in parent[2:] if isinstance(x,list) and x[0] not in ('property','extends')]
  s=[x for x in s if x is not base]+inherited
  for sub in nodes(s,'symbol'): sub[1]=re.sub(r'^.*?(_\d+_\d+)$',name+r'\1',sub[1])
 return s
