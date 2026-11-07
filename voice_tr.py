"""Local Turkish narration with official GitHub first-use setup."""
import argparse,array,importlib.util,json,math,os,pathlib,platform,subprocess,sys,wave
ROOT=pathlib.Path(__file__).resolve().parent.parent

def main():
 ap=argparse.ArgumentParser();ap.add_argument('project');ap.add_argument('--offline',action='store_true');ap.add_argument('--runtime-ready',action='store_true',help=argparse.SUPPRESS);a=ap.parse_args()
 path=pathlib.Path(a.project).resolve();p=json.loads(path.read_text(encoding='utf-8'));work=path.parent/'speech-work';work.mkdir(exist_ok=True)
 if not a.runtime_ready:
  if sys.platform!='linux' or platform.machine().lower() not in ('x86_64','amd64') or sys.version_info[:2] not in [(3,10),(3,11),(3,12),(3,13)]:
   raise RuntimeError('This runtime supports Linux x86_64 and CPython 3.10–3.13; do not install incompatible wheels.')
  site=work/'runtime';marker=site/'.kare-runtime-2.0.1'
  if not marker.exists():
   if a.offline:raise RuntimeError('Offline Turkish runtime not installed; run once with network enabled for PyPI setup.')
   subprocess.run([sys.executable,'-m','pip','install','--target',str(site),'--upgrade','sherpa-onnx==2.0.1','sherpa-onnx-core==2.0.1'],check=True)
   marker.write_text('2.0.1')
  env=dict(os.environ);env['PYTHONPATH']=str(site)+os.pathsep+env.get('PYTHONPATH','')
  subprocess.run([sys.executable,__file__,str(path),'--runtime-ready']+(['--offline'] if a.offline else []),env=env,check=True);return
 import sherpa_onnx as s
 from supertonic_setup import prepare_model
 model=prepare_model(offline=a.offline)
 required=['duration_predictor.int8.onnx','text_encoder.int8.onnx','vector_estimator.int8.onnx','vocoder.int8.onnx','tts.json','unicode_indexer.bin','voice.bin']
 if any(not (model/f).is_file() for f in required):raise RuntimeError('Turkish cache is incomplete. Run supertonic_setup.py to repair the official GitHub download.')
 cfg=s.OfflineTtsSupertonicModelConfig(**{key:str(model/file) for key,file in zip(['duration_predictor','text_encoder','vector_estimator','vocoder','tts_json','unicode_indexer','voice_style'],required)})
 tts=s.OfflineTts(s.OfflineTtsConfig(model=s.OfflineTtsModelConfig(supertonic=cfg,num_threads=2,provider='cpu')))
 gen=s.GenerationConfig();gen.sid=int(p.get('turkish_voice_id',0));gen.num_steps=12;gen.speed=float(p.get('speed',1.0));gen.extra['lang']='tr'
 if not 0<=gen.sid<=9 or not .6<=gen.speed<=1.5:raise ValueError('turkish_voice_id must be 0–9; speed must be 0.6–1.5')
 chunks=[];lines=[];elapsed=0.;sample_rate=None
 for scene in p['scenes']:
  text=scene['text'].strip()
  if not text:raise ValueError('Narration scene text is empty')
  if len(text)>600:raise ValueError('Split narration into connected sentence groups shorter than 600 characters')
  audio=tts.generate(text,gen);values=audio.samples
  if len(values)<audio.sample_rate*.2 or not all(math.isfinite(v) for v in values) or max(map(abs,values),default=0)<.001:raise RuntimeError('Empty, silent or invalid Turkish speech')
  if sample_rate is not None and sample_rate!=audio.sample_rate:raise RuntimeError('Inconsistent sample rate')
  sample_rate=audio.sample_rate
  samples=array.array('h',(round(max(-1.,min(1.,v))*32767) for v in values))
  if sys.byteorder!='little':samples.byteswap()
  gap=round(sample_rate*.12);data=samples.tobytes()+b'\0\0'*gap;duration=(len(values)+gap)/sample_rate
  lines.append({'text':text,'start':elapsed,'end':elapsed+len(values)/sample_rate});elapsed+=duration
  scene['duration']=duration;scene.pop('words',None);chunks.append(data)
 if not chunks:raise ValueError('No narration scenes')
 wav=work/'narration-tr.wav'
 with wave.open(str(wav),'wb') as f:
  f.setnchannels(1);f.setsampwidth(2);f.setframerate(sample_rate);f.writeframes(b''.join(chunks))
 (work/'lines-tr.json').write_text(json.dumps({'lines':lines,'duration':elapsed},ensure_ascii=False,indent=2),encoding='utf-8')
 p.update(audio=str(wav.relative_to(path.parent)),voice_engine='supertonic-3-local',voice_name=f'speaker-{gen.sid}',caption_timing='estimated until multilingual word alignment')
 out=path.parent/'project-voiced.json';out.write_text(json.dumps(p,ensure_ascii=False,indent=2),encoding='utf-8');print(out)
if __name__=='__main__':
 try:main()
 except Exception as exc:sys.exit(f'Turkish narration incomplete: {exc}')
