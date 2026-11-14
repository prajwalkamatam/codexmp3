from sexpr import *
import csv,shutil
ROOT=Path(__file__).parent
OUT=ROOT/'hardware'; OUT.mkdir(exist_ok=True)
libs['Espressif']={x[1]:x for x in nodes(parse((ROOT/'sources/Espressif-2.0.6.kicad_sym').read_text()),'symbol')}
# Deterministic UUIDs make regeneration reviewable.
def uid(s): return str(uuid.uuid5(uuid.NAMESPACE_URL,'mp3-digital-core/'+s))
components=[]
def add(ref,lib,name,value,fp,pins,x,y,section):
 components.append(dict(ref=ref,lib=lib,name=name,value=value,fp=fp,pins={str(k):v for k,v in pins.items()},x=round(round(x/1.27)*1.27,3),y=round(round(y/1.27)*1.27,3),section=section))
RFP='Resistor_SMD:R_0603_1608Metric'; CFP='Capacitor_SMD:C_0603_1608Metric'; SWFP='Button_Switch_SMD:SW_SPST_TL3342'
def r(ref,val,a,b,x,y): add(ref,'Device','R',val,RFP,{1:a,2:b},x,y,'bias')
def c(ref,val,a,b,x,y): add(ref,'Device','C',val,CFP,{1:a,2:b},x,y,'decoupling')
mcunets={1:'GND',2:'+3V3',3:'ESP_EN',4:'BTN_PWR',5:'BTN_PLAY',6:'BATT_SENSE',7:'IO_INT',8:'I2C_SDA',9:'I2C_SCL',10:'I2S_WS',11:'I2S_BCK',12:'I2S_DATA',13:'AMP_ENABLE',14:'STRAP_GPIO12',15:'GND',16:'SD_CS',23:'STRAP_GPIO15',24:'STRAP_GPIO2',25:'ESP_BOOT',26:'TFT_BL',29:'TFT_CS',30:'SPI_SCK',31:'SPI_MISO',33:'TFT_DC',34:'UART_RX',35:'UART_TX',36:'TFT_RST',37:'SPI_MOSI',38:'GND',39:'GND'}
add('U1','Espressif','ESP32-WROVER-E','ESP32-WROVER-E (memory variant TBD)','Local:ESP32-WROVER-E',mcunets,70,110,'MCU')
for i,(net,rail,val) in enumerate([('ESP_EN','+3V3','10k'),('ESP_BOOT','+3V3','10k'),('STRAP_GPIO12','GND','10k'),('STRAP_GPIO2','GND','10k'),('STRAP_GPIO15','+3V3','10k'),('TFT_CS','+3V3','10k'),('SD_CS','+3V3','10k'),('TFT_RST','+3V3','10k'),('AMP_ENABLE','GND','100k'),('TFT_BL','GND','100k')]):
 r('R'+str(i+1),val,rail,net,150+(i%5)*45,55+(i//5)*60)
c('C1','1uF / 10V','ESP_EN','GND',150,175)
c('C2','100nF / 10V','+3V3','GND',195,175)
add('C3','Device','C','10uF / 10V','Capacitor_SMD:C_0805_2012Metric',{1:'+3V3',2:'GND'},240,175,'decoupling')
add('SW8','Switch','SW_Push','RESET',SWFP,{1:'ESP_EN',2:'GND'},285,175,'reset')
add('SW9','Switch','SW_Push','BOOT',SWFP,{1:'ESP_BOOT',2:'GND'},330,175,'reset')
# Display carrier connector: logical interface only; purchased module pin order remains a datasheet gate.
add('J2','Connector_Generic','Conn_01x08','GC9A01 MODULE INTERFACE','Connector_PinHeader_2.54mm:PinHeader_1x08_P2.54mm_Vertical',{1:'+3V3',2:'GND',3:'SPI_MOSI',4:'SPI_SCK',5:'TFT_CS',6:'TFT_DC',7:'TFT_RST',8:'TFT_BL'},420,65,'display')
# Explicit external interfaces keep the unverified power/audio/USB circuits outside this subsystem.
add('J1','Connector_Generic','Conn_01x03','REGULATED 3V3 / GND / BAT SENSE INPUT','Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical',{1:'+3V3',2:'GND',3:'VBAT_SENSE_IN'},420,125,'external power')
add('J3','Connector_Generic','Conn_01x03','3V3 LOGIC UART / GND','Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical',{1:'UART_TX',2:'UART_RX',3:'GND'},420,175,'external USB-UART')
add('J4','Connector_Generic','Conn_01x06','I2S TO PENDING AUDIO SHEET','Connector_PinHeader_2.54mm:PinHeader_1x06_P2.54mm_Vertical',{1:'+3V3',2:'GND',3:'I2S_BCK',4:'I2S_WS',5:'I2S_DATA',6:'AMP_ENABLE'},420,225,'external audio')
add('U4','Interface_Expansion','TCA9534','TCA9534PWR','Package_SO:TSSOP-16_4.4x5mm_P0.65mm',{1:'GND',2:'GND',3:'GND',4:'BTN_NEXT',5:'BTN_PREV',6:'BTN_VOLUP',7:'BTN_VOLDN',8:'GND',9:'BTN_MODE',10:'CHG_STAT',11:'SD_CD',12:'HP_DET',13:'IO_INT',14:'I2C_SCL',15:'I2C_SDA',16:'+3V3'},70,295,'buttons')
for i,net in enumerate(['I2C_SDA','I2C_SCL','IO_INT','BTN_PWR','BTN_PLAY','BTN_NEXT','BTN_PREV','BTN_VOLUP','BTN_VOLDN','BTN_MODE','CHG_STAT','SD_CD','HP_DET']):
 r('R'+str(i+11),'4.7k' if i<2 else '10k','+3V3',net,150+(i%5)*45,250+(i//5)*55)
for i,net in enumerate(['BTN_PWR','BTN_PLAY','BTN_NEXT','BTN_PREV','BTN_VOLUP','BTN_VOLDN','BTN_MODE']):
 add('SW'+str(i+1),'Switch','SW_Push',net,SWFP,{1:net,2:'GND'},70+(i%7)*50,455,'buttons')
c('C4','100nF / 10V','+3V3','GND',70,390)
c('C5','100nF / 10V','BTN_PWR','GND',120,510)
c('C6','100nF / 10V','BTN_PLAY','GND',170,510)
# Battery measurement only. No charging current or cell protection circuit is implied.
r('R24','100k 1%','VBAT_SENSE_IN','BATT_SENSE',220,510)
r('R25','100k 1%','BATT_SENSE','GND',270,510)
c('C7','100nF / 10V','BATT_SENSE','GND',320,510)
add('J5','Connector_Generic','Conn_01x04','CHARGER / CARD / HEADPHONE STATUS','Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical',{1:'CHG_STAT',2:'SD_CD',3:'HP_DET',4:'GND'},420,300,'external status')
add('J6','Connector_Generic','Conn_01x06','3V3 SPI MICROSD INTERFACE','Connector_PinHeader_2.54mm:PinHeader_1x06_P2.54mm_Vertical',{1:'+3V3',2:'GND',3:'SPI_MOSI',4:'SPI_MISO',5:'SPI_SCK',6:'SD_CS'},420,390,'external SD socket')
r('R26','10k','+3V3','SPI_MISO',370,510)
# Flags represent the regulated external supply at J1, not a fictitious on-board regulator.
for i,net in enumerate(['+3V3','GND']): add('#FLG'+str(i+1),'power','PWR_FLAG','PWR_FLAG','',{1:net},420+i*45,510,'power source declaration')
# Vendor every used footprint; no global footprint configuration is required.
for comp in components:
 if comp['fp'] and not comp['fp'].startswith('Local:'):
  lib,foot=comp['fp'].split(':'); source=Path('/usr/share/kicad/footprints')/(lib+'.pretty')/(foot+'.kicad_mod')
  assert source.exists(),source
  shutil.copy(source,OUT/'libraries/Local.pretty'/source.name)
  comp['fp']='Local:'+foot
rootid=uid('root'); root=[Atom('kicad_sch'),[Atom('version'),Atom('20230121')],[Atom('generator'),'eeschema'],[Atom('uuid'),rootid],[Atom('paper'),'A1'],[Atom('title_block'),[Atom('title'),'MP3 digital core — SUBSYSTEM ONLY'],[Atom('rev'),'2-DIGITAL-DRAFT'],[Atom('comment'),Atom('1'),'External power, audio, USB and SD interfaces: full product pending datasheet verification']]]
embedded=[Atom('lib_symbols')];cache={}
for comp in components:
 lid=comp['lib']+':'+comp['name']
 if lid not in cache:
  d=sym(comp['lib'],comp['name']); d[1]=lid; cache[lid]=d;embedded.append(d)
root.append(embedded)
for comp in components:
 ref=comp['ref'];x=comp['x'];y=comp['y'];lid=comp['lib']+':'+comp['name'];d=cache[lid]
 inst=[Atom('symbol'),[Atom('lib_id'),lid],[Atom('at'),Atom(str(x)),Atom(str(y)),Atom('0')],[Atom('unit'),Atom('1')],[Atom('in_bom'),Atom('no' if ref.startswith('#') else 'yes')],[Atom('on_board'),Atom('no' if ref.startswith('#') else 'yes')],[Atom('dnp'),Atom('no')],[Atom('uuid'),uid(ref)]]
 for key,val,dy in [('Reference',ref,-18),('Value',comp['value'],-15),('Footprint',comp['fp'],0)]:
  prop=[Atom('property'),key,val,[Atom('at'),Atom(str(x)),Atom(str(y+dy)),Atom('0')],[Atom('effects'),[Atom('font'),[Atom('size'),Atom('1.27'),Atom('1.27')]]]]
  if key=='Footprint': prop[-1].append([Atom('hide'),Atom('yes')])
  inst.append(prop)
 seen=set()
 for sub in nodes(d,'symbol'):
  for pin in nodes(sub,'pin'):
   num=str(first(pin,'number')[1]);seen.add(num);net=comp['pins'][num]
   inst.append([Atom('pin'),num,[Atom('uuid'),uid(ref+'.'+num)]])
   at=first(pin,'at');px=x+float(at[1]);py=y-float(at[2]);angle=float(at[3]);ex,ey=px,py
   if angle==0: ex-=7.62
   elif angle==180: ex+=7.62
   elif angle==90: ey+=7.62
   elif angle==270: ey-=7.62
   else: raise ValueError(angle)
   def pt(xx,yy): return [Atom('xy'),Atom(f'{xx:.3f}'),Atom(f'{yy:.3f}')]
   root.append([Atom('wire'),[Atom('pts'),pt(px,py),pt(ex,ey)],[Atom('stroke'),[Atom('width'),Atom('0')],[Atom('type'),Atom('default')]],[Atom('uuid'),uid(ref+'.wire.'+num)]])
   # Local labels connect throughout the single sheet.
   root.append([Atom('label'),net,[Atom('at'),Atom(f'{ex:.3f}'),Atom(f'{ey:.3f}'),Atom('0')],[Atom('effects'),[Atom('font'),[Atom('size'),Atom('1.0'),Atom('1.0')]],[Atom('justify'),Atom('left'),Atom('bottom')]],[Atom('uuid'),uid(ref+'.label.'+num)]])
 assert seen==set(comp['pins']), (ref,seen,set(comp['pins']))
 inst.append([Atom('instances'),[Atom('project'),'digital_core',[Atom('path'),'/'+rootid,[Atom('reference'),ref],[Atom('unit'),Atom('1')]]]])
 root.append(inst)
root.append([Atom('text'),'SUBSYSTEM ONLY — DO NOT FABRICATE AS COMPLETE MP3 PLAYER.\nPower supply, charger, headphone amplifier, USB and SD socket circuits are external interfaces here.\nPin-level connectivity is checked; electrical ratings and the full product remain under review.',[Atom('at'),Atom('35'),Atom('25'),Atom('0')],[Atom('effects'),[Atom('font'),[Atom('size'),Atom('2'),Atom('2')]],[Atom('justify'),Atom('left'),Atom('bottom')]],[Atom('uuid'),uid('notice')]])
(OUT/'digital_core.kicad_sch').write_text(dump(root)+'\n')
(ROOT/'engineering/digital_components.json').write_text(json.dumps(components,indent=2))
with (ROOT/'engineering/digital_pinmap.csv').open('w') as f:
 w=csv.writer(f);w.writerow(['reference','pin','net','symbol','footprint'])
 for comp in components:
  for pin,net in comp['pins'].items(): w.writerow([comp['ref'],pin,net,comp['lib']+':'+comp['name'],comp['fp']])
# Footprint vendored from official 2.0.6 release.
print('Generated',len(components),'components with explicit pin assignments')

# Self-contained, resolved symbol libraries matching embedded definitions.
for lib in {c['lib'] for c in components}:
 defs=[]
 for lid,d in cache.items():
  if lid.split(':')[0]==lib:
   d=copy.deepcopy(d);d[1]=lid.split(':')[1];defs.append(d)
 (OUT/'libraries'/(lib+'.kicad_sym')).write_text(dump([Atom('kicad_symbol_lib'),[Atom('version'),Atom('20231120')],[Atom('generator'),Atom('kicad_symbol_editor')]]+defs)+'\n')
table=[Atom('sym_lib_table'),[Atom('version'),Atom('7')]]
for lib in sorted({c['lib'] for c in components}):
 table.append([Atom('lib'),[Atom('name'),lib],[Atom('type'),'KiCad'],[Atom('uri'),'${KIPRJMOD}/libraries/'+lib+'.kicad_sym'],[Atom('options'),''],[Atom('descr'),'Vendored symbols; see source attribution']])
(OUT/'sym-lib-table').write_text(dump(table)+'\n')
(OUT/'digital_core.kicad_pro').write_text(json.dumps({'meta':{'filename':'digital_core.kicad_pro','version':1}},indent=2))
