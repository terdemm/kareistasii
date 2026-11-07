---
name: kare-ustasi
description: Create original narrated 2D animated Shorts, Reels and explainers from a topic, including script, acting characters, scene-specific code, captions, procedural sound and an MP4. Use for Kare Ustası animation tutorials, flat cartoon stories, science cutaways, stick-style storytelling or map explainers. Supports local Turkish narration with automatic GitHub setup and the original English Kokoro helper or a supplied recording. CPU rendering with Python, Pillow and FFmpeg; no paid image/video generation API required.
---

# Kare Ustası

Build an animated short, not a slideshow. Work in a new project directory. Resolve `SKILL_DIR` to this file's parent; never assume a fixed installation path. Keep installed resources unchanged and customize copies in the project.

## Execution and honesty

First run `python SKILL_DIR/scripts/doctor.py`. Require Python 3.10+, Pillow and FFmpeg. Install Pillow only when needed (`python -m pip install Pillow`). Check FFmpeg availability; if absent, use an available package manager or request the user install FFmpeg. Do not claim an MP4 exists without rendering it.

This package does not unlock models or remove Claude usage limits. A Free account must expose Skills and code/file execution. If execution, dependency installation or internet access is unavailable, explain the actual blocker. Offer downloadable source files or a local run, clearly distinguishing those from a finished MP4. Never promise unlimited free production.

Use a 360x640, 12fps test first. Final defaults: 720x1280, 24fps, 25–40 seconds. Use `--width 1080 --fps 30` when requested and feasible. No Chromium, Node, GPU, paid generation service or video model is required by this renderer. Online narration still needs network access.

## Story and visual plan

Infer topic, language, length and tone from the request; default to Turkish, approximately 30 seconds, conversational narration, captions on, music off. If the request says to produce the video, proceed after briefly showing the plan; do not add a second permission gate. Ask only for a genuinely missing central topic.

Write a hook whose action is visible in the first second. Write 60–90 words for approximately 30–40 seconds, then use the measured voice duration instead of forcing that estimate. Keep natural connected sentences. Split at visual/action beats, including inside sentences; do not mechanically equate one sentence with one picture. Never promise virality.

For each beat specify: narration, exact visible action, scene setting, camera, object positions, the causal reveal and optional sound cue. Change composition every 1.5–4 seconds. Do not depict repeated generic talking poses beneath unrelated narration. Fact-check factual claims against primary sources and record URLs in project `sources`; if browsing is unavailable, flag verification as incomplete. Use a fictional everyday story for a tool demo if verification would otherwise block production.

Read [references/production.md](references/production.md) for visual styles, schema and customization. Study `assets/demo.json` only as an API example, never as the default script for unrelated topics.

## Create topic-specific artwork and motion

Copy `assets/custom_scene.py` into the new project as `scenes.py`, then replace its drawing logic with original scenes for this topic. Use the Canvas API from `scripts/studio.py`. The bundled actor, props, arrow and primitives reduce setup, but are not a sufficient visual vocabulary for every subject. Add the required organs, animals, mechanisms, objects and scenery as Python drawing functions in the project module.

Use `draw(c,t,d,s,p)` as the entry point; dispatch on an added scene `id` or `visual` field. Keep drawing a pure function of time. Derive all poses, cameras and effects from `t`; never mutate animation state across frames. Use smooth easing, expressive face/arm poses, anticipation, contact and follow-through. Keep held objects attached to hand coordinates; show consumption, damage and lighting changes when narrated. Avoid camera shake unless explicitly requested. Keep the important action within x 50–670, y 240–940; captions occupy y 1005–1125. The renderer supplies a smooth camera push, captions and an optional single handle after your scene draw.

## Voice and alignment

Use `python SKILL_DIR/scripts/narrate.py PROJECT/project.json`. Infer the requested narration language and store it in project.language. No user engine/voice prompt is required. English uses the preserved local Kokoro voice helper with its original sentence grouping, pacing and cut timing; default am_michael, optional p.voice override. Its original Whisper word helper is retained in speech/kokoro/words.py and works on speech-work/script.json, data/narration.wav and data/lines.json. It is English-only; do not apply small.en or its ASCII alignment normalization to Turkish. Helper-model first downloads still require permitted network access. Dependencies are installed only when needed and permitted. No Bing/Edge speech endpoint is part of the default route.

Turkish uses local Supertonic 3 ONNX through sherpa-onnx. Just run `python SKILL_DIR/scripts/narrate.py PROJECT/project.json --language tr`; no extra user voice instruction or attachment is needed. First use automatically installs sherpa-onnx 2.0.1 and its core from PyPI into PROJECT/speech-work/runtime and downloads the official model archive (~128 MB) from `https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/sherpa-onnx-supertonic-3-tts-int8-2026-05-11.tar.bz2`. GitHub redirects to release-assets.githubusercontent.com. This route does not contact Hugging Face, Bing or an online speech service. Setup verifies the archive SHA-256 and caches only the required local model files under ~/.cache/kare-ustasi/supertonic-3. KARE_SUPERTONIC_MODELS may override the cache path. Run the same command with --offline only after first setup completes; it never downloads in offline mode. Runtime target: Linux x86_64 CPython 3.10–3.13. Default speaker 0, 12 steps, speed 1.0; optional project.turkish_voice_id (0–9) and project.speed. Synthesize connected sentences; review pronunciation and prosody before the final render. Check speech setup before doing a full animation render, retaining all finished artwork if a network restriction blocks setup. Model licensing is OpenRAIL-M (commercial use permitted subject to included use restrictions); see speech/supertonic/LICENSE.txt and NOTICE.txt.

For a supplied recording use the original `scripts/voice.py --align RECORDING --language LANGUAGE` with multilingual Whisper. Keep original scenes, narration text and all completed visual work if speech fails. Never substitute robot tones or silently deliver an unvoiced final. Measure scene durations from audio. Word times remain estimates unless explicitly aligned; never describe them as measured on the basis of a successful encode.

## Optional additional visual tools

Keep scripts/studio.py and assets/custom_scene.py as the primary animation foundation. Additional backends live in addons/visuals and are used only for requested maps, charts, timelines, paper/science primitives or simple mesh diagrams. Read references/maps.md and references/scene-library.md as appropriate. Their script paths resolve to SKILL_DIR/addons/visuals, not SKILL_DIR/scripts. The geographic data is bundled under addons/assets. Use addons/visuals/studio.py to render a separate map/diagram project; do not silently swap it in for character stories. Detailed topical scenes must still be authored in a project-local module using the original Canvas API. These additions do not change the primary character drawing, camera, captions, sound synthesis or custom-scene API.

## Render, inspect, improve

Validate the final voiced project and create a contact sheet:

```bash
python SKILL_DIR/scripts/studio.py PROJECT/project-voiced.json --check
python SKILL_DIR/scripts/studio.py PROJECT/project-voiced.json --module PROJECT/scenes.py --out PROJECT/review --sheet-only
```

Open the contact sheet. Inspect action beginnings, middles and endings plus extra frames around contacts/transitions. Fix clipping, repeated scenes, unreadable text, incorrect anatomy, background contradictions, duplicated logos and a prop appearing before its cause. Review word timing against audio and make sure effects do not obscure speech.

Render a draft, inspect it, then render the final:

```bash
python SKILL_DIR/scripts/studio.py PROJECT/project-voiced.json --module PROJECT/scenes.py --out PROJECT/draft --width 360 --fps 12
python SKILL_DIR/scripts/studio.py PROJECT/project-voiced.json --module PROJECT/scenes.py --out PROJECT/final --width 720 --fps 24
```

Verify with FFprobe that video and audio streams exist, dimensions are correct and duration matches narration. Do not count a contact sheet or technical stream check as evidence of narrative quality. Include `render-report.json` in the project; distinguish measured vs estimated captions and manual QA performed.

## Deliver and extend

Return the actual MP4, one cover frame, narration text, a short title and project source when requested. Do not publish, schedule or connect accounts unless explicitly requested. Do not add promotional marks beyond the requested handle.

To add a visual style, document a new palette, silhouette language, line weight, setting motifs and movement rules in the project's style brief; extend `PALETTES` in a project copy of studio.py and check three representative frames. Never claim the installed ZIP was permanently updated by editing a temporary project. To distribute an updated skill, rebuild and provide a new ZIP.
