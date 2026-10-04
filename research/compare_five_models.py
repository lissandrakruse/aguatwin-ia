"""Reproducible spatial comparison; no synthetic labels or test-set tuning."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
import csv, json, math, hashlib
from pathlib import Path
import numpy as np
import sklearn
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GroupKFold
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.cluster import KMeans
from sklearn.metrics import confusion_matrix, accuracy_score, balanced_accuracy_score, f1_score

ROOT=Path(__file__).resolve().parent; DIST=ROOT.parent/'dist'
NAMES=['knn','random_forest','naive_bayes','k_means','cnn']
LABELS=['KNN','Random Forest','Naive Bayes','K-means','CNN 1D']

class TinyCNN:
    """Conv1D(8 filters, width 2), ReLU, flatten, linear softmax.
    Feature order latitude/longitude/planned depth is arbitrary, not an image.
    Implemented in NumPy and checked by central finite differences.
    """
    def __init__(self,seed=42,epochs=250):
        self.seed=seed; self.epochs=epochs; rng=np.random.default_rng(seed)
        self.params={'wc':rng.normal(0,.35,(8,2)),'bc':np.zeros(8),'wd':rng.normal(0,.2,(16,2)),'bd':np.zeros(2)}
    def forward(self,x):
        windows=np.stack([x[:,:2],x[:,1:]],axis=1)
        pre=np.einsum('npk,fk->npf',windows,self.params['wc'])+self.params['bc']
        h=np.maximum(pre,0).reshape(-1,16)
        z=h@self.params['wd']+self.params['bd']; z-=z.max(axis=1,keepdims=True)
        p=np.exp(z);p/=p.sum(axis=1,keepdims=True)
        return p,(windows,pre,h)
    def loss_grad(self,x,y,sample_weights=None):
        p,(w,pre,h)=self.forward(x)
        sw=np.ones(len(y)) if sample_weights is None else sample_weights
        sw=sw/sw.sum(); reg=.001
        loss=float(-np.sum(sw*np.log(np.maximum(p[np.arange(len(y)),y],1e-300)))+reg*.5*(np.sum(self.params['wc']**2)+np.sum(self.params['wd']**2)))
        dz=p.copy();dz[np.arange(len(y)),y]-=1;dz*=sw[:,None]
        dp=(dz@self.params['wd'].T).reshape(-1,2,8)*(pre>0)
        grads={'wc':np.einsum('npf,npk->fk',dp,w)+reg*self.params['wc'],'bc':dp.sum(axis=(0,1)),'wd':h.T@dz+reg*self.params['wd'],'bd':dz.sum(axis=0)}
        return loss,grads
    def fit(self,x,y):
        counts=np.bincount(y,minlength=2);sw=np.array([len(y)/(2*counts[t]) for t in y])
        m={k:np.zeros_like(v) for k,v in self.params.items()};v={k:np.zeros_like(a) for k,a in self.params.items()}
        for t in range(1,self.epochs+1):
            loss,g=self.loss_grad(x,y,sw)
            for k in self.params:
                m[k]=.9*m[k]+.1*g[k];v[k]=.999*v[k]+.001*g[k]**2
                self.params[k]-=.01*(m[k]/(1-.9**t))/(np.sqrt(v[k]/(1-.999**t))+1e-8)
        self.loss=loss;return self
    def predict_proba(self,x):return self.forward(x)[0]
    def predict(self,x):return np.argmax(self.predict_proba(x),axis=1)

def check_gradients():
    rng=np.random.default_rng(19); x=rng.normal(size=(9,3)); y=np.array([0,1,0,1,1,0,0,1,1]);model=TinyCNN()
    _,g=model.loss_grad(x,y);errors=[]
    for k,a in model.params.items():
        for ix in list(np.ndindex(a.shape))[:10]:
            original=a[ix];a[ix]=original+1e-5;up=model.loss_grad(x,y)[0];a[ix]=original-1e-5;down=model.loss_grad(x,y)[0];a[ix]=original
            errors.append(abs((up-down)/2e-5-g[k][ix]))
    assert max(errors)<1e-6, max(errors)
    return {'method':'Central finite differences, epsilon 1e-5','parameters_checked':len(errors),'max_absolute_error':max(errors),'passed':True}

def build_method(name,x,y):
    if name=='knn':return KNeighborsClassifier(n_neighbors=9,weights='uniform',n_jobs=1).fit(x,y)
    if name=='random_forest':return RandomForestClassifier(n_estimators=64,max_depth=6,min_samples_leaf=5,class_weight='balanced_subsample',random_state=42,n_jobs=1).fit(x,y)
    if name=='naive_bayes':return GaussianNB(var_smoothing=1e-9).fit(x,y)
    if name=='k_means':
        m=KMeans(n_clusters=2,n_init=10,random_state=42).fit(x)
        m.class_map=np.array([np.bincount(y[m.labels_==k],minlength=2).argmax() for k in range(2)])
        return m
    if name=='cnn':return TinyCNN().fit(x,y)
    raise KeyError(name)

def prediction(m,name,x):
    if name=='k_means':return m.class_map[m.predict(x)]
    return m.predict(x)
def metric(y,p):
    c=confusion_matrix(y,p,labels=[0,1]); return {'accuracy':float(accuracy_score(y,p)),'balanced_accuracy':float(balanced_accuracy_score(y,p)),'macro_f1':float(f1_score(y,p,average='macro',zero_division=0)),'recall_class0':float(c[0,0]/c[0].sum()) if c[0].sum() else None,'recall_class1':float(c[1,1]/c[1].sum()) if c[1].sum() else None,'confusion_matrix':c.tolist()}

def export_model(m,name,x,y):
    if name=='knn':return {'k':9,'x':x.tolist(),'y':y.tolist()}
    if name=='random_forest':
        trees=[]
        for est in m.estimators_:
            t=est.tree_;v=t.value[:,0,:];v=v/np.maximum(v.sum(axis=1,keepdims=True),1e-300)
            trees.append({'left':t.children_left.tolist(),'right':t.children_right.tolist(),'feature':t.feature.tolist(),'threshold':t.threshold.tolist(),'p1':v[:,1].tolist()})
        return {'trees':trees}
    if name=='naive_bayes':return {'mean':m.theta_.tolist(),'variance':m.var_.tolist(),'prior':m.class_prior_.tolist()}
    if name=='k_means':return {'centers':m.cluster_centers_.tolist(),'class_map':m.class_map.tolist()}
    if name=='cnn':return {k:v.tolist() for k,v in m.params.items()}

def run_task(task,filename):
    data=json.loads((ROOT/filename).read_text());rows=data['wells']
    x=np.array([[r['latitude'],r['longitude'],r['depth_m']] for r in rows],dtype=float)
    y=np.array([r['label'] if task=='potential' else int(r['ce_us_cm']>3000) for r in rows],dtype=int)
    # Approximately 4 km grid. Adjacent blocks can appear in different folds; no buffer.
    groups=np.array([f'{math.floor((r[0]+8)/.04)}:{math.floor((r[1]+37)/.04)}' for r in x])
    oof={n:np.full(len(y),-1,dtype=int) for n in NAMES};baseline=np.full(len(y),-1,dtype=int);fold_index=np.full(len(y),-1,dtype=int);folds={n:[] for n in NAMES}
    splits=list(GroupKFold(n_splits=5).split(x,y,groups))
    for fold,(train,test) in enumerate(splits,1):
        assert not (set(groups[train])&set(groups[test]))
        assert not (set(rows[i]['id'] for i in train)&set(rows[i]['id'] for i in test))
        scale=StandardScaler().fit(x[train]); xt=scale.transform(x[train]); xv=scale.transform(x[test]);fold_index[test]=fold
        baseline[test]=np.bincount(y[train],minlength=2).argmax()
        for name in NAMES:
            m=build_method(name,xt,y[train]);p=prediction(m,name,xv);oof[name][test]=p
            folds[name].append({'fold':fold,'train_n':len(train),'test_n':len(test),'train_groups':len(set(groups[train])),'test_groups':len(set(groups[test])),'test_class_counts':np.bincount(y[test],minlength=2).tolist(),**metric(y[test],p)})
        print(task,'fold',fold,'completed',flush=True)
    for name in NAMES:assert np.all(oof[name]>=0)
    scale=StandardScaler().fit(x); xs=scale.transform(x);models={}
    refs=x[[0,len(x)//2,-1]]
    for name,label in zip(NAMES,LABELS):
        m=build_method(name,xs,y)
        models[name]={'label':label,'parameters':export_model(m,name,xs,y),'metrics_oof':metric(y,oof[name]),'folds':folds[name],'reference_predictions':[{'input':a.tolist(),'label':int(p)} for a,p in zip(refs,prediction(m,name,scale.transform(refs)))]}
    # Full observations and OOF predictions allow held-out display for a selected well.
    records=[{**r,'label':int(y[i]),'group':groups[i],'fold':int(fold_index[i]),'oof':{n:int(oof[n][i]) for n in NAMES}} for i,r in enumerate(rows)]
    result={'task':task,'n':len(rows),'groups':len(set(groups)),'municipalities':len({r['municipality'] for r in rows}),'class_counts':np.bincount(y,minlength=2).tolist(),'features':['latitude','longitude','depth_m'],'scaler':{'mean':scale.mean_.tolist(),'scale':scale.scale_.tolist()},'bounds':{'min':x.min(axis=0).tolist(),'max':x.max(axis=0).tolist()},'records':records,'models':models,'baseline':metric(y,baseline),'provenance':data['provenance']}
    with (DIST/f'dataset_{task}_Paraiba.csv').open('w',newline='',encoding='utf-8-sig') as out:
        keys=['id','municipality','latitude','longitude','depth_m','label','fold','group']+(['ce_us_cm'] if task=='salinity' else ['status','specific_yield'])
        w=csv.DictWriter(out,fieldnames=keys,extrasaction='ignore');w.writeheader();w.writerows(records)
    print(task,'summary',json.dumps({n:models[n]['metrics_oof'] for n in NAMES}),flush=True)
    return result

if __name__=='__main__':
    gradient=check_gradients();print('CNN gradient check',gradient,flush=True)
    tasks={'salinity':run_task('salinity','paraiba_dataset.json'),'potential':run_task('potential','potential_dataset.json')}
    bundle={'version':'2.0','trained_at':'2026-10-04','libraries':{'numpy':np.__version__,'sklearn':sklearn.__version__},'cnn_gradient_check':gradient,'validation':'Five shared spatial GroupKFold folds on 0.04-degree cells; standardization and cluster-to-class mapping fit on train only; pooled out-of-fold scores. No held-out hyperparameter tuning. No spatial buffer or prospective independent validation.','feature_warning':'Latitude, longitude and well depth only. Depth is a chosen scenario for a new site, not a causal drilling-depth recommendation. No lithology, fractures, relief or rainfall predictors yet.','nasa_role':'POWER provides climatic context for water/solar simulation; it is not a predictor in these two ML tasks.','cnn_warning':'Experimental 1D convolution on three ordered tabular features, not satellite imagery.','kmeans_warning':'Unsupervised two-cluster fit, followed by train-only majority assignment to outcome classes. This is not a supervised classifier.','domain_rule':'Within training feature bounds and within 5 km of a recorded observation. A practical screen, not proof of hydrogeological applicability or a calibrated uncertainty estimate.','settings':{'seed':42,'knn':'k=9 uniform; standardized inputs','random_forest':'64 trees, depth<=6, leaf>=5, balanced_subsample','naive_bayes':'Gaussian, var_smoothing=1e-9, empirical priors','k_means':'2 clusters, n_init=10, train-only majority class map','cnn':'8 width-2 filters, ReLU, flatten16, dense2, weighted cross entropy, L2=.001, Adam lr=.01, 250 epochs; standardized inputs'},'tasks':tasks}
    blob=json.dumps(bundle,ensure_ascii=False,separators=(',',':')).encode()
    (DIST/'ai_models.json').write_bytes(blob)
    report={k:v for k,v in bundle.items() if k!='tasks'}
    report['tasks']={k:{**{p:q for p,q in v.items() if p not in ('models','records')},'models':{n:{a:b for a,b in m.items() if a!='parameters'} for n,m in v['models'].items()},'validation_records':v['records']} for k,v in tasks.items()}
    (DIST/'validacao_IA_AguaTwin.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    (ROOT/'ai_models.sha256').write_text(hashlib.sha256(blob).hexdigest())
    print('model_bundle_bytes',len(blob),flush=True)
