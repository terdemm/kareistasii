"""Original Kare Ustası 2D renderer. Python 3.10+, Pillow, FFmpeg; no browser/GPU.
Scene modules export draw(canvas, local_seconds, duration, scene, project).
Coordinates use a 720x1280 design space at every output resolution.
"""
import argparse, array, importlib.util, json, math, os, pathlib, shutil, subprocess, sys, wave
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
BASE_W, BASE_H = 720, 1280
PALETTES = {
 'merak': {'bg':'#F5EEE5','ink':'#20304A','accent':'#EE6B48','cool':'#258F99','paper':'#FFFFFF'},
 'gece': {'bg':'#152338','ink':'#EDF1ED','accent':'#F6B34B','cool':'#5DC3BA','paper':'#273C57'},
 'atlas': {'bg':'#E8DFCB','ink':'#343A40','accent':'#AA4E39','cool':'#497F79','paper':'#FAF5E9'}}
def run(args, **kw):
 return subprocess.run([str(a) for a in args], check=True, **kw)
def ease(t):
 t=max(0,min(1,t)); return t*t*(3-2*t)
def mix(a,b,t): return a+(b-a)*t
def font_path(bold=True):
 paths=[os.environ.get('KU_FONT',''),'/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf','/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf','C:/Windows/Fonts/arialbd.ttf','/System/Library/Fonts/Supplemental/Arial Bold.ttf']
 return next((p for p in paths if p and pathlib.Path(p).is_file()),None)
class Canvas:
 def __init__(self,palette):
  self.im=Image.new('RGB',(BASE_W,BASE_H),palette['bg']); self.d=ImageDraw.Draw(self.im); self.p=palette
 def line(self,pts,fill=None,width=8): self.d.line(pts,fill=fill or self.p['ink'],width=width,joint='curve')
 def oval(self,box,fill,outline=None,width=4): self.d.ellipse(box,fill=fill,outline=outline,width=width)
 def box(self,box,fill,r=20,outline=None,width=4): self.d.rounded_rectangle(box,radius=r,fill=fill,outline=outline,width=width)
 def text(self,text,x,y,size=44,fill=None,anchor='mm',max_width=630):
  path=font_path(); size=int(size)
  while True:
   f=ImageFont.truetype(path,size) if path else ImageFont.load_default(size=size)
   if self.d.textbbox((0,0),text,font=f)[2]<=max_width or size<=16: break
   size-=2
  self.d.text((x,y),text,font=f,fill=fill or self.p['ink'],anchor=anchor,stroke_width=0)
 def arrow(self,a,b,fill=None):
  color=fill or self.p['accent']; self.line([a,b],color,9); ang=math.atan2(b[1]-a[1],b[0]-a[0]); self.d.polygon([b,(b[0]-26*math.cos(ang-.5),b[1]-26*math.sin(ang-.5)),(b[0]-26*math.cos(ang+.5),b[1]-26*math.sin(ang+.5))],fill=color)
 def actor(self,x,y,scale=1,pose=0,expression='curious',holding=None,xray=False):
  # Body-relative joints; props attach to hand so they cannot drift away.
  def pt(a,b): return (x+a*scale,y+b*scale)
  ink=self.p['ink']; shirt=self.p['cool']; skin='#DCA77C'
  hip=pt(0,160); feet=[pt(-43,310),pt(49,310)]
  self.line([feet[0],hip,feet[1]],ink,max(2,int(24*scale)))
  self.box((*pt(-68,-13),*pt(68,178)),shirt,int(32*scale))
  hand=pt(126-49*pose,88-181*pose); elbow=pt(112,60-64*pose)
  self.line([pt(56,15),elbow,hand],skin,max(2,int(20*scale)))
  self.line([pt(-56,15),pt(-102,80),pt(-96,150)],skin,max(2,int(20*scale)))
  self.oval((*pt(-79,-175),*pt(79,-10)),skin)
  self.box((*pt(-72,-174),*pt(54,-128)),ink,int(15*scale))
  for ex in [-27,29]: self.oval((*pt(ex-6,-111),*pt(ex+6,-96)),ink)
  self.line([pt(-43,-128),pt(-16,-132-5*math.sin(pose))],ink,max(2,int(4*scale)))
  if expression=='surprise': self.oval((*pt(-9,-72),*pt(9,-48)),ink)
  else: self.line([pt(-20,-65),pt(0,-58),pt(22,-66)],ink,max(2,int(4*scale)))
  if xray:
   self.box((*pt(-47,8),*pt(47,155)),'#BCE3DE',int(20*scale))
   self.line([pt(0,20),pt(0,140)],'#FFFFFF',max(2,int(6*scale)))
   for yy in [35,57,79]: self.line([pt(-31,yy+9),pt(0,yy),pt(31,yy+9)],'#FFFFFF',max(2,int(5*scale)))
   self.oval((*pt(3,91),*pt(34,128)),self.p['accent'])
  if holding: self.prop(holding,*hand,scale=.55*scale)
  return hand
 def stick(self,x,y,t,action='idle',prop=None,expression='neutral',scale=1):
  import looks;return looks.stick(self,x,y,t,action,prop,expression,scale)
 def prop(self,kind,x,y,scale=1):
  def b(a,c,d,e): return (x+a*scale,y+c*scale,x+d*scale,y+e*scale)
  if kind=='phone':
   self.box(b(-40,-65,40,65),self.p['ink'],int(12*scale)); self.box(b(-30,-50,30,42),self.p['paper'],int(6*scale)); self.oval(b(-5,49,5,59),self.p['accent'])
  elif kind=='parcel':
   self.box(b(-65,-48,65,48),'#C79760',int(7*scale),self.p['ink']); self.box(b(-8,-48,8,48),'#E7CB8B',0)
  elif kind=='clock':
   self.oval(b(-65,-65,65,65),self.p['paper'],self.p['ink']); self.line([(x,y),(x,y-38*scale)],width=6); self.line([(x,y),(x+30*scale,y+14*scale)],width=6)
  elif kind=='apple':
   self.oval(b(-38,-28,3,35),self.p['accent']); self.oval(b(-3,-28,38,35),self.p['accent']); self.line([(x,y-24*scale),(x+7*scale,y-45*scale)],width=5)
  elif kind=='moon': self.oval(b(-42,-42,42,42),'#F6CF75'); self.oval(b(-15,-54,59,19),self.p['bg'])
  else:
   self.oval(b(-42,-42,42,42),self.p['accent']); self.text(str(kind)[:12],x,y,24*scale,self.p['paper'],max_width=160)
def load(path):
 p=json.loads(pathlib.Path(path).read_text(encoding='utf-8')); scenes=p.get('scenes',[])
 if not scenes: raise ValueError('At least one scene is required')
 for i,s in enumerate(scenes):
  if not isinstance(s.get('text'),str) or not s['text'].strip(): raise ValueError(f'Scene {i}: narration text missing')
  if not isinstance(s.get('duration'),(float,int)) or not 0.25<=s['duration']<=30: raise ValueError(f'Scene {i}: duration must be 0.25..30 seconds')
  if s.get('kind','actor') not in ['actor','detail','diagram','map','custom','geomap','stick','science','paper','timeline','chart','kinetic','scene3d']: raise ValueError(f'Scene {i}: unknown kind')
  if s.get('kind')=='map' and (len(s.get('route',[[0,0],[1,1]]))<2): raise ValueError(f'Scene {i}: route requires at least two points')
  if s.get('kind')=='chart' and any(v.get('value',0)<0 for v in s.get('values',[])):raise ValueError(f'Scene {i}: built-in bars support nonnegative values; draw a custom chart for negative data')
  if not 0<=float(s.get('zoom',.035))<=1:raise ValueError(f'Scene {i}: zoom must be 0..1')
  if s.get('kind')=='geomap':
   bounds=s.get('map',{}).get('bounds',[-180,-65,180,85])
   if len(bounds)!=4 or bounds[0]>=bounds[2] or bounds[1]>=bounds[3]:raise ValueError(f'Scene {i}: invalid geographic bounds')
   for point in s.get('map',{}).get('route',[]):
    if len(point)!=2 or not -90<=point[1]<=90:raise ValueError(f'Scene {i}: route points require longitude,latitude')
  for cue in s.get('sfx',[]):
   if not 0<=float(cue.get('at',0))<s['duration']:raise ValueError(f'Scene {i}: sound cue outside scene')
  for word in s.get('words',[]):
   if not 0<=word['start']<word['end']<=s['duration']+.05: raise ValueError(f'Scene {i}: invalid word timing')
 if p.get('style','merak') not in PALETTES: raise ValueError('Unknown style')
 return p
def timeline(p):
 out=[]; t=0
 for s in p['scenes']: out.append((t,t+s['duration'],s)); t+=s['duration']
 return out,t
def default_scene(c,t,d,s,p):
 u=ease(t/.6); kind=s.get('kind','actor'); phase=t/max(d,.001)
 if kind=='geomap':
  import geo; geo.draw(c,t,d,s,p)
 elif kind=='scene3d':
  import space3d;space3d.draw(c,t,d,s,p)
 elif kind in ['stick','science','paper','timeline','chart','kinetic']:
  import looks;looks.draw(c,t,d,s,p)
 elif kind=='actor':
  c.box((42,235,678,907),c.p['paper'],40)
  c.line([(45,810),(675,810)],c.p['cool'],5)
  if s.get('setting')=='night':
   c.box((475,285,625,465),c.p['bg']); c.prop('moon',547,358,.6)
  else:
   c.box((475,285,625,465),c.p['bg']); c.line([(550,285),(550,465)],c.p['cool'],5)
  pose=ease((t-.3)/.8) if s.get('action')=='lift' else .08*math.sin(t*2.5)
  c.actor(310,520+3*math.sin(t*3),.9,pose,s.get('expression','curious'),s.get('prop'),s.get('xray',False))
  if s.get('action')=='wait':
   c.prop('clock',545,635,.65); a=t*1.5; c.line([(545,635),(545+24*math.sin(a),635-24*math.cos(a))],c.p['accent'],4)
 elif kind=='detail':
  c.oval((95,285,625,815),c.p['paper']); c.prop(s.get('prop','phone'),360,550,2.3+.06*math.sin(t*3))
  if s.get('label'): c.text(s['label'],360,880,48)
 elif kind=='diagram':
  c.actor(215,540,.9,xray=s.get('xray',False))
  c.oval((410,380,650,620),c.p['paper']); c.prop(s.get('prop','apple'),530,500,1.2)
  c.arrow((300,570),(430,510)); c.oval((mix(305,423,ease((phase*1.7)%1))-9,540-9,mix(305,423,ease((phase*1.7)%1))+9,540+9),c.p['accent'])
  if s.get('label'): c.text(s['label'],470,740,38,max_width=400)
 elif kind=='map':
  c.d.polygon([(80,410),(230,310),(410,360),(610,290),(650,670),(460,790),(260,700),(100,810)],fill=c.p['paper'])
  route=s.get('route',[[180,620],[350,430],[550,570]])
  for a,b in zip(route,route[1:]): c.line([tuple(a),tuple(b)],c.p['cool'],7)
  f=min(.999,phase)*max(1,len(route)-1); k=min(len(route)-2,int(f)); a,b=route[k:k+2]; x=mix(a[0],b[0],f-k); y=mix(a[1],b[1],f-k)
  c.oval((x-17,y-17,x+17,y+17),c.p['accent'])
 else: raise ValueError('Custom scene requires --module with draw()')
 # Small reveal elements are separate from the camera and caption overlay.
 if s.get('badge'): c.box((80,155+30*(1-u),640,222+30*(1-u)),c.p['accent']); c.text(s['badge'],360,190+30*(1-u),32,c.p['paper'])
def caption(c,s,t):
 if s.get('captions',True) is False:return
 words=s.get('words'); text=s.get('caption',s['text'])
 if words:
  active=next((i for i,w in enumerate(words) if w['start']<=t<w['end']),None)
  if active is None:return
  start=(active//3)*3; group=words[start:start+3]; content=' '.join(w['text'] for w in group)
 else:
  # Explicitly estimated: never claim word sync for equal subdivisions.
  tokens=text.split(); chunk=min(max(0,len(tokens)-1),int(t/max(.01,s['duration'])*len(tokens)))//3
  content=' '.join(tokens[chunk*3:chunk*3+3])
 c.box((35,1005,685,1125),c.p['ink'],24); c.text(content,360,1065,51,c.p['bg'])
def frame(p,s,t,w,h,module=None):
 c=Canvas(PALETTES[p.get('style','merak')]); d=s['duration']
 if module: module.draw(c,t,d,s,p)
 else: default_scene(c,t,d,s,p)
 # Continuous deterministic camera move with zero random jitter.
 z=1+float(s.get('zoom',.035))*ease(t/d); cw=int(BASE_W/z); ch=int(BASE_H/z)
 pan=s.get('pan',[0,0]);px=pan[0]*ease(t/d);py=pan[1]*ease(t/d);cx=max(cw/2,min(BASE_W-cw/2,BASE_W/2+px));cy=max(ch/2,min(BASE_H-ch/2,BASE_H/2+py))
 c.im=c.im.crop((int(cx-cw/2),int(cy-ch/2),int(cx+cw/2),int(cy+ch/2))).resize((BASE_W,BASE_H),Image.Resampling.BICUBIC); c.d=ImageDraw.Draw(c.im)
 if s.get('transition')=='fade':
  opacity=min(1,t/.15,(d-t)/.15);c.im=Image.blend(Image.new('RGB',(BASE_W,BASE_H),c.p['bg']),c.im,max(0,opacity));c.d=ImageDraw.Draw(c.im)
 caption(c,s,t)
 if p.get('handle'): c.text(p['handle'],360,1180,22,c.p['ink'])
 if h/w<1.6:
  view=Image.new('RGB',(1280,720),c.p['bg']);panel=c.im.crop((0,100,720,990)).resize((493,610),Image.Resampling.LANCZOS);view.paste(panel,(70,45));vd=ImageDraw.Draw(view)
  words=s.get('words');display=' '.join(x['text'] for x in words if x['start']<=t) if words else s.get('caption',s['text'])
  tokens=display.split();lines=[];current=[]
  for word in tokens:
   current.append(word)
   if len(' '.join(current))>24:lines.append(' '.join(current));current=[]
  if current:lines.append(' '.join(current))
  f=ImageFont.truetype(font_path(),32) if font_path() else ImageFont.load_default(size=32)
  if s.get('captions',True):
   for i,line in enumerate(lines[-6:]):vd.text((650,230+i*48),line,font=f,fill=c.p['ink'])
  return view.resize((w,h),Image.Resampling.LANCZOS)
 return c.im.resize((w,h),Image.Resampling.LANCZOS)
def sfx_audio(p,path,voice=None):
 sr=24000; _,dur=timeline(p); n=math.ceil(dur*sr); sound=array.array('h',[0])*n
 if voice:
  tmp=path.with_suffix('.voice.wav'); run(['ffmpeg','-v','error','-y','-i',voice,'-ar',sr,'-ac','1','-c:a','pcm_s16le',tmp]);
  with wave.open(str(tmp),'rb') as f: v=array.array('h');v.frombytes(f.readframes(f.getnframes()))
  if abs(len(v)/sr-dur)>.3: raise ValueError('Voice duration and scene timeline differ by more than 0.3 seconds; align durations first')
  sound[:min(n,len(v))]=v[:min(n,len(v))]; tmp.unlink()
 start=0
 for idx,s in enumerate(p['scenes']):
  for cue in s.get('sfx',[{'at':0,'type':'pop'}]):
   sec=float(cue.get('at',0)); typ=cue.get('type','pop'); length=float(cue.get('duration',.22 if typ=='whoosh' else .12));gain=max(0,min(2,float(cue.get('gain',1))))
   for j in range(int(sr*length)):
    at=int((start+sec)*sr)+j
    if not 0<=at<n:continue
    u=j/sr; env=math.sin(math.pi*u/length)**2; freq=420*math.exp(-u*9) if typ=='pop' else 160+1200*u
    freq={'impact':100,'notification':720,'tick':600,'bubble':250,'sparkle':1400,'whoosh':freq,'pop':freq}.get(typ,freq)
    value=int(1900*gain*env*math.sin(2*math.pi*freq*u))
    sound[at]=max(-32767,min(32767,sound[at]+value))
  start+=s['duration']
 if p.get('music')=='procedural':
  for j in range(n):
   tt=j/sr;chord=[196,246.94,293.66][int(tt/4)%3];fade=min(1,tt,dur-tt);bed=int(250*fade*(math.sin(2*math.pi*chord*tt)+.4*math.sin(2*math.pi*chord*1.5*tt)));sound[j]=max(-32767,min(32767,sound[j]+bed))
 with wave.open(str(path),'wb') as f:f.setnchannels(1);f.setsampwidth(2);f.setframerate(sr);f.writeframes(sound.tobytes())
def subtitles(p,path):
 def stamp(t):
  ms=round(t*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
 out=[];offset=0;idx=0
 for scene in p['scenes']:
  words=scene.get('words')
  chunks=[(words[i]['start'],words[min(i+2,len(words)-1)]['end'],' '.join(w['text'] for w in words[i:i+3])) for i in range(0,len(words),3)] if words else [(0,scene['duration'],scene['text'])]
  if scene.get('captions',True):
   for start,end,text in chunks:idx+=1;out.append(f'{idx}\n{stamp(offset+start)} --> {stamp(offset+end)}\n{text}\n')
  offset+=scene['duration']
 path.write_text('\n'.join(out),encoding='utf-8')

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('project'); ap.add_argument('--out',default='render'); ap.add_argument('--width',type=int,default=720); ap.add_argument('--fps',type=int,default=24); ap.add_argument('--aspect',choices=['9:16','16:9','1:1'],default='9:16'); ap.add_argument('--range',nargs=2,type=float,metavar=('START','END')); ap.add_argument('--voice'); ap.add_argument('--silent-demo',action='store_true'); ap.add_argument('--module'); ap.add_argument('--check',action='store_true'); ap.add_argument('--sheet-only',action='store_true'); a=ap.parse_args()
 try:
  p=load(a.project); cuts,dur=timeline(p)
  if a.check: print(json.dumps({'scenes':len(cuts),'seconds':dur,'estimated_caption_scenes':sum(not bool(s.get('words')) and s.get('captions',True) for s in p['scenes'])}));return
  if a.width%2 or not 180<=a.width<=2160 or not 1<=a.fps<=60: raise ValueError('Even width 180..2160 and fps 1..60 required')
  if not shutil.which('ffmpeg'):raise ValueError('FFmpeg is missing')
  module=None
  if a.module:
   spec=importlib.util.spec_from_file_location('ku_scene',a.module);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
  out=pathlib.Path(a.out);out.mkdir(parents=True,exist_ok=True); ratio={'9:16':16/9,'16:9':9/16,'1:1':1}[a.aspect];h=2*round(a.width*ratio/2)
  thumbs=[]
  for i,(st,en,s) in enumerate(cuts):
   for phase in [.15,.5,.85]:
    im=frame(p,s,s['duration']*phase,180,320,module); tile=Image.new('RGB',(180,350),'white');tile.paste(im,(0,0)); ImageDraw.Draw(tile).text((6,326),f'{i+1} | {st+s["duration"]*phase:.2f}s',fill='black');thumbs.append(tile)
  sheet=Image.new('RGB',(180*3,350*len(cuts)),'white')
  for i,im in enumerate(thumbs):sheet.paste(im,((i%3)*180,(i//3)*350))
  sheet.save(out/'contact-sheet.jpg')
  if a.sheet_only:print(out/'contact-sheet.jpg');return
  voice=a.voice or p.get('audio')
  if voice and not pathlib.Path(voice).is_absolute():voice=str(pathlib.Path(a.project).resolve().parent/voice)
  if not voice and not a.silent_demo:raise ValueError('Narration missing. Run voice.py or pass --voice. Use --silent-demo only for explicitly unvoiced previews.')
  sfx_audio(p,out/'mix.wav',voice)
  begin,end=(a.range if a.range else [0,dur])
  if not 0<=begin<end<=dur+.001:raise ValueError('Render range must be inside timeline')
  render_dur=end-begin
  target=out/'video.mp4'; cmd=['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{a.width}x{h}','-r',str(a.fps),'-i','pipe:0','-ss',str(begin),'-i',str(out/'mix.wav'),'-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-b:a','128k','-t',str(render_dur),'-movflags','+faststart',str(target)]
  proc=subprocess.Popen(cmd,stdin=subprocess.PIPE); count=math.ceil(render_dur*a.fps); idx=0
  try:
   for i in range(count):
    t=min(begin+i/a.fps,end-1e-6)
    while idx+1<len(cuts) and t>=cuts[idx][1]:idx+=1
    st,en,s=cuts[idx];proc.stdin.write(frame(p,s,t-st,a.width,h,module).tobytes())
  finally:proc.stdin.close()
  if proc.wait()!=0:raise RuntimeError('FFmpeg render failed')
  (out/'render-report.json').write_text(json.dumps({'frames':count,'fps':a.fps,'duration':render_dur,'source_start':begin,'width':a.width,'height':h,'narration':bool(voice),'caption_timing':('disabled' if not any(s.get('captions',True) for s in p['scenes']) else 'measured' if all(s.get('words') for s in p['scenes'] if s.get('captions',True)) else 'some estimated'),'note':'Manual image/audio review still required'},indent=2),encoding='utf-8')
  st,en,first=next(cut for cut in cuts if cut[0]<=begin<cut[1]);frame(p,first,min(begin-st+first['duration']*.2,first['duration']-.01),a.width,h,module).save(out/'cover.jpg')
  subtitles(p,out/('captions-full-timeline.srt' if a.range else 'captions.srt'))
  print(target)
 except (ValueError,RuntimeError,FileNotFoundError,subprocess.CalledProcessError) as e:ap.exit(1,f'ERROR: {e}\n')
if __name__=='__main__':main()
