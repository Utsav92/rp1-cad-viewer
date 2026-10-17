# RP1 Humanoid: Interactive CAD Viewer

A single-file, browser-based 3D viewer for the [RoboParty RP1](https://github.com/Roboparty/RP1) humanoid.
Open `index.html` (needs internet for three.js from a CDN).

Features: 28 joint sliders with URDF limits, pose presets, walk cycle, part inspector (mass, size, joint axis and limits),
isolate/hide, X-ray/wireframe, colour modes, explode view, section cuts, edge overlay, joint axes, camera presets, PNG export.

## Electrical layer
The **Electrical** tab shows 14 PCB types (18 instances) built from the real STEP models in
[Roboparty/RP1_hardware](https://github.com/Roboparty/RP1_hardware) (`02_PCB`): main RK3588S board, back hub, head board, IMU,
motor capacitor boards, hand adapters, hot-swap, charger dock and more, with part numbers, revisions and BOM stats.
Batteries and waist fans have no CAD in the repo, so they are labelled proxy blocks.
**Placement is approximate**: the repo publishes no robot-level electrical assembly, so positions follow `00_Docs/RP1_Hardware_Architecture.pdf`.

## Rebuild
```
git clone https://github.com/Roboparty/RP1_description desc
python tools/build_data.py desc data.json 520000      # needs trimesh, fast-simplification
# electrical layer (needs cadquery-ocp, scipy, openpyxl, fast-simplification):
#   python tools/fetch_hw.py            # downloads board STEP files + BOMs (~500 MB) into hw/
#   python tools/step2mesh.py <board.step> hw/mesh/<name>.npz 3.0 0.3   # per board, see tools/run_all.sh
#   python tools/build_electrical.py    # -> elec.json
python tools/assemble.py tools/template.html data.json elec.json index.html
```

## Attribution
Robot geometry and kinematics come from [Roboparty/RP1_description](https://github.com/Roboparty/RP1_description)
(meshes decimated to ~520k triangles and embedded in `index.html`). That repository declares no license, so the model
data remains RoboParty's (the RP1_hardware repo is CERN-OHL-W); contact them before any reuse beyond viewing. This is an unofficial viewer.
The viewer code (`tools/`) is MIT-licensed.
