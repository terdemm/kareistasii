"""Small deterministic CPU 3D illustration renderer. Original implementation.
Perspective camera, orbit, shaded triangle meshes and procedural characters/sets.
Painter sorting has limitations for intersecting/transparent geometry. Not PBR.
"""
import math
import numpy as np
from PIL import ImageDraw

def rgb(h):return np.array([int(h[i:i+2],16) for i in (1,3,5)],dtype=float)
def normalize(v):v=np.asarray(v,dtype=float);return v/(np.linalg.norm(v)+1e-10)
class World:
 def __init__(self,eye=(5,3,7),target=(0,1,0),focal=700):
  self.eye=np.array(eye,dtype=float);forward=normalize(np.array(target)-self.eye);right=normalize(np.cross(forward,[0,1,0]));up=np.cross(right,forward);self.camera=np.array([right,up,forward]);self.focal=focal;self.faces=[];self.light=normalize([-.5,.9,.7])
 def mesh(self,vertices,faces,color):
  verts=np.asarray(vertices,dtype=float);cam=(verts-self.eye)@self.camera.T;z=cam[:,2];screen=np.column_stack([360+self.focal*cam[:,0]/np.maximum(z,.1),620-self.focal*cam[:,1]/np.maximum(z,.1)])
  base=rgb(color)
  for f in faces:
   ids=np.array(f);v=verts[ids]
   if min(z[ids])<.1:continue
   normal=normalize(np.cross(v[1]-v[0],v[2]-v[0]));shade=.45+.55*abs(float(normal@self.light));tint=tuple(int(x) for x in np.clip(base*shade,0,255));self.faces.append((float(np.mean(z[ids])),[tuple(x) for x in screen[ids]],tint))
 def box(self,at,size,color):
  a=np.array(at);sz=np.array(size)/2;verts=[a+sz*np.array([x,y,z]) for x,y,z in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]];faces=[(0,1,2,3),(4,7,6,5),(0,4,5,1),(3,2,6,7),(0,3,7,4),(1,5,6,2)];self.mesh(verts,faces,color)
 def ellipsoid(self,at,size,color,rows=7,cols=12):
  verts=[];a=np.array(at);sz=np.array(size)
  for j in range(rows+1):
   v=math.pi*j/rows
   for i in range(cols):
    u=2*math.pi*i/cols;verts.append(a+sz*np.array([math.sin(v)*math.cos(u),math.cos(v),math.sin(v)*math.sin(u)]))
  faces=[]
  for j in range(rows):
   for i in range(cols):faces.append((j*cols+i,j*cols+(i+1)%cols,(j+1)*cols+(i+1)%cols,(j+1)*cols+i))
  self.mesh(verts,faces,color)
 def limb(self,a,b,r,color,sides=9):
  a,b=np.array(a),np.array(b);axis=normalize(b-a);side=normalize(np.cross(axis,[0,1,0] if abs(axis[1])<.9 else [1,0,0]));up=np.cross(axis,side);verts=[]
  for endpoint in [a,b]:
   for i in range(sides):angle=i*2*math.pi/sides;verts.append(endpoint+r*(side*math.cos(angle)+up*math.sin(angle)))
  self.mesh(verts,[(i,(i+1)%sides,(i+1)%sides+sides,i+sides) for i in range(sides)]+[tuple(range(sides)),tuple(range(sides,2*sides))],color)
 def render(self,c):
  for depth,points,color in sorted(self.faces,key=lambda f:-f[0]):c.d.polygon(points,fill=color)

def person(w,t,skin,shirt,pose=0,xray=False,flat=False):
 depth=.08 if flat else .23
 w.ellipsoid((0,2.4,0),(.32,.4,depth),skin)
 w.box((0,2.69,-.025),(.56,.17,depth*1.7),'#26324D')
 w.ellipsoid((0,1.65,0),(.4,.57,depth),shirt)
 for x in [-.16,.16]:
  w.limb((x,1.15,0),(x*1.4,.25,.06),.10,'#25384F');w.box((x*1.4,.15,.13),(.23,.16,.4),'#26324D')
  w.ellipsoid((x*.68,2.46,depth*.95),(.038,.045,.035),'#1D293A',4,6)
 w.limb((-.37,1.94,0),(-.52,1.28,.04),.095,skin)
 shoulder=(.37,1.94,0);elbow=(.68,1.65+.35*pose,.06);hand=(.63-.21*pose,1.22+1.04*pose,.18+.08*pose)
 w.limb(shoulder,elbow,.095,skin);w.limb(elbow,hand,.085,skin);w.ellipsoid(hand,(.12,.12,.10),skin,5,8)
 if xray:
  # Stylized open panel; not simulated tissue or medical anatomy.
  w.box((0,1.65,depth+.015),(.49,.7,.03),'#91DCD4');w.limb((0,1.34,depth+.05),(0,1.97,depth+.05),.025,'#FFFFFF')
  w.ellipsoid((-.10,1.78,depth+.09),(.09,.11,.055),'#E76B62',5,8)
 return hand

def draw(c,t,d,s,p):
 mode=s.get('space',{});look=mode.get('look','sunny');u=t/d;orbit=mode.get('orbit',.5);angle=mode.get('angle',.55)+orbit*u;r=mode.get('radius',5.8);eye=(r*math.sin(angle),mode.get('height',3.2),r*math.cos(angle));w=World(eye,mode.get('target',[0,1.4,0]),mode.get('focal',840))
 dark=look=='mystery'
 c.d.rectangle((0,0,720,1280),fill='#101C2E' if dark else c.p['bg'])
 floor='#26384B' if dark else '#D8C7B2';wall='#1C2A3F' if dark else '#EEE4D6';shirt='#B8594B' if dark else c.p['cool']
 w.box((0,-.08,0),(7,.16,6),floor)
 if mode.get('set','room')=='room':
  w.box((0,1.5,-2.3),(7,3,.12),wall);w.box((-2.7,1.5,0),(.12,3,4.5),wall)
  w.box((-1.4,1.5,-2.18),(1.2,1.3,.05),'#3C6A85' if dark else '#C4DEE2')
  w.box((1.7,.8,-1),(1.2,.12,1),'#A57752')
  for x in [1.2,2.2]:w.box((x,.4,-1),(.08,.8,.65),'#896348')
 pose=(math.sin(min(1,t/.9)*math.pi/2)) if s.get('action')=='lift' else .1+.05*math.sin(t*2)
 hand=person(w,t,'#DCA77C',shirt,pose,mode.get('xray',False),look=='toon')
 if s.get('prop')=='phone':w.box((hand[0],hand[1]+.06,hand[2]+.08),(.18,.33,.04),'#24344B')
 if s.get('prop')=='apple':w.ellipsoid(hand,(.15,.15,.14),'#D75B4A',6,10)
 if mode.get('object')=='heart':
  # Dedicated macro composition can replace room and person in a custom scene.
  pulse=1+.05*math.sin(t*7)
  for x in [-.13,.13]:w.ellipsoid((x,1.7,1),(.22*pulse,.28*pulse,.18),'#DA605D')
 w.render(c)
 if s.get('label'):c.text(s['label'],360,160,42)
