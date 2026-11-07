"""Create a small editable project. Never overwrites existing user files."""
import argparse,json,pathlib,shutil
ROOT=pathlib.Path(__file__).resolve().parent.parent
KIND={'stick':'actor','line-stick':'stick','cartoon':'actor','science':'science','map':'geomap','paper':'paper','three-d':'scene3d'}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('directory');ap.add_argument('--kind',choices=list(KIND),default='stick');a=ap.parse_args();out=pathlib.Path(a.directory);out.mkdir(parents=True,exist_ok=True)
 if (out/'project.json').exists() or (out/'scenes.py').exists():ap.exit(1,'Project exists; refusing to overwrite.\n')
 scene={'text':'Bu bir örnek sahnedir.','duration':3,'kind':KIND[a.kind],'label':'','captions':True,'zoom':.03,'sfx':[{'at':.3,'type':'pop'}]}
 if a.kind in ['stick','cartoon','three-d']:scene.update({'action':'lift','prop':'apple'})
 if a.kind=='science':scene.update({'organ':'heart','particles':True})
 if a.kind=='map':scene.update({'zoom':0,'map':{'bounds':[5,34,40,57],'route':[[28.9784,41.0082],[13.405,52.52]],'highlight':['TUR','DEU'],'markers':[{'name':'İstanbul','at':[28.9784,41.0082]},{'name':'Berlin','at':[13.405,52.52]}]}})
 (out/'project.json').write_text(json.dumps({'title':'Yeni animasyon','style':'merak','language':'tr','music':'none','sources':[],'scenes':[scene]},ensure_ascii=False,indent=2),encoding='utf-8')
 (out/'scenes.py').write_text('from studio import default_scene\n\ndef draw(c,t,d,s,p):\n    # Add original custom scenes here; built-in dispatch remains available.\n    default_scene(c,t,d,s,p)\n',encoding='utf-8')
 print(out/'project.json')
if __name__=='__main__':main()
