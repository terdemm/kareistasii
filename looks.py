"""Original 2D scene vocabulary: stick acting, science, paper stories and diagrams."""
import math

def smooth(x):x=max(0,min(1,x));return x*x*(3-2*x)
def stick(c,x,y,t,action='idle',prop=None,expression='neutral',scale=1):
 def pt(a,b):return (x+a*scale,y+b*scale)
 bodybob=3*math.sin(t*3);walk=math.sin(t*7) if action=='walk' else 0;pose=smooth((t-.15)/.8) if action in ['lift','eat'] else .05*math.sin(t*3)
 y+=bodybob
 head=pt(0,-145);c.oval((head[0]-57*scale,head[1]-57*scale,head[0]+57*scale,head[1]+57*scale),c.p['paper'],c.p['ink'],max(2,int(6*scale)))
 for xx in [-18,19]:c.oval((*pt(xx-3,-152),*pt(xx+3,-141)),c.p['ink'])
 if expression=='surprise':c.oval((*pt(-7,-125),*pt(7,-110)),c.p['ink'])
 else:c.line([pt(-15,-119),pt(0,-113),pt(16,-119)],width=max(2,int(4*scale)))
 c.line([pt(0,-87),pt(0,90)],width=max(2,int(8*scale)))
 for side in [-1,1]:c.line([pt(0,90),pt(side*(42+walk*18),160),pt(side*(68-walk*28),228)],width=max(2,int(8*scale)))
 c.line([pt(0,-50),pt(-60,10),pt(-71,70)],width=max(2,int(7*scale)))
 hand=pt(96-66*pose,55-178*pose);c.line([pt(0,-50),pt(62,-10-43*pose),hand],width=max(2,int(7*scale)))
 if prop:
  # A bite is a visual state change rather than an unchanged looping prop.
  c.prop(prop,*hand,.7*scale)
  if action=='eat' and t>1.2:
   c.oval((hand[0]+10*scale,hand[1]-28*scale,hand[0]+35*scale,hand[1]-2*scale),c.p['bg'])
 return hand

def draw(c,t,d,s,p):
 kind=s['kind'];u=smooth(t/.5);ph=t/d
 if kind=='stick':
  c.line([(40,855),(680,855)],c.p['cool'],4)
  if s.get('setting')=='night':c.box((490,280,640,440),c.p['paper']);c.prop('moon',565,355,.55)
  else:c.box((490,280,640,440),c.p['paper']);c.line([(565,280),(565,440)],c.p['cool'],3)
  x=230+210*ph if s.get('action')=='walk' else 320
  stick(c,x,620,t,s.get('action','idle'),s.get('prop'),s.get('expression','neutral'),1)
  if s.get('action')=='wait':c.prop('clock',565,670,.8)
 elif kind=='science':
  c.actor(215,570,.95,pose=.1,xray=True)
  c.oval((392,330,675,613),c.p['paper'],c.p['cool'],4)
  organ=s.get('organ','heart');cx,cy=535,470
  if organ=='heart':
   a=1+.06*math.sin(t*8)
   c.oval((cx-65*a,cy-65*a,cx+10*a,cy+20*a),c.p['accent']);c.oval((cx-10*a,cy-65*a,cx+65*a,cy+20*a),c.p['accent']);c.d.polygon([(cx-60*a,cy-12),(cx,cy+85*a),(cx+60*a,cy-12)],fill=c.p['accent'])
  elif organ=='lungs':
   a=1+.06*math.sin(t*3);c.oval((cx-100*a,cy-65*a,cx-8,cy+80*a),c.p['accent']);c.oval((cx+8,cy-65*a,cx+100*a,cy+80*a),c.p['accent']);c.line([(cx,cy-90),(cx,cy+20)],c.p['ink'],8)
  elif organ=='stomach':
   c.oval((cx-50,cy-42,cx+76,cy+62),c.p['accent']);c.line([(cx-22,cy-100),(cx-22,cy-12)],c.p['accent'],24)
  else:c.prop(organ,cx,cy,1.6)
  c.arrow((290,620),(410,540));c.text(s.get('label',organ),530,700,40,max_width=310)
  if s.get('particles'):
   for i in range(9):
    a=t*1.7+i*.7;c.oval((cx+65*math.sin(a)-5,cy+45*math.cos(a*.8)-5,cx+65*math.sin(a)+5,cy+45*math.cos(a*.8)+5),c.p['paper'])
 elif kind=='paper':
  # Parallax sheets with physical offsets rather than a reused text-only card.
  for i in range(3):
   xx=50+i*65+10*math.sin(t*.6+i);yy=280+i*95
   c.box((xx+8,yy+12,xx+430,yy+330),'#BDB4A2',8);c.box((xx,yy,xx+420,yy+318),c.p['paper'],8)
  if s.get('prop'):c.prop(s['prop'],380,620,2)
  else:stick(c,360,600,t,s.get('action','idle'),None,scale=.8)
  if s.get('date'):c.box((60,180,350,250),c.p['accent']);c.text(str(s['date']),205,215,38,c.p['paper'])
 elif kind=='timeline':
  events=s.get('events',[]);c.line([(105,300),(105,880)],c.p['cool'],7)
  for i,event in enumerate(events):
   at=i/max(1,len(events));reveal=smooth((ph-at)*4)
   if reveal<=0:continue
   yy=340+i*min(170,490/max(1,len(events)-1));r=12*reveal;c.oval((105-r,yy-r,105+r,yy+r),c.p['accent']);c.text(str(event['date']),175,yy-22,28,anchor='lm',max_width=460);c.text(event['text'],175,yy+22,30,anchor='lm',max_width=460)
 elif kind=='chart':
  values=s.get('values',[]);maxval=max([abs(v['value']) for v in values]+[1]);c.line([(105,845),(650,845)],c.p['ink'],4)
  for i,v in enumerate(values):
   bw=min(90,480/max(1,len(values)));x=140+i*min(125,490/max(1,len(values)));hh=400*v['value']/maxval*smooth((ph-i*.08)*2);c.box((x,845-hh,x+bw,845),c.p['accent'],8);c.text(v['name'],x+bw/2,885,24,max_width=110);c.text(str(v['value']),x+bw/2,825-hh,26)
 elif kind=='kinetic':
  text=s.get('label',s['text']);tokens=text.split();n=max(1,len(tokens))
  for i,word in enumerate(tokens):
   appear=smooth((ph-i/n)*n*2)
   if appear: c.text(word,360+25*(1-appear),330+i*min(100,500/n),int(55+12*(1-appear)),c.p['accent'] if i%2 else c.p['ink'])
 if s.get('label') and kind not in ['kinetic','science']:c.text(s['label'],360,145,38)
