"""Independent sklearn reference outputs for verifying exported browser models."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
import json
from pathlib import Path
import numpy as np
from sklearn.preprocessing import StandardScaler
from compare_five_models import build_method,prediction,NAMES

ROOT=Path(__file__).resolve().parent;DIST=ROOT.parent/'dist'
b=json.loads((DIST/'ai_models.json').read_text());out={};rng=np.random.default_rng(573)
for task,t in b['tasks'].items():
    rows=t['records'];x=np.array([[r['latitude'],r['longitude'],r['depth_m']] for r in rows]);y=np.array([r['label'] for r in rows]);scaler=StandardScaler().fit(x);xs=scaler.transform(x)
    refs=x[rng.choice(len(x),size=24,replace=False)].copy();refs[:12,:2]+=rng.normal(0,.004,(12,2));refs[:12,2]*=rng.uniform(.9,1.1,12)
    expected={}
    for name in NAMES:
        m=build_method(name,xs,y);p=prediction(m,name,scaler.transform(refs));score=m.predict_proba(scaler.transform(refs))[:,1] if name!='k_means' else [None]*len(refs)
        expected[name]=[{'input':a.tolist(),'label':int(v),'score':None if s is None else float(s)} for a,v,s in zip(refs,p,score)]
    out[task]=expected
(ROOT/'reference_predictions.json').write_text(json.dumps(out))
print('Independent references:',sum(len(rows) for t in out.values() for rows in t.values()))
