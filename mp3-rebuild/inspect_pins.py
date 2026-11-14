from sexpr import *
libs['Espressif']={x[1]:x for x in nodes(parse(Path('/workspace/reference-libraries/espressif/symbols/Espressif.kicad_sym').read_text()),'symbol')}
for lib,name in [('Espressif','ESP32-WROVER-E'),('Interface_Expansion','TCA9534'),('Connector','Micro_SD_Card'),('Audio','PCM5102A'),('Amplifier_Audio','TPA6132A2RTE'),('Battery_Management','MCP73871-2CC'),('Regulator_Switching','TPS63031DSK')]:
 s=sym(lib,name);print(lib,name)
 for sub in nodes(s,'symbol'):
  for p in nodes(sub,'pin'): print(first(p,'number')[1],first(p,'name')[1],p[1])
