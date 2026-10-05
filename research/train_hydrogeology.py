"""Predeclared geological ablation and distance-buffered spatial validation."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
import json,math
from pathlib import Path
import numpy as np
from shapely.geometry import shape,Point
from shapely.ops import transform
from shapely.strtree import STRtree
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GroupKFold
from sklearn.neighbors import BallTree
from sklearn.preprocessing import OneHotEncoder
from compare_five_models import metric,export_model
ROOT=Path(__file__).resolve().parent;DIST=ROOT.parent/'dist'
FEATURE_SETS={'cadastre':['latitude','longitude','depth_m'],'geology':['latitude','longitude','depth_m','log_structure_distance'],'pre_drill':['latitude','longitude','log_structure_distance']}
BUFFERS_KM=[0,2,5]
GEO_CRS='Local equirectangular approximation: lat0=-7.15, lon0=-36.5, 111.195 km/degree; identical in Python/browser; not survey distances'
class Geology:
 def __init__(self):
  d=json.loads((DIST/'hydro_context.json').read_text());self.domains=d['domains']['features'];self.structures=d['structures']['features']
  self.project=lambda lon,lat,z=None:((np.asarray(lon)+36.5)*111195*math.cos(math.radians(-7.15)),(np.asarray(lat)+7.15)*111195)
  polygons=[shape(f['geometry']) for f in self.domains]
  if any(not g.is_valid for g in polygons):raise ValueError('Invalid derived geometry')
  self.domtree=STRtree(polygons);self.lines=[transform(self.project,shape(f['geometry'])) for f in self.structures];self.linetree=STRtree(self.lines)
 def features(self,rows):
  out=[]
  for r in rows:
   point=Point(r['longitude'],r['latitude']);matches=sorted(self.domtree.query(point,predicate='covered_by').tolist());domain=self.domains[matches[0]]['properties']['u_hl_afl'] if matches else None
   xy=transform(self.project,point);ix=int(self.linetree.nearest(xy));distance=float(xy.distance(self.lines[ix])/1000)
   out.append({**r,'hydrolithological_domain':domain or '__unmapped__','domain_polygon_matches':len(matches),'mapped_structure_distance_km':distance,'nearest_structure_id':self.structures[ix]['id'],'log_structure_distance':math.log1p(distance)})
  return out
def design(rows,kind,encoder=None,fit=False):
 x=np.array([[r[k] for k in FEATURE_SETS[kind]] for r in rows],dtype=float)
 if kind=='cadastre':return x,None
 categories=np.array([[r['hydrolithological_domain']] for r in rows],dtype=object)
 if fit:encoder=OneHotEncoder(handle_unknown='ignore',sparse_output=False).fit(categories)
 return np.column_stack([x,encoder.transform(categories)]),encoder
def model():return RandomForestClassifier(n_estimators=64,max_depth=6,min_samples_leaf=5,class_weight='balanced_subsample',random_state=42,n_jobs=1)
def run():
 geology=Geology();p=json.loads((ROOT/'hydro_provenance.json').read_text())
 report={'version':'2.1','source':p,'buffers_km':BUFFERS_KM,'distance_crs':GEO_CRS,'features':{k:v+([] if k=='cadastre' else ['hydrolithological_domain (train-only one-hot)']) for k,v in FEATURE_SETS.items()},'fold_definition':'Same five 0.04-degree GroupKFold splits as v2.0; remove training points closer than each buffer to any held-out point','selection':'Settings, buffers and feature sets fixed before testing. No best-result selection. Deploy pre_drill because observed borehole depth is unavailable at new locations.','limitations':['Historical status, not dated drilling outcome','Regional structures are not verified water-bearing fractures','Uncalibrated scores; tree dispersion is a heuristic','No terrain variables, field geophysics or community reports in this training','No prospective validation or efficacy claim'],'tasks':{}}
 bundle={'version':'2.1','calibrated_probabilities':False,'distance_crs':GEO_CRS,'numeric_features':FEATURE_SETS['pre_drill'],'tasks':{}}
 allrows={}
 for task,filename in [('potential','potential_dataset.json'),('salinity','paraiba_dataset.json')]:
  rows=geology.features(json.loads((ROOT/filename).read_text())['wells']);allrows[task]=rows
  y=np.array([r['label'] if task=='potential' else int(r['ce_us_cm']>3000) for r in rows]);coords=np.array([[r['latitude'],r['longitude']] for r in rows]);groups=np.array([f'{math.floor((a+8)/.04)}:{math.floor((b+37)/.04)}' for a,b in coords]);splits=list(GroupKFold(n_splits=5).split(coords,y,groups))
  tr={'n':len(rows),'unmapped':sum(r['hydrolithological_domain']=='__unmapped__' for r in rows),'multiple_domain_matches':sum(r['domain_polygon_matches']>1 for r in rows),'evaluations':[]}
  for buffer in BUFFERS_KM:
   pred={k:np.full(len(y),-1,dtype=int) for k in FEATURE_SETS};folds=[]
   for fold,(train,test) in enumerate(splits,1):
    before=len(train);near=BallTree(np.radians(coords[test]),metric='haversine').query(np.radians(coords[train]),k=1)[0][:,0]*6371;train=train[near>=buffer]
    info={'fold':fold,'train_before':before,'train_n':len(train),'test_n':len(test),'train_class_counts':np.bincount(y[train],minlength=2).tolist(),'minimum_train_test_km':float(near[near>=buffer].min()) if len(train) else None}
    if len(train)<30 or len(np.unique(y[train]))!=2:info['skipped']='Insufficient training support';folds.append(info);continue
    assert not set(groups[train]).intersection(groups[test])
    for kind in FEATURE_SETS:
     xt,enc=design([rows[i] for i in train],kind,fit=True);xv,_=design([rows[i] for i in test],kind,enc);pred[kind][test]=model().fit(xt,y[train]).predict(xv)
    folds.append(info)
   for kind,pr in pred.items():
    valid=pr>=0;tr['evaluations'].append({'feature_set':kind,'buffer_km':buffer,'tested_n':int(valid.sum()),'coverage':float(valid.mean()),'folds':folds,'metrics':metric(y[valid],pr[valid]) if valid.any() else None})
   print(task,'buffer',buffer,'completed',flush=True)
  x,enc=design(rows,'pre_drill',fit=True);rf=model().fit(x,y)
  t={'category_levels':enc.categories_[0].tolist(),'parameters':export_model(rf,'random_forest',x,y),'n':len(rows),'bounds':{'min':coords.min(axis=0).tolist(),'max':coords.max(axis=0).tolist()},'support_records':[{'id':r['id'],'latitude':r['latitude'],'longitude':r['longitude']} for r in rows],'reference_predictions':[]}
  for i in np.linspace(0,len(rows)-1,15,dtype=int):
   scores=np.array([e.predict_proba(x[i:i+1])[0,1] for e in rf.estimators_]);t['reference_predictions'].append({'record':rows[int(i)],'features':x[i].tolist(),'score':float(rf.predict_proba(x[i:i+1])[0,1]),'tree_std':float(scores.std(ddof=0))})
  bundle['tasks'][task]=t;report['tasks'][task]=tr
 (ROOT/'hydro_features.json').write_text(json.dumps({'provenance':p,'tasks':allrows},ensure_ascii=False,separators=(',',':')))
 (DIST/'hydro_models.json').write_text(json.dumps(bundle,ensure_ascii=False,separators=(',',':')));(DIST/'hydro_validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
 for task,t in report['tasks'].items():
  for e in t['evaluations']:print(task,e['feature_set'],e['buffer_km'],round(e['metrics']['balanced_accuracy'],4) if e['metrics'] else None)
if __name__=='__main__':run()
