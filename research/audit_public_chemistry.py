"""Audit the frozen public Cabaceiras pages; never infer unnamed ions."""
import csv, hashlib, json, math, zipfile, gzip
from pathlib import Path
from html.parser import HTMLParser

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / 'research/chemistry'

class TableParser(HTMLParser):
    def __init__(self):
        super().__init__(); self.rows=[]; self.row=None; self.cell=None
    def handle_starttag(self, tag, attrs):
        if tag == 'tr': self.row=[]
        elif tag in ('td', 'th'): self.cell=[]
    def handle_data(self, data):
        if self.cell is not None: self.cell.append(data)
    def handle_endtag(self, tag):
        if tag in ('td', 'th') and self.cell is not None:
            if self.row is not None: self.row.append(' '.join(''.join(self.cell).split()))
            self.cell=None
        elif tag == 'tr' and self.row is not None:
            self.rows.append(self.row); self.row=None

def ras_mg_l(na, ca, mg):
    if any(v is None or not math.isfinite(v) or v < 0 for v in (na,ca,mg)):
        return None
    denominator=(ca/20.039 + mg/12.1525)/2
    return (na/22.989769)/math.sqrt(denominator) if denominator > 0 else None

def audit():
    raw=json.loads(gzip.decompress((FOLDER/'hosted_pb_raw.json.gz').read_bytes()))
    attributes=[f['attributes'] for f in raw['features'] if f['attributes']['str_municipio']=='Cabaceiras']
    records=[]; sources=[]
    for a in sorted(attributes, key=lambda r:r['idt_ponto']):
        code=str(a['idt_ponto']); path=FOLDER/'pages'/(code+'.html')
        blob=path.read_bytes() if path.exists() else zipfile.ZipFile(FOLDER/'pages.zip').read(code+'.html')
        parser=TableParser(); parser.feed(blob.decode('latin1'))
        params={}; unnamed=[]
        for row in parser.rows:
            if len(row)==3 and row[2]=='mg/L (ppm)':
                try: value=float(row[1])
                except ValueError: continue
                if row[0]: params[row[0]]=value
                else: unnamed.append(value)
        fields={}
        for row in parser.rows:
            if len(row)==2 and row[0] in ('Amostra:','Data da Coleta:','Condutividade Elétrica (µS/cm):'):
                fields[row[0]]=row[1] or None
        r={'id':code,'municipality':a['str_municipio'],'locality':a['str_local_ponto'],
           'latitude':a['num_latitude_decimal'],'longitude':a['num_longitude_decimal'],
           'sample_id':fields.get('Amostra:'),'collection_date':fields.get('Data da Coleta:'),
           'tds_mg_l':params.get('Solidos dissolvidos totais'),
           'na_mg_l':params.get('Sodio (Na)'), 'ca_mg_l':params.get('Calcio (Ca)'),
           'mg_mg_l':params.get('Magnesio (Mg)'), 'unnamed_values_mg_l':unnamed,
           'ce_us_cm':None,'ras':None,'status':'incomplete',
           'source_url':'https://siagasweb.sgb.gov.br/layout/detalhe.php?ponto='+code}
        # Zero-filled chemistry header values are not treated as measurements.
        ce=fields.get('Condutividade Elétrica (µS/cm):')
        try: ce=float(ce)
        except (ValueError, TypeError): ce=None
        if ce is not None and ce>0: r['ce_us_cm']=ce
        r['ras']=ras_mg_l(r['na_mg_l'],r['ca_mg_l'],r['mg_mg_l'])
        if r['ras'] is not None and r['collection_date'] and r['sample_id'] and r['ce_us_cm']:
            r['status']='eligible_for_review'
        records.append(r)
        sources.append({'id':code,'url':r['source_url'],'sha256':hashlib.sha256(blob).hexdigest()})
    result={'access_date':'2026-10-05','scope':'13 Cabaceiras wells with a chemistry parameter in the consulted public layer',
            'state_layer_records':len(raw['features']),'detail_pages_audited':len(records),
            'eligible_for_review':sum(r['status']=='eligible_for_review' for r in records),
            'notes':['The map layer is a partial export, not the complete SIAGAS chemistry database.',
                     'An unnamed concentration is never assigned to sodium.',
                     'Drilling and registration dates are not collection dates.',
                     'No independent validation or irrigation suitability is established.'],
            'sources':sources,'records':records}
    (FOLDER/'audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    columns=['id','municipality','locality','latitude','longitude','sample_id','collection_date','tds_mg_l','na_mg_l','ca_mg_l','mg_mg_l','ce_us_cm','ras','status','source_url']
    with (FOLDER/'cabaceiras_chemistry.csv').open('w',newline='') as file:
        writer=csv.DictWriter(file,fieldnames=columns,extrasaction='ignore');writer.writeheader();writer.writerows(records)
    return result

if __name__=='__main__':
    result=audit()
    print(json.dumps({k:result[k] for k in ['state_layer_records','detail_pages_audited','eligible_for_review']}))
