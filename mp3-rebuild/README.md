# MP3 hardware rebuild — checkpoint, not a production release

This archive is NOT the completed MP3 player and is NOT a fabrication package.
It replaces the previous ad-hoc symbol recovery with a separately scoped digital
core schematic and a routed digital-core PCB prototype. The original complete-board
PCB is still invalid and must not be manufactured. No production-ready PCB,
Gerbers, or assembly files are supplied.

## Completed and checked

- Built a 52-symbol digital-core schematic (50 physical components plus two
  external-supply flags) with explicit pin assignments.
- Used Espressif's official ESP32-WROVER-E symbol and footprint, release 2.0.6,
  commit 3343256bd40fa1d049b444767d4b935ad93ba91f.
- Added EN reset RC, boot/reset switches, boot strapping, bias resistors,
  decoupling, battery ADC divider/filter, TCA9534 expander and seven buttons.
- Provided explicit interfaces for the intended GC9A01 display, SPI SD socket,
  regulated power, UART, I2S audio, and status signals. These interfaces are
  engineering boundaries, not substitutes for the missing product circuits.
- Bundled the symbol and footprint definitions required to open the schematic.
- KiCad 9.0.2 ERC: zero errors, zero warnings, exit status 0.
- KiCad XML export: completed with no annotation warning after reference cleanup.
- Exported connectivity: all 160 physical component-pin assignments match the
  digital-core connection model; specific ESP32 GPIO/reserved-pad assertions pass.
- Exported PDF and visually inspected the sheet. Zoom in for pin labels.
- Routed hardware/digital_core.kicad_pcb with 50 footprints and 36 named nets.
  KiCad 9.0.2 DRC with all severities and schematic parity reports zero
  violations, zero unconnected items and zero schematic parity issues.
  The underlying DRC command completed with exit status 0.
- Independently checked all 160 component-pin net assignments after importing
  copper. Reserved pads remain unassigned. See reports/routed-pad-check.txt.
- Routing was restored on 2026-11-14 using Freerouting 2.0.1. Both routing inputs
  and sessions are retained in engineering/. The ESP32 antenna keep-out is
  retained on both actual copper layers (F.Cu and B.Cu); the local library rule
  area was made specific to those two layers to match the board layer stack.
- The board remains a prototype with roomy 160 x 100 mm placement and 0.2 mm
  routing rules. Power-current capability, return paths, decoupling placement,
  and signal integrity require engineering review and physical validation.

Open hardware/digital_core.kicad_pro in KiCad 9 or newer. The project includes
hardware/digital_core.kicad_sch and hardware/digital_core.kicad_pcb.
See reports/digital-erc.txt, reports/digital-pcb-drc.txt, and
reports/netlist-check.txt for scoped evidence.
Open the extracted project with its matching .kicad_pcb, .kicad_sch and libraries
together. A .kicad_pro file contains project settings, not the routed copper.
Use the latest routed ZIP; the older GitHub commit 77369ca contains an unrouted PCB.
A clean ERC checks schematic rules; it does not prove analog performance,
component ratings, routing, power integrity, or physical operation.

## Historical datasheet-access blocker (not retested during routing)

During the earlier circuit-rebuild session, an HTTPS request to
https://www.ti.com/lit/ds/symlink/tpa6132a2.pdf returned
403 Forbidden at the proxy CONNECT stage. TLS checking was not disabled and the
network restriction was not bypassed.

Required manufacturer-domain additions were saved to the environment draft,
preserving the existing dl.espressif.com entry:
- www.ti.com
- ww1.microchip.com
- www.silabs.com
- www.waveshare.com
- files.waveshare.com
- www.espressif.com
- docs.espressif.com

Review/save the network changes in environment settings and publish the updated
environment configuration. A saved draft alone does not change running access.
After application, retest the affected request before resuming circuit selection.

## Remaining product work

1. Verify the exact Waveshare 1.28-inch GC9A01 module revision, supply, BL input,
   connector order, and mechanical drawing. J2 is the proposed carrier interface;
   do not connect an old ST7789 cable by position.
2. Select and verify the protected 1S 2000 mAh cell. Confirm 4.2 V termination,
   500 mA charging compatibility, temperature sensing, polarity and protection.
3. Rebuild the charger and load-sharing supply from manufacturer references.
   Evaluate MCP73871 power-path charging and a buck-boost regulator capable of
   the complete 3.3 V load at minimum battery voltage. The original AP2112 LDO
   does not maintain 3.3 V over the full single-cell discharge range. Do not
   finalize component values from symbol names or an ERC result.
4. Complete PCM5102A analog supplies, charge pump, output filtering and mode pins.
   Evaluate TPA6132A2 as a concrete headphone-amplifier replacement for the
   original invalid MAX97220A MPN/footprint combination, using its datasheet.
5. Complete the USB-C CC termination, ESD, CP2102N supplies and programming
   circuit, and the actual microSD and headphone socket circuits.
6. Merge sheets into the full product schematic, resolve the complete BOM,
   verify every symbol-to-pad mapping and run full-design ERC.
7. Place and route a new PCB from that verified netlist. Preserve RF antenna
   exclusion, switching-current loops, continuous return paths, analog layout,
   connector mechanics and required thermal copper. Run full DRC and parity.
8. Generate fabrication/assembly outputs only from the final checked board.
9. Implement missing firmware functionality: audio_player_play_file currently
   only updates metadata/state and uses a hardcoded duration. There is no MP3
   decoder producer feeding the PCM ring buffer. The Bluetooth path only delays.
   The display driver remains ST7789-specific. These are confirmed source-code
   gaps, not environment failures.
10. Build and test a prototype: current-limited rail bring-up, charger termination
    and temperature behavior, boot/flash, GC9A01 display, SD access, decoded wired
    and Bluetooth audio, RF operation, noise, battery life and thermal margins.

## Reproduction

With Python 3 and KiCad 9.0.2 standard libraries installed:
  python3 build_digital.py
  kicad-cli sch erc --exit-code-violations -o reports/digital-erc.txt hardware/digital_core.kicad_sch
  kicad-cli sch export netlist --format kicadxml -o engineering/digital_core.xml hardware/digital_core.kicad_sch
  python3 check_netlist.py
  /usr/bin/python3 build_pcb.py
  /usr/bin/python3 apply_routing.py engineering/digital_core.ses
  /usr/bin/python3 apply_routing.py engineering/finish.ses
  kicad-cli pcb drc --schematic-parity --severity-all --exit-code-violations -o reports/digital-pcb-drc.txt hardware/digital_core.kicad_pcb
  kicad-cli sch export pdf -o engineering/digital_core.pdf hardware/digital_core.kicad_sch

Run KiCad commands sequentially because they can update project settings.
The routing sessions apply only to the current component positions and netlist.
If you change either, generate new routing rather than replaying the sessions.
Preserve the bundled official footprint under hardware/libraries/Local.pretty.
3D model paths in standard footprints may refer to an installed KiCad model pack;
3D model availability was not validated and is not included in the ERC claim.

Source licenses and Espressif release source are in sources/. The original
repository's tracked mp3.zip was preserved. This checkpoint makes no certification,
production-release, or end-to-end functionality claim.
