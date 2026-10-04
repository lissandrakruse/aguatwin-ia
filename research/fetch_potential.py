"""Read-only retrieval of SIAGAS well outcomes; no invented dry wells."""
import json, hashlib, urllib.parse, urllib.request
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

ROOT=Path(__file__).resolve().parent
BASE='https://geoportal.sgb.gov.br/server/rest/services/Hosted/siagas_web/FeatureServer/1/query'
WHERE="str_uf='PB' AND str_natureza_ponto='Poço tubular' AND num_profundidade>0 AND (str_tipo_situacao='Seco' OR num_vazao_especifica>0)"
FIELDS='idt_ponto,str_municipio,str_uf,str_natureza_ponto,str_tipo_situacao,str_aquifero,num_profundidade,num_vazao_especifica,num_condutividade_eletrica,num_latitude_decimal,num_longitude_decimal,data_cadastro,data_perfuracao'
def fetch(params):
    url=BASE+'?'+urllib.parse.urlencode({'f':'json',**params})
    with urllib.request.urlopen(url,timeout=60) as r: blob=r.read()
    data=json.loads(blob)
    if 'error' in data: raise RuntimeError(data['error'])
    return data,url,hashlib.sha256(blob).hexdigest()
count,url,sha=fetch({'where':WHERE,'returnCountOnly':'true'})
total=count['count']; print('eligible outcomes',total,flush=True)
def page(offset):
    d,u,h=fetch({'where':WHERE,'outFields':FIELDS,'returnGeometry':'false','orderByFields':'idt_ponto','resultOffset':offset,'resultRecordCount':2000})
    (ROOT/f'potential_{offset}.json').write_text(json.dumps(d,ensure_ascii=False))
    return {'url':u,'sha256':h,'count':len(d['features'])},[f['attributes'] for f in d['features']]
with ThreadPoolExecutor(max_workers=3) as pool: pages=list(pool.map(page,range(0,total,2000)))
all_rows=[r for _,p in pages for r in p]
assert len(all_rows)==total==len({r['idt_ponto'] for r in all_rows})
def valid(r):
    a,b=r.get('num_latitude_decimal'),r.get('num_longitude_decimal')
    return isinstance(a,(int,float)) and isinstance(b,(int,float)) and -8.6<a<-5.9 and -39.1<b<-34.6
clean=[]; rejected=[]; conflicts=[]
for r in all_rows:
    if not valid(r): rejected.append(r['idt_ponto']); continue
    dry=r.get('str_tipo_situacao')=='Seco'; q=r.get('num_vazao_especifica')
    if dry and isinstance(q,(int,float)) and q>0: conflicts.append(r['idt_ponto']);continue
    clean.append({'id':str(r['idt_ponto']),'municipality':r['str_municipio'],'latitude':r['num_latitude_decimal'],'longitude':r['num_longitude_decimal'],'depth_m':r['num_profundidade'],'label':0 if dry else 1,'status':r['str_tipo_situacao'],'specific_yield':q,'aquifer':r['str_aquifero'],'ce_us_cm':r.get('num_condutividade_eletrica'),'measurement_date':None})
provenance={'provider':'SGB / SIAGAS','accessed':'2026-10-04','where':WHERE,'count_url':url,'count_sha256':sha,'returned_count':total,'valid_count':len(clean),'coordinate_rejected_ids':rejected,'contradictory_dry_and_positive_yield_ids':conflicts,'sources':[p for p,_ in pages],'label_definition':{'0':'Situação cadastral Seco, sem vazão específica positiva','1':'Vazão específica positiva; situação diferente de Seco'},'label_limit':'Situação cadastral histórica, não desfecho confirmado de nova perfuração. Falta data do teste. Não preencher ausência com zero.'}
(ROOT/'potential_dataset.json').write_text(json.dumps({'provenance':provenance,'wells':clean},ensure_ascii=False,separators=(',',':')))
print({'valid':len(clean),'productive_evidence':sum(r['label'] for r in clean),'dry_status':sum(1-r['label'] for r in clean),'municipalities':len({r['municipality'] for r in clean}),'conflicts':len(conflicts),'coordinates_rejected':len(rejected)},flush=True)
