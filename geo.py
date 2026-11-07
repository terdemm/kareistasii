"""Offline GeoJSON map rendering, geographic route interpolation and camera framing.
Independently implemented using public-domain Natural Earth data.
"""
import json,math,pathlib,functools
from PIL import Image,ImageDraw
ROOT=pathlib.Path(__file__).resolve().parent.parent
@functools.lru_cache(maxsize=4)
def read_geo(path):
 data=json.loads(pathlib.Path(path).read_text(encoding='utf-8'))
 if data.get('type')!='FeatureCollection':raise ValueError('GeoJSON FeatureCollection required')
 return data['features']
def wrap(lon,center):return center+(lon-center+180)%360-180
def merc(lat):return math.degrees(math.log(math.tan(math.pi/4+math.radians(max(-85,min(85,lat)))/2)))
def distance(a,b):
 la,lb=map(math.radians,[a[1],b[1]]);dl=math.radians(b[0]-a[0]);da=lb-la
 return 6371.0088*2*math.asin(min(1,math.sqrt(math.sin(da/2)**2+math.cos(la)*math.cos(lb)*math.sin(dl/2)**2)))
def arc(a,b,n=80):
 def xyz(v):lo,la=map(math.radians,v);return [math.cos(la)*math.cos(lo),math.cos(la)*math.sin(lo),math.sin(la)]
 va,vb=xyz(a),xyz(b);angle=math.acos(max(-1,min(1,sum(x*y for x,y in zip(va,vb)))))
 if math.pi-angle<1e-7:raise ValueError('Antipodal route needs an intermediate waypoint')
 out=[]
 for i in range(n+1):
  u=i/n
  v=[(1-u)*x+u*y for x,y in zip(va,vb)] if angle<1e-7 else [(math.sin((1-u)*angle)*x+math.sin(u*angle)*y)/math.sin(angle) for x,y in zip(va,vb)]
  out.append([math.degrees(math.atan2(v[1],v[0])),math.degrees(math.atan2(v[2],math.hypot(v[0],v[1])))])
 return out
def color_mix(a,b,t):
 def rgb(h):return tuple(int(h[i:i+2],16) for i in [1,3,5])
 return tuple(round(x+(y-x)*t) for x,y in zip(rgb(a),rgb(b)))
def draw(c,t,d,s,p):
 cfg=s.get('map',{});bounds=cfg.get('bounds',[-180,-65,180,85]);left,bottom,right,top=bounds
 if right<=left or top<=bottom:raise ValueError('Map bounds must increase; dateline bounds may use longitudes >180')
 route=cfg.get('route',[]);great=cfg.get('great_circle',True);center=(left+right)/2
 points=[]
 for a,b in zip(route,route[1:]):points.extend(arc(a,b,60)[:-1] if great else [[a[0]+(b[0]-a[0])*i/60,a[1]+(b[1]-a[1])*i/60] for i in range(60)])
 if route:points.append(route[-1])
 points=[[wrap(a,center),b] for a,b in points]
 progress=max(0,min(1,t/max(.01,d-.3)));sample=min(len(points)-1,int(progress*max(0,len(points)-1))) if points else 0
 if cfg.get('follow') and points:
  cx,cy=points[sample];bw=right-left;bh=top-bottom;left,right=cx-bw/2,cx+bw/2;bottom,top=cy-bh/2,cy+bh/2;center=cx
 if cfg.get('end_bounds'):
  u=progress*progress*(3-2*progress);left,bottom,right,top=[a+(b-a)*u for a,b in zip([left,bottom,right,top],cfg['end_bounds'])];center=(left+right)/2
 projection=cfg.get('projection','mercator');latfn=merc if projection=='mercator' else lambda x:x
 x0,y0,x1,y1=30,245,690,940;spanx=right-left;spany=latfn(top)-latfn(bottom)
 factor=min((x1-x0)/spanx,(y1-y0)/spany);ox=(x0+x1)/2;oy=(y0+y1)/2;my=(latfn(top)+latfn(bottom))/2
 def project(lon,lat):return (ox+(wrap(lon,center)-center)*factor,oy-(latfn(lat)-my)*factor)
 layer=Image.new('RGB',(720,1280),c.p['bg']);dr=ImageDraw.Draw(layer)
 highlights=cfg.get('highlight',[]);values=cfg.get('values',{});vmin=cfg.get('vmin',min(values.values()) if values else 0);vmax=cfg.get('vmax',max(values.values()) if values else 1)
 features=read_geo(str(cfg.get('geojson',ROOT/'assets/world-110m.geojson')))
 for feature in features:
  g=feature.get('geometry') or {};typ=g.get('type');polygons=[g['coordinates']] if typ=='Polygon' else g.get('coordinates',[]) if typ=='MultiPolygon' else []
  props=feature.get('properties',{});code=props.get('iso',props.get('ISO_A3',props.get('ADM0_A3','')));name=props.get('name',props.get('ADMIN',''))
  value=values.get(code,values.get(name));fill=c.p['accent'] if code in highlights or name in highlights else c.p['paper']
  if value is not None:fill=color_mix(c.p['paper'],c.p['accent'],max(0,min(1,(value-vmin)/max(1e-9,vmax-vmin))))
  for rings in polygons:
   for idx,ring in enumerate(rings):
    xy=[project(*v[:2]) for v in ring]
    # Dateline seams cannot become a stripe across the world map.
    if len(xy)<3 or any(abs(a[0]-b[0])>factor*180 for a,b in zip(xy,xy[1:])):continue
    dr.polygon(xy,fill=fill if idx==0 else c.p['bg']);dr.line(xy,fill=c.p['cool'],width=1)
 if len(points)>1:
  xy=[project(*v) for v in points]
  for i in range(1,len(xy)):
   if abs(xy[i][0]-xy[i-1][0])<factor*180:dr.line([xy[i-1],xy[i]],fill=c.p['cool'],width=3)
  for i in range(1,sample+1):
   if abs(xy[i][0]-xy[i-1][0])<factor*180:dr.line([xy[i-1],xy[i]],fill=c.p['accent'],width=7)
  x,y=xy[sample];r=9+3*math.sin(t*5);dr.ellipse((x-r,y-r,x+r,y+r),fill=c.p['accent'])
 # Clip the entire geographic world into its viewport before screen-space labels.
 c.im.paste(layer.crop((x0,y0,x1,y1)),(x0,y0));c.d=ImageDraw.Draw(c.im)
 occupied=[]
 for mark in cfg.get('markers',[]):
  x,y=project(*mark['at'])
  if not x0+10<x<x1-10 or not y0+20<y<y1-20:continue
  c.oval((x-7,y-7,x+7,y+7),c.p['accent']);label=mark.get('name','');ly=y-25
  if any(abs(x-a)<110 and abs(ly-b)<30 for a,b in occupied):ly=y+27
  labelx=max(x0+100,min(x1-100,x));ly=max(y0+20,min(y1-20,ly));occupied.append((labelx,ly));c.text(label,labelx,ly,25,max_width=190)
 if cfg.get('distance') and len(route)>1:
  km=sum(distance(a,b) for a,b in zip(route,route[1:]));c.text(f'{km:,.0f} km',360,188,40);c.text('Great-circle distance / not a road route',360,965,18)
 if s.get('label'):c.text(s['label'],360,120,38)
 c.text('Natural Earth · 1:110m',130,935,14,max_width=200)
