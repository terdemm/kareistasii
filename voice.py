"""Optional online TTS and measured word boundaries; no API key.
Requires edge-tts. Sends narration to Microsoft's online speech service.
Can also align an existing recording with --align using faster-whisper.
No synthetic silence is ever substituted for a failed voice request.
"""
import argparse, asyncio, json, pathlib, subprocess, sys, wave, array

def ff(*args): subprocess.run(['ffmpeg','-v','error','-y',*map(str,args)],check=True)
async def synthesize(p,root,voice,rate):
 import edge_tts
 pieces=[]
 for i,s in enumerate(p['scenes']):
  media=root/f'voice-{i:03d}.mp3'; words=[]
  comm=edge_tts.Communicate(s['text'],voice,rate=rate,boundary='WordBoundary',connect_timeout=10,receive_timeout=20)
  with media.open('wb') as f:
   async for item in comm.stream():
    if item['type']=='audio':f.write(item['data'])
    elif item['type']=='WordBoundary':words.append({'text':item['text'],'start':item['offset']/10_000_000,'end':(item['offset']+item['duration'])/10_000_000})
  wav=root/f'voice-{i:03d}.wav';ff('-i',media,'-ar',24000,'-ac',1,'-c:a','pcm_s16le',wav)
  with wave.open(str(wav),'rb') as f:audio=f.readframes(f.getnframes())
  duration=len(audio)/48000
  if duration<=.1:raise ValueError('Empty TTS response')
  tail=.12; s['duration']=round(duration+tail,5);s['words']=words
  pieces.append(audio+b'\x00\x00'*int(24000*tail))
 with wave.open(str(root/'narration.wav'),'wb') as f:f.setnchannels(1);f.setsampwidth(2);f.setframerate(24000);f.writeframes(b''.join(pieces))
 p['audio']='narration.wav';return p

def local_voice(p,root,model,voices,voice):
 from kokoro_onnx import Kokoro
 import numpy as np
 engine=Kokoro(model,voices); pieces=[]
 for scene in p['scenes']:
  samples,sr=engine.create(scene['text'],voice=voice,lang='en-us')
  samples=np.asarray(samples)
  if sr!=24000:raise ValueError('Expected Kokoro output at 24000Hz')
  pieces.append((np.clip(samples,-1,1)*30000).astype('<i2').tobytes()+b'\x00\x00'*2880)
  scene['duration']=len(samples)/24000+.12
  scene.pop('words',None)
 with wave.open(str(root/'narration.wav'),'wb') as f:f.setnchannels(1);f.setsampwidth(2);f.setframerate(24000);f.writeframes(b''.join(pieces))
 p['audio']='narration.wav'
 p['timing_note']='Scene lengths measured from audio; word captions estimated until Whisper alignment.'
 return p

def align(p,root,audio,language):
 from faster_whisper import WhisperModel
 import difflib,re
 normalized=root/'aligned-narration.wav'; ff('-i',audio,'-ar',24000,'-ac',1,'-c:a','pcm_s16le',normalized)
 model=WhisperModel('tiny',device='cpu',compute_type='int8');segments,_=model.transcribe(str(normalized),language=language,word_timestamps=True)
 words=[{'text':w.word.strip(),'start':w.start,'end':w.end} for seg in segments for w in (seg.words or [])]
 clean=lambda text:re.findall(r'\w+',text.casefold())
 actual=clean(' '.join(w['text'] for w in words));expected=clean(' '.join(s['text'] for s in p['scenes']))
 if difflib.SequenceMatcher(None,expected,actual).ratio()<.9:raise ValueError('Recording/transcript mismatch. Correct transcript; do not guess alignment.')
 # Partition at token counts, after verifying a strict one-to-one normalized token match.
 if actual!=expected:raise ValueError('Alignment needs manual correction: recognized word sequence differs from script.')
 expanded=[]
 for w in words:
  toks=clean(w['text'])
  for j,tok in enumerate(toks):expanded.append({**w,'text':tok,'start':w['start']+(w['end']-w['start'])*j/len(toks),'end':w['start']+(w['end']-w['start'])*(j+1)/len(toks)})
 with wave.open(str(normalized),'rb') as f:duration=f.getnframes()/f.getframerate()
 pos=0;start=0
 for i,s in enumerate(p['scenes']):
  n=len(clean(s['text']));group=expanded[pos:pos+n];pos+=n
  end=duration if i==len(p['scenes'])-1 else (group[-1]['end']+expanded[pos]['start'])/2
  s['duration']=round(end-start,5);s['words']=[{**w,'start':round(w['start']-start,5),'end':round(w['end']-start,5)} for w in group];start=end
 p['audio']='aligned-narration.wav';return p

def main():
 ap=argparse.ArgumentParser();ap.add_argument('project');ap.add_argument('--voice',default='tr-TR-AhmetNeural');ap.add_argument('--rate',default='+0%');ap.add_argument('--align');ap.add_argument('--language',default='tr');ap.add_argument('--kokoro-model');ap.add_argument('--kokoro-voices');ap.add_argument('--local-voice',default='af_heart');a=ap.parse_args()
 source=pathlib.Path(a.project).resolve();root=source.parent;p=json.loads(source.read_text(encoding='utf-8'))
 try:
  if a.kokoro_model:
   if not a.kokoro_voices:raise ValueError('--kokoro-voices is required')
   if a.language!='en':raise ValueError('Bundled local Kokoro path is English only; use --language en')
   p=local_voice(p,root,a.kokoro_model,a.kokoro_voices,a.local_voice)
  else:p=align(p,root,a.align,a.language) if a.align else asyncio.run(synthesize(p,root,a.voice,a.rate))
  target=root/'project-voiced.json';target.write_text(json.dumps(p,ensure_ascii=False,indent=2),encoding='utf-8');print(target)
 except Exception as exc:ap.exit(1,f'Voice failed: {exc}. Use your own recording or retry when network/TTS is available. No voiced video was produced.\n')
if __name__=='__main__':main()
