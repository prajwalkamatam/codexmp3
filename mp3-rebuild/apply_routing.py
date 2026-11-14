"""Import a routing session, restore schematic association, and audit pad nets.

Run with KiCad's system Python: /usr/bin/python3 apply_routing.py SESSION.ses
"""
from pathlib import Path
import json
import sys
import uuid
import pcbnew

root = Path(__file__).resolve().parent
path = root / 'hardware/digital_core.kicad_pcb'
board = pcbnew.LoadBoard(str(path))
if len(sys.argv) == 2:
    assert pcbnew.ImportSpecctraSES(board, str(Path(sys.argv[1]).resolve()))
model = {c['ref']: c for c in json.loads((root / 'engineering/digital_components.json').read_text()) if not c['ref'].startswith('#')}
for net in board.GetNetsByNetcode().values():
    if net.GetNetname() and not net.GetNetname().startswith('/'):
        net.SetNetname('/' + net.GetNetname())
checked = set()
assert {fp.GetReference() for fp in board.GetFootprints()} == set(model)
for fp in board.GetFootprints():
    ref = fp.GetReference()
    fp.SetFPID(pcbnew.LIB_ID('Local', model[ref]['fp'].split(':', 1)[1]))
    path_id = pcbnew.KIID_PATH()
    for key in ['root', ref]:
        path_id.push_back(pcbnew.KIID(str(uuid.uuid5(uuid.NAMESPACE_URL, 'mp3-digital-core/' + key))))
    fp.SetPath(path_id)
    for pad in fp.Pads():
        pin = pad.GetNumber()
        if pin in model[ref]['pins']:
            assert pad.GetNetname().removeprefix('/') == model[ref]['pins'][pin], (ref, pin)
            checked.add((ref, pin))
        else:
            assert not pad.GetNetname(), (ref, pin, 'Unexpected reserved-pad connection')
assert len(checked) == 160
for item in board.GetDrawings():
    if isinstance(item, pcbnew.PCB_TEXT) and 'PLACEMENT DRAFT' in item.GetText():
        item.SetText('ROUTED DIGITAL CORE - PROTOTYPE - NOT COMPLETE MP3 PLAYER')
pcbnew.SaveBoard(str(path), board)
assert pcbnew.LoadBoard(str(path)) is not None
report = f'PASS: {len(checked)} PCB component-pin net assignments match the schematic model.\n'
report += 'PASS: reserved pads remain unassigned.\n'
report += f'Copper items (tracks and vias): {len(list(board.GetTracks()))}\n'
(root / 'reports/routed-pad-check.txt').write_text(report)
print(report)
