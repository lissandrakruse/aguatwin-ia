from pathlib import Path
import urllib.request,urllib.parse,json,hashlib,concurrent.futures
ROOT=Path(__file__).resolve().parents[1]
base='https://geoportal.sgb.gov.br/server/rest/services/Hosted/siagas_web/FeatureServer/1'
where="str_uf='PB' AND str_natureza_ponto='Poço tubular' AND num_condutividade_eletrica>0 AND num_profundidade>0"
fields='idt_ponto,str_municipio,str_uf,str_natureza_ponto,str_aquifero,num_profundidade,num_condutividade_eletrica,num_ph,num_latitude_decimal,num_longitude_decimal,data_cadastro,data_perfuracao'
def query(params,name):
 url=base+'/query?'+urllib.parse.urlencode(params)
 raw=urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'AguaTwin research'}),timeout=40).read();obj=json.loads(raw)
 if obj.get('error'):raise RuntimeError(obj['error'])
 (ROOT/'research'/f'{name}.json').write_bytes(raw);(ROOT/'research'/f'{name}_url.txt').write_text(url)
 return obj
counts=query({'where':where,'returnCountOnly':'true','f':'json'},'paraiba_count')
print(json.dumps({'expected_eligible_records':counts['count']},ensure_ascii=False),flush=True)
def fetch(offset):
 obj=query({'where':where,'outFields':fields,'returnGeometry':'false','orderByFields':'idt_ponto','resultOffset':offset,'resultRecordCount':2000,'f':'json'},f'paraiba_{offset}')
 print(json.dumps({'offset':offset,'received':len(obj['features']),'exceeded':obj.get('exceededTransferLimit',False)}),flush=True);return obj
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:parts=list(pool.map(fetch,range(0,counts['count'],2000)))
features=[f for p in parts for f in p['features']]
assert len(features)==counts['count']
assert len({f['attributes']['idt_ponto'] for f in features})==len(features)
all_data={'expected_count':counts['count'],'features':features,'fields':parts[0].get('fields',[])}
(ROOT/'research/paraiba_raw.json').write_text(json.dumps(all_data,ensure_ascii=False))
print(json.dumps({'complete_records':len(features),'municipalities':len({f['attributes']['str_municipio'] for f in features})},ensure_ascii=False),flush=True)
