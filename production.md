# Production reference

## Styles

- `merak`: warm cream, navy ink, rust and teal; compact asymmetrical cartoon character, rounded objects. Prefer physical acting and clear scientific diagrams over text cards.
- `gece`: navy rooms, pale outlines, warm amber highlights. Use environment-specific dark windows/lamps; a power cut must change visible lighting.
- `atlas`: muted sand paper colors, teal routes and rust markers. Maps in the example are fictional schematics. Actual geography requires sourced boundaries and correctly labeled locations; never present the abstract polygon as a real country.

These palettes and drawing primitives were independently authored for this package. No example, character code, font or style sheet from the supplied third-party ZIP is included.

## Project JSON

Required top level: `scenes` array. Optional: title, style (merak/gece/atlas), language, handle, sources (URL strings), audio (path relative to JSON file).

Scene fields:

| Field | Meaning |
|---|---|
| text | Narration, required, nonempty |
| duration | Seconds, required, 0.25–30 per scene; replace estimates with measured voice timing |
| kind | actor/detail/diagram/map/custom |
| id / visual | Your custom dispatch key, read in scenes.py |
| prop | phone/parcel/clock/apple/moon; other strings become a labeled token placeholder, so draw topic-specific objects yourself |
| action | lift/wait for bundled actor scene; arbitrary custom actions belong in scenes.py |
| setting | night, or default day; only bundled actor scene consumes this |
| xray | Optional simple stylized diagram, not anatomically detailed or diagnostic |
| badge / label | Optional short on-screen text; avoid screen text repeating narration |
| zoom | Smooth fractional push, default 0.035; keep small |
| captions | false to hide captions |
| caption | Alternative caption text, only used when word timing is absent |
| words | Array of {text,start,end} with seconds relative to this scene |
| sfx | Array of {at,type}; type pop/whoosh, seconds relative to scene |
| route | Array of two or more [x,y] points for an abstract map |

Without `words`, the engine estimates three-word caption groups from scene duration. This is a draft convenience, not forced alignment. With `words`, the active three-word group is displayed only while a word is being spoken. Custom `caption` is ignored when measured words exist.

## Drawing API

`c.p`: bg, ink, accent, cool, paper. `c.im`: Pillow RGB image. `c.d`: ImageDraw object.

- `c.actor(x,y,scale=1,pose=0,expression='curious',holding=None,xray=False)` → hand (x,y). y is upper torso, head extends 175px up, feet 310px down. pose 0..1 raises the right hand.
- `c.prop(kind,x,y,scale=1)` draws a bundled object.
- `c.box((x0,y0,x1,y1),fill,r=20,outline=None,width=4)`.
- `c.oval(box,fill,outline=None,width=4)`.
- `c.line([(x,y),...],fill=None,width=8)`.
- `c.arrow((x0,y0),(x1,y1),fill=None)`.
- `c.text(text,x,y,size=44,fill=None,anchor='mm',max_width=630)` shrinks single-line text to fit.

Custom sample: add moving legs, hand gestures, eye direction, collision/contact, cutaways and independently changing backgrounds. Reading an image reference gives design information, not permission to copy its character or exact scene sequence.

## Toolchain and conditions

Pillow renders raster frames on CPU; FFmpeg encodes H.264/AAC MP4. No JavaScript or GPU dependency. Fonts are resolved on the host (set KU_FONT to a local Unicode font if necessary); fonts are not bundled.

Optional narration uses the open-source edge-tts client to call an external service. It is not offline, not a guaranteed service contract and not a paid API included in this ZIP. Check the service's applicable terms for your intended use. Optional Whisper alignment downloads its own model and may take time on CPU.

Do not add automatic account creation, proxies, payment bypasses or automatic public uploads. A free Claude plan's limits remain intact.
