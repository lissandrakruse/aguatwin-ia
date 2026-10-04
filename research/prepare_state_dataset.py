from pathlib import Path
import json,collections,hashlib,math,csv,datetime
ROOT=Path(__file__).resolve().parents[1]
raw=json.loads((ROOT/'research/paraiba_raw.json').read_text())
rows=[];rejected=[]
def date(v):return None if v is None else datetime.datetime.fromtimestamp(v/1000,datetime.timezone.utc).date().isoformat()
for f in raw['features']:
 a=f['attributes'];lat=a.get('num_latitude_decimal');lon=a.get('num_longitude_decimal');depth=a.get('num_profundidade');ce=a.get('num_condutividade_eletrica')
 ok=all(isinstance(v,(int,float)) and math.isfinite(v) for v in (lat,lon,depth,ce)) and -8.6<lat<-5.9 and -39.1<lon<-34.6 and depth>0 and ce>0
 if not ok:rejected.append(str(a['idt_ponto']));continue
 rows.append({'id':str(a['idt_ponto']),'municipality':a['str_municipio'],'uf':a['str_uf'],'nature':a['str_natureza_ponto'],'aquifer':a['str_aquifero'],'latitude':lat,'longitude':lon,'depth_m':depth,'ce_us_cm':ce,'ce_ds_m':ce/1000,'q_m3_h':None,'coordinates_valid_pb_bbox':True,'registration_date':date(a.get('data_cadastro')),'drilling_date':date(a.get('data_perfuracao')),'ce_measurement_date':None,'pumping_test_date':None})
assert len({r['id'] for r in rows})==len(rows)
source=[]
for offset in range(0,raw['expected_count'],2000):
 path=ROOT/'research'/f'paraiba_{offset}.json'
 source.append({'query_url':(ROOT/'research'/f'paraiba_{offset}_url.txt').read_text(),'sha256_original_json':hashlib.sha256(path.read_bytes()).hexdigest(),'received':len(json.loads(path.read_text())['features'])})
meta={'provider':'Serviço Geológico do Brasil / SIAGAS','access_date':'2026-10-04','scope':'Registros estaduais de poços tubulares com CE e profundidade positivas; dados secundários de observações de campo, sem afirmar atualização das medições.','source_layer':'https://geoportal.sgb.gov.br/server/rest/services/Hosted/siagas_web/FeatureServer/1','query_filter':"str_uf='PB' AND str_natureza_ponto='Poço tubular' AND num_condutividade_eletrica>0 AND num_profundidade>0",'returned_count':raw['expected_count'],'coordinate_audit':'Caixa ampla da Paraíba; não foi feita validação por polígonos oficiais municipais ou estaduais.','coordinate_rejected_ids':rejected,'valid_count':len(rows),'municipalities':len({r['municipality'] for r in rows}),'dates':'Datas das medições de CE e bombeamento não expostas; cadastro e perfuração preservados como tais.','units':{'ce_us_cm':'µS/cm','ce_ds_m':'µS/cm / 1000','depth_m':'m','q_m3_h':'m³/h, quando recuperado da camada Legacy'},'sources':source}
dataset={'provenance':meta,'wells':rows}
(ROOT/'research/paraiba_dataset.json').write_text(json.dumps(dataset,ensure_ascii=False,separators=(',',':')))
with (ROOT/'dist/dataset_campo_Paraiba.csv').open('w',newline='') as f:
 writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
print(json.dumps({'raw':raw['expected_count'],'valid':len(rows),'rejected_coordinates':len(rejected),'municipalities':meta['municipalities'],'CE_gt_3_ds_m':sum(r['ce_us_cm']>3000 for r in rows),'depth_range':[min(r['depth_m'] for r in rows),max(r['depth_m'] for r in rows)],'ce_range':[min(r['ce_us_cm'] for r in rows),max(r['ce_us_cm'] for r in rows)]},ensure_ascii=False))
