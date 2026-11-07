"""Fetch verified Supertonic 3 weights from the official sherpa-onnx GitHub release."""
import argparse,hashlib,json,os,pathlib,shutil,tarfile,tempfile,urllib.request
URL='https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/sherpa-onnx-supertonic-3-tts-int8-2026-05-11.tar.bz2'
SHA256='82fa96f91c4ef8abaae3a14a3f4153facf88bed821d1f7331cec2700f432c427'
DEFAULT=pathlib.Path(os.environ.get('KARE_SUPERTONIC_MODELS',str(pathlib.Path.home()/'.cache/kare-ustasi/supertonic-3')))
FILES=['duration_predictor.int8.onnx','text_encoder.int8.onnx','vector_estimator.int8.onnx','vocoder.int8.onnx','tts.json','unicode_indexer.bin','voice.bin']

def prepare_model(cache=None,offline=False):
 cache=pathlib.Path(cache or DEFAULT).resolve();manifest=cache/'verified.json'
 if manifest.is_file() and all((cache/f).is_file() and (cache/f).stat().st_size>0 for f in FILES):
  hashes=json.loads(manifest.read_text())
  if hashes.get('archive_sha256')==SHA256 and all(hashlib.sha256((cache/f).read_bytes()).hexdigest()==hashes.get(f) for f in FILES):return cache
 if offline:raise RuntimeError('Turkish model cache missing or incomplete. First run needs the official GitHub release download.')
 cache.parent.mkdir(parents=True,exist_ok=True)
 with tempfile.TemporaryDirectory(prefix='supertonic-',dir=cache.parent) as tmp:
  tmp=pathlib.Path(tmp);archive=tmp/'model.tar.bz2'
  print('Downloading Turkish model from official GitHub release (~128 MB)...',flush=True)
  req=urllib.request.Request(URL,headers={'User-Agent':'Kare-Ustasi/7'})
  with urllib.request.urlopen(req,timeout=90) as response,archive.open('wb') as out:
   if urllib.parse.urlparse(response.url).hostname not in ['github.com','release-assets.githubusercontent.com']:raise RuntimeError('Unexpected model download host')
   shutil.copyfileobj(response,out)
  if hashlib.sha256(archive.read_bytes()).hexdigest()!=SHA256:raise RuntimeError('Model archive checksum mismatch; cache left unchanged')
  stage=tmp/'model';stage.mkdir()
  with tarfile.open(archive,'r:bz2') as tar:
   for name in FILES:
    matches=[m for m in tar.getmembers() if m.isfile() and pathlib.PurePosixPath(m.name).name==name]
    if len(matches)!=1:raise RuntimeError('Required model file missing or ambiguous: '+name)
    with tar.extractfile(matches[0]) as source,(stage/name).open('wb') as out:shutil.copyfileobj(source,out)
  notices=pathlib.Path(__file__).resolve().parent.parent/'speech/supertonic'
  for name in ['LICENSE.txt','NOTICE.txt']:shutil.copy2(notices/name,stage/name)
  hashes={f:hashlib.sha256((stage/f).read_bytes()).hexdigest() for f in FILES};hashes['archive_sha256']=SHA256
  (stage/'verified.json').write_text(json.dumps(hashes,indent=2))
  cache.mkdir(exist_ok=True)
  for file in stage.iterdir():os.replace(file,cache/file.name)
 return cache
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--cache',type=pathlib.Path,default=DEFAULT);ap.add_argument('--offline',action='store_true');a=ap.parse_args()
 print(prepare_model(a.cache,a.offline))
