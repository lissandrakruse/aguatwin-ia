"""Audit manually reviewed reports. Community narratives never generate labels."""
import argparse,json,math
from datetime import date
from pathlib import Path
def numeric(value,minimum,maximum=math.inf):
 return isinstance(value,(int,float)) and not isinstance(value,bool) and math.isfinite(value) and minimum<=value<=maximum
def audit(records,today=None):
 today=today or date.today();accepted=[];leads=[];pending=[];ids=set();sites=set()
 for original in records:
  r=dict(original);reasons=[];rid=r.get('record_id');site=r.get('site_id')
  if not rid or rid in ids:reasons.append('missing_or_duplicate_record_id')
  if rid:ids.add(rid)
  if r.get('source_kind')=='community_report':
   if reasons:pending.append({'record':r,'reasons':reasons})
   else:leads.append({'record':r,'use':'Plan investigation only; no training label'})
   continue
  if r.get('source_kind') not in ['technical_report','field_measurement']:reasons.append('unsupported_source_kind')
  if r.get('review_status')!='reviewed':reasons.append('technical_review_pending')
  if not str(r.get('evidence_reference') or '').strip():reasons.append('missing_traceable_evidence')
  if not site or site in sites:reasons.append('missing_or_duplicate_accepted_site')
  try:
   measured=date.fromisoformat(r.get('measurement_date') or '')
   if measured>today:reasons.append('future_measurement_date')
  except (ValueError,TypeError):reasons.append('missing_or_invalid_measurement_date')
  if not numeric(r.get('latitude'),-90,90) or not numeric(r.get('longitude'),-180,180):reasons.append('invalid_coordinates')
  if not numeric(r.get('coordinate_accuracy_m'),.01):reasons.append('missing_coordinate_accuracy')
  test=r.get('production_test') or {};flow=test.get('flow_m3_h');outcome=test.get('outcome');method=test.get('method');label=None
  if method not in ['pumping_test','documented_drilling_test']:reasons.append('unsupported_production_method')
  if method=='pumping_test' and not numeric(test.get('duration_h'),.000001):reasons.append('missing_pumping_test_duration')
  if not numeric(flow,0):reasons.append('missing_or_invalid_operational_flow')
  elif outcome=='production_measured' and flow>0:label=1
  elif outcome=='dry_confirmed' and flow==0:label=0
  else:reasons.append('unresolved_or_contradictory_outcome')
  if reasons:pending.append({'record':r,'reasons':reasons})
  else:
   sites.add(site);accepted.append({'record':r,'label':label,'label_semantics':'Dated reviewed production/drilling test; separate from historical SIAGAS status'})
 return {'accepted_for_future_field_cohort':accepted,'community_leads':leads,'pending':pending,'counts':{'accepted':len(accepted),'community_leads':len(leads),'pending':len(pending)},'note':'Review status is supplied by humans; this audit cannot authenticate documents or technical review. Do not automatically append to historical training. Reserve sites and time periods for independent field validation.'}
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('input',type=Path);parser.add_argument('output',type=Path);args=parser.parse_args();records=json.loads(args.input.read_text());
 if not isinstance(records,list):raise ValueError('Expected JSON list of records')
 args.output.write_text(json.dumps(audit(records),ensure_ascii=False,indent=2));print('Audit saved to',args.output)
