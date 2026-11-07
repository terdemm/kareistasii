# Scene library

| Scene kind | Ready components | Extend when |
|---|---|---|
| actor | Full cartoon, hand-linked props, lift/wait, room day/night | Topic needs different acting or a new character |
| stick | Line figure, lift/eat/walk, expressive face, bite state change | Complex interactions need bespoke pose code |
| science | Stylized body cutaway + heart/lungs/stomach macro | Any claim needs accurate organs/mechanism beyond illustrative symbols |
| paper | Offset parallax papers, date badge, character/object | Actual history needs specific artifacts, architecture and geography |
| timeline | Progressive dates/events | More than four events require pacing/splitting |
| chart | Progressive bars and numeric labels | Negative values/uncertainty require a custom chart implementation |
| kinetic | Sequential emphasized words | Useful as a brief accent; never substitute text cards for an entire story |
| geomap | Actual boundaries, highlighted regions, camera/route/marker | Detailed/historical geography requires a new data source |
| scene3d | Perspective polygon world, orbit, person, room, macro heart | Detailed anatomy, soft shadows, PBR, complex collisions require a higher-quality backend |
| custom | Any independently coded Python scene | Default for an original topic-specific hero action |

## Three 3D looks

`s.space.look`: `sunny` (warm room), `mystery` (dark palette) or `toon` (flat-depth character inside the 3D world). `space` also accepts orbit (radians), angle, radius, height, focal, target, set and xray. Source is scripts/space3d.py; World offers mesh, box, ellipsoid, limb, render. All vertices are projected in 3D and triangles/faces are depth-sorted on CPU.

This is a simple shaded mesh renderer. It has no GPU requirement but no physically based light, depth of field or robust transparent intersections. Detailed cinematic rendering requires a richer backend. Use Blender/Three.js in a capable environment for those specific requests; do not silently downgrade. For x-ray requests, label diagrams as stylized and author anatomy appropriately.

## Original style from screenshots

Infer palette, silhouette rules, line weight, staging, camera rhythm and type hierarchy. Create a new style brief and a new character/prop kit. Do not trace a reference creator's character or copy their scenes/script. Show representative frames before an expensive full render, unless the user already authorized the design. To make a permanent style addition, update the actual packaged resource files and rebuild the ZIP; a temporary project edit does not install a new style.

## Camera and action

Scene fields: zoom (smooth push), pan [x,y] within available overscan, transition "fade" for 150ms fades. Use cuts for causal beats, limited fades for time/setting changes. Remain deterministic at arbitrary times. Custom functions receive design-space canvas 720x1280. Draw scenery to the edge; important action stays within y 240..940. Captions and optional handle are composited last. `--aspect 16:9` and `--aspect 1:1` use a side-caption editorial reframe, not a stretched vertical picture. Redesign a composition in a custom module for a fully cinematic horizontal layout.

## Checkpoints and efficient revisions

`--range START END` renders a timeline segment with matching audio trim. Use it to inspect a revised shot; do not deliver this excerpt as the full video. Full source SRT remains in full-timeline coordinates and is named accordingly for excerpts. Store unchanged audio and layout files; do not redo TTS for a camera-only edit.
