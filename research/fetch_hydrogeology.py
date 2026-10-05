"""Freeze descriptive SGB layers, preserving raw sources and documented geometry edits."""
import hashlib,json,urllib.parse,urllib.request,zipfile
from datetime import datetime,timezone
from pathlib import Path
import shapely
from shapely.geometry import shape,mapping
ROOT=Path(__file__).resolve().parent;DIST=ROOT.parent/'dist'
SERVICE='https://geoportal.sgb.gov.br/server/rest/services/hidrologia/Mapa_Midrogeologico_Paraiba/FeatureServer'
LAYERS={2:'structures',5:'domains'}
def request(url):
 with urllib.request.urlopen(url,timeout=90) as r:d=json.load(r)
 if 'error' in d:raise RuntimeError(d['error'])
 return d
def rounded(v):
 if isinstance(v,(list,tuple)):return [rounded(x) for x in v]
 return round(v,6) if isinstance(v,float) else v
def prepare_context(output):
 features=[];repairs=[];fallbacks=[]
 for f in output['domains']['features']:
  g=shape(f['geometry'])
  if not g.is_valid:
   reason=shapely.is_valid_reason(g);fixed=shapely.make_valid(g);change=abs(fixed.area-g.area)/g.area if g.area else None
   if fixed.geom_type not in ['Polygon','MultiPolygon'] or change is None or change>.001:raise ValueError('Geometry repair requires manual review')
   repairs.append({'feature_id':f['id'],'reason':reason,'relative_area_change':change,'operation':'shapely.make_valid'});g=fixed
  m=mapping(g.simplify(.0005,preserve_topology=True));compact={'type':m['type'],'coordinates':rounded(m['coordinates'])}
  if not shape(compact).is_valid:compact=m;fallbacks.append(f['id'])
  if not shape(compact).is_valid:raise ValueError('Invalid derived polygon')
  features.append({**f,'geometry':compact})
 output['provenance']['derivation']={'domain_simplification_degrees':.0005,'coordinate_decimals':6,'preserve_topology':True,'geometry_repairs':repairs,'full_precision_fallback_feature_ids':fallbacks,'boundary_warning':'Regional map. Unit membership near boundaries needs field verification. Training and browser share the same derived geometry.'}
 (ROOT/'hydro_provenance.json').write_text(json.dumps(output['provenance'],ensure_ascii=False,indent=2))
 with zipfile.ZipFile(ROOT/'hydro_layers_source.zip','w',zipfile.ZIP_DEFLATED) as z:
  for name in LAYERS.values():z.write(ROOT/f'hydro_{name}.geojson',f'hydro_{name}.geojson')
  z.writestr('hydro_provenance.json',json.dumps(output['provenance'],ensure_ascii=False,indent=2))
 derived={**output,'domains':{'type':'FeatureCollection','features':features}}
 (DIST/'hydro_context.json').write_text(json.dumps(derived,ensure_ascii=False,separators=(',',':')))
 return derived
def fetch():
 p={'provider':'SGB/CPRM','service':SERVICE,'accessed_utc':datetime.now(timezone.utc).isoformat(),'map_reference':'Brito & Paula, 2019','catalog_url':'https://rigeo.sgb.gov.br/handle/doc/21598','excluded_predictor_layers':[0,1,4,6,7,8,9],'excluded_reason':'Avoid target-derived conductivity, productivity and well-density information; use descriptive structures and hydrolithological domains only.','layers':{}}
 output={'provenance':p}
 for layer,name in LAYERS.items():
  base=f'{SERVICE}/{layer}';meta=request(base+'?f=pjson');idurl=base+'/query?'+urllib.parse.urlencode({'where':'1=1','returnIdsOnly':'true','f':'json'})
  ids=sorted(request(idurl)['objectIds']);features=[];urls=[]
  for start in range(0,len(ids),400):
   url=base+'/query?'+urllib.parse.urlencode({'objectIds':','.join(map(str,ids[start:start+400])),'outFields':'*','returnGeometry':'true','outSR':'4326','f':'geojson'})
   page=request(url)
   if page.get('type')!='FeatureCollection' or page.get('exceededTransferLimit'):raise ValueError('Unexpected or truncated SGB geometry')
   features.extend(page['features']);urls.append(url)
  if len(features)!=len(ids) or len({f['id'] for f in features})!=len(ids):raise ValueError('Missing or repeated SGB features')
  collection={'type':'FeatureCollection','features':features};raw=json.dumps(collection,ensure_ascii=False,separators=(',',':')).encode();(ROOT/f'hydro_{name}.geojson').write_bytes(raw)
  p['layers'][name]={'id':layer,'name':meta['name'],'features':len(features),'metadata_url':base+'?f=pjson','ids_url':idurl,'query_urls':urls,'sha256':hashlib.sha256(raw).hexdigest(),'source_crs':meta['extent']['spatialReference'],'output_crs':'EPSG:4326','copyright':meta.get('copyrightText','SGB/CPRM')};output[name]=collection
  print(name,len(features),'features',flush=True)
 return prepare_context(output)
if __name__=='__main__':fetch()
