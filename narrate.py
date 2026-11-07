"""Add local narration without modifying the original rendering pipeline."""
import argparse,importlib.util,json,os,pathlib,subprocess,sys,wave
ROOT=pathlib.Path(__file__).resolve().parent.parent

def run(cmd):subprocess.run(list(map(str,cmd)),check=True)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('project');ap.add_argument('--language');ap.add_argument('--offline',action='store_true');a=ap.parse_args()
 path=pathlib.Path(a.project).resolve();p=json.loads(path.read_text(encoding='utf-8'));root=path.parent;lang=(a.language or p.get('language','tr')).lower().replace('_','-').split('-')[0]
 try:
  if lang=='tr':
   run([sys.executable,ROOT/'scripts/voice_tr.py',path]+(['--offline'] if a.offline else []));return
  if lang!='en':raise ValueError('The preserved Kokoro helper is English-only. Supply a recording or an installed language-specific provider for '+lang)
  packages=[package for module,package in [('numpy','numpy'),('scipy','scipy'),('kokoro_onnx','kokoro-onnx')] if importlib.util.find_spec(module) is None]
  if packages:
   if a.offline:raise ValueError('Offline Kokoro dependencies are missing')
   run([sys.executable,'-m','pip','install',*packages])
  work=root/'speech-work';work.mkdir(exist_ok=True)
  voice=p.get('voice','am_michael')
  script={'voice':voice,'speed':p.get('speed',1.0),'lead':0,'outro':0,'gap':.12,'lines':[{'text':s['text']} for s in p['scenes']]}
  (work/'script.json').write_text(json.dumps(script,ensure_ascii=False,indent=2),encoding='utf-8')
  if a.offline:
   base=pathlib.Path(os.environ.get('FACELESS_HOME',pathlib.Path.home()/'.faceless-shorts'))/'kokoro'
   if not all((base/name).is_file() for name in ['kokoro-v1.0.onnx','voices-v1.0.bin']):raise ValueError('Offline Kokoro model files are missing')
  run([sys.executable,ROOT/'speech/kokoro/voice.py',work])
  lines=json.loads((work/'data/lines.json').read_text())
  for i,s in enumerate(p['scenes']):
   start=0 if i==0 else lines['lines'][i]['start'];end=lines['duration'] if i==len(p['scenes'])-1 else lines['lines'][i+1]['start']
   s['duration']=end-start;s.pop('words',None)
  p['audio']=str((work/'data/narration.wav').relative_to(root));p['voice_engine']='kokoro-local';p['timing_note']='Measured cut durations; word timing estimated until alignment.'
  out=root/'project-voiced.json';out.write_text(json.dumps(p,ensure_ascii=False,indent=2),encoding='utf-8');print(out)
 except Exception as exc:ap.exit(1,f'Narration incomplete: {exc}. Project and animation remain intact. No silent or robotic replacement was made.\n')
if __name__=='__main__':main()
