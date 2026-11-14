#!/usr/bin/env /usr/bin/python3
"""Generate a valid, unrouted KiCad placement draft from digital_components.json."""

from pathlib import Path
import json
import pcbnew


ROOT = Path(__file__).resolve().parent
HARDWARE = ROOT / "hardware"
FOOTPRINTS = HARDWARE / "libraries" / "Local.pretty"
MODEL = json.loads((ROOT / "engineering" / "digital_components.json").read_text())
OUTPUT = HARDWARE / "digital_core.kicad_pcb"


def mm(value):
    return pcbnew.FromMM(value)


def point(x, y):
    return pcbnew.VECTOR2I(mm(x), mm(y))


board = pcbnew.BOARD()
board.GetDesignSettings().SetBoardThickness(mm(1.6))

# The board is deliberately roomy because this is a connectivity/placement draft.
# Production dimensions must come from the enclosure and mechanical drawings.
for start, end in [
    ((0, 0), (160, 0)),
    ((160, 0), (160, 100)),
    ((160, 100), (0, 100)),
    ((0, 100), (0, 0)),
]:
    edge = pcbnew.PCB_SHAPE(board)
    edge.SetShape(pcbnew.SHAPE_T_SEGMENT)
    edge.SetStart(point(*start))
    edge.SetEnd(point(*end))
    edge.SetLayer(pcbnew.Edge_Cuts)
    edge.SetWidth(mm(0.15))
    board.Add(edge)

nets = {}
for component in MODEL:
    for net_name in component["pins"].values():
        if net_name not in nets:
            net = pcbnew.NETINFO_ITEM(board, net_name)
            board.Add(net)
            nets[net_name] = net

# Hand-placed functional blocks, followed by roomy passive grids.
fixed = {
    "U1": (80, 24),
    "U4": (142, 64),
    "J1": (7, 12),
    "J2": (153, 18),
    "J3": (7, 28),
    "J4": (7, 42),
    "J5": (7, 64),
    "J6": (7, 80),
    "SW1": (46, 88),
    "SW2": (58, 88),
    "SW3": (70, 88),
    "SW4": (82, 88),
    "SW5": (94, 88),
    "SW6": (106, 88),
    "SW7": (118, 88),
    "SW8": (130, 88),
    "SW9": (142, 88),
}

resistors = [c for c in MODEL if c["ref"].startswith("R")]
capacitors = [c for c in MODEL if c["ref"].startswith("C")]
for index, component in enumerate(resistors):
    fixed[component["ref"]] = (32 + (index % 9) * 11, 47 + (index // 9) * 10)
for index, component in enumerate(capacitors):
    fixed[component["ref"]] = (120 + (index % 4) * 8, 36 + (index // 4) * 8)

for component in MODEL:
    ref = component["ref"]
    if ref.startswith("#"):
        continue
    library_name = component["fp"].split(":", 1)[1]
    footprint = pcbnew.FootprintLoad(str(FOOTPRINTS), library_name)
    if footprint is None:
        raise RuntimeError(f"Unable to load footprint {library_name} for {ref}")
    footprint.SetReference(ref)
    footprint.SetValue(component["value"])
    footprint.SetPosition(point(*fixed[ref]))
    board.Add(footprint)

    expected_pins = component["pins"]
    actual_pins = {pad.GetNumber() for pad in footprint.Pads()}
    missing = set(expected_pins) - actual_pins
    if missing:
        raise RuntimeError(f"{ref}: footprint lacks pads {sorted(missing)}")
    for pad in footprint.Pads():
        pin = pad.GetNumber()
        if pin in expected_pins:
            pad.SetNet(nets[expected_pins[pin]])

notice = pcbnew.PCB_TEXT(board)
notice.SetText("DIGITAL CORE PLACEMENT DRAFT - UNROUTED - NOT FOR FABRICATION")
notice.SetPosition(point(80, 96))
notice.SetTextSize(point(1.5, 1.5))
notice.SetTextThickness(mm(0.25))
notice.SetLayer(pcbnew.F_SilkS)
notice.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_CENTER)
board.Add(notice)

pcbnew.SaveBoard(str(OUTPUT), board)
loaded = pcbnew.LoadBoard(str(OUTPUT))
if loaded is None:
    raise RuntimeError("KiCad could not reload the generated board")

print(f"Generated {OUTPUT}")
print(f"Footprints: {len(list(loaded.GetFootprints()))}")
print(f"Nets: {len(nets)}")
