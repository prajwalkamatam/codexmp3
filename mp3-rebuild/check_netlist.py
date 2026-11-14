from pathlib import Path
import xml.etree.ElementTree as ET
import json
root=Path(__file__).parent
model=json.loads((root/'engineering/digital_components.json').read_text())
expected={(c['ref'],p):n for c in model if not c['ref'].startswith('#') for p,n in c['pins'].items()}
actual={}
for net in ET.parse(root/'engineering/digital_core.xml').findall('.//nets/net'):
 for node in net.findall('node'):
  key=(node.attrib['ref'],node.attrib['pin'])
  if not key[0].startswith('#'): actual[key]=net.attrib['name'].removeprefix('/')
errors=[]
for key in sorted(set(expected)|set(actual)):
 if actual.get(key)!=expected.get(key): errors.append(f'{key}: expected {expected.get(key)}, exported {actual.get(key)}')
if errors: raise SystemExit('\n'.join(errors))
assert actual[('U1','4')]=='BTN_PWR'
assert actual[('U1','5')]=='BTN_PLAY'
assert actual[('U1','7')]=='IO_INT'
assert actual[('U1','8')]=='I2C_SDA'
assert actual[('U1','9')]=='I2C_SCL'
assert actual[('U1','10')]=='I2S_WS'
assert actual[('U1','11')]=='I2S_BCK'
assert actual[('U1','12')]=='I2S_DATA'
assert actual[('U1','39')]=='GND'
assert actual[('U1','2')]=='+3V3'
assert all(p not in {str(x) for x in range(17,23)}|{'27','28'} for r,p in actual if r=='U1')
result=f'PASS: {len(actual)} exported component-pin assignments match the digital-core model.\nPASS: supply, ground, I2S, I2C, input-only GPIO and reserved-pad assertions.\nScope: digital schematic only; no full-board DRC or production-readiness claim.\n'
(root/'reports/netlist-check.txt').write_text(result)
print(result)
