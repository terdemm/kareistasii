"""Starting point for ORIGINAL topic-specific animation. Copy into project, then rewrite.
All positions are in 720x1280 space. No inter-frame state. draw receives local t.
"""
import math

def draw(c,t,d,s,p):
 # Example: a delivery notification makes the character lift a phone.
 # Replace this blocking with the requested scene; do not reuse it for every topic.
 c.box((45,240,675,930),c.p['paper'],35)
 c.line([(45,840),(675,840)],c.p['cool'],5)
 pose=min(1,max(0,(t-.25)/.8));pose=pose*pose*(3-2*pose)
 c.actor(300,550,1,pose,'surprise' if pose>.7 else 'curious',s.get('prop','phone'))
 if t>.7:
  c.box((440,330,655,425),c.p['accent'],20)
  c.text(s.get('label','DİNG!'),548,378,29,c.p['paper'],max_width=195)
