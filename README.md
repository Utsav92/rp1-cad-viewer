# RP1 Humanoid: Interactive CAD Viewer

A single-file, browser-based 3D viewer for the [RoboParty RP1](https://github.com/Roboparty/RP1) humanoid.
Open `index.html` (needs internet for three.js from a CDN).

Features: 28 joint sliders with URDF limits, pose presets, walk cycle, part inspector (mass, size, joint axis and limits),
isolate/hide, X-ray/wireframe, colour modes, explode view, section cuts, edge overlay, joint axes, camera presets, PNG export.

## Rebuild
```
git clone https://github.com/Roboparty/RP1_description desc
python tools/build_data.py desc data.json 520000      # needs trimesh, fast-simplification
python tools/assemble.py tools/template.html data.json index.html
```

## Attribution
Robot geometry and kinematics come from [Roboparty/RP1_description](https://github.com/Roboparty/RP1_description)
(meshes decimated to ~520k triangles and embedded in `index.html`). That repository declares no license, so the model
data remains RoboParty's; contact them before any reuse beyond viewing. This is an unofficial viewer.
The viewer code (`tools/`) is MIT-licensed.
