import os,tempfile,unittest
fd,path=tempfile.mkstemp(suffix='.sqlite3');os.close(fd);os.environ['BIZDNA_DB']=path
from storage import init,save,delete
from followup import init_followup,add_action,update_action,actions,add_measurement,evaluate
class TestFollowup(unittest.TestCase):
 @classmethod
 def setUpClass(cls):init();init_followup()
 def test_tracking_and_cascade(self):
  payload={'profile':{'name':'가상점포','sector':'외식업','monthly_sales':100,'monthly_cost':80}}
  sid=save(payload,{'overall':55},'가상상권',True)
  add_action(sid,'원가개선','재료비 분석','점주','2026-12-01')
  aid=actions(sid)[0]['id'];update_action(aid,'완료');self.assertEqual(actions(sid)[0]['status'],'완료')
  add_measurement(sid,'2026-11-01',120,90,repeat=30)
  s=evaluate(sid);self.assertEqual(s['measurements'][0]['sales_change_from_baseline_pct'],20)
  self.assertEqual(s['measurements'][0]['operating_surplus_proxy'],30)
  delete(sid);self.assertEqual(actions(sid),[])
 def test_validation(self):
  with self.assertRaises(ValueError):add_measurement(1,'2026-11-01',-1,5)
  with self.assertRaises(ValueError):update_action(1,'invalid')
if __name__=='__main__':unittest.main()
