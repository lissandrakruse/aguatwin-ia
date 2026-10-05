"""Synthetic software fixtures, never groundwater observations or model data."""
import copy,unittest
from datetime import date
from import_field_reports import audit
class AuditTests(unittest.TestCase):
 def record(self):return {'record_id':'test-1','site_id':'synthetic-site','source_kind':'field_measurement','evidence_reference':'synthetic QA fixture','review_status':'reviewed','measurement_date':'2025-01-01','latitude':-7.49,'longitude':-36.29,'coordinate_accuracy_m':5,'production_test':{'method':'pumping_test','outcome':'production_measured','flow_m3_h':1,'duration_h':24}}
 def check_pending(self,r):self.assertEqual(audit([r])['counts']['pending'],1)
 def test_community_text_is_not_label(self):
  r=self.record();r['source_kind']='community_report';r['notes']='poço seco sem água';self.assertEqual(audit([r])['counts'],{'accepted':0,'community_leads':1,'pending':0})
 def test_missing_flow_is_not_zero(self):
  r=self.record();r['production_test']['flow_m3_h']=None;self.check_pending(r)
 def test_broken_pump_is_not_dry(self):
  r=self.record();r['production_test'].update(outcome='pump_broken',flow_m3_h=0);self.check_pending(r)
 def test_dry_with_positive_flow_is_contradictory(self):
  r=self.record();r['production_test']['outcome']='dry_confirmed';self.check_pending(r)
 def test_reviewed_production_and_dry(self):
  r=self.record();dry=copy.deepcopy(r);dry.update(record_id='test-2',site_id='synthetic-2');dry['production_test'].update(method='documented_drilling_test',outcome='dry_confirmed',flow_m3_h=0);self.assertEqual([x['label'] for x in audit([r,dry])['accepted_for_future_field_cohort']],[1,0])
 def test_duplicate_site_is_not_second_sample(self):
  r=self.record();dup=copy.deepcopy(r);dup['record_id']='test-2';self.assertEqual(audit([r,dup])['counts'],{'accepted':1,'community_leads':0,'pending':1})
 def test_future_or_missing_date(self):
  for when in ['2099-01-01',None]:
   r=self.record();r['measurement_date']=when;self.check_pending(r)
 def test_pending_review(self):
  r=self.record();r['review_status']='pending';self.check_pending(r)
if __name__=='__main__':unittest.main()
