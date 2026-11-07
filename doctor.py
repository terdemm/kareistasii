"""Inspect dependencies without installing or downloading anything."""
import importlib.util,json,shutil,subprocess,sys
info={'python':sys.version.split()[0],'pillow':bool(importlib.util.find_spec('PIL')),'ffmpeg':shutil.which('ffmpeg'),'ffprobe':shutil.which('ffprobe'),'optional_online_tts':bool(importlib.util.find_spec('edge_tts')),'optional_recording_alignment':bool(importlib.util.find_spec('faster_whisper'))}
info['render_ready']=bool(info['pillow'] and info['ffmpeg']);print(json.dumps(info,indent=2));sys.exit(0 if info['render_ready'] else 1)
